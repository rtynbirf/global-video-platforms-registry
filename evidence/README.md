# Verification evidence / Свидетельства верификации

Raw artifacts from the HTTP verification passes behind this registry. Files are
published as-is (only paths kept, no content edited) so that every status verdict
in the dataset can be traced to a machine-readable probe result.

Сырые артефакты HTTP-проверок, на которых основан реестр. Файлы опубликованы
как есть — каждый вердикт `status` в датасете прослеживается до результата пробы.

| File | What it is |
|---|---|
| `summary.json` | Aggregate counters of registry v3.1 build (status/region/category counts, `active_total`) |
| `verification_uv_final.txt` | curl probe results for the final 23-record "unverified tail" pass (2026-10-25) |
| `decisions_uv_final.txt` | Human-adjudicated verdicts for those 23 records, with source links |
| `http_batch5_results.json` | Raw HTTP verdicts for the batch-5 candidate sweep |
| `http_doh_results.json` | DNS-over-HTTPS fallback probes for domains where direct TLS was blocked |

Methodology: `curl` + DoH (`dns.google/resolve`) with `--resolve` fallback,
8 parallel workers, timeout budget 20 s; verdicts mapped to
`ALIVE / BLOCKED / NOT_FOUND / SERVER_ERR / DNS_FAIL / TIMEOUT / PARKED`.
Domains that block the probe network (401/403/405/406/429/451) are treated as
alive-with-protection (`BLOCKED`), not dead.
