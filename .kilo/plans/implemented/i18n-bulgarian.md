# i18n: Bulgarian + other languages

## Decisions
- Switching: manual toggle button + localStorage, no URL changes
- Server bridge: cookie `django_language` synced from localStorage by a blocking `<head>` script
- Default: Accept-Language header auto-detect, fallback to English
- Translation storage: Python dict in `calculator/translations.py` + JS object in template
- No gettext, no .po files, no LocaleMiddleware
- Languages: `en` (default), `bg`. Bulgarian translations provided in the plan.
- JS fallback: `t(key)` returns the key itself if translation missing

## Key naming convention
All keys are `snake_case`. Python and JS use the exact same keys. Server-only strings are prefixed with their section (e.g. `recipe_*`, `distill_*`). JS-only strings have descriptive names.

---

## Steps

### 1. calculator/translations.py — complete translations module
**Create new file.** Write the exact content below:

```python
"""UI translations for the Gin Calculator."""

TRANSLATIONS = {
    "en": {
        # -- Page chrome
        "page_title": "Spirit Calculator",
        "toggle_theme": "Toggle light/dark mode",
        "switch_language": "Switch language",
        "tagline": "Scale spirit recipes to any volume",
        # -- Mode toggle
        "mode_compound": "Compound - gin / aquavit",
        "mode_distill": "Distill - rakia / brandy",
        # -- Recipe card
        "recipe": "Recipe",
        "select_recipe": "Select recipe",
        "recipe_settings_aria": "Recipe settings",
        # -- Spirit type
        "spirit_type": "Spirit type",
        "spirit_neutral_label": "Neutral / food-grade",
        "spirit_neutral_hint": "~10-15% losses. Cut off at ~92C",
        "spirit_home_label": "Home-distilled spirit",
        "spirit_home_hint": "~30-35% losses. Cut off at ~88-90C",
        # -- Compound parameters
        "input_spirit_abv": "Input spirit ABV",
        "input_spirit_abv_title": "Alcohol strength of the raw spirit you're starting with",
        "still_yield": "Still yield",
        "still_yield_title": "Percentage of liquid recovered from distillation after accounting for losses",
        "maceration_abv": "Maceration ABV",
        "maceration_abv_title": "ABV to dilute the maceration charge down to partway through (e.g. after the neat phase)",
        "target_abv": "Target ABV",
        "target_abv_title": "Desired final alcohol percentage of the finished spirit",
        "desired_volume": "Desired volume",
        "desired_volume_title": "Total amount of finished spirit you want to produce",
        "calculation_results_aria": "Calculation results",
        # -- Results placeholder
        "results_placeholder": "Results appear automatically as you adjust parameters.",
        # -- Volumes card
        "volumes": "Volumes",
        "maceration_alc": "Maceration alc",
        "maceration_water_needed": "Maceration water needed",
        "est_water": "Est. Water",
        "varies_with_distillation": "varies with distillation output",
        # -- Botanicals card
        "botanicals": "Botanicals",
        # -- Distill inputs
        "wash_and_still": "Wash & Still",
        "wash_volume": "Wash volume",
        "wash_abv": "Wash ABV",
        "still_capacity": "Still capacity",
        "collection_abv": "Collection ABV",
        "distill_target_abv": "Target ABV",
        "distill_params_aria": "Distill parameters",
        "distill_results_aria": "Distill results",
        # -- Distill results
        "distillation_output": "Distillation Output",
        "pure_alcohol": "Pure alcohol",
        "expected_distillate": "Expected distillate",
        "batches_needed": "Batches needed",
        "water_to_proof": "Water to proof",
        # -- Empty state
        "no_recipes": "No recipes available",
        "no_recipes_hint": "Ask an administrator to add a recipe to get started.",
        # -- Footer
        "footer_text": "Spirit Calculator - scale any recipe with confidence",
        # -- JS strings (also used by server error responses)
        "error_maceration_abv_lower": "Maceration ABV must be lower than the input spirit ABV.",
        "error_spirit_abv_higher": "Input spirit ABV must be higher than the target ABV.",
        "hearts_cut_abv": "Hearts cut ABV",
        "optional_badge": "Optional",
        "base_recipe_tooltip": "Base recipe (1L)",
        "var_min_label": "Minimum amount",
        "var_base_label": "Base",
        "var_max_label": "Maximum amount",
        "var_min_title": "Min",
        "var_max_title": "Max",
        "cuts_heads_note": "Heads (~10% of distillate): discard. Hearts: keep until ABV drops below target. Tails: blend back or use as base for second run.",
        "cuts_low_abv_note": "Low-ABV wash - cut heads generously (~15%). Consider a second distillation for cleaner spirit.",
        # -- Server error responses
        "error_recipe_not_found": "Recipe not found",
        "error_invalid_input": "Invalid input data",
        "error_invalid_method": "Invalid request method",
    },
    "bg": {
        "page_title": "Калкулатор за спиртни напитки",
        "toggle_theme": "Превключване на тема",
        "switch_language": "Смяна на език",
        "tagline": "Мащабирайте рецепти за всякакъв обем",
        "mode_compound": "Комбиниране - джин / аквавит",
        "mode_distill": "Дестилация - ракия / бренди",
        "recipe": "Рецепта",
        "select_recipe": "Изберете рецепта",
        "recipe_settings_aria": "Настройки на рецепта",
        "spirit_type": "Тип спирт",
        "spirit_neutral_label": "Неутрален / хранителен",
        "spirit_neutral_hint": "~10-15% загуби. Отрязване при ~92C",
        "spirit_home_label": "Домашна ракия",
        "spirit_home_hint": "~30-35% загуби. Отрязване при ~88-90C",
        "input_spirit_abv": "Начален алкохолен градус",
        "input_spirit_abv_title": "Алкохолен градус на суровия спирт",
        "still_yield": "Рандеман на казана",
        "still_yield_title": "Процент течност, възстановена след дестилация",
        "maceration_abv": "Градус за мацерация",
        "maceration_abv_title": "Градус за разреждане на мацерационния разтвор",
        "target_abv": "Целеви градус",
        "target_abv_title": "Желан краен алкохолен процент",
        "desired_volume": "Желан обем",
        "desired_volume_title": "Общо количество готов продукт",
        "calculation_results_aria": "Резултати от изчислението",
        "results_placeholder": "Резултатите се появяват автоматично при промяна на параметрите.",
        "volumes": "Обеми",
        "maceration_alc": "Алкохол за мацерация",
        "maceration_water_needed": "Необходима вода за мацерация",
        "est_water": "Очаквана вода",
        "varies_with_distillation": "зависи от дестилационния изход",
        "botanicals": "Ботаникали",
        "wash_and_still": "Материал и казан",
        "wash_volume": "Обем на материала",
        "wash_abv": "Градус на материала",
        "still_capacity": "Капацитет на казана",
        "collection_abv": "Градус на дестилата",
        "distill_target_abv": "Целеви градус",
        "distill_params_aria": "Параметри на дестилация",
        "distill_results_aria": "Резултати от дестилация",
        "distillation_output": "Дестилационен изход",
        "pure_alcohol": "Чист алкохол",
        "expected_distillate": "Очакван дестилат",
        "batches_needed": "Необходими партиди",
        "water_to_proof": "Вода за разреждане",
        "no_recipes": "Няма налични рецепти",
        "no_recipes_hint": "Помолете администратор да добави рецепта.",
        "footer_text": "Калкулатор за спиртни напитки - мащабирайте всяка рецепта с увереност",
        "error_maceration_abv_lower": "Градусът за мацерация трябва да е по-нисък от началния алкохолен градус.",
        "error_spirit_abv_higher": "Началният алкохолен градус трябва да е по-висок от целевия.",
        "hearts_cut_abv": "Градус на сърцето",
        "optional_badge": "Опционално",
        "base_recipe_tooltip": "Базова рецепта (1L)",
        "var_min_label": "Минимално количество",
        "var_base_label": "Основа",
        "var_max_label": "Максимално количество",
        "var_min_title": "Мин",
        "var_max_title": "Макс",
        "cuts_heads_note": "Глави (~10% от дестилата): изхвърлете. Сърце: задръжте докато градусът падне под целевия. Опашки: смесете обратно или използвайте като основа за втора дестилация.",
        "cuts_low_abv_note": "Материал с нисък градус - отрежете главите щедро (~15%). Препоръчителна втора дестилация за по-чист спирт.",
        "error_recipe_not_found": "Рецептата не е намерена",
        "error_invalid_input": "Невалидни входни данни",
        "error_invalid_method": "Невалиден метод на заявка",
    },
}
```

