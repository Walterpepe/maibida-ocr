# -*- coding: utf-8 -*-
"""Build the structured prelaunch compliance audit (JSON + visual HTML report)."""
from __future__ import annotations
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "tools/compliance-audit.json"
OUT_HTML = ROOT / "tools/compliance-audit-report.html"

BASIS = {
    "site": "www.maibida.com",
    "targets": "墨西哥、西班牙、新加坡、越南、泰国、韩国（海外采购商 / B2B 工业设备）",
    "online": "DNS 查询 Non-existent domain；HTTP / HTTPS 均 502 Bad Gateway；robots.txt / sitemap.xml 线上不可取",
    "package": "D:/20260919GPT/maibida-ocr-rebuilt（106 个可部署 HTML：88 正式页 + 11 留言页 + 4 迁移页 + 3 工具页）",
    "method": "被动式只读核查：静态全量扫描 106 页 + 本地 8899 服务 Edge 运行时抽查 27 页（1440×900 / 390×844）；未修改任何站点页面；未执行攻击性渗透测试",
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

HIGH = [
    {
        "id": "H1", "module": "功能 / SEO / 全局",
        "title": "生产域名不可达，全站无法访问",
        "location": "www.maibida.com（DNS A/AAAA、HTTP/HTTPS 80/443、https://www.maibida.com/robots.txt、/sitemap.xml）",
        "risk": "nslookup 返回 Non-existent domain，HTTP 与 HTTPS 实测均为 502 Bad Gateway，线上 robots.txt / sitemap.xml 取不到。六个目标市场的采购商与 Googlebot 当前完全无法打开网站；所有 SEO、合规与内容整改在域名恢复前都不产生上线效果，上线即等于业务中断。",
        "fix": "① 在域名注册商配置 A/AAAA 或 CNAME 指向源站或 CDN，确认 TTL 与解析全球生效；② 源站开放 443、部署有效证书链（含中间证书），HTTP 统一 301 到 HTTPS；③ 用 Googlebot UA 与墨西哥/西班牙/新加坡/越南/泰国/韩国节点实测 curl -I、TLS 握手与首字节时间；④ 解析生效后在 Google Search Console 提交 https://www.maibida.com/sitemap.xml 并请求编制索引。",
    },
    {
        "id": "H2", "module": "合规 - 隐私",
        "title": "缺少隐私政策页面与主动同意机制（六个目标市场普遍违法）",
        "location": "全站 106 页无 privacy / privacidad / 隐私政策 / Aviso de Privacidad / Terms 页面；11 个 contact*.html 表单采集姓名、邮箱、电话、公司、国家/地区、留言内容；表单仅有一句 cf-privacy「提交即表示同意…」，checkboxes=0（默示同意）",
        "risk": "墨西哥 LFPDPPP 要求 Aviso de Privacidad（控制者身份、目的、数据类型、转移、ARCO 权利、撤回同意方式）；西班牙 GDPR + LOPDGDD + ePrivacy 要求 Art.13 告知与 Cookie 同意；新加坡 PDPA 要求目的告知与 DPO 渠道；越南 Decree 13/2023 对跨境传输有评估要求；泰国 PDPA 要求 Privacy Notice；韩国 PIPA 要求必需项/可选项同意分离、跨境传输单独告知。「提交即同意」属默示同意，不被认可且无法举证。收集海外客户 PII 而无政策页，可能面临监管处罚、询盘数据不可用及广告/搜索平台信任降级。",
        "fix": "① 新建 11 语种 Privacy Policy 页（至少覆盖 zh-CN / en / es-MX / vi / th / ko），内容包括：数据控制者名称与联系方式、采集字段与用途（仅回复本次询盘）、法律依据、保存期限（建议 24 个月）、不向第三方出售、数据存储地为中国境内及跨境传输说明、访问/更正/删除/撤回同意的行使渠道、Cookie 与日志说明、生效日期与版本；② 全站页脚加入可访问链接（含 11 个首页，见 M1）；③ 表单加未预勾选的同意 checkbox + 政策页链接，未勾选禁止提交；④ 服务端记录 consent=true、时间戳、政策版本、来源语种；⑤ messages.ndjson 限权/加密并设置到期自动清理与删除流程。",
    },
    {
        "id": "H3", "module": "功能 - 询盘",
        "title": "留言接口依赖本地 Node 服务，纯静态上线即失效",
        "location": "11 个 contact*.html → POST /api/messages；实现位于 tools/preview-server.js；数据写入站点外 D:/20260919GPT/maibida-ocr-rebuilt_messages/messages.ndjson",
        "risk": "本地 8899 服务实测提交成功并返回「提交成功，我们会尽快与您联系。」，但该接收端只在本地 Node 进程运行时存在。部署到纯静态托管 / CDN / 对象存储后 /api/messages 返回 404，全部询盘静默丢失，前端仅作简单提示、无明确失败反馈。询盘是 B2B 站唯一转化链路，此缺陷等同业务功能不可用。",
        "fix": "① 上线必须随站部署 Node 服务（或 Serverless / 云函数 / 表单服务），由域名反向代理 /api/messages 并走 HTTPS；② 配置请求体大小限制、字段白名单、同源校验、限流与 honeypot/CAPTCHA；③ 前端补失败重试、明确错误文案与备用邮箱/WhatsApp 提示；④ 上线后从六个目标市场各提交一次真实询盘并确认后台收到；⑤ 若改用云表单服务，需按其数据处理协议同步更新 H2 的隐私政策。",
    },
    {
        "id": "H4", "module": "合规 - 宣传用语",
        "title": "「100% 全检零遗漏」无依据的绝对化性能承诺（11 语种全命中）",
        "location": "productlist/10034.html 及 .en-US/.en-SG/.es-MX/.id-ID/.th-TH/.vi-VN/.ko-KR/.ja-JP/.ms-MY/.ru-RU.html 共 11 页「高精度全检」段落；对应译文如 100% inspection with no missed parts / inspección del 100% sin omisiones / 見逃しのない100%全数検査 / 검출 누락 없는 100% 전수 검사 / 100% сплошного контроля без пропусков",
        "risk": "工业视觉检测检出率必然受工件表面、光照、治具定位、来料波动与参数设定影响，「零遗漏」不可能无条件成立。该表述在中国广告法、欧盟 UCPD 误导性商业行为、墨西哥 LFPC、韩国标示广告法等框架下均可能被认定为无依据的性能保证；一旦验收达不到，直接引发虚假宣传投诉与合同索赔，且 11 个语种同步扩散风险。",
        "fix": "① 全 11 语种统一改为条件化表述，例如「支持对产线全数在线检测；实际检出率与节拍取决于工件表面、光照、治具定位及参数设定，以双方签署的技术协议 / 验收标准为准」；② 禁止任何语种残留 100%、零遗漏、no missed parts、sin omisiones、без пропусков 等绝对词；③ 与 H6 免责条款合并落地，由母语审校确认语气不构成保证；④ 建立宣传用语禁用词表并纳入发版前自动扫描。",
    },
    {
        "id": "H5", "module": "合规 - 知识产权 / 图片真实性",
        "title": "产品页使用带「百度AI生成」第三方中文水印的 AI 生成图",
        "location": "UserFiles/upload/image/20251230/6390268955757181277238280.jpg（alt=\"led\"）；被 productlist/10036.html 及 10 个语种变体共 11 页引用；ocr-inventory.json 与 _ocr_result.json 记录图内文字「百度AI生成」；页面已有 sr-only 转录「图内文字：AI 生成图片水印」",
        "risk": "① 图内嵌第三方平台中文水印用于商业展示，存在平台使用条款与商标/标识使用争议，且无法证明图片授权与版权归属；② 该图位于产品应用展示区，AI 生成图易被海外采购商理解为实物或真实检测效果，构成图片与实物不符的误导；③ 中文水印出现在英/西/泰/越/韩页面，损害 B2B 工厂站专业度。",
        "fix": "① 以自有实拍图替换，或彻底去水印并在图片可见说明与 alt 中标注「示意图 / Schematic illustration, not an actual product photo」；② 建立图片来源台账（拍摄日期、授权、版权归属、是否 AI 生成）；③ 用 OCR 对全站产品图复检第三方水印与其他品牌 logo；④ 下线或替换所有 11 个语种页的该引用并复测图片加载。",
    },
    {
        "id": "H6", "module": "合规 - 免责条款",
        "title": "产品说明与技术参数页全站缺少免责 / 适用性声明",
        "location": "product/10032.html、product/smart-camera.html、productlist/10029|10030|10034|10036|10039.html 及 80 个外语变体；4 个抽样页正文检索「免责 / 仅供参考 / 以实物为准 / subject to change / disclaimer / warranty」命中 0",
        "risk": "页面明确列出 ±0.02 mm、0.0007 mm、4500 PCS/H、60 个/分、8 MP 等精度与节拍参数，却无「参数随工件与工况变化」「仅供选型参考，以技术协议与最终报价为准」「规格变更不另行通知」「网页内容不构成性能保证」等声明。B2B 设备合同金额高，采购商可直接援引网页参数主张违约，售后纠纷与索赔风险显著。",
        "fix": "① 在所有参数表下方加统一 Disclaimer 区块并做 11 语种本地化；② 同步新建 Terms of Sale / Warranty 页面并从页脚链接；③ 把 H4 的条件化表述纳入同一免责体系；④ 报价单、技术协议与合同中引用该网页免责声明，形成证据链；⑤ 记录参数版本与更新日期，避免历史页面与最新规格冲突。",
    },
]

MEDIUM = [
    {
        "id": "M1", "module": "合规 - 版权 / 内容一致",
        "title": "11 个首页无页脚：缺版权声明、公司名、地址、电话、邮箱",
        "location": "index.html 及 .en-US/.en-SG/.es-MX/.id-ID/.th-TH/.vi-VN/.ko-KR/.ja-JP/.ms-MY/.ru-RU.html；实测版权声明覆盖 77/88 正式页，缺失的 11 页全部为首页；首页正文尾部仅有返回顶部按钮与脚本",
        "risk": "首页是海外采购商第一落点，无版权与主体信息会削弱公司主体可识别性与可信度，也不利于 GDPR / LFPDPPP 对数据控制者身份的公示要求；与其他 77 页页脚不一致。",
        "fix": "为 11 个首页补统一页脚区块（公司法定名称、© 年份、地址、电话、邮箱、隐私政策链接），复用现有 77 页页脚模板，保持字号与版式一致。",
    },
    {
        "id": "M2", "module": "合规 - 版权标注",
        "title": "ICP 备案标注残缺，外文页为占位译文",
        "location": "product/10032.html 页脚「© 2026 昆山迈必达智能设备有限公司 All Rights Reserved. 苏ICP备 中国」；10 个外语页译为 Jiangsu ICP Registration / Registro ICP de Jiangsu / 江蘇省ICP登録 等，均无备案编号与工信链接",
        "risk": "「苏ICP备」后缺具体备案号属标注不规范；若服务器位于中国大陆，可能不符合备案公示要求；面向海外客户展示无编号的占位文本亦不专业。",
        "fix": "补齐真实备案号并链接 https://beian.miit.gov.cn，外文页统一译为「ICP Filing No. 苏ICP备XXXXXXXX号, China」；若无备案且主机在海外，则整行移除，不要保留残缺占位符。© 年份建议改为动态或定期更新。",
    },
    {
        "id": "M3", "module": "功能 - 联系方式",
        "title": "电话与邮箱为纯文本，无 tel: / mailto: 链接",
        "location": "88 个正式页页脚的 15995675085 与 mai_bida@163.com；运行时抽查 27 页 telLinks=0、mailtoLinks=0；仅 WhatsApp 为 88 页一致的 https://wa.me/8615995675085 链接",
        "risk": "移动端采购商无法一键拨号/发邮件，海外客户更依赖 WhatsApp 与邮件，纯文本显著降低询盘转化；也不满足「电话链接点击跳转正常」的上线检查项。",
        "fix": "将电话包为 <a href=\"tel:+8615995675085\">，邮箱包为 <a href=\"mailto:mai_bida@163.com\">（11 语种同步），并加 aria-label 与点击埋点；确认国际格式 +86 前缀。",
    },
    {
        "id": "M4", "module": "合规 - 商标",
        "title": "技术参数表使用第三方商标「Sony」描述 sensor 品牌",
        "location": "product/10032.html「sensor品牌 → Sony」及 10 个外语变体（Sensor Brand / Marca del sensor / Марка sensor 等）共 11 页",
        "risk": "指示性使用第三方商标说明元器件来源通常允许，但需有真实供货凭证；否则易被理解为 Sony 原厂合作或背书，在部分市场构成商标性使用争议。",
        "fix": "保留可核实的技术描述但加注「第三方传感器，非 SONY 品牌整机或与 SONY 存在授权合作关系」；或改为不出现品牌、只写「CMOS 图像传感器 / 8 MP」；留存采购凭证备查。",
    },
    {
        "id": "M5", "module": "合规 - 宣传用语",
        "title": "「保证产品交期」等承诺性描述",
        "location": "product/10032.html「防止模具损坏…保证产品交期…」；product/10032.es-MX.html 译为「garantiza los plazos de entrega del producto」等对应译文",
        "risk": "交期受订单、产能、物流与清关影响，网页无条件保证交期属无依据承诺，可能成为延期交付时的争议依据。",
        "fix": "改为「有助于减少模具损坏导致的停线风险，帮助稳定生产计划」，交期一律以合同/订单确认为准；11 语种同步复核 garantiza / guarantee 类措辞。",
    },
    {
        "id": "M6", "module": "SEO / 内容本地化",
        "title": "目标市场含西班牙，但无 es-ES 版本",
        "location": "hreflang 12 项（zh-CN + 10 语种 + x-default）不含 es-ES；sitemap 88 URL 不含 es-ES；旧 product/smart-camera.es-ES.html 为 noindex 跳转页；全站西语仅 es-MX 拉美版",
        "risk": "西班牙采购商会看到拉美西语用词与格式，本地化贴合度不足；es-ES 历史外链只落到跳转页，无法沉淀西班牙市场的自然搜索流量。",
        "fix": "按现有 10 语种生成流程补 es-ES 变体（欧洲西语用词、日期/小数格式、€ 报价语境），补 hreflang 与 sitemap；或明确对外说明统一使用拉美西语并在语言菜单标注。",
    },
    {
        "id": "M7", "module": "内容 - 翻译专业度",
        "title": "技术表头混用未译英文词 sensor",
        "location": "product/10032 系列多语种页：「Марка sensor」「sensor 브랜드」「ยี่ห้อ sensor」「Thương hiệu sensor」「sensorブランド」「Merek sensor」等；另 smart-camera 系列 15–19 处（其中西语/印尼语/马来语 sensor 为本地正确词，不计入）",
        "risk": "俄、韩、泰、越、日页表头出现未译英文词，属机翻/术语表未覆盖的痕迹，削弱 B2B 技术文档专业度。",
        "fix": "统一术语表：ru Марка сенсора / ko 센서 브랜드 / th ยี่ห้อเซ็นเซอร์ / vi Thương hiệu cảm biến / ja センサーメーカー；批量替换后跑中文残留与未译词扫描。",
    },
    {
        "id": "M8", "module": "SEO - 性能",
        "title": "WebP 已生成但生产端内容协商尚未部署",
        "location": "26 张 .png.webp / .jpg.webp 副本已生成，最大原图 1.1 MB（UserFiles/upload/image/20251212/6390113110640403958074666.png）；Accept 协商目前仅实现于 tools/preview-server.js，生产配置仅在 tools/deploy/nginx-maibida.conf.example 中提供样例",
        "risk": "若直接把部署包丢到普通静态托管而不配置 Accept/Vary 协商，浏览器仍加载原始 PNG/JPG，海外移动端首屏与 LCP 明显变慢，影响 Core Web Vitals 与跳出率。",
        "fix": "上线时启用提供的 Nginx 内容协商片段（Accept: image/webp、Vary: Accept、静态资源 Cache-Control），或用 CDN 自动 WebP/AVIF 转换；上线后用 WebPageTest / Lighthouse 在目标市场节点复测 LCP。",
    },
    {
        "id": "M9", "module": "功能 / 安全 - 上线配置",
        "title": "生产侧安全头与接口防护仍停留在本地实现",
        "location": "本地 8899 实测已输出 HSTS、CSP、X-Frame-Options、X-Content-Type-Options、Referrer-Policy、Permissions-Policy、COOP、CORP；但生产 Nginx 配置尚未部署；POST /api/messages 无验证码、无限流、无 honeypot；PII 以明文 NDJSON 存放，未定义保留期限与删除机制",
        "risk": "上线后若沿用默认静态托管配置，安全头全部缺失，且留言接口可被批量刷单/注入垃圾数据；明文 PII 无生命周期管理，与 H2 的隐私承诺冲突。",
        "fix": "部署 tools/deploy/nginx-security-headers.conf（含 HSTS preload、CSP、TLS 1.2+、HTTP→HTTPS 301）；接口加限流、同源校验、honeypot 与日志告警；NDJSON 目录限权、加密或迁移到受控数据库，并实现到期自动清理与删除工单。",
    },
]

LOW = [
    {"id": "O1", "module": "合规 - 多语言", "title": "日文页「最高速度 / 最高10个/秒」建议改「最大…」", "location": "productlist/10029|10030|10034|10039.ja-JP.html", "detail": "语义为技术上限（maximum），非广告绝对化用语；但日本景品表示法对「最高」敏感，建议统一改为「最大速度」「最大10個/秒」以彻底规避争议。"},
    {"id": "O2", "module": "SEO - 标签", "title": "两个英文留言页 title 重复", "location": "contact.en-SG.html 与 contact.en-US.html 均为「Leave a Message | Maibida」", "detail": "两页均 noindex 且不进 sitemap，对收录无实质影响；建议改为含地域标识的标题（如 ... | MAIBIDA Singapore / Global）。"},
    {"id": "O3", "module": "内容 - 本地化", "title": "25 张图二进制内嵌中文 UI 字形", "location": "设备实拍、软件 UI 截图、铭牌等共用图片", "detail": "已通过 11 语种 sr-only 转录让 Googlebot 可读文字；但海外客户视觉上仍看到中文界面。建议逐步替换为多语种 UI 截图或在图注标明语言版本。"},
    {"id": "O4", "module": "功能 - 联系", "title": "WhatsApp 号码需人工验证有效性", "location": "https://wa.me/8615995675085（88 页一致，格式正确）", "detail": "自动检测只能验证 URL 格式；需确认该号已注册 WhatsApp Business、可接收海外消息并有值班响应，否则链接会打开空会话。"},
    {"id": "O5", "module": "SEO - 结构化", "title": "首页缺面包屑与 BreadcrumbList", "location": "index.html 及 10 个首页变体（产品页已有 breadcrumb 标记）", "detail": "建议在产品/分类页补可见面包屑 + BreadcrumbList JSON-LD，改善 Google 结果展示与站内导航。"},
    {"id": "O6", "module": "内容 - 一致性", "title": "首页未展示公司法定名称与地址", "location": "11 个首页（详见 M1）", "detail": "建议与 77 个内页页脚保持同一套公司名、地址、电话、邮箱，避免询盘时主体信息不一致。"},
    {"id": "O7", "module": "合规 - 品牌", "title": "WhatsApp 图标使用需遵循 Meta 品牌指南", "location": "88 页文字/字符型入口，站点内未发现官方 logo 图片资产", "detail": "当前为文字提及（指示性使用），无侵权风险；若后续换成官方绿色气泡 logo，需按 Meta Brand Guidelines 使用并避免暗示合作关系。"},
    {"id": "O8", "module": "SEO - 数据", "title": "未部署统计与搜索控制台", "location": "88 个正式页未发现 GA4 / GTM / 百度统计 / Meta Pixel 等第三方脚本", "detail": "建议上线后部署 GA4 + Google Search Console 并配合 H2 的 Cookie 同意机制；用于跟踪六个目标市场的抓取、收录与询盘转化。"},
]

PASSED = [
    ("合规", "极限词 / 夸大功效", "精确词边界扫描 88 正式页：中文绝对化用语 0、英西等绝对化用语 0；命中的「最高800万像素」「标准款最高速度」为技术上限参数，非广告绝对化；唯一确凿违规见 H4。"),
    ("合规", "敏感违规内容", "军用/武器/管制/违禁/赌博/色情/走私 与 ITAR/military grade/counterfeit 等精确检索 0 命中；子串命中「itar」（西语 evitar 等）已排除为误报。"),
    ("合规", "多语言歧视 / 冒犯词", "精确检索 0 命中；「Backward Compatible」（向下兼容）、西语「inferior」（下模位）为技术词误报。"),
    ("合规", "第三方 logo / 图片文件名", "全站图片文件名未发现第三方品牌标识；无 WhatsApp 官方 logo 资产；文本中第三方品牌仅 Sony（M4）与 WhatsApp 指示性使用。"),
    ("功能", "页面可打开 / 空白 / 乱码", "静态 106 页均非空且含完整 title；运行时 27 页 HTTP 全 200、无 U+FFFD 乱码；contact 页正文约 99 字符属短表单页，非空白页。"),
    ("功能", "图片与图标加载", "运行时 27 页破图 0；静态本地引用 0 死链。"),
    ("功能", "链接 / 404 / 循环跳转", "106 页 7555 条引用中本地死链 0；4 个 en-AU/es-ES 迁移页为 noindex + canonical + 一次性跳转，无循环重定向。"),
    ("功能", "询盘表单提交", "本地 8899 实测填写 6 字段并提交成功，返回「提交成功，我们会尽快与您联系。」；字段与必填校验正常（生产可用性见 H3）。"),
    ("功能", "WhatsApp 联系链接", "88 个正式页均为 https://wa.me/8615995675085，格式合法、跨页一致（号码有效性见 O4）。"),
    ("功能", "多语言切换", "88 页各 1 个 details.vp-language-switch，运行时 27/27 可展开；html lang 与页面语种一致；hreflang 12 项互指；无中文残留。"),
    ("功能", "移动端适配", "1440×900 与 390×844 双视口抽查 27 页，横向溢出 0、JS 报错 0；窄屏导航图标化正常。"),
    ("功能", "导航 / 面包屑 / 产品分类", "产品页存在 nav 与 breadcrumb 标记，分类链接指向有效页（首页面包屑建议见 O5）。"),
    ("功能", "HTTPS 混合内容", "部署包内 http:// 资源引用 0、http:// 链接 0；本地已输出完整安全响应头（生产部署见 M9）。"),
    ("SEO", "robots.txt", "User-agent: * / Allow: /，9 条路径级 Disallow 均不覆盖 88 个正式页，含 Sitemap 绝对地址；规则语法合法。"),
    ("SEO", "sitemap.xml", "88 个 URL 与 88 个正式页一一对应，hreflang 12 项；无孤立 URL、无遗漏正式页。"),
    ("SEO", "Title / Description / H1", "title 与 description 空值 0；106 页各 1 个 H1；正式页无重复 title/description（重复仅见于 2 个 noindex 留言页，O2）。"),
    ("SEO", "canonical / 图片 alt", "88 正式页 canonical 0 缺失、自指正确；图片 alt 缺失 0（231 处已按 11 语种本地化）。"),
    ("SEO", "noindex 索引障碍", "88 个需收录正式页 noindex 误加 0；noindex 仅用于 11 留言页、3 工具页、4 迁移页。"),
    ("SEO", "页面性能资源", "26 张 WebP 副本 + 原图温和重编码，最大原图 1.1 MB；本地 Accept 协商已生效（生产配置见 M8）。"),
    ("内容", "外文翻译 / 术语", "80 个外语页 0 中文残留；未发现机翻硬伤性错句；未译词问题见 M7。"),
    ("内容", "产品参数一致性", "3840、4500、0.0007、V3 Pro、AtomCV 等关键参数在 11 个语种页均存在且一致；800万 / 8 MP 为合规本地化写法，无前后矛盾。"),
    ("内容", "联系方式一致性", "WhatsApp 88 页一致；邮箱 mai_bida@163.com、电话 15995675085 在 77 个含页脚页面一致；地址 11 语种为同一地址的本地化译文；首页缺失见 M1。"),
    ("内容", "排版整洁", "抽检未发现空段落、重复标点、错乱列表；表格结构与技术参数表对齐正常。"),
]

CONCLUSION = {
    "verdict": "不满足上线条件",
    "blockers": 6,
    "medium": len(MEDIUM),
    "low": len(LOW),
    "text": (
        "当前不具备上线条件。6 项高危中，H1（域名 DNS 未解析 / 502）使网站在六个目标市场与 Googlebot 侧完全不可达；"
        "H2（缺隐私政策与主动同意）、H4（11 语种「零遗漏」绝对化承诺）、H5（带第三方中文水印的 AI 生成图）、"
        "H6（全站无免责条款）构成跨墨西哥、西班牙、新加坡、越南、泰国、韩国的合规法律风险；"
        "H3（留言接口仅本地 Node 可用）会令静态上线后询盘全部丢失。"
        "功能、SEO 与内容三大模块的机械性检查表现良好：106 页静态、27 页运行时抽查均为 0 死链 / 0 破图 / 0 JS 报错 / 0 横向溢出，"
        "robots 与 sitemap 配置正确、title/description/H1/canonical/alt/noindex 全部达标，参数与联系方式跨 11 语种一致。"
        "但机械达标不能替代合规与线上可用性：须先完成 H1–H6 整改并从目标市场实测复验，"
        "建议将 9 项中风险同批处理，8 项优化建议可上线后迭代。"
    ),
}


def esc(s):
    return html.escape(str(s), quote=True)


def card(item):
    return f"""<div class="issue {item['level']}">
  <div class="issue-head"><span class="badge {item['level']}">{esc(item['id'])}</span>
    <span class="module">{esc(item['module'])}</span>
    <h3>{esc(item['title'])}</h3></div>
  <div class="row"><span class="k">问题位置</span><div class="v">{esc(item['location'])}</div></div>
  <div class="row"><span class="k">风险说明</span><div class="v">{esc(item['risk'])}</div></div>
  <div class="row"><span class="k">详细整改方案</span><div class="v">{esc(item['fix'])}</div></div>
</div>"""


def main():
    data = {"basis": BASIS, "high": HIGH, "medium": MEDIUM, "low": LOW,
            "passed": [{"module": m, "item": i, "detail": d} for m, i, d in PASSED],
            "conclusion": CONCLUSION}
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    high_cards = "\n".join(card({**x, "level": "high"}) for x in HIGH)
    med_cards = "\n".join(card({**x, "level": "medium"}) for x in MEDIUM)
    low_rows = "\n".join(
        f"<tr><td class='oid'>{esc(x['id'])}</td><td>{esc(x['module'])}</td>"
        f"<td><b>{esc(x['title'])}</b><div class='loc'>{esc(x['location'])}</div></td>"
        f"<td>{esc(x['detail'])}</td></tr>" for x in LOW)
    pass_rows = "\n".join(
        f"<tr><td class='mod'>{esc(m)}</td><td>{esc(i)}</td><td>{esc(d)}</td></tr>"
        for m, i, d in PASSED)

    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>MAIBIDA 上线前全项预审报告</title>
<style>
:root{{--bg:#f5f7fa;--card:#fff;--ink:#16202c;--muted:#5d6b7a;--line:#dfe5ec;
--red:#c0392b;--redbg:#fdf0ee;--amber:#b26a00;--amberbg:#fff6e6;--blue:#1c6ba8;--bluebg:#eef5fc;--green:#18794e;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.65 "Segoe UI","Microsoft YaHei",system-ui,sans-serif}}
.wrap{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:27px;margin:0 0 8px;letter-spacing:.3px}}
h2{{font-size:19px;margin:38px 0 14px;padding-left:11px;border-left:4px solid var(--blue)}}
h3{{font-size:15px;margin:0;display:inline}}
.sub{{color:var(--muted);font-size:13px;margin:0 0 20px}}
.meta{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 20px;margin-bottom:22px}}
.meta div{{padding:3px 0;color:var(--muted)}}.meta b{{color:var(--ink);display:inline-block;min-width:76px}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0 8px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;text-align:center}}
.card .n{{font-size:30px;font-weight:700;line-height:1.2}}.card .l{{color:var(--muted);font-size:12px;margin-top:5px}}
.n.red{{color:var(--red)}}.n.amber{{color:var(--amber)}}.n.blue{{color:var(--blue)}}.n.green{{color:var(--green)}}
.notice{{background:var(--redbg);border:1px solid #f0c4bd;border-left:5px solid var(--red);border-radius:8px;padding:14px 18px;margin:18px 0}}
.notice b{{color:var(--red)}}
.issue{{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:14px 0;overflow:hidden}}
.issue.high{{border-left:5px solid var(--red)}}.issue.medium{{border-left:5px solid var(--amber)}}
.issue-head{{padding:13px 17px;border-bottom:1px solid var(--line);background:#fbfcfe}}
.badge{{display:inline-block;font-weight:700;font-size:12px;padding:2px 9px;border-radius:5px;margin-right:10px}}
.badge.high{{background:var(--red);color:#fff}}.badge.medium{{background:var(--amber);color:#fff}}
.module{{font-size:11px;color:var(--muted);background:#eef2f6;padding:2px 8px;border-radius:4px;margin-right:10px}}
.row{{display:flex;gap:14px;padding:11px 17px;border-bottom:1px solid #f0f3f7;align-items:flex-start}}
.row:last-child{{border-bottom:0}}
.k{{flex:0 0 92px;color:var(--muted);font-size:12px;font-weight:600;padding-top:2px}}
.v{{flex:1;white-space:pre-wrap;word-break:break-word}}
table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden;font-size:13px}}
th{{background:#eef2f7;text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);font-weight:600}}
td{{padding:10px 12px;border-bottom:1px solid #f0f3f7;vertical-align:top}}
tr:last-child td{{border-bottom:0}}
.oid{{color:var(--blue);font-weight:700;white-space:nowrap}}.loc{{color:var(--muted);font-size:12px;margin-top:4px}}
.mod{{color:var(--green);font-weight:600;white-space:nowrap}}
.concl{{background:var(--card);border:1px solid var(--line);border-top:5px solid var(--red);border-radius:10px;padding:20px 22px}}
.concl .v{{font-size:21px;font-weight:700;color:var(--red);margin-bottom:10px}}
.foot{{color:var(--muted);font-size:12px;margin-top:34px;text-align:center}}
@media(max-width:760px){{.cards{{grid-template-columns:repeat(2,1fr)}}.row{{display:block}}.k{{padding-bottom:4px}}}}
</style></head><body><div class="wrap">
<h1>MAIBIDA B2B 工业设备独立站 · 上线前全项预审报告</h1>
<p class="sub">四大模块逐条核查 ｜ 风险三级分类 ｜ 高危优先 ｜ 生成时间 {esc(BASIS['generated_at'])}</p>
<div class="meta">
<div><b>网站地址</b> {esc(BASIS['site'])}</div>
<div><b>目标市场</b> {esc(BASIS['targets'])}</div>
<div><b>线上实测</b> {esc(BASIS['online'])}</div>
<div><b>审计对象</b> {esc(BASIS['package'])}</div>
<div><b>审计方式</b> {esc(BASIS['method'])}</div>
</div>
<div class="cards">
<div class="card"><div class="n red">{len(HIGH)}</div><div class="l">高危 · 阻断上线</div></div>
<div class="card"><div class="n amber">{len(MEDIUM)}</div><div class="l">中风险 · 建议整改</div></div>
<div class="card"><div class="n blue">{len(LOW)}</div><div class="l">优化建议 · 非强制</div></div>
<div class="card"><div class="n green">{len(PASSED)}</div><div class="l">逐条核查通过项</div></div>
</div>
<div class="notice"><b>审计前提说明：</b>线上域名当前 DNS 解析失败、HTTP/HTTPS 均 502，因此「爬虫抓取、HTTPS 混合内容、Googlebot 可访问性」三项为对本地部署包的预上线核验，线上状态以 H1 为准。本报告为被动式只读审计，未修改任何站点页面，未执行攻击性测试。</div>

<h2>一、【高危｜必须整改，否则不能上线】</h2>
{high_cards}

<h2>二、【中风险｜建议整改，减少纠纷 / 收录问题】</h2>
{med_cards}

<h2>三、【优化建议｜提升体验，非强制】</h2>
<table><thead><tr><th>编号</th><th>模块</th><th>位置与问题</th><th>建议</th></tr></thead><tbody>
{low_rows}
</tbody></table>

<h2>四、逐条核查通过清单（四大模块 23 项）</h2>
<table><thead><tr><th>模块</th><th>检查项</th><th>核查结论</th></tr></thead><tbody>
{pass_rows}
</tbody></table>

<h2>五、上线自检小结</h2>
<div class="concl"><div class="v">结论：{esc(CONCLUSION['verdict'])}</div>
<p>{esc(CONCLUSION['text'])}</p>
<p style="margin:0;color:var(--muted);font-size:12px">阻断项 {CONCLUSION['blockers']} 个 ｜ 中风险 {CONCLUSION['medium']} 条 ｜ 优化建议 {CONCLUSION['low']} 条 ｜ 通过项 {len(PASSED)} 条</p></div>
<p class="foot">报告由 tools/build-compliance-report.py 生成；结构化明细见 tools/compliance-audit.json；原始证据见 tools/compliance-audit-data.json、tools/compliance-evidence.json、tools/compliance-runtime.json。本次审计为只读，站点页面未被修改。</p>
</div></body></html>"""
    OUT_HTML.write_text(html_doc, encoding="utf-8")
    print("JSON:", OUT_JSON)
    print("HTML:", OUT_HTML, "bytes", OUT_HTML.stat().st_size)
    print("HIGH", len(HIGH), "MEDIUM", len(MEDIUM), "LOW", len(LOW), "PASSED", len(PASSED))


if __name__ == "__main__":
    main()
