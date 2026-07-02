# Pencil Templates — инфографика через MCP

Читать этот файл перед генерацией в Pencil-режиме.

---

## Маппинг дизайн-токенов клиента

Извлечи из `data/design-tokens.md` клиента:

| Что нужно | Где искать в файле | Использовать в Pencil как |
|-----------|-------------------|--------------------------|
| Акцент (primary) | `primary`, `accent`, `brand` | цвет заголовков колонок, бейджей, чисел |
| Тёмный (dark) | `dark`, `secondary` | хедер, metric-бары, тёмные блоки |
| Фон страницы | `bg`, `background` | `fill` корневого фрейма |
| Фон карточки | `bg-secondary`, `card`, `white` | `fill` карточек |
| Основной текст | `text`, `color-text` | `fill` заголовков и тела |
| Приглушённый | `muted`, `text-muted`, `text-light` | `fill` подписей и лейблов |
| Граница | `border` | `stroke.fill` карточек |
| Шрифт | `font-family`, `--font` | `fontFamily` (если Google/system) |

**Шрифты:** если в токенах указан платный (TT Smalls, Graphik, Styrene, GT Walsheim) → использовать `Inter`. Если `Manrope`, `Inter`, `Roboto`, `Montserrat`, `Open Sans` → использовать как есть.

---

## Общие правила Pencil

1. **Placeholder:** ставить `placeholder: true` на все незавершённые фреймы. Снимать когда готово.
2. **Биндинги:** живут только внутри одного `batch_design`. В следующем батче — использовать реальные ID из предыдущего ответа.
3. **fill_container на тексте:** работает только если родительский фрейм имеет явную ширину. Если родитель `fit_content` — текст с `fill_container` рендерится вертикально. Фикс: добавить `width: "fill_container"` на строку-родитель тоже.
4. **textGrowth:** для wrapping текста обязательно `textGrowth: "fixed-width"` + `width: "fill_container"`.
5. **Скриншот:** делать `get_screenshot` после каждого крупного батча (не реже чем через 3 батча).
6. **Макс. 25 операций** на один `batch_design`.

---

## Шаблон: FUNNEL — воронка

**Когда:** воронка продаж, этапы конверсии, лид → сделка, до/после.

**Размер канваса:** 1200 × 680px

**Структура:**
```
root (1200×680, vertical, fill=color_bg)
  header (fill_container, vertical, padding [32,48,24,48])
    title (text, 22px, 700, fill=color_text, uppercase)
    subtitle (text, 13px, fill=color_muted)
  funnel (fill_container, vertical, gap 0, alignItems center, padding [0,80,32,80])
    stage_1 (fill_container × 72px, fill=color_dark opacity 0.15, radius 4)
      label (text, 15px, 700, fill=color_text)
      desc (text, 12px, fill=color_muted)
    arrow (vertical, gap 0, alignItems center) → line (2×20, fill=color_accent) + triangle
    stage_2 (90% width × 72px, fill=color_dark opacity 0.22)
    arrow
    stage_KEY (70% width × 72px, fill=color_accent opacity 0.15, border 2px color_accent) ← ключевой
      label (fill=color_accent, 700)
      pct (fill=color_accent, 14px, 700)
    arrow
    stage_4 (50% width × 72px, fill=color_dark opacity 0.30)
```

**Операции (пример):**
```javascript
root=I(document,{type:"frame",width:1200,height:680,fill:COLOR_BG,layout:"vertical",gap:0,placeholder:true})
hdr=I(root,{type:"frame",width:"fill_container",layout:"vertical",padding:[32,48,20,48],gap:6,alignItems:"center"})
I(hdr,{type:"text",content:"ВОРОНКА ПРОДАЖ",fontFamily:FONT_HEADING,fontSize:22,fontWeight:"700",fill:COLOR_TEXT,letterSpacing:2})
I(hdr,{type:"text",content:"подзаголовок",fontFamily:FONT_BODY,fontSize:13,fill:COLOR_MUTED})
funnel=I(root,{type:"frame",width:"fill_container",height:"fill_container",layout:"vertical",gap:0,alignItems:"center",padding:[0,80,32,80]})
// этапы через I(funnel, ...) с убывающей шириной
```

**Правила заполнения:**
- 3–5 этапов, убывающая ширина: 100% → 85% → 70% → 55%
- Ключевой этап (КЭВ, встреча, демо): акцентный цвет клиента
- Стрелка между этапами: прямоугольник 2×20px + треугольник (rectangle 10×8px)
- Боковые бейджи (если есть цифры «без X» / «с X»): абсолютное позиционирование через `layoutPosition: "absolute"`

---

## Шаблон: STEPS — шаги в кружках ⚠️ LEGACY

> **Устарел.** Кружки step-circle больше не используются. Актуальный стиль для шагов и алгоритмов — карточки cards-num / cards-badge (см. `design-style.md`): те же данные, но каждая ступень — карточка с номером или бейджем. Шаблон оставлен для справки по старым статьям.

