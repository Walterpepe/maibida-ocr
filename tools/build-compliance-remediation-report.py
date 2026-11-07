"""Build the H1-H6 + M/O compliance remediation report (HTML)."""
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"


def load(name):
    return json.loads((TOOLS / name).read_text(encoding="utf-8"))


def esc(s):
    return html.escape(str(s), quote=True)


V = load("compliance-remediation-verify.json")
SA = load("site-audit.json")
SC = load("google-crawl-score.json")
MF = load("message-feature-verify.json")
PL = load("prelaunch-audit.json")
RT = load("compliance-runtime.json")
CP = load("compliance-pages.json")
PG = load("policy-pages.json")
WM = load("watermark-fix.json")

levels = {}
for i in SA["issues"]:
    levels[i["level"]] = levels.get(i["level"], 0) + 1
rt = RT["summary"]
PAGES_CHECKED = SA["stats"]["pages_checked"]
REFS = SA.get("asset_references", "—")
WM_DIR = next((p for p in Path(WM["original_backup"]).parts
               if p.startswith("maibida-ocr-rebuilt_watermark_original_")), "水印原图备份")
INLINE = sum(1 for i in PL["issues"] if "内联" in i["issue"])

HIGH = [
    ("H1", "生产域名不可达", "www.maibida.com DNS / 80 / 443 / robots.txt / sitemap.xml",
     "DNS 返回 NXDOMAIN，HTTPS 502；六个目标市场与 Googlebot 完全无法访问，任何 SEO/合规整改在域名恢复前不生效。",
     "本地部署包无法修改注册商 DNS。已交付 tools/deploy/check-production.sh（12 项上线验收）、nginx-maibida.conf.example（301/TLS/反代/限流）与 nginx-security-headers.conf；审计脚本保持每次实跑 DNS+HTTPS 动态探测。",
     "PENDING", "需用户在注册商配置 A/AAAA 或 CNAME、部署证书链并跑验收脚本"),
    ("H2", "缺少隐私政策与主动同意", "106 页原无政策页；11 个 contact 表单采集姓名/邮箱/电话/公司/国家/留言",
     "墨西哥 LFPDPPP、西班牙 GDPR/LOPDGDD、新加坡 PDPA、越南 Decree 13、泰国 PDPA、韩国 PIPA 均要求完整告知与可举证的同意；「提交即同意」为默示同意。",
     "新建 11 语种《隐私政策》+ 11 语种《销售条款与技术声明》（共 22 页，10 节合规要素）；88 页页脚加本地化链接；11 个表单改为未预勾选 checkbox + 政策链接 + honeypot + 备用邮箱；服务端记录 consent/版本/时间/IP 哈希/24 个月保留期；新增到期清理脚本。",
     "DONE", "22 页齐全 / 88 页链接 / 11 页 checkbox / 65 项功能验证通过"),
    ("H3", "留言接口依赖本地 Node", "11 个 contact 页 POST /api/messages",
     "纯静态托管/CDN 上线后接口 404，询盘静默丢失，前端无明确失败反馈。",
     "接收端加同源校验、每 IP 每分钟 8 次限流、honeypot、体大小限制、consent 强校验、保留期限与 chmod 600；前端加 10s 超时、分类错误提示与 mailto 备用渠道；生产 Nginx 提供 /api/messages 反代 + limit_req；附进程守护与验收说明。",
     "DONE", "65/65 功能验证（含真实提交落盘、无 consent 400、honeypot 不落盘、429/415）"),
    ("H4", "「100% 全检零遗漏」绝对化承诺", "productlist/10034 及 10 个语种变体",
     "检出率受工件/光照/治具/参数影响，无条件承诺在中国广告法、欧盟 UCPD、墨西哥 LFPC、韩国标示广告法下属误导性保证，已在 11 语种扩散。",
     "11 语种统一改为「支持产线全数在线检测；实际表现以双方技术协议与验收标准为准」；全站绝对化词表扫描 0 确凿命中（销售条款中「不代表任何条件下均达到 100% 检出」为免责表述，保留）。",
     "DONE", "11/11 语种 CLEAN，条件化表述 11/11 落地"),
    ("H5", "百度 AI 生成第三方水印图", "UserFiles/.../6390268955757181277238280.jpg，11 个 10036 页引用",
     "第三方平台中文水印用于商业展示存在条款与授权争议；采购商易误认为实物或真实检测效果。",
     "右下角纯白区域重绘清除水印（原图完整保留于站点外）；11 页 alt/图注/sr-only 转录改为「示意图、非实际产品照片」；同步更新 T8 转录译文数据，评分仍按真实 DOM 动态检测。",
     "DONE", "像素级复核水印为 0、11 页三处文案同步、100 分未回归"),
    ("H6", "参数页缺免责与适用性声明", "7 个产品/列表页 × 11 语种 = 77 页；±0.02mm / 4500 PCS/H / 8MP 等",
     "网页列明精度与节拍却无「仅供选型参考、以技术协议为准」，B2B 设备采购商可直接援引主张违约。",
     "77 页参数表下新增 11 语种技术声明（工况依赖、非性能保证、规格可变更）；新建销售条款页涵盖网页性质、保修除外、责任限制、适用法律；88 页页脚链接。",
     "DONE", "77/77 页声明、22 页政策/条款、88 页页脚链接"),
]

