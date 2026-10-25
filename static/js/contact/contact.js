/* Contact: the form is a UI preview, so nothing is sent. Browser validation still runs first;
   once the fields are valid we stay on the page (and keep what was typed) and say so. */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('contactForm');
  const status = document.getElementById('contactStatus');
  if (!form || !status) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    status.textContent = 'Your message was not sent: this form is a preview and has no email service connected yet.';
    status.hidden = false;
  });
});
