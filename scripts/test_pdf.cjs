const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs/promises'),path=require('node:path'),os=require('node:os');
const {spawnSync}=require('node:child_process');
const http=require('node:http');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
test('PDF follows HTML edits, rejects missing images, and rejects overflowing copy',async()=>{
  const fixture=await fs.mkdtemp(path.join(os.tmpdir(),'career-pdf-test-'));
  try {
    for(const name of ['index.html','app.js','styles.css','assets','scripts'])await fs.cp(path.join(root,name),path.join(fixture,name),{recursive:true});
    const input=await fs.readFile(path.join(fixture,'index.html'),'utf8');
    const marker='HTML source synchronization check';
    let edited=input.replace('복호화된 요청의 XSS 필터 적용과 결과 전달</h4>',marker+'</h4>');
    assert.notEqual(edited,input);
    const env={...process.env,GITHUB_SHA:'test-fixture',PDF_OUTPUT:path.join(fixture,'career.pdf'),NODE_PATH:[path.join(root,'node_modules'),process.env.NODE_PATH].filter(Boolean).join(path.delimiter)};
    delete env.PDF_PREVIEW_DIR;
    const run=()=>spawnSync(process.execPath,[path.join(fixture,'scripts/build_pdf.cjs')],{env,encoding:'utf8',timeout:90000});
    await fs.writeFile(path.join(fixture,'index.html'),edited);
    const good=run();assert.equal(good.status,0,good.stderr);
    const metadata=JSON.parse(await fs.readFile(path.join(fixture,'career.json'),'utf8'));
    assert(metadata.titles.some(title=>title.includes(marker)));
    assert.equal((await fs.readFile(path.join(fixture,'career.pdf'))).subarray(0,5).toString(),'%PDF-');
    await fs.writeFile(path.join(fixture,'index.html'),edited.replace('assets/architecture/wallet-xss-flow.svg','assets/architecture/missing-test.svg'));
    const missing=run();assert.notEqual(missing.status,0,'Missing diagram must block publishing');
    await fs.writeFile(path.join(fixture,'index.html'),edited.replace(marker,Array(110).fill('Overflow test').join(' ')));
    const overflow=run();assert.notEqual(overflow.status,0,'Overflow must block publishing');
    assert.match(overflow.stderr,/overflow/);
  } finally {
    if(path.dirname(fixture)===path.resolve(os.tmpdir())&&path.basename(fixture).startsWith('career-pdf-test-'))await fs.rm(fixture,{recursive:true,force:true});
  }
});

test('an already-open page downloads the current PDF after deployment',async()=>{
  const original=await fs.readFile(path.join(root,'output/pdf/Jang-MoonSu-Career.pdf'));
  let revision=1;const requests=[];
  const server=http.createServer(async(req,res)=>{
    try {
      const url=new URL(req.url,'http://localhost');
      if(url.pathname.endsWith('.pdf')) {
        requests.push(req.headers['cache-control']);
        res.writeHead(200,{'Content-Type':'application/pdf','Cache-Control':'public, max-age=3600'});
        res.end(Buffer.concat([original,Buffer.from(`\n% deployment ${revision}\n`)]));return;
      }
      const target=path.resolve(root,'.'+(url.pathname==='/'?'/index.html':url.pathname));
      const relative=path.relative(root,target);
      if(relative.startsWith('..')||path.isAbsolute(relative)){res.writeHead(403);res.end();return;}
      const types={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.webp':'image/webp'};
      res.setHeader('Content-Type',types[path.extname(target)]||'application/octet-stream');res.end(await fs.readFile(target));
    }catch{res.writeHead(404);res.end();}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  let browser;
  try {
    browser=await chromium.launch({headless:true,...(process.env.PDF_CHROMIUM_PATH?{executablePath:process.env.PDF_CHROMIUM_PATH}:{})});
    const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/`);
    for(revision=1;revision<=2;revision++) {
      const downloading=page.waitForEvent('download');await page.locator('.button-pdf').click();
      const download=await downloading;assert.equal(download.suggestedFilename(),'Jang-MoonSu-Career.pdf');
      const received=await fs.readFile(await download.path());assert(received.toString('latin1').endsWith(`% deployment ${revision}\n`));
    }
    assert.equal(requests.length,2,'Both clicks must reach the server');
    assert(requests.every(value=>/no-cache|no-store/.test(value)));
  } finally {if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
});
