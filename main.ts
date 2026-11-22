// main.ts — hand in THE WORLD TODAY for make.fun's news-image-20261122.
// Validates entry.png (PNG signature, 680x1024, at most 1 MiB, whole file
// ending in IEND) and copies it to the output directory the grader reads
// from (MAKEFUN_OUTPUT_DIR outside the grader, /output inside it).
// Node 22, standard library only.
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, resolve } from "node:path";

const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576;
const WANT_W = 680;
const WANT_H = 1024;

function fail(msg: string): never {
  throw new Error(`entry.png invalid: ${msg}`);
}

const here = resolve(import.meta.dirname);
const src = join(here, "entry.png");
const buf = readFileSync(src);

if (buf.length > MAX_BYTES) fail(`too large: ${buf.length} bytes (max ${MAX_BYTES})`);
if (buf.length < 8 || !buf.subarray(0, 8).equals(PNG_SIG)) fail("bad PNG signature");
if (buf.length < 33 || buf.toString("ascii", 12, 16) !== "IHDR") fail("no IHDR chunk");
const w = buf.readUInt32BE(16);
const h = buf.readUInt32BE(20);
if (w !== WANT_W || h !== WANT_H) fail(`dimensions ${w}x${h}, expected ${WANT_W}x${WANT_H}`);
const tail = buf.subarray(buf.length - 12);
if (tail.readUInt32BE(0) !== 0 || tail.toString("ascii", 4, 8) !== "IEND") {
  fail("file does not end with an IEND chunk");
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const dest = join(outDir, "entry.png");
copyFileSync(src, dest);
// Verify the copy landed whole: same bytes, same size.
const copied = readFileSync(dest);
const digest = (b: Buffer) => createHash("sha256").update(b).digest("hex");
if (copied.length !== buf.length || digest(copied) !== digest(buf)) {
  fail("copied file does not match entry.png");
}
const size = statSync(dest).size;
console.log(`entry.png ${w}x${h} ${size} bytes sha256 ${digest(buf)} -> ${dest}`);
