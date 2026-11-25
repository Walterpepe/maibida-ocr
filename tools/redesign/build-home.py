"""Build the commercial, product-led flagship homepage.

Only index.html (zh-CN) and index.en-US.html are generated. Existing SEO
metadata and canonical/hreflang declarations are preserved from the current
pages; the entire visual body is replaced with the new static design.
"""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = "202611260152"
BASE_COMMIT = "86f6b2e"

LANGUAGES = [
    ("zh-CN", "/", "简体中文"),
    ("en-US", "index.en-US.html", "English (US)"),
    ("en-SG", "index.en-SG.html", "English (Singapore)"),
    ("ja-JP", "index.ja-JP.html", "日本語"),
    ("vi-VN", "index.vi-VN.html", "Tiếng Việt"),
    ("th-TH", "index.th-TH.html", "ไทย"),
    ("id-ID", "index.id-ID.html", "Bahasa Indonesia"),
    ("ms-MY", "index.ms-MY.html", "Bahasa Melayu"),
    ("ko-KR", "index.ko-KR.html", "한국어"),
    ("ru-RU", "index.ru-RU.html", "Русский"),
    ("es-MX", "index.es-MX.html", "Español (Latinoamérica)"),
    ("es-ES", "index.es-ES.html", "Español (España)"),
]

