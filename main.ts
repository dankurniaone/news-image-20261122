// news-image-20261122 entrypoint (Node 22, standard library only).
//
// The entry is the broadsheet in entry.png, drawn by tools/render22.py
// from news.json and three CC-licensed file photos. This program does
// not draw anything: it checks the image the repository ships against
// the competition's limits, then writes it to the grader's output
// directory as entry.png. It reads no clock and no network, and it
// writes nothing but that one file, so running it twice produces the
// same bytes both times.
//
// Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const SOURCE = new URL("./entry.png", import.meta.url);
const DEST_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const DEST = join(DEST_DIR, "entry.png");

// Competition limits for news-image-20261122.
const LIMITS = {
  maxBytes: 1024 * 1024,
  maxSide: 1024,
  width: 680,
  height: 1024,
};

// PNG magic: 89 50 4E 47 0D 0A 1A 0A.
const SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
// A whole PNG ends with the IEND chunk: length 0, type "IEND",
// CRC ae 42 60 82.
const TRAILER = Buffer.from([
  0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
]);

function fail(reason) {
  throw new Error(`entry.png rejected: ${reason}`);
}

function pngSize(bytes) {
  // The IHDR chunk holds width at bytes 16..19 and height at 20..23,
  // both big-endian unsigned 32-bit.
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

function validate(bytes) {
  if (bytes.length > LIMITS.maxBytes) {
    fail(`is ${bytes.length} bytes, over the ${LIMITS.maxBytes} cap`);
  }
  if (bytes.length < SIGNATURE.length ||
      !bytes.subarray(0, SIGNATURE.length).equals(SIGNATURE)) {
    fail("does not start with the PNG signature");
  }
  if (bytes.length < TRAILER.length ||
      !bytes.subarray(bytes.length - TRAILER.length).equals(TRAILER)) {
    fail("does not end with the PNG IEND chunk");
  }
  const { width, height } = pngSize(bytes);
  if (width > LIMITS.maxSide || height > LIMITS.maxSide) {
    fail(`is ${width}x${height}, over the ${LIMITS.maxSide}x${LIMITS.maxSide} cap`);
  }
  if (width !== LIMITS.width || height !== LIMITS.height) {
    fail(`is ${width}x${height}, expected ${LIMITS.width}x${LIMITS.height}`);
  }
}

function run() {
  if (!existsSync(SOURCE)) {
    fail("missing from the repository");
  }
  const bytes = readFileSync(SOURCE);
  validate(bytes);
  mkdirSync(DEST_DIR, { recursive: true });
  writeFileSync(DEST, bytes);
  console.log(`wrote ${DEST} (${bytes.length} bytes, ${LIMITS.width}x${LIMITS.height})`);
}

run();
