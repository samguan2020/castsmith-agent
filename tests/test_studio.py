from __future__ import annotations

import contextlib
import importlib.metadata
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("studio", ROOT / "scripts" / "studio.py")
assert SPEC is not None and SPEC.loader is not None
studio = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(studio)


class WorkspaceTests(unittest.TestCase):
    def test_character_preflight_checks_final_prompt_at_exact_limit(self):
        from castsmith.workflow import character_generation_prompt

        overhead = len(character_generation_prompt(""))
        request = {
            "asset_id": "test-dancer", "profile": "threejs-humanoid-lite", "motions": [],
            "description": "x" * (1024 - overhead),
        }
        with patch("castsmith.generation.GenerationEngine.start", side_effect=AssertionError("paid")):
            result = studio.validate_request(request, "character")
            self.assertEqual(result["character_prompt"]["characters"], 1024)
            self.assertEqual(result["character_prompt"]["description_limit"], 1024 - overhead)
            self.assertFalse(result["provider_called"])
            request["description"] += "x"
            with self.assertRaisesRegex(ValueError, "1024"):
                studio.validate_request(request, "character")

    def test_motion_preflight_checks_1000_characters_and_schema_without_changing_request(self):
        request = {
            "asset_id": "test-dancer", "profile": "threejs-humanoid-lite", "description": "Dancer",
            "motions": [{"name": "dance", "description": "x" * 1000, "duration_seconds": 8, "loop": True}],
        }
        before = json.dumps(request)
        self.assertEqual(studio.validate_request(request, "motion")["motion_prompts"][0]["characters"], 1000)
        self.assertEqual(json.dumps(request), before)
        request["motions"][0]["description"] += "x"
        with self.assertRaisesRegex(ValueError, "1000"):
            studio.validate_request(request, "motion")
        request["motions"][0]["description"] = "Dance"
        request["motions"][0]["loop"] = "yes"
        with self.assertRaisesRegex(ValueError, "boolean"):
            studio.validate_request(request, "motion")

    def test_preflight_reports_invalid_file_and_request_without_success_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON object"):
                studio.validate_request_file(path, "character")
            with self.assertRaisesRegex(ValueError, "non-secret"):
                studio.validate_request_file(Path(directory) / ".env", "character")
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                self.assertEqual(studio.main([
                    "validate-request", "--kind", "character", "--file", str(path),
                ]), 1)
            self.assertIn("JSON object", output.getvalue())

    def test_preflight_cli_succeeds_without_credentials_or_asset_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "request.json"
            path.write_text(json.dumps({
                "asset_id": "test-dancer", "description": "A red-haired adult street dancer",
                "profile": "threejs-humanoid-lite", "motions": [],
            }), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "studio.py"),
                 "validate-request", "--kind", "character", "--file", str(path)],
                env={
                    **os.environ, "CASTSMITH_ENV_FILE": str(root / "absent.env"),
                    "CASTSMITH_STATE_ROOT": str(root / "state"),
                },
                capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["valid"])
            self.assertFalse(report["provider_called"])
            self.assertFalse((root / "state").exists())

    def test_workflow_handoffs_and_unavailable_user_contract(self):
        agent = (ROOT / ".github" / "agents" / "castsmith-studio.agent.md").read_text()
        self.assertIn("two independent choices", agent)
        self.assertIn("pause\nonce", agent)
        self.assertIn("Revalidate any edited request", agent)
        for skill in ("character-design", "character-build", "motion-build"):
            content = (ROOT / ".github" / "skills" / skill / "SKILL.md").read_text()
            self.assertIn("validate-request", content)
            self.assertRegex(content.lower(), r"proactively offer")
        for name in ("evals.json", "scenarios.json"):
            suite = json.loads((ROOT / "evals" / name).read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(suite.get("evals", suite.get("scenarios", []))), 6)

    def test_pin_is_full_and_installed_commit_matches(self):
        pin = studio.expected_commit()
        self.assertRegex(pin, r"^[0-9a-f]{40}$")
        installed = importlib.metadata.distribution("castsmith")
        provenance = json.loads(installed.read_text("direct_url.json"))
        self.assertEqual(provenance["vcs_info"]["commit_id"], pin)

    def test_init_is_exclusive_and_preserves_existing_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.example").write_text("TRIPO_API_KEY=\n", encoding="utf-8")
            with patch.object(studio, "ROOT", root), contextlib.redirect_stdout(io.StringIO()):
                studio.initialize()
                self.assertEqual((root / ".env").read_text(), "TRIPO_API_KEY=\n")
                (root / ".env").write_text("private-test-sentinel", encoding="utf-8")
                studio.initialize()
                self.assertEqual((root / ".env").read_text(), "private-test-sentinel")

    def test_environment_defaults_do_not_depend_on_cwd_and_preserve_overrides(self):
        with patch.dict(os.environ, {}, clear=True):
            studio.configure_environment()
            self.assertEqual(os.environ["CASTSMITH_STATE_ROOT"], str(ROOT / ".castsmith"))
            os.environ["CASTSMITH_STATE_ROOT"] = "explicit-state"
            studio.configure_environment()
            self.assertEqual(os.environ["CASTSMITH_STATE_ROOT"], "explicit-state")

    def test_doctor_redacts_values_and_checks_blender_version(self):
        from castsmith.config import Settings

        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "blender.exe"
            executable.touch()
            settings = Settings(
                Path(directory), Path(directory) / "state",
                tripo_api_key="secret-tripo-sentinel",
                saymotion_api_url="https://secret-host-sentinel",
                saymotion_client_id="secret-id-sentinel",
                saymotion_client_secret="secret-client-sentinel",
                blender_executable=str(executable),
            )
            for version, expected in (("3.6.23", True), ("4.2.0", False)):
                output = io.StringIO()
                result = subprocess.CompletedProcess([], 0, stdout=f"Blender {version}\n", stderr="")
                with patch("castsmith.config.Settings.from_env", return_value=settings), \
                        patch.object(studio.subprocess, "run", return_value=result), \
                        contextlib.redirect_stdout(output):
                    code = studio.doctor("motion")
                self.assertNotIn("sentinel", output.getvalue())
                report = json.loads(output.getvalue())
                self.assertEqual(report["blender"]["supported"], expected)
                self.assertEqual(code, 0 if expected else 1)
                self.assertFalse(report["provider_authentication_checked"])

    def test_doctor_missing_engine_is_explicit(self):
        output = io.StringIO()
        with patch.object(
            studio.importlib.metadata, "distribution",
            side_effect=importlib.metadata.PackageNotFoundError("castsmith"),
        ), contextlib.redirect_stdout(output):
            self.assertEqual(studio.doctor(), 1)
        self.assertFalse(json.loads(output.getvalue())["core_ready"])

    def test_customization_contract(self):
        expected = {
            "studio-setup", "character-design", "character-build", "rig-diagnose",
            "motion-build", "motion-diagnose", "asset-deliver",
        }
        files = list((ROOT / ".github" / "skills").glob("*/SKILL.md"))
        self.assertEqual({path.parent.name for path in files}, expected)
        for path in files:
            content = path.read_text(encoding="utf-8")
            frontmatter = yaml.safe_load(content.split("---", 2)[1])
            self.assertEqual(frontmatter["name"], path.parent.name)
            self.assertIsInstance(frontmatter["description"], str)
            self.assertTrue(frontmatter["description"])
            self.assertLess(len(content.splitlines()), 500)
        agent_files = list((ROOT / ".github" / "agents").glob("*.agent.md"))
        self.assertEqual(len(agent_files), 1)
        agent = yaml.safe_load(agent_files[0].read_text().split("---", 2)[1])
        self.assertEqual(agent["agents"], [])
        self.assertIn("castsmith/*", agent["tools"])
        config = json.loads((ROOT / ".vscode" / "mcp.json").read_text())
        self.assertEqual(list(config["servers"]), ["castsmith"])
        self.assertIn("CASTSMITH_STATE_ROOT", config["servers"]["castsmith"]["env"])
        self.assertFalse((ROOT / "src" / "castsmith").exists())


class EngineIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_mcp_handshake_draft_and_persisted_status(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        with tempfile.TemporaryDirectory() as directory:
            environment = {
                **os.environ,
                "CASTSMITH_ENV_FILE": str(Path(directory) / "absent.env"),
                "CASTSMITH_WORKSPACE_ROOT": directory,
                "CASTSMITH_STATE_ROOT": str(Path(directory) / "state"),
            }
            parameters = StdioServerParameters(
                command=sys.executable,
                args=[str(ROOT / "scripts" / "studio.py"), "mcp"],
                env=environment,
            )
            async with (
                stdio_client(parameters) as (reader, writer),
                ClientSession(reader, writer) as session,
            ):
                await session.initialize()
                tools = {tool.name for tool in (await session.list_tools()).tools}
                self.assertTrue({
                    "build_create", "build_status", "character_library",
                    "motion_create", "build_reprocess",
                }.issubset(tools))
                draft = await session.call_tool("build_create", {
                    "asset_id": "test-traveler", "description": "A low-poly traveler",
                    "motions": [],
                })
                self.assertFalse(draft.isError, draft)
                payload = json.loads(draft.content[0].text)
                result = await session.call_tool("build_status", {"build_id": payload["id"]})
                self.assertFalse(result.isError, result)
                saved = json.loads(result.content[0].text)
                self.assertEqual(saved["id"], payload["id"])
                self.assertNotEqual(saved["status"], "succeeded")
                self.assertFalse(saved.get("provider_tasks"))
                library = await session.call_tool("character_library", {})
                self.assertFalse(library.isError, library)
            self.assertTrue((Path(directory) / "state" / "castsmith.sqlite3").is_file())


class WebIntegrationTests(unittest.TestCase):
    def test_read_only_preview_routes_renderer_modules_and_exact_version_links(self):
        from castsmith.config import Settings
        from castsmith.store import SQLiteStore
        from castsmith.workflow import BuildWorkflow

        spec = importlib.util.spec_from_file_location("preview", ROOT / "scripts" / "preview.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = Settings(root, root / "state")
            workflow = BuildWorkflow(SQLiteStore(settings.state_root))
            with module.PreviewServer(("127.0.0.1", 0), workflow, settings) as server:
                thread = threading.Thread(target=server.serve_forever)
                thread.start()
                try:
                    base = f"http://127.0.0.1:{server.server_port}"
                    with urllib.request.urlopen(base + "/?character=exact&section=rig", timeout=10) as response:
                        html = response.read().decode("utf-8")
                        self.assertIn("sha256-", response.headers["Content-Security-Policy"])
                        self.assertNotIn("'unsafe-inline'", response.headers["Content-Security-Policy"].split("style-src")[0])
                        self.assertEqual(html.count("<section "), 3)
                    for route in module.static_files():
                        with urllib.request.urlopen(base + route, timeout=10) as response:
                            self.assertGreater(len(response.read()), 0)
                    with urllib.request.urlopen(base + "/api/builds", timeout=10) as response:
                        self.assertEqual(json.load(response)["builds"], [])
                    for route, status in (("/api/builds", 405), ("/api/builds/fake/review", 405)):
                        request = urllib.request.Request(base + route, data=b"{}", method="POST")
                        with self.assertRaises(urllib.error.HTTPError) as caught:
                            urllib.request.urlopen(request, timeout=10)
                        self.assertEqual(caught.exception.code, status)
                    for route in ("/api/config", "/vendor/three/package.json", "/static/../.env"):
                        with self.assertRaises(urllib.error.HTTPError) as caught:
                            urllib.request.urlopen(base + route, timeout=10)
                        self.assertEqual(caught.exception.code, 404)
                    self.assertEqual(workflow.list(), [])
                finally:
                    server.shutdown()
                    thread.join(timeout=10)
                    self.assertFalse(thread.is_alive())

    def test_real_viewer_health_and_bundle_without_provider_access(self):
        from castsmith.config import Settings
        from castsmith.store import SQLiteStore
        from castsmith.web import WorkbenchServer
        from castsmith.workflow import BuildWorkflow

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = Settings(root, root / "state")
            workflow = BuildWorkflow(SQLiteStore(settings.state_root))
            with WorkbenchServer(("127.0.0.1", 0), workflow, settings) as server:
                thread = threading.Thread(target=server.serve_forever)
                thread.start()
                try:
                    base = f"http://127.0.0.1:{server.server_port}"
                    with urllib.request.urlopen(base + "/api/health", timeout=10) as response:
                        self.assertEqual(json.load(response)["status"], "ok")
                    with urllib.request.urlopen(base + "/", timeout=10) as response:
                        html = response.read().decode("utf-8")
                    self.assertIn("CastSmith", html)
                    script = re.search(r'src="(/static/[^"]+\.js)"', html)
                    self.assertIsNotNone(script)
                    with urllib.request.urlopen(base + script[1], timeout=10) as response:
                        self.assertGreater(len(response.read()), 1000)
                finally:
                    server.shutdown()
                    thread.join(timeout=10)
                    self.assertFalse(thread.is_alive())


if __name__ == "__main__":
    unittest.main()
