const {chromium} = require('playwright');
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const {spawn} = require('child_process');
const server = spawn('python3', ['-m','http.server','8765','--bind','127.0.0.1'], {cwd:root, stdio:'ignore'});
server.unref();
process.on('exit',()=>server.kill());
(async () => {
  for(let attempt=0;attempt<40;attempt++) {
    try { const response=await fetch('http://127.0.0.1:8765/index.html'); if(response.ok)break; } catch(_) {}
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  const manifest = JSON.parse(fs.readFileSync(root + '/archive-manifest.json'));
  const browser = await chromium.launch({headless:true, args:['--no-sandbox']});
  const rows = [], errors = [];
  const numbered = (process.argv.includes('--editorial') ? Array.from({length:10}, (_,i)=>i+51) : [1,3,7,13,14,16,19,24,27,32,33,38,42,201,215,250,417,1000]).map(n=>manifest.entries[n-1]);
  const seen = new Set();
  const honorable = manifest.honorable_mentions.filter(r=>{if(seen.has(r.category))return false;seen.add(r.category);return true});
  for (const viewport of [{width:1440,height:1000},{width:390,height:844}]) {
    const context = await browser.newContext({viewport});
    await context.route('**/*', async route=>{
      const url = route.request().url();
      if (url.startsWith('http://127.0.0.1:8765/'))return route.continue();
      if (route.request().resourceType()==='image') return route.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>'});
      return route.fulfill({contentType:'application/json',body:'{"data":[]}'});
    });
    const page = await context.newPage();
    page.on('pageerror', e=>errors.push(e.message));
    for (const r of [...numbered,...honorable]) {
      await page.goto('http://127.0.0.1:8765/'+r.file,{waitUntil:'domcontentloaded'});
      const title = await page.locator('h1').textContent();
      const overflow = await page.evaluate(()=>document.documentElement.scrollWidth > innerWidth + 1);
      const returnHref = await page.locator('a.archive-link').getAttribute('href');
      const vignettes = await page.locator('#opening > .play-vignette').count();
      if(overflow) errors.push(r.file+' horizontal overflow at '+viewport.width);
      if(returnHref!==r.landing_return_href)errors.push(r.file+' incorrect return href');
      if(process.argv.includes('--editorial') && numbered.includes(r) && vignettes!==1)errors.push(r.file+' missing story');
      await page.locator('a.archive-link').click();
      await page.waitForURL('**/index.html?focus='+r.landing_anchor+'#'+r.landing_anchor);
      const row = page.locator('#'+r.landing_anchor);
      if(!(await row.isVisible()))errors.push(r.file+' hidden landing row');
      const box = await row.boundingBox();
      if(!box || box.y< -2 || box.y>viewport.height)errors.push(r.file+' unfocused landing row');
      rows.push({file:r.file,width:viewport.width,title,returnHref,landingVisible:await row.isVisible(),vignettes});
    }
    await context.close();
  }
  await browser.close();
  const report={status:errors.length?'FAIL':'PASS',externalMedia:'Offline placeholders; live image delivery was not tested.',visits:rows.length*2,articles:rows.length,errors,rows};
  const out=root+(process.argv.includes('--editorial')?'/audit/reader-v31-051-060/browser.json':'/audit/github-migration/browser.json');
  fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({status:report.status,visits:report.visits,articles:report.articles,errors},null,2));
  server.kill();
  process.exitCode=errors.length?1:0;
})().catch(e=>{console.error(e);server.kill();process.exit(1)});

