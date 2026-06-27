/**
 * main.js — Event binding and app initialization
 */

document.addEventListener('DOMContentLoaded', function() {
  // Language toggle
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
  document.querySelectorAll('input[name="spirit_type"]').forEach(function(radio) {
    radio.addEventListener('change', function(e) {
      var yieldInput = document.getElementById('still_yield');
      var abvLabel = document.getElementById('pb-abv-label');
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
    var dropdownName = document.getElementById('still-dropdown-name').textContent;
    if (!dropdownName || dropdownName === t('still_select')) {
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

  // Ingredient variation pill click handler
  document.getElementById('ingredient-list').addEventListener('click', function(e) {
    var pill = e.target.closest('.var-pill');
    if (!pill) return;
    e.stopPropagation();
    var wrap = pill.closest('.variation-pills');
    wrap.querySelectorAll('.var-pill').forEach(function(p) { p.classList.remove('active'); });
    pill.classList.add('active');
  });

  // Compound calculator input listeners
  var debouncedCalculate = debounce(calculateLocally, 120);
  ['volume', 'input_spirit_abv', 'target_abv', 'still_yield', 'maceration_abv'].forEach(function(id) {
    var element = document.getElementById(id);
    if (element) {
      element.addEventListener('input', debouncedCalculate);
    }
  });

  // Distill calculator input listeners
  var debouncedDistill = debounce(calculateDistill, 120);
  ['wash_volume', 'wash_abv', 'collection_abv', 'distill_target_abv'].forEach(function(id) {
    var element = document.getElementById(id);
    if (element) {
      element.addEventListener('input', debouncedDistill);
    }
  });
});

window.addEventListener('load', function() {
  renderStillDropdown();
  onRecipeChange();
  restoreState();
});
