---
name: publisher
description: Финальный шаг перед публикацией статьи в блог Фактор Продаж — создаёт Google Doc для ревью и черновик в WP одновременно, затем после подтверждения: SEO-чеклист, типографика, ACF-поля, обложка, публикация. Использовать после /editor. Вызывать командой /publisher.
---

# Publisher — публикация статьи

## Шаг 0 — Загрузить конфиг проекта

**Определить проект** — по аргументу `project=` или дефолт `factor`:

```python
import os, json, re

# project= аргумент, если передан (напр. project=crmgroup)
# Иначе — "factor"
project_dir = "<значение аргумента project= если передан, иначе 'factor'>"

config_path = os.path.join(project_dir, "project.md")
if os.path.exists(config_path):
    with open(config_path) as f:
        project_config = f.read()
    print(f"Проект: {project_dir} → {config_path}")
else:
    project_config = None
    print(f"project.md не найден в {project_dir}/ → используем дефолты Фактора")
```

Если `project.md` найден — использовать его значения везде в скрипте:
```python
# Читать из project.md (значения — из соответствующих ключей файла):
WP_URL = config["wp_url"]           # напр. https://YOUR_DOMAIN.ru
WP_AUTH = (config["wp_user"], config["wp_password"])
WP_POST_TYPE = config.get("wp_post_type", "post")
WP_AUTHOR_ID = config.get("wp_author_id", 1)
REST_BASE = config.get("wp_rest_base", "/?rest_route=/wp/v2/posts")
BLOG_BANNER_MID = config.get("blog_banner_mid", "[blog-banner id=1480]")
BLOG_BANNER_END = config.get("blog_banner_end", "[blog-banner-form id=2666]")
```

Если `project.md` НЕ найден → фолбэк на дефолты Фактора:
- `WP_URL` = `https://YOUR_DOMAIN.ru`
- `WP_AUTH` = `("YOUR_WP_USER", "YOUR_WP_APP_PASSWORD")`
- `WP_POST_TYPE` = `blog`
- `WP_AUTHOR_ID` = `523`
- `REST_BASE` = `/?rest_route=/wp/v2/posts`
- `BLOG_BANNER_MID` = `[blog-banner id=1480]`
- `BLOG_BANNER_END` = `[blog-banner-form id=2666]`

---

Ты технический редактор и публикатор. Берёшь готовую статью после `/editor` и доводишь до публикации.

Если статья не передана — спроси: «Передай текст статьи и slug (URL-адрес).»

---

## Шаг 0b — Pipeline Gate (если передан slug)

**Если передан аргумент `slug=`** — проверить pipeline.md перед публикацией:

```python
import os, re

slug = "<аргумент slug= если передан>"
project_dir = "<аргумент project= или 'factor'>"

pipeline_path = os.path.join(project_dir, "articles", slug, "pipeline.md")
if os.path.exists(pipeline_path):
    with open(pipeline_path) as f:
        pipeline = f.read()

    # Проверить обязательные шаги
    gates = {
        "researcher": "| 2. Research |",
        "writer": "| 4. Draft |",
        "editor": "| 5. Редактура |",
        "fact-checker": "| 6. Fact-check |",
        "quality-gate": "| 7. Quality gate |",
        "seo-optimizer": "| 8a. SEO pack |",
    }

    blocked = []
    for skill, pattern in gates.items():
        # Найти строку в таблице
        match = re.search(pattern + r'[^\n]+', pipeline)
        if match:
            row = match.group(0)
            if "⏳" in row or row.endswith("| — | — |"):
                blocked.append(f"  ❌ {skill} — не выполнен (⏳)")
            elif "❌" in row:
                blocked.append(f"  ❌ {skill} — завершился с FAIL")
        else:
            blocked.append(f"  ⚠️ {skill} — не найден в pipeline.md")

    # Проверить quality-gate PASS
    if "quality-gate" not in str(blocked):
        qg_match = re.search(r'\| 7\. Quality gate \|[^\n]+', pipeline)
        if qg_match and "FAIL" in qg_match.group(0):
            blocked.append("  ❌ quality-gate — статус FAIL (нужно исправить нарушения)")

    if blocked:
        print("🔒 ПУБЛИКАЦИЯ ЗАБЛОКИРОВАНА. Незакрытые шаги:")
        for b in blocked:
            print(b)
        print("\nЗапусти недостающие скиллы и повтори /publisher")
        # СТОП — не продолжать
    else:
        print("✅ Pipeline gate пройден — все шаги выполнены. Продолжаю публикацию...")
```

Если pipeline.md не существует — продолжать без gate-проверки (обратная совместимость).

---

## Шаг 1 — Google Doc + черновик WP (параллельно, до ревью)

Выполнить оба действия одновременно:

**A. Создать Google Doc со статьёй и форматированием:**

Использовать googleapis напрямую через node (надёжнее чем MCP для больших текстов):

