# Глобальный реестр видеоплатформ 2026 / Global Video Platforms Registry

![Records](https://img.shields.io/badge/records-1071-2c7fb8)
![Active](https://img.shields.io/badge/active-1032-41ab5d)
![Verified](https://img.shields.io/badge/verified-2026--10--25-f5a623)
![License](https://img.shields.io/badge/license-CC_BY_4.0-blue)
![CI](https://github.com/rtynbirf/global-video-platforms-registry/actions/workflows/validate.yml/badge.svg)
![Version](https://img.shields.io/badge/version-v3.2-8250df)

**Верифицированный машинно-читаемый реестр из 1071 видеоплатформы мира** — с HTTP-проверкой каждого домена, трассировкой ребрендингов и слияний, открытой методологией и полным аудит-следом. Включает стриминговые сервисы, UGC-хостинги, публичные iPlayer-ы, спортивные DTC, вертикальные платформы и само-хостинговые системы.

A machine-readable, individually verified registry of 1,071 global video platforms: every domain HTTP-checked, rebrands and closures traced, methodology and audit trail fully open. *(English summary at the bottom.)*

---

## Содержание

1. [Что это](#что-это)
2. [Ключевые цифры](#ключевые-цифры)
3. [Методология верификации](#методология-верификации)
4. [Политика включения и исключения](#политика-включения-и-исключения)
5. [Схема данных](#схема-данных)
6. [Файлы и структура](#файлы-и-структура)
7. [Быстрый старт](#быстрый-старт)
8. [Качество и честные ограничения](#качество-и-честные-ограничения)
9. [Цитирование](#цитирование)
10. [Лицензия](#лицензия)

## Что это

Реестр построен из трёх слоёв источников и прошёл два полных прохода верификации (2026-10-24 и 2026-10-25), плюс финальную дочистку 23 «застрявших» хвостов. Каждый источник уникален на уровне домена; каждая запись несёт категорию, регион, страну, признак публичной пользовательской загрузки, источник, дату и метод верификации. Реестр спроектирован как рабочий инструмент: он отвечает на вопросы «какие платформы реально живы», «куда переехал закрытый бренд» и «что где доступно пользователям» — без накрутки и мёртвых ссылок.

- **Формат:** CSV (UTF-8 BOM, 17 колонок), JSON, XLSX (4 листа), PDF-отчёт (10+ страниц)
- **Покрытие:** 12 регионов, 20 категорий — от глобальных гигантов (YouTube, Netflix, Disney+) до нишевых национальных iPlayer-ов
- **Воспроизводимость:** все скрипты проверки и сырые результаты HTTP-прогонов включены в репозиторий

## Ключевые цифры

| Статус | Записей | Доля |
|---|---:|---:|
| **active** (подтверждённо жива) | **1032** | 96.4% |
| merged (слита с преемником) | 21 | 2.0% |
| closed (закрыта) | 15 | 1.4% |
| parked (домен-паркинг) | 1 | 0.1% |
| unverified / unverified_dead | 2 | 0.2% |
| **Всего** | **1071** | 100% |

По регионам: Europe 278 · Global 234 · Asia 198 · North America 223 · Latin America 34 · Middle East 31 · CIS 15 · Africa 21 · Oceania 22 · Self-Hosted 6 · Historical 8. По категориям: broadcaster_iplayer 120, vod_subscription 115, live_streaming 55, sports 74, cinema_vod 37, vod_ad_supported 46 и др. (полная разбивка — в PDF-отчёте, раздел 3).

## Методология верификации

1. **HTTP-проба каждого домена** — многопоточный чекер (32 потока, ≤6 ручных редиректов, Chrome UA, чтение заголовков + тела 128KB).
2. **Вердикт-схема:** `ALIVE` (200–299) · `BLOCKED` (401/403/405/406/429/451 = жив за анти-ботом или гео-блоком — **засчитывается как активная**) · `NOT_FOUND` · `DNS_FAIL` · `PARKED` (детект паркинг-страниц) · `MOVED` (с фиксацией преемника).
3. **DoH-фолбэк** (dns.google) для доменов, не резолвящихся из песочницы; повторные пробы TLS-вариантами и через curl.
4. **Кросс-проверка фактами:** Wikipedia/отраслевые источники для ребрендингов и закрытий 2025–2026 (Showmax, Optus Sport, NHK ONE, Filmatique→Kino Film Collection, Anime Times→Prime Video Channels и др.).
5. **Двойной проход + хвостовая дочистка:** все сомнительные статусы перепроверены 2026-10-25; остались 2 честных «неизвестных» (Playeur, iROKOtv) — они помечены, а не выдуманы.

## Политика включения и исключения

- **Включаются:** публичные видеоплатформы с веб-слоем: SVOD/AVOD/FAST, UGC-хостинги, публичные iPlayer-ы вещателей, спортивные DTC, вертикальные (аниме/дети/вера/образование/фитнес/концерты), само-хостинговые системы (PeerTube и аналоги).
- **Исключаются и не входят:** пираты (Cuevana, Adjaranet и т.п.), B2B-инфраструктура без потребительского слоя, радио без видео, чистые каталоги-агрегаторы, **политическая пропаганда** (Rumble, Odysee, BitChute, Brighteon, Gab, Gan Jing World, Espreso TV, Hromadske, 24 Канал, Belsat — 11 записей вынесено в `excluded_policy`) и **18+ платформы** (OnlyFans).
- **Не считаются отдельными:** региональные версии глобальных платформ, продукты на одном домене (Vimeo ↔ Vimeo OTT, LinkedIn ↔ LinkedIn Learning — разные продукты, домен один, это задокументировано).
- **Трассировка слияний:** 21 запись имеет `status=merged` и `moved_to` с именем преемника — Hulu→Disney+, Max↔HBO Max, Mitele→Mediaset Infinity, Filmatique→Kino Film Collection и др.

## Схема данных

17 колонок; полные описания и енумы — в [DATA_DICTIONARY.md](DATA_DICTIONARY.md), машиночитаемая схема — в [datapackage.json](datapackage.json) (стандарт [Data Package v2](https://datapackage.org)).

| Колонка | Смысл |
|---|---|
| `id` | Стабильный идентификатор (база 1–451, добор B5-xxx) |
| `name` | Название платформы |
| `official_url` | Официальный домен (актуальный после ребрендингов) |
| `region`, `region_orig`, `country` | География |
| `category` | Категория (20 енумов, напр. `broadcaster_iplayer`, `sports`, `anime`) |
| `user_upload` | Публичная загрузка от пользователей: `yes` / `no` / `partial` |
| `status` | `active` / `merged` / `closed` / `parked` / `unverified` / `unverified_dead` |
| `verdict_http` | Сырой HTTP-вердикт последней пробы |
| `moved_to` | Преемник (для merged) |
| `verified_date` | Дата последней проверки |
| `source`, `confidence`, `origin` | Источник, уверенность, происхождение записи |

## Файлы и структура

```
download/
  global_video_platforms_registry_2026.csv    # основная таблица (UTF-8 BOM)
  global_video_platforms_registry_2026.json   # полный дамп + summary + excluded_policy
  global_video_platforms_registry_2026.xlsx   # 4 листа: реестр, статусы, регионы, методология
  registry_verification_report_2026.pdf       # отчёт о верификации (RU, с графиками)
evidence/
  summary.json                               # агрегаты сборки (статусы/регионы/категории)
  verification_uv_final.txt                  # сырые HTTP-пробы финального прохода
  decisions_uv_final.txt                     # вердикты по 23 хвостам со ссылками на источники
scripts/
  check_urls.py          # HTTP-чекер (32 потока, DoH-фолбэк)
  audit_repo.py          # целостность: дубли, енумы, консистентность CSV/JSON
  build_registry2.py     # сборка из кандидатов + патчи
  make_xlsx.py / make_report_pdf.py / make_charts_report.py / export_csv_json.py
.github/workflows/validate.yml               # CI: валидация на каждый push
DATA_DICTIONARY.md · datapackage.json · CITATION.cff · CHANGELOG.md
```

## Быстрый старт

```python
import pandas as pd
df = pd.read_csv("download/global_video_platforms_registry_2026.csv", encoding="utf-8-sig")
active = df[df.status == "active"]
print(active.category.value_counts().head(10))
eu_sports = active[(active.region == "Europe") & (active.category == "sports")]
```

## Качество и честные ограничения

- **1032/1071 (96.4%)** подтверждены живыми; у 180+ активных проба дала анти-бот/гео-блок (`BLOCKED`) — такие засчитаны активными с фиксацией метода.
- Две записи (Playeur, iROKOtv) сознательно оставлены `unverified`/`unverified_dead`: противоречивые внешние сигналы, требуют проверки с чистых IP.
- Метрики популярности не выдуманы: колонки там, где нет официальных цифр, пусты.
- Верификация проводилась из одной сетевой среды (2026-10-24/25); домены, заблокированные для песочницы, проверены через DoH и внешние источники, а не «угаданы».
- Региональные кандидаты проходили кросс-дедупликацию на уровне registrable-домена и имени; 3 дубля выявлены финальным аудитом и слиты (см. CHANGELOG).

## Цитирование

Файл [CITATION.cff](CITATION.cff) — GitHub встроит кнопку «Cite this repository».

```bibtex
@dataset{rtynbirf_2026_global_video_platforms,
  title  = {Global Video Platforms Registry 2026 (verified, 1071 records)},
  author = {rtynbirf and contributors},
  year   = {2026},
  doi    = {10.5281/zenodo.TODO},
  url    = {https://github.com/rtynbirf/global-video-platforms-registry},
  note   = {v3.2, verified 2026-10-25}
}
```

## Лицензия

Данные — [CC BY 4.0](LICENSE): свободное использование с указанием авторства. Скрипты — MIT. Бренды принадлежат их владельцам; реестр — фактологический каталог, никакой аффилиации.

---

### English summary

**What:** individually verified registry of 1,071 global video platforms (1,032 confirmed active, 96.4%). Every domain HTTP-probed with a documented verdict scheme (ALIVE / BLOCKED / PARKED / MOVED…), DoH fallback and Wikipedia-grade cross-checks; rebrands and closures traced (21 `merged` rows with successors). **Why it's different:** zero padding — pirates, B2B-only infrastructure, political propaganda and adult platforms are explicitly excluded and listed in `excluded_policy`; uncertain entries stay honestly marked instead of being invented. **Format:** CSV/JSON/XLSX + a 10-page verification report (Russian), frictionless `datapackage.json`, CI-validated on every push. **License:** CC BY 4.0. See the Russian sections above for methodology and data dictionary — the schema is language-independent.
