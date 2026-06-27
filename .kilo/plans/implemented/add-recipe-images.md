# Add Pictures to Famous Gin Recipes

## Goal
Display a brand image for each famous gin recipe in the UI. The image appears as a
banner inside the left "Recipe" card, directly under the recipe `<select>` and above
the description, and updates whenever the selected recipe changes.

## Decisions (resolved with the user)
| Decision | Choice |
|---|---|
| Image source | **External image URLs** (Wikimedia Commons / Wikipedia), hot-linked via `<img src>` |
| Who sourced the URLs | Architect sourced 8 stable `upload.wikimedia.org` URLs; baked in as exact literals |
| Where stored on the model | New `image_url = URLField(blank=True, default="")` on `GinRecipe` |
| Where the URL literals live | A `name → url` dict **inside the management command** (NOT the fixture) |
| Backfill of existing rows | `create_famous_recipes` upserts `image_url` on already-existing recipes |
| UI placement | Banner in the left "Recipe" card, under the dropdown |
| Fallback | Empty `image_url` → banner hidden; broken link → `onerror` hides it |
| Image fit | `object-fit: contain`, ~160px tall (tall bottle shots not cropped) |

## Why the URLs live in the command, not the fixture
`calculator/fixtures/famous_gin_recipes.json` is large (Monkey 47 has 47 ingredients).
Asking the executor to rewrite that whole file to inject a key per recipe risks silently
dropping or mangling ingredient data. Instead the 8 URL literals live in a small dict in
the command file, which the command already iterates by recipe name. **The fixture is
never modified by this plan.**

## Executor notes (IMPORTANT — read before each step)
- Do exactly ONE step at a time, then run its Verify before moving on.
- Each step touches exactly ONE file.
- Steps 4 and 5 are **surgical anchored inserts** into a 359-line template. Do NOT
  rewrite the whole file. Find the exact anchor text given and insert the snippet
  relative to it. Leave all other lines unchanged.
- Use the project's Python env. Commands assume `pyenv activate gin` (or the equivalent
  active virtualenv) and that a Django superuser already exists.

## Name → image URL mapping (exact literals — copy verbatim, do not invent)
| Recipe `name` (must match exactly) | image_url |
|---|---|
| `Tanqueray London Dry` | `https://upload.wikimedia.org/wikipedia/commons/3/3d/Tanqueray_bottle.JPG` |
| `Hendrick's` | `https://upload.wikimedia.org/wikipedia/en/c/c6/Hendricks_Gin_Logo.jpg` |
| `Bombay Sapphire` | `https://upload.wikimedia.org/wikipedia/commons/f/f7/Bombay_Sapphire_-_bouteilles.JPG` |
| `Beefeater London Dry` | `https://upload.wikimedia.org/wikipedia/commons/3/37/BEEFEATER2022_%28cropped%29.jpg` |
| `Aviation American Gin` | `https://upload.wikimedia.org/wikipedia/commons/a/a5/Aviation_American_Gin_Distillery_filling_station.jpg` |
| `Gordon's London Dry` | `https://upload.wikimedia.org/wikipedia/commons/f/ff/Gordons_London_Dry_Gin_im_Regal.jpg` |
| `Monkey 47 Schwarzwald Dry Gin` | `https://upload.wikimedia.org/wikipedia/commons/b/b7/Monkey_47_-_Schwarzwald_Dry_Gin_-_Packshot.jpg` |
| `Sipsmith London Dry` | `https://upload.wikimedia.org/wikipedia/commons/4/4b/Sipsmith_London_Logo.png` |

> Note: Hendrick's and Sipsmith URLs are brand logos and Aviation is a distillery photo;
> Commons had no clean bottle shot for those. They are valid, hot-linkable, and can be
> swapped later by editing the dict in the command.

---

## Step 1 — Add `image_url` field to the model
**File:** `calculator/models.py`

In class `GinRecipe`, add one field. Put it immediately after the `description` field
(line currently reads `description = models.TextField(blank=True)`):

```python
    image_url = models.URLField(blank=True, default="", help_text="External image URL for this recipe")
```

Do not change any other field. `URLField` default `max_length=200` is sufficient (all
URLs above are under 200 chars).

**Verify:**
```bash
pyenv activate gin
python manage.py makemigrations calculator   # creates calculator/migrations/0003_ginrecipe_image_url.py
python manage.py migrate                      # applies it
python manage.py check                        # System check identified no issues
```
Then read back `calculator/models.py` and confirm the `image_url` line is present in
`GinRecipe`.

---

## Step 2 — Backfill + set `image_url` in the seed command
**File:** `calculator/management/commands/create_famous_recipes.py`

Make two edits to the existing command.

**Edit 2a — add the URL dict.** Inside `handle`, right after the superuser check returns
(after the `return` that follows the "No superuser found" warning) and before the
`# Load the fixture data` comment, add:

