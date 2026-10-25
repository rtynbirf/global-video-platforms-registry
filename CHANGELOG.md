# Changelog

Все значимые изменения реестра. Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/); версионирование — [SemVer](https://semver.org/lang/ru/).

## [3.2.0] — 2026-10-25

### Исправлено (аудит целостности)
- Сняты 3 доменных дубля, пропущенных в v3.0–v3.1:
  - `Ustream` (id 342/450, дубль из исходного набора) → обе записи `merged → IBM Video Streaming`;
  - `Cignal Play (ex-Pilipinas Live)` (id 1383) → `merged → Cignal Play` (id 144).
- Запись `Slow Channel` (id 441) — заполнен отсутствовавший URL (`https://slowchannel.com`, жив за Cloudflare).
- Пару Vimeo/Vimeo OTT и LinkedIn/LinkedIn Learning проверили и **сохранили** как легитимные разные продукты на одном домене (задокументировано в DATA_DICTIONARY).

### Итоговые счётчики
- active 1035 → **1032**, merged 18 → **21**, всего 1071 (не изменилось).

## [3.1.0] — 2026-10-25

### Верификация
- Финальный проход по 23 «застрявшим» записям: **+15 активных** с переносом доменов (Toffee → toffeelive.com, Atrangii → atrangii.in, smash. → smash-media.jp, UpLive → h5.upliveapp.com, Stievie → stievie.be, Bstation → bilibili.tv), **3 слияния** (Anime Times → Amazon Prime Video Channels; Filmatique → Kino Film Collection; BrutX → Brut), **2 закрытия** (Trace Play — паркинг; GoPlay.bg — NXDOMAIN), Josh подтверждён как паркинг (HugeDomains).

### Итоговые счётчики
- active 1020 → 1035; unverified 19 → 1; unverified_dead 3 → 1; merged 15 → 18; closed 13 → 15.

## [3.0.0] — 2026-10-25

### Добавлено
- Батч-5 добора: 163 новых платформы (Европа-2 45, Америки-2 44, АТР-2 32, глобальные вертикали 50, минус кросс-дедуп).
- Вербификация 72 хвостов: закрытия Showmax (2026-04-30), Optus Sport (2025-08-01), Mola (2025-12-31); ребренды NHK Plus → NHK ONE, Pilipinas Live → Cignal Play, Aloula → SNRT Live.
- Поставка: XLSX (4 листа), CSV 1071×17 (UTF-8 BOM), JSON, PDF-отчёт 10 стр., ZIP.

## [1.0.0] — 2026-10-24

### Добавлено
- Исходный набор 451 запись (ZIP заказчика) → HTTP-верификация: 321 ALIVE / 87 BLOCKED / 24 проблемных.
- Вики-сборка кандидатов + 419 региональных кандидатов, доменная дедупликация, фильтр политики контента (11 записей: 10 политических, 1 adult).
