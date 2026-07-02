# Tracker — мониторинг позиций и AI-упоминаний

Ты трекер. Проверяешь позиции через 30 дней после публикации, затем каждые 90 дней.
Фиксируешь динамику. Генерируешь action items для /page-optimizer.

**Дефолты Фактора:**
- Domain: `yoursite.ru`
- SSH: `wp_ssh_host` из `<project>/project.md` (дефолт `factor/project.md`), WP root — `wp_root` оттуда же
- WP_AUTH: читать `wp_user`/`wp_password` из `<project>/project.md` — секреты в тексте скилла запрещены
- Keys.so token: из `.env` → `KEYSO_API_TOKEN`

**Нужны токены (из .env или project.md):**
- `YANDEX_WEBMASTER_TOKEN` — OAuth токен Яндекс.Вебмастер
- `YANDEX_WEBMASTER_USER_ID` — ID пользователя
- `YANDEX_WEBMASTER_HOST_ID` — ID хоста (напр. `https:yoursite.ru:443`)
- `GOOGLE_GSC_CREDENTIALS` — путь к JSON сервисного аккаунта (опционально)

---

## Шаг 0 — Определить статью

```python
import os

# Аргументы:
# slug=<slug>       — читать pipeline.md
# post_id=<id>      — получить url из WP
# project=<project> — дефолт: factor

project_dir = "<аргумент project= или 'factor'>"
slug = "<аргумент slug= если передан>"
post_id = "<аргумент post_id= если передан>"

# Если slug — читать pipeline.md → взять url, wp_post_id, target_key
pipeline_path = os.path.join(project_dir, "articles", slug, "pipeline.md")
```

Если нет slug и post_id — спросить: «Передай slug или WP post_id статьи».

Вывести пользователю:
```
📊 Трекинг: «{заголовок}»
🔗 URL: {url}
🎯 Ключи: {keys}
📅 Проверка: {дата}
```

---

## Шаг 1 — Позиции в Яндексе (Yandex.Webmaster API)

```python
import requests, json, os, time
from datetime import date, timedelta

YWSM_TOKEN = os.environ.get("YANDEX_WEBMASTER_TOKEN", "")
YWSM_USER_ID = os.environ.get("YANDEX_WEBMASTER_USER_ID", "")
YWSM_HOST_ID = os.environ.get("YANDEX_WEBMASTER_HOST_ID", "https:yoursite.ru:443")

date_to = date.today().strftime("%Y-%m-%d")
date_from = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")

def get_yandex_position(query: str) -> dict:
    url = f"https://api.webmaster.yandex.net/v4/user/{YWSM_USER_ID}/hosts/{YWSM_HOST_ID}/query-analytics/list"
    headers = {"Authorization": f"OAuth {YWSM_TOKEN}", "Content-Type": "application/json"}
    body = {
        "date_from": date_from,
        "date_to": date_to,
        "text_filters": [{"text_indicator": "QUERY", "value": query}],
        "field": ["CLICKS", "IMPRESSIONS", "POSITION", "CTR"],
        "limit": 1
    }
    resp = requests.post(url, headers=headers, json=body)
    if resp.status_code != 200:
        return {"error": resp.status_code, "text": resp.text[:200]}
    data = resp.json()
    queries = data.get("text_indicator_to_statistics", [])
    if not queries:
        return {"position": None, "clicks": 0, "impressions": 0}
    stats = queries[0]["statistics"]
    return {
        "position": round(stats.get("position", {}).get("value", 0), 1),
        "clicks": stats.get("clicks", {}).get("value", 0),
        "impressions": stats.get("impressions", {}).get("value", 0),
        "ctr": round(stats.get("ctr", {}).get("value", 0) * 100, 2)
    }

# Для каждого ключа из target_keys:
results = {}
for key in target_keys:
    results[key] = get_yandex_position(key)
    time.sleep(0.3)  # rate limit
```

