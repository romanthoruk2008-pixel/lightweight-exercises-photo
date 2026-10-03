# Схвалення PNG і перенесення Supabase — 2026-10-03

Найсвіжіший опублікований звіт імпортера містить **377 перенесених image links**, а не 77. Його checkpoint читання бази: `2026-10-03T13:36:34.707151+00:00`; commit `742c53007eb384141f0602d516f861ec691234a4` гілки `agent-04-supabase-integration`.

| Стан за перевіреними Git commits | Унікальних exercise_id |
| --- | ---: |
| PNG є, явно схвалено користувачем | 377 |
| PNG є, схвалення користувача немає | 21 |
| Активні, PNG немає | 50 |
| Архівні, зараз не генеруємо | 3 |
| Разом каталог | 451 |

Усі **398 ID із PNG** перевірено лише за файлами та записами Git, без visual QA. Сума 377 + 21 + 50 + 3 = 451; кілька версій одного ID не збільшують кількість вправ.

Незалежно звірено всі batch entries імпорту: 377 унікальних complete записів; accepted SHA256 збігається з записаним public file verification; exact ID і image_fields_equal підтверджені записаним database_verification. Повний список перенесених ID **дорівнює** повному списку явно схвалених; imported_not_approved = 0, approved_not_imported = 0. Це не нове завантаження або зміна Supabase.

## Виявлена помилка попереднього підрахунку

Попередній approval collector помилково пропускав усю папку `data/batches/`, разом із actual result manifests. Через це в ньому було 372 замість 377 і 26 замість 21 кандидатів переробки. Скрипт виправлено: actual `*-manifest.json` читаються, task batch JSON не трактуються як схвалення.

Ці 5 схвалених ID вилучені з revision queue:

- `swimming`
- `thruster-barbell`
- `thruster-kettlebell`
- `wall-ball`
- `warm-up`

Джерело: `agent-05-parallel-generation` @ `058e4810f858b5f0cca1d27384c8e36d525b24fa`, `data/batches/agent-03-others-023-agent-05-manifest.json`, exact `user_review=approved`. Старі схвалення й файли не змінено.

Окремо перед цим fresh generator push вилучив 9 нових approved ID з попередньої planning queue; їхні точні ID/джерела є в `data/audits/agent-03-common-variants-2026-10-03-approval-recheck.json`.

## Різні scope pending

Останній review list імпортера містить 12 pending. Загальний Git union містить ще 9 pending з `agent-02-machines-001`; разом 21. Це не 21 схвалене зображення й не нове призначення. Дев’ять інших pending:

- `hip-adduction-machine`
- `lat-pulldown-cable-machine`
- `lateral-raise-machine`
- `leg-extension-machine`
- `preacher-curl-machine`
- `pullover-machine`
- `rear-delt-reverse-fly-machine`
- `seated-cable-row-v-grip-cable-machine`
- `triceps-rope-pushdown-machine`

Для всіх дев’яти actual result manifest `data/batches/agent-02-machines-001-manifest.json` має `status=generated_needs_review`, `user_review=pending`, `technical_check=passed`. Наявний PNG не є user approval або Supabase upload.

## Захист від повторної генерації та межі

У нових пакетах 037–040 **34 tasks**, жодного перетину зі збереженими PNG, approved IDs чи чужими чинними призначеннями. Revision queue містить **21 planning-only** ID; їхні prompts ще треба перевірити, нових rework assignments немає. Any approved/accepted evidence захищає весь ID; перед кожним майбутнім call обов’язкова fresh перевірка всіх result/review manifests, включно з `data/batches/*-manifest.json`. Не видаляти старі PNG, не підміняти accepted hash і не змінювати review від імені користувача.

Власний live REST read заблокований cloud proxy CONNECT 403 до доступу до Supabase. Тому **377 у Supabase тут підтверджено за збереженим readback імпортера**, не моїм новим запитом до бази. Незапушені результати/рішення та подальші зміни можуть бути невидимі. Жодних Supabase записів, завантажень PNG із Supabase, imagegen calls або review changes не виконано.

Повні exact ID, commits, paths і докази: `data/audits/agent-03-common-variants-2026-10-03-supabase-reconciliation.json`; готові prompts/передача: `docs/agent-03-common-variants-2026-10-03-handoff.md`.

[Оригінальний completion імпортера](https://github.com/romanthoruk2008-pixel/lightweight-exercises-photo/blob/742c53007eb384141f0602d516f861ec691234a4/integration/supabase/uploads/continuation-2026-10-03-04/completion.json).
