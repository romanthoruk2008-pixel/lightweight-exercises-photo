# Наступні пакети 034–036 для одного генератора

Готово **29 вправ**: 10 + 10 + 9. Створено тільки prompts/призначення, викликів image_gen немає.
Джерельна гілка: `agent-03-inventory-2026-10-01`; незмінний коміт завдань: `fec6f45faa15189808e8dfd765916825d4894007`.
Виконавець той самий: `agent-08-generator-single-2026-10-03`. Чинні завдання та спроби 001–033, A/B і чужі призначення не забираються.

## Пакети й точні ID

### agent-03-others-034 — ready, 10

Файл: `data/batches/agent-03-others-034.json`; порядок: 1.

| exercise_id | Назва з каталогу |
| --- | --- |
| `back-extension-hyperextension-machine` | Back Extension (Hyperextension) |
| `chest-supported-t-bar-row-machine` | Chest Supported T Bar Row |
| `hip-thrust-machine` | Hip Thrust (Machine) |
| `iso-lateral-low-row-machine` | Iso-Lateral Low Row |
| `iso-lateral-row-machine` | Iso-Lateral Row (Machine) |
| `leg-press-machine` | Leg Press (Machine) |
| `lying-leg-curl-machine` | Lying Leg Curl (Machine) |
| `pendulum-squat-machine` | Pendulum Squat (Machine) |
| `single-leg-press-machine` | Single Leg Press (Machine) |
| `squat-machine` | Squat (Machine) |

### agent-03-others-035 — ready, 10

Файл: `data/batches/agent-03-others-035.json`; порядок: 2.

| exercise_id | Назва з каталогу |
| --- | --- |
| `triceps-extension-machine` | Triceps Extension (Machine) |
| `cycling-machine` | Cycling |
| `elliptical-trainer-machine` | Elliptical Trainer |
| `cable-crunch-machine` | Cable Crunch |
| `front-raise-cable-machine` | Front Raise (Cable) |
| `lat-pulldown-close-grip-cable-machine` | Lat Pulldown - Close Grip (Cable) |
| `lateral-raise-cable-machine` | Lateral Raise (Cable) |
| `overhead-triceps-extension-cable-machine` | Overhead Triceps Extension (Cable) |
| `rear-delt-reverse-fly-cable-machine` | Rear Delt Reverse Fly (Cable) |
| `rope-straight-arm-pulldown-machine` | Rope Straight Arm Pulldown |

### agent-03-others-036 — ready, 9

Файл: `data/batches/agent-03-others-036.json`; порядок: 3.

| exercise_id | Назва з каталогу |
| --- | --- |
| `shrug-cable-machine` | Shrug (Cable) |
| `single-arm-cable-row-machine` | Single Arm Cable Row |
| `single-arm-curl-cable-machine` | Single Arm Curl (Cable) |
| `single-arm-lat-pulldown-machine` | Single Arm Lat Pulldown |
| `triceps-extension-cable-machine` | Triceps Extension (Cable) |
| `triceps-kickback-cable-machine` | Triceps Kickback (Cable) |
| `upright-row-cable-machine` | Upright Row (Cable) |
| `decline-bench-press-smith-machine` | Decline Bench Press (Smith Machine) |
| `hip-thrust-smith-machine` | Hip Thrust (Smith Machine) |

## Джерела, рішення і стиль

Каталог незмінний: 451 ID, 4448 мовних блоків; SHA256 `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`.
Кожне завдання самодостатнє: точний exercise_id/name, весь English, equipment і primary/secondary саме цього ID, хеші каталогу/запису/English/prompt, конкретні поза/фаза/хват/контакти/траєкторія/ракурс, approved style files, appearance reference та planned cloud/Git PNG paths. Вихідні тексти не редагувалися.

Технічні джерела й selected scene: `data/audits/agent-03-single-generator-round3-2026-10-03-technique.json`. Прочитані фактичні instruction_steps вибраного dataset, а не лише назва/ID/binding. Authored записи без dataset спираються на свої English description/instructions/cues/mistakes/safety. Стандартна сумісна конструкція без бренду дозволена AGENTS.md: функціональне розміщення рами/виходу троса відокремлено від факту джерела; невказані кут, хват, навантаження або насадка не записані як підтверджені джерелом. Вибір сторони/фази та прямо дозволеного варіанта є вибором ілюстрації, а не новим схваленням користувача.

Окремий журнал: `data/audits/agent-03-single-generator-round3-2026-10-03-source-errors.json`. Для cable-crunch-machine description каже supine, але actual English instructions і dataset однозначно підтверджують kneeling facing away: scene відтворює це підтверджене виконання, raw description лишено. У leg-press / single-leg-press / lying-leg-curl збережені загальні upper-limb поля: вони не перетворюють завдання на arm press/curl; actual instructions/dataset визначають робочі суглоби. Upright row зображає English stop на верхній частині грудей, без переходу до вищого dataset chin endpoint. Iso-lateral row має chest pad за safety note саме цього ID. Single-arm cable row використовує явно дозволений upright bench варіант; conditional chest-pad поле не додає відсутньої опори.

