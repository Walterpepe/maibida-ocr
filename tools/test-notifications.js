#!/usr/bin/env node
"use strict";

const {
  formatEmailMessage,
  formatWeComMarkdown,
  notifyInquiry
} = require("./notifications");

const record = {
  id: "test-record",
  receivedAt: "2026-11-24T13:45:00.000Z",
  name: "测试客户",
  email: "customer@example.com",
  phone: "+86 138 0000 0000",
  company: "Example Ltd.",
  country: "CN",
  source: "/contact.html",
  message: "请提供视觉传感器选型建议。"
};

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const markdown = formatWeComMarkdown(record);
  assert(markdown.includes(record.name), "WeCom message missing name");
  assert(Buffer.byteLength(markdown, "utf8") <= 4096, "WeCom message too large");
  const longMarkdown = formatWeComMarkdown({
    ...record,
    message: "测".repeat(2500)
  });
  assert(
    Buffer.byteLength(longMarkdown, "utf8") <= 4096,
    "truncated WeCom message is too large"
  );

  const email = formatEmailMessage(
    { ...record, message: "First line\n.spam-like line" },
    "noreply@maibida.com",
    ["sales@maibida.com"]
  );
  assert(email.includes("Reply-To: customer@example.com"), "email Reply-To missing");
  assert(email.includes("Content-Type: text/plain"), "email content type missing");
  assert(email.includes("\r\n..spam-like line"), "email dot-stuffing missing");

  const result =
    process.env.MAIBIDA_NOTIFY_LIVE === "1"
      ? await notifyInquiry(record)
      : ["preview-only"];
  console.log(JSON.stringify({ markdown, emailBytes: Buffer.byteLength(email), result }, null, 2));
}

main().catch(error => {
  console.error(`FAIL ${error.message}`);
  process.exit(1);
});
