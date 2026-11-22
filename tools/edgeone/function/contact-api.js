// EdgeOne Edge Function: validate POST /api/messages before origin storage.
const API_PATH = "/api/messages";
const MAX_BODY = 16 * 1024;
const RATE_MAX = 8;
const RATE_WINDOW_MS = 60 * 1000;
const ALLOWED_ORIGINS = new Set([
  "https://www.maibida.com",
  "https://maibida.com"
]);
const rateMap = new Map();

function json(body, status, extraHeaders) {
  return new Response(JSON.stringify(body), {
    status,
    headers: Object.assign(
      {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff"
      },
      extraHeaders || {}
    )
  });
}

function clientIp(request) {
  return (
    request.headers.get("eo-client-ip") ||
    request.headers.get("x-real-ip") ||
    (request.headers.get("x-forwarded-for") || "").split(",")[0].trim() ||
    "unknown"
  );
}

function rateOk(ip) {
  const now = Date.now();
  const hits = (rateMap.get(ip) || []).filter(
    timestamp => now - timestamp < RATE_WINDOW_MS
  );
  if (hits.length >= RATE_MAX) {
    rateMap.set(ip, hits);
    return false;
  }
  hits.push(now);
  rateMap.set(ip, hits);
  if (rateMap.size > 2000) {
    for (const [key, values] of rateMap) {
      if (!values.length || now - values[values.length - 1] >= RATE_WINDOW_MS) {
        rateMap.delete(key);
      }
    }
  }
  return true;
}

function clean(value, maxLength) {
  return typeof value === "string" ? value.trim().slice(0, maxLength) : "";
}

async function handle(event) {
  event.passThroughOnException();
  const request = event.request;
  const url = new URL(request.url);

  if (url.pathname !== API_PATH) return fetch(request);
  if (request.method !== "POST") {
    return json({ ok: false, error: "Method not allowed" }, 405, {
      Allow: "POST"
    });
  }

  const origin = request.headers.get("origin");
  if (origin && !ALLOWED_ORIGINS.has(origin)) {
    return json(
      { ok: false, error: "Cross-origin submissions are not allowed" },
      403
    );
  }

  const contentType = request.headers.get("content-type") || "";
  if (!/^application\/(?:json|x-www-form-urlencoded)/i.test(contentType)) {
    return json({ ok: false, error: "Expected application/json" }, 415);
  }

  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > MAX_BODY) {
    return json({ ok: false, error: "Payload too large" }, 413);
  }

  const ip = clientIp(request);
  if (!rateOk(ip)) {
    return json(
      { ok: false, error: "Too many submissions, please try again later" },
      429,
      { "Retry-After": "60" }
    );
  }

  const raw = await request.clone().text();
  const encoded = new TextEncoder().encode(raw);
  if (encoded.byteLength > MAX_BODY) {
    return json({ ok: false, error: "Payload too large" }, 413);
  }

  let data;
  try {
    if (/^application\/json/i.test(contentType)) {
      data = JSON.parse(raw);
    } else {
      data = {};
      for (const [key, value] of new URLSearchParams(raw)) data[key] = value;
    }
  } catch (_error) {
    return json({ ok: false, error: "Invalid JSON" }, 400);
  }

  if (clean(data.website, 200)) {
    return json({ ok: true, id: "ignored" }, 200);
  }

  const record = {
    name: clean(data.name, 100),
    email: clean(data.email, 200),
    message: clean(data.message, 4000),
    consent: clean(data.consent, 20).toLowerCase()
  };
  if (!record.name || !record.message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(record.email)) {
    return json({ ok: false, error: "Missing or invalid fields" }, 400);
  }
  if (record.consent !== "yes") {
    return json({ ok: false, error: "Privacy consent is required" }, 400);
  }

  // EdgeOne resolves fetch(request) through the configured origin. The origin
  // remains authoritative for persistence and its own IP-based rate limit.
  const originHeaders = new Headers(request.headers);
  originHeaders.set("X-Maibida-Edge-Client-IP", ip);
  originHeaders.set("X-Real-IP", ip);
  originHeaders.set("X-Forwarded-For", ip);
  const forwarded = new Request(request, { headers: originHeaders });
  const response = await fetch(forwarded);
  const headers = new Headers(response.headers);
  headers.set("Cache-Control", "no-store");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

addEventListener("fetch", event => {
  event.respondWith(handle(event));
});
