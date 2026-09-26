---
name: designer
description: Дизайнер инфографики для статей — два режима: Pencil MCP (если есть data/design-tokens.md клиента) или HTML→Playwright (Фактор Продаж). Анализирует WP черновик, находит 2–3 места для визуализации, генерирует схемы в стиле клиента, загружает PNG в WP медиатеку и вставляет в контент. Запускать после /publisher sync (WP-черновик создан), перед /publisher formatting. Вызывать командой /designer.
---

# Designer — инфографика для статей

## Шаг 0 — Определить режим

**Определить проект** — по аргументу `project=` (путь или имя папки проекта в рабочей директории), дефолт `factor`. НЕ полагаться на `os.getcwd()` — cwd между вызовами не гарантирован.

```python
import os

# project= аргумент, если передан (напр. project=crmgroup) → project_dir
project_dir = "<значение аргумента project= если передан, иначе 'factor'>"

# 1. project.md проекта
config_path = os.path.join(project_dir, "project.md")
has_project = os.path.exists(config_path)

# 2. <project>/data/design-tokens.md клиента (признак клиентского проекта)
tokens_path = os.path.join(project_dir, "data", "design-tokens.md")
has_tokens = os.path.exists(tokens_path)

if has_tokens:
    MODE = "pencil"
    print(f"Режим: PENCIL MCP → читаем {tokens_path}")
else:
    MODE = "html"
    print("Режим: HTML→Playwright (дефолты из project.md или Фактора)")
```

**Если неоднозначно** (аргумент `project=` не передан, а в рабочей директории несколько папок проектов с `project.md`) — явно спросить пользователя, для какого проекта работаем, а не угадывать.

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
- `wp_url` = `https://factor-prodazh.ru`
- `wp_auth` — учётку читать из `<project>/project.md` (поле `wp_auth`) или `.env`; секреты в тексте скилла не хранить
- `wp_post_type` = `blog`
- `color_accent` = `#CC955B` / `color_bg` = `#ECEADF` / `color_text` = `#252525` / `font` = `Raleway`

---

## Шаг 2 — Прочитать статью из WP

Если WP ID не передан — спроси: «Передай ID черновика в WordPress.»

**Обязательно `context=edit` и `content["raw"]`.** `rendered` содержит раскрытые шорткоды — если потом записать rendered обратно в WP, шорткоды (например `[blog-banner-form id=2666]`) будут уничтожены безвозвратно.

```python
import requests
resp = requests.get(
    f"{WP_URL}/?rest_route=/wp/v2/{WP_POST_TYPE}/{wp_id}",
    auth=WP_AUTH,
    params={"context": "edit"},
)
post = resp.json()
content_html = post["content"]["raw"]  # НЕ "rendered"!
print(post["title"]["raw"], post["slug"])  # сверить с ожидаемой статьёй ДО записи
# 🔴 Гард: designer работает ТОЛЬКО с черновиками. Неверный ID = молчаливая правка live-страницы.
if post["status"] != "draft":
    raise SystemExit(f"Пост {wp_id} имеет статус {post['status']} — designer работает только с draft")
```

---

## Шаг 3 — Выбрать 2–3 места для визуализации

**Роли (зафиксированы владельцем 11.09).** Редактор говорит, ГДЕ в статье нужна картинка и ЧТО она должна вынести, и может предложить, КАК это лучше показать. Форму выбираешь ты: каталог из тридцати двух форм и умение их рисовать — твои, не его.

**Сначала ищи слоты от /editor.** Редактор размечает места тегами `[ВИЗУАЛ: заголовок=… | данные=… | смысл=…]` (см. editor SKILL «Разметка визуализаций»). Есть слоты в черновике или в WP-контенте — место и текст берёшь ИЗ НИХ, заново не выбираешь:

```python
import re
viz_markers = re.findall(r'\[ВИЗУАЛ:\s*(.+?)\]', article_text)
# каждый разбить по '|' на заголовок=/данные=/смысл= (в старых статьях ещё тип=)
```

**🔴 Форму выбираешь ты, а не метка.** Место и содержание метки — ТЗ, он читал статью целиком. Поле `смысл=` (`подсказка=`, `идея=`) — предложение: прочитай, оно часто точное, но каталог знаешь ты. Старое поле `тип=` — предложение посильнее; в статьях до 11.09 у редактора в словаре было всего четыре шаблона (funnel / cards-num / cards-badge / stats), из-за которых статьи и выходили одинаковыми: «читатель видит не смысл, а обои». Механика всё это уже посчитала — план бери отсюда:

