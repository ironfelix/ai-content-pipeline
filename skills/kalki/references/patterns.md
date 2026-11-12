# Библиотека калек и неестественных оборотов

Растёт: каждое замечание владельца про кальку добавляется сюда в тот же день (формат: `regex | почему | как по-русски | дата и откуда`). Скрипт `scripts/kalki_scan.py` читает строки между «```patterns» и «(?i)\bЧто открывает (окно|чат|виджет)|calque: what opens the window|«Как открывалось окно», «Почему открылось окно»|24.10.2026, портал МедИИума (владелец)
(?i)\bСколько держат\b|calque: how long they hold|«Сколько окно было открыто»|24.10.2026, портал
(?i)\b(МИС|CRM|система|сервис\w*)\s+(не\s+)?отда(ёт|ет|ют)\b|жаргон разработчиков: returns|«передаёт», «в МИС не видно»|24.10.2026, портал
(?i)\bслот(ы|ов|ам|ами)?\b|жаргон: slots|«свободное время», «окна»|24.10.2026, портал
(?i)\bтикет\w*|жаргон: tickets|«обращения»|24.10.2026, портал
(?i)\bстенд\w*|жаргон: test bench|«тестовый сайт»|24.10.2026, портал
(?i)\b(сайты|филиалы|клиники)\s+(получат|берут|возьмут)\b|неодушевлённое подлежащее-получатель|«на сайтах появится», «для филиала действуют»|24.10.2026, портал
(?i)\bс прошлого шага\b|calque: from the previous step|«от прошлого шага»|24.10.2026, портал
(?i)\b(Наследуется|Переопределено)\b|жаргон программистов: inherited, overridden|«как в настройках организации», «в филиале свои настройки»|24.10.2026, портал
(?i)\bЗамер (виджета|показа)\b|calque: widget measurement|«считает виджет», «по данным виджета»|24.10.2026, портал
(?i)\bв ссылке для клиента\b|данные «лежат в ссылке»|«на странице для клиента»|24.10.2026, портал
(?i)\bотвечать по \w+ после (проверки|публикации)|отглагольные без деятеля: after publishing|«когда вы опубликуете», «когда его проверят и опубликуют»|24.10.2026, портал
(?i)\bИтоговые записи\b|calque: final bookings|«Всего записей»|24.10.2026, портал
(?i)^Всё время$|calque: all time|«За всё время»|24.10.2026, портал
(?i)\bв прошлые \d+ дн|calque: in the previous N days|«за предыдущие N дней»|24.10.2026, портал
(?i)\b(начнут приходить|идут в счётчик|шлёт в него)\b|глагол движения у данных|«появятся в Метрике», «передаются в счётчик»|24.10.2026, портал
(?i)\bс сбоем\b|опечатка|«со сбоем»|24.10.2026, портал
(?i)\bвыш(ел|ла|ли) за границы\b|calque: out of bounds|«вышел за рамки»|24.10.2026, портал
(?i)\bпо своему графику\b|calque: per its own schedule|«по графику», «пока филиал не работал»|24.10.2026, портал
(?i)\bиз оставивших\b|субстантивированное причастие: of those who left|«от тех, кто оставил»|24.10.2026, портал
(?i)\bадресу(ем|ет|ют)\s+(этот|эту|вопрос|проблем)|calque: address the issue|«исправим», «займёмся»|24.10.2026, канарейка
(?i)\b(делаем|делать|держит|держать)\s+фокус\b|calque: make or keep focus|«в первую очередь работаем на…», «ведёт разговор к…»|24.10.2026, канарейка
(?i)\bимеет\s+(кнопку|функци\w*|возможност\w*)|calque: X has Y|«в X есть Y»|24.10.2026, канарейка
(?i)\bслучается\s+(чаще|реже)\b|calque: happens more often|«записываются чаще вечером»|24.10.2026, канарейка
(?i)\b(был|была|было|были)\s+\w+\s+(пациентом|агентом|клиникой|администратором)\b|страдательный оборот с деятелем в творительном|«агент ответил», «пациент открыл»|24.10.2026, канарейка
```».

