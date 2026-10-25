#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_candidates.py — merge base registry (451) + sub-agent candidates (419).
Dedupe by registrable domain and normalized name. Apply content policy filter:
EXCLUDE political/propaganda platforms and adult/porn platforms (user directive).
Outputs to /home/z/my-project/registry_work/merged/:
  new_candidates.json  — unique, filtered, ids 1001+, ready for HTTP check
  dupes.json           — candidates dropped as duplicates of base
  excluded.json        — entries excluded by content policy (with reason)
  internal_dupes.json  — duplicates between candidate files
  summary.txt          — human-readable counts
"""
import json, os, re, unicodedata
from urllib.parse import urlparse

WORK = '/home/z/my-project/registry_work'
OUT = os.path.join(WORK, 'merged')
os.makedirs(OUT, exist_ok=True)

# ---------- registrable domain ----------
TWO_PART = {
 'co.uk','org.uk','ac.uk','gov.uk','co.jp','com.au','net.au','org.au','co.nz','org.nz',
 'co.kr','or.kr','ne.jp','ac.jp','co.in','net.in','org.in','com.br','com.mx','com.ar',
 'com.co','com.pe','com.ve','com.uy','com.py','com.bo','com.ec','com.do','com.gt',
 'com.tr','com.eg','com.sa','com.ae','com.qa','com.kw','com.bh','com.om','com.jo',
 'com.lb','com.sy','com.ye','com.pk','com.bd','com.lk','com.np','com.my','com.sg',
 'com.hk','com.tw','com.vn','com.ph','com.id','com.th','co.za','org.za','com.ng',
 'com.gh','co.ke','com.tz','com.et','com.ua','net.ua','org.ua','co.il','org.il',
 'com.kz','org.kz','net.kz','co.kr','com.cn','net.cn','org.cn','gov.cn','edu.cn',
 'com.ru','net.ru','org.ru','co.id','or.id','web.id','co.th','or.th','in.th',
 'com.pl','net.pl','org.pl','com.pt','com.es','com.gr','com.cy','com.mt','com.ro',
 'com.md','com.ge','com.am','com.az','co.hu','org.hu','co.at','or.at','co.ch',
 'co.dk','co.no','co.se','co.fi','co.il','com.mx','gob.mx','edu.mx'
}
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

def norm_name(n):
    n = unicodedata.normalize('NFKD', n or '')
    n = re.sub(r'[^\w\s]', '', n.lower())
    return re.sub(r'\s+', ' ', n).strip()

# ---------- content policy: EXCLUDE politics & porn ----------
POLITICAL_DOMAINS = {
 'rt.com','russia.tv','rtd.rt.com','sputniknews.com','sputnikglobe.com','svpressa.ru',
 'presstv.ir','hispantv.com','almayadeen.net','alalam.ir','irib.ir','telewebion.com',
 'manototv.com','manoto1.com','ntd.com','ntdtv.com','epochtimes.com','epochtv.com',
 'ganjingworld.com','cgtn.com','cctv.com','cntv.cn','tvp.info','tvpworld.com',
 'trtworld.com','trt.net.tr','belsat.eu','oann.com','newsmax.com','foxnation.com',
 'dailywire.com','blazetv.com','prageru.com','thefederalist.com','breitbart.com',
 'infowars.com','banned.video','rumble.com','gab.com','getter.com','parler.com',
 'bitchute.com','odysee.com','brighteon.com','sonar21.com','thegrayzone.com',
 'mintpressnews.com','thecradle.co','unz.com','vdare.com','amren.com',
 'espreso.tv','hromadske.ua','24tv.ua','pravda.com.ua','censor.net','obozrevatel.com',
 'strana.ua','ukraina.ru','vz.ru','kp.ru','lenta.ru','gazeta.ru','aif.ru','riafan.ru',
 'eadaily.com','regnum.ru','ng.ru','kommersant.ru','theduran.com','durtytruths.com',
 'concerned.app','frontpagemag.com','jihadwatch.org','gatesofvienna.net',
 'bollywoodhungama.com','nation.com.pk','thenews.com.pk','jang.com.pk',
 'bangla.polphoto.net','deepstatemap.live','war Monitor',
}
POLITICAL_NAME_RX = re.compile(
 r'\b(russia today|rt russia|sputnik|press ?tv|hispantv|al-?mayadeen|al ?alam|'
 r'ntd ?(tv|televisión)?|epoch ?(times|tv)|ganjing|cgtn|cctv|tvp ?world|'
 r'trt ?world|belsat|oann|one america|newsmax|fox nation|daily wire|dailywire|'
 r'blaze ?tv|prageru|breitbart|infowars|banned\.video|bitchute|gab |parler|'
 r'brighteon|odysee|propaganda|politic|election|kremlin|zvezda|tv ?zvezda|'
 r'(spas|союз).*orthodox|politics)\b', re.I)
# NOTE: Odysee/Rumble/Bitchute/Parler/Gab are included deliberately: mostly
# political-content-first platforms per user directive "ИСКЛЮЧИ ПОЛИТИКУ".

ADULT_DOMAINS = {
 'pornhub.com','xvideos.com','xhamster.com','xnxx.com','onlyfans.com','fansly.com',
 'brazzers.com','chaturbate.com','stripchat.com','bongacams.com','cam4.com',
 'youporn.com','redtube.com','txxx.com','spankbang.com','beeg.com','eporner.com',
 'hclips.com','porntrex.com','iwank.tv','fapello.com','upornia.com','hotmovs.com',
 'togafiti.com','thumbzilla.com','motherless.com','4chan.org','8kun.top','8chan.moe',
 'thesauce.io','erocast','vivid.com','playboy.com','hustler.com','fleshlight.com',
 'faphouse.com','camwhores.tv','jav.guru','javhd.com','hanime.tv','hentaihaven.xxx',
 'kimochi.info','rule34video.com','pornone.com','analdin.com','spankwire.com',
 'empflix.com','tnaflix.com','deviants.com','light.xyz','adultswim.com',
}
ADULT_NAME_RX = re.compile(
 r'\b(porn|xxx|adult|sex|erotic|hentai|fap|cam ?girl|strip|nude|nsfw|'
 r'playboy|hustler|bondage|fetish|swinger|escort)\w*\b', re.I)
# NOTE adultswim.com is Cartoon Network's adult block — legit! Remove it.
ADULT_DOMAINS.discard('adultswim.com')

def classify_content(name, url):
    d = registrable(url)
    if d in POLITICAL_DOMAINS or any(d.endswith('.' + x) for x in POLITICAL_DOMAINS):
        return 'excluded_political'
    if d in ADULT_DOMAINS or any(d.endswith('.' + x) for x in ADULT_DOMAINS):
        return 'excluded_adult'
    if POLITICAL_NAME_RX.search(name or ''):
        return 'excluded_political'
    if ADULT_NAME_RX.search(name or ''):
        return 'excluded_adult'
    return None

# ---------- load base ----------
BASE_DIR = os.path.join(WORK, 'extracted/global_video_platforms_research_RU')
base = json.load(open(os.path.join(BASE_DIR, 'register.json'), encoding='utf-8'))
base_results = json.load(open(os.path.join(WORK, 'checks/base_results.json'), encoding='utf-8'))
res_by_id = {r['id']: r for r in base_results}

base_hosts, base_reg_names, base_names = {}, {}, {}
for b in base:
    hh = host_of(b.get('official_url') or '')
    if hh: base_hosts.setdefault(hh, []).append(b)
    rd = registrable(b.get('official_url') or '')
    nm = norm_name(b.get('name'))
    if rd and nm: base_reg_names.setdefault((rd, nm), []).append(b)
    if nm: base_names.setdefault(nm, []).append(b)

# ---------- load candidates ----------
cand_files = ['3b_europe.json','3c_asia.json','3d_americas.json','3e_africa_mea.json','3f_niche.json','3g_supplement.json','3h_batch3.json']
seen_cand_host, seen_cand_regname, seen_cand_name = {}, {}, {}
internal_dupes, excluded, new_rows = [], [], []
cid = 1000
for cf in cand_files:
    arr = json.load(open(os.path.join(WORK, 'candidates', cf), encoding='utf-8'))
    for c in arr:
        rec = {
            'name': (c.get('name') or '').strip(),
            'official_url': (c.get('official_url') or '').strip(),
            'region': c.get('region') or 'Global',
            'country': c.get('country') or '',
            'category': c.get('category') or 'vod_subscription',
            'user_upload': c.get('user_upload') or 'no',
            'source': c.get('source') or '',
            'confidence': c.get('confidence') or 'medium',
            'candidate_file': cf,
        }
        if not rec['name'] or not rec['official_url']:
            continue
        d = registrable(rec['official_url'])
        hh = host_of(rec['official_url'])
        nm = norm_name(rec['name'])
        pol = classify_content(rec['name'], rec['official_url'])
        if pol:
            rec['exclusion_reason'] = pol
            excluded.append(rec); continue
        # dupes vs base: exact host first, then registrable+name, then name
        if hh and hh in base_hosts:
            rec['duplicate_of'] = base_hosts[hh][0]['name'] + ' (base #%s)' % base_hosts[hh][0]['id']
            rec['dup_type'] = 'host_vs_base'; internal_dupes.append(rec)
            continue
        if (d, nm) in base_reg_names:
            m = base_reg_names[(d, nm)][0]
            rec['duplicate_of'] = m['name'] + ' (base #%s)' % m['id']
            rec['dup_type'] = 'regname_vs_base'; internal_dupes.append(rec)
            continue
        if nm and nm in base_names:
            rec['duplicate_of'] = base_names[nm][0]['name'] + ' (base #%s)' % base_names[nm][0]['id']
            rec['dup_type'] = 'name_vs_base'; internal_dupes.append(rec)
            continue
        # dupes within candidates
        if hh and hh in seen_cand_host:
            rec['duplicate_of'] = seen_cand_host[hh]
            rec['dup_type'] = 'host_vs_cand'; internal_dupes.append(rec)
            continue
        if (d, nm) in seen_cand_regname:
            rec['duplicate_of'] = seen_cand_regname[(d, nm)]
            rec['dup_type'] = 'regname_vs_cand'; internal_dupes.append(rec)
            continue
        if nm and nm in seen_cand_name:
            rec['duplicate_of'] = seen_cand_name[nm]
            rec['dup_type'] = 'name_vs_cand'; internal_dupes.append(rec)
            continue
        cid += 1
        rec['id'] = cid
        seen_cand_host[hh] = rec['name']
        seen_cand_regname[(d, nm)] = rec['name']
        seen_cand_name[nm] = rec['name']
        new_rows.append(rec)

# ---------- base-level content policy scan ----------
base_excluded = []
for b in base:
    pol = classify_content(b.get('name'), b.get('official_url') or '')
    if pol:
        bb = dict(b); bb['exclusion_reason'] = pol
        base_excluded.append(bb)

# ---------- write ----------
json.dump(new_rows, open(os.path.join(OUT, 'new_candidates.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(excluded, open(os.path.join(OUT, 'excluded_candidates.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(base_excluded, open(os.path.join(OUT, 'excluded_base.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(internal_dupes, open(os.path.join(OUT, 'dupes.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

lines = [
 'base=%d  new_unique=%d  cand_excluded=%d  base_excluded=%d  dupes_dropped=%d'
 % (len(base), len(new_rows), len(excluded), len(base_excluded), len(internal_dupes)),
 'PROJECTED TOTAL = base(%d) - base_excluded(%d) + new(%d) = %d'
 % (len(base), len(base_excluded), len(new_rows),
    len(base) - len(base_excluded) + len(new_rows)),
 '', 'Excluded candidates:', ' POLITICAL:', '  ' + ', '.join(sorted({e['name'] for e in excluded if e['exclusion_reason']=='excluded_political'})),
 ' ADULT:', '  ' + ', '.join(sorted({e['name'] for e in excluded if e['exclusion_reason']=='excluded_adult'})),
 '', 'Excluded base entries:', '  ' + '; '.join('%s [%s]' % (b['name'], b['exclusion_reason'].replace('excluded_','')) for b in base_excluded),
 '', 'Dupes dropped (first 60):',
 '  ' + '; '.join('%s->%s' % (x['name'], x.get('duplicate_of','?')) for x in internal_dupes[:60]),
]
open(os.path.join(OUT, 'summary.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
