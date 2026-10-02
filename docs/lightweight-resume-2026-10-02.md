# Lightweight — відновлення хмарної задачі, підготовка 010–015

Перевірено 2026-10-02T13:56:07.321243+03:00. **Генерацію не запускати: чекати окремої команди користувача.** Викликів imagegen: 0. Supabase не використовувався.

## Середовище й джерела

- Runtime provider=cloud, observed_phase=running, connectivity=connected, failure=null. Термінал працює; вбудований image_gen.imagegen доступний, квоту не перевіряли викликом.
- Команди виконуються в /workspace/lightweight-exercises-photo, hostname 256b990d161c. systemd-detect-virt: container-other; mounts: Kata Containers overlay та tmpfs. Монтувань Mac або зовнішніх дисків ноутбука не виявлено; /Users, /Volumes, /System/Volumes/Data, /host, /host_mnt і Desktop/Downloads/Documents контейнера відсутні. /mnt та /media існують без окремих монтувань. Висновок стосується доступу цього завдання, не всіх завантажень на Mac.
- Працювати тільки в цьому cloud workspace й наявному checkout; не створювати worktree, не підключатися до ноутбука, не читати особисті файли/секрети.
- Авторитетне джерело каталогу, статусів і PNG — work `a6f296cbc6737991dd367e929b3e2df25874d4d8`; main не використовувати.
- Підготовча гілка agent-03-inventory-2026-10-01, commit `d0e7bede47d8f21165015e74b00c58dafcadbe82`, джерельний handoff docs/agent-03-other-completion-handoff.md. Перенесено лише 22 явно перелічені підготовчі файли/залежності, без merge гілки й без заміни shared progress.
- Звірені інші гілки: agent-02-machines-001 `2c27f90d8e2be0c1f349b81231897fd204d543b5`; agent-04-supabase-integration `68e9f7a30666d4fa6f83aa48717311f8876f2021`. Читалися Git tree/JSON-метадані; API Supabase не викликався.
- Прочитано AGENTS.md, style/workflow/handoff, workflow progress, каталог і потрібні manifests. Історичні правила пілоту не замінюють поточний прямий запит користувача.

## Незмінні джерела й еталон

