#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const skipDirs = new Set([".git", "node_modules", "tools"]);
const attributeUrl = /\b(?:href|src)\s*=\s*(["'])(.*?)\1/gi;
const versionedAsset = /(?:^|\/)cn\/(?:css|js)\/.+\.(?:css|js)$/i;

function walk(directory) {
  const entries = fs.readdirSync(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      if (!skipDirs.has(entry.name)) files.push(...walk(fullPath));
    } else if (/\.(?:html?|htm)$/i.test(entry.name)) {
      files.push(fullPath);
    }
  }
  return files;
}

let checked = 0;
const failures = [];

for (const file of walk(root)) {
  const text = fs.readFileSync(file, "utf8");
  const relativeFile = path.relative(root, file);
  let match;
  while ((match = attributeUrl.exec(text)) !== null) {
    const rawUrl = match[2];
    const [pathAndQuery] = rawUrl.split("#");
    const queryIndex = pathAndQuery.indexOf("?");
    const assetPath = queryIndex >= 0 ? pathAndQuery.slice(0, queryIndex) : pathAndQuery;
    const normalizedPath = assetPath.replace(/\\/g, "/");
    if (!versionedAsset.test(normalizedPath)) continue;

    checked += 1;
    const query = queryIndex >= 0 ? pathAndQuery.slice(queryIndex + 1) : "";
    const version = new URLSearchParams(query).get("v");
    if (!/^\d{12}$/.test(version || "")) {
      failures.push(`${relativeFile}: missing minute-level v parameter: ${rawUrl}`);
      continue;
    }

    const target = path.resolve(path.dirname(file), assetPath);
    if (!fs.existsSync(target) || !fs.statSync(target).isFile()) {
      failures.push(`${relativeFile}: missing asset target: ${rawUrl}`);
    }
  }
}

if (failures.length) {
  for (const failure of failures) console.error(`FAIL ${failure}`);
  console.error(`\n${failures.length} asset-version failures among ${checked} references.`);
  process.exit(1);
}

console.log(`PASS ${checked} local CSS/JS references are versioned and resolve to existing files.`);
