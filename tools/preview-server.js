const http=require('http');
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const root=path.resolve(__dirname,'..');
const port=Number(process.argv[2]||8899);
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.gif':'image/gif','.webp':'image/webp','.avif':'image/avif','.ico':'image/x-icon','.mp4':'video/mp4','.svg':'image/svg+xml','.txt':'text/plain; charset=utf-8','.xml':'application/xml; charset=utf-8'};
const API='/api/messages';
const MAX_BODY=16*1024;
const POLICY_VERSION='1.0';
const RETENTION_MONTHS=24;
const RATE_MAX=8;                 // submissions per IP per window
const RATE_WINDOW=60*1000;
const ALLOWED_ORIGINS=new Set([
  'https://www.maibida.com','https://maibida.com',
  'http://127.0.0.1:'+port,'http://localhost:'+port
]);
// Personal data must not be reachable as a static asset: keep it outside root.
const messageDir=path.resolve(root,'..','maibida-ocr-rebuilt_messages');
const messageFile=path.join(messageDir,'messages.ndjson');

// Prelaunch remediation: security response headers. CSP allows inline
// script/style because this static site ships 1000+ legacy inline blocks;
// everything else is locked to same-origin with no third-party dependencies.
const CSP=[
  "default-src 'self'",
  "base-uri 'self'",
  "object-src 'none'",
  "frame-ancestors 'self'",
  "form-action 'self'",
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  "connect-src 'self'",
  "media-src 'self'",
  "worker-src 'self' blob:"
].join('; ');
const SECURITY_HEADERS={
  'Strict-Transport-Security':'max-age=31536000; includeSubDomains; preload',
  'Content-Security-Policy':CSP,
  'X-Frame-Options':'SAMEORIGIN',
  'X-Content-Type-Options':'nosniff',
  'Referrer-Policy':'strict-origin-when-cross-origin',
  'Permissions-Policy':'camera=(), microphone=(), geolocation=(), payment=(), usb=()',
  'Cross-Origin-Opener-Policy':'same-origin',
  'Cross-Origin-Resource-Policy':'same-origin'
};
function headers(extra){return Object.assign({},SECURITY_HEADERS,extra||{});}

// Never expose credentials, VCS metadata or the private message store.
const DENY=/(^|\/)\.(env|git|htpasswd|htaccess)(\/|$)|messages\.ndjson$|\.ndjson$/i;

// In-memory rate limiting; production should also enforce it at the edge.
const rateMap=new Map();
function rateOk(ip){
  const now=Date.now();
  let hits=(rateMap.get(ip)||[]).filter(t=>now-t<RATE_WINDOW);
  if(hits.length>=RATE_MAX){rateMap.set(ip,hits);return false;}
  hits.push(now);rateMap.set(ip,hits);
  if(rateMap.size>2000){
    for(const [k,v] of rateMap) if(!v.length||now-v[v.length-1]>=RATE_WINDOW) rateMap.delete(k);
  }
  return true;
}
function clientIp(req){
  const xf=String(req.headers['x-forwarded-for']||'').split(',')[0].trim();
  return xf||req.socket.remoteAddress||'unknown';
}
function ipHash(ip){
  return crypto.createHash('sha256').update(ip+'|maibida').digest('hex').slice(0,16);
}
function retentionUntil(iso){
  const d=new Date(iso);d.setMonth(d.getMonth()+RETENTION_MONTHS);
  return d.toISOString();
}

