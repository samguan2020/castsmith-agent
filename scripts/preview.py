"""Read-only presentation shell over the installed engine's renderer and HTTP APIs."""

from __future__ import annotations

import argparse
import base64
import hashlib
import re
from pathlib import Path

import castsmith.web as engine_web
from castsmith.config import Settings
from castsmith.store import SQLiteStore
from castsmith.workflow import BuildWorkflow

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
THREE = ROOT / "node_modules" / "three"


def static_files() -> dict[str, tuple[Path, str]]:
    javascript = "text/javascript; charset=utf-8"
    return {
        "/": (WEB / "index.html", "text/html; charset=utf-8"),
        "/static/preview.js": (WEB / "preview.js", javascript),
        "/static/viewer.js": (engine_web.WORKBENCH_HTML.parent / "viewer.js", javascript),
        "/static/THREE-LICENSE.txt": (THREE / "LICENSE", "text/plain; charset=utf-8"),
        **{
            f"/vendor/three/{name}": (THREE / name, javascript)
            for name in (
                "build/three.module.js",
                "build/three.core.js",
                "examples/jsm/loaders/GLTFLoader.js",
                "examples/jsm/controls/OrbitControls.js",
                "examples/jsm/utils/BufferGeometryUtils.js",
            )
        },
    }


class PreviewHandler(engine_web.WorkbenchHandler):
    def send_header(self, keyword: str, value: str) -> None:
        if keyword.lower() == "content-security-policy":
            html = (WEB / "index.html").read_text(encoding="utf-8")
            import_map = re.search(r'<script type="importmap">([\s\S]*?)</script>', html)
            if import_map is None:
                raise ValueError("Preview import map is missing")
            digest = base64.b64encode(
                hashlib.sha256(import_map[1].encode("utf-8")).digest()
            ).decode("ascii")
            value = value.replace("script-src 'self'", f"script-src 'self' 'sha256-{digest}'")
        super().send_header(keyword, value)

    def do_GET(self) -> None:
        if not self._validate_host():
            self._send_error(400, "Invalid Host header")
            return
        route = self.path.split("?", 1)[0]
        resource = static_files().get(route)
        if resource:
            self._send_file(*resource)
        elif self.path in {"/api/health", "/api/builds", "/api/library"} or (
            self.path.startswith("/api/builds/")
        ):
            super().do_GET()
        else:
            self._send_error(404, "Preview resource not found")

    def do_POST(self) -> None:
        self._send_error(405, "Read-only preview; use the chat workflow for generation and reviews")


class PreviewServer(engine_web.WorkbenchServer):
    def __init__(self, address: tuple[str, int], workflow: BuildWorkflow, settings: Settings):
        super().__init__(address, workflow, settings)
        self.RequestHandlerClass = PreviewHandler


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("127.0.0.1",), default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        raise ValueError("--port must be between 0 and 65535")
    for path, _ in static_files().values():
        if not path.is_file():
            raise ValueError(f"Preview dependency missing: {path.name}. Run npm ci in the workspace.")
    settings = Settings.from_env()
    workflow = BuildWorkflow(SQLiteStore(settings.state_root))
    with PreviewServer((args.host, args.port), workflow, settings) as server:
        print(f"CastSmith Preview: http://{args.host}:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping CastSmith Preview.")
