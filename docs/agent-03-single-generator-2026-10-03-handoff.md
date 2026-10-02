# Передача 30 вправ одному генератору

Джерельна гілка: `agent-03-inventory-2026-10-01`. Коміт завдань: `599a31cd52cee8a34a19b1fb1bc7792438140c2d`.
Виконавець: **один `generator-single`**, власна гілка результатів `agent-08-generator-single-2026-10-03`. Підготовка не викликала генератор.

Виконувати строго **028 → 029 → 030**. Перші 10 — без спеціалізованих тренажерів; наступні 20 — обладнання в кінці. Чинні A: 024–025 і B: 009/026/027 та всі старі пакети залишені без змін. Нове призначення не забирає їхніх вправ.

Призначення: `data/assignments/agent-03-single-generator-2026-10-03.json`. Manifest: `data/manifests/agent-03-single-generator-2026-10-03/generator-single.json`. Перевірка: `data/audits/agent-03-single-generator-2026-10-03-validation.json` — passed, 30 унікальних ID, 451 запис і 4448 мовних блоків каталогу збережено.

| Порядок | Статус | Кількість | Точний файл |
| --- | --- | --- | --- |
| 1 | ready | 10 | `data/batches/agent-03-others-028.json` |
| 2 | ready | 10 | `data/batches/agent-03-others-029.json` |
| 3 | ready | 10 | `data/batches/agent-03-others-030.json` |

## agent-03-others-028

| exercise_id | Назва з точного запису каталогу |
| --- | --- |
| `floor-triceps-dip` | Floor Triceps Dip |
| `chest-dip-weighted-machine` | Chest Dip (Weighted) |
| `drag-curl-barbell` | Drag Curl |
| `feet-up-bench-press-barbell` | Feet Up Bench Press (Barbell) |
| `hammer-curl-band-resistance-band` | Hammer Curl (Band) |
| `hip-thrust-barbell` | Hip Thrust (Barbell) |
| `landmine-180-barbell` | Landmine 180 |
| `lying-neck-extension` | Lying Neck Extension |
| `lying-neck-extension-weighted-plate` | Lying Neck Extension (Weighted) |
| `seated-incline-curl-dumbbell` | Seated Incline Curl (Dumbbell) |

## agent-03-others-029

| exercise_id | Назва з точного запису каталогу |
| --- | --- |
| `biceps-curl-machine` | Bicep Curl (Machine) |
| `chinup-assisted-machine` | Chin Up (Assisted) |
| `incline-chest-press-machine` | Incline Chest Press (Machine) |
| `iso-lateral-chest-press-machine` | Iso-Lateral Chest Press (Machine) |
| `iso-lateral-high-row-machine` | Iso-Lateral High Row (Machine) |
| `seated-row-machine` | Seated Row (Machine) |
| `shoulder-press-machine-plates` | Shoulder Press (Machine Plates) |
| `t-bar-row-machine` | T Bar Row |
| `triceps-dip-assisted-machine` | Triceps Dip (Assisted) |
| `single-leg-extensions-machine` | Single Leg Extensions |

## agent-03-others-030

| exercise_id | Назва з точного запису каталогу |
| --- | --- |
| `standing-leg-curls-machine` | Standing Leg Curls |
| `chest-press-machine` | Chest Press (Machine) |
| `air-bike-machine` | Air Bike |
| `recumbent-bike-machine` | Recumbent Bike |
| `rowing-machine` | Rowing Machine |
| `spinning-machine` | Spinning |
| `stair-machine-floors` | Stair Machine (Floors) |
| `stair-machine-steps` | Stair Machine (Steps) |
| `treadmill-machine` | Treadmill |
| `inverted-row-machine` | Inverted Row |

## Джерела, стиль і сцени

