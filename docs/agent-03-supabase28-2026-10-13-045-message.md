# Повідомлення генератору — пакет 045

Користувач копіює це повідомлення обраному генератору. Підготовчий агент генерацію не запускав і доручення сам не надсилав.

```text
Виконай тільки пакет agent-03-others-045, 10 вправ, у своєму поточному хмарному workspace та своїй виконавчій гілці. Не змінюй чужі гілки та не скидай свої поточні задачі.

Джерельна гілка: agent-03-inventory-2026-10-01.
Незмінний коміт завдань: 7f88ab32d296d4d73be9a9e6430bb9c8aa1256a6.
Точний файл: data/batches/agent-03-others-045.json.
Повний handoff: docs/agent-03-supabase28-2026-10-13-handoff.md.
Registry призначень: data/assignments/agent-03-supabase28-2026-10-13.json.
Окремий manifest: data/manifests/agent-03-supabase28-2026-10-13/agent-03-others-045.json.

Це 28 НОВИХ ID з Supabase, яких немає в старому catalog.json із 451 вправою. Єдине джерело для цих ID — data/exercises/supabase-additions-2026-10-13.json з указаного commit; SHA256 907950559a5bf4be84a791deb73fcd03d502a48ec8b936296df8a3e42651bf0f. Експорт походить із agent-04-supabase-integration, commit f64538a37d63f7512527ab2a57cb195645a4a354. Використовуй source_record і весь source_english саме цього exercise_id; не зіставляй за назвою, не змінюй каталог або його переклади.

Вправи цього пакета, у точному порядку:
1. dragon-flag-negative — Dragon Flag (Negative)
2. handstand-pushup-negative — Handstand Push Up (Negative)
3. l-sit-hold-tuck — L-Sit Hold (Tuck)
4. parallel-bar-support-hold — Parallel Bar Support Hold
5. flexed-arm-hang — Flexed-Arm Hang
6. front-lever-hold-tuck — Front Lever Hold (Tuck)
7. front-lever-hold-advanced-tuck — Front Lever Hold (Advanced Tuck)
8. front-lever-hold-one-leg — Front Lever Hold (One Leg)
9. front-lever-hold-straddle — Front Lever Hold (Straddle)
10. skin-the-cat — Skin the Cat

Перед початком запиши свою гілку як execution_owner для цього пакета у копії окремого registry своєї гілки. Одного пакета не можуть одночасно виконувати два агенти. Перед КОЖНИМ викликом звір актуальні доступні гілки, PNG, manifests, approvals, assignments і свої локальні результати. Будь-який наявний PNG, включно з pending, або чужий активний owner — пропусти ID й повідом. Approved/accepted захищає весь ID. Не забирай чужі поточні завдання. Якщо раніше виклик цього пакета вже був невдалим без PNG, збережи його історію в цьому ж manifest, не створюй дублікат.

Передай інструменту повний непорожній exercises[].generation_prompt, перевіривши prompt_sha256. Не передавай замість тексту лише ID чи шлях. Поля scene конкретно визначають фазу, позу, хват, опори, обладнання, траєкторію й ракурс. Equipment=machine тут не означає силовий тренажер: читай точні описи статичного турніка/брусів. Equipment=none не скасовує опор, указаних в instructions.

Еталон: assets/exercises/biceps-curl-dumbbell.png; SHA256 52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f. Використовуй його лише для зовнішності, пропорцій і матеріалів, не для пози, обладнання чи підсвітки. Стиль: docs/exercise-image-style.md; для primary=full_body/cardio/other також docs/exercise-image-style-neutral-primary.md. Конкретний primary підсвічується #F26445 повною інтенсивністю, exact secondary — 40–50%. Для full_body/cardio/other primary нейтральний, лише exact secondary отримує 40–50%; порожній secondary — без підсвітки. Не додавай м’язів від себе.

Лише вбудований image_gen: одна людина, одна фаза, прозорий PNG 1024×1024. Зберігай файли за exact planned_png_path і planned_git_png_path кожного запису. Корені цього пакета:
/workspace/exercise-image-results/agent-03-supabase28-2026-10-13/agent-03-others-045/<exercise_id>/attempt-1.png
assets/exercises/pending/agent-03-supabase28-2026-10-13/agent-03-others-045/<exercise_id>/attempt-1.png
Підставляй тільки вихідний exercise_id, не створюй ID з назви. Якщо PNG ignored, у своїй гілці додай лише вузькі .gitignore винятки для exact planned_git_png_path цього пакета, без глобального дозволу всіх PNG.

Збережи фактичний prompt/hash, source record/hash, reference/style, спроби, помилки й PNG path/SHA256 у вказаному окремому manifest. Уже початий manifest не перезаписуй порожнім шаблоном. Нові результати: user_review=pending до мого явного схвалення, agent_visual_review=not_performed. Проведи лише файлові перевірки; без візуального QA, автоматичних виправлень, ресайзу чи автоматичних повторів.

Після пакета закоміть і запуш лише свою виконавчу гілку, звір віддалені файли та покажи результати користувачу. При першій помилці квоти/rate limit запиши помилку, збережи й запуш checkpoint та зупинись без повторних викликів або стороннього API. Не змінюй original catalog.json, export, shared progress, схвалення, інші пакети або Supabase. Після цього пакета зупинись.
```