LOCALES = {
    "zh-CN": {
        "file": "index.html",
        "title": "MAIBIDA 迈必达｜工业机器视觉检测平台",
        "description": "MAIBIDA 迈必达提供模具监视器、AI 视觉传感器、在线检测、视觉筛选与柔性上料系统，为制造业提供稳定、精准的机器视觉解决方案。",
        "nav_products": "产品",
        "nav_technology": "技术",
        "nav_applications": "应用",
        "nav_contact": "联系",
        "language": "语言",
        "quote": "获取报价",
        "menu": "菜单",
        "eyebrow": "IMX-790 SERIES · 工业机器视觉平台",
        "hero_actions": ("探索产品", "联系工程团队"),
        "manifesto_eyebrow": "MAIBIDA INDUSTRIAL VISION",
        "manifesto_title": "工业视觉检测平台",
        "manifesto_body": "从模具保护、边缘 AI 视觉传感到在线筛选与柔性上料，按工件、公差和生产节拍组合成可落地的检测系统。",
        "hero_facts": [
            ("0.03 s", "视觉判断"),
            ("8 MP", "工业成像"),
            ("MES", "数据追溯"),
        ],
        "proof_eyebrow": "检测结果直接进入产线动作",
        "proof_title": "判断、报警、剔除、追溯，在一个节拍内完成。",
        "proof_body": "相机、算法与 I/O 协同工作，检测结果可连接报警、剔除、分流和 MES，不停留在单张图像。",
        "metrics": [
            ("0.03s", "快速视觉判断"),
            ("100%", "在线全检覆盖"),
            ("MES", "检测数据连接"),
        ],
        "products_eyebrow": "产品矩阵",
        "products_title": "按检测任务选型，而不是从参数表猜方案。",
        "products_body": "五大产品族覆盖模具保护、边缘 AI、尺寸外观检测、视觉筛选和柔性上料，可按产线接口组合。",
        "learn_more": "了解更多",
        "product_kickers": [
            "模具防护",
            "边缘 AI",
            "视觉筛选",
            "柔性上料",
            "在线检测",
        ],
        "products": [
            ("模具监视器", "实时识别模具异常，降低压模风险与停机损失。", "product/10032.html"),
            ("视觉传感器", "边缘 AI 视觉传感器，兼顾速度、精度与部署灵活性。", "product/smart-camera.html"),
            ("视觉筛选机", "面向多品类零件的外观与尺寸筛选，自动识别并分类。", "productlist/10039.html"),
            ("柔性上料摆盘机", "视觉引导的高速上料与摆盘，适配多规格柔性生产。", "productlist/10029.html"),
            ("在线检测设备", "在线完成外观、尺寸与缺陷检测，并联动剔除与追溯。", "productlist/10030.html"),
        ],
        "product_specs": [
            ("0.03 s", "8 MP", "5 路相机"),
            ("15 s 找图", "3 s 参数生成", "IP65"),
            ("60 件/min", "0.0007 mm", "360°"),
            ("±0.05 mm", "4500 件/h", "8 型号"),
            ("10 件/s", "±0.02 mm", "1–6 CCD"),
        ],
        "catalog_label": "快速查看产品族",
        "feature_caption": "IMX-790 系列工业视觉平台",
        "tech_eyebrow": "工程能力",
        "tech_title": "光学、算法与 I/O，在同一节拍协同。",
        "tech_body": "平台围绕工件、光源、治具与产线接口配置，把成像、判断和控制放在现场完成。",
        "capabilities": [
            ("边缘 AI 视觉", "将识别判断放在生产现场，减少链路延迟。"),
            ("亚秒级响应", "高速拍摄与处理，匹配连续生产节拍。"),
            ("可追溯数据", "保存检测结果与报警图像，支持质量分析。"),
        ],
        "tech_image_alt": "MAIBIDA AI 视觉传感器与智能相机",
        "applications_eyebrow": "应用场景",
        "applications_title": "按材料与工件，快速匹配检测方案。",
        "applications_body": "同一套视觉能力，适配不同材料、尺寸、表面条件与生产速度。",
        "applications": [
            ("01", "注塑成型", "模具状态、缺料、毛刺与产品尺寸在线判断。"),
            ("02", "连接器", "端子变形、缺料、间距与外观缺陷全检。"),
            ("03", "电子元器件", "微小零件的高速识别、分类与自动剔除。"),
            ("04", "精密零部件", "复杂轮廓与关键尺寸的稳定重复检测。"),
        ],
        "cta_eyebrow": "从样品开始",
        "cta_title": "上传工件信息，获取平台与集成建议。",
        "cta_body": "提供样品、目标缺陷、公差与节拍，我们将给出平台配置、成像路径与接口建议。",
        "cta_button": "开始沟通",
        "footer_tagline": "为每一条产线，提供可靠的视觉判断。",
        "footer_products": "产品",
        "footer_contact": "联系",
        "footer_privacy": "隐私政策",
        "footer_terms": "销售条款",
        "footer_icp": "苏ICP备2026089220号",
        "footer_address": "中国江苏省苏州昆山市玉山镇乐山路6号裕大科技园2楼213室",
        "hero_image_alt": "MAIBIDA IMX-790 模具监视器系列",
    },
    "en-US": {
        "file": "index.en-US.html",
        "title": "MAIBIDA | Industrial Machine Vision Platforms",
        "description": "MAIBIDA builds mold monitors, AI vision sensors, inline inspection, vision sorting and flexible feeding systems for precision manufacturing.",
        "nav_products": "Products",
        "nav_technology": "Technology",
        "nav_applications": "Applications",
        "nav_contact": "Contact",
        "language": "Language",
        "quote": "Request a Quote",
        "menu": "Menu",
        "eyebrow": "IMX-790 SERIES · INDUSTRIAL MACHINE VISION",
        "hero_actions": ("Explore products", "Talk to engineering"),
        "manifesto_eyebrow": "MAIBIDA INDUSTRIAL VISION",
        "manifesto_title": "Industrial vision platforms",
        "manifesto_body": "Mold protection, edge AI sensing, inline inspection, sorting and flexible feeding, configured around the part, tolerance and production cycle.",
        "hero_facts": [
            ("0.03 s", "vision decision"),
            ("8 MP", "industrial imaging"),
            ("MES", "traceable results"),
        ],
        "proof_eyebrow": "RESULTS MOVE THE LINE",
        "proof_title": "Judge, alarm, reject and trace within one cycle.",
        "proof_body": "Cameras, algorithms and I/O work together, connecting inspection results to alarms, rejection, sorting and MES instead of stopping at an image.",
        "metrics": [
            ("0.03s", "Vision decision cycle"),
            ("100%", "Inline inspection coverage"),
            ("MES", "Inspection data connection"),
        ],
        "products_eyebrow": "PRODUCT MATRIX",
        "products_title": "Start with the inspection task, not the data sheet.",
        "products_body": "Five product families cover mold protection, edge AI, dimensional and cosmetic inspection, sorting and flexible feeding, with line interfaces selected per application.",
        "learn_more": "Learn more",
        "product_kickers": [
            "Mold protection",
            "Edge AI",
            "Vision sorting",
            "Flexible feeding",
            "Inline inspection",
        ],
        "products": [
            ("Mold Protection Monitor", "Real-time mold protection that reduces crash risk and unplanned downtime.", "product/10032.en-US.html"),
            ("Vision Sensor", "Edge AI vision sensing with a balance of speed, accuracy and deployment flexibility.", "product/smart-camera.en-US.html"),
            ("Vision Sorting Machine", "Appearance and dimensional sorting for mixed parts, with automatic recognition and classification.", "productlist/10039.en-US.html"),
            ("Flexible Feeding System", "Vision-guided high-speed feeding and tray loading for flexible, multi-product production.", "productlist/10029.en-US.html"),
            ("Inline Inspection Equipment", "Inline appearance, dimensional and defect inspection connected to rejection and traceability.", "productlist/10030.en-US.html"),
        ],
        "product_specs": [
            ("0.03 s", "8 MP", "5-camera I/O"),
            ("15 s setup", "3 s recipe", "IP65"),
            ("60 ppm", "0.0007 mm", "360°"),
            ("±0.05 mm", "4500 pcs/h", "8 models"),
            ("10 pcs/s", "±0.02 mm", "1–6 CCD"),
        ],
        "catalog_label": "Browse product families",
        "feature_caption": "IMX-790 industrial vision platform",
        "tech_eyebrow": "ENGINEERING",
        "tech_title": "Optics, AI and I/O on one production cycle.",
        "tech_body": "Each platform is configured around the part, illumination, fixture and line interface, with imaging and judgment completed on site.",
        "capabilities": [
            ("Edge AI vision", "Keep classification and judgment close to the production line."),
            ("Sub-second response", "High-speed capture and processing designed for continuous production."),
            ("Traceable data", "Store inspection results and alarm images for quality analysis."),
        ],
        "tech_image_alt": "MAIBIDA AI vision sensor and smart camera",
        "applications_eyebrow": "APPLICATIONS",
        "applications_title": "Match the inspection to the part.",
        "applications_body": "One vision platform, tuned for different materials, tolerances, surface conditions and line speeds.",
        "applications": [
            ("01", "Injection Molding", "Inline mold status, part presence, flash and dimensional judgment."),
            ("02", "Connectors", "Full inspection of terminal deformation, missing material, pitch and appearance."),
            ("03", "Electronic Components", "High-speed recognition, classification and automatic rejection of small parts."),
            ("04", "Precision Parts", "Stable, repeatable inspection of complex contours and critical dimensions."),
        ],
        "cta_eyebrow": "START WITH A SAMPLE",
        "cta_title": "Get a platform and integration recommendation.",
        "cta_body": "Share the sample, target defect, tolerance and cycle. We will recommend the platform, imaging path and line interface.",
        "cta_button": "Talk to an engineer",
        "footer_tagline": "Reliable vision intelligence, built for the production line.",
        "footer_products": "Products",
        "footer_contact": "Contact",
        "footer_privacy": "Privacy Policy",
        "footer_terms": "Terms of Sale",
        "footer_icp": "苏ICP备2026089220号",
        "footer_address": "Room 213, 2F, Yuda Technology Park, No. 6 Leshan Road, Yushan Town, Kunshan, Jiangsu, China",
        "hero_image_alt": "MAIBIDA IMX-790 mold protection monitor series",
    },
}


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def language_menu(current: str):
    return "".join(
        '<a href="{href}" hreflang="{code}" lang="{code}"{current}>{label}</a>'.format(
            href=escape(href),
            code=escape(code),
            label=escape(label),
            current=' aria-current="page"' if code == current else "",
        )
        for code, href, label in LANGUAGES
    )


