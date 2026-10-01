# Supabase integration preparation — agent-04

Це підготовка, не імпортер із правом запису. Скрипт не має `--apply` і не
викликає SQL, REST mutation, Storage upload чи imagegen. Він не змінює
каталог, PNG, progress або схвалення.

Гілка: `agent-04-supabase-integration`; база: `work` на
`a6f296cbc6737991dd367e929b3e2df25874d4d8`. Використовувати існуючий cloud
checkout; не створювати worktree та не використовувати Mac користувача.

## Файли

- `audit.md` — результати та межі перевірки.
- `field_mapping.md` — відповідність полів і послідовність майбутнього імпорту.
- `verify_schema.sql` — лише SELECT для підтвердження count/default/CHECK/RLS.
- `dry_run.py` — перевірка прийнятих байтів і read-only API audit.
- `inspect_source_archive.py` — відтворювана перевірка оригінального manifest
  через HTTPS byte ranges; не завантажує весь ZIP і не витягує медіа/інструменти.
- `source_archive_inspection.json` — результат; manifest SHA256 перевірений,
  повний ZIP SHA256 не перевірявся.
- `results/approved_png_plan.json` — 135 точних ID, source paths, accepted
  SHA256, фактичні PNG-перевірки, destination paths і відповідні DB records.
- `results/catalog_import_plan.json` — 451 ID і hashes незмінних мовних JSON;
  insert payload не створюється до рішення щодо `replaces_ids`.
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

Код завершення: `1` — помилка виконання, `2` — підготовку сформовано, але
імпорт блокований. Під час поточного етапу очікується `2`: невідомі
`replaces_ids`, незалежний SQL count, клієнтські права; записи Supabase
не авторизовані. Це не означає невдале декодування PNG.

Read-only API потребує наявної прив'язки `exerciseuploader` та HTTPS proxy.
Секрет використовується лише у `apikey` до проєкту Supabase. Не виводити
його, не записувати у файли, не передавати у Git або фронтенд. Не обходити
proxy і не відключати TLS/контроль цілісності.

`POST /storage/v1/object/list/exercise-images` — читання переліку, не upload.
Інші POST, усі RPC, PATCH, DELETE та PUT відсутні або заборонені guard.

135 PNG готові за байтами; імпорт у БД/Storage не виконано. Recorded
technical failures і нестандартні dimensions збережено окремо від
схвалення користувача та готовності за MIME/size/SHA256.
