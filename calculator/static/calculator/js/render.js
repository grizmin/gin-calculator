/**
 * render.js — DOM rendering functions
 */

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function renderRecipeImage(recipe) {
  var wrap = document.getElementById('recipe-image-wrap');
  var img = document.getElementById('recipe-image');
  if (!wrap || !img) return;
  var url = (recipe.image_url || '').trim();
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

function renderRecipeDescription(recipe) {
  var el = document.getElementById('recipe-description');
  if (recipe.description) {
    var safeName = escHtml(recipe.name);
    el.innerHTML = '<strong>' + safeName + '</strong>' + escHtml(recipe.description);
    el.classList.add('show');
  } else {
    el.classList.remove('show');
  }
}

function renderResults(data) {
  document.getElementById('spirit-load-value').textContent = data.spirit_to_load || data.spirit_needed;
  document.getElementById('maceration-water-value').textContent = data.maceration_water;
  document.getElementById('water-value').textContent = data.water_to_add;
  document.getElementById('result-recipe-name').textContent = data.recipe_name;

  var list = document.getElementById('ingredient-list');
  list.innerHTML = data.scaled_ingredients.map(function(ing, idx) {
    var parsed = parseVariation(ing.notes);
    var notes = ing.notes ? '<span class="ingredient-row-notes">' + escHtml(ing.notes) + '</span>' : '';
    var badge = ing.is_optional ? '<span class="optional-badge">' + t('optional_badge') + '</span>' : '';
    var key = 'var-' + idx;

    var amountHtml;
    if (parsed.pct > 0) {
      var minVal = (ing.amount * (1 - parsed.pct / 100)).toFixed(2);
      var maxVal = (ing.amount * (1 + parsed.pct / 100)).toFixed(2);
      amountHtml = '<span class="variation-pills" data-key="' + key + '" data-min="' + minVal + '" data-base="' + ing.amount + '" data-max="' + maxVal + '">' +
        '<button class="var-pill var-min" data-state="min" aria-label="' + t('var_min_label') + '" title="' + t('var_min_title') + ' (\u2212' + parsed.pct + '%)">' + minVal + '</button>' +
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

  var placeholder = document.getElementById('results-placeholder');
  placeholder.style.display = 'none';
  placeholder.innerHTML =
    '<span class="results-placeholder-icon" aria-hidden="true">\uD83C\uDF78</span>' +
    '<p>' + t('results_placeholder') + '</p>';
  var panel = document.getElementById('results');
  panel.classList.add('show');
}

function positionTooltip(el) {
  var tip = el.querySelector('.tooltip-text');
  if (!tip) return;
  var rect = el.getBoundingClientRect();
  tip.style.setProperty('--tooltip-top', (rect.top - 8) + 'px');
  tip.style.setProperty('--tooltip-left', (rect.left + rect.width / 2) + 'px');
  tip.style.opacity = '1';
  tip.style.visibility = 'visible';
}

function hideTooltip(el) {
  var tip = el.querySelector('.tooltip-text');
  if (!tip) return;
  tip.style.opacity = '0';
  tip.style.visibility = 'hidden';
}
