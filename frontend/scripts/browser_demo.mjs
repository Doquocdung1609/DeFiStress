/** Repeatable browser walkthrough against an already started local demo. */
import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const output = process.env.DEMO_BROWSER_OUTPUT ?? path.join(root, "docs/demo/evidence/browser");
const base = process.env.DEMO_WEB_URL ?? "http://localhost:3100";
const recordDir = process.env.DEMO_RECORD_DIR;
await mkdir(output, { recursive: true });
if (recordDir) await mkdir(recordDir, { recursive: true });
const browser = await chromium.launch({ channel: "chrome", headless: true });
const context = await browser.newContext({
  viewport: recordDir ? { width: 1920, height: 1080 } : { width: 1440, height: 900 },
  acceptDownloads: true,
  ...(recordDir ? { recordVideo: { dir: recordDir, size: { width: 1920, height: 1080 } } } : {}),
});
const page = await context.newPage();
page.setDefaultTimeout(90000);
let capture = 0;
const began = Date.now();
const timeline = [];
async function shot(name) {
  capture += 1;
  timeline.push({ scene: name, seconds: (Date.now() - began) / 1000, url: page.url() });
  await page.screenshot({ path: path.join(output, `${String(capture).padStart(2, "0")}-${name}.png`) });
  if (recordDir) {
    await page.waitForTimeout(4000);
    await page.mouse.wheel(0, 560);
    await page.waitForTimeout(5000);
    await page.mouse.wheel(0, -560);
    await page.waitForTimeout(4000);
  }
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
  if (recordDir) {
    await open("/positions", "Positions");
    await shot("aave-positions");
  }
  await aave("Baseline", "aave-baseline");
  await aave("Severe", "aave-severe");
  await aave("Low Liquidity", "uniswap-feedback");

  if (recordDir) {
    await open("/terra/overview", "Research Overview");
    await shot("terra-overview");
  }

  await open("/terra/historical-data", "Historical Data");
  await page.getByRole("combobox", { name: "Historical chart range" }).selectOption("crisis");
  await page.getByText("missing hours shown as gaps").first().waitFor();
  await shot("terra-historical-crisis-week");

  if (recordDir) {
    await open("/terra/historical-fit", "Historical Fit");
    await shot("terra-historical-fit");
  }

  await open("/terra/warning-lab", "Synthetic B0–B3");
  await page.getByRole("button", { name: "Chạy B0–B3" }).click();
  await page.locator(".metricCard").filter({ hasText: "B3" }).getByText("WATCH", { exact: true }).waitFor();
  await shot("terra-synthetic-warning");
  await page.getByRole("link", { name: "Đánh giá phương án thoát từ cảnh báo tổng hợp này" }).click();
  await page.getByRole("heading", { name: "Exit Calculator" }).waitFor();
  await page.getByText("Đã lấy giá và thời điểm từ cảnh báo tổng hợp").first().waitFor();
  assert.equal(await page.getByLabel("Warning price").inputValue(), "0.99");
  if (recordDir) await shot("warning-to-exit-prefill");
  await open("/terra/warning-lab", "Synthetic B0–B3");
  await page.getByRole("button", { name: "MISSING", exact: true }).click();
  await page.getByRole("button", { name: "Chạy B0–B3" }).click();
  await page.locator(".metricCard").filter({ hasText: "B3" }).getByText("ABSTAIN", { exact: true }).waitFor();
  await shot("terra-missing-abstain");
  if (recordDir) {
    await page.getByRole("button", { name: "HIGH", exact: true }).click();
    await page.getByRole("button", { name: "Chạy B0–B3" }).click();
    await page.locator(".metricCard").filter({ hasText: "B3" }).getByText("HIGH", { exact: true }).waitFor();
    await shot("terra-high-warning");
  }

  await open("/terra/early-warning", "Early Warning");
  await page.getByRole("button", { name: "Cutoff-Safe" }).click();
  await page.getByText("CUTOFF SAFE", { exact: false }).first().waitFor();
  await shot("terra-retrospective-cutoff-safe");

  await open("/terra/stress-test", "Stress Test");
  await page.getByRole("button", { name: "Adverse" }).click();
  const stressResponse = page.waitForResponse((response) => response.url().includes("/api/v1/terra/stress-test") && response.request().method() === "POST");
  await page.getByRole("button", { name: "Run one scenario" }).click();
  const computedStress = await stressResponse;
  assert.equal(computedStress.status(), 200);
  assert.equal((await computedStress.json()).runs, 1);
  await page.locator(".metricCard").filter({ hasText: "Runs" }).getByText("1", { exact: true }).waitFor();
  await shot("terra-stress-adverse");
  if (recordDir) {
    await open("/terra/data-sources", "Data Sources");
    await shot("terra-data-sources");
  }

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
  await context.close();
  if (recordDir) {
    await writeFile(path.join(recordDir, "timeline.json"), JSON.stringify(timeline, null, 2));
    console.log(`recorded ${await page.video().path()}`);
  }
  await browser.close();
}
