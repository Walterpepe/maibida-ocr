"""Build the experimental Apple-grade flagship homepage.

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
VERSION = "202611261625"
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
        "eyebrow": "IMX-790 · 工业机器视觉平台",
        "hero_actions": ("探索产品", "联系工程团队"),
        "manifesto_eyebrow": "为真实产线而生",
        "manifesto_title": "视觉判断，融入每一次生产节拍。",
        "manifesto_body": "MAIBIDA 将光学、AI 与自动化执行整合为可落地的检测平台，从单点识别延伸到整线质量控制。",
        "hero_facts": [
            ("多相机", "同步成像"),
            ("实时 I/O", "产线联动"),
            ("MES", "数据追溯"),
        ],
        "proof_eyebrow": "从图像到动作",
        "proof_title": "看到问题，只是开始。",
        "proof_body": "更重要的是在同一节拍内完成判断、输出与追溯，让检测真正进入生产控制，而不只是停留在结果查看。",
        "metrics": [
            ("0.03s", "快速视觉判断"),
            ("100%", "在线全检覆盖"),
            ("MES", "检测数据连接"),
        ],
        "products_eyebrow": "产品家族",
        "products_title": "五类平台，一套完整检测链。",
        "products_body": "从防护、识别到筛选与上料，每个系统围绕真实生产节拍设计，并可组合成完整的自动化检测流程。",
        "learn_more": "了解更多",
        "product_kickers": [
            "模具防护",
            "边缘 AI",
            "视觉筛选",
            "柔性上料",
            "在线检测",
        ],
        "feature_points": ["多相机成像", "实时 I/O", "MES 接口"],
        "products": [
            ("模具监视器", "实时识别模具异常，降低压模风险与停机损失。", "product/10032.html"),
            ("视觉传感器", "边缘 AI 视觉传感器，兼顾速度、精度与部署灵活性。", "product/smart-camera.html"),
            ("视觉筛选机", "面向多品类零件的外观与尺寸筛选，自动识别并分类。", "productlist/10039.html"),
            ("柔性上料摆盘机", "视觉引导的高速上料与摆盘，适配多规格柔性生产。", "productlist/10029.html"),
            ("在线检测设备", "在线完成外观、尺寸与缺陷检测，并联动剔除与追溯。", "productlist/10030.html"),
        ],
        "feature_caption": "IMX-790 系列工业视觉平台",
        "tech_eyebrow": "核心技术",
        "tech_title": "视觉不只是一张图片，而是一次实时决策。",
        "tech_body": "光学、算法与执行机构在同一节拍下协同，让检测结果不只知道“有没有问题”，还能进入生产决策。",
        "capabilities": [
            ("边缘 AI 视觉", "将识别判断放在生产现场，减少链路延迟。"),
            ("亚秒级响应", "高速拍摄与处理，匹配连续生产节拍。"),
            ("可追溯数据", "保存检测结果与报警图像，支持质量分析。"),
        ],
        "tech_image_alt": "MAIBIDA AI 视觉传感器与智能相机",
        "applications_eyebrow": "应用场景",
        "applications_title": "从微小连接，到精密组件。",
        "applications_body": "同一套视觉能力，适配不同材料、尺寸、表面与生产速度。",
        "applications": [
            ("注塑成型", "模具状态、缺料、毛刺与产品尺寸在线判断。"),
            ("连接器", "端子变形、缺料、间距与外观缺陷全检。"),
            ("电子元器件", "微小零件的高速识别、分类与自动剔除。"),
            ("精密零部件", "复杂轮廓与关键尺寸的稳定重复检测。"),
        ],
        "cta_eyebrow": "从样品开始",
        "cta_title": "告诉我们，您需要检测什么。",
        "cta_body": "提供样品与检测需求，我们将给出选型、节拍与集成建议。",
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
        "eyebrow": "IMX-790 · INDUSTRIAL MACHINE VISION",
        "hero_actions": ("Explore products", "Talk to engineering"),
        "manifesto_eyebrow": "BUILT FOR THE LINE",
        "manifesto_title": "Vision intelligence, built into every cycle.",
        "manifesto_body": "MAIBIDA combines optics, AI and automated action into practical inspection platforms that scale from one station to the entire quality flow.",
        "hero_facts": [
            ("Multi-camera", "synchronised imaging"),
            ("Real-time I/O", "line control"),
            ("MES", "traceable results"),
        ],
        "proof_eyebrow": "FROM IMAGE TO ACTION",
        "proof_title": "Seeing the defect is only the beginning.",
        "proof_body": "The value is in making a reliable decision, triggering the right I/O and preserving the result trace within the same production cycle.",
        "metrics": [
            ("0.03s", "Vision decision cycle"),
            ("100%", "Inline inspection coverage"),
            ("MES", "Inspection data connection"),
        ],
        "products_eyebrow": "THE PRODUCT FAMILY",
        "products_title": "Five platforms. One inspection chain.",
        "products_body": "From protection and recognition to sorting and feeding, every system is designed around real production speed and can work as one automated inspection flow.",
        "learn_more": "Learn more",
        "product_kickers": [
            "Mold protection",
            "Edge AI",
            "Vision sorting",
            "Flexible feeding",
            "Inline inspection",
        ],
        "feature_points": ["Multi-camera imaging", "Real-time I/O", "MES interface"],
        "products": [
            ("Mold Protection Monitor", "Real-time mold protection that reduces crash risk and unplanned downtime.", "product/10032.en-US.html"),
            ("Vision Sensor", "Edge AI vision sensing with a balance of speed, accuracy and deployment flexibility.", "product/smart-camera.en-US.html"),
            ("Vision Sorting Machine", "Appearance and dimensional sorting for mixed parts, with automatic recognition and classification.", "productlist/10039.en-US.html"),
            ("Flexible Feeding System", "Vision-guided high-speed feeding and tray loading for flexible, multi-product production.", "productlist/10029.en-US.html"),
            ("Inline Inspection Equipment", "Inline appearance, dimensional and defect inspection connected to rejection and traceability.", "productlist/10030.en-US.html"),
        ],
        "feature_caption": "IMX-790 industrial vision platform",
        "tech_eyebrow": "THE CORE",
        "tech_title": "Vision is not an image. It is a decision in motion.",
        "tech_body": "Optics, AI and actuation work on the same production rhythm, turning every inspection result into an actionable line decision.",
        "capabilities": [
            ("Edge AI vision", "Keep classification and judgment close to the production line."),
            ("Sub-second response", "High-speed capture and processing designed for continuous production."),
            ("Traceable data", "Store inspection results and alarm images for quality analysis."),
        ],
        "tech_image_alt": "MAIBIDA AI vision sensor and smart camera",
        "applications_eyebrow": "APPLICATIONS",
        "applications_title": "From tiny connectors to precision components.",
        "applications_body": "One vision platform, tuned for different materials, tolerances, surface conditions and line speeds.",
        "applications": [
            ("Injection Molding", "Inline mold status, part presence, flash and dimensional judgment."),
            ("Connectors", "Full inspection of terminal deformation, missing material, pitch and appearance."),
            ("Electronic Components", "High-speed recognition, classification and automatic rejection of small parts."),
            ("Precision Parts", "Stable, repeatable inspection of complex contours and critical dimensions."),
        ],
        "cta_eyebrow": "START WITH A SAMPLE",
        "cta_title": "Tell us what needs to be inspected.",
        "cta_body": "Share a sample and your production requirement. We will recommend the platform, cycle strategy and integration path.",
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
    feature_points = "".join(
        f"<span>{escape(point)}</span>" for point in data["feature_points"]
    )
    feature = f"""