```bash
python3 "$SEO_BIN/visual_formats.py" choose --run "$RUN" --json --record-plan
python3 "$SEO_BIN/visual_mockup.py" render --run "$RUN" --output /tmp/$RUN-viz.html
```

В каталоге тридцать две формы (поток шагов, развилка, дорожки пути клиента, лестница зрелости, тепловая сетка, петля обратной связи, анатомия объекта, полосы против нормы, сетка долей и другие) с рецептами вёрстки — они приезжают в промпт разделом `PLAYBOOK ФОРМАТОВ СХЕМ`, а витрина всех форм лежит в `preview_artifacts/visual-world-gallery/index.html`. Шестнадцати формам данные из текста не собрать (координаты, значения клеток, баллы): в плане они помечены строкой «данные механика из текста не соберёт», и спеку к ним ты собираешь сам — `visual_mockup.py render --spec spec.json --template …`. Числа в спеке — только из статьи: полоса «на глаз» врёт так же, как выдуманная строка.

Отойти от плана можно, но в `notes` отчёта напиши, от чего и почему. Молча свести форму к карточкам нельзя — ровно из-за этого всё и переписывалось. Карточки понятий — одна форма из тридцати двух, а не режим по умолчанию.

**Строка «редактор разметил это место, схемы в плане нет»** появляется, когда соседний раздел оказался сильнее или улик не хватило. Место — слово редактора, поэтому пройти мимо молча нельзя: либо собери спеку и нарисуй, либо напиши в `notes`, почему схемы здесь не будет.

`заголовок` метки → TITLE, `данные` → содержимое схемы. Если рецепт из плана вёрсткой не покрыт, старые шаблоны из `references/design-style.md` остаются запасным вариантом. После генерации PNG — удалить текстовую метку из контента (она техническая, читателю не нужна).

### 🔴 ПРАВИЛО: текст инфографики = текст редактора. НЕ сочинять.

Весь текст на схеме (заголовок, подписи, пункты, итог) бери **дословно из статьи после /editor** или из поля `данные=` метки. Редактор уже вычистил ИИ-шность — твоя задача перенести, а не переписать.

- **Заголовок** — из `заголовок=` метки или H2 раздела, как есть.
- **Подзаголовок** — взять готовое предложение из текста раздела. Если в `данные=` его нет, а нужен — НЕ выдумывать слоган, а либо опустить, либо вырезать короткую фразу из абзаца дословно.
- **Пункты/подписи** — формулировки и цифры из статьи слово в слово (можно только сократить: убрать вводные слова, оставить суть). Нельзя добавлять новые тезисы, оценки, призывы.
- **ЗАПРЕЩЕНО:** придумывать маркетинговые слоганы («Выбирайте под задачу, а не по цене», «Лучшее решение для…»), эмодзи-восторги, новые факты/цифры, оценочные эпитеты. Это вернёт ИИ-шность, которую редактор убирал.
- Тест перед рендером: каждую строку схемы можно найти (дословно или как явное сокращение) в тексте статьи? Если строки нет в статье — убрать или заменить на текст из статьи.

**🔴 ТИРЕ — гейт редактора действует и на инфографику.** При переносе текста НЕ вводи новые длинные тире `—`. Если в исходнике двоеточие, точка или запятая — сохрани их. Для связок «условие → результат» в схеме используй стрелку `→` (это визуальный символ потока, не пунктуация), не тире. После сборки посчитай `—` в тексте схемы: должно быть близко к 0, и ни одного, которого нет в самой статье. Тире в схемах — такой же ИИ-маркер, как и в тексте.

При сокращении длинной фразы — режь по словам исходника, не перефразируй и не меняй пунктуацию на тире. `данные=` от редактора имеет приоритет над текстом тела статьи.

**Если слотов нет** (старая статья или editor не проставил) — выбери сам, РОВНО 2–3 инфографики (текст всё равно из статьи дословно, см. правило выше). Форму называй из каталога, а не из четырёх старых шаблонов: полный список с назначением каждой формы — `python3 "$SEO_BIN/visual_mockup.py" templates`, как они выглядят — `preview_artifacts/visual-world-gallery/index.html`.

