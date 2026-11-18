/** Repeatable browser walkthrough against an already started local demo. */
import assert from "node:assert/strict";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const output = path.join(root, "docs/demo/evidence/browser");
const base = process.env.DEMO_WEB_URL ?? "http://localhost:3100";
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ channel: "chrome", headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, acceptDownloads: true });
page.setDefaultTimeout(90000);
let capture = 0;
async function shot(name) {
  capture += 1;
  await page.screenshot({ path: path.join(output, `${String(capture).padStart(2, "0")}-${name}.png`) });
}
async function open(route, heading) {
  await page.goto(`${base}${route}`);
  await page.getByRole("heading", { name: heading }).first().waitFor();
}
async function aave(preset, name) {
  await open("/scenarios", "Scenario Builder");
  await page.getByRole("button", { name: preset, exact: true }).click();
  await page.getByRole("button", { name: "Run deterministic" }).click();
  await page.waitForURL(/\/results\/[0-9a-f-]+$/);
  await page.getByText("Total liquidated", { exact: false }).first().waitFor();
  await shot(name);
  console.log(`${name}: ${page.url()}`);
}

try {
  await open("/overview", "System Overview");
  await page.getByText("FIXTURE DATA", { exact: true }).waitFor();
  await shot("aave-fixture");
  await aave("Baseline", "aave-baseline");
  await aave("Severe", "aave-severe");
  await aave("Low Liquidity", "uniswap-feedback");

  await open("/terra/historical-data", "Historical Data");
  await page.getByRole("combobox", { name: "Historical chart range" }).selectOption("crisis");
  await page.getByText("missing hours shown as gaps").first().waitFor();
  await shot("terra-historical-crisis-week");

  await open("/terra/warning-lab", "Synthetic B0–B3");
  await page.getByRole("button", { name: "Chạy B0–B3" }).click();
  await page.locator(".metricCard").filter({ hasText: "B3" }).getByText("WATCH", { exact: true }).waitFor();
  await shot("terra-synthetic-warning");
  await page.getByRole("button", { name: "MISSING", exact: true }).click();
  await page.getByRole("button", { name: "Chạy B0–B3" }).click();
  await page.locator(".metricCard").filter({ hasText: "B3" }).getByText("ABSTAIN", { exact: true }).waitFor();
  await shot("terra-missing-abstain");

  await open("/terra/early-warning", "Early Warning");
  await page.getByRole("button", { name: "Cutoff-Safe" }).click();
  await page.getByText("CUTOFF SAFE", { exact: false }).first().waitFor();
  await shot("terra-retrospective-cutoff-safe");

  await open("/terra/stress-test", "Stress Test");
  await page.getByRole("button", { name: "Adverse" }).click();
  await page.getByRole("button", { name: "Run one scenario" }).click();
  await page.getByText("1 / 1", { exact: false }).first().waitFor().catch(async () => {
    await page.getByText("Runs", { exact: true }).first().waitFor();
  });
  await shot("terra-stress-adverse");

  await open("/terra/exit-planner", "Exit Calculator");
  await page.getByRole("button", { name: "Tính phương án" }).click();
  await page.getByRole("heading", { name: "NOT_VERIFIABLE" }).waitFor();
  await page.getByRole("textbox", { name: "Assumed capacity" }).fill("600");
  await page.getByRole("button", { name: "Tính phương án" }).click();
  await page.getByRole("heading", { name: "CAPACITY_ASSUMED_PARTIAL" }).waitFor();
  assert.match(await page.locator("main").innerText(), /465\.6/);
  await shot("exit-capacity-partial");
  await page.getByRole("link", { name: "Mở kết quả đã lưu" }).click();
  await page.getByRole("heading", { name: /ILLUSTRATIVE_EXIT/ }).waitFor();
  assert.match(await page.locator("main").innerText(), /"net_usd": "465\.6"/);
  await shot("saved-run-readback");
  const pending = page.waitForEvent("download");
  await page.getByRole("link", { name: "Tải kết quả ZIP" }).click();
  const download = await pending;
  assert.match(download.suggestedFilename(), /defistress-demo-.*\.zip/);
  console.log(`browser: ${capture} screenshots; saved run and ZIP download verified`);
} finally {
  await browser.close();
}