def product_menu(items):
    return "".join(
        '<a href="{href}"><span>{label}</span><small>{description}</small></a>'.format(
            href=escape(href),
            label=escape(label),
            description=escape(description),
        )
        for label, description, href in items
    )


def nav_links(data):
    return "".join(
        f'<a href="#{anchor}">{escape(label)}</a>'
        for anchor, label in [
            ("technology", data["nav_technology"]),
            ("applications", data["nav_applications"]),
        ]
    )


def product_cards(data):
    names = [item[0] for item in data["products"]]
    descriptions = [item[1] for item in data["products"]]
    hrefs = [item[2] for item in data["products"]]
    kickers = data["product_kickers"]
    learn = escape(data["learn_more"])
    images = [
        ("product-monitor.webp", 542, 530),
        ("product-camera.webp", 970, 970),
        ("product-inline.webp", 970, 900),
        ("product-sorter.webp", 685, 470),
        ("product-feeder.webp", 810, 1020),
    ]
    variants = ("vh-product-card--hero", "vh-product-card--feature", "vh-product-card--tile")
    cards = []
    for index, ((name, description, href), (image, width, height), specs) in enumerate(
        zip(data["products"], images, data["product_specs"]), 1
    ):
        variant = variants[0] if index == 1 else variants[1] if index == 2 else variants[2]
        spec_items = "".join(f"<span>{escape(spec)}</span>" for spec in specs)
        cards.append(
            f"""
<article class="vh-product-card {variant}" data-reveal>
  <figure><img src="cn/images/redesign/{image}?v={VERSION}" width="{width}" height="{height}"
    loading="lazy" decoding="async" alt="{escape(name)}"></figure>
  <div class="vh-product-copy">
    <div class="vh-product-meta"><span>{index:02d}</span><span>{escape(kickers[index - 1])}</span></div>
    <h3>{escape(name)}</h3>
    <p>{escape(description)}</p>
    <div class="vh-card-specs" aria-label="{escape(name)}">{spec_items}</div>
    <a class="vh-product-link" href="{escape(href)}"><span>{learn}</span><span aria-hidden="true">&rarr;</span></a>
  </div>
</article>"""
        )
    return '<div class="vh-product-grid">' + "".join(cards) + "</div>"


