#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""doh_check.py — verify sandbox DNS failures via DNS-over-HTTPS (dns.google).
If DoH returns NOERROR with A/AAAA records, the domain is registered and
serving; the local resolver is at fault. NXDOMAIN => domain truly dead."""
import json, urllib.request, urllib.parse

DOMAINS = {
 'FTV (RTFBiH)': 'ftv.ba',
 'Mola': 'mola.tv',
 'MX TakaTak': 'mxtakatak.com',
 'Filmatique': 'filmatique.tv',
 'Sooner': 'sooner.club',
 'Festhome TV': 'festhome.tv',
 'WRESTLE UNIVERSE': 'wrestle-universe.jp',
 'Vidgo': 'vidgo.com',
 'UpLive': 'upliveapps.com',
 'Aloula': 'aloula.ma',
 'GoPlay.bg': 'goplay.bg',
 'J:COM STREAM': 'jcom.stream',
 'LINE TV': 'line.me',
 'Bstation': 'bstation.com',
 'Toffee': 'toffee.com.bd',
 'Anime Times': 'animetimestv.com',
 'WASD.tv': 'wasd.tv',
 'Pilipinas Live': 'pilipinas.live',
 'DistroTV': 'distro.tv',
 'RugbyPass TV': 'rugbypasstv.com',
}

def doh(name):
    u = 'https://dns.google/resolve?name=%s&type=A' % urllib.parse.quote(name)
    req = urllib.request.Request(u, headers={'Accept': 'application/dns-json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:  # noqa: BLE001
        return {'Status': -1, 'error': str(e)[:80]}

out = {}
for label, dom in DOMAINS.items():
    d = doh(dom)
    st = d.get('Status', -1)
    answers = [a.get('data') for a in d.get('Answer', []) if a.get('type') in (1, 28)]
    verdict = 'RESOLVES' if answers else ('NXDOMAIN_dead' if st == 3 else 'no_A/%s' % st)
    out[label] = {'domain': dom, 'status': st, 'ips': answers[:3], 'verdict': verdict}
    print('%-18s %-16s %s' % (label, dom, verdict), answers[:2] if answers else '')

json.dump(out, open('/home/z/my-project/registry_work/checks/doh_results.json', 'w',
                    encoding='utf-8'), ensure_ascii=False, indent=1)
