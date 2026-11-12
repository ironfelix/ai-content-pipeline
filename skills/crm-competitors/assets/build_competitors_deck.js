/**
 * ШАБЛОН деки «Конкурентное поле: CRM и коммуникации».
 * Обезличен: данные ниже синтетические, замените своими.
 *
 * Стили: crmgroup/data/design-tokens.md — каноничный источник, значения не дублировать.
 * Содержание берётся из <project>/research/competitors-crm.md.
 *
 * Запуск из корня репозитория:
 *   npm install pptxgenjs --prefix <scratchpad>
 *   NODE_PATH=<scratchpad>/node_modules node <project>/build_competitors_deck.js
 *
 * Проверять результат ТОЛЬКО после загрузки в Slides: экспорт обратно в PDF + pdftoppm.
 * Конвертация теряет часть оформления, на исходном PPTX этих дефектов не видно.
 */
const pptxgen = require("pptxgenjs");

const C = {
  ink: "0D0D0D", ink2: "1A1A1A", red: "C01020",
  amber: "D48B00", green: "1A9E5C",
  gray1: "F4F4F4", gray2: "E8E8E8",
  muted: "6B6B6B", light: "9A9A9A", white: "FFFFFF",
};
const F = "Golos Text";              // TT Runs в Slides не загрузить — только Google Fonts
const W = 13.3, H = 7.5, M = 0.75;
const CW = W - 2 * M;
const LOGO = { white: "assets/crm-logo-white.png", dark: "assets/crm-logo-dark.png" };
const RATIO = 21 / 140;

/* ═════════════════ ДАННЫЕ. Правится только этот блок ═════════════════ */

const CLIENT = "Наш бренд";                    // бренд заказчика
const CLIENT2 = null;                          // второй бренд заказчика или null
const PERIOD  = "сентябрь 2026";               // дата наблюдения, идёт в подписи

// Параметры сравнения. 5–7 штук, каждый проверяем снаружи и одинаково у всех.
const COLS = ["Форма\nподписки", "Приложение\nклиента", "Личный\nкабинет",
              "Клуб или\nсообщество", "Механика\nвозврата", "Триггеры\nзаявлены"];

// Y — да, P — частично, N — искали и не нашли, X — нет данных
const ROWS = [
  ["Бренд A", "YYNYNN"],
  ["Бренд B", "YYYNYY"],
  ["Бренд C", "YYYYNN"],
  ["Бренд D", "NYNYNN"],
  ["Бренд E", "NYYNNN"],
  ["Бренд F", "NYNNPN"],
  ["Бренд G", "NNNYNN"],
  ["Бренд H", "XXXXXX"],
];
const OURS = [[CLIENT, "YYNNYN"]].concat(CLIENT2 ? [[CLIENT2, "YYNYNN"]] : []);

// Матрица 2×2: [бренд, x 0..1, y 0..1]. X — данные в одном месте, Y — есть продукт для клиента
const MATRIX = [
  ["Бренд A", 0.78, 0.72], ["Бренд B", 0.85, 0.80], ["Бренд C", 0.60, 0.55],
  ["Бренд D", 0.30, 0.45], ["Бренд F", 0.80, 0.15], ["Бренд G", 0.20, 0.35],
];
const MATRIX_OURS = [[CLIENT, 0.25, 0.65]];

// Карточки: заголовок, лид, три факта, сноска-источник
const CARDS = [
  { brand: "Бренд B",
    lead: "Единственный, кто описал триггерные коммуникации в правовом документе",
    facts: [["689 ₽", "в месяц за платные функции продукта"],
            ["200 000 ₽", "выгода за возврат постоянного клиента"],
            ["1 строка", "про триггеры в политике — на весь рынок"]],
    src: "Источник: политика обработки персональных данных, п. 3.19, проверено 03.09.2026" },
  { brand: "Бренд A",
    lead: "Профиль привязан к продукту, а не к адресу почты",
    facts: [["5 UTM", "меток в каждой форме — источник виден у каждого лида"],
            ["76 546", "клиентов в базе по публичным данным"],
            ["офлайн", "сообщество встречается вживую в течение года"]],
    src: "Источник: HTML форм и раздел для клиентов, проверено 03.09.2026" },
];