def build_head(source: str, data):
    match = re.search(r"<head\b[^>]*>.*?</head>", source, re.S | re.I)
    if not match:
        raise RuntimeError("source page has no head element")
    head = match.group(0)
    head = re.sub(
        r'<title>.*?</title>',
        f"<title>{escape(data['title'])}</title>",
        head,
        count=1,
        flags=re.S,
    )
    head = re.sub(
        r'<meta\b[^>]*\bname="description"[^>]*>',
        f'<meta name="description" content="{escape(data["description"])}"/>',
        head,
        count=1,
        flags=re.S,
    )
    head = re.sub(
        r'<meta\b[^>]*\bproperty="og:title"[^>]*>',
        f'<meta content="{escape(data["title"])}" property="og:title"/>',
        head,
        count=1,
        flags=re.S,
    )
    head = re.sub(
        r'<meta\b[^>]*\bproperty="og:description"[^>]*>',
        f'<meta content="{escape(data["description"])}" property="og:description"/>',
        head,
        count=1,
        flags=re.S,
    )
    head = re.sub(
        r'<link[^>]*href="cn/css/[^"]*"[^>]*>',
        "",
        head,
        flags=re.I,
    )
    head = re.sub(
        r'<link[^>]*href="cn/css/vision-home\.css[^"]*"[^>]*>',
        "",
        head,
        flags=re.I,
    )
    head = re.sub(
        r'<link[^>]*rel="preload"[^>]*home-banner[^>]*>',
        "",
        head,
        flags=re.I,
    )
    additions = f'''
<meta name="theme-color" content="#07111f"/>
<link rel="preload" as="image" href="cn/images/redesign/hero-monitor-lineup.webp?v={VERSION}" fetchpriority="high"/>
<link rel="stylesheet" href="cn/css/vision-home.css?v={VERSION}"/>
'''
    return head.replace("</head>", additions + "</head>")


