#!/usr/bin/env python3
"""
Build a self-contained HTML audit report from research/*.md files.

Styled in compact consultant-deliverable format (inspired by factor/reports/seo-strategy-factor.html).
Reads design tokens from <project>/data/design-tokens.md if present — uses brand colors/fonts.

Usage:
    python3 build_report.py <project_path> [--accent "#hex"] [--client "Name"]

Input:
    <project>/research/audit-summary.md   (main document)
    <project>/research/*.md               (other sections)
    <project>/data/brief.md               (client name + URL for hero)
    <project>/data/design-tokens.md       (OPTIONAL brand colors/fonts)

Output:
    <project>/reports/audit-report.html
"""
import argparse
import re
import sys
import datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    print("ERROR: pip3 install --user markdown pygments", file=sys.stderr)
    sys.exit(1)


SECTION_ORDER = ["audit-summary", "gap-analysis", "content-audit", "tech-seo-audit"]

SECTION_META = {
    "audit-summary":   {"title": "Сводный отчёт",        "tag": "SUMMARY"},
    "gap-analysis":    {"title": "Gap-анализ конкурентов", "tag": "GAP"},
    "content-audit":   {"title": "Контент и семантика", "tag": "CONTENT"},
    "tech-seo-audit":  {"title": "Технический SEO",      "tag": "TECH"},
}
DEFAULT_SECTION = {"title": "Дополнительно", "tag": "EXTRA"}


def parse_brief(brief_path: Path) -> dict:
    out = {"client": "", "url": "", "niche": "", "region": ""}
    if not brief_path.exists():
        return out
    text = brief_path.read_text(encoding="utf-8")

    def get(label):
        m = re.search(rf"\|\s*{label}\s*\|\s*([^|\n]+?)\s*\|", text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    out["url"] = get("URL")
    out["client"] = get("Название")
    out["niche"] = get("Ниша")
    out["region"] = get("Целевой регион") or get("География поиска")
    return out


def parse_design_tokens(tokens_path: Path) -> dict:
    """Extract brand colors + fonts from design-tokens.md if present.

    Looks for:
    - Table rows with "Primary accent", "Background main", "Text primary" etc
    - Fenced code block with Google Fonts URLs
    """
    defaults = {
        "accent": "#453FDF",
        "accent_soft": "#eef0ff",
        "text": "#1a1a1a",
        "text_soft": "#333",
        "bg": "#fafafa",
        "card": "#ffffff",
        "border": "#e5e5e5",
        "hero_bg": "#1a1a1a",
        "crit": "#c01020",
        "warn": "#e89020",
        "ok": "#16a34a",
        "font_headline": "Inter",
        "font_body": "Inter",
        "font_weights": "400;500;600;700;800",
    }
    if not tokens_path.exists():
        return defaults

    text = tokens_path.read_text(encoding="utf-8")

    def find_hex(label_keywords):
        for kw in label_keywords:
            m = re.search(rf"\|[^|]*{kw}[^|]*\|\s*`?(#[0-9A-Fa-f]{{6}})`?", text, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    tokens = dict(defaults)
    accent = find_hex(["primary accent", "brand", "Primary accent"])
    if accent:
        tokens["accent"] = accent
    accent_soft = find_hex(["soft accent bg", "soft accent", "accent bg"])
    if accent_soft:
        tokens["accent_soft"] = accent_soft
    text_primary = find_hex(["text primary"])
    if text_primary:
        tokens["text_soft"] = text_primary
    text_dark = find_hex(["text darker", "text dark"])
    if text_dark:
        tokens["text"] = text_dark
        tokens["hero_bg"] = text_dark
    bg_main = find_hex(["background main", "bg main"])
    if bg_main:
        tokens["bg"] = bg_main
    border = find_hex(["^border$", "border "])
    if border:
        tokens["border"] = border
    crit = find_hex(["pink", "magenta", "cta", "critical"])
    if crit:
        tokens["crit"] = crit

    # Fonts
    font_block = re.search(r"Manrope[^`\n]*", text)
    if "Manrope" in text:
        tokens["font_headline"] = "Manrope"
    if "Inter" in text:
        tokens["font_body"] = "Inter"

    return tokens


def read_md_files(research_dir: Path) -> dict:
    files = {}
    for md in research_dir.glob("*.md"):
        files[md.stem] = md.read_text(encoding="utf-8")
    return files


def strip_h1(md_text: str) -> tuple:
    lines = md_text.splitlines()
    title = ""
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            start = i + 1
            break
    return title, "\n".join(lines[start:]).lstrip("\n")


def md_to_html(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists", "smarty"],
        output_format="html5",
    )


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={font_headline_url}:wght@400;500;600;700;800&family={font_body_url}:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: {bg};
  --card: {card};
  --text: {text};
  --text-soft: {text_soft};
  --muted: #6b6b6b;
  --muted2: #9a9a9a;
  --accent: {accent};
  --accent-soft: {accent_soft};
  --border: {border};
  --border-soft: #f0f0f0;
  --crit: {crit};
  --warn: {warn};
  --ok: {ok};
  --hero-bg: {hero_bg};
  --font-h: '{font_headline}', 'Inter', system-ui, sans-serif;
  --font-b: '{font_body}', 'Inter', system-ui, sans-serif;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 24px; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-b);
  font-size: 15px;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  font-feature-settings: 'tnum', 'lnum';
}}
.wrap {{ max-width: 820px; margin: 0 auto; padding: 0 28px; }}