// Свободные места: что не занял никто
const GAPS = [
  ["Календарь жизненного цикла не собран ни у кого",
   "Даты покупки и обслуживания лежат в системах, но до писем не доходят"],
  ["Инбокс свободнее, чем push и соцсети",
   "Приложения ставят, но уведомления отключают — почта остаётся"],
  ["Никто не платит адресом за ценность",
   "Форма подписки есть, а причины оставить контакт нет"],
];

// Этапы жизненного цикла: [название, что делает коммуникация, "пусто"|"есть"]
// Пустые этапы — это и есть места под сценарии. Порядок слева направо.
const LIFECYCLE = [
  ["Интерес",     "Новости, подборки, повод вернуться на сайт", "есть"],
  ["Первый контакт", "Заявка или лид-магнит, первое письмо",    "есть"],
  ["Покупка",     "Подтверждение и что дальше",                 "есть"],
  ["Онбординг",   "Первые дни: как начать и не бросить",        "пусто"],
  ["Пользование", "Прогресс, поддержка, помощь вовремя",        "пусто"],
  ["Риск оттока", "Возврат того, кто остановился",              "пусто"],
  ["Повтор",      "Второй продукт, рекомендация",               "пусто"],
];

// Сценарии первого этапа: [название, повод, когда, канал, целевое действие, статус]
// Статус: "есть" — данные и событие в системе; "доработка" — нужно от платформы;
//         "гипотеза" — снаружи не проверить, подтверждаем в первые две недели
const SCENARIOS = [
  ["Приветствие после покупки", "оплата прошла", "через 2 часа", "email", "первый вход", "есть"],
  ["Возврат к продукту", "нет активности 14 дней", "утро вторника", "email", "вернуться", "доработка"],
  ["Помощь на середине", "пройдено 40–60%", "по событию", "email", "дойти до конца", "доработка"],
  ["Второй продукт", "первый завершён", "через 10 дней", "email", "заявка", "гипотеза"],
];

// Отраслевой контекст: [число, подпись, источник]. Только проверяемые факты.
const CONTEXT = [
  ["3 из 6", "брендов рынка работают на одной CDP", "публичные SPF-записи, 08.09.2026"],
  ["3 из 5", "конкурентов платят рефералку через одну партнёрскую сеть", "их же публичные страницы"],
  ["1 из 5", "конкурентов имеет живое мобильное приложение", "RuStore и App Store"],
];

// ESP из публичного SPF. Проверять перед защитой: записи меняются
const ESP = [
  ["Бренд B", "UniOne, Unisender"],
  ["Бренд C", "Unisender"],
  ["Бренд E", "Unisender, отраслевая платформа"],
  ["Бренд A", "только хостер — массовых рассылок с домена не видно"],
  [CLIENT,    "SPF-записи нет"],
];

/* ═════════════════ ДАЛЬШЕ КОД. Обычно править не нужно ═════════════════ */

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "CRM Group";
pres.company = "ООО «Емейл Солджерс»";
pres.title = `Конкурентное поле ${CLIENT}: CRM и коммуникации`;

const sl = (bg, onDark) => {
  const s = pres.addSlide();
  s.background = { color: bg || C.white };
  const w = 1.25;
  s.addImage({ path: onDark ? LOGO.white : LOGO.dark, x: W - M - w, y: 0.62, w, h: w * RATIO });
  return s;
};
function head(s, t, sub, onDark) {
  s.addText(t, { x: M, y: 0.52, w: CW - 1.6, h: 0.9, isTextBox: true, margin: 0,
    fontFace: F, fontSize: 36, bold: true, color: onDark ? C.white : C.ink });
  if (sub) s.addText(sub, { x: M, y: 1.42, w: CW, h: 0.4, isTextBox: true, margin: 0,
    fontFace: F, fontSize: 14, color: onDark ? C.light : C.muted });
}
const box = (s, x, y, w, h, fill) =>
  s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: fill || C.gray1 } });
function foot(s, text, onDark, y) {
  s.addText(text, { x: M, y: y || 6.5, w: CW, h: 0.55, isTextBox: true, margin: 0,
    fontFace: F, fontSize: 10.5, color: onDark ? C.light : C.muted, lineSpacing: 14 });
}
function lead(s, text, onDark, y) {
  s.addText(text, { x: M, y, w: CW, h: 0.5, isTextBox: true, margin: 0,
    fontFace: F, fontSize: 12, color: onDark ? C.white : C.ink2, lineSpacing: 16 });
}

