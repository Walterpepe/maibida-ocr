"""Add a localized message form to the static site (idempotent).

Creates 11 standalone contact pages (zh-CN + 10 locales), a shared CSS/JS,
injects one localized nav link into each of the 88 formal pages, appends the
nav style to site-multilingual.css, and registers the new pages as tool pages
in the site audit. Existing page bytes are only touched at the insertion point.
"""
import html
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compliance_i18n as C
import whatsapp_content as W

ROOT = Path(__file__).resolve().parent.parent
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT.parent / f"maibida-ocr-rebuilt_contact_backup_{TS}"

LOCALES = ["en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN",
           "ko-KR", "ja-JP", "ms-MY", "ru-RU"]
LANGS = ["zh-CN"] + LOCALES
PAGES = ["index.html", "product/10032.html", "product/smart-camera.html",
         "productlist/10029.html", "productlist/10030.html",
         "productlist/10034.html", "productlist/10036.html",
         "productlist/10039.html"]

EN = {
    "nav": "Contact", "title": "Leave a Message", "heading": "Leave a Message",
    "intro": "Fill in the form below and we will get back to you shortly.",
    "name": "Name", "email": "Email", "phone": "Phone", "company": "Company",
    "country": "Country/Region", "message": "Message",
    "placeholder": "Tell us about your requirements, equipment model or application...",
    "submit": "Send Message",
    "privacy": "By submitting, you agree that we use these details only to reply to your enquiry.",
    "back": "Back to home",
    "success": "Thank you. We will get back to you shortly.",
    "error": "Could not send. Please try again later.",
    "invalid": "Please provide your name, a valid email and a message.",
}

I18N = {
    "zh-CN": {
        "nav": "留言反馈", "title": "留言反馈", "heading": "留言反馈",
        "intro": "填写下表提交您的需求，我们会尽快与您联系。",
    "name": "姓名", "email": "邮箱", "phone": "电话", "company": "公司",
    "country": "国家/地区", "message": "留言内容",
        "placeholder": "请描述您的需求、设备型号或应用场景…",
        "submit": "提交留言",
        "privacy": "提交即表示同意我们仅将上述信息用于回复本次咨询。",
        "back": "返回首页",
        "success": "提交成功，我们会尽快与您联系。",
        "error": "提交失败，请稍后重试。",
        "invalid": "请填写姓名、有效邮箱和留言内容。",
    },
    "en-US": dict(EN),
    "en-SG": dict(EN, title="Leave a Message (Singapore / Asia-Pacific)"),
    "es-MX": {
        "nav": "Contacto", "title": "Enviar un mensaje", "heading": "Enviar un mensaje",
        "intro": "Complete el formulario y le responderemos a la brevedad.",
        "name": "Nombre", "email": "Correo electrónico", "phone": "Teléfono",
        "company": "Empresa", "country": "País/Región", "message": "Mensaje",
        "placeholder": "Describa sus necesidades, el modelo de equipo o la aplicación...",
        "submit": "Enviar mensaje",
        "privacy": "Al enviar, acepta que usemos estos datos solo para responder a su consulta.",
        "back": "Volver al inicio",
        "success": "Gracias. Le responderemos a la brevedad.",
        "error": "No se pudo enviar. Intente de nuevo más tarde.",
        "invalid": "Proporcione su nombre, un correo válido y un mensaje.",
    },
    "id-ID": {
        "nav": "Kontak", "title": "Kirim Pesan", "heading": "Kirim Pesan",
        "intro": "Isi formulir di bawah ini dan kami akan segera menghubungi Anda.",
        "name": "Nama", "email": "Email", "phone": "Telepon",
        "company": "Perusahaan", "country": "Negara/Wilayah", "message": "Pesan",
        "placeholder": "Jelaskan kebutuhan, model peralatan atau aplikasi Anda...",
        "submit": "Kirim Pesan",
        "privacy": "Dengan mengirim, Anda menyetujui penggunaan data ini hanya untuk menanggapi pertanyaan Anda.",
        "back": "Kembali ke beranda",
        "success": "Terima kasih. Kami akan segera menghubungi Anda.",
        "error": "Gagal mengirim. Silakan coba lagi nanti.",
        "invalid": "Mohon isi nama, email yang valid, dan pesan.",
    },
    "th-TH": {
        "nav": "ติดต่อ", "title": "ส่งข้อความ", "heading": "ส่งข้อความ",
        "intro": "กรอกแบบฟอร์มด้านล่าง แล้วเราจะติดต่อกลับโดยเร็ว",
        "name": "ชื่อ", "email": "อีเมล", "phone": "โทรศัพท์",
        "company": "บริษัท", "country": "ประเทศ/ภูมิภาค", "message": "ข้อความ",
        "placeholder": "อธิบายความต้องการ รุ่นอุปกรณ์ หรือการใช้งานของคุณ...",
        "submit": "ส่งข้อความ",
        "privacy": "การส่งถือว่าคุณยินยอมให้เราใช้ข้อมูลนี้เพื่อตอบคำถามของคุณเท่านั้น",
        "back": "กลับสู่หน้าแรก",
        "success": "ขอบคุณ เราจะติดต่อกลับโดยเร็ว",
        "error": "ส่งไม่สำเร็จ กรุณาลองใหม่ภายหลัง",
        "invalid": "กรุณากรอกชื่อ อีเมลที่ถูกต้อง และข้อความ",
    },
    "vi-VN": {
        "nav": "Liên hệ", "title": "Gửi tin nhắn", "heading": "Gửi tin nhắn",
        "intro": "Điền vào biểu mẫu bên dưới, chúng tôi sẽ phản hồi sớm nhất có thể.",
        "name": "Họ tên", "email": "Email", "phone": "Điện thoại",
        "company": "Công ty", "country": "Quốc gia/Khu vực", "message": "Nội dung",
        "placeholder": "Mô tả nhu cầu, model thiết bị hoặc ứng dụng của bạn...",
        "submit": "Gửi tin nhắn",
        "privacy": "Khi gửi, bạn đồng ý chúng tôi chỉ dùng thông tin này để phản hồi yêu cầu của bạn.",
        "back": "Về trang chủ",
        "success": "Cảm ơn bạn. Chúng tôi sẽ phản hồi sớm.",
        "error": "Gửi không thành công. Vui lòng thử lại sau.",
        "invalid": "Vui lòng điền họ tên, email hợp lệ và nội dung.",
    },
    "ko-KR": {
        "nav": "문의", "title": "문의하기", "heading": "문의하기",
        "intro": "아래 양식을 작성해 주시면 빠르게 연락드리겠습니다.",
        "name": "이름", "email": "이메일", "phone": "전화번호",
        "company": "회사", "country": "국가/지역", "message": "문의 내용",
        "placeholder": "요구 사항, 장비 모델 또는 적용 분야를 알려주세요...",
        "submit": "문의 보내기",
        "privacy": "제출 시 위 정보가 문의 회신에만 사용됨에 동의하게 됩니다.",
        "back": "홈으로",
        "success": "감사합니다. 빠르게 연락드리겠습니다.",
        "error": "전송에 실패했습니다. 잠시 후 다시 시도해 주세요.",
        "invalid": "이름, 유효한 이메일, 문의 내용을 입력해 주세요.",
    },
    "ja-JP": {
        "nav": "お問い合わせ", "title": "お問い合わせ", "heading": "お問い合わせ",
        "intro": "下記フォームにご記入いただければ、担当者よりご連絡いたします。",
        "name": "お名前", "email": "メールアドレス", "phone": "電話番号",
        "company": "会社名", "country": "国・地域", "message": "お問い合わせ内容",
        "placeholder": "ご要望、装置の型番、用途などをご記入ください…",
        "submit": "送信する",
        "privacy": "送信により、上記情報を本件の返信にのみ使用することに同意したものとみなされます。",
        "back": "ホームへ戻る",
        "success": "送信しました。担当者よりご連絡いたします。",
        "error": "送信できませんでした。しばらくしてからもう一度お試しください。",
        "invalid": "お名前、有効なメールアドレス、お問い合わせ内容をご記入ください。",
    },
    "ms-MY": {
        "nav": "Hubungi", "title": "Hantar Mesej", "heading": "Hantar Mesej",
        "intro": "Isi borang di bawah dan kami akan menghubungi anda secepat mungkin.",
        "name": "Nama", "email": "E-mel", "phone": "Telefon",
        "company": "Syarikat", "country": "Negara/Wilayah", "message": "Mesej",
        "placeholder": "Terangkan keperluan, model peralatan atau aplikasi anda...",
        "submit": "Hantar Mesej",
        "privacy": "Dengan menghantar, anda bersetuju kami menggunakan maklumat ini hanya untuk membalas pertanyaan anda.",
        "back": "Kembali ke laman utama",
        "success": "Terima kasih. Kami akan menghubungi anda tidak lama lagi.",
        "error": "Gagal menghantar. Sila cuba lagi kemudian.",
        "invalid": "Sila isi nama, e-mel yang sah dan mesej.",
    },
    "ru-RU": {
        "nav": "Контакты", "title": "Отправить сообщение", "heading": "Отправить сообщение",
        "intro": "Заполните форму ниже, и мы свяжемся с вами в ближайшее время.",
        "name": "Имя", "email": "Эл. почта", "phone": "Телефон",
        "company": "Компания", "country": "Страна/Регион", "message": "Сообщение",
        "placeholder": "Опишите ваши требования, модель оборудования или область применения...",
        "submit": "Отправить",
        "privacy": "Отправляя форму, вы соглашаетесь, что данные используются только для ответа на ваш запрос.",
        "back": "На главную",
        "success": "Спасибо. Мы свяжемся с вами в ближайшее время.",
        "error": "Не удалось отправить. Повторите попытку позже.",
        "invalid": "Укажите имя, корректный e-mail и текст сообщения.",
    },
}

# Prelaunch remediation: localized <meta description>, canonical URL and the
# overseas WhatsApp entry point. Kept separate from I18N so the generator stays
# idempotent and the 11 contact pages remain reproducible.
WA_NUMBER = W.WA_NUMBER  # from the Organization JSON-LD: +86-159-9567-5085
WA_URL = W.WA_BASE

DESCRIPTIONS = {
    "zh-CN": "联系昆山迈必达智能设备有限公司，提交机器视觉光源、模具监视器与智能相机的产品咨询或定制需求，我们将尽快回复。",
    "en-US": "Contact Maibida for machine vision lights, mold monitors and smart cameras. Send your enquiry or OEM requirement and our team will reply shortly.",
    "en-SG": "Contact Maibida for machine vision lights, mould monitors and smart cameras. Send your enquiry or OEM requirement and our team will reply shortly.",
    "es-MX": "Contacte a Maibida para iluminación de visión artificial, monitores de molde y cámaras inteligentes. Envíe su consulta y le responderemos pronto.",
    "id-ID": "Hubungi Maibida untuk lampu machine vision, pemantau cetakan dan kamera pintar. Kirim pertanyaan Anda dan tim kami akan segera membalas.",
    "th-TH": "ติดต่อ Maibida สำหรับไฟ Machine Vision ระบบตรวจสอบแม่พิมพ์และกล้องอัจฉริยะ ส่งคำถามของคุณมาให้เราตอบกลับโดยเร็ว",
    "vi-VN": "Liên hệ Maibida về đèn thị giác máy, hệ thống giám sát khuôn và camera thông minh. Gửi yêu cầu của bạn, chúng tôi sẽ phản hồi sớm.",
    "ko-KR": "머신비전 조명, 금형 감시기, 스마트 카메라 관련 문의는 Maibida에 남겨주세요. 담당자가 빠르게 회신드립니다.",
    "ja-JP": "マシンビジョン用照明、金型監視装置、スマートカメラに関するお問い合わせは Maibida へ。ご要望をお送りください。担当者より折り返しご連絡いたします。",
    "ms-MY": "Hubungi Maibida untuk lampu penglihatan mesin, pemantau acuan dan kamera pintar. Hantar pertanyaan anda dan kami akan membalas tidak lama lagi.",
    "ru-RU": "Свяжитесь с Maibida по вопросам освещения для машинного зрения, систем контроля пресс-форм и смарт-камер. Отправьте запрос — мы ответим в ближайшее время.",
}

WA_LABELS = {
    "zh-CN": "WhatsApp 咨询", "en-US": "WhatsApp", "en-SG": "WhatsApp",
    "es-MX": "WhatsApp", "id-ID": "WhatsApp", "th-TH": "WhatsApp",
    "vi-VN": "WhatsApp", "ko-KR": "WhatsApp 문의", "ja-JP": "WhatsApp で問い合わせ",
    "ms-MY": "WhatsApp", "ru-RU": "WhatsApp",
}

# Shown when /api/messages is unavailable (e.g. a pure static host). The
# mailto fallback guarantees an enquiry channel even without the Node service.
FALLBACK = {
    "zh-CN": "若提交失败，也可直接发送邮件至", "en-US": "If submission fails, you can also email",
    "en-SG": "If submission fails, you can also email", "es-MX": "Si falla el envío, también puede escribir a",
    "id-ID": "Jika pengiriman gagal, Anda juga dapat mengirim email ke",
    "th-TH": "หากส่งไม่สำเร็จ คุณสามารถส่งอีเมลไปที่",
    "vi-VN": "Nếu gửi không thành công, bạn cũng có thể gửi email tới",
    "ko-KR": "전송이 실패하면 다음 이메일로 보내주세요",
    "ja-JP": "送信できない場合は、下記メールアドレスへご連絡ください",
    "ms-MY": "Jika penghantaran gagal, anda juga boleh menghantar e-mel ke",
    "ru-RU": "Если отправка не удалась, напишите на",
}

CONTACT_CSS = """*{box-sizing:border-box}
body{margin:0;background:#f6f9f7;color:#26313a;font-family:Arial,"Microsoft YaHei","PingFang SC",sans-serif;line-height:1.6}
.cf-head{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 24px;background:#fff;border-bottom:1px solid #e4ebe7}
.cf-head img{height:44px;width:auto;max-width:220px}
.cf-back{color:#009944;text-decoration:none;font-size:14px;font-weight:700}
.cf-main{max-width:720px;margin:40px auto 72px;padding:0 20px}
.cf-main h1{margin:0 0 10px;font-size:clamp(26px,3vw,34px);color:#17352a}
.cf-intro{margin:0 0 28px;color:#5c6871}
.cf-form{display:grid;gap:18px;padding:28px;background:#fff;border:1px solid #dfe7e3;border-radius:14px;box-shadow:0 10px 30px rgba(23,53,42,.06)}
.cf-field{display:grid;gap:6px}
.cf-field label{font-size:14px;font-weight:700;color:#17352a}
.cf-field input,.cf-field textarea{width:100%;padding:10px 12px;border:1px solid #cfdcd4;border-radius:8px;font:inherit;font-size:15px;color:#26313a;background:#fff}
.cf-field textarea{min-height:130px;resize:vertical}
.cf-field input:focus,.cf-field textarea:focus{outline:2px solid #009944;outline-offset:1px}
.cf-privacy{margin:0;font-size:13px;color:#68747d}
.cf-form button{justify-self:start;padding:11px 26px;border:0;border-radius:8px;background:#009944;color:#fff;font:inherit;font-size:15px;font-weight:700;cursor:pointer}
.cf-form button:hover{background:#087b3d}
.cf-form button:disabled{opacity:.6;cursor:wait}
.cf-status{margin:0;font-size:14px;font-weight:700;min-height:0}
.cf-status.ok{color:#087b3d}
.cf-status.err{color:#c0392b}
.cf-consent{display:block}
.cf-consent label{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:13px;color:#4d5b64;cursor:pointer}
.cf-consent input{flex:0 0 auto;width:17px;height:17px;margin:2px 0 0;accent-color:#009944}
.cf-consent a,.cf-fallback a{color:#087b3d;text-decoration:underline}
.cf-hp{position:absolute!important;left:-9999px!important;width:1px!important;height:1px!important;opacity:0!important}
.cf-fallback{margin:0;font-size:13px;color:#68747d}
@media(max-width:640px){.cf-head{padding:12px 16px}.cf-head img{height:34px}.cf-main{margin:24px auto 48px}.cf-form{padding:20px}}
""" + "\n" + W.CONTACT_CSS_BLOCK + "\n"

