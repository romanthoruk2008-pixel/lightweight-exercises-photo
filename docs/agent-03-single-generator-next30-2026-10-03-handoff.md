# Наступні 30 вправ для одного генератора

Джерельна гілка: `agent-03-inventory-2026-10-01`. Коміт завдань: `77cd54d73b1f2546d29e7f17bd816faf9ec14f5e`.
Той самий єдиний виконавець `generator-single`, гілка результатів `agent-08-generator-single-2026-10-03`. Це нове призначення лише для **031 → 032 → 033**. Старі пакети, призначення й manifests залишені незмінними.

| Порядок | Статус | Кількість | Склад | Точний файл |
| --- | --- | --- | --- | --- |
| 1 | ready | 10 | 4 спеціалізовані + 6 тросових | `data/batches/agent-03-others-031.json` |
| 2 | ready | 10 | 10 тросових | `data/batches/agent-03-others-032.json` |
| 3 | ready | 10 | 1 тросова + 9 Сміт | `data/batches/agent-03-others-033.json` |

Призначення: `data/assignments/agent-03-single-generator-next30-2026-10-03.json`. Новий окремий manifest: `data/manifests/agent-03-single-generator-next30-2026-10-03/generator-single.json`. Попередній manifest для 028–030 не перезаписувати.
Факт підготовки не означає PNG або схвалення. attempts=0, user_review=null до появи результату; після появи — pending до явного рішення користувача. Генерацію підготовчий агент не запускав.

## Точний перелік

### agent-03-others-031

| exercise_id | Назва з каталогу |
| --- | --- |
| `standing-calf-raise-machine` | Standing Calf Raise (Machine) |
| `lat-pulldown-machine` | Lat Pulldown (Machine) |
| `vertical-traction-machine` | Vertical Traction (Machine) |
| `torso-rotation-machine` | Torso Rotation |
| `biceps-curl-cable-machine` | Bicep Curl (Cable) |
| `hammer-curl-cable-machine` | Hammer Curl (Cable) |
| `rope-cable-curl-machine` | Rope Cable Curl |
| `triceps-pressdown-machine` | Triceps Pressdown |
| `triceps-pushdown-machine` | Triceps Pushdown |
| `reverse-grip-triceps-pushdown-machine` | Reverse Grip Triceps Pushdown |

### agent-03-others-032

| exercise_id | Назва з каталогу |
| --- | --- |
| `straight-arm-lat-pulldown-cable-machine` | Straight Arm Lat Pulldown (Cable) |
| `reverse-grip-lat-pulldown-cable-machine` | Reverse Grip Lat Pulldown (Cable) |
| `low-cable-fly-crossovers-machine` | Low Cable Fly Crossovers |
| `seated-cable-row-bar-grip-machine` | Seated Cable Row - Bar Grip |
| `seated-cable-row-bar-wide-grip-machine` | Seated Cable Row - Bar Wide Grip |
| `face-pull-machine` | Face Pull |
| `standing-y-raise-cable-machine` | Standing Y Raise (Cable) |
| `cable-core-pallof-press-machine` | Cable Core Pallof Press |
| `cable-pull-through-machine` | Cable Pull Through |
| `single-arm-cable-crossover-machine` | Single Arm Cable Crossover |

### agent-03-others-033

| exercise_id | Назва з каталогу |
| --- | --- |
| `seated-chest-flys-cable-machine` | Seated Chest Flys (Cable) |
| `bench-press-smith-machine` | Bench Press (Smith Machine) |
| `bent-over-row-smith-machine` | Bent Over Row (Smith Machine) |
| `deadlift-smith-machine` | Deadlift (Smith Machine) |
| `incline-bench-press-smith-machine` | Incline Bench Press (Smith Machine) |
| `overhead-press-smith-machine` | Overhead Press (Smith Machine) |
| `romanian-deadlift-smith-machine` | Romanian Deadlift (Smith Machine) |
| `shrug-smith-machine` | Shrug (Smith Machine) |
| `squat-smith-machine` | Squat (Smith Machine) |
| `standing-calf-raise-smith-machine` | Standing Calf Raise (Smith) |

## Джерела й підсвітка