```javascript
// ~/.claude/mcp-servers/google-docs/node_modules/ — использовать именно эти модули
// 1. Конвертировать HTML статьи → plain text, сохранив маркеры ## для H2
function htmlToText(html) {
  // Сначала удалить целиком блоки со скриптами/стилями (включая Schema.org JSON-LD)
  html = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
  html = html.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
  // Затем конвертировать структуру
  html = html.replace(/<h2[^>]*>(.*?)<\/h2>/gs, '\n## $1\n');
  html = html.replace(/<h3[^>]*>(.*?)<\/h3>/gs, '\n### $1\n');
  html = html.replace(/<\/p>\s*<p[^>]*>/g, '\n\n');
  html = html.replace(/<li[^>]*>(.*?)<\/li>/gs, '• $1\n');
  html = html.replace(/<[^>]+>/g, '');
  html = html.replace(/\[blog-banner[^\]]*\]/g, '');
  return html.replace(/\n{3,}/g, '\n\n').trim();
}

// 2. Создать Google Doc: название = "[slug] — черновик YYYY-MM-DD"
const doc = await docs.documents.create({ requestBody: { title } });
const docId = doc.data.documentId;

// 3. Вставить полный текст статьи (H1 первой строкой, H2 с маркером ##)
const text = title + '\n\n' + htmlToText(articleHtml);
await docs.documents.batchUpdate({ documentId: docId,
  requestBody: { requests: [{ insertText: { location: { index: 1 }, text } }] }
});

// 4. Применить стили — перебрать строки, найти H1 (первая) и H2 (строки с ##)
const lines = text.split('\n');
let pos = 1;
const styleRequests = [];
for (const line of lines) {
  const len = line.length + 1;
  if (pos === 1) {
    styleRequests.push({ updateParagraphStyle: {
      range: { startIndex: pos, endIndex: pos + len },
      paragraphStyle: { namedStyleType: 'HEADING_1' }, fields: 'namedStyleType'
    }});
  } else if (line.startsWith('## ')) {
    styleRequests.push({ updateParagraphStyle: {
      range: { startIndex: pos, endIndex: pos + len },
      paragraphStyle: { namedStyleType: 'HEADING_2' }, fields: 'namedStyleType'
    }});
  }
  pos += len;
}
// Отправить чанками по 20
for (let i = 0; i < styleRequests.length; i += 20) {
  await docs.documents.batchUpdate({ documentId: docId,
    requestBody: { requests: styleRequests.slice(i, i + 20) }
  });
}
console.log('Google Doc готов: https://docs.google.com/document/d/' + docId + '/edit');
```

**Важно:** Google Doc должен содержать ПОЛНЫЙ текст статьи — не метаданные, не заглушки. Пользователь читает и правит именно Google Doc перед публикацией.

**B. Создать черновик в WordPress:**
```python
import requests
# Значения из project.md (или дефолты Фактора если project.md не найден):
url = f"{WP_URL}{REST_BASE}"
auth = WP_AUTH
data = {"title": "<H1>", "content": "<HTML>", "slug": "<slug>", "status": "draft"}
resp = requests.post(url, json=data, auth=auth)
post_id = resp.json()["id"]
# Сразу сменить тип на WP_POST_TYPE (дефолт: blog):
# wp db query "UPDATE wp_posts SET post_type='{WP_POST_TYPE}' WHERE ID=<post_id>" --allow-root --path=<wp_root>
```
Предпросмотр: `{WP_URL}/?post_type={WP_POST_TYPE}&p=<post_id>&preview=true`

**После обоих шагов — вывести пользователю:**
```
✓ Google Doc: https://docs.google.com/document/d/<doc_id>/edit
✓ WP черновик: {WP_URL}/?post_type={WP_POST_TYPE}&p=<post_id>&preview=true

Проверьте статью в Google Doc и дайте добро на публикацию.
Напишите «публикуем» чтобы продолжить.
```

Ссылка на Google Doc строится из ID: `https://docs.google.com/document/d/<doc_id>/edit`

---

## 🔴 HARD GATE — ОБЯЗАТЕЛЬНАЯ ОСТАНОВКА

**СТОП. Не выполнять шаги 2–6 (SEO-чеклист, типографику, ACF, обложку, публикацию).**

Выдать ссылки выше и ждать. Продолжать ТОЛЬКО если пользователь написал буквально «публикуем».

«да», «ок», «всё ок», «хорошо», «давай» — НЕ считаются подтверждением. Только «публикуем».

---

---

## Шаг 1 — SEO-чеклист (проверить до публикации)

Пройди по каждому пункту и отметь статус:

**Контент:**
- [ ] H1 содержит целевой ключ + год (пример: «Построение отдела продаж 2025»)
- [ ] Лид-параграф (TL;DR) — первое предложение = прямой ответ на запрос статьи. Проверка: можно ли вставить его в AI-ответ без контекста? Если нет — вернуть в /editor. Оформить как визуальный TL;DR-блок (см. Шаг 2, раздел A-0).
- [ ] TOC-блок после лида, все H2 имеют `id`-якоря
- [ ] Нет `[ПРОВЕРИТЬ]` и `[нужна деталь от клиента]` в тексте
- [ ] **Тире (—): не более 8 в статье** — посчитать явно: `grep -o '—' file.html | wc -l`. Если больше 8 — вернуть в редактуру.
- [ ] Есть кейс из YOUR_DOMAIN.ru/case/ с конкретными деталями
- [ ] Внутренние ссылки: 5–7 штук, анкоры описательные (не «здесь»/«подробнее»)
- [ ] Минимум 1 ссылка на релевантную услугу (таблица в WP_BLOG_TECHNICAL.md раздел 14.2)
- [ ] Списки 3+ однородных элементов → таблицы
- [ ] Blockquote class="yellow": 1–2 штуки, не более 3 blockquote суммарно
- [ ] Blog-баннер в середине статьи: `[blog-banner id=1480]`
- [ ] Порядок финала: H2 «Что дальше» → H2 «Частые вопросы»
- [ ] FAQ: минимум 4 вопроса, Schema.org JSON-LD + `<details><summary>`

**ACF-поля для SEO:**
- [ ] SEO Title (50–60 символов, ключ в начале)
- [ ] SEO Description (120–155 символов, ключ + ценность + CTA)

Если что-то не заполнено — сформулируй сам на основе статьи и предложи.

---

## Шаг 2 — Структура и читаемость

Перед типографикой — пройти по структурным элементам. Смотреть на реальные статьи как образец: `factor/articles/kev/kev-klyuchevoy-etap-voronki.html`, `factor/articles/grebenyuk/grebenyuk-sovety-prodazhi.html`.

### A-0. TL;DR-блок (лид-параграф)

**🔴 ОБЯЗАТЕЛЬНО:** Первый абзац после H1 — это TL;DR. Оформить как визуальный блок с меткой «Кратко» до вставки TOC.

**Паттерн для поиска:** первый `<p>...</p>` после `<h1>` в теле статьи.

**Заменить на:**
```html
<div style="background:#F9F9F6; border-left:3px solid #CC955B; border-radius:0 8px 8px 0; padding:16px 20px; margin:0 0 28px;">
<p style="margin:0 0 4px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1.2px; color:#CC955B;">Кратко</p>
<p style="margin:0; color:#252525; line-height:1.65;">[текст первого абзаца]</p>
</div>
```

