# Волна ×3 · W3-E (добивание) · «Патруль-Кольцо» (предложение global-video-platforms-registry#3).
# Ежемесячная стратифицированная проба URL реестра: 10% ротация без повторов (seed = месяц)
# плюс 100% строк с last_check старше 180 дней. Зона записи патруля — только статус-колонки
# (last_check, http_status, dead_streak, patrol_state) и evidence; содержательные поля
# платформ не изменяются (контролируется снимком до/после). python-stdlib, 3.11+.
import argparse, csv, glob, json, os, random, sys, time
import urllib.error, urllib.request
from datetime import date

PATROL_COLS = ["last_check", "http_status", "dead_streak", "patrol_state"]
URL_KEYS = ("url", "platform_url", "site", "website", "link", "homepage")
# UA строго ASCII: не-latin1 символы в заголовке роняют urllib.request ещё на отправке
# (UnicodeEncodeError → мгновенный code="error", ms=0 — так «патруль» ноября 2026 ни разу
# реально не постучался: все пробы вернули error, не доходя до сети).
UA = ("global-video-platforms-registry-patrol/1.0 "
      "(+https://github.com/rtynbirf/global-video-platforms-registry; monthly URL patrol)")


def first_sunday(y, m):
    d = date(y, m, 1)
    return d.replace(day=1 + (6 - d.weekday()) % 7)  # weekday: Пн=0 … Вс=6; если 1-е — воскресенье, вернётся 1-е


