const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const pages = [
  'index.html',
  'product/10032.html',
  'product/smart-camera.html',
  'productlist/10029.html',
  'productlist/10030.html',
  'productlist/10034.html',
  'productlist/10036.html',
  'productlist/10039.html',
];
const ocr = JSON.parse(fs.readFileSync(path.join(root, '_ocr_result.json'), 'utf8'));

function attr(tag, name) {
  const match = tag.match(new RegExp(`\\b${name}\\s*=\\s*(["'])(.*?)\\1`, 'i'));
  return match ? match[2] : '';
}

const inventory = [];
for (const page of pages) {
  const html = fs.readFileSync(path.join(root, page), 'utf8');
  const tags = html.match(/<img\b[^>]*>/gi) || [];
  for (const tag of tags) {
    const src = attr(tag, 'src');
    if (!src || /^(?:data:|https?:|\/\/)/i.test(src)) continue;
    const pageDir = path.posix.dirname(page.replace(/\\/g, '/'));
    const normalized = path.posix.normalize(path.posix.join(pageDir, src.replace(/\\/g, '/'))).replace(/^\.\//, '');
    const record = ocr[normalized];
    inventory.push({
      page,
      src,
      image: normalized,
      alt: attr(tag, 'alt'),
      ocr: record?.text || '',
      hasOcr: Boolean(record?.text?.trim()),
    });
  }
}

fs.writeFileSync(path.join(root, 'ocr-inventory.json'), JSON.stringify(inventory, null, 2));
const textLines=[];
for(const page of pages){textLines.push(`# ${page}`);const seen=new Set();for(const item of inventory.filter(x=>x.page===page&&x.hasOcr)){if(seen.has(item.image))continue;seen.add(item.image);textLines.push(`\n[${item.image}]\n${item.ocr}`)}textLines.push('');}
fs.writeFileSync(path.join(root,'ocr-text.txt'),textLines.join('\n'),'utf8');
const unique = new Map();
for (const item of inventory) {
  if (!unique.has(item.image)) unique.set(item.image, item);
}
const candidates = [...unique.values()].filter((item) => item.hasOcr);
console.log(JSON.stringify({ pages: pages.length, imageUses: inventory.length, uniqueImages: unique.size, ocrCandidates: candidates.length }, null, 2));
for (const item of candidates) console.log(`${item.page}\t${item.image}\t${item.ocr.slice(0, 180)}`);
