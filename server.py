"""A loopback-only, no-upload, no-storage application server."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
from engine import LocalEncoder, InputError, analyze

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
FILES = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"), "/style.css": ("style.css", "text/css")}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Deliberately never log request bodies or brief text.
        return

    def allowed(self):
        origins = {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}
        return self.headers.get("Host") in {x.removeprefix("http://") for x in origins} and self.headers.get("Origin", next(iter(origins))) in origins

    def respond(self, status, body, mime="application/json"):
        if isinstance(body, dict):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", mime + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.allowed():
            return self.respond(403, {"error": "Loopback origin required"})
        if self.path == "/api/health":
            return self.respond(200, {"ready": True, "model": "all-MiniLM-L6-v2", "revision": self.server.encoder.revision})
        if self.path == "/api/example":
            return self.respond(200, json.loads((ROOT / "examples.json").read_text(encoding="utf-8")))
        if self.path in FILES:
            name, mime = FILES[self.path]
            return self.respond(200, (WEB / name).read_bytes(), mime)
        return self.respond(404, {"error": "Not found"})

    def do_POST(self):
        if not self.allowed():
            return self.respond(403, {"error": "Loopback origin required"})
        if self.path != "/api/analyze":
            return self.respond(404, {"error": "Not found"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 65536:
                raise InputError("Request must be below 64 KiB.")
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise InputError("JSON required.")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise InputError("JSON object required.")
            result = analyze(self.server.encoder, data.get("brief"), data.get("requests"))
            return self.respond(200, result)
        except (InputError, ValueError, UnicodeDecodeError) as exc:
            return self.respond(400, {"error": str(exc)})
        except Exception:
            return self.respond(500, {"error": "Analysis failed. No result was produced."})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8793)
    args = parser.parse_args()
    encoder = LocalEncoder()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.encoder = encoder
    print(f"BriefTrace ready: http://127.0.0.1:{args.port} (local inference; no text storage)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
