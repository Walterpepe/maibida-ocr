const fs=require('fs');const path=require('path');
const file=path.resolve(__dirname,'..','product','smart-camera.html');
let html=fs.readFileSync(file,'utf8');

const diagram=(lens,near,far,views)=>`<div class="fov-diagram" aria-label="${lens}镜头视野示意图"><div class="fov-camera">V3 Pro</div><div class="fov-axis"></div><div class="fov-cone left"></div><div class="fov-cone right"></div><span class="fov-near">${near}mm</span><span class="fov-far">${far}mm</span>${views.map((v,i)=>`<span class="fov-view v${i+1}">${v}</span>`).join('')}<span class="fov-zoom">Zoom</span></div>`;
const lensSection=(title,order,rows,diag)=>`<tr class="lens-order"><th colspan="2">订货号（${title}）</th><td colspan="6">${order}</td></tr><tr><th>工作距离WD<br>(mm)</th><th>视野范围<br>(mm)<br>（水平×垂直）</th><th>单像素精度<br>(mm)</th><th>HFOV(mm)</th><th>HFOV(°)</th><th>VFOV(°)</th><th>DFOV(°)</th><th>示意图(mm)</th></tr>${rows.map((r,i)=>`<tr>${r.map(v=>`<td>${v}</td>`).join('')}${i===0?`<td rowspan="${rows.length}" class="diagram-cell">${diag}</td>`:''}</tr>`).join('')}`;
const v3=`<section class="fov-html-block" aria-labelledby="v3-fov-heading"><h3 id="v3-fov-heading">V3 Pro 检测视野</h3><div class="fov-scroll"><table class="fov-exact-table"><tbody>
${lensSection('8mm F2.8','V3 Pro-150M-08 / V3 Pro-150C-08',[
['20','17×12','0.04','22.02','44.39','33.4','57.67'],['95','63×47','0.04','78.60','37.31','27.8','44.95'],['245','224×167','0.16','279.40','49.73','37.02','59.38'],['345','310×227','0.22','384.23','49.22','36.32','58.22'],['945','840×620','0.58','1044.03','48.81','36.19','57.83']],diagram('8mm','20','945',['17×12mm','224×167mm','840×620mm']))}
${lensSection('12mm F5.6','V3 Pro-150M-12 / V3 Pro-150C-12',[
['55','25×18','0.02','30.81','25.61','18.66','31.29'],['95','41×31','0.03','51.40','24.35','18.33','30.28'],['245','104×78','0.07','130.00','23.97','17.93','29.72'],['345','145×107','0.1','180.21','23.74','17.69','29.27'],['945','396×298','0.28','495.60','23.67','17.80','29.39']],diagram('12mm','55','945',['25×18mm','104×78mm','396×298mm']))}
${lensSection('16mm F5.6','V3 Pro-150M-16 / V3 Pro-150C-16',[
['90','27×20','0.02','33.6','17.06','12.75','21.15'],['95','28×21','0.02','35','16.77','12.53','20.88'],['245','75×56','0.05','93.6','17.40','12.99','21.63'],['345','107×79','0.07','133','17.63','12.95','21.82'],['755','236×174','0.16','293.21','17.77','12.99','21.98']],diagram('16mm','90','755',['27×20mm','75×56mm','236×174mm']))}
</tbody></table></div><p class="fov-unit">单位：mm</p></section>`;

const cvRows=(model,lens,values)=>`<tr><th rowspan="2">${model}</th><td rowspan="2">${lens}</td><th>视野范围(mm)</th>${values[0].map(v=>`<td>${v}</td>`).join('')}</tr><tr><th>单像素精度(mm)</th>${values[1].map(v=>`<td>${v}</td>`).join('')}</tr>`;
const cv3=`<section class="fov-html-block" aria-labelledby="cv3-range-heading"><h3 id="cv3-range-heading">CV3 Pro 检测范围</h3><div class="fov-scroll"><table class="cv3-exact-table"><tbody>
<tr><th rowspan="2">订货号</th><th rowspan="2">镜头<br>焦距</th><th>型号</th><th colspan="5">CV3 Pro-150M</th></tr><tr><th>工作距离(mm)</th><th>105</th><th>155</th><th>205</th><th>255</th><th>355</th></tr>
${cvRows('CV3 PRO-150M-06','6mm',[['62×86','94×125','124×166','154×205','213×285'],['0.06','0.09','0.12','0.14','0.20']])}
${cvRows('CV3 PRO-150M-08','8mm',[['49×65','72×96','96×126','117×156','162×217'],['0.05','0.07','0.09','0.11','0.15']])}
${cvRows('CV3 PRO-150M-12','12mm',[['31×42','48×64','64×84','78×104','110×145'],['0.03','0.04','0.06','0.07','0.10']])}
${cvRows('CV3 PRO-150M-16','16mm',[['22×29','33×45','45×60','57×75','80×106'],['0.02','0.03','0.04','0.05','0.07']])}
<tr><th rowspan="2">订货号</th><th rowspan="2">镜头<br>焦距</th><th>型号</th><th colspan="4">CV3 Pro-500M</th><th></th></tr><tr><th>工作距离(mm)</th><th>105</th><th>155</th><th>205</th><th>255</th><th></th></tr>
${cvRows('CV3 PRO-500M-06','6mm',[['94×124','136×180','180×240','224×298',''],['0.05','0.07','0.10','0.12','']])}
${cvRows('CV3 PRO-500M-12','12mm',[['46×60','68×95','90×120','112×149',''],['0.02','0.04','0.05','0.06','']])}
${cvRows('CV3 PRO-500M-16','16mm',[['31×40','49×64','66×87','82×108',''],['0.02','0.03','0.04','0.04','']])}
</tbody></table></div></section>`;

html=html.replace(/<div class="ocr-original-table">[\s\S]*?v3pro-fov\.jpg[\s\S]*?<\/div>/,v3);
html=html.replace(/<h3>CV3 Pro 检测范围<\/h3>\s*<div class="ocr-original-table">[\s\S]*?cv3-range\.jpg[\s\S]*?<\/div>/,cv3);
if(html.includes('v3pro-fov.jpg')||html.includes('cv3-range.jpg'))throw new Error('Original raster table still referenced');
fs.writeFileSync(file,html,'utf8');console.log('Rebuilt both smart-camera tables as exact HTML.');
