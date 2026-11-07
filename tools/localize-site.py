# -*- coding: utf-8 -*-
"""Generate separate deployable MAIBIDA HTML files for the confirmed 11 locales."""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
from collections import defaultdict
import argparse, csv, html, json, re, sys, time
import requests
from localization_terms import LANGS, TARGET_CODES, TERMS

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / 'tools' / 'localization-cache.json'
PAGES = ['index.html', 'product/10032.html', 'product/smart-camera.html',
         'productlist/10029.html', 'productlist/10030.html', 'productlist/10034.html',
         'productlist/10036.html', 'productlist/10039.html']
BASE = 'https://www.maibida.com/'
SKIP = {'script', 'style', 'svg', 'noscript', 'template', 'iframe', 'comment'}
SKIP_CLASS = {'vp-language-switch', 'g-translate', 'notranslate'}
CJK = re.compile(r'[㐀-鿿]')


def cached():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding='utf-8'))
    return {}


def save_cache(data):
    CACHE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')


class Translator:
    def __init__(self):
        self.cache = cached()
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0'
        self.changed = False
        self.requests = 0

    @staticmethod
    def protect(text, lang):
        """One-pass XML placeholders avoid nested matches and survive MT services."""
        terms = sorted(TERMS, key=len, reverse=True)
        immutable = r'(?:[A-Za-z]+[-_]?[A-Za-z]*\d+[A-Za-z0-9_./:+*%-]*|[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\+\d[\d -]{5,}\d|\b(?:HDMI|USB|Insert\s+Molding|Molding|ROI|OK|NG|AI|CCD|IO|I/O|MES|NVR|PLC|GigE|AtomCV|SIF|SIS|TCP-IP|RS485)\b)'
        pattern = re.compile('|'.join(map(re.escape, terms)) + '|' + immutable, re.I)
        tokens = []
        def reserve(m):
            value = m.group(0)
            if value in TERMS:
                value = TERMS[value]['en'] if lang.startswith('en') else (TERMS[value].get(lang) or TERMS[value]['en'])
            key = '<m id="%d"/>' % len(tokens)
            tokens.append((key, value))
            return key
        return pattern.sub(reserve, text), tokens

    @staticmethod
    def restore(text, tokens):
        for key, value in tokens:
            ident = re.search(r'\d+', key).group(0)
            text = re.sub(r'<m\s+id=["\']?' + ident + r'["\']?\s*/?>', lambda _: value, text, flags=re.I)
            text = text.replace(key, value)
        return text

    def translate(self, text, lang):
        key = lang + '\0' + text
        if key in self.cache and not re.search(r'ZXQ\s*\d+\s*QXZ', self.cache[key], re.I):
            return self.cache[key]
        if not CJK.search(text):
            return text
        protected, tokens = self.protect(text, lang)
        url = 'https://api.mymemory.translated.net/get'
        result = None
        for attempt in range(3):
            try:
                r = self.session.get(url, params={'q': protected, 'langpair': 'zh-CN|' + TARGET_CODES[lang]}, timeout=35)
                data = r.json()
                if r.status_code == 200 and data.get('responseStatus') == 200:
                    result = data['responseData']['translatedText']
                    break
                if 'QUERY LENGTH LIMIT' in str(data) and len(protected) > 220:
                    parts = re.split(r'(?<=[。；;])', protected)
                    result = ''.join(self.translate(x, lang) for x in parts if x)
                    break
                print('TRANSLATE_SERVICE', lang, str(data)[:200], flush=True)
            except (requests.RequestException, ValueError) as e:
                print('TRANSLATE_RETRY', lang, type(e).__name__, flush=True)
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
        if result is None:
            raise RuntimeError('Untranslated source: ' + lang + ': ' + text[:80])
        result = html.unescape(result)
        if lang == 'ja-JP':
            stripped = result
            for _, value in tokens:
                stripped = stripped.replace(value, '')
            if any(len(c) >= 2 and any(k in c for k in ['支持', '检测', '设备', '产品', '连接器']) for c in re.findall(r'[一-鿿]+', stripped)):
                raise RuntimeError('Untranslated MT result: ' + lang + ': ' + text[:80])
        elif CJK.search(result):
            print('MT_CJK_REVIEW', lang, repr(text), repr(result), flush=True)
        result = self.restore(result, tokens)
        if re.search(r'ZXQ\s*\d+\s*QXZ', result, re.I):
            raise RuntimeError('Unrestored immutable token: ' + lang + ': ' + text[:80])
        self.cache[key] = result
        self.changed = True
        self.requests += 1
        if self.requests % 40 == 0:
            save_cache(self.cache)
            self.changed = False
            print('TRANSLATION_CHECKPOINT', self.requests, 'entries', len(self.cache), flush=True)
        return result

    def finish(self):
        if self.changed:
            save_cache(self.cache)
        print('TRANSLATION_DONE', self.requests, 'new / total', len(self.cache), flush=True)