// таблица переменной высоты. colColors — красить ячейки по значению статуса
function table(s, cols, headers, rows, y0, rowH, onDark, colColors) {
  const off = (i) => M + cols.slice(0, i).reduce((a, b) => a + b, 0);
  const STATUS = { "да": C.green, "есть": C.green, "частично": C.amber,
                   "доработка": C.amber, "гипотеза": C.muted };
  headers.forEach((h0, i) => {
    box(s, off(i), y0, cols[i], 0.52, C.ink);
    s.addText(h0, { x: off(i) + 0.14, y: y0, w: cols[i] - 0.28, h: 0.52, isTextBox: true,
      margin: 0, fontFace: F, fontSize: 10, bold: true, color: C.white, valign: "middle",
      align: i === 0 ? "left" : "center", lineSpacing: 12 });
  });
  rows.forEach((row, r) => {
    const y = y0 + 0.52 + r * rowH;
    row.forEach((cell, i) => {
      const alt = r % 2 ? (onDark ? C.ink2 : C.gray1) : (onDark ? C.ink : C.white);
      box(s, off(i), y, cols[i], rowH, alt);
      let col = i === 0 ? (onDark ? C.white : C.ink) : (onDark ? C.light : C.muted);
      if (colColors && i === row.length - 1 && STATUS[cell]) col = STATUS[cell];
      s.addText(cell, { x: off(i) + 0.14, y, w: cols[i] - 0.28, h: rowH, isTextBox: true,
        margin: 0, fontFace: F, fontSize: 10, valign: "middle", lineSpacing: 12,
        color: col, bold: i === 0 || (colColors && i === row.length - 1),
        align: i === 0 ? "left" : "center" });
    });
  });
}

/* типографика: висящие предлоги и неразрывные пробелы в числах.
   Перехватываем addText, чтобы не править текст в трёхстах местах. */
const NB = "\u00A0";   // неразрывный пробел
const SHORT = "в|во|к|ко|с|со|и|а|о|об|у|я|из|за|на|до|по|от|не|ни|же|бы|ли";
const RE_SHORT = new RegExp(`(?<=^|[\\s(«„"'${NB}])(${SHORT})[ \\t]+`, "gi");
function typo(str) {
  return String(str)
    .replace(RE_SHORT, `$1${NB}`).replace(RE_SHORT, `$1${NB}`)
    .replace(/(\d)[ \t]+(?=\d)/g, `$1${NB}`)
    .replace(/(\d)[ \t]+(₽|%|ч\b)/g, `$1${NB}$2`);
}
function typoDeep(x) {
  if (typeof x === "string") return typo(x);
  if (Array.isArray(x)) return x.map(typoDeep);
  if (x && typeof x === "object" && typeof x.text === "string")
    return Object.assign({}, x, { text: typo(x.text) });
  return x;
}
const _addSlide = pres.addSlide.bind(pres);
pres.addSlide = function () {
  const s = _addSlide();
  const _addText = s.addText.bind(s);
  s.addText = (txt, opts) => _addText(typoDeep(txt), opts);
  return s;
};

/* ── 1. обложка ── */
{
  const s = sl(C.ink, true);
  s.addText("Конкурентное поле", { x: M, y: 2.3, w: CW, h: 0.9, isTextBox: true, margin: 0,
    fontFace: F, fontSize: 46, bold: true, color: C.white });
  s.addText("CRM и коммуникации с клиентом", { x: M, y: 3.2, w: CW, h: 0.6, isTextBox: true,
    margin: 0, fontFace: F, fontSize: 22, color: C.light });
  s.addText(`${ROWS.length} брендов · ${COLS.length} признаков · только открытые источники · ${PERIOD}`,
    { x: M, y: 4.3, w: CW, h: 0.5, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 13, color: C.red, bold: true });
}

