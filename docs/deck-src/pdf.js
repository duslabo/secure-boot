const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, colorScheme: 'light' });
  await p.goto('file://' + process.cwd() + '/out/tc4xx-secure-boot-deck.html');
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
  await p.pdf({ path: 'out/tc4xx-secure-boot-deck.pdf', width: '1280px', height: '720px', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
