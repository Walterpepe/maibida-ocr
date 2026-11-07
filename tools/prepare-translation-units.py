from pathlib import Path
from bs4 import BeautifulSoup, Comment
from collections import OrderedDict
import json, re

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['productlist/10029.html', 'productlist/10030.html', 'productlist/10034.html',
         'productlist/10036.html', 'productlist/10039.html']
CJK = re.compile(r'[㐀-鿿]')
units = OrderedDict()

for rel in PAGES:
    soup = BeautifulSoup((ROOT / rel).read_text(encoding='utf-8'), 'html.parser')
    for node in soup.find_all(string=True):
        if not str(node).strip() or isinstance(node, Comment):
            continue
        if node.parent.name in ['script', 'style', '[document]'] or node.find_parent(['script', 'style', 'svg']):
            continue
        if node.find_parent(class_='vp-language-switch'):
            continue
        value = str(node).strip()
        if CJK.search(value):
            units.setdefault(value, [])
            units[value].append(rel + ':text')
    for img in soup.find_all('img'):
        for attr in ['alt', 'title']:
            value = img.get(attr, '').strip()
            if CJK.search(value):
                units.setdefault(value, [])
                units[value].append(rel + ':' + attr)
    for element in soup.head.find_all(attrs={'content': True}):
        value = element['content'].strip()
        if CJK.search(value):
            units.setdefault(value, [])
            units[value].append(rel + ':meta')
    for script in soup.find_all('script', type='application/ld+json'):
        for value in re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', script.get_text()):
            if CJK.search(value):
                units.setdefault(value, [])
                units[value].append(rel + ':jsonld')

output = [{'id': 'u%04d' % i, 'zh': value, 'locations': sorted(set(locations))}
          for i, (value, locations) in enumerate(units.items())]
path = ROOT / 'tools' / 'translation-units.json'
path.write_text(json.dumps(output, ensure_ascii=False, indent=1), encoding='utf-8')
print(path)
print('unique_units=', len(output), 'source_chars=', sum(len(x['zh']) for x in output))