**Verify**: `python -c "from calculator.translations import TRANSLATIONS; assert set(TRANSLATIONS['en']) == set(TRANSLATIONS['bg']); print(len(TRANSLATIONS['en']), 'keys, languages:', list(TRANSLATIONS))"`

Expected: `61 keys, languages: ['en', 'bg']`

---

### 2. calculator/views.py — language detection + context + cookie
**Edit the `index` view** (lines 8-21) to:
1. Add import at top: `from .translations import TRANSLATIONS`
2. Detect language: read `django_language` cookie; if valid (`en` or `bg`) use it. Else parse `Accept-Language` header for `bg` substring; if found use `bg`, else `en`.
3. Set the `django_language` cookie on the response so the browser remembers it.
4. Pass `t=TRANSLATIONS[lang]` and `lang=lang` to template context.

Replace the `index` function with this exact code:

```python
def index(request):
    """Main calculator page"""
    # Language detection
    lang = request.COOKIES.get('django_language')
    if lang not in ('en', 'bg'):
        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        lang = 'bg' if 'bg' in accept.lower() else 'en'

    recipes = Recipe.objects.filter(is_active=True).prefetch_related('ingredients__ingredient')
    default_recipe = Recipe.objects.filter(is_default=True, is_active=True).first()
    if not default_recipe and recipes.exists():
        default_recipe = recipes.first()

    response = render(request, 'calculator/index.html', {
        'recipes': recipes,
        'default_recipe': default_recipe,
        't': TRANSLATIONS[lang],
        'lang': lang,
    })
    response.set_cookie('django_language', lang, max_age=31536000, samesite='Lax')
    return response
```

