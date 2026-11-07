#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把站点内部 .html 页面链接从（被翻译脚本改坏的）根绝对路径
修复为正确的【相对路径】。
- 去叠：X 路径在磁盘不存在时，去掉首段直到存在（处理 /product/product/... 这类叠层）
- 转相对：基于当前文件所在目录，计算到目标文件的相对路径
- 只处理 href/src 中以 "/" 开头、指向内部 .html 的链接；不动外链(https)、不动资源(已是相对)
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

link_re = re.compile(r'(href|src)="(/[^"]*\.html(?:\#[^"]*)?)"')

def demangle(abs_path):
    """abs_path 不带前导 '/'，例如 'product/product/10032.html'。
    反复去掉首段直到对应文件存在，返回修正后的(不带前导'/')路径。"""
    parts = [p for p in abs_path.split('/') if p]
    while parts:
        cand = os.path.join(ROOT, *parts)
        if os.path.isfile(cand):
            return '/'.join(parts)
        # 末段不是 .html 也尝试（理论上都是 .html）
        if len(parts) == 1:
            break
        parts = parts[1:]
    return None  # 无法修复

def to_relative(target_abs, from_dir):
    """target_abs: 修正后的根绝对(不带前导'/')，如 'product/10032.html'
       from_dir:   当前文件目录(相对 ROOT)，如 'product' 或 ''（根）
       返回相对路径。"""
    tgt = target_abs.split('#')[0]
    rel = os.path.relpath(tgt, from_dir if from_dir else '.')
    # os.path 在 win 用反斜杠，统一为正斜杠
    rel = rel.replace('\\', '/')
    if rel == '.':
        rel = './'
    return rel

def fix_file(path):
    rel_dir = os.path.dirname(os.path.relpath(path, ROOT))
    with open(path, encoding='utf-8') as f:
        html = f.read()
    changed = []
    def repl(m):
        attr, val = m.group(1), m.group(2)
        raw = val[1:]  # 去掉前导 '/'
        frag = ''
        if '#' in raw:
            raw, frag = raw.split('#', 1)
            frag = '#' + frag
        fixed = demangle(raw)
        if fixed is None:
            return m.group(0)  # 修不了，保持原样
        new_abs = fixed  # 已是根绝对(不带'/')
        new_rel = to_relative(new_abs, rel_dir) + frag
        changed.append((val, new_rel))
        return '%s="%s"' % (attr, new_rel)
    new_html, n = link_re.subn(repl, html)
    if n:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_html)
    return n, changed

def main():
    count = 0
    total = 0
    for dirpath, _, files in os.walk(ROOT):
        # 跳过备份目录 / en 目录 / 隐藏目录
        if '/en/' in dirpath or '\\en\\' in dirpath:
            continue
        if any(seg.startswith('micromat-site.bak') for seg in dirpath.split(os.sep)):
            continue
        if dirpath.startswith('.'):
            continue
        for fn in files:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dirpath, fn)
            n, changed = fix_file(p)
            if n:
                count += 1
                total += n
                # print sample
                for old, new in changed[:3]:
                    print('  %s -> %s' % (old, new))
    print('fixed files:', count, 'links:', total)

if __name__ == '__main__':
    main()
