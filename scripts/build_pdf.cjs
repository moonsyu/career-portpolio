// The deployed HTML and its images are the only portfolio content source.
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const {execFileSync} = require('node:child_process');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const output = path.resolve(process.env.PDF_OUTPUT || path.join(root, 'output/pdf/Jang-MoonSu-Career.pdf'));
const mime = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'};

async function build() {
  const server = http.createServer(async(req,res) => {
    try {
      const url = new URL(req.url, 'http://localhost');
      const target = path.resolve(root, '.' + (url.pathname === '/' ? '/index.html' : decodeURIComponent(url.pathname)));
      const relative = path.relative(root,target);
      if (relative.startsWith('..') || path.isAbsolute(relative)) {res.writeHead(403);res.end();return;}
      res.setHeader('Content-Type', mime[path.extname(target)] || 'application/octet-stream');
      res.end(await fs.readFile(target));
    } catch {res.writeHead(404);res.end();}
  });
  await new Promise(resolve => server.listen(0,'127.0.0.1',resolve));
  let browser;
  try {
    browser = await chromium.launch({headless:true,...(process.env.PDF_CHROMIUM_PATH ? {executablePath:process.env.PDF_CHROMIUM_PATH} : {})});
    const page = await browser.newPage({viewport:{width:1600,height:900},reducedMotion:'reduce'});
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    page.on('response',response=>{if(response.status()>=400)errors.push(`${response.status()} ${response.url()}`);});
    await page.goto(`http://127.0.0.1:${server.address().port}/`,{waitUntil:'networkidle'});
    const source = await page.evaluate(() => {
      const content = document.createElement('main');content.id='pdf-pages';
      const titles=[];
      function add(kind,title,nodes) {
        const slide=document.createElement('section');slide.className=`pdf-slide ${kind}`;
        const heading=document.createElement('header');heading.className='pdf-heading';
        heading.innerHTML='<span class="pdf-brand">Jang MoonSu / CAREER</span><span class="pdf-topic"></span>';
        heading.querySelector('.pdf-topic').textContent=title;
        const body=document.createElement('div');body.className='pdf-body';
        nodes.forEach(node=>{if(node)body.append(node.cloneNode(true));});
        slide.append(heading,body);content.append(slide);titles.push(title);
      }
      add('cover','경력기술서',[document.querySelector('.hero .container'),document.querySelector('.project-index')]);
      add('profile','소개 · 연락처',[document.querySelector('.about-grid'),document.querySelector('.contact-links')]);
      for(const project of document.querySelectorAll('article.project')) {
        const name=project.querySelector('h3').textContent.trim();
        add('overview',name,[project.querySelector('.project-heading'),project.querySelector('.project-overview')]);
        for(const section of project.querySelectorAll('.detail-body > section')) {
          const title=section.querySelector('h4')?.textContent.trim();
          if(!title)throw new Error('Every project section needs a PDF title');
          const kind=section.querySelector('.application-architecture')?'architecture':section.querySelector('.troubleshooting-grid')?'case':section.dataset.pageKind==='benchmark'?'benchmark':'implementation';
          add(kind,name+' / '+title,[section]);
        }
      }
      const count=content.children.length;
      [...content.children].forEach((slide,i)=>{
        const footer=document.createElement('footer');footer.className='pdf-footer';
        footer.innerHTML='<span>Jang MoonSu · 경력기술서</span><span>'+String(i+1).padStart(2,'0')+' / '+String(count).padStart(2,'0')+'</span>';
        slide.append(footer);
      });
      // Use the full desktop diagrams on the fixed-size slides.
      content.querySelectorAll('source,.hero-actions,.hero-bottom,.project-category,.visually-hidden').forEach(el=>el.remove());
      content.querySelectorAll('img').forEach(img=>{img.loading='eager';img.src=new URL(img.getAttribute('src'),location.href).href;});
      content.querySelectorAll('a').forEach(a=>{if(a.getAttribute('href')?.startsWith('#'))a.removeAttribute('href');});
      content.querySelectorAll('[id]').forEach(el=>{if(el!==content)el.removeAttribute('id');});
      document.querySelectorAll('link[rel="stylesheet"],style,script').forEach(el=>el.remove());
      document.body.replaceChildren(content);
      return {titles,count};
    });
    await page.addStyleTag({path:path.join(__dirname,'pdf-layout.css')});
    await page.emulateMedia({media:'print'});
    await page.evaluate(async()=>{
      await document.fonts.ready;
      await Promise.all([...document.images].map(img=>img.decode()));
    });
    const failures=await page.evaluate(()=>{
      const problems=[];
      for(const [i,slide] of [...document.querySelectorAll('.pdf-slide')].entries()) {
        const bounds=slide.querySelector('.pdf-body').getBoundingClientRect();
        for(const el of slide.querySelectorAll('.pdf-body img,.pdf-body h1,.pdf-body h3,.pdf-body h4,.pdf-body p,.pdf-body li,.pdf-body dt,.pdf-body dd')) {
          const r=el.getBoundingClientRect();
          if(r.width && r.height && (r.bottom>bounds.bottom+2||r.right>bounds.right+2||r.left<bounds.left-2||r.top<bounds.top-2))problems.push(`Page ${i+1}: overflow ${el.textContent?.slice(0,60)||el.getAttribute('src')}`);
          if(el.tagName==='IMG' && !el.naturalWidth)problems.push(`Page ${i+1}: missing image`);
        }
      }
      return problems;
    });
    if(errors.length||failures.length)throw new Error([...errors,...failures].join('\n'));
    await fs.mkdir(path.dirname(output),{recursive:true});
    await page.pdf({path:output,preferCSSPageSize:true,printBackground:true,tagged:true,outline:true});
    if(process.env.PDF_PREVIEW_DIR) {
      await fs.mkdir(process.env.PDF_PREVIEW_DIR,{recursive:true});
      for(let i=0;i<source.count;i++)await page.locator('.pdf-slide').nth(i).screenshot({path:path.join(process.env.PDF_PREVIEW_DIR,`slide-${String(i+1).padStart(2,'0')}.png`)});
    }
    const bytes=await fs.readFile(output);
    const metadata={sourceCommit:process.env.GITHUB_SHA||execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),workingTreeDirty:!process.env.GITHUB_SHA&&Boolean(execFileSync('git',['status','--porcelain'],{cwd:root,encoding:'utf8'}).trim()),htmlSha256:crypto.createHash('sha256').update(await fs.readFile(path.join(root,'index.html'))).digest('hex'),pdfSha256:crypto.createHash('sha256').update(bytes).digest('hex'),pageCount:source.count,titles:source.titles};
    await fs.writeFile(output.replace(/\.pdf$/i,'.json'),JSON.stringify(metadata,null,2)+'\n');
    console.log(JSON.stringify({output,pages:source.count,bytes:bytes.length,overflow:0}));
  } finally {if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
}
build().catch(error=>{console.error(error);process.exitCode=1;});
