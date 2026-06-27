/**
 * State management for the Gin Calculator
 */

/**
 * Get current mode (compound or distill)
 * @returns {string} Current mode
 */
export function getCurrentMode() {
  const distillActive = document.getElementById('mode-distill').classList.contains('active');
  return distillActive ? 'distill' : 'compound';
}

/**
 * Set the current mode
 * @param {string} mode - Mode to set ('compound' or 'distill')
 */
export function setMode(mode) {
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

/**
 * Save current state to localStorage
 */
export function saveState() {
  const state = {
    recipeId: document.getElementById('recipe_select') ? document.getElementById('recipe_select').value : null,
    mode: getCurrentMode(),
    selectedStill: document.querySelector('.still-dropdown-item.active') ? document.querySelector('.still-dropdown-item.active').dataset.still : null,
    inputs: {}
  };
  const inputFields = ['input_spirit_abv', 'still_yield', 'maceration_abv', 'target_abv', 'volume',
                       'wash_volume', 'wash_abv', 'collection_abv', 'distill_target_abv'];
  inputFields.forEach(field => {
    const input = document.getElementById(field);
    if (input) { state.inputs[field] = input.value; }
  });
  localStorage.setItem('calculator_state', JSON.stringify(state));
}

/**
 * Restore state from localStorage
 */
export function restoreState() {
  const savedState = localStorage.getItem('calculator_state');
  if (savedState) {
    const state = JSON.parse(savedState);
    const recipeSelect = document.getElementById('recipe_select');
    if (recipeSelect && state.recipeId) {
      recipeSelect.value = state.recipeId;
      // Trigger recipe change to load recipe data and update UI
      onRecipeChange();
    }
    for (const [field, value] of Object.entries(state.inputs)) {
      const input = document.getElementById(field);
      if (input) { input.value = value; }
    }
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