**Когда (исторически):** алгоритм, 5 шагов, пошаговый процесс, «как сделать».

**Размер канваса:** 1200 × 620px

**Структура:**
```
root (1200×620, vertical)
  header (текст заголовка и подзаголовка)
  grid (fill_container, horizontal, gap 24, padding [0,48,32,48], alignItems start)
    step_1..N (vertical, alignItems center, gap 10, width fill_container)
      circle (width 130, height 130, ellipse или frame с radius 65)
        num (text, 24px, 800, fill=color_accent)
        title (text, 13px, 700, fill=color_text, textGrowth fixed-width, width 110, textAlign center)
      desc (text, 12px, fill=color_muted, textGrowth fixed-width, width fill_container, textAlign center)
```

**Правила:**
- 3 шага: одна строка (3 колонки)
- 4 шага: 4 колонки или 2+2 через вложенные горизонтальные фреймы
- 5–6 шагов: 3+2 или 3+3 (два горизонтальных ряда)
- Ключевой шаг: `fill = color_accent + opacity 0.12`, `stroke = color_accent`
- Номер ключевого шага: `fill = color_accent`
- Стрелки между шагами в одном ряду: icon_font «arrow-right» или rectangle 20×2px с color_accent

---

## Шаблон: STATS — ключевые цифры

**Когда:** 3–5 бенчмарков, конверсий, показателей.

**Размер канваса:** 1200 × 480px

**Структура:**
```
root (1200×480, vertical)
  header
  cards_row (fill_container, horizontal, gap 16, padding [0,40,32,40])
    card_1..N (fill_container, vertical, padding [24,20,24,20], gap 8, alignItems center,
               fill=color_bg_secondary, radius 10, stroke color_border)
      value (text, 38px, 800, fill=color_accent)
      label (text, 14px, 600, fill=color_text, textAlign center, textGrowth fixed-width, width fill_container)
      sub (text, 12px, fill=color_muted, textAlign center, textGrowth fixed-width, width fill_container)
```

**Правила:**
- 3 карточки: три равных колонки
- 4 карточки: четыре колонки
- Центральная / главная карточка: `fill = color_accent + opacity 0.1`, `stroke = color_accent`
- `value` формат: «40–70%», «×10», «3 мес.», «200+» — не просто число

---

## Шаблон: CANVAS — стратегический канвас

**Когда:** 360 маркетинг, роадмап, сравнение аудиторий, план на квартал.

**Размер канваса:** 1440 × fit_content (обычно 600–700px)

**Структура:**
```
root (1440, vertical, fill=color_bg_secondary)
  header (64px, fill=color_dark, horizontal, padding [0,28,0,28], space_between)
    left: dots (3 ellipse × 7px, акцентные цвета) + title (700, 17px, white) + badge (accent)
    right: subtitle (12px, color_muted_light)
  body (fill_container, vertical, gap 12, padding [12,16,12,16])
    colRow (fill_container, horizontal, gap 12)
      col_1..N (fill_container, vertical, gap 8)
        col_header (fill_container, fill=accent_N, radius 6, vertical, padding [12,14])
          num_label (9px, 700, darker accent, letterSpacing 1.5)
          title (22px, 700, white)
          subtitle (11px, white, opacity 0.85, textGrowth fixed-width)
        card_ЗАДАЧА (white, radius 6, stroke border, vertical, padding [10,12], gap 6)
        card_КАНАЛЫ (white, radius 6, stroke border, vertical, padding [10,12], gap 7)
        card_ПОБЕДЫ (light accent bg, radius 6, vertical, padding [10,12], gap 8)
        metric_bar (fill=color_dark, radius 6, horizontal, padding [8,12])
    bottom_strip (fill_container, horizontal, gap 1, fill=color_dark, radius 8)
      block_1..4 (fill_container, vertical, padding [12,14], gap 5)
        tag + title + description
```

**Акцентные цвета колонок:** использовать color_accent клиента для P1, color_dark для P2, color_success (или другой контрастный) для P3. Если в токенах нет success → использовать `#34A853`.

**ПОБЕДЫ строки (критично):** каждая строка с номером-бейджем должна иметь `width: "fill_container"`, иначе текст рендерится вертикально.

---

## Экспорт и загрузка

```python
# После сборки канваса:
# 1. Экспорт через MCP
mcp__pencil__export_nodes(
    filePath="pencil-new.pen",
    nodeIds=[root_node_id],
    outputDir=os.path.join(os.getcwd(), "reports"),
    format="png",
    scale=2
)
# 2. Переименовать в читаемое имя
import shutil
shutil.copy(
    f"{reports_dir}/{root_node_id}.png",
    f"/tmp/infographic_{N}.png"
)
# 3. Дальше → Шаг 6 основного SKILL.md (upload to WP)
```
