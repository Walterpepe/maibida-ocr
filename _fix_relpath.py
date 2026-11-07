# -*- coding: utf-8 -*-
"""为子目录页的资源引用补上 ../ 前缀。
安全策略：只匹配 (src|href|data-src)=" 后紧跟 cn/ 或 UserFiles/ 的情形，
逐个属性值精确处理，不跨引号、不动其它文本。"""
import re, glob, os, sys

FILES = sorted(glob.glob('productInfo/*.html'))
# 属性名 + 引号 + 紧跟路径前缀（不含前缀后的内容）
ATTR = re.compile(r'((?:src|href|data-src)=")(cn/|UserFiles/)')

total_attr = 0
changed_files = 0
for f in FILES:
    t = open(f, encoding='utf-8', errors='ignore').read()
    n = len(ATTR.findall(t))
    if not n:
        continue
    # 逐个属性值替换（用 re.sub 的 lambda，只改前缀）
    t2 = ATTR.sub(lambda m: m.group(1) + '../' + m.group(2), t)
    open(f, 'w', encoding='utf-8').write(t2)
    total_attr += n
    changed_files += 1
    print(f'  {f}: {n} 处')
print(f'修复文件数={changed_files} 修复属性数={total_attr}')
