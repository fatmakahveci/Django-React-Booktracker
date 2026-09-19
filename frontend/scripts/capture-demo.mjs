import { chromium } from '@playwright/test';
import { mkdir } from 'node:fs/promises';
const base = process.env.DEMO_URL || 'http://localhost:8080';
if (!process.env.BOOKTRACKER_DEMO_PASSWORD) throw new Error('Set the synthetic demo password.');
const directory = new URL('../../docs/demo/', import.meta.url).pathname;
await mkdir(directory, { recursive:true });
const browser = await chromium.launch();
try {
  const context = await browser.newContext({ viewport:{ width:1280, height:920 } });
  const page = await context.newPage();
  const issues=[]; page.on('pageerror', error=>issues.push(error.message));
  await page.goto(base); await page.screenshot({ path:`${directory}landing.png` });
  await page.goto(`${base}/login`); await page.getByLabel('Email address').fill('demo@example.invalid'); await page.getByLabel('Password',{exact:true}).fill(process.env.BOOKTRACKER_DEMO_PASSWORD); await page.getByRole('button',{name:'Sign in',exact:true}).click(); await page.getByRole('heading',{name:'Your library.'}).waitFor(); await page.getByRole('heading',{name:'Piranesi',exact:true}).waitFor();
  await page.screenshot({ path:`${directory}bookshelf.png`,fullPage:true }); await page.screenshot({path:`${directory}frame-1.png`});
  await page.getByRole('button',{name:'Finished',exact:true}).click(); await page.getByRole('heading',{name:'Piranesi',exact:true}).waitFor(); await page.waitForTimeout(350); await page.screenshot({path:`${directory}frame-2.png`});
  await page.getByRole('button',{name:'Add a book',exact:true}).click(); await page.getByRole('dialog').getByLabel('Title',{exact:true}).fill('The next good read'); await page.getByRole('dialog').getByLabel('Author',{exact:true}).fill('An author to discover'); await page.screenshot({path:`${directory}frame-3.png`}); await page.keyboard.press('Escape');
  await page.getByRole('link',{name:'Account',exact:true}).click(); await page.getByRole('heading',{name:'Account & security.'}).waitFor(); await page.screenshot({path:`${directory}frame-4.png`});
  await page.setViewportSize({width:390,height:844}); await page.goto(`${base}/library`); await page.getByRole('heading',{name:'Piranesi',exact:true}).waitFor(); await page.screenshot({path:`${directory}mobile.png`,fullPage:true});
  await page.goto(`${base}/api/docs/`); await page.getByRole('heading',{name:/Booktracker API/}).waitFor(); const responses=await page.locator('.opblock').count();
  console.log(JSON.stringify({ screenshots:directory, javascriptErrors:issues, documentedOperations:responses }));
} finally { await browser.close(); }
