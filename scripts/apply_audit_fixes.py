#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_audit_fixes.py — v3.2: resolve 3 duplicate-domain records + fill Slow Channel URL."""
import json, collections

W = '/home/z/my-project/registry_work/final'
reg = json.load(open(W + '/registry_final.json', encoding='utf-8'))
by_id = {str(r['id']): r for r in reg}

FIX = {
 '342': dict(status='merged', moved_to='IBM Video Streaming',
             notes='Дубль записи id 450 из исходного набора; бренд Ustream закрыт, продукт жив как IBM Video Streaming'),
 '450': dict(status='merged', moved_to='IBM Video Streaming',
             notes='Ustream закрыт как бренд (поглощён IBM), продукт жив как IBM Video Streaming'),
 '1383': dict(status='merged', moved_to='Cignal Play',
              notes='Pilipinas Live поглощён Cignal Play; домен cignalplay.com уже зарегистрирован (id 144)'),
 '441': dict(official_url='https://slowchannel.com'),
}
for i, patch in FIX.items():
    r = by_id[i]
    r.update(patch)
    r['verified_date'] = '2026-10-25'

json.dump(reg, open(W + '/registry_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

sc = dict(collections.Counter(x['status'] for x in reg))
summary = json.load(open(W + '/summary.json', encoding='utf-8'))
summary['status_counts'] = sc
summary['active_total'] = sc.get('active', 0)
summary['audit_v32'] = {'date': '2026-10-25', 'dedup_fixed': ['id342/id450 Ustream->IBM Video Streaming',
                        'id1383 Cignal Play dup (ex-Pilipinas Live)', 'id441 Slow Channel URL filled'],
                        'legit_same_domain_products': ['Vimeo/vimeo.com/ott', 'LinkedIn/linkedin.com/learning']}
json.dump(summary, open(W + '/summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v3.2 status:', sc, '| active_total:', summary['active_total'])
