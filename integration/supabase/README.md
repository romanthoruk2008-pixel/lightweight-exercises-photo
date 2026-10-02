# Supabase integration preparation — agent-04

Початкова підготовка збережена в `dry_run.py`, audit і results. Після
окремого дозволу користувача додано `import_catalog_images.py` для
відновлюваного імпорту. Локальні source JSON, PNG, progress і схвалення
не змінюються; imagegen, міграцій і змін користувацьких таблиць немає.

Гілка: `agent-04-supabase-integration`; база: `work` на
`a6f296cbc6737991dd367e929b3e2df25874d4d8`. Використовувати існуючий cloud
checkout; не створювати worktree та не використовувати Mac користувача.

## Файли

- `import_authorization.md` — точна область дозволеного імпорту.
- `import_catalog_images.py` — dry-run за замовчуванням; авторизовані
  записи з `--apply`, read-only перевірка Supabase з `--verify-only`.
- `uploads/catalog_manifest.json` — insert batches та повне читання назад.
- `uploads/batch-001.json` — gate перших трьох; наступні batch-файли — по
  десять (останній може бути меншим), результати Storage/public hash/DB.
- `uploads/completion.json` — підсумкова перевірка, межі клієнтського доступу.
- `handoff.md` — актуальний стан імпорту і наступні дії.
- `audit.md` — результати та межі перевірки.
- `field_mapping.md` — відповідність полів і послідовність майбутнього імпорту.
- `verify_schema.sql` — лише SELECT для підтвердження count/default/CHECK/RLS.
- `sql_editor_evidence.json` — надані користувачем SQL результати: count=0
  без RLS, JSONB NOT NULL DEFAULT '[]'::jsonb і всі 8 CHECK definitions.
- `dry_run.py` — перевірка прийнятих байтів і read-only API audit.
- `inspect_source_archive.py` — відтворювана перевірка оригінального manifest
  через HTTPS byte ranges; не завантажує весь ZIP і не витягує медіа/інструменти.
- `source_archive_inspection.json` — результат; manifest SHA256 перевірений,
  повний ZIP SHA256 не перевірявся.
- `results/approved_png_plan.json` — 135 точних ID, source paths, accepted
  SHA256, фактичні PNG-перевірки, destination paths і відповідні DB records.
- `results/catalog_import_plan.json` — 451 ID, hashes незмінних мовних JSON
  і чернетка 451 insert record. `replaces_ids`/`updated_at` пропущені для
  server defaults; п'ять image-полів спочатку NULL. Це не дозвіл на запис.
- `results/access_audit.json` — схема та результати доступу без секретів і
  без збереження користувацьких записів.
- `results/summary.json` — підсумок перевірки й конкретні блокування.

## Відтворення у cloud workspace

Потрібні Python 3.10+ і Pillow 12.3.0; вони вже доступні в перевіреному
середовищі. Якщо Pillow відсутній, створити venv поза checkout і встановити
`requirements.txt`, не змінюючи manifests або lockfiles репозиторію:

```sh
cd /workspace/lightweight-exercises-photo
python3 -m venv /workspace/lightweight-integration-venv
/workspace/lightweight-integration-venv/bin/python -m pip install -r integration/supabase/requirements.txt
```

Результати побудовано з pinned source commit. Після checkout власної гілки
всі source JSON і PNG мають залишатися доступними та незмінними. Скрипт
перевіряє вихідні JSON проти Git commit і SHA256 кожного прийнятого PNG.

```sh
cd /workspace/lightweight-exercises-photo
PYTHONDONTWRITEBYTECODE=1 python3 integration/supabase/dry_run.py --offline
PYTHONDONTWRITEBYTECODE=1 python3 integration/supabase/dry_run.py --output-dir integration/supabase/results
PYTHONDONTWRITEBYTECODE=1 python3 integration/supabase/inspect_source_archive.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s integration/supabase -p 'test_*.py' -v
```

Варіант без `--output-dir` тільки читає та друкує summary. `--output-dir`
явно оновлює лише чотири підготовчі JSON у `integration/supabase`; це локальні
робочі файли, а не зміни Supabase. Скрипт не друкує всі записи в чат/термінал.

`dry_run.py` і `results` — зафіксована підготовка до дозволу на імпорт,
включно з тодішніми блокуваннями. Для поточного стану/відновлення
використовувати `import_catalog_images.py` і `uploads`, а не трактувати
історичний summary як результат фактичного імпорту.

## Авторизований імпорт і відновлення

```sh
cd /workspace/lightweight-exercises-photo
PYTHONDONTWRITEBYTECODE=1 python3 integration/supabase/import_catalog_images.py
PYTHONDONTWRITEBYTECODE=1 python3 integration/supabase/import_catalog_images.py --apply
PYTHONDONTWRITEBYTECODE=1 python3 integration/supabase/import_catalog_images.py --verify-only
```

