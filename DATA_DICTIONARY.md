# Словарь данных / Data Dictionary

Реестр: 1071 запись × 17 колонок. Машиночитаемая схема: [`datapackage.json`](datapackage.json) (Data Package v2 / Table Schema).

## Колонки CSV

| # | Колонка | Тип | Обязательна | Описание |
|---|---|---|---|---|
| 1 | `id` | string | да | Стабильный ID. База заказчика — числовой (1–451); добор батчей — префиксный (`B5-xxx`); промежуточные доборы — числовые с продолжением. |
| 2 | `name` | string | да | Название платформы на момент проверки. |
| 3 | `official_url` | string (URL) | да* | Официальный домен/путь. *Для `merged`-записей может указывать на преемника; для 2 unverified — на восстановленный домен. |
| 4 | `region` | string (enum) | да | Текущая география: `Global`, `Europe`, `Asia`, `North America`, `Latin America`, `Middle East`, `Africa`, `CIS`, `Oceania`, `Self-Hosted`, `Historical`, `Unverified`. |
| 5 | `region_orig` | string | нет | Регион из исходного набора (для трассировки перемещений). |
| 6 | `country` | string | нет | Страна происхождения/штаб-квартиры. |
| 7 | `category` | string (enum, 20 значений) | да | Категория: `broadcaster_iplayer` 120 · `vod_subscription` 115 · `sports` 74 · `vod_ad_supported` 46 · `live_streaming` 55 · `cinema_vod` 37 · `education` 29 · `fitness` 21 · `music_video` 22 · `faith` 15 · `documentary` 14 · `anime` 11 · `kids` 17 · `culture` 8 · `ugc_hosting` 8 · `operator_iplayer` 17 · `gaming_video` 6 · `niche_other` 9 · `creator` 4 · `family` 1. Устаревшие/проприетарные подписи исходного набора сохранены в свободной форме для base-записей. |
| 8 | `user_upload` | string (enum) | да | Публичная загрузка видео пользователями: `yes` (37) · `no` (1028) · `partial` (6). |
| 9 | `status` | string (enum) | да | `active` (1032) · `merged` (21) · `closed` (15) · `parked` (1) · `unverified` (1) · `unverified_dead` (1). |
| 10 | `status_detail` | string | нет | Уточнение статуса, если нужно. |
| 11 | `verdict_http` | string (enum) | да | Сырой вердикт последней HTTP-пробы: `ALIVE` (200–299) · `BLOCKED` (401/403/405/406/429/451 — жив за анти-ботом/гео-блоком, **засчитывается как активная**) · `PARKED` · `CLOSED` · `MOVED` · `NOT_FOUND` · `DNS_FAIL` · `TIMEOUT` · `UNREACHABLE` · `REDIRECT_LOOP` · `CRASH` · `BAD_URL`. |
| 12 | `moved_to` | string | для merged | Имя платформы-преемника (21 запись): напр. `Disney+`, `IBM Video Streaming`, `Kino Film Collection`, `Amazon Prime Video Channels`, `Cignal Play`. |
| 13 | `notes` | string | нет | Факты последней проверки: перенос домена, дата закрытия, источник решения. |
| 14 | `verified_date` | string (date ISO-8601) | да | Дата последней верификации: `2026-10-24` или `2026-10-25`. |
| 15 | `source` | string | нет | Метод/источник последней проверки (HTTP-прогон, DoH, Wikipedia, PR компании). |
| 16 | `confidence` | string (enum) | да | `High` / `Medium` / `Low` (регистр не нормализован исторически). |
| 17 | `origin` | string | да | Происхождение записи: `base_451` (исходный набор) или файл кандидата (`3b_europe.json`, `batch5_5a` и т.п.). |

## Правила целостности (проверяет CI)

1. **Уникальность `id`** — по всему реестру.
2. **Один активный домен** — среди `status=active` не бывает двух записей с одним registrable-доменом. Исключение задокументировано: `vimeo.com` (Vimeo и Vimeo OTT — разные продукты) и `linkedin.com` (LinkedIn и LinkedIn Learning). `merged`/`closed`-записи могут ссылаться на те же URL — это трассировка.
3. **Активная запись всегда с валидным URL** (`http…`), никогда — `UNKNOWN`.
4. `verified_date` — строго `YYYY-MM-DD`.
5. Счётчики `status` в JSON-обёртке и README синхронны с данными.

## Политические исключения

11 записей вынесены из основной таблицы в `excluded_policy` (в JSON-обёртке): 10 политических (Rumble, Odysee, BitChute, Brighteon, Gab, Gan Jing World, Espreso TV, Hromadske, 24 Канал, Belsat) и 1 adult (OnlyFans). Каждая с `exclusion_reason` — ничего не удалено молча.

## Известные ограничения схемы

- `category` у base-записей (451) сохранил исторические подписи исходного набора (свободная форма); у доборных записей — строгий енум из 20 значений. Не нормализуем задним числом, чтобы не терять исходную семантику заказчика.
- `confidence` содержит оба регистра (`High`/`high`) — артефакт двух волн сбора; значения эквивалентны.
