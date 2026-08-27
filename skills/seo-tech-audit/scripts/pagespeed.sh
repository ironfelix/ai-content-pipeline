#!/usr/bin/env bash
# PageSpeed Insights API — Core Web Vitals для URL
# Usage: ./pagespeed.sh <url> [mobile|desktop]
# Требует GOOGLE_PSI_API_KEY в окружении или в ai-seo/.env
#
# Вывод: core_web_vitals_field — полевые данные CrUX (реальные CWV: LCP/INP/CLS,
# percentile + category), lab_metrics — лабораторный прогон Lighthouse.
# Поля может не быть (мало трафика в CrUX) — тогда core_web_vitals_field: null.

set -e

URL="${1:-}"
STRATEGY="${2:-mobile}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <url> [mobile|desktop]" >&2
  exit 1
fi

# Подхватываем .env из ai-seo если нет в окружении
if [ -z "$GOOGLE_PSI_API_KEY" ] && [ -f "$HOME/Documents/ivanilin/ai-seo/.env" ]; then
  export $(grep -E '^GOOGLE_PSI_API_KEY=' "$HOME/Documents/ivanilin/ai-seo/.env" | xargs) 2>/dev/null || true
fi

if [ -z "$GOOGLE_PSI_API_KEY" ]; then
  echo "ERROR: GOOGLE_PSI_API_KEY не задан. Получи ключ: https://developers.google.com/speed/docs/insights/v5/get-started" >&2
  exit 2
fi

TMP_JSON="$(mktemp)"
trap 'rm -f "$TMP_JSON"' EXIT

# До 3 попыток: ретрай на 429/5xx/пустой ответ, пауза растёт
ATTEMPTS=3
HTTP_CODE=000
for i in $(seq 1 $ATTEMPTS); do
  HTTP_CODE=$(curl -sS -G -o "$TMP_JSON" -w "%{http_code}" \
    "https://www.googleapis.com/pagespeedonline/v5/runPagespeed" \
    --data-urlencode "url=${URL}" \
    --data-urlencode "strategy=${STRATEGY}" \
    --data-urlencode "category=performance" \
    --data-urlencode "category=seo" \
    --data-urlencode "category=accessibility" \
    --data-urlencode "category=best-practices" \
    --data-urlencode "key=${GOOGLE_PSI_API_KEY}") || HTTP_CODE=000
  if [ "$HTTP_CODE" = "200" ] && [ -s "$TMP_JSON" ]; then
    break
  fi
  if [ "$i" -lt "$ATTEMPTS" ]; then
    echo "PSI attempt $i/$ATTEMPTS failed (HTTP $HTTP_CODE), retry in $((i * 5))s..." >&2
    sleep $((i * 5))
  fi
done

if [ "$HTTP_CODE" != "200" ] || [ ! -s "$TMP_JSON" ]; then
  echo "ERROR: PSI API вернул HTTP $HTTP_CODE после $ATTEMPTS попыток" >&2
  head -c 500 "$TMP_JSON" >&2 || true
  exit 3
fi

python3 -c '
import sys, json
d = json.load(sys.stdin)
lr = d.get("lighthouseResult", {})
cats = lr.get("categories", {})
audits = lr.get("audits", {})

def pct(cat): return round((cats.get(cat, {}).get("score") or 0) * 100)
def metric(key): return audits.get(key, {}).get("displayValue", "—")

# Полевые данные CrUX (реальные CWV) — могут отсутствовать при малом трафике
le = d.get("loadingExperience", {}) or {}
le_metrics = le.get("metrics", {}) or {}

def field(key, divisor=1):
    m = le_metrics.get(key)
    if not m:
        return None
    p = m.get("percentile")
    return {
        "percentile": (p / divisor if p is not None and divisor != 1 else p),
        "category": m.get("category"),
    }

cwv_field = None
if le_metrics:
    cwv_field = {
        "overall_category": le.get("overall_category"),
        "LCP_ms": field("LARGEST_CONTENTFUL_PAINT_MS"),
        "INP_ms": field("INTERACTION_TO_NEXT_PAINT"),
        "CLS": field("CUMULATIVE_LAYOUT_SHIFT_SCORE", divisor=100),
    }

opportunities = sorted(
    (
        {"id": k, "title": v.get("title"), "saving": v.get("displayValue", "—"),
         "savings_ms": v.get("details", {}).get("overallSavingsMs", 0)}
        for k, v in audits.items()
        if v.get("details", {}).get("overallSavingsMs", 0) > 100
    ),
    key=lambda o: -o["savings_ms"],
)

out = {
  "url": d.get("id"),
  "strategy": "'"$STRATEGY"'",
  "scores": {
    "performance": pct("performance"),
    "seo": pct("seo"),
    "accessibility": pct("accessibility"),
    "best_practices": pct("best-practices"),
  },
  "core_web_vitals_field": cwv_field,
  "lab_metrics": {
    "LCP": metric("largest-contentful-paint"),
    "INP": metric("interaction-to-next-paint"),
    "CLS": metric("cumulative-layout-shift"),
    "TBT": metric("total-blocking-time"),
    "FCP": metric("first-contentful-paint"),
    "TTFB": metric("server-response-time"),
  },
  "top_opportunities": opportunities[:5],
}
print(json.dumps(out, ensure_ascii=False, indent=2))
' < "$TMP_JSON"
