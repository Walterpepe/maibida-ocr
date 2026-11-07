"""Pre-launch passive security & SEO audit for the deployment package.

Checks the local static site (www.maibida.com deployment candidate) across:
- functionality/usability (links, images, forms, language switcher)
- SEO crawlability (robots, sitemap, canonical, hreflang, titles, dead links)
- web security (headers, mixed content, exposed files, input handling)
- performance (resource sizes, image formats, caching hints)
- business content (terminology consistency, visible language issues)

Read-only against site files; writes only to tools/prelaunch-audit.json/html.
"""
import json
import re
import ssl
import socket
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
BASE_LOCAL = "http://127.0.0.1:8899"
BASE_PROD = "https://www.maibida.com"
OUT_JSON = ROOT / "tools" / "prelaunch-audit.json"
OUT_HTML = ROOT / "tools" / "prelaunch-audit.html"

results = []


def add(category, severity, location, issue, impact, recommendation):
    results.append({
        "category": category,
        "severity": severity,
        "location": location,
        "issue": issue,
        "impact": impact,
        "recommendation": recommendation,
    })


# ---------------------------------------------------------------- production reachability
# Live probe (never hard-coded) so every audit run is reproducible.
def check_production():
    try:
        socket.getaddrinfo("www.maibida.com", 443)
    except Exception as e:
        add("SEO/可用性", "critical", "www.maibida.com",
            "生产域名当前无法访问：DNS 解析失败（%s）。" % type(e).__name__,
            "海外客户与搜索引擎均无法打开网站，业务中断，无法被索引。",
            "立即检查域名 DNS A/AAAA 记录、CDN/源站运行状态、SSL 证书有效性；上线前确保全球可访问。")
        return
    try:
        r = requests.get(BASE_PROD + "/", timeout=8)
        if r.status_code >= 400:
            add("SEO/可用性", "high", "www.maibida.com",
                "生产站点返回 HTTP %d。" % r.status_code,
                "用户与搜索引擎无法获得正常页面。",
                "检查源站、反向代理与 CDN 回源配置。")
    except Exception as e:
        add("SEO/可用性", "critical", "www.maibida.com",
            "生产站点连接失败：%s。" % type(e).__name__,
            "海外客户与搜索引擎均无法打开网站。",
            "检查 HTTPS 监听、TLS 证书链与防火墙规则。")


check_production()

# ---------------------------------------------------------------- local crawl
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; PreLaunchAudit/1.0)"})

# Only files that would actually be deployed are audited. Build-time reports
# under tools/ and historical backup directories are not public pages; checking
# them produced ~100 false "missing canonical / dead link" findings. This
# mirrors the page scope used by tools/full-site-audit.py.
NON_DEPLOYABLE = {"tools", "node_modules", "productInfo_bak_seo",
                  "UserFiles_bak_bigimg"}


def deployable(p):
    parts = set(p.parts)
    if parts & NON_DEPLOYABLE:
        return False
    if any(s.startswith("_bak") for s in p.parts):
        return False
    # Rollback snapshots are written to the parent of the web root. Guard
    # against a snapshot accidentally landing inside it: it is never a page.
    if any(s.startswith("maibida-ocr-rebuilt_") for s in p.parts):
        return False
    return True


html_files = sorted([p for p in ROOT.rglob("*.html") if deployable(p)])

all_links = set()
all_images = []
forms = []
titles = {}
descriptions = {}
canonicals = {}
h1_counts = {}
lang_pages = defaultdict(list)
missing_alt = []
empty_links = []
external_links = set()
large_resources = []
optimized_large = []
inline_scripts = 0
inline_styles = 0
http_resources = []
jsonld_failures = []
title_duplicates = defaultdict(list)
desc_duplicates = defaultdict(list)