```patterns
# Новые строки дописывать ВНУТРИ блока, перед закрывающей тройной кавычкой (25.10: 53 строки ниже блока скан не видел)
(?i)\bдоход\w+ до (отчёт|отчет|сервис|данных|системы|CRM|МИС)|calque: data reaches report|данные попадают в отчёт, звонок попадает в отчёт, не попадает в отчёт|21.10.2026, коллтрекинг (владелец)
(?i)\bпроход\w+ мимо|calque: passes by|не попадают в учёт, не учитываются, идут мимо подмены (мимо чего именно, уточнить)|21.10.2026
(?i)\b(клиник\w*|компани\w*|сервис\w*|человек\w*|пациент\w*|администратор\w*),\s+(котор(ая|ый|ые|ого|ую|ых))\s+(откры|получ|звон|пиш|выбира|использ|подключ)|calque: a clinic that…|«Если клиника открывает чат, …», «Клиника, которая…» заменить на условие через «если»|05.10.2026
(?im)^(Это|Эти|Таким образом|Данн(ый|ая|ое|ом|ой|ого|ую))\s|calque: These are… / Thus|фраза с глаголом вместо «Это данные…»|03.10.2026 (24.10.2026: «Данные» как «data» больше не ловим, только канцелярское «данный»)
(?i)\bв \d+(,\d+)?\s?% случаев|calque: in N% of cases|«пишет примерно половина», «пишут 81–94%» (о долях людей)|05.10.2026, «очень иишно»
(?i)\b(позволяет|обеспечивает|осуществляет|является|представляет собой)\b|канцелярит / allows, provides|показывает, даёт, делает, это|общие правила
(?i)\bна основе\b|calque: based on|по, из, исходя из, по данным|общее
(?i)\bв рамках\b|calque: within the framework of|в, при, во время|общее
(?i)\b(имеет|делает) смысл\b|calque: makes sense|«есть смысл», «оправданно», «разумно»|общее
(?i)\bиграет роль\b|calque: plays a role|«влияет», «важен»|общее
(?i)\bна самом деле\b|calque: in fact|убрать или «но по факту»|общее
(?i)\bзначим(ый|ая|ое|ые)\b.*\b(рост|снижение|разница)|calque: significant|«заметный», «большой», «статистически значимый» только в статистике|общее
(?i)\b(исследование|отчёт|опрос|данные|сервис|таблица)\s+(показал[аио]?|нашл[аио]?|говор(ит|ят)|утверждает|обещает)\b|calque: the study found/shows (допустимо «показал», но «нашло», «говорят» у неодушевлённого проверять)|подлежащее-источник по-русски: «по данным X», «в исследовании X…»|общее
(?i)\b(звонки|данные|отчёт|сервис|подписка|цена|выборка|аналитика)\s+(покрыва|держит|ловит|падает|лежит|стоит|несёт|слышит)\w*|физический глагол у абстрактного|показывает, составляет, помогает увидеть, звонят реже|08.10.2026
(?i)\bполучен[аоы]?\b|страдательное без деятеля|назвать, кто получил|08.10.2026
(?i)\bпринадлежат\b|calque: belong to the vendor|«опубликовал подрядчик», «замеры сделал разработчик»|21.10.2026
(?i)\bорганик\w*|жаргон|звонки из бесплатного поиска|21.10.2026
(?i)\bвендор\w*|жаргон|поставщик, сервис|21.10.2026
(?i)\bлид(ы|ов|ам|ами)?\b|жаргон|заявка, обращение|21.10.2026
(?i)\bпо построению\b|calque: by construction|«по самой схеме», «потому что оба числа берутся из одной телефонии»|21.10.2026
(?i)\bсодержательн\w+ (останутся|числа)|calque: meaningful|«важными», «показательными»|21.10.2026
(?i)\bвызыва(ет|ют)\s+(более )?позитивн|calque: elicits more positive|«сотрудники принимают лучше»|21.10.2026
(?i)\bпрепринт\b|непонятное слово|«статья, которая ещё не прошла рецензирование», или «исследование»|21.10.2026
(?i)\bаннотаци\w+|calque: abstract|«краткое изложение», «в кратком виде»|21.10.2026
(?i)\b(обращени\w+)\s+(приход|приходит|приходят)\w*\s+(перепиской|звонком)|calque: arrive by chat|на переписку приходится N обращений|03.10.2026
(?i)\bтелефонн(ые|ых) контакт|calque: telephone encounters|звонки|03.10.2026
(?i)\bпрактик[аиу]\b.*(врач|клиник)|calque: practice|клиника|03.10.2026
(?i)\b(это )?не просто\b.*\b(а|это)\b|структурная калька not just X but Y|прямая фраза|общие правила
(?i)\bпо (его )?пункту \d+|calque: per clause N|«такой срок задаёт пункт N», «пункт N обязывает»|23.10.2026, МИС что такое
(?i)\bдопускаются не (дольше|больше)|calque: are allowed for no more than (SLA)|«отводится не больше»|23.10.2026, МИС что такое
(?i)\bфункционал\b|calque: functionality|функции, возможности|23.10.2026, МИС что такое
(?i)\bоблако избавляет|неодушевлённое подлежащее с глаголом человека|«если у клиники один адрес, в облаке не нужно…»|23.10.2026, МИС что такое
(?i)\bв пересказе [«\[]|calque: as retold by|«как пишет X»|23.10.2026, МИС что такое
(?i)\bведётся работа\b|страдательное с отглагольным «работа»|«клиника ведёт пациента от записи до…»|23.10.2026, МИС что такое
(?i)\bне дойд(ут|ёт) до стойки|calque: won't reach the front desk|«телефоны на стойке замолчат»|24.10.2026, IP-телефония
(?i)\bкто перезванивает, не назначено|calque: who calls back is not assigned|«перезванивать никому не поручено»|24.10.2026, IP-телефония
(?i)\bпуть \w+ (в \w+ )?выглядит так|calque: the path of X looks like this|«вот что происходит, когда…»|24.10.2026, IP-телефония
(?i)\bозначает то же самое\b|calque: means the same thing|«так называют то же самое»|24.10.2026, IP-телефония
(?i)\bсколько разрешает тариф|calque: as many as the plan allows|«в пределах тарифа»|24.10.2026, IP-телефония
(?i)\bза набор номера\b|calque: per dial|«за каждый вызов»|24.10.2026, IP-телефония
(?i)\bвыручка в нём стоит на дату|calque: revenue sits on the date|«выручка учитывается по дате оплаты»|24.10.2026, ROMI
(?i)\bставить (её|выручку) на дату|calque: put revenue on the date|«относить выручку к дате»|24.10.2026, ROMI
(?i)\bлежит между (январской|.*стоимостью)|calque: lies between X and Y|«укладывается в данные: в январе…, в июне…»|24.10.2026, ROMI
(?i)\bответ пациента (\w+ )?выясняет|calque: the answer finds out|«по ответу пациента видно»|24.10.2026, ROMI
(?i)\bвышел ровно на порог|calque: came out exactly at the threshold|«только вышел на порог окупаемости»|24.10.2026, ROMI
(?i)\bсрок выручки\b|calque: revenue term|«выручка считается за одинаковый срок»|24.10.2026, ROMI
(?i)\bсвязь между каналом и пациентом (надёжнее )?отметить|calque: mark the link between|«отметить канал в карточке пациента»|24.10.2026, ROMI
(?i)\bROMI по выручке выше нуля ещё может означать|calque: ROMI can still mean a loss|«даже при ROMI выше нуля канал может быть убыточным»|24.10.2026, ROMI
(?i)\bМы советуем, чтобы \w+ (при|в) |calque: we recommend that X do|«администратору достаточно…», «пусть администратор…»|24.10.2026, ROMI
(?i)\bпринимает по пришедшим пациентам|calque: decisions the clinic makes by arrived patients|«решать судьбу канала по пришедшим пациентам»|24.10.2026, ROMI
(?i)\bрейтинг\w* [а-яё]+ по (выдумкам|галлюцинациям)\b|calque: hallucination leaderboard|«рейтинг моделей по тому, как часто они выдумывают сведения»|25.10.2026, ii-assistent
(?i)\bвводит [^.]{0,40}правила о (предупреждении|уведомлении|раскрытии)\b|calque: introduces rules on disclosure|«обяжет … предупреждать, что отвечает ИИ»|25.10.2026, ii-assistent
(?i)\bизделием (программу|продукт|сервис) делает\b|calque: what makes a program a device is|«программа считается медицинским изделием, если производитель заявил …»|25.10.2026, ii-assistent
(?i)\bвыложил\w* для свободной установки\b|calque: released for free installation|«выложил в свободный доступ»|25.10.2026, ii-assistent
(?i)\bтекст(а)? в модель\b|calque: text into the model (input)|«запрос к модели», «текст, который получает модель»|25.10.2026, ii-assistent
(?i)\bвыполня\w* шаги (сам|в других)|calque: performs steps (agentic)|«сам выполняет действия в других программах»|25.10.2026, ii-assistent
(?i)\bвзять в составе\b|calque: get it as part of|«бывает встроен в рабочие сервисы»|25.10.2026, ii-assistent
(?i)\bили пришл[оа] вместе с\b|calque: came along with the question|«что ей передали вместе с вопросом»|25.10.2026, ii-assistent
(?i)сохранять след|calque: keep a trail (audit trail)|«сохранять подтверждение», «сохранять запись о согласии»|24.10.2026, ip-telefoniya
(?i)галочк\w+, по умолчанию пуст|calque: checkbox empty by default|«галочка заранее не проставлена»|24.10.2026, ip-telefoniya
(?i)мимо (него|неё|них) (обычно )?проход|calque: calls go past it|«он не учитывает звонки…»|24.10.2026, voronka-prodazh
(?i)запись была возможна не в каждом|calque: booking was not possible in every call|«не каждый звонок мог закончиться записью»|24.10.2026, voronka-prodazh
(?i)посчитаны людьми|calque: counted as people|«посчитаны по людям, а не по звонкам»|24.10.2026, voronka-prodazh
(?i)разница в срезах (обычно )?говорит|calque: the difference in slices speaks of|«если цифры в разбивке расходятся, причина обычно в…»|24.10.2026, voronka-prodazh
(?i)путь помогает понять причину потери|calque: the journey helps understand the cause of the loss|«путь пациента помогает понять, почему он ушёл»|24.10.2026, voronka-prodazh
(?i)узкое место (тогда )?находится в|calque: the bottleneck is located in|«тогда причина в расписании»|24.10.2026, voronka-prodazh
(?i)у других входов свои|calque: other entry points have their own|«у других каналов первые шаги свои»|24.10.2026, voronka-prodazh
(?i)дала \d+ \S+ моделям пересказать|calque: had N models summarize|«попросила N моделей пересказать»|24.10.2026, chat-bot
(?i)переписку, которую иначе|calque: otherwise conducts|«которую без него приходится вести»|24.10.2026, chat-bot
(?i)открываются у пациентов|calque: open differently for patients|«работают не у всех пациентов одинаково»|24.10.2026, chat-bot
(?i)читает ответ бота как|calque: reads the answer as|«ответ бота звучит для него как слова клиники»|24.10.2026, chat-bot
(?i)банковский ID|calque: bank ID|«вход через банк (T-Business ID, Alfa ID)»|24.10.2026, chat-bot
(?i)советует \[?справка|calque: the help center recommends|«в справке X советуют»|24.10.2026, chat-bot
(?i)так его и стоит настроить|calque: that's how it should be configured|«бота стоит настроить так, чтобы…»|24.10.2026, chat-bot
(?i)окно к врачу|calque: slot to the doctor|«свободное время у врача»|24.10.2026, chat-bot
(?i)не набирает \d+ целевых|calque: the strategy doesn't gather N target actions|«за день не наберётся N целевых действий»|24.10.2026, avito-reklama
(?i)с переходом на сайт (её |этой )?бюджет|calque: with click-through to the site, the budget|«если реклама ведёт на сайт, бюджет…»|24.10.2026, avito-reklama
(?i)связать (пациента|авито) с|calque: to link/attribute a patient to|«понять, что пациент пришёл с X»|24.10.2026, avito-reklama
(?i)ставка (клиники )?выиграла|calque: if the bid wins|«если клиника выиграла аукцион»|24.10.2026, avito-reklama
(?i)кабинет (сам )?тратит бюджет|calque: the account spends the budget|«как Авито расходует бюджет»|24.10.2026, avito-reklama
(?i)ищет людей, которые (скорее|с большей вероятностью)|calque: looks for people more likely to|«показывает баннер тем, кто скорее всего…»|24.10.2026, avito-reklama
(?i)ни в одном из способов|calque: in none of the methods|«ни при одном из способов»|24.10.2026, avito-reklama
(?i)в открытом кейсе|calque: in the public case study|«агентство опубликовало кейс»|24.10.2026, avito-reklama
(?i)вернула больше, чем на неё потратили|calque: returned more than was spent|«сколько процентов сверх вложенного принесла реклама»|24.10.2026, avito-reklama
(?i)отзывы [а-я ]*помогают объявлению|calque: reviews help the listing|«клинику выбирают и по отзывам»|24.10.2026, avito-reklama
(?i)поделится им в боте|calque: shares it in the bot|«если пациент отправит его боту»|25.10.2026, whatsapp-business
(?i)сети находят адреса|calque: networks find addresses|«провайдеры определяют адреса сайтов»|25.10.2026, whatsapp-business
(?i)ограничения (обоих|этих) мессенджеров не сняты|calque: restrictions of both messengers|«ограничения с обоих мессенджеров не сняты»|25.10.2026, whatsapp-business
(?i)работает у всех без|calque: works for everyone without|«пользуется без регистрации и VPN»|25.10.2026, whatsapp-business
(?i)API означает способ|calque: API means a way|«API — способ подключить одну программу к другой»|25.10.2026, whatsapp-business
(?i)тексту?, который [A-Za-zА-Яа-я*]+ заранее проверил|calque: a text pre-approved by|«заранее одобренный текст»|25.10.2026, whatsapp-business
(?i)того, кто ведёт телефон|calque: the one who runs the phone|«того, кто отвечает за телефон клиники»|25.10.2026, whatsapp-business
(?i)получат сохранившие номер|calque: received by those who saved|«сообщение получат те, кто сохранил номер»|25.10.2026, whatsapp-business
(?i)информировать граждан [а-я ]+ (таким|этим) организациям|calque: prohibits informing … to organizations|«запрещает таким организациям информировать граждан»|25.10.2026, whatsapp-business
(?i)расчёт прибыли на одну единицу бизнеса|calque: profit per one unit of business|«расчёт прибыли на одного клиента, заказ или другую единицу, которую продаёт бизнес»|25.10.2026, unit-ekonomika
(?i)распадается на несколько юнитов|calque: splits into several units|«превращается в несколько единиц расчёта»|25.10.2026, unit-ekonomika
(?i)(Внутри|внутри) расчёта по|calque: inside the per-X calculation|«как часть расчёта по …»|25.10.2026, unit-ekonomika
(?i)придётся покрывать (ортопедии|имплантации|[а-я]+ии)\b|calque: X will have to cover the costs|«придётся оплачивать из прибыли …»|25.10.2026, unit-ekonomika
(?i)отчёт считает (по графику|часы)|calque: the report counts hours by|«в отчёте три вида часов: …»|25.10.2026, unit-ekonomika
(?i)уже заплатила рекламой|calque: has already paid for with advertising|«реклама, которая привела обращение, уже оплачена»|25.10.2026, unit-ekonomika
(?i)фирма [A-Za-z ]+, которая работает со|calque: firm X, which works with|«фирма X ведёт учёт у …»|25.10.2026, unit-ekonomika
(?i)порог [0-9,]+ при [0-9,]+|calque: threshold X at Y|«порог X, а фактическое значение Y»|25.10.2026, unit-ekonomika
(?i)окн[оаеу]м? сообщений|calque: message inbox / messaging window|«единое окно», «сервис переписки»|25.10.2026, omnikanalnost
(?i)узнаёт пациента в разных каналах|calque: recognizes a patient across channels|«понимает, что пишет и звонит один пациент»|25.10.2026, omnikanalnost
(?i)путь (пациента|клиента) [^.]{0,40}проходит через|calque: the patient journey passes through|«пациент может сменить несколько каналов»|25.10.2026, omnikanalnost
(?i)(три|два) (сотрудника|пользователя) включены|calque: three users included|«в тариф входят три сотрудника»|25.10.2026, omnikanalnost
(?i)связка из (её|его) справки|calque: the bundle from its docs|«справка называет X и Y»|25.10.2026, omnikanalnost
(?i)результат показывают|calque: the result is shown by|«результат видно по …»|25.10.2026, omnikanalnost
(?i)первое (обычно )?означает [^.]+, второе означает|calque: the former means…, the latter means|«первым словом называют …. Второе значит …»|25.10.2026, omnikanalnost
(?i)тот же путь распадается|calque: the same journey breaks down into|«та же пациентка оставляет три обращения»|25.10.2026, omnikanalnost
(?i)\bтелефонии и окна\b|calque: which telephonies and inboxes it supports|«с какой телефонией и каким единым окном она работает»|25.10.2026, omnikanalnost
(?i)\bпроход(ит|ят|ил|или)\s+план\w* лечения|calque: go through the treatment plan|«доводят план лечения до конца»|27.10.2026, kak-privlech-pacientov
(?i)\bне найд(ут|ёт)\s+времени для записи\b|calque: won't find time to book (смысл: нет окон)|«некуда будет записаться»|27.10.2026, kak-privlech-pacientov
(?i)\bв данных \w+ на первом месте\b|calque: in X's data, Y is in first place|«По данным X, больше всего обращений приходит из Y»|27.10.2026, kak-privlech-pacientov
(?i)\bпри нулевом балансе\b|calque: at zero balance|«когда деньги на балансе заканчиваются»|27.10.2026, kak-privlech-pacientov
(?i)\bответственн\w+ за (ответы|перезвон)\b|calque: person responsible for responses or callbacks|«сотрудник, который отвечает на отзывы», «перезвон ни за кем не закреплён»|27.10.2026, kak-privlech-pacientov
(?i)\bставят\b[^.]{0,30}\bусловий\b|calque: impose N conditions on|«Чтобы реклама не нарушала закон, нужно выполнить N условий»|27.10.2026, kak-privlech-pacientov
(?i)\b(соцсети|сервисы|площадки|каналы|мессенджеры) вроде\b|calque: social networks like|перечислить без «вроде»: «ВКонтакте, Telegram…» или «например»|27.10.2026, kak-privlech-pacientov
(?i)\bне назван\w* по имени\b|calque: not named by name|«не упомянут»|29.10.2026, урок о сайте клиники (слепой судья)
(?i)\bв первую найденную\b|calque: the first clinic found|«в первую же клинику, которую нашли»|29.10.2026, урок о сайте клиники
(?i)\bПравила по постановлению\b|calque: Rules under Resolution|«Правила, утверждённые постановлением»|29.10.2026, урок о сайте клиники
(?i)\bдля закона\b.{0,40}\b(означает|важн)|calque: for the law, X means|«по закону X считается…»|29.10.2026, урок о сайте клиники (Р1, Р7)
(?i)\bс телефона приходится\b|смешение come from и приходится на|«на телефоны приходится»|29.10.2026, урок о сайте клиники
(?i)\bзаплатил\w*\s+к\s+каждому\s+месяцу\b|paid by each month|«нарастающим итогом по месяцам с первого визита»|02.11.2026, подписи схем уроков (ltv)
(?i)\b(Google\s+)?Таблиц\w*\s+(сама\s+)?считает\b|the sheet calculates (неодушевлённый деятель)|«рассчитан в Google Таблице», «в таблице считается»|02.11.2026, подписи схем уроков (dashbord)
(?i)\bотметка\s+(на\s+\w+\s+)?показывает\b|the mark shows|«пунктиром отмечен…», «риской отмечен…»|02.11.2026, подписи схем уроков (romi)
```

