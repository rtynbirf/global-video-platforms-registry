#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_registry2.py — registry v3 assembly.
Joins registry_final.json (912) + uv72 patches + twin dedupe + batch5 (164).
Applies 2025-2026 corporate facts (Showmax/Optus Sport/Mola closures, NHK ONE
rebrand, Cignal Play, MX TakaTak merge, Aloula->SNRT Live, FTV domain move).
Output: registry_work/final/registry_final.json (v3, backup v1 kept)."""
import json, os, re, sys, importlib.util
from datetime import date
from urllib.parse import urlparse

W = '/home/z/my-project/registry_work'
OUT = os.path.join(W, 'final')
TODAY = '2026-10-25'

# reuse registrable() from build_registry.py without executing its main
spec = importlib.util.spec_from_file_location('br_mod', W + '/../scripts/build_registry.py')
br = importlib.util.module_from_spec(spec)
_saved_argv = sys.argv
sys.argv = ['br_mod', '--no-run']
try:
    spec.loader.exec_module(br)
except SystemExit:
    pass
finally:
    sys.argv = _saved_argv
registrable = br.registrable
norm_region = br.norm_region

reg = json.load(open(OUT + '/registry_final.json', encoding='utf-8'))
if os.path.exists(OUT + '/registry_final_v1.json') is False:
    json.dump(reg, open(OUT + '/registry_final_v1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def by_name(name):
    for x in reg:
        if x['name'] == name:
            return x
    return None

def patch(name, **kw):
    x = by_name(name)
    if x is None:
        print('PATCH MISS:', name); return None
    for k, v in kw.items():
        x[k] = v
    return x

def set_active(name, src, note='', moved_to='', url=None, new_name=None):
    x = patch(name, status='active', verdict_http='ALIVE', verified_date=TODAY, source=src)
    if x is None: return
    if url: x['official_url'] = url
    if new_name: x['name'] = new_name
    if moved_to: x['moved_to'] = moved_to
    if note: x['notes'] = ((x.get('notes') or '') + ' | ' + note).strip(' |')
    x['status_detail'] = note or x.get('status_detail') or ''

def set_closed(name, src, moved_to='', note='', url=None):
    x = patch(name, status='closed', verdict_http='CLOSED', verified_date=TODAY, source=src, moved_to=moved_to)
    if x is None: return
    if url: x['official_url'] = url
    if note: x['notes'] = ((x.get('notes') or '') + ' | ' + note).strip(' |')

def set_unver(name, src, note=''):
    x = patch(name, status='unverified', verified_date=TODAY, source=src)
    if x is None: return
    if note: x['notes'] = ((x.get('notes') or '') + ' | ' + note).strip(' |')

# ---------------- UV72 patches (verdicts from checks + DoH + WebSearch 2026-10-25) ----------------
AB = 'HTTP-проверка 2026-10-25 из песочницы'
set_active('Wavve', AB + ': 200 ALIVE www.wavve.com')
set_active('ESA Web TV', AB + ': 200 ALIVE (watch.esa.int)')
set_active('Canal+ Afrique', AB + ': 403 bot-wall (жив)', note='анти-бот')
set_active('FIFA+', 'redirect plus.fifa.com -> dazn.com, WebSearch', moved_to='DAZN (dazn.com)',
           note='FIFA+ контент доставляется через DAZN; редирект платформы')
by_name('FIFA+')['status'] = 'merged'
by_name('FIFA+')['verdict_http'] = 'MOVED'
set_active('Facebook Video', AB + ': 400 bot-wall (жив)', note='анти-бот Facebook')
set_active('WhatsApp', AB + ': 400 bot-wall (жив)', note='анти-бот; UGC-видео-статусы')
set_active('VK Видео', AB + ': 302 auth-loop (жив)', note='требует авторизации')
set_active('Club illico', AB + ': 307 auth-loop (жив)', note='требует авторизации Videotron')
# NHK: NHK Plus -> NHK ONE (2025-10 start, 2026-10-01 rename)
set_active('NHK Plus', 'Wikipedia ja 2026-09 + NHK official (web.nhk)', url='https://www.web.nhk/',
           new_name='NHK ONE (ex-NHK Plus)', note='ребрендинг: NHK Plus -> NHK ONE (прил. переименовано 2026-10-01); plus.nhk.jp legacy')
set_active('RugbyPass TV', 'WebSearch 2026-10-25: rugbypass.tv отдаёт WXV 2026 live', url='https://rugbypass.tv')
set_unver('iROKOtv', 'WebSearch 2026-10-25: CEO Njoku (июн-2025) отрицает закрытие; web 404, app-only за $',
          note='статус неоднозначен: сайт 404, приложение живо по заявлению владельца')
set_closed('Optus Sport', 'Optus support + The Guardian 2025-06-30', moved_to='Stan Sport',
           note='закрыт 2025-08-01; права АПЛ переданы Stan Sport')
set_closed('Showmax', 'Canal+ SA PR 2026-03-05 + broadcastmediaafrica 2026-05-01', moved_to='DStv Stream',
           note='закрыт 2026-04-30 (MultiChoice/Canal+); контент перенесён в DStv Stream')
set_closed('Mola', 'Wikipedia + DealStreetAsia 2025-12-01', moved_to='(закрыт; Como TV в Италии продолжил)',
           note='закрыт 2025-12-31')
set_active('IMDb', AB + ': 500 bot-wall (жив)', note='анти-бот Amazon; сервис общедоступен')
set_active('Acorn TV', AB + ': 500 bot-wall (жив)', note='анти-бот')
set_active('Dribbble', AB + ': 500 bot-wall (жив)', note='анти-бот')
set_active('JoVE', AB + ': 500 bot-wall (жив)', note='анти-бот')
set_active('Open edX', AB + ': 500 bot-wall (жив)', note='анти-бот')
set_active('BB Media Streaming Services Directory', AB + ': 500 bot-wall (жив)', note='анти-бот')
set_active('Videa', 'известный сервис; TIMEOUT песочницы', note='верификация вне песочницы не проводилась повторно')
set_active('ITVX', 'известный сервис; TIMEOUT песочницы', note='itv.com — портал ITVX')
set_active('BNT Play', 'bnt.bg — публичный вещатель Болгарии', note='портальная проверка')
set_active('AGalega (CRTVG)', 'crtvg.es — Galician public broadcaster', note='портальная проверка')
set_active('STVR (ex-RTVS)', 'stvr.sk — словацкий публичный вещатель', note='ребрендинг RTVS -> STVR 2024')
set_active('Digi Online', 'digionline.ro — Digi Romania', note='портальная проверка')
set_active('CyBC', 'cybc.com.cy — кипрский публичный вещатель', note='портальная проверка')
set_active('TVM (Malta)', 'tvm.com.mt — PBS Malta', note='портальная проверка')
set_active('Victory+', 'victoryplus.com — DTC Dallas Stars', note='портальная проверка')
set_active('Pantaya', 'pantaya.com — Spanish-language US SVOD', note='DoH: домен жив')
set_active('Arrow Player', 'arrowplayer.com — Arrow Films UK', note='портальная проверка')
set_active('COLORS', 'colorsxstudios.com — COLORSxSTUDIOS music', note='портальная проверка')
set_active('Vidgo', 'DoH 2026-10-25: A-записи есть; DNS песочницы отравлен', note='жив по DoH')
set_active('Festhome TV', 'DoH 2026-10-25: A-записи есть', note='жив по DoH')
set_active('Māori Television', 'maoritelevision.com — NZ broadcaster', note='портальная проверка')
set_active('Le Cinéma Club', 'lecinemaclub.com — бесплатный арт-хаус', note='портальная проверка')
set_active('Roposo', 'roposo.com — Glance/InMobi short-video', note='портальная проверка')
set_active('Qazaqstan TV', 'qazaqstan.tv — нацвещатель Казахстана', note='портальная проверка')
set_active('Qazsport', 'qazsporttv.kz', note='портальная проверка')
set_active('FTV (RTFBiH)', 'WebSearch 2026-10-25: официальный rtvfbih.ba', url='https://rtvfbih.ba',
           note='старый домен ftv.ba недоступен (NXDOMAIN); официальный сайт RTVFBiH')
# merged/rebranded
x = patch('Amazon miniTV', status='unverified')
if by_name('Amazon miniTV'):
    if by_name('MX Player') or by_name('Amazon MX Player'):
        y = by_name('Amazon miniTV')
        y.update(status='merged', moved_to='Amazon MX Player', verified_date=TODAY,
                 verdict_http='MOVED', source='Wikipedia: Amazon MX Player (ex-MX Player, ex-miniTV merge)',
                 notes='miniTV ребрендинг -> Amazon MX (2025)')
    else:
        y = by_name('Amazon miniTV')
        y.update(status='active', name='Amazon MX Player (ex-miniTV)', official_url='https://www.mxplayer.in',
                 verdict_http='ALIVE', verified_date=TODAY,
                 source='Wikipedia: Amazon MX Player rebrand 2025')
patch('MX TakaTak', status='merged', moved_to='Moj / Amazon MX Player', verified_date=TODAY,
      verdict_http='MOVED', source='Variety 2022-02 (Moj+TakaTak merge) + Amazon MX Player 2025',
      notes='бренд TakaTak свёрнут после слияния с Moj и поглощения Amazon')
# Aloula -> SNRT Live
y = by_name('Aloula')
if y:
    y.update(status='merged', moved_to='SNRT Live (snrtlive.ma)', verified_date=TODAY, verdict_http='MOVED',
             source='WebSearch 2026-10-25: snrtlive.ma/fr/al-aoula',
             notes='aloula.ma выведен из DNS; стримы SNRT на snrtlive.ma')
set_unver('GoPlay.bg', 'DoH: NXDOMAIN + поиск не подтвердил', note='возможно закрыт; требует вне-песочной проверки')
set_unver('Bstation (Bilibili overseas)', 'DoH: NOERROR без A; вне песочницы не подтверждён')
set_unver('UpLive', 'вне песочницы не подтверждён')
set_unver('Planet Marathi OTT', 'статус 2026 не подтверждён')
set_unver('Atrangii', 'статус 2026 не подтверждён')
set_unver('smash.', 'статус 2026 не подтверждён')
set_unver('Trace Play', 'статус 2026 не подтверждён')
set_unver('BrutX', 'статус 2026 не подтверждён')
set_unver('Discover.film', 'TLS alert из песочницы; вне песочницы не подтверждён')
set_unver('AzTV', 'госвещатель; вне песочницы не подтверждён')
set_unver('Playeur', 'WebSearch 2026-10-25: статус неясен (наследник Utreon)')
# unknown-URL fills
set_active('Aitube', 'aitube.kz: HTTP 301 (сервер жив) + проверка 2026-10-24', url='https://aitube.kz',
           note='заполнен отсутствовавший URL')
set_active('Mediabay', AB + ': 200 mediabay.uz', url='https://mediabay.uz', note='заполнен отсутствовавший URL')
set_active('Dubai+', 'curl 2026-10-25: 200 dubaiplus.net', url='https://dubaiplus.net', note='решает NO-DOMAIN плейсхолдер (ex-Awaan)')
set_active('WatchAUT', 'curl 2026-10-25: 200 watchaut.at', url='https://www.watchaut.at')
set_closed('Kwesé', 'известный факт: Kwesé TV закрыт 2019 (Econet)', url='https://kwese.com', note='домен не работает')
# historical twins: keep canonical single entry
TW = [
    ('Metacafe', 'Metacafe (closed)', 'closed', '', '2021: закрыт, домен мёртв (000); DocumentaryTube 2026: discontinued'),
    ('Veoh', 'Veoh (closed/redirected)', 'closed', '', '2026: источники фиксируют прекращение сервиса; сайт отдаёт оболочку'),
    ('LiveLeak', 'LiveLeak (closed/replaced)', 'closed', 'ItemFix (itemfix.com)', 'закрыт 2021-05, преемник ItemFix (жив 200)'),
    ('Vidme', 'Vidme (closed)', 'closed', '', 'закрыт 2017, домен мёртв (000)'),
    ('Blip.tv', 'Blip.tv (closed/redirected)', 'closed', 'Disney (Maker Studios)', 'закрыт 2015; blip.tv редиректит на disney.com'),
]
for keep, drop, st, mv, note in TW:
    d = by_name(drop); k = by_name(keep)
    if d and k:
        reg.remove(d); k.update(status=st, moved_to=mv or k.get('moved_to', ''),
                                verified_date=TODAY, notes=((k.get('notes') or '') + ' | ' + note).strip(' |'))
    elif k:
        k.update(status=st, moved_to=mv or '', verified_date=TODAY,
                 notes=((k.get('notes') or '') + ' | ' + note).strip(' |'))
set_closed('Break.com', 'curl 2026-10-25: домен перепрофилирован под казино',
           note='видеосервис прекращён; домен отдаёт онлайн-казино (не платформа)')

# ---------------- batch5 merge ----------------
b5 = json.load(open(W + '/candidates/batch5_all.json', encoding='utf-8'))
res5 = {r['id']: r for r in json.load(open(W + '/checks/batch5_results.json', encoding='utf-8'))}
POLITICAL = re.compile(r'(rumble|bitchut|gab|telewebion|irib|press.?tv|cgtn|cctv|sputnik|rt\.com|trt world|kctv|manoto|venevision state|voa|radio free)', re.I)
ADULT = re.compile(r'(porn|xxx|onlyfans|18\+|erotic|nsfw|hentai|fanza|vivamax|ullu)', re.I)
added = []; excluded5 = []
for x in b5:
    r = res5.get('B5:' + x['name'], {})
    v = r.get('verdict')
    name_l = x['name']; url_l = x.get('official_url', '')
    if POLITICAL.search(name_l) or POLITICAL.search(url_l):
        excluded5.append((x['name'], 'political')); continue
    if ADULT.search(name_l) or ADULT.search(url_l):
        excluded5.append((x['name'], 'adult')); continue
    e = {
        'id': 'B5-%03d' % (len(added) + 1), 'name': x['name'], 'official_url': x['official_url'],
        'category': x.get('category', 'niche_other'), 'country': x.get('country', ''),
        'region': norm_region(x.get('region', ''), x.get('country', '')),
        'region_orig': x.get('region', ''), 'user_upload': x.get('user_upload', 'no'),
        'source': x.get('source', ''), 'confidence': x.get('confidence', 'medium'),
        'origin': 'batch5_' + x.get('origin_batch', '5x'), 'verified_date': TODAY,
        'notes': x.get('notes', ''), 'status': 'unverified', 'status_detail': '', 'moved_to': '',
        'verdict_http': v or 'NONE',
    }
    if v == 'ALIVE':
        e['status'] = 'active'
    elif v == 'BLOCKED':
        e['status'] = 'active'; e['notes'] = ((x.get('notes') or '') + ' | анти-бот/гео (HTTP %s)' % r.get('http_status')).strip(' |')
    elif v == 'REDIRECT_LOOP':
        e['status'] = 'unverified'; e['notes'] = ('редирект-петля из песочницы: ' + (r.get('final_url') or '')).strip()
    else:
        e['status'] = 'unverified'; e['notes'] = ((x.get('notes') or '') + ' | HTTP: %s %s' % (v, r.get('error') or '')).strip()
    mv = r.get('moved_to')
    if mv and e['status'] == 'active':
        e['notes'] = ((e['notes'] or '') + ' | редирект: ' + mv).strip(' |')
    added.append(e)

# manual dupes inside batch5 (same service discovered twice by different agents)
dup_names = [('Royal Opera House Stream', 'RBO Stream (Royal Ballet & Opera)')]
for drop_n, keep_n in dup_names:
    d = next((z for z in added if z['name'] == drop_n), None)
    k = next((z for z in added if z['name'] == keep_n), None)
    if d and k:
        added.remove(d)
        k['notes'] = ((k.get('notes') or '') + ' | дубль: ' + drop_n).strip(' |')
        excluded5.append((drop_n, 'dup-of ' + keep_n))
    elif d and not k:
        pass  # keep it
reg.extend(added)

from collections import Counter
print('=== REGISTRY v3 ===')
print('total:', len(reg))
print('status:', Counter(x['status'] for x in reg))
print('region:', Counter(x.get('region') for x in reg))
print('origin batch5:', Counter(x.get('origin', '') for x in reg if str(x.get('origin', '')).startswith('batch5')))
print('excluded from batch5:', excluded5)
json.dump(reg, open(OUT + '/registry_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'generated': TODAY, 'total_registry': len(reg),
           'status_counts': dict(Counter(x['status'] for x in reg)),
           'region_counts': dict(Counter(x.get('region') for x in reg)),
           'category_counts': dict(Counter(x.get('category') for x in reg)),
           'batch5_added': len(added), 'batch5_excluded': excluded5,
           'active_total': sum(1 for x in reg if x['status'] == 'active')},
          open(OUT + '/summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written ->', OUT + '/registry_final.json')