Also edit the `get_recipe` view (lines 25-70): add language detection and use translated error strings. Add at the top of `get_recipe` (after the docstring):

```python
    lang = request.COOKIES.get('django_language', 'en')
    if lang not in ('en', 'bg'):
        lang = 'en'
    t = TRANSLATIONS[lang]
```

Then replace these three strings:
- `'Recipe not found'` → `t['error_recipe_not_found']`
- `'Invalid input data'` → `t['error_invalid_input']`
- `'Invalid request method'` → `t['error_invalid_method']`

**Verify**: `python manage.py check`

---

### 3. calculator/templates/calculator/index.html — language cookie sync script in <head>
**Insert a blocking `<script>` tag** between `<head>` and `</head>`, after the existing `<link>` elements. The script syncs localStorage from the `django_language` cookie (which Django sets on every response). No reload needed here — Django already rendered the correct language.

Insert AFTER `<link rel="stylesheet" href="{% static 'calculator/calculator.css' %}">`:

```html
<script>
(function(){
  var cookieMatch = document.cookie.match(/(?:^|;\s*)django_language=([^;]*)/);
  var cookieLang = cookieMatch ? cookieMatch[1] : null;
  if (cookieLang && localStorage.getItem('lang') !== cookieLang) {
    localStorage.setItem('lang', cookieLang);
  }
})();
</script>
```

**Verify**: `python manage.py check` (checks template syntax — no error means the insertion is valid)

---

### 4. calculator/templates/calculator/index.html — body + header + mode toggle strings
**Make these 8 edits** (all in `<head>` through the mode toggle at line ~33):

a) `<html lang="en">` → `<html lang="{{ lang }}">`

b) `<title>Spirit Calculator</title>` → `<title>{{ t.page_title }}</title>`

c) `aria-label="Toggle light/dark mode"` → `aria-label="{{ t.toggle_theme }}"`

d) `<h1>Spirit Calculator</h1>` → `<h1>{{ t.page_title }}</h1>`

e) `<span class="tagline">Scale spirit recipes to any volume</span>` → `<span class="tagline">{{ t.tagline }}</span>`

f) Button text `Compound - gin / aquavit` → `{{ t.mode_compound }}`

g) Button text `Distill - rakia / brandy` → `{{ t.mode_distill }}`

h) `aria-label="Recipe settings"` → `aria-label="{{ t.recipe_settings_aria }}"`

**Verify**: `python manage.py check`

---

### 5. calculator/templates/calculator/index.html — recipe card + spirit type strings
**Make these 7 edits** in the recipe card section (lines ~40-80):

a) `<h2>Recipe</h2>` → `<h2>{{ t.recipe }}</h2>`

b) `<label for="recipe_select">Select recipe</label>` → `<label for="recipe_select">{{ t.select_recipe }}</label>`

