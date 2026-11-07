const fs=require('fs');const path=require('path');const root=path.resolve(__dirname,'..');
const css='<link href="../cn/css/ocr-rebuild.css" rel="stylesheet" type="text/css"/>';
function edit(file,fn){const p=path.join(root,file);let s=fs.readFileSync(p,'utf8');if(!s.includes('ocr-rebuild.css'))s=s.replace('</head>',css+'\n</head>');s=fn(s);fs.writeFileSync(p,s);console.log('finished',file)}
edit('product/smart-camera.html',s=>s.replace(/<img\s+src="\.\.\/UserFiles\/upload\/image\/v3pro-site\/(app-[^"]+\.jpg)"\s+alt="([^"]+)"\s*>/g,(_,src,alt)=>`<span class="ocr-case-card"><img src="../UserFiles/upload/image/v3pro-site/${src}" alt=""><span class="ocr-case-title">${alt}</span></span>`));
edit('productlist/10039.html',s=>{
  const labels={
    'lm2.jpg':'适检产品：','lm4.jpg':'适检产品：','lm6.jpg':'适检产品：'
  };
  for(const [img,label] of Object.entries(labels)){
    const re=new RegExp(`<div class="pics"><img([^>]+src="\\.\\.\\/cn\\/testimg\\/${img.replace('.','\\.')}"[^>]*)\\/><\\/div>`,'i');
    s=s.replace(re,`<div class="pics" style="position:relative;"><img$1/><div class="ocr-overlay" style="position:absolute;left:0;top:0;width:100%;height:100%;overflow:hidden;"><span style="position:absolute;left:0;top:72%;padding:2px 5px;font-size:17px;color:#fff;font-weight:bold;background:rgba(0,0,0,.3);white-space:nowrap;">${label}</span></div></div>`);
  }
  return s;
});
// 10029 页面没有版式型图片文字；加入统一 CSS，供可选中行为与后续后台编辑复用。
edit('productlist/10029.html',s=>s);
