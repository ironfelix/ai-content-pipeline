#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Поиск калек в тексте статьи. Два выхода:
  1) findings: срабатывания библиотеки references/patterns.md (regex) с пояснением;
  2) sentences_shuffled.txt: ВСЕ предложения, заголовки, пункты списков и ячейки таблиц, перемешанные, без соседнего текста.
     Их читает слепой судья (агент): вне контекста беглость не маскирует кальку.

  kalki_scan.py <draft.md|page.html> <out_dir> [--baseline live.html]
"""
import io, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAT = os.path.join(HERE, '..', 'references', 'patterns.md')

def load_patterns():
    txt = io.open(PAT, encoding='utf-8').read()
    m = re.search(r'```patterns\n(.*?)```', txt, re.S)
    out = []
    for ln in (m.group(1).split('\n') if m else []):
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        parts = [p.strip() for p in ln.split('|')]
        # regex может содержать «|»: склеиваем всё, пока не найдём разделитель-пояснение с «calque|…»
        # формат строки: <regex>|<почему>|<как надо>|<дата>; regex экранирует «|» как \|, поэтому делим по неэкранированным
        parts = re.split(r'(?<!\\)\|', ln)
        parts = [p.strip() for p in parts]
        if len(parts) < 3:
            continue
        rx, why, fix = parts[0], parts[1], parts[2]
        try:
            out.append((re.compile(rx), why, fix))
        except re.error:
            continue
    return out

def units(md):
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    md = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', md)
    md = re.sub(r'\[ПРИЗЫВ:[^\]]*\]', '', md)
    res = []
    for blk in re.split(r'\n\s*\n', md):
        b = blk.strip()
        if not b:
            continue
        if re.match(r'^\|[-| :]+\|$', b.split('\n')[0]):
            continue
        for ln in b.split('\n'):
            ln = ln.strip()
            if not ln or re.fullmatch(r'\|[-| :]+\|', ln):
                continue
            if ln.startswith('|'):
                for c in ln.strip('|').split('|'):
                    c = re.sub(r'\*+', '', c).strip()
                    if len(c) > 3:
                        res.append(c)
                continue
            ln = re.sub(r'^(#{1,3}|\d+\.|-|\*|>)\s+', '', ln)
            ln = re.sub(r'\*+', '', ln).strip()
            if len(ln) < 4:
                continue
            for s in re.split(r'(?<=[.!?»])\s+(?=[А-ЯA-Z«])', ln):
                s = s.strip()
                if len(s) > 3:
                    res.append(s)
    return res

def html_to_md(h):
    """HTML страницы → блоки текста: каждый блочный тег отдельным абзацем, разметка снята.
    Нужен дожиму на сервере: там правят готовую страницу (edited.html), а не draft.md."""
    import html as _html
    h = re.sub(r'<(script|style)\b.*?</\1>', ' ', h, flags=re.S | re.I)
    h = re.sub(r'<!--.*?-->', ' ', h, flags=re.S)
    # Карточки тултипов (span.explain-card) — отдельный текст: внутри предложения они
    # склеиваются с ним в «конверсииКонверсияДоля…». Вынимаем их и судим отдельно.
    card_rx = r'<span[^>]*class="[^"]*explain-card[^"]*"[^>]*>(.*?)</span>'
    cards = [re.sub(r'</strong>', '. ', c) for c in re.findall(card_rx, h, flags=re.S | re.I)]
    h = re.sub(card_rx, '', h, flags=re.S | re.I) + ''.join('<p>%s</p>' % c for c in cards)
    h = re.sub(r'</?(p|h[1-6]|li|td|th|tr|div|section|details|summary|blockquote|figcaption|br)\b[^>]*>',
               '\n\n', h, flags=re.I)
    h = re.sub(r'<[^>]+>', '', h)
    h = _html.unescape(h).replace('\xa0', ' ')
    return '\n\n'.join(re.sub(r'[ \t]+', ' ', b).strip() for b in re.split(r'\n\s*\n', h) if b.strip())


def read_units(path):
    text = io.open(path, encoding='utf-8').read()
    if path.lower().endswith(('.html', '.htm')):
        text = html_to_md(text)
    return units(text)


def main():
    args = sys.argv[1:]
    baseline = None
    if '--baseline' in args:
        i = args.index('--baseline')
        baseline = args[i + 1]
        del args[i:i + 2]
    src, out = args[0], args[1]
    os.makedirs(out, exist_ok=True)
    us = read_units(src)
    if baseline:
        # Дожим: судим только фразы, которых не было на живой странице, старый текст не трогаем.
        old = set(read_units(baseline))
        total = len(us)
        us = [u for u in us if u not in old]
        print(f'новых фраз против {os.path.basename(baseline)}: {len(us)} из {total}')
    pats = load_patterns()
    finds = []
    for i, u in enumerate(us):
        for rx, why, fix in pats:
            m = rx.search(u)
            if m:
                finds.append({'id': i, 'match': m.group(0), 'sentence': u, 'why': why, 'fix': fix})
    json.dump(finds, io.open(os.path.join(out, 'findings.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    CANARY = ['Какая часть звонков не доходит до отчёта, у каждой клиники своя.', 'Эти данные принадлежат подрядчику клиники.', 'Клинике, которая открывает чат, стоит ждать обращений вечером.']
    base = len(us)
    us = us + CANARY
    canary_ids = set(range(base, len(us)))
    idx = list(range(len(us)))
    random.Random(42).shuffle(idx)
    with io.open(os.path.join(out, 'sentences_shuffled.txt'), 'w', encoding='utf-8') as f:
        for n, i in enumerate(idx, 1):
            f.write(f'{n:03d}\t{us[i]}\n')
    json.dump({f'{n:03d}': (('CANARY: ' if i in canary_ids else '') + us[i]) for n, i in enumerate(idx, 1)}, io.open(os.path.join(out, 'key.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'единиц текста: {base} (+3 контрольные фразы-кальки); срабатываний библиотеки: {len(finds)}')
    for f_ in finds:
        print(f"  [{f_['id']}] «{f_['match']}» ← {f_['why']} | {f_['fix']}\n      {f_['sentence'][:160]}")

if __name__ == '__main__':
    main()
