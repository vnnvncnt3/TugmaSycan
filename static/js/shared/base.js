document.addEventListener('DOMContentLoaded', () => {
  // Mega dropdown
  const megaHost = document.getElementById('megaHost');

  function positionHost() {
    if (!megaHost) return;
    const header = document.querySelector('.top-bar');
    if (header) {
      megaHost.style.top = `${header.getBoundingClientRect().bottom}px`;
    }
  }
  positionHost();
  window.addEventListener('resize', positionHost);
  window.addEventListener('scroll', positionHost);

  if (megaHost) {
    let closeTimer = null;

    function syncAria(name) {
      document.querySelectorAll('.nav-trigger').forEach((t) => t.setAttribute('aria-expanded', String(t.dataset.target === name)));
    }

    function showPanel(name) {
      clearTimeout(closeTimer);
      megaHost.querySelectorAll('.mega-panel').forEach((p) => {
        p.classList.toggle('open', p.dataset.panel === name);
      });
      syncAria(name);
    }

    function hideAll() {
      megaHost.querySelectorAll('.mega-panel').forEach((p) => p.classList.remove('open'));
      syncAria(null);
    }

    // A click "pins" a panel open (hover alone only previews it); Esc, an outside click,
    // or clicking the same button again closes it.
    let pinned = null;

    function scheduleHideAll() {
      if (pinned) return;
      closeTimer = setTimeout(hideAll, 200);
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { pinned = null; hideAll(); }
    });

    document.addEventListener('click', (e) => {
      if (!pinned) return;
      if (e.target.closest('.nav-item') || e.target.closest('#megaHost')) return;
      pinned = null;
      hideAll();
    });

    document.querySelectorAll('.nav-item').forEach((item) => {
      const trigger = item.querySelector('.nav-trigger');
      const name = trigger.dataset.target;
      item.addEventListener('mouseenter', () => showPanel(name));
      item.addEventListener('mouseleave', scheduleHideAll);
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        if (pinned === name) {
          pinned = null;
          hideAll();
        } else {
          pinned = name;
          showPanel(name);
        }
      });
    });

    megaHost.addEventListener('mouseenter', () => clearTimeout(closeTimer));
    megaHost.addEventListener('mouseleave', scheduleHideAll);
  }

  // Profile dropdown
  const trigger = document.getElementById('profileTrigger');
  const dropdown = document.getElementById('profileDropdown');
  if (trigger && dropdown) {
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = dropdown.classList.toggle('open');
      trigger.setAttribute('aria-expanded', isOpen);
    });
    document.addEventListener('click', () => {
      dropdown.classList.remove('open');
      trigger.setAttribute('aria-expanded', false);
    });
  }

  // Mobile menu
  const mobileToggle = document.getElementById('mobileMenuToggle');
  const mobileMenu = document.getElementById('mobileMenu');
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      mobileToggle.setAttribute('aria-expanded', isOpen);
    });

    document.querySelectorAll('.nav-item-mobile[data-target]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const submenu = mobileMenu.querySelector(`[data-submenu="${btn.dataset.target}"]`);
        if (submenu) submenu.classList.toggle('open');
      });
    });
  }

    // Icon sidebar toggle (Profile, Settings, Dashboard)
  const sidebar = document.getElementById('iconSidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebar && sidebarToggle) {
    sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('expanded'));
  }
});