c) `<span class="params-group-label">Spirit type</span>` → `<span class="params-group-label">{{ t.spirit_type }}</span>`

d) `<span class="spirit-option-label">Neutral / food-grade</span>` → `<span class="spirit-option-label">{{ t.spirit_neutral_label }}</span>`

e) `<span class="spirit-option-hint">~10-15% losses. Cut off at ~92C</span>` → `<span class="spirit-option-hint">{{ t.spirit_neutral_hint }}</span>`

f) `<span class="spirit-option-label">Home-distilled spirit</span>` → `<span class="spirit-option-label">{{ t.spirit_home_label }}</span>`

g) `<span class="spirit-option-hint">~30-35% losses. Cut off at ~88-90C</span>` → `<span class="spirit-option-hint">{{ t.spirit_home_hint }}</span>`

**Verify**: `python manage.py check`

---

### 6. calculator/templates/calculator/index.html — compound panel parameter labels
**Make these 12 edits** in the `.params-bar` section (lines ~82-120):

a) `<label ... for="input_spirit_abv" id="pb-abv-label">Input spirit ABV</label>` → `{{ t.input_spirit_abv }}`
   (replace the text content only, keep the HTML attributes)

b) `title="Alcohol strength of the raw spirit you're starting with"` → `title="{{ t.input_spirit_abv_title }}"`

c) `<label ... for="still_yield">Still yield</label>` → `{{ t.still_yield }}` (text content only)

d) `title="Percentage of liquid recovered from distillation after accounting for losses"` → `title="{{ t.still_yield_title }}"`

e) `<label ... for="maceration_abv">Maceration ABV</label>` → `{{ t.maceration_abv }}`

f) `title="ABV to dilute the maceration charge down to partway through (e.g. after the neat phase)"` → `title="{{ t.maceration_abv_title }}"`

g) `<label ... for="target_abv">Target ABV</label>` → `{{ t.target_abv }}`

h) `title="Desired final alcohol percentage of the finished spirit"` → `title="{{ t.target_abv_title }}"`

i) `<label ... for="volume">Desired volume</label>` → `{{ t.desired_volume }}`

j) `title="Total amount of finished spirit you want to produce"` → `title="{{ t.desired_volume_title }}"`

k) `aria-label="Calculation results"` → `aria-label="{{ t.calculation_results_aria }}"`

**Verify**: `python manage.py check`

---

### 7. calculator/templates/calculator/index.html — results section strings
**Make these 10 edits** in the results/volumes/botanicals area (lines ~121-167):

a) `<p>Results appear automatically as you adjust parameters.</p>` → `<p>{{ t.results_placeholder }}</p>`

b) `<h2>Volumes</h2>` → `<h2>{{ t.volumes }}</h2>`

c) `<div class="volume-stat-label">Maceration alc</div>` → `{{ t.maceration_alc }}`

d) `<div class="volume-stat-label">Maceration water needed</div>` → `{{ t.maceration_water_needed }}`

e) `<div class="volume-stat-label">Est. Water</div>` → `{{ t.est_water }}`

f) `<div class="volume-stat-note">varies with distillation output</div>` → `{{ t.varies_with_distillation }}`

g) `<h2>Botanicals</h2>` → `<h2>{{ t.botanicals }}</h2>`

In the JS section (the `renderResults` function that resets placeholder HTML at line ~499): change the hardcoded English fallback:

h) Find: `'<p>Results appear automatically as you adjust parameters.</p>'` → use `t('results_placeholder')` — but this is a JS string, handle in Step 10.

**Verify**: `python manage.py check`

---

### 8. calculator/templates/calculator/index.html — distill panel strings
**Make these 14 edits** in the distill panel section (lines ~175-267):

a) `<h2>Wash &amp; Still</h2>` → `<h2>{{ t.wash_and_still }}</h2>`

b) `<label for="wash_volume">Wash volume</label>` → `{{ t.wash_volume }}`

c) `<label for="wash_abv">Wash ABV</label>` → `{{ t.wash_abv }}`

d) `<label for="still_capacity">Still capacity</label>` → `{{ t.still_capacity }}`

e) `<label for="collection_abv">Collection ABV</label>` → `{{ t.collection_abv }}`

f) `<label for="distill_target_abv">Target ABV</label>` → `{{ t.distill_target_abv }}`

g) `aria-label="Distill parameters"` → `aria-label="{{ t.distill_params_aria }}"`