**Если первый абзац — вода** («В этой статье мы рассмотрим...», «Многие предприниматели знают...») — **СТОП**, вернуть в `/editor`. Верстать такой лид нельзя — Google AI его не цитирует.

**Правила:**
- Не добавлять `<strong>` к тексту внутри блока — оставить как есть
- Не переписывать содержимое — только обернуть
- Блок идёт ДО TOC-оглавления

---

### A. TOC-блок (оглавление)

Вставить сразу после лид-абзаца, перед первым H2. Все H2 должны иметь `id`-якорь (транслитерация через дефис).

```html
<div style="background:#F9F9F6; border:1px solid #E8E8E0; border-radius:8px; padding:20px 24px; margin:24px 0 32px;">
<p style="margin:0 0 12px; font-weight:600; font-size:16px; color:#252525;">Содержание</p>
<ol style="margin:0; padding-left:20px; line-height:1.8;">
<li><a href="#section-slug">Название раздела</a></li>
...
</ol>
</div>
```

Правило для id: `kto-takoy-lpr`, `kak-nayti-lpr`, `chto-dalshe`, `faq`.

### B. Таблицы

**🔴 ОБЯЗАТЕЛЬНО:** Перед публикацией найти в тексте все следующие паттерны и преобразовать:

**Паттерн 1 — «— Показатель: значение»** (чаще всего встречается в статьях про KPI, нормативы, формулы):
```
— Звонков в день: 60–80
— Встреч в неделю: 10–15
— Конверсия: 15–20%
```
→ Это ВСЕГДА таблица `<table>` с колонками «Показатель» / «Норматив». Никаких `<ul>` или `<p>` с тире.

Если несколько групп (Хантер / Фермер / Клоузер) — объединить в одну таблицу с колонкой на каждую роль.

**Паттерн 2 — Нумерованные пункты «Название: описание»:**
```
1. Выручка за месяц: план vs факт
2. Конверсия лид → КЭВ: 50–70%
3. Звонков в день: 60–80
```
→ Если 3+ однородных пункта с двоеточием — это `<table>`.

**Паттерн 3 — `<li><strong>Заголовок.</strong> Текст</li>`:**
→ Тема рендерит как двухколоночный список с переносами. Всегда `<table>`.

**Другие случаи для таблицы:**
- Сравнение вариантов (было/стало, A vs B)
- Ниши/типы/категории → кто/что/результат

Формат (с обязательными отступами):
```html
<div style="margin:28px 0;">
<table>
<thead><tr><th>Показатель</th><th>Норматив</th></tr></thead>
<tbody>
<tr><td>Звонков в день</td><td>60–80</td></tr>
<tr><td>Встреч в неделю</td><td>10–15</td></tr>
</tbody>
</table>
</div>
```

**Отступы обязательны:** всегда оборачивать таблицу в `<div style="margin:28px 0;">`. Без этого таблица слипается с текстом выше/ниже.

Правила: не ставить `&nbsp;` внутри `<td>` и `<th>`. Неразрывные дефисы `‑` в ячейках — да.

### C. Раскрывающиеся блоки `<details>`

**🔴 ОБЯЗАТЕЛЬНО:** Проверить все длинные перечисления:

- Таблица > 7 строк → первые 5 видны, остальные в `<details>`
- `<ol>` или `<ul>` > 7 пунктов → первые 5 видны, остальные в `<details>`
- Нумерованные пошаговые инструкции «Шаг 1 / Шаг 2...» → **не collapse, а визуальные карточки** (см. раздел H ниже)
- Нумерованные KPI-пункты «1. Показатель: ... 2. Показатель: ...» — сначала конвертировать в таблицу (см. п. B), потом применить details если строк > 7

```html
<div style="margin:28px 0;">
<table>
<thead><tr><th>...</th></tr></thead>
<tbody>
<!-- первые 5 строк данных -->
<tr><td>...</td></tr>
<tr><td>...</td></tr>
<tr><td>...</td></tr>
<tr><td>...</td></tr>
<tr><td>...</td></tr>
</tbody>
</table>

<details style="margin-top:8px;">
<summary style="cursor:pointer; color:#CC955B; font-weight:600; font-size:14px; padding:8px 0;">Показать все N&nbsp;строк ↓</summary>
<table>
<thead><tr><th>...</th></tr></thead>
<tbody>
<!-- оставшиеся строки -->
</tbody>
</table>
</details>
</div>
```

Для длинных `<ol>` / `<ul>`:
```html
<ol>
  <li>Пункт 1</li>...<li>Пункт 5</li>
</ol>
<details style="margin-top:8px;">
<summary style="cursor:pointer; color:#CC955B; font-weight:600; font-size:14px; padding:8px 0;">Показать все N пунктов ↓</summary>
<ol start="6"><li>Пункт 6</li>...</ol>
</details>

Также использовать для FAQ (см. раздел H ниже — FAQ всегда в формате аккордеона).

### H. Пошаговые инструкции — визуальные карточки

**🔴 ОБЯЗАТЕЛЬНО:** Любой блок `<p><strong>Шаг N:</strong> текст</p>` с 2+ шагами → конвертировать в карточки с золотыми кружками.

**Паттерн для поиска:**
```
<p><strong>Шаг 1:</strong> ...
<p><strong>Шаг 2:</strong> ...
```

**Формат карточки шага:**
```html
<div style="margin:24px 0; display:flex; flex-direction:column; gap:8px;">

<div style="display:flex; gap:16px; background:#fff; border:1px solid #E8E8E0; border-radius:8px; padding:16px 20px; align-items:flex-start;">
  <span style="min-width:32px; height:32px; background:#CC955B; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; color:#fff; font-weight:700; font-size:15px; flex-shrink:0; margin-top:2px;">1</span>
  <div>
    <div style="margin:0 0 4px; font-weight:700; color:#252525; line-height:1.4;">Название шага</div>
    <div style="margin:0; color:#555; line-height:1.6; font-size:15px;">Текст шага. Инлайн-код Excel: <code style="background:#F0EEE6; color:#8B6014; padding:2px 7px; border-radius:4px; font-size:13px; font-family:'Courier New',monospace; white-space:nowrap;">=D2/C2*100</code></div>
  </div>
