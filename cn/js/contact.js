(function () {
  var form = document.getElementById('message-form');
  if (!form) return;
  var out = document.getElementById('form-status');
  var cfg = (document.currentScript && document.currentScript.dataset) || {};
  var btn = form.querySelector('button[type="submit"]');
  var consent = document.getElementById('cf-consent');
  var endpoint = form.getAttribute('action') || '/api/messages';
  var submitText = btn ? btn.textContent : '';

  function setInvalid(field, invalid) {
    if (!field) return;
    if (invalid) field.setAttribute('aria-invalid', 'true');
    else field.removeAttribute('aria-invalid');
  }

  function clearInvalid() {
    ['name', 'email', 'phone', 'company', 'country', 'message', 'consent']
      .forEach(function (key) {
        setInvalid(form.elements[key], false);
      });
  }

  function show(kind, msg) {
    out.className = 'cf-status ' + kind;
    out.textContent = msg;
  }

  function setBusy(busy) {
    form.setAttribute('aria-busy', busy ? 'true' : 'false');
    if (!btn) return;
    btn.disabled = busy;
    btn.textContent = busy ? (cfg.submitting || '...') : submitText;
  }

  function firstInvalid(fields) {
    var first = fields.find(function (field) { return field; });
    if (first && first.focus) first.focus();
    return first;
  }

  form.addEventListener('input', function (e) {
    if (e.target && e.target.getAttribute('aria-invalid') === 'true') {
      setInvalid(e.target, false);
    }
  });

  form.addEventListener('change', function (e) {
    if (e.target && e.target.getAttribute('aria-invalid') === 'true') {
      setInvalid(e.target, false);
    }
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    clearInvalid();
    out.className = 'cf-status';
    out.textContent = '';
    var d = {};
    ['name', 'email', 'phone', 'company', 'country', 'message'].forEach(function (k) {
      var el = form.elements[k];
      d[k] = el ? String(el.value || '').trim() : '';
    });
    var invalid = [
      !d.name && form.elements.name,
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email) && form.elements.email,
      !d.message && form.elements.message
    ].filter(Boolean);
    if (invalid.length) {
      invalid.forEach(function (field) { setInvalid(field, true); });
      firstInvalid(invalid);
      show('err', cfg.invalid || 'Invalid input');
      return;
    }
    if (consent && !consent.checked) {
      setInvalid(consent, true);
      if (consent.focus) consent.focus();
      show('err', cfg.consentRequired || 'Please accept the privacy policy.');
      return;
    }
    d.lang = document.documentElement.lang || 'zh-CN';
    d.source = location.pathname;
    d.consent = 'yes';
    d.consentVersion = cfg.policyVersion || '1.0';
    d.website = form.elements['website'] ? String(form.elements['website'].value || '') : '';
    setBusy(true);
    show('pending', cfg.submitting || '...');
    var ctrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 10000) : null;
    var opts = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(d)
    };
    if (ctrl) opts.signal = ctrl.signal;
    fetch(endpoint, opts).then(function (r) {
      return r.json().then(function (j) { return { ok: r.ok && !!j.ok, status: r.status }; })
        .catch(function () { return { ok: false, status: r.status }; });
    }).then(function (r) {
      if (r.ok) {
        show('ok', cfg.success || 'OK');
        // GA4/GTM 标准转化事件:询盘提交成功
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
          event: 'generate_lead',
          lead_source: location.pathname,
          language: document.documentElement.lang || 'zh-CN'
        });
        form.reset();
        clearInvalid();
      } else {
        show('err', cfg.error || 'Error');
      }
    }).catch(function () {
      show('err', cfg.error || 'Error');
    }).then(function () {
      if (timer) clearTimeout(timer);
      setBusy(false);
    });
  });
})();
