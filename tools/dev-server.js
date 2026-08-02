#!/usr/bin/env node
/**
 * Zero-dependency static dev server for the learning.voyage site.
 *
 * Usage:
 *   node tools/dev-server.js [--host 127.0.0.1] [--port 8000]
 *   npm run dev -- --port 7100
 *
 * Honors --host/--host=, --port/--port=, -p, and the HOST/PORT environment
 * variables so preview tooling can forward its own address.
 */

const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".json": "application/json; charset=utf-8",
  ".webmanifest": "application/manifest+json",
  ".xml": "application/xml; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
};

function argValue(flag, shortFlag) {
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === flag || (shortFlag && argv[i] === shortFlag)) return argv[i + 1];
    if (argv[i].startsWith(`${flag}=`)) return argv[i].slice(flag.length + 1);
  }
  return undefined;
}

const HOST = argValue("--host") || process.env.HOST || "127.0.0.1";
const PORT = Number(argValue("--port", "-p") || process.env.PORT || 8000);

function resolvePath(urlPath) {
  const decoded = decodeURIComponent(urlPath.split("?")[0]);
  const normalized = path.normalize(decoded).replace(/^([/\\])+/, "");
  const filePath = path.join(ROOT, normalized);
  if (!filePath.startsWith(ROOT)) return null; // path traversal guard
  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    return path.join(filePath, "index.html");
  }
  return filePath;
}

const server = http.createServer((req, res) => {
  const filePath = resolvePath(req.url || "/");
  if (filePath && fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    res.writeHead(200, { "Content-Type": MIME[path.extname(filePath).toLowerCase()] || "application/octet-stream" });
    fs.createReadStream(filePath).pipe(res);
    return;
  }
  const notFound = path.join(ROOT, "404.html");
  res.writeHead(404, { "Content-Type": "text/html; charset=utf-8" });
  if (fs.existsSync(notFound)) {
    fs.createReadStream(notFound).pipe(res);
  } else {
    res.end("404");
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Learning Voyage dev server: http://${HOST}:${PORT}/`);
});