Вихідний каталог: `data/exercises/catalog.json`, SHA256 `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. 451 унікальний ID, 4448 мовних блоків, без змін. Весь English description/instructions/form_cues/common_mistakes/safety та equipment/muscles витягнуто за точним ID і збережено verbatim у кожному завданні. Не використовувати схожі назви або позицію в масиві.
Джерела технічних рішень: `data/audits/agent-03-single-generator-next30-2026-10-03-technique.json`. Там точні selected dataset IDs, original instruction_steps, прив’язки до working-manifest, source hashes і selected scenes. Фактичні рухи, хват та опори перевірено за текстами, не тільки за назвами/ID. Жодних фотографій/відео не завантажували; зовнішні muscle lists не імпортовано.
lat-pulldown-machine і vertical-traction-machine — важільні reverse-grip станції за equipment та інструкціями dataset 0673. Тросові вправи мають визначені висоту блоку/насадки/контакти за своїми текстами. Smith-вправи мають гриф, механічно зв’язаний із напрямними, відповідну опору та конкретну фазу.
Повторення одного dataset ID для різних catalog ID збережені як окремі вправи: hammer-curl / rope-cable-curl; pressdown / pushdown; lat-pulldown / vertical-traction. М’язи беруться окремо з кожного точного catalog ID, навіть якщо сцени схожі.
Еталон: `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Лише зовнішність/матеріали/пропорції; перед першою генерацією його пікселі мають бути доступні виконавцю. Не переносити позу, гантелі чи підсвітку.
Стиль усіх 30 — v1 (`docs/exercise-image-style.md`): одна сріблясто-сіра лиса анатомічна чоловіча модель, чорні шорти, barefoot, одна фаза, повний figure/equipment, прозорий PNG 1024×1024. Усі 30 мають конкретний primary_muscle і відповідну підсвітку #F26445; тільки secondary точного ID — той самий колір на 40–50%. Порожній secondary — без допоміжної підсвітки. Затверджене `docs/exercise-image-style-neutral-primary.md` зберігається, але ці 30 не мають generic primary.
Вибір сцени відокремлений від підтвердження техніки: стоячий curl — допустимий варіант, прямо дозволений English і підтверджений dataset; 30° incline — вибір ілюстрації в дозволеному джерелом діапазоні 30–45°; сторона й одна фаза — ілюстративні рішення. Жодне з них не записано як нове схвалення користувачем.
Помилки/умовні поля: `data/audits/agent-03-single-generator-next30-2026-10-03-source-errors.json`. Dataset squat містить free-bar walk-out boilerplate, що несумісний зі Смітом; scene виконує точні English Smith-squat instructions без такого кроку. У seated cable rows обрано явно дозволений upright варіант; загальне chest-pad поле не додає відсутню опору. Каталог і dataset-тексти не виправлялися.

## Виконання та передача

1. Працювати лише в поточному хмарному workspace і на власній гілці `agent-08-generator-single-2026-10-03`. Вона вже існує: не reset/recreate її від підготовчої гілки та не втрачати старі результати/спроби. Fetch source/work/усі доступні гілки агентів. Не merge чужі гілки й не push у work або підготовчу гілку.
2. Перенести тільки нові пакети/призначення/evidence/new manifest із `77cd54d73b1f2546d29e7f17bd816faf9ec14f5e` через читання Git blobs або вузьке відновлення точних нових файлів. Якщо власний новий manifest уже містить спроби — не перезаписувати його початковим файлом. Не копіювати поверх старого shared progress, каталогу, 028–030 чи попереднього manifest. Еталон і стиль звірити за SHA256.
3. Перед КОЖНИМ викликом звіряти PNG у всіх доступних актуальних remote-гілках і власних локальних папках, manifests/progress читанням та нові чинні призначення. Будь-який PNG точного ID, включно з pending, або нове чуже призначення — skip із точним branch/commit/path/reason. Старі failed без PNG залишаються у своєму попередньому пакеті, не переносити їх у новий.
4. Використовувати повний generation_prompt саме цього ID та його human reference. Тільки вбудований image_gen, по одній вправі/одній фазі/одній людині. Не додавати насадки, muscle targets, бренд, числове навантаження чи техніку з іншої схожої вправи.
5. Точні результати: planned_png_path = `/workspace/exercise-image-results/agent-03-single-generator-next30-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`; planned_git_png_path = `assets/exercises/pending/agent-03-single-generator-next30-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`. .gitignore підготовчої гілки містить точні 30 allowlist-рядків. На гілці виконавця за потреби додати лише ці точні рядки зі збереженням чинних правил; широких винятків не робити.
6. Власний новий manifest `data/manifests/agent-03-single-generator-next30-2026-10-03/generator-single.json` оновлювати після КОЖНОЇ вправи: actual attempt/history, повний prompt/hash, ID/catalog/style/reference SHA256, cloud/Git result path/SHA256, час, помилки. Після результату user_review=pending, agent_visual_review=not_performed; технічний статус окремо. Файлові перевірки розміру/PNG/прозорості дозволені; візуальний QA і автоматичні повтори не запускати.
7. Після КОЖНОГО пакета commit/push тільки власної гілки результатів, перевірити remote файли, записати checkpoint у власний handoff. Каталог/переклади, shared progress, чужі manifests, схвалення PNG та Supabase не змінювати.
8. Перша помилка квоти/ліміту: зберегти failed attempt, історію та помилку; push checkpoint і зупинитися без повторних викликів. Не обходити через платний API. Недоступний image_gen — блокер, не привід змінювати спосіб.
9. Після 033 зупинитися й показати результати, skips та помилки. Наступні невизначені/заблоковані вправи не брати самостійно.

## Блокування та межі

10 раніше невирішених ID лишаються в `data/queues/agent-03-user-answers-2026-10-03-blocked.json`. Ще 11 відкладених записів: `data/audits/agent-03-single-generator-next30-2026-10-03-technique.json` → read_but_not_selected і blocked_source_records; черга містить current_equipment_blocked_ids/path. Вони не ready й не мають нового призначення. Для кожного збережені точні raw поля та причина конфлікту.
Скрипт перевірки підготовки на її власній гілці: `python scripts/prepare_agent03_single_generator_followup.py --fetch --check`. Він перевіряє ID/джерела/хеші/повтори/PNG і збереження старих файлів. Це не команда продовження на гілці виконавця після генерації. Результат перевірки: `data/audits/agent-03-single-generator-next30-2026-10-03-validation.json`.
Звірено опубліковані Git-файли всіх доступних агентських гілок. Незапушені результати й незавершені виклики інших cloud задач можуть бути недоступні; живі перевірки виконавця перед кожним викликом обов’язкові.

Готове повідомлення: `docs/agent-03-single-generator-next30-2026-10-03-message.md`.
