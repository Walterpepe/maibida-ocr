"""Build a human-readable pre-launch audit report."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "tools" / "prelaunch-audit.json").read_text(encoding="utf-8"))

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEV_LABEL = {"critical": "严重", "high": "高危", "medium": "中危", "low": "低危"}
SEV_CLASS = {"critical": "critical", "high": "high", "medium": "medium", "low": "low"}

# group issues into buckets
buckets = {
    "critical": [],
    "high": [],
    "medium": [],
    "low": [],
}
for issue in data["issues"]:
    sev = issue["severity"]
    if sev in ("高", "高危"):
        sev = "high"
    elif sev in ("中", "中危"):
        sev = "medium"
    elif sev in ("低", "低危"):
        sev = "low"
    elif sev in ("严重",):
        sev = "critical"
    buckets[sev].append(issue)

# classify must-fix vs SEO suggestion
MUST_FIX = []
SEO_SUGGEST = []
for issue in data["issues"]:
    cat = issue["category"]
    sev = issue["severity"]
    if sev in ("高", "高危"):
        sev = "high"
    elif sev in ("中", "中危"):
        sev = "medium"
    elif sev in ("低", "低危"):
        sev = "low"
    elif sev in ("严重",):
        sev = "critical"
    if "安全" in cat or "功能" in cat or "可用性" in cat or sev == "critical":
        MUST_FIX.append(issue)
    else:
        SEO_SUGGEST.append(issue)

MUST_FIX.sort(key=lambda x: SEV_ORDER.get(x["severity"], 4))
SEO_SUGGEST.sort(key=lambda x: SEV_ORDER.get(x["severity"], 4))

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>maibida.com 上线前安全 & SEO 审计报告</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:Arial,"Microsoft YaHei",sans-serif;margin:0;background:#f5f7fa;color:#1a202c;line-height:1.6}}
.container{{max-width:1200px;margin:0 auto;padding:24px}}
h1{{font-size:28px;margin:0 0 8px;color:#0f3d2e}}
h2{{font-size:22px;margin:32px 0 12px;color:#0f3d2e;border-left:4px solid #009944;padding-left:12px}}
h3{{font-size:18px;margin:24px 0 8px;color:#17352a}}
.meta{{color:#5c6871;font-size:14px;margin-bottom:24px}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:20px 0}}
.stat{{background:#fff;border:1px solid #dfe7e3;border-radius:10px;padding:14px;text-align:center}}
.stat .n{{font-size:26px;font-weight:700;color:#009944}}
.stat .l{{font-size:13px;color:#5c6871}}
.issue{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px;margin:12px 0;border-left:4px solid #cbd5e0}}
.issue.critical{{border-left-color:#c0392b}}
.issue.high{{border-left-color:#e74c3c}}
.issue.medium{{border-left-color:#f39c12}}
.issue.low{{border-left-color:#3498db}}
.issue .head{{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}}
.issue .sev{{font-size:12px;font-weight:700;padding:2px 8px;border-radius:4px;color:#fff;text-transform:uppercase}}
.sev.critical{{background:#c0392b}}
.sev.high{{background:#e74c3c}}
.sev.medium{{background:#f39c12}}
.sev.low{{background:#3498db}}
.issue .loc{{font-family:monospace;font-size:13px;color:#4a5568;word-break:break-all}}
.issue .title{{font-weight:700;margin:8px 0 4px;font-size:16px}}
.issue .impact,.issue .rec{{font-size:14px;margin:6px 0}}
.issue .impact{{color:#744210}}
.issue .rec{{color:#22543d}}
.section-note{{background:#fffbea;border:1px solid #f6e05e;border-radius:8px;padding:12px;font-size:14px;margin:12px 0}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;margin:12px 0}}
th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid #e2e8f0;font-size:14px}}
th{{background:#edf2f7;font-weight:700}}
tr:hover{{background:#f7fafc}}
</style>
</head>
<body>
<div class="container">
<h1>maibida.com 上线前安全 & SEO 审计报告</h1>
<div class="meta">
审计时间：{data['audit_time']}<br/>
审计范围：被动式检查（不执行注入/攻击性测试）<br/>
目标站点：https://www.maibida.com<br/>
审计对象：本地部署包 {data['stats']['html_pages']} 个 HTML 页面 + 线上可达性探测
</div>

<div class="stats">
<div class="stat"><div class="n">{data['stats']['html_pages']}</div><div class="l">HTML 页面</div></div>
<div class="stat"><div class="n">{data['stats']['images']}</div><div class="l">图片引用</div></div>
<div class="stat"><div class="n">{data['stats']['internal_links']}</div><div class="l">内部链接</div></div>
<div class="stat"><div class="n">{data['stats']['broken_links']}</div><div class="l">死链</div></div>
<div class="stat"><div class="n">{len(data['issues'])}</div><div class="l">发现问题</div></div>
</div>

<div class="section-note">
<strong>重要发现：</strong>生产域名 <code>www.maibida.com</code> 当前无法访问（DNS 解析失败 / 502 Bad Gateway）。
以下问题基于本地部署包扫描，上线前请优先解决严重与高危项。
</div>

<h2>一、必须修复（漏洞 / 功能 bug）</h2>
"""

