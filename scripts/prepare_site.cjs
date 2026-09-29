const fs=require('node:fs/promises'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
(async()=>{
  const output=path.join(root,'_site');
  await fs.mkdir(output,{recursive:true});
  for(const name of ['assets','output/pdf','styles.css','app.js'])await fs.cp(path.join(root,name),path.join(output,name),{recursive:true});
  const metadata=JSON.parse(await fs.readFile(path.join(root,'output/pdf/Jang-MoonSu-Career.json'),'utf8'));
  let html=await fs.readFile(path.join(root,'index.html'),'utf8');
  // A deployment-specific URL prevents an old browser-cached PDF after an update.
  html=html.replace(/Jang-MoonSu-Career\.pdf(?:\?[^"\s]*)?/g,'Jang-MoonSu-Career.pdf?v='+metadata.pdfSha256.slice(0,16));
  const resources=[...html.matchAll(/(?:src|srcset|href)="(\.\/[^"?#]+)(?:\?[^"#]*)?"/g)];
  for(const match of resources) {
    if(!/\.(css|js|svg|png|webp|jpg)$/.test(match[1]))continue;
    const digest=crypto.createHash('sha256').update(await fs.readFile(path.join(root,match[1]))).digest('hex').slice(0,16);
    html=html.replace(match[0],match[0].split('=')[0]+'="'+match[1]+'?v='+digest+'"');
  }
  await fs.writeFile(path.join(output,'index.html'),html);
  metadata.deployedHtmlSha256=crypto.createHash('sha256').update(html).digest('hex');
  await fs.writeFile(path.join(output,'output/pdf/Jang-MoonSu-Career.json'),JSON.stringify(metadata,null,2)+'\n');
  await fs.writeFile(path.join(output,'.nojekyll'),'');
  console.log('Website and generated PDF staged together.');
})().catch(error=>{console.error(error);process.exitCode=1;});
