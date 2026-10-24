const EYE_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/></svg>';
const EYE_OFF_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.94 10.94 0 0112 19c-7 0-11-7-11-7a21.8 21.8 0 015.06-6.06M9.9 4.24A10.94 10.94 0 0112 4c7 0 11 7 11 7a21.8 21.8 0 01-3.22 4.48M1 1l22 22"/></svg>';

document.addEventListener('DOMContentLoaded', () => {
  const passwordField = document.querySelector('input[type="password"]');
  if (!passwordField) return;

  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'password-toggle';
  toggle.innerHTML = EYE_ICON;
  toggle.setAttribute('aria-label', 'Show password');
  passwordField.insertAdjacentElement('afterend', toggle);

  toggle.addEventListener('click', () => {
    const isHidden = passwordField.type === 'password';
    passwordField.type = isHidden ? 'text' : 'password';
    toggle.innerHTML = isHidden ? EYE_OFF_ICON : EYE_ICON;
    toggle.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
  });
});