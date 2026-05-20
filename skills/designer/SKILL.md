---
name: designer
description: Дизайнер инфографики для статей — два режима: Pencil MCP (если есть data/design-tokens.md клиента) или HTML→Playwright (Фактор Продаж). Анализирует WP черновик, находит 2–3 места для визуализации, генерирует схемы в стиле клиента, загружает PNG в WP медиатеку и вставляет в контент. Запускать после /editor, перед /seo-optimizer. Вызывать командой /designer.
---

# Designer — инфографика для статей

## Шаг 0 — Определить режим

Проверить два условия:

```python
import os

# 1. project.md в текущей директории
config_path = os.path.join(os.getcwd(), "project.md")
has_project = os.path.exists(config_path)

# 2. data/design-tokens.md клиента (признак клиентского проекта)
tokens_path = os.path.join(os.getcwd(), "data", "design-tokens.md")
has_tokens = os.path.exists(tokens_path)

if has_tokens:
    MODE = "pencil"
    print(f"Режим: PENCIL MCP → читаем {tokens_path}")
else:
    MODE = "html"
    print("Режим: HTML→Playwright (Фактор дефолты)")
```

**PENCIL режим** — если `data/design-tokens.md` существует:
- Инфографика собирается через Pencil MCP `batch_design`
- Экспорт в PNG через `export_nodes`
- Подробные инструкции → `references/pencil-templates.md`

**HTML режим** — если `data/design-tokens.md` нет:
- Текущий путь HTML → Playwright → PNG
- Дефолты Фактора или `project.md`

---

## Шаг 1 — Загрузить конфиг проекта

```python
import os, json

if has_project:
    with open(config_path) as f:
        project_config = f.read()
    print(f"Проект загружен из: {config_path}")
else:
    project_config = None
    print("project.md не найден → используем настройки Фактора")
```

Если `project.md` найден — использовать:
- `wp_url`, `wp_user`, `wp_password` — WP URL и авторизация
- `wp_post_type` — тип поста (дефолт: `blog`)
- `color_accent`, `color_bg`, `color_text`, `font` — токены для HTML-режима

Дефолты Фактора (если project.md нет):
- `wp_url` = `https://YOUR_DOMAIN.ru`
- `wp_auth` = `("YOUR_WP_USER", "YOUR_WP_APP_PASSWORD")`
- `wp_post_type` = `blog`
- `color_accent` = `#CC955B` / `color_bg` = `#ECEADF` / `color_text` = `#252525` / `font` = `Raleway`

---

## Шаг 2 — Прочитать статью из WP

Если WP ID не передан — спроси: «Передай ID черновика в WordPress.»

```python
import requests
resp = requests.get(
    f"{WP_URL}/?rest_route=/wp/v2/{WP_POST_TYPE}/{wp_id}",
    auth=WP_AUTH
)
post = resp.json()
content_html = post["content"]["rendered"]
print(post["title"]["rendered"])
```

---

## Шаг 3 — Выбрать 2–3 места для визуализации

Анализируй контент. РОВНО 2–3 инфографики.

**Хорошие места:**
- Перечисление 3–6 этапов / шагов / фаз → тип `steps`
- Воронка / конверсия → тип `funnel`
- 3–5 ключевых цифр / бенчмарков → тип `stats`
- Сравнение «было / стало» → тип `comparison`

**Не добавлять:** в введение, FAQ, кейс, два раздела подряд.

Для каждого места:
```
[N]. Раздел: «<текст H2>»
     Тип: funnel / steps / stats / comparison
     Заголовок: <TITLE>
     Подзаголовок: <SUBTITLE>
     Данные: <что внутри>
```

---

## Шаг 4A — PENCIL режим: сборка инфографики

> Только если `MODE == "pencil"`. Читать `references/pencil-templates.md` перед генерацией.

**4A.1 — Загрузить дизайн-токены клиента**

```python
with open(tokens_path) as f:
    tokens_raw = f.read()
# Извлечь вручную из markdown-таблицы или CSS-блока:
# - color_accent (primary brand color)
# - color_dark (dark bg для хедеров/баров)
# - color_bg (фон канваса/карточек)
# - color_text (основной текст)
# - color_muted (приглушённый текст)
# - color_border (рамки карточек)
# - font_heading (шрифт заголовков — если доступен в Pencil)
# - font_body (шрифт тела)
```

