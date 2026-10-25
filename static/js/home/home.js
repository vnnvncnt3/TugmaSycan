document.addEventListener('DOMContentLoaded', () => {
  // Scroll reveal
  const revealItems = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('visible'));
  }

  // Process slideshow auto-advance
  const slideshow = document.getElementById('processSlideshow');
  if (!slideshow) return;

  const radios = Array.from(slideshow.querySelectorAll('input[type="radio"]'));
  let autoTimer = null;

  function goToNext() {
    const currentIndex = radios.findIndex((r) => r.checked);
    radios[(currentIndex + 1) % radios.length].checked = true;
  }

  function startAuto() {
    stopAuto();
    autoTimer = setInterval(goToNext, 4000);
  }

  function stopAuto() {
    if (autoTimer) clearInterval(autoTimer);
  }

  startAuto();
  slideshow.addEventListener('mouseenter', stopAuto);
  slideshow.addEventListener('mouseleave', startAuto);
  radios.forEach((radio) => radio.addEventListener('change', startAuto));
});