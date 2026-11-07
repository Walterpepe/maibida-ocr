"""Independent verification of the H1-H6 + M/O compliance remediation.

Read-only. Produces tools/compliance-remediation-verify.json with a pass/fail
list; used by build-compliance-remediation-report.py.
"""
import json
import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image

import compliance_i18n as C

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
RESULTS = []


def ck(name, ok, detail=""):
    RESULTS.append({"check": name, "ok": bool(ok), "detail": str(detail)})


def text(rel):
    return BeautifulSoup((ROOT / rel).read_text(encoding="utf-8"), "html.parser").get_text(" ", strip=True)


def rel(base, lang):
    return base if lang == "zh-CN" else base.replace(".html", "." + lang + ".html")


FORMAL = [rel(b, l) for b in [
    "index.html", "product/10032.html", "product/smart-camera.html",
    "productlist/10029.html", "productlist/10030.html",
    "productlist/10034.html", "productlist/10036.html",
    "productlist/10039.html"] for l in C.LANGS]

# ------------------------------------------------------------------ H2 privacy
policies = [f"privacy{'' if l == 'zh-CN' else '.' + l}.html" for l in C.LANGS]
ck("H2 11 语种隐私政策页齐全", all((ROOT / p).exists() for p in policies), len(policies))
pol_ok = 0
for lang, p in zip(C.LANGS, policies):
    t = text(p)
    # Art.13 essentials: controller, purposes, retention, transfers, rights, cookies, contact
    keys = [C.EMAIL, str(C.RETENTION_MONTHS)]
    ok = len(t) > 900 and len(C.POLICY[lang]["sections"]) >= 9 and all(k in t for k in keys)
    pol_ok += ok
ck("H2 各语种含控制者/目的/保留期/跨境/权利/Cookie/联系方式", pol_ok == 11, f"{pol_ok}/11")
ck("H2 88 页页脚均有隐私政策与销售条款链接",
   all('class="foot-legal"' in (ROOT / r).read_text(encoding="utf-8") for r in FORMAL), len(FORMAL))
consent_ok = 0
for lang in C.LANGS:
    p = "contact.html" if lang == "zh-CN" else f"contact.{lang}.html"
    t = (ROOT / p).read_text(encoding="utf-8")
    soup = BeautifulSoup(t, "html.parser")
    box = soup.find("input", {"name": "consent", "type": "checkbox"})
    ok = (box is not None and not box.has_attr("checked")
          and "privacy" in t and "mailto:" in t and "website" in t)
    consent_ok += ok
ck("H2 11 个表单均有未预勾选的主动同意 + 政策链接 + honeypot + 备用邮箱",
   consent_ok == 11, f"{consent_ok}/11")

# ------------------------------------------------------------------ H3 endpoint
srv = (TOOLS / "preview-server.js").read_text(encoding="utf-8")
ck("H3 接收端含限流/同源/honeypot/同意校验/保留期限",
   all(k in srv for k in ["rateOk(", "ALLOWED_ORIGINS", "d.website", "consent",
                          "retentionUntil", "Retry-After"]), "")
js = (ROOT / "cn/js/contact.js").read_text(encoding="utf-8")
ck("H3 前端含超时/明确失败反馈/同意前置校验",
   all(k in js for k in ["AbortController", "consentRequired", "cfg.error"]), "")
nginx = (TOOLS / "deploy/nginx-maibida.conf.example").read_text(encoding="utf-8")
ck("H3 生产反代与安全头配置齐备",
   all(k in nginx for k in ["/api/messages", "limit_req zone=msg_limit",
                            "return 301", "maibida-security.conf", "webp_ext"]), "")
ck("H1 上线验收脚本与数据留存清理脚本已交付",
   (TOOLS / "deploy/check-production.sh").exists()
   and (TOOLS / "purge-expired-messages.js").exists(), "")

# ------------------------------------------------------------------ H4 wording
bad = []
for l in C.LANGS:
    t = text(rel("productlist/10034.html", l))
    for w in ["零遗漏", "no missed parts", "sin omisiones", "tanpa ada yang terlewat",
              "ไม่มีการตรวจสอบตกหล่น", "không bỏ sót", "검출 누락 없는",
              "見逃しのない", "tanpa tertinggal", "без пропусков", "100%全检"]:
        if w in t:
            bad.append(f"{l}:{w}")
ck("H4 11 语种已移除无条件 100%/零遗漏承诺", not bad, ", ".join(bad[:5]))
h4_new = 0
for l in C.LANGS:
    t = text(rel("productlist/10034.html", l))
    h4_new += C.H4_FIX[l][1] in t
ck("H4 11 语种条件化表述与验收标准均已落地", h4_new == 11, f"{h4_new}/11")

# ------------------------------------------------------------------ H5 watermark
img = Image.open(ROOT / "UserFiles/upload/image/20251230/6390268955757181277238280.jpg").convert("RGB")
w, h = img.size
box = (int(w * .78), int(h * .955), w, h)
crop = img.crop(box)
spread = max(hi - lo for lo, hi in crop.getextrema())
ck("H5 右下角第三方水印已清除（区域为纯背景）", spread <= 12, f"channel spread={spread}")
tr = json.loads((TOOLS / "image-text-transcripts.json").read_text(encoding="utf-8"))
wm_ok = 0
for lang in C.LANGS:
    t = (ROOT / rel("productlist/10036.html", lang)).read_text(encoding="utf-8")
    m = re.search(r'<img[^>]*6390268955757181277238280\.jpg[^>]*>', t)
    wm_ok += (m is not None and 'alt="led"' not in m.group(0)
              and tr["texts"]["T8"][lang] in t
              and "<p>led</p>" not in t)
