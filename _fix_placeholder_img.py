# -*- coding: utf-8 -*-
"""把 productlist 里的坏占位图 images/search.png 换成对应产品的真实图。
匹配方式：占位图 alt 的产品名 -> 在各 productInfo 页的图片 alt/文件名中找同一产品 -> 取其主图。"""
import re, glob, os, json, html as htmlmod

# 1) 收集 productInfo 页里出现的 (产品名关键词, 图片路径)
entries = []   # (页面id, 产品名, 图片rel路径)
for f in sorted(glob.glob('productInfo/*.html')):
    pid = os.path.basename(f).replace('.html','')
    t = open(f, encoding='utf-8', errors='ignore').read()
    # 抓 img 标签: alt + src
    for m in re.finditer(r'<img[^>]*?alt="([^"]*)"[^>]*?src="((?:\.\./)?UserFiles/[^"]+)"', t):
        alt = htmlmod.unescape(m.group(1)).strip()
        src = m.group(2)
        if not src.startswith('../'):
            src = '../' + src
        entries.append((pid, alt, src))
    # 也抓 src 在前 alt 在后的
    for m in re.finditer(r'<img[^>]*?src="((?:\.\./)?UserFiles/[^"]+)"[^>]*?alt="([^"]*)"', t):
        alt = htmlmod.unescape(m.group(2)).strip()
        src = m.group(1)
        if not src.startswith('../'):
            src = '../' + src
        entries.append((pid, alt, src))

print('productInfo 中抓到的 (产品名, 图片) 组合:', len(entries))

# 2) 修正 productlist 的占位图
changed = 0
report = []
for f in sorted(glob.glob('productlist/*.html')):
    t = open(f, encoding='utf-8', errors='ignore').read()
    if 'images/search.png' not in t:
        continue
    replaced = 0
    def repl(m):
        global replaced
        tag = m.group(0)
        alt = re.search(r'alt="([^"]*)"', tag)
        alt_txt = htmlmod.unescape(alt.group(1)).strip() if alt else ''
        # 在 entries 中找 alt 完全相同 或 互相包含的
        cand = None
        for pid, ealt, esrc in entries:
            if not ealt: continue
            if alt_txt and (ealt == alt_txt or (alt_txt in ealt) or (ealt in alt_txt)):
                cand = esrc
                break
        if cand:
            replaced_local = True
            newtag = tag.replace('src="images/search.png"', 'src="%s"' % cand)
            globals()['_inc'] = True
            return newtag
        return tag
    # 逐个 img 标签处理
    out = []
    pos = 0
    for m in re.finditer(r'<img[^>]*?src="images/search\.png"[^>]*?>', t):
        tag = m.group(0)
        alt = re.search(r'alt="([^"]*)"', tag)
        alt_txt = htmlmod.unescape(alt.group(1)).strip() if alt else ''
        cand = None
        for pid, ealt, esrc in entries:
            if not ealt: continue
            if alt_txt and (ealt == alt_txt or alt_txt in ealt or ealt in alt_txt):
                cand = esrc; break
        if cand:
            tag2 = tag.replace('src="images/search.png"', 'src="%s"' % cand)
            out.append(t[pos:m.start()]); out.append(tag2); pos = m.end()
            replaced += 1
            report.append((os.path.basename(f), alt_txt, cand))
        else:
            pass
    out.append(t[pos:])
    t2 = ''.join(out)
    if replaced:
        open(f, 'w', encoding='utf-8').write(t2)
        changed += 1

print('修改页数:', changed, ' 替换图片数:', replaced)
for r in report:
    print('   %-24s %-28s -> %s' % r)
