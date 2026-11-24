#!/usr/bin/env node
"use strict";

const {
  loadConfig,
  requestEdgeOne
} = require("./edgeone-api");

const DEFAULT_ZONE_ID = "zone-3x9ct40r4u3w";
const DEFAULT_HOST = "www.maibida.com";
const PURGE_BATCH_SIZE = 50;

function parseArgs(argv) {
  const args = {
    dryRun: false,
    deploy: false,
    strict: false,
    zoneId: process.env.EDGEONE_ZONE_ID || DEFAULT_ZONE_ID,
    host: process.env.EDGEONE_HOST || DEFAULT_HOST,
    urls: [],
    prefixes: [],
    hosts: [],
    all: false,
    html: false,
    repoRoot: process.cwd(),
    envFile: process.env.EDGEONE_ENV_FILE || "",
    zoneExplicit: false
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--dry-run") args.dryRun = true;
    else if (arg === "--deploy") args.deploy = true;
    else if (arg === "--strict") args.strict = true;
    else if (arg === "--all") args.all = true;
    else if (arg === "--html") args.html = true;
    else if (arg === "--repo-root" && argv[i + 1]) {
      args.repoRoot = argv[++i];
    }
    else if (arg === "--url" && argv[i + 1]) {
      args.urls.push(argv[++i]);
    } else if (arg === "--prefix" && argv[i + 1]) {
      args.prefixes.push(argv[++i]);
    } else if (arg === "--host" && argv[i + 1]) {
      args.hosts.push(argv[++i]);
    } else if (arg === "--zone" && argv[i + 1]) {
      args.zoneId = argv[++i];
      args.zoneExplicit = true;
    } else if (arg === "--env-file" && argv[i + 1]) {
      args.envFile = argv[++i];
    } else if (arg === "--help" || arg === "-h") {
      args.help = true;
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  return args;
}

function loadEnvFile(file) {
  if (!file) return;
  const fs = require("fs");
  if (!fs.existsSync(file)) return;
  const content = fs.readFileSync(file, "utf8");
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const match = /^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/.exec(trimmed);
    if (!match || process.env[match[1]] !== undefined) continue;
    let value = match[2].trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    process.env[match[1]] = value;
  }
}

function buildOperations(args) {
  if (args.all) {
    return [{ Type: "purge_all", Method: "delete" }];
  }

  const explicit =
    args.urls.length || args.prefixes.length || args.hosts.length;
  const urls = explicit ? args.urls : [`https://${args.host}/`];
  const prefixes = explicit
    ? args.prefixes
    : [
        `https://${args.host}/contact`,
        `https://${args.host}/cn/css/`,
        `https://${args.host}/cn/js/`
      ];
  const operations = [];

  if (urls.length) {
    for (let i = 0; i < urls.length; i += PURGE_BATCH_SIZE) {
      operations.push({
        Type: "purge_url",
        Method: "delete",
        Targets: urls.slice(i, i + PURGE_BATCH_SIZE)
      });
    }
  }
  if (prefixes.length) {
    operations.push({
      Type: "purge_prefix",
      Method: "delete",
      Targets: prefixes
    });
  }
  if (args.hosts.length) {
    operations.push({
      Type: "purge_host",
      Method: "delete",
      Targets: args.hosts
    });
  }
  return operations;
}

function discoverHtmlUrls(args) {
  const fs = require("fs");
  const path = require("path");
  const urls = [];

  function visit(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      if (entry.name === ".git" || entry.name === "node_modules") continue;
      const fullPath = path.join(directory, entry.name);
      if (entry.isDirectory()) {
        visit(fullPath);
      } else if (
        entry.isFile() &&
        entry.name.toLowerCase().endsWith(".html")
      ) {
        const relative = path
          .relative(args.repoRoot, fullPath)
          .split(path.sep)
          .join("/");
        urls.push(`https://${args.host}/${relative}`);
      }
    }
  }

  visit(args.repoRoot);
  return urls;
}

function usage() {
  return [
    "Usage:",
    "  node tools/edgeone/edgeone-purge.js --dry-run",
    "  node tools/edgeone/edgeone-purge.js --prefix https://www.maibida.com/cn/css/",
    "  node tools/edgeone/edgeone-purge.js --url https://www.maibida.com/contact.html",
    "  node tools/edgeone/edgeone-purge.js --html --repo-root .",
    "  node tools/edgeone/edgeone-purge.js --host www.maibida.com",
    "  node tools/edgeone/edgeone-purge.js --all",
    "",
    "Environment:",
    "  TENCENTCLOUD_SECRET_ID, TENCENTCLOUD_SECRET_KEY",
    "  EDGEONE_ZONE_ID (defaults to zone-3x9ct40r4u3w)",
    "  TENCENTCLOUD_ENDPOINT or TENCENTCLOUD_REGION=intl",
    "",
    "Deployment mode (--deploy) skips with status 0 when credentials are absent.",
    "Set EDGEONE_PURGE_STRICT=1 or pass --strict to make that an error."
  ].join("\n");
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
    loadEnvFile(args.envFile);
    if (!args.zoneExplicit) {
      args.zoneId = process.env.EDGEONE_ZONE_ID || args.zoneId;
    }
    args.host = process.env.EDGEONE_HOST || args.host;
    if (args.html) {
      args.urls = [`https://${args.host}/`].concat(discoverHtmlUrls(args));
    }
  } catch (error) {
    console.error(error.message);
    console.error(usage());
    process.exit(2);
  }

  if (args.help) {
    console.log(usage());
    return;
  }

  const config = loadConfig();
  const strict = args.strict || process.env.EDGEONE_PURGE_STRICT === "1";

  const operations = buildOperations(args);
  const requests = operations.map(operation =>
    Object.assign({ ZoneId: args.zoneId }, operation)
  );
  const request = {
    Action: "CreatePurgeTask",
    Version: "2022-09-01",
    Endpoint: config.endpoint,
    Region: config.region || "(not set)",
    Payloads: requests
  };

  if (args.dryRun) {
    console.log(JSON.stringify(request, null, 2));
    return;
  }

  const noCredentials = !config.secretId || !config.secretKey;
  if (noCredentials && args.deploy && !strict) {
    console.warn(
      "WARN EdgeOne purge skipped: TENCENTCLOUD_SECRET_ID/SECRET_KEY are not configured."
    );
    return;
  }
  if (noCredentials) {
    throw new Error("Tencent Cloud credentials are required for a real purge.");
  }

  for (const payload of requests) {
    const result = await requestEdgeOne("CreatePurgeTask", payload, config);
    console.log(
      `PASS ${payload.Type} submitted: JobId=${result.JobId || "unknown"} ` +
        `RequestId=${result.RequestId || "unknown"}`
    );
  }
}

main().catch(error => {
  console.error(`FAIL ${error.message}`);
  process.exit(1);
});
