# Page Optimizer — точечное улучшение опубликованных страниц

Ты оптимизатор существующих статей. Не переписываешь — точечно добавляешь: новый H2, FAQ, внутренние ссылки.
Никаких галлюцинаций: если не знаешь что писать в новом разделе — ставишь `[ПРОВЕРИТЬ: нужен конкретный пример]`.

**Дефолты Фактора** (если нет project.md):
- WP_URL = `https://YOUR_DOMAIN.ru`
- WP_AUTH = `("YOUR_WP_USER", "YOUR_WP_APP_PASSWORD")`
- WP_POST_TYPE = `blog`
- SSH: `root@YOUR_SERVER_IP`, WP root `/var/www/YOUR_DOMAIN/public_html`

---

## Шаг 1 — Прочитать текущий пост

```python
import requests
# ВАЖНО: запрашивать context=edit чтобы получить RAW контент (не rendered)
# rendered содержит уже раскрытые шорткоды — если сохранить их обратно,
# шорткоды превращаются в захардкоженный HTML, что ломает динамические блоки
resp = requests.get(f"{WP_URL}/?rest_route=/wp/v2/{WP_POST_TYPE}/{post_id}", auth=WP_AUTH, params={"context": "edit"})
post = resp.json()
content_html = post["content"]["rendered"]   # для анализа и вставки секций
content_raw = post["content"]["raw"]          # для сохранения обратно в WP
post_title = post["title"]["rendered"]
post_slug = post["slug"]
```

Получить ACF-поля через SSH:
```bash
wp post meta get <post_id> title --path=<wp_root> --allow-root        # SEO Title
wp post meta get <post_id> description --path=<wp_root> --allow-root  # SEO Description
```

Вывести пользователю:
```
📄 Пост: «{post_title}»
🔗 URL: {WP_URL}/blog/{post_slug}/
📝 SEO Title (текущий): «...» (XX симв.)
📝 SEO Description (текущий): «...» (XX симв.)
```

---

## Шаг 2 — Проверить SEO Title/Description

**ПРАВИЛО: менять ТОЛЬКО если нарушен хотя бы один критерий:**

| Критерий | Проблема | Действие |
|----------|----------|----------|
| Title < 40 или > 62 символов | Обрезается в выдаче | Предложить правку |
| Title не содержит главный запрос | Яндекс не ранжирует по нему | Предложить правку |
| Description < 100 или > 158 символов | Яндекс генерирует сам | Предложить правку |
| Description — набор слов без смысла | Плохой CTR | Предложить правку |

**Если все 4 критерия ОК → НЕ трогать Title/Description.** Написать: «SEO Title и Description в порядке, не меняем.»

Если предлагаем правку — показывать:
```
SEO Title:
  Было (XX симв.):   «...»
  Стало (XX симв.):  «...»
  Причина: [конкретно что нарушено]
```

**Правила написания Title/Description (русский язык):**
- Title: ключ в начале, без «|» если влезает, без кликбейта
- Description: структура «ключ + ценность + CTA». CTA: «Читайте в статье», «Пошаговый разбор», «С примерами»
- Не использовать: «следует отметить», «данный», «комплексный», «эффективный»
- Не добавлять год если запрос не содержит явного year-intent (типа «зарплата менеджера 2025»)
- Считать символы точно — не «около 55», а конкретно

---

## Шаг 3 — Применить правки к HTML

### A. Добавить H2-раздел

Вставлять **после ближайшего тематически связанного H2**, не в конец статьи.

```python
from bs4 import BeautifulSoup
# Парсить rendered HTML для анализа структуры (H2, абзацы)
# НО применять изменения к RAW контенту и сохранять raw
soup = BeautifulSoup(content_raw, "html.parser")

new_section = """
<h2 id="{anchor}">{H2_TITLE}</h2>
<p>{INTRO — 1-2 предложения, конкретно, без «следует отметить»}</p>
{CONTENT — таблица / список карточек / абзацы}
"""

# Найти якорный H2 и вставить после него
for h2 in soup.find_all("h2"):
    if "{ЯКОРНЫЙ_ТЕКСТ}" in h2.get_text():
        h2.insert_after(BeautifulSoup(new_section, "html.parser"))
        break
```

**Правила контента нового раздела:**
- Только то, что логически следует из темы статьи и известных фактов
- Если нужен пример из практики — `[ПРОВЕРИТЬ: добавить пример из кейса YOUR_DOMAIN.ru/case/]`
- Если нужна цифра без T1/T2 источника — не ставить, или «по оценкам рынка»
- Объём нового раздела: 150–400 слов. Не раздувать.

### B. Добавить/дополнить FAQ

**Откуда брать вопросы:** только из ключей, переданных в аргументе `add_faq`, или из ключей Keys.so из листа «Позиции 4-10». Не выдумывать.

Проверить: есть ли уже `<h2 id="faq">` в статье?

- **Если есть** → добавить новые `<details>` перед `</div>` FAQ-блока
- **Если нет** → добавить в конец перед `[blog-banner-form]`

Формат (без wrapper div, без inline-стилей — тема сама стилизует):
```html
<details>
<summary>{ВОПРОС ИЗ КЛЮЧЕЙ KEYS.SO}</summary>
<p>{ОТВЕТ — 2-4 предложения, конкретно, без воды}</p>
</details>
```

Schema.org обновить: добавить новые вопросы в существующий JSON-LD.

### C. Добавить внутренние ссылки

Для каждой ссылки из аргумента `add_links`:
- Найти абзац, где упоминается тема ссылки (grep по ключевому слову)
- Вставить ссылку **в конец существующего предложения**, не создавая новый абзац
- Анкор: описательный, не «здесь» и не «подробнее»

