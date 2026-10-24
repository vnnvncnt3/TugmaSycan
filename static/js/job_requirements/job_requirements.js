/* Job requirement editor: add/remove criterion rows (Django inline formset). */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('[data-criteria-form]');
  if (!form) return;

  const rows = form.querySelector('[data-criteria-rows]');
  const template = document.getElementById('criterion-template');
  const total = form.querySelector('input[name$="-TOTAL_FORMS"]');
  const emptyHint = form.querySelector('[data-criteria-empty]');
  const EXPERIENCE = 'EX';

  // Minimum years only applies to Experience criteria.
  function syncYears(row) {
    const type = row.querySelector('select[name$="-criterion_type"]');
    const years = row.querySelector('input[name$="-min_years"]');
    if (!type || !years) return;
    const enabled = type.value === EXPERIENCE;
    years.disabled = !enabled;
    years.title = enabled ? '' : 'Only used for Experience criteria';
  }

  function visibleRows() {
    return Array.from(rows.querySelectorAll('[data-criterion-row]')).filter((r) => !r.hidden);
  }

  function updateEmptyHint() {
    if (emptyHint) emptyHint.hidden = visibleRows().length > 0;
  }

  function addRow() {
    const index = parseInt(total.value, 10);
    const holder = document.createElement('div');
    holder.innerHTML = template.innerHTML.replace(/__prefix__/g, String(index)).trim();
    const row = holder.firstElementChild;
    rows.appendChild(row);
    total.value = String(index + 1);
    syncYears(row);
    updateEmptyHint();
    const first = row.querySelector('select, input:not([type="hidden"])');
    if (first) first.focus();
  }

  form.querySelector('[data-add-criterion]').addEventListener('click', addRow);

  rows.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-remove-criterion]');
    if (!btn) return;
    const row = btn.closest('[data-criterion-row]');
    const del = row.querySelector('input[name$="-DELETE"]');
    if (del) del.value = '1';   // server deletes saved rows and ignores unsaved ones
    row.hidden = true;
    updateEmptyHint();
  });

  rows.addEventListener('change', (e) => {
    if (e.target.matches('select[name$="-criterion_type"]')) syncYears(e.target.closest('[data-criterion-row]'));
  });

  rows.querySelectorAll('[data-criterion-row]').forEach(syncYears);
  updateEmptyHint();
});
