#!/usr/bin/env python3
"""
Keys.so API client — минимальная обёртка для SEO-аудита.

Usage:
  python3 keyso_client.py check
  python3 keyso_client.py profile <domain> [--base ru]
  python3 keyso_client.py competitors <domain> [--limit 30] [--base ru]
  python3 keyso_client.py keys <domain> [--limit 1000] [--base ru]
  python3 keyso_client.py gap <our_domain> <comp1> [<comp2> ...] [--base ru]

Токен берётся из переменной окружения KEYSO_API_TOKEN или из ai-seo/.env.
Header: X-Keyso-TOKEN
Base URL: https://api.keys.so/

Документация keys.so API: https://www.keys.so/ru/api-doc
Если эндпоинты не совпадают — скорректируй API_PATHS ниже.
"""
import os
import sys
import json
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

# База по умолчанию (msk, spb, yarus, ekb и т.д.)
DEFAULT_BASE = "msk"


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
    r = requests.get(url, headers=headers, params=params, timeout=60)
    return {
        "status": r.status_code,
        "url": r.url,
        "body": _try_json(r),
    }


def _try_json(r):
    try:
        return r.json()
    except Exception:
        return r.text[:2000]


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
    result = api_request(
        API_PATHS["keys"],
        {"domain": args.domain, "base": args.base, "per_page": args.limit, "page": 1},
        token,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_gap(args, token: str):
    """
    Gap-анализ (lost keywords): фразы, где наш домен не в топе,
    но исторически был или конкуренты ранжируются.

    ВАЖНО: keys.so lost endpoint не принимает список конкурентов.
    Для полноценного gap vs конкретных конкурентов — используй
    стратегию через cmd_keys: получить ключи каждого конкурента
    и вычесть из них ключи нашего домена в Python.
    """
    result = api_request(
        API_PATHS["lost"],
        {"domain": args.our_domain, "base": args.base, "per_page": args.limit, "page": 1},
        token,
    )
    print(json.dumps({"our_domain": args.our_domain, "lost_keywords": result}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Keys.so API client")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="Проверить, что токен живой")
    p_check.add_argument("--base", default="msk", help="База keys.so (ru/by/kz/ua)")

    p_prof = sub.add_parser("profile", help="Органический профиль домена")
    p_prof.add_argument("domain")
    p_prof.add_argument("--base", default="msk")

    p_comp = sub.add_parser("competitors", help="Список конкурентов домена")
    p_comp.add_argument("domain")
    p_comp.add_argument("--limit", type=int, default=30)
    p_comp.add_argument("--base", default="msk")

    p_keys = sub.add_parser("keys", help="Органические ключи домена")
    p_keys.add_argument("domain")
    p_keys.add_argument("--limit", type=int, default=1000)
    p_keys.add_argument("--base", default="msk")

    p_gap = sub.add_parser("gap", help="Gap-ключи vs конкуренты")
    p_gap.add_argument("our_domain")
    p_gap.add_argument("competitors", nargs="+")
    p_gap.add_argument("--limit", type=int, default=500)
    p_gap.add_argument("--base", default="msk")

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
    }
    handlers[args.cmd](args, token)


if __name__ == "__main__":
    main()
