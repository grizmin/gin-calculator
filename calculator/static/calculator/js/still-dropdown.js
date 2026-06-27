/**
 * still-dropdown.js — Still dropdown behavior
 * Uses window.STILL_PRESETS (provided inline in template).
 */

function renderStillDropdown() {
  var menu = document.getElementById('still-dropdown-menu');
  if (!menu) return;
  menu.innerHTML = '';
  Object.keys(window.STILL_PRESETS).forEach(function(key) {
    var p = window.STILL_PRESETS[key];
    var li = document.createElement('li');
    li.className = 'still-dropdown-item';
    li.setAttribute('role', 'option');
    li.setAttribute('data-still', key);
    li.innerHTML = '<div class="still-dropdown-thumb"><img src="' + p.image + '" alt=""></div>' +
      '<div class="still-dropdown-text">' +
        '<span class="still-dropdown-name">' + t(p.nameKey) + '</span>' +
        '<span class="still-dropdown-desc">' + t(p.descKey) + '</span>' +
      '</div>';
    li.addEventListener('click', function() { selectStill(key); });
    menu.appendChild(li);
  });
}

function selectStill(presetKey) {
  var preset = window.STILL_PRESETS[presetKey];
  if (!preset) return;

  document.getElementById('still-dropdown-name').textContent = t(preset.nameKey);
  document.getElementById('still-dropdown-desc').textContent = t(preset.descKey);
  document.getElementById('still-dropdown-thumb').innerHTML = '<img src="' + preset.image + '" alt="">';

  document.querySelectorAll('.still-dropdown-item').forEach(function(item) {
    item.classList.toggle('active', item.dataset.still === presetKey);
  });

  document.getElementById('wash_volume').value = preset.wash_volume;
  document.getElementById('wash_abv').value = preset.wash_abv;
  document.getElementById('collection_abv').value = preset.collection_abv;
  document.getElementById('distill_target_abv').value = preset.distill_target_abv;

  closeStillDropdown();
  saveState();
  calculateDistill();
}

function openStillDropdown() {
  var menu = document.getElementById('still-dropdown-menu');
  var toggle = document.getElementById('still-dropdown-toggle');
  menu.removeAttribute('hidden');
  toggle.setAttribute('aria-expanded', 'true');
}

function closeStillDropdown() {
  var menu = document.getElementById('still-dropdown-menu');
  var toggle = document.getElementById('still-dropdown-toggle');
  if (menu && toggle) {
    menu.setAttribute('hidden', '');
    toggle.setAttribute('aria-expanded', 'false');
  }
}

function toggleStillDropdown() {
  var menu = document.getElementById('still-dropdown-menu');
  if (menu.hasAttribute('hidden')) {
    openStillDropdown();
  } else {
    closeStillDropdown();
  }
}
