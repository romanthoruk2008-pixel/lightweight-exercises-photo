# Agent-03: наступні 30 «Інші» — пакети 004–006

Гілка `agent-03-inventory-2026-10-01`. Актуальний work: `fcc2cf3227cbe8e52932c0c56b7ca89018cd0a10`; agent-02: `2c27f90d8e2be0c1f349b81231897fd204d543b5`.

Каталог SHA256: `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. Стиль v1 SHA256: `8956307274990bdefd11bcc18e6d6deb2aed35580b5c2ea3ac0061dee708e578`.

001–003 (30 ID) передані першому агенту за повідомленням користувача. Їхні файли й prompts залишено байт-у-байт незмінними; усі їхні ID зарезервовані та виключені з нового добору.

Перевірено решту 97 ID через актуальні Git PNG, progress та всі batch/manifest/index/clarification файли work, agent-02 і власної гілки. Нових виключень: 0. Підготовлено наступні 30; без prompts залишається **67**.

У queue збережено історичні eligible_exercise_ids усіх відібраних вправ, first_launch_ids першої тридцятки, next_launch_ids нової тридцятки й окремий remaining_unprepared_ids. prepared_count=60 включає обидва раунди; це не кількість виконаних зображень.

Нові prompts обирають одну конкретну фазу й стандартні сумісні опори з англійського запису саме цього ID. У кожному batch — точні name, повний content.en, equipment, primary_muscle, secondary_muscles; SHA256 всього каталогу, запису, англійського блока й prompt. Текст каталогу не виправляли.

Планований PNG: `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png`. Це майбутній шлях, не наявний результат. attempts=0, result_path/result_sha256/user_review=null. Генерацію не запускали, візуального QA не було.

## agent-03-others-004

- `21s-biceps-curl-barbell` — 21s Bicep Curl
- `arnold-press-dumbbell` — Arnold Press (Dumbbell)
- `bent-over-row-barbell` — Bent Over Row (Barbell)
- `bent-over-row-dumbbell` — Bent Over Row (Dumbbell)
- `bulgarian-split-squat-barbell` — Bulgarian Split Squat (Barbell)
- `decline-bench-press-barbell` — Decline Bench Press (Barbell)
- `decline-bench-press-dumbbell` — Decline Bench Press (Dumbbell)
- `floor-press-barbell` — Floor Press (Barbell)
- `front-raise-barbell` — Front Raise (Barbell)
- `handstand-pushup` — Handstand Push Up

## agent-03-others-005

- `incline-bench-press-barbell` — Incline Bench Press (Barbell)
- `incline-bench-press-dumbbell` — Incline Bench Press (Dumbbell)
- `incline-chest-fly-dumbbell` — Incline Chest Fly (Dumbbell)
- `jm-press-barbell` — JM Press (Barbell)
- `lunge-barbell` — Lunge (Barbell)
- `overhead-dumbbell-lunge` — Overhead Dumbbell Lunge
- `overhead-press-barbell` — Overhead Press (Barbell)
- `partial-glute-bridge-barbell` — Partial Glute Bridge (Barbell)
- `pause-squat-barbell` — Pause Squat (Barbell)
- `pendlay-row-barbell` — Pendlay Row (Barbell)

## agent-03-others-006

- `pullover-dumbbell` — Pullover (Dumbbell)
- `push-press-barbell` — Push Press
- `renegade-row-dumbbell` — Renegade Row (Dumbbell)
- `reverse-grip-concentration-curl-dumbbell` — Reverse Grip Concentration Curl
- `reverse-lunge-barbell` — Reverse Lunge (Barbell)
- `seal-row-barbell` — Seal Row (Barbell)
- `seal-row-dumbbell` — Seal Row (Dumbbell)
- `seated-overhead-press-barbell` — Seated Overhead Press (Barbell)
- `seated-overhead-press-dumbbell` — Seated Overhead Press (Dumbbell)
- `seated-wrist-extension-barbell` — Seated Wrist Extension (Barbell)

## Повторна перевірка й передача

Read-only перевірка нового раунду (старий скрипт --check перевіряв лише початковий формат черги й після її оновлення не є валідатором цього раунду):

```bash
git fetch --no-tags origin '+refs/heads/work:refs/remotes/origin/work' '+refs/heads/agent-02-machines-001:refs/remotes/origin/agent-02-machines-001'
python scripts/prepare_agent03_other_followup.py --check
```

Звіт: [`data/queues/agent-03-other-next-validation.json`](../data/queues/agent-03-other-next-validation.json). Перевірено 451 унікальний catalog ID, 30 нових ID, точну відповідність полів, prompts/hash/PNG paths і відсутність перетинів. Негативні тести: 10; усі навмисні підміни/перетини відхилені.

Перед майбутнім дозволеним викликом fetch усі актуальні agent-гілки, звірити результати й призначення; новий конфлікт означає зупинити конкретний ID та повідомити. Незапушені файли й призначення інших хмарних задач можуть бути недоступні. Перевірка охоплює збережені Git-зрізи, не приховані локальні завдання.

Виконавцю брати запис та generation_prompt лише за exercise_id. Журнал зв’язує batch_id, exercise_id, source_catalog_sha256, source_catalog_record_sha256, generation_prompt_sha256, фактичний tool call, attempt і PNG SHA256/path. Зберегти саме output цього виклику під відповідним ID; не використовувати позицію масиву чи схожість назв. Хеші підтверджують походження файлів, не правильність зображеної техніки.

Reference тільки для зовнішності; зараз не відкривали, не шукали й не завантажували зовнішніх референсів. Подальша генерація лише за окремим дорученням, без автоматичних повторів/ресайзу, платного API чи Supabase.

## 105 уточнень

50 записів мають суперечність або недостатню конкретність техніки/обладнання. 55 мають primary_muscle=full_body/cardio/other без правила локальної підсвітки v1; це окреме питання стилю, не автоматичний дефект техніки. Усі лишаються виключеними; дані не змінено.

Точні проблемні поля, цитати, питання та приклади за категоріями й підтипами: [пояснення уточнень](agent-03-other-clarifications-explained.md). Початковий повний JSON 105 уточнень збережено без змін.

Каталог, спільний progress, інвентаризація, старі handoff/пакети/результати залишено незмінними. Роботу зупинено після підготовки й передачі.