h) `aria-label="Distill results"` → `aria-label="{{ t.distill_results_aria }}"`

i) The distill placeholder `<p>Results appear automatically as you adjust parameters.</p>` → `{{ t.results_placeholder }}`

j) `<h2>Distillation Output</h2>` → `<h2>{{ t.distillation_output }}</h2>`

k) `<div class="volume-stat-label">Pure alcohol</div>` → `{{ t.pure_alcohol }}`

l) `<div class="volume-stat-label">Expected distillate</div>` → `{{ t.expected_distillate }}`

m) `<div class="volume-stat-label">Batches needed</div>` → `{{ t.batches_needed }}`

n) `<div class="volume-stat-label">Water to proof</div>` → `{{ t.water_to_proof }}`

**Verify**: `python manage.py check`

---

### 9. calculator/templates/calculator/index.html — empty state + footer strings
**Make these 4 edits:**

a) `<h2>No recipes available</h2>` → `<h2>{{ t.no_recipes }}</h2>`

b) `<p>Ask an administrator to add a recipe to get started.</p>` → `<p>{{ t.no_recipes_hint }}</p>`

c) Footer text `Spirit Calculator - scale any recipe with confidence` → `{{ t.footer_text }}`

d) Add language toggle button in the header, inside `.header-controls`, BEFORE the theme toggle button:

```html
<button id="lang-toggle" class="lang-toggle" aria-label="{{ t.switch_language }}">
  <span class="lang-code" id="lang-code-display">{{ lang|upper }}</span>
</button>
```

**Verify**: `python manage.py check`

---

### 10. calculator/templates/calculator/index.html — JS translations object + helpers + toggle handler
**In the `<script>` block**, add these at the very top (after `'use strict';`), BEFORE any other JS code:

a) Declare `window.__lang` from the server-rendered language:

```javascript
window.__lang = '{{ lang }}';
```

b) Add the JS `TRANSLATIONS` object. This is the SAME translations data as `calculator/translations.py` but as a JS object, with ONLY the keys used by JS (not the template-only keys). However, to keep it simple and avoid mismatches, include ALL keys. The template already handles its own keys via `{{ t.key }}`; the JS object is used by `t()` calls in JS code.

Add this EXACT JSON block:

```javascript
window.__t = {
  en: {
    error_maceration_abv_lower: "Maceration ABV must be lower than the input spirit ABV.",
    error_spirit_abv_higher: "Input spirit ABV must be higher than the target ABV.",
    hearts_cut_abv: "Hearts cut ABV",
    input_spirit_abv: "Input spirit ABV",
    optional_badge: "Optional",
    base_recipe_tooltip: "Base recipe (1L)",
    var_min_label: "Minimum amount",
    var_base_label: "Base",
    var_max_label: "Maximum amount",
    var_min_title: "Min",
    var_max_title: "Max",
    cuts_heads_note: "Heads (~10% of distillate): discard. Hearts: keep until ABV drops below target. Tails: blend back or use as base for second run.",
    cuts_low_abv_note: "Low-ABV wash - cut heads generously (~15%). Consider a second distillation for cleaner spirit.",
    results_placeholder: "Results appear automatically as you adjust parameters.",
    varies_with_distillation: "varies with distillation output"
  },
  bg: {
    error_maceration_abv_lower: "\u0413\u0440\u0430\u0434\u0443\u0441\u044a\u0442 \u0437\u0430 \u043c\u0430\u0446\u0435\u0440\u0430\u0446\u0438\u044f \u0442\u0440\u044f\u0431\u0432\u0430 \u0434\u0430 \u0435 \u043f\u043e-\u043d\u0438\u0441\u044a\u043a \u043e\u0442 \u043d\u0430\u0447\u0430\u043b\u043d\u0438\u044f \u0430\u043b\u043a\u043e\u0445\u043e\u043b\u0435\u043d \u0433\u0440\u0430\u0434\u0443\u0441.",
    error_spirit_abv_higher: "\u041d\u0430\u0447\u0430\u043b\u043d\u0438\u044f\u0442 \u0430\u043b\u043a\u043e\u0445\u043e\u043b\u0435\u043d \u0433\u0440\u0430\u0434\u0443\u0441 \u0442\u0440\u044f\u0431\u0432\u0430 \u0434\u0430 \u0435 \u043f\u043e-\u0432\u0438\u0441\u043e\u043a \u043e\u0442 \u0446\u0435\u043b\u0435\u0432\u0438\u044f.",
    hearts_cut_abv: "\u0413\u0440\u0430\u0434\u0443\u0441 \u043d\u0430 \u0441\u044a\u0440\u0446\u0435\u0442\u043e",
    input_spirit_abv: "\u041d\u0430\u0447\u0430\u043b\u0435\u043d \u0430\u043b\u043a\u043e\u0445\u043e\u043b\u0435\u043d \u0433\u0440\u0430\u0434\u0443\u0441",
    optional_badge: "\u041e\u043f\u0446\u0438\u043e\u043d\u0430\u043b\u043d\u043e",
    base_recipe_tooltip: "\u0411\u0430\u0437\u043e\u0432\u0430 \u0440\u0435\u0446\u0435\u043f\u0442\u0430 (1L)",
    var_min_label: "\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u043d\u043e \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e",
    var_base_label: "\u041e\u0441\u043d\u043e\u0432\u0430",
    var_max_label: "\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u043d\u043e \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e",
    var_min_title: "\u041c\u0438\u043d",
    var_max_title: "\u041c\u0430\u043a\u0441",
    cuts_heads_note: "\u0413\u043b\u0430\u0432\u0438 (~10% \u043e\u0442 \u0434\u0435\u0441\u0442\u0438\u043b\u0430\u0442\u0430): \u0438\u0437\u0445\u0432\u044a\u0440\u043b\u0435\u0442\u0435. \u0421\u044a\u0440\u0446\u0435: \u0437\u0430\u0434\u0440\u044a\u0436\u0442\u0435 \u0434\u043e\u043a\u0430\u0442\u043e \u0433\u0440\u0430\u0434\u0443\u0441\u044a\u0442 \u043f\u0430\u0434\u043d\u0435 \u043f\u043e\u0434 \u0446\u0435\u043b\u0435\u0432\u0438\u044f. \u041e\u043f\u0430\u0448\u043a\u0438: \u0441\u043c\u0435\u0441\u0435\u0442\u0435 \u043e\u0431\u0440\u0430\u0442\u043d\u043e \u0438\u043b\u0438 \u0438\u0437\u043f\u043e\u043b\u0437\u0432\u0430\u0439\u0442\u0435 \u043a\u0430\u0442\u043e \u043e\u0441\u043d\u043e\u0432\u0430 \u0437\u0430 \u0432\u0442\u043e\u0440\u0430 \u0434\u0435\u0441\u0442\u0438\u043b\u0430\u0446\u0438\u044f.",
    cuts_low_abv_note: "\u041c\u0430\u0442\u0435\u0440\u0438\u0430\u043b \u0441 \u043d\u0438\u0441\u044a\u043a \u0433\u0440\u0430\u0434\u0443\u0441 - \u043e\u0442\u0440\u0435\u0436\u0435\u0442\u0435 \u0433\u043b\u0430\u0432\u0438\u0442\u0435 \u0449\u0435\u0434\u0440\u043e (~15%). \u041f\u0440\u0435\u043f\u043e\u0440\u044a\u0447\u0438\u0442\u0435\u043b\u043d\u0430 \u0432\u0442\u043e\u0440\u0430 \u0434\u0435\u0441\u0442\u0438\u043b\u0430\u0446\u0438\u044f \u0437\u0430 \u043f\u043e-\u0447\u0438\u0441\u0442 \u0441\u043f\u0438\u0440\u0442.",
    results_placeholder: "\u0420\u0435\u0437\u0443\u043b\u0442\u0430\u0442\u0438\u0442\u0435 \u0441\u0435 \u043f\u043e\u044f\u0432\u044f\u0432\u0430\u0442 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u043d\u043e \u043f\u0440\u0438 \u043f\u0440\u043e\u043c\u044f\u043d\u0430 \u043d\u0430 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0438\u0442\u0435.",
    varies_with_distillation: "\u0437\u0430\u0432\u0438\u0441\u0438 \u043e\u0442 \u0434\u0435\u0441\u0442\u0438\u043b\u0430\u0446\u0438\u043e\u043d\u043d\u0438\u044f \u0438\u0437\u0445\u043e\u0434"
  }
};
```

c) Add the `t(key)` helper function:

```javascript
function t(key) {
  var dict = window.__t[window.__lang] || window.__t['en'];
  return dict[key] || key;
}
```