## Принципы (не regex)
- Подлежащее-неодушевлённое + глагол действия человека («отчёт нашёл», «данные принадлежат»).
- Глагол движения или веса у данных и понятий («доходит», «проходит», «лежит», «держится»).
- Определительное придаточное «клиника, которая…» там, где по-русски нужно «если».
- Приложение-ярлык «X, Y компания, которая…» у каждого источника.
- Порядок слов, при котором подлежащее в конце: «16% пациентов клиника удерживает».
- Существительное + существительное цепочкой: «оценка результатов сотрудников клиник».
- Любое слово, которое пришлось перевести, чтобы понять.
(?i)\bданные принадлежат\b|calque: data belongs to|«данные хранит …»|26.10.2026, ltv (канарейка подтверждена судьёй)
(?i)\bпроходит план лечения\b|calque: goes through the treatment plan|«заканчивает лечение по плану»|26.10.2026, ltv
(?i)\bкогорт\w* окупа\w*|calque: the cohort pays off|«реклама окупилась у когорты …»|26.10.2026, ltv
(?i)\bсрок жизни (клиента|пациента)\b|calque: customer lifetime|«срок, пока клиент покупает у компании»|26.10.2026, ltv
(?i)\bпринесли \d+([,.]\d+)?% выручки первого года к\b|calque: brought N% of first-year revenue by month M|«к шестому месяцу принесли уже N% выручки, которую дали за весь первый год»|26.10.2026, ltv
(?i)\bлист [«"][^»"]+[»"] сам (находит|считает)|calque: the sheet finds/calculates|«на листе … формулы сами найдут …»|26.10.2026, ltv
(?i)\bсчитает наша Google Таблица\b|calque: our Google Sheet calculates|«посчитан в нашей Google Таблице»|26.10.2026, ltv
(?i)\bотмен\w* (в МИС )?доходит до канала\b|calque: the cancellation reaches the channel|«отмена в МИС видна в канале»|26.10.2026, onlajn-zapis
(?i)\bуход(ит|ят) ли в канал\b|calque: does it go to the channel|«увидит ли это пациент на сайте и в агрегаторе»|26.10.2026, onlajn-zapis
(?i)\bна ПроДокторов не уходит\b|calque: doesn't go to ProDoctorov|«ПроДокторов об этом не узнает»|26.10.2026, onlajn-zapis
(?i)\bс двойной записью путают\b|calque: X is confused with double booking|«часто принимают за двойную запись»|26.10.2026, onlajn-zapis
(?i)\bканалы не видят\b|calque: channels don't see|«ни на сайте, ни на агрегаторах не видно»|26.10.2026, onlajn-zapis
(?i)\bв открытых справках\b|calque: public help docs|«в справках … не сказано»|26.10.2026, onlajn-zapis
(?i)\bближайшие часы сегодняшнего дня\b|calque: the nearest hours of today|«ближайшие два часа»|26.10.2026, onlajn-zapis
(?i)\bчерез лидогенератора\b|одушевлённый винительный у сервиса|«через лидогенератор»|26.10.2026, onlajn-zapis
(?i)\bпереводит разговор\b.{0,40}\bиз публичной ленты\b|calque: the reply moves the conversation from the public feed|«клиника приглашает автора обсудить случай лично»|26.10.2026, serm
(?i)\bвыглядеть подтверждёнными\b|calque: will look confirmed|«остальным отзывам читатель скорее поверит»|26.10.2026, serm
(?i)\bведут работу с отзывами\b|calque: handle review work|«берут на себя всю работу с отзывами»|26.10.2026, serm
(?i)\bРады, что вы нашли время\b|calque: glad you took the time to write|«Спасибо, что написали»|26.10.2026, serm
(?i)\bнам жаль\b|calque: we're sorry (if)|«жаль, что…», «простите, что…»|26.10.2026, serm
(?i)\bклиника как организация\b|calque: the clinic as an organization|«клинике как юрлицу»|26.10.2026, serm
(?i)\bот 24 часов\b|calque: from 24 hours|«не меньше суток»|26.10.2026, serm
(?i)\bзаинтересован\w* в высоком рейтинге\b|calque: interested in a high rating|«кому выгоден высокий рейтинг»|26.10.2026, serm
(?i)\bРядом с \w+ часто встречается термин\b|calque: alongside X you'll see the term Y|«вместе с X часто упоминают Y»|26.10.2026, serm
(?i)\bоценено на \d|calque: rated X based on N ratings|«средняя оценка X, оценок N»|26.10.2026, integration-yclients
(?i)\bсвязывается с системой по\b|calque: integrates per one service|«через интеграцию можно связать только одну услугу»|26.10.2026, integration-yclients
(?i)\bсправка не (предусматривает|описывает)\b|calque: the help doesn't provide for|«по справке, нельзя» / «в справке об этом ничего нет»|26.10.2026, integration-yclients
(?i)\bпревратил\w* в запис|calque: turned into bookings|«закончилось записью»|26.10.2026, integration-yclients
(?i)\bна стороне SQNS\b|calque: on the X side|«хранит X», «в X»|26.10.2026, integration-yclients
(?i)\bМы видим за этим\b|calque: we see behind this|«причина, по-нашему, в…»|27.10.2026, plan-lecheniya
(?i)\bна \d+% влияет\b|calque: X% is affected by|«эти N% зависят от…»|27.10.2026, plan-lecheniya
(?i)\bПубличных справок о\b|calque: public help docs on|«в открытых справках X мы не нашли описания…»|27.10.2026, plan-lecheniya
(?i)\bсогласился на связь\b|calque: agreed to contact|«разрешил с ним связываться»|27.10.2026, plan-lecheniya
(?i)\bс начатым планом без будущей записи\b|calque: patients with a started plan without a future appointment|«которые начали лечение и не записаны на следующий визит»|27.10.2026, plan-lecheniya
(?i)\bкак план попадает к\b|calque: how the plan gets to|«как передать план пациенту»|27.10.2026, plan-lecheniya
(?i)\bсоветуем, чтобы \w+ \w+л\b|calque: recommend that X do|«советуем так: X делает…»|27.10.2026, plan-lecheniya
(?i)\bсогласие \w+ позволяет\b|calque: consent allows you to|«с согласия X можно…»|27.10.2026, medicinskij-marketing
(?i)\bотвечает за весь путь\b|calque: is responsible for the entire journey|«входит весь путь… от … до …»|27.10.2026, medicinskij-marketing
(?i)\bпо итогу видно\b|calque: from the total you can see|«итоговая цифра покажет»|27.10.2026, medicinskij-marketing
(?i)\bв регионах без Москвы\b|calque: in regions excluding Moscow|«за пределами Москвы и Петербурга»|27.10.2026, medicinskij-marketing
(?i)\bтак посчитал сервис\b|calque: as calculated by X (источник в конце)|«По подсчётам X, …»|27.10.2026, medicinskij-marketing
(?i)\bзвонк\w+, которые закончились без записи\b|calque: calls that ended without a booking|«звонки, после которых пациент не записался»|27.10.2026, medicinskij-marketing
(?i)\bзаявок, которые закончились записью\b|calque: requests that ended in an appointment|«заявок, по которым пациент записался»|27.10.2026, obratnyj-zvonok
(?i)\bсделали это в среднем\b|calque: did so on average|повторить глагол: «перезванивали в среднем»|27.10.2026, obratnyj-zvonok
(?i)\bзаявку некому вовремя\b.*\bостаётся без разговора\b|calque: is left without a conversation|«так и не поговорит с клиникой»|27.10.2026, obratnyj-zvonok
(?i)\bотсекает \w+ \w+ как отправленн|calque: cuts off X as sent by|«принимает X за ботов и отсеивает»|27.10.2026, obratnyj-zvonok
(?i)\bразбор \w+ решает\b|calque: the review decides|«зависит от того, как разберут…»|27.10.2026, obratnyj-zvonok
(?i)\bставит себе задачей\b|calque: sets as a task|«заводит задачу»|27.10.2026, obratnyj-zvonok
(?i)\bприятнее, однако\b|calque: is nicer; however|«Пациенту приятно, когда… Но…»|27.10.2026, obratnyj-zvonok
(?i)\bначало звонков по\b|calque: start of calls on … is configurable|«когда начинать звонки по…, можно настроить»|27.10.2026, obratnyj-zvonok
(?i)\bгде после недозвона был\b|calque: where after a failed call there was|«по которым после недозвона позвонили ещё раз»|27.10.2026, obratnyj-zvonok
(?i)\bдальше [«"]порядок[»"]|calque: hereinafter "procedure"|«дальше называем его просто порядком» или без определения|29.10.2026, informirovannoe-soglasie
(?i)\bвписал себя\b|calque: entered himself in the form|«вписал свои ФИО и должность»|29.10.2026, informirovannoe-soglasie
(?i)\bзаконопроект оставляет\b|calque: the bill keeps|«по законопроекту … можно будет пользоваться до …»|29.10.2026, informirovannoe-soglasie
(?i)\bстатья \d+ не называет среди\b|calque: Article N does not name among|«в статье N среди … нет …»|29.10.2026, informirovannoe-soglasie
(?i)\bс памятками о\b.*\bрезультат другой\b|calque: with decision aids … the result is different|«когда памятки готовят сами врачи, результат другой»|29.10.2026, informirovannoe-soglasie
неделя с \d+% | a week at X% | «X% за одну неделю и Y% за другую» | 01.11.2026, dashbord
отдаёт данные | the connection returns data | «в нём видны данные» | 01.11.2026, dashbord
дают слишком широк | N inquiries give too wide a band | «если обращений меньше N, … получается слишком широким» | 01.11.2026, dashbord
стоит в списке | is on the list | «X не поддерживает Y» | 01.11.2026, dashbord
(?:наше|нашему) прочтени | our reading of | как мы понимаем | 01.11.2026, telemedicina
прямо в норме | directly in the rule | прямо указано | 01.11.2026, telemedicina
закон .{0,12}не решает | the law does not settle | закон прямо не говорит | 01.11.2026, telemedicina
проходит за \S+ шагов | goes through N steps | состоит из N шагов | 01.11.2026, telemedicina
отличается от значения прошлого | differs from the previous value | меняется за месяц | 01.11.2026, NPS
Пригодность для \w+ не провер | suitability for X is not verified | метод не проверен для X | 01.11.2026, NPS
в день оценки | on the day of rating | в тот же день | 01.11.2026, NPS
работает с темой | works with the topic of | «на тему», «о здоровье» | 2026-11-01, chat-bot
работала на территории \S+ | worked on the territory of | «можно было в …», «есть в …» | 2026-11-01, chat-bot
выходит под брендом(?! журнал| книг) | released under the brand | продаёт под брендом, работает под брендом | 2026-11-01, mis-dlya-stomatologii
поставить приём|ставит приём | to put an appointment | записать пациента на приём | 01.11.2026, crm-dlya-kliniki
дошл[оа] до записи | leads reached booking | закончились записью, записались | 01.11.2026, crm-dlya-kliniki
разница идёт от | the difference comes from | разница объясняется | 01.11.2026, crm-dlya-kliniki
данные не остаются внутри | data doesn't stay inside | удержать данные внутри | 01.11.2026, crm-dlya-kliniki
дело не освобождает|довод, что .* не освобождает | the argument that… does not exempt | «то, что …, не освобождает» | 01.11.2026, reklama-kliniki
несовпадение с \S+ может сделать | mismatch with X can make | «если он расходится с X, могут признать…» | 01.11.2026, reklama-kliniki
меняют ответ|могут изменить ответ | changes the answer | «ответ другой», «ответ может быть другим» | 01.11.2026, reklama-kliniki
который прош(ёл|ел) модерацию в \S+, \S+ могут | text that passed moderation in X, Y may reject | «Y могут отклонить текст, даже если X его пропустил» | 01.11.2026, reklama-kliniki
(?i)\bобращени\w+ приход\w+ (ночью )?в (обе|вторую|первую)\b|движение у данных: inquiries came to|«приходятся на вторую стоматологию», «обращались в обе»|01.11.2026, detskie-obrashcheniya-nochyu
(?i)\bопределяет в основном\b|driven mainly by|«получились в основном за счёт»|01.11.2026, detskie-obrashcheniya-nochyu
(?i)\bобращени\w+ получил\w* ответ\b|inquiry received a response, деятеля нет|«на какую часть обращений клиника ответила»|02.11.2026, detskie-obrashcheniya-nochyu
(?i)\bпусть этот человек\b|have this person…|«пусть разбирает», «пусть он разбирает»|02.11.2026, detskie-obrashcheniya-nochyu
(?i)\bобращени\w+ в стоматологии\b|падеж двоит: одна клиника, отрасль или несколько клиник|«в стоматологических клиниках … обращения», проверить глазами|02.11.2026, detskie-obrashcheniya-nochyu
(?i)период цены|price period|«за какой срок указана цена»|02.11.2026, integration-klientiks
(?i)\bзвон\w+ придёт с именем\b|the call will come with the name|«пациент увидит имя, под которым сохранил клинику»|03.11.2026, markirovka-zvonkov
(?i)\bпередаёт оператор звонящего по договору\b|transmitted by the caller's carrier under contract (заголовок-пассив)|«оператор звонящего, если заключён договор»|03.11.2026, markirovka-zvonkov
(?i)\bзвонок не получил ответа\b|call received no answer|«никто не взял трубку»|03.11.2026, markirovka-zvonkov
(?i)\bклиник\w*, котор\w+ делает \d|a clinic that makes N calls|«допустим, администраторы клиники набирают пациентов N раз»|03.11.2026, markirovka-zvonkov
(?i)\bс обязательным по закону информированием\b|calls with legally mandatory informing|«если абонента по закону обязаны о чём-то известить»|03.11.2026, markirovka-zvonkov
(?i)\bвместе с массовыми звонками\b|labeling together with mass calls|«маркировка и массовые звонки одним тарифом»|03.11.2026, markirovka-zvonkov
(?i)\bсочли \d+%|was found useful by N%|«N% считают полезной…», подлежащее вперёд|03.11.2026, markirovka-zvonkov
(?i)\bв измеренном эффекте\b|in the measured effect … was at work|«в исследовании эффект дала обычная автоматизация»|03.11.2026, ii-v-stomatologii
(?i)\bпригодится сама механика\b|the mechanics itself will be useful|«пригодится сам подход»|03.11.2026, ii-v-stomatologii
(?i)\bвклад ИИ в\b|AI's contribution to X is less tested|«насколько ИИ помогает с X, проверяли меньше»|03.11.2026, ii-v-stomatologii
(?i)\bработу пересказывает\b|the work is summarized by|«о работе рассказал …»|03.11.2026, ii-v-stomatologii
(?i)\bИИ означает\b|in the table AI means|«ИИ в таблице мы называем…»|03.11.2026, ii-v-stomatologii
(?i)\bчужие данные мало скажут\b|others' data will tell little|«по чужим данным трудно судить»|03.11.2026, ii-v-stomatologii
(?i)\bзадачи вокруг приёма\b|tasks around the visit|«остальные задачи», «работа с пациентами до и после приёма»|03.11.2026, ii-v-stomatologii
(?i)\bсодержит врачебную тайну\b|contains medical confidentiality|«в записи есть сведения, составляющие врачебную тайну»|03.11.2026, ii-v-stomatologii
(?i)\bбез функций интерпретации данных\b|EMRs without data interpretation functions|«если они не интерпретируют медицинские данные»|03.11.2026, ii-v-stomatologii
(?i)\bвести медкарту голосом\b|keep the medical record by voice (голосом говорит врач)|«заполнять медкарту на приёме», «заполнять голосом»|03.11.2026, ii-v-stomatologii
(?i)\bраспределил\w* \d+ врач\w* между\b|randomized N physicians across arms|«по жребию разделили N врачей на группы»|03.11.2026, ii-v-stomatologii
(?i)\b(?:первое|второе|осторожное|два) прочтени\w*|first/second/conservative reading (юр.)|«толкование», «толковать двояко», «если толковать закон строго»|03.11.2026, zakon-ob-ii
(?i)\bначинает касаться\b|begins to apply to|«распространяется на»|03.11.2026, zakon-ob-ii
(?i)\bграницу проводит\b|X draws the line|«где проходит граница, определяет X»|03.11.2026, zakon-ob-ii
(?i)\bнорм\w* «[^»]+» (?:мы )?не нашли|no rule «do X» found|«требования делать X мы не нашли»|03.11.2026, zakon-ob-ii
(?i)\bпереписк\w* с данными\b|correspondence with patient data|«переписка, в которой есть данные пациентов»|03.11.2026, zakon-ob-ii
(?i)\bсрок поставщика\b|the supplier's deadline|«поставщик должен сообщать раньше»|03.11.2026, zakon-ob-ii
(?i)\bвремя до первого контакта\b|time to first contact (метрика)|«как быстро сотрудник связался с пациентом»|05.11.2026, kurator-lecheniya
(?i)\bузким местом \w+ называ\w*|names X as the bottleneck|«главное ограничение, по словам X, в том, что…»|05.11.2026, kurator-lecheniya
(?i)\bперевел\w* в число пациент\w*|converted into the number of patients|«разделили расходы на прибыль с одного пациента»|05.11.2026, kurator-lecheniya
(?i)\bМИС по задаче на\b|MIS by a task for (обрывок без глагола)|«МИС ставит задачу на дату врача»|05.11.2026, kurator-lecheniya
(?i)\bэти часы стоят клинике\b|these hours cost the clinic|«клинике это обходится в»|05.11.2026, kurator-lecheniya
(?i)\bдол\w+ согласий почти не связан\w*|acceptance rate is barely linked to|«рост выручки почти не зависит от того, как часто пациенты соглашаются»|05.11.2026, kurator-lecheniya
(?i)\bупоминают \d+ из \d+ ваканси\w*|mentioned in 3 of 10 vacancies (подлежащее в конце)|«из 10 вакансий о X говорится в трёх»|05.11.2026, kurator-lecheniya
(?i)\bкто или что делает\b|who or what does it (шапка)|«Кто делает»|05.11.2026, kurator-lecheniya
(?i)\bзакон \w+ не подтверждает\b|the law doesn't confirm (the phrase)|«в законе для этого нет оснований»|09.11.2026, otkaz-pacientu
(?i)\bпостроить (весь )?(входящий )?звонок\b|build/structure the call|«вести звонок от начала до конца»|09.11.2026, otkaz-pacientu
(?i)\bответ по-прежнему дают\b|the answer is given by (the Code)|«ответ ищут в кодексе»|09.11.2026, otkaz-pacientu
(?i)\bМне жаль, что так вышло\b|I'm sorry this happened (скрипт поддержки)|«Понимаю, получилось неприятно»|09.11.2026, otkaz-pacientu
(?i)\bпереписка поможет показать\b|the correspondence will help show|«по переписке клиника сможет подтвердить»|09.11.2026, otkaz-pacientu
(?i)\bостаётся следующий шаг\b|still has a next step|«можно предложить, что делать дальше»|09.11.2026, otkaz-pacientu
(?i)\bназывает \w+ среди\b|names X among Y|«X относится к Y»|09.11.2026, otkaz-pacientu
(?i)\bговорит о человеке\b|speaks about the person|«отказывает человеку из-за…»|09.11.2026, otkaz-pacientu
(?i)\bДля долга по прошлому\b|for the debt under the previous contract|«Если пациент должен за прошлое лечение»|09.11.2026, otkaz-pacientu
(?i)\bостаётся законной причиной\b|remains a legitimate reason|«по-прежнему законная причина»|09.11.2026, otkaz-pacientu
(?i)\bоткрыт(ые|ых) смет|open estimates|«опубликованные сметы», «сметы в открытом доступе»|09.11.2026, skolko-stoit-otkryt-stomatologiyu
(?i)\bкому принадлежат лицензи|who owns the license|«на кого оформлена лицензия»|09.11.2026, skolko-stoit-otkryt-stomatologiyu
(?i)\bвернуть пошлину\b|bring back the fee|«снова ввести пошлину» (читается как «вернут деньги»)|09.11.2026, skolko-stoit-otkryt-stomatologiyu
(?i)\bцен[ау] пациента\b|cost per patient|«во сколько обошёлся один пациент»|09.11.2026, skolko-stoit-otkryt-stomatologiyu
(?i)\bтакой разброс не объясняют\b|prices don't explain such a spread|«разброс получается не из-за цен»|09.11.2026, skolko-stoit-otkryt-stomatologiyu
(?i)\bрешает по заявлению\b|decides on the application|«рассматривает заявление»|09.11.2026, skolko-stoit-otkryt-stomatologiyu
(?i)\bмож(но|ете) поставить в Таблиц|put your numbers in the sheet|«подставить в Таблицу»|09.11.2026, skolko-stoit-otkryt-stomatologiyu
