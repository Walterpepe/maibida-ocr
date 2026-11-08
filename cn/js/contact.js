(function () {
  var form = document.getElementById('message-form');
  if (!form) return;
  var out = document.getElementById('form-status');
  var cfg = (document.currentScript && document.currentScript.dataset) || {};
  var btn = form.querySelector('button[type="submit"]');
  var consent = document.getElementById('cf-consent');
  function show(ok, msg) {
    out.className = 'cf-status ' + (ok ? 'ok' : 'err');
    out.textContent = msg;
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    out.className = 'cf-status';
    out.textContent = '';
    var d = {};
    ['name', 'email', 'phone', 'company', 'country', 'message'].forEach(function (k) {
      var el = form.elements[k];
      d[k] = el ? String(el.value || '').trim() : '';
    });
    if (!d.name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email) || !d.message) {
      show(false, cfg.invalid || 'Invalid input');
      return;
    }
    if (consent && !consent.checked) {
      show(false, cfg.consentRequired || 'Please accept the privacy policy.');
      if (consent.focus) consent.focus();
      return;
    }
    d.lang = document.documentElement.lang || 'zh-CN';
    d.source = location.pathname;
    d.consent = 'yes';
    d.consentVersion = cfg.policyVersion || '1.0';
    d.website = form.elements['website'] ? String(form.elements['website'].value || '') : '';
    btn.disabled = true;
    var ctrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 10000) : null;
    var opts = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(d)
    };
    if (ctrl) opts.signal = ctrl.signal;
    fetch('https://www.maibida.com/api/messages', opts).then(function (r) {
      return r.json().then(function (j) { return { ok: r.ok && !!j.ok, status: r.status }; })
        .catch(function () { return { ok: false, status: r.status }; });
    }).then(function (r) {
      show(r.ok, r.ok ? (cfg.success || 'OK') : (cfg.error || 'Error'));
      if (r.ok) form.reset();
    }).catch(function () {
      show(false, cfg.error || 'Error');
    }).then(function () {
      if (timer) clearTimeout(timer);
      btn.disabled = false;
    });
  });
})();
