/**
 * Shared JavaScript helpers for the Gin Calculator
 */

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} str - String to escape
 * @returns {string} Escaped string
 */
export function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/**
 * Parse ingredient variation notes (e.g. "±5%")
 * @param {string} notes - Notes string to parse
 * @returns {Object} Object with percentage value
 */
export function parseVariation(notes) {
  if (!notes) return { pct: 0 };
  const m = notes.match(/±(\d+)%/);
  return m ? { pct: parseInt(m[1], 10) } : { pct: 0 };
}

/**
 * Debounce function to limit execution frequency
 * @param {Function} fn - Function to debounce
 * @param {number} ms - Delay in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(fn, ms) {
  let timer;
  return function(...args) { 
    clearTimeout(timer); 
    timer = setTimeout(() => fn.apply(this, args), ms); 
  };
}

/**
 * Position tooltip for ingredient variations
 * @param {HTMLElement} el - Element containing tooltip
 */
export function positionTooltip(el) {
  const tip = el.querySelector('.tooltip-text');
  if (!tip) return;
  const rect = el.getBoundingClientRect();
  tip.style.setProperty('--tooltip-top', (rect.top - 8) + 'px');
  tip.style.setProperty('--tooltip-left', (rect.left + rect.width / 2) + 'px');
  tip.style.opacity = '1';
  tip.style.visibility = 'visible';
}

/**
 * Hide tooltip
 * @param {HTMLElement} el - Element containing tooltip
 */
export function hideTooltip(el) {
  const tip = el.querySelector('.tooltip-text');
  if (!tip) return;
  tip.style.opacity = '0';
  tip.style.visibility = 'hidden';
}