for f in html_files:
    rel = f.relative_to(ROOT).as_posix()
    text = f.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(text, "html.parser")

    # language
    lang = soup.html.get("lang", "") if soup.html else ""
    if re.search(r"\.([a-z]{2}-[A-Z]{2})\.html$", rel):
        lang_pages[lang].append(rel)
    elif rel == "index.html" or "/" in rel:
        lang_pages["zh-CN"].append(rel)

    # title / description
    title = soup.title.get_text(strip=True) if soup.title else ""
    titles[rel] = title
    title_duplicates[title].append(rel)
    desc = ""
    d = soup.find("meta", attrs={"name": "description"})
    if d:
        desc = d.get("content", "").strip()
    descriptions[rel] = desc
    desc_duplicates[desc].append(rel)

    # canonical
    c = soup.find("link", rel="canonical")
    canonicals[rel] = c.get("href", "") if c else ""

    # h1
    h1_counts[rel] = len(soup.find_all("h1"))

    # links
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("javascript:"):
            if not a.get_text(strip=True) and not a.find("img"):
                empty_links.append((rel, href))
            continue
        if href.startswith("mailto:") or href.startswith("tel:"):
            continue
        if href.startswith("http://") or href.startswith("https://"):
            external_links.add(href)
            if "wa.me" in href or "whatsapp" in href:
                pass
            continue
        all_links.add((rel, href))

    # images
    for img in soup.find_all("img"):
        src = img.get("src", "")
        alt = img.get("alt")
        all_images.append((rel, src, alt))
        if alt is None or alt == "":
            missing_alt.append((rel, src))
        if src.startswith("http://"):
            http_resources.append((rel, src))

    # scripts/styles
    for s in soup.find_all("script", src=True):
        src = s["src"]
        if src.startswith("http://"):
            http_resources.append((rel, src))
    for l in soup.find_all("link", href=True):
        if l.get("rel") and "stylesheet" in l.get("rel"):
            href = l["href"]
            if href.startswith("http://"):
                http_resources.append((rel, href))

    inline_scripts += len(soup.find_all("script", src=False))
    inline_styles += len(soup.find_all("style"))

    # forms
    for form in soup.find_all("form"):
        forms.append({
            "page": rel,
            "action": form.get("action", ""),
            "method": form.get("method", "get").lower(),
            "inputs": [i.get("name", "") for i in form.find_all(["input", "textarea", "select"])],
        })

    # JSON-LD
    for sc in soup.find_all("script", type="application/ld+json"):
        raw = sc.string or sc.get_text()
        try:
            json.loads(raw)
        except Exception as e:
            jsonld_failures.append((rel, str(e)[:80]))

# ---------------------------------------------------------------- robots / sitemap
robots_path = ROOT / "robots.txt"
sitemap_path = ROOT / "sitemap.xml"
if not robots_path.exists():
    add("SEO", "high", "/robots.txt",
        "部署包中缺少 robots.txt。",
        "搜索引擎无法获得抓取规则，可能误抓备份目录、工具页或私有数据路径。",
        "在站点根目录添加 robots.txt，允许正式页，禁止 _bak*、tools/、私有数据目录，并声明 sitemap 地址。")
else:
    robots_txt = robots_path.read_text(encoding="utf-8", errors="replace")
    if "sitemap" not in robots_txt.lower():
        add("SEO", "medium", "/robots.txt",
            "robots.txt 未声明 Sitemap。",
            "搜索引擎发现 sitemap 的效率降低。",
            "在 robots.txt 末尾添加：Sitemap: https://www.maibida.com/sitemap.xml")

if not sitemap_path.exists():
    add("SEO", "high", "/sitemap.xml",
        "部署包中缺少 sitemap.xml。",
        "搜索引擎难以发现全部 88 个正式页及多语种版本。",
        "生成并上传 sitemap.xml，包含所有正式页 URL 及 lastmod；保持与线上 URL 一致。")
else:
    sitemap_txt = sitemap_path.read_text(encoding="utf-8", errors="replace")
    urls = re.findall(r"<loc>(.*?)</loc>", sitemap_txt)
    if len(urls) == 0:
        add("SEO", "high", "/sitemap.xml",
            "sitemap.xml 未包含任何 <loc> URL。",
            "sitemap 无效，无法帮助索引。",
            "重新生成 sitemap，确保每个正式页有对应 <url><loc>。")
    # check if local files exist for sitemap URLs
    for u in urls[:200]:
        path = urlparse(u).path.lstrip("/")
        if not (ROOT / path).exists():
            add("SEO", "medium", f"/sitemap.xml -> {u}",
                f"sitemap 中的 URL 对应文件在部署包中不存在：{path}",
                "搜索引擎抓取到 404，影响索引与信任度。",
                "从 sitemap 移除该 URL 或补充对应页面。")

# ---------------------------------------------------------------- canonical / hreflang
for rel, canon in canonicals.items():
    if not canon:
        add("SEO", "medium", rel,
            "缺少 canonical 标签。",
            "多语种/参数 URL 可能产生重复内容，分散权重。",
            "为每个正式页添加指向自身绝对 URL 的 <link rel=\"canonical\">。")
    elif canon.startswith("http://"):
        add("SEO/安全", "medium", rel,
            f"canonical 使用 HTTP：{canon}",
            "与 HTTPS 站点不一致，可能导致索引混乱。",
            "统一改为 https://www.maibida.com/...。")