<div class="vh-product-feature" data-reveal>
  <div class="vh-product-copy">
    <div class="vh-product-meta"><span>01</span><span>{escape(kickers[0])}</span></div>
    <h3>{escape(names[0])}</h3>
    <p>{escape(descriptions[0])}</p>
    <a class="vh-product-link" href="{escape(hrefs[0])}">{learn}</a>
    <div class="vh-feature-points" aria-label="{escape(names[0])}">{feature_points}</div>
  </div>
  <figure>
    <img src="cn/images/redesign/product-monitor.webp?v={VERSION}"
      width="542" height="530" loading="lazy" decoding="async"
      alt="{escape(names[0])}">
  </figure>
</div>"""

    cards = []
    images = [
        ("product-camera.webp", 970, 970),
        ("product-inline.webp", 970, 900),
    ]
    for (name, description, href), (image, width, height) in zip(
        data["products"][1:3], images
    ):
        index = len(cards) + 2
        cards.append(
            f"""
<article class="vh-product-card" data-reveal>
  <figure><img src="cn/images/redesign/{image}?v={VERSION}" width="{width}" height="{height}"
    loading="lazy" decoding="async" alt="{escape(name)}"></figure>
  <div class="vh-product-copy">
    <div class="vh-product-meta"><span>{index:02d}</span><span>{escape(kickers[index - 1])}</span></div>
    <h3>{escape(name)}</h3>
    <p>{escape(description)}</p>
    <a class="vh-product-link" href="{escape(href)}">{learn}</a>
  </div>