for issue in MUST_FIX:
    sev = issue["severity"]
    if sev in ("高", "高危"):
        sev = "high"
    elif sev in ("中", "中危"):
        sev = "medium"
    elif sev in ("低", "低危"):
        sev = "low"
    elif sev in ("严重",):
        sev = "critical"
    html += f"""
<div class="issue {SEV_CLASS[sev]}">
  <div class="head">
    <span class="sev {SEV_CLASS[sev]}">{SEV_LABEL[sev]}</span>
    <span class="loc">{issue['location']}</span>
  </div>
  <div class="title">{issue['issue']}</div>
  <div class="impact"><strong>影响：</strong>{issue['impact']}</div>
  <div class="rec"><strong>修复建议：</strong>{issue['recommendation']}</div>
</div>
"""

html += "<h2>二、SEO 优化建议</h2>"

for issue in SEO_SUGGEST:
    sev = issue["severity"]
    if sev in ("高", "高危"):
        sev = "high"
    elif sev in ("中", "中危"):
        sev = "medium"
    elif sev in ("低", "低危"):
        sev = "low"
    elif sev in ("严重",):
        sev = "critical"
    html += f"""
<div class="issue {SEV_CLASS[sev]}">
  <div class="head">
    <span class="sev {SEV_CLASS[sev]}">{SEV_LABEL[sev]}</span>
    <span class="loc">{issue['location']}</span>
  </div>
  <div class="title">{issue['issue']}</div>
  <div class="impact"><strong>影响：</strong>{issue['impact']}</div>
  <div class="rec"><strong>修复建议：</strong>{issue['recommendation']}</div>
</div>
"""

html += f"""
<h2>三、上线前检查清单</h2>
<table>
<tr><th>优先级</th><th>事项</th><th>负责人</th></tr>
<tr><td> P0 </td><td>恢复 www.maibida.com 域名解析与 HTTPS 访问</td><td>运维 / 域名商</td></tr>
<tr><td> P0 </td><td>配置 HSTS、CSP、X-Frame-Options 等安全响应头</td><td>运维 / CDN</td></tr>
<tr><td> P0 </td><td>修复部署包中 495 条内部死链（重点：productInfo_bak_seo 目录）</td><td>前端</td></tr>
<tr><td> P1 </td><td>删除或隔离 _bak* 备份目录，禁止搜索引擎抓取</td><td>运维</td></tr>
<tr><td> P1 </td><td>为 231 张图片补充有效 alt 文本</td><td>内容 / SEO</td></tr>
<tr><td> P1 </td><td>压缩大体积图片与视频（最大 9.7 MB），启用 WebP/AVIF</td><td>前端 / 设计</td></tr>
<tr><td> P1 </td><td>为 11 个留言页添加 canonical 与 meta description</td><td>前端</td></tr>
<tr><td> P2 </td><td>增加 WhatsApp 海外联系入口</td><td>业务 / 前端</td></tr>
<tr><td> P2 </td><td>统一产品术语（如“模具监视器” vs “模具监视保护器”）</td><td>内容</td></tr>
</table>

<h2>四、审计限制</h2>
<ul>
<li>本次为<strong>被动式审计</strong>，未执行 SQL 注入、XSS 弹窗、暴力破解等攻击性测试。</li>
<li>线上服务当前不可达，安全头与服务器配置检查基于本地预览服务推断，实际上线后需复查。</li>
<li>性能数据基于文件体积静态分析，未进行真实海外节点测速。</li>
<li>业务文案语法检查以术语一致性为主，未做全语种人工润色。</li>
</ul>

</div>
</body>
</html>
"""

(ROOT / "tools" / "prelaunch-audit.html").write_text(html, encoding="utf-8")
print("report written:", ROOT / "tools" / "prelaunch-audit.html")
print("must_fix:", len(MUST_FIX), "seo_suggest:", len(SEO_SUGGEST))
