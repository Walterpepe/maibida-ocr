#!/usr/bin/env node
"use strict";

const fs = require("fs");
const { loadConfig, requestEdgeOne } = require("./edgeone-api");

const DEFAULT_ZONE_ID = "zone-3x9ct40r4u3w";
const DEFAULT_HOST = "www.maibida.com";
const DEFAULT_RULE_NAME = "maibida-html-node-cache";
const DEFAULT_STABLE_TTL = 600;

function parseArgs(argv) {
  const args = {
    dryRun: false,
    deploy: false,
    strict: false,
    mode: process.env.EDGEONE_HTML_CACHE_MODE || "stable",
    ttl: Number(process.env.EDGEONE_HTML_CACHE_TTL || DEFAULT_STABLE_TTL),
    zoneId: process.env.EDGEONE_ZONE_ID || DEFAULT_ZONE_ID,
    host: process.env.EDGEONE_HOST || DEFAULT_HOST,
    ruleName: process.env.EDGEONE_HTML_CACHE_RULE_NAME || DEFAULT_RULE_NAME,
    envFile: process.env.EDGEONE_ENV_FILE || "",
    modeExplicit: false,
    ttlExplicit: false,
    ruleNameExplicit: false,
    zoneExplicit: false,
    hostExplicit: false
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--dry-run") args.dryRun = true;
    else if (arg === "--deploy") args.deploy = true;
    else if (arg === "--strict") args.strict = true;
    else if (arg === "--mode" && argv[i + 1]) {
      args.mode = argv[++i];
      args.modeExplicit = true;
    } else if (arg === "--ttl" && argv[i + 1]) {
      args.ttl = Number(argv[++i]);
      args.ttlExplicit = true;
    }
    else if (arg === "--zone" && argv[i + 1]) {
      args.zoneId = argv[++i];
      args.zoneExplicit = true;
    } else if (arg === "--host" && argv[i + 1]) {
      args.host = argv[++i];
      args.hostExplicit = true;
    } else if (arg === "--rule-name" && argv[i + 1]) {
      args.ruleName = argv[++i];
      args.ruleNameExplicit = true;
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
  if (!fs.existsSync(file)) return;
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
    "  node tools/edgeone/configure-html-cache.js --dry-run",
    "  node tools/edgeone/configure-html-cache.js --mode stable --ttl 600",
    "  node tools/edgeone/configure-html-cache.js --mode development",
    "",
    "Stable mode forces EdgeOne node caching for / and *.html for a short TTL.",
    "Development mode disables the same rule. Browser Cache-Control remains",
    "no-cache because only the node cache policy is changed.",
    "",
    "Environment:",
    "  TENCENTCLOUD_SECRET_ID, TENCENTCLOUD_SECRET_KEY",
    "  EDGEONE_ZONE_ID, EDGEONE_HOST",
    "  EDGEONE_HTML_CACHE_MODE (stable or development)",
    "  EDGEONE_HTML_CACHE_TTL (seconds; stable default 600)"
  ].join("\n");
}

function hostCondition(args) {
  return `\${http.request.host} in ['${args.host.replace(/'/g, "\\'")}']`;
}

function cacheAction(ttl) {
  return {
    Name: "Cache",
    CacheParameters: {
      CustomTime: {
        Switch: "on",
        IgnoreCacheControl: "on",
        CacheTime: ttl
      }
    }
  };
}

function developmentAction() {
  return {
    Name: "Cache",
    CacheParameters: {
      FollowOrigin: {
        Switch: "on",
        DefaultCache: "on",
        DefaultCacheStrategy: "on",
        DefaultCacheTime: 0
      }
    }
  };
}

function ruleSet(args) {
  const stable = args.mode === "stable";
  return [
    {
      RuleName: `${args.ruleName}-home`,
      Status: stable ? "enable" : "disable",
      Description: [
        stable
          ? "Stable-mode homepage node cache"
          : "Development mode: homepage cache disabled",
        "Short forced node TTL; browser responses still require revalidation"
      ],
      Branches: [
        {
          Condition:
            `${hostCondition(args)} and \${http.request.uri.path} in ['/']`,
          Actions: [stable ? cacheAction(args.ttl) : developmentAction()]
        }
      ]
    },
    {
      RuleName: `${args.ruleName}-files`,
      Status: stable ? "enable" : "disable",
      Description: [
        stable
          ? "Stable-mode HTML file node cache"
          : "Development mode: HTML file cache disabled",
        "Short forced node TTL; browser responses still require revalidation"
      ],
      Branches: [
        {
          Condition:
            `${hostCondition(args)} and ` +
            "\${http.request.file_extension} in ['html']",
          Actions: [stable ? cacheAction(args.ttl) : developmentAction()]
        }
      ]
    }
  ];
}

async function findRule(config, args, ruleName) {
  const result = await requestEdgeOne(
    "DescribeL7AccRules",
    { ZoneId: args.zoneId, Limit: 1000, Offset: 0 },
    config
  );
  return (result.Rules || []).find(rule => rule.RuleName === ruleName);
}

async function upsertRules(config, args, rules) {
  const missing = [];
  let updated = 0;

  for (const rule of rules) {
    const existing = await findRule(config, args, rule.RuleName);
    if (!existing) {
      missing.push(rule);
      continue;
    }
    await requestEdgeOne(
      "ModifyL7AccRule",
      {
        ZoneId: args.zoneId,
        Rule: Object.assign({ RuleId: existing.RuleId }, rule)
      },
      config
    );
    updated += 1;
  }

  if (missing.length) {
    const created = await requestEdgeOne(
      "CreateL7AccRules",
      { ZoneId: args.zoneId, Rules: missing },
      config
    );
    console.log(
      `PASS EdgeOne HTML cache ${args.mode} rules created: ` +
        `${(created.RuleIds || []).join(",") || "unknown"} TTL=${args.ttl}s`
    );
  }
  if (updated) {
    console.log(
      `PASS EdgeOne HTML cache ${args.mode} rules updated: ` +
        `${updated} TTL=${args.ttl}s`
    );
  }
}

function validate(args) {
  if (args.mode !== "stable" && args.mode !== "development") {
    throw new Error("--mode must be stable or development");
  }
  if (args.mode === "stable" && (!Number.isInteger(args.ttl) || args.ttl < 1)) {
    throw new Error("--ttl must be a positive integer number of seconds");
  }
  if (args.ttl > 315360000) {
    throw new Error("--ttl cannot exceed 315360000 seconds");
  }
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
    if (!args.modeExplicit) {
      args.mode = process.env.EDGEONE_HTML_CACHE_MODE || args.mode;
    }
    if (!args.ttlExplicit) {
      args.ttl = Number(process.env.EDGEONE_HTML_CACHE_TTL || args.ttl);
    }
    if (!args.ruleNameExplicit) {
      args.ruleName =
        process.env.EDGEONE_HTML_CACHE_RULE_NAME || args.ruleName;
    }
    validate(args);
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
  const strict = args.strict || process.env.EDGEONE_HTML_CACHE_STRICT === "1";
  const rules = ruleSet(args);
  const request = {
    Action: "UpsertL7AccRules",
    Version: "2022-09-01",
    Endpoint: config.endpoint,
    Region: config.region || "(not set)",
    Payload: { ZoneId: args.zoneId, Rules: rules }
  };

  if (args.dryRun) {
    console.log(JSON.stringify(request, null, 2));
    return;
  }

  const noCredentials = !config.secretId || !config.secretKey;
  if (noCredentials && args.deploy && !strict) {
    console.warn(
      "WARN EdgeOne HTML cache skipped: TENCENTCLOUD_SECRET_ID/SECRET_KEY " +
        "are not configured."
    );
    return;
  }
  if (noCredentials) {
    throw new Error("Tencent Cloud credentials are required.");
  }

  await upsertRules(config, args, rules);
}

main().catch(error => {
  console.error(`FAIL ${error.message}`);
  process.exit(1);
});
