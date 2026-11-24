"use strict";

const fs = require("fs");
const https = require("https");
const os = require("os");
const path = require("path");
const crypto = require("crypto");
const { spawn } = require("child_process");
const { URL } = require("url");

const WECOM_HOST = "qyapi.weixin.qq.com";
const MAX_WECOM_BYTES = 4096;

function cleanHeader(value) {
  return String(value || "").replace(/\r|\n/g, "").trim();
}

function cleanBody(value) {
  return String(value || "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
}

function escapeWeCom(value) {
  return cleanBody(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function formatWeComMarkdown(rec) {
  const lines = [
    "## 新的网站咨询",
    `> 姓名：${escapeWeCom(rec.name)}`,
    `> 邮箱：${escapeWeCom(rec.email)}`,
    `> 电话：${escapeWeCom(rec.phone || "-")}`,
    `> 公司：${escapeWeCom(rec.company || "-")}`,
    `> 国家/地区：${escapeWeCom(rec.country || "-")}`,
    `> 来源：${escapeWeCom(rec.source || "-")}`,
    `> 时间：${escapeWeCom(rec.receivedAt)}`,
    "",
    "**留言：**",
    escapeWeCom(rec.message)
  ];
  const content = lines.join("\n");
  if (Buffer.byteLength(content, "utf8") <= MAX_WECOM_BYTES) return content;
  const suffix = "\n...";
  let end = content.length;
  while (
    end > 0 &&
    Buffer.byteLength(content.slice(0, end) + suffix, "utf8") > MAX_WECOM_BYTES
  ) {
    end -= 8;
  }
  return content.slice(0, Math.max(0, end)) + suffix;
}

function postJson(urlValue, body, timeoutMs) {
  const endpoint = new URL(urlValue);
  const payload = Buffer.from(JSON.stringify(body));
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        protocol: endpoint.protocol,
        hostname: endpoint.hostname,
        port: endpoint.port || 443,
        method: "POST",
        path: `${endpoint.pathname}${endpoint.search}`,
        headers: {
          "Content-Type": "application/json; charset=utf-8",
          "Content-Length": payload.length
        },
        timeout: timeoutMs
      },
      res => {
        const chunks = [];
        res.on("data", chunk => chunks.push(chunk));
        res.on("end", () => {
          let parsed;
          try {
            parsed = JSON.parse(Buffer.concat(chunks).toString("utf8"));
          } catch (_error) {
            reject(new Error(`notification returned HTTP ${res.statusCode}`));
            return;
          }
          if (res.statusCode < 200 || res.statusCode >= 300) {
            reject(new Error(`notification returned HTTP ${res.statusCode}`));
            return;
          }
          if (parsed.errcode !== undefined && parsed.errcode !== 0) {
            reject(new Error(`WeCom error ${parsed.errcode}`));
            return;
          }
          resolve(parsed);
        });
      }
    );
    req.on("timeout", () => req.destroy(new Error("notification timed out")));
    req.on("error", reject);
    req.end(payload);
  });
}

function validateWeComUrl(value) {
  const url = new URL(value);
  if (url.protocol !== "https:" || url.hostname !== WECOM_HOST) {
    throw new Error("MAIBIDA_WECOM_WEBHOOK_URL must use https://qyapi.weixin.qq.com");
  }
  if (!url.pathname.startsWith("/cgi-bin/webhook/send")) {
    throw new Error("MAIBIDA_WECOM_WEBHOOK_URL has an unexpected path");
  }
  return url;
}

async function sendWeCom(rec) {
  const url = validateWeComUrl(process.env.MAIBIDA_WECOM_WEBHOOK_URL);
  await postJson(
    url,
    {
      msgtype: "markdown",
      markdown: { content: formatWeComMarkdown(rec) }
    },
    Number(process.env.MAIBIDA_NOTIFY_TIMEOUT_MS || 15000)
  );
}

function formatEmailMessage(rec, from, to) {
  const subject = `[Maibida] New inquiry from ${cleanHeader(rec.name)}`;
  const body = [
    `Name: ${cleanBody(rec.name)}`,
    `Email: ${cleanBody(rec.email)}`,
    `Phone: ${cleanBody(rec.phone || "-")}`,
    `Company: ${cleanBody(rec.company || "-")}`,
    `Country: ${cleanBody(rec.country || "-")}`,
    `Source: ${cleanBody(rec.source || "-")}`,
    `Received: ${cleanBody(rec.receivedAt)}`,
    "",
    "Message:",
    cleanBody(rec.message)
  ].join("\r\n");
  const domain = cleanHeader(from).split("@")[1] || "maibida.com";
  const messageId = `<${crypto.randomBytes(16).toString("hex")}@${domain}>`;
  const message = [
    `From: ${cleanHeader(from)}`,
    `To: ${to.map(cleanHeader).join(", ")}`,
    `Reply-To: ${cleanHeader(rec.email)}`,
    `Subject: =?UTF-8?B?${Buffer.from(subject).toString("base64")}?=`,
    `Date: ${new Date().toUTCString()}`,
    `Message-ID: ${messageId}`,
    "MIME-Version: 1.0",
    "Content-Type: text/plain; charset=UTF-8",
    "Content-Transfer-Encoding: 8bit",
    "",
    body
  ].join("\n");
  return message
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n")
    .replace(/^\./gm, "..")
    .replace(/\n/g, "\r\n");
}

