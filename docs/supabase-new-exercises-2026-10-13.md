# Нові вправи Supabase для Exercise Creator

Вхідний файл: [`data/exercises/supabase-additions-2026-10-13.json`](../data/exercises/supabase-additions-2026-10-13.json).
Він містить усі 28 нових вправ, про перенесення яких користувач попросив
2026-10-13, із `public.catalog_exercise` проєкту `yywyrbhqfavjdgonlzma`.

## Як читати дані для промптів

Формат кореня такий самий, як у історичного каталогу:
`schema_version`, `source`, `languages`, `exercises`.
`exercises` — масив записів із точним `id`; назви не використовувати як ключ.

Для кожного запису читати `name`, `equipment`, `primary_muscle`,
`secondary_muscles`, `tracking_type` і весь `content.en`:
`description`, `instructions`, `form_cues`, `common_mistakes`,
`safety_note`, `provenance`. Усі отримані колонки Supabase, включно з
`replaces_ids`, image-полями, `attribution`, `updated_at` та всіма мовними
блоками, збережені без перетворення значень. Відсутні переклади або
Hevy reference IDs не вигадувалися.

Інструкція для Exercise Creator:

> Прочитай data/exercises/supabase-additions-2026-10-13.json з цієї гілки
> GitHub. Підготуй промпти для його 28 exercises, зберігаючи кожен точний id.
> Використовуй повний content.en, обладнання та м'язи відповідного запису
> й правила стилю репозиторію. Не зіставляй за назвою; не генеруй зображення
> та не позначай результати approved під час підготовки промптів.

На момент експорту всі 28 записів активні, кожен має один повний англійський
мовний блок. Зображення до них у Supabase ще не прив'язані. У файлі немає
генерацій, промптів, нових схвалень чи вигаданих перекладів.

## Історичний каталог і перевірка

`data/exercises/catalog.json` із 451 записом та 4448 мовними блоками залишено
незмінним: історичні manifests і скрипти перенесення посилаються на його
SHA256. Цей файл є доповненням із 28 окремими новими ID.
Об'єднаний набір за ID містить 479 записів та 4476 мовних блоків;
3 архівні записи залишаються у історичному каталозі.

Точні ID, hashes усіх повних записів та hash вхідного файлу:
[`new-exercises-manifest.json`](../integration/supabase/exports/2026-10-13/new-exercises-manifest.json).

Відтворювана перевірка з поточного хмарного workspace:

```bash
python3 -B integration/supabase/export_new_exercises.py --check
```

Без параметрів скрипт виконує dry-run; `--write` створює лише ще не наявні
файли експорту в хмарному workspace. Доступ до Supabase обмежений GET;
використовується наявна прив'язка `exerciseuploader` через HTTPS-проксі.
Секрет не записується у файли. Значення всіх експортованих полів перевіряються
порівнянням із новим повним читанням Supabase.

Коду або налаштувань самого Exercise Creator у цьому репозиторії немає.
Перевірено JSON, точну множину ID, повноту англійських полів для промптів
і рівність повним записам Supabase; запуск самого Creator не перевірявся.
