const {chromium} = require(process.env.QA_NODE_MODULES+'/playwright');
const fs = require('fs');
(async()=>{
 const browser = await chromium.launch({executablePath:process.env.CHROME_PATH,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page = await browser.newPage({viewport:{width:390,height:844},isMobile:true,deviceScaleFactor:1});
 const base='http://127.0.0.1:8765/russian-rustbook/';
 const errors=[],failed=[],overflow=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()})});
 page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure().errorText}));
 page.setDefaultTimeout(15000);
 const urls=[...fs.readFileSync('book/sitemap.xml','utf8').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>m[1].replace('https://waikizashi.github.io/russian-rustbook/',base));
 for(const url of urls){await page.goto(url,{waitUntil:'load'});const size=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));if(size.scroll>size.width+1)overflow.push({url,...size});}
 await page.goto(base,{waitUntil:'networkidle'});
 await page.screenshot({path:'dist/mobile-home.png',fullPage:true});
 await page.locator('#mdbook-search-toggle').click();
 const input=page.locator('#mdbook-searchbar');await input.fill('владение');
 await page.locator('#mdbook-searchresults a').first().waitFor();
 const mainSearch=await page.locator('#mdbook-searchresults a').count();
 await input.press('Escape');
 await page.locator('#mdbook-theme-toggle').click();
 await page.getByRole('menuitem',{name:'Navy',exact:true}).click();
 const darkTheme=await page.locator('html').getAttribute('class');
 await page.locator('#mdbook-theme-toggle').click();
 await page.getByRole('menuitem',{name:'Light',exact:true}).click();
 const github=await page.locator('a[href="https://github.com/Waikizashi/russian-rustbook"]').count();
 const edit=await page.locator('a[href$="/edit/main/src/title-page.md"]').count();
 await page.locator('a.mobile-nav-chapters.next').click();
 const navigation=page.url().endsWith('/foreword.html');
 await page.goto(base+'extras/bits-bytes/',{waitUntil:'networkidle'});
 await page.locator('#mdbook-search-toggle').click();await input.fill('байты');
 await page.locator('#mdbook-searchresults a').first().waitFor();
 const extraSearch=await page.locator('#mdbook-searchresults a').count();
 for (const width of [320,768]) {
  await page.setViewportSize({width,height:900});
  for (const path of ['ch08-02-strings.html','appendix-02-operators.html','extras/bits-bytes/07-parser.html']) {
   await page.goto(base+path,{waitUntil:'load'});
   const size=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
   if(size.scroll>size.width+1)overflow.push({url:page.url(),...size});
  }
 }
 await page.setViewportSize({width:1440,height:900});
 await page.goto(base+'ch04-02-references-and-borrowing.html',{waitUntil:'networkidle'});
 await page.screenshot({path:'dist/desktop-borrowing.png',fullPage:false});
 await page.keyboard.press('Tab');
 const keyboardFocus=await page.evaluate(()=>document.activeElement.tagName);
 const report={keyboardFocus,pages:urls.length,mobileViewport:390,overflow,errors,failed,mainSearch,extraSearch,darkTheme,github,edit,navigation};
 fs.writeFileSync('dist/browser-verification.json',JSON.stringify(report,null,2)+'\n'); console.log(report);
 await browser.close(); if(!darkTheme.includes('navy')||errors.length||failed.length||overflow.length||!navigation||!mainSearch||!extraSearch||!github||!edit)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
