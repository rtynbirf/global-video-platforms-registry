#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_csv_json.py — flat CSV (UTF-8 BOM, 17 cols) + JSON dump to download/."""
import json, csv

W = '/home/z/my-project/registry_work/final'
D = '/home/z/my-project/download'
reg = json.load(open(W + '/registry_final.json', encoding='utf-8'))
summary = json.load(open(W + '/summary.json', encoding='utf-8'))
excluded = json.load(open(W + '/excluded_policy.json', encoding='utf-8'))

COLS = ['id', 'name', 'official_url', 'region', 'region_orig', 'country', 'category',
        'user_upload', 'status', 'status_detail', 'verdict_http', 'moved_to', 'notes',
        'verified_date', 'source', 'confidence', 'origin']

with open(D + '/global_video_platforms_registry_2026.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
    w.writeheader()
    for r in reg:
        w.writerow({k: (r.get(k) or '') for k in COLS})
print('csv ok:', len(reg), 'rows')

with open(D + '/global_video_platforms_registry_2026.json', 'w', encoding='utf-8') as f:
    json.dump({'generated': '2026-10-25', 'summary': summary,
               'registry': reg, 'excluded_policy': excluded}, f, ensure_ascii=False, indent=1)
print('json ok')
