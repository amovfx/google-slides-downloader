const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs').promises;

async function captureScreenshot() {
  console.log('Launching browser...');
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  console.log('Navigating to http://localhost:3000...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle0' });

  console.log('Capturing screenshot...');
  const screenshot = await page.screenshot({ fullPage: true });

  await browser.close();

  const fileName = `screenshot-${Date.now()}.png`;
  const filePath = path.join(__dirname, 'screenshots', fileName);

  console.log('Saving screenshot...');
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, screenshot);

  console.log(`Screenshot saved: ${filePath}`);
}

captureScreenshot().catch(console.error);