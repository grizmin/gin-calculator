/**
 * Theme management for the Gin Calculator
 */

/**
 * Initialize theme based on saved preference or system preference
 */
export function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  } else if (prefersLight) {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
  updateThemeIcon();
}

/**
 * Update the theme icon in the UI
 */
export function updateThemeIcon() {
  const theme = document.documentElement.getAttribute('data-theme');
  const icon = document.querySelector('.theme-icon');
  if (icon) {
    icon.textContent = theme === 'light' ? '☀️' : '🌙';
  }
}

/**
 * Toggle between light and dark themes
 */
export function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  updateThemeIcon();
}

// Initialize theme when DOM is loaded
document.addEventListener('DOMContentLoaded', initTheme);