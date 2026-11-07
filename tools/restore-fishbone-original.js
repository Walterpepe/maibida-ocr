const fs=require('fs');const path=require('path');
const file=path.resolve(__dirname,'..','product','10032.html');
let html=fs.readFileSync(file,'utf8');
const original='<img alt="集中监控系统集中监控系统可实现模具监视器数据的集中采集及大数据看板功能，对模具监视器数据进行实时监控，并通过集中监控程序对接客户mes系统。" src="../cn/testimg/mjbh2.jpg"/>';
const re=/<div class="fishbone-restored">[\s\S]*?<\/section><\/div>/;
if(!re.test(html))throw new Error('Restored fishbone block not found');
html=html.replace(re,original);
fs.writeFileSync(file,html,'utf8');console.log('Fishbone section returned to original image-only state.');
