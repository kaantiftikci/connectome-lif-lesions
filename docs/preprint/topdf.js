const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  for (const [name, lang] of [['en','en'], ['tr','tr']]) {
    const page = await browser.newPage();
    await page.goto(`file://${process.argv[2]}/${name}.html`, { waitUntil: 'load' });
    await page.evaluate(l => document.documentElement.lang = l, lang);
    await page.waitForTimeout(500);
    await page.pdf({ path: `${process.argv[2]}/${name}.pdf`, format: 'A4', printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
      headerTemplate: '<div></div>',
      footerTemplate: `<div style="font-size:8px;color:#666;width:100%;text-align:center;font-family:serif">${name==='en' ? 'Tiftikçi (2026) · preprint · doi:10.5281/zenodo.23808330' : 'Tiftikçi (2026) · önbaskı · doi:10.5281/zenodo.23808330'} · <span class="pageNumber"></span> / <span class="totalPages"></span></div>` });
    await page.close();
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
