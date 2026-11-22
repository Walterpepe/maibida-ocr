"use strict";

const crypto = require("crypto");
const https = require("https");
const { URL } = require("url");

const SERVICE = "teo";
const VERSION = "2022-09-01";
const DEFAULT_ENDPOINT = "https://teo.tencentcloudapi.com";
const DEFAULT_INTL_ENDPOINT = "https://teo.intl.tencentcloudapi.com";

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function hmac(key, value) {
  return crypto.createHmac("sha256", key).update(value).digest();
}

function loadConfig(overrides = {}) {
  const configuredRegion =
    overrides.region || process.env.TENCENTCLOUD_REGION || "";
  const intl = configuredRegion === "intl";
  const endpoint =
    overrides.endpoint ||
    process.env.TENCENTCLOUD_ENDPOINT ||
    (intl ? DEFAULT_INTL_ENDPOINT : DEFAULT_ENDPOINT);

  return {
    secretId: overrides.secretId || process.env.TENCENTCLOUD_SECRET_ID || "",
    secretKey: overrides.secretKey || process.env.TENCENTCLOUD_SECRET_KEY || "",
    region: intl ? "" : configuredRegion,
    endpoint,
    timeoutMs:
      Number(overrides.timeoutMs || process.env.TENCENTCLOUD_TIMEOUT_MS || 15000)
  };
}

function signRequest({ action, payload, config, timestamp }) {
  const body = JSON.stringify(payload || {});
  const endpoint = new URL(config.endpoint);
  const date = new Date(timestamp * 1000).toISOString().slice(0, 10);
  const headers = {
    "content-type": "application/json; charset=utf-8",
    host: endpoint.host,
    "x-tc-action": action,
    "x-tc-timestamp": String(timestamp),
    "x-tc-version": VERSION
  };

  if (config.region) headers["x-tc-region"] = config.region;

  // Tencent's TC3 examples sign content-type and host. The x-tc-* headers are
  // part of the wire request but intentionally not part of the signature scope.
  const canonicalHeaders =
    `content-type:${headers["content-type"]}\n` + `host:${headers.host}\n`;
  const signedHeaders = "content-type;host";
  const canonicalRequest = [
    "POST",
    "/",
    "",
    canonicalHeaders,
    signedHeaders,
    sha256(body)
  ].join("\n");
  const credentialScope = `${date}/${SERVICE}/tc3_request`;
  const stringToSign = [
    "TC3-HMAC-SHA256",
    String(timestamp),
    credentialScope,
    sha256(canonicalRequest)
  ].join("\n");
  const secretDate = hmac(Buffer.from(`TC3${config.secretKey}`), date);
  const secretService = hmac(secretDate, SERVICE);
  const secretSigning = hmac(secretService, "tc3_request");
  const signature = crypto
    .createHmac("sha256", secretSigning)
    .update(stringToSign)
    .digest("hex");

  headers.authorization =
    `TC3-HMAC-SHA256 Credential=${config.secretId}/${credentialScope}, ` +
    `SignedHeaders=${signedHeaders}, Signature=${signature}`;

  return { body, headers };
}

function requestEdgeOne(action, payload, options = {}) {
  const config = Object.assign(loadConfig(), options);
  if (!config.secretId || !config.secretKey) {
    return Promise.reject(
      new Error(
        "Missing TENCENTCLOUD_SECRET_ID or TENCENTCLOUD_SECRET_KEY. " +
          "Load tools/edgeone/edgeone.env or run with --dry-run."
      )
    );
  }

  const timestamp = Math.floor(Date.now() / 1000);
  const signed = signRequest({ action, payload, config, timestamp });
  const endpoint = new URL(config.endpoint);

  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        protocol: endpoint.protocol,
        hostname: endpoint.hostname,
        port: endpoint.port || 443,
        method: "POST",
        path: endpoint.pathname || "/",
        headers: signed.headers,
        timeout: config.timeoutMs
      },
      res => {
        const chunks = [];
        res.on("data", chunk => chunks.push(chunk));
        res.on("end", () => {
          const raw = Buffer.concat(chunks).toString("utf8");
          let parsed;
          try {
            parsed = raw ? JSON.parse(raw) : {};
          } catch (error) {
            reject(
              new Error(
                `EdgeOne returned HTTP ${res.statusCode} with non-JSON body: ${raw}`
              )
            );
            return;
          }

          const response = parsed.Response || {};
          if (
            res.statusCode < 200 ||
            res.statusCode >= 300 ||
            response.Error
          ) {
            const err = response.Error || {};
            reject(
              new Error(
                `${action} failed: ${err.Code || `HTTP_${res.statusCode}`} ` +
                  `${err.Message || raw} RequestId=${response.RequestId || "unknown"}`
              )
            );
            return;
          }
          resolve(response);
        });
      }
    );

    req.on("timeout", () => req.destroy(new Error(`${action} timed out`)));
    req.on("error", reject);
    req.end(signed.body);
  });
}

module.exports = {
  DEFAULT_ENDPOINT,
  DEFAULT_INTL_ENDPOINT,
  VERSION,
  loadConfig,
  requestEdgeOne,
  signRequest
};
