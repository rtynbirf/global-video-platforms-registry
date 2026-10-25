#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_datapackage.py — frictionless Data Package v2 descriptor generated from actual data."""
import json, collections, hashlib

W = '/home/z/my-project/registry_work/final'
D = '/home/z/my-project/download'

reg = json.load(open(W + '/registry_final.json', encoding='utf-8'))
recs = reg
sc = dict(collections.Counter(r['status'] for r in recs))

COLS = ['id', 'name', 'official_url', 'region', 'region_orig', 'country', 'category',
        'user_upload', 'status', 'status_detail', 'verdict_http', 'moved_to', 'notes',
        'verified_date', 'source', 'confidence', 'origin']

DESCR = {
 'id': 'Стабильный ID записи (база 1-451, добор B5-xxx)',
 'name': 'Название платформы',
 'official_url': 'Официальный домен/путь (актуальный после ребрендингов)',
 'region': 'География (12 енумов)',
 'region_orig': 'Регион исходного набора',
 'country': 'Страна',
 'category': 'Категория платформы',
 'user_upload': 'Публичная пользовательская загрузка',
 'status': 'Статус жизненного цикла',
 'status_detail': 'Уточнение статуса',
 'verdict_http': 'Сырой HTTP-вердикт последней пробы',
 'moved_to': 'Платформа-преемник (для merged)',
 'notes': 'Факты последней проверки',
 'verified_date': 'Дата последней верификации (ISO-8601)',
 'source': 'Метод/источник проверки',
 'confidence': 'Уверенность High/Medium/Low',
 'origin': 'Происхождение записи',
}
TYPES = {'id': 'string', 'name': 'string', 'official_url': 'string', 'region': 'string',
         'region_orig': 'string', 'country': 'string', 'category': 'string',
         'user_upload': 'string', 'status': 'string', 'status_detail': 'string',
         'verdict_http': 'string', 'moved_to': 'string', 'notes': 'string',
         'verified_date': 'date', 'source': 'string', 'confidence': 'string', 'origin': 'string'}

fields = []
for c in COLS:
    f = {'name': c, 'type': TYPES[c], 'description': DESCR[c]}
    if c == 'status':
        f['constraints'] = {'enum': ['active', 'merged', 'closed', 'parked', 'unverified', 'unverified_dead']}
    if c == 'user_upload':
        f['constraints'] = {'enum': ['yes', 'no', 'partial']}
    if c == 'verified_date':
        f['constraints'] = {'pattern': r'\d{4}-\d{2}-\d{2}'}
    if c in ('id', 'name', 'region', 'category', 'status', 'verified_date', 'origin'):
        f['constraints'] = {**f.get('constraints', {}), 'required': True}
    fields.append(f)

sha = hashlib.sha256(open(D + '/global_video_platforms_registry_2026.csv', 'rb').read()).hexdigest()

pkg = {
 '$schema': 'https://datapackage.org/schemas/data-package.json',
 'name': 'global-video-platforms-registry-2026',
 'title': 'Global Video Platforms Registry 2026 (verified)',
 'description': 'Верифицированный реестр 1071 видеоплатформы: HTTP-проверка каждого домена, трассировка ребрендингов (merged→moved_to), явная политика контента. Два прохода верификации 2026-10-24/25 + финальная дочистка хвостов.',
 'version': '3.2.0',
 'created': '2026-10-25',
 'licenses': [{'name': 'CC-BY-4.0', 'path': 'https://creativecommons.org/licenses/by/4.0/legalcode.txt', 'title': 'Creative Commons Attribution 4.0 International'}],
 'contributors': [{'title': 'rtynbirf', 'role': 'author'}, {'title': 'Z.ai verification pipeline', 'role': 'contributor'}],
 'keywords': ['video platforms', 'streaming', 'OTT', 'registry', 'verified dataset', 'media research'],
 'homepage': 'https://github.com/rtynbirf/global-video-platforms-registry',
 'resources': [{
   'name': 'global_video_platforms_registry_2026',
   'title': 'Реестр видеоплатформ (основная таблица)',
   'path': 'download/global_video_platforms_registry_2026.csv',
   'type': 'table',
   'format': 'csv',
   'mediatype': 'text/csv',
   'encoding': 'utf-8-sig',
   'dialect': {'csv': {'delimiter': ',', 'header': True, 'lineTerminator': '\r\n'}},
   'schema': {'fields': fields, 'primaryKey': ['id']},
   'hash': f'sha256:{sha}',
   'stats': {'rows': len(recs)},
 }],
 'views': [
   {'name': 'status_summary', 'title': 'Статусы', 'type': 'report',
    'spec': {'bins': [{'value': k, 'count': v} for k, v in sorted(sc.items(), key=lambda x: -x[1])]}},
 ],
 'custom': {
   'status_counts': sc,
   'active_total': sc.get('active', 0),
   'verified_dates': ['2026-10-24', '2026-10-25'],
   'policy_exclusions': 'see excluded_policy in JSON package (11 records: political, adult)',
   'same_domain_distinct_products': ['vimeo.com (Vimeo / Vimeo OTT)', 'linkedin.com (LinkedIn / LinkedIn Learning)'],
 },
}
json.dump(pkg, open(D + '/datapackage.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
import shutil
shutil.copy(D + '/datapackage.json', '/home/z/my-project/datapackage.json')
print('datapackage.json written:', len(json.dumps(pkg)), 'bytes; sha256:', sha[:12])
