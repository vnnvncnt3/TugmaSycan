document.addEventListener('DOMContentLoaded', () => {
  const darkToggle = document.querySelector('input[name="dark_mode"]');
  if (!darkToggle) return;

  const applyTheme = () => document.body.classList.toggle('dark', darkToggle.checked);
  applyTheme();
  darkToggle.addEventListener('change', applyTheme);
});