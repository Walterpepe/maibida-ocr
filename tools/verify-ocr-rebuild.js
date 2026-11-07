const fs=require('fs');const path=require('path');const root=path.resolve(__dirname,'..');
const pages=['index.html','product/10032.html','product/10032.en-US.html','product/10032.en-SG.html','product/10032.en-AU.html','product/smart-camera.html','productlist/10029.html','productlist/10030.html','productlist/10034.html','productlist/10036.html','productlist/10039.html'];
const removed=['6389629582092201704208292.jpg','6389953424155226788430313.jpg','6389953465917435748749439.jpg','6390277860987534319894448.png','mjbh5.jpg','6389742973523664431139609.png','mjbh6.jpg','6389743000645652104098007.png'];
const diagramPages=pages.filter(p=>p.startsWith('product/10032'));
let bad=0,tableCount=0,caseCount=0,diagramCount=0,specTableCount=0;
for(const page of pages){const abs=path.join(root,page);const html=fs.readFileSync(abs,'utf8');const activeHtml=html.replace(/<!--[\s\S]*?-->/g,'');tableCount+=(html.match(/class="ocr-table"/g)||[]).length;caseCount+=(html.match(/class="ocr-case-title"/g)||[]).length;
 for(const m of activeHtml.matchAll(/(?:src|href)="([^"#?]+)"/g)){const ref=m[1];if(/^(?:https?:|javascript:|mailto:|tel:|data:|\/\/)/i.test(ref)||ref.endsWith('.html')||ref.endsWith('.aspx'))continue;const target=path.resolve(path.dirname(abs),ref.replace(/\//g,path.sep));if(!fs.existsSync(target)){console.log('BROKEN',page,ref);bad++;}}
}
for(const name of removed){for(const page of pages){if(fs.readFileSync(path.join(root,page),'utf8').includes(name)){console.log('OLD_RASTER_TEXT_REMAINS',page,name);bad++;}}}
for(const page of diagramPages){const html=fs.readFileSync(path.join(root,page),'utf8');const diagrams=(html.match(/class="ocr-diagram/g)||[]).length;diagramCount+=diagrams;if(diagrams!==3){console.log('OCR_DIAGRAM_COUNT',page,diagrams);bad++;}if(!html.includes('cn/css/ocr-diagrams.css')){console.log('OCR_DIAGRAM_CSS_MISSING',page);bad++;}
 const specs=(html.match(/class="ocr-spec-table/g)||[]).length;specTableCount+=specs;if(specs!==1){console.log('OCR_SPEC_TABLE_COUNT',page,specs);bad++;}if(!html.includes('cn/css/ocr-spec-table.css')){console.log('OCR_SPEC_CSS_MISSING',page);bad++;}const specBlock=(html.match(/<table class="ocr-spec-table[\s\S]*?<\/table>/)||[''])[0];const specRows=(specBlock.match(/<tr/g)||[]).length;if(specRows!==24){console.log('OCR_SPEC_ROWS_MISSING',page,specRows);bad++;}}
console.log(JSON.stringify({pages:pages.length,htmlTables:tableCount,selectableCaseTitles:caseCount,selectableDiagramSections:diagramCount,selectableSpecTables:specTableCount,errors:bad},null,2));
if(bad)process.exit(1);