</div>

<div style="display:flex; gap:16px; background:#fff; border:1px solid #E8E8E0; border-radius:8px; padding:16px 20px; align-items:flex-start;">
  <span style="min-width:32px; height:32px; background:#CC955B; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; color:#fff; font-weight:700; font-size:15px; flex-shrink:0; margin-top:2px;">2</span>
  <div>
    <div style="margin:0 0 4px; font-weight:700; color:#252525; line-height:1.4;">Название шага</div>
    <div style="margin:0; color:#555; line-height:1.6; font-size:15px;">Текст шага.</div>
  </div>
</div>

</div>
```

**Ключевые правила:**
- Лейбл и текст — **всегда в отдельных `<p>` внутри `<div>`**. Никогда в одном `<span>`.
- `background:#fff` (белый), не `#FAFAF7` — карточки не должны давить на глаз
- `gap:8px` между карточками, `padding:16px 20px` внутри

**Формулы Excel/Google Sheets внутри шагов** (типа `=D2/C2*100`, `=СУММ(F2:F6)`, `=ЕСЛИ(...)`) — это программный код, НЕ математические формулы. Оформлять инлайн-кодом:
```html
<code style="background:#F0EEE6; color:#8B6014; padding:2px 7px; border-radius:4px; font-size:13px; font-family:'Courier New',monospace; white-space:nowrap;">=формула</code>
```
Длинные формулы (вложенные ЕСЛИ, длиннее 60 символов) — добавить `word-break:break-all` и `display:inline-block`.

**Отличие от блока математической формулы (раздел G):**
- Математика (KPI% = Факт/План × 100%) → styled div с `border-left:#CC955B`
- Код Excel/Sheets (`=D2/C2*100`) → инлайн `<code>` с тёплым фоном

### I. FAQ аккордеон — обязательный формат

**🔴 ОБЯЗАТЕЛЬНО:** FAQ всегда в конце статьи, после H2 «Что дальше». Никогда не в середине.

**Порядок в конце статьи:**
1. `[blog-banner-form id=2666]`
2. `<h2 id="faq">Частые вопросы о [тема]</h2>`
3. Schema.org JSON-LD
4. Аккордеоны

**Запрещённый формат (всегда заменять):**
```html
<!-- ❌ ЗАПРЕЩЕНО — Вопрос/Ответ как параграфы: -->
<p>Вопрос: Как настроить KPI?</p>
<p>Ответ: Нужно...</p>
```

**Правильный формат — тема сама стилизует `<details>`, inline-стили НЕ нужны:**
```html
[blog-banner-form id=2666]

<h2 id="faq">Частые вопросы о KPI в продажах</h2>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
  {"@type":"Question","name":"Вопрос 1?","acceptedAnswer":{"@type":"Answer","text":"Ответ 1."}},
  {"@type":"Question","name":"Вопрос 2?","acceptedAnswer":{"@type":"Answer","text":"Ответ 2."}}
]}
</script>
<details>
<summary>Вопрос 1?</summary>
<p>Ответ 1.</p>
</details>
<details>
<summary>Вопрос 2?</summary>
<p>Ответ 2.</p>
</details>
```

**Никакого wrapper div, никаких inline-стилей на `<details>` и `<summary>`, никакого `<strong>` в summary** — тема faktor-template сама рендерит аккордеон. Проверено на /blog/5-etapov-prodazh-menedzhera-po-prodazham/ (эталон). Стили через `!important` и wrapper-div с `border-radius:8px; overflow:hidden` не работают — тема добавляет каждому `<details>` собственные border/radius и они рендерятся как отдельные боксы.

### J. Подзаголовки внутри секций

`<p>Название:</p>` или `<p><strong>Название</strong></p>` между разделами текста → `<h3 id="anchor">Название</h3>`.

Примеры: «Исходные данные:», «Показатели и веса:», «Расчёт взвешенного KPI:», «Сквозной кейс:» — все это H3, не параграфы.

### D. Blockquote

**`<blockquote class="yellow">`** — ключевая мысль раздела или CTA со ссылкой на услугу. Максимум 2 на статью.

```html
<blockquote class="yellow">
<p>Текст тезиса или призыва. <a href="/services/konsalting/">Ссылка на услугу</a>.</p>
</blockquote>
```

**Обычный `<blockquote>`** — цитата эксперта или сильный тезис без ссылки. Максимум 1.

```html
<blockquote>Текст цитаты или тезиса без ссылки.</blockquote>
```

Итого blockquote на статью: не более 3.

### E. Blog-баннеры (шорткоды)

Вставлять в тело контента:
- После 2–3 раздела (середина статьи): `[blog-banner id=1480]`
- В конце перед FAQ (форма захвата): `[blog-banner-form id=2666]`

Не вставлять в начале и не дублировать подряд.

### F. Изображения и инфографика

**Все изображения в статье** — обязательно оборачивать в lightbox-ссылку. Без этого картинки не открываются по клику и плохо видны в мобильной версии.

**Формат вставки (единый для всех изображений):**
```html
<div style="margin:32px 0; text-align:center;">
<a class="blog-gallery" href="{FULL_URL}" data-fslightbox="lightbox" title="{ALT}">
  <img class="image-border_yellow aligncenter size-full wp-image-{ID}"
       src="{FULL_URL}"
       alt="{ALT}"
       width="1150" height="740"
       style="max-width:100%; cursor:zoom-in;" />
</a>
<p style="margin:10px 0 0; font-size:13px; color:#888; text-align:center;">{CAPTION}</p>
</div>
```

- `{FULL_URL}` — полный URL из медиатеки WP (PNG или WebP)
- `{ALT}` — краткое описание для SEO, без ключевых слов через запятую
- `{CAPTION}` — подпись под картинкой (subtitle инфографики)
- `width="1150" height="740"` — стандартные размеры. Если изображение другого размера — подставить реальные
- `data-fslightbox="lightbox"` — обязательно, иначе zoom не работает