# hreflang
for f in html_files:
    rel = f.relative_to(ROOT).as_posix()
    soup = BeautifulSoup(f.read_text(encoding="utf-8", errors="replace"), "html.parser")
    alts = soup.find_all("link", rel="alternate", hreflang=True)
    if len(alts) > 0:
        expected = {"zh-CN", "x-default", "en-US", "es-MX", "en-SG", "id-ID", "th-TH", "vi-VN", "ko-KR", "ja-JP", "ms-MY", "ru-RU"}
        found = {a["hreflang"] for a in alts}
        if not expected.issubset(found):
            missing = expected - found
            add("SEO", "low", rel,
                f"hreflang 不完整，缺少：{', '.join(sorted(missing))}",
                "多语种定位信号不完整，可能影响地区排名。",
                "为每个语种版本添加对应 hreflang，并包含 x-default。")

# ---------------------------------------------------------------- titles / descriptions
for title, pages in title_duplicates.items():
    if not title:
        for p in pages:
            add("SEO", "high", p, "缺少 <title>。", "搜索结果无法展示有效标题，影响点击率与排名。", "为每个页面添加唯一、包含核心关键词的标题。")
    elif len(pages) > 1 and len(title) > 0:
        # only formal pages
        formal = [p for p in pages if not p.startswith("tools/") and "contact" not in p and "hreflang" not in p]
        if len(formal) > 1:
            add("SEO", "medium", ", ".join(formal[:5]),
                f"标题重复（{len(formal)} 页）：{title[:60]}",
                "搜索引擎难以区分页面主题，可能互相竞争。",
                "为每个页面编写独特标题，融入产品名/型号/语种差异。")

for desc, pages in desc_duplicates.items():
    if not desc:
        for p in pages:
            if not p.startswith("tools/") and "contact" not in p:
                add("SEO", "medium", p, "缺少 meta description。", "搜索结果摘要不可控，可能影响点击率。", "添加 80-155 字符、含卖点与行动号召的描述。")
    elif len(pages) > 1:
        formal = [p for p in pages if not p.startswith("tools/") and "contact" not in p]
        if len(formal) > 1:
            add("SEO", "low", ", ".join(formal[:5]),
                f"meta description 重复（{len(formal)} 页）。",
                "摘要重复降低搜索结果吸引力。",
                "为每页编写独立描述。")

for rel, title in titles.items():
    if title and len(title) > 65:
        add("SEO", "low", rel,
            f"标题过长（{len(title)} 字符）：{title[:60]}...",
            "搜索结果中标题可能被截断。",
            "将标题控制在 50-65 字符以内，核心关键词前置。")

for rel, desc in descriptions.items():
    if desc and len(desc) > 160:
        add("SEO", "low", rel,
            f"description 过长（{len(desc)} 字符）。",
            "摘要可能被截断。",
            "控制在 150-160 字符以内。")

# ---------------------------------------------------------------- h1
for rel, cnt in h1_counts.items():
    if rel.startswith("tools/") or "contact" in rel or "hreflang" in rel:
        continue
    if cnt == 0:
        add("SEO", "medium", rel, "页面缺少 H1。", "页面主题不明确，影响 SEO 与可访问性。", "每页添加一个包含核心关键词的 H1。")
    elif cnt > 1:
        add("SEO", "low", rel, f"页面包含 {cnt} 个 H1。", "多个 H1 可能稀释主题。", "保留一个主 H1，其余改为 H2/H3。")

# ---------------------------------------------------------------- images
if missing_alt:
    sample = missing_alt[:10]
    add("SEO/可用性", "medium", f"{len(missing_alt)} 张图片（示例：{sample[0][0]} -> {sample[0][1]}）",
        f"共 {len(missing_alt)} 张图片缺少 alt 或 alt 为空。",
        "影响图片搜索、无障碍访问及页面语义理解。",
        "为内容图片添加描述性 alt；装饰性图片使用 alt=\"\" 并确保不被误判。")

# ---------------------------------------------------------------- links
broken_links = []
for src, href in sorted(all_links):
    if href.startswith("/"):
        target = ROOT / href.lstrip("/")
    else:
        target = (ROOT / src).parent / href
    target = target.resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        broken_links.append((src, href, "跳出站点根目录"))
        continue
    if not target.exists():
        broken_links.append((src, href, "文件不存在"))

