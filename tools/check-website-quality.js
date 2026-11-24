#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const fs = require("fs");
const net = require("net");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const REPORT = path.join(__dirname, "website-quality.json");
const checks = [];
const failures = [];

function check(name, ok, detail = "") {
  checks.push({ name, ok: Boolean(ok), detail: String(detail) });
  if (!ok) failures.push(`${name}: ${detail}`);
}

function read(relative) {
  return fs.readFileSync(path.join(ROOT, relative), "utf8");
}

function walk(directory, output = []) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (
      entry.name === ".git" ||
      entry.name === "node_modules" ||
      entry.name === "tools" ||
      entry.name.includes("_bak")
    ) {
      continue;
    }
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(full, output);
    else if (entry.isFile() && entry.name.endsWith(".html")) output.push(full);
  }
  return output;
}

const contactPages = fs
  .readdirSync(ROOT, { withFileTypes: true })
  .filter(entry => entry.isFile() && /^contact(?:\.[a-z]{2}-[A-Z]{2})?\.html$/.test(entry.name))
  .map(entry => entry.name)
  .sort();

check(
  "all localized contact pages are present",
  contactPages.length >= 11,
  `${contactPages.length} pages`
);

for (const page of contactPages) {
  const htmlText = read(page);
  const form = /<form\b[^>]*\bid="message-form"[^>]*>/i.exec(htmlText)?.[0] || "";
  const issues = [];
  if (!/\baction="\/api\/messages"/.test(form)) issues.push("same-origin action");
  if (!/\baria-labelledby="cf-form-heading"/.test(form)) issues.push("form name");
  if (!/\baria-busy="false"/.test(form)) issues.push("aria-busy");
  if (!/<h1\b[^>]*\bid="cf-form-heading"/i.test(htmlText)) issues.push("heading id");
  if (!/<p\b[^>]*\bid="form-status"[^>]*\brole="status"[^>]*\baria-live="polite"/i.test(htmlText)) {
    issues.push("live status");
  }
  if (!/<button\b[^>]*\btype="submit"/i.test(htmlText)) issues.push("submit type");
  if (!/<script\b[^>]*\bsrc="[^"]*cn\/js\/contact\.js[^"]*"[^>]*\bdata-submitting=/i.test(htmlText)) {
    issues.push("localized busy label");
  }

  const autocomplete = {
    name: "name",
    email: "email",
    phone: "tel",
    company: "organization",
    country: "country-name"
  };
  for (const name of ["name", "email", "phone", "company", "country", "message"]) {
    const control = new RegExp(`<(?:input|textarea)\\b[^>]*\\bname="${name}"[^>]*>`, "i").exec(htmlText)?.[0] || "";
    const id = new RegExp(`\\bid="(cf-${name})"`, "i").exec(control)?.[1];
    if (!id) issues.push(`${name} id`);
    if (id && !new RegExp(`<label\\b[^>]*\\bfor="${id}"`, "i").test(htmlText)) {
      issues.push(`${name} label`);
    }
    if (
      autocomplete[name] &&
      !new RegExp(`\\bautocomplete="${autocomplete[name]}"`).test(control)
    ) {
      issues.push(`${name} autocomplete`);
    }
  }
  for (const name of ["name", "email", "message", "consent"]) {
    const control = new RegExp(`<(?:input|textarea)\\b[^>]*\\bname="${name}"[^>]*>`, "i").exec(htmlText)?.[0] || "";
    if (!/\baria-describedby="form-status"/.test(control)) {
      issues.push(`${name} error association`);
    }
  }
  check(`contact semantics ${page}`, issues.length === 0, issues.join(", "));
}