MEDIUM = [
    ("M1", "11 个首页无页脚", "复用对应语种产品页页脚模板并修正相对路径，注入 11 个首页", "DONE"),
    ("M2", "备案号占位残缺", "移除无编号的「苏ICP备」占位链接（0 残留）；真实备案号需用户提供后补", "PARTIAL"),
    ("M3", "电话/邮箱为纯文本", "88 页包为 tel:+8615995675085 与 mailto: 链接；运行时 27/27 页可点击", "DONE"),
    ("M4", "Sony 指示性使用", "表头与值改为各语种「图像传感器 / 8 MP CMOS（第三方供应）」，全站 Sony 字样 0", "DONE"),
    ("M5", "「保证产品交期」", "11 语种改为「有助于稳定生产计划 / 稳定化に寄与」等条件化表述", "DONE"),
    ("M6", "西班牙市场无 es-ES 变体", "语言菜单 88 页统一标注 Español (Latinoamérica)；交付 add-es-ES-variant.py（默认 dry-run，含 sitemap/评分口径后续步骤）", "DECISION"),
    ("M7", "俄/韩/泰/越/日表头混入 sensor", "11 语种表头本地化为图像传感器，未译词 0", "DONE"),
    ("M8", "生产未启用 WebP 协商", "Nginx 样例含 map $http_accept + Vary: Accept + 缓存；验收脚本第 12 项实测", "DONE"),
    ("M9", "生产安全头/接口限流/数据生命周期", "8 类头实测齐全；反代加 limit_req；NDJSON 限权 + 24 个月 retentionUntil + 到期清理脚本", "DONE"),
]

OPT = [
    ("O1", "日语「最高速度/最高10个」", "4 处改为「最大」，日本景品表示法敏感词规避", "DONE"),
    ("O2", "en-SG 留言页标题重复", "改为 Leave a Message (Singapore / Asia-Pacific)；政策/条款 en-SG 标题与描述亦已区分", "DONE"),
    ("O3", "图片二进制内嵌中文", "保持既有 11 语种 sr-only 转录；设备实拍/UI 截图/铭牌无法随语言切换，未改图片文件", "KEPT"),
    ("O4", "WhatsApp 号码需人工确认", "88 页链接格式一致合法；需人工确认已注册 WhatsApp Business 且可接收海外消息", "USER"),
    ("O5", "首页面包屑", "11 个首页补 BreadcrumbList JSON-LD（无视觉改动）", "DONE"),
    ("O6", "首页未展示公司法定名称/地址", "随 M1 统一页脚一并补齐", "DONE"),
    ("O7", "WhatsApp 图标资产", "保持文字/字符型入口，未引入第三方 logo，无商标风险", "KEPT"),
    ("O8", "缺 GA4 / Search Console", "未擅自注入第三方追踪脚本（会破坏 CSP 与隐私政策的「无第三方追踪」承诺）；上线后按需配套 Cookie 同意再部署", "USER"),
]