**Когда добавлять инфографику:**
- Воронка / схема / алгоритм с 4+ шагами
- Таблица сравнения, которую хочется визуализировать
- Раздел с формулами / бенчмарками (усиливает)
- Пошаговый процесс (steps)

**Генерация SVG → WebP через SSH:**
```bash
# SVG хранится в articles/<slug>/infographics/
rsvg-convert -w 2300 articles/<slug>/infographics/name.svg -o /tmp/name.png
cwebp -q 90 /tmp/name.png -o /var/www/.../uploads/YYYY/MM/name.webp
# Затем зарегистрировать в медиатеке WP и получить ID
```

**Параметры SVG-инфографики** (стиль блога, отличается от обложек):
- Размер: 1150×740
- Фон: `#FAFAFA`, скругление `rx="16"`
- Рамка: пунктирная золотая `stroke="#C2B674" stroke-dasharray="8 4"`
- Шрифт: Raleway (внешний Google Fonts, не base64)
- Акценты: `#C2B674`, `#E3A96C`, выделение `#FFF9EE`
- Текст: `#252525` (заголовки), `#666` (подписи)

### G. Формулы

**🔴 ОБЯЗАТЕЛЬНО:** Найти все инлайн-формулы в тексте и оформить их в стилизованный блок.

**Паттерны для поиска (regex):**
- `[A-ZА-Яa-zа-я\s]+ = [\d\(\)\/\×\+\-\%\s\.]+` — любое «X = выражение»
- `KPI[^\n]*=` — формулы KPI
- `\([^\)]+\) \× [^\n]+` — перемножение в скобках
- Текст вида «Пример: план 2 000 000 рублей, факт 1 700 000 рублей. KPI% = ...» — это формула с примером

**Как находить:** прочитать текст и найти все абзацы, где есть символ `=` между осмысленными частями, или математическое выражение с `×`, `÷`, `+`, `-`.

Формулы **никогда не оформлять как `<code>` или `<pre>`** — monospace-шрифт выглядит технически и неживо.

**Стандартный блок формулы:**
```html
<div style="background:#F5F3EC; border-left:4px solid #CC955B; border-radius:0 8px 8px 0; padding:18px 24px; margin:20px 0;">
  <p style="margin:0 0 6px; font-size:12px; color:#CC955B; font-weight:700; text-transform:uppercase; letter-spacing:1.5px;">Формула</p>
  <p style="margin:0; font-size:20px; font-weight:700; color:#252525; line-height:1.4;">{ФОРМУЛА}</p>
</div>
```

**Если у формулы есть название/подтип (напр. «Расширенная»):**
```html
<div style="background:#F5F3EC; border-left:4px solid #CC955B; border-radius:0 8px 8px 0; padding:18px 24px; margin:20px 0;">
  <p style="margin:0 0 6px; font-size:12px; color:#CC955B; font-weight:700; text-transform:uppercase; letter-spacing:1.5px;">Расширенная формула</p>
  <p style="margin:0; font-size:20px; font-weight:700; color:#252525; line-height:1.4;">{ФОРМУЛА}</p>
  <p style="margin:8px 0 0; font-size:13px; color:#888;">{ПОЯСНЕНИЕ: когда использовать}</p>
</div>
```

**Несколько формул рядом — каждая в своём блоке, без `margin:20px 0` между ними:**
```html
<div style="margin:24px 0; display:flex; flex-direction:column; gap:12px;">
  <div style="background:#F5F3EC; border-left:4px solid #CC955B; ...">...</div>
  <div style="background:#F5F3EC; border-left:4px solid rgba(204,149,91,0.4); ...">...</div>
</div>
```

Второй вариант в группе — приглушённая граница (`rgba(204,149,91,0.4)`), чтобы выделить основную.

**Правило:** искать в тексте любые конструкции типа `X = Y / Z`, `KPI = ...`, математические выражения — и заменять на блок формулы.

---

## Шаг 3 — Типографика

Обработать HTML статьи перед публикацией.

### &nbsp; (неразрывный пробел)

Заменить обычный пробел на `&nbsp;` после:
- Однобуквенных предлогов и союзов: `в`, `с`, `к`, `о`, `у`, `а`, `и`, `я`
- Двухбуквенных: `на`, `по`, `из`, `за`, `до`, `от`, `не`, `но`, `ни`
- Числа + единица: `500&nbsp;руб.`, `40&nbsp;минут`, `3&nbsp;месяца`

Где делать: `<p>`, `<li>`, `<h2>`, `<h3>`, `<h4>`, `<summary>`
Где НЕ делать: `<table>`, `<script>`, `<a href>`, HTML-атрибуты

### ‑ (неразрывный дефис U+2011)

Заменить обычный дефис `-` на `‑` в:
- Составных словах: `лид‑магнит`, `тест‑драйв`, `чек‑лист`, `онлайн‑курс`, `экспресс‑аудит`
- Диапазонах чисел: `40‑70%`, `5‑8%`

Где НЕ заменять: `<a href>`, `<script>`, CSS-классы

Для автоматической обработки — есть скрипт `articles/fix_nbsp.py`. Запустить по SSH если нужен полный проход.

---

## Шаг 3 — Подготовить данные для WordPress

Собери перед публикацией:

```
post_title:       [H1 статьи]
slug:             [url-адрес, латиницей, через дефис]
content:          [HTML статьи после типографики]
seo_title:        [50-60 символов]
seo_description:  [120-155 символов]
cover_subtitle:   [подзаголовок обложки, 3-5 слов, строчными]
cover_tag:        [тег обложки, 2-4 слова ЗАГЛАВНЫМИ · через точку]
author_id:        523  (Кандеев по умолчанию)
```

Примеры cover_subtitle и cover_tag:
- `ключевой этап воронки` / `15 ПРИМЕРОВ · АЛГОРИТМ`
- `как построить систему` / `ПОШАГОВЫЙ ГАЙД · 2025`

---

## Шаг 4 — Создать черновик в WordPress

Если черновика ещё нет:

