#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把导航里 "在线检测设备" 与 "柔性上料振动盘设备" 顺序颠倒的页面改正。
正确顺序: ... 六面光学分拣机 -> 柔性上料振动盘设备 -> 在线检测设备(含子菜单)
实现: 在 <ul class="fr T-nav"> 内，把"柔性上料振动盘设备"的 <li> 移到"在线检测设备"的 <li>(含<div class="secon">...</div>) 之前。
只处理顺序错的页面；保留各自 href 与 class="cur"。
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

# 匹配单个 li（含可能的嵌套 div.secon，div 内没有 </li>，所以非贪婪到第一个 </li> 即可）
LI_RE = re.compile(r'<li><a[^>]*>在线检测设备</a>(?:<div class="secon">.*?</div>)?</li>', re.S)
FLEX_RE = re.compile(r'<li><a[^>]*>柔性上料振动盘设备</a></li>')

def fix(text):
    m_nav = re.search(r'(<ul class="fr T-nav">)(.*?)(</ul>)', text, re.S)
    if not m_nav:
        return text, False
    nav = m_nav.group(2)
    m_on = LI_RE.search(nav)
    m_flex = FLEX_RE.search(nav)
    if not m_on or not m_flex:
        return text, False
    # 顺序已正确（柔性在在线之前）则不动
    if m_flex.start() < m_on.start():
        return text, False
    on_li = m_on.group(0)
    flex_li = m_flex.group(0)
    # 从 nav 移除这两项，再按正确顺序拼回
    nav2 = nav[:m_on.start()] + nav[m_on.end():]
    # flex 位置可能因删除而改变，重新定位
    m_flex2 = FLEX_RE.search(nav2)
    nav2 = nav2[:m_flex2.start()] + nav2[m_flex2.end():]
    # 在"六面光学分拣机"之后插入 flex + on；若找不到则插到导航末尾
    m_six = re.search(r'<li><a[^>]*>六面光学分拣机</a></li>', nav2)
    if m_six:
        insert_at = m_six.end()
        nav3 = nav2[:insert_at] + flex_li + on_li + nav2[insert_at:]
    else:
        nav3 = nav2 + flex_li + on_li
    new_text = text[:m_nav.start(2)] + nav3 + text[m_nav.end(2):]
    return new_text, True

def main():
    changed = 0
    for dp, _, fs in os.walk(ROOT):
        if any(s.startswith('micromat-site.bak') for s in dp.split(os.sep)):
            continue
        for fn in fs:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dp, fn)
            with open(p, encoding='utf-8') as f:
                t = f.read()
            nt, did = fix(t)
            if did:
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(nt)
                changed += 1
    print('fixed nav order in', changed, 'pages')

if __name__ == '__main__':
    main()
