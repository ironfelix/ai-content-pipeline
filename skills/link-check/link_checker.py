#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Чекер битых ссылок по сайту. Берёт все страницы из sitemap, на каждой
собирает ссылки, проверяет HTTP-статусы. Вежливый (ограниченный параллелизм).

Usage:
  python3 link_checker.py <domain> [max_pages] [--external] [--workers N]

  <domain>     https://crmgroup.ru  (с протоколом)
  max_pages    сколько страниц проверить (0 или пусто = все из sitemap)
  --external   проверять и внешние ссылки (по умолчанию только внутренние)
  --workers N  параллелизм (по умолчанию 8; для слабых серверов ставь 4)

Пример: python3 link_checker.py https://crmgroup.ru 0 --external
"""
import sys, re, ssl, urllib.request, urllib.parse, concurrent.futures, collections

UA = "Mozilla/5.0 (compatible; link-check/1.0)"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# WP-системный шум + ресурсные домены (шрифты/трекеры) — не считаем «битыми»
IGNORE = re.compile(
    r'xmlrpc\.php|/wp-login|/wp-admin|/feed/?(\?|$)|/feed$|=[^&]*?/feed|\?replytocom|\?rsd\b|\?pingback|/comment-page|/trackback'
    r'|fonts\.googleapis\.com|fonts\.gstatic\.com|//mc\.yandex|google-analytics\.com|googletagmanager\.com|//cdn\.|//ajax\.googleapis',
    re.I)

import time as _time
def fetch(url, method="GET", timeout=20, retries=2):
    url = urllib.parse.quote(url, safe=":/?&=#%+~@!$'()*,;[]")  # кодируем кириллицу/не-ASCII
    last = (0, "")
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
            r = urllib.request.urlopen(req, timeout=timeout, context=CTX)
            body = r.read().decode("utf-8", "ignore") if method == "GET" else ""
            return r.status, body
        except urllib.error.HTTPError as e:
            return e.code, ""          # реальный HTTP-код (404 и т.п.) — не ретраим
        except Exception as e:
            last = (0, str(e)[:50])    # таймаут/DNS — транзиент, ретраим
            if attempt < retries:
                _time.sleep(1.5)
    return last

def sitemap_urls(domain):
    urls, seen = set(), set()
    def parse(sm):
        if sm in seen:
            return
        seen.add(sm)
        st, body = fetch(sm, timeout=30, retries=4)   # sitemap читаем настойчивее
        if st != 200:
            return
        for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body):
            (parse if loc.lower().endswith(".xml") else urls.add)(loc)
    for sm in ("/sitemap_index.xml", "/sitemap.xml", "/wp-sitemap.xml"):
        parse(domain.rstrip("/") + sm)
        if urls:
            break
    return sorted(urls)

def extract_links(html, base):
    out = set()
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html):
        href = m.group(1).strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
            continue
        full = urllib.parse.urljoin(base, href).split("#")[0].rstrip("/")
        if full.startswith("http") and not IGNORE.search(full):
            out.add(full)
    return out

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    domain = sys.argv[1].rstrip("/")
    host = urllib.parse.urlparse(domain).netloc
    args = sys.argv[2:]
    external = "--external" in args
    workers = 8
    if "--workers" in args:
        workers = int(args[args.index("--workers") + 1])
    # позиционные числа: пропускаем значения опций (иначе `--workers 4` даст max_pages=4)
    nums, skip_next = [], False
    for a in args:
        if skip_next:
            skip_next = False
            continue
        if a == "--workers":
            skip_next = True
            continue
        if a.isdigit():
            nums.append(a)
    max_pages = int(nums[0]) if nums else 0

    pages = sitemap_urls(domain)
    if not pages:
        print("⚠️ sitemap не найден — проверь домен/sitemap"); return
    if max_pages:
        pages = pages[:max_pages]
    print(f"Сайт: {domain} | страниц в карте: {len(pages)} | внешние: {'да' if external else 'нет'} | воркеров: {workers}")

    src = collections.defaultdict(set)   # ссылка -> {страницы-источники}
    bad_pages = []
    def crawl(pg):
        st, html = fetch(pg)
        if st == 200:
            for l in extract_links(html, pg):
                src[l].add(pg)
        elif st != 200:
            bad_pages.append((st, pg))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(crawl, pages))

    links = list(src)
    if not external:
        links = [l for l in links if urllib.parse.urlparse(l).netloc == host]
    print(f"Уникальных ссылок к проверке: {len(links)}")

    broken = []
    def check(l):
        st, _ = fetch(l, method="HEAD")
        if st in (0, 403, 405, 501):           # HEAD не поддержан/запрещён → GET
            st, _ = fetch(l, method="GET")
        return l, st
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for l, st in ex.map(check, links):
            if st == 0 or st >= 400:
                broken.append((st, l))

    if bad_pages:
        print(f"\n⚠️ Страницы sitemap с не-200 ({len(bad_pages)}):")
        for st, pg in sorted(bad_pages):
            print(f"  [{st}] {pg}")

    dead = sorted([(st, l) for st, l in broken if st in (404, 410) or 500 <= st < 600])
    unver = sorted([(st, l) for st, l in broken if not (st in (404, 410) or 500 <= st < 600)],
                   key=lambda x: (-1 if x[0] == 0 else x[0]))
    def show(items, title):
        print(f"\n{'='*60}\n{title}: {len(items)}\n{'='*60}")
        for st, l in items:
            label = "TIMEOUT/ERR" if st == 0 else st
            print(f"\n[{label}] {l}")
            for s in sorted(src[l])[:4]:
                print(f"      ← {s}")
    show(dead, "🔴 ТОЧНО МЁРТВЫЕ (404/410/5xx) — чинить")
    show(unver, "🟡 НЕ ПРОВЕРИЛИСЬ (403/429/таймаут — часто бот-блок соцсетей, глянуть вручную)")
    if not broken:
        print("\n✅ битых ссылок не найдено")

if __name__ == "__main__":
    main()
