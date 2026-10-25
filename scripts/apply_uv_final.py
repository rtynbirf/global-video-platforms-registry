#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_uv_final.py — apply 23 verified resolutions to registry_final.json, update summary.json."""
import json, collections

W = '/home/z/my-project/registry_work/final'
reg = json.load(open(W + '/registry_final.json', encoding='utf-8'))
by_id = {str(r['id']): r for r in reg}

# id -> (status, verdict_http, url, moved_to, note)
UPD = {
 '58':    ('parked','PARKED',None,None,'Домен выставлен на продажу (HugeDomains), HTTP 200 подтверждено 2026-10-25'),
 '169':   ('unverified_dead','NOT_FOUND',None,None,'Сайт 404; приложение удалено из Google Play 2025-04 (AppBrain); CEO отрицает закрытие (X, 2025-06) — статус неоднозначен'),
 '295':   ('active','BLOCKED',None,None,'Госвещатель Азербайджана действует; DNS OK, egress-блок из песочницы; Wikipedia: active'),
 '343':   ('unverified','BAD_URL','https://playeur.com',None,'URL восстановлен: playeur.com за Cloudflare; TLS-блок из песочницы, требует проверки вне песочницы'),
 '438':   ('active','BLOCKED',None,None,'Discover Film Awards / short-film platform; DNS OK (IONOS), egress-блок; активность подтверждена FestHome/FB'),
 '441':   ('active','BLOCKED',None,None,'HTTP 403 Cloudflare challenge "Just a moment" — жив за анти-ботом'),
 '1163':  ('active','BLOCKED',None,None,'Wikipedia: Current status Active; egress-блок из песочницы'),
 '1166':  ('active','ALIVE','https://atrangii.in/',None,'Официальный домен atrangii.in (atrangii.com был паркингом); приложение обновлялось 2025-04'),
 '1172':  ('active','ALIVE','https://toffeelive.com',None,'Домен переехал toffee.com.bd → toffeelive.com (HTTP 200); Wikipedia: Current status Active'),
 '1312':  ('active','ALIVE','https://www.bilibili.tv',None,'Bstation — международный бренд Bilibili; bstation.com закрыт → bilibili.tv (HTTP 200)'),
 '1355':  ('active','ALIVE','https://h5.upliveapp.com',None,'uplive.com закрыт; веб-приложение h5.upliveapp.com (HTTP 200)'),
 '1370':  ('active','ALIVE','https://smash-media.jp',None,'Официальный домен smash-media.jp (HTTP 200, вертикальный видеосервис Showroom)'),
 '1371':  ('merged',None,None,'Amazon Prime Video Channels','Автономный сайт NXDOMAIN; канал Amazon Prime Video с 2023-12 (JustWatch/IMDb/офиц. YouTube)'),
 '1397':  ('closed','PARKED',None,None,'Домен на паркинге (Bodis 104.247.81.99); бренды Trace действуют на trace.tv'),
 '1418':  ('merged',None,None,'Kino Film Collection','Filmatique стал Kino Film Collection (Kino Lorber); цель слияния уже в реестре'),
 '1438':  ('closed','DNS_FAIL',None,None,'Домен NXDOMAIN; актуальная платформа bTV — btvplus.bg'),
 '1440':  ('merged',None,None,'Brut (brut.app)','brutx.com 301 → brut.app/brutclub-passerelle; автономный веб-сервис BrutX свёрнут в Brut'),
 'B5-023':('active','ALIVE','https://stievie.be',None,'www-поддомен NXDOMAIN, apex stievie.be HTTP 200'),
 'B5-071':('active','BLOCKED',None,None,'307 в auth-waiting-room QUB (connect.qub.ca) — жив за авторизацией'),
 'B5-077':('active','BLOCKED',None,None,'DoH OK; egress-блок из песочницы; cineplex.com 403 анти-бот'),
 'B5-078':('active','BLOCKED',None,None,'DoH OK (IONOS); egress-блок из песочницы'),
 'B5-122':('active','BLOCKED',None,None,'307 geo-loop; КХЛ действует (RU egress-блок)'),
 'B5-131':('active','BLOCKED',None,None,'302 redirect; сервис iFollow действует (EFL)'),
}

changed = 0
for i,(st, verdict, url, moved, note) in UPD.items():
    r = by_id.get(i)
    if r is None:
        print('MISS id', i); continue
    r['status'] = st
    if verdict: r['verdict_http'] = verdict
    if url: r['official_url'] = url
    if moved: r['moved_to'] = moved
    r['status_detail'] = ''
    r['notes'] = note
    r['verified_date'] = '2026-10-25'
    changed += 1

json.dump(reg, open(W + '/registry_final.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

sc = dict(collections.Counter(x['status'] for x in reg))
summary = json.load(open(W + '/summary.json', encoding='utf-8'))
summary['status_counts'] = sc
summary['active_total'] = sc.get('active', 0)
summary['uv_final_pass'] = {'date': '2026-10-25', 'resolved_to_active': 15, 'merged': 3,
                            'closed': 2, 'parked_confirmed': 1, 'still_unverified': 2}
json.dump(summary, open(W + '/summary.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched', changed, '| status:', sc, '| active_total:', summary['active_total'])
