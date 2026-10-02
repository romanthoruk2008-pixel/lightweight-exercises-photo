# Agent-03: опрацювання 89 blocked записів

Власна гілка `agent-03-inventory-2026-10-01`; підготовка без генерації. Дата 2026-10-02T15:47:08.155282+03:00.

Актуальний work snapshot `6924e3d9dc2cad59de83d523903c2933e5bdad8a`. Каталог SHA256 `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. Чинний стиль v1 SHA256 `8956307274990bdefd11bcc18e6d6deb2aed35580b5c2ea3ac0061dee708e578`.

**22 ready** із 34 технічних; **12 blocked** із конкретними варіантами. **55 awaiting_style_decision**; із них 45 повних conditional prompts і 10 templates без вигадування відсутнього руху/спорядження. Ні approved, ні generation/attempt не додано.

## Нові ready пакети

| Пакет | Статус | Кількість | Точний файл |
| --- | --- | ---: | --- |
| agent-03-others-016 | ready | 10 | `data/batches/agent-03-others-016.json` |
| agent-03-others-017 | ready | 10 | `data/batches/agent-03-others-017.json` |
| agent-03-others-018 | ready | 2 | `data/batches/agent-03-others-018.json` |
| Власні style drafts (не generation пакет) | awaiting_style_decision | 55 | `data/queues/agent-03-neutral-primary-style-drafts.json` |
| Технічні питання (не generation пакет) | blocked | 12 | `data/queues/agent-03-blocked-research.json` |

Пакети 001–015 незмінні; 010–015 вже передані генератору. Їхні 143 ID збережено зарезервованими, включно з failed/noPNG продовженням 009. Нові файли не скидають жодної попередньої спроби. Live PNG перевірено лише за Git paths і manifests/призначеннями; повторного технічного/візуального аудиту зображень не було.

## Самодостатність і джерела

Кожен ready запис містить exact exercise_id/name, повний незмінний source_english (description/instructions/form_cues/common_mistakes/safety/provenance), equipment/primary/secondary, catalog/record/English hashes, phase/pose/grip/supports/trajectory/camera, повний prompt і його SHA256, embedded evidence/URL/quotes, style v1/hash, human reference/path/hash та planned PNG path із тим самим ID.

Еталон: `/workspace/lightweight-exercises-photo/assets/exercises/biceps-curl-dumbbell.png`; repo path `assets/exercises/biceps-curl-dumbbell.png`; SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Роль лише зовнішність/пропорції/матеріали. Нове вкладення в чаті не використано як техніку/обладнання/підсвітку; його локальних байтів/SHA не надано, тому самодостатній пакет посилається на чинний accepted reference, не вигаданий attachment path.

Результати плануються поза Git: `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png`. У style drafts є окремий planned staging path з exact ID; після рішення стилю формувати окремі нові пакети й явно зафіксувати остаточний шлях/manifest перед викликом. Draft не запускати напряму.

Original archive прочитано HTTP ranges лише для working-manifest.json і dataset.json. Manifest SHA256 збігається з каталогом; dataset_commit збігається. Selected dataset records приєднані ВИКЛЮЧНО через source.dataset_id exact ID, із звіркою того самого selected candidate у verified manifest. Generated/null-source записи не отримували схожий кандидат. Whole 411MB media archive не завантажено/не хешовано; whole archive hash НЕ позначено перевіреним.

Точні джерела, quotes та обмеження: `data/audits/agent-03-blocked-source-evidence.json`. Первинні матеріали TRX, CrossFit, Rogue прочитано як текст, без завантаження фото/відео. Не використано коментарі користувачів як інструкції. Не підмінялися half-kneeling landmine, dumbbell hammer curl або vest carrier там, де вони мають інші опори/обладнання.

Для вирішених помилок raw English лишається дослівним provenance, а prompt явно надає пріоритет resolved scene та його same-ID/source-variant evidence. Каталог не виправлено. Зокрема Trap Bar має зафіксовану помилку source 0811, але виробник конкретно визначає inside-frame neutral handles; Clap — source 1273 wider hands; Dragonfly — власний pl/match описує shoulder-supported abdominals, а не generic chest fly.

## Нерозв’язані технічні питання

- `chest-dip-weighted-machine`: Паралельні бруси з English instructions чи одна пряма перекладина з назви dataset 3313? Пояс із ланцюгом можливий для обтяження, але не вирішує суперечність опор.
- `drag-curl-barbell`: Потрібен drag curl із ліктями назад і грифом уздовж тулуба чи звичайний curl з нерухомими верхніми руками, як у dataset 0038?
- `feet-up-bench-press-barbell`: Стопи у повітрі зі зігнутими колінами (pl/it) чи поставлені на лаву (es)? English feet planted також збережено як суперечність; звичайним жимом ID не підміняти.
- `hammer-curl-band-resistance-band`: Який саме band hammer curl: центр стрічки під стопами з двома нейтральними ручками чи низький зовнішній анкер? Знайдені regular/seated curls не є підтвердженням цього варіанта.
- `hip-thrust-barbell`: Верхня спина на краю лави, таз поза лавою, чи lying hip lift із тулубом на лаві й підйомом таза з неї, як у 0058? Потрібна одна геометрія опор.
- `landmine-180-barbell`: Повна дуга від одного стегна до іншого чи right hip → left shoulder із вихідного 0562? Уточніть кінцеві точки та напрямок обох повторів.
- `lying-neck-extension-weighted-plate`: Лежачи животом на лаві з головою за краєм (тоді head supported потребує пояснення) чи інша лежача орієнтація з рухомою опорою голови? Укажіть опору та доступний діапазон.
- `nordic-hamstrings-curls`: Фіксувати щиколотки під нерухомою рейкою/валиком у стійці чи ременем до нерухомої опори? Потрібна однозначна конструкція без другої людини й спеціалізованого тренажера.
- `pushup-weighted`: Зберігаємо млинець на верхній спині — тоді який перевірений фіксатор для однієї людини — чи дозволено ваговий жилет/плитний носій? Виробник описує carrier, але це не доказ способу утримання круглого вільного млинця.
- `side-bend-dumbbell`: Нахил до руки з гантеллю, коли вага опускається, чи від неї, коли вага піднімається? Dataset 0407 повторює суперечливе away + lowering.
- `single-arm-landmine-press-barbell`: Стоячий split-stance press вільного кінця без спинки чи окремий supported варіант зі спинкою? У всіх блоках переплутано anchored/free end і додано back-pad cues; half-kneeling приклад виробника має інші опори й відхилений.
- `single-leg-standing-calf-raise-barbell`: Обидві руки утримують вільний гриф без ручної опори чи одна рука на грифі, друга на визначеній опорі? English safety handhold/machine support не задає спосіб одночасного утримання; Smith не додавати.

## Стиль — окреме рішення

Пропозиція `docs/agent-03-neutral-primary-style-proposal.md` з одним списком усіх **60 ID** (55 власних + 5 чужих): broad primary нейтральний; лише explicit concrete secondary на 40–50% #F26445. Тільки kettlebell-high-pull має traps, решта 59 secondary пусті. Стиль НЕ затверджено, чинний style документ не змінено.

Foreign IDs лише у груповому списку: downward-dog, bear-crawl, jumping-jack, high-knees, mountain-climber. Чужі prompts/пакети/результати не змінено й їх не перепризначено.

Окремі additional questions для 10 власних style IDs (рішення кольору їх не усуває):

- `clean-barbell`: Яка глибина приймання Clean: повний присід чи partial/power? Match відкидає power як іншу глибину, але soft knees/elbows under не задають приймання. Уточніть також лікті вперед у front rack.
- `hiit`: Який конкретний bodyweight рух показувати в робочому HIIT інтервалі? Ходьба в source є лише відновленням; оберіть рух або окрему ілюстрацію відновлення.
- `hiking`: Для Hiking з вимогою suitable footwear дозволити сумісне взуття чи окремо погодити анатомічну ілюстрацію босоніж? Нейтральне фарбування не змінює barefoot v1.
- `muscle-up-machine`: Зберігати overhand bar muscle-up з переходом кистей над баром чи справді змінювати хват на supinated, як у instructions[2]? Визначте також повну press-to-support фазу, яку instructions пропускають.
- `pilates`: Який конкретний Pilates рух/позу показувати? Selected Pilates movement не визначено; не підставляти Hundred, Roll-Up чи іншу вправу самостійно.
- `press-under-barbell`: Яке receiving положення Press Under: частковий присід, повний присід чи інше? Start chest/finish overhead задані, але рух тіла під грифом і опори ніг не визначені.
- `snowboarding`: Погодити snowboard boots/сумісні кріплення й захисне спорядження, чи потрібен окремо визначений тренувальний barefoot варіант? Наявний текст вимагає secured feet/protective gear.
- `stretching`: Яку конкретну ділянку і stretch-позу показувати? Chosen muscle group/position відсутні; основну групу чи позу не вигадувати.
- `walking`: Для Walking з appropriate footwear дозволити сумісне взуття чи окремо погодити анатомічну ілюстрацію босоніж? Потрібне одне рішення разом із Hiking/Snowboarding.
- `yoga`: Яку конкретну Yoga позу/перехід показувати? Planned poses не задані; standing/kneeling setup не підміняє визначену асану.

## Перевірка та наступна передача

Валідатор `data/queues/agent-03-blocked-validation.json`: 10 навмисних підмін відхилено; exact-ID поля/source binding, prompt/hash/path, відсутність старих/чужих/PNG перетинів і незмінність protected файлів перевірено. Queue історичні prepared/eligible містять старі 143 ID; нові actionable ready IDs — queue.blocked_preparation.new_ready_ids; awaiting_style_decision_ids не є ready.

```bash
git fetch origin '+refs/heads/work:refs/remotes/origin/work' '+refs/heads/agent-02-machines-001:refs/remotes/origin/agent-02-machines-001' '+refs/heads/agent-04-supabase-integration:refs/remotes/origin/agent-04-supabase-integration'
python scripts/prepare_agent03_blocked_records.py --check
```

Додаткові agent-гілки fetch перед check; --prepare не повторювати. Старі checker scripts є історичними й не перевіряють новий формат queue. Якщо з’явився PNG/нове призначення, НЕ запускати відповідний ID. Непушені файли інших cloud задач можуть бути недоступні; це межа перевірки.

Для майбутнього окремо дозволеного запуску журнал має зв’язувати batch_id, exact exercise_id, catalog/record/prompt/reference/style hashes, фактичний виклик/attempt та PNG path/SHA. Не зіставляти отримані файли за назвами/позицією. Hash provenance не є візуальним QA.

work/shared progress/каталог/style v1/Supabase/схвалення не змінені. Генерація не виконувалася. Пропозицію доступу до первинних доменів збережено через cloud-environment-onboarding:setup як draft; saving не означає застосування runtime-політики. Частина додаткових першоджерел усе ще повертає 403; це не дозвіл підбирати альтернативу навмання.
