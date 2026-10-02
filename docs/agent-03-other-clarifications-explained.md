# Agent-03: пояснення 105 нових уточнень

Джерело даних вправ — тільки `data/exercises/catalog.json`, work `fcc2cf3227cbe8e52932c0c56b7ca89018cd0a10`. SHA256: `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. Кожен повний запис отримано за точним ID; усі 105 вихідних записів звірено з каталогом. Нижче назви полів відносні до запису цього ID, індекси instructions/cues/mistakes починаються з нуля.

Це 105 нових уточнень попереднього раунду, а не додаткові 105 до нього. Попередні 15 зі старих пакетів не входять у цю кількість і не перепризначені. Повні 105 ID, незмінний англійський текст, питання й SHA256 джерел: [clarifications.json](../data/queues/agent-03-other-clarifications.json).

Є дві основні категорії: **50 питань техніки/обладнання** (17 суперечностей між полями та 33 випадки недостатньої конкретності) і **55 питань правила стилю**. Групи взаємовиключні за першою причиною відкладення. Наявність причини стилю не підтверджує і не спростовує достатність техніки — її треба перевірити перед майбутнім допуском.

| Основна категорія | Кількість | Що треба вирішити |
| --- | ---: | --- |
| Техніка / обладнання — суперечності | 17 | Яке з несумісних формулювань правильне; потрібне вихідне уточнення, не вибір агента |
| Техніка / обладнання — недостатня конкретність | 33 | Точні опори, кріплення, обтяження, хват, траєкторія або характерна відмінність варіанта |
| Стиль: full_body | 40 | Правило локальної підсвітки для full_body |
| Стиль: cardio | 14 | Правило підсвітки для cardio |
| Стиль: other | 1 | Правило підсвітки для other |

Стиль v1 вимагає локально підсвічувати primary #F26445 і secondary тим самим кольором із 40–50% інтенсивності. full_body/cardio/other не визначають локальну анатомічну групу. Не можна довільно вибрати м’язи, зафарбувати все тіло або мовчки прибрати підсвітку. Потрібне окреме правило стилю; за потреби власник даних може окремо погодити уточнення м’язових полів.

## Три приклади кожної основної категорії

| Категорія | ID | Точні проблемні поля / значення | Питання |
| --- | --- | --- | --- |
| Техніка: опори | `feet-up-bench-press-barbell` | `name`: "Feet Up Bench Press (Barbell)"; `content.en.instructions[0]`: "Lie on a flat bench with feet planted. Grip the barbell and hold it over the chest." | Стопи підняті чи мають опору? Де саме вони розташовані? |
| Техніка: обладнання | `hack-squat-barbell` | `equipment`: "barbell"; `content.en.instructions[0]`: "Stand with bodyweight and feet about shoulder-width apart."; решта instructions не задає гриф | Це вправа зі штангою чи власною вагою? Якщо зі штангою, де гриф і який хват? |
| Техніка: cues | `jump-squat` | `content.en.instructions[2]`: "Jump explosively off the ground, extending your hips, knees, and ankles."; `content.en.form_cues[0]`: "Keep the feet planted."; `content.en.common_mistakes[1]`: "Rising onto the toes." | До яких фаз належать вимоги тримати стопи на опорі та заборона підйому на носки? Які cues правильні для відштовхування й приземлення? |
| Стиль: cardio | `aerobics` | `primary_muscle`: "cardio"; `secondary_muscles`: [] | Яке правило підсвітки має діяти для cardio, без довільного вибору анатомічних м’язів? |
| Стиль: full_body | `ball-slams` | `primary_muscle`: "full_body"; `secondary_muscles`: [] | Яке правило підсвітки має діяти для full_body, зберігаючи заборону загального помаранчевого тону? |
| Стиль: other | `stretching` | `primary_muscle`: "other"; `secondary_muscles`: [] | Яке правило підсвітки має діяти для other, де цільова анатомічна група не визначена? |

## Кількості за підтипами

| Код | Підтип | Кількість | Категорія |
| --- | --- | ---: | --- |
| `muscle_style_mapping` | Правило підсвітки для загальної м’язової категорії | 55 | стиль |
| `movement_unspecified` | Невизначений рух / траєкторія | 3 | недостатня конкретність техніки |
| `support_unspecified` | Невизначені опори | 6 | недостатня конкретність техніки |
| `conflicting_supports` | Суперечливі опори | 7 | суперечність техніки |
| `variant_missing` | Не визначена відмінність варіанта | 7 | недостатня конкретність техніки |
| `anchor_unspecified` | Не визначено кріплення стрічки | 7 | недостатня конкретність техніки |
| `load_unspecified` | Не визначено обтяження | 8 | недостатня конкретність техніки |
| `equipment_unspecified` | Не визначено конструкцію обладнання / хват | 2 | недостатня конкретність техніки |
| `conflicting_movement` | Суперечливий рух | 4 | суперечність техніки |
| `conflicting_equipment` | Суперечливе обладнання | 4 | суперечність техніки |
| `conflicting_cues` | Суперечливі підказки до техніки | 2 | суперечність техніки |

## Приклади за кожним підтипом

По три приклади для кожного підтипу, де є щонайменше три записи. equipment_unspecified і conflicting_cues мають лише по два ID — наведено обидва, третій не вигадано. Відсутня деталь означає потребу уточнення, не доказ того, що загальна техніка вправи хибна.

### Правило підсвітки для загальної м’язової категорії — 55

**`aerobics` — Aerobics**

Точні вихідні поля:

```json
{
  "primary_muscle": "cardio",
  "secondary_muscles": []
}
```

Питання стилю: Яке погоджене правило локальної підсвітки слід застосовувати для `cardio`? Чи потрібна окрема політика без зміни техніки? Не обирати м’язи або відсутність підсвітки самостійно.

Каталожний запис SHA256: `740c785885ba92265788aa3469e87a376e59095ae27a40187dd746c4773ab219`.

**`ball-slams` — Ball Slams**

Точні вихідні поля:

```json
{
  "primary_muscle": "full_body",
  "secondary_muscles": []
}
```

Питання стилю: Яке погоджене правило локальної підсвітки слід застосовувати для `full_body`? Чи потрібна окрема політика без зміни техніки? Не обирати м’язи або відсутність підсвітки самостійно.

Каталожний запис SHA256: `916354dda0484f4f320d1665fe1f509c346e42f9f4d70176f4b474e45efd3fc8`.

**`stretching` — Stretching**

Точні вихідні поля:

```json
{
  "primary_muscle": "other",
  "secondary_muscles": []
}
```

Питання стилю: Яке погоджене правило локальної підсвітки слід застосовувати для `other`? Чи потрібна окрема політика без зміни техніки? Не обирати м’язи або відсутність підсвітки самостійно.

Каталожний запис SHA256: `eb53f30899511e6fdcb7cf6d6ad08938498c6cb84b7ddd65c9d6ae6f3adf69a9`.

### Невизначений рух / траєкторія — 3

**`around-the-world-dumbbell` — Around The World**

Точні вихідні поля:

```json
{
  "content.en.instructions[0]": "Stand tall holding the dumbbells with your arms extended as appropriate for the movement.",
  "content.en.instructions[1]": "Sweep the weight(s) in a smooth circle around the body without twisting the torso.",
  "content.en.instructions[2]": "Keep the shoulders controlled as the hands pass through the front and overhead portions of the path."
}
```

Проблема й питання: arms extended as appropriate та weight(s) не визначають площину кола й однозначну кількість/контакти гантелей. Уточніть конкретний варіант.

Каталожний запис SHA256: `a9a0eb52b0332ab807a6f169c98c560d5f361b84e1ed44ef4580fa24fa457a61`.

**`box-jump` — Box Jump**

Точні вихідні поля:

```json
{
  "content.en.instructions[0]": "Set up with a sturdy box and land in a balanced athletic stance.",
  "content.en.instructions[1]": "Dip through the hips and knees, then drive upward or forward as the exercise requires.",
  "content.en.instructions[2]": "Land softly with knees and hips flexed and the feet stable."
}
```

Проблема й питання: upward or forward as the exercise requires не задає однозначного напрямку й місця приземлення відносно box. Уточніть одну фазу та траєкторію.

Каталожний запис SHA256: `d1b7ae6e396aecf883a432e46f4737b9ab0acaccf29174c7a3577a425603b421`.

**`frog-jumps` — Frog Jumps**

Точні вихідні поля:

```json
{
  "name": "Frog Jumps",
  "content.en.instructions[0]": "Set up with your bodyweight and land in a balanced athletic stance.",
  "content.en.instructions[1]": "Dip through the hips and knees, then drive upward or forward as the exercise requires."
}
```

Проблема й питання: Типовий jump текст upward or forward as the exercise requires не визначає frog-позицію та напрямок. Уточніть варіант.

Каталожний запис SHA256: `5f5e541c4089572b04d19c0a69eb2a5d5b2cae324cac30fa60055399c4111405`.

### Невизначені опори — 6

**`assisted-pistol-squats` — Assisted Pistol Squats**

Точні вихідні поля:

```json
{
  "name": "Assisted Pistol Squats",
  "content.en.instructions[0]": "Stand on one leg with the other leg extended forward and use a stable support if needed.",
  "content.en.safety_note": "Use a support and reduced depth until the single-leg heel and knee stay aligned."
}
```

Проблема й питання: Assisted в назві, але stable support лише if needed; вид опори й контакт руки не визначені. Уточніть потрібну опору та спосіб тримання.

Каталожний запис SHA256: `03fd5f07ba93bc8be19b2daa6da36c995f90d6ae6b4441d20f3b2a3d24678487`.

**`biceps-curl-suspension` — Bicep Curl (Suspension)**

Точні вихідні поля:

```json
{
  "equipment": "suspension",
  "content.en.instructions": [
    "Stand or sit tall with suspension straps and use a underhand grip.",
    "Keep the upper arms still and curl the resistance toward the shoulders.",
    "Pause at the top without lifting the elbows.",
    "Lower slowly until the elbows are nearly straight."
  ]
}
```

Проблема й питання: Не визначено анкер, нахил тіла та контакти зі стопами; текст схожий на звичайний curl. Уточніть suspension-композицію.

Каталожний запис SHA256: `b6ef6da16947235467e682be59e790d349df103616df896231976f412af702f7`.

**`chest-fly-suspension` — Chest Fly (Suspension)**

Точні вихідні поля:

```json
{
  "equipment": "suspension",
  "content.en.instructions[0]": "Set up on your bodyweight with a soft bend in the elbows and the chest supported as required."
}
```

Проблема й питання: Instructions кажуть set up on your bodyweight та chest supported as required, не задаючи ролі straps або нахилу. Уточніть опори/анкер.

Каталожний запис SHA256: `6e7a1c1668dbda3967615b90bde53f0dbaaadec32e4c4450a4ec1430563e27c8`.

### Суперечливі опори — 7

**`bench-dip` — Bench Dip**

Точні вихідні поля:

```json
{
  "content.en.description": "The Bench Dip lowers the body by bending the elbows between parallel supports, then presses back up while the shoulders remain controlled.",
  "content.en.instructions[0]": "Place your hands on a stable bench behind you and walk the feet forward to support your body."
}
```

Проблема й питання: Description задає parallel supports, instructions — лавку позаду та стопи на підлозі. Уточніть опори; не підміняти опис здогадкою.

Каталожний запис SHA256: `521020e5df6974c72377255be300ed0c3eba082416a3cedf6689000a5925a3f0`.

**`feet-up-bench-press-barbell` — Feet Up Bench Press (Barbell)**

Точні вихідні поля:

```json
{
  "name": "Feet Up Bench Press (Barbell)",
  "content.en.instructions[0]": "Lie on a flat bench with feet planted. Grip the barbell and hold it over the chest."
}
```

Проблема й питання: Feet Up у назві суперечить Lie on a flat bench with feet planted. Уточніть положення ніг.

Каталожний запис SHA256: `4392780c4d3b66eda6be8bb84cc4b66dd3df6c840f11d563aeb6c9ce3e5b4da6`.

**`hip-thrust-barbell` — Hip Thrust (Barbell)**

Точні вихідні поля:

```json
{
  "content.en.description": "With the shoulders supported on a bench and a barbell across the hips, drive the hips upward until the torso and thighs align.",
  "content.en.instructions[0]": "Lie flat on your back on a bench with your feet flat on the ground and your knees bent.",
  "content.en.instructions[2]": "Engaging your glutes, lift your hips off the bench until your body forms a straight line from your knees to your shoulders.",
  "content.en.form_cues[1]": "Keep the upper back on the bench as the hips reach full extension."
}
```

Проблема й питання: Description/cue: upper back on bench; instructions: lie flat on your back on a bench, lift hips off bench. Уточніть геометрію опор.

Каталожний запис SHA256: `01222d152171562c044d3b797797e9b6c5b52511a6424fae8e71bcc4935a9422`.

### Не визначена відмінність варіанта — 7

**`bench-press-close-grip-barbell` — Bench Press - Close Grip (Barbell)**

Точні вихідні поля:

```json
{
  "name": "Bench Press - Close Grip (Barbell)",
  "content.en.instructions": [
    "Lie on a flat bench with feet planted. Grip the barbell and hold it over the chest.",
    "Lower the resistance toward the chest with elbows controlled.",
    "Pause without bouncing or losing shoulder position.",
    "Press back to straight arms, then rerack or set the weights down safely."
  ]
}
```

Проблема й питання: Назва Close Grip, але весь англійський блок не задає вузьку ширину хвата. Вкажіть хват цього варіанта.

Каталожний запис SHA256: `f9e476b9927f6aade2ca2ae35e25d7d39672eec1bc22b26b6d4cd92bbaaadd75`.

**`bench-press-wide-grip-barbell` — Bench Press - Wide Grip (Barbell)**

Точні вихідні поля:

```json
{
  "name": "Bench Press - Wide Grip (Barbell)",
  "content.en.instructions": [
    "Lie on a flat bench with feet planted. Grip the barbell and hold it over the chest.",
    "Lower the resistance toward the chest with elbows controlled.",
    "Pause without bouncing or losing shoulder position.",
    "Press back to straight arms, then rerack or set the weights down safely."
  ]
}
```

Проблема й питання: Назва Wide Grip, але весь англійський блок не задає широкий хват. Вкажіть хват цього варіанта.

Каталожний запис SHA256: `1cdfba6a27d35752e0e938eb33b06951cf8e70b8988a8cf1321d8b2e8806de9b`.

**`clap-push-ups` — Clap Push Ups**

Точні вихідні поля:

```json
{
  "name": "Clap Push Ups",
  "content.en.description": "Clap Push Ups lowers the chest from a braced plank and presses back up with the hands under the shoulders.",
  "content.en.instructions[2]": "Press through the palms; for clap push-ups, leave the floor briefly and land softly."
}
```

Проблема й питання: Назва Clap, але instructions задають лише leave the floor briefly, без однозначного плескання й пози рук. Уточніть характерну фазу.

Каталожний запис SHA256: `597e5358848ddc3f1529328678eb0ec93e071943b8447ec3d8ba50337d347b5f`.

### Не визначено кріплення стрічки — 7

**`bent-over-row-band-resistance-band` — Bent Over Row (Band)**

Точні вихідні поля:

```json
{
  "equipment": "resistance_band",
  "content.en.description": "Bent Over Row (Band) pulls band handles toward the lower ribs from a fixed hip hinge.",
  "content.en.instructions": [
    "Stand with feet hip-width apart, hinge until the torso is inclined, and grip the resistance.",
    "Pull toward the lower ribs while keeping the spine fixed.",
    "Pause with elbows behind the torso and shoulders away from the ears.",
    "Lower until the arms lengthen, then reset."
  ]
}
```

Проблема й питання: Вказано band handles, але не визначено точку/спосіб закріплення стрічки. Вкажіть анкер або контакт зі стопами.

Каталожний запис SHA256: `fba18c0ed9c3fbd3c8cce7fbb273e3bdbb7ffa54d349820f02f3ce9efe59f08e`.

**`chest-fly-band-resistance-band` — Chest Fly (Band)**

Точні вихідні поля:

```json
{
  "equipment": "resistance_band",
  "content.en.instructions[0]": "Set up on the resistance band with a soft bend in the elbows and the chest supported as required."
}
```

Проблема й питання: Set up on the resistance band та chest supported as required не визначають анкер, положення тулуба й опору. Уточніть конструкцію.

Каталожний запис SHA256: `ed4893ab23d658973e2bb9f2cc323260a0dfaba330f4921a831a6e11af2d86af`.

**`chest-press-band-resistance-band` — Chest Press (Band)**

Точні вихідні поля:

```json
{
  "equipment": "resistance_band",
  "content.en.description": "Chest Press (Band) is a supported chest press using band handles.",
  "content.en.instructions": [
    "Lie on a flat bench with feet planted. Grip band handles and hold it over the chest.",
    "Lower the resistance toward the chest with elbows controlled.",
    "Pause without bouncing or losing shoulder position.",
    "Press back to straight arms, then rerack or set the weights down safely."
  ]
}
```

Проблема й питання: Жим лежачи з band handles задано, але точка закріплення стрічки відсутня. Уточніть конфігурацію стрічки відносно лави.

Каталожний запис SHA256: `e81afbb5607dbdaae2b72a16c541a3c61e12dcc61629c62b2ffb869ccb97f9ff`.

### Не визначено обтяження — 8

**`chest-dip-weighted-machine` — Chest Dip (Weighted)**

Точні вихідні поля:

```json
{
  "name": "Chest Dip (Weighted)",
  "equipment": "machine",
  "content.en.instructions": [
    "Mount the parallel handles with arms straight and the torso slightly inclined.",
    "Bend the elbows to lower until the upper arms approach parallel with the floor.",
    "Pause before the shoulders lose control.",
    "Press through the handles to straighten the elbows and reset."
  ],
  "content.en.safety_note": "Use the assistance platform or a lighter load if the full dip depth cannot stay controlled."
}
```

Проблема й питання: Weighted у назві, але немає зовнішньої ваги, способу закріплення чи місця навантаження. Вкажіть конкретне обтяження.

Каталожний запис SHA256: `351231c64248ce62b940b99b806293e579db87b20e112c1a0bd6b37f60c1fc60`.

**`crunch-weighted` — Crunch (Weighted)**

Точні вихідні поля:

```json
{
  "name": "Crunch (Weighted)",
  "equipment": "none",
  "content.en.instructions": [
    "Lie on your back with knees bent and feet flat.",
    "Brace and curl the ribs toward the pelvis.",
    "Pause without pulling the neck.",
    "Lower the torso slowly to the support."
  ]
}
```

Проблема й питання: Weighted у назві при equipment=none; весь англійський блок описує crunch без ваги. Вкажіть тип, місце й тримання обтяження.

Каталожний запис SHA256: `f88eded54fa113168d7827f95113aef4ab3182066d98e106d7ef6406ac92d37c`.

**`decline-crunch-weighted` — Decline Crunch (Weighted)**

Точні вихідні поля:

```json
{
  "name": "Decline Crunch (Weighted)",
  "equipment": "none",
  "content.en.instructions": [
    "Secure your feet on a decline bench and lie back.",
    "Brace and curl the ribs toward the pelvis.",
    "Pause without pulling the neck.",
    "Lower the torso slowly to the support."
  ]
}
```

Проблема й питання: Weighted у назві при equipment=none; declined crunch не має визначеної ваги або місця навантаження. Уточніть обтяження.

Каталожний запис SHA256: `2f428c5fd0ad898f6594e3cce163e7bd4b470c3ba3046a7553aa9e68e6db2180`.

### Не визначено конструкцію обладнання / хват — 2

У всьому підтипі тільки 2 записи; нижче наведено всі.

**`deadlift-trap-bar-barbell` — Deadlift (Trap bar)**

Точні вихідні поля:

```json
{
  "name": "Deadlift (Trap bar)",
  "equipment": "barbell",
  "content.en.description": "Deadlift (Trap bar) hinges to the barbell, drives the floor away, and finishes with the hips tall before reversing the hinge.",
  "content.en.instructions[0]": "Stand with the barbell over the mid-foot and hinge to grip it."
}
```

Проблема й питання: Trap bar у назві, але опис та setup — barbell over the mid-foot, без положення всередині рами чи бічних руків’їв. Уточніть конструкцію й хват.

Каталожний запис SHA256: `2be008f9aa120008b542de236623cf68fdd0b0e02f2002b71779f3edd77d4689`.

**`ez-bar-biceps-curl-barbell` — EZ Bar Biceps Curl**

Точні вихідні поля:

```json
{
  "name": "EZ Bar Biceps Curl",
  "equipment": "barbell",
  "content.en.description": "EZ Bar Biceps Curl curls the barbell toward the shoulders with the underhand grip, keeping the upper arms controlled.",
  "content.en.instructions[0]": "Stand or sit tall with the barbell and use a underhand grip."
}
```

Проблема й питання: Назва EZ Bar, але техніка задає лише barbell та underhand grip, без відповідної конструкції/контактів хвата. Підтвердьте гриф і хват.

Каталожний запис SHA256: `9cb4c1eaf5829a1812882f4a8ba7d6ab5f397d908721471619fa0c4451c92beb`.

### Суперечливий рух — 4

**`dragonfly` — Dragonfly**

Точні вихідні поля:

```json
{
  "name": "Dragonfly",
  "content.en.description": "The Dragonfly opens and closes the arms around the chest with a soft elbow bend rather than turning the motion into a press.",
  "content.en.instructions[0]": "Set up on your bodyweight with a soft bend in the elbows and the chest supported as required."
}
```

Проблема й питання: Для Dragonfly подано chest-fly текст з your bodyweight та невизначеною chest support. Уточніть сам рух і положення тіла.

Каталожний запис SHA256: `df42af6b3784de8a7e8cec55e432cdabdc2a39acfb1cb466a32a48d89ef4606c`.

**`landmine-180-barbell` — Landmine 180**

Точні вихідні поля:

```json
{
  "content.en.description": "Swing the anchored barbell in a controlled arc from one hip across the body to the other.",
  "content.en.instructions[2]": "As you reach the bottom of the movement, quickly reverse the motion and rotate your torso to the left, swinging the barbell up and across your body towards your left shoulder.",
  "content.en.form_cues[1]": "Keep the feet planted while the bar traces a controlled arc from one hip to the other."
}
```

Проблема й питання: Description/cue задають hip-to-hip arc, instructions — right hip to left shoulder. Уточніть кінцеві точки.

Каталожний запис SHA256: `c5f25e5bd7749530c5511f43787ba25dc316da1a585a2a50c36366548e9c1860`.

**`negative-pullup` — Negative Pull Up**

Точні вихідні поля:

```json
{
  "content.en.description": "Negative Pull Up pulls from a controlled hang until the chin reaches or clears the bar, then lowers under control.",
  "content.en.instructions[0]": "Use a step or jump to start with your chin above the pull-up bar and a secure overhand grip.",
  "content.en.instructions[2]": "Descend as slowly as possible until the arms are straight."
}
```

Проблема й питання: Description каже pulls from a controlled hang until chin clears; instructions — почати зверху й тільки опускатися. Уточніть опис негативної фази.

Каталожний запис SHA256: `c09b9c58d28ad7e5d3aef56365508ba44bd5f653c9202a45e3349b0d6065cae7`.

### Суперечливе обладнання — 4

**`front-raise-suspension` — Front Raise (Suspension)**

Точні вихідні поля:

```json
{
  "equipment": "suspension",
  "content.en.description": "Front Raise (Suspension) raises bodyweight forward to a controlled shoulder-height range without leaning back.",
  "content.en.instructions[0]": "Stand tall holding your bodyweight in front of the thighs with a soft bend in the elbows."
}
```

Проблема й питання: Instructions пропонують holding your bodyweight in front of the thighs замість конфігурації suspension. Уточніть straps, анкер і нахил тіла.

Каталожний запис SHA256: `a23b7887b4c9eb9e37a55430ea2cce993a0312a2dd491a9f878af967a0f5d25b`.

**`hack-squat-barbell` — Hack Squat**

Точні вихідні поля:

```json
{
  "equipment": "barbell",
  "content.en.instructions": [
    "Stand with bodyweight and feet about shoulder-width apart.",
    "Bend the hips and knees to the controlled depth while keeping both feet planted.",
    "Keep knees tracking over the toes and pause at the endpoint.",
    "Drive through the whole foot to stand and reset."
  ]
}
```

Проблема й питання: equipment=barbell, але instructions починаються Stand with bodyweight і не описують гриф. Уточніть обладнання та його положення.

Каталожний запис SHA256: `e1409ee2e92d284482bad8dc4c889b52ac2ccfb2f7acd74376563f6a00154961`.

**`ring-pullup` — Ring Pull Up**

Точні вихідні поля:

```json
{
  "content.en.description": "Ring Pull Up pulls from a controlled hang until the chin reaches or clears the bar, then lowers under control.",
  "content.en.instructions[0]": "Hang from the rings with arms straight, shoulders active, and legs controlled.",
  "content.en.instructions[2]": "Reach the chin above ring height or to a controlled top position."
}
```

Проблема й питання: Description задає chin clears the bar, instructions — кільця. Підтвердьте текст без підміни одного обладнання іншим.

Каталожний запис SHA256: `b26ec8a2881e0240dbea23e7934416b35604017d65e321c6e96f3168f4018087`.

### Суперечливі підказки до техніки — 2

У всьому підтипі тільки 2 записи; нижче наведено всі.

**`jump-squat` — Jump Squat**

Точні вихідні поля:

```json
{
  "content.en.instructions[2]": "Jump explosively off the ground, extending your hips, knees, and ankles.",
  "content.en.instructions[4]": "Land softly on the balls of your feet and immediately go into the next repetition.",
  "content.en.form_cues[0]": "Keep the feet planted.",
  "content.en.common_mistakes[1]": "Rising onto the toes."
}
```

Проблема й питання: Instructions вимагають стрибка з відривом стоп, form_cues — Keep the feet planted, mistakes — Rising onto the toes. Уточніть область дії цих суперечливих cues.

Каталожний запис SHA256: `2e7a00e40f074c36d605756fc8a6bb2befd4b2a590966567a906094b14487b7c`.

**`jumping-lunge` — Jumping Lunge**

Точні вихідні поля:

```json
{
  "content.en.instructions[2]": "Push off with your right foot and jump into the air, switching the position of your feet mid-air.",
  "content.en.form_cues[0]": "Keep the feet planted.",
  "content.en.common_mistakes[1]": "Rising onto the toes."
}
```

Проблема й питання: Instructions вимагають переключення ніг у повітрі, form_cues — Keep the feet planted, mistakes — Rising onto the toes. Уточніть cues для стрибкового варіанта.

Каталожний запис SHA256: `26d3f6567fcc63f89e3ef79563ed766665a2c677bd01c9049378cf1f2c98a88e`.

## Пріоритет уточнень

Спочатку узгодити 17 прямих суперечностей: feet-up/feet-planted, bodyweight/barbell, опори hip thrust/bench dip, кінці траєкторії landmine, кільця/перекладина, негативна фаза pull-up і стрибкові cues. Вибір одного поля агентом змінив би техніку здогадкою. Далі конкретизувати 33 неповні композиції.

Правило стилю для 55 ID вирішувати окремо: воно може зняти спільний блокер для групи, але не замінює перевірку техніки кожного exact ID. Уточнення не потрапили в пакети 004–006. Ні каталог, ні вихідні питання/дані не виправлялися; prompts і зображення для них не створювалися.