STATUS = {
    "DONE": ("已整改", "#087b3d", "#e8f5ee"),
    "PARTIAL": ("部分整改", "#a06a00", "#fff5e0"),
    "DECISION": ("业务决策", "#1c5f9e", "#e8f1fb"),
    "PENDING": ("待用户操作", "#b3261e", "#fdecea"),
    "KEPT": ("保持现状", "#5c6871", "#eef1f3"),
    "USER": ("需人工确认", "#a06a00", "#fff5e0"),
}


def badge(s):
    label, fg, bg = STATUS[s]
    return f'<span class="badge" style="color:{fg};background:{bg}">{esc(label)}</span>'


def rows(items, cols):
    out = []
    for it in items:
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in it) + "</tr>")
    return "\n".join(out)


high_rows = rows([
    (f'<b>{esc(k)}</b>', esc(name), esc(loc), esc(risk), esc(fix), badge(st) + "<br/><small>" + esc(note) + "</small>")
    for k, name, loc, risk, fix, st, note in HIGH], 6)
med_rows = rows([(f"<b>{esc(k)}</b>", esc(n), esc(f), badge(st)) for k, n, f, st in MEDIUM], 4)
opt_rows = rows([(f"<b>{esc(k)}</b>", esc(n), esc(f), badge(st)) for k, n, f, st in OPT], 4)

verdict = ("结论：除 H1 外，上线前全项预审列出的所有高危、中风险与可自动化优化项均已在本地部署包中整改完毕；"
           "机械性检测（功能/SEO/内容）全部达标。但 H1 生产域名仍不可达，属上线阻断项，"
           "<b>当前不满足上线条件</b>。须完成域名解析与 HTTPS 部署、跑通 check-production.sh，"
           "并从六个目标市场实测复验后方可上线。")

doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>合规整改报告 · H1–H6 | Maibida</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#f4f7f5;color:#22303a;font-family:Arial,"Microsoft YaHei","PingFang SC",sans-serif;line-height:1.7}}
.wrap{{max-width:1180px;margin:0 auto;padding:32px 20px 80px}}
h1{{font-size:30px;margin:0 0 8px;color:#17352a}}
.sub{{color:#5c6871;margin:0 0 26px}}
.banner{{padding:18px 22px;border-radius:12px;background:#fff5e0;border-left:5px solid #d99200;margin:0 0 24px;font-size:15px}}
.banner b{{color:#8a5a00}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:0 0 30px}}
.card{{background:#fff;border:1px solid #dfe7e3;border-radius:12px;padding:16px 18px}}
.card .n{{font-size:26px;font-weight:800;color:#087b3d;line-height:1.2}}
.card .l{{font-size:13px;color:#5c6871;margin-top:4px}}
h2{{font-size:21px;margin:34px 0 12px;color:#17352a;border-bottom:2px solid #d7e5dd;padding-bottom:8px}}
table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid #dfe7e3;border-radius:10px;overflow:hidden;font-size:14px}}
th{{background:#eef4f0;text-align:left;padding:11px 12px;color:#17352a;font-size:13px}}
td{{padding:11px 12px;border-top:1px solid #edf1ef;vertical-align:top}}
tr:hover td{{background:#fafcfb}}
.badge{{display:inline-block;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:700;white-space:nowrap}}
small{{color:#5c6871;font-size:12px}}
.note{{background:#fff;border:1px solid #dfe7e3;border-left:4px solid #009944;border-radius:10px;padding:16px 20px;margin:16px 0}}
ul{{margin:8px 0 0;padding-left:20px}} li{{margin:4px 0}}
code{{background:#eef2f0;padding:1px 5px;border-radius:4px;font-size:12px}}
.foot{{margin-top:36px;color:#68747d;font-size:13px}}
</style></head><body><div class="wrap">
<h1>上线前全项预审 · 整改报告</h1>
<p class="sub">站点 www.maibida.com ｜ 目标市场：墨西哥 / 西班牙 / 新加坡 / 越南 / 泰国 / 韩国 ｜ 生成时间 {esc(datetime.now().strftime('%Y-%m-%d %H:%M'))}</p>

<div class="banner"><b>⚠️ 唯一未闭环的 P0：H1 生产域名不可达。</b> DNS 仍返回 NXDOMAIN，本地部署包无法代替注册商配置。
已完成的所有整改在域名恢复前不产生上线效果。请按 <code>tools/deploy/check-production.sh</code> 验收。</div>

<div class="cards">
<div class="card"><div class="n">{V['passed']}/{V['total']}</div><div class="l">整改独立验证</div></div>
<div class="card"><div class="n">{MF['passed']}/{MF['total']}</div><div class="l">留言功能验证</div></div>
<div class="card"><div class="n">{levels.get('error',0)} / {levels.get('warning',0)}</div><div class="l">全站错误 / 警告</div></div>
<div class="card"><div class="n">{SC['score']:.1f}</div><div class="l">Google 抓取评分</div></div>
<div class="card"><div class="n">{PAGES_CHECKED}</div><div class="l">检测页面数</div></div>
<div class="card"><div class="n">{rt['http_ok']}/{rt['checked']}</div><div class="l">运行时 HTTP 200</div></div>
</div>

<h2>一、高危项 H1–H6</h2>
<table><thead><tr><th style="width:52px">编号</th><th style="width:150px">问题</th><th style="width:190px">位置</th><th>风险</th><th>整改动作</th><th style="width:150px">状态</th></tr></thead>
<tbody>{high_rows}</tbody></table>

<h2>二、中风险 M1–M9</h2>
<table><thead><tr><th style="width:52px">编号</th><th style="width:230px">问题</th><th>整改动作</th><th style="width:120px">状态</th></tr></thead>
<tbody>{med_rows}</tbody></table>

<h2>三、优化建议 O1–O8</h2>
<table><thead><tr><th style="width:52px">编号</th><th style="width:250px">建议</th><th>处理</th><th style="width:120px">状态</th></tr></thead>
<tbody>{opt_rows}</tbody></table>

<h2>四、验证结果与口径</h2>
<div class="note"><ul>
<li><b>整改专项</b>：{V['passed']}/{V['total']} 项通过（政策页要素、同意机制、水印像素、11 语种文案、77 页免责、页脚链接、回归指标逐条实测）。</li>
<li><b>全站检测</b>：{PAGES_CHECKED} 页 / {REFS} 条引用，<b>0 错误 / 0 警告</b>，{levels.get('info', 0)} 条提示（留言页、政策页与工具页的性质说明）。</li>
<li><b>Google 抓取评分</b>：{SC['score']:.1f}/100，四维全满（30/30、30/30、25/25、15/15），静态失败项为空。</li>
<li><b>留言功能</b>：{MF['passed']}/{MF['total']} 通过，含真实提交落盘、consent 必填、honeypot 不落盘、405/415/429/403 边界；自测记录已清理。</li>
<li><b>运行时抽查</b>：{rt['checked']} 页双视口（1440×900 / 390×844）HTTP 全 200，破图 0、乱码 0、JS 报错 0、横向溢出 0、语言菜单 27/27 可展开；tel/mailto/WhatsApp 入口已生效。</li>
<li><b>预上线审计</b>：从整改前的 161 条问题降至 {len(PL['issues'])} 条 —— 1 条 critical 即 H1 域名，4 条 low（WebP 回退状态说明、{INLINE} 项历史内联脚本说明、2 条产品正式命名术语）。<b>0 高危 / 0 中危</b>。</li>
<li><b>口径修正</b>：语言菜单标注的回滚快照曾被误放在站点根目录，导致审计把 88 个备份页当成上线页并产生 203 条误报；已移出 Web 根目录，并在 prelaunch-audit.py 的 deployable() 加通用排除规则。sitemap 仍为 88 个正式 URL，20 项评分口径未改。</li>
</ul></div>

<h2>五、仍需你操作 / 业务决策</h2>
<div class="note"><ul>
<li><b>H1（阻断）</b>：注册商配置 A/AAAA 或 CNAME → 源站开放 443 与完整证书链 → 部署 <code>tools/deploy/nginx-maibida.conf.example</code> 与 Node 服务 → 在 http{{}} 加 <code>limit_req_zone</code> → 运行 <code>sh tools/deploy/check-production.sh</code> → 六个目标市场节点实测。</li>
<li><b>M2</b>：提供真实 ICP 备案号后补回页脚备案标注；无备案且主机在海外则保持移除。</li>
<li><b>M6</b>：是否启用独立 es-ES 版本属业务决策。当前单一拉美西语版已在菜单明确标注；如需西班牙专用 URL，运行 <code>python tools/add-es-ES-variant.py --apply</code> 并按脚本输出的 5 步同步 sitemap 与评分口径，且需母语者重译。</li>
<li><b>O4</b>：人工确认 +86 159 9567 5085 已注册 WhatsApp Business 且可接收海外消息。</li>
<li><b>O8 / 术语</b>：GA4 上线后按需部署（须同步 Cookie 同意）；「模具监视保护器 / 智能相机」为产品正式名与 URL 语义，牵动 11 语种译文与鱼骨图卡片宽度，未擅自替换。</li>
</ul></div>

<h2>六、上线自检小结</h2>
<div class="note" style="border-left-color:#d99200;background:#fffaf0"><p style="margin:0">{verdict}</p></div>

<h2>七、交付与回滚</h2>
<div class="note"><ul>
<li>新增页面：22 个政策/条款页 + 11 个重生成留言页；共用样式 <code>cn/css/policy.css</code>、<code>cn/css/contact.css</code>。</li>
<li>生成器（均幂等）：<code>build-policy-pages.py</code>、<code>apply-compliance-fixes.py</code>、<code>fix-watermark-asset.py</code>、<code>add-message-feature.py</code>、<code>compliance_i18n.py</code>（11 语种单一数据源）。</li>
<li>验证与配置：<code>verify-compliance-remediation.py</code>、<code>verify-message-feature.py</code>、<code>deploy/check-production.sh</code>、<code>purge-expired-messages.js</code>、<code>add-es-ES-variant.py</code>。</li>
<li>回滚快照：<code>{esc(Path('D:/20260919GPT/maibida-ocr-rebuilt_compliance_backup_20261107_103336').name)}</code>（整改前全量，581 文件 / 377,298,395 字节）、<code>{esc(Path(CP['backup']).name)}</code>（88 页）、<code>{esc(Path(PG['backup']).name)}</code>（政策页）、<code>{esc(WM_DIR)}</code>（水印原图）。</li>
</ul></div>

<p class="foot">本次为整改执行，站点 88 个正式页、77 个参数页、11 个首页与 11 个留言页均已实际修改；sitemap.xml 未改。
Google 抓取评分为自建工程指标，非 Google / Lighthouse 官方分数。图片二进制内嵌中文、纯静态托管下接口可用性、线上域名可达性三项不是本地部署包能解决的边界。</p>
</div></body></html>"""

out = TOOLS / "compliance-remediation-report.html"
out.write_text(doc, encoding="utf-8")
print("report:", out, out.stat().st_size, "bytes")
print("verification:", V["passed"], "/", V["total"], "| score:", SC["score"],
      "| errors:", levels.get("error", 0), "| warnings:", levels.get("warning", 0))