```python
        # Exact image URLs per recipe name (source of truth for images).
        IMAGE_URLS = {
            "Tanqueray London Dry": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Tanqueray_bottle.JPG",
            "Hendrick's": "https://upload.wikimedia.org/wikipedia/en/c/c6/Hendricks_Gin_Logo.jpg",
            "Bombay Sapphire": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Bombay_Sapphire_-_bouteilles.JPG",
            "Beefeater London Dry": "https://upload.wikimedia.org/wikipedia/commons/3/37/BEEFEATER2022_%28cropped%29.jpg",
            "Aviation American Gin": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Aviation_American_Gin_Distillery_filling_station.jpg",
            "Gordon's London Dry": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Gordons_London_Dry_Gin_im_Regal.jpg",
            "Monkey 47 Schwarzwald Dry Gin": "https://upload.wikimedia.org/wikipedia/commons/b/b7/Monkey_47_-_Schwarzwald_Dry_Gin_-_Packshot.jpg",
            "Sipsmith London Dry": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Sipsmith_London_Logo.png",
        }
```

**Edit 2b — upsert image_url in the loop.** Find the existing block that skips existing
recipes:

```python
            # Check if recipe already exists
            if GinRecipe.objects.filter(name=recipe_data['name']).exists():
                self.stdout.write(
                    self.style.WARNING(f'Recipe "{recipe_data["name"]}" already exists. Skipping.')
                )
                continue
```

Replace it with a version that backfills the image before continuing:

```python
            # Check if recipe already exists -> backfill its image_url, then skip re-create
            existing = GinRecipe.objects.filter(name=recipe_data['name']).first()
            if existing:
                new_url = IMAGE_URLS.get(recipe_data['name'], "")
                if new_url and existing.image_url != new_url:
                    existing.image_url = new_url
                    existing.save(update_fields=['image_url'])
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated image for existing recipe "{existing.name}".')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Recipe "{recipe_data["name"]}" already exists. Skipping.')
                    )
                continue
```

Then find the `GinRecipe.objects.create(` call and add `image_url` to it. Change:

```python
                is_default=recipe_data['is_default'],
                created_by=admin_user
            )
```
to:
```python
                is_default=recipe_data['is_default'],
                image_url=IMAGE_URLS.get(recipe_data['name'], ""),
                created_by=admin_user
            )
```

Leave the ingredient-creation loop and summary print untouched.

**Verify:**
```bash
pyenv activate gin
python manage.py create_famous_recipes        # updates or creates; no traceback
python manage.py create_famous_recipes        # idempotent; still no traceback
python manage.py shell -c "from calculator.models import GinRecipe; print([(r.name, bool(r.image_url)) for r in GinRecipe.objects.filter(name__in=['Tanqueray London Dry','Monkey 47 Schwarzwald Dry Gin','Sipsmith London Dry'])])"
# Expect each tuple's second value to be True
```

---

## Step 3 — Expose `image_url` in the JSON endpoint
**File:** `calculator/views.py`

In `get_recipe`, find the serialized `recipe` dict and add `image_url`. Change:

```python
                    'name': recipe.name,
                    'description': recipe.description,
```
to:
```python
                    'name': recipe.name,
                    'description': recipe.description,
                    'image_url': recipe.image_url,
```

Do not change `calculate` or `index`.

**Verify:**
```bash
pyenv activate gin
python manage.py shell -c "from calculator.models import GinRecipe; from calculator.views import get_recipe; from django.test import RequestFactory; import json; r=GinRecipe.objects.get(name='Tanqueray London Dry'); req=RequestFactory().post('/get-recipe/', data=json.dumps({'recipe_id': r.id}), content_type='application/json'); resp=get_recipe(req); print('image_url' in json.loads(resp.content)['recipe'])"
# Expect: True
```

---

## Step 4 — Add the image banner markup (anchored insert)
**File:** `calculator/templates/calculator/index.html`

This is a SURGICAL INSERT. Do not rewrite the file.

Find this exact block (the recipe select field and the description div that follows it):

```html
          <div class="field">
            <label for="recipe_select">Select recipe</label>
            <select id="recipe_select" onchange="onRecipeChange()">
              {% for recipe in recipes %}
                <option value="{{ recipe.id }}"{% if recipe == default_recipe %} selected{% endif %}>{{ recipe.name }}</option>
              {% endfor %}
            </select>
          </div>
          <div id="recipe-description" class="recipe-description" role="note" aria-live="polite"></div>
```

Insert a new banner block BETWEEN the closing `</div>` of the field and the
`recipe-description` div, so the result is:

```html
          <div class="field">
            <label for="recipe_select">Select recipe</label>
            <select id="recipe_select" onchange="onRecipeChange()">
              {% for recipe in recipes %}
                <option value="{{ recipe.id }}"{% if recipe == default_recipe %} selected{% endif %}>{{ recipe.name }}</option>
              {% endfor %}
            </select>
          </div>
          <div id="recipe-image-wrap" class="recipe-image-wrap" hidden>
            <img id="recipe-image" alt="" loading="lazy">
          </div>
          <div id="recipe-description" class="recipe-description" role="note" aria-live="polite"></div>
```

Change nothing else.

**Verify:** Read back the file and confirm the `recipe-image-wrap` div now sits between
the select field and `recipe-description`, and that no other markup changed.

---