/* ── 2. как смотрели и как читать ── */
{
  const s = sl(C.white);
  head(s, "Как мы смотрели", "И что означает «не найдено»");
  const items = [
    ["Сайты и код форм", "Поля, обязательность, тексты чекбоксов, какие параметры уходят"],
    ["Правовые документы", "Политики и согласия описывают каналы и подрядчиков точнее маркетинга"],
    ["Публичный DNS", "SPF называет платформу рассылок — читается без доступа к системам"],
    ["Магазины приложений", "Разработчик, рейтинг, установки и отзывы пользователей"],
  ];
  items.forEach((it, i) => {
    const y = 2.15 + i * 0.92;
    box(s, M, y, 0.06, 0.72, C.red);
    s.addText(it[0], { x: M + 0.3, y, w: 3.2, h: 0.36, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 14, bold: true, color: C.ink, valign: "middle" });
    s.addText(it[1], { x: M + 3.7, y, w: CW - 3.9, h: 0.72, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 12, color: C.muted, valign: "middle", lineSpacing: 15 });
  });
  box(s, M, 5.95, CW, 0.62, C.gray1);
  s.addText([{ text: "«Не найдено» значит, что мы искали и не нашли. ", options: { bold: true, color: C.ink } },
             { text: "Это не значит, что механики нет: она может жить в приложении, в закрытой части или в офлайне.",
               options: { color: C.muted } }],
    { x: M + 0.25, y: 5.95, w: CW - 0.5, h: 0.62, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 12, valign: "middle" });
}

/* ── 3. карта рынка: тепловая карта ── */
{
  const s = sl(C.white);
  head(s, "Карта рынка", `${COLS.length} признаков, по которым сравнивали бренды`);
  const NAMEW = 1.95, GAP = 0.06;
  const cw = (CW - NAMEW - COLS.length * GAP) / COLS.length;
  const colX = (k) => M + NAMEW + k * (cw + GAP);
  const FILL = { Y: C.green, P: C.amber, N: C.gray2, X: C.gray1 };

  COLS.forEach((c, k) => s.addText(c, { x: colX(k), y: 1.95, w: cw, h: 0.5, isTextBox: true,
    margin: 0, fontFace: F, fontSize: 9.5, bold: true, color: C.muted, align: "center",
    valign: "bottom", lineSpacing: 11 }));

  const rowH = 0.29;
  const draw = (list, y0, ours) => list.forEach((r, i) => {
    const y = y0 + i * rowH;
    s.addText(r[0], { x: M, y, w: NAMEW - 0.15, h: rowH, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 10.5, bold: ours, color: ours ? C.ink : C.ink2, valign: "middle" });
    r[1].split("").forEach((v, k) => {
      // X («нет данных») почти неотличим от N («не найдено») после конвертации в Slides,
      // поэтому рисуем его белым с серой обводкой, а не второй заливкой серого
      if (v === "X")
        s.addShape(pres.ShapeType.rect, { x: colX(k), y: y + 0.05, w: cw, h: rowH - 0.1,
          fill: { color: C.white }, line: { color: C.gray2, width: 1, dashType: "dash" } });
      else box(s, colX(k), y + 0.05, cw, rowH - 0.1, FILL[v]);
    });
  });

  draw(ROWS, 2.45, false);
  const yOurs = 2.45 + ROWS.length * rowH + 0.44;
  s.addShape(pres.ShapeType.line, { x: M, y: yOurs - 0.36, w: CW, h: 0, line: { color: C.ink, width: 1 } });
  s.addText("Бренды заказчика, не конкуренты: та же шкала для сравнения",
    { x: M, y: yOurs - 0.33, w: 5.0, h: 0.27, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 9.5, bold: true, color: C.red, valign: "middle" });
  draw(OURS, yOurs, true);

  [["Найдено", C.green], ["Частично", C.amber], ["Не найдено", C.gray2], ["Нет данных", null]]
    .forEach((l, i) => {
      const x = M + 5.35 + i * 1.65;
      if (l[1]) box(s, x, yOurs - 0.27, 0.2, 0.15, l[1]);
      else s.addShape(pres.ShapeType.rect, { x, y: yOurs - 0.27, w: 0.2, h: 0.15,
        fill: { color: C.white }, line: { color: C.gray2, width: 1, dashType: "dash" } });
      s.addText(l[0], { x: x + 0.28, y: yOurs - 0.33, w: 1.35, h: 0.27, isTextBox: true,
        margin: 0, fontFace: F, fontSize: 9.5, color: C.muted, valign: "middle" });
    });
}

