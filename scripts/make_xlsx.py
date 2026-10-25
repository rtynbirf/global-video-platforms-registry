#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_xlsx.py — registry_final.xlsx per xlsx-skill design system.
Sheets: Сводка / Реестр / Исключённые / Методология. Russian UI."""
import json, sys, os
XLSX_SKILL_DIR = '/home/z/my-project/skills/xlsx'
for sub in [XLSX_SKILL_DIR, os.path.join(XLSX_SKILL_DIR, 'templates')]:
    if sub not in sys.path:
        sys.path.insert(0, sub)
from base import *  # design tokens + helpers
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

W = '/home/z/my-project/registry_work'
records = json.load(open(W + '/final/registry_final.json', encoding='utf-8'))
summary = json.load(open(W + '/final/summary.json', encoding='utf-8'))
excluded = json.load(open(W + '/final/excluded_policy.json', encoding='utf-8'))

STATUS_RU = {
 'active': 'активен', 'unverified': 'не верифицирован', 'merged': 'слияние/ребрендинг',
 'closed': 'закрыт', 'parked': 'парковка домена', 'unverified_dead': 'вероятно закрыт',
}
CAT_RU_SHORT = {}  # keep English category slugs (machine-readable per user request)

def style_status_cell(cell, status, sub):
    if status == 'active' and sub != 'antibot':
        cell.font = Font(name=FONT_NAME, size=11, color=ACCENT_POSITIVE)
    elif status == 'active' and sub == 'antibot':
        cell.font = Font(name=FONT_NAME, size=11, color=ACCENT_POSITIVE)
    elif status in ('closed', 'unverified_dead', 'parked'):
        cell.font = Font(name=FONT_NAME, size=11, color=ACCENT_NEGATIVE)
    elif status in ('unverified', 'merged'):
        cell.font = Font(name=FONT_NAME, size=11, color=ACCENT_WARNING)

wb = Workbook()

# ============ Sheet 1: Сводка ============
ws = wb.active
ws.title = 'Сводка'
last_col = 4
setup_sheet(ws, title='Глобальный реестр видеоплатформ — сводка верификации', last_col=last_col)
ws['B3'] = 'Дата проверки: %s · HTTP-проверка всех URL из песочницы + WebSearch/DoH-кросс-проверки' % summary['generated']
ws['B3'].font = font_caption()
rows = [
 ('Всего записей в реестре', summary['total_registry'], 'после дедупликации и контент-фильтра'),
 ('Активные (HTTP 200)', sum(1 for r in records if r['status']=='active' and r['status_detail']!='antibot'), 'сайт отвечает 200 OK'),
 ('Активные за анти-ботом', sum(1 for r in records if r['status_detail']=='antibot'), '401/403/405/429/451 — сервис жив, бот-стена'),
 ('ИТОГО активных', summary['active_total'], 'цель 1000; честный потолок без накрутки'),
 ('Не верифицированы', sum(1 for r in records if r['status']=='unverified'), 'DNS/сеть песочницы, 404/5xx'),
 ('Слияния/ребрендинги', sum(1 for r in records if r['status']=='merged'), 'указан преемник'),
 ('Закрытые', sum(1 for r in records if r['status']=='closed'), 'подтверждено внешне'),
 ('Вероятно закрытые', sum(1 for r in records if r['status']=='unverified_dead'), 'NXDOMAIN по DoH'),
 ('Парковка домена', sum(1 for r in records if r['status']=='parked'), 'домен продаётся'),
 ('Исключено политикой контента', len(summary['excluded_policy']), 'политика/пропаганда и adult — по требованию'),
]
hdr = ['Показатель', 'Значение', 'Комментарий']
for ci, h in enumerate(hdr, 2):
    ws.cell(row=4, column=ci, value=h)
style_header_row(ws, row_num=4, col_start=2, col_end=last_col)
for i, (a, b, c) in enumerate(rows):
    rn = 5 + i
    ws.cell(row=rn, column=2, value=a)
    ws.cell(row=rn, column=3, value=b)
    ws.cell(row=rn, column=4, value=c)
    style_data_row(ws, row_num=rn, col_start=2, col_end=last_col, row_index=i)
    ws.cell(row=rn, column=3).alignment = align_number()
# region block
r0 = 5 + len(rows) + 2
ws.cell(row=r0, column=2, value='По макро-регионам (все статусы)')
ws.cell(row=r0, column=2).font = font_subheader()
from collections import Counter
regc = Counter(r['region'] for r in records)
catc = Counter(r['category'] for r in records).most_common()
orgc = Counter(r['origin'] for r in records)
rr = r0 + 1
for ci, h in enumerate(['Регион', 'Кол-во', ''], 2):
    ws.cell(row=rr, column=ci, value=h)
style_header_row(ws, row_num=rr, col_start=2, col_end=last_col)
for i, (k, v) in enumerate(sorted(regc.items(), key=lambda x: -x[1])):
    rn = rr + 1 + i
    ws.cell(row=rn, column=2, value=k)
    ws.cell(row=rn, column=3, value=v)
    style_data_row(ws, row_num=rn, col_start=2, col_end=last_col, row_index=i)
    ws.cell(row=rn, column=3).alignment = align_number()
r1 = rr + 1 + len(regc) + 2
ws.cell(row=r1, column=2, value='Происхождение записей')
ws.cell(row=r1, column=2).font = font_subheader()
ORIG_RU = {'base_451': 'Исходный архив (451)', '3b_europe.json': 'Батч Европа', '3c_asia.json': 'Батч Азия',
 '3d_americas.json': 'Батч Америки', '3e_africa_mea.json': 'Батч Африка/БВ', '3f_niche.json': 'Батч ниши',
 '3g_supplement.json': 'Батч-2 дополнение', '3h_batch3.json': 'Батч-3 финал'}
rr2 = r1 + 1
for ci, h in enumerate(['Батч', 'Кол-во', ''], 2):
    ws.cell(row=rr2, column=ci, value=h)
style_header_row(ws, row_num=rr2, col_start=2, col_end=last_col)
for i, (k, v) in enumerate(sorted(orgc.items(), key=lambda x: -x[1])):
    rn = rr2 + 1 + i
    ws.cell(row=rn, column=2, value=ORIG_RU.get(k, k))
    ws.cell(row=rn, column=3, value=v)
    style_data_row(ws, row_num=rn, col_start=2, col_end=last_col, row_index=i)
    ws.cell(row=rn, column=3).alignment = align_number()
auto_fit_columns(ws, min_width=8, max_width=60, header_row=4, data_start_row=5)

# ============ Sheet 2: Реестр ============
ws2 = wb.create_sheet('Реестр')
headers = ['ID', 'Название', 'Официальный URL', 'Регион', 'Регион/страна (исх.)',
           'Категория', 'Загрузка польз.', 'Статус', 'HTTP-вердикт', 'Перенаправление',
           'Примечания', 'Источник', 'Дата проверки']
last_col2 = len(headers) + 1
setup_sheet(ws2, title='Реестр видеоплатформ (%d записей, верификация %s)' % (len(records), summary['generated']), last_col=last_col2)
for ci, h in enumerate(headers, 2):
    ws2.cell(row=4, column=ci, value=h)
style_header_row(ws2, row_num=4, col_start=2, col_end=last_col2)
rn = 5
for i, r in enumerate(records):
    vals = [r['id'], r['name'], r['official_url'], r['region'],
            (r.get('country') or '') + (' / ' if r.get('country') and r.get('region_orig') else '') + (r.get('region_orig') or ''),
            r['category'], r['user_upload'],
            STATUS_RU.get(r['status'], r['status']) + (' (анти-бот)' if r.get('status_detail') == 'antibot' else ''),
            r['verdict_http'] or '', r['moved_to'] or '', r['notes'] or '',
            r['origin'].replace('.json','').replace('base_451','архив-451'), r['verified_date']]
    for ci, v in enumerate(vals, 2):
        ws2.cell(row=rn, column=ci, value=v)
    style_data_row(ws2, row_num=rn, col_start=2, col_end=last_col2, row_index=i)
    style_status_cell(ws2.cell(row=rn, column=9), r['status'], r.get('status_detail'))
    rn += 1
ws2.freeze_panes = 'D5'
auto_fit_columns(ws2, min_width=6, max_width=44, header_row=4, data_start_row=5)

# ============ Sheet 3: Исключённые ============
ws3 = wb.create_sheet('Исключённые')
setup_sheet(ws3, title='Исключено политикой контента (политика и adult)', last_col=4)
hdr3 = ['Название', 'URL', 'Причина', 'Происхождение']
for ci, h in enumerate(hdr3, 2):
    ws3.cell(row=4, column=ci, value=h)
style_header_row(ws3, row_num=4, col_start=2, col_end=5)
for i, e in enumerate(excluded):
    rn = 5 + i
    ws3.cell(row=rn, column=2, value=e.get('name'))
    ws3.cell(row=rn, column=3, value=e.get('official_url') or '')
    ws3.cell(row=rn, column=4, value='политика/пропаганда' if e.get('exclusion_reason') == 'excluded_political' else 'adult/порно')
    ws3.cell(row=rn, column=5, value='архив' if 'id' in e else 'кандидат')
    style_data_row(ws3, row_num=rn, col_start=2, col_end=5, row_index=i)
auto_fit_columns(ws3, min_width=8, max_width=50, header_row=4, data_start_row=5)

# ============ Sheet 4: Методология ============
ws4 = wb.create_sheet('Методология')
setup_sheet(ws4, title='Методология верификации и правила отбора', last_col=3)
meth = [
 ('1. Источник', 'Исходный архив пользователя: register.json (451 записей, глобальные видеоплатформы, RU-исследование).'),
 ('2. Расширение', '5 региональных батчей суб-агентов (Европа 140, Азия 57, Америки 101, Африка/БВ 21, ниши 100) + 2 партии куратора (187 и 24) + второй проход 2026-10-25: 4 батча (Европа-2 45, Америки-2 44, АТР-2 32, глобальные вертикали 50; после дедупа 164). Все кандидаты — только реально существующие сервисы; URL не выдумывались.'),
 ('3. Дедупликация', 'Полный хост (без www) → домен+нормализованное имя → нормализованное имя. Сверка с базой и внутри батчей. Снято 165 дублей (158 в первом проходе + 7 во втором, включая 5 исторических близнецов).'),
 ('4. HTTP-проверка', 'check_urls.py: 32-48 потоков, Chrome UA, до 6 редиректов, gzip, таймаут 14 с, ретраи с вариантами URL. Вердикты: ALIVE (200) / BLOCKED (401/403/405/429/451 = жив за анти-ботом) / PARKED / NOT_FOUND / SERVER_ERR / DNS_FAIL / TIMEOUT / UNREACHABLE.'),
 ('5. Кросс-проверки', 'WebSearch (официальные страницы, Google Play, отраслевые новости) для DNS-неоднозначных; DNS-over-HTTPS (dns.google) для отделения «домен мёртв» от «DNS песочницы сломан». Песочница агрессивно фильтрует сеть — часть DNS_FAIL помечена «не верифицировано», а не «мёртв» (по чек-листу: UNKNOWN не считается подтверждением).'),
 ('6. Слияния/ребрендинги', 'HTTP-редиректы между доменами + внешние источники: Hulu→Disney+, BET+→Paramount+, Awaan→Dubai+, Mitele→Mediaset Infinity, d Anime Store→Lemino, JioCinema→JioHotstar, iflix→WeTV, BluTV→Max, TRT İzle→tabii, Freevee→Prime Video, FITE→TrillerTV, Kino Now→Kino Film Collection, Stöð 2→Sýn, PlayPlus→RecordPlus, ConTV→Midnight Pulp, Wondrium→The Great Courses, NHK Plus→NHK ONE (2026-10), Pilipinas Live→Cignal Play, Aloula→SNRT Live, Amazon miniTV→Amazon MX Player и др. Слившиеся не считаются дважды.'),
 ('7. Обнаруженные смерти', 'Showmax (закрыт 2026-04-30, контент → DStv Stream), Optus Sport (закрыт 2025-08-01, права АПЛ → Stan Sport), Mola (закрыт 2025-12-31), Anime Onegai (окт. 2025), LINE TV (Таиланд), WASD.tv, myVideo.com.tw (домен перехвачен казино), Buni TV, Nollyland, ICFLIX, Weyyak, Caffeine, Blim TV и др. — закрытые помечены статусом, из активного набора исключены.'),
 ('8. Контент-политика', 'По требованию заказчика исключены политические/пропагандистские платформы (Rumble, Odysee, BitChute, Brighteon, Gab, Gan Jing World из архива; Belsat, Espreso TV, Hromadske, 24 Канал из кандидатов) и adult (OnlyFans). Лист «Исключённые».'),
 ('9. Статусы', 'активен (HTTP 200) · активен (анти-бот) · не верифицирован (DNS/сеть песочницы) · слияние/ребрендинг (указан преемник) · закрыт · вероятно закрыт (NXDOMAIN) · парковка домена. Активными считаются только первые два.'),
 ('10. Честность', 'Цель «1000» достигнута без накрутки: 1071 реальных записей, из них 1032 подтверждены активными (второй + финальный проходы верификации 2026-10-24/25). В реестр не включены пираты (Cuevana, Adjaranet и т.п.), B2B-инфраструктура, радио и чистые каталоги.'),
]
for ci, h in enumerate(['Пункт', 'Описание', ''], 2):
    ws4.cell(row=4, column=ci, value=h)
style_header_row(ws4, row_num=4, col_start=2, col_end=3)
for i, (a, b) in enumerate(meth):
    rn = 5 + i
    ws4.cell(row=rn, column=2, value=a)
    ws4.cell(row=rn, column=3, value=b)
    style_data_row(ws4, row_num=rn, col_start=2, col_end=3, row_index=i)
    ws4.cell(row=rn, column=3).alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
ws4.column_dimensions['C'].width = 95
auto_fit_columns(ws4, min_width=8, max_width=28, header_row=4, data_start_row=5)

wb.properties.creator = 'Z.ai'
out = '/home/z/my-project/download/global_video_platforms_registry_2026.xlsx'
wb.save(out)
print('saved', out)
