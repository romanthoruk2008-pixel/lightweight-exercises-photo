# Перевірка техніки для передачі B

Перевірено весь англійський блок кожного з 15 нічних ID, його equipment/muscles, match/source, точний запис working-manifest і вибраний dataset record. Вибірка тільки за точним ID; збіг ID/назви не вважався підтвердженням техніки. Каталог і 4448 мовних блоків не змінено.

Докази, дослівні цитати, SHA256, джерела та журнал доступності: `data/audits/agent-03-generator-b-continuation-2026-10-02-technique.json`. Помилки й проблемні поля: `data/audits/agent-03-source-description-errors-2026-10-02.json`. Повний поточний blocked review: `data/queues/agent-03-generator-b-continuation-2026-10-02-blocked.json`.

## Перші вісім нічних записів

| ID | Результат і що саме підтверджено |
| --- | --- |
| downward-dog | ready: inverted-V, долоні/стопи як опори, довгий нейтральний хребет, допустиме м’яке згинання колін. English authored + [ACE](https://www.acefitness.org/resources/everyone/exercise-library/18/downward-facing-dog/). |
| bear-crawl | ready: низький тулуб, коліна над підлогою, протилежні рука/нога. English + вибраний dataset + [ACE](https://www.acefitness.org/resources/everyone/exercise-library/150/bear-crawl/). Вибір правої руки/лівої ноги — дзеркальна фаза того самого руху. |
| jumping-jack | ready: одночасне розведення стоп і підняття рук; м’яке приземлення. English і вихідні instructions визначають рух. Слово pedal у generic cue не застосовується. |
| high-knees | ready: права нога до висоти таза, ліва опорна; quick step саме для high knees. English authored прямо відрізняє це від skips/hop. |
| mountain-climber | ready: high plank, руки під плечима, коліно до грудей, низький таз. English + вихідні instructions визначають усі контакти; не TRX і не cross-body. |
| diamond-pushup | ready: контакт великих/вказівних пальців ромбом, лікті близько, без clap. Точні Polish instructions + [TRX](https://www.trxtraining.com/blogs/news/bicep-workouts-at-home). Помилкові м’язові твердження видавця не переносилися. |
| chest-fly-dumbbell | ready: спина на горизонтальній лаві, дві гантелі, долоні одна до одної, м’які лікті, широка дуга. Вихідні instructions + [ACE](https://www.acefitness.org/resources/everyone/exercise-library/21/lying-chest-fly/). |
| waiter-curl-dumbbell | blocked: і English, і dataset описують звичайний двогантельний supinated curl. Це повторення опису, а не незалежне підтвердження відмінної техніки Waiter Curl. Не підмінено одно- чи двогантельним варіантом навмання. |

Сім ready включено в окремий пакет **026**. Усі 15 нічних записів повернуто під підготовку agent-03 прямим рішенням користувача; початковий нічний файл залишено без змін.

## Додатково розв’язані записи

| ID | Вид рішення | Підстава |
| --- | --- | --- |
| cross-body-hammer-curl-dumbbell | Підтвердження техніки | Вибрані вихідні instructions і точний Polish задають дві гантелі, neutral grip, лікті близько й діагональний рух до протилежного плеча. [TRX](https://www.trxtraining.com/blogs/news/bicep-workouts-at-home) підтверджує cross-body hammer variation. English barbell — записана помилка, не джерело сцени. |
| concentration-curl-dumbbell | Підтвердження техніки | Вихідні instructions і Polish прямо задають сидіння на лаві, одну гантель, underhand grip та лікоть на внутрішній стороні стегна. Підтверджено конкретні контакти й рух, не лише dataset name. English barbell/stand-or-sit — записана помилка. |
| clean-barbell | Допустимі варіанти + обґрунтований вибір ілюстрації | [CrossFit](https://www.crossfit.com/essentials/foundational-movement-clean-what-is-a-clean) визначає hook grip, pull-under, elbows forward та два допустимі catch: power/full squat. Саме catalog match відхиляє Power Clean через глибину; тому обрано full-squat receiving. Це не схвалення попередньої рекомендації від імені користувача. |

Вони включені в **027**, разом із сімома явно погодженими загальними сценами/взуттям. HIIT/Pilates/Stretching/Yoga — **вибір ілюстрації користувача**, а не зовнішнє підтвердження, що широка категорія дорівнює лише одному руху. Взуття Walking/Hiking і boots/bindings/protection Snowboarding — вузьке погоджене доповнення; захисний helmet у snowboard сцені — сумісний вибір ілюстрації підготовчого агента, не вигадана цитата користувача. Див. `docs/exercise-image-style-illustration-footwear.md`.

## Що залишається blocked: 20

Користувача не просимо вгадувати техніку. Для цих записів потрібне точне джерельне підтвердження, якого наразі недостатньо; до отримання такого джерела prompts не передаються.

| Точний ID | Конкретна причина |
| --- | --- |
| waiter-curl-dumbbell | Не підтверджено відмінну кількість гантелей/контакт долонь саме Waiter Curl. |
| bicycle-crunch | Звичайний feet-flat crunch у English проти alternating elbow/knee у match; конкретний велосипедний варіант не визначений. |
| bicycle-crunch-raised-legs | Feet-flat English проти raised-leg bicycle; геометрія ніг і відмінність від окремого bicycle-crunch не визначені. |
| floor-triceps-dip | Підлога в instructions, паралельні опори в description, край лави/стільця в dataset: три різні сцени. |
| lying-neck-extension | Не визначені орієнтація тулуба, його опора й вільне положення голови. |
| seated-incline-curl-dumbbell | Руки висять за тулубом у description, але upper arms спираються на лаву в instructions і dataset. |
| chest-dip-weighted-machine | Parallel supports у English проти straight-bar source; dip belt підтверджує лише обтяження. |
| drag-curl-barbell | Нерухомі upper arms у source проти потрібної відмінної drag-траєкторії. |
| feet-up-bench-press-barbell | Стопи на підлозі / ноги в повітрі зі згинанням / стопи на лаві — суперечливі джерельні варіанти. |
| hammer-curl-band-resistance-band | Neutral grip відомий, але точні handles/стрічка/анкер не визначені; гантельний приклад не підходить. |
| hip-thrust-barbell | Опора лише верхньої спини проти лежання всім тулубом на лаві; знайдений dumbbell приклад не підтверджує весь barbell варіант. |
| landmine-180-barbell | Hip-to-hip проти hip-to-opposite-shoulder; інший landmine press/row не визначає кінцевих точок. |
| lying-neck-extension-weighted-plate | Plate на потилиці, але орієнтація тулуба/опора голови/доступний рух не визначені. |
| nordic-hamstrings-curls | Не підтверджено точний пасивний анкер щиколоток і повернення без партнера/відкладеного тренажера. |
| pushup-weighted | TRX підтверджує vest як допустимий варіант, але не його відповідність саме upper-back/plate запису. |
| side-bend-dumbbell | Нахил від гантелі й одночасне опускання гантелі задають суперечливий напрямок. |
| single-arm-landmine-press-barbell | Standing split stance/free sleeve проти anchored-end і back-pad тексту; half-kneeling демонстрація — інші опори. |
| single-leg-standing-calf-raise-barbell | Обидві руки утримують вільний гриф, але safety одночасно вимагає handhold/machine support. |
| muscle-up-machine | Bar support з розігнутими руками підтверджено CrossFit; catalogue/source вимагають повороту overhand у palms-toward-self і закінчення зі зігнутими руками. Точний перехід хвата не підтверджено. |
| press-under-barbell | Не визначено receiving stance/depth: partial/full squat або split. Інший overhead press не замінює drill. |

403/404, HTTP200 зі звичайною головною сторінкою й демонстрації інших варіантів не використані як докази. Збережені посилання на невдалі/недостатні дослідження не означають, що їхній зміст підтвердив техніку. Фотографії/відео не завантажувалися, генерація не запускалася.

## Призначення й збереження

A — **12 вправ 024–025 без змін**. B — **009: 9 продовжень; 026: 7; 027: 10**. Dead Hang пропущено через збережений PNG. Hanging Knee Raise має дві історичні невдалі спроби; наступна — 3, решта восьми 009 — 1. Це історія, а не нові виклики.

Перед передачею звірені Git-дерева PNG і конкретні selected assignments у всіх доступних віддалених гілках. У нових пакетах немає PNG/pending чи перетинів із A/чужими призначеннями. Незапушені результати або виклики інших хмарних задач можуть бути невидимі; повторна перевірка потрібна перед кожним викликом генератора.

Тренажери, троси й Сміт — наступний етап. Існуючі 114 планових кандидатів не призначені одним завданням. Shared progress, catalog, схвалення PNG, Supabase і чужі результати не змінено.