Єдине джерело вихідних полів: `data/exercises/catalog.json`, SHA256 `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. Lookup лише за точним ID; raw source_english, equipment, primary_muscle і secondary_muscles у кожному завданні збережені дослівно. Додаткові мови не змінені.
Еталон людини: `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Лише зовнішність, пропорції та матеріали; перед першою генерацією виконавець має відкрити еталон. Не копіювати позу, гантелі або підсвітку еталона.
Файли стилю: `docs/exercise-image-style.md` (v1) і `docs/exercise-image-style-neutral-primary.md` (v1-neutral-primary-2026-10-02). Файл і SHA256 для відповідного стилю записані в кожному завданні. Одна людина, одна фаза, прозорий PNG 1024×1024; манекен сріблясто-сірий, лисий, чорні шорти, barefoot за чинними правилами. Нічого не додавати до затверджених винятків щодо взуття.
Для 7 cardio-записів тіло нейтральне без підсвітки: конкретних secondary_muscles у них немає. Це затверджене правило, не пропущена розмітка. ID: `air-bike-machine`, `recumbent-bike-machine`, `rowing-machine`, `spinning-machine`, `stair-machine-floors`, `stair-machine-steps`, `treadmill-machine`.
Точне зіставлення з working-manifest і dataset: `data/audits/agent-03-single-generator-2026-10-03-technique.json`. Dataset перевірений за source.dataset_id, а механіка — за реальними instructions/supports/grip/motion. Ні збіг назви, ні збіг ID самі по собі не були достатнім підтвердженням. Архів медіа і фото не завантажувалися; PNG візуально не перевірялися.
028: вихідні готові prompts з `data/queues/agent-03-user-answers-2026-10-03-prepared.json` збережені byte-for-byte, перебіндовано лише заплановані шляхи та призначення. Старий файл є історичним staging, а актуальна маршрутизація — у черзі та новому призначенні.
Виявлені помилкові поля збережені у `data/audits/agent-03-single-generator-2026-10-03-source-errors.json`: barbell/лежача сцена для chest-press-machine, hips-on-pad для assisted triceps dip, elbow cues/mistakes для single-leg leg extension. Англійський raw текст не виправлений. Render за selected_render_scene і документованим technique_resolution, не за помилковим шаблоном.
Для chest-press-machine користувач обрав сидячий важільний тренажер зі спинкою; grip/motion підтверджує саме dataset 0576. Для inverted-row-machine обрано нерухомий гриф Сміта на висоті пояса; хват і рух підтверджує саме dataset 0499. Гриф у цій вправі не рухається по напрямних. Для решти конструкції сумісні з точними описами, без вигаданого бренду чи числового навантаження.

## Виконання й зберігання

1. Працювати лише в наявному хмарному checkout. Fetch джерельну гілку, work і всі доступні гілки агентів. Створити власну гілку результатів від актуальної джерельної гілки; не reset чужу гілку, не merge і не push у work або підготовчу гілку.
2. Звірити hashes призначення, пакетів, каталогу та стилю з комітом `599a31cd52cee8a34a19b1fb1bc7792438140c2d`. Перед кожним викликом перевіряти точний ID та вихідні поля. `python scripts/prepare_agent03_single_generator.py --check --fetch` — перевірка ПІДГОТОВКИ на її власній гілці до старту; після генерації вона закономірно виявляє PNG і не є командою продовження.
3. Перед КОЖНИМ викликом звірити локальні результати, manifest, progress лише читанням і Git-дерева актуальних доступних remote-гілок. Будь-який PNG цього ID, включно з pending, або нове чинне призначення іншому агенту означає skip, записавши branch/commit/path і причину. Невдалий виклик без PNG — не готовий результат; попередні чужі failed задачі залишаються у їхніх пакетах.
4. Використовувати тільки вбудований image_gen, повний generation_prompt конкретного ID і його еталон людини. Не генерувати колажі/кілька вправ за один виклик. Не змінювати prompt, техніку або підсвітку здогадками.
5. Результат кожного ID зберігати точно у planned_png_path (`/workspace/exercise-image-results/agent-03-single-generator-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`), копію в planned_git_png_path (`assets/exercises/pending/agent-03-single-generator-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`). Вузькі allowlist-правила .gitignore уже підготовлено для цих 30 шляхів; не додавати широких винятків.
6. Після КОЖНОЇ вправи оновлювати тільки власний manifest `data/manifests/agent-03-single-generator-2026-10-03/generator-single.json`: фактичний attempt, повний prompt/hash, style/reference/catalog SHA256, cloud/Git path/result SHA256, час і помилки. На збережений результат — user_review=pending до явного рішення користувача; technical_check незалежний, agent_visual_review=not_performed. За потреби провести лише файлову перевірку PNG, розміру і прозорості; не робити повторного аудиту вже готових чужих PNG.
7. Після КОЖНОГО пакета зробити commit і push тільки власної гілки результатів, перевірити remote-файли, зафіксувати checkpoint у власному handoff; потім перейти до наступного пакета. Shared progress, каталог/переклади, схвалення, чужі manifest і Supabase не змінювати.
8. При першій помилці квоти/ліміту image_gen записати невдалий attempt, помилку й next attempt, зберегти/push checkpoint і зупинитися. Не робити повторних викликів, автоматичних виправлень або обходу через платний API. Якщо інструмент недоступний — зупинитися, а не міняти спосіб генерації.
9. Після 030 зупинитися й передати користувачу результати/помилки та skipped ID. Не брати нові пакети, не перегенеровувати готові PNG, не затверджувати власні результати.

## Межі та відкладені записи

10 попередніх питань техніки залишаються blocked у `data/queues/agent-03-user-answers-2026-10-03-blocked.json`; не включені до нових пакетів. Додатково прочитані, але не відібрані суперечливі machine-записи перелічені в evidence.read_but_not_selected. Решту обладнання не передано одним масовим завданням.
Звірено всі доступні опубліковані Git-гілки; точні commit наведено у validation.live_commits. Незапушені результати й виклики інших хмарних задач можуть бути недоступні. Тому перевірка генератора перед кожним викликом обов’язкова.

Готове повідомлення для копіювання: `docs/agent-03-single-generator-2026-10-03-message.md`.