def probe(url, timeout, retries):
    """HEAD → GET при 405/403 (и на сбой HEAD), таймаут, повторы. Возвращает (код|'error', мс)."""
    last_ms = 0
    for attempt in range(retries + 1):
        for method in ("HEAD", "GET"):
            t0 = time.perf_counter()
            try:
                req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return int(r.status), int((time.perf_counter() - t0) * 1000)
            except urllib.error.HTTPError as e:
                last_ms = int((time.perf_counter() - t0) * 1000)
                if method == "HEAD":
                    break  # HEAD отклонён — уточняем GET-ом
                if e.code < 500:
                    return e.code, last_ms
            except Exception:
                last_ms = int((time.perf_counter() - t0) * 1000)
                if method == "GET" and attempt == retries:
                    return "error", last_ms
    return "error", last_ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv-glob", default="download/*.csv")
    ap.add_argument("--evidence-dir", default="evidence")
    ap.add_argument("--sample-frac", type=float, default=0.10)
    ap.add_argument("--stale-days", type=int, default=180)
    ap.add_argument("--timeout", type=int, default=10)
    ap.add_argument("--retries", type=int, default=2)
    args = ap.parse_args()

    # Крон стреляет 1-7 числа; под schedule работаем только 1-е воскресенье месяца.
    today = date.today()
    if os.environ.get("GITHUB_EVENT_NAME") == "schedule" and today != first_sunday(today.year, today.month):
        print("Патруль: сегодня не первое воскресенье месяца (%s) — пропуск." % today)
        return
    candidates = sorted(glob.glob(args.csv_glob))
    if not candidates:
        print("Патруль: CSV реестра не найден по шаблону %s" % args.csv_glob); sys.exit(1)
    src = max(candidates, key=os.path.getsize)
    print("Патруль: источник данных — %s" % src)

    # Диалект строго csv.excel: Sniffer на этом файле угадывает QUOTE_NONE/doublequote=False
    # (из-за кавычек внутри notes) — так он ИСКАЖАЕТ чтение канона и требовал escapechar при
    # записи (первопричина _csv.Error в c8bc7e1). Канон — стандартный excel-CSV с удвоенными
    # кавычками; читаем и пишем одинаковым csv.excel — круговой рейс точный.
    with open(src, encoding="utf-8-sig", newline="") as f:
        dialect = csv.excel
        rows = list(csv.DictReader(f, dialect=dialect))
        fields = list(rows[0].keys()) if rows else []
    url_col = next((c for c in fields if c.lower() in URL_KEYS), None) \
        or next((c for c in fields if "url" in c.lower()), None)
    if not url_col:
        print("Патруль: в %s не найдена колонка URL (%s)" % (src, fields)); sys.exit(1)
    for c in PATROL_COLS:
        if c not in fields:
            fields.append(c)

    # Стратифицированная проба: seed = номер месяца (ротация без повторов внутри года).
    seed = today.year * 100 + today.month
    rng = random.Random(seed)
    idx = list(range(len(rows)))
    n_sample = max(1, int(len(idx) * args.sample_frac))
    sample = set(rng.sample(idx, n_sample))
    for i in idx:  # 100% строк, чей последний осмотр старше 180 дней
        lc = (rows[i].get("last_check") or "").strip()
        if lc:
            try:
                if (today - date.fromisoformat(lc[:10])).days > args.stale_days:
                    sample.add(i)
            except ValueError:
                sample.add(i)
        else:
            pass  # пустой last_check — строку накроет ротация 10% либо финальный маркер unverified
    sample = sorted(sample)
    print("Патруль: строк всего %d, проба месяца %d (10%% = %d + просроченные)" %
          (len(rows), len(sample), n_sample))

    snapshot = [{k: r.get(k, "") for k in fields if k not in PATROL_COLS} for r in rows]
    stamp = "%sT%sZ" % (today.isoformat(), time.strftime("%H:%M:%S", time.gmtime()))
    ev_path = os.path.join(args.evidence_dir, "%04d-%02d-patrol.jsonl" % (today.year, today.month))
    os.makedirs(args.evidence_dir, exist_ok=True)
    alive = failed = 0
    with open(ev_path, "a", encoding="utf-8") as ev:
        for n, i in enumerate(sample):
            url = (rows[i].get(url_col) or "").strip()
            if not url:
                rows[i]["last_check"] = today.isoformat()
                rows[i]["http_status"] = "unverified: нет URL в строке реестра"
                rows[i]["patrol_state"] = rows[i].get("patrol_state") or "unverified"
                continue
            code, ms = probe(url, args.timeout, args.retries)
            ok = isinstance(code, int) and code < 400
            alive += ok
            failed += not ok
            streak = 0 if ok else int(rows[i].get("dead_streak") or 0) + 1
            rows[i]["last_check"] = today.isoformat()
            rows[i]["http_status"] = str(code)
            rows[i]["dead_streak"] = str(streak)
            rows[i]["patrol_state"] = "alive" if ok else ("stale" if streak >= 2 else "suspect")
            ev.write(json.dumps({"url": url, "code": code, "ms": ms, "checked_at": stamp},
                                ensure_ascii=False) + "\n")
            if (n + 1) % 25 == 0:
                print("Патруль: %d/%d проб…" % (n + 1, len(sample)))
    # Явный маркер для строк, ещё не охваченных кольцом (критерий 1).
    for r in rows:
        if not (r.get("http_status") or "").strip():
            r["http_status"] = "unverified: не входила в пробу (ждёт кольца)"
            r["patrol_state"] = r.get("patrol_state") or "unverified"
    # Контроль зоны записи: содержательные поля не тронуты (критерий 3).
    after = [{k: r.get(k, "") for k in fields if k not in PATROL_COLS} for r in rows]
    if after != snapshot:
        print("Патруль: НАРУШЕНИЕ ЗОНЫ ЗАПИСИ — содержательные поля изменились; откат."); sys.exit(2)

    # Атомарная запись: крах посреди writerows (как было до фикса диалекта в c8bc7e1)
    # усекал реестр на месте (1071 → 428 строк). Пишем во временный файл, перечитываем,
    # сверяем число строк И контентные поля (круговой рейс) — и только потом заменяем.
    tmp = src + ".patrol.tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, dialect=csv.excel, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(rows)
        f.flush()
        os.fsync(f.fileno())
    reread = list(csv.DictReader(open(tmp, encoding="utf-8-sig", newline="")))
    content_cols = [c for c in fields if c not in PATROL_COLS]
    roundtrip_ok = len(reread) == len(rows) and all(
        (a.get(c) or "") == (b.get(c) or "")
        for a, b in zip(reread, rows) for c in content_cols)
    if not roundtrip_ok:
        os.remove(tmp)
        print("Патруль: САМОПРОВЕРКА ЗАПИСИ не сошлась (строк %d ≠ %d или дрейф контента) — исходник не тронут." % (len(reread), len(rows)))
        sys.exit(2)
    os.replace(tmp, src)
    total = len(rows)
    states = {}
    for r in rows:
        states[r.get("patrol_state") or "unverified"] = states.get(r.get("patrol_state") or "unverified", 0) + 1
    summary = {"source_csv": src, "date": today.isoformat(), "rows_total": total,
               "probed": len(sample), "alive": alive, "failed": failed, "states": states}
    with open(os.path.join(args.evidence_dir, "%04d-%02d-patrol-summary.json" % (today.year, today.month)),
              "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("Патруль: итог %s" % json.dumps(summary, ensure_ascii=False))
    print("Патруль: счётчики пересчитаны из CSV, не вписаны вручную; evidence → %s" % ev_path)


if __name__ == "__main__":
    main()