**Хорошие места (форма ← мыслительная операция раздела):**
- Порядок действий, этапы, алгоритм → поток шагов, цепочка с развилками, дорожки ролей
- Развилка «когда что» → дерево решений, матрица выбора отметками
- Сопоставление вариантов → сравнение колонками, оценочная карта, квадрант, радар
- Уровни, которые растут по смыслу → лестница зрелости
- Путь клиента, процесс с несколькими участниками → дорожки пути, сервисный блюпринт
- Цифры: 3–5 ключевых → блок цифр; значение против нормы → полосы против нормы; доля из ста → сетка долей; из чего сложился прирост → водопад
- Сужение потока (есть чем измерить) → воронка
- Типовые ошибки и что вместо → карточки ошибок, карта антипаттернов
- Разбор одного объекта или чужого примера → анатомия с выносками, размеченный экран, разбор примера
- Причина возвращается следствием → петля обратной связи
- Признаки, виды, определения без порядка → карточки понятий (одна форма из тридцати двух, не значение по умолчанию)

**Не добавлять:** в введение, FAQ, кейс, CTA, два раздела подряд.

Для каждого места:
```
[N]. Раздел: «<текст H2>»
     Форма: <из каталога, id рецепта — например maturity-ladder>
     Почему эта: <какая операция в разделе>
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
mcp__pencil__get_editor_state(include_schema: true)
# затем сборка узлов через mcp__pencil__batch_design (см. references/pencil-templates.md). Инструмента open_document НЕТ.
```

Затем собрать по шаблону из `references/pencil-templates.md`:
- `funnel` — вертикальная воронка с суживающимися блоками
- `cards-num` / `cards-badge` — карточки с номерами/бейджами (актуальный стиль для шагов; шаблон STEPS «кружки» в pencil-templates.md — legacy, не использовать)
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

# Поля под мягкую тень. Тень рисуется ЗА границей блока, а кадр по самому
# элементу (elem.screenshot) режется ровно по рамке — тень в PNG не попадала
# вовсе, и на белой странице схема висела без опоры. Поэтому снимаем клипом
# шире элемента; внешняя ширина блока при этом остаётся 1100, растут только поля.
SHADOW_PAD = 26

def render_to_png(html_path, png_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # device_scale_factor=3 → retina-резкость текста (×1 = мылит!). 2 — минимум, 3 — лучше для текстовых схем.
        page = browser.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=3)
        with open(html_path) as f:
            page.set_content(f.read(), wait_until="networkidle")
        # Поля добавляем странице, а не блоку: клип с отрицательным x Playwright
        # не возьмёт, а padding на body отодвигает блок от края кадра.
        page.add_style_tag(content=f"body{{margin:0;padding:{SHADOW_PAD}px}}")
        elem = page.query_selector(".infographic")
        if elem:
            box = elem.bounding_box()
            page.screenshot(
                path=png_path, full_page=True, omit_background=True,
                clip={"x": box["x"] - SHADOW_PAD, "y": box["y"] - SHADOW_PAD,
                      "width": box["width"] + 2 * SHADOW_PAD,
                      "height": box["height"] + 2 * SHADOW_PAD},
            )
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

**🔴 Фолбэк при HTTP 500: REST-медиа на этой площадке стабильно падает — грузить через SSH.** Не ретраить REST (WAF банит серию ошибок), сразу:
```bash
scp /tmp/infographic_1.png <wp_ssh_host>:/tmp/
ssh <wp_ssh_host> "cd <wp_root> && wp media import /tmp/infographic_1.png --porcelain --allow-root"
# → печатает media_id; source_url взять GET-запросом /wp/v2/media/<id> (файлы >2560px WP ужимает → в src брать вернувшийся ...-scaled.png, это норма)
```
`wp_ssh_host`/`wp_root` — из project.md. При транзиентном `Permission denied` (троттлинг sshd при быстрой серии) — пауза 2–3 с и повтор.

---

## Шаг 7 — Вставить изображение в контент

Вставить сразу **после** `</h2>` якорного раздела.

**Разметка зависит от темы сайта — единого шаблона на все проекты нет.** Ветвить по тому же
`has_project`/`project_config`, что и в Шаге 1 (`has_project=False` = Фактор, дефолты Фактора;
`has_project=True` = клиентский проект с `project.md`, для crmgroup.ru/emailsoldiers.ru — тема
`content_hub`). Ставить Factor-разметку клиентскому проекту без проверки — известный класс
дефекта: content_hub не знает классов `blog-gallery`/`data-fslightbox`/`image-border_yellow`,
картинка приходит без рамки и без рабочего зума (клик открывает мелкий дефолтный просмотр вместо
lightbox). Наступали дважды на emailsoldiers.ru — инцидент (2026-09-16) и повтор на этом же
шаблоне (2026-09-23, прогон `20260923-ems-brenda-kannibalizaciya`, найдено на `/publisher prepare`
через `selfcheck.py`, не здесь).