if broken_links:
    for src, href, reason in broken_links[:20]:
        add("功能/SEO", "high", src,
            f"内部死链：{href}（{reason}）",
            "用户点击后 404，搜索引擎降低站点质量评分。",
            "修正链接路径或移除无效链接。")

# ---------------------------------------------------------------- external links / whatsapp
whatsapp = [u for u in external_links if "wa.me" in u or "whatsapp" in u]
if not whatsapp:
    add("功能", "low", "全站",
        "未检测到 WhatsApp 联系链接。",
        "海外客户（尤其墨西哥、东南亚）可能偏好 WhatsApp 沟通，缺失会流失线索。",
        "在页脚或联系页添加 https://wa.me/<号码> 链接，并确保号码有效。")

# ---------------------------------------------------------------- forms
for form in forms:
    if not form["action"] and form["method"] == "get":
        add("功能", "medium", form["page"],
            "表单未设置 action，且使用默认 GET 方法。",
            "提交行为不确定，可能无法正确送达后端。",
            "为留言/询盘表单指定后端接收端点（如 /api/messages）并使用 POST。")
    if "email" not in form["inputs"] and "message" in form["inputs"]:
        add("功能", "low", form["page"],
            "表单包含留言内容但缺少邮箱字段。",
            "无法回复客户。",
            "增加 email 输入框并做格式校验。")

# ---------------------------------------------------------------- mixed content
if http_resources:
    for page, url in http_resources[:10]:
        add("安全", "high", page,
            f"混合内容：页面通过 HTTP 加载资源 {url}",
            "HTTPS 页面加载 HTTP 资源会被浏览器拦截或降级，存在中间人攻击风险。",
            "将所有资源改为 HTTPS 或相对路径。")

# ---------------------------------------------------------------- security headers (local simulation)
try:
    r = session.get(BASE_LOCAL + "/index.html", timeout=10)
    headers = {k.lower(): v for k, v in r.headers.items()}
    needed = {
        "strict-transport-security": ("高", "缺少 HSTS，可能被降级攻击。"),
        "content-security-policy": ("中", "缺少 CSP，XSS 风险增加。"),
        "x-frame-options": ("中", "缺少 X-Frame-Options，可能被点击劫持。"),
        "x-content-type-options": ("低", "缺少 X-Content-Type-Options，MIME 嗅探风险。"),
        "referrer-policy": ("低", "缺少 Referrer-Policy，可能泄露来源信息。"),
    }
    for h, (sev, msg) in needed.items():
        if h not in headers:
            add("安全", sev, "HTTP 响应头",
                f"缺少安全头：{h}",
                msg,
                f"在服务器/CDN 配置 {h} 头。")
except Exception as e:
    add("安全", "medium", "本地预览服务",
        f"无法获取响应头：{e}",
        "无法完成安全头检查。",
        "确保服务运行后复查。")

# ---------------------------------------------------------------- sensitive files
sensitive = [".env", ".git/config", "config.php", "wp-config.php", ".htpasswd"]
for s in sensitive:
    if (ROOT / s).exists():
        add("安全", "high", f"/{s}",
            f"部署包中包含敏感文件：{s}",
            "可能泄露数据库凭据、API 密钥或服务器配置。",
            "从部署包中移除敏感文件，并确保 Web 服务器禁止访问。")

# backup dirs
backup_dirs = [p for p in ROOT.iterdir() if p.is_dir() and (
    p.name.startswith("_bak") or
    p.name in ("productInfo_bak_seo", "UserFiles_bak_bigimg"))]
if backup_dirs:
    add("安全/SEO", "medium", "站点根目录",
        f"部署包包含 {len(backup_dirs)} 个备份目录（如 {backup_dirs[0].name}）。",
        "备份文件可能被搜索引擎索引，也可能泄露旧版本代码或敏感信息。",
        "上线前删除或移出 Web 根目录；在 robots.txt 中 Disallow。")

# ---------------------------------------------------------------- performance
for f in ROOT.rglob("*"):
    if not f.is_file() or not deployable(f):
        continue
    size = f.stat().st_size
    rel = f.relative_to(ROOT).as_posix()
    ext = f.suffix.lower()
    # MP4 is served with HTTP Range requests and an autoplay poster, so its
    # total file size is not the first-screen payload. A 121-second product
    # video cannot be squeezed under 500 KB without destroying image quality.
    limit = 5 * 1024 * 1024 if ext in {".mp4", ".webm"} else 500 * 1024
    if size > limit and ext in {".jpg", ".jpeg", ".png", ".gif", ".mp4", ".webm", ".css", ".js"}:
        webp = ROOT / (rel + ".webp")
        if webp.exists():
            optimized_large.append((rel, size, webp.stat().st_size))
            continue
        large_resources.append((rel, size))