Еталон тільки зовнішності/матеріалів: `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Перед першим викликом еталон треба відкрити. Поза/обладнання/підсвітка еталона не копіюються.
Стиль: `docs/exercise-image-style.md` (v1), затверджене `docs/exercise-image-style-neutral-primary.md` (v1-neutral-primary-2026-10-02), рішення `data/style-decisions/agent-03-neutral-primary-approved.json`. Сріблясто-сіра лиса анатомічна чоловіча модель, чорні шорти, barefoot, одна фаза/людина, прозорий 1024×1024 PNG, весь figure/equipment.
Конкретний primary — #F26445; лише secondary точного ID — 40–50%. **cycling-machine та elliptical-trainer-machine мають primary=cardio і порожній secondary: залишаються повністю нейтральними, без підсвітки.** Не додавати їм м'язи за знаннями чи з іншої вправи. Інші 27 мають конкретний primary.

## Продовження виконавцем

1. Fetch актуальні work, підготовчу та всі доступні агентські гілки. Продовжувати existing `agent-08-generator-single-2026-10-03`; не reset/recreate гілку й не втрачати старі PNG/failed attempts/history. Пуш тільки власної гілки виконавця.
2. Прочитати нове призначення `data/assignments/agent-03-single-generator-round3-2026-10-03.json`. Перенести лише нові 034–036, new assignment/evidence/errors і `data/manifests/agent-03-single-generator-round3-2026-10-03/generator-single.json` з коміту `fec6f45faa15189808e8dfd765916825d4894007`. Якщо цей manifest уже має attempts, не замінювати стартовим. Каталог, shared progress, стару чергу та попередні manifests не копіювати поверх. Style/reference звірити за hashes у task. Повідомлення/handoff читати з актуальної підготовчої гілки.
3. Виконувати 034 → 035 → 036, після раніше взятих завдань. Перед КОЖНИМ викликом читанням звіряти актуальні Git PNG/призначення доступних агентів, власні локальні результати та manifests. Будь-який PNG точного ID, включно з pending, або нове чуже призначення — skip із branch/commit/path/reason. Старий failed call без PNG не є результатом і залишається в попередньому пакеті; не переносити його сюди.
4. Використовувати generation_prompt саме точного ID, exact approved style та appearance-only reference. Лише вбудований image_gen, одна вправа/фаза/людина. Не застосовувати загальний pose шаблон, не додавати equipment або muscles.
5. Окрема папка результатів `/workspace/exercise-image-results/agent-03-single-generator-round3-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`; Git `assets/exercises/pending/agent-03-single-generator-round3-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`. У task є точні planned paths. За потреби додати лише 29 точних PNG allowlist-рядків у свою .gitignore, не замінювати весь файл підготовчою версією і не робити широких винятків.
6. Оновлювати `data/manifests/agent-03-single-generator-round3-2026-10-03/generator-single.json` після кожної вправи: actual attempts/history/errors, ID/name, full prompt/hash, catalog/style/reference SHA256, result paths/SHA256/time, файлові PNG/dimensions/реальна transparency checks. До PNG result_path/technical_check/user_review null; після PNG user_review=pending до явного рішення користувача, agent_visual_review=not_performed. Не проводити visual QA або автоматичні повтори.
7. Після кожного пакета commit/push власної гілки виконавця, verify remote файли й checkpoint у власному handoff. Shared progress, каталог/переклади, схвалення і Supabase не змінювати.
8. Перша quota/rate-limit помилка: зберегти failed call/history, push checkpoint і зупинитися без повторного виклику або іншого API. Недоступний image_gen — конкретний блокер. Після 036 зупинитися; blocked не брати.

## Непідготовлені та межі

З перевірених 54 непризначених кандидатів підготовлено 29; **25 потребують уточнення**, тому останній пакет має 9, а не вигадане тридцяте завдання. Разом equipment blocked ledger містить 36 = 11 попередніх + 25 нових: `data/audits/agent-03-single-generator-round3-2026-10-03-technique.json` → read_but_not_selected + blocked_source_records. Поза цим незмінні 10 раніше unresolved technical ID: `data/queues/agent-03-user-answers-2026-10-03-blocked.json`. Це підмножини власної черги, а не загальна кількість вправ без PNG у проєкті.

Основні питання: несумісний seated/standing/supine support; hip hinge versus knee flexion; assistance kneeling versus standing; напрям руху body versus handles; placement/contact loading pads; ambiguous cable hand/anchor. Для кожного blocked збережено exact raw поля та питання, без нового призначення. Чужі історичні failed jobs не забиралися. Немає вимоги шукати масово фотографії тренажерів.

Підготовку перевірено скриптом: `python scripts/prepare_agent03_single_generator_round3.py --fetch --check`, тільки на preparation branch до виконання. Це не команда продовження worker після появи PNG. Звіт: `data/audits/agent-03-single-generator-round3-2026-10-03-validation.json` — passed, 29 unique IDs, 3 batches, 1 generator, hashes/exact fields/overlaps/old routes/files checked. Старі пакети 001–033, каталог, shared progress, approvals і Supabase незмінні.
Звірено pushed Git-файли доступних гілок. Незапушені результати/активні виклики інших cloud задач можуть бути недоступні; live recheck виконавцем обов'язковий.

Готове повідомлення: `docs/agent-03-single-generator-round3-2026-10-03-message.md`.
