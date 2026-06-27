/**
 * calculator.js — Calculation engine and recipe loading
 */

var currentRecipe = null;

function loadRecipeDetails(recipeId) {
  return fetch('/get-recipe/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recipe_id: parseInt(recipeId) }),
  })
  .then(function(res) { return res.json(); })
  .then(function(data) {
    if (!data.success) { console.error('Recipe load error:', data.error); return null; }
    currentRecipe = data.recipe;
    renderRecipeImage(data.recipe);
    renderRecipeDescription(data.recipe);
    var targetInput = document.getElementById('target_abv');
    if (targetInput && data.recipe.target_abv_percentage) {
      targetInput.value = data.recipe.target_abv_percentage;
    }
    return data.recipe;
  })
  .catch(function(err) {
    console.error('Failed to load recipe:', err);
    throw err;
  });
}

function onRecipeChange() {
  var select = document.getElementById('recipe_select');
  var recipeId = select.value;
  return loadRecipeDetails(recipeId).then(function() {
    calculateLocally();
  });
}

function calculateLocally() {
  var volume = parseFloat(document.getElementById('volume').value);
  var inputSpiritAbv = parseFloat(document.getElementById('input_spirit_abv').value);
  var targetAbv = parseFloat(document.getElementById('target_abv').value);
  var stillYield = parseFloat(document.getElementById('still_yield').value) || 85;
  var macerationAbv = parseFloat(document.getElementById('maceration_abv').value);

  if (!currentRecipe) return;
  if (!volume || volume <= 0) return;
  if (!inputSpiritAbv || inputSpiritAbv <= 0) return;
  if (!targetAbv || targetAbv <= 0) return;

  if (!macerationAbv || macerationAbv <= 0 || macerationAbv >= inputSpiritAbv) {
    document.getElementById('results-placeholder').style.display = '';
    document.getElementById('results').classList.remove('show');
    document.getElementById('results-placeholder').innerHTML =
      '<span class="results-placeholder-icon" aria-hidden="true">\u26A0\uFE0F</span>' +
      '<p>' + t('error_maceration_abv_lower') + '</p>';
    return;
  }

  var scaleFactor = volume / currentRecipe.base_volume;
  var scaledIngredients = currentRecipe.ingredients.map(function(ing) {
    return {
      name: ing.name,
      name_bg: ing.name_bg,
      amount: Math.round(ing.amount * scaleFactor * 100) / 100,
      base_amount: ing.amount,
      is_optional: ing.is_optional,
      notes: ing.notes
    };
  });

  var spiritNeeded = Math.round(
    ((volume * targetAbv / 100) / (inputSpiritAbv / 100)) * 100
  ) / 100;
  var waterToAdd = Math.round((volume - spiritNeeded) * 100) / 100;

  if (waterToAdd < 0) {
    document.getElementById('results-placeholder').style.display = '';
    document.getElementById('results').classList.remove('show');
    document.getElementById('results-placeholder').innerHTML =
      '<span class="results-placeholder-icon" aria-hidden="true">\u26A0\uFE0F</span>' +
      '<p>' + t('error_spirit_abv_higher') + '</p>';
    return;
  }

  var spiritToLoad = Math.round((spiritNeeded / (stillYield / 100)) * 100) / 100;
  var waterForMaceration = Math.round(
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

function parseVariation(notes) {
  if (!notes) return { pct: 0 };
  var m = notes.match(/[\u00B1](\d+)%/);
  return m ? { pct: parseInt(m[1], 10) } : { pct: 0 };
}

function debounce(fn, ms) {
  var timer;
  return function() {
    var args = arguments;
    var context = this;
    clearTimeout(timer);
    timer = setTimeout(function() { fn.apply(context, args); }, ms);
  };
}

function calculateDistill() {
  var washVolume = parseFloat(document.getElementById('wash_volume').value);
  var washAbv = parseFloat(document.getElementById('wash_abv').value);
  var collectionAbv = parseFloat(document.getElementById('collection_abv').value);
  var targetAbv = parseFloat(document.getElementById('distill_target_abv').value);

  if (!washVolume || washVolume <= 0) return;
  if (!washAbv || washAbv <= 0) return;
  if (!collectionAbv || collectionAbv <= 0) return;
  if (!targetAbv || targetAbv <= 0) return;

  var pureAlcohol = Math.round(washVolume * washAbv / 100 * 100) / 100;
  var expectedDistillate = Math.round((pureAlcohol / (collectionAbv / 100)) * 100) / 100;
  var waterToProof = Math.round((expectedDistillate * (collectionAbv / targetAbv - 1)) * 100) / 100;

  document.getElementById('d-pure-alcohol').textContent = pureAlcohol.toFixed(2);
  document.getElementById('d-expected-distillate').textContent = expectedDistillate.toFixed(2);
  document.getElementById('d-water-to-proof').textContent = waterToProof > 0 ? waterToProof.toFixed(2) : '0.00';
  document.getElementById('d-batches-needed').textContent = '1';

  var placeholder = document.getElementById('distill-results-placeholder');
  placeholder.style.display = 'none';
  var panel = document.getElementById('distill-results');
  panel.classList.add('show');
}
