# -*- coding: utf-8 -*-
"""
还原脚本：撤销英文翻译对中文站点的改动
- 清除中文页注入的语言切换按钮 / 样式 / 脚本
- 清理 sitemap.xml 中的 /en/ 网址
- 删除 en/ 英文目录

保留：中文正文（build 未翻译中文页）、设计修复（视频/轮播样式、图片放大）、
      原有 <head> 的 hreflang/canonical（脚本未生成这些，属站点原有）。
内部链接保持根绝对路径（/product/...），避免改回相对路径导致子目录页导航失效。
"""
import re, shutil
from pathlib import Path

ROOT = Path(r"D:\WorkBuddy20260919\2026-10-29-21-31-27\micromat-site")

def strip_lang_stuff(t):
    # 按钮 div（含嵌套 lang-menu）：</ul> 后插入，结束于 </div></div>
    t = re.sub(r'<div class="lang-switch">[\s\S]*?</div>\s*</div>', '', t)
    # 注入的 <style> 语言样式块
    t = re.sub(r'<style>\s*/\* language switch in header \*/[\s\S]*?</style>', '', t)
    # 注入的 <script> 语言脚本块（精确的 IIFE 签名，避免误伤其它内联脚本）
    t = re.sub(r'<script>\s*\(function\(\)\{[\s\S]*?__langSwitchInit[\s\S]*?\}\)\(\);\s*</script>', '', t)
    # 收敛因删除产生的多余空行（>2 连续换行 -> 2）
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t

# 1) 清除中文页的语言切换注入
n_strip = 0
for p in sorted(ROOT.rglob('*.html')):
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith('en/'):
        continue
    t = p.read_text(encoding='utf-8', errors='ignore')
    if 'lang-switch' not in t and 'language switch in header' not in t:
        continue
    t2 = strip_lang_stuff(t)
    if t2 != t:
        p.write_text(t2, encoding='utf-8')
        n_strip += 1
print(f"stripped lang injection from {n_strip} zh pages")

# 2) 清理 sitemap.xml 中的 /en/ 网址块
sm = ROOT / 'sitemap.xml'
if sm.exists():
    s = sm.read_text(encoding='utf-8', errors='ignore')
    s2 = re.sub(r'<url>[\s\S]*?/en/[\s\S]*?</url>', '', s)
    if s2 != s:
        sm.write_text(s2, encoding='utf-8')
        print("sitemap.xml: removed /en/ url blocks")
    else:
        print("sitemap.xml: no /en/ blocks found")

# 3) 删除 en/ 英文目录
en = ROOT / 'en'
if en.exists() and en.is_dir():
    shutil.rmtree(en)
    print("deleted en/ directory")
else:
    print("en/ not found (already removed?)")

print("REVERT DONE")
