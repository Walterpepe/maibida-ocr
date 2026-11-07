(function () {
  var triggers = document.querySelectorAll('[data-wa-toggle]');
  if (!triggers.length) return;
  Array.prototype.forEach.call(triggers, function (btn) {
    var id = btn.getAttribute('aria-controls') || 'wa-consult-panel';
    var panel = document.getElementById(id);
    if (!panel) return;
    function setOpen(open) {
      panel.hidden = !open;
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var open = panel.hidden;
      setOpen(open);
      if (open) {
        var first = panel.querySelector('.wa-consult-btn');
        if (first && first.focus) first.focus({ preventScroll: true });
      }
    });
    var close = panel.querySelector('.wa-consult-close');
    if (close) close.addEventListener('click', function () {
      setOpen(false);
      if (btn.focus) btn.focus();
    });
    document.addEventListener('click', function (e) {
      if (panel.hidden) return;
      if (panel.contains(e.target) || btn === e.target || btn.contains(e.target)) return;
      setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if ((e.key === 'Escape' || e.keyCode === 27) && !panel.hidden) {
        setOpen(false);
        if (btn.focus) btn.focus();
      }
    });
  });
})();
