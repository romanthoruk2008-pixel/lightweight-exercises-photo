# Bed Cardio: новий Easter egg

Статус текстового запису: **готовий**, точний ID `bed-cardio`. Каталог у підготовчій гілці: **452 записи**, 449 активних + 3 архівних; **4456** мовних блоків. Попередні 451 записи / 4448 блоків залишені без змін. У work поки попередній каталог; цей commit не означає merge або запис у Supabase.

Поточний запит користувача явно дозволяє додавання одного нового запису, тому старе обмеження AGENTS.md «каталог не змінювати: 451 ID, 4448 мовних блоків» збережено для попередніх вправ, а новий record додано окремо. Не змінювати їх під цим приводом.

## Картка й локалізація

- Стандартна exercise card; category/primary=`cardio`, equipment=`none`, secondary=[]; archived=false.
- Tracking=`duration`; лише тривалість, без reps/sets/weight/distance; контракт у `data/cards/bed-cardio.json`.
- Перегляд картки з перемикачем восьми мов: `docs/bed-cardio-card.html`. Це самостійний preview, не реалізація в production-застосунку; його репозиторій у цій задачі відсутній.
- Canonical `name="Bed Cardio"` та ID залишаються стабільними. Локалізовані назви — `content.<locale>.name`; це additive JSONB-поле тільки нового record, не зміна SQL-колонок.
- Для UI: `content[locale].name -> content.en.name -> name`; застосунок, який читає тільки top-level name, показуватиме English доки його renderer не підтримуватиме цей lookup. Content JSONB зберігає всі назви й тексти без перетворення; renderer production не перевірений.

| Мова | Назва |
|---|---|
| EN | Bed Cardio |
| UK | Кардіо в ліжку |
| ES | Cardio en la cama |
| IT | Cardio a letto |
| TR | Yatakta Kardiyo |
| FR | Cardio au lit |
| RU | Кардио в постели |
| PL | Cardio w łóżku |

Український опис: «Кардіо, приємна компанія та комфортний темп. Записуйте тривалість — особисті рекорди необов’язкові».

Усі вісім мов мають name, description, 4 instructions, 3 form_cues, 3 common_mistakes, safety_note, provenance=authored. Це завуальований жарт для дорослих із взаємною згодою, без explicit-описів, техніки сексуальних дій, вигаданих м’язів чи обіцянок витрати калорій.

## Оригінальна ілюстрація

Користувач прямо обрав прикріплене зображення й сказав залишити його без змін. **Не генерувати заміну, не ретушувати, не змінювати підсвітку, фон, людей, розмір чи співвідношення сторін.** Рішення: `data/image-decisions/bed-cardio.json`. Виняток стилю тільки для цього asset: `data/style-decisions/bed-cardio-original-image.json`.

Видимий у чаті сюжет: двоє дорослих лежать поруч під ковдрою; збережений користувацький файл, а не демонстрація руху. Cardio/secondary=[] не дає підстав виводити anatomical muscle targets із помаранчевих ділянок цього жарту. Базовий neutral-primary стиль інших вправ не змінюється.

Технічний блокер: у доступних вкладеннях workspace немає оригінального image-файлу або downloadable file ID. Видимі пікселі чату не дорівнюють доступним незмінним байтам. `assets/exercises/bed-cardio.png` — лише запланований шлях, файла ще немає. Тому SHA256, MIME, dimensions, alpha та creator provenance залишені null/unknown; preview показує місце для обраного asset. Користувацький візуальний вибір зафіксовано; після надходження саме оригіналу його байти треба прив’язати до цього рішення, без повторного запиту схвалення і без конвертації.

Supabase CHECK дозволяє image_origin лише generated або gym_visual_edit. Походження цього файла не встановлено за зовнішнім виглядом; **не записувати навмання generated і не підставляти user_provided у SQL enum**. За відсутності підтвердженого походження імпортується лише текстовий рядок з усіма п’ятьма image-полями NULL. Подальший image patch — після оригінальних байтів і коректного origin, всі п’ять полів разом.

## Майбутній імпорт одного рядка

`data/imports/bed-cardio/catalog-exercise.insert.json` — список рівно з одним рядком для public.catalog_exercise. Точні direct fields скопійовані з catalog.json за ID. content включає всі 8 localized names та повні тексти. Attribution NULL: record авторський, не Gym Visual / не Hevy, dataset_id=NULL. Replaces_ids пропущено за чинним importer mapping; підтверджений server default [] враховано тільки в локальній перевірці. updated_at пропущено для server default.

Порядок:
1. Отримати підготовчий commit та прочитати `data/catalog-changes/bed-cardio.json`; звірити catalog SHA256 і exact ID. Не замінювати весь імпортований каталог новим bulk upsert.
2. Перед майбутнім записом прочитати тільки поточний ID bed-cardio. Якщо він існує — звірити, зупинитися при конфлікті; не перезаписувати його чи image-поля сліпим upsert. Якщо не існує — вставити лише цей рядок, коли користувач доручить імпорт.
3. Відновити назви/JSONB без зміни локалізації; readback direct fields/content повинен точно відповідати payload. Не чіпати попередні 451 row, Supabase images, зв’язки або shared progress.
4. Залишити image-поля NULL до отримання оригінального файла. Потім byte-for-byte копія у planned repository path, фактичні hash/format/dimensions/alpha й creator provenance; жодної генерації чи обробки. При невідповідності формату зупинитися, не конвертувати потай.
5. Не перевизначати у старому importer глобальний SOURCE_COMMIT/CATALOG_SHA256 і старі 451/4448 перевірки для bulk-операції. Це окремий user-authored delta поверх старого source release, задокументований change manifest.

## Перевірки

`python scripts/add_bed_cardio.py` перевіряє точний record, всі localized blocks, відсутність змін старих records/bytes та shared progress, duration-only contract, payload і стилістичне рішення. Усі вісім наявних SQL CHECK пройшли локально через реальний validator із agent-04. SQL/REST виклики на запис: 0; генерацій: 0. Audit: `data/audits/bed-cardio-validation.json`.

Джерельний archive metadata не підмінений: старий release/working-manifest описує legacy 451, а bed-cardio — один новий user-authored record. Історичні PNG, batches/queues і результати не змінювалися.
