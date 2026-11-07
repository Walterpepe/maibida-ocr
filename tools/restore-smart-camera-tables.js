const fs=require('fs');
const path=require('path');
const file=path.resolve(__dirname,'..','product','smart-camera.html');
let html=fs.readFileSync(file,'utf8');

function replaceSection(label,image,alt){
  const escaped=label.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  const re=new RegExp(`<section class="ocr-table-wrap" aria-label="${escaped}">[\\s\\S]*?<\\/section>`);
  if(!re.test(html))throw new Error(`Rebuilt table not found: ${label}`);
  const semantic=`<span class="ocr-semantic-text">${alt}</span>`;
  html=html.replace(re,`<div class="ocr-original-table">${semantic}<img src="../UserFiles/upload/image/v3pro-site/${image}" alt="${alt}"></div>`);
}

replaceSection(
  'V3 Pro-150M 视野参数（单位：mm）',
  'v3pro-fov.jpg',
  'V3 Pro 检测视野及订货镜头参数：8mm F2.8、12mm F5.6、16mm F5.6；包含工作距离、视野范围、单像素精度、HFOV、VFOV、DFOV及示意图。'
);
replaceSection(
  'CV3 Pro 检测范围',
  'cv3-range.jpg',
  'CV3 Pro 检测范围参数：CV3 Pro-150M与CV3 Pro-500M，包含6mm、8mm、12mm、16mm镜头的工作距离、视野范围及单像素精度。'
);

fs.writeFileSync(file,html,'utf8');
console.log('Restored original V3 Pro and CV3 Pro table images.');