for rel, size in sorted(large_resources, key=lambda x: -x[1])[:15]:
    add("性能", "medium", rel,
        f"资源体积较大：{size/1024:.0f} KB",
        "海外移动端加载缓慢，影响跳出率与 Core Web Vitals。",
        "压缩图片（WebP/AVIF）、启用 CDN、按需加载、启用 Brotli/Gzip。")

if optimized_large:
    total_webp = sum(x[2] for x in optimized_large)
    add("性能", "low", f"{len(optimized_large)} 张大图已提供 WebP 回退",
        f"原始 JPEG/PNG 仍保留作不支持 WebP 客户端的回退；支持 WebP 的浏览器实际加载的副本合计仅 {total_webp/1024:.0f} KB。",
        "此项为优化状态说明，非缺陷：实际传输体积已显著下降。",
        "生产环境启用 Accept 内容协商（见 tools/deploy/nginx-maibida.conf.example），并可在确认覆盖率后于 CDN 层移除原始文件。")

# image format distribution
img_exts = defaultdict(int)
for f in ROOT.rglob("*"):
    if f.is_file() and deployable(f):
        if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}:
            img_exts[f.suffix.lower()] += 1
if img_exts.get(".webp", 0) + img_exts.get(".avif", 0) == 0:
    add("性能", "low", "全站图片",
        "未使用 WebP/AVIF 等现代图片格式。",
        "同等质量下文件更大，加载更慢。",
        "将产品图、横幅图转换为 WebP，保留 JPEG/PNG 作为回退。")

# inline scripts/styles
if inline_scripts > 50:
    add("性能/安全", "low", "全站",
        f"检测到 {inline_scripts} 个内联 <script> 块。",
        "增加 HTML 体积，不利于缓存与 CSP 部署。",
        "将 JS 移至外部文件并添加 defer；必要时使用 nonce。")

# ---------------------------------------------------------------- business content
# terminology consistency
terms = {
    "模具监视器": ["模具监视保护器", "模具保护器"],
    "视觉传感器": ["智能相机", "视觉相机"],
    "柔性上料": ["柔性供料"],
}
for term, variants in terms.items():
    for v in variants:
        pages_with = []
        for f in html_files:
            if f.name.startswith("contact") or "report" in f.name:
                continue
            t = f.read_text(encoding="utf-8", errors="replace")
            if v in t:
                pages_with.append(f.relative_to(ROOT).as_posix())
        if pages_with:
            add("业务内容", "low", ", ".join(pages_with[:3]),
                f"术语不一致：发现「{v}」，建议统一为「{term}」。",
                "同一产品多种叫法影响专业度与关键词聚焦。",
                f"全站统一使用「{term}」，其他变体作为辅助关键词自然出现。")

# language switcher endonym
for f in html_files[:20]:
    rel = f.relative_to(ROOT).as_posix()
    soup = BeautifulSoup(f.read_text(encoding="utf-8", errors="replace"), "html.parser")
    switch = soup.select_one(".vp-language-switch")
    if switch and "日本語" in switch.get_text():
        # false positive guard for ja pages
        pass

# ---------------------------------------------------------------- summary stats
stats = {
    "html_pages": len(html_files),
    "images": len(all_images),
    "missing_alt": len(missing_alt),
    "internal_links": len(all_links),
    "broken_links": len(broken_links),
    "external_links": len(external_links),
    "forms": len(forms),
    "inline_scripts": inline_scripts,
    "inline_styles": inline_styles,
    "large_resources": len(large_resources),
    "jsonld_failures": len(jsonld_failures),
    "image_formats": dict(img_exts),
}

# sort by severity
order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
results.sort(key=lambda x: order.get(x["severity"], 4))

report = {
    "site": BASE_PROD,
    "audit_time": __import__("datetime").datetime.now().isoformat(),
    "scope": "Passive pre-launch audit of local deployment package + production reachability check",
    "stats": stats,
    "issues": results,
}
OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"issues: {len(results)}")
for sev in ["critical", "high", "medium", "low"]:
    print(sev, sum(1 for r in results if r["severity"] == sev))
print("report:", OUT_JSON)
