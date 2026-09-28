#!/usr/bin/env python
"""Pocket File Server: a small, authenticated Flask file server for Termux."""

import getpass
import hmac
import logging
import os
import shutil
import stat
import time
from pathlib import Path
from urllib.parse import quote
from html import escape

from flask import Flask, Response, abort, request, send_from_directory

ROOT = Path(os.environ.get("SD_SERVER_ROOT", "/storage/sdcard1")).expanduser().resolve()
HOST = "0.0.0.0"
PORT = int(os.environ.get("SD_SERVER_PORT", "8000"))

if not ROOT.is_dir():
    raise SystemExit(
        f"Shared directory not found: {ROOT}\n"
        "Check the SD_SERVER_ROOT setting and Termux storage permissions."
    )

USERNAME = input("Server username: ").strip()
PASSWORD = getpass.getpass("Set server password: ")

if not USERNAME or not PASSWORD:
    raise SystemExit("Username and password must not be empty.")

app = Flask(__name__)
started_at = time.monotonic()
request_count = 0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)


@app.before_request
def authenticate():
    auth = request.authorization
    valid = (
        auth is not None
        and hmac.compare_digest(auth.username or "", USERNAME)
        and hmac.compare_digest(auth.password or "", PASSWORD)
    )
    if not valid:
        return Response(
            "Authentication required",
            401,
            {"WWW-Authenticate": 'Basic realm="Pocket File Server"'},
        )


@app.after_request
def count_and_log_request(response):
    global request_count
    request_count += 1
    app.logger.info(
        "%s %s -> %s",
        request.remote_addr or "unknown client",
        request.method,
        response.status_code,
    )
    return response


def render_page(title, content):
    elapsed = int(time.monotonic() - started_at)
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"

    try:
        total, used, free = shutil.disk_usage(ROOT)
        storage_text = (
            f"{free / (1024 ** 3):.1f} GB free / "
            f"{total / (1024 ** 3):.1f} GB total"
        )
        storage_state = "Available"
    except OSError:
        storage_text = "Storage information unavailable"
        storage_state = "Check storage"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} - Pocket File Server</title>
<style>
* {{ box-sizing: border-box; }}
body {{
    font: 16px system-ui, sans-serif;
    max-width: 950px;
    margin: 30px auto;
    padding: 0 16px;
    background: #111827;
    color: #e5e7eb;
}}
header, .item, .stat {{
    padding: 14px;
    margin: 10px 0;
    background: #1f2937;
    border-radius: 10px;
}}
header h1 {{ margin: 0 0 8px; font-size: 1.8rem; }}
small, .muted {{ color: #9ca3af; }}
a {{ color: #7dd3fc; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px;
    margin: 14px 0 24px;
}}
.stat {{ margin: 0; min-width: 0; }}
.stat-label {{ color: #9ca3af; font-size: .85rem; }}
.stat-value {{
    font-size: 1.2rem;
    font-weight: 650;
    overflow-wrap: anywhere;
    margin-top: 4px;
}}
.online {{ color: #86efac; }}
.item {{ overflow-wrap: anywhere; }}
.section-title {{ margin-top: 26px; }}
</style>
</head>
<body>
<header>
<h1>📱 Pocket File Server</h1>
<small>Android · HTTP · Port {PORT}</small>
</header>

<h2>📊 Server Monitor</h2>
<div class="stats">
  <div class="stat">
    <div class="stat-label">Server status</div>
    <div class="stat-value online">● Online</div>
  </div>
  <div class="stat">
    <div class="stat-label">Uptime</div>
    <div class="stat-value">{uptime}</div>
  </div>
  <div class="stat">
    <div class="stat-label">HTTP requests</div>
    <div class="stat-value">{request_count}</div>
    <small>Since server started</small>
  </div>
  <div class="stat">
    <div class="stat-label">SD card</div>
    <div class="stat-value">{escape(storage_state)}</div>
    <small>{escape(storage_text)}</small>
  </div>
</div>

<h2 class="section-title">📂 File Browser</h2>
{content}
<footer class="muted"><p>Pocket File Server · Local network only</p></footer>
</body>
</html>"""


@app.route("/")
def index():
    return browse("")


@app.route("/browse/", defaults={"relpath": ""})
@app.route("/browse/<path:relpath>")
def browse(relpath):
    directory = (ROOT / relpath).resolve()

    try:
        directory.relative_to(ROOT)
    except ValueError:
        abort(403)

    try:
        if not directory.is_dir():
            abort(404)
    except OSError:
        abort(403)

    entries = []
    try:
        for item in directory.iterdir():
            try:
                info = item.stat()
                is_directory = stat.S_ISDIR(info.st_mode)
            except OSError:
                # Skip entries the Android storage layer will not allow us to inspect.
                continue
            entries.append((is_directory, item, info.st_size))
    except OSError:
        abort(403)

    entries.sort(key=lambda entry: (not entry[0], entry[1].name.lower()))
    rows = []

    if relpath:
        parent = str(Path(relpath).parent)
        if parent == ".":
            parent = ""
        rows.append(
            f'<div class="item"><a href="/browse/{quote(parent, safe="/")}">'
            "⬅ Parent folder</a></div>"
        )

    for is_directory, item, size in entries:
        relative = item.relative_to(ROOT).as_posix()
        safe_name = escape(item.name)
        encoded_path = quote(relative, safe="/")

        if is_directory:
            rows.append(
                f'<div class="item">📁 '
                f'<a href="/browse/{encoded_path}">{safe_name}/</a></div>'
            )
        else:
            rows.append(
                f'<div class="item">📄 '
                f'<a href="/file/{encoded_path}">{safe_name}</a> '
                f'<small>({size:,} bytes)</small></div>'
            )

    content = f"<h3>📁 /{escape(relpath)}</h3>" + "".join(rows)
    return render_page("Files", content)


@app.route("/file/<path:relpath>")
def get_file(relpath):
    target = (ROOT / relpath).resolve()

    try:
        target.relative_to(ROOT)
    except ValueError:
        abort(403)

    try:
        if not target.is_file():
            abort(404)
    except OSError:
        abort(403)

    return send_from_directory(
        str(ROOT),
        relpath,
        as_attachment=False,
        conditional=True,
    )


if __name__ == "__main__":
    print(f"Pocket File Server: http://<PHONE-IP>:{PORT}")
    print(f"Shared directory: {ROOT}")
    print("Keep this server on a trusted local network.")
    print("Press Ctrl+C to stop.")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
