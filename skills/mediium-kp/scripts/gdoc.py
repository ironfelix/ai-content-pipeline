#!/usr/bin/env python3
"""Google Doc для КП МедИИума: создать из HTML и точечно править готовый документ.

  gdoc.py create kp.html "КП МедИИум для <клиники>"   # новый Doc, доступ по ссылке на редактирование
  gdoc.py dump   <docId>                              # абзацы и таблицы с индексами + комментарии
  gdoc.py edit   <docId> edits.json                   # правки, см. формат ниже

edits.json — список операций, применяются к свежей версии документа:
  {"op": "replace",   "find": "точный текст", "to": "новый текст"}
  {"op": "del_para",  "prefix": "начало абзаца"}          # абзац целиком, включая ячейки таблиц
  {"op": "set_para",  "prefix": "начало абзаца", "to": "новый текст"}   # снимает жёлтую подсветку
  {"op": "del_row",   "table": "заголовок 1-й ячейки таблицы", "first_cell": "текст 1-й ячейки строки"}

Токен берётся у MCP-сервера google-docs: ~/.claude/mcp-servers/google-docs/token.json.
Никогда не перезаливать весь документ после того, как его правил человек: только edit.
"""
import json
import sys
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

TOKEN_DIR = Path.home() / ".claude" / "mcp-servers" / "google-docs"


def access_token() -> str:
    t = json.loads((TOKEN_DIR / "token.json").read_text())
    ci = json.loads((TOKEN_DIR / "credentials.json").read_text())["installed"]
    data = urllib.parse.urlencode({
        "client_id": t.get("client_id") or ci["client_id"],
        "client_secret": t.get("client_secret") or ci["client_secret"],
        "refresh_token": t["refresh_token"], "grant_type": "refresh_token"}).encode()
    try:
        return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data))["access_token"]
    except urllib.error.HTTPError as e:
        sys.exit("Токен Google не обновился (invalid_grant?): нужна повторная авторизация. " + e.read().decode()[:200])


AT = None


def call(url, body=None, method=None, ctype="application/json"):
    global AT
    AT = AT or access_token()
    headers = {"Authorization": "Bearer " + AT}
    if body is not None:
        headers["Content-Type"] = ctype
        if not isinstance(body, bytes):
            body = json.dumps(body).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    return json.load(urllib.request.urlopen(req))


def text(p):
    return "".join(e.get("textRun", {}).get("content", "") for e in p["elements"])


def create(html_path, title):
    html = Path(html_path).read_bytes()
    b = "====" + uuid.uuid4().hex
    meta = json.dumps({"name": title, "mimeType": "application/vnd.google-apps.document"}).encode()
    body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n").encode() + meta + \
           (f"\r\n--{b}\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n").encode() + html + f"\r\n--{b}--".encode()
    r = call("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,webViewLink",
             body, ctype="multipart/related; boundary=" + b)
    call(f"https://www.googleapis.com/drive/v3/files/{r['id']}/permissions", {"role": "writer", "type": "anyone"})
    print(r["id"])
    print(f"https://docs.google.com/document/d/{r['id']}/edit")


def doc(doc_id):
    return call(f"https://docs.googleapis.com/v1/documents/{doc_id}")


def paragraphs(d):
    out = []

    def walk(content):
        for el in content:
            if "paragraph" in el:
                out.append(el)
            if "table" in el:
                for r in el["table"]["tableRows"]:
                    for c in r["tableCells"]:
                        walk(c["content"])
    walk(d["body"]["content"])
    return out


def dump(doc_id):
    d = doc(doc_id)
    for el in d["body"]["content"]:
        if "paragraph" in el:
            s = text(el["paragraph"]).rstrip("\n")
            if s:
                style = el["paragraph"]["paragraphStyle"].get("namedStyleType", "")
                print(f'{el["startIndex"]}-{el["endIndex"]} [{style}] {s}')
        elif "table" in el:
            print(f'{el["startIndex"]} TABLE')
            for r in el["table"]["tableRows"]:
                cells = [" / ".join(text(p["paragraph"]).strip() for p in c["content"] if "paragraph" in p)
                         for c in r["tableCells"]]
                print("   " + " | ".join(cells))
    c = call(f"https://www.googleapis.com/drive/v3/files/{doc_id}/comments"
             "?fields=comments(content,quotedFileContent,author/displayName,resolved)")
    print("КОММЕНТАРИИ:", json.dumps(c.get("comments", []), ensure_ascii=False))


def edit(doc_id, edits_path):
    edits = json.loads(Path(edits_path).read_text())
    d = doc(doc_id)
    paras = paragraphs(d)
    indexed, replaces = [], []

    def one(prefix):
        m = [p for p in paras if text(p["paragraph"]).startswith(prefix)]
        if len(m) != 1:
            sys.exit(f"абзац «{prefix[:50]}» найден {len(m)} раз")
        return m[0]

    for e in edits:
        op = e["op"]
        if op == "replace":
            replaces.append({"replaceAllText": {"containsText": {"text": e["find"], "matchCase": True},
                                                "replaceText": e["to"]}})
        elif op == "del_para":
            p = one(e["prefix"])
            indexed.append((p["startIndex"], [{"deleteContentRange": {"range": {
                "startIndex": p["startIndex"], "endIndex": p["endIndex"]}}}]))
        elif op == "set_para":
            p = one(e["prefix"])
            s, end = p["startIndex"], p["endIndex"] - 1
            reqs = []
            if end > s:
                reqs.append({"deleteContentRange": {"range": {"startIndex": s, "endIndex": end}}})
            reqs += [{"insertText": {"location": {"index": s}, "text": e["to"]}},
                     {"updateTextStyle": {"range": {"startIndex": s, "endIndex": s + len(e["to"])},
                                          "textStyle": {"backgroundColor": {}}, "fields": "backgroundColor"}}]
            indexed.append((s, reqs))
        elif op == "del_row":
            for el in d["body"]["content"]:
                if "table" not in el:
                    continue
                rows = el["table"]["tableRows"]
                cell = lambda r, i=0: "".join(text(p["paragraph"]) for p in r["tableCells"][i]["content"]
                                              if "paragraph" in p).strip()
                if cell(rows[0]) != e["table"]:
                    continue
                for ri, r in enumerate(rows):
                    if cell(r) == e["first_cell"]:
                        indexed.append((r["startIndex"], [{"deleteTableRow": {"tableCellLocation": {
                            "tableStartLocation": {"index": el["startIndex"]}, "rowIndex": ri, "columnIndex": 0}}}]))
        else:
            sys.exit("неизвестная операция " + op)

    reqs = [r for _, rs in sorted(indexed, key=lambda x: -x[0]) for r in rs] + replaces
    if reqs:
        res = call(f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate", {"requests": reqs})
        missed = [e["find"][:50] for e, r in zip([x for x in edits if x["op"] == "replace"],
                                                 res["replies"][-len(replaces):] if replaces else [])
                  if not r.get("replaceAllText", {}).get("occurrencesChanged")]
        print("готово", f"({len(reqs)} запросов)")
        if missed:
            print("НЕ НАЙДЕНО для replace:", missed)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "create" and len(sys.argv) == 4:
        create(sys.argv[2], sys.argv[3])
    elif cmd == "dump" and len(sys.argv) == 3:
        dump(sys.argv[2])
    elif cmd == "edit" and len(sys.argv) == 4:
        edit(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
