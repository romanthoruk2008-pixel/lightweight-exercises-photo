# Доповнення v1: нейтральне тіло для узагальненого primary

Пропонована версія: `v1-neutral-primary-draft-2026-10-02`. **awaiting_style_decision, НЕ затверджено.**

Пропозиція: коли primary_muscle дорівнює full_body, cardio або other, залишати анатомічне тіло нейтральним непрозорим сріблясто-сірим. Не фарбувати все тіло й не виводити основну м’язову групу з руху, назви чи зовнішнього джерела.

Підсвічувати лише конкретні secondary_muscles, прямо записані для цього exact ID, тим самим #F26445 на 40–50% інтенсивності. Порожній secondary список → жодної підсвітки. Це інтенсивність кольору, не прозорість тканин.

Зовнішність, матеріали, чорні шорти, один манекен/одна фаза, квадратний PNG і прозорий фон успадковано від v1. Чинний docs/exercise-image-style.md не змінено. Правило не додає обладнання й не вирішує суперечностей техніки.

**55 власних + 5 попередніх чужих = 60 ID.** Лише kettlebell-high-pull має secondary=[traps]; для нього легша підсвітка трапецій. У всіх інших 59 secondary=[]: повністю нейтральне тіло.

Власні conditional prompts: `data/queues/agent-03-neutral-primary-style-drafts.json`. Дозвіл на генерацію не надано. 45 записів мають конкретний повний prompt, 10 потребують ще визначення руху/варіанта або сумісності взуття; для них збережено template без вигаданих сцен.

Одне спільне питання: **затвердити це доповнення нейтрального primary й підсвітки лише явно зазначених secondary?** До рішення всі 55 власних записи awaiting_style_decision.

Окреме спільне питання footwear для hiking/walking/snowboarding: дозволити сумісне взуття/кріплення й захист, чи погодити окрему barefoot ілюстрацію/тренувальний варіант? Сама пропозиція кольорів НЕ змінює barefoot v1.

Для HIIT, Pilates, Stretching і Yoga також потрібен один конкретний рух/поза; для Clean/Press Under — receiving варіант; Muscle Up має суперечливий поворот хвата. Ці питання не замінено рішенням стилю.

## Єдиний список застосовності (точні ID)

Позначка foreign означає вже зарезервований чужий запис: лише включений до групового рішення, без нового prompt/пакета/результату.

| exercise_id | Власність |
| --- | --- |
| `aerobics` | agent-03 |
| `ball-slams` | agent-03 |
| `battle-ropes-machine` | agent-03 |
| `boxing` | agent-03 |
| `burpee` | agent-03 |
| `burpee-broad-jumps` | agent-03 |
| `burpee-over-the-bar` | agent-03 |
| `clean-barbell` | agent-03 |
| `clean-and-jerk-barbell` | agent-03 |
| `clean-and-press-barbell` | agent-03 |
| `clean-pull-barbell` | agent-03 |
| `climbing` | agent-03 |
| `deadlift-high-pull-barbell` | agent-03 |
| `dumbbell-snatch` | agent-03 |
| `farmers-walk` | agent-03 |
| `front-lever-hold` | agent-03 |
| `front-lever-raise` | agent-03 |
| `handstand-hold` | agent-03 |
| `hang-clean-barbell` | agent-03 |
| `hang-snatch-barbell` | agent-03 |
| `high-knee-skips` | agent-03 |
| `hiit` | agent-03 |
| `hiking` | agent-03 |
| `jump-rope` | agent-03 |
| `jump-shrug-barbell` | agent-03 |
| `kettlebell-clean` | agent-03 |
| `kettlebell-high-pull` | agent-03 |
| `kettlebell-snatch` | agent-03 |
| `kettlebell-swing` | agent-03 |
| `kettlebell-turkish-get-up` | agent-03 |
| `landmine-squat-and-press-barbell` | agent-03 |
| `muscle-up-machine` | agent-03 |
| `overhead-squat-barbell` | agent-03 |
| `pilates` | agent-03 |
| `power-clean-barbell` | agent-03 |
| `power-snatch-barbell` | agent-03 |
| `press-under-barbell` | agent-03 |
| `running` | agent-03 |
| `skating` | agent-03 |
| `skiing` | agent-03 |
| `sled-pull` | agent-03 |
| `sled-push` | agent-03 |
| `snatch-barbell` | agent-03 |
| `snowboarding` | agent-03 |
| `split-jerk-barbell` | agent-03 |
| `sprints` | agent-03 |
| `stretching` | agent-03 |
| `suitcase-carry-dumbbell` | agent-03 |
| `swimming` | agent-03 |
| `thruster-barbell` | agent-03 |
| `thruster-kettlebell` | agent-03 |
| `walking` | agent-03 |
| `wall-ball` | agent-03 |
| `warm-up` | agent-03 |
| `yoga` | agent-03 |
| `downward-dog` | foreign: night-2026-10-01-clarifications |
| `bear-crawl` | foreign: night-2026-10-01-clarifications |
| `jumping-jack` | foreign: night-2026-10-01-clarifications |
| `high-knees` | foreign: night-2026-10-01-clarifications |
| `mountain-climber` | foreign: night-2026-10-01-clarifications |

Після рішення спочатку перевірити актуальні PNG/призначення; лише technical_status=ready допускає окреме формування нових пакетів. Власний style draft не є запуском або схваленням зображення.