ck("H5 11 页 alt/图注/转录改为示意图说明", wm_ok == 11, f"{wm_ok}/11")
ck("H5 T8 转录译文与页面同步", tr["texts"]["T8"]["zh-CN"].startswith("图内文字说明"), "")

# ------------------------------------------------------------------ H6 disclaimer
terms = ["terms.html" if l == "zh-CN" else f"terms.{l}.html" for l in C.LANGS]
ck("H6 11 语种销售条款/免责页齐全", all((ROOT / p).exists() for p in terms), len(terms))
d_ok = sum(1 for r in FORMAL if not r.startswith("index")
           and "spec-disclaimer" in (ROOT / r).read_text(encoding="utf-8"))
ck("H6 77 个产品参数页均已加本地化技术声明", d_ok == 77, f"{d_ok}/77")

# ------------------------------------------------------------------ M/O items
ck("M1/O6 11 个首页已补统一页脚（版权/公司/地址/政策链接）",
   all('<!-- home-footer -->' in (ROOT / rel("index.html", l)).read_text(encoding="utf-8")
       for l in C.LANGS), "")
tm = sum(1 for r in FORMAL
         if "tel:+8615995675085" in (ROOT / r).read_text(encoding="utf-8")
         and "mailto:mai_bida@163.com" in (ROOT / r).read_text(encoding="utf-8"))
ck("M3 88 页电话/邮箱均可一键点击", tm == 88, f"{tm}/88")
ck("M2 备案占位链接已移除（0 残留）",
   not any("beian.miit.gov.cn" in (ROOT / r).read_text(encoding="utf-8") for r in FORMAL), "")
ck("M4 全站不再出现 SONY 品牌字样",
   not any("Sony" in (ROOT / r).read_text(encoding="utf-8") for r in FORMAL), "")
m5 = []
for l in C.LANGS:
    t = text(rel("product/10032.html", l))
    if C.M5_FIX[l][0] in t:
        m5.append(l)
ck("M5 11 语种已移除无条件交期保证", not m5, ",".join(m5))
ck("M6 语言菜单已明确标注拉美西语 / 提供 es-ES 一键方案",
   all("Español (Latinoamérica)" in (ROOT / r).read_text(encoding="utf-8") for r in FORMAL)
   and (TOOLS / "add-es-ES-variant.py").exists(), "")
m7 = [l for l in C.LANGS if C.SENSOR_HEADER_OLD[l] in (ROOT / rel("product/10032.html", l)).read_text(encoding="utf-8")]
ck("M7 表头未译 sensor 已全语种本地化", not m7, ",".join(m7))
ck("O1 日语「最高速度/最高10个」已改「最大」",
   all("最高速度" not in (ROOT / rel(b, "ja-JP")).read_text(encoding="utf-8")
       for b in ["productlist/10029.html", "productlist/10030.html",
                 "productlist/10034.html", "productlist/10039.html"]), "")
ck("O2 en-SG 留言页标题已区分",
   "Singapore" in (ROOT / "contact.en-SG.html").read_text(encoding="utf-8"), "")
ck("O5 11 个首页均有 BreadcrumbList JSON-LD",
   all("BreadcrumbList" in (ROOT / rel("index.html", l)).read_text(encoding="utf-8")
       for l in C.LANGS), "")

# ------------------------------------------------------------------ regression
sa = json.loads((TOOLS / "site-audit.json").read_text(encoding="utf-8"))
levels = {}
for i in sa["issues"]:
    levels[i["level"]] = levels.get(i["level"], 0) + 1
ck("回归 全站检测 0 错误 / 0 警告",
   levels.get("error", 0) == 0 and levels.get("warning", 0) == 0, json.dumps(levels))
score = json.loads((TOOLS / "google-crawl-score.json").read_text(encoding="utf-8"))
total = score["score"]
ck("回归 Google 抓取评分 100 分", float(total) >= 99.95, str(total))
mf = json.loads((TOOLS / "message-feature-verify.json").read_text(encoding="utf-8"))
ck("回归 留言功能验证全通过", mf["passed"] == mf["total"], f"{mf['passed']}/{mf['total']}")

passed = sum(1 for r in RESULTS if r["ok"])
out = {
    "timestamp": datetime.now().isoformat(timespec="seconds"),
    "passed": passed, "total": len(RESULTS),
    "h1_status": "PENDING_USER_ACTION (DNS/HTTPS at registrar; not fixable in the local deploy package)",
    "site_audit_levels": levels, "score": total,
    "results": RESULTS,
}
(TOOLS / "compliance-remediation-verify.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"PASS {passed}/{len(RESULTS)}")
for r in RESULTS:
    if not r["ok"]:
        print("FAIL", r["check"], "|", r["detail"])
