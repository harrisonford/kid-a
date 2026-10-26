"""kid-a: serve the organic-learning brain, frozen at each level it has passed.

    python server.py                     # listens on the Tailscale address, port 8787
    KIDA_HOST=0.0.0.0 KIDA_PORT=8787 ORGANIC_PATH=~/organic-learning python server.py

Endpoints
  GET  /                the chat app (Svelte 5, built from web/ into static/)
  GET  /api/levels      released levels (levels/*.json)
  POST /api/chat        {"level": "L0", "text": "...", "image": "data:image/...;base64,..." | null}
                        -> {"answer", "ticks", "gaze", "gaze_xy", "copied", "ms", "level"}

Brains are frozen: they answer with learn=False, so nothing they hear here
changes them. One brain is kept in memory at a time (they are large).
No database: the chat history lives in the browser.
"""

import base64
import io
import json
import os
import pickle
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np
from PIL import Image

import release

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser(os.environ.get("ORGANIC_PATH", "~/organic-learning")))
SIZE = 64
LOCK = threading.Lock()
LOADED = {"id": None, "brain": None}
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon"}


def tailscale_ip():
    try:
        return subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=5).stdout.split()[0]
    except Exception:  # noqa: BLE001
        return "127.0.0.1"


def levels():
    out = []
    for f in sorted(os.listdir(os.path.join(ROOT, "levels"))):
        if f.endswith(".json"):
            card = json.load(open(os.path.join(ROOT, "levels", f)))
            card["available"] = os.path.exists(os.path.join(ROOT, "models", card["id"] + ".pkl"))
            out.append(card)
    return out


def brain_for(level):
    if LOADED["id"] != level:
        LOADED["brain"] = None  # free the previous one first
        LOADED["brain"] = pickle.load(open(os.path.join(ROOT, "models", level + ".pkl"), "rb"))
        LOADED["id"] = level
        backfill(level, LOADED["brain"])
    return LOADED["brain"]


def backfill(level, brain):
    """Cards released before parameters were counted get the count the first time their brain loads."""
    path = os.path.join(ROOT, "levels", level + ".json")
    card = json.load(open(path))
    if "parameters" not in card:
        card["parameters"] = release.parameters(brain)
        json.dump(card, open(path, "w"), indent=1)


def picture(data_url):
    """What the eye gets: the photo center-cropped to a square, 64x64 RGB."""
    if not data_url:
        return np.zeros((SIZE, SIZE, 3), np.float32)  # eyes closed
    raw = base64.b64decode(data_url.split(",", 1)[1])
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((SIZE, SIZE), Image.BILINEAR)
    return np.asarray(im, np.float32) / 255


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):  # quiet
        pass

    def do_GET(self):
        if self.path == "/api/levels":
            return self._send(200, levels())
        # the built web app (web/ -> npm run build -> static/)
        rel = "index.html" if self.path in ("/", "/index.html") else self.path.split("?", 1)[0].lstrip("/")
        path = os.path.realpath(os.path.join(ROOT, "static", rel))
        if not path.startswith(os.path.join(ROOT, "static") + os.sep) or not os.path.isfile(path):
            return self._send(404, {"error": "not found"})
        ctype = TYPES.get(os.path.splitext(path)[1], "application/octet-stream")
        self._send(200, open(path, "rb").read(), ctype)

    def do_POST(self):
        if self.path != "/api/chat":
            return self._send(404, {"error": "not found"})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            level = req.get("level") or levels()[-1]["id"]
            text = (req.get("text") or "").strip()
            img = picture(req.get("image"))
            t0 = time.time()
            with LOCK:
                brain = brain_for(level)
                said, tick, _, path, _, _ = brain.live(img, text, learn=False, explore=False)
                copied = bool(getattr(brain, "copied", False))
            targets = brain.eye.sensor.targets  # fixation centres in the 64x64 view
            gaze_xy = [[round(float(targets[p][0]) / SIZE, 3), round(float(targets[p][1]) / SIZE, 3)] for p in path]
            self._send(200, {"answer": said or "", "ticks": int(tick), "gaze": [int(p) for p in path], "gaze_xy": gaze_xy, "copied": copied,
                             "ms": int(1000 * (time.time() - t0)), "level": level})
        except Exception as e:  # noqa: BLE001
            self._send(500, {"error": str(e)})


if __name__ == "__main__":
    host = os.environ.get("KIDA_HOST") or tailscale_ip()
    port = int(os.environ.get("KIDA_PORT", 8787))
    print(f"kid-a on http://{host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