/* ── 4. матрица 2×2 ── */
{
  const s = sl(C.white);
  head(s, "Где каждый бренд", "По горизонтали — данные в одном месте. По вертикали — есть продукт для клиента");
  const X0 = M + 1.2, Y0 = 2.2, PW = CW - 2.4, PH = 3.9;
  box(s, X0, Y0, PW, PH, C.gray1);
  s.addShape(pres.ShapeType.line, { x: X0 + PW / 2, y: Y0, w: 0, h: PH, line: { color: C.gray2, width: 1 } });
  s.addShape(pres.ShapeType.line, { x: X0, y: Y0 + PH / 2, w: PW, h: 0, line: { color: C.gray2, width: 1 } });

  const put = (list, ours) => list.forEach(([n, x, y]) => {
    const px = X0 + x * PW, py = Y0 + (1 - y) * PH;
    s.addShape(pres.ShapeType.ellipse, { x: px - 0.07, y: py - 0.07, w: 0.14, h: 0.14,
      fill: { color: ours ? C.red : C.ink } });
    s.addText(n, { x: px + 0.14, y: py - 0.13, w: 1.9, h: 0.28, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 10, bold: ours, color: ours ? C.red : C.ink2, valign: "middle" });
  });
  put(MATRIX, false); put(MATRIX_OURS, true);

  s.addText("Данные собраны в одном месте  →", { x: X0, y: Y0 + PH + 0.1, w: PW, h: 0.3,
    isTextBox: true, margin: 0, fontFace: F, fontSize: 10, color: C.muted, align: "center" });
  s.addText("Есть продукт\nдля клиента", { x: M - 0.05, y: Y0, w: 1.15, h: 0.6, isTextBox: true,
    margin: 0, fontFace: F, fontSize: 10, color: C.muted, lineSpacing: 12 });
  foot(s, "Положение по осям — оценка по публичным признакам, а не по внутренним данным брендов.", false, 6.45);
}

/* ── 5. карточки брендов ── */
CARDS.forEach((c) => {
  const s = sl(C.white);
  head(s, c.brand, c.lead);
  c.facts.forEach((f, i) => {
    const x = M + i * (CW / 3);
    s.addText(f[0], { x, y: 2.5, w: CW / 3 - 0.4, h: 0.9, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 40, bold: true, color: C.red });
    s.addText(f[1], { x, y: 3.5, w: CW / 3 - 0.4, h: 1.1, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 12, color: C.muted, lineSpacing: 16 });
  });
  foot(s, c.src, false, 6.3);
});

/* ── 6. чем шлют: ESP из публичного SPF ── */
{
  const s = sl(C.white);
  head(s, "Чем они шлют", "SPF-записи домена публичны и называют платформу рассылок");
  ESP.forEach((e, i) => {
    const y = 2.2 + i * 0.62, ours = e[0] === CLIENT;
    box(s, M, y, CW, 0.5, i % 2 ? C.white : C.gray1);
    s.addText(e[0], { x: M + 0.2, y, w: 3.0, h: 0.5, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 12, bold: true, color: ours ? C.red : C.ink, valign: "middle" });
    s.addText(e[1], { x: M + 3.4, y, w: CW - 3.6, h: 0.5, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 12, color: ours ? C.red : C.muted, valign: "middle" });
  });
  foot(s, `Записи проверены ${PERIOD} и меняются. Платформа может стоять на поддомене — «не нашли» не равно «не шлют».`,
    false, 6.5);
}

/* ── 7. свободные места ── */
{
  const s = sl(C.white);
  head(s, "Что не занял никто", "Места, где рынок пустой — и туда можно зайти первым");
  GAPS.forEach((g, i) => {
    const y = 2.2 + i * 1.35;
    s.addText(String(i + 1), { x: M, y, w: 0.6, h: 0.6, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 30, bold: true, color: C.red });
    s.addText(g[0], { x: M + 0.75, y, w: CW - 0.9, h: 0.45, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 17, bold: true, color: C.ink });
    s.addText(g[1], { x: M + 0.75, y: y + 0.5, w: CW - 0.9, h: 0.6, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 12, color: C.muted, lineSpacing: 16 });
  });
}

/* ── 8. схема жизненного цикла ── */
if (LIFECYCLE && LIFECYCLE.length) {
  const s = sl(C.white);
  head(s, "Жизненный цикл клиента", "Красным — этапы, на которых коммуникации сейчас нет");
  const n = LIFECYCLE.length;
  const cw = (CW - (n - 1) * 0.12) / n;
  const yLine = 2.75;
  s.addShape(pres.ShapeType.line, { x: M, y: yLine, w: CW, h: 0, line: { color: C.gray2, width: 2 } });
  LIFECYCLE.forEach((st, i) => {
    const x = M + i * (cw + 0.12);
    const empty = st[2] === "пусто";
    s.addShape(pres.ShapeType.ellipse, { x: x + cw / 2 - 0.09, y: yLine - 0.09, w: 0.18, h: 0.18,
      fill: { color: empty ? C.red : C.ink } });
    s.addText(st[0], { x, y: yLine - 0.85, w: cw, h: 0.6, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 12.5, bold: true, align: "center", valign: "bottom",
      color: empty ? C.red : C.ink, lineSpacing: 14 });
    s.addText(st[1], { x, y: yLine + 0.3, w: cw, h: 1.5, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 10, align: "center", color: C.muted, lineSpacing: 13 });
  });
  foot(s, "Пустые этапы — это не упрёк, а место, где программа может начать зарабатывать.", false, 6.3);
}

