/* Run screening: "Select all" and a live count of chosen batches / resumes. */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('[data-run-form]');
  if (!form) return;

  const boxes = Array.from(form.querySelectorAll('input[name="batches"]'));
  const summary = form.querySelector('[data-batch-summary]');
  const selectAll = form.querySelector('[data-select-all]');

  function update() {
    const chosen = boxes.filter((b) => b.checked);
    const resumes = chosen.reduce((sum, b) => sum + (parseInt(b.dataset.resumes, 10) || 0), 0);
    if (summary) {
      summary.textContent = chosen.length
        ? chosen.length + (chosen.length === 1 ? ' batch' : ' batches') + ' selected · ' + resumes + (resumes === 1 ? ' resume' : ' resumes')
        : '';
    }
    if (selectAll) selectAll.textContent = chosen.length === boxes.length ? 'Clear all' : 'Select all';
  }

  if (selectAll) {
    selectAll.addEventListener('click', () => {
      const everyChecked = boxes.every((b) => b.checked);
      boxes.forEach((b) => { b.checked = !everyChecked; });
      update();
    });
  }
  boxes.forEach((b) => b.addEventListener('change', update));
  update();
});
