#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给导航里缺少"视觉传感器"的页面补上该菜单项。
插入位置: "模具监视保护器" 项之后、"六面光学分拣机" 之前。
路径前缀按文件所在目录层级:
  - product/     -> smart-camera.html
  - productInfo/ -> ../product/smart-camera.html
  - productlist/ -> ../product/smart-camera.html
只处理含顶部导航(class="fr T-nav")、且当前没有 smart-camera 链接的页面。
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

def rel_prefix(path):
    d = os.path.dirname(os.path.relpath(path, ROOT))
    if d == 'product':
        return 'smart-camera.html'
    return '../product/smart-camera.html'

def process(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if 'class="fr T-nav"' not in html:
        return False, 'no-nav'
    if 'smart-camera' in html:
        return False, 'already-has'
    href = rel_prefix(path)
    new_li = '<li><a href="%s">视觉传感器</a></li>' % href
    # 在"模具监视保护器"的 </li> 之后插入
    m = re.search(r'(<li><a[^>]*>模具监视保护器</a></li>)', html)
    if not m:
        return False, 'no-anchor'
    html = html[:m.end()] + new_li + html[m.end():]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return True, 'added'

def main():
    added = 0; skipped = 0
    for dirpath, _, files in os.walk(ROOT):
        if any(seg.startswith('micromat-site.bak') for seg in dirpath.split(os.sep)):
            continue
        for fn in files:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dirpath, fn)
            ok, why = process(p)
            if ok:
                added += 1
            else:
                skipped += 1
    print('added vision-nav to', added, 'pages; skipped', skipped)

if __name__ == '__main__':
    main()
