# Останні 13 user-selected варіантів: передача одному генератору

**13 ready tasks, 10 + 3**, тільки підготовка, generation calls=0. Один existing виконавець: `agent-08-generator-single-2026-10-03`. Source branch: `agent-03-inventory-2026-10-01`; immutable task commit: `5fc5fba256adf609384953004c9b096604ab6002`.
Після чинних 037–040 та раніше взятих завдань. Старі 001–040, manifests/PNG/history, A/B/agent-02 призначення і revision planning queue незмінні.

## Пакети й exact ID

### agent-03-others-041 — ready, 10

Файл: `data/batches/agent-03-others-041.json`; порядок: 1.

| exercise_id | Точна name з каталогу |
| --- | --- |
| `waiter-curl-dumbbell` | Waiter Curl (Dumbbell) |
| `single-leg-standing-calf-raise-barbell` | Single Leg Standing Calf Raise (Barbell) |
| `press-under-barbell` | Press Under |
| `back-extension-machine` | Back Extension (Machine) |
| `seated-dip-machine` | Seated Dip Machine |
| `seated-triceps-press-machine` | Seated Triceps Press |
| `shrug-machine` | Shrug (Machine) |
| `belt-squat-machine` | Belt Squat (Machine) |
| `rear-kick-machine` | Rear Kick (Machine) |
| `single-leg-standing-calf-raise-machine` | Single Leg Standing Calf Raise (Machine) |

### agent-03-others-042 — ready, 3

Файл: `data/batches/agent-03-others-042.json`; порядок: 2.

| exercise_id | Точна name з каталогу |
| --- | --- |
| `bench-press-cable-machine` | Bench Press (Cable) |
| `reverse-fly-single-arm-cable-machine` | Reverse Fly Single Arm (Cable) |
| `squat-row-machine` | Squat Row |

## Рішення та вихідні суперечності

Повний незмінний user-provided текст «Вставлений текст.txt»: `docs/agent-03-final13-user-variants-2026-10-03-source.txt`, SHA256 `752aa941dcf4b69794b06a9c608f62a16f6f0c7e00d09eda3ec831b63304368e`. Exact ID/номер пункту/повний paragraph → selected scene: `data/technique-decisions/agent-03-final13-user-variants-2026-10-03.json`.
Це user_selected_illustration_variant. Мітки chatgpt-content-reference не містять URL: незалежне зовнішнє підтвердження не заявляється, бренди у вставці не роблять наш unbranded апарат підтвердженою моделлю виробника. Це також не схвалення PNG.
У рендері конкретна user-selected scene має пріоритет над суперечливими raw pose/equipment instructions. Raw English лишається походженням, а не дозволом змішувати старий і вибраний варіанти. Каталог — єдине джерело exact ID/name/English/equipment category/primary/secondary; не підміняти його іншою вправою.
Журнал exact conflicting fields та raw English: `data/audits/agent-03-final13-user-variants-2026-10-03-catalogue-conflicts.json`. Exact dataset binding і actual instruction_steps: `data/audits/agent-03-final13-user-variants-2026-10-03-technique.json`. Matching name/ID саме по собі не підтверджує техніку. Каталог не виправляли.

Критичні вибори: Waiter — одна вертикальна dumbbell на двох долонях під верхнім head; Press Under — behind neck/широкий grip/quarter squat, не front-chest/full/split; Back Extension — seated rear-pad lever, не Roman chair; belt squat — belt/chain/carabiner вниз між ногами до under-platform lever anchor, plates на lever horns; rear kick — standing sole-to-moving-footplate; reverse fly — tower зліва, RIGHT/FAR працює, LEFT/NEAR підтримує; seated dip/triceps press — body/seat fixed, handles DOWN; shrug — standing plate-loaded, neutral handles/straight arms/vertical shoulders; barbell single calf — дві руки на FREE bar і одна forefoot на fixed step, без handhold; machine single calf — dedicated shoulder pads, не Smith; squat row — LOW pulley/rope/neutral grip і row В ПРИСІДІ, руки випрямити в присіді, потім встати.
Для barbell calf raw floor/handhold safety текст збережено як розбіжність; light/empty bar та пасивні nearby safety arms — ілюстраційний вибір. Для machine calf selectorized load — обраний із дозволених користувачем варіантів, без числової ваги або підтвердженого бренду. Не додавати нового clinical/training advice.

## Стиль, еталон та джерельні хеші