d) Add language toggle click handler at the end of the `<script>` block (before the closing `</script>`):

```javascript
document.getElementById('lang-toggle').addEventListener('click', function() {
  var newLang = window.__lang === 'bg' ? 'en' : 'bg';
  localStorage.setItem('lang', newLang);
  document.cookie = 'django_language=' + newLang + ';path=/;max-age=31536000;samesite=lax';
  location.reload();
});
```

**Verify**: `python manage.py check`

---

### 11. calculator/templates/calculator/index.html — replace JS hardcoded strings with t() calls
**Make these 14 edits** in the JS code. Each replaces a hardcoded English string literal with `t('key_name')`:

a) In `calculateLocally()`, first error (line ~409): the string `'Maceration ABV must be lower than the input spirit ABV.'` → `t('error_maceration_abv_lower')`

b) In `calculateLocally()`, second error (line ~433): the string `'Input spirit ABV must be higher than the target ABV.'` → `t('error_spirit_abv_higher')`

c) In `renderResults()` (line ~465): `'Optional'` → `t('optional_badge')`

d) In `renderResults()` (line ~489): `'Base recipe (1L)'` → `t('base_recipe_tooltip')`

e) In `renderResults()` (line ~499): the reset placeholder HTML string `'<p>Results appear automatically as you adjust parameters.</p>'` — change to use `t('results_placeholder')`:

Old: `placeholder.innerHTML = '<span class="results-placeholder-icon" aria-hidden="true">\u{1f378}</span>' + '<p>Results appear automatically as you adjust parameters.</p>';`

New: `placeholder.innerHTML = '<span class="results-placeholder-icon" aria-hidden="true">\u{1f378}</span><p>' + t('results_placeholder') + '</p>';`

f) In `renderResults()`, the `var-min` pill `aria-label="Minimum amount"` → use `t('var_min_label')`

g) In `renderResults()`, the `var-min` pill `title="Min..."` — the title is dynamically built: `'Min (\u2212' + parsed.pct + '%)'`. Replace the `'Min'` part:

Old: `title="Min (\u2212${parsed.pct}%)"` → New: `title="${t('var_min_title')} (\u2212${parsed.pct}%)"`

h) In `renderResults()`, the `var-base` pill `title="Base"` → `title="${t('var_base_label')}"`

i) In `renderResults()`, the `var-max` pill `aria-label="Maximum amount"` → `t('var_max_label')`

j) In `renderResults()`, the `var-max` pill `title="Max..."`:

Old: `title="Max (+\${parsed.pct}%)"` → New: `title="\${t('var_max_title')} (+\${parsed.pct}%)"`

k) In the spirit type radio handler (line ~562): `'Hearts cut ABV'` → `t('hearts_cut_abv')`

l) In the spirit type radio handler (line ~565): `'Input spirit ABV'` → `t('input_spirit_abv')`

m) In `calculateDistill()`, first cuts note (line ~624): the long string starting with `'Heads (~10% of distillate): discard...'` → `t('cuts_heads_note')`

n) In `calculateDistill()`, second cuts note (line ~625): `'Low-ABV wash - cut heads generously (~15%). Consider a second distillation for cleaner spirit.'` → `t('cuts_low_abv_note')`

**Verify**: `python manage.py check`

---

### 12. calculator/static/calculator/calculator.css — language toggle styles
**Add CSS** at the end of the file for the language toggle button:

```css
/* -- Language toggle -- */
.lang-toggle {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  padding: 2px 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-text-secondary);
  font-family: inherit;
  font-size: 0.75rem;
  font-weight: 600;
  transition: background var(--transition), border-color var(--transition);
}

.lang-toggle:hover {
  background: var(--color-surface-2);
  border-color: var(--color-accent);
}

.lang-code {
  letter-spacing: 0.04em;
}
```

**Verify**: visual inspection after running server — button appears next to theme toggle, styled consistently.

---

## Validation (after all steps)
```bash
python manage.py check && python manage.py test calculator
```

Then run the dev server and manually:
1. Open `/` — page renders in English (or auto-detected language)
2. Click language toggle → page reloads in Bulgarian
3. Click language toggle again → page reloads in English
4. Verify JS-generated text changes: switch to distill mode, change parameters, check cuts note language
5. Verify cookie is set: `document.cookie` in console shows `django_language=en` or `bg`
6. Verify localStorage: `localStorage.lang` matches
