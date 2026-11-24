"use strict";

const assert = require("assert");
const { spawnSync } = require("child_process");
const path = require("path");

const script = path.join(__dirname, "configure-html-cache.js");
const result = spawnSync(
  process.execPath,
  [script, "--dry-run", "--mode", "stable", "--ttl", "600"],
  {
    cwd: path.join(__dirname, "..", ".."),
    encoding: "utf8"
  }
);

assert.strictEqual(result.status, 0, result.stderr);
const request = JSON.parse(result.stdout);
assert.strictEqual(request.Payload.Rules.length, 2);
for (const rule of request.Payload.Rules) {
  assert.strictEqual(rule.Status, "enable");
  assert.strictEqual(
    rule.Branches[0].Actions[0].CacheParameters.CustomTime.CacheTime,
    600
  );
}
assert.match(
  request.Payload.Rules[0].Branches[0].Condition,
  /http\.request\.uri\.path/
);
assert.match(
  request.Payload.Rules[1].Branches[0].Condition,
  /http\.request\.file_extension/
);

const purgeResult = spawnSync(
  process.execPath,
  [
    path.join(__dirname, "edgeone-purge.js"),
    "--dry-run",
    "--html",
    "--repo-root",
    path.join(__dirname, "..", "..")
  ],
  {
    cwd: path.join(__dirname, "..", ".."),
    encoding: "utf8"
  }
);
assert.strictEqual(purgeResult.status, 0, purgeResult.stderr);
const purgeRequest = JSON.parse(purgeResult.stdout);
assert.ok(purgeRequest.Payloads.length >= 2);
assert.ok(
  purgeRequest.Payloads[0].Targets.includes("https://www.maibida.com/")
);
for (const operation of purgeRequest.Payloads) {
  assert.ok(operation.Targets.length <= 50);
}

const purgeSource = require("fs").readFileSync(
  path.join(__dirname, "edgeone-purge.js"),
  "utf8"
);
assert.match(purgeSource, /discoverHtmlUrls/);

console.log("PASS EdgeOne HTML cache automation");