CONTACT_JS = """(function () {
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
    if (!d.name || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(d.email) || !d.message) {
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
    fetch('/api/messages', opts).then(function (r) {
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
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="robots" content="noindex,follow"/>
<meta name="description" content="{description}"/>
<link rel="canonical" href="{canonical}"/>
<title>{title} | Maibida</title>
<link href="cn/css/contact.css" rel="stylesheet"/>
</head>
<body>
<header class="cf-head">
<a class="cf-brand" href="{home}"><img alt="Maibida" src="UserFiles/upload/image/20260130/6390537782397634082084337.png"/></a>
<a class="cf-back" href="{home}">{back}</a>
{wa_block}</header>
<main class="cf-main">
<h1>{heading}</h1>
<p class="cf-intro">{intro}</p>
<form class="cf-form" id="message-form" method="post" action="/api/messages" novalidate>
<div class="cf-field"><label for="cf-name">{name}</label><input id="cf-name" name="name" type="text" maxlength="100" required/></div>
<div class="cf-field"><label for="cf-email">{email}</label><input id="cf-email" name="email" type="email" maxlength="200" required/></div>
<div class="cf-field"><label for="cf-phone">{phone}</label><input id="cf-phone" name="phone" type="tel" maxlength="50"/></div>
<div class="cf-field"><label for="cf-company">{company}</label><input id="cf-company" name="company" type="text" maxlength="200"/></div>
<div class="cf-field"><label for="cf-country">{country}</label><input id="cf-country" name="country" type="text" maxlength="100"/></div>
<div class="cf-field"><label for="cf-message">{message}</label><textarea id="cf-message" name="message" maxlength="4000" placeholder="{placeholder}" required></textarea></div>
<input class="cf-hp" name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true"/>
<div class="cf-field cf-consent"><label><input id="cf-consent" name="consent" type="checkbox" value="yes" required/><span>{consent}</span></label></div>
<p class="cf-privacy">{privacy} <a href="{privacy_url}">{privacy_label}</a></p>
<button type="submit">{submit}</button>
<p class="cf-status" id="form-status" role="status" aria-live="polite"></p>
<p class="cf-fallback">{fallback} <a href="mailto:mai_bida@163.com">mai_bida@163.com</a></p>
</form>
</main>
<script src="cn/js/whatsapp-consult.js" defer></script>
<script src="cn/js/contact.js" data-success="{success}" data-error="{error}" data-invalid="{invalid}" data-consent-required="{consent_required}" data-policy-version="{policy_version}"></script>
</body>
</html>
"""

NAV_CSS_BEGIN = "/* BEGIN vp-contact-link (message form nav entry) */"
NAV_CSS_END = "/* END vp-contact-link */"
NAV_CSS = NAV_CSS_BEGIN + """
.top .vp-contact-link,.top2 .vp-contact-link,.top .vp-whatsapp-link,.top2 .vp-whatsapp-link{flex:0 0 auto;margin:0 0 0 10px;padding:5px 12px;border-radius:6px;color:#fff;font-size:13px;font-weight:700;line-height:22px;text-decoration:none;white-space:nowrap}
.top .vp-contact-link,.top2 .vp-contact-link{background:#009944}
.top .vp-whatsapp-link,.top2 .vp-whatsapp-link{margin-left:8px;background:#128c7e}
.top .vp-contact-link:hover,.top2 .vp-contact-link:hover,.top .vp-contact-link:focus,.top2 .vp-contact-link:focus{background:#087b3d;color:#fff}
.top .vp-whatsapp-link:hover,.top2 .vp-whatsapp-link:hover,.top .vp-whatsapp-link:focus,.top2 .vp-whatsapp-link:focus{background:#0e7268;color:#fff}
@media(max-width:640px){
  .top .vp-language-switch,.top2 .vp-language-switch{margin-left:8px}
  .top .vp-contact-link,.top2 .vp-contact-link,.top .vp-whatsapp-link,.top2 .vp-whatsapp-link{font-size:0;margin-left:6px;padding:4px 7px;line-height:20px}
  .top .vp-contact-link:before,.top2 .vp-contact-link:before{content:"\\2709";font-size:16px;line-height:20px}
  .top .vp-whatsapp-link:before,.top2 .vp-whatsapp-link:before{content:"\\260E";font-size:16px;line-height:20px}
}
""" + NAV_CSS_END

