# Agent-03: раунд 3 — пакети 007–009, тільки підготовка

Власна гілка `agent-03-inventory-2026-10-01`. Work `11eea90c1b4201c50539f5b944f21db963a41db4`. Інші перевірені commits: `{"origin/work": "11eea90c1b4201c50539f5b944f21db963a41db4", "origin/agent-02-machines-001": "2c27f90d8e2be0c1f349b81231897fd204d543b5", "HEAD": "47f772a7824e2377f4454efe2e7365bcb2fec0b1"}`.

Каталог SHA256 `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. Стиль v1 SHA256 `8956307274990bdefd11bcc18e6d6deb2aed35580b5c2ea3ac0061dee708e578`.

У вхідній черзі 67 ID. Після актуальної перевірки виключено 0. Підготовлено **30** вправ у пакетах по максимум 10; **37** залишаються без prompts. Нестача до 30: 0.

Усі 60 ID пакетів 001–006 зарезервовані й не включені повторно. У work вже збережено PNG для 60 з цих ID; це зафіксовано окремо у queue Git-зрізі. Власні файли 001–006 збережено байт-у-байт. Каталог, shared progress, старі handoff, manifests і результати не змінено.

Відбір: тільки active inventory group other, без PNG, спроб, поданого pending/rejected/approved результату, іншого batch/manifest/index/clarification призначення або невирішеного уточнення. Untouched not_started/attempts=0 без output/history і з legacy default pending не є поданим результатом; це правило попередньої інвентаризації.

Категорію machine не трактувати як точну конструкцію. chest-dip/chinup/kipping-pullup/knee-raise-parallel-bars задають статичні перекладини/бруси; kneeling-pulldown-band задає еластичну стрічку на верхньому анкері. Їхні вихідні equipment та ID збережено; prompts не додають ваговий стек, блоки, троси або Сміт. Тренажери/блокові станції/Сміт і всі невирішені уточнення лишаються поза пакетами.

## agent-03-others-007 — 10

- `single-arm-triceps-extension-dumbbell` — Single Arm Tricep Extension (Dumbbell)
- `single-leg-hip-thrust-dumbbell` — Single Leg Hip Thrust (Dumbbell)
- `single-leg-romanian-deadlift-barbell` — Single Leg Romanian Deadlift (Barbell)
- `skullcrusher-barbell` — Skullcrusher (Barbell)
- `skullcrusher-dumbbell` — Skullcrusher (Dumbbell)
- `spider-curl-barbell` — Spider Curl (Barbell)
- `squat-barbell` — Squat (Barbell)
- `standing-calf-raise-barbell` — Standing Calf Raise (Barbell)
- `standing-military-press-barbell` — Standing Military Press (Barbell)
- `straight-leg-deadlift-barbell` — Straight Leg Deadlift

## agent-03-others-008 — 10

- `sumo-deadlift-barbell` — Sumo Deadlift
- `sumo-squat-barbell` — Sumo Squat (Barbell)
- `upright-row-barbell` — Upright Row (Barbell)
- `wide-elbow-triceps-press-dumbbell` — Wide-Elbow Triceps Press (Dumbbell)
- `zercher-squat-barbell` — Zercher Squat
- `band-pullaparts-resistance-band` — Band Pullaparts
- `chest-dip-machine` — Chest Dip
- `chinup-machine` — Chin Up
- `chinup-weighted-machine` — Chin Up (Weighted)
- `clamshell-resistance-band` — Clamshell

## agent-03-others-009 — 10

- `dead-hang` — Dead Hang
- `hanging-knee-raise` — Hanging Knee Raise
- `hanging-leg-raise` — Hanging Leg Raise
- `jack-knife-suspension` — Jack Knife (Suspension)
- `kipping-pullup-machine` — Kipping Pull Up
- `knee-raise-parallel-bars-machine` — Knee Raise Parallel Bars
- `kneeling-pulldown-band-machine` — Kneeling Pulldown (band)
- `lat-pulldown-band-resistance-band` — Lat Pulldown (Band)
- `lateral-band-walks-resistance-band` — Lateral Band Walks
- `lateral-raise-band-resistance-band` — Lateral Raise (Band)

## ID → каталог → prompt → PNG

Дані вправ тільки з catalog.json. Повний запис отримано exact-ID словником, не за назвою чи позицією масиву. У кожному batch збережено точні name, весь content.en (description, instructions, form_cues, common_mistakes, safety_note, provenance), equipment, primary_muscle, secondary_muscles; SHA256 каталогу, запису, en-блока й generation_prompt. Prompt payload містить ті самі поля, конкретну одну фазу та цитати instructions цього ID.

Планований шлях `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png`; це не наявний PNG. attempts=0, result_path/result_sha256/user_review/technical_check=null. generation_authorized_now=false. Генерацію та візуальний QA не запускали.

Перед майбутнім виконанням отримати всі актуальні agent-гілки та work, звірити PNG/призначення. Нова невідповідність або суперечність → виключити конкретний ID і повідомити, не підставляти сусідній запис. Виклик/вихідний файл пов’язувати з exact exercise_id, batch_id, source_catalog_sha256, source_catalog_record_sha256, generation_prompt_sha256, фактичним attempt та tool-call identity; записати PNG SHA256 і фактичний шлях. Не асоціювати outputs за порядком повернення або схожістю назв.

## Перевірка

Звіт [`data/queues/agent-03-other-round3-validation.json`](../data/queues/agent-03-other-round3-validation.json): 451 унікальний catalog ID, 30 нових ID, 60 захищених попередніх ID, відповідність полів/prompt/hash/PNG, відсутність перетинів, 12 негативних контрольних випадків. Власні черга та packages мають історичні prepared_count/eligible_exercise_ids; вільний залишок визначає тільки remaining_unprepared_ids. latest_launch_ids — раунд 3; first_launch_ids і next_launch_ids залишені як історичні раунди 1 і 2.

Read-only перевірка після fetch:

```bash
git fetch --no-tags origin '+refs/heads/work:refs/remotes/origin/work' '+refs/heads/agent-02-machines-001:refs/remotes/origin/agent-02-machines-001'
python scripts/prepare_agent03_other_round3.py --check
```

Якщо з’явились інші віддалені agent-гілки, спочатку fetch їх у refs/remotes/origin; валідатор сканує всі fetched agent-гілки. Попередні скрипти --check є історичними валідаторами своїх раундів, не поточного формату черги.

Межа: незапушені файли/призначення інших хмарних задач можуть бути недоступні. Поточна перевірка охоплює збережені Git-зрізи. References не шукали/не завантажували/не відкривали для візуального QA. Хеші та provenance не доводять візуальної правильності майбутньої картинки.

Працювати лише в хмарному checkout. Після окремого дозволу на генерацію — тільки вбудований image_gen, без автоматичних повторів/ресайзу, платного API, Supabase або змін shared progress. На цьому етапі зупинитися після підготовки, commit, push і віддаленої звірки.

Початковий commit джерела для підготовлених пакетів: `988f7d8ab38ccdc5ad16c30cf215e1d0952605ef`. Кінцева перевірка перед commit: work `11eea90c1b4201c50539f5b944f21db963a41db4`; каталог/style незмінні. Усі 30 нових ID й 37 решти пройшли актуальну перевірку. Початковий зріз та кінцеву перевірку збережено окремо в queue/validation.
