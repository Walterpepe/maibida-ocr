#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const source = fs.readFileSync(
  path.join(__dirname, "function", "contact-api.js"),
  "utf8"
);
let listener;
let originCalls = 0;

const context = {
  URL,
  URLSearchParams,
  Request,
  Response,
  Headers,
  TextEncoder,
  fetch: async request => {
    originCalls += 1;
    if (!request.headers.get("x-real-ip")) throw new Error("missing client IP");
    if (!request.headers.get("content-type")) {
      throw new Error("origin forwarding dropped Content-Type");
    }
    return new Response(JSON.stringify({ ok: true, id: "origin-test" }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  },
  addEventListener: (name, handler) => {
    if (name === "fetch") listener = handler;
  }
};
vm.runInNewContext(source, context, {
  filename: "tools/edgeone/function/contact-api.js"
});

async function invoke(request) {
  let responsePromise;
  listener({
    request,
    passThroughOnException: () => {},
    respondWith: value => {
      responsePromise = Promise.resolve(value);
    }
  });
  return responsePromise;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const url = "https://www.maibida.com/api/messages";
  const json = {
    "Content-Type": "application/json",
    "EO-Client-IP": "203.0.113.10"
  };

  let response = await invoke(new Request(url, { method: "GET" }));
  assert(response.status === 405, "GET should return 405");
  assert(response.headers.get("cache-control") === "no-store", "405 must be no-store");

  response = await invoke(
    new Request(url, {
      method: "POST",
      headers: json,
      body: JSON.stringify({
        name: "Bot",
        email: "bot@example.com",
        message: "spam",
        consent: "yes",
        website: "https://spam.example"
      })
    })
  );
  assert(response.status === 200, "honeypot should fake success");
  assert(originCalls === 0, "honeypot must not reach origin");

  response = await invoke(
    new Request(url, {
      method: "POST",
      headers: json,
      body: JSON.stringify({
        name: "Test",
        email: "test@example.com",
        message: "Hello",
        consent: "no"
      })
    })
  );
  assert(response.status === 400, "missing consent should return 400");
  assert(originCalls === 0, "invalid consent must not reach origin");

  response = await invoke(
    new Request(url, {
      method: "POST",
      headers: json,
      body: JSON.stringify({
        name: "Test",
        email: "test@example.com",
        message: "Hello",
        consent: "yes"
      })
    })
  );
  assert(response.status === 200, "valid submission should reach origin");
  assert(originCalls === 1, "valid submission should call origin exactly once");
  assert(response.headers.get("cache-control") === "no-store", "200 must be no-store");

  console.log("PASS Edge Function validation and origin forwarding");
}

main().catch(error => {
  console.error(`FAIL ${error.message}`);
  process.exit(1);
});
