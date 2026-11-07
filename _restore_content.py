#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把旧快照(bak-before-domain)里带内容的 productInfo 详情页恢复到现站，并做品牌替换。
- 复制旧页正文(整个文件)
- 品牌替换: 迈兴（厦门）电子有限公司->昆山迈必达智能设备有限公司 ; micromat.com.cn / www.micromat.com.cn -> www.maibida.com
  电话/邮箱/ICP 保留(与现站一致)
- 资源路径: 把根绝对的 /cn/ /UserFiles/ 改成 ../cn/ ../UserFiles/ (详情页在 productInfo/ 子目录)
- 旧页面包屑里的 ../product/ ../productlist/ 相对链接保留(现站同结构)
用法: python _restore_content.py            # 全部 75 页
      python _restore_content.py 10200      # 只处理指定 id(测试)
"""
import os, re, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE  # micromat-site
OLD = os.path.dirname(ROOT)  # 上级
SNAP = os.path.join(OLD, 'micromat-site.bak-before-domain')
# (源子目录, 目标子目录) —— productInfo 详情页 + productlist 列表页 + product 主页
PAIRS = [
    ('productInfo', 'productInfo'),
    ('productlist', 'productlist'),
    ('product', 'product'),
]

REPL = [
    ('迈兴（厦门）电子有限公司', '昆山迈必达智能设备有限公司'),
    ('迈兴(厦门)电子有限公司', '昆山迈必达智能设备有限公司'),
    ('www.micromat.com.cn', 'www.maibida.com'),   # 先替换带 www 的完整域名
    ('micromat.com.cn', 'maibida.com'),            # 再替换裸域
]

def fix_paths(html):
    # 详情页在 productInfo/ 下，资源在根 cn/、UserFiles/，故根绝对需加 ..
    # 只改资源类根绝对，不动页面链接(页面链接旧页本是 ../ 相对)
    html = re.sub(r'(src|href)="/(cn/[^"]*)"', r'\1="../\2"', html)
    html = re.sub(r'(src|href)="/(UserFiles/[^"]*)"', r'\1="../\2"', html)
    return html

def process(sub, pid):
    src = os.path.join(SNAP, sub, '%s.html' % pid)
    dst = os.path.join(ROOT, sub, '%s.html' % pid)
    if not os.path.isfile(src):
        print('  [skip] no source %s/%s' % (sub, pid)); return False
    with open(src, encoding='utf-8') as f:
        html = f.read()
    for a, b in REPL:
        html = html.replace(a, b)
    html = fix_paths(html)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)
    return True

def main():
    args = sys.argv[1:]
    # 指定模式: python _restore_content.py productlist:10039,10029 productInfo:10200
    if args:
        ok = 0; tot = 0
        for a in args:
            if ':' in a:
                sub, idlist = a.split(':', 1)
                ids = [x for x in re.split(r'[,，\s]+', idlist) if x]
            else:
                sub, ids = 'productInfo', [a]
            for pid in ids:
                tot += 1
                if process(sub, pid):
                    ok += 1
        print('restored', ok, 'of', tot)
        return
    # 默认: 全量恢复所有 Pairs 下旧快照里存在、而目标缺内容(id=info/info_con)的页
    ok = 0; tot = 0
    for sub, dstsub in PAIRS:
        srcdir = os.path.join(SNAP, sub)
        if not os.path.isdir(srcdir):
            continue
        for fn in sorted(os.listdir(srcdir)):
            m = re.match(r'(\d+)\.html$', fn)
            if not m:
                continue
            pid = m.group(1)
            src = os.path.join(srcdir, fn)
            dst = os.path.join(ROOT, dstsub, fn)
            # 只恢复"目标页当前是空壳/无内容容器"的；已有内容(如 smart-camera)跳过
            need = True
            if os.path.isfile(dst):
                with open(dst, encoding='utf-8') as f:
                    cur = f.read()
                if ('id="info"' in cur) or ('class="info_con"' in cur) or ('vision-page' in cur) or len(cur) > 12000:
                    need = False
            if need:
                tot += 1
                if process(dstsub, pid):
                    ok += 1
    print('restored', ok, 'of', tot, '(only empty/missing pages)')

if __name__ == '__main__':
    main()
