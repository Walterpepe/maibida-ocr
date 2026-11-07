// Enforce the retention period promised in the Privacy Policy (24 months).
//
//   node tools/purge-expired-messages.js --dry-run   # report only
//   node tools/purge-expired-messages.js            # rewrite, keeping live rows
//
// Schedule it (cron / systemd timer) so the promise in privacy.*.html is
// actually honoured. The file lives outside the web root by design.
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const file = path.resolve(root, '..', 'maibida-ocr-rebuilt_messages', 'messages.ndjson');
const dry = process.argv.includes('--dry-run');

if (!fs.existsSync(file)) {
  console.log('No message store yet:', file);
  process.exit(0);
}

const lines = fs.readFileSync(file, 'utf8').split('\n').filter(x => x.trim());
const now = Date.now();
const kept = [];
let expired = 0;
let invalid = 0;

for (const line of lines) {
  let rec;
  try { rec = JSON.parse(line); } catch (_) { invalid++; kept.push(line); continue; }
  const until = Date.parse(rec.retentionUntil || '');
  if (!Number.isFinite(until)) { kept.push(line); continue; }  // keep unknown-age rows
  if (until <= now) expired++;
  else kept.push(line);
}

console.log(JSON.stringify({
  file, dryRun: dry, total: lines.length,
  expired, kept: kept.length, invalidJson: invalid
}, null, 2));

if (!dry && expired > 0) {
  const tmp = file + '.tmp';
  fs.writeFileSync(tmp, kept.length ? kept.join('\n') + '\n' : '', 'utf8');
  try { fs.chmodSync(tmp, 0o600); } catch (_) { /* Windows ACLs */ }
  fs.renameSync(tmp, file);
  console.log('Purged', expired, 'expired record(s).');
}

// A record can also be deleted on request under the data-subject rights
// described in the Privacy Policy; filter by rec.email before rewriting.