LOGO = "UserFiles/upload/image/20260130/6390537782397634082084337.png"
SWITCH_RE = re.compile(r'(<details class="vp-language-switch">.*?</details>)', re.S)
LINK_RE = re.compile(r'<a class="vp-contact-link"[^>]*>.*?</a>', re.S)
WA_LINK_RE = re.compile(r'<a class="vp-whatsapp-link"[^>]*>.*?</a>', re.S)
PANEL_RE = re.compile(r"<!-- BEGIN whatsapp-consult-panel -->.*?<!-- END whatsapp-consult-panel -->\s*", re.S)
WA_SCRIPT_RE = re.compile(r'<script src="(?:\.\./)?cn/js/whatsapp-consult\.js"[^>]*></script>\s*')


def esc(s):
    return html.escape(s, quote=True)


def page_rel(lang):
    return "contact.html" if lang == "zh-CN" else f"contact.{lang}.html"


def home_rel(lang):
    return "/" if lang == "zh-CN" else f"index.{lang}.html"


def formal_pages():
    out = []
    for p in PAGES:
        out.append((p, "zh-CN"))
        q = Path(p)
        for l in LOCALES:
            out.append((str(q.with_name(q.stem + "." + l + ".html")).replace("\\", "/"), l))
    return out


def backup(rels):
    BACKUP.mkdir(parents=True, exist_ok=True)
    for rel in rels:
        src = ROOT / rel
        dst = BACKUP / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return str(BACKUP)


def build_pages():
    made = []
    for lang in LANGS:
        d = {k: esc(v) for k, v in I18N[lang].items()}
        d["lang"] = lang
        d["home"] = home_rel(lang)
        d["description"] = esc(DESCRIPTIONS[lang])
        d["canonical"] = "https://www.maibida.com/" + page_rel(lang)
        privacy_url = ("privacy.html" if lang == "zh-CN"
                       else f"privacy.{lang}.html")
        privacy_label = C.FOOTER_LABELS[lang][0]
        link = f'<a href="{privacy_url}">{esc(privacy_label)}</a>'
        d["consent"] = C.CONSENT[lang].replace("{link}", link)
        d["consent_required"] = esc(C.CONSENT_REQUIRED[lang])
        d["privacy_url"] = privacy_url
        d["privacy_label"] = esc(privacy_label)
        d["fallback"] = esc(FALLBACK[lang])
        d["policy_version"] = C.POLICY_VERSION
        d["wa_block"] = W.contact_widget(lang, privacy_url)
        html_text = PAGE_TEMPLATE.format(**d)
        f = ROOT / page_rel(lang)
        f.write_bytes(html_text.encode("utf-8"))
        made.append(f.name)
    return made


def build_assets():
    (ROOT / "cn/css/contact.css").write_bytes(CONTACT_CSS.encode("utf-8"))
    (ROOT / "cn/js/contact.js").write_bytes(CONTACT_JS.encode("utf-8"))
    (ROOT / "cn/js/whatsapp-consult.js").write_bytes(W.NAV_JS.encode("utf-8"))
    # append / replace the nav style block
    f = ROOT / "cn/css/site-multilingual.css"
    t = f.read_bytes().decode("utf-8")
    if NAV_CSS_BEGIN in t:
        t = re.sub(re.escape(NAV_CSS_BEGIN) + r".*?" + re.escape(NAV_CSS_END),
                   lambda m: NAV_CSS, t, flags=re.S)
    else:
        t = t.rstrip() + "\n\n" + NAV_CSS + "\n"
    # WhatsApp consultation panel styles (shared by all 88 formal pages)
    t = re.sub(r"/\* BEGIN whatsapp-consult-content \*/.*?/\* END whatsapp-consult-content \*/",
               "", t, flags=re.S)
    if W.CSS_BEGIN in t:
        t = re.sub(re.escape(W.CSS_BEGIN) + r".*?" + re.escape(W.CSS_END),
                   lambda m: W.NAV_CSS_BLOCK, t, flags=re.S)
    else:
        t = t.rstrip() + "\n\n" + W.NAV_CSS_BLOCK + "\n"
    f.write_bytes(t.encode("utf-8"))