Без flags виконується лише preflight read і звірка локальних hashes.
`--apply` перечитує каталог, відмовляється від конфліктів і вставляє лише
відсутні записи з `missing=default,return=minimal`, без upsert і без
replaces_ids. Image uploads мають `x-upsert=false`. PATCH змінює лише
п'ять image-полів з умовами точного ID, old image fields і updated_at.
Публічний GET без apikey/Authorization повинен пройти до PATCH.

Кожний успішний PNG має checkpoint. Повторний запуск для complete entries
перевіряє public bytes і DB, але не повторює upload/PATCH. Невизначений
результат після мережевого переривання відновлюється читанням фактичного
object/row, не сліпим повтором запису. Конфлікт object/hash або DB link
зупиняє роботу. `--verify-only` не має дозволених Supabase mutations;
локальний completion report може оновитися. Код 0 — перевірку завершено,
1 — зупинка/помилка; dry-run повертає 2 при конфлікті.

Read-only API потребує наявної прив'язки `exerciseuploader` та HTTPS proxy.
Секрет використовується лише у `apikey` до проєкту Supabase. Не виводити
його, не записувати у файли, не передавати у Git або фронтенд. Не обходити
proxy і не відключати TLS/контроль цілісності.

`POST /storage/v1/object/list/exercise-images` — читання переліку, не upload.
Інші POST, усі RPC, PATCH, DELETE та PUT відсутні або заборонені guard.

Порожнеча каталогу на момент SQL-перевірки підтверджена результатом
`postgres / rls_applies_to_editor=false / count=0`. Це не припущення з
порожнього REST response та не твердження про майбутній стан БД. Якщо
новий REST read покаже рядки, dry-run додасть блокування зміни каталогу.
Код перевіряє checksum відомих CHECK definitions; невідомі нові правила
не видаються за перевірені. Default [] використовується лише для локальної
перевірки ефективного рядка, не записується в insert draft і не пояснює
бізнес-семантики поля. Усі 451 seed row і 135 image patch проходять 8 правил
із наданого SQL snapshot; реальний SQL INSERT не виконувався.

Підсумок фактичного імпорту — у `uploads/completion.json` і handoff.
Recorded technical failures і нестандартні dimensions залишаються
незмінними в source і плані. Всі mutations обмежено catalog_exercise та
перевіреним набором Storage paths. Admin secret не замінює publishable
key для перевірки звичайного клієнта.
# Continuing approved images without importing the catalog

Use `continue_images.py` for subsequent approved PNGs. It reuses the existing
proxy client, PNG byte validator, public SHA256 verifier and `transfer_one`.
Its API guard prohibits catalog INSERTs and PATCHes containing anything other
than the five image fields. It never deletes old objects, changes approvals,
performs visual QA or generates images.

From `/workspace/lightweight-exercises-photo`, refresh only remote refs:

```bash
git fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*'
python3 -B integration/supabase/continue_images.py --run-id continuation-2026-10-02
python3 -B integration/supabase/continue_images.py --run-id continuation-2026-10-02 --apply
```

The first Python command reads Supabase and prepares cloud working files; it
does not write to Supabase. The second performs explicitly authorized image
transfers, in batches of ten, with separate manifests and handoff checkpoints.
Use the same run ID to resume an interrupted plan. A new review scope needs a
new run ID; omitting it derives one from the UTC date and fetched remote refs.
Plans pin the exact source commits and accepted user decisions. They do not
automatically choose the latest attempt or merge source branches.

All PNG bytes are extracted by Git from accepted paths into
`/workspace/supabase-image-staging/<source_commit>/<source_png>` outside the
checkout. SHA256, decoding, dimensions, alpha and the bucket limit are checked.
Explicitly accepted historical technical exceptions are retained as metadata.
Staging can be restored from pinned Git blobs if a subsequent cloud runtime
lacks those files. PNGs are not committed to the integration branch.

An approved replacement may change an existing link only when its old five
image fields match a previously verified import. The old Storage object is
retained. Public hash verification precedes PATCH, a fresh row read reconciles
concurrent changes, and optimistic filters include ID, updated_at and all old
image fields. An unresolved conflict stops the batch without a blind retry.

The original 135-PNG manifests remain historical evidence. Subsequent runs are
recorded under `uploads/<run-id>/`, including source commits, approval evidence,
exact hashes/paths, pending exclusions, byte checks, live reconciliation and
individual transfer results. Keep the `exerciseuploader` binding and HTTPS proxy
inherited from the cloud runtime; never copy their values into scripts or files.
