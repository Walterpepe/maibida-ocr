(function () {
  'use strict';

  var header = document.querySelector('[data-vh-header]');
  var reducedMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function syncHeader() {
    if (!header) return;
    header.classList.toggle('is-scrolled', window.scrollY > 12);
  }

  syncHeader();
  window.addEventListener('scroll', syncHeader, { passive: true });

  var menus = Array.prototype.slice.call(
    document.querySelectorAll('.vh-menu, .vh-language, .vh-mobile-menu')
  );

  menus.forEach(function (menu) {
    menu.addEventListener('toggle', function () {
      if (!menu.open) return;
      menus.forEach(function (other) {
        if (other !== menu) other.open = false;
      });
    });
  });

  document.addEventListener('click', function (event) {
    menus.forEach(function (menu) {
      if (!menu.contains(event.target)) menu.open = false;
    });
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    menus.forEach(function (menu) {
      if (menu.open) {
        menu.open = false;
        var summary = menu.querySelector('summary');
        if (summary) summary.focus();
      }
    });
  });

  var revealItems = Array.prototype.slice.call(
    document.querySelectorAll('[data-reveal]')
  );
  if (!revealItems.length || reducedMotion || !('IntersectionObserver' in window)) {
    return;
  }

  document.documentElement.classList.add('vh-motion-ready');
  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.12 }
  );

  revealItems.forEach(function (item, index) {
    item.style.transitionDelay = Math.min(index % 4, 3) * 60 + 'ms';
    observer.observe(item);
  });
})();
