#!/usr/bin/env node
/**
 * Dependency-free static dev server for the Learning Voyage site.
 *
 *   npm run dev                       # serves on http://localhost:7100/
 *   npm run dev -- --port 8080        # custom port
 *   npm run dev -- --host 0.0.0.0     # custom host
 *
 * Forwards --host/--port CLI arguments; PORT and HOST env vars also work.
 */
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL(".", import.meta.url));

const args = process.argv.slice(2);
const argValue = (name, fallback) => {
  const i = args.indexOf(name);
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback;
};

const PORT = Number(argValue("--port", process.env.PORT || 7100));
const HOST = argValue("--host", process.env.HOST || "localhost");

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".ico": "image/x-icon",
  ".json": "application/json; charset=utf-8",
  ".webmanifest": "application/manifest+json",
  ".xml": "application/xml; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
};

const server = createServer(async (req, res) => {
  try {
    let pathname = decodeURIComponent(new URL(req.url, `http://${req.headers.host}`).pathname);
    if (pathname.endsWith("/")) pathname += "index.html";
    const filePath = normalize(join(ROOT, pathname));
    if (!filePath.startsWith(ROOT)) {
      res.writeHead(403).end("Forbidden");
      return;
    }
    const body = await readFile(filePath);
    res.writeHead(200, { "Content-Type": MIME[extname(filePath).toLowerCase()] || "application/octet-stream" });
    res.end(body);
  } catch {
    try {
      const notFound = await readFile(join(ROOT, "404.html"));
      res.writeHead(404, { "Content-Type": MIME[".html"] });
      res.end(notFound);
    } catch {
      res.writeHead(404).end("Not found");
    }
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Learning Voyage dev server → http://${HOST}:${PORT}/`);
  console.log(`AutoQA case study        → http://${HOST}:${PORT}/work/autoqa-foundation.html`);
});
