import puppeteer from 'puppeteer';
import { resolve } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

const browser = await puppeteer.launch({
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});

const page = await browser.newPage();
await page.setViewport({ width: 1080, height: 1080, deviceScaleFactor: 1 });

const file = resolve(__dirname, 'post-imoveis-populares.html');
await page.goto(`file://${file}`, { waitUntil: 'networkidle0', timeout: 15000 });

// wait for fonts
await new Promise(r => setTimeout(r, 2000));

await page.screenshot({
  path: resolve(__dirname, 'post-imoveis-populares.png'),
  clip: { x: 0, y: 0, width: 1080, height: 1080 }
});

await browser.close();
console.log('done');