/* Hero */
.hero {{
  background: var(--hero-bg);
  color: #fff;
  padding: 48px 0 38px;
}}
.hero-label {{
  font-family: var(--font-h);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 12px;
}}
.hero h1 {{
  font-family: var(--font-h);
  font-size: 32px;
  font-weight: 800;
  color: #fff;
  line-height: 1.15;
  letter-spacing: -0.4px;
  margin-bottom: 10px;
}}
.hero-sub {{
  font-size: 15px;
  color: rgba(255,255,255,0.65);
  font-weight: 400;
}}
.hero-meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  margin-top: 22px;
  padding-top: 20px;
  border-top: 1px solid rgba(255,255,255,0.12);
}}
.hero-meta > div {{ min-width: 120px; }}
.hero-meta .label {{
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.4);
  margin-bottom: 3px;
}}
.hero-meta .value {{
  font-size: 13px;
  color: #fff;
  font-weight: 500;
}}
.hero-meta .value a {{
  color: #fff;
  text-decoration: none;
  border-bottom: 1px dotted rgba(255,255,255,0.4);
}}

/* TOC strip */
.toc-strip {{
  background: var(--card);
  border-bottom: 1px solid var(--border);
  padding: 14px 0;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(8px);
  background: rgba(255,255,255,0.92);
}}
.toc-strip ul {{
  display: flex;
  gap: 4px;
  list-style: none;
  flex-wrap: wrap;
}}
.toc-strip a {{
  display: inline-block;
  font-family: var(--font-h);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: var(--muted);
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.15s;
}}
.toc-strip a:hover {{
  background: var(--accent-soft);
  color: var(--accent);
}}

/* Content */
.content {{ padding: 40px 0 48px; }}

.section {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 34px 38px;
  margin-bottom: 22px;
  scroll-margin-top: 80px;
}}
.section-head {{
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 6px;
}}
.section-num {{
  font-family: var(--font-h);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--accent);
}}
.section h2.section-title {{
  font-family: var(--font-h);
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.3px;
  line-height: 1.25;
  margin: 4px 0 18px;
}}

/* Markdown content inside sections */
.md {{ font-size: 14.5px; line-height: 1.7; color: var(--text-soft); }}
.md > *:first-child {{ margin-top: 0; }}
.md > *:last-child {{ margin-bottom: 0; }}

.md h1 {{ display: none; }}
.md h2 {{
  font-family: var(--font-h);
  font-size: 18px;
  font-weight: 800;
  color: var(--text);
  margin: 32px 0 10px;
  letter-spacing: -0.2px;
  line-height: 1.3;
}}
.md h3 {{
  font-family: var(--font-h);
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  margin: 22px 0 8px;
  letter-spacing: -0.1px;
}}
.md h4 {{
  font-family: var(--font-h);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--muted);
  margin: 18px 0 6px;
}}
.md p {{ margin: 0 0 12px; }}
.md strong {{ font-weight: 700; color: var(--text); }}
.md em {{ font-style: italic; color: var(--muted); }}

.md ul, .md ol {{ margin: 0 0 14px; padding-left: 22px; }}
.md li {{ margin-bottom: 4px; }}
.md li::marker {{ color: var(--accent); }}

.md a {{
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid;
  border-color: color-mix(in srgb, var(--accent) 30%, transparent);
}}
.md a:hover {{ border-color: var(--accent); }}

.md code {{
  font-family: 'JetBrains Mono', ui-monospace, 'SF Mono', monospace;
  font-size: 0.87em;
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--text);
}}
.md pre {{
  background: #1a1a1a;
  color: #e0e0e0;
  padding: 14px 18px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 14px 0;
  font-size: 12.5px;
  line-height: 1.55;
}}
.md pre code {{ background: none; padding: 0; color: inherit; }}