const contactJs = read("cn/js/contact.js");
check(
  "contact client uses the current same-origin endpoint",
  /form\.getAttribute\('action'\)/.test(contactJs) &&
    /fetch\(endpoint, opts\)/.test(contactJs) &&
    !/https:\/\/www\.maibida\.com\/api\/messages/.test(contactJs),
  "fetch must use the form action"
);
check(
  "contact client exposes loading and invalid states",
  /aria-busy/.test(contactJs) &&
    /aria-invalid/.test(contactJs) &&
    /cfg\.submitting/.test(contactJs),
  "aria-busy, aria-invalid, localized busy text"
);
check(
  "contact client does not inject HTML",
  !/\.innerHTML\s*=/.test(contactJs),
  "textContent only"
);

const contactCss = read("cn/css/contact.css");
check(
  "contact styles support accessibility states and touch targets",
  /aria-invalid/.test(contactCss) &&
    /focus-visible/.test(contactCss) &&
    /min-height:44px/.test(contactCss),
  "invalid, focus-visible, 44px controls"
);

const htmlPages = walk(ROOT);
const globalIssues = [];
for (const full of htmlPages) {
  const relative = path.relative(ROOT, full).split(path.sep).join("/");
  if (relative.includes("report") || relative.includes("hreflang")) continue;
  const text = fs.readFileSync(full, "utf8");
  if (!/<html\b[^>]*\blang="[^"]+"/i.test(text)) globalIssues.push(`${relative}: lang`);
  if (!/<meta\b[^>]*\bname="viewport"/i.test(text)) globalIssues.push(`${relative}: viewport`);
  if (!/<title>[^<]+<\/title>/i.test(text)) globalIssues.push(`${relative}: title`);
  for (const match of text.match(/<img\b[^>]*>/gi) || []) {
    if (!/\balt\s*=/.test(match)) globalIssues.push(`${relative}: image alt`);
  }
  for (const match of text.match(/<a\b[^>]*\btarget="_blank"[^>]*>/gi) || []) {
    if (!/\b(?:noopener|noreferrer)\b/i.test(match)) {
      globalIssues.push(`${relative}: target=_blank rel`);
    }
  }
}
check(
  "deployable HTML has baseline semantics and safe external links",
  globalIssues.length === 0,
  globalIssues.slice(0, 8).join(", ")
);

function findFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
  });
}

