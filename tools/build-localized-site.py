# -*- coding: utf-8 -*-
"""Offline, glossary-driven localization of the MAIBIDA static site.

Produces one standalone deployable HTML file per page x locale, with local SEO
metadata, hreflang/canonical, localised alt text and a shared terminology base.
No network access is required: all translations come from reviewed JSON maps.
"""
from __future__ import annotations

from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment
from collections import defaultdict
import argparse, copy, csv, html, json, os, re, sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from localization_terms import LANGS, TERMS

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT.parent / 'maibida-ocr-rebuilt_backup_20261105_215430'
TOOLS = ROOT / 'tools'
TRANS = TOOLS / 'translations'
BASE = 'https://www.maibida.com/'

PAGES = ['index.html', 'product/10032.html', 'product/smart-camera.html',
         'productlist/10029.html', 'productlist/10030.html', 'productlist/10034.html',
         'productlist/10036.html', 'productlist/10039.html']
MAIN_PAGES = ['index.html', 'product/10032.html', 'product/smart-camera.html']
NON_EN = [l for l in LANGS if l not in ('en-US', 'en-SG')]

CJK = re.compile(r'[\u3400-\u9fff]')
# Characters used only in Simplified Chinese; safe for checking Japanese pages.
SIMPLIFIED_ONLY = re.compile(
    r'[\u8fd9\u4eec\u4e2a\u4e3a\u5e94\u8be5\u8fd8\u8fdb\u8fde\u9002\u65e0\u5382'
    r'\u5e7f\u5f00\u5173\u95ee\u9898\u4ec5\u5bfc\u51fb\u8d28\u7b80\u9009'
    r'\u62e9\u8f6f\u4f18\u5b9e\u73b0\u6807\u51c6\u7ee7\u7eed\u603b]')
# Numeric spec expressions are deliberately kept verbatim (numbers/models/specs are not translated).
PRESERVED_SPEC = re.compile(r'\d+(?:\s*[–~\-]\s*\d+)?\s*[万千百寸秒倍]|SD卡|[0-9][0-9.,]*\s*[万千百]')
FULLWIDTH = {'，': ', ', '；': '; ', '、': ', ', '：': ': ', '（': ' (', '）': ') '}
SD_CARD = {'en-US': 'SD card', 'en-SG': 'SD card', 'es-MX': 'tarjeta SD',
           'id-ID': 'kartu SD', 'th-TH': 'การ์ด SD', 'vi-VN': 'thẻ SD',
           'ko-KR': 'SD 카드', 'ja-JP': 'SDカード', 'ms-MY': 'kad SD', 'ru-RU': 'SD-карта'}
SKIP = {'script', 'style', 'svg', 'noscript', 'template', 'iframe', 'comment'}
SKIP_CLASS = {'vp-language-switch', 'g-translate', 'notranslate'}
SWITCH_LABEL = {'en-US': 'Language', 'en-SG': 'Language', 'es-MX': 'Idioma',
                'id-ID': 'Bahasa', 'th-TH': 'ภาษา', 'vi-VN': 'Ngôn ngữ',
                'ko-KR': '언어', 'ja-JP': '言語', 'ms-MY': 'Bahasa', 'ru-RU': 'Язык'}
# Endonym of the Chinese entry, shown in each locale's language switcher.
ZH_SWITCH_LABEL = {'en-US': 'Chinese (Simplified)', 'en-SG': 'Chinese (Simplified)',
                   'es-MX': 'Chino simplificado', 'id-ID': 'Tionghoa Aksara Sederhana',
                   'th-TH': 'ภาษาจีนตัวย่อ', 'vi-VN': 'Tiếng Trung Giản thể',
                   'ko-KR': '중국어(간체)', 'ja-JP': '簡体字中国語',
                   'ms-MY': 'Bahasa Cina Ringkas', 'ru-RU': 'Китайский (упрощённый)'}
ALT_TERM = {'index.html': '模具监视器', 'product/10032.html': '模具监视器',
            'product/smart-camera.html': '视觉传感器', 'productlist/10029.html': '柔性上料摆盘机',
            'productlist/10030.html': '柔性上料摆盘机', 'productlist/10034.html': '视觉筛选机',
            'productlist/10036.html': '在线检测设备', 'productlist/10039.html': '在线检测设备'}


def variant_filename(rel, lang):
    p = Path(rel)
    return p.with_name(p.stem + '.' + lang + '.html').as_posix()


def abs_url(rel):
    return BASE + rel


def relative_path(start_dir, target):
    return os.path.relpath(str(target), str(start_dir)).replace('\\', '/')


def visible_strings(soup):
    out = []
    for x in soup.find_all(string=True):
        if not str(x).strip() or isinstance(x, Comment) or x.parent.name == '[document]':
            continue
        if any(p.name in SKIP for p in x.parents):
            continue
        if any(SKIP_CLASS.intersection(p.get('class', [])) for p in x.parents if p.name):
            continue
        out.append(x)
    return out


def attr_pairs(soup):
    out = []
    for img in soup.find_all('img'):
        for a in ['alt', 'title']:
            v = img.get(a, '').strip()
            if v:
                out.append((a, v))
    if soup.head:
        for el in soup.head.find_all(attrs={'content': True}):
            v = el.get('content', '').strip()
            if v:
                out.append(('content', v))
    return out


def jsonld_pairs(soup):
    out = []
    for sc in soup.find_all('script', type='application/ld+json'):
        out.extend(re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', sc.get_text()))
    return out


def load_dictionaries():
    units = json.loads((TOOLS / 'translation-units.json').read_text(encoding='utf-8'))
    extra = json.loads((TOOLS / 'translation-units-extra.json').read_text(encoding='utf-8'))
    result = {}
    for lang in LANGS:
        src_lang = 'en-US' if lang == 'en-SG' else lang
        d = {}
        for group, path in [(units, TRANS / (src_lang + '.json')),
                            (extra, TRANS / 'extra' / (src_lang + '.json'))]:
            translated = json.loads(path.read_text(encoding='utf-8'))
            if len(group) != len(translated):
                raise RuntimeError('Translation count mismatch: ' + str(path))
            for a, b in zip(group, translated):
                if a['id'] != b['id'] or not b.get('text', '').strip():
                    raise RuntimeError('Bad translation entry: ' + str(path) + ' ' + a['id'])
                d[a['zh']] = b['text']
        result[lang] = d
    return result


def load_seo():
    result = {}
    for lang in LANGS:
        data = json.loads((TOOLS / 'seo' / (lang + '.json')).read_text(encoding='utf-8'))
        if len(data) != len(PAGES) or {x['page'] for x in data} != set(PAGES):
            raise RuntimeError('SEO metadata incomplete: ' + lang)
        result[lang] = {x['page']: (x['title'], x['description']) for x in data}
    return result


def collect_aligned():
    """Reviewed translations already deployed for the three main pages."""
    page, glob = {}, defaultdict(dict)
    for rel in MAIN_PAGES:
        src = BeautifulSoup((BACKUP / rel).read_text(encoding='utf-8'), 'html.parser')
        a_text, a_attr, a_json = visible_strings(src), attr_pairs(src), jsonld_pairs(src)
        for lang in LANGS:
            p = (BACKUP / rel).with_name(Path(rel).stem + '.' + lang + '.html')
            if not p.exists():
                continue
            tgt = BeautifulSoup(p.read_text(encoding='utf-8'), 'html.parser')
            b_text, b_attr, b_json = visible_strings(tgt), attr_pairs(tgt), jsonld_pairs(tgt)
            m = {}
            if len(a_text) == len(b_text):
                for x, y in zip(a_text, b_text):
                    s = str(x).strip()
                    if CJK.search(s):
                        m[s] = str(y).strip()
            if len(a_attr) == len(b_attr):
                for x, y in zip(a_attr, b_attr):
                    if CJK.search(x[1]):
                        m.setdefault(x[1], y[1])
            if len(a_json) == len(b_json):
                for x, y in zip(a_json, b_json):
                    if CJK.search(x):
                        m.setdefault(x, y)
            page[(rel, lang)] = m
            for k, v in m.items():
                glob[lang].setdefault(k, v)
    return page, glob


class Builder:
    def __init__(self):
        self.dicts = load_dictionaries()
        self.attributes = json.loads((TRANS / 'attributes.json').read_text(encoding='utf-8'))
        self.seo = load_seo()
        self.page, self.glob = collect_aligned()
        self.missing = set()
        self.restored_cells = 0

    @staticmethod
    def polish(text, lang):
        text = re.sub(r'Kunshan\s+(?:Mabida|Meibida|Mebida)\b', 'Kunshan Maibida', text)
        text = re.sub(r'(?<!Kunshan )\b(?:Maibida|Mabida|Meibida|Mebida)\b', 'MAIBIDA', text)
        if lang == 'ja-JP':
            # Chinese fullwidth punctuation should become Japanese punctuation.
            text = text.replace('，', '、').replace('；', '; ')
            return text.strip()
        text = text.replace('SD\u5361', SD_CARD.get(lang, 'SD card'))
        for k, v in FULLWIDTH.items():
            text = text.replace(k, v)
        return text.strip()

    def t(self, value, rel, lang):
        s = value.strip()
        if not CJK.search(s):
            return value
        if s == '\u8bed\u8a00 / Language':
            return SWITCH_LABEL[lang]
        if s == '\u7b80\u4f53\u4e2d\u6587':
            return ZH_SWITCH_LABEL[lang]
        pm = self.page.get((rel, lang), {})
        candidates = [pm.get(s), (self.attributes.get(s) or {}).get(lang),
                      self.dicts[lang].get(s), self.glob[lang].get(s)]
        # Some previously reviewed pages still carry Chinese inside JSON-LD and
        # image alt text. Prefer the first fully localised candidate.
        for out in candidates:
            if out and not self.chinese_left(out, lang):
                return self.polish(out, lang)
        for out in candidates:
            if out:
                return self.polish(out, lang)
        self.missing.add((rel, lang, s))
        return value

    def chinese_left(self, text, lang):
        # Japanese legitimately uses kanji and fullwidth punctuation.
        if lang == 'ja-JP':
            return bool(SIMPLIFIED_ONLY.search(text))
        # In every other locale, visible CJK characters are untranslated Chinese.
        return bool(CJK.search(text))

    def translate_nodes(self, soup, rel, lang):
        for node in list(soup.find_all(string=True)):
            raw = str(node)
            if not raw.strip() or isinstance(node, Comment) or node.parent.name == '[document]':
                continue
            if any(p.name in SKIP for p in node.parents):
                continue
            if any(SKIP_CLASS.intersection(p.get('class', [])) for p in node.parents if p.name):
                continue
            s = raw.strip()
            if not CJK.search(s):
                continue
            lead = raw[:len(raw) - len(raw.lstrip())]
            trail = raw[len(raw.rstrip()):]
            node.replace_with(NavigableString(lead + self.t(s, rel, lang).strip() + trail))

    def translate_attributes(self, soup, rel, lang):
        for el in soup.find_all(True):
            for attr in ['alt', 'title', 'placeholder', 'aria-label', 'content']:
                v = el.get(attr, '')
                if v and CJK.search(v):
                    el[attr] = self.t(v, rel, lang)
        for sc in soup.find_all('script', type='application/ld+json'):
            text = sc.string or sc.get_text()

            def repl(m):
                val = m.group(1)
                if not CJK.search(val):
                    return m.group(0)
                return json.dumps(self.t(val, rel, lang).strip(), ensure_ascii=False)

            text = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', repl, text)
            text = re.sub(r'"inLanguage"\s*:\s*"[^"]*"', '"inLanguage":"' + lang + '"', text)
            for p in PAGES:
                text = text.replace(abs_url(p), abs_url(variant_filename(p, lang)))
            sc.string = text

    def preserve_spec_cells(self, source_soup, soup, rel, lang):
        """Never copy Chinese source text back into a translated numeric cell.

        Localising Chinese count units (800万 -> 8 MP) legitimately changes the
        numeric tokens. Re-copying the source cell used to put Chinese back onto
        every locale page. Only retranslate when the target is still Chinese.
        """
        for srow, trow in zip(source_soup.find_all('tr'), soup.find_all('tr')):
            scs, tcs = srow.find_all(['td', 'th']), trow.find_all(['td', 'th'])
            if len(scs) != len(tcs):
                continue
            for sc, tc in zip(scs, tcs):
                if not re.search(r'\d', sc.get_text()):
                    continue
                if not self.chinese_left(tc.get_text(), lang):
                    continue
                for node in list(tc.find_all(string=True)):
                    s = str(node).strip()
                    if CJK.search(s):
                        node.replace_with(NavigableString(self.t(s, rel, lang)))
                self.restored_cells += 1

    def localize_head(self, soup, rel, out_rel, lang):
        soup.html['lang'] = lang
        title = soup.title.get_text(strip=True) if soup.title else ''
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        desc = desc_tag.get('content', '') if desc_tag else ''
        # Hand-written, length-controlled local search metadata per page and locale.
        if rel in self.seo[lang]:
            title, desc = self.seo[lang][rel]
            if soup.title:
                soup.title.string = title
            if desc_tag:
                desc_tag['content'] = desc
        for m in soup.select('meta[property="og:locale"]'):
            m['content'] = lang.replace('-', '_')
        for m in soup.select('meta[property="og:url"]'):
            m['content'] = abs_url(out_rel)
        for m in soup.select('meta[property="og:title"]'):
            m['content'] = title
        for m in soup.select('meta[property="og:description"]'):
            m['content'] = desc
        for m in soup.select('meta[property="og:site_name"]'):
            m['content'] = 'MAIBIDA'
        for m in soup.select('meta[name="keywords"]'):
            if CJK.search(m.get('content', '')):
                keys = ['模具监视器', '机器视觉', '视觉传感器', '在线检测设备']
                m['content'] = ', '.join(
                    TERMS[k]['en'] if lang.startswith('en') else (TERMS[k].get(lang) or TERMS[k]['en'])
                    for k in keys)
        canonical_tag = soup.find('link', rel='canonical')
        if canonical_tag:
            canonical_tag['href'] = abs_url(out_rel)
        for link in soup.find_all('link', rel='alternate'):
            h = link.get('hreflang')
            if h in {'es-ES', 'en-AU'}:
                link.decompose()
            elif h == lang:
                link['href'] = abs_url(out_rel)
            elif h == 'zh-CN':
                link['href'] = abs_url(rel)
            elif h in LANGS:
                link['href'] = abs_url(variant_filename(rel, h))
            elif h == 'x-default':
                link['href'] = abs_url(variant_filename(rel, 'en-US'))

    def localize_links(self, soup, rel, out_rel, lang):
        out_path = ROOT / out_rel
        for a in soup.find_all('a', href=True):
            href = a['href']
            if re.match(r'^(?:https?:|javascript:|mailto:|tel:|data:|#|//)', href) or not href.endswith('.html'):
                continue
            if a.get('hreflang'):
                continue
            resolved = (out_path.parent / href).resolve()
            try:
                target_rel = resolved.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if target_rel in PAGES:
                a['href'] = relative_path(out_path.parent, ROOT / variant_filename(target_rel, lang))
        switch = soup.select_one('.vp-language-switch')
        if switch:
            summary = switch.find('summary')
            if summary:
                icon = summary.find('span')
                label = SWITCH_LABEL[lang]
                summary.clear()
                if icon:
                    summary.append(icon)
                summary.append(NavigableString(label))
                summary['aria-label'] = label
            nav = switch.find('nav')
            if nav:
                nav['aria-label'] = SWITCH_LABEL[lang]
            for a in switch.select('a[hreflang]'):
                h = a.get('hreflang')
                if h in {'es-ES', 'en-AU'}:
                    a.decompose()
                    continue
                if h == 'zh-CN':
                    target_rel = rel
                elif h in LANGS:
                    target_rel = variant_filename(rel, h)
                else:
                    continue
                a['href'] = relative_path(out_path.parent, ROOT / target_rel)
                a.attrs.pop('aria-current', None)
                a['class'] = [c for c in a.get('class', []) if c != 'active']
                if h == lang:
                    a['aria-current'] = 'page'
                    a['class'] = a.get('class', []) + ['active']

    def add_missing_alt(self, soup, rel, lang):
        term = TERMS.get(ALT_TERM.get(rel, '模具监视器'), {})
        fallback = term.get('en', 'machine vision') if lang.startswith('en') else (term.get(lang) or term.get('en') or 'machine vision')
        count = 0
        for img in soup.find_all('img'):
            if not img.get('alt') and not img.get('aria-hidden'):
                img['alt'] = 'MAIBIDA ' + fallback
                count += 1
        return count

    def build_page(self, rel, lang):
        source_html = (ROOT / rel).read_text(encoding='utf-8')
        out_rel = variant_filename(rel, lang)
        soup = BeautifulSoup(source_html, 'html.parser')
        self.translate_nodes(soup, rel, lang)
        self.translate_attributes(soup, rel, lang)
        self.preserve_spec_cells(BeautifulSoup(source_html, 'html.parser'), soup, rel, lang)
        # The switcher is excluded from text translation; localise its Chinese endonym.
        switch = soup.select_one('.vp-language-switch')
        if switch:
            for node in list(switch.find_all(string=True)):
                if str(node).strip() == '\u7b80\u4f53\u4e2d\u6587':
                    node.replace_with(NavigableString(ZH_SWITCH_LABEL[lang]))
        alt_added = self.add_missing_alt(soup, rel, lang)
        self.localize_head(soup, rel, out_rel, lang)
        self.localize_links(soup, rel, out_rel, lang)
        (ROOT / out_rel).write_text(str(soup), encoding='utf-8')
        return out_rel, alt_added


def build_sitemap():
    ns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml"'
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset ' + ns + '>']
    alternates = [('zh-CN', lambda rel: rel)] + [(l, lambda rel, l=l: variant_filename(rel, l)) for l in LANGS]
    for rel in PAGES:
        for file in [rel] + [variant_filename(rel, l) for l in LANGS]:
            lines.append('  <url>')
            lines.append('    <loc>' + abs_url(file) + '</loc>')
            for h, fn in alternates:
                lines.append('    <xhtml:link rel="alternate" hreflang="' + h + '" href="' + abs_url(fn(rel)) + '"/>')
            lines.append('    <xhtml:link rel="alternate" hreflang="x-default" href="' + abs_url(variant_filename(rel, 'en-US')) + '"/>')
            lines.append('  </url>')
    lines.append('</urlset>')
    (ROOT / 'sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_glossary():
    cols = ['en-US', 'es-MX', 'en-SG', 'id-ID', 'th-TH', 'vi-VN', 'ko-KR', 'ja-JP', 'ms-MY', 'ru-RU']
    with (ROOT / 'localization-glossary.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['中文 / Chinese'] + cols)
        for zh, values in TERMS.items():
            w.writerow([zh] + [values.get(l) or values.get('en') or '' for l in cols])
    head = ['<!DOCTYPE html>', '<html lang="zh-CN"><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>MAIBIDA 多语种工业术语库 | Localization Glossary</title>',
            '<style>body{font:14px/1.6 Arial,"Microsoft YaHei",sans-serif;padding:24px;color:#222}',
            'table{border-collapse:collapse;width:100%;background:#fff}th,td{border:1px solid #d7dde3;padding:8px;text-align:left;vertical-align:top}',
            'th{background:#eaf4ef;position:sticky;top:0}div{overflow-x:auto}h1{font-size:22px}</style></head><body>',
            '<h1>MAIBIDA 多语种工业术语库</h1>',
            '<p>共 %d 条术语。墨西哥采用拉美西语 es-MX；新加坡采用英语 en-SG；马来西亚采用马来语 ms-MY。' % len(TERMS),
            '型号、数字、联系方式及规格参数值一律不翻译。</p><div><table>']
    head.append('<tr><th>中文 / Chinese</th>' + ''.join('<th>' + l + '</th>' for l in cols) + '</tr>')
    for zh, values in TERMS.items():
        head.append('<tr><td>' + html.escape(zh) + '</td>' + ''.join(
            '<td>' + html.escape(values.get(l) or values.get('en') or '') + '</td>' for l in cols) + '</tr>')
    head.append('</table></div></body></html>')
    (ROOT / 'localization-glossary.html').write_text('\n'.join(head), encoding='utf-8')
    return len(TERMS)


def protected_tokens(text):
    out = set()
    out.update(re.findall(r'[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text))
    out.update(re.findall(r'\+\d[\d\s-]{5,}\d', text))
    out.update(re.findall(r'\b(?:V1PRO|IMX-790|SIF/SIS|AtomCV|V3\s?Pro|RS485|TCP-IP|GigE|HDMI|USB|MES|ROI|CCD|AI|IO|I/O|OK|NG|HDR|Gamma|fov)\b', text))
    return out


def audit(builder):
    errors, warnings = [], []
    counts = defaultdict(int)
    title_by_page, desc_by_page = defaultdict(list), defaultdict(list)
    for rel in PAGES:
        source_html = (ROOT / rel).read_text(encoding='utf-8')
        source = BeautifulSoup(source_html, 'html.parser')
        # Chinese count units (800万 -> 8 MP, 200–500万 -> 2–5 MP) are localised,
        # so those digits legitimately change. Exclude whole ranges first, then
        # single values, from the lost-number check.
        numeric_source = re.sub(
            r'\d+(?:\.\d+)?\s*[–~\-]\s*\d+(?:\.\d+)?\s*[万千百]', '', source_html)
        numeric_source = re.sub(r'\d+(?:\.\d+)?\s*[万千百]', '', numeric_source)
        source_numbers = re.findall(r'\d+(?:\.\d+)?', numeric_source)
        tokens = protected_tokens(source_html)
        source_tables = [[c.get_text(' ', strip=True) for c in row.find_all(['td', 'th'])]
                         for row in source.find_all('tr')]
        for lang in LANGS:
            out_rel = variant_filename(rel, lang)
            path = ROOT / out_rel
            if not path.exists():
                errors.append(out_rel + ': MISSING')
                continue
            counts[lang] += 1
            text = path.read_text(encoding='utf-8')
            soup = BeautifulSoup(text, 'html.parser')
            left = builder.chinese_left
            if soup.html.get('lang') != lang:
                errors.append(out_rel + ': html lang')
            if not soup.title or not soup.title.get_text(strip=True):
                errors.append(out_rel + ': no title')
            else:
                t = soup.title.get_text(strip=True)
                if left(t, lang):
                    errors.append(out_rel + ': untranslated title')
                if len(t) > 65:
                    errors.append(out_rel + ': title too long ' + str(len(t)))
                if re.search(r'\b(?:Maibida|Mabida|Meibida|Mebida)\b', t):
                    errors.append(out_rel + ': brand casing in title')
                title_by_page[rel].append(t)
            desc = soup.find('meta', attrs={'name': 'description'})
            if not desc or not desc.get('content'):
                errors.append(out_rel + ': no description')
            else:
                d = desc['content']
                if left(d, lang):
                    errors.append(out_rel + ': untranslated description')
                if len(d) > 155:
                    errors.append(out_rel + ': description too long ' + str(len(d)))
                if re.search(r'\b(?:Maibida|Mabida|Meibida|Mebida)\b', d):
                    errors.append(out_rel + ': brand casing in description')
                desc_by_page[rel].append(d)
            canon = soup.find('link', rel='canonical')
            if not canon or canon.get('href') != abs_url(out_rel):
                errors.append(out_rel + ': canonical mismatch')
            ogu = soup.select_one('meta[property="og:url"]')
            if ogu and ogu.get('content') != abs_url(out_rel):
                errors.append(out_rel + ': og:url mismatch')
            alts = [x for x in soup.find_all('link', rel='alternate')]
            expected = {'zh-CN': abs_url(rel), 'x-default': abs_url(variant_filename(rel, 'en-US'))}
            expected.update({l: abs_url(variant_filename(rel, l)) for l in LANGS})
            if len(alts) != len(expected):
                errors.append(out_rel + ': hreflang count ' + str(len(alts)))
            for a in alts:
                if expected.get(a.get('hreflang')) != a.get('href'):
                    errors.append(out_rel + ': hreflang ' + str(a.get('hreflang')))
            switch = soup.select_one('.vp-language-switch')
            links = switch.select('a[hreflang]') if switch else []
            if len(links) != 1 + len(LANGS):
                errors.append(out_rel + ': language links ' + str(len(links)))
            if not (switch and switch.select('a[hreflang="' + lang + '"][aria-current="page"]')):
                errors.append(out_rel + ': active language missing')
            for img in soup.find_all('img'):
                if left(img.get('alt', ''), lang):
                    errors.append(out_rel + ': untranslated alt ' + img.get('alt', '')[:40])
                    break
            for a in soup.find_all('a', href=True):
                href = a['href']
                if re.match(r'^(?:https?:|javascript:|mailto:|tel:|data:|#|//)', href) or not href.endswith('.html'):
                    continue
                if not (path.parent / href).resolve().exists():
                    errors.append(out_rel + ': broken ' + href)
            # Distinct numeric tokens must all survive; link rewrites legitimately
            # change how often a page id appears, so multiset counts are not used.
            remaining = sorted(set(source_numbers) - set(re.findall(r'\d+(?:\.\d+)?', text)))
            if remaining:
                errors.append(out_rel + ': numbers lost ' + ','.join(remaining[:8]))
            for tok in tokens:
                if tok not in text:
                    errors.append(out_rel + ': protected token lost ' + tok)
            if '<m id=' in text or re.search(r'ZXQ\s*\d+\s*QXZ', text):
                errors.append(out_rel + ': placeholder left')
            target_tables = [[c.get_text(' ', strip=True) for c in row.find_all(['td', 'th'])]
                             for row in soup.find_all('tr')]
            if len(source_tables) != len(target_tables):
                errors.append(out_rel + ': table rows changed')
            for a, b in zip(source_tables, target_tables):
                for x, y in zip(a, b):
                    if not CJK.search(x) and x != y:
                        errors.append(out_rel + ': immutable cell changed ' + x[:30])
            # Visible Chinese anywhere, including numeric spec cells (previously skipped).
            leftover = []
            for node in soup.find_all(string=True):
                if not str(node).strip() or isinstance(node, Comment) or node.parent.name == '[document]':
                    continue
                if any(p.name in SKIP for p in node.parents):
                    continue
                if any(SKIP_CLASS.intersection(p.get('class', [])) for p in node.parents if p.name):
                    continue
                if left(str(node), lang):
                    leftover.append(str(node).strip()[:40])
            if leftover:
                warnings.append(out_rel + ': visible Chinese ' + str(len(leftover)) + ' e.g. ' + ' | '.join(leftover[:3]))
    for rel in PAGES:
        if len(set(title_by_page[rel])) != len(LANGS):
            errors.append(rel + ': duplicate SEO titles across locales')
        if len(set(desc_by_page[rel])) != len(LANGS):
            errors.append(rel + ': duplicate SEO descriptions across locales')
    report = {
        'generated_files': sum(counts.values()),
        'locales': dict(counts),
        'pages': len(PAGES),
        'locales_per_page': len(LANGS),
        'glossary_terms': len(TERMS),
        'untranslated_units': len(builder.missing),
        'untranslated_samples': ['%s | %s | %s' % m for m in sorted(builder.missing)[:40]],
        'untranslated_all': ['%s | %s | %s' % m for m in sorted(builder.missing)],
        'restored_spec_cells': builder.restored_cells,
        'errors': errors,
        'warnings': warnings,
    }
    (ROOT / 'localization-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='report coverage without writing HTML')
    ap.add_argument('--lang', choices=LANGS)
    args = ap.parse_args()
    b = Builder()
    terms = write_glossary()
    if args.check:
        all_units = set()
        for rel in PAGES:
            s = BeautifulSoup((ROOT / rel).read_text(encoding='utf-8'), 'html.parser')
            for x in visible_strings(s):
                if CJK.search(str(x).strip()):
                    all_units.add(str(x).strip())
            for _, v in attr_pairs(s):
                if CJK.search(v):
                    all_units.add(v)
            for v in jsonld_pairs(s):
                if CJK.search(v):
                    all_units.add(v)
            for el in s.find_all(True):
                for a in ['alt', 'title', 'placeholder', 'aria-label', 'content']:
                    v = el.get(a, '').strip()
                    if v and CJK.search(v):
                        all_units.add(v)
        for lang in LANGS:
            missing = sorted(v for v in all_units
                             if v != '\u8bed\u8a00 / Language'
                             and v not in b.dicts[lang] and v not in b.glob[lang]
                             and not (v in b.attributes and lang in b.attributes[v])
                             and not any(v in b.page.get((p, lang), {}) for p in MAIN_PAGES))
            print('COVERAGE', lang, 'total', len(all_units), 'missing', len(missing))
            for v in missing[:12]:
                print('   ', repr(v[:80]))
        print('GLOSSARY_TERMS', terms)
        return
    targets = [args.lang] if args.lang else LANGS
    for rel in PAGES:
        for lang in targets:
            out_rel, alt = b.build_page(rel, lang)
            print('BUILD', out_rel, 'alt_added', alt, flush=True)
    build_sitemap()
    report = audit(b)
    print('AUDIT', report['generated_files'], 'files', len(report['errors']), 'errors',
          len(report['warnings']), 'warnings', 'untranslated_units', report['untranslated_units'],
          'restored_spec_cells', report['restored_spec_cells'])
    print('\n'.join(report['errors'][:40]))
    if report['errors'] or report['untranslated_units']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