- Каталог: 451 ID, 448 активних, 3 архівні, 4448 мовних блоків. SHA256 `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. ID, описи, переклади та історію не змінювати; старі 48 PNG не використовувати.
- Shared progress із work збережено байт-у-байт: SHA256 `3804ed233776c64aa3dbf9e0676ee893a7c274be0222367e2001ef6b740a251c`. Числа 451/135/21 зі старої Supabase-задачі не є актуальною чергою.
- Стиль v1, docs/exercise-image-style.md, SHA256 `8956307274990bdefd11bcc18e6d6deb2aed35580b5c2ea3ac0061dee708e578`.
- Еталон assets/exercises/biceps-curl-dumbbell.png; accepted SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Збігається з поточним progress, approved manifest, підготовчими пакетами й completion handoff; іншого погодженого еталона не виявлено.
- Еталон відкрито через view_image, пікселі доступні. PNG/RGBA 1254×1254, 1263295 повністю прозорих пікселів. Це прийнятий оригінал; не ресайзити під ціль 1024×1024. Роль: зовнішність, пропорції, матеріали та деталізація дорослої анатомічної людини (не маскот Сережа), без перенесення biceps-curl пози, гантелей чи підсвітки.
- Перед кожним майбутнім викликом передавати цей локальний файл як referenced_image_paths; у новій задачі перевірити SHA256 і відкрити його знову.

## Точна черга

Окрема актуальна черга й доказ перевірки: data/queues/agent-03-resume-2026-10-02.json. Усі 53 ID мають not_started/attempts=0; для них не знайдено наявних PNG, pending/rejected/needs_fix результатів або чужих призначень у доступних refs. Каталожні English/equipment/muscles, record/English/prompt/style/reference hashes, конкретні сцени й supplemental evidence того самого ID перевірені оригінальним валідатором як бібліотекою. CLI історичного prepare --check на work не запускався: він має guard власної підготовчої гілки.

| Пакет і точний файл | Залишок | ID у порядку виконання |
| --- | ---: | --- |
| `data/batches/agent-03-others-010.json` | 10 | `low-row-suspension`, `pullup-band-resistance-band`, `pullup-machine`, `ring-pushup`, `scapular-pull-ups`, `squat-suspension`, `sternum-pullup-gironda-machine`, `toes-to-bar`, `triceps-dip-machine`, `triceps-dip-weighted-machine` |
| `data/batches/agent-03-others-011.json` | 10 | `triceps-extension-suspension`, `wide-pullup-machine`, `box-squat-barbell-hevy-3338464331414239`, `gorilla-row-kettlebell`, `kettlebell-around-the-world`, `kettlebell-curl`, `kettlebell-goblet-squat`, `kettlebell-shoulder-press`, `landmine-row-barbell`, `lateral-box-jump` |
| `data/batches/agent-03-others-012.json` | 10 | `lying-neck-curls-weighted-plate`, `meadows-rows-barbell`, `overhead-plate-raise`, `plate-curl`, `plate-front-raise`, `plate-press`, `preacher-curl-barbell`, `preacher-curl-dumbbell`, `rack-pull-barbell`, `russian-twist-weighted-plate` |
| `data/batches/agent-03-others-013.json` | 7 | `single-leg-standing-calf-raise-dumbbell`, `sissy-squat-weighted`, `situp-weighted`, `step-up`, `sumo-squat-kettlebell`, `walking-lunge-sandbag`, `wrist-roller-machine` |
| `data/batches/agent-03-others-014.json` | 10 | `around-the-world-dumbbell`, `bench-press-close-grip-barbell`, `bench-press-wide-grip-barbell`, `box-jump`, `chest-fly-band-resistance-band`, `chest-fly-suspension`, `crunch-weighted`, `decline-chest-fly-dumbbell`, `decline-crunch-weighted`, `dumbbell-squeeze-press` |
| `data/batches/agent-03-others-015.json` | 6 | `dumbbell-step-up`, `ez-bar-biceps-curl-barbell`, `frog-jumps`, `full-squat-barbell`, `glute-bridge-barbell`, `hex-press-dumbbell` |

**Разом: 53 = 10 + 10 + 10 + 7 + 10 + 6.** Перший ID: low-row-suspension. Жоден із 010–015 не викликався.

Поза цим запуском: 89 blocked із data/queues/agent-03-other-blocked.json та дев’ять недороблених 009: `hanging-knee-raise`, `hanging-leg-raise`, `jack-knife-suspension`, `kipping-pullup-machine`, `knee-raise-parallel-bars-machine`, `kneeling-pulldown-band-machine`, `lat-pulldown-band-resistance-band`, `lateral-band-walks-resistance-band`, `lateral-raise-band-resistance-band`. Їхні статуси/attempts не змінені.

Для повторної read-only перевірки після fetch актуальної work й доступних agent-гілок: `python3 scripts/check_agent03_resume.py`. Не використовувати --prepare і не перезаписувати історичні reports. Нові непушені PNG/броні інших задач недоступні; перед кожним викликом перечитувати актуальні progress/results/assignments і пропускати вже зайняті ID.

## Правила після окремої команди на генерацію

- Тільки вбудований image_gen.imagegen, по одному окремому PNG на точний exercise_id, пакети 010→015 послідовно. Без платного API, додавання нових вправ, другої людини чи кількох фаз. Турнік/бруси/лави/стрічки/вільні ваги визначаються технікою; machine у суфіксі не означає тренажер. Спеціалізовані машини, троси й Сміт не додавати.
- Брати готовий generation_prompt exact-ID запису та його незмінні source_english description/instructions/form_cues/common_mistakes, equipment, primary_muscle, secondary_muscles. Не переписувати prompt без конкретної причини; справжні суперечності фіксувати за ID, не вигадувати техніку. Погоджені supplemental поля вже прив’язані до того самого ID, English не замінений перекладом.
- Одна доросла об’ємна 3D-анатомічна модель; непрозоре тіло; основні м’язи #F26445, допоміжні той самий відтінок 40–50% інтенсивності; справжня прозорість, квадратний PNG, ціль 1024×1024, повністю видимі людина й потрібне обладнання. Без тексту, UI, рамок, логотипів, світіння та декору.
- Дотримуватися scene.pose/grip/supports_and_equipment/single_phase/camera. Контакти рук/стоп із опорами фізично узгоджені, правильні кількість/місце снарядів і анкери, цілісний гриф; без зайвих кінцівок, дублів, злиття тіла з обладнанням і предметів без опори. Текст не гарантує візуальної якості; остаточний перегляд робить користувач.
- **Поточний шлях користувача замінює старий planned_png_path/output_root та outputs_outside_git із підготовчих файлів:** assets/exercises/pending/<batch_id>/<exercise_id>/attempt-1.png. Оригінальні batch/prompts залишені незмінними; фактичні шляхи зафіксовано в окремій resume queue. Не перезаписувати зайняті шляхи й не створювати дубль автоматично.
- Після кожного результату одразу зберігати PNG та ID, повний фактичний prompt і hash, style v1, reference SHA256, шлях/SHA256/розміри, tool-call identity і номер спроби. user_review=pending, agent_visual_review=not_performed. Read-only технічна перевірка: PNG signature/успішне декодування, квадратність, прозорі пікселі, SHA256 і прив’язка до ID/шляху. Невідповідність → needs_fix; без автоматичних crop/resize/повторів або детального агентського візуального QA.
- approved/uploaded, наявний pending PNG, rejected/needs_fix без окремої команди на корекцію та чужі активні призначення пропускати. Відсутність approved-файла не дозволяє генерувати заміну.
- Після кожного пакета: checkpoint, commit і push лише PNG/метаданих цього пакета в work; перед push fetch актуальної work і збереження чужих змін. Без reset --hard/force push. .gitignore ігнорує pending PNG: за цим прямим дозволом користувача додавати лише конкретні нові PNG, не змінювати ignore для всієї бібліотеки. Перевіряти remote наявність і SHA256 лише доданих файлів, без повного повторного аудиту бібліотеки.
- HTTP 429: зберегти й push уже готового, записати точний ID/спробу продовження в handoff і зупинитися. Без нескінченних повторів. Іншу помилку окремої вправи записати; якщо інструмент працює, продовжити наступну.

## Блокування й межі

Конкретних блокувань підготовки немає. Квота генератора не перевірена і попередній HTTP 429 не вважається автоматично усуненим. Непушені чужі файли недоступні. Supabase не є залежністю й секретів не потребуємо. Зараз лише підготовка: не генерувати; чекати команди користувача. Shared progress, каталог, старі PNG та статуси збережені.


## Пакет 010 — локальний checkpoint перед push

2026-10-02: 10/10 PNG збережено окремо, технічні перевірки PNG/decode/square/transparency/ID/SHA256 пройшли; всі user_review=pending та agent_visual_review=not_performed. Під час інструментальної підготовки вісім запитів не містили prompt і були відхилені до генерації; вони не рахуються спробами й не витратили квоту. Після виправлення викликано точні batch prompts; остаточні valid tool-call indices: 1, 2, 11–18. Віддалену перевірку ще не проводили. Наступна дія: fetch актуальної work, push PNG+progress+manifest, перевірити всі 10 remote SHA256, відмітити github_verified і зафіксувати цей стан.

Пакет 010 завершено й перевірено: 10/10 PNG у `work`, remote SHA256 кожного збігається з локальним файлом, progress і manifest. Content/verified commit: `8f61dedac47ec814a183a69508e10f05fb63f0fb` (`2026-10-02T11:24:07.853615+00:00`). Усі результати лишаються `user_review=pending`, `agent_visual_review=not_performed`; технічні перевірки пройшли. Продовження: пакет 011, перший ID `triceps-extension-suspension`.

## Пакет 010 — чотири точкові корекції за запитом користувача

2026-10-02: після завершення й push пакета 010 користувач замовив окремі правки. Використано вбудований image_gen.imagegen; для кожної edit-вправи передано її attempt-1 та погоджений еталон людини/стилю `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Attempt-1 лишили незмінними. У всіх 4 нових файлів PNG декодується, квадратний формат 1254×1254, RGBA з прозорими пікселями, SHA256/ID/path записані в shared progress і `data/batches/agent-03-others-manifest.json`; `technical_check=passed`, `user_review=pending`, `agent_visual_review=not_performed`.