function sendJson(res,code,obj,extra){
  const b=Buffer.from(JSON.stringify(obj));
  res.writeHead(code,headers(Object.assign({
    'Content-Type':'application/json; charset=utf-8',
    'Content-Length':b.length,'Cache-Control':'no-store'
  },extra||{})));
  res.end(b);
}
function readBody(req){
  return new Promise((resolve,reject)=>{
    let size=0;const chunks=[];
    req.on('data',c=>{size+=c.length;if(size>MAX_BODY){reject(new Error('too_large'));req.destroy();}else chunks.push(c);});
    req.on('end',()=>resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error',reject);
  });
}
function parsePayload(contentType,raw){
  if(/^application\/json/i.test(contentType)) return JSON.parse(raw);
  if(/^application\/x-www-form-urlencoded/i.test(contentType))
    return Object.fromEntries(new URLSearchParams(raw));
  const e=new Error('unsupported_media_type');e.code=415;throw e;
}
function handleMessage(req,res){
  if(req.method!=='POST') return sendJson(res,405,{ok:false,error:'Method not allowed'});
  const origin=req.headers['origin'];
  if(origin&&!ALLOWED_ORIGINS.has(origin))
    return sendJson(res,403,{ok:false,error:'Cross-origin submissions are not allowed'});
  const ip=clientIp(req);
  if(!rateOk(ip))
    return sendJson(res,429,{ok:false,error:'Too many submissions, please try again later'},{'Retry-After':'60'});
  const ct=req.headers['content-type']||'';
  if(!/^(application\/json|application\/x-www-form-urlencoded)/i.test(ct))
    return sendJson(res,415,{ok:false,error:'Expected application/json'});
  readBody(req).then(raw=>{
    let d;try{d=parsePayload(ct,raw);}catch(e){
      return sendJson(res,e.code===415?415:400,{ok:false,error:e.code===415?'Unsupported media type':'Invalid JSON'});
    }
    // Honeypot: the hidden "website" field is never filled by a human.
    // Reply success but do not persist, so bots cannot probe the validation.
    if(typeof d.website==='string'&&d.website.trim())
      return sendJson(res,200,{ok:true,id:'ignored'});
    if(String(d.consent||'').toLowerCase()!=='yes')
      return sendJson(res,400,{ok:false,error:'Privacy consent is required'});
    const s=(v,max)=>typeof v==='string'?v.trim().slice(0,max):'';
    const receivedAt=new Date().toISOString();
    const rec={
      id:Date.now().toString(36)+'-'+crypto.randomBytes(4).toString('hex'),
      receivedAt:receivedAt,
      name:s(d.name,100),email:s(d.email,200),phone:s(d.phone,50),
      company:s(d.company,200),country:s(d.country,100),message:s(d.message,4000),
      lang:s(d.lang,10),source:s(d.source,200),
      consent:'yes',consentVersion:s(d.consentVersion,20)||POLICY_VERSION,
      policyVersion:POLICY_VERSION,
      retentionUntil:retentionUntil(receivedAt),
      ipHash:ipHash(ip)
    };
    if(!rec.name||!rec.message||!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(rec.email))
      return sendJson(res,400,{ok:false,error:'Missing or invalid fields'});
    fs.mkdirSync(messageDir,{recursive:true});
    fs.appendFileSync(messageFile,JSON.stringify(rec)+'\n','utf8');
    try{fs.chmodSync(messageFile,0o600);}catch(_){/* Windows ACLs handled by deployment */}
    sendJson(res,200,{ok:true,id:rec.id});
  }).catch(err=>{
    if(!res.headersSent){
      const tooLarge=err&&err.message==='too_large';
      sendJson(res,tooLarge?413:500,{ok:false,error:tooLarge?'Payload too large':'Server error'});
    }
  });
}

http.createServer((req,res)=>{
  const pathname=decodeURIComponent((req.url||'/').split('?')[0]);
  if(pathname===API) return handleMessage(req,res);
  if(DENY.test(pathname)){res.writeHead(403,headers());return res.end('Forbidden');}
  const target=path.resolve(root,'.'+pathname);
  if(!target.startsWith(root+path.sep)&&target!==root){res.writeHead(403,headers());return res.end('Forbidden');}
  let file=target;
  let st;
  try{st=fs.statSync(file);if(st.isDirectory())file=path.join(file,'index.html');}
  catch{res.writeHead(404,headers());return res.end('Not found');}
  try{st=fs.statSync(file);}catch{res.writeHead(404,headers());return res.end('Not found');}

  // Content negotiation: serve the WebP sibling when the client supports it.
  // Original JPEG/PNG files stay untouched as the fallback.
  const accept=String(req.headers['accept']||'');
  let served=file;
  let negotiated=false;
  if(/\.(png|jpe?g)$/i.test(file)&&/image\/webp/i.test(accept)){
    const w=file+'.webp';
    if(fs.existsSync(w)){served=w;negotiated=true;}
  }
  const ext=path.extname(served).toLowerCase();
  const isAsset=!['.html','.xml','.txt','.json'].includes(ext);
  const cache=isAsset?'public, max-age=604800':'no-cache';
  const extra={
    'Content-Type':types[ext]||'application/octet-stream',
    'Content-Length':fs.statSync(served).size,
    'Cache-Control':cache,
    'Last-Modified':fs.statSync(served).mtime.toUTCString()
  };
  if(negotiated) extra['Vary']='Accept';
  res.writeHead(200,headers(extra));
  if(req.method==='HEAD') return res.end();
  fs.createReadStream(served).on('error',()=>res.end()).pipe(res);
}).listen(port,'127.0.0.1',()=>console.log(`Preview: http://127.0.0.1:${port}/index.html`));
