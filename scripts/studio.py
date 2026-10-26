"""Workspace launcher; all asset execution belongs to the pinned CastSmith engine."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def expected_commit() -> str:
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    match = re.search(r"^castsmith @ git\+\S+@([0-9a-f]{40})$", text, re.MULTILINE)
    if match is None:
        raise ValueError("requirements.txt must pin one full engine commit")
    return match.group(1)


def configure_environment() -> None:
    os.environ.setdefault("CASTSMITH_ENV_FILE", str(ROOT / ".env"))
    os.environ.setdefault("CASTSMITH_WORKSPACE_ROOT", str(ROOT))
    os.environ.setdefault("CASTSMITH_STATE_ROOT", str(ROOT / ".castsmith"))


def initialize() -> None:
    target = ROOT / ".env"
    try:
        with target.open("xb") as stream:
            stream.write((ROOT / ".env.example").read_bytes())
    except FileExistsError:
        print("Existing .env preserved.")
    else:
        print("Created .env template. Edit credentials locally; do not paste them into chat.")


def doctor(require_generation: str | None = None) -> int:
    checks: dict[str, object] = {
        "python_supported": sys.version_info >= (3, 11),
        "expected_engine_commit": expected_commit(),
    }
    try:
        distribution = importlib.metadata.distribution("castsmith")
    except importlib.metadata.PackageNotFoundError:
        checks["engine_installed"] = False
        print(json.dumps({"core_ready": False, "checks": checks}, indent=2))
        return 1
    checks["engine_installed"] = True
    direct_url = json.loads(distribution.read_text("direct_url.json") or "{}")
    commit = direct_url.get("vcs_info", {}).get("commit_id")
    checks["engine_commit_matches"] = commit == checks["expected_engine_commit"]

    from castsmith.config import Settings

    settings = Settings.from_env()
    blender: dict[str, object] = {"supported": False, "status": "missing"}
    if settings.blender_executable and Path(settings.blender_executable).is_file():
        try:
            result = subprocess.run(
                [settings.blender_executable, "--version"],
                capture_output=True, text=True, timeout=20, check=False,
            )
        except subprocess.TimeoutExpired:
            blender["status"] = "version_check_timed_out"
        except OSError:
            blender["status"] = "version_check_could_not_start"
        else:
            match = re.search(r"^Blender (\d+)\.(\d+)\.(\d+)", result.stdout, re.MULTILINE)
            supported = (
                result.returncode == 0 and match is not None
                and match.groups()[:2] == ("3", "6")
            )
            blender.update({
                "supported": supported,
                "status": "supported" if supported else "unsupported_or_failed",
                "version": match[0] if match else None,
            })
    # Only presence is returned. Do not expose settings, URLs or subprocess output.
    credentials = {
        "TRIPO_API_KEY": bool(settings.tripo_api_key),
        "SAYMOTION_API_URL": bool(settings.saymotion_api_url),
        "SAYMOTION_CLIENT_ID": bool(settings.saymotion_client_id),
        "SAYMOTION_CLIENT_SECRET": bool(settings.saymotion_client_secret),
    }
    generation_ready = {
        "character": bool(blender["supported"] and credentials["TRIPO_API_KEY"]),
        "motion": bool(blender["supported"] and all(
            credentials[key] for key in (
                "SAYMOTION_API_URL", "SAYMOTION_CLIENT_ID", "SAYMOTION_CLIENT_SECRET"
            )
        )),
    }
    core_ready = bool(checks["python_supported"] and checks["engine_commit_matches"])
    print(json.dumps({
        "core_ready": core_ready,
        "checks": checks,
        "blender": blender,
        "credential_presence": credentials,
        "generation_prerequisites_present": generation_ready,
        "provider_authentication_checked": False,
        "capabilities": {
            "mcp": True, "web_preview": True, "local_rig_test": True,
            "local_reprocessing": True, "generation_is_synchronous": True,
            "durable_jobs": False, "general_weight_repair": False,
            "agent_proof_approval": False,
        },
    }, indent=2))
    return 0 if core_ready and (
        require_generation is None or generation_ready[require_generation]
    ) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Create .env only if absent; never read existing credentials")
    check = commands.add_parser("doctor", help="Redacted, provider-free environment diagnostics")
    check.add_argument("--require-generation", choices=("character", "motion"))
    commands.add_parser("mcp", help="Run the engine's stdio MCP server")
    web = commands.add_parser("web", help="Run the engine's loopback-only asset viewer")
    web.add_argument("--port", type=int, default=8766)
    commands.add_parser("library")
    commands.add_parser("builds")
    status = commands.add_parser("status")
    status.add_argument("build_id")
    args = parser.parse_args(argv)
    configure_environment()
    try:
        if args.command == "init":
            initialize()
            return 0
        if args.command == "doctor":
            return doctor(args.require_generation)
        if args.command == "mcp":
            from castsmith.server import main as serve
            serve()
            return 0
        if args.command == "web":
            from castsmith.web import main as web_main
            web_main(["--host", "127.0.0.1", "--port", str(args.port)])
            return 0
        from castsmith.cli import main as cli_main
        return cli_main([args.command] + (
            [args.build_id] if args.command == "status" else []
        ))
    except ModuleNotFoundError as error:
        print(f"Dependency unavailable ({error.name}). Run scripts\\bootstrap.ps1.", file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f"castsmith-agent: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
