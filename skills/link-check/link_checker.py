#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Чекер битых ссылок по сайту. Берёт все страницы из sitemap, на каждой
собирает ссылки, проверяет HTTP-статусы. Вежливый (ограниченный параллелизм,
per-host rate limit ≥1 с для внешних хостов).

Usage:
  python3 link_checker.py <domain> [max_pages] [--external] [--workers N] [--json out.json]

  <domain>       https://crmgroup.ru  (с протоколом)
  max_pages      сколько страниц проверить (0 или пусто = все из sitemap)
  --external     проверять и внешние ссылки (по умолчанию только внутренние)
  --workers N    параллелизм (по умолчанию 8; для слабых серверов ставь 4)
  --json out.json  дополнительно записать машиночитаемый отчёт (тот же состав, что stdout)

Пример: python3 link_checker.py https://crmgroup.ru 0 --external --json report.json

Особенности:
  - sitemap поддерживает .xml.gz (по magic-байтам gzip)
  - хосты с невалидным SSL-сертификатом помечаются ssl_invalid и выводятся
    отдельной секцией — даже если контент отдался (не считаем живыми молча)
"""
import sys, re, ssl, json, gzip, time, threading
import urllib.request, urllib.parse, urllib.error
import concurrent.futures, collections

UA = "Mozilla/5.0 (compatible; link-check/1.0)"

VERIFY_CTX = ssl.create_default_context()
NOVERIFY_CTX = ssl.create_default_context()
NOVERIFY_CTX.check_hostname = False
NOVERIFY_CTX.verify_mode = ssl.CERT_NONE

MAIN_HOST = ""                     # свой хост — без rate limit
HOST_RATE_INTERVAL = 1.0           # сек между запросами к одному внешнему хосту
_rate_lock = threading.Lock()
_host_next = {}                    # netloc -> monotonic-время, когда можно следующий запрос

_ssl_lock = threading.Lock()
ssl_invalid_hosts = set()          # netloc с невалидным сертификатом

# WP-системный шум + ресурсные домены (шрифты/трекеры) — не считаем «битыми»
IGNORE = re.compile(
    r'xmlrpc\.php|/wp-login|/wp-admin|/feed/?(\?|$)|/feed$|=[^&]*?/feed|\?replytocom|\?rsd\b|\?pingback|/comment-page|/trackback'
    r'|fonts\.googleapis\.com|fonts\.gstatic\.com|//mc\.yandex|google-analytics\.com|googletagmanager\.com|//cdn\.|//ajax\.googleapis',
    re.I)


def _rate_limit(netloc):
    """≥1 с между запросами к одному внешнему хосту (свой хост не тормозим)."""
    if not netloc or netloc == MAIN_HOST:
        return
    with _rate_lock:
        now = time.monotonic()
        start = max(now, _host_next.get(netloc, 0.0))
        _host_next[netloc] = start + HOST_RATE_INTERVAL
    delay = start - now
    if delay > 0:
        time.sleep(delay)


def _is_cert_error(e):
    if isinstance(e, ssl.SSLCertVerificationError):
        return True
    reason = getattr(e, "reason", None)
    if isinstance(reason, ssl.SSLCertVerificationError):
        return True
    return "CERTIFICATE_VERIFY_FAILED" in str(e)


def fetch(url, method="GET", timeout=20, retries=2):
    url = urllib.parse.quote(url, safe=":/?&=#%+~@!$'()*,;[]")  # кодируем кириллицу/не-ASCII
    netloc = urllib.parse.urlparse(url).netloc
    last = (0, "")
    for attempt in range(retries + 1):
        _rate_limit(netloc)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
            try:
                r = urllib.request.urlopen(req, timeout=timeout, context=VERIFY_CTX)
            except urllib.error.HTTPError:
                raise                                      # реальный HTTP-код — наружу
            except Exception as e:
                if not _is_cert_error(e):
                    raise
                # битый сертификат: помечаем хост и дожимаем без верификации
                with _ssl_lock:
                    ssl_invalid_hosts.add(netloc)
                r = urllib.request.urlopen(req, timeout=timeout, context=NOVERIFY_CTX)
            raw = r.read() if method == "GET" else b""
            if raw[:2] == b"\x1f\x8b":                    # gzip magic (.xml.gz и т.п.)
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    pass
            return r.status, raw.decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            return e.code, ""          # реальный HTTP-код (404 и т.п.) — не ретраим
        except Exception as e:
            last = (0, str(e)[:50])    # таймаут/DNS — транзиент, ретраим
            if attempt < retries:
                time.sleep(1.5)
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
            if loc.lower().endswith((".xml", ".xml.gz")):
                parse(loc)
            else:
                urls.add(loc)
    for sm in ("/sitemap_index.xml", "/sitemap.xml", "/sitemap.xml.gz", "/wp-sitemap.xml"):
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
    global MAIN_HOST
    if len(sys.argv) < 2:
        print(__doc__); return
    domain = sys.argv[1].rstrip("/")
    host = urllib.parse.urlparse(domain).netloc
    MAIN_HOST = host
    args = sys.argv[2:]
    external = "--external" in args
    workers = 8
    if "--workers" in args:
        workers = int(args[args.index("--workers") + 1])
    json_path = None
    if "--json" in args:
        json_path = args[args.index("--json") + 1]
    # позиционные числа: пропускаем значения опций (иначе `--workers 4` даст max_pages=4)
    nums, skip_next = [], False
    for a in args:
        if skip_next:
            skip_next = False
            continue
        if a in ("--workers", "--json"):
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
    src_lock = threading.Lock()
    bad_pages = []
    bad_pages_lock = threading.Lock()
    def crawl(pg):
        st, html = fetch(pg)
        if st == 200:
            links = extract_links(html, pg)
            with src_lock:
                for l in links:
                    src[l].add(pg)
        else:
            with bad_pages_lock:
                bad_pages.append((st, pg))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(crawl, pages))

    links = list(src)
    if not external:
        links = [l for l in links if urllib.parse.urlparse(l).netloc == host]
    print(f"Уникальных ссылок к проверке: {len(links)}")

    broken = []
    alive = []
    def check(l):
        st, _ = fetch(l, method="HEAD")
        if st in (0, 403, 405, 501):           # HEAD не поддержан/запрещён → GET
            st, _ = fetch(l, method="GET")
        return l, st
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for l, st in ex.map(check, links):
            if st == 0 or st >= 400:
                broken.append((st, l))
            else:
                alive.append((st, l))

    if bad_pages:
        print(f"\n⚠️ Страницы sitemap с не-200 ({len(bad_pages)}):")
        for st, pg in sorted(bad_pages):
            print(f"  [{st}] {pg}")

    def is_ssl_invalid(l):
        return urllib.parse.urlparse(l).netloc in ssl_invalid_hosts

    dead = sorted([(st, l) for st, l in broken if st in (404, 410) or 500 <= st < 600])
    unver = sorted([(st, l) for st, l in broken if not (st in (404, 410) or 500 <= st < 600)],
                   key=lambda x: (-1 if x[0] == 0 else x[0]))
    ssl_alive = sorted([(st, l) for st, l in alive if is_ssl_invalid(l)])

    def show(items, title):
        print(f"\n{'='*60}\n{title}: {len(items)}\n{'='*60}")
        for st, l in items:
            label = "TIMEOUT/ERR" if st == 0 else st
            flag = " [SSL_INVALID]" if is_ssl_invalid(l) else ""
            print(f"\n[{label}]{flag} {l}")
            for s in sorted(src[l])[:4]:
                print(f"      ← {s}")
    show(dead, "🔴 ТОЧНО МЁРТВЫЕ (404/410/5xx) — чинить")
    show(unver, "🟡 НЕ ПРОВЕРИЛИСЬ (403/429/таймаут — часто бот-блок соцсетей, глянуть вручную)")
    if ssl_alive:
        show(ssl_alive, "🟠 SSL НЕВАЛИДЕН (контент отдаётся, но сертификат битый — не считать живыми молча)")
    if not broken and not ssl_alive:
        print("\n✅ битых ссылок не найдено")

    if json_path:
        def as_items(items):
            return [{"status": st, "url": l, "ssl_invalid": is_ssl_invalid(l),
                     "sources": sorted(src[l])} for st, l in items]
        report = {
            "domain": domain,
            "pages_in_sitemap": len(pages),
            "external_checked": external,
            "links_checked": len(links),
            "bad_sitemap_pages": [{"status": st, "url": pg} for st, pg in sorted(bad_pages)],
            "dead": as_items(dead),
            "unverified": as_items(unver),
            "ssl_invalid_alive": as_items(ssl_alive),
            "ssl_invalid_hosts": sorted(ssl_invalid_hosts),
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 JSON-отчёт: {json_path}")

if __name__ == "__main__":
    main()
