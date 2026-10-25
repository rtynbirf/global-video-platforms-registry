#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_urls.py — HTTP liveness checker for the global video-platform registry.

Usage:
  python3 check_urls.py <input.json> <output.json> [workers]

Input:  JSON array of records having at least {"id","name","official_url"}.
Output: JSON array of results with verdicts:
  ALIVE / BLOCKED(bot-protection) / PARKED / NOT_FOUND / CLIENT_ERR /
  SERVER_ERR / DNS_FAIL / TIMEOUT / UNREACHABLE / SSL_ERR / REDIRECT_LOOP / BAD_URL
Verdicts are saved incrementally (atomic tmp+rename) so a crash or context
loss never destroys partial work.
"""
import concurrent.futures
import gzip
import io
import json
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

IN_PATH = sys.argv[1] if len(sys.argv) > 1 else \
    '/home/z/my-project/registry_work/extracted/global_video_platforms_research_RU/register.json'
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else \
    '/home/z/my-project/registry_work/checks/base_results.json'
WORKERS = int(sys.argv[3]) if len(sys.argv) > 3 else 32
TIMEOUT = 14
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
BLOCKED_CODES = {401, 403, 405, 406, 429, 451}
PARKED_RX = re.compile(
    r'(domain\s+(is\s+)?for\s+sale|buy\s+this\s+domain|parked\s+domain|hugedomains|'
    r'sedoparking|afternic|dan\.com|domain\s+is\s+listed|продам\s+домен|'
    r'домен\s+прода(ё|е)тся|купить\s+домен|спаркован|this\s+webpage\s+parked)', re.I)
TITLE_RX = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def fetch(url):
    """Return (final_url, status, body, err). status None => transport error."""
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip',
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
            raw = r.read(131072)
            if r.headers.get('Content-Encoding', '').lower() == 'gzip':
                try:
                    raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read(131072)
                except Exception:
                    pass
            return r.geturl(), r.status, raw, None
    except urllib.error.HTTPError as e:
        return getattr(e, 'url', url), e.code, b'', str(e)[:120]
    except urllib.error.URLError as e:
        reason = getattr(e, 'reason', None)
        s = str(reason).lower()
        if isinstance(reason, socket.gaierror) or 'name or service' in s or 'nodename' in s:
            return url, None, b'', 'dns_error'
        if 'certificate' in s:
            return url, None, b'', 'ssl_error'
        if 'refused' in s:
            return url, None, b'', 'conn_refused'
        if 'timed out' in s:
            return url, None, b'', 'timeout'
        return url, None, b'', 'urlopen:%s' % (reason or e)
    except socket.timeout:
        return url, None, b'', 'timeout'
    except Exception as e:  # noqa: BLE001
        return url, None, b'', '%s:%s' % (type(e).__name__, e)


def extract_title(body):
    if not body:
        return ''
    text = body[:65536].decode('utf-8', 'ignore')
    m = TITLE_RX.search(text)
    return re.sub(r'\s+', ' ', m.group(1)).strip()[:300] if m else ''


def classify(src_netloc, final_url, status, body, err):
    final_netloc = urllib.parse.urlparse(final_url or '').netloc.lower()
    if status is None:
        if err == 'dns_error':
            return 'DNS_FAIL'
        if err in ('timeout',) or (err or '').startswith('urlopen:timed out'):
            return 'TIMEOUT'
        if err == 'ssl_error':
            return 'SSL_ERR'
        if err == 'conn_refused':
            return 'UNREACHABLE'
        return 'UNREACHABLE'
    if status == 200:
        text = (body or b'')[:40960].decode('utf-8', 'ignore')
        if PARKED_RX.search(text):
            return 'PARKED'
        return 'ALIVE'
    if status in BLOCKED_CODES:
        return 'BLOCKED'
    if 300 <= status < 400:
        return 'REDIRECT_LOOP'
    if status in (404, 410):
        return 'NOT_FOUND'
    if 400 <= status < 500:
        return 'CLIENT_ERR'
    return 'SERVER_ERR'


def normalize(u):
    if not u or not isinstance(u, str) or u.strip().upper() == 'UNKNOWN':
        return None
    u = u.strip()
    if not re.match(r'^https?://', u, re.I):
        u = 'https://' + u
    return u


def check_rec(rec):
    rid = rec.get('id')
    name = rec.get('name', '')
    url0 = normalize(rec.get('official_url'))
    base = {'id': rid, 'name': name, 'url': rec.get('official_url', ''),
            'checked_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    if not url0:
        base.update(verdict='BAD_URL', http_status=None, final_url='', title='',
                    error='no url', moved_to='')
        return base
    attempts = [url0]
    p = urllib.parse.urlparse(url0)
    host = p.netloc.lower()
    # variant 1: add www.
    if not host.startswith('www.'):
        attempts.append(urllib.parse.urlunparse(p._replace(netloc='www.' + host)))
    # variant 2: https fallback for plain http
    if p.scheme == 'http':
        attempts.append(urllib.parse.urlunparse(p._replace(scheme='https')))
    verdict, status, final_url, title, err = None, None, url0, '', ''
    seen = set()
    for i, u in enumerate(attempts):
        if u in seen:
            continue
        seen.add(u)
        final_url, status, body, err = fetch(u)
        verdict = classify(urllib.parse.urlparse(u).netloc, final_url, status, body, err)
        if verdict in ('ALIVE', 'BLOCKED', 'PARKED', 'NOT_FOUND', 'CLIENT_ERR',
                       'SERVER_ERR', 'REDIRECT_LOOP'):
            title = extract_title(body)
            break
        if i + 1 < len(attempts):
            time.sleep(0.3)
    moved = ''
    try:
        src = urllib.parse.urlparse(url0).netloc.lower().replace('www.', '')
        dst = urllib.parse.urlparse(final_url or '').netloc.lower().replace('www.', '')
        if verdict in ('ALIVE', 'BLOCKED') and dst and src and src != dst:
            moved = dst
    except Exception:
        pass
    base.update(verdict=verdict, http_status=status, final_url=final_url,
                title=title, error=err if verdict not in ('ALIVE', 'BLOCKED') else '',
                moved_to=moved)
    return base


def main():
    with open(IN_PATH, encoding='utf-8') as f:
        recs = json.load(f)
    print('Input records: %d' % len(recs), flush=True)
    results = []
    lock_step = max(1, len(recs) // 20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(check_rec, r): r.get('id') for r in recs}
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            try:
                results.append(fut.result())
            except Exception as e:  # noqa: BLE001
                results.append({'id': futs[fut], 'name': '', 'url': '',
                                'verdict': 'CRASH', 'http_status': None,
                                'final_url': '', 'title': '',
                                'error': str(e)[:200], 'moved_to': ''})
            done += 1
            if done % lock_step == 0 or done == len(recs):
                tmp = OUT_PATH + '.tmp'
                with open(tmp, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False)
                import os
                os.replace(tmp, OUT_PATH)
    # summary
    from collections import Counter
    c = Counter(r['verdict'] for r in results)
    print('=== DONE %d ===' % len(results))
    for k, v in c.most_common():
        print('  %-14s %d' % (k, v))
    moved = [r for r in results if r.get('moved_to')]
    print('Cross-domain redirects: %d' % len(moved))
    for r in moved[:40]:
        print('  #%s %s -> %s (%s)' % (r['id'], r['url'], r['moved_to'], r['verdict']))


if __name__ == '__main__':
    main()