## Step 5 — Render the image in JS (anchored insert)
**File:** `calculator/templates/calculator/index.html`

This is a SURGICAL INSERT into the `<script>` block. Do not rewrite the file.

**Edit 5a — call the renderer.** Find this block inside `loadRecipeDetails`:

```javascript
      currentRecipe = data.recipe;
      renderRecipeDescription(data.recipe);
      renderReferenceRecipe(data.recipe);
```

Change it to add one line:

```javascript
      currentRecipe = data.recipe;
      renderRecipeImage(data.recipe);
      renderRecipeDescription(data.recipe);
      renderReferenceRecipe(data.recipe);
```

**Edit 5b — define the renderer.** Find the start of the existing function:

```javascript
  function renderRecipeDescription(recipe) {
```

Insert this new function immediately BEFORE it:

```javascript
  function renderRecipeImage(recipe) {
    const wrap = document.getElementById('recipe-image-wrap');
    const img = document.getElementById('recipe-image');
    if (!wrap || !img) return;

    const url = (recipe.image_url || '').trim();
    // Only allow https URLs; hide on missing or broken image.
    if (!url || !/^https:\/\//i.test(url)) {
      wrap.hidden = true;
      img.removeAttribute('src');
      return;
    }
    img.alt = recipe.name || '';
    img.onerror = function () { wrap.hidden = true; };
    img.onload = function () { wrap.hidden = false; };
    img.src = url;
  }

```

**Verify:** Read back the file and confirm `renderRecipeImage` is defined once, is called
inside `loadRecipeDetails`, and references `recipe.image_url`. Then load the app in a
browser (`python manage.py runserver`), pick "Monkey 47 Schwarzwald Dry Gin" — the banner
image should appear; pick "Classic London Dry" — the banner should disappear.

---

## Step 6 — Style the banner (append)
**File:** `calculator/static/calculator/calculator.css`

APPEND this block to the end of the file. Do not modify existing rules.

```css

/* ── Recipe image banner (inside the Recipe card) ── */
.recipe-image-wrap {
  margin-top: 12px;
  width: 100%;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-2, rgba(127, 127, 127, 0.08));
  border: 1px solid var(--color-border, rgba(127, 127, 127, 0.2));
  border-radius: 12px;
  overflow: hidden;
}

.recipe-image-wrap[hidden] {
  display: none;
}

#recipe-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}
```

> The `var(..., fallback)` forms mean this works whether or not the theme defines those
> custom properties.

**Verify:** Read back the tail of the file and confirm the block is present and the file
still ends cleanly. Reload the app and confirm the banner has rounded corners, a subtle
background, and the bottle is shown un-cropped (letterboxed if needed).

---

## Step 7 — Tests (append)
**File:** `calculator/tests.py`

APPEND a new test class at the end of the file. Do not modify existing tests.

```python
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from calculator.models import GinRecipe


class RecipeImageTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin_img", email="a@b.c", password="x")

    def test_image_urls_backfilled(self):
        call_command("create_famous_recipes")
        tanqueray = GinRecipe.objects.get(name="Tanqueray London Dry")
        self.assertTrue(tanqueray.image_url.startswith("https://"))

    def test_image_url_idempotent(self):
        call_command("create_famous_recipes")
        first = GinRecipe.objects.get(name="Monkey 47 Schwarzwald Dry Gin").image_url
        call_command("create_famous_recipes")
        second = GinRecipe.objects.get(name="Monkey 47 Schwarzwald Dry Gin").image_url
        self.assertEqual(first, second)
        self.assertTrue(second.startswith("https://"))

    def test_recipe_without_image_stays_blank(self):
        admin = User.objects.get(username="admin_img")
        r = GinRecipe.objects.create(
            name="No Image Recipe", abv_volume=0.4, created_by=admin
        )
        self.assertEqual(r.image_url, "")
```

> If `calculator/tests.py` already imports `TestCase`/`User`/`call_command`, the executor
> may drop the duplicate imports — but duplicate imports are harmless if left in.

**Verify:**
```bash
pyenv activate gin
python manage.py test calculator.tests.RecipeImageTest   # 3 tests pass
python manage.py test                                    # full suite still passes
```

---

## Final validation (run after all 7 steps)
```bash
pyenv activate gin
python manage.py check
python manage.py migrate
python manage.py create_famous_recipes
python manage.py test
python manage.py runserver   # manual: switch recipes, confirm banner shows/hides
```

## Risks & notes
- **External-link fragility:** Wikimedia may rename/remove a file, breaking a link. The
  `onerror` handler hides the banner so the page never shows a broken-image icon. URLs
  can be updated in the dict in `create_famous_recipes.py`.
- **Mixed content:** all URLs are `https://`; the JS also refuses non-`https` URLs.
- **Not all images are bottles:** Hendrick's & Sipsmith are logos, Aviation is a
  distillery photo (Commons lacked clean bottle shots). Swap later via the command dict.
- **Default & user recipes** have no entry in the dict, so `image_url` stays `""` and the
  banner stays hidden — intended graceful fallback.
- The fixture `famous_gin_recipes.json` is intentionally **not** modified by this plan.