.md blockquote {{
  margin: 14px 0;
  padding: 12px 18px;
  border-left: 3px solid var(--accent);
  background: var(--accent-soft);
  color: var(--text-soft);
  border-radius: 0 6px 6px 0;
}}
.md blockquote p:last-child {{ margin-bottom: 0; }}

.md hr {{
  border: none;
  border-top: 1px solid var(--border-soft);
  margin: 28px 0;
}}

.md table {{
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0 18px;
  font-size: 13px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}}
.md table th {{
  text-align: left;
  padding: 10px 12px;
  background: #f8f8f8;
  font-family: var(--font-h);
  border-bottom: 1px solid var(--border);
  font-weight: 700;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--muted);
  white-space: nowrap;
}}
.md table td {{
  padding: 9px 12px;
  border-bottom: 1px solid var(--border-soft);
  vertical-align: top;
}}
.md table tr:last-child td {{ border-bottom: none; }}
.md table tr:hover td {{ background: #fafbfc; }}

.md input[type="checkbox"] {{
  margin-right: 6px;
  accent-color: var(--accent);
}}

/* Footer */
footer {{
  border-top: 1px solid var(--border);
  padding: 20px 0 40px;
  text-align: center;
  font-size: 11px;
  color: var(--muted2);
  margin-top: 20px;
}}
footer code {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  background: #f0f0f0;
  padding: 2px 7px;
  border-radius: 3px;
  color: var(--muted);
}}
footer .files {{
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 10px;
}}

/* Responsive */
@media (max-width: 640px) {{
  .wrap {{ padding: 0 18px; }}
  .hero h1 {{ font-size: 24px; }}
  .section {{ padding: 24px 20px; }}
  .section h2.section-title {{ font-size: 20px; }}
  .md table {{ font-size: 11.5px; }}
  .md table th, .md table td {{ padding: 7px 8px; }}
}}

/* Print */
@media print {{
  body {{ background: #fff; font-size: 10.5pt; }}
  .hero {{
    background: var(--hero-bg) !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    padding: 24px 0;
  }}
  .hero h1 {{ font-size: 22pt; }}
  .toc-strip {{ display: none; }}
  .section {{
    break-inside: avoid-page;
    border: none;
    padding: 16px 0;
    margin-bottom: 8px;
    box-shadow: none;
  }}
  .section h2.section-title {{ font-size: 16pt; }}
  .md h2 {{ font-size: 13pt; break-after: avoid; }}
  .md h3 {{ break-after: avoid; }}
  .md table, .md pre, .md blockquote {{ break-inside: avoid; }}
  footer {{ display: none; }}
}}
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <div class="hero-label">Маркетинг-аудит</div>
    <h1>{hero_title}</h1>
    <p class="hero-sub">{hero_subtitle}</p>
    <div class="hero-meta">
      <div><div class="label">URL</div><div class="value">{url_link}</div></div>
      <div><div class="label">Ниша</div><div class="value">{niche}</div></div>
      <div><div class="label">Регион</div><div class="value">{region}</div></div>
      <div><div class="label">Дата</div><div class="value">{date}</div></div>
    </div>
  </div>
</header>

<nav class="toc-strip">
  <div class="wrap">{toc}</div>
</nav>

<main class="content">
  <div class="wrap">
    {sections_html}
  </div>
</main>

<footer>
  <div class="wrap">
    <div>Сгенерировано автоматически из research/*.md · {date}</div>
    <div class="files">{file_chips}</div>
  </div>
</footer>

</body>
</html>
"""


DARK_TOKENS = {
    "bg": "#0c0e11",
    "card": "#141720",
    "text": "#eef0f5",
    "text_soft": "#b0b8cc",
    "muted": "#636e88",
    "accent": "#4e7fff",
    "accent_soft": "rgba(78,127,255,0.14)",
    "border": "rgba(255,255,255,0.07)",
    "border_soft": "rgba(255,255,255,0.12)",
    "hero_bg": "#141720",
    "crit": "#e05252",
    "warn": "#d4813a",
    "ok": "#4fb86a",
}

DARK_CSS_PATCH = """
/* dark-mode overrides */
.toc-strip { background: rgba(12,14,17,0.92) !important; border-color: rgba(255,255,255,0.07) !important; }
.toc-strip a { color: #b0b8cc !important; }
.toc-strip a:hover, .toc-strip a.active { color: #4e7fff !important; background: rgba(78,127,255,0.12) !important; }
.section { background: #141720 !important; border-color: rgba(255,255,255,0.07) !important; }
.section-head { border-color: rgba(255,255,255,0.07) !important; }
.md table th { background: #1c2030 !important; color: #eef0f5 !important; }
.md table td { border-color: rgba(255,255,255,0.07) !important; }
.md table tr:hover { background: rgba(78,127,255,0.06) !important; }
.md code { background: #1c2030 !important; color: #eef0f5 !important; }
.md pre { background: #1c2030 !important; }
.md blockquote { border-color: #4e7fff !important; background: rgba(78,127,255,0.08) !important; }
.footer { background: #141720 !important; border-color: rgba(255,255,255,0.07) !important; color: #636e88 !important; }
"""


def build_report(project_path: Path, accent_override: str = None, client_override: str = None, dark: bool = False) -> Path:
    research_dir = project_path / "research"
    reports_dir = project_path / "reports"
    brief_path = project_path / "data" / "brief.md"
    tokens_path = project_path / "data" / "design-tokens.md"

    if not research_dir.exists():
        print(f"ERROR: {research_dir} does not exist", file=sys.stderr)
        sys.exit(1)
    summary_path = research_dir / "audit-summary.md"
    if not summary_path.exists():
        print(f"ERROR: {summary_path} missing", file=sys.stderr)
        sys.exit(1)

    reports_dir.mkdir(parents=True, exist_ok=True)

    brief = parse_brief(brief_path)
    if client_override:
        brief["client"] = client_override

    tokens = parse_design_tokens(tokens_path)
    if dark:
        tokens.update(DARK_TOKENS)
    if accent_override:
        tokens["accent"] = accent_override

    files = read_md_files(research_dir)

    ordered_keys = [k for k in SECTION_ORDER if k in files]
    for k in sorted(files.keys()):
        if k not in ordered_keys:
            ordered_keys.append(k)

    sections_list = []
    for idx, key in enumerate(ordered_keys, start=1):
        md_text = files[key]
        h1_title, body = strip_h1(md_text)
        meta = SECTION_META.get(key, DEFAULT_SECTION)
        display_title = meta["title"] if key in SECTION_META else (h1_title or key)
        tag = meta["tag"]

        body_html = md_to_html(body)
        sec_html = f'''
<section class="section" id="section-{key}">
  <div class="section-head">
    <span class="section-num">{idx:02d} · {tag}</span>
  </div>
  <h2 class="section-title">{display_title}</h2>
  <div class="md">{body_html}</div>
</section>
'''
        sections_list.append((key, display_title, sec_html))

    toc_items = "".join(
        f'<li><a href="#section-{k}">{t}</a></li>'
        for k, t, _ in sections_list
    )
    toc_html = f"<ul>{toc_items}</ul>"
    sections_html = "\n".join(s[2] for s in sections_list)

    client_name = brief.get("client") or project_path.name
    url = brief.get("url") or ""
    niche = brief.get("niche") or "—"
    region = brief.get("region") or "—"
    url_link = f'<a href="{url}" target="_blank">{url}</a>' if url else "—"
    date_str = datetime.date.today().isoformat()
    file_chips = " ".join(f"<code>{k}.md</code>" for k in ordered_keys)

    html = HTML_TEMPLATE.format(
        title=f"Маркетинг-аудит — {client_name}",
        bg=tokens["bg"],
        card=tokens["card"],
        text=tokens["text"],
        text_soft=tokens["text_soft"],
        accent=tokens["accent"],
        accent_soft=tokens["accent_soft"],
        border=tokens["border"],
        crit=tokens["crit"],
        warn=tokens["warn"],
        ok=tokens["ok"],
        hero_bg=tokens["hero_bg"],
        font_headline=tokens["font_headline"],
        font_body=tokens["font_body"],
        font_headline_url=tokens["font_headline"].replace(" ", "+"),
        font_body_url=tokens["font_body"].replace(" ", "+"),
        hero_title=client_name,
        hero_subtitle=f"Маркетинг-аудит и SEO-стратегия · {url}" if url else "Маркетинг-аудит и SEO-стратегия",
        url_link=url_link,
        niche=niche,
        region=region,
        date=date_str,
        toc=toc_html,
        sections_html=sections_html,
        file_chips=file_chips,
    )

    if dark:
        html = html.replace("</style>", DARK_CSS_PATCH + "\n</style>", 1)

    output_path = reports_dir / "audit-report.html"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path")
    parser.add_argument("--accent", default=None)
    parser.add_argument("--client", default=None)
    parser.add_argument("--dark", action="store_true", help="Dark theme (like aimclo)")
    args = parser.parse_args()

    path = Path(args.project_path).expanduser().resolve()
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        sys.exit(1)

    output = build_report(path, accent_override=args.accent, client_override=args.client, dark=args.dark)
    size_kb = output.stat().st_size / 1024
    print(f"✓ Report built: {output}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Open: open {output}")


if __name__ == "__main__":
    main()