/* ── 9. сценарии первого этапа ── */
if (SCENARIOS && SCENARIOS.length) {
  const s = sl(C.white);
  head(s, "Сценарии первого этапа", "Меряем действием, а не открытиями");
  const cols = [3.0, 2.5, 1.7, 1.1, 1.9, 1.6];
  table(s, cols, ["Сценарий", "Повод", "Когда", "Канал", "Целевое действие", "Готовность"],
    SCENARIOS, 2.15, 0.62, false, true);
  // легенда встаёт под таблицу, а не на фиксированную высоту:
  // при пяти строках захардкоженный y наезжал на последнюю строку
  const yLeg = 2.15 + 0.52 + SCENARIOS.length * 0.62 + 0.22;
  const LEG = [["есть", "данные и событие уже в системе"],
               ["доработка", "нужно получить от платформы"],
               ["гипотеза", "проверяем в первые две недели"]];
  LEG.forEach((l, i) => {
    s.addText([{ text: l[0] + " — ", options: { bold: true, color: C.ink } },
               { text: l[1], options: { color: C.muted } }],
      { x: M + i * (CW / 3), y: yLeg, w: CW / 3 - 0.3, h: 0.4, isTextBox: true, margin: 0,
        fontFace: F, fontSize: 10 });
  });
  foot(s, "Целевые значения ставим после замера baseline: число в контракте без замера становится проблемой для обеих сторон.",
    false, Math.min(yLeg + 0.55, 6.5));
}

/* ── 10. отраслевой контекст ── */
if (CONTEXT && CONTEXT.length) {
  const s = sl(C.gray1);
  head(s, "Контекст рынка", "Три факта, которые меняют расстановку сил");
  CONTEXT.forEach((c, i) => {
    const y = 2.25 + i * 1.4;
    s.addText(c[0], { x: M, y, w: 2.4, h: 0.75, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 34, bold: true, color: C.red });
    s.addText(c[1], { x: M + 2.6, y: y + 0.05, w: CW - 2.8, h: 0.5, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 15, color: C.ink, lineSpacing: 18 });
    s.addText(c[2], { x: M + 2.6, y: y + 0.58, w: CW - 2.8, h: 0.35, isTextBox: true, margin: 0,
      fontFace: F, fontSize: 10, color: C.muted });
  });
}

/* ── 11. что добавит регулярный отчёт (тёмный финал) ── */
{
  const s = sl(C.ink, true);
  head(s, "Что добавит регулярный отчёт", "Чего принципиально нет в версии по открытым источникам", true);
  lead(s, "Сейчас мы видим то, что бренды опубликовали сами. Их писем мы не видели: "
        + "форм не заполняли, на рассылки не подписывались.", true, 2.2);
  ["Подписка с отдельного адреса на каждый бренд",
   "Частота, поводы и структура писем месяц к месяцу",
   "Их welcome-цепочки целиком",
   "Сравнение с вашей программой на одной шкале"]
    .forEach((t, i) => {
      s.addShape(pres.ShapeType.ellipse, { x: M, y: 3.35 + i * 0.5, w: 0.09, h: 0.09, fill: { color: C.green } });
      s.addText(t, { x: M + 0.3, y: 3.27 + i * 0.5, w: CW - 0.5, h: 0.4, isTextBox: true, margin: 0,
        fontFace: F, fontSize: 12.5, color: C.light, valign: "middle" });
    });
  s.addText([{ text: "Полная версия с источниками: ", options: { bold: true, color: C.white } },
             { text: "отдельным файлом, полный URL на каждую находку", options: { color: C.light } }],
    { x: M, y: 6.2, w: CW, h: 0.4, isTextBox: true, margin: 0, fontFace: F, fontSize: 11.5 });
}

pres.writeFile({ fileName: "Конкуренты_CRM.pptx" }).then((f) => console.log("Сохранено:", f));
