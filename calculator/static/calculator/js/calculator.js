/**
 * Calculator logic for the Gin Calculator
 */

let currentRecipe = null;

/**
 * Load recipe details from server
 * @param {number} recipeId - ID of recipe to load
 * @returns {Promise<Object>} Recipe data
 */
export async function loadRecipeDetails(recipeId) {
  return fetch('/get-recipe/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recipe_id: parseInt(recipeId) }),
  })
  .then(res => res.json())
  .then(data => {
    if (!data.success) { console.error('Recipe load error:', data.error); return null; }
    currentRecipe = data.recipe;
    renderRecipeImage(data.recipe);
    renderRecipeDescription(data.recipe);
    const targetInput = document.getElementById('target_abv');
    if (targetInput && data.recipe.target_abv_percentage) {
      targetInput.value = data.recipe.target_abv_percentage;
    }
    return data.recipe;
  })
  .catch(err => {
    console.error('Failed to load recipe:', err);
    throw err;
  });
}

/**
 * Handle recipe change
 */
export async function onRecipeChange() {
  const select = document.getElementById('recipe_select');
  const recipeId = select.value;
  await loadRecipeDetails(recipeId);
  calculateLocally();
}

/**
 * Render recipe image
 * @param {Object} recipe - Recipe data
 */
export function renderRecipeImage(recipe) {
  const wrap = document.getElementById('recipe-image-wrap');
  const img = document.getElementById('recipe-image');
  if (!wrap || !img) return;
  const url = (recipe.image_url || '').trim();
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

/**
 * Render recipe description
 * @param {Object} recipe - Recipe data
 */
export function renderRecipeDescription(recipe) {
  const el = document.getElementById('recipe-description');
  if (recipe.description) {
    const safeName = escHtml(recipe.name);
    el.innerHTML = '<strong>' + safeName + '</strong>' + escHtml(recipe.description);
    el.classList.add('show');
  } else {
    el.classList.remove('show');
  }
}

/**
 * Calculate locally based on input values
 */
export function calculateLocally() {
  const volume = parseFloat(document.getElementById('volume').value);
  const inputSpiritAbv = parseFloat(document.getElementById('input_spirit_abv').value);
  const targetAbv = parseFloat(document.getElementById('target_abv').value);
  const stillYield = parseFloat(document.getElementById('still_yield').value) || 85;
  const macerationAbv = parseFloat(document.getElementById('maceration_abv').value);

  if (!currentRecipe) return;
  if (!volume || volume <= 0) return;
  if (!inputSpiritAbv || inputSpiritAbv <= 0) return;
  if (!targetAbv || targetAbv <= 0) return;

  if (!macerationAbv || macerationAbv <= 0 || macerationAbv >= inputSpiritAbv) {
    document.getElementById('results-placeholder').style.display = '';
    document.getElementById('results').classList.remove('show');
    document.getElementById('results-placeholder').innerHTML =
      '<span class="results-placeholder-icon" aria-hidden="true">⚠️</span>' +
      '<p>' + t('error_maceration_abv_lower') + '</p>';
    return;
  }

  const scaleFactor = volume / currentRecipe.base_volume;
  const scaledIngredients = currentRecipe.ingredients.map(ing => ({
    name: ing.name,
    name_bg: ing.name_bg,
    amount: Math.round(ing.amount * scaleFactor * 100) / 100,
    base_amount: ing.amount,
    is_optional: ing.is_optional,
    notes: ing.notes
  }));

  const spiritNeeded = Math.round(
    ((volume * targetAbv / 100) / (inputSpiritAbv / 100)) * 100
  ) / 100;
  const waterToAdd = Math.round((volume - spiritNeeded) * 100) / 100;

  if (waterToAdd < 0) {
    document.getElementById('results-placeholder').style.display = '';
    document.getElementById('results').classList.remove('show');
    document.getElementById('results-placeholder').innerHTML =
      '<span class="results-placeholder-icon" aria-hidden="true">⚠️</span>' +
      '<p>' + t('error_spirit_abv_higher') + '</p>';
    return;
  }

  const spiritToLoad = Math.round((spiritNeeded / (stillYield / 100)) * 100) / 100;
  const waterForMaceration = Math.round(
    (spiritToLoad * (inputSpiritAbv / macerationAbv - 1)) * 100
  ) / 100;

  renderResults({
    success: true,
    recipe_name: currentRecipe.name,
    spirit_needed: spiritNeeded,
    water_to_add: waterToAdd,
    spirit_to_load: spiritToLoad,
    maceration_water: waterForMaceration,
    scaled_ingredients: scaledIngredients
  });
}

/**
 * Render calculation results
 * @param {Object} data - Calculation results
 */
export function renderResults(data) {
  document.getElementById('spirit-load-value').textContent = data.spirit_to_load || data.spirit_needed;
  document.getElementById('maceration-water-value').textContent = data.maceration_water;
  document.getElementById('water-value').textContent = data.water_to_add;
  document.getElementById('result-recipe-name').textContent = data.recipe_name;

  const list = document.getElementById('ingredient-list');
  list.innerHTML = data.scaled_ingredients.map((ing, idx) => {
    const parsed = parseVariation(ing.notes);
    const notes = ing.notes ? '<span class="ingredient-row-notes">' + escHtml(ing.notes) + '</span>' : '';
    const badge = ing.is_optional ? '<span class="optional-badge">' + t('optional_badge') + '</span>' : '';
    const key = 'var-' + idx;

    let amountHtml;
    if (parsed.pct > 0) {
      const minVal = (ing.amount * (1 - parsed.pct / 100)).toFixed(2);
      const maxVal = (ing.amount * (1 + parsed.pct / 100)).toFixed(2);
      amountHtml = '<span class="variation-pills" data-key="' + key + '" data-min="' + minVal + '" data-base="' + ing.amount + '" data-max="' + maxVal + '">' +
        '<button class="var-pill var-min" data-state="min" aria-label="' + t('var_min_label') + '" title="' + t('var_min_title') + ' (−' + parsed.pct + '%)">' + minVal + '</button>' +
        '<button class="var-pill var-base active" data-state="base" aria-label="' + t('var_base_label') + '" title="' + t('var_base_label') + '">' + ing.amount + '</button>' +
        '<button class="var-pill var-max" data-state="max" aria-label="' + t('var_max_label') + '" title="' + t('var_max_title') + ' (+' + parsed.pct + '%)">' + maxVal + '</button>' +
      '</span>';
    } else {
      amountHtml = '<span class="ingredient-amount">' + ing.amount + '</span>';
    }

    return '<div class="ingredient-row' + (ing.is_optional ? ' optional' : '') + '">' +
      '<div class="ingredient-row-left">' +
        '<span class="ingredient-row-name">' + escHtml(window.__lang === 'bg' && ing.name_bg ? ing.name_bg : ing.name) + '</span>' +
        notes +
      '</div>' +
      '<div class="ingredient-row-right">' +
        badge +
        amountHtml +
        '<span class="ingredient-base-amount" onmouseenter="positionTooltip(this)" onmouseleave="hideTooltip(this)"><span class="tooltip-text">' + t('base_recipe_tooltip') + '</span> / ' + ing.base_amount + '</span>' +
        '<span class="ingredient-unit">g</span>' +
      '</div>' +
    '</div>';
  }).join('');

  const placeholder = document.getElementById('results-placeholder');
  placeholder.style.display = 'none';
  placeholder.innerHTML =
    '<span class="results-placeholder-icon" aria-hidden="true">🍸</span>' +
    '<p>' + t('results_placeholder') + '</p>';
  const panel = document.getElementById('results');
  panel.classList.add('show');
}