| ID | Новий файл | SHA256 | Запитана правка |
| --- | --- | --- | --- |
| `scapular-pull-ups` | `assets/exercises/pending/agent-03-others-010/scapular-pull-ups/attempt-2.png` | `61247ed96a77b0107d7b18265d1341c034a3c6e33f0f9811c8a1328f015a328c` | Рівна горизонтальна перекладина, міцні рівні кріплення, легка додаткова підсвітка біцепсів. |
| `sternum-pullup-gironda-machine` | `assets/exercises/pending/agent-03-others-010/sternum-pullup-gironda-machine/attempt-2.png` | `f7899d3fead2f1a745ba711de619cf934d9177a7ba4ff9eaf97d48b94e169828` | Рівна горизонтальна перекладина та узгоджені кріплення. |
| `triceps-dip-machine` | `assets/exercises/pending/agent-03-others-010/triceps-dip-machine/attempt-2.png` | `6d8afacd9e2cbe5cc0331cbed50b80fad3e431fcc29ae5b4e632fd32e0b00064` | Груди й плечі — активний #F26445 на повній інтенсивності за прямим уточненням користувача. |
| `triceps-dip-weighted-machine` | `assets/exercises/pending/agent-03-others-010/triceps-dip-weighted-machine/attempt-2.png` | `47148b6bb149951a53192d35e62a494fd3750d2fa3d3c1c88233b742c8525f42` | Груди й плечі — активний #F26445 на повній інтенсивності за прямим уточненням користувача. |