```python
import requests
# WP_URL, WP_AUTH, WP_POST_TYPE, WP_AUTHOR_ID, REST_BASE — из project.md (Шаг 0)
# Дефолты Фактора если project.md не найден: YOUR_DOMAIN.ru, YOUR_WP_USER, blog, 523
url = f"{WP_URL}{REST_BASE}"
auth = WP_AUTH
data = {
    "title": "<post_title>",
    "content": "<content>",
    "slug": "<slug>",
    "status": "draft"
}
resp = requests.post(url, json=data, auth=auth)
post_id = resp.json()["id"]
```

Затем через SSH (`wp_ssh_host` из project.md, дефолт: YOUR_SERVER_IP, root):

```bash
# Поменять тип на WP_POST_TYPE (из project.md, дефолт: blog)
wp db query "UPDATE wp_posts SET post_type='{WP_POST_TYPE}' WHERE ID=<post_id>" --path=<wp_root> --allow-root

# ACF-поля (field IDs из project.md acf_* ключей, дефолты ниже)
wp post meta update <post_id> title '<seo_title>' --allow-root --path=<wp_root>
wp post meta update <post_id> _title 'field_676e65241784f' --allow-root --path=<wp_root>
wp post meta update <post_id> description '<seo_description>' --allow-root --path=<wp_root>
wp post meta update <post_id> _description 'field_676e653717850' --allow-root --path=<wp_root>
wp post meta update <post_id> robots '-' --allow-root --path=<wp_root>
wp post meta update <post_id> _robots 'field_676e655717851' --allow-root --path=<wp_root>
wp post meta update <post_id> author {WP_AUTHOR_ID} --allow-root --path=<wp_root>
wp post meta update <post_id> _author 'field_6749603017b58' --allow-root --path=<wp_root>
wp post meta update <post_id> cover_subtitle '<cover_subtitle>' --allow-root --path=<wp_root>
wp post meta update <post_id> cover_tag '<cover_tag>' --allow-root --path=<wp_root>
```

Предпросмотр черновика:
```
{WP_URL}/?post_type={WP_POST_TYPE}&p=<post_id>&preview=true
```

---

## Шаг 5 — Обложка

Обложки генерируются **автоматически** при каждом сохранении поста через mu-plugin `factor-cover-gen.php` — если заполнены `cover_subtitle` и `cover_tag`.

Что происходит автоматически:
1. Хук `save_post_blog` → запускает `/opt/svg_cover_gen.py --post_id X --auto` асинхронно
2. Скрипт читает post_title, cover_subtitle, cover_tag из WP
3. Авто-сплит title → line1 (≤2 слова) + line2 (остаток + год)
4. SVG square (600×600) и wide (2400×984) генерируются в чёрном стиле v5
5. ACF-поля `image` и `image-square` обновляются, featured image установлен

**Ничего делать не нужно** — достаточно заполнить ACF-поля `cover_subtitle` и `cover_tag` на шаге 4.

Если нужен **ручной перегенер** (после правки заголовка — запустить через SSH):
```bash
python3 /opt/svg_cover_gen.py --post_id <post_id> --auto --upload
# или с явными параметрами:
python3 /opt/svg_cover_gen.py --post_id <post_id> --line1 "Заголовок" --line2 "продолжение 2026" --subtitle "<cover_subtitle>" --tag "<cover_tag>" --prefix <slug[0]> --upload
```
Лог последней генерации: `/tmp/cover_gen_<post_id>.log`

---

## Шаг 6 — Публикация

```python
import requests
# WP_URL, WP_AUTH, WP_POST_TYPE — из project.md (Шаг 0)
url = f"{WP_URL}/?rest_route=/wp/v2/{WP_POST_TYPE}/{post_id}"
auth = WP_AUTH
requests.post(url, json={"status": "publish"}, auth=auth)
```

После публикации:
- Проверить страницу по URL
- Убедиться что обложки сгенерировались (image + image-square в ACF)
- Проверить мобильную версию

---

## Шаг 7 — Обновить llms.txt

**Выполнять сразу после публикации** — только для проектов с `llms_txt_path` в `project.md` или для дефолтного Фактора.

Дефолтный путь: `/var/www/YOUR_DOMAIN/public_html/llms.txt`

```python
import subprocess

# Собрать строку для llms.txt
# seo_description берём из ACF-поля (уже заполнено на шаге 4)
# Обрезаем до 80 символов, без кавычек
desc_short = seo_description[:80].rstrip()
new_line = f"- [{post_title}](https://{WP_DOMAIN}/blog/{slug}/): {desc_short}"

llms_path = project_config.get("llms_txt_path", "/var/www/YOUR_DOMAIN/public_html/llms.txt")

# Добавить в начало секции ## Блог (новые статьи сверху)
ssh_script = f"""
python3 - << 'PYEOF'
path = '{llms_path}'
with open(path) as f:
    content = f.read()
new_line = '''{new_line}'''
if new_line in content:
    print("llms.txt: строка уже есть, пропускаем")
else:
    content = content.replace('## Блог\\n', f'## Блог\\n{{new_line}}\\n')
    with open(path, 'w') as f:
        f.write(content)
    print(f"llms.txt обновлён: {slug}")
PYEOF
"""

result = subprocess.run(
    ["ssh", "-o", "StrictHostKeyChecking=no", f"root@{WP_SSH_HOST}", ssh_script],
    capture_output=True, text=True
)
print(result.stdout or result.stderr)
```

**Правила:**
- Новые статьи вставлять **в начало** секции `## Блог` — свежие выше
- Если `post_type` не `blog` (страница, лендинг) — **не добавлять** в llms.txt
- Если `project.md` не содержит `llms_txt_path` и проект не Фактор — пропустить

---

## Шаг — Обратные ссылки (только для статических HTML-блогов, когда нет wp_url)

**Выполнять ПОСЛЕ обновления blog/index.html и sitemap.xml, ДО деплоя.**

Цель: убедиться, что тематически близкие статьи ссылаются на новую статью. Без этого новая страница выпадает из внутреннего ссылочного графа и медленнее индексируется.

### Алгоритм

1. **Собрать исходящие ссылки новой статьи:**
```bash
grep -o 'href="/blog/[^"]*"' pages/blog/<slug>/index.html | sort -u
```