def translatable(node):
    if not isinstance(node, NavigableString) or not str(node).strip():
        return False
    if node.parent.name in SKIP or node.parent.name == '[document]':
        return False
    if any(p.name in SKIP for p in node.parents):
        return False
    if isinstance(node, __import__('bs4').Comment):
        return False
    if any(SKIP_CLASS.intersection(p.get('class', [])) for p in node.parents if p.name):
        return False
    return bool(CJK.search(str(node)))


def reuse_translations():
    """Map each Chinese text node to its aligned existing translation."""
    mapping = defaultdict(dict)
    def visible_nodes(soup, source=False):
        result = []
        for x in soup.find_all(string=True):
            if not str(x).strip() or isinstance(x, __import__('bs4').Comment) or x.parent.name == '[document]':
                continue
            if any(p.name in SKIP for p in x.parents):
                continue
            if any(SKIP_CLASS.intersection(p.get('class', [])) for p in x.parents if p.name):
                continue
            if source and isinstance(x, __import__('bs4').Comment):
                continue
            result.append(x)
        return result
    # Read the known-good, pre-build versions from the full snapshot.
    backup = ROOT.parent / 'maibida-ocr-rebuilt_backup_20261105_215430'
    for rel in ['index.html', 'product/10032.html', 'product/smart-camera.html']:
        source = BeautifulSoup((backup / rel).read_text(encoding='utf-8'), 'html.parser')
        for lang in LANGS:
            target_path = (backup / rel).with_name(Path(rel).stem + '.' + lang + '.html')
            if not target_path.exists():
                continue
            target = BeautifulSoup(target_path.read_text(encoding='utf-8'), 'html.parser')
            a, b = visible_nodes(source, True), visible_nodes(target)
            if len(a) != len(b):
                print('ALIGNMENT_MISMATCH', rel, lang, len(a), len(b))
                continue
            mapping[rel][lang] = {str(x): str(y) for x, y in zip(a, b)}
    return mapping


def variant_filename(rel, lang):
    p = Path(rel)
    return p.with_name(p.stem + '.' + lang + '.html').as_posix()


def canonical(rel):
    return BASE + rel


def alt_url(rel):
    return canonical(rel)