async function waitForServer(baseUrl, server) {
  const started = Date.now();
  while (Date.now() - started < 15000) {
    if (server.exitCode !== null) throw new Error(`preview server exited ${server.exitCode}`);
    try {
      const response = await fetch(`${baseUrl}/contact.html`);
      if (response.ok) return;
    } catch {
      // Wait for the local listener.
    }
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  throw new Error("preview server did not start within 15s");
}

async function loadPlaywright() {
  try {
    return require("playwright");
  } catch {
    throw new Error(
      "Playwright is required for runtime checks. Install it with " +
        "`npm install --no-save playwright`, or set NODE_PATH to a Playwright installation."
    );
  }
}

async function launchBrowser(chromium) {
  try {
    return await chromium.launch({
      channel: process.env.PLAYWRIGHT_CHANNEL || "msedge",
      headless: true
    });
  } catch {
    return chromium.launch({ headless: true });
  }
}

function boxIsAccessible(box, minimum = 40) {
  return Boolean(box && box.width >= minimum && box.height >= minimum);
}

async function runtimeChecks() {
  const { chromium } = await loadPlaywright();
  const port = await findFreePort();
  const baseUrl = `http://127.0.0.1:${port}`;
  const output = [];
  const server = childProcess.spawn(
    process.execPath,
    [path.join(ROOT, "tools", "preview-server.js"), String(port)],
    {
      cwd: ROOT,
      env: Object.assign({}, process.env, {
        HOST: "127.0.0.1",
        PORT: String(port),
        MAIBIDA_MESSAGE_DIR: path.join(ROOT, "tools", "quality-check-messages"),
        MAIBIDA_SMTP_HOST: "",
        MAIBIDA_WECOM_WEBHOOK_URL: ""
      }),
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"]
    }
  );
  server.stdout.on("data", chunk => output.push(String(chunk)));
  server.stderr.on("data", chunk => output.push(String(chunk)));

  try {
    await waitForServer(baseUrl, server);
    const getApi = await fetch(`${baseUrl}/api/messages`);
    check(
      "message API blocks GET and disables caching",
      getApi.status === 405 && getApi.headers.get("cache-control") === "no-store",
      `status=${getApi.status} cache=${getApi.headers.get("cache-control")}`
    );
    const missingConsent = await fetch(`${baseUrl}/api/messages`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name: "test", email: "test@example.com", message: "test" })
    });
    check(
      "message API rejects missing consent without persisting",
      missingConsent.status === 400,
      `status=${missingConsent.status}`
    );
    const wrongType = await fetch(`${baseUrl}/api/messages`, {
      method: "POST",
      headers: { "content-type": "text/html" },
      body: "<p>not json</p>"
    });
    check(
      "message API rejects unsupported content types",
      wrongType.status === 415,
      `status=${wrongType.status}`
    );
    const honeypot = await fetch(`${baseUrl}/api/messages`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        name: "test",
        email: "test@example.com",
        message: "test",
        consent: "yes",
        website: "https://spam.example"
      })
    });
    const honeypotBody = await honeypot.json();
    check(
      "message API silently absorbs honeypot submissions",
      honeypot.status === 200 && honeypotBody.id === "ignored",
      `status=${honeypot.status} id=${honeypotBody.id}`
    );
    const browser = await launchBrowser(chromium);
    try {
      const viewports = [
        { width: 320, height: 568 },
        { width: 390, height: 844 },
        { width: 768, height: 1024 },
        { width: 1440, height: 900 }
      ];
      const samplePages = [
        "index.html",
        "index.en-US.html",
        "contact.html",
        "contact.en-US.html",
        "contact.es-ES.html"
      ];
      const localizedContacts = contactPages.filter(page =>
        page !== "contact.html" && page !== "contact.en-US.html" && page !== "contact.es-ES.html"
      );

      for (const viewport of viewports) {
        for (const relative of samplePages) {
          const context = await browser.newContext({ viewport });
          const page = await context.newPage();
          const pageErrors = [];
          page.on("pageerror", error => pageErrors.push(String(error)));
          const response = await page.goto(`${baseUrl}/${relative}`, {
            waitUntil: "domcontentloaded",
            timeout: 20000
          });
          await page.waitForTimeout(250);
          const metrics = await page.evaluate(() => {
            const images = Array.from(document.images);
            const visibleImages = images.filter(image => {
              const box = image.getBoundingClientRect();
              return box.top < innerHeight && box.bottom > 0;
            });
            const imageResources = performance
              .getEntriesByType("resource")
              .filter(entry => entry.initiatorType === "image")
              .sort((a, b) => b.transferSize - a.transferSize);
            return {
              overflow: Math.max(
                0,
                document.documentElement.scrollWidth - window.innerWidth
              ),
              h1: document.querySelectorAll("h1").length,
              brokenImages: images
                .filter(
                  image =>
                    image.getAttribute("src") &&
                    image.complete &&
                    image.naturalWidth === 0
                )
                .map(image => image.getAttribute("src")),
              missingDimensions: visibleImages
                .filter(
                  image =>
                    !image.hasAttribute("width") || !image.hasAttribute("height")
                )
                .map(image => image.getAttribute("src")),
              largestImage: imageResources[0]
                ? {
                    url: imageResources[0].name,
                    bytes: imageResources[0].transferSize
                  }
                : null
            };
          });
          check(
            `runtime ${relative} ${viewport.width}px`,
            response &&
              response.ok() &&
              metrics.overflow <= 1 &&
              metrics.h1 === 1 &&
              metrics.brokenImages.length === 0 &&
              metrics.missingDimensions.length === 0 &&
              (!metrics.largestImage || metrics.largestImage.bytes <= 750000) &&
              pageErrors.length === 0,
            `status=${response ? response.status() : 0} overflow=${metrics.overflow} ` +
              `h1=${metrics.h1} broken=${metrics.brokenImages.slice(0, 2)} ` +
              `dimensions=${metrics.missingDimensions.slice(0, 2)} ` +
              `largest=${JSON.stringify(metrics.largestImage)} ` +
              `js=${pageErrors.slice(0, 1)}`
          );
          await context.close();
        }
      }

      for (const relative of localizedContacts) {
        const context = await browser.newContext({
          viewport: { width: 390, height: 844 }
        });
        const page = await context.newPage();
        const pageErrors = [];
        page.on("pageerror", error => pageErrors.push(String(error)));
        const response = await page.goto(`${baseUrl}/${relative}`, {
          waitUntil: "domcontentloaded",
          timeout: 20000
        });
        await page.waitForTimeout(150);
        const overflow = await page.evaluate(
          "Math.max(0, document.documentElement.scrollWidth - window.innerWidth)"
        );
        check(
          `localized contact overflow ${relative}`,
          response && response.ok() && overflow <= 1 && pageErrors.length === 0,
          `status=${response ? response.status() : 0} overflow=${overflow} js=${pageErrors.slice(0, 1)}`
        );
        await context.close();
      }

      const context = await browser.newContext({
        viewport: { width: 390, height: 844 }
      });
      const page = await context.newPage();
      await page.goto(`${baseUrl}/contact.html`, { waitUntil: "domcontentloaded" });
      const backBox = await page.locator(".cf-back").boundingBox();
      const submitBox = await page.locator("#message-form button[type=submit]").boundingBox();
      const consentBox = await page.locator(".cf-consent label").boundingBox();
      check(
        "contact touch targets",
        boxIsAccessible(backBox) &&
          boxIsAccessible(submitBox) &&
          boxIsAccessible(consentBox),
        `back=${JSON.stringify(backBox)} submit=${JSON.stringify(submitBox)} ` +
          `consent=${JSON.stringify(consentBox)}`
      );
      await page.locator(".wa-consult-trigger").click();
      const closeBox = await page.locator(".wa-consult-close").boundingBox();
      check(
        "WhatsApp panel close target",
        boxIsAccessible(closeBox),
        JSON.stringify(closeBox)
      );
      await page.keyboard.press("Escape");
      check(
        "WhatsApp panel closes with Escape",
        await page.locator(".wa-consult-panel").isHidden(),
        "panel should be hidden"
      );
      await page.locator("#cf-name").focus();
      const focusStyle = await page.locator("#cf-name").evaluate(element => {
        const style = getComputedStyle(element);
        return {
          outlineStyle: style.outlineStyle,
          outlineWidth: style.outlineWidth,
          boxShadow: style.boxShadow
        };
      });
      check(
        "form focus indicator",
        focusStyle.outlineStyle !== "none" || focusStyle.boxShadow !== "none",
        JSON.stringify(focusStyle)
      );
      await context.close();

      const valid = {
        name: "QUALITY CHECK",
        email: "quality@example.com",
        message: "automated quality check"
      };

      async function formContext(handler) {
        const ctx = await browser.newContext({
          viewport: { width: 390, height: 844 }
        });
        const pg = await ctx.newPage();
        pg.on("pageerror", error =>
          check("quality test JS errors", false, String(error))
        );
        await pg.goto(`${baseUrl}/contact.html`, { waitUntil: "domcontentloaded" });
        await pg.route("**/api/messages", handler);
        return { ctx, pg };
      }

      let submittedUrl = "";
      let scenario = "success";
      {
        const { ctx, pg } = await formContext(route => {
          submittedUrl = route.request().url();
          if (scenario === "failure") {
            return route.fulfill({
              status: 503,
              contentType: "application/json",
              body: '{"ok":false,"error":"temporary"}'
            });
          }
          return route.fulfill({
            status: 200,
            contentType: "application/json",
            body: '{"ok":true}'
          });
        });
        await pg.fill("#cf-name", valid.name);
        await pg.fill("#cf-email", valid.email);
        await pg.fill("#cf-message", valid.message);
        await pg.check("#cf-consent");
        await pg.click("#message-form button[type=submit]");
        await pg.waitForSelector("#form-status.ok", { timeout: 5000 });
        check(
          "contact submit stays on the current origin",
          submittedUrl === `${baseUrl}/api/messages`,
          submittedUrl
        );
        check(
          "successful submit resets form and busy state",
          (await pg.inputValue("#cf-name")) === "" &&
            (await pg.getAttribute("#message-form", "aria-busy")) === "false" &&
            (await pg.locator("#message-form button[type=submit]").isEnabled()),
          "form reset, enabled button, aria-busy=false"
        );

        scenario = "failure";
        await pg.fill("#cf-name", valid.name);
        await pg.fill("#cf-email", valid.email);
        await pg.fill("#cf-message", valid.message);
        await pg.check("#cf-consent");
        await pg.click("#message-form button[type=submit]");
        await pg.waitForSelector("#form-status.err", { timeout: 5000 });
        check(
          "API failure leaves a recoverable form",
          (await pg.getAttribute("#message-form", "aria-busy")) === "false" &&
            (await pg.locator("#message-form button[type=submit]").isEnabled()),
          "error visible, button enabled, aria-busy=false"
        );
        await ctx.close();
      }

      {
        const { ctx, pg } = await formContext(route =>
          route.fulfill({
            status: 200,
            contentType: "application/json",
            body: '{"ok":true}'
          })
        );
        await pg.fill("#cf-email", valid.email);
        await pg.fill("#cf-message", valid.message);
        await pg.check("#cf-consent");
        await pg.click("#message-form button[type=submit]");
        await pg.waitForSelector("#form-status.err", { timeout: 3000 });
        check(
          "invalid required field is focused and announced",
          (await pg.getAttribute("#cf-name", "aria-invalid")) === "true" &&
            (await pg.evaluate(() => document.activeElement?.id)) === "cf-name",
          "name aria-invalid=true and focused"
        );
        await ctx.close();
      }

      {
        const { ctx, pg } = await formContext(route =>
          route.fulfill({
            status: 200,
            contentType: "application/json",
            body: '{"ok":true}'
          })
        );
        await pg.fill("#cf-name", valid.name);
        await pg.fill("#cf-email", valid.email);
        await pg.fill("#cf-message", valid.message);
        await pg.click("#message-form button[type=submit]");
        await pg.waitForSelector("#form-status.err", { timeout: 3000 });
        check(
          "missing consent is focused and announced",
          (await pg.getAttribute("#cf-consent", "aria-invalid")) === "true" &&
            (await pg.evaluate(() => document.activeElement?.id)) === "cf-consent",
          "consent aria-invalid=true and focused"
        );
        await ctx.close();
      }
    } finally {
      await browser.close();
    }
  } finally {
    if (server.exitCode === null) server.kill();
    await Promise.race([
      new Promise(resolve => server.once("exit", resolve)),
      new Promise(resolve => setTimeout(resolve, 3000))
    ]);
  }
}

async function main() {
  const staticOnly = process.argv.includes("--static-only");
  if (!staticOnly) await runtimeChecks();
  const report = {
    generatedAt: new Date().toISOString(),
    mode: staticOnly ? "static" : "runtime",
    passed: checks.filter(item => item.ok).length,
    total: checks.length,
    failures,
    checks
  };
  const reportPath = process.env.QUALITY_REPORT || REPORT;
  if (reportPath !== "off") {
    fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  }
  console.log(`PASS ${report.passed}/${report.total} (${report.mode})`);
  for (const failure of failures) console.error(`FAIL ${failure}`);
  if (reportPath !== "off") console.log(`Report: ${reportPath}`);
  process.exitCode = failures.length ? 1 : 0;
}

main().catch(error => {
  console.error(`FAIL ${error.message}`);
  process.exitCode = 1;
});
