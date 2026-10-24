document.addEventListener('DOMContentLoaded', () => {
  const avatarInput = document.getElementById('avatarInput');
  const avatarLarge = document.querySelector('.avatar-large');
  if (avatarInput && avatarLarge) {
    avatarInput.addEventListener('change', () => {
      const file = avatarInput.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        avatarLarge.innerHTML = `<img src="${e.target.result}" alt="">`;
      };
      reader.readAsDataURL(file);
    });
  }
});