def build_body(data):
    lang = LANGUAGES[0][0] if data["file"] == "index.html" else "en-US"
    language_links = language_menu(lang)
    product_dropdown = product_menu(data["products"])
    nav_extra = nav_links(data)
    cards = product_cards(data)
    metrics = "".join(
        f'<div class="vh-metric"><strong>{escape(value)}</strong>'
        f"<span>{escape(label)}</span></div>"
        for value, label in data["metrics"]
    )
    capabilities = "".join(
        f"<li><span>{index:02d}</span><div><strong>{escape(title)}</strong>"
        f"<small>{escape(description)}</small></div></li>"
        for index, (title, description) in enumerate(data["capabilities"], 1)
    )
    applications = "".join(
        f'<article class="vh-application"><span>{escape(number)}</span>'
        f'<h3>{escape(title)}</h3><p>{escape(description)}</p></article>'
        for number, title, description in data["applications"]
    )
    hero_facts = "".join(
        f"<li><strong>{escape(value)}</strong><span>{escape(label)}</span></li>"
        for value, label in data["hero_facts"]
    )
    products_footer = "".join(
        f'<a href="{escape(href)}">{escape(label)}</a>'
        for label, _, href in data["products"][:5]
    )
    catalog_links = "".join(
        f'<a href="{escape(href)}"><span>{escape(label)}</span><small>{escape(kicker)}</small></a>'
        for (label, _, href), kicker in zip(data["products"], data["product_kickers"])
    )
    primary_action, secondary_action = data["hero_actions"]
    contact_path = "contact.html" if lang == "zh-CN" else "contact.en-US.html"
    privacy_path = "privacy.html" if lang == "zh-CN" else "privacy.en-US.html"
    terms_path = "terms.html" if lang == "zh-CN" else "terms.en-US.html"
    home_path = "/" if lang == "zh-CN" else "index.en-US.html"
    logo_path = "UserFiles/upload/image/20260130/6390537782787865841043014.webp"
    return f'''
<a class="vh-skip" href="#main-content">{escape("Skip to content" if lang == "en-US" else "跳到主要内容")}</a>
<header class="vh-header" data-vh-header>
  <nav class="vh-nav" aria-label="{escape(data["menu"])}">
    <a class="vh-brand" href="{home_path}" aria-label="MAIBIDA">
      <img src="{logo_path}" width="339" height="112" alt="MAIBIDA">
    </a>
    <div class="vh-desktop-nav">
      <details class="vh-menu">
        <summary>{escape(data["nav_products"])}</summary>
        <div class="vh-menu-popover">{product_dropdown}</div>
      </details>
      {nav_extra}
      <a href="{contact_path}">{escape(data["nav_contact"])}</a>
    </div>
    <div class="vh-actions">
      <details class="vh-language">
        <summary>{escape(data["language"])}</summary>
        <div class="vh-language-popover">{language_links}</div>
      </details>
      <a class="vh-quote" href="{contact_path}">{escape(data["quote"])}</a>
      <details class="vh-mobile-menu">
        <summary aria-label="{escape(data["menu"])}"><span></span></summary>
        <div class="vh-mobile-popover">
          <a href="#products">{escape(data["nav_products"])}</a>
          <a href="#technology">{escape(data["nav_technology"])}</a>
          <a href="#applications">{escape(data["nav_applications"])}</a>
          <a href="{contact_path}">{escape(data["nav_contact"])}</a>
          <a href="{contact_path}">{escape(data["quote"])}</a>
          {language_links}
        </div>
      </details>
    </div>
  </nav>
</header>

<main id="main-content">
  <section class="vh-hero" aria-labelledby="vh-hero-title">
    <div class="vh-hero-shell">
      <div class="vh-hero-copy" data-reveal>
        <p class="vh-eyebrow"><span class="vh-eyebrow-mark" aria-hidden="true"></span>{escape(data["eyebrow"])}</p>
        <h1 id="vh-hero-title">{escape(data["manifesto_title"])}</h1>
        <p class="vh-hero-body">{escape(data["manifesto_body"])}</p>
        <div class="vh-actions-row">
          <a class="vh-button" href="#products">{escape(primary_action)}</a>
          <a class="vh-text-link" href="{contact_path}">{escape(secondary_action)}</a>
        </div>
        <ul class="vh-hero-facts" aria-label="{escape(data["manifesto_eyebrow"])}">{hero_facts}</ul>
      </div>
      <figure class="vh-hero-figure" data-reveal>
        <img src="cn/images/redesign/hero-monitor-lineup.webp?v={VERSION}"
          width="1600" height="530" fetchpriority="high" decoding="async"
          alt="{escape(data["hero_image_alt"])}">
        <figcaption><span>IMX-790</span>{escape(data["feature_caption"])}</figcaption>
      </figure>
    </div>
  </section>

  <section class="vh-proof" aria-labelledby="vh-proof-title">
    <div class="vh-proof-inner">
      <div class="vh-proof-copy" data-reveal>
        <p class="vh-section-eyebrow">{escape(data["proof_eyebrow"])}</p>
        <h2 id="vh-proof-title">{escape(data["proof_title"])}</h2>
        <p>{escape(data["proof_body"])}</p>
      </div>
      <div class="vh-metrics" aria-label="{escape(data["metrics"][0][1])}">
        {metrics}
      </div>
    </div>
  </section>

  <section class="vh-section vh-products" id="products" aria-labelledby="vh-products-title">
    <div class="vh-section-head" data-reveal>
      <p class="vh-section-eyebrow">{escape(data["products_eyebrow"])}</p>
      <h2 id="vh-products-title">{escape(data["products_title"])}</h2>
      <p>{escape(data["products_body"])}</p>
    </div>
    <nav class="vh-product-catalog" aria-label="{escape(data["catalog_label"])}">{catalog_links}</nav>
    {cards}
  </section>

  <section class="vh-tech" id="technology" aria-labelledby="vh-tech-title">
    <div class="vh-tech-inner">
      <div data-reveal>
        <p class="vh-section-eyebrow">{escape(data["tech_eyebrow"])}</p>
        <h2 id="vh-tech-title">{escape(data["tech_title"])}</h2>
        <p>{escape(data["tech_body"])}</p>
        <ul class="vh-capabilities">{capabilities}</ul>
      </div>
      <figure data-reveal>
        <img src="cn/images/redesign/technology-camera.webp?v={VERSION}"
          width="1760" height="850" loading="lazy" decoding="async"
          alt="{escape(data["tech_image_alt"])}">
      </figure>
    </div>
  </section>

  <section class="vh-section vh-applications" id="applications" aria-labelledby="vh-applications-title">
    <div class="vh-applications-layout">
      <div class="vh-section-head" data-reveal>
        <p class="vh-section-eyebrow">{escape(data["applications_eyebrow"])}</p>
        <h2 id="vh-applications-title">{escape(data["applications_title"])}</h2>
        <p>{escape(data["applications_body"])}</p>
      </div>
      <div class="vh-application-grid">{applications}</div>
    </div>
  </section>

  <section class="vh-cta" aria-labelledby="vh-cta-title">
    <div class="vh-cta-inner" data-reveal>
      <p class="vh-section-eyebrow">{escape(data["cta_eyebrow"])}</p>
      <h2 id="vh-cta-title">{escape(data["cta_title"])}</h2>
      <p>{escape(data["cta_body"])}</p>
      <a class="vh-button" href="{contact_path}">{escape(data["cta_button"])}</a>
    </div>
  </section>
</main>

<footer class="vh-footer">
  <div class="vh-footer-inner">
    <div class="vh-footer-top">
      <div class="vh-footer-brand">
        <img src="{logo_path}" width="339" height="112" loading="lazy" decoding="async" alt="MAIBIDA">
        <p>{escape(data["footer_tagline"])}</p>
      </div>
      <div class="vh-footer-col">
        <h3>{escape(data["footer_products"])}</h3>
        {products_footer}
      </div>
      <div class="vh-footer-col">
        <h3>{escape(data["footer_contact"])}</h3>
        <a href="tel:+8615995675085">+86 159 9567 5085</a>
        <a href="mailto:mai_bida@163.com">mai_bida@163.com</a>
        <p>{escape(data["footer_address"])}</p>
      </div>
    </div>
    <div class="vh-footer-bottom">
      <span>© 2020–2026 Kunshan Maibida Intelligent Equipment Co., Ltd.</span>
      <div class="vh-footer-links">
        <a href="{privacy_path}">{escape(data["footer_privacy"])}</a>
        <a href="{terms_path}">{escape(data["footer_terms"])}</a>
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">{escape(data["footer_icp"])}</a>
      </div>
    </div>
  </div>
</footer>
<script src="cn/js/vision-home.js?v={VERSION}" defer></script>
'''


def main():
    for lang, data in LOCALES.items():
        path = ROOT / data["file"]
        source = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:{data['file']}"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
        )
        head = build_head(source, data)
        page = (
            "<!DOCTYPE html>\n"
            f'<html lang="{lang}">\n'
            + head
            + "\n<body class=\"vision-home\">\n"
            + build_body(data)
            + "\n</body>\n</html>\n"
        )
        path.write_text(page, encoding="utf-8")
        print(f"built {data['file']}")


if __name__ == "__main__":
    main()
