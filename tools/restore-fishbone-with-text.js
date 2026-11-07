const fs=require('fs');const path=require('path');
const file=path.resolve(__dirname,'..','product','10032.html');
let html=fs.readFileSync(file,'utf8');
const replacement=`<div class="fishbone-restored"><img alt="模具监视保护器检测内容鱼骨图" src="../cn/testimg/mjbh2.jpg"/><section class="fishbone-transcript" aria-labelledby="fishbone-text-title"><h3 id="fishbone-text-title">模具监视保护器检测内容</h3><ol><li>合模前进行模穴、模芯、产品残留确认</li><li>滑块位置、顶针折断和复位位置确认</li><li>镶件是否到位和遗漏检测</li><li>产品是否完全脱模、产品是否缺料检测</li><li>产品尺寸是否合格、产品毛边检测</li><li>多穴产品是否缺失和残留检测</li><li>多色产品混色是否正确检测</li><li>安全门开关消除报警、安全门动作自动复检</li><li>减少脱模剂使用，适用于脱模困难的产品</li><li>减少顶针顶出次数，提升注塑成型周期，提高生产效率</li></ol><p><strong>作用：</strong>降低生产成本，提高生产效率。</p></section></div>`;
const re=/<section class="fishbone"[\s\S]*?<\/section>/;
if(!re.test(html))throw new Error('Rebuilt fishbone section not found');
html=html.replace(re,replacement);
fs.writeFileSync(file,html,'utf8');console.log('Original fishbone restored with plain-text transcript.');
