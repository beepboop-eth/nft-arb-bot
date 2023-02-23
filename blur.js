const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    userDataDir: '/Users/janusmanlapaz/Library/Application Support/Google/Chrome/',
    args: [
      '--disable-features=IsolateOrigins,site-per-process',
      // `--profile-directory=Profile 12`,
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage'
    ],
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  });

  const page = await browser.newPage();
  const url = 'https://core-api.prod.blur.io/v1/collections/boredapeyachtclub/executable-bids?filters=%7B%7D';
  await page.goto(url);

  const data = await page.content();
  fs.writeFileSync('data.json', data);

  await browser.close();
})();