def localize_links(soup, rel, lang):
    # Every new page is self-contained with the site's shared assets, not one merged document.
    for a in soup.find_all('a', href=True):
        href = a['href']
        for source in PAGES:
            localized = variant_filename(source, lang)
            prefix = '../' if '/' in rel else ''
            if href == source or href == prefix + source:
                a['href'] = prefix + localized
    # Link only pages that exist. es-ES is not a confirmed target of this build.
    for a in soup.select('.vp-language-switch a[hreflang="es-ES"]'):
        a.decompose()
    for a in soup.select('.vp-language-switch a[hreflang="en-AU"]'):
        a.decompose()
    switch = soup.select_one('.vp-language-switch')
    if switch:
        label = {'en-US': 'Language', 'en-SG': 'Language', 'es-MX': 'Idioma', 'id-ID': 'Bahasa', 'th-TH': 'ภาษา', 'vi-VN': 'Ngôn ngữ', 'ko-KR': '언어', 'ja-JP': '言語', 'ms-MY': 'Bahasa', 'ru-RU': 'Язык'}[lang]
        summary = switch.find('summary')
        if summary:
            icon = summary.find('span')
            summary.clear()
            if icon:
                summary.append(icon)
            summary.append(NavigableString(label))
            summary['aria-label'] = label
        nav = switch.find('nav')
        if nav:
            nav['aria-label'] = label
        for a in switch.select('a[hreflang]'):
            a.attrs.pop('aria-current', None)
            a['class'] = []
            if a.get('hreflang') == lang:
                a['aria-current'] = 'page'
                a['class'] = ['active']
    for link in soup.find_all('link', rel='alternate'):
        if link.get('hreflang') in {'es-ES', 'en-AU'}:
            link.decompose()
        elif link.get('hreflang') == lang:
            link['href'] = alt_url(rel)
        elif link.get('hreflang') == 'zh-CN':
            base_rel = re.sub(r'\.[a-z]{2}-[A-Z]{2}\.html$', '.html', rel)
            link['href'] = canonical(base_rel)
        elif link.get('hreflang') in LANGS:
            base_rel = re.sub(r'\.[a-z]{2}-[A-Z]{2}\.html$', '.html', rel)
            link['href'] = canonical(variant_filename(base_rel, link['hreflang']))
        elif link.get('hreflang') == 'x-default':
            base_rel = re.sub(r'\.[a-z]{2}-[A-Z]{2}\.html$', '.html', rel)
            link['href'] = canonical(variant_filename(base_rel, 'en-US'))
    canonical_tag = soup.find('link', rel='canonical')
    if canonical_tag:
        canonical_tag['href'] = alt_url(rel)


def localize_head(soup, rel, lang):
    soup.html['lang'] = lang
    for m in soup.select('meta[property="og:locale"]'):
        m['content'] = lang.replace('-', '_')
    for m in soup.select('meta[property="og:url"]'):
        m['content'] = canonical(rel)
    for m in soup.select('meta[property="og:title"]'):
        m['content'] = soup.title.get_text(strip=True)
    description = soup.find('meta', attrs={'name': 'description'})
    if description:
        for m in soup.select('meta[property="og:description"]'):
            m['content'] = description.get('content', '')
    for m in soup.select('meta[property="og:site_name"]'):
        m['content'] = 'MAIBIDA'
    for m in soup.select('meta[name="keywords"]'):
        if CJK.search(m.get('content', '')):
            m['content'] = ', '.join((TERMS[t].get(lang) or TERMS[t]['en']) if not lang.startswith('en') else TERMS[t]['en'] for t in ['模具监视器', '机器视觉', '视觉传感器', '在线检测设备'])
    # JSON-LD gets locale URLs, not a shared Chinese canonical.
    for sc in soup.find_all('script', attrs={'type': 'application/ld+json'}):
        value = sc.string or sc.get_text()
        for page in PAGES:
            value = value.replace(canonical(page), canonical(variant_filename(page, lang)))
        value = re.sub(r'"inLanguage"\s*:\s*"zh-CN"', '"inLanguage":"' + lang + '"', value)
        sc.string = value


def build_sitemap():
    ns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml"'
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset ' + ns + '>']
    for rel in PAGES:
        for file in [rel] + [variant_filename(rel, l) for l in LANGS]:
            out.append('  <url>')
            out.append('    <loc>' + canonical(file) + '</loc>')
            for lang, source in [('zh-CN', rel)] + [(l, variant_filename(rel, l)) for l in LANGS] + [('x-default', variant_filename(rel, 'en-US'))]:
                out.append('    <xhtml:link rel="alternate" hreflang="' + lang + '" href="' + canonical(source) + '"/>')
            out.append('  </url>')
    out.append('</urlset>')
    (ROOT / 'sitemap.xml').write_text('\n'.join(out) + '\n', encoding='utf-8')


