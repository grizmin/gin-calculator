/**
 * theme.js — Theme management
 */

function initTheme() {
  var savedTheme = localStorage.getItem('theme');
  var prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  } else if (prefersLight) {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
  updateThemeIcon();
}

function updateThemeIcon() {
  var theme = document.documentElement.getAttribute('data-theme');
  var icon = document.querySelector('.theme-icon');
  if (icon) {
    icon.textContent = theme === 'light' ? '\u2600\uFE0F' : '\uD83C\uDF19';
  }
}

function toggleTheme() {
  var currentTheme = document.documentElement.getAttribute('data-theme');
  var newTheme = currentTheme === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  updateThemeIcon();
}

document.addEventListener('DOMContentLoaded', initTheme);
