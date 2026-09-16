// Docs screenshot harness. Usage:
//   SESSION_ID=... node capture.js <plan.json> <outDir>
// plan.json = [{ name, url, clicks?: [text|{selector}|{text,nth}], waitFor?: text, scrollTo?: text, fullPage?, clip?, delay? }]
const { chromium } = require('/Users/nitesh.saini/offload-cspm/frontend/node_modules/playwright');
const fs = require('fs'); const path = require('path');

const BASE = process.env.BASE_URL || 'http://localhost:3001';
const [,, planFile, outDir] = process.argv;
const plan = JSON.parse(fs.readFileSync(planFile, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });

const user = {"user_id":"b54cf4e7-3434-4ab4-aa74-632f23b92a2b","email":"admin@offloadsecurity.com","name":"Admin User","role":"admin","team_ids":["default-team"],"current_team_id":"default-team","status":"active","permissions":[],"is_platform_admin":true};

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, colorScheme: 'light' });
  await ctx.addInitScript(({ sid, user }) => {
    if (!localStorage.getItem('sessionId')) {
      localStorage.setItem('sessionId', sid);
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('userRole', 'admin');
      localStorage.setItem('userPermissions', '[]');
      localStorage.setItem('theme', 'light');
    }
  }, { sid: process.env.SESSION_ID, user });
  const authPage = await ctx.newPage();
  let page = authPage;
  page.on('pageerror', e => console.log('  pageerror:', e.message.slice(0, 120)));
  page.on('response', r => { if (r.status() >= 400 && r.url().includes('/api/')) console.log('  HTTP', r.status(), r.url().replace(BASE, '')); });

  const settle = async (ms = 1200) => { await page.waitForLoadState('networkidle').catch(() => {}); await page.waitForTimeout(ms); };
  const clickText = async (spec) => {
    if (typeof spec === 'string') spec = { text: spec };
    if (spec.selector) { await page.locator(spec.selector).first().click(); return; }
    // Prefer a visible button/tab with that accessible name (tabs, actions); fall back to visible text.
    let cands = null;
    for (const role of (spec.role ? [spec.role] : ['tab', 'button', 'link'])) {
      const c = page.getByRole(role, { name: spec.text, exact: spec.exact !== false }).filter({ visible: true });
      if (await c.count() > 0) { cands = c; spec.role = spec.role || role; break; }
    }
    if (!cands) cands = page.getByText(spec.text, { exact: spec.exact !== false }).filter({ visible: true });
    const n = await cands.count();
    if (n === 0) throw new Error('no visible match for ' + spec.text);
    const loc = cands.nth(spec.nth !== undefined ? spec.nth : (spec.role ? 0 : n - 1));
    await loc.scrollIntoViewIfNeeded(); await loc.click();
  };

  const anonCtx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, colorScheme: 'light' });
  const anonPage = await anonCtx.newPage();
  for (const step of plan) {
    page = step.noAuth ? anonPage : authPage;
    try {
      console.log('•', step.name);
      await page.goto(BASE + step.url, { waitUntil: 'domcontentloaded' });
      await settle(1500);
      for (const c of step.clicks || []) { await clickText(c); await settle(step.delay || 1200); }
      for (const a of step.actions || []) {
        if (a.click) { await clickText(a.click); await settle(step.delay || 1200); }
        else if (a.selectSelector) { await page.locator(a.selectSelector.selector).nth(a.selectSelector.index || 0).selectOption(a.selectSelector.value); await page.waitForTimeout(300); }
        else if (a.fillSelector) { await page.locator(a.fillSelector.selector).first().fill(a.fillSelector.value); await page.waitForTimeout(300); }
        else if (a.fill) { await page.getByPlaceholder(a.fill.placeholder).first().fill(a.fill.value); await page.waitForTimeout(300); }
        else if (a.check) { await page.getByLabel(a.check, { exact: false }).first().check().catch(async () => { await page.getByText(a.check, { exact: false }).first().click(); }); await page.waitForTimeout(300); }
        else if (a.scrollTop) { await page.evaluate(() => { window.scrollTo(0, 0); document.querySelectorAll('*').forEach(el => { if (el.scrollTop > 0) el.scrollTop = 0; }); }); await page.waitForTimeout(300); }
      }
      if (step.waitFor) await page.getByText(step.waitFor).first().waitFor({ timeout: 15000 }).catch(() => console.log('  (waitFor timed out:', step.waitFor, ')'));
      if (step.scrollTo) { await page.getByText(step.scrollTo).first().scrollIntoViewIfNeeded(); await page.waitForTimeout(400); }
      if (step.scrollY) {
        // Scroll the window AND the tallest scrollable container (app layouts often scroll an inner main pane).
        await page.evaluate(y => {
          window.scrollTo(0, y);
          let best = null, span = 0;
          document.querySelectorAll('*').forEach(el => { const s = el.scrollHeight - el.clientHeight; if (s > span && getComputedStyle(el).overflowY !== 'visible') { span = s; best = el; } });
          if (best) best.scrollTop = y;
        }, step.scrollY);
        await page.waitForTimeout(500);
      }
      if (step.hideSidebar) await page.evaluate(() => { const s = document.querySelector('aside, nav[class*="sidebar"], [class*="Sidebar"]'); if (s) s.style.display = 'none'; });
      const file = path.join(outDir, step.name + '.png');
      if (step.clipSelector) {
        const el = page.locator(step.clipSelector).first(); await el.screenshot({ path: file });
      } else {
        await page.screenshot({ path: file, fullPage: !!step.fullPage });
      }
    } catch (e) { console.log('  FAILED:', e.message.split('\n')[0]); }
  }
  await browser.close();
})();
