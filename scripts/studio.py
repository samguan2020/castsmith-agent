"""Workspace launcher; all asset execution belongs to the pinned CastSmith engine."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from castsmith.workflow import BuildWorkflow

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


def validate_request(request: dict, kind: str) -> dict:
    from castsmith.workflow import BuildWorkflow, character_generation_prompt

    if not isinstance(request, dict):
        raise ValueError("Request must be a JSON object")
    normalized = BuildWorkflow._validate_request(request)
    if kind == "character":
        if normalized["motions"]:
            raise ValueError("Character-first requests must use motions=[]")
        prompt = character_generation_prompt(normalized["description"])
        character = {
            "characters": len(prompt),
            "limit": 1024,
            "description_limit": 1024 - len(character_generation_prompt("")),
        }
    elif kind == "motion":
        if len(normalized["motions"]) != 1:
            raise ValueError("Motion requests must contain exactly one clip")
        character = None
    else:
        raise ValueError("Expected character or motion")
    return {
        "valid": True,
        "kind": kind,
        "character_prompt": character,
        "motion_prompts": [
            {"name": motion["name"], "characters": len(motion["description"]), "limit": 1000}
            for motion in normalized["motions"]
        ],
        "provider_called": False,
    }


def validate_request_file(path: Path, kind: str) -> dict:
    if path.suffix.lower() != ".json":
        raise ValueError("Preflight accepts only a non-secret .json request file")
    return validate_request(json.loads(path.read_text(encoding="utf-8-sig")), kind)


def deliver_assets(
    workflow: BuildWorkflow, exports_root: Path, character_id: str, motion_id: str, clip: int,
) -> dict:
    character = workflow.get(character_id)
    motion = workflow.get(motion_id)
    if (
        character.get("kind") != "character" or character.get("character_build_id")
        or character.get("status") != "succeeded"
    ):
        raise ValueError("Delivery requires an exact completed character build")
    if (
        motion.get("kind") not in ("motion", "reprocess")
        or motion.get("status") != "succeeded"
        or motion.get("character_build_id") != character_id
    ):
        raise ValueError("Delivery requires a completed creative motion pinned to this character, not RigTest")
    if type(clip) is not int or not 0 <= clip < len(motion["request"]["motions"]):
        raise ValueError("Delivery clip index is out of range")
    state_root = workflow.store.root.resolve()
    artifacts_root = (state_root / "artifacts").resolve()
    if not artifacts_root.is_relative_to(state_root):
        raise ValueError("Artifact root must stay inside the local state directory")
    files = []
    for build, required, optional in (
        (character, ["character.glb", "manifest.json"], ["preview.png"]),
        (motion, [f"motion-{clip}.glb", f"quality-{clip}.json", "manifest.json"],
         [f"source-motion-{clip}.glb"]),
    ):
        artifacts = {item["name"]: item for item in build["artifacts"]}
        for name in required + [name for name in optional if name in artifacts]:
            if name not in artifacts:
                raise ValueError(f"Required delivery artifact missing: {build['id']} / {name}")
            source = (artifacts_root / build["id"] / name).resolve()
            if not source.is_relative_to(artifacts_root) or not source.is_file():
                raise ValueError(f"Unsafe or missing delivery artifact: {build['id']} / {name}")
            expected = artifacts[name]
            with source.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            if (
                source.stat().st_size != expected.get("size_bytes")
                or digest != expected.get("sha256")
            ):
                raise ValueError(f"Delivery artifact integrity check failed: {build['id']} / {name}")
            files.append((source, {
                "build_id": build["id"], "name": name,
                "path": f"{build['id']}/{name}",
                "size_bytes": expected["size_bytes"], "sha256": expected["sha256"],
            }))
    report = {
        "character_build_id": character_id, "motion_build_id": motion_id, "clip": clip,
        "appearance_review": character.get("appearance_review", {"status": "pending"}),
        "motion_review": motion.get("review", {"status": "pending"}),
        "quality_status": motion.get("quality", {}).get("status", "not_checked"),
        "limitations": "Existing files only; delivery is not quality acceptance or a validated game-engine import.",
        "files": [entry for _, entry in files],
    }
    exports_root.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix=f"{motion_id}-clip{clip}-", dir=exports_root))
    try:
        for source, entry in files:
            target = destination / entry["build_id"] / entry["name"]
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(source, target)
            with target.open("rb") as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != entry["sha256"]:
                    raise ValueError(f"Copied artifact integrity check failed: {entry['name']}")
        (destination / "delivery.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    except (OSError, ValueError):
        shutil.rmtree(destination)
        raise
    return {"directory": str(destination.resolve()), **report}


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
            "rig_test_requires_appearance_acceptance": True,
            "local_delivery": True,
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
    web = commands.add_parser("web", help="Run the read-only local three-section preview")
    web.add_argument("--port", type=int, default=8766)
    validate = commands.add_parser("validate-request", help="Validate prompts locally without credits")
    validate.add_argument("--kind", required=True, choices=("character", "motion"))
    validate.add_argument("--file", required=True, type=Path)
    deliver = commands.add_parser("deliver", help="Copy exact saved assets to a fresh exports folder; no generation")
    deliver.add_argument("--character", required=True)
    deliver.add_argument("--motion", required=True)
    deliver.add_argument("--clip", type=int, default=0)
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
        if args.command == "validate-request":
            print(json.dumps(validate_request_file(args.file, args.kind), indent=2))
            return 0
        if args.command == "deliver":
            from castsmith.config import Settings
            from castsmith.store import SQLiteStore, StoreError
            from castsmith.workflow import BuildWorkflow

            try:
                workflow = BuildWorkflow(SQLiteStore(Settings.from_env().state_root))
                result = deliver_assets(workflow, ROOT / "exports", args.character, args.motion, args.clip)
            except StoreError as error:
                raise ValueError(str(error)) from error
            print(json.dumps(result, indent=2))
            return 0
        if args.command == "mcp":
            from castsmith.server import main as serve
            serve()
            return 0
        if args.command == "web":
            from preview import main as web_main
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
