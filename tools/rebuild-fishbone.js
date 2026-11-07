const fs=require('fs');const path=require('path');
const file=path.resolve(__dirname,'..','product','10032.html');
let html=fs.readFileSync(file,'utf8');
const items=[
 ['01','合模前进行模穴、模芯、产品残留确认'],
 ['02','滑块位置、顶针折断和复位位置确认'],
 ['03','镶件是否到位和遗漏检测'],
 ['04','产品是否完全脱模、产品是否缺料检测'],
 ['05','产品尺寸是否合格、产品毛边检测'],
 ['06','多穴产品是否缺失和残留检测'],
 ['07','多色产品混色是否正确检测'],
 ['08','安全门开关消除报警、安全门动作自动复检'],
 ['09','减少脱模剂使用，适用于脱模困难的产品'],
 ['10','减少顶针顶出次数，提升注塑成型周期，提高生产效率']
];
const card=(x,place)=>`<div class="fish-card fish-${place}"><p>${x[1]}</p><span>${x[0]}</span></div>`;
const fish=`<section class="fishbone" aria-labelledby="fishbone-title"><h3 id="fishbone-title">模具监视保护器</h3><div class="fishbone-core"><div class="fish-grid fish-top">${items.slice(0,5).map(x=>card(x,'top')).join('')}</div><div class="fish-spine"><div class="fish-arrow a1"></div><div class="fish-arrow a2"></div><div class="fish-arrow a3"><strong>检测内容</strong></div><div class="fish-arrow a4"></div></div><div class="fish-grid fish-bottom">${items.slice(5).map(x=>card(x,'bottom')).join('')}</div></div><div class="fish-result">降低生产成本<br>提高生产效率</div></section>`;
const re=/<img[^>]+src="\.\.\/cn\/testimg\/mjbh2\.jpg"[^>]*\/>/i;
if(!re.test(html))throw new Error('Fishbone image not found');
html=html.replace(re,fish);
if(html.includes('cn/testimg/mjbh2.jpg'))throw new Error('Fishbone raster reference remains');
fs.writeFileSync(file,html,'utf8');console.log('Fishbone rebuilt as HTML/CSS.');
