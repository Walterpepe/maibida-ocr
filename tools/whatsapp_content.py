# -*- coding: utf-8 -*-
"""WhatsApp consultation content for all 11 locales (data only, no side effects).

Shared by add-whatsapp-content.py (incremental patch on the deployed pages),
add-message-feature.py (regenerating the contact pages) and the verification
script, so the label, the pre-filled chat text and the contact block always
stay in sync.
"""
from __future__ import annotations

import html
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compliance_i18n as C

WA_NUMBER = "8615995675085"          # from the Organization JSON-LD
WA_DISPLAY = "+86 159 9567 5085"
WA_BASE = "https://wa.me/" + WA_NUMBER
WA_EMAIL = "mai_bida@163.com"

LANGS = ["zh-CN", "en-US", "en-SG", "es-MX", "id-ID", "th-TH",
         "vi-VN", "ko-KR", "ja-JP", "ms-MY", "ru-RU"]

EN = {
    "prefill": ("Hello Maibida, I would like to enquire about your machine vision "
                "lights, mold monitors or smart cameras. Please send selection "
                "advice and a quotation. Source: maibida.com"),
    "footer": "WhatsApp: ",
    "title": "WhatsApp Consultation",
    "intro": ("Overseas buyers can chat directly with our sales and technical team "
              "on WhatsApp for product selection, quotations and technical documents."),
    "items": [
        "Models, specifications and compatibility of mold monitors, vision sensors and smart cameras",
        "Pricing, lead-time information and sample or trial arrangements",
        "OEM and custom projects, installation guidance and after-sales support",
    ],
    "hours_label": "Availability: ",
    "hours": ("Monday to Friday, 09:00-18:00 (GMT+8, China Standard Time). "
              "Messages outside these hours are welcome; for urgent matters please "
              "also email " + WA_EMAIL + "."),
    "number_label": "WhatsApp number: ",
    "button": "Start a WhatsApp chat",
    "privacy": ("Please do not send passwords or banking details over WhatsApp. "
                "We use the conversation only to answer your enquiry; see our {link} for details."),
}