Каталог `data/exercises/catalog.json` незмінний: 451 ID, 4448 мовних блоків, 3 архівні; SHA256 `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. Кожен task містить весь exact English, equipment/muscles того самого ID, hashes каталогу/record/English/prompt, конкретні pose/phase/grip/supports/trajectory/camera і planned cloud/Git PNG paths.
Еталон appearance/materials ONLY: `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`; відкрити перед першим call. Позу/обладнання/підсвітку не копіювати.
Стиль `docs/exercise-image-style.md` (v1) + approved `docs/exercise-image-style-neutral-primary.md` (v1-neutral-primary-2026-10-02), рішення `data/style-decisions/agent-03-neutral-primary-approved.json`. Сріблясто-сіра лиса анатомічна чоловіча модель, чорні шорти, barefoot, прозорий 1024×1024, одна людина/фаза, весь figure/equipment, без UI/text/arrows.
Конкретний catalog primary — #F26445, тільки конкретні catalog secondary — 40–50%. **press-under-barbell і squat-row-machine: full_body + secondary=[]; обидва повністю нейтральні БЕЗ підсвітки.** Не додавати muscles із зовнішніх джерел, не фарбувати equipment/pads і не показувати muscles через opaque material. Style/reference hashes у tasks.

## Продовження одним генератором

Новий registry: `data/assignments/agent-03-final13-user-variants-2026-10-03.json`; окремий NEW manifest: `data/manifests/agent-03-final13-user-variants-2026-10-03/generator-single.json`.
1. Fetch актуальні work/preparation та доступні agent branches. Продовжувати existing worker branch, не reset/recreate; зберегти попередні PNG/attempts/errors/history. Пуш лише worker branch.
2. Прочитати актуальний handoff; із task commit `5fc5fba256adf609384953004c9b096604ab6002` перенести тільки 041–042/new assignment/source text/decisions/evidence/conflict ledger і NEW manifest. Якщо manifest уже почато, не замінювати стартовим. Не копіювати поверх каталог, shared progress, стару чергу, всю .gitignore, старі/чужі manifests або results.
3. Перед КОЖНИМ call перечитати свіжі PNG/явні approvals/assignments усіх доступних гілок, включно actual `data/batches/*-manifest.json`, власні local outputs/history. ANY approved/accepted evidence захищає ВЕСЬ ID: skip навіть при іншій pending копії або відсутньому accepted файлі. Для цих нових missing-PNG tasks будь-який existing PNG включно pending — skip; чуже чинне призначення — skip. Записувати branch/commit/path/reason. Старий failed без PNG лишається у старому job.
4. Після раніше взятих tasks виконати 041 → 042, тільки exact generation_prompt/user-selected scene/style/reference. Не змішувати raw contradictory English у pose. Лише вбудований image_gen; без automatic retries/visual QA.
5. Cloud: `/workspace/exercise-image-results/agent-03-final13-user-variants-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`; Git: `assets/exercises/pending/agent-03-final13-user-variants-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`. Exact paths у tasks. За потреби додати лише 13 exact allowlist рядків; не замінювати весь .gitignore, не перезаписувати жоден PNG або attempt/history.
6. Оновлювати тільки `data/manifests/agent-03-final13-user-variants-2026-10-03/generator-single.json` після кожної вправи: full prompt/hash, actual attempts/history/errors, catalog/style/reference hashes, result path/SHA256/time. До PNG user_review/result null; після PNG user_review=pending до явного рішення користувача, agent_visual_review=not_performed. Лише file/size/реальна transparency checks.
7. Commit/push worker branch після кожного пакета, verify remote PNG/manifest і checkpoint handoff. Каталог/переклади, shared progress, схвалення, старі PNG та Supabase не змінювати.
8. Перша quota/rate-limit помилка: записати failed/history, push checkpoint і STOP без повторного call/іншого API. Після 042 STOP і показати PNG/skips/errors. Revision planning queue не виконувати.

## Залишок та перевірка

Усі 13 fresh-check активні, без PNG/approval/foreign assignment. Current unresolved illustration ledger порожній: `data/queues/agent-03-final13-user-variants-2026-10-03-blocked.json`. Historical blocked reports збережено; catalogue contradictions лишаються в окремому журналі, не змінюючи source records.
Три older jobs не перепризначено: treadmill-machine (030, agent-08), reverse-grip-lat-pulldown-cable-machine (032, agent-08), leg-press-horizontal-machine (agent-02-machines-001, agent-02). Ця передача не дозволяє забрати їхні ID або повторити чужі failed calls; актуальний стан перед продовженням перевіряє власник.
Межа — pushed Git metadata; непушені approvals/results/live calls можуть бути недоступні. Не виконували imagegen, pixel QA, пошук/завантаження зовнішніх фотографій або Supabase audit.
Preparation check до виконання: `python scripts/prepare_agent03_final13_user_variants.py --fetch`; звіт `data/audits/agent-03-final13-user-variants-2026-10-03-validation.json`: passed, 13 unique/10+3, exact fields/hashes/paragraphs/scene/overlaps і старі frozen files/routes. Це не worker continuation command після появи PNG.
Готове повідомлення: `docs/agent-03-final13-user-variants-2026-10-03-message.md`.
