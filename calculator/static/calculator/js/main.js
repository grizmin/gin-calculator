/**
 * Main entry point for the Gin Calculator JavaScript
 */

// Import all modules
import { escHtml, parseVariation, debounce, positionTooltip, hideTooltip } from './helpers.js';
import { initTheme, updateThemeIcon, toggleTheme } from './theme.js';
import { getCurrentMode, setMode, saveState, restoreState } from './state.js';
import { 
  loadRecipeDetails, onRecipeChange, renderRecipeImage, 
  renderRecipeDescription, calculateLocally, renderResults 
} from './calculator.js';
import { renderStillDropdown, selectStill, openStillDropdown, closeStillDropdown, toggleStillDropdown, calculateDistill } from './still-dropdown.js';

// Make functions available globally for inline event handlers in template
window.t = function(key) {
  var dict = window.__t[window.__lang] || window.__t['en'];
  return dict[key] || key;
};

window.getCurrentMode = getCurrentMode;
window.setMode = setMode;
window.saveState = saveState;
window.restoreState = restoreState;
window.loadRecipeDetails = loadRecipeDetails;
window.onRecipeChange = onRecipeChange;
window.renderRecipeImage = renderRecipeImage;
window.renderRecipeDescription = renderRecipeDescription;
window.calculateLocally = calculateLocally;
window.renderResults = renderResults;
window.escHtml = escHtml;
window.parseVariation = parseVariation;
window.positionTooltip = positionTooltip;
window.hideTooltip = hideTooltip;
window.selectStill = selectStill;
window.openStillDropdown = openStillDropdown;
window.closeStillDropdown = closeStillDropdown;
window.toggleStillDropdown = toggleStillDropdown;
window.calculateDistill = calculateDistill;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  // Restore saved state
  restoreState();
  
  // Set up event listeners
  document.getElementById('lang-toggle').addEventListener('click', function() {
    saveState();
    var currentLang = localStorage.getItem('lang') || 'en';
    var newLang = currentLang === 'bg' ? 'en' : 'bg';
    localStorage.setItem('lang', newLang);
    document.cookie = 'django_language=' + newLang + ';path=/;max-age=' + (365*24*60*60);
    window.location.reload();
  });

  // Theme toggle
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

  // Spirit type toggle
  document.querySelectorAll('input[name="spirit_type"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      const yieldInput = document.getElementById('still_yield');
      const abvLabel = document.getElementById('pb-abv-label');
      if (e.target.value === 'home') {
        yieldInput.value = 65;
        abvLabel.textContent = t('hearts_cut_abv');
      } else {
        yieldInput.value = 85;
        abvLabel.textContent = t('input_spirit_abv');
      }
      calculateLocally();
    });
  });

  // Mode switching
  document.getElementById('mode-compound').addEventListener('click', function() {
    setMode('compound');
    saveState();
  });

  document.getElementById('mode-distill').addEventListener('click', function() {
    setMode('distill');
    saveState();
    if (!document.getElementById('still-dropdown-name').textContent ||
        document.getElementById('still-dropdown-name').textContent === t('still_select')) {
      selectStill('vevor');
    }
    calculateDistill();
  });

  // Still dropdown
  document.getElementById('still-dropdown-toggle').addEventListener('click', toggleStillDropdown);

  document.addEventListener('click', function(e) {
    var dd = document.getElementById('still-dropdown');
    if (dd && !dd.contains(e.target)) {
      closeStillDropdown();
    }
  });

  // Set up input event listeners with debouncing
  const debouncedCalculate = debounce(calculateLocally, 120);
  ['volume', 'input_spirit_abv', 'target_abv', 'still_yield', 'maceration_abv'].forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      element.addEventListener('input', debouncedCalculate);
    }
  });

  // Set up ingredient variation pill click handler
  document.getElementById('ingredient-list').addEventListener('click', (e) => {
    const pill = e.target.closest('.var-pill');
    if (!pill) return;
    e.stopPropagation();
    const wrap = pill.closest('.variation-pills');
    wrap.querySelectorAll('.var-pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
  });

  // Render still dropdown on page load
  renderStillDropdown();
});