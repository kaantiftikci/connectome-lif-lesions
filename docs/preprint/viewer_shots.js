const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const dir = '/home/user/sinek/viewer';
const srv = http.createServer((req, res) => {
  const p = path.join(dir, req.url === '/' ? 'index.html' : req.url.split('?')[0]);
  fs.readFile(p, (e, b) => { if (e) { res.writeHead(404); return res.end(); } res.writeHead(200, {'Content-Type': p.endsWith('.json') ? 'application/json' : 'text/html'}); res.end(b); });
}).listen(8765);
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 }, deviceScaleFactor: 2 });
  page.on('console', m => console.log('console:', m.text()));
  await page.goto('http://127.0.0.1:8765/', { waitUntil: 'load' });
  await page.waitForSelector('#status', { state: 'hidden', timeout: 120000 });
  await page.addStyleTag({ content: '.hud, #bar, #legend { display: none !important; }' });
  await page.evaluate(() => { const c = document.getElementById('gl'); for (let i = 0; i < 3; i++) c.dispatchEvent(new WheelEvent('wheel', { deltaY: -100, bubbles: true, cancelable: true })); });
  for (const [idx, name] of [[0, 'sparse'], [1, 'attractor']]) {
    await page.evaluate(i => document.querySelectorAll('#regime button')[i].click(), idx);
    await page.waitForTimeout(3000);
    await page.waitForSelector('#status', { state: 'hidden', timeout: 120000 });
    for (const [run, label] of [[0, 'intact'], [1, 'ppl1']]) {
      await page.evaluate(i => document.querySelectorAll('#runs button')[i].click(), run);
      await page.evaluate(() => { const t = document.getElementById('t'); t.value = 60; t.dispatchEvent(new Event('input')); });
      await page.waitForTimeout(1500);
      const txt = await page.evaluate(() => [document.getElementById('tms').textContent, document.getElementById('nact').textContent, document.getElementById('ncum').textContent]);
      console.log(name, label, txt);
      await page.locator('#gl').screenshot({ path: `${process.argv[2]}/view_${name}_${label}.png`, clip: { x: 100, y: 100, width: 1200, height: 800 } });
    }
  }
  await browser.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