def inject_nav():
    injected, skipped = [], []
    for rel, lang in formal_pages():
        f = ROOT / rel
        t = f.read_bytes().decode("utf-8")
        t = LINK_RE.sub("", t)
        t = WA_LINK_RE.sub("", t)
        t = PANEL_RE.sub("", t)
        t = WA_SCRIPT_RE.sub("", t)
        prefix = "../" if "/" in rel else ""
        href = prefix + page_rel(lang)
        policy_name = "privacy.html" if lang == "zh-CN" else f"privacy.{lang}.html"
        link = f'<a class="vp-contact-link" href="{href}">{esc(I18N[lang]["nav"])}</a>'
        wa = (W.nav_trigger(lang, WA_LABELS[lang]) + "\n" +
              W.nav_panel(lang, prefix + policy_name))
        new_t, n = SWITCH_RE.subn(lambda m: m.group(1) + link + wa, t, count=1)
        if n != 1:
            skipped.append(rel)
            continue
        new_t = re.sub(r"(</body>)",
                       lambda m: f'<script src="{prefix}cn/js/whatsapp-consult.js" defer></script>\n' + m.group(1),
                       new_t, count=1, flags=re.I)
        f.write_bytes(new_t.encode("utf-8"))
        injected.append(rel)
    return injected, skipped


def register_audit_pages():
    f = ROOT / "tools/full-site-audit.py"
    t = f.read_bytes().decode("utf-8")
    m = re.search(r"TOOL_PAGES\s*=\s*\[[^\]]*\]", t, re.S)
    if not m:
        return "FAILED"
    if '"contact.html"' in m.group(0):
        return "already-present"
    block = ('TOOL_PAGES = ["localization-glossary.html", '
             '"product/smart-camera-localization-report.html", '
             '"product/smart-camera.hreflang.html", "contact.html"] '
             '+ ["contact." + l + ".html" for l in LOCALES]')
    f.write_bytes(t.replace(m.group(0), block, 1).encode("utf-8"))
    return "registered"


def main():
    targets = [rel for rel, _ in formal_pages()] + [
        "cn/css/site-multilingual.css", "tools/full-site-audit.py",
        "tools/preview-server.js"]
    backup_path = backup(targets)
    made = build_pages()
    build_assets()
    injected, skipped = inject_nav()
    audit = register_audit_pages()
    summary = {
        "timestamp": TS, "backup": backup_path,
        "contact_pages": made, "contact_pages_count": len(made),
        "nav_injected": len(injected), "nav_skipped": skipped,
        "assets": ["cn/css/contact.css", "cn/js/contact.js",
                   "cn/css/site-multilingual.css"],
        "audit_registration": audit,
        "fields": ["name", "email", "phone", "company", "country", "message",
                   "consent", "consentVersion"],
        "endpoint": "POST /api/messages",
        "privacy_policy": "privacy.html (+ 10 localized variants)",
        "consent_required": True,
        "honeypot": "website",
        "storage": "../maibida-ocr-rebuilt_messages/messages.ndjson (outside site root)",
        "sitemap_changed": False,
    }
    (ROOT / "tools/message-feature.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "nav_injected"},
                     ensure_ascii=False, indent=2))
    print("nav_injected =", len(injected))
    if skipped or audit == "FAILED":
        raise SystemExit("FAILED: " + str(skipped) + " " + audit)


if __name__ == "__main__":
    main()