Если шрифт из токенов — платный (TT, Graphik, Styrene и т.д.) → заменить на `Inter`.
Если `Manrope`, `Inter`, `Roboto`, `Montserrat` — использовать как есть.

**4A.2 — Создать инфографику в Pencil**

```
mcp__pencil__open_document("new")
```

Затем собрать по шаблону из `references/pencil-templates.md`:
- `funnel` — вертикальная воронка с суживающимися блоками
- `steps` — сетка кружков с номерами
- `stats` — горизонтальные карточки с цифрами
- `canvas` — стратегический канвас с колонками

Применять цвета клиента из токенов (не хардкодить дефолты Фактора).

**4A.3 — Экспорт PNG**

```python
# После сборки — экспортировать корневой узел
# output_dir = os.path.join(os.getcwd(), "reports")
# Через: mcp__pencil__export_nodes(nodeIds=[root_id], outputDir=output_dir, format="png", scale=2)
png_path = f"{output_dir}/{root_node_id}.png"
```

Переименовать в читаемое имя:
```python
import shutil
final_path = f"/tmp/infographic_{N}.png"
shutil.copy(png_path, final_path)
```

---

## Шаг 4B — HTML режим: генерация HTML-инфографики

> Только если `MODE == "html"`. Читать `references/design-style.md`.

Для каждого места:
1. Взять нужный шаблон из `references/design-style.md`
2. Заполнить реальными данными из статьи
3. Подставить цвета из project.md (дефолты Фактора если нет)
4. Сохранить в `/tmp/infographic_<N>.html`

```python
COLOR_ACCENT = config.get("color_accent", "#CC955B")
COLOR_BG     = config.get("color_bg",     "#ECEADF")
COLOR_TEXT   = config.get("color_text",   "#252525")
FONT         = config.get("font",         "Raleway")

html = """...шаблон из design-style.md с данными..."""
html = html.replace("#CC955B", COLOR_ACCENT).replace("#ECEADF", COLOR_BG)
with open("/tmp/infographic_1.html", "w") as f:
    f.write(html)
```

---

## Шаг 5 — Рендер HTML → PNG (только HTML режим)

```python
import subprocess, sys
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright", "-q"])
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium", "--quiet"])
    from playwright.sync_api import sync_playwright

def render_to_png(html_path, png_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        with open(html_path) as f:
            page.set_content(f.read(), wait_until="networkidle")
        elem = page.query_selector(".infographic")
        if elem:
            elem.screenshot(path=png_path)
        else:
            page.screenshot(path=png_path, full_page=False)
        browser.close()
    print(f"PNG: {png_path} ({os.path.getsize(png_path)//1024} KB)")

render_to_png("/tmp/infographic_1.html", "/tmp/infographic_1.png")
```

---

## Шаг 6 — Загрузить PNG в WP медиатеку

```python
import requests

def upload_to_wp_media(png_path, filename):
    with open(png_path, "rb") as f:
        resp = requests.post(
            f"{WP_URL}/?rest_route=/wp/v2/media",
            auth=WP_AUTH,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "image/png",
            },
            data=f.read(),
        )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Upload failed: {resp.status_code} {resp.text[:300]}")
    media = resp.json()
    print(f"Uploaded: media_id={media['id']} url={media['source_url']}")
    return media["id"], media["source_url"]

media_id_1, media_url_1 = upload_to_wp_media("/tmp/infographic_1.png", "infographic-<slug>-1.png")
```

---

## Шаг 7 — Вставить изображение в контент

Вставить сразу **после** `</h2>` якорного раздела.

```html
<div style="margin:32px 0; text-align:center;">
<a class="blog-gallery" href="{url}" data-fslightbox="lightbox" title="{alt}">
  <img class="image-border_yellow aligncenter size-full wp-image-{id}"
       src="{url}" alt="{alt}" width="1150" height="740"
       style="max-width:100%; cursor:zoom-in;" />
</a>
<p style="margin:10px 0 0; font-size:13px; color:#888; text-align:center;">{caption}</p>
</div>
```

