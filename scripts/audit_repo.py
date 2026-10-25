#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_repo.py — integrity + consistency audit of the registry deliverables."""
import json, csv, re, sys, collections, os

ROOT = os.environ.get('REPO_ROOT', '/home/z/my-project')
D = ROOT + '/download'
E = ROOT + '/evidence'
issues, warns = [], []

reg = json.load(open(D + '/global_video_platforms_registry_2026.json', encoding='utf-8'))
recs = reg['registry']
try:
    summary = json.load(open(E + '/summary.json', encoding='utf-8'))
except FileNotFoundError:
    summary = None
    warns.append('evidence/summary.json missing — counts cross-check skipped')

# 1. CSV <-> JSON sync
rows = list(csv.DictReader(open(D + '/global_video_platforms_registry_2026.csv', encoding='utf-8-sig')))
if len(rows) != len(recs):
    issues.append(f'CSV({len(rows)}) != JSON({len(recs)}) row count')

# 2. duplicate ids / domains
ids = [r['id'] for r in recs]
dups = [k for k, v in collections.Counter(ids).items() if v > 1]
if dups: issues.append(f'dup ids: {dups[:5]}')
doms = [re.sub(r'^www\.', '', (r.get('official_url') or '').lower()).split('?')[0].replace('https://','').replace('http://','').split('/')[0] for r in recs if r['status'] == 'active']
# whitelisted same-domain distinct products (documented in DATA_DICTIONARY)
PRODUCT_PAIRS = {'vimeo.com', 'linkedin.com'}
ddups = [k for k, v in collections.Counter(d for d in doms if d and d != 'unknown').items() if v > 1 and k not in PRODUCT_PAIRS]
if ddups: issues.append(f'dup domains: {ddups[:8]}')

# 3. status enum + counts
VALID = {'active','merged','closed','parked','unverified','unverified_dead'}
sc = collections.Counter(r['status'] for r in recs)
bad = set(sc) - VALID
if bad: issues.append(f'bad status: {bad}')
if summary and dict(sc) != {k: v for k, v in summary['status_counts'].items()}:
    warns.append(f'summary.status_counts drift: {dict(sc)} vs {summary["status_counts"]}')

# 3b. datapackage.json cross-check
pkg = json.load(open(ROOT + '/datapackage.json', encoding='utf-8'))
res = pkg['resources'][0]
if res['stats']['rows'] != len(recs):
    issues.append(f'datapackage rows {res["stats"]["rows"]} != JSON {len(recs)}')
if pkg['custom']['active_total'] != sc['active']:
    issues.append(f'datapackage active_total {pkg["custom"]["active_total"]} != computed {sc["active"]}')

# 4. required fields
for r in recs:
    miss = [k for k in ('id','name','region','category','status','verified_date') if not r.get(k)]
    if miss: issues.append(f'{r["id"]}: missing {miss}')
    u = r.get('official_url') or ''
    if r['status'] == 'active' and not u.startswith('http'):
        issues.append(f'{r["id"]}: active without http URL: {u!r}')
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', r.get('verified_date') or ''):
        issues.append(f'{r["id"]}: bad verified_date {r.get("verified_date")!r}')

# 5. user_upload enum
ue = set(r.get('user_upload') for r in recs) - {'yes','no','partial',None,''}
if ue: warns.append(f'user_upload extra values: {ue}')

# 6. README_RU numbers sync (computed, not hardcoded)
readme = open(D + '/README_RU.md', encoding='utf-8').read()
if f'{sc["active"]} активных' not in readme:
    warns.append('README_RU: active count string not found/updated')
if f'{len(recs)} запис' not in readme:
    warns.append('README_RU: total count string not found/updated')

# 7. URL sanity for actives
bad_urls = [r['id'] for r in recs if r['status']=='active' and re.search(r'\s|[а-яё]', (r.get('official_url') or ''))]
if bad_urls: issues.append(f'weird active urls: {bad_urls[:5]}')

print(f'RECORDS={len(recs)}  STATUS={dict(sc)}')
print(f'REGIONS={len(set(r["region"] for r in recs))} unique')
print('ISSUES:', len(issues)); [print('  !', i) for i in issues[:30]]
print('WARNS:', len(warns)); [print('  ~', w) for w in warns[:10]]
sys.exit(1 if issues else 0)