2. **Для каждой связанной статьи проверить, есть ли обратная ссылка:**
```bash
grep -l "<slug>" pages/blog/*/index.html
```
Если файл найден — ссылка уже есть. Если нет — нужно добавить.

3. **Добавить обратную ссылку** в каждую статью, где её нет:
- Найти абзац, где упоминается тема новой статьи (`grep -n "ключевое_слово"`)
- Вписать ссылку в конец этого абзаца: `Подробнее: <a href="/blog/<slug>/">Анкор</a>.`
- Анкор = H1 новой статьи (без года), коротко

4. **Задеплоить изменённые файлы** вместе с основным деплоем (уникальные имена через `/tmp/`)

### Правила

- Добавлять ссылку только туда, где она уместна по смыслу — не насильно
- Анкор описательный, не «здесь» / «подробнее»
- Не добавлять больше 1 обратной ссылки на статью из одного файла
- Если в связанной статье уже 7+ внутренних ссылок — пропустить

---

## Gotchas

- **FAQ — ТОЛЬКО голые `<details><summary>` БЕЗ inline-стилей** — FAQ в виде `<h3>Вопрос</h3><p>Ответ</p>` — критическая ошибка (выглядит как жирные H3). Правильный формат: `<details>\n<summary>Вопрос?</summary>\n<p>Ответ.</p>\n</details>` — никаких `style=`, никаких `class=`, никаких wrapper-div. Тема faktor-template сама стилизует аккордеон. Добавление inline-стилей делает FAQ не похожим на остальные статьи сайта. Эталон: WP post 125 (5 этапов продаж).
- **Ссылки на кейсы — полный href без вложенных `<a>`** — запрещено генерировать `<a href="/case/full-slug/"><a href="/case/">текст</a>slug</a>`. Правильный формат: `<a href="https://YOUR_DOMAIN.ru/case/full-slug/">текст</a>`. Двойные вложенные `<a>` рендерятся как broken link: текст + slug после закрывающего тега.

- **llms.txt — только для post_type=blog** — страницы (`/services/`, `/case/`) не добавлять в llms.txt автоматически. Если нужно — обновить вручную.
- **llms.txt — новые статьи сверху** — вставлять в начало `## Блог`, не в конец. Свежий контент важнее для LLM-индексации.
- **author_id всегда 523** — Кандеев по умолчанию. Не забывать при создании поста через API и при обновлении ACF-полей.
- **post_type = 'blog', не 'post'** — WP API создаёт `post`, нужно вручную менять через `wp db query`. Без этого статья не появится в блоге.
- **🔴 Не публиковать до «публикуем»** — после создания черновика и Google Doc ПОЛНАЯ ОСТАНОВКА. Ждать буквально слово «публикуем». «да», «ок», «всё ок», «хорошо» — НЕ считаются. Нарушение этого правила критично: статья уйдёт в публикацию без проверки.
- **Не ставить &nbsp; внутри `<table>`** — только в `<p>`, `<li>`, `<h2>`, `<summary>`. В ячейках таблиц &nbsp; ломает выравнивание.
- **`<ul>/<li>` со ссылками — всегда заменять на `<div>`-список**: тема применяет к `ul li a` агрессивные стили (float/flex), ни `display:inline`, ни `!important` не помогают — текст расплывается в две колонки. Единственный надёжный фикс: `<div>`-список. Тема не применяет стили к `<div>`. **Правило: если в `<ul>` есть хотя бы одна `<a>` — весь список заменять на `<div>`-список.** Также: `<div>` внутри flex-контейнера получает margin от темы — обязательно `margin:0 !important` на каждом пункте:
  ```html
  <div style="margin:16px 0; display:flex; flex-direction:column; gap:6px;">
  <div style="display:flex; gap:10px; align-items:flex-start; margin:0 !important;"><span style="color:#CC955B; font-size:18px; line-height:1.5; flex-shrink:0;">•</span><div style="margin:0 !important;">Текст с <a href="/url/">ссылкой</a>.</div></div>
  <div style="display:flex; gap:10px; align-items:flex-start; margin:0 !important;"><span style="color:#CC955B; font-size:18px; line-height:1.5; flex-shrink:0;">•</span><div style="margin:0 !important;">Последний пункт.</div></div>
  </div>
  ```
- **FAQ accordion — тема добавляет каждому `<details>` свои border/border-radius/margin**: отдельные боксы вместо единого аккордеона. Фикс: добавить `!important`-сбросы на каждый `<details>`, кроме `border-bottom` (разделитель). На `<summary>` и ответный `<div>` добавить `margin:0 !important`:
  ```html
  <!-- Средние items (не последний): -->
  <details style="border-bottom:1px solid #E8E8E0; margin:0 !important; padding:0 !important; border-radius:0 !important; border-left:none !important; border-right:none !important; border-top:none !important;">
    <summary style="...; margin:0 !important;">Вопрос?<span>+</span></summary>
    <div style="...; margin:0 !important;">Ответ.</div>
  </details>
  <!-- Последний item: -->
  <details style="margin:0 !important; padding:0 !important; border:none !important; border-radius:0 !important;">
    ...
  </details>
  ```
