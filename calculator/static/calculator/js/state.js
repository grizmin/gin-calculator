/**
 * state.js — Mode switching and state persistence
 */

function getCurrentMode() {
  var distillActive = document.getElementById('mode-distill').classList.contains('active');
  return distillActive ? 'distill' : 'compound';
}

function setMode(mode) {
  if (mode === 'distill') {
    document.getElementById('compound-panel').setAttribute('hidden', '');
    document.getElementById('distill-panel').removeAttribute('hidden');
    document.getElementById('mode-compound').classList.remove('active');
    document.getElementById('mode-distill').classList.add('active');
    document.getElementById('mode-compound').setAttribute('aria-selected', 'false');
    document.getElementById('mode-distill').setAttribute('aria-selected', 'true');
  } else {
    document.getElementById('compound-panel').removeAttribute('hidden');
    document.getElementById('distill-panel').setAttribute('hidden', '');
    document.getElementById('mode-compound').classList.add('active');
    document.getElementById('mode-distill').classList.remove('active');
    document.getElementById('mode-compound').setAttribute('aria-selected', 'true');
    document.getElementById('mode-distill').setAttribute('aria-selected', 'false');
  }
}

function saveState() {
  var state = {
    recipeId: document.getElementById('recipe_select') ? document.getElementById('recipe_select').value : null,
    mode: getCurrentMode(),
    selectedStill: document.querySelector('.still-dropdown-item.active') ? document.querySelector('.still-dropdown-item.active').dataset.still : null,
    inputs: {}
  };
  var inputFields = ['input_spirit_abv', 'still_yield', 'maceration_abv', 'target_abv', 'volume',
                     'wash_volume', 'wash_abv', 'collection_abv', 'distill_target_abv'];
  inputFields.forEach(function(field) {
    var input = document.getElementById(field);
    if (input) { state.inputs[field] = input.value; }
  });
  localStorage.setItem('calculator_state', JSON.stringify(state));
}

function restoreState() {
  var savedState = localStorage.getItem('calculator_state');
  if (savedState) {
    var state = JSON.parse(savedState);
    var recipeSelect = document.getElementById('recipe_select');
    if (recipeSelect && state.recipeId) {
      recipeSelect.value = state.recipeId;
      onRecipeChange();
    }
    Object.entries(state.inputs).forEach(function(entry) {
      var field = entry[0], value = entry[1];
      var input = document.getElementById(field);
      if (input) { input.value = value; }
    });
    if (state.mode) {
      setMode(state.mode);
      if (state.mode === 'distill') {
        if (state.selectedStill) {
          selectStill(state.selectedStill);
        }
        calculateDistill();
      }
    }
  }
}
