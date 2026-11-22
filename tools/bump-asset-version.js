#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const version = process.argv[2];
if (!/^\d{12}$/.test(version || "")) {
  console.error("Usage: node tools/bump-asset-version.js YYYYMMDDHHMM");
  process.exit(1);
}

const root = path.resolve(__dirname, "..");
const skipDirs = new Set([".git", "node_modules", "tools"]);
const assetReference =
  /\b((?:href|src)\s*=\s*)(["'])((?:\.\.\/)?\/?cn\/(?:css|js)\/[^?#"']+\.(?:css|js))([^"']*)\2/gi;

function walk(directory) {
  const entries = fs.readdirSync(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (entry.isDirectory()) {
      if (!skipDirs.has(entry.name)) files.push(...walk(path.join(directory, entry.name)));
    } else if (/\.(?:html?|htm)$/i.test(entry.name)) {
      files.push(path.join(directory, entry.name));
    }
  }
  return files;
}

function versionAssetReference(match, prefix, quote, assetPath, suffix) {
  const hashIndex = suffix.indexOf("#");
  const hash = hashIndex >= 0 ? suffix.slice(hashIndex) : "";
  const query = hashIndex >= 0 ? suffix.slice(0, hashIndex) : suffix;
  const params = new URLSearchParams(query.startsWith("?") ? query.slice(1) : query);
  params.set("v", version);
  return `${prefix}${quote}${assetPath}?${params.toString()}${hash}${quote}`;
}

let changedFiles = 0;
let changedReferences = 0;

for (const file of walk(root)) {
  const bytes = fs.readFileSync(file);
  const hasBom = bytes.length >= 3 &&
    bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf;
  const text = bytes.toString("utf8", hasBom ? 3 : 0);
  let fileReferences = 0;
  const next = text.replace(assetReference, (...args) => {
    fileReferences += 1;
    return versionAssetReference(...args);
  });

  if (next !== text) {
    fs.writeFileSync(file, (hasBom ? "\uFEFF" : "") + next, "utf8");
    changedFiles += 1;
    changedReferences += fileReferences;
    console.log(`${path.relative(root, file)}: ${fileReferences}`);
  }
}

console.log(`Updated ${changedReferences} asset references in ${changedFiles} HTML files to v=${version}.`);