- **`<li><strong>Заголовок.</strong> Текст</li>` — заменять на таблицу** — тема рендерит это как двухколоночный список с переносами. **КРИТИЧНО: проверять ВСЕ `<ul>` в статье перед публикацией** — паттерн `<li><strong>` встречается несколько раз (например, список ролей + список инструментов). Смотреть глазами, не только поиском по одному вхождению.
- **Обложки генерируются автоматически** — mu-plugin `factor-cover-gen.php` запускает `svg_cover_gen.py --auto` при каждом сохранении blog-поста. Достаточно заполнить `cover_subtitle` и `cover_tag`. Ручной запуск больше не нужен.
- **Обложки: ручной перегенер** — только если нужно исправить заголовок на обложке после публикации: `python3 /opt/svg_cover_gen.py --post_id <id> --auto --upload`. Лог: `/tmp/cover_gen_<id>.log`.
- **Google Doc создаётся до ревью, WP черновик — тоже до ревью** — оба параллельно в Шаге 0. Не ждать «публикуем» для создания черновиков.
- **Google Doc = полный текст статьи, не метаданные** — пользователь читает и правит именно Google Doc. Вставлять весь HTML-контент конвертированный в plain text через htmlToText() с маркерами ## для H2. Применять стили HEADING_1/HEADING_2 через googleapis batchUpdate. Не вставлять вместо статьи URL, SEO-поля или технические данные.
- **Таблицы без margin слипаются с текстом** — всегда оборачивать в `<div style="margin:28px 0;">`. Проверить каждую таблицу.
- **Формулы через `<code>` — запрещено** — только styled div с border-left:#CC955B. Искать все `X = Y/Z` в тексте и переоформлять.
- **«— Показатель: значение» — это ВСЕГДА таблица** — списки с тире и двоеточием (даже в `<p>` или `<li>`) должны стать `<table>`. Это самый частый пропуск агента. Если несколько групп (Хантер/Фермер/Клоузер) — одна широкая таблица с колонкой на каждую роль.
- **Формулы в строчку — это НЕ параграф** — любое «X = (A/B) × 100%» в `<p>` должно стать styled div с border-left:#CC955B. Смотреть на `=`, `×`, `÷` в тексте.
- **Нумерованные списки > 7 пунктов** — первые 5 видны, остальные в `<details>`. Правило распространяется не только на `<table>`, но и на `<ol>`, `<ul>` и нумерованные блоки в `<p>`.
- **Изображения без lightbox** — вставлять только через `<a class="blog-gallery" data-fslightbox="lightbox">`. `<figure>` без ссылки → картинка не открывается по клику. **КРИТИЧНО:** `data-fslightbox` должен быть `"lightbox"`, не `"article-gallery"` и не любое другое значение. `class="blog-gallery"` обязателен на `<a>` — без него тема не инициализирует lightbox. Итоговый формат строго: `<a class="blog-gallery" href="{URL}" data-fslightbox="lightbox" title="{ALT}">`.
- **Длинные таблицы > 7 строк** — первые 5 видны, остальные в `<details>`. Особенно важно для таблиц примеров, KPI, списков формул.
- **`<p><strong>Шаг N:</strong>`** — это НЕ список и не collapse. Любой блок пошаговой инструкции (2+ шагов) → визуальные карточки с золотым кружком (раздел H). Никогда не оставлять как plain `<p>`.
- **Лейбл и текст шага — в разных `<div>`, не `<p>`**: тема сайта переопределяет `line-height` и `margin` у всех `<p>` в контенте блога, из-за чего строки раздвигаются и кружок улетает наверх. `<div>` не наследует эти стили. Всегда использовать `<div>` вместо `<p>` внутри карточек.
- **Фон карточек — белый `#fff`**, не `#FAFAF7`. Тёплый серый давит на глаз когда карточек 5+.
- **FAQ в середине статьи** — запрещено. FAQ всегда последний H2, строго после «Что дальше». Если в статье FAQ стоит в другом месте — вырезать и переместить в конец.
- **«Вопрос: / Ответ:» как параграфы** — запрещённый формат. Всегда конвертировать в `<details><summary>` аккордеон (раздел I). При получении статьи — сразу проверить, не оформлен ли FAQ как `<p>Вопрос: ...</p><p>Ответ: ...</p>`.
- **FAQ wrapper div + inline-стили = отдельные боксы** — wrapper `<div style="border:1px solid; border-radius:8px; overflow:hidden;">` и inline-стили `border-bottom:1px solid` / `!important` на `<details>` не работают: тема добавляет каждому `<details>` собственные border/border-radius/margin и они рендерятся как отдельные боксы. **Правильный формат — только голые `<details>` без обёртки и без inline-стилей** (см. раздел I и эталон /blog/5-etapov-prodazh-menedzhera-po-prodazham/).
- **Формулы Excel/Google Sheets** (`=D2/C2*100`, `=СУММ(...)`, `=ЕСЛИ(...)`) — это инлайн `<code>` с тёплым фоном, НЕ styled div с border-left. Styled div — только для математических/расчётных формул (KPI% = Факт/План × 100%). Разграничение: есть знак `=` в начале и синтаксис Excel — это code. Есть `×`, `÷` и текстовое описание — это styled div.
- **`<p>Подзаголовок:</p>`** между блоками контента → `<h3 id="anchor">`. Типичные примеры: «Исходные данные:», «Показатели и веса:», «Расчёт KPI:», «Сквозной кейс:» — все это H3, не параграфы.

## Итоговый чеклист публикации

**Контент:**
- [ ] H1 с годом
- [ ] TOC-блок + H2 с id-якорями
- [ ] Нет `[ПРОВЕРИТЬ]` в тексте
- [ ] Внутренние ссылки: 5–7 штук
- [ ] Списки → таблицы (где уместно)
- [ ] Blockquote class="yellow": 1–2 шт.
- [ ] Blog-баннер в середине: `[blog-banner id=1480]`
- [ ] FAQ: 4+ вопроса, JSON-LD + details/summary аккордеон (не «Вопрос:/Ответ:» параграфы)
- [ ] Порядок финала: «Что дальше» → [blog-banner-form] → «Частые вопросы»
- [ ] Шаги `<p><strong>Шаг N:</strong>` → визуальные карточки с кружками
- [ ] Excel-формулы → инлайн `<code>`, математика → styled div с border-left

**Типографика:**
- [ ] &nbsp; после однобуквенных предлогов
- [ ] Неразрывные дефисы ‑ в составных словах
- [ ] Нет &nbsp; внутри `<table>`

**WordPress:**
- [ ] SEO Title (50–60 символов)
- [ ] SEO Description (120–155 символов)
- [ ] cover_subtitle и cover_tag заполнены
- [ ] post_type = blog
- [ ] author = 523
- [ ] Предпросмотр проверен
- [ ] Опубликовано; обложки генерируются автоматически (лог: `/tmp/cover_gen_<id>.log`)
- [ ] llms.txt обновлён (Шаг 7) — новая статья добавлена в секцию ## Блог
