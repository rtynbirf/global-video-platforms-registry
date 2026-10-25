#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_registry.py — final assembly of the verified global video-platform
registry. Joins:
  base register (451) + base HTTP results
  468 new unique candidates + new HTTP results + retry + batch3 + DoH/web notes
Applies: content policy (political/adult excluded), known merges/rebrands,
status normalization, region normalization. Outputs registry_work/final/*.json
"""
import json, os, re, unicodedata
from datetime import date
from urllib.parse import urlparse

W = '/home/z/my-project/registry_work'
OUT = os.path.join(W, 'final')
os.makedirs(OUT, exist_ok=True)
TODAY = '2026-10-24'

# ---------- helpers (same as merge script) ----------
TWO_PART = {'co.uk','org.uk','ac.uk','gov.uk','co.jp','com.au','net.au','org.au',
 'co.nz','org.nz','co.kr','or.kr','ne.jp','ac.jp','co.in','net.in','org.in',
 'com.br','com.mx','com.ar','com.co','com.pe','com.ve','com.uy','com.py','com.bo',
 'com.ec','com.do','com.gt','com.tr','com.eg','com.sa','com.ae','com.qa','com.kw',
 'com.bh','com.om','com.jo','com.lb','com.pk','com.bd','com.lk','com.np','com.my',
 'com.sg','com.hk','com.tw','com.vn','com.ph','com.id','com.th','co.za','org.za',
 'com.ng','com.gh','co.ke','com.tz','com.et','com.ua','net.ua','org.ua','co.il',
 'org.il','com.kz','org.kz','net.kz','com.cn','net.cn','org.cn','com.ru','net.ru',
 'org.ru','co.id','or.id','web.id','co.th','or.th','in.th','com.pl','net.pl',
 'org.pl','com.pt','com.es','com.gr','com.cy','com.mt','com.ro','com.md','com.ge',
 'com.am','com.az','co.hu','org.hu','co.at','or.at','co.ch','co.dk','co.no','co.se','co.fi'}

def registrable(url):
    try:
        h = urlparse(url if re.match(r'^https?://', url or '', re.I) else 'https://' + (url or '')).netloc.lower()
    except Exception:
        return (url or '').lower()
    h = h.split('@')[-1].split(':')[0]
    if h.startswith('www.'): h = h[4:]
    parts = h.split('.')
    if len(parts) >= 3 and ('.'.join(parts[-2:])) in TWO_PART:
        return '.'.join(parts[-3:])
    return '.'.join(parts[-2:]) if len(parts) >= 2 else h

def host_of(url):
    try:
        h = urlparse(url if re.match(r'^https?://', url or '', re.I) else 'https://' + (url or '')).netloc.lower()
    except Exception:
        return (url or '').lower()
    return h.split('@')[-1].split(':')[0].replace('www.', '', 1) if h else ''

COUNTRY_TO_REGION = {
 'china':'Asia','japan':'Asia','south korea':'Asia','korea':'Asia','india':'Asia',
 'philippines':'Asia','singapore':'Asia','indonesia':'Asia','vietnam':'Asia',
 'malaysia':'Asia','pakistan':'Asia','bangladesh':'Asia','nepal':'Asia','thailand':'Asia',
 'kazakhstan':'Asia','uzbekistan':'Asia','azerbaijan':'Asia','iran':'Asia','turkey':'Asia',
 'hong kong':'Asia','us':'North America','usa':'North America','united states':'North America',
 'uk':'Europe','united kingdom':'Europe','germany':'Europe','spain':'Europe','poland':'Europe',
 'bulgaria':'Europe','hungary':'Europe','czechia':'Europe','austria':'Europe','slovakia':'Europe',
 'serbia':'Europe','croatia':'Europe','slovenia':'Europe','montenegro':'Europe','italy':'Europe',
 'portugal':'Europe','switzerland':'Europe','france':'Europe','belgium':'Europe',
 'netherlands':'Europe','denmark':'Europe','sweden':'Europe','norway':'Europe','finland':'Europe',
 'catalonia':'Europe','brazil':'Latin America','argentina':'Latin America','colombia':'Latin America',
 'uruguay':'Latin America','peru':'Latin America','venezuela':'Latin America','mexico':'Latin America',
 'egypt':'Middle East','jordan':'Middle East','uae':'Middle East','mena':'Middle East',
 'nigeria':'Africa','kenya':'Africa','south africa':'Africa','morocco':'Africa',
 'israel':'Middle East','qatar':'Middle East','russia':'CIS','canada':'North America','spanish-speaking markets':'Global',
}
def norm_region(r, c=''):
    r0 = (r or '').strip(); r = r0.lower(); c = (c or '').lower()
    if 'europe' in r: return 'Europe'
    if 'north america' in r: return 'North America'
    if 'latin' in r: return 'Latin America'
    if 'africa' in r: return 'Africa'
    if 'middle east' in r: return 'Middle East'
    if 'asia' in r: return 'Asia'
    if 'oceania' in r or 'australia' in r or 'new zealand' in c: return 'Oceania'
    if 'cis' in r or 'russia' in r: return 'CIS'
    if 'global' in r or 'world' in r or 'multi' in r: return 'Global'
    for k, v in COUNTRY_TO_REGION.items():
        if r == k or r.startswith(k + '/') or r.startswith(k + ' ') or c.startswith(k):
            return v
    if 'historical' in r: return 'Historical'
    if 'self-hosted' in r: return 'Self-Hosted'
    if 'selected markets' in r: return 'Global'
    return r0.title() if r0 else 'Global'

# ---------- known merges / rebrands / closures (verified externally) ----------
MERGES = {
 # base-id or name-key -> (target, note_ru)
 'hulu': ('Disney+', 'Hulu интегрирован в Disney+ (междунар. rollout 2024-2026)'),
 'bet+': ('Paramount+', 'BET+ присоединён к Paramount+ (2026)'),
 'awaan': ('Dubai+', 'Awaan перезапущен как Dubai+ (Dubai Media Inc)'),
 'mitele': ('Mediaset Infinity', 'Mitele переименован в Mediaset Infinity'),
 'd anime store': ('Lemino', 'd Anime Store перезапущен как Lemino (docomo)'),
 'jiocinema': ('JioHotstar', 'JioCinema слит с JioHotstar (2025)'),
 'iflix': ('WeTV', 'iflix свёрнут в WeTV (Tencent)'),
 'blutv': ('Max', 'BluTV закрыт и поглощён Max (апрель 2025)'),
 'trt izle': ('tabii', 'TRT İzle слит с tabii (дек. 2023)'),
 'amazon freevee': ('Prime Video', 'Freevee закрыт, контент в Prime Video (2024)'),
 'wwe network': ('Peacock / Netflix', 'WWE Network: Peacock (США) / Netflix (мир)'),
 'vix+': ('ViX', 'Vix+ слит с ViX'),
 'starzplay': ('Starz On (Lionsgate+)', 'MENA-бренд StarzPlay переведён под Lionsgate+'),
 'paravi': ('U-NEXT', 'Paravi слит с U-NEXT (2023)'),
 'gyao': ('TVer', 'GYAO! закрыт, контент перенесён в TVer (2024)'),
 'myvideo (tw)': ('DEAD (domain squatted)', 'myvideo.com.tw перехвачен под казино'),
 'anime onegai': ('CLOSED', 'Anime Onegai закрыт (окт. 2025, tavilatam.com)'),
 'ocs': ('Canal+', 'OCS поглощён Canal+ (2025)'),
 'salto': ('CLOSED', 'Salto закрыт (2023)'),
 'viafree': ('TV4 Play / discovery+', 'Viafree свёрнут'),
 'stod2': ('Sýn', 'Stöð 2 перешёл под бренд Sýn (HTTP redirect)'),
 'playplus': ('RecordPlus', 'PlayPlus перезапущен как RecordPlus (HTTP redirect)'),
 'kinonow': ('Kino Film Collection', 'Kino Now переименован в Kino Film Collection'),
 'fite': ('TrillerTV', 'FITE переименован в TrillerTV'),
 'contv': ('Midnight Pulp', 'ConTV свёрнут в Midnight Pulp'),
 'wondrium': ('The Great Courses Plus', 'Wondrium вернулся к бренду The Great Courses'),
 'noovo': ('Crave', 'noovo.ca редиректит на Crave (Bell)'),
 'lifetimemovieclub': ('A+E Networks', 'Lifetime Movie Club: редирект на aenetworks'),
 'tennischannel': ('Tennis.com', 'Tennis Channel редиректит на tennis.com'),
 'motorsport.tv': ('Motorsport.com', 'motorsport.tv переведён на motorsport.com'),
 'line tv': ('CLOSED', 'LINE TV прекратил сервис (Таиланд, 2024-2025)'),
 'wasd.tv': ('CLOSED', 'WASD.tv закрыт (VK Play поглотил аудиторию)'),
 'filmatique': ('UNVERIFIED_DEAD', 'домен не резолвится публично (NXDOMAIN)'),
 'toffee': ('UNVERIFIED_DEAD', 'домен не резолвится публично (NXDOMAIN)'),
 'anime times': ('UNVERIFIED_DEAD', 'домен не резолвится публично (NXDOMAIN)'),
 'aloula': ('UNVERIFIED', 'домен не резолвится из песочницы; сервис SNRT, вероятно, сменил URL'),
 'goplay.bg': ('UNVERIFIED', 'домен не резолвится из песочницы'),
 'ftv (rtfbih)': ('UNVERIFIED', 'домен не резолвится из песочницы'),
 'mola': ('UNVERIFIED', 'домен не резолвится из песочницы'),
 'mx takatak': ('UNVERIFIED', 'домен не резолвится из песочницы'),
 'uplive': ('UNVERIFIED', 'домен не резолвится из песочницы'),
 'bstation (bilibili overseas)': ('UNVERIFIED', 'домен не резолвится из песочницы'),
 'pilipinas live': ('UNVERIFIED', 'домен не резолвится из песочницы'),
 'rugbypass tv': ('UNVERIFIED', 'HTTP 404 на /en; статус неясен'),
 'distrotv': ('active', 'DNS резолвится; вердикт PARKED сочтён ложным срабатыванием'),
 'j:com stream': ('active', 'подтверждён через jcom.co.jp и Google Play (100K+), окт. 2026'),
 'wrestle universe': ('active', 'подтверждён через Google Play (обновл. окт. 2026)'),
 'sooner': ('active', 'подтверждён на sooner.de (домен sooner.club больше не используется)'),
 'wrestle-universe': ('active', 'подтверждён через Google Play'),
}
def merge_key(name):
    k = re.sub(r'\s+', ' ', (name or '').lower()).strip()
    return k

# ---------- content policy sets (mirror of merge script) ----------
import importlib.util
spec = importlib.util.spec_from_file_location('mc', '/home/z/my-project/scripts/merge_candidates.py')
# We don't execute merge script (it would re-run); replicate only the filter:
POLITICAL_DOMAINS = {'rt.com','russia.tv','sputniknews.com','sputnikglobe.com','presstv.ir',
 'hispantv.com','almayadeen.net','alalam.ir','irib.ir','telewebion.com','manototv.com',
 'ntd.com','ntdtv.com','epochtimes.com','epochtv.com','ganjingworld.com','cgtn.com',
 'cctv.com','cntv.cn','tvp.info','tvpworld.com','trtworld.com','trt.net.tr','belsat.eu',
 'oann.com','newsmax.com','foxnation.com','dailywire.com','blazetv.com','prageru.com',
 'breitbart.com','infowars.com','banned.video','gab.com','parler.com','bitchute.com',
 'odysee.com','brighteon.com','espreso.tv','hromadske.ua','24tv.ua','pravda.com.ua',
 'censor.net','obozrevatel.com','strana.ua','ukraina.ru','rumble.com'}
ADULT_DOMAINS = {'pornhub.com','xvideos.com','xhamster.com','xnxx.com','onlyfans.com',
 'fansly.com','brazzers.com','chaturbate.com','stripchat.com','bongacams.com','youporn.com',
 'redtube.com','txxx.com','spankbang.com','beeg.com','eporner.com','hclips.com',
 'porntrex.com','fapello.com','upornia.com','hotmovs.com','camwhores.tv','jav.guru',
 'hanime.tv','rule34video.com','vivamax','ullu','fanza'}

def policy_exclusion(name, url):
    d = registrable(url)
    if d in POLITICAL_DOMAINS: return 'excluded_political'
    if d in ADULT_DOMAINS: return 'excluded_adult'
    n = (name or '').lower()
    if any(x in n for x in ('rumble','odysee','bitchute','brighteon','gab ','gan jing')): return 'excluded_political'
    if any(x in n for x in ('pornhub','xvideos','xhamster','onlyfans','vivamax','ullu')): return 'excluded_adult'
    return None

# ---------- load everything ----------
base = json.load(open(W + '/extracted/global_video_platforms_research_RU/register.json', encoding='utf-8'))
base_res = {r['id']: r for r in json.load(open(W + '/checks/base_results.json', encoding='utf-8'))}
new_c = json.load(open(W + '/merged/new_candidates.json', encoding='utf-8'))
new_res = {r['id']: r for r in json.load(open(W + '/checks/new_results.json', encoding='utf-8'))}
retry_res = {r['name']: r for r in json.load(open(W + '/checks/retry_results.json', encoding='utf-8'))}
b3_res = {r['id']: r for r in json.load(open(W + '/checks/batch3_results.json', encoding='utf-8'))}

# ---------- build records ----------
records = []

# BASE 451
for b in base:
    pol = policy_exclusion(b.get('name'), b.get('official_url') or '')
    if pol:
        continue  # excluded entirely; counted separately
    r = base_res.get(b['id'], {})
    verdict = r.get('verdict', 'UNVERIFIED')
    moved = r.get('moved_to', '') or ''
    note_parts = []
    status, sub = None, ''
    mk = merge_key(b['name'])
    if mk in MERGES:
        target, mnote = MERGES[mk]
        if target == 'active':
            status = 'active'; note_parts.append(mnote)
        elif target in ('UNVERIFIED', 'UNVERIFIED_DEAD'):
            status = 'unverified' if target == 'UNVERIFIED' else 'unverified_dead'
            note_parts.append(mnote)
        elif target in ('CLOSED', 'DEAD (domain squatted)'):
            status = 'closed'; note_parts.append(mnote)
        else:
            status = 'merged'; note_parts.append('%s: %s' % (target, mnote)); sub = target
    if status is None:
        if verdict == 'ALIVE':
            status = 'active'
            if moved and registrable(moved) != registrable(b.get('official_url') or ''):
                note_parts.append('HTTP-редирект на %s' % moved)
        elif verdict == 'BLOCKED':
            status = 'active'; sub = 'antibot'
            note_parts.append('Жив, отдаёт анти-бот страницу (%s)' % r.get('http_status'))
        elif verdict == 'PARKED':
            status = 'parked'; note_parts.append('Домен показывает паркованную страницу')
        elif verdict in ('NOT_FOUND', 'CLIENT_ERR', 'SERVER_ERR', 'REDIRECT_LOOP', 'BAD_URL'):
            status = 'unverified'; note_parts.append('HTTP %s' % verdict)
        else:
            status = 'unverified'; note_parts.append('Сеть/ DNS из песочницы: %s' % (r.get('error') or verdict))
    # historical flag from base
    base_note = (b.get('status_note') or '')
    if 'istor' in base_note.lower() or 'Historical' in base_note or 'closed' in base_note.lower():
        if status == 'active':
            note_parts.append('База помечала как исторический — перепроверить')
    records.append({
        'id': b['id'], 'name': b['name'], 'official_url': b.get('official_url') or '',
        'region': norm_region(b.get('region'), b.get('region')),
        'region_orig': b.get('region'), 'country': '', 'category': b.get('category') or '',
        'user_upload': 'yes' if str(b.get('public_user_upload_confirmed', '')).lower() in ('yes','true','1') else 'no',
        'status': status, 'status_detail': sub, 'verdict_http': verdict,
        'moved_to': moved, 'notes': '; '.join(note_parts), 'verified_date': TODAY,
        'source': 'user archive register v1', 'confidence': b.get('confidence') or '',
        'origin': 'base_451',
    })

# NEW candidates
for c in new_c:
    r = new_res.get(c['id']) or b3_res.get(c['id']) or {}
    retry = retry_res.get(c['name'])
    if retry and retry.get('verdict') in ('ALIVE', 'BLOCKED') and r.get('verdict') in ('DNS_FAIL', 'TIMEOUT', 'UNREACHABLE', None):
        r = retry
    verdict = r.get('verdict', 'UNVERIFIED')
    moved = r.get('moved_to', '') or ''
    mk = merge_key(c['name'])
    note_parts, status, sub = [], None, ''
    if mk in MERGES:
        target, mnote = MERGES[mk]
        if target == 'active':
            status = 'active'; note_parts.append(mnote)
        elif target in ('UNVERIFIED', 'UNVERIFIED_DEAD'):
            status = 'unverified' if target == 'UNVERIFIED' else 'unverified_dead'
            note_parts.append(mnote)
        elif target in ('CLOSED', 'DEAD (domain squatted)'):
            status = 'closed'; note_parts.append(mnote)
        else:
            status = 'merged'; note_parts.append('%s: %s' % (target, mnote)); sub = target
    if status is None:
        if verdict == 'ALIVE':
            status = 'active'
            if moved and registrable(moved) != registrable(c['official_url']):
                note_parts.append('HTTP-редирект на %s' % moved)
        elif verdict == 'BLOCKED':
            status = 'active'; sub = 'antibot'
            note_parts.append('Жив, отдаёт анти-бот страницу (%s)' % r.get('http_status'))
        elif verdict == 'PARKED':
            status = 'parked'; note_parts.append('Домен показывает паркованную страницу')
        elif verdict in ('NOT_FOUND', 'CLIENT_ERR', 'SERVER_ERR', 'REDIRECT_LOOP', 'BAD_URL'):
            status = 'unverified'; note_parts.append('HTTP %s' % verdict)
        else:
            status = 'unverified'; note_parts.append('Сеть/DNS из песочницы: %s' % (r.get('error') or verdict))
    records.append({
        'id': c['id'], 'name': c['name'], 'official_url': c['official_url'],
        'region': norm_region(c.get('region'), c.get('country')),
        'region_orig': c.get('region'), 'country': c.get('country') or '',
        'category': c.get('category') or '', 'user_upload': c.get('user_upload') or 'no',
        'status': status, 'status_detail': sub, 'verdict_http': verdict,
        'moved_to': moved, 'notes': '; '.join(note_parts), 'verified_date': TODAY,
        'source': c.get('source') or '', 'confidence': c.get('confidence') or '',
        'origin': c.get('candidate_file', 'candidates'),
    })

# ---------- excluded list ----------
excluded_all = []
excluded_all += json.load(open(W + '/merged/excluded_base.json', encoding='utf-8'))
excluded_all += json.load(open(W + '/merged/excluded_candidates.json', encoding='utf-8'))

# ---------- stats ----------
from collections import Counter
st = Counter(x['status'] for x in records)
reg = Counter(x['region'] for x in records)
cat = Counter(x['category'] for x in records)
orig = Counter(x['origin'] for x in records)
print('TOTAL records:', len(records))
print('STATUS:', dict(st))
print('REGION:', dict(reg))
print('ORIGIN:', dict(orig))
active = st.get('active', 0)
print('ACTIVE (incl. antibot):', active)

summary = {
    'generated': TODAY,
    'total_registry': len(records),
    'status_counts': dict(st),
    'active_total': active,
    'region_counts': dict(reg),
    'category_counts': dict(cat.most_common(30)),
    'origin_counts': dict(orig),
    'excluded_policy': [{'name': e.get('name'), 'reason': e.get('exclusion_reason')} for e in excluded_all],
    'content_policy': 'Политические/пропагандистские и adult-платформы исключены по требованию заказчика',
}
json.dump(summary, open(OUT + '/summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(records, open(OUT + '/registry_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(excluded_all, open(OUT + '/excluded_policy.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written ->', OUT)