function curlQuote(value) {
  return String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

function smtpConfig() {
  const host = cleanHeader(process.env.MAIBIDA_SMTP_HOST);
  const user = String(process.env.MAIBIDA_SMTP_USER || "");
  const pass = String(process.env.MAIBIDA_SMTP_PASS || "");
  const from = cleanHeader(process.env.MAIBIDA_SMTP_FROM);
  const recipients = String(process.env.MAIBIDA_EMAIL_TO || "")
    .split(",")
    .map(cleanHeader)
    .filter(Boolean);
  if (!host && !from && !recipients.length && !user && !pass) return null;
  if (!host || !user || !pass || !from || !recipients.length) {
    throw new Error(
      "SMTP notification requires MAIBIDA_SMTP_HOST, USER, PASS, FROM and EMAIL_TO"
    );
  }
  if (!/^[a-z0-9.-]+$/i.test(host)) throw new Error("invalid MAIBIDA_SMTP_HOST");
  return {
    host,
    port: Number(process.env.MAIBIDA_SMTP_PORT || 465),
    user,
    pass,
    from,
    recipients
  };
}

function runCurl(args, input, timeoutMs) {
  return new Promise((resolve, reject) => {
    const child = spawn("curl", args, { stdio: ["pipe", "pipe", "pipe"] });
    let stderr = "";
    const timer = setTimeout(() => {
      child.kill("SIGKILL");
      reject(new Error("SMTP notification timed out"));
    }, timeoutMs + 5000);
    child.stderr.on("data", chunk => {
      stderr += chunk.toString("utf8").slice(0, 1000);
    });
    child.on("error", error => {
      clearTimeout(timer);
      reject(error);
    });
    child.on("exit", code => {
      clearTimeout(timer);
      if (code === 0) resolve();
      else reject(new Error(`curl SMTP failed with exit ${code}: ${stderr.trim()}`));
    });
    child.stdin.end(input);
  });
}

async function sendEmail(rec) {
  const config = smtpConfig();
  if (!config) return;
  const timeoutMs = Number(process.env.MAIBIDA_NOTIFY_TIMEOUT_MS || 15000);
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "maibida-mail-"));
  const configFile = path.join(tempDir, "curl.conf");
  try {
    fs.writeFileSync(
      configFile,
      `user = "${curlQuote(config.user)}:${curlQuote(config.pass)}"\n`,
      { encoding: "utf8", mode: 0o600 }
    );
    const args = [
      "--silent",
      "--show-error",
      "--ssl-reqd",
      "--connect-timeout",
      "10",
      "--max-time",
      String(Math.ceil(timeoutMs / 1000)),
      "--config",
      configFile,
      "--url",
      `smtps://${config.host}:${config.port}`,
      "--mail-from",
      config.from,
      "--upload-file",
      "-"
    ];
    for (const recipient of config.recipients) {
      args.push("--mail-rcpt", recipient);
    }
    await runCurl(
      args,
      formatEmailMessage(rec, config.from, config.recipients),
      timeoutMs
    );
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

async function notifyInquiry(rec) {
  const jobs = [];
  if (process.env.MAIBIDA_WECOM_WEBHOOK_URL) {
    jobs.push(
      sendWeCom(rec)
        .then(() => "wecom-sent")
        .catch(error => {
          console.error(`WARN WeCom notification failed for ${rec.id}: ${error.message}`);
          return "wecom-failed";
        })
    );
  }
  try {
    if (smtpConfig()) {
      jobs.push(
        sendEmail(rec)
          .then(() => "email-sent")
          .catch(error => {
            console.error(`WARN email notification failed for ${rec.id}: ${error.message}`);
            return "email-failed";
          })
      );
    }
  } catch (error) {
    console.error(`WARN email notification config failed for ${rec.id}: ${error.message}`);
    jobs.push(Promise.resolve("email-failed"));
  }
  if (!jobs.length) return ["disabled"];
  return Promise.all(jobs);
}

module.exports = {
  formatEmailMessage,
  formatWeComMarkdown,
  notifyInquiry,
  sendEmail,
  sendWeCom
};
