"use strict";

const fs = require("fs");
const https = require("https");
const net = require("net");
const tls = require("tls");
const crypto = require("crypto");
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

class SmtpSession {
  constructor(socket, timeoutMs) {
    this.socket = socket;
    this.timeoutMs = timeoutMs;
    this.buffer = "";
    this.lines = [];
    this.responses = [];
    this.waiters = [];
    this.error = null;
    this.attach(socket);
  }

  attach(socket) {
    socket.setTimeout(this.timeoutMs);
    socket.on("data", chunk => this.onData(chunk));
    socket.on("timeout", () => socket.destroy(new Error("SMTP timed out")));
    socket.on("error", error => this.fail(error));
    socket.on("close", () => {
      if (this.waiters.length && !this.error) {
        this.fail(new Error("SMTP connection closed"));
      }
    });
  }

  detach() {
    this.socket.removeAllListeners("data");
    this.socket.removeAllListeners("timeout");
    this.socket.removeAllListeners("error");
    this.socket.removeAllListeners("close");
  }

  fail(error) {
    this.error = error;
    while (this.waiters.length) this.waiters.shift().reject(error);
    this.socket.destroy();
  }

  onData(chunk) {
    this.buffer += chunk.toString("utf8");
    let newline;
    while ((newline = this.buffer.indexOf("\n")) >= 0) {
      const line = this.buffer.slice(0, newline).replace(/\r$/, "");
      this.buffer = this.buffer.slice(newline + 1);
      const match = /^(\d{3})([ -])(.*)$/.exec(line);
      if (!match) continue;
      this.lines.push(line);
      if (match[2] === "-") continue;
      const response = {
        code: Number(match[1]),
        lines: this.lines.slice()
      };
      this.lines = [];
      const waiter = this.waiters.shift();
      if (waiter) waiter.resolve(response);
      else this.responses.push(response);
    }
  }

  nextResponse() {
    if (this.error) return Promise.reject(this.error);
    if (this.responses.length) return Promise.resolve(this.responses.shift());
    return new Promise((resolve, reject) => {
      this.waiters.push({ resolve, reject });
    });
  }

  async command(line, expectedCodes) {
    if (this.waiters.length) throw new Error("SMTP command overlap");
    this.socket.write(`${line}\r\n`);
    const response = await this.nextResponse();
    if (!expectedCodes.includes(response.code)) {
      throw new Error(`SMTP ${response.code}: ${response.lines.join(" | ")}`);
    }
    return response;
  }

  upgrade() {
    this.detach();
    const secureSocket = tls.connect({
      socket: this.socket,
      servername: this.host,
      rejectUnauthorized: true
    });
    this.socket = secureSocket;
    this.attach(secureSocket);
  }

  close() {
    this.socket.end();
  }
}

async function sendEmail(rec) {
  const config = smtpConfig();
  if (!config) return;
  const timeoutMs = Number(process.env.MAIBIDA_NOTIFY_TIMEOUT_MS || 15000);
  const implicitTls = config.port === 465;
  const socket = implicitTls
    ? tls.connect({
        host: config.host,
        port: config.port,
        servername: config.host,
        rejectUnauthorized: true
      })
    : net.connect({ host: config.host, port: config.port });
  const session = new SmtpSession(socket, timeoutMs);
  session.host = config.host;

  try {
    const greeting = await session.nextResponse();
    if (greeting.code !== 220) {
      throw new Error(`SMTP ${greeting.code}: ${greeting.lines.join(" | ")}`);
    }
    await session.command("EHLO maibida.local", [250]);
    if (!implicitTls) {
      await session.command("STARTTLS", [220]);
      session.upgrade();
      await session.command("EHLO maibida.local", [250]);
    }

    await session.command("AUTH LOGIN", [334]);
    await session.command(Buffer.from(config.user).toString("base64"), [334]);
    await session.command(Buffer.from(config.pass).toString("base64"), [235]);
    await session.command(`MAIL FROM:<${config.from}>`, [250]);
    for (const recipient of config.recipients) {
      await session.command(`RCPT TO:<${recipient}>`, [250, 251]);
    }
    await session.command("DATA", [354]);

    const message = formatEmailMessage(rec, config.from, config.recipients);
    session.socket.write(`${message.replace(/\r\n$/, "")}\r\n.\r\n`);
    const response = await session.nextResponse();
    if (response.code !== 250) {
      throw new Error(`SMTP ${response.code}: ${response.lines.join(" | ")}`);
    }
    await session.command("QUIT", [221]);
  } finally {
    session.close();
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
