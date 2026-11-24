// Render a web page with headless Chromium and print visible text. Usage: node render_page.js URL [waitms]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36' });
  try {
    await p.goto(process.argv[2], { waitUntil: 'domcontentloaded', timeout: 60000 });
    await p.waitForTimeout(parseInt(process.argv[3] || '6000'));
    console.log(await p.innerText('body'));
  } catch (e) { console.log('ERROR', e.message); }
  await b.close();
})();