**Фактор (`has_project=False`)** — тема `factor-prodazh.ru` ждёт lightbox-обвязку:
```html
<div style="margin:32px 0; text-align:center;">
<a class="blog-gallery" href="{url}" data-fslightbox="lightbox" title="{alt}">
  <img class="image-border_yellow aligncenter size-full wp-image-{id}"
       src="{url}" alt="{alt}" width="{w}" height="{h}"
       style="max-width:100%; cursor:zoom-in;" />
</a>
</div>
```

**crmgroup.ru / emailsoldiers.ru (`has_project=True`, тема content_hub)** — НЕ Factor-разметка.
Нативная вставка WP, без lightbox-обёртки (клик открывает файл по прямой ссылке):
```html
<div style="margin:32px 0; text-align:center;">
<a href="{url}" title="{alt}">
<img class="aligncenter size-full wp-image-{id}" src="{url}" alt="{alt}" width="{w}" height="{h}" style="max-width:100%;" />
</a>
</div>
```
Формат сверен с живой продакшен-страницей `emailsoldiers.ru/glossary/poiskovyj-zapros` —
идентичная структура; crmgroup.ru использует Gutenberg-`wp:image` с core-лайтбоксом, см.
`ai-seo/crmgroup/data/wp-blocks-reference.md`.

**`{w}`/`{h}` — реальные размеры PNG ÷ device_scale_factor**, не хардкод (браузер резервирует бокс по этим атрибутам — враньё даёт скачок вёрстки или искажение):
```python
from PIL import Image
pw, ph = Image.open(png_path).size
w, h = pw // 3, ph // 3   # ÷ device_scale_factor из Шага 5
```

<!-- caption НЕ добавлять (см. правило ниже). Только если есть ДРУГОЙ текст (источник/атрибуция):
     <p style="margin:10px 0 0; font-size:13px; color:#888; text-align:center;">{источник}</p> -->

**🔴 Подпись `{caption}` НЕ дублирует заголовок/подзаголовок инфографики.** Title и subtitle уже отрисованы ВНУТРИ картинки — если caption = subtitle, читатель видит одну и ту же строку дважды (реальный дефект батча 4423–4433). Правило: инфографики этого билдера самодостаточны → **внешний `<p>`-caption опущен — в шаблоне выше его нет, не добавлять.** Оставлять caption только если это ДРУГОЙ текст: источник данных, пояснение к схеме, атрибуция — то, чего на самой картинке нет.

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

**`updated_content` должен быть собран из `content["raw"]`** (Шаг 2), не из `rendered` — иначе шорткоды (`[blog-banner-form id=2666]` и т.п.) запишутся в раскрытом виде и будут потеряны. Перед POST проверить, что шорткоды из исходного raw на месте.

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

## Шаг 9 — Отметить прогон в pipeline.md

После записи контента (Шаг 8) обновить строку 8b в `<project>/articles/<slug>/pipeline.md`. Slug — из поста (Шаг 2) или аргумента, проект — из `project=`; если определить нельзя — спросить пользователя.

```
| 8b. Инфографика | /designer | ✅ | <дата> | N схем |
```

Осознанное решение «схемы не нужны» — легитимный результат, фиксировать так (без записи /publisher вернёт статью на /designer):

```
| 8b. Инфографика | /designer | ✅ | <дата> | 0 схем: <причина> |
```

Например: `0 схем: статья без данных/таблиц/воронок`. Если pipeline.md не существует — шаг пропустить и отметить в финальном выводе: «pipeline.md не найден — статус 8b не записан».

---

## Gotchas

**🛡️ WAF / fail2ban (общая механика площадок).** Сервер банит IP за серию ошибочных или слишком частых запросов:
- после **401/403 НЕ ретраить** — это не транзиент: проверить креды (не ушёл ли плейсхолдер вместо пароля из secrets);
- между REST-запросами держать паузу 1–2 с (конвейер делает 10–20 запросов подряд);
- если в ответ пришла HTML-страница вместо JSON — это бан-страница WAF: остановиться и подождать, не долбить.


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
- **FAQ — НЕ зона designer.** FAQ-аккордеон делает /publisher (голые `<details><summary>` БЕЗ inline-стилей — тема faktor-template сама стилизует). Designer в FAQ инфографику не ставит (см. Шаг 3 «Не добавлять: FAQ») и стили `<details>` не трогает.
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
   Тип: cards-badge | WP media ID: YYYY

Preview: {WP_URL}/?post_type={WP_POST_TYPE}&p={wp_id}&preview=true
Pipeline: строка 8b отмечена ✅ (или: pipeline.md не найден — статус 8b не записан)
```
