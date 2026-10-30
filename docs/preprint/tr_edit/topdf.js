const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(`file://${process.argv[2]}/out.html`, { waitUntil: 'load' });
  await page.waitForTimeout(500);
  await page.pdf({ path: `${process.argv[2]}/out.pdf`, format: 'A4', printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
    headerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:right;padding-right:20mm;font-family:serif">Konnektomla Sınırlandırılmış <i>Drosophila</i> Beyin Modelleri</div>',
    footerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;font-family:serif"><span class="pageNumber"></span></div>' });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
