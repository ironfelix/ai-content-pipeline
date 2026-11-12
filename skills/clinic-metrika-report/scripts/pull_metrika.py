#!/usr/bin/env python3
"""Снимает стандартный набор срезов из Яндекс Метрики для отчёта по клинике.

Метрика доступна только с сервер (там токен и утилита <agent_home>/bin/metrika.py),
поэтому скрипт запускает удалённую программу по ssh и печатает компактный дайджест.

Примеры:
    python3 pull_metrika.py 47752981 --days 30
    python3 pull_metrika.py 47752981 --days 30 --goals 223197928:телефон 251697454:мессенджер 39123667:спасибо
    python3 pull_metrika.py 47752981 --exclude-city 193 --goals ...
    python3 pull_metrika.py --list            # список счётчиков
    python3 pull_metrika.py 47752981 --goals-only   # список целей счётчика

Сначала всегда: --goals-only, чтобы взять ID целей. Без --goals скрипт даёт только трафик.
"""
import argparse, json, subprocess, sys

SSH = ["ssh", "-i", "~/.ssh/<ssh_key>", "root@<host>"]
MET = "<agent_home>/bin/metrika.py"


def ssh_run(remote_cmd, timeout=180):
    cmd = [c.replace("~", "/Users/" + __import__("os").environ.get("USER", "")) if c.startswith("~") else c for c in SSH]
    r = subprocess.run(cmd + [remote_cmd], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        sys.exit("ssh не отработал: " + r.stderr[:300])
    return r.stdout


REMOTE = r'''
import json, subprocess, time, sys
CID = "%(cid)s"; DAYS = "%(days)s"; FILT = %(filt)r; AI_DAYS = "%(ai_days)s"
# визиты с сайта нейросети: домены реферера ChatGPT, Алисы, Perplexity, Gemini и др. (сверено 24.09.2026)
AI = "ym:s:refererDomain=.('chatgpt.com','chat.openai.com','perplexity.ai','www.perplexity.ai','gemini.google.com','alice.yandex.ru','claude.ai','chat.qwen.ai','chat.deepseek.com','copilot.microsoft.com','giga.chat','grok.com')"
def q(metrics, dims=None, limit="100", filters=FILT, days=None):
    cmd = ["python3", "%(met)s", "raw", CID, "--metrics", metrics, "--days", days or DAYS, "--limit", limit]
    if dims: cmd += ["--dims", dims]
    if filters: cmd += ["--filters", filters]
    for attempt in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            if attempt == 2:
                return {"error": (r.stdout or r.stderr)[:200]}
            time.sleep(3)
def show(title, metrics, dims=None, limit="100", extra=None, days=None):
    filters = " AND ".join(f for f in (FILT, extra) if f) or None
    d = q(metrics, dims, limit, filters, days)
    print("==", title)
    if "error" in d:
        print("ОШИБКА:", d["error"]); print("---"); return
    print("ИТОГО\t" + "\t".join(str(round(x, 2)) for x in d["totals"]))
    for row in d["rows"]:
        print("\t".join([str(x) for x in row["dims"]] + [str(round(m, 2)) for m in row["metrics"]]))
    print("---")
G = %(goals)r
gm = ",".join("ym:s:goal%%dvisits" %% g for g, _ in G)
gn = ", ".join(n for _, n in G)
base = "ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:avgVisitDurationSeconds,ym:s:pageDepth"
print("ЦЕЛИ В ПОРЯДКЕ КОЛОНОК:", gn or "нет")
show("итог", base)
if gm:
    show("цели всего", "ym:s:visits," + gm)
    show("по часам", "ym:s:visits," + gm, "ym:s:hour", "30")
    show("по дням", "ym:s:visits," + gm, "ym:s:date", "40")
    show("источники", "ym:s:visits," + gm, "ym:s:lastsignTrafficSource", "8")
    show("нейросети за " + AI_DAYS + " дн.", "ym:s:visits," + gm, "ym:s:refererDomain", "15", extra=AI, days=AI_DAYS)
    show("устройства", "ym:s:visits," + gm, "ym:s:deviceCategory", "4")
    show("города", "ym:s:visits," + gm, "ym:s:regionCity", "10")
    show("страницы входа", "ym:s:visits," + gm, "ym:s:startURL", "12")
    show("разделы входа", "ym:s:visits," + gm, "ym:s:startURLPathLevel2", "12")
    show("часы и устройства", "ym:s:visits," + gm, "ym:s:hour,ym:s:deviceCategory", "100")
else:
    show("по часам", base, "ym:s:hour", "30")
    show("по дням", base, "ym:s:date", "40")
    show("источники", base, "ym:s:lastsignTrafficSource", "8")
    show("нейросети за " + AI_DAYS + " дн.", "ym:s:visits", "ym:s:refererDomain", "15", extra=AI, days=AI_DAYS)
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("counter", nargs="?", help="ID счётчика или алиас (3dgastro, crocodent, atmosfera)")
    ap.add_argument("--days", default="30")
    ap.add_argument("--ai-days", default="365", help="окно для среза «нейросети»: визитов мало, за 30 дней там единицы")
    ap.add_argument("--goals", nargs="*", default=[], help="ID:имя через пробел, напр. 223197928:телефон")
    ap.add_argument("--exclude-city", help="ID города-аномалии, напр. 193 (Воронеж)")
    ap.add_argument("--list", action="store_true", help="список счётчиков")
    ap.add_argument("--goals-only", action="store_true", help="только список целей счётчика")
    a = ap.parse_args()

    if a.list:
        print(ssh_run("python3 %s counters" % MET)); return
    if not a.counter:
        ap.error("нужен ID счётчика или --list")
    if a.goals_only:
        print(ssh_run("python3 %s goals %s" % (MET, a.counter))); return

    goals = []
    for g in a.goals:
        gid, _, name = g.partition(":")
        goals.append((int(gid), name or gid))
    filt = "ym:s:regionCity!='%s'" % a.exclude_city if a.exclude_city else None
    prog = REMOTE % {"cid": a.counter, "days": a.days, "met": MET, "goals": goals, "filt": filt, "ai_days": a.ai_days}
    remote = "python3 - <<'PYEOF'\n" + prog + "\nPYEOF"
    print(ssh_run(remote, timeout=600))


if __name__ == "__main__":
    main()
