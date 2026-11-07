const fs=require('fs');const path=require('path');
const file=path.resolve(__dirname,'..','product','smart-camera.html');
let html=fs.readFileSync(file,'utf8');
const positions=['8mm','12mm','16mm'];let index=0;
html=html.replace(/<div class="fov-diagram"[\s\S]*?<span class="fov-zoom">Zoom<\/span><\/div>/g,()=>{const lens=positions[index++]||'';return `<div class="fov-original-crop lens-${lens.replace('mm','')}" role="img" aria-label="原版 ${lens} 镜头视野示意图"></div>`;});
if(index!==3)throw new Error(`Expected 3 diagrams, replaced ${index}`);
fs.writeFileSync(file,html,'utf8');console.log('Restored 3 original diagram crops.');
