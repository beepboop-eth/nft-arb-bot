const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    userDataDir: '/Users/janusmanlapaz/Library/Application Support/Google/Chrome/',
    args: [
      '--disable-features=IsolateOrigins,site-per-process',
      // `--profile-directory=Profile 12`,
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage'
    ],
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  }).catch((err) => {
    console.log('err', err)
  });

  const page = await browser.newPage();

  const url = 'https://core-api.prod.blur.io/v1/collections/boredapeyachtclub/executable-bids?filters=%7B%7D';
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
  await page.goto(url);

  // Get the JSON data from the page content
  const jsonData = await page.evaluate(() => {
    const pre = document.querySelector('pre');
    if (pre) {
      return JSON.parse(pre.textContent);
    }
    return null;
  });

  if (jsonData) {
    // Save the data to a file
    fs.writeFileSync('data.json', JSON.stringify(jsonData));
    console.log('Data saved to data.json');
  } else {
    console.log('JSON data not found in the page content.');
  }

  await browser.close();
})();