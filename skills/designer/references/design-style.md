# Design Style — Инфографика Фактор Продаж

## Дизайн-токены

```
Фон контейнера:   #ECEADF  (тёплый бежевый)
Граница:          2px dashed rgba(204,149,91,0.55)
Радиус:           18px
Золото (акцент):  #CC955B
Золото светлое:   #E3A96C
Тёмный текст:     #252525
Приглушённый:     #888888
Хороший бейдж:    bg #E8F5E9, text #1B5E20
Плохой бейдж:     bg #FDECEA, text #B71C1C
Нейтральный блок: #D8D4C6
Подсветка блока:  rgba(204,149,91,0.12), border 2px solid #CC955B
Шрифт:            Raleway (Google Fonts, wght 400;600;700;800)
```

## Общий CSS-каркас (одинаков для всех типов)

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Raleway','Helvetica Neue',Arial,sans-serif; background: transparent; }

.infographic {
  width: 1100px;
  background: #ECEADF;
  border: 2px dashed rgba(204,149,91,0.55);
  border-radius: 18px;
  padding: 48px 72px 56px;
  position: relative;
  overflow: hidden;
}
/* Декоративные круги */
.deco { position:absolute; border-radius:50%; border:2px solid rgba(204,149,91,0.10); pointer-events:none; }

.header { text-align: center; margin-bottom: 44px; }
.header h2 {
  font-size: 27px; font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 3px;
  color: #252525; line-height: 1.25;
}
.header p { font-size: 13px; color: #888; font-weight: 400; margin-top: 9px; }
```

---

## Шаблон 1: FUNNEL — воронка с этапами

Использовать когда: воронка продаж, этапы с конверсией, «до/после», лид → сделка.

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Raleway','Helvetica Neue',Arial,sans-serif; background:transparent; }
.infographic {
  width:1100px; background:#ECEADF;
  border:2px dashed rgba(204,149,91,0.55);
  border-radius:18px; padding:48px 72px 56px;
  position:relative; overflow:hidden;
}
.deco { position:absolute; border-radius:50%; border:2px solid rgba(204,149,91,0.10); pointer-events:none; }
.header { text-align:center; margin-bottom:44px; }
.header h2 { font-size:27px; font-weight:800; text-transform:uppercase; letter-spacing:3px; color:#252525; }
.header p { font-size:13px; color:#888; margin-top:9px; }

.funnel { display:flex; flex-direction:column; align-items:center; gap:0; }

/* Каждая строка: обёртка для позиционирования бейджей */
.f-row { position:relative; display:flex; justify-content:center; width:100%; }

/* Блок этапа: вложение bg-слой + text-слой */
.f-stage { position:relative; height:78px; }
.f-bg {
  position:absolute; inset:0;
  clip-path:polygon(3% 0%,97% 0%,95% 100%,5% 100%);
  /* для каждого этапа менять clip-path — см. ниже */
}
.f-content {
  position:relative; height:100%;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  gap:3px;
}
.f-title { font-size:17px; font-weight:700; color:#252525; letter-spacing:0.3px; }
.f-desc  { font-size:12px; color:#888; }
.f-pct   { font-size:14px; font-weight:700; color:#CC955B; }

/* Стрелка между этапами */
.f-arrow {
  display:flex; flex-direction:column; align-items:center;
  padding:5px 0;
}
.f-arrow-line { width:0; border-left:2px dashed rgba(204,149,91,0.7); height:22px; }
.f-arrow-head {
  width:0; height:0;
  border-left:7px solid transparent;
  border-right:7px solid transparent;
  border-top:9px solid #CC955B;
}

/* Боковые бейджи */
.badge {
  position:absolute; top:50%; transform:translateY(-50%);
  padding:5px 13px; border-radius:50px;
  font-size:12px; font-weight:700; white-space:nowrap;
}
.badge-r { right:0; }
.badge-l { left:0; }
.badge-good { background:#E8F5E9; color:#1B5E20; }
.badge-bad  { background:#FDECEA; color:#B71C1C; }
.badge-neutral { background:#F5F3EC; border:1.5px dashed rgba(204,149,91,0.5); color:#252525; }
</style>
</head>
<body>
<div class="infographic">
  <div class="deco" style="width:220px;height:220px;top:-90px;left:-90px;"></div>
  <div class="deco" style="width:110px;height:110px;bottom:-45px;right:50px;"></div>

  <div class="header">
    <h2>{{TITLE}}</h2>
    <p>{{SUBTITLE}}</p>
  </div>

  <div class="funnel" style="padding:0 80px;">

    <!-- ЭТАП 1 (самый широкий: 82%) -->
    <div class="f-row">
      <div class="f-stage" style="width:82%;">
        <div class="f-bg" style="background:#D8D4C6;clip-path:polygon(0% 0%,100% 0%,97% 100%,3% 100%);"></div>
        <div class="f-content">
          <span class="f-title">{{STAGE_1_TITLE}}</span>
          <span class="f-desc">{{STAGE_1_DESC}}</span>
          <span class="f-pct" style="color:#999;">{{STAGE_1_PCT}}</span>
        </div>
      </div>
      <!-- бейдж слева/справа — добавить если нужно:
      <div class="badge badge-r badge-bad">Без X: 3–5%</div>
      -->
    </div>

    <div class="f-arrow"><div class="f-arrow-line"></div><div class="f-arrow-head"></div></div>

    <!-- ЭТАП 2 (70%) -->
    <div class="f-row">
      <div class="f-stage" style="width:70%;">
        <div class="f-bg" style="background:#CFCBB9;clip-path:polygon(0% 0%,100% 0%,96% 100%,4% 100%);"></div>
        <div class="f-content">
          <span class="f-title">{{STAGE_2_TITLE}}</span>
          <span class="f-desc">{{STAGE_2_DESC}}</span>
        </div>
      </div>
      <!-- <div class="badge badge-r badge-bad">{{BADGE_BAD}}</div> -->
    </div>

    <div class="f-arrow"><div class="f-arrow-line"></div><div class="f-arrow-head"></div></div>

    <!-- ЭТАП 3 — КЛЮЧЕВОЙ, золото (58%) -->
    <div class="f-row">
      <div class="f-stage" style="width:58%;">
        <div class="f-bg" style="background:rgba(204,149,91,0.15);clip-path:polygon(0% 0%,100% 0%,95% 100%,5% 100%);outline:2px solid #CC955B;border-radius:4px;"></div>
        <div class="f-content">
          <span class="f-title" style="color:#CC955B;">{{STAGE_3_TITLE}}</span>
          <span class="f-desc">{{STAGE_3_DESC}}</span>
          <span class="f-pct">{{STAGE_3_PCT}}</span>
        </div>
      </div>
      <!-- <div class="badge badge-l badge-neutral">×10</div> -->
      <!-- <div class="badge badge-r badge-good">{{BADGE_GOOD}}</div> -->
    </div>

    <div class="f-arrow"><div class="f-arrow-line"></div><div class="f-arrow-head"></div></div>

    <!-- ЭТАП 4 (самый узкий: 46%) -->
    <div class="f-row">
      <div class="f-stage" style="width:46%;">
        <div class="f-bg" style="background:#D8D4C6;clip-path:polygon(0% 0%,100% 0%,94% 100%,6% 100%);"></div>
        <div class="f-content">
          <span class="f-title">{{STAGE_4_TITLE}}</span>
          <span class="f-desc">{{STAGE_4_DESC}}</span>
        </div>
      </div>
    </div>

  </div><!-- /funnel -->
</div>
</body>
</html>
```

**Правила заполнения FUNNEL:**
- Этапов может быть 3–5, удалить/добавить строки f-row + f-arrow по необходимости
- `{{STAGE_3_TITLE}}` = ключевой этап (КЭВ, Встреча, Демо и т.д.) — выделяется золотом
- Бейджи badge-bad/badge-good — только если в статье есть цифры «без X» и «с X»
- TITLE инфографики: краткий тезис (не просто «Воронка»). Пример: «ВОРОНКА ПРОДАЖ B2B»

---

## Шаблон 2a: CARDS-NUM — карточки с большими italic номерами (3–5 элементов)

Использовать когда: перечисление признаков, условий, типов, принципов (не последовательных шагов).
Эталон: infographic-stratsessiya-1.png (5 признаков, сетка 3+2).

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Raleway','Helvetica Neue',Arial,sans-serif; background:transparent; }
.infographic {
  width:1100px; background:#ECEADF;
  border:2px dashed rgba(204,149,91,0.55);
  border-radius:18px; padding:48px 52px 52px;
  position:relative; overflow:hidden;
}
.deco { position:absolute; border-radius:50%; border:2px solid rgba(204,149,91,0.10); pointer-events:none; }
.header { text-align:center; margin-bottom:36px; }
.header h2 { font-size:26px; font-weight:800; text-transform:uppercase; letter-spacing:2.5px; color:#252525; line-height:1.25; }
.header p  { font-size:13px; color:#888; margin-top:10px; line-height:1.5; }

.cards-grid {
  display:grid;
  grid-template-columns: repeat(3, 1fr);
  gap:16px;
}
/* При 4 элементах: grid-template-columns: repeat(2,1fr) */
/* При 5 элементах: первый ряд 3 колонки, второй — 2 карточки с grid-column span */

.card {
  background:#fff;
  border:1px solid rgba(204,149,91,0.25);
  border-radius:14px;
  padding:22px 20px 20px;
  display:flex; flex-direction:column; gap:8px;
}
.card.highlight {
  background:rgba(204,149,91,0.07);
  border:2px solid #CC955B;
}

.card-num {
  font-size:38px; font-weight:800; font-style:italic;
  color:#CC955B; line-height:1;
}
.card-title { font-size:15px; font-weight:700; color:#252525; line-height:1.35; }
.card-desc  { font-size:13px; color:#666; line-height:1.6; }
</style>
</head>
<body>
<div class="infographic">
  <div class="deco" style="width:200px;height:200px;top:-80px;left:-80px;"></div>
  <div class="deco" style="width:100px;height:100px;bottom:-40px;right:40px;"></div>

  <div class="header">
    <h2>{{TITLE}}</h2>
    <p>{{SUBTITLE}}</p>
  </div>

  <!-- Сетка карточек. Для 5 элементов — добавить второй ряд с 2 карточками: -->
  <!-- <div class="card" style="grid-column: 1 / span 1; margin-left:calc(50% + 8px);"> -->
  <div class="cards-grid">

    <!-- КАРТОЧКА 1 — выделенная -->
    <div class="card highlight">
      <div class="card-num">01</div>
      <div class="card-title">{{CARD_1_TITLE}}</div>
      <div class="card-desc">{{CARD_1_DESC}}</div>
    </div>

    <div class="card">
      <div class="card-num">02</div>
      <div class="card-title">{{CARD_2_TITLE}}</div>
      <div class="card-desc">{{CARD_2_DESC}}</div>
    </div>

    <div class="card">
      <div class="card-num">03</div>
      <div class="card-title">{{CARD_3_TITLE}}</div>
      <div class="card-desc">{{CARD_3_DESC}}</div>
    </div>

    <!-- Добавить при 4–5 карточках: -->
    <!-- <div class="card">04 ...</div> -->
    <!-- <div class="card">05 ...</div> -->

  </div>
</div>
</body>
</html>
```

**Правила CARDS-NUM:**
- 3–6 карточек. При 3: одна строка (repeat(3,1fr)). При 4: 2+2 (repeat(2,1fr)). При 5: 3+2. При 6: 3+3.
- Первая карточка — всегда `highlight` (золотая рамка, золотой фон)
- `{{CARD_N_DESC}}` — 1–3 предложения, конкретика без воды
- TITLE инфографики: краткий тезис заглавными. SUBTITLE: подзаголовок строчными через `·`

---

## Шаблон 2b: CARDS-BADGE — карточки с круглым badge слева (3–4 элемента)

Использовать когда: пошаговый алгоритм, ошибки, последовательные действия.
Эталон: infographic-stratsessiya-2.png (4 ошибки, сетка 2x2).

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Raleway','Helvetica Neue',Arial,sans-serif; background:transparent; }
.infographic {
  width:1100px; background:#ECEADF;
  border:2px dashed rgba(204,149,91,0.55);
  border-radius:18px; padding:48px 52px 52px;
  position:relative; overflow:hidden;
}
.deco { position:absolute; border-radius:50%; border:2px solid rgba(204,149,91,0.10); pointer-events:none; }
.header { text-align:center; margin-bottom:36px; }
.header h2 { font-size:26px; font-weight:800; text-transform:uppercase; letter-spacing:2.5px; color:#252525; line-height:1.25; }
.header p  { font-size:13px; color:#888; margin-top:10px; line-height:1.5; }

.cards-grid {
  display:grid;
  grid-template-columns: repeat(2, 1fr);
  gap:16px;
}

.card {
  background:#fff;
  border:1px solid rgba(204,149,91,0.25);
  border-radius:14px;
  padding:20px 22px 20px;
}
.card.highlight {
  background:rgba(204,149,91,0.07);
  border:2px solid #CC955B;
}

.card-header { display:flex; align-items:center; gap:14px; margin-bottom:12px; }
.badge {
  min-width:36px; height:36px; width:36px;
  border-radius:50%;
  background:#CC955B;
  display:flex; align-items:center; justify-content:center;
  font-size:16px; font-weight:800; color:#fff;
  flex-shrink:0;
}
.card-title { font-size:15px; font-weight:700; color:#252525; line-height:1.35; }
.card-desc  { font-size:13px; color:#666; line-height:1.65; }
</style>
</head>
<body>
<div class="infographic">
  <div class="deco" style="width:200px;height:200px;top:-80px;left:-80px;"></div>
  <div class="deco" style="width:100px;height:100px;bottom:-40px;right:40px;"></div>

  <div class="header">
    <h2>{{TITLE}}</h2>
    <p>{{SUBTITLE}}</p>
  </div>

  <div class="cards-grid">

    <!-- КАРТОЧКА 1 — выделенная -->
    <div class="card highlight">
      <div class="card-header">
        <div class="badge">1</div>
        <div class="card-title">{{CARD_1_TITLE}}</div>
      </div>
      <div class="card-desc">{{CARD_1_DESC}}</div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="badge">2</div>
        <div class="card-title">{{CARD_2_TITLE}}</div>
      </div>
      <div class="card-desc">{{CARD_2_DESC}}</div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="badge">3</div>
        <div class="card-title">{{CARD_3_TITLE}}</div>
      </div>
      <div class="card-desc">{{CARD_3_DESC}}</div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="badge">4</div>
        <div class="card-title">{{CARD_4_TITLE}}</div>
      </div>
      <div class="card-desc">{{CARD_4_DESC}}</div>
    </div>

  </div>
</div>
</body>
</html>
```

**Правила CARDS-BADGE:**
- 3–4 карточки (оптимально 4 в сетке 2x2, или 3 в одну строку)
- Первая карточка — `highlight`
- Badge: всегда золотой `#CC955B`, белая цифра
- `{{CARD_N_DESC}}` — 2–4 предложения, объяснение + последствие

---

## Шаблон 3: STATS — ключевые цифры

Использовать когда: 3–5 бенчмарков, конверсий, ключевых показателей.

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Raleway','Helvetica Neue',Arial,sans-serif; background:transparent; }
.infographic {
  width:1100px; background:#ECEADF;
  border:2px dashed rgba(204,149,91,0.55);
  border-radius:18px; padding:44px 64px 52px;
  position:relative; overflow:hidden;
}
.deco { position:absolute; border-radius:50%; border:2px solid rgba(204,149,91,0.10); pointer-events:none; }
.header { text-align:center; margin-bottom:40px; }
.header h2 { font-size:27px; font-weight:800; text-transform:uppercase; letter-spacing:3px; color:#252525; }
.header p  { font-size:13px; color:#888; margin-top:9px; }

.stats-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
/* для 4 карточек: grid-template-columns:repeat(4,1fr) */

.stat-card {
  background:#F5F3EC;
  border:1.5px solid rgba(204,149,91,0.3);
  border-radius:12px;
  padding:28px 20px 24px;
  text-align:center;
  display:flex; flex-direction:column; align-items:center; gap:8px;
}
.stat-card.highlight {
  background:rgba(204,149,91,0.12);
  border:1.5px solid #CC955B;
}
.stat-value { font-size:38px; font-weight:800; color:#CC955B; line-height:1; }
.stat-label { font-size:14px; font-weight:600; color:#252525; line-height:1.35; }
.stat-sub   { font-size:12px; color:#888; line-height:1.4; }
.stat-icon  { font-size:22px; margin-bottom:2px; } /* эмодзи опционально */
</style>
</head>
<body>
<div class="infographic">
  <div class="deco" style="width:200px;height:200px;top:-80px;left:-80px;"></div>
  <div class="deco" style="width:100px;height:100px;bottom:-40px;right:50px;"></div>

  <div class="header">
    <h2>{{TITLE}}</h2>
    <p>{{SUBTITLE}}</p>
  </div>

  <div class="stats-grid">

    <div class="stat-card">
      <div class="stat-value">{{STAT_1_VALUE}}</div>
      <div class="stat-label">{{STAT_1_LABEL}}</div>
      <div class="stat-sub">{{STAT_1_SUB}}</div>
    </div>

    <!-- Центральная — ключевая, выделена -->
    <div class="stat-card highlight">
      <div class="stat-value">{{STAT_2_VALUE}}</div>
      <div class="stat-label">{{STAT_2_LABEL}}</div>
      <div class="stat-sub">{{STAT_2_SUB}}</div>
    </div>

    <div class="stat-card">
      <div class="stat-value">{{STAT_3_VALUE}}</div>
      <div class="stat-label">{{STAT_3_LABEL}}</div>
      <div class="stat-sub">{{STAT_3_SUB}}</div>
    </div>

    <!-- Добавить 4-ю и 5-ю карточки по необходимости -->

  </div>
</div>
</body>
</html>
```

**Правила заполнения STATS:**
- `{{STAT_N_VALUE}}` = число с единицей: «40–70%», «×10», «3 мес.», «200+»
- `{{STAT_N_LABEL}}` = что это за показатель (2–5 слов)
- `{{STAT_N_SUB}}` = контекст / источник / пояснение (опционально)
- Центральная карточка — самый важный показатель
- Не использовать эмодзи в label, только в stat-icon (опционально)
- При 4 карточках: `grid-template-columns: repeat(4,1fr)`

---

## Выбор типа шаблона

| Содержание раздела | Тип |
|---|---|
| Воронка, лид → сделка, этапы конверсии | `funnel` |
| Перечисление признаков, условий, принципов (без жёсткой последовательности) | `cards-num` |
| Пошаговый алгоритм, ошибки, последовательные действия | `cards-badge` |
| Бенчмарки, нормы конверсий, ключевые показатели | `stats` |
| До/после, проблема/решение (2 колонки) | `stats` (2 карточки: проблема / результат) |

**ЗАПРЕЩЕНО:** кружки (`.step-circle`) — устаревший стиль. Эталон — infographic-stratsessiya-1.png и infographic-stratsessiya-2.png на yoursite.ru.
