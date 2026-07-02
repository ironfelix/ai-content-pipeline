# AI Content Pipeline — скиллы для Claude Code

Система AI-агентов, которая автоматизирует создание контента — от исследования темы до публикации в WordPress и отслеживания позиций. Ядро — конвейер из 11 агентов; плюс /link-check и 6 скиллов для аудита и онбординга клиента. Каждый агент — отдельный скилл для [Claude Code](https://claude.ai/code).

**Живая демонстрация:** [ironfelix.github.io/agentiq-reviews/ai-seo-pipeline](https://ironfelix.github.io/agentiq-reviews/ai-seo-pipeline/)

---

## Как это работает

Один запрос типа «напиши статью про управление отделом продаж» проходит через цепочку специализированных агентов:

```
/researcher → /writer → /methodology-gate → /editor → /fact-checker → /quality-gate
     → /seo-optimizer → /publisher sync → [/designer] → /publisher → /tracker → /page-optimizer
```

Каждый агент делает одно и делает это хорошо. Результат каждого шага записывается в `pipeline.md` — трекер состояния статьи.

---

## Агенты

### 1. `/researcher` — исследование темы
Читает топ-10 конкурентов, находит уникальный угол, строит Query fan-out кластер (5–8 смежных вопросов которые Google AI генерирует вокруг запроса). Сохраняет Research Report в файл.

**Вход:** тема / ключевой запрос
**Выход:** `research/slug-research.md` + создаёт `articles/slug/pipeline.md`

### 2. `/writer` — написание черновика
Пишет статью по Research Report. Первый абзац = TL;DR (прямой ответ → цифра из опыта → контр-интуитивная позиция). Структура H2 закрывает весь fan-out кластер.

**Вход:** `research=путь/к/research.md`
**Выход:** черновик в Google Doc

### 3. `/methodology-gate` — методологический гейт
Сверяет черновик с реальной методологией и продуктом клиента (воронка, этапы, роли, метрики, платность услуг, границы «что делаем / не делаем») и БЛОКИРУЕТ при искажениях. Автоматизированная замена нишевого эксперта-ревьюера. Запускается после /writer и повторно после /editor; вердикт пишет в pipeline.md, /publisher без PASS не публикует.

### 4. `/editor` — редактура
Убирает AI-паттерны («следует отметить», «важно понимать», «таким образом»), добавляет голос бренда, заменяет расплывчатость на конкретику. Оставляет комментарии прямо в Google Doc.

**Вход:** Google Doc ID или текст
**Выход:** отредактированный Google Doc с комментариями

### 5. `/fact-checker` — верификация фактов
Проверяет каждый факт по трёхуровневой системе: T1 (оригинальный отчёт), T2 (крупное СМИ), T3 (неверифицировано). Помечает сомнительные данные, правит Google Doc.

**Вход:** Google Doc ID
**Выход:** исправленный Google Doc + обновлённая `knowledge-base.md`

### 6. `/quality-gate` — автоматический чеклист
Прогоняет 24 проверки (17 блокирующих + 2 мягких + 5 WARN): запрещённые обороты, тире, метки [ПРОВЕРИТЬ], H1 с ключом, TOC, H2 минимум 3, FAQ минимум 4, Schema.org, длина ≥ 1500 слов, внутренние ссылки 2–4 (макс 1 коммерческая), кейс, автор, год, non-commodity check, первый абзац = TL;DR, burstiness, живой сленг аудитории, резкие мнения.

**Результат:** `PASS` → разблокирует /publisher. `FAIL` → конкретные замечания → возврат в /editor.

### 7. `/seo-optimizer` — SEO-упаковка
Генерирует 3 варианта H1, SEO title (до 62 символов), description (до 158 символов), проверяет H2 как самостоятельные поисковые запросы, добавляет FAQ из Wordstat, проставляет внутренние ссылки.

**Вход:** slug статьи
**Выход:** SEO-пакет в `pipeline.md`

### 8. `/designer` — инфографика
Создаёт supporting визуалы: воронки, шаги, статистику, сравнительные таблицы. Два режима: HTML→PNG через Playwright (для WordPress) или Pencil MCP (для дизайн-системы).

**Вход:** тип инфографики + данные
**Выход:** изображения загружены в WordPress media library

### 9. `/publisher` — публикация
Синхронизирует Google Doc → WordPress черновик. После команды «публикуем»: форматирует HTML (TOC, TL;DR-блок, FAQ в `<details>`, Schema.org JSON-LD), заполняет ACF-поля, генерирует обложки, публикует.

**Hard gates:** pipeline.md PASS по всем этапам + явная команда «публикуем»
**Выход:** опубликованная статья на сайте

### 10. `/tracker` — мониторинг позиций
Проверяет позиции в Яндекс.Вебмастер и Google Search Console, ищет упоминания в AI-ответах (ChatGPT, Perplexity, Claude), составляет action items для /page-optimizer, обновляет `llms.txt`.

**Вход:** slug или post_id
**Выход:** отчёт по позициям + action items в pipeline.md

### 11. `/page-optimizer` — улучшение опубликованных страниц
Добавляет новые H2 под запросы с позиций 4–10, дополняет FAQ, проставляет внутренние ссылки. Работает с RAW-контентом WordPress чтобы не сломать шорткоды.

**Вход:** `post_id=123`
**Выход:** обновлённая опубликованная статья + `pipeline.md` отмечен ✅

---

## Дополнительные скиллы (аудит и онбординг)

Нужны не для каждой статьи, а на старте проекта или для аудитов.

- **`/marketing-audit`** — оркестратор аудита сайта: тех-SEO → контент/семантика → конкуренты и gap, по порядку.
- **`/knowledge-session`** — структурированное интервью с клиентом (~60 мин). Выдаёт `data/company-context.md` и `data/voice.md`, на которых работают writer/editor.
- **`/seo-tech-audit`** — технический аудит: robots, sitemap, индексация, мета, canonical, Core Web Vitals, структура URL.
- **`/seo-content-audit`** — семантическое ядро, кластеризация по интентам, покрытие страницами, дыры в контент-плане.
- **`/seo-competitors-gap`** — органические конкуренты через keys.so + gap-анализ (какие ключи есть у них и нет у нас).
- **`/audit-report-builder`** — собирает из research-файлов единый HTML-отчёт для клиента.

---

## Что накапливается с каждой статьёй

| Файл | Что хранит |
|------|-----------|
| `articles/slug/pipeline.md` | Статус каждого шага конвейера |
| `knowledge-base.md` | Верифицированные факты и источники |
| `review-patterns.md` | Типичные ошибки из редакторских правок |
| `llms.txt` | AI-читаемая карта сайта (для Claude, Perplexity) |

Система умнеет с каждой статьёй — накопленная база знаний используется в следующих материалах.

---

## Требования

- [Claude Code](https://claude.ai/code) (Pro или API)
- WordPress с REST API и Application Passwords
- Google Docs MCP (`~/.claude/mcp-servers/google-docs/`)
- SSH-доступ к серверу (для обложек и llms.txt)
- Python 3.8+ с `requests`, `beautifulsoup4`
- [Keys.so](https://keys.so) API (для /seo-optimizer и /tracker, опционально)

---

## Установка

### 1. Скопировать скиллы

```bash
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

### 2. Создать project.md для своего проекта

```bash
cp project-template/project.md myproject/project.md
# Заполнить: WP_URL, WP_USER, WP_PASSWORD, SSH_HOST, бренд-голос, правила
```

### 3. Настроить .env

```bash
cp .env.example .env
# Добавить: KEYSO_API_TOKEN, YANDEX_WEBMASTER_TOKEN, GOOGLE_PSI_API_KEY
```

### 4. Первая статья

```bash
# В Claude Code:
/researcher тема="управление командой продаж" project=myproject
/writer research=myproject/research/upravlenie-komandoy-research.md
/editor doc_id=GOOGLE_DOC_ID
/quality-gate slug=upravlenie-komandoy
/seo-optimizer slug=upravlenie-komandoy
/publisher slug=upravlenie-komandoy
```

---

## Структура проекта

```
myproject/
├── project.md              # конфиг проекта (WP, SSH, бренд-голос)
├── brief.md                # шаблон брифа для новых статей
├── WRITING_RULES.md        # правила написания под голос бренда
├── research/               # research reports от /researcher
├── articles/               # pipeline.md трекеры для каждой статьи
│   └── slug/
│       └── pipeline.md
└── data/
    ├── company-context.md  # контекст компании (кейсы, цифры, продукт)
    ├── knowledge-base.md   # накопленная база фактов
    └── review-patterns.md  # ошибки из редакторских правок
```

---

## Формат project.md

```markdown
# Project Config

wp_url: https://yoursite.com
wp_user: YOUR_WP_USER
wp_password: YOUR_WP_APP_PASSWORD
wp_post_type: post
wp_author_id: 1
ssh_host: YOUR_SERVER_IP
ssh_user: root
wp_root: /var/www/YOUR_DOMAIN/public_html

author_name: Иван Иванов
brand_voice: компания с 100+ клиентами, тон прямой и партнёрский
writing_rules: myproject/WRITING_RULES.md
company_context: myproject/data/company-context.md
cases_url: yoursite.com/cases/
do_not_mention: конкуренты X, Y, Instagram, Facebook
```

---

## Ключевые принципы системы

**TL;DR-первый абзац.** По данным исследования 36 млн AI Overviews: 55% цитат берётся из первых 30% текста. Первый абзац должен давать полный ответ без опоры на остальную статью. Формула: `[ключ + прямой ответ] → [цифра из опыта] → [контр-интуитивная позиция]`

**Query fan-out.** Google AI генерирует 5–8 смежных запросов вокруг одного запроса. /researcher строит кластер этих вопросов, /writer закрывает каждый вопрос отдельным H2.

**Non-commodity check.** Контент который можно заменить промптом «напиши статью про X» — AI не цитирует. Нужен хотя бы один элемент: кейс с числами, позиция с которой часть читателей не согласится, или факт которого нет у конкурентов.

**pipeline.md как state machine.** /publisher не публикует без PASS по всем этапам. Каждый скилл записывает свой результат. История каждой статьи сохраняется.

---

## Лицензия

MIT — используй, адаптируй, улучшай.