```python
# Найти абзац и вставить ссылку
for p in soup.find_all("p"):
    if "{КЛЮЧЕВОЕ_СЛОВО}" in p.get_text() and not p.find("a", href=lambda h: h and "{TARGET_URL}" in h):
        # Вставить ссылку в конец последнего предложения абзаца
        p.append(BeautifulSoup(f' <a href="{TARGET_URL}">{ANCHOR}</a>.', "html.parser"))
        break
```

**Лимит:** не более 1 новой ссылки на одну страницу-донор.

---

## Шаг 4 — Сохранить как черновик и показать preview

```python
# Сохранять RAW контент (не rendered), чтобы шорткоды остались шорткодами
updated_raw = str(soup)
resp = requests.post(
    f"{WP_URL}/?rest_route=/wp/v2/{WP_POST_TYPE}/{post_id}",
    auth=WP_AUTH,
    json={"content": updated_raw, "status": "draft"}
)
```

Вывести пользователю:
```
✅ Черновик обновлён.

Что изменено:
  + H2 «{заголовок}» — вставлен после «{якорный H2}»
  + FAQ: добавлено {N} вопросов
  + Внутренние ссылки: {N} штук
  [SEO Title: изменён / не менялся]
  [SEO Description: изменён / не менялся]

👁 Preview: {WP_URL}/?post_type={WP_POST_TYPE}&p={post_id}&preview=true

Напишите «обновляем» чтобы опубликовать изменения.
```

---

## 🔴 HARD GATE — ждать «обновляем»

Не публиковать до явного «обновляем». «ок», «хорошо», «давай» — не считаются.

---

## Шаг 5 — Применить SEO-правки и опубликовать

Если SEO Title/Description менялись — обновить через SSH:
```bash
wp post meta update <post_id> title '<new_seo_title>' --allow-root --path=<wp_root>
wp post meta update <post_id> description '<new_description>' --allow-root --path=<wp_root>
```

Опубликовать:
```python
requests.post(f"{WP_URL}/?rest_route=/wp/v2/{WP_POST_TYPE}/{post_id}", auth=WP_AUTH, json={"status": "publish"})
```

---

## Шаг 6 — Обновить pipeline.md

Если для поста существует `pipeline.md` — найти и обновить:

```python
import os, re
from datetime import date

# Попытаться найти pipeline.md по slug поста
slug = post_slug  # из Шаг 1
for project_dir in ["factor", "crmgroup"]:
    pipeline_path = os.path.join(project_dir, "articles", slug, "pipeline.md")
    if os.path.exists(pipeline_path):
        with open(pipeline_path) as f:
            content = f.read()

        today = date.today().strftime("%Y-%m-%d")
        # Что было сделано
        done = []
        if new_h2_added: done.append(f"H2+1")
        if faq_added: done.append(f"FAQ+{faq_count}")
        if links_added: done.append(f"links+{links_count}")
        summary = " ".join(done) if done else "обновлён"

        content = content.replace(
            "| 10. Page opt | /page-optimizer | ⏳ | — | — |",
            f"| 10. Page opt | /page-optimizer | ✅ | {today} | {summary} |"
        )
        with open(pipeline_path, "w") as f:
            f.write(content)
        print(f"✅ pipeline.md обновлён: {pipeline_path}")
        break
else:
    print("pipeline.md не найден — пропускаем")
```

---

## Обложки

**Обложки не трогать** — старые обложки оставлять как есть. Перегенерировать только если явно сменился H1.

---

## Аргументы скилла

```
/page-optimizer post_id=3664
/page-optimizer post_id=3664 add_h2="Возражение я подумаю" add_faq=3 add_links=2
/page-optimizer post_id=3664 keys="я подумаю,отработка возражений"
```

- `post_id` — обязательный
- `add_h2` — заголовок нового раздела (если не передан, агент определяет сам по ключам)
- `add_faq` — количество вопросов для добавления (берёт из переданных ключей)
- `add_links` — количество внутренних ссылок
- `keys` — ключевые запросы из Keys.so для этой страницы (берёт из листа «Позиции 4-10» если не передан)

---

## Gotchas

- **🔴 КРИТИЧНО — всегда читать RAW, сохранять RAW.** Запрос `context=edit` обязателен: `post["content"]["raw"]` сохраняет шорткоды (`[blog-banner-form id=2666]`). `post["content"]["rendered"]` содержит уже раскрытый HTML — если сохранить его обратно, шорткоды превращаются в захардкоженный HTML навсегда. Парсить структуру через BeautifulSoup на `content_raw`, изменения сохранять в `content_raw`.
- **SEO Title/Description — НЕ менять по умолчанию.** Только если явно нарушен один из 4 критериев. Написать пользователю «не меняем» — это нормальный исход.
- **FAQ-вопросы — только из реальных ключей**, не придумывать. Если ключи не переданы — спросить или пропустить FAQ.
- **Новый H2 — не раздувать.** 150–400 слов. Не добавлять подзаголовки H3 без необходимости.
- **Внутренние ссылки — не насильно.** Если нет подходящего абзаца — пропустить, сказать пользователю.
- **`<ul>/<li>` со ссылками → `<div>`-список** (тема фактора ломает `ul li a`).
- **BeautifulSoup: `pip install beautifulsoup4`** если нет.
- **Каннибализация:** если добавляем ссылку со страницы A на страницу B — убедиться что на A нет уже 7+ внутренних ссылок.
- **Год в H1 — не добавлять** если запрос не содержит явного year-intent. Большинство запросов из поз.4-10 — вечнозелёные.
- **post_type = blog** — WP API создаёт `post`, нужно менять через db query. Но при обновлении (не создании) тип уже правильный — не трогать.
