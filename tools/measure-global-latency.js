#!/usr/bin/env node
"use strict";

const DEFAULT_TARGET = "www.maibida.com";
const API_ROOT = "https://api.globalping.io/v1/measurements";
const LOCATIONS = [
  { country: "CN", limit: 2 },
  { country: "SG", limit: 2 },
  { country: "JP", limit: 2 },
  { country: "DE", limit: 2 },
  { country: "US", limit: 2 },
  { country: "BR", limit: 1 }
];

function parseArgs(argv) {
  const args = { id: "", target: DEFAULT_TARGET };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--id" && argv[i + 1]) args.id = argv[++i];
    else if (argv[i] === "--target" && argv[i + 1]) args.target = argv[++i];
    else if (argv[i] === "--help" || argv[i] === "-h") args.help = true;
    else throw new Error(`Unknown argument: ${argv[i]}`);
  }
  return args;
}

async function request(url, options) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) {
    throw new Error(
      `Globalping HTTP ${response.status}: ${JSON.stringify(body)}`
    );
  }
  return body;
}

async function createMeasurement(target) {
  const created = await request(API_ROOT, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      type: "http",
      target,
      locations: LOCATIONS,
      measurementOptions: {
        request: { method: "GET" }
      }
    })
  });
  let measurement = created;
  const started = Date.now();

  while (measurement.status !== "finished") {
    if (Date.now() - started > 120000) {
      throw new Error(`Measurement ${measurement.id} did not finish in 120s`);
    }
    await new Promise(resolve => setTimeout(resolve, 2000));
    measurement = await request(`${API_ROOT}/${measurement.id}`);
  }
  return measurement;
}

function formatMs(value) {
  return Number.isFinite(value) ? String(value) : "-";
}

function printResults(measurement) {
  console.log(
    `Measurement ${measurement.id} (${measurement.status}) ` +
      `${measurement.target} at ${measurement.createdAt}`
  );
  console.log(
    [
      "COUNTRY",
      "CITY",
      "CACHE",
      "STATUS",
      "DNS",
      "TCP",
      "TLS",
      "TTFB",
      "TOTAL"
    ].join("\t")
  );

  for (const item of measurement.results || []) {
    const probe = item.probe || {};
    const result = item.result || {};
    const headers = result.headers || {};
    const timings = result.timings || {};
    console.log(
      [
        probe.country || "-",
        probe.city || "-",
        headers["eo-cache-status"] || "-",
        result.statusCode || "-",
        formatMs(timings.dns),
        formatMs(timings.tcp),
        formatMs(timings.tls),
        formatMs(timings.firstByte),
        formatMs(timings.total)
      ].join("\t")
    );
  }
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(error.message);
    process.exit(2);
  }
  if (args.help) {
    console.log(
      [
        "Usage:",
        "  node tools/measure-global-latency.js",
        "  node tools/measure-global-latency.js --id MEASUREMENT_ID",
        "",
        "Without --id, submits the same six-country HTTP GET profile used for",
        "the stable-mode cache baseline and prints TTFB for each probe."
      ].join("\n")
    );
    return;
  }

  const measurement = args.id
    ? await request(`${API_ROOT}/${args.id}`)
    : await createMeasurement(args.target);
  printResults(measurement);
}

main().catch(error => {
  console.error(`FAIL ${error.message}`);
  process.exit(1);
});