</article>"""
        )

    pair = []
    images = [
        ("product-sorter.webp", 685, 470),
        ("product-feeder.webp", 810, 1020),
    ]
    for (name, description, href), (image, width, height) in zip(
        data["products"][3:5], images
    ):
        index = len(pair) + 4
        pair.append(
            f"""
<article class="vh-product-card" data-reveal>
  <figure><img src="cn/images/redesign/{image}?v={VERSION}" width="{width}" height="{height}"
    loading="lazy" decoding="async" alt="{escape(name)}"></figure>
  <div class="vh-product-copy">
    <div class="vh-product-meta"><span>{index:02d}</span><span>{escape(kickers[index - 1])}</span></div>
    <h3>{escape(name)}</h3>
    <p>{escape(description)}</p>
    <a class="vh-product-link" href="{escape(href)}">{learn}</a>
  </div>
</article>"""
        )
    return (
        feature
        + '<div class="vh-product-grid">'
        + "".join(cards)
        + "</div>"
        + '<div class="vh-product-pair">'
        + "".join(pair)
        + "</div>"
    )


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
<meta name="theme-color" content="#f5f5f7"/>
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
        f'<article class="vh-application"><h3>{escape(title)}</h3>'
        f"<p>{escape(description)}</p></article>"
        for title, description in data["applications"]
    )
    hero_facts = "".join(
        f"<li><strong>{escape(value)}</strong><span>{escape(label)}</span></li>"
        for value, label in data["hero_facts"]
    )
    products_footer = "".join(
        f'<a href="{escape(href)}">{escape(label)}</a>'
        for label, _, href in data["products"][:5]
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
      <figcaption>{escape(data["feature_caption"])}</figcaption>
    </figure>
  </section>

  <section class="vh-manifesto" aria-labelledby="vh-manifesto-title">
    <div class="vh-manifesto-inner" data-reveal>
      <p class="vh-section-eyebrow">{escape(data["proof_eyebrow"])}</p>
      <h2 id="vh-manifesto-title">{escape(data["proof_title"])}</h2>
      <p>{escape(data["proof_body"])}</p>
    </div>
  </section>

  <div class="vh-metrics" aria-label="{escape(data["metrics"][0][1])}">
    {metrics}
  </div>

  <section class="vh-section vh-products" id="products" aria-labelledby="vh-products-title">
    <div class="vh-section-head" data-reveal>
      <h2 id="vh-products-title">{escape(data["products_title"])}</h2>
      <p>{escape(data["products_body"])}</p>
    </div>
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
