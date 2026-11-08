# KNOWN ISSUES · global-video-platforms-registry

## Волна ×5 · 2026-11-09

| Воркфлоу | Run id (sha) | Диагноз | Статус после патча |
|---|---|---|---|
| validate | 42516478560 (97f66c5, 19:43) | CSV(428) != JSON(1071) — усечённый CSV после краха посреди writerows | 🟢 CSV перегенерирован ×4 (c7f2448: 1071 строк); локальное репро scripts/audit_repo.py: ISSUES 0; диспатч ×5 42527780228 🟢 |
| validate | 42514888483 (c8bc7e1, 19:24) | тот же корень | 🟢 то же |
| patrol | 42513915700 / 42513897295 (65a70fb, 19:12–13) | _csv.Error «need to escape, but no escapechar set» при writerows | 🟢 ×4 (8ad7a72): чтение/запись на csv.excel + атомарная запись с круговым рейсом; прогоны 42516735451 🟢 (19:46), 42517046963 🟢 (19:50) |

### Квирки

- Sniffer на канон-CSV угадывает QUOTE_NONE/doublequote=False (кавычки внутри notes) — patrol.py сознательно фиксирует dialect=csv.excel; «улучшать» на sniffer нельзя.
- UA патруля строго ASCII: не-latin1 в User-Agent роняет urllib.request ещё на отправке (UnicodeEncodeError → все пробы «error», ms=0 — ноябрь 2026 так и сходил).
- PRODUCT_PAIRS (vimeo.com, linkedin.com) — задокументированные whitelist-дубль-домены в audit_repo.py; не «чинить» без правки DATA_DICTIONARY.
- Патруль пишет только статус-колонки; самопроверка записи перечитывает tmp-файл и сверяет контентные поля до замены (os.replace) — держать атомарность при любых правках writerows.
