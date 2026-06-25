#!/usr/bin/env bash
# PageSpeed Insights API — Core Web Vitals для URL
# Usage: ./pagespeed.sh <url> [mobile|desktop]
# Требует GOOGLE_PSI_API_KEY в окружении или в ai-seo/.env

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

curl -sS "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${URL}&strategy=${STRATEGY}&category=performance&category=seo&category=accessibility&category=best-practices&key=${GOOGLE_PSI_API_KEY}" \
  | python3 -c '
import sys, json
d = json.load(sys.stdin)
lr = d.get("lighthouseResult", {})
cats = lr.get("categories", {})
audits = lr.get("audits", {})

def pct(cat): return round((cats.get(cat, {}).get("score") or 0) * 100)
def metric(key): return audits.get(key, {}).get("displayValue", "—")

out = {
  "url": d.get("id"),
  "strategy": "'"$STRATEGY"'",
  "scores": {
    "performance": pct("performance"),
    "seo": pct("seo"),
    "accessibility": pct("accessibility"),
    "best_practices": pct("best-practices"),
  },
  "core_web_vitals": {
    "LCP": metric("largest-contentful-paint"),
    "INP": metric("interaction-to-next-paint"),
    "CLS": metric("cumulative-layout-shift"),
    "TBT": metric("total-blocking-time"),
    "FCP": metric("first-contentful-paint"),
    "TTFB": metric("server-response-time"),
  },
  "top_opportunities": [
    {"id": k, "title": v.get("title"), "saving": v.get("displayValue", "—")}
    for k, v in audits.items()
    if v.get("details", {}).get("overallSavingsMs", 0) > 100
  ][:5]
}
print(json.dumps(out, ensure_ascii=False, indent=2))
'
