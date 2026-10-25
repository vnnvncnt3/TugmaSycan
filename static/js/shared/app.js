/* TugmaSycan — shared behaviour for the signed-in app (base_app.html). */
document.addEventListener('DOMContentLoaded', () => {
  /* Sidebar: fixed rail. Desktop: expand/collapse (remembered). Mobile: slide-in drawer.
     State lives on <html> (nav-expanded / nav-open); base_app.html sets nav-expanded
     before first paint so the rail does not animate on every page load. */
  const root = document.documentElement;
  const sidebar = document.getElementById('iconSidebar');
  const toggles = document.querySelectorAll('[data-sidebar-toggle]');
  const backdrop = document.querySelector('[data-sidebar-backdrop]');
  const mobile = window.matchMedia('(max-width: 860px)');
  const KEY = 'tugmasycan.sidebar';
  const stateClass = () => (mobile.matches ? 'nav-open' : 'nav-expanded');

  function syncAria() {
    const open = root.classList.contains(stateClass());
    toggles.forEach((b) => b.setAttribute('aria-expanded', String(open)));
  }

  function setOpen(open) {
    root.classList.toggle(stateClass(), open);
    if (!mobile.matches) {
      try { localStorage.setItem(KEY, open ? '1' : '0'); } catch (e) { /* storage unavailable */ }
    }
    syncAria();
  }

  if (sidebar) {
    root.classList.remove('nav-open');
    syncAria();
    toggles.forEach((b) => b.addEventListener('click', () => setOpen(!root.classList.contains(stateClass()))));
    if (backdrop) backdrop.addEventListener('click', () => setOpen(false));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && mobile.matches) setOpen(false); });
    mobile.addEventListener('change', () => { root.classList.remove('nav-open'); syncAria(); });
  }

  /* Dropzone: show chosen files, flag unsupported or oversized ones */
  document.querySelectorAll('[data-dropzone]').forEach((zone) => {
    const input = zone.querySelector('input[type="file"]');
    const list = zone.parentElement.querySelector('[data-file-list]');
    const summary = zone.parentElement.querySelector('[data-file-summary]');
    const allowed = (zone.dataset.accept || '').split(',').map((s) => s.trim().toLowerCase()).filter(Boolean);
    const maxBytes = (parseFloat(zone.dataset.maxMb) || 0) * 1024 * 1024;
    if (!input || !list) return;

    ['dragenter', 'dragover'].forEach((ev) => zone.addEventListener(ev, () => zone.classList.add('is-over')));
    ['dragleave', 'drop'].forEach((ev) => zone.addEventListener(ev, () => zone.classList.remove('is-over')));

    const fmt = (n) => (n >= 1048576 ? (n / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB');

    input.addEventListener('change', () => {
      list.textContent = '';
      let bad = 0;
      Array.from(input.files).forEach((file) => {
        const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
        const invalid = (allowed.length && !allowed.includes(ext)) || (maxBytes && file.size > maxBytes);
        if (invalid) bad += 1;
        const li = document.createElement('li');
        const name = document.createElement('span');
        const size = document.createElement('span');
        name.textContent = file.name + (invalid ? ' — not accepted' : '');
        size.textContent = fmt(file.size);
        size.className = 'file-size';
        if (invalid) li.className = 'is-invalid';
        li.append(name, size);
        list.appendChild(li);
      });
      if (summary) {
        const n = input.files.length;
        summary.textContent = n
          ? n + (n === 1 ? ' file selected' : ' files selected') + (bad ? ' · ' + bad + ' will be rejected' : '')
          : '';
      }
    });
  });

  /* Fair Review: mask names, emails and file names on this page */
  document.querySelectorAll('[data-fair-toggle]').forEach((box) => {
    const scope = box.closest('[data-fair-scope]');
    if (!scope) return;
    box.addEventListener('change', () => scope.classList.toggle('fair-on', box.checked));
  });

  /* Confirm destructive actions */
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (e) => { if (!window.confirm(form.dataset.confirm)) e.preventDefault(); });
  });

  /* Toasts fade out; errors stay until the page changes */
  document.querySelectorAll('.toast:not(.toast--error)').forEach((t) => setTimeout(() => t.remove(), 7000));
});