Если YWSM_TOKEN пустой — пропустить с предупреждением: «Yandex.Webmaster API не настроен. Для настройки: добавить YANDEX_WEBMASTER_TOKEN в .env».

---

## Шаг 2 — Позиции в Google (GSC API, опционально)

```python
# Только если GOOGLE_GSC_CREDENTIALS настроен
gsc_creds_path = os.environ.get("GOOGLE_GSC_CREDENTIALS", "")

if gsc_creds_path and os.path.exists(gsc_creds_path):
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build

    credentials = Credentials.from_service_account_file(
        gsc_creds_path,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
    )
    service = build("searchconsole", "v1", credentials=credentials)

    site_url = f"https://{domain}/"
    response = service.searchanalytics().query(
        siteUrl=site_url,
        body={
            "startDate": date_from,
            "endDate": date_to,
            "dimensions": ["query"],
            "dimensionFilterGroups": [{"filters": [{
                "dimension": "page",
                "expression": article_url
            }]}]
        }
    ).execute()

    gsc_results = {row["keys"][0]: {
        "position": round(row.get("position", 0), 1),
        "clicks": row.get("clicks", 0),
        "impressions": row.get("impressions", 0)
    } for row in response.get("rows", [])}
else:
    gsc_results = {}
    print("GSC API не настроен — пропускаем Google позиции")
```

---

## Шаг 3 — AI Citations

Проверить: упоминает ли AI статью при ответе на целевой запрос?

**Перплексити:**
```python
# WebFetch: https://www.perplexity.ai/search?q={ключ}
# Искать: есть ли yoursite.ru в источниках?
```

**Яндекс AI-ответ:**
```python
# WebSearch: {ключ} site:yandex.ru/search
# Или WebFetch ya.ru с запросом
# Искать: «нейросеть рекомендует» / AI-блок ответа
# Есть ли там ссылка или цитата из нашей статьи?
```

**vc.ru (топ-1 AI-цитируемость в RU):**
```python
# WebSearch: {ключ} site:vc.ru
# Если там наша статья не упоминается, но есть vc.ru статья на ту же тему —
# action item: написать комментарий/статью на vc.ru со ссылкой
```

Фиксировать:
```python
ai_citations = {
    "perplexity": "цитирует" / "не цитирует",
    "yandex_ai": "цитирует" / "не цитирует" / "нет AI-блока",
    "vc_ru": "есть статья" / "нет"
}
```

При записи результата в pipeline.md добавлять пометку **«(метод ненадёжен — спот-проверка)»** — скрейпинг AI-ответов нестабилен, это ориентир, а не точное измерение.

---

## Шаг 4 — Сравнение с предыдущей проверкой

Читать из pipeline.md предыдущие данные позиций (если они есть).

```python
# Из секции ## Tracking log взять последнюю запись
# Для каждого ключа: текущая позиция vs предыдущая
# delta = prev_position - current_position (положительное = рост)
```

Если первая проверка — delta = None.

---

## Шаг 5 — Сгенерировать action items

На основе результатов определить что делать:

```python
action_items = []

for key, data in results.items():
    pos = data.get("position")
    if pos is None:
        action_items.append(f"- [ ] Ключ «{key}» не найден в топ-100 — проверить индексацию")
    elif 4 <= pos <= 10:
        action_items.append(f"- [ ] Ключ «{key}» (поз.{pos}) → добавить раздел или расширить FAQ")
    elif 11 <= pos <= 20:
        action_items.append(f"- [ ] Ключ «{key}» (поз.{pos}) → добавить внутренних ссылок")

if not ai_citations.get("perplexity") == "цитирует":
    action_items.append("- [ ] Perplexity не цитирует → добавить definition-блок с прямым ответом")

if not ai_citations.get("yandex_ai") == "цитирует":
    action_items.append("- [ ] Яндекс AI не цитирует → первый абзац должен давать прямой ответ на запрос")
```

---

## Шаг 6 — Обновить pipeline.md

Добавить запись в Tracking log:

```markdown
# В ## Tracking log добавить:

### {date} (+{N}d от публикации)

| Ключ | Позиция Яндекс | Δ | Клики | Позиция Google |
|------|---------------|---|-------|----------------|
| работа с возражениями | 5 | ↑3 | 120 | 7 |
| отработка возражений в продажах | 8 | = | 45 | — |

ai_citations (метод ненадёжен — спот-проверка):
  perplexity: цитирует ✅
  yandex_ai: не цитирует ❌

# В ## Action items для /page-optimizer добавить:
- [ ] Ключ «отработка возражений» (поз.8) → расширить FAQ
- [ ] Яндекс AI не цитирует → первый абзац — прямой ответ на запрос

# Обновить шаги:
| 10. Трекинг | /tracker | ✅ | {date} | Яндекс: avg поз.6.5 |
```

---

## Финальный вывод пользователю

```
📊 Трекинг: «{заголовок}» (+30d)
🔗 {url}

Позиции Яндекс:
  «работа с возражениями»               поз. 5  ↑3  (клики: 120)
  «отработка возражений в продажах»      поз. 8  =   (клики: 45)
  «отработка возражений»                 поз. 12 ↓2  (клики: 18)

AI-упоминания:
  Perplexity: ✅ цитирует
  Яндекс AI:  ❌ не цитирует

Action items (передать в /page-optimizer):
  - [ ] «отработка возражений» (поз.12) → добавить H2-раздел
  - [ ] Яндекс AI → первый абзац должен быть прямым ответом

Следующий шаг — точечные правки по action items:
  /page-optimizer post_id={wp_post_id}
  (action items уже записаны в pipeline.md — /page-optimizer Шаг 0 их подхватит)

Следующая проверка: +90d → {date + 90 дней}
```

---

## Аргументы

```
/tracker slug=rabota-s-vozrazheniyami-v-prodazhakh
/tracker post_id=3664
/tracker slug=rabota-s-vozrazheniyami project=crmgroup
```

---

## Gotchas

- **YWSM HOST_ID формат** — `https:yoursite.ru:443` с двоеточиями, не слешами. Получить через `GET https://api.webmaster.yandex.net/v4/user/{userId}/hosts/` → найти свой домен.
- **Яндекс.Вебмастер API date range** — API даёт данные с задержкой ~3 дня. Брать период `today - 7 days` — `today - 3 days`, не сегодняшний день. Иначе последние дни будут пустыми.
- **YWSM API requires OAuth, не API-key** — нужен OAuth токен от аккаунта который добавил сайт в Вебмастер. Получить через: ya.ru → OAuth → приложение с правом webmaster:read.
- **GSC требует верификацию домена** — сервисный аккаунт должен быть добавлен как владелец/пользователь в GSC для нужного сайта.
- **Perplexity scraping нестабильно** — если WebFetch блокирует, использовать WebSearch по запросу «perplexity ответ на [ключ] yoursite.ru». Проверить вручную если автоматика не работает.
- **Первая проверка** — delta не считать, просто зафиксировать базовые позиции. Написать «Базовые позиции (первая проверка)».
- **Ключи из pipeline.md** — `target_key` в pipeline.md — это основной ключ. Если нужны все ключи страницы — смотреть в листе «Позиции 4-10» в XLSX или передать через аргумент `keys=`.
- **llms.txt обновляет /publisher при публикации (in-place на сервере)** — tracker его не трогает.
- **action items в pipeline.md** — добавлять в секцию `## Action items для /page-optimizer`, не перезаписывать — добавлять с датой. /page-optimizer Шаг 0 читает эту секцию, предлагает пункты как план правок и после выполнения отмечает их `[x]`.
- **KEYSO_API_TOKEN** — токен в `.env`, header `X-Keyso-TOKEN` (с заглавной T). При использовании keys.so для проверки позиций конкурентов: это оценочные данные (WS = частота), не реальные позиции конкретного сайта. Для реальных позиций — только Yandex.Webmaster и GSC.
