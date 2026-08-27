#!/usr/bin/env python3
"""
Простой crawler для технического SEO-аудита одной страницы.
Usage: python3 crawl.py <url>
       python3 crawl.py --batch <file_with_urls>   # по URL на строку, вывод JSON-массивом
Output: JSON со всеми важными мета-данными для SEO.
"""
import sys
import json
import re
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEO-Audit/1.0; +https://factor-prodazh.ru)"
}


def collect_jsonld_types(data, out: list):
    """Собирает @type из JSON-LD: разворачивает списки, @graph (Yoast) и списочные @type."""
    if isinstance(data, list):
        for item in data:
            collect_jsonld_types(item, out)
        return
    if not isinstance(data, dict):
        return
    t = data.get("@type")
    if isinstance(t, list):
        out.extend(str(x) for x in t)
    elif t:
        out.append(str(t))
    if "@graph" in data:
        collect_jsonld_types(data["@graph"], out)


def fetch(url: str) -> dict:
    result = {"url": url}
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
    except Exception as e:
        result["error"] = str(e)
        return result

    result["final_url"] = r.url
    result["status"] = r.status_code
    result["redirect_chain"] = [h.url for h in r.history] + [r.url] if r.history else None
    result["content_type"] = r.headers.get("content-type")
    result["content_length_bytes"] = len(r.content)
    result["server"] = r.headers.get("server")
    result["x_powered_by"] = r.headers.get("x-powered-by")
    result["response_time_ms"] = int(r.elapsed.total_seconds() * 1000)

    if "text/html" not in (r.headers.get("content-type") or ""):
        return result

    # Коррекция кодировки: requests при отсутствии charset ставит iso-8859-1 → мойибейк на windows-1251
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = r.apparent_encoding

    soup = BeautifulSoup(r.text, "html.parser")

    # Title
    title_tag = soup.find("title")
    result["title"] = title_tag.get_text(strip=True) if title_tag else None
    result["title_length"] = len(result["title"]) if result["title"] else 0

    # Meta description
    md = soup.find("meta", attrs={"name": "description"})
    result["meta_description"] = md.get("content", "").strip() if md else None
    result["meta_description_length"] = len(result["meta_description"]) if result["meta_description"] else 0

    # Meta keywords (deprecated но смотрим)
    mk = soup.find("meta", attrs={"name": "keywords"})
    result["meta_keywords"] = mk.get("content", "").strip() if mk else None

    # Robots meta
    mr = soup.find("meta", attrs={"name": "robots"})
    result["meta_robots"] = mr.get("content", "").strip() if mr else None

    # Canonical
    canonical = soup.find("link", attrs={"rel": "canonical"})
    result["canonical"] = canonical.get("href") if canonical else None

    # hreflang
    result["hreflang"] = [
        {"lang": link.get("hreflang"), "href": link.get("href")}
        for link in soup.find_all("link", attrs={"rel": "alternate"})
        if link.get("hreflang")
    ]

    # Open Graph
    og = {}
    for tag in soup.find_all("meta"):
        prop = tag.get("property", "")
        if prop.startswith("og:"):
            og[prop[3:]] = tag.get("content", "")
    result["open_graph"] = og or None

    # Headings
    headings = {}
    for i in range(1, 7):
        tags = soup.find_all(f"h{i}")
        headings[f"h{i}_count"] = len(tags)
        if i <= 3:
            headings[f"h{i}_texts"] = [t.get_text(strip=True)[:200] for t in tags[:20]]
    result["headings"] = headings

    # Images без alt
    imgs = soup.find_all("img")
    result["images_total"] = len(imgs)
    result["images_without_alt"] = sum(1 for img in imgs if not img.get("alt"))

    # Внутренние и внешние ссылки
    parsed_base = urlparse(r.url)
    base_domain = parsed_base.netloc
    internal, external = 0, 0
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        full = urljoin(r.url, href)
        if urlparse(full).netloc == base_domain:
            internal += 1
        else:
            external += 1
    result["internal_links"] = internal
    result["external_links"] = external

    # Schema.org (JSON-LD)
    jsonld_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    result["jsonld_blocks"] = len(jsonld_scripts)
    result["jsonld_types"] = []
    for s in jsonld_scripts:
        try:
            data = json.loads(s.string or "{}")
            collect_jsonld_types(data, result["jsonld_types"])
        except Exception:
            pass

    # Видимый текст body (без script/style/noscript) — для SSR-проверки и поиска тонких страниц
    body = soup.find("body")
    if body:
        for tag in body.find_all(["script", "style", "noscript"]):
            tag.decompose()
        visible_text = " ".join(body.get_text(separator=" ").split())
        result["visible_text_length"] = len(visible_text)
    else:
        result["visible_text_length"] = 0

    # Viewport (мобилка)
    vp = soup.find("meta", attrs={"name": "viewport"})
    result["viewport"] = vp.get("content") if vp else None

    # lang
    html_tag = soup.find("html")
    result["html_lang"] = html_tag.get("lang") if html_tag else None

    return result


def normalize_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 crawl.py <url>\n       python3 crawl.py --batch <file_with_urls>", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Usage: python3 crawl.py --batch <file_with_urls>", file=sys.stderr)
            sys.exit(1)
        with open(sys.argv[2]) as f:
            urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        results = []
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url}", file=sys.stderr)
            results.append(fetch(normalize_url(url)))
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    data = fetch(normalize_url(sys.argv[1]))
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
