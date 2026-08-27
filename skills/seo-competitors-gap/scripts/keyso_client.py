#!/usr/bin/env python3
"""
Keys.so API client — минимальная обёртка для SEO-аудита.

Usage:
  python3 keyso_client.py check
  python3 keyso_client.py profile <domain> [--base msk]
  python3 keyso_client.py competitors <domain> [--limit 30] [--base msk]
  python3 keyso_client.py keys <domain> [--per-page 1000] [--max-pages 10] [--base msk]
  python3 keyso_client.py gap <our_domain> <comp1> [<comp2> ...] [--base msk] [--top 1000]
  python3 keyso_client.py lost <domain> [--limit 500] [--base msk]

Токен берётся из переменной окружения KEYSO_API_TOKEN или из ai-seo/.env.
Header: X-Keyso-TOKEN
Base URL: https://api.keys.so/

Документация keys.so API: https://www.keys.so/ru/api-doc
Если эндпоинты не совпадают — скорректируй API_PATHS ниже.

Формат ответа keywords (проверено 2026-08-27):
  {"current_page": 1, "per_page": N, "last_page": M,
   "data": [{"word": "...", "pos": 14, "ws": 624, "url": "/...", ...}]}
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: pip install requests", file=sys.stderr)
    sys.exit(1)


BASE_URL = "https://api.keys.so"

# Актуальные эндпоинты keys.so (проверено 2026-04-10 по apidoc.keys.so)
API_PATHS = {
    "profile": "/report/simple/domain_dashboard",
    "competitors": "/report/simple/organic/competitors",
    "keys": "/report/simple/organic/keywords",
    "lost": "/report/simple/organic/keywords/lost",
}

# База по умолчанию — регион выдачи Яндекса (msk, spb, ekb и т.д.)
DEFAULT_BASE = "msk"
BASE_HELP = "База keys.so — регион выдачи (msk/spb/ekb и др., default: msk)"

MAX_RETRIES = 3


def load_token() -> str:
    token = os.environ.get("KEYSO_API_TOKEN")
    if token:
        return token
    # Пробуем .env
    env_paths = [
        Path.home() / "Documents/ivanilin/ai-seo/.env",
        Path.cwd() / ".env",
    ]
    for p in env_paths:
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("KEYSO_API_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def api_request(path: str, params: dict, token: str) -> dict:
    headers = {"X-Keyso-TOKEN": token, "Accept": "application/json"}
    url = BASE_URL + path
    last = None
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=60)
        except requests.RequestException as e:
            last = {"status": 0, "url": url, "body": str(e)}
        else:
            last = {"status": r.status_code, "url": r.url, "body": _try_json(r)}
            if r.status_code != 429 and r.status_code < 500:
                return last
        if attempt < MAX_RETRIES - 1:
            delay = 2 ** attempt  # 1s, 2s
            print(f"retry {attempt + 1}/{MAX_RETRIES - 1} after status {last['status']}, sleep {delay}s", file=sys.stderr)
            time.sleep(delay)
    return last


def _try_json(r):
    try:
        return r.json()
    except Exception:
        return r.text[:2000]


def normalize_phrase(phrase: str) -> str:
    """Нормализация для сравнения: lower, strip, ё→е, схлопывание пробелов."""
    return " ".join(phrase.lower().replace("ё", "е").split())


def fetch_all_keys(domain: str, token: str, base: str, per_page: int = 1000, max_pages: int = 10) -> list:
    """
    Выгружает органические ключи домена постранично.
    Останавливается на last_page из метаданных, пустой странице или max_pages.
    Возвращает список dict'ов как в data[] ответа API.
    """
    rows = []
    page = 1
    last_page = None
    while page <= max_pages:
        result = api_request(
            API_PATHS["keys"],
            {"domain": domain, "base": base, "per_page": per_page, "page": page},
            token,
        )
        if result["status"] != 200:
            print(f"WARN: {domain} page {page} → status {result['status']}, останавливаюсь", file=sys.stderr)
            break
        body = result["body"]
        data = body.get("data", []) if isinstance(body, dict) else []
        if not data:
            break
        rows.extend(data)
        if last_page is None and isinstance(body, dict):
            last_page = body.get("last_page")
        if last_page and page >= last_page:
            break
        page += 1
    truncated = last_page and last_page > max_pages
    note = f" (обрезано: на домене {last_page} страниц, взято {min(page, max_pages)})" if truncated else ""
    print(f"{domain}: получено {len(rows)} ключей{note}", file=sys.stderr)
    return rows


def cmd_check(args, token: str):
    """Проверка живости токена — дергаем domain_dashboard для заведомо рабочего домена."""
    result = api_request(
        API_PATHS["profile"],
        {"domain": "yandex.ru", "base": args.base},
        token,
    )
    if result["status"] == 200:
        print(json.dumps({"ok": True, "status": 200, "message": "Token is alive", "sample": result["body"]}, ensure_ascii=False, indent=2))
        sys.exit(0)
    elif result["status"] == 401:
        print(json.dumps({"ok": False, "status": 401, "message": "Token expired or invalid — update KEYSO_API_TOKEN"}, ensure_ascii=False, indent=2))
        sys.exit(2)
    else:
        print(json.dumps({"ok": False, "status": result["status"], "body": result["body"]}, ensure_ascii=False, indent=2))
        sys.exit(3)


def cmd_profile(args, token: str):
    result = api_request(
        API_PATHS["profile"],
        {"domain": args.domain, "base": args.base},
        token,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_competitors(args, token: str):
    result = api_request(
        API_PATHS["competitors"],
        {"domain": args.domain, "base": args.base, "per_page": args.limit, "page": 1},
        token,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_keys(args, token: str):
    rows = fetch_all_keys(args.domain, token, args.base, per_page=args.per_page, max_pages=args.max_pages)
    print(json.dumps({"domain": args.domain, "total": len(rows), "keys": rows}, ensure_ascii=False, indent=2))


def cmd_gap(args, token: str):
    """
    Честный gap-анализ: ключи, по которым ранжируются конкуренты,
    но нет нашего домена. Выгружает keys по каждому домену и делает
    set-difference по нормализованной фразе (lower, strip, ё→е) в Python.
    """
    our_rows = fetch_all_keys(args.our_domain, token, args.base, per_page=args.per_page, max_pages=args.max_pages)
    our_phrases = {normalize_phrase(row["word"]) for row in our_rows if row.get("word")}

    # gap: normalized phrase → {phrase, ws, competitors: [{domain, pos, url}]}
    gap = {}
    for comp in args.competitors:
        comp_rows = fetch_all_keys(comp, token, args.base, per_page=args.per_page, max_pages=args.max_pages)
        for row in comp_rows:
            word = row.get("word")
            if not word:
                continue
            norm = normalize_phrase(word)
            if norm in our_phrases:
                continue
            entry = gap.setdefault(norm, {"phrase": word, "ws": row.get("ws", 0), "competitors": []})
            entry["ws"] = max(entry["ws"] or 0, row.get("ws", 0) or 0)
            entry["competitors"].append({"domain": comp, "pos": row.get("pos"), "url": row.get("url")})

    # лучший конкурент по позиции для каждого gap-ключа
    for entry in gap.values():
        best = min(entry["competitors"], key=lambda c: c["pos"] if c["pos"] is not None else 999)
        entry["best_pos"] = best["pos"]
        entry["best_competitor"] = best["domain"]
        entry["competitors_count"] = len(entry["competitors"])

    ranked = sorted(gap.values(), key=lambda e: (-(e["ws"] or 0), e["best_pos"] if e["best_pos"] is not None else 999))
    out = {
        "our_domain": args.our_domain,
        "our_keys_total": len(our_phrases),
        "competitors": args.competitors,
        "gap_keys_total": len(ranked),
        "shown": min(len(ranked), args.top),
        "note": "gap = ключ есть хотя бы у одного конкурента и отсутствует у нас (сравнение по нормализованной фразе)",
        "gap_keys": ranked[: args.top],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_lost(args, token: str):
    """Потерянные ключи домена (endpoint lost keys.so) — фразы, где домен выпал из топа. Это НЕ gap vs конкуренты."""
    result = api_request(
        API_PATHS["lost"],
        {"domain": args.domain, "base": args.base, "per_page": args.limit, "page": 1},
        token,
    )
    print(json.dumps({"domain": args.domain, "lost_keywords": result}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Keys.so API client")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="Проверить, что токен живой")
    p_check.add_argument("--base", default=DEFAULT_BASE, help=BASE_HELP)

    p_prof = sub.add_parser("profile", help="Органический профиль домена")
    p_prof.add_argument("domain")
    p_prof.add_argument("--base", default=DEFAULT_BASE, help=BASE_HELP)

    p_comp = sub.add_parser("competitors", help="Список конкурентов домена")
    p_comp.add_argument("domain")
    p_comp.add_argument("--limit", type=int, default=30)
    p_comp.add_argument("--base", default=DEFAULT_BASE, help=BASE_HELP)

    p_keys = sub.add_parser("keys", help="Органические ключи домена (все страницы)")
    p_keys.add_argument("domain")
    p_keys.add_argument("--per-page", type=int, default=1000)
    p_keys.add_argument("--max-pages", type=int, default=10, help="Потолок страниц пагинации (default 10 = до 10000 ключей)")
    p_keys.add_argument("--base", default=DEFAULT_BASE, help=BASE_HELP)

    p_gap = sub.add_parser("gap", help="Gap-ключи: есть у конкурентов, нет у нас (set-difference по keys)")
    p_gap.add_argument("our_domain")
    p_gap.add_argument("competitors", nargs="+")
    p_gap.add_argument("--per-page", type=int, default=1000)
    p_gap.add_argument("--max-pages", type=int, default=10, help="Потолок страниц пагинации на домен")
    p_gap.add_argument("--top", type=int, default=1000, help="Сколько gap-ключей вывести (сортировка по частоте)")
    p_gap.add_argument("--base", default=DEFAULT_BASE, help=BASE_HELP)

    p_lost = sub.add_parser("lost", help="Потерянные ключи домена (endpoint lost, не gap)")
    p_lost.add_argument("domain")
    p_lost.add_argument("--limit", type=int, default=500)
    p_lost.add_argument("--base", default=DEFAULT_BASE, help=BASE_HELP)

    args = parser.parse_args()

    token = load_token()
    if not token:
        print(json.dumps({"error": "KEYSO_API_TOKEN not found in env or ai-seo/.env"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    handlers = {
        "check": cmd_check,
        "profile": cmd_profile,
        "competitors": cmd_competitors,
        "keys": cmd_keys,
        "gap": cmd_gap,
        "lost": cmd_lost,
    }
    handlers[args.cmd](args, token)


if __name__ == "__main__":
    main()