До push: зробити fetch актуальної `work`, push чотири нові PNG, metadata й цей checkpoint без force push, перевірити remote SHA256 лише цих чотирьох файлів та записати `github_verified`. Після цього зупинитися й чекати перегляду/нової команди; пакет 011 не запускати.

Remote checkpoint: four attempt-2 corrections were pushed to `work` at commit `9b90a1aaedf462baf40bf8c188a4c9ec144cafc6`. SHA256 was read from the remote Git blobs and matched the local PNG and progress/manifest for each ID. `backup_status=github_verified`; all remain `user_review=pending`, with no visual QA. Next action: wait for user review/instruction; keep package 011 paused.

2026-10-02: користувач схвалив чотири корекції attempt-2 пакета 010. Рішення, accepted path/SHA256/attempt і user review history записані у shared progress та manifest; перевірений backup у `work` збережено. Продовжити пакетами 011→015 послідовно. Нові зображення залишати `user_review=pending`; показ пакета не є схваленням.


Package 011 локально завершено 2026-10-02T12:09:10.099225+00:00: 10/10 PNG, технічні помилки 0. `user_review=pending`, `agent_visual_review=not_performed`. Наступне: push і remote SHA256 checkpoint, потім package 012.

Package 011: push and remote verification completed at commit `56501c890d54273add7f6fa49947f74a9da8f6ab` (10/10 remote SHA256 matched). User review remains pending; continue to package 012.