def audit():
    errors = []
    counts = defaultdict(int)
    for rel in PAGES:
        source = (ROOT / rel).read_text(encoding='utf-8')
        source_soup = BeautifulSoup(source, 'html.parser')
        source_tables = [[c.get_text(' ', strip=True) for c in row.find_all(['td', 'th'])] for row in source_soup.find_all('tr')]
        source_numbers = re.findall(r'\d+(?:\.\d+)?', source)
        for lang in LANGS:
            out_rel = variant_filename(rel, lang)
            path = ROOT / out_rel
            if not path.exists():
                errors.append(out_rel + ': MISSING')
                continue
            counts[lang] += 1
            text = path.read_text(encoding='utf-8')
            soup = BeautifulSoup(text, 'html.parser')
            if soup.html.get('lang') != lang:
                errors.append(out_rel + ': html lang')
            for selector in [('meta', {'name': 'description'}), ('link', {'rel': 'canonical'})]:
                if not soup.find(*selector):
                    errors.append(out_rel + ': missing ' + str(selector))
            canonical_tag = soup.find('link', rel='canonical')
            if canonical_tag and canonical_tag['href'] != canonical(out_rel):
                errors.append(out_rel + ': canonical mismatch')
            if len(soup.select('.vp-language-switch a[hreflang]')) != 11:
                errors.append(out_rel + ': language links != 11')
            if not soup.select('.vp-language-switch a[hreflang="' + lang + '"][aria-current="page"]'):
                errors.append(out_rel + ': active language missing')
            if any(CJK.search(img.get('alt', '')) for img in soup.find_all('img')):
                errors.append(out_rel + ': untranslated alt')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if re.match(r'^(?:https?:|javascript:|mailto:|tel:|data:|#|//)', href) or not href.endswith('.html'):
                    continue
                if not (path.parent / href.replace('/', '/')).resolve().exists():
                    errors.append(out_rel + ': broken ' + href)
            target_numbers = re.findall(r'\d+(?:\.\d+)?', text)
            missing = list(source_numbers)
            for number in target_numbers:
                if number in missing:
                    missing.remove(number)
            if missing:
                errors.append(out_rel + ': numbers missing ' + ','.join(missing[:10]))
            target_tables = [[c.get_text(' ', strip=True) for c in row.find_all(['td', 'th'])] for row in soup.find_all('tr')]
            if len(source_tables) != len(target_tables):
                errors.append(out_rel + ': table rows changed')
            for a, b in zip(source_tables, target_tables):
                for x, y in zip(a, b):
                    if not CJK.search(x) and x != y:
                        errors.append(out_rel + ': immutable cell changed: ' + x)
    (ROOT / 'localization-audit.json').write_text(json.dumps({'files': sum(counts.values()), 'locales': dict(counts), 'errors': errors}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('AUDIT', sum(counts.values()), 'errors', len(errors))
    print('\n'.join(errors[:60]))
    return not errors


def write_glossary():
    with (ROOT / 'localization-glossary.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['中文', 'en-US / en-SG', 'es-MX', 'id-ID', 'th-TH', 'vi-VN', 'ko-KR', 'ja-JP', 'ms-MY', 'ru-RU'])
        for zh, values in TERMS.items():
            writer.writerow([zh] + [values.get(l) or values.get('en') for l in ['en-US', 'es-MX', 'id-ID', 'th-TH', 'vi-VN', 'ko-KR', 'ja-JP', 'ms-MY', 'ru-RU']])
    lines = ['<!DOCTYPE html>', '<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">', '<title>MAIBIDA 多语种工业术语库</title><style>body{font:14px Arial,sans-serif;padding:24px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccc;padding:8px;text-align:left;vertical-align:top}th{background:#e9f5ef}div{overflow-x:auto}</style></head><body>', '<h1>MAIBIDA 多语种工业术语库</h1><p>墨西哥版本统一使用 es-MX。型号、数字、联系方式及规格参数值不翻译。</p><div><table>']
    lines.append('<tr><th>中文</th>' + ''.join('<th>' + l + '</th>' for l in ['en-US / en-SG', 'es-MX', 'id-ID', 'th-TH', 'vi-VN', 'ko-KR', 'ja-JP', 'ms-MY', 'ru-RU']) + '</tr>')
    for zh, values in TERMS.items():
        lines.append('<tr><td>' + html.escape(zh) + '</td>' + ''.join('<td>' + html.escape(values.get(l) or values.get('en')) + '</td>' for l in ['en-US', 'es-MX', 'id-ID', 'th-TH', 'vi-VN', 'ko-KR', 'ja-JP', 'ms-MY', 'ru-RU']) + '</tr>')
    lines.append('</table></div></body></html>')
    (ROOT / 'localization-glossary.html').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit-only', action='store_true')
    parser.add_argument('--lang', choices=LANGS)
    parser.add_argument('--page', choices=PAGES)
    args = parser.parse_args()
    write_glossary()
    if args.audit_only:
        raise SystemExit(0 if audit() else 1)
    translator = Translator()
    reused = reuse_translations()
    targets = [args.lang] if args.lang else LANGS
    for rel in ([args.page] if args.page else PAGES):
        source_html = (ROOT / rel).read_text(encoding='utf-8')
        for lang in targets:
            target_path = ROOT / variant_filename(rel, lang)
            print('BUILD', rel, lang, flush=True)
            soup = BeautifulSoup(source_html, 'html.parser')
            mapping = reused.get(rel, {}).get(lang, {})
            for node in [x for x in soup.find_all(string=True) if translatable(x)]:
                source = str(node)
                if source in mapping:
                    translated = mapping[source]
                else:
                    translated = translator.translate(source.strip(), lang)
                node.replace_with(NavigableString(translated))
            for img in soup.find_all('img'):
                for attr in ['alt', 'title']:
                    value = img.get(attr, '')
                    if CJK.search(value):
                        img[attr] = translator.translate(value, lang)
                    elif not img.get('alt') and not img.get('aria-hidden'):
                        img['alt'] = (TERMS['机器视觉'].get(lang) or 'machine vision')
            for attr in ['aria-label', 'title', 'placeholder']:
                for element in soup.find_all(attrs={attr: True}):
                    value = element.get(attr, '')
                    if CJK.search(value):
                        element[attr] = translator.translate(value, lang)
            # Numeric cells and immutable table content must remain exactly as supplied.
            if soup.find_all('table'):
                for srow, trow in zip(BeautifulSoup(source_html, 'html.parser').find_all('tr'), soup.find_all('tr')):
                    for sc, tc in zip(srow.find_all(['td', 'th']), trow.find_all(['td', 'th'])):
                        if re.search(r'\d', sc.get_text()):
                            tc.clear()
                            for child in list(sc.contents):
                                tc.append(child)
            # Attribute text (title/description/keywords) is separate from visible nodes.
            for element in soup.find_all(True):
                for attr in ['content']:
                    value = element.get(attr, '')
                    if CJK.search(value):
                        element[attr] = translator.translate(value.strip(), lang)
            for old, new in [('Mabida', 'MAIBIDA'), ('Maibida', 'MAIBIDA')]:
                if soup.title:
                    soup.title.string = soup.title.get_text().replace(old, new)
            # Restore the original supplied specs when old English localized measurements.
            for snode, tnode in zip([x for x in BeautifulSoup(source_html, 'html.parser').find_all(string=True) if str(x).strip()], [x for x in soup.find_all(string=True) if str(x).strip()]):
                if CJK.search(str(snode)) and re.search(r'\d', str(snode)):
                    snums = re.findall(r'\d+(?:\.\d+)?', str(snode))
                    tnums = re.findall(r'\d+(?:\.\d+)?', str(tnode))
                    if snums != tnums and str(snode).strip() in mapping:
                        tnode.replace_with(NavigableString(translator.translate(str(snode).strip(), lang)))
            localize_head(soup, variant_filename(rel, lang), lang)
            localize_links(soup, rel, lang)
            target_path.write_text(str(soup), encoding='utf-8')
    translator.finish()
    if not args.page:
        build_sitemap()
        if not audit():
            raise SystemExit(1)


if __name__ == '__main__':
    main()
