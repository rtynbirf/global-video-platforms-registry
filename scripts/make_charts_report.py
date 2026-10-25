#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_charts_report.py — 2 charts for the registry PDF report (RU).
Palette: Template 07 Crystal Blue body subset (fixed, per cover.md)."""
import json
import matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

ACCENT = '#2d7ab3'
HEADER = '#1a4a7a'
MUTED = '#5a7a96'
STRIPE = '#eef3fa'
TEXT = '#142840'

W = '/home/z/my-project/registry_work'
records = json.load(open(W + '/final/registry_final.json', encoding='utf-8'))
from collections import Counter

# ---- Chart 1: horizontal bar — active platforms by region ----
act = Counter(r['region'] for r in records if r['status'] == 'active')
order = [('Европа', 'Europe'), ('Сев. Америка', 'North America'), ('Глобальные', 'Global'),
         ('Азия', 'Asia'), ('Бл. Восток', 'Middle East'), ('Лат. Америка', 'Latin America'),
         ('Африка', 'Africa'), ('Океания', 'Oceania'), ('СНГ', 'CIS'), ('Селф-хостинг', 'Self-Hosted')]
labels = [ru for ru, _ in order]
vals = [act.get(k, 0) for _, k in order]
pairs = sorted(zip(labels, vals), key=lambda x: x[1])
labels = [p[0] for p in pairs]
vals = [p[1] for p in pairs]

fig, ax = plt.subplots(figsize=(7.6, 4.4), constrained_layout=True)
bars = ax.barh(labels, vals, color=ACCENT, height=0.62, edgecolor='none', zorder=3)
for b, v in zip(bars, vals):
    ax.text(b.get_width() + 3, b.get_y() + b.get_height() / 2, str(v),
            va='center', ha='left', fontsize=10.5, color=TEXT)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#c0d0e2')
ax.tick_params(axis='y', length=0, labelsize=11, colors=TEXT)
ax.tick_params(axis='x', colors=MUTED, labelsize=9)
ax.set_xlim(0, max(vals) * 1.14)
ax.grid(axis='x', linestyle='--', linewidth=0.5, alpha=0.2, zorder=0)
ax.set_xlabel('Активных платформ (HTTP 200 или анти-бот)', fontsize=10, color=MUTED)
fig.savefig('/home/z/my-project/registry_work/final/chart_regions.png', dpi=200,
            facecolor='white')
plt.close(fig)
print('chart 1 ok')

# ---- Chart 2: donut — verification status breakdown ----
st = Counter(r['status'] for r in records)
mapping = [
 ('Активен (HTTP 200)', st.get('active', 0) - sum(1 for r in records if r['status_detail'] == 'antibot'), ACCENT),
 ('Активен за анти-ботом', sum(1 for r in records if r['status_detail'] == 'antibot'), '#4da8da'),
 ('Не верифицирован', st.get('unverified', 0), '#c0d0e2'),
 ('Слияние/ребрендинг', st.get('merged', 0), MUTED),
 ('Закрыт / вероятно закрыт', st.get('closed', 0) + st.get('unverified_dead', 0) + st.get('parked', 0), '#8a4a4a'),
]
labels2 = [m[0] for m in mapping]
vals2 = [m[1] for m in mapping]
cols2 = [m[2] for m in mapping]
total = sum(vals2)

fig, ax = plt.subplots(figsize=(7.6, 3.9), constrained_layout=True)
wedges, _ = ax.pie(vals2, colors=cols2, startangle=90, counterclock=False,
                   wedgeprops=dict(width=0.34, edgecolor='white', linewidth=1.5))
ax.text(0, 0.06, str(total), ha='center', va='center', fontsize=26,
        color=TEXT, fontweight='bold')
ax.text(0, -0.22, 'записей', ha='center', va='center', fontsize=10, color=MUTED)
# rich legend to the right (Strategy C — zero text on chart)
legend_labels = ['%s — %d (%.1f%%)' % (l, v, v * 100.0 / total) for l, v in zip(labels2, vals2)]
ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1.02, 0.5),
          frameon=False, fontsize=10.5, handlelength=1.0, handleheight=1.0,
          labelcolor=TEXT)
ax.set_aspect('equal')
fig.savefig('/home/z/my-project/registry_work/final/chart_status.png', dpi=200,
            facecolor='white')
plt.close(fig)
print('chart 2 ok')
