const fs=require('fs');const path=require('path');
const root=path.resolve(__dirname,'..');
const descriptions={
 'product/10032.html':'迈必达IMX-790模具监视器支持多相机、AI图像采集和ROI检测，用于注塑模具保护、镶件到位、产品残留及脱模状态检测。',
 'productlist/10030.html':'迈必达连接器在线检测设备面向冲压件单料带与双料带检测，覆盖产品正反面和侧面的毛刺、异色、尺寸不良等缺陷。',
 'productlist/10034.html':'迈必达Insert Molding带料检测设备支持单、双、四料带在线视觉检测，可识别缺料、尺寸不良等问题并与冲压生产同步。',
 'productlist/10036.html':'迈必达塑料件在线检测设备适配注塑机与机械手，可进行产品外观、尺寸、缺料和位置检测，支持多相机高速在线检测。',
 'productlist/10039.html':'迈必达视觉筛选机覆盖摄像头、电机配件、纽扣、硅塑胶、金属件和换向器等产品，实现外观缺陷、尺寸检测与自动分拣。'
};
const products={
 'product/10032.html':['IMX-790模具监视器','工业视觉模具保护设备','模具监视器'],
 'productlist/10030.html':['连接器在线检测设备','连接器及冲压料带在线视觉检测设备','在线检测设备'],
 'productlist/10034.html':['Insert Molding带料检测设备','单料带、双料带和四料带在线视觉检测设备','在线检测设备'],
 'productlist/10036.html':['塑料件在线检测设备','适配注塑机与机械手的塑料件在线视觉检测系统','在线检测设备'],
 'productlist/10039.html':['视觉筛选机','工业零部件外观与尺寸视觉检测及自动分拣设备','视觉筛选机']
};
function write(file,fn){const p=path.join(root,file);let s=fs.readFileSync(p,'utf8');s=fn(s);fs.writeFileSync(p,s,'utf8');console.log('SEO updated',file)}
for(const [file,desc] of Object.entries(descriptions))write(file,s=>s.replace(/<meta\s+content="[^"]*"\s+name="description"\s*\/>/i,`<meta content="${desc}" name="description"/>`));
write('productlist/10029.html',s=>s.replaceAll('觉并联上料机器人','视觉并联上料机器人'));
write('index.html',s=>s.replace(/<link rel="alternate" hreflang="en"[^>]*>/i,''));
// 案例标题已经紧邻图片显示；同步到 alt，兼顾图片理解与无障碍回退。
write('product/smart-camera.html',s=>s.replace(/<span class="ocr-case-card"><img src="([^"]+)" alt=""><span class="ocr-case-title">([^<]+)<\/span><\/span>/g,(_,src,title)=>`<span class="ocr-case-card"><img src="${src}" alt="${title}"><span class="ocr-case-title">${title}</span></span>`));
for(const [file,[name,description,category]] of Object.entries(products))write(file,s=>{
 if(s.includes('"@id":"https://www.maibida.com/'+file+'#product"'))return s;
 const schema={"@context":"https://schema.org","@type":"Product","@id":`https://www.maibida.com/${file}#product`,name,description,category,url:`https://www.maibida.com/${file}`,image:'https://www.maibida.com/cn/images/maibida-logo.png',brand:{"@type":"Brand",name:'迈必达'},manufacturer:{"@type":"Organization",name:'昆山迈必达智能设备有限公司',url:'https://www.maibida.com/'}};
 return s.replace('</head>',`<script type="application/ld+json">${JSON.stringify(schema)}</script>\n</head>`);
});
// 首页 canonical 使用根 URL，因此 sitemap 和首页 hreflang 也统一到根 URL。
write('sitemap.xml',s=>s.replaceAll('https://www.maibida.com/index.html','https://www.maibida.com/'));
