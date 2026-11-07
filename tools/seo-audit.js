const fs=require('fs');const path=require('path');
const root=path.resolve(__dirname,'..');
const pages=['index.html','product/10032.html','product/smart-camera.html','productlist/10029.html','productlist/10030.html','productlist/10034.html','productlist/10036.html','productlist/10039.html'];
const grab=(s,re)=>(s.match(re)||[])[1]?.replace(/\s+/g,' ').trim()||'';
const strip=s=>s.replace(/<!--[\s\S]*?-->/g,'').replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<[^>]+>/g,' ').replace(/&\w+;|&#\d+;/g,' ').replace(/\s+/g,' ').trim();
const titles=new Map(),descs=new Map();let broken=0;
for(const page of pages){const abs=path.join(root,page),raw=fs.readFileSync(abs,'utf8'),html=raw.replace(/<!--[\s\S]*?-->/g,'');
 const title=grab(html,/<title[^>]*>([\s\S]*?)<\/title>/i),desc=grab(html,/<meta[^>]+name=["']description["'][^>]+content=["']([^"']*)/i)||grab(html,/<meta[^>]+content=["']([^"']*)["'][^>]+name=["']description["']/i),canonical=grab(html,/<link[^>]+rel=["']canonical["'][^>]+href=["']([^"']*)/i)||grab(html,/<link[^>]+href=["']([^"']*)["'][^>]+rel=["']canonical["']/i);
 const h1=(html.match(/<h1\b/gi)||[]).length,imgs=[...html.matchAll(/<img\b[^>]*>/gi)].map(x=>x[0]),missingAlt=imgs.filter(x=>!(/\balt\s*=\s*["'][^"']+["']/i.test(x))).length;
 const json=[...html.matchAll(/<script[^>]+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)];let jsonBad=0;for(const x of json){try{JSON.parse(x[1])}catch{jsonBad++}}
 let localBroken=0;for(const m of html.matchAll(/(?:href|src)=["']([^"'#?]+)["']/gi)){const ref=m[1];if(/^(?:https?:|mailto:|tel:|javascript:|data:|\/\/)/i.test(ref)||ref.endsWith('.aspx'))continue;const target=path.resolve(path.dirname(abs),ref.replace(/\//g,path.sep));if(!fs.existsSync(target)){localBroken++;broken++;}}
 const words=strip(html).replace(/[^\u4e00-\u9fffA-Za-z0-9]+/g,'').length;
 if(!titles.has(title))titles.set(title,[]);titles.get(title).push(page);if(!descs.has(desc))descs.set(desc,[]);descs.get(desc).push(page);
 console.log(JSON.stringify({page,title,titleChars:title.length,descriptionChars:desc.length,canonical,h1,images:imgs.length,missingAlt,jsonLd:json.length,jsonLdInvalid:jsonBad,localBroken,textChars:words}));
}
console.log('DUPLICATE_TITLES',JSON.stringify([...titles].filter(([,v])=>v.length>1)));
console.log('DUPLICATE_DESCRIPTIONS',JSON.stringify([...descs].filter(([,v])=>v.length>1)));
console.log('BROKEN_TOTAL',broken);