```python
from bs4 import BeautifulSoup
soup = BeautifulSoup(content_html, "html.parser")
for h2 in soup.find_all("h2"):
    if "ЯКОРНЫЙ ЗАГОЛОВОК" in h2.get_text():
        h2.insert_after(BeautifulSoup(figure_html, "html.parser"))
        break
updated_content = str(soup)
```

---

## Шаг 8 — Обновить WP черновик

```python
resp = requests.post(
    f"{WP_URL}/?rest_route=/wp/v2/{WP_POST_TYPE}/{wp_id}",
    auth=WP_AUTH,
    json={"content": updated_content}
)
if resp.status_code == 200:
    print(f"Preview: {WP_URL}/?post_type={WP_POST_TYPE}&p={wp_id}&preview=true")
else:
    print(f"ERROR: {resp.status_code} {resp.text[:300]}")
```

---

## Gotchas

**Общие:**
- WP CPT `blog` → endpoint `/wp/v2/blog/{id}`, НЕ `/wp/v2/posts/{id}`
- BeautifulSoup: `pip install beautifulsoup4` если нет
- `<figure>` без lightbox-ссылки запрещён
- Не вставлять figure внутрь `<ul>`, `<ol>`, `<blockquote>`

**Проверять перед финальным выводом (тема агрессивно переопределяет стили):**
- **`<ul>/<li>` со ссылками** → заменить на `<div>`-список. Тема применяет к `ul li a` float/flex — ссылка становится блоком, текст расплывается в две колонки. `display:inline !important` не помогает. Шаблон `<div>`-списка (обязательно `margin:0 !important` на каждом пункте):
  ```html
  <div style="margin:16px 0; display:flex; flex-direction:column; gap:6px;">
  <div style="display:flex; gap:10px; align-items:flex-start; margin:0 !important;"><span style="color:#CC955B; font-size:18px; line-height:1.5; flex-shrink:0;">•</span><div style="margin:0 !important;">Текст с <a href="/url/">ссылкой</a>.</div></div>
  </div>
  ```
- **FAQ `<details>` — тема добавляет каждому border/border-radius/margin** → отдельные боксы вместо единого аккордеона. Добавить `!important`-сбросы:
  ```html
  <details style="border-bottom:1px solid #E8E8E0; margin:0 !important; padding:0 !important; border-radius:0 !important; border-left:none !important; border-right:none !important; border-top:none !important;">
    <summary style="...; margin:0 !important;">...</summary>
    <div style="...; margin:0 !important;">...</div>
  </details>
  ```
  Последний `<details>`: `border:none !important` вместо `border-bottom`.
- **`<div>` внутри flex получает theme margin** → всегда `margin:0 !important` на flex-items внутри кастомных компонентов (step cards, bullet lists).

**HTML режим:**
- `wait_until="networkidle"` обязательно — без него Google Fonts не загрузятся
- PNG > 500 KB → уменьши `viewport.width` до 1000
- clip-path + текст: делай вложение (фон-слой с clip-path + контент-слой поверх)

**Pencil режим:**
- Платные шрифты (TT Smalls, Graphik, Styrene) → заменять на `Inter`
- `fill_container` на тексте внутри `fit_content`-родителя → вертикальный текст-баг. Фикс: добавить `width: "fill_container"` на строку-родитель
- Биндинги живут ТОЛЬКО внутри одного `batch_design` вызова — в следующем батче использовать реальные node ID из предыдущего ответа
- `placeholder: true` — обязательно на всех незавершённых фреймах, убирать когда готово
- Размер канваса: инфографика 1200×700px, стратегический канвас 1440×640px
- Всегда брать скриншот (`get_screenshot`) после каждого крупного батча

---

## Финальный вывод

```
✅ Добавлено 2 инфографики в черновик WP #{wp_id} [режим: pencil / html]:

1. «Воронка продаж с КЭВ» → после H2 «Как работает КЭВ»
   Тип: funnel | WP media ID: XXXX

2. «5 шагов к построению ОП» → после H2 «Этапы построения отдела продаж»
   Тип: steps | WP media ID: YYYY

Preview: {WP_URL}/?post_type={WP_POST_TYPE}&p={wp_id}&preview=true
```