DATA = {
    "zh-CN": {
        "prefill": ("您好，我想咨询迈必达的机器视觉光源、模具监视器或智能相机，"
                    "请协助提供选型建议与报价。来源：maibida.com"),
        "footer": "WhatsApp 咨询：",
        "title": "WhatsApp 咨询",
        "intro": "海外客户可通过 WhatsApp 直接与我们的业务与技术人员沟通，获取产品选型、报价与技术资料。",
        "items": [
            "模具监视器、视觉传感器与智能相机的型号、参数及兼容性",
            "产品报价、交期信息与样品或试用安排",
            "OEM 与定制方案、安装调试及售后技术支持",
        ],
        "hours_label": "在线时间：",
        "hours": ("周一至周五 09:00–18:00（GMT+8，中国标准时间）。非工作时间也可留言；"
                  "如需紧急协助，请同时发送邮件至 " + WA_EMAIL + "。"),
        "number_label": "WhatsApp 号码：",
        "button": "打开 WhatsApp 发起咨询",
        "privacy": ("请勿通过 WhatsApp 发送密码、银行账号等敏感信息。我们仅将沟通内容用于回复您的咨询，"
                    "处理方式详见 {link}。"),
    },
    "en-US": dict(EN),
    "en-SG": dict(
        EN,
        prefill=("Hello Maibida, I would like to enquire about your machine vision "
                 "lights, mould monitors or smart cameras. Please send selection "
                 "advice and a quotation. Source: maibida.com"),
        items=[
            "Models, specifications and compatibility of mould monitors, vision sensors and smart cameras",
            "Pricing, lead-time information and sample or trial arrangements",
            "OEM and custom projects, installation guidance and after-sales support",
        ],
    ),
    "es-MX": {
        "prefill": ("Hola, quisiera solicitar información sobre la iluminación para visión "
                    "artificial, los monitores de molde o las cámaras inteligentes Maibida. "
                    "¿Podrían enviarme una recomendación de selección y una cotización? "
                    "Fuente: maibida.com"),
        "footer": "WhatsApp: ",
        "title": "Consulta por WhatsApp",
        "intro": ("Los clientes en el extranjero pueden escribir directamente a nuestro "
                  "equipo comercial y técnico por WhatsApp para recibir apoyo en la "
                  "selección, cotizaciones y documentación técnica."),
        "items": [
            "Modelos, especificaciones y compatibilidad de monitores de molde, sensores de visión y cámaras inteligentes",
            "Precios, plazos de entrega y gestión de muestras o pruebas",
            "Proyectos OEM y a la medida, instalación, puesta en marcha y soporte posventa",
        ],
        "hours_label": "Horario de atención: ",
        "hours": ("De lunes a viernes, 09:00 a 18:00 (GMT+8, hora estándar de China). "
                  "Puede dejar su mensaje fuera de este horario; para asuntos urgentes, "
                  "escriba también a " + WA_EMAIL + "."),
        "number_label": "Número de WhatsApp: ",
        "button": "Iniciar chat por WhatsApp",
        "privacy": ("No envíe contraseñas ni datos bancarios por WhatsApp. Usamos la "
                    "conversación únicamente para responder a su consulta; consulte "
                    "nuestro {link} para más detalles."),
    },
    "id-ID": {
        "prefill": ("Halo Maibida, saya ingin menanyakan lampu machine vision, pemantau "
                    "cetakan, atau kamera pintar. Mohon kirimkan rekomendasi pemilihan "
                    "dan penawaran harga. Sumber: maibida.com"),
        "footer": "WhatsApp: ",
        "title": "Konsultasi WhatsApp",
        "intro": ("Pembeli luar negeri dapat menghubungi tim penjualan dan teknis kami "
                  "langsung melalui WhatsApp untuk pemilihan produk, penawaran harga "
                  "dan dokumen teknis."),
        "items": [
            "Model, spesifikasi, dan kompatibilitas pemantau cetakan, sensor visi, dan kamera pintar",
            "Harga, informasi waktu pengiriman, serta pengaturan sampel atau uji coba",
            "Proyek OEM dan khusus, panduan instalasi, serta dukungan purna jual",
        ],
        "hours_label": "Jam layanan: ",
        "hours": ("Senin sampai Jumat, 09:00-18:00 (GMT+8, Waktu Standar Tiongkok). "
                  "Pesan di luar jam tersebut tetap dapat dikirim; untuk hal mendesak, "
                  "kirim juga email ke " + WA_EMAIL + "."),
        "number_label": "Nomor WhatsApp: ",
        "button": "Mulai chat WhatsApp",
        "privacy": ("Jangan kirim kata sandi atau data perbankan melalui WhatsApp. "
                    "Percakapan hanya digunakan untuk menjawab pertanyaan Anda; "
                    "lihat {link} untuk detailnya."),
    },
    "th-TH": {
        "prefill": ("สวัสดี Maibida ต้องการสอบถามเกี่ยวกับไฟ Machine Vision "
                    "ระบบตรวจสอบแม่พิมพ์ หรือกล้องอัจฉริยะ "
                    "กรุณาส่งคำแนะนำการเลือกรุ่นและใบเสนอราคาให้ด้วย ที่มา: maibida.com"),
        "footer": "WhatsApp: ",
        "title": "ปรึกษาผ่าน WhatsApp",
        "intro": ("ลูกค้าต่างประเทศสามารถพูดคุยกับทีมขายและทีมเทคนิคของเราโดยตรงผ่าน WhatsApp "
                  "เพื่อขอคำแนะนำการเลือกผลิตภัณฑ์ ใบเสนอราคา และเอกสารทางเทคนิค"),
        "items": [
            "รุ่น สเปค และความเข้ากันได้ของระบบตรวจสอบแม่พิมพ์ เซ็นเซอร์วิชัน และกล้องอัจฉริยะ",
            "ราคา ข้อมูลระยะเวลาจัดส่ง และการขอตัวอย่างหรือทดลองใช้งาน",
            "โครงการ OEM และแบบสั่งทำ การติดตั้ง การเดินเครื่อง และการสนับสนุนหลังการขาย",
        ],
        "hours_label": "เวลาทำการ: ",
        "hours": ("วันจันทร์ถึงวันศุกร์ 09:00-18:00 น. (GMT+8 เวลามาตรฐานจีน) "
                  "สามารถฝากข้อความนอกเวลาทำการได้ สำหรับเรื่องเร่งด่วน "
                  "กรุณาส่งอีเมลไปที่ " + WA_EMAIL + " ด้วย"),
        "number_label": "หมายเลข WhatsApp: ",
        "button": "เริ่มแชท WhatsApp",
        "privacy": ("กรุณาอย่าส่งรหัสผ่านหรือข้อมูลธนาคารผ่าน WhatsApp "
                    "เราใช้บทสนทนาเพื่อตอบคำถามของท่านเท่านั้น "
                    "รายละเอียดเพิ่มเติมดูได้ที่ {link}"),
    },
    "vi-VN": {
        "prefill": ("Xin chào Maibida, tôi muốn được tư vấn về đèn thị giác máy, hệ thống "
                    "giám sát khuôn hoặc camera thông minh. Vui lòng gửi đề xuất lựa chọn "
                    "và báo giá. Nguồn: maibida.com"),
        "footer": "WhatsApp: ",
        "title": "Tư vấn qua WhatsApp",
        "intro": ("Khách hàng quốc tế có thể trao đổi trực tiếp với đội ngũ kinh doanh và "
                  "kỹ thuật qua WhatsApp để được hỗ trợ chọn sản phẩm, báo giá và tài liệu kỹ thuật."),
        "items": [
            "Mã máy, thông số và khả năng tương thích của hệ thống giám sát khuôn, cảm biến thị giác và camera thông minh",
            "Báo giá, thông tin thời gian giao hàng và sắp xếp mẫu hoặc chạy thử",
            "Dự án OEM và theo yêu cầu, hướng dẫn lắp đặt và hỗ trợ sau bán hàng",
        ],
        "hours_label": "Thời gian hỗ trợ: ",
        "hours": ("Thứ Hai đến Thứ Sáu, 09:00-18:00 (GMT+8, giờ chuẩn Trung Quốc). "
                  "Có thể nhắn tin ngoài giờ; với việc gấp, vui lòng gửi thêm email tới "
                  + WA_EMAIL + "."),
        "number_label": "Số WhatsApp: ",
        "button": "Bắt đầu chat WhatsApp",
        "privacy": ("Vui lòng không gửi mật khẩu hoặc thông tin ngân hàng qua WhatsApp. "
                    "Chúng tôi chỉ dùng nội dung trao đổi để phản hồi yêu cầu của bạn; "
                    "xem {link} để biết chi tiết."),
    },
    "ko-KR": {
        "prefill": ("안녕하세요, 마이비다의 머신비전 조명, 금형 감시기 또는 스마트 카메라에 대해 "
                    "문의드립니다. 모델 선정 자문과 견적을 보내주세요. 출처: maibida.com"),
        "footer": "WhatsApp 문의: ",
        "title": "WhatsApp 상담",
        "intro": ("해외 고객은 WhatsApp을 통해 영업·기술 담당자와 직접 상담하실 수 있으며, "
                  "제품 선정, 견적 및 기술 자료를 받아보실 수 있습니다."),
        "items": [
            "금형 감시기, 비전 센서, 스마트 카메라의 모델·사양 및 호환성",
            "가격, 납기 정보 및 샘플·시험 사용 일정",
            "OEM 및 맞춤 프로젝트, 설치 안내와 사후 기술 지원",
        ],
        "hours_label": "응대 시간: ",
        "hours": ("월~금 09:00-18:00 (GMT+8, 중국 표준시). 근무 시간 외에도 메시지를 "
                  "남기실 수 있으며, 긴급한 경우 " + WA_EMAIL + "로 이메일도 함께 보내주세요."),
        "number_label": "WhatsApp 번호: ",
        "button": "WhatsApp으로 문의하기",
        "privacy": ("WhatsApp으로 비밀번호나 계좌 정보 등 민감한 정보를 보내지 마세요. "
                    "대화 내용은 문의 회신에만 사용되며 자세한 내용은 {link}를 참조해 주세요."),
    },
    "ja-JP": {
        "prefill": ("Maibida 様、マシンビジョン用照明・金型監視装置・スマートカメラについて"
                    "問い合わせいたします。選定のご助言とお見積りをご送付ください。"
                    "参照元：maibida.com"),
        "footer": "WhatsApp お問い合わせ：",
        "title": "WhatsApp でのお問い合わせ",
        "intro": ("海外のお客様は WhatsApp から営業・技術担当へ直接ご相談いただけます。"
                  "製品選定、お見積り、技術資料のご提供に対応いたします。"),
        "items": [
            "金型監視装置、ビジョンセンサ、スマートカメラの型式・仕様・互換性",
            "価格、納期情報、サンプルまたは試用の手配",
            "OEM・特注案件、設置・立ち上げのご案内、アフターサポート",
        ],
        "hours_label": "対応時間：",
        "hours": ("平日 09:00-18:00（GMT+8／中国標準時）。時間外にもメッセージを"
                  "お送りいただけます。お急ぎの場合は " + WA_EMAIL + " へもご連絡ください。"),
        "number_label": "WhatsApp 番号：",
        "button": "WhatsApp で相談を始める",
        "privacy": ("パスワードや口座情報などの機微情報は WhatsApp で送信しないでください。"
                    "会話内容はお問い合わせへの回答にのみ使用します。詳細は {link} をご確認ください。"),
    },
    "ms-MY": {
        "prefill": ("Halo Maibida, saya ingin bertanya tentang lampu penglihatan mesin, "
                    "pemantau acuan atau kamera pintar. Sila hantar cadangan pemilihan "
                    "dan sebut harga. Sumber: maibida.com"),
        "footer": "WhatsApp: ",
        "title": "Perundingan WhatsApp",
        "intro": ("Pembeli luar negara boleh menghubungi pasukan jualan dan teknikal kami "
                  "terus melalui WhatsApp untuk pemilihan produk, sebut harga dan "
                  "dokumen teknikal."),
        "items": [
            "Model, spesifikasi dan keserasian pemantau acuan, sensor penglihatan dan kamera pintar",
            "Harga, maklumat tempoh penghantaran serta urusan sampel atau percubaan",
            "Projek OEM dan tempahan khas, panduan pemasangan serta sokongan selepas jualan",
        ],
        "hours_label": "Waktu perkhidmatan: ",
        "hours": ("Isnin hingga Jumaat, 09:00-18:00 (GMT+8, Waktu Piawai China). "
                  "Mesej di luar waktu ini boleh ditinggalkan; untuk perkara segera, "
                  "sila e-mel juga ke " + WA_EMAIL + "."),
        "number_label": "Nombor WhatsApp: ",
        "button": "Mula sembang WhatsApp",
        "privacy": ("Jangan hantar kata laluan atau maklumat perbankan melalui WhatsApp. "
                    "Perbualan hanya digunakan untuk menjawab pertanyaan anda; "
                    "lihat {link} untuk butiran."),
    },
    "ru-RU": {
        "prefill": ("Здравствуйте! Хочу узнать об освещении для машинного зрения, системах "
                    "контроля пресс-форм и смарт-камерах Maibida. Прошу направить "
                    "рекомендации по подбору и коммерческое предложение. Источник: maibida.com"),
        "footer": "WhatsApp: ",
        "title": "Консультация в WhatsApp",
        "intro": ("Зарубежные клиенты могут напрямую связаться с нашими специалистами по "
                  "продажам и технической поддержке в WhatsApp для подбора оборудования, "
                  "получения коммерческого предложения и технической документации."),
        "items": [
            "Модели, характеристики и совместимость систем контроля пресс-форм, датчиков зрения и смарт-камер",
            "Цены, информация о сроках поставки, образцы и тестовые испытания",
            "OEM и индивидуальные проекты, монтаж, наладка и послепродажная поддержка",
        ],
        "hours_label": "Время работы: ",
        "hours": ("Понедельник-пятница, 09:00-18:00 (GMT+8, стандартное время Китая). "
                  "Сообщения можно оставлять и в нерабочее время; по срочным вопросам "
                  "дополнительно напишите на " + WA_EMAIL + "."),
        "number_label": "Номер WhatsApp: ",
        "button": "Начать чат в WhatsApp",
        "privacy": ("Не отправляйте через WhatsApp пароли или банковские данные. "
                    "Переписка используется только для ответа на ваш запрос; "
                    "подробности — {link}."),
    },
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def wa_url(lang: str) -> str:
    """wa.me deep link with a localized, URL-encoded pre-filled message."""
    return WA_BASE + "?text=" + quote(DATA[lang]["prefill"], safe="")


def wa_href(lang: str) -> str:
    """HTML-attribute-safe version of wa_url()."""
    return esc(wa_url(lang))


def footer_line(lang: str) -> str:
    """One extra line in the existing footer contact column."""
    d = DATA[lang]
    return ('<p class="fc-line fc-wa">' + esc(d["footer"]) +
            '<span><a href="' + wa_href(lang) + '" target="_blank" '
            'rel="noopener noreferrer" aria-label="' + esc(d["title"]) + ' ' + WA_DISPLAY + '" '
            'style="color:inherit;text-decoration:none">' + WA_DISPLAY + '</a></span></p>')


CLOSE_LABELS = {
    "zh-CN": "关闭咨询面板", "en-US": "Close", "en-SG": "Close",
    "es-MX": "Cerrar", "id-ID": "Tutup", "th-TH": "ปิด",
    "vi-VN": "Đóng", "ko-KR": "닫기", "ja-JP": "閉じる",
    "ms-MY": "Tutup", "ru-RU": "Закрыть",
}

PANEL_BEGIN = "<!-- BEGIN whatsapp-consult-panel -->"
PANEL_END = "<!-- END whatsapp-consult-panel -->"


def nav_trigger(lang: str, label: str, in_nav: bool = True) -> str:
    """Nav entry: keeps the crawlable wa.me href, opens the panel when JS is on.

    in_nav=False is used on the standalone contact pages, which have no .top
    wrapper and therefore need the standalone trigger class.
    """
    cls = "vp-whatsapp-link" if in_nav else "wa-consult-trigger"
    return ('<a class="' + cls + '" href="' + wa_href(lang) + '" '
            'target="_blank" rel="noopener noreferrer" '
            'aria-haspopup="dialog" aria-expanded="false" aria-controls="wa-consult-panel" '
            'data-wa-toggle title="' + esc(label) + '" aria-label="' + esc(label) + '">' +
            esc(label) + '</a>')


def nav_panel(lang: str, privacy_url: str) -> str:
    """The consultation content, now expanded from the nav entry."""
    d = DATA[lang]
    href = wa_href(lang)
    policy = ('<a href="' + esc(privacy_url) + '">' +
              esc(C.FOOTER_LABELS[lang][0]) + '</a>')
    before, _, after = d["privacy"].partition("{link}")
    note = esc(before) + policy + esc(after)
    items = "".join("<li>" + esc(x) + "</li>" for x in d["items"])
    return (PANEL_BEGIN + "\n" +
            '<div class="wa-consult-panel" id="wa-consult-panel" role="dialog" '
            'aria-modal="false" aria-labelledby="wa-consult-title" hidden>\n'
            '<div class="wa-consult-head"><h2 id="wa-consult-title">' +
            esc(d["title"]) + '</h2>' +
            '<button class="wa-consult-close" type="button" aria-label="' +
            esc(CLOSE_LABELS[lang]) + '">&times;</button></div>\n'
            '<p class="wa-consult-intro">' + esc(d["intro"]) + '</p>\n'
            '<ul class="wa-consult-list">' + items + '</ul>\n'
            '<p class="wa-consult-meta"><strong>' + esc(d["hours_label"]) + '</strong>' +
            esc(d["hours"]) + '</p>\n'
            '<p class="wa-consult-meta"><strong>' + esc(d["number_label"]) + '</strong>'
            '<a href="' + href + '" target="_blank" rel="noopener noreferrer">' +
            WA_DISPLAY + '</a></p>\n'
            '<a class="wa-consult-btn" href="' + href + '" target="_blank" '
            'rel="noopener noreferrer">' + esc(d["button"]) + '</a>\n'
            '<p class="wa-consult-note">' + note + '</p>\n'
            '</div>\n' + PANEL_END)


def contact_widget(lang: str, privacy_url: str) -> str:
    """Header widget for the standalone contact pages (no global nav)."""
    return (nav_trigger(lang, DATA[lang]["title"], in_nav=False) + "\n" +
            nav_panel(lang, privacy_url))


# Kept as an alias so the message-page generator stays source-compatible.
contact_block = contact_widget


CSS_BEGIN = "/* BEGIN whatsapp-consult-nav */"
CSS_END = "/* END whatsapp-consult-nav */"
NAV_CSS_BLOCK = CSS_BEGIN + """
.top .clear.wrap,.top2 .clear.wrap{position:relative}
.cf-head{position:relative}
.cf-head .cf-back{margin-left:auto}
.wa-consult-trigger{border:0;cursor:pointer;font:inherit}
.cf-head .wa-consult-trigger{margin-left:12px}
.cf-head .wa-consult-trigger{display:inline-flex;align-items:center;padding:7px 14px;border-radius:6px;background:#128c7e;color:#fff;font-size:13px;font-weight:700;line-height:22px;text-decoration:none;white-space:nowrap}
.cf-head .wa-consult-trigger:hover,.cf-head .wa-consult-trigger:focus{background:#0e7268;color:#fff}
.wa-consult-panel{position:absolute;right:12px;top:calc(100% + 8px);z-index:1200;width:min(420px,calc(100vw - 24px));max-height:calc(100vh - 150px);overflow-y:auto;padding:20px 22px;border:1px solid #dfe7e3;border-radius:12px;background:#fff;box-shadow:0 16px 40px rgba(23,53,42,.18);color:#26313a;font-size:14px;line-height:1.6;text-align:left}
.wa-consult-panel[hidden]{display:none}
.wa-consult-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 0 10px}
.wa-consult-head h2{margin:0;font-size:18px;color:#17352a}
.wa-consult-close{flex:0 0 auto;width:28px;height:28px;border:1px solid #dfe7e3;border-radius:6px;background:#fff;color:#26313a;font-size:18px;line-height:1;cursor:pointer}
.wa-consult-close:hover{background:#f3f8f5}
.wa-consult-intro{margin:0 0 12px;color:#5c6871}
.wa-consult-list{margin:0 0 12px;padding-left:20px;color:#3d4a52}
.wa-consult-list li{margin:0 0 6px;overflow-wrap:break-word}
.wa-consult-meta{margin:0 0 8px;color:#3d4a52;overflow-wrap:break-word}
.wa-consult-meta strong{color:#17352a}
.wa-consult-meta a{color:#0e7268;text-decoration:underline}
.wa-consult-btn{display:block;margin:10px 0 12px;padding:10px 18px;border-radius:8px;background:#128c7e;color:#fff;font-size:14px;font-weight:700;text-align:center;text-decoration:none}
.wa-consult-btn:hover,.wa-consult-btn:focus{background:#0e7268;color:#fff}
.wa-consult-note{margin:0;font-size:12px;color:#68747d;overflow-wrap:break-word}
.wa-consult-note a{color:#087b3d;text-decoration:underline}
@media(max-width:640px){
  .wa-consult-panel{right:8px;top:calc(100% + 6px);width:calc(100vw - 16px);max-height:calc(100vh - 120px);padding:18px}
  .cf-head .wa-consult-trigger{font-size:12px;padding:6px 10px}
}
""" + CSS_END
CONTACT_CSS_BLOCK = NAV_CSS_BLOCK

NAV_JS = """(function () {
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
"""
