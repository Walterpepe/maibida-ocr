#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { loadConfig, requestEdgeOne } = require("./edgeone-api");

const DEFAULT_ZONE_ID = "zone-3x9ct40r4u3w";
const DEFAULT_HOST = "www.maibida.com";
const DEFAULT_FUNCTION_NAME = "maibida-contact-api";
const FUNCTION_FILE = path.join(__dirname, "function", "contact-api.js");

function parseArgs(argv) {
  const args = {
    dryRun: false,
    strict: false,
    zoneId: process.env.EDGEONE_ZONE_ID || DEFAULT_ZONE_ID,
    host: process.env.EDGEONE_HOST || DEFAULT_HOST,
    functionId: process.env.EDGEONE_FUNCTION_ID || "",
    ruleId: process.env.EDGEONE_FUNCTION_RULE_ID || "",
    functionName:
      process.env.EDGEONE_FUNCTION_NAME || DEFAULT_FUNCTION_NAME,
    envFile: process.env.EDGEONE_ENV_FILE || "",
    zoneExplicit: false,
    hostExplicit: false
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--dry-run") args.dryRun = true;
    else if (arg === "--strict") args.strict = true;
    else if (arg === "--zone" && argv[i + 1]) {
      args.zoneId = argv[++i];
      args.zoneExplicit = true;
    } else if (arg === "--host" && argv[i + 1]) {
      args.host = argv[++i];
      args.hostExplicit = true;
    }
    else if (arg === "--function-id" && argv[i + 1]) args.functionId = argv[++i];
    else if (arg === "--rule-id" && argv[i + 1]) args.ruleId = argv[++i];
    else if (arg === "--function-name" && argv[i + 1]) {
      args.functionName = argv[++i];
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
  if (!file || !fs.existsSync(file)) return;
  for (const line of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
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

function usage() {
  return [
    "Usage:",
    "  node tools/edgeone/deploy-function.js --dry-run",
    "  node tools/edgeone/deploy-function.js --strict",
    "",
    "First deployment:",
    "  set EDGEONE_FUNCTION_ID after CreateFunction, then set",
    "  EDGEONE_FUNCTION_RULE_ID after CreateFunctionRule.",
    "",
    "Environment:",
    "  TENCENTCLOUD_SECRET_ID, TENCENTCLOUD_SECRET_KEY",
    "  EDGEONE_ZONE_ID, EDGEONE_HOST",
    "  EDGEONE_FUNCTION_ID, EDGEONE_FUNCTION_RULE_ID"
  ].join("\n");
}

function rulePayload(zoneId, host, functionId) {
  return {
    ZoneId: zoneId,
    FunctionRuleConditions: [
      {
        RuleConditions: [
          { Target: "host", Operator: "equal", Values: [host] },
          { Target: "url", Operator: "equal", Values: ["/api/messages"] }
        ]
      }
    ],
    TriggerType: "direct",
    FunctionId: functionId,
    Remark: "Maibida contact form API validation"
  };
}

async function findExistingFunction(config, args, content) {
  if (args.functionId) return { id: args.functionId, created: false };
  const response = await requestEdgeOne(
    "DescribeFunctions",
    {
      ZoneId: args.zoneId,
      Filters: [{ Name: "name", Values: [args.functionName] }],
      Limit: 200
    },
    config
  );
  const functions = response.Functions || [];
  const exact = functions.find(
    fn => fn.Name === args.functionName || fn.FunctionName === args.functionName
  );
  if (exact) {
    return { id: exact.FunctionId, created: false };
  }

  const created = await requestEdgeOne(
    "CreateFunction",
    {
      ZoneId: args.zoneId,
      Name: args.functionName,
      Content: content,
      Remark: "Validate and forward Maibida contact form submissions"
    },
    config
  );
  console.log(`EdgeOne function created: ${created.FunctionId}`);
  return { id: created.FunctionId, created: true };
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
    loadEnvFile(args.envFile);
    if (!args.zoneExplicit) {
      args.zoneId = process.env.EDGEONE_ZONE_ID || args.zoneId;
    }
    if (!args.hostExplicit) {
      args.host = process.env.EDGEONE_HOST || args.host;
    }
    args.functionId = process.env.EDGEONE_FUNCTION_ID || args.functionId;
    args.ruleId = process.env.EDGEONE_FUNCTION_RULE_ID || args.ruleId;
    args.functionName =
      process.env.EDGEONE_FUNCTION_NAME || args.functionName;
  } catch (error) {
    console.error(error.message);
    console.error(usage());
    process.exit(2);
  }

  if (args.help) {
    console.log(usage());
    return;
  }

  const content = fs.readFileSync(FUNCTION_FILE, "utf8");
  const config = loadConfig();
  const strict = args.strict || process.env.EDGEONE_FUNCTION_STRICT === "1";

  if (args.dryRun) {
    console.log(
      JSON.stringify(
        {
          ZoneId: args.zoneId,
          Host: args.host,
          FunctionName: args.functionName,
          FunctionId: args.functionId || "(discover-or-create)",
          RuleId: args.ruleId || "(discover-or-create)",
          ContentBytes: Buffer.byteLength(content)
        },
        null,
        2
      )
    );
    return;
  }

  const noCredentials = !config.secretId || !config.secretKey;
  if (noCredentials && !strict) {
    console.warn(
      "WARN EdgeOne function deploy skipped: Tencent Cloud credentials are not configured."
    );
    return;
  }
  if (noCredentials) {
    throw new Error("Tencent Cloud credentials are required.");
  }

  const discovered = await findExistingFunction(config, args, content);
  const functionId = discovered.id;
  if (!discovered.created) {
    await requestEdgeOne(
      "ModifyFunction",
      {
        ZoneId: args.zoneId,
        FunctionId: functionId,
        Content: content,
        Remark: "Validate and forward Maibida contact form submissions"
      },
      config
    );
  }

  let ruleId = args.ruleId;
  if (!ruleId) {
    const rulesResponse = await requestEdgeOne(
      "DescribeFunctionRules",
      {
        ZoneId: args.zoneId,
        Filters: [{ Name: "function-id", Values: [functionId] }]
      },
      config
    );
    const existing = (rulesResponse.FunctionRules || []).find(
      rule => rule.FunctionId === functionId
    );
    ruleId = existing ? existing.RuleId : "";
  }
  if (!ruleId) {
    const rule = await requestEdgeOne(
      "CreateFunctionRule",
      rulePayload(args.zoneId, args.host, functionId),
      config
    );
    ruleId = rule.RuleId;
    console.log(
      `EdgeOne function rule created: ${ruleId}. Set EDGEONE_FUNCTION_RULE_ID=${ruleId}.`
    );
  } else {
    await requestEdgeOne(
      "ModifyFunctionRule",
      Object.assign(rulePayload(args.zoneId, args.host, functionId), {
        RuleId: ruleId
      }),
      config
    );
  }

  console.log(
    `PASS EdgeOne function deployed: FunctionId=${functionId} RuleId=${ruleId}`
  );
}

main().catch(error => {
  console.error(`FAIL ${error.message}`);
  process.exit(1);
});
