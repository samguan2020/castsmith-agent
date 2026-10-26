---
name: studio-setup
description: "Initialize or troubleshoot the local CastSmith workspace. Use on first use, dependency or Blender failures, MCP connection problems, or credential configuration requests."
---

# Set up the studio

1. Check whether .venv exists. If missing, guide the user to run
   `.\scripts\bootstrap.ps1` in Windows PowerShell. Installation needs Git,
   Python 3.11+ and access to the private engine repository.
2. Run `.\.venv\Scripts\python.exe .\scripts\studio.py doctor`.
   This reports credential presence, never values, and checks the pinned engine
   and Blender version without contacting paid services.
3. Ask the user to edit .env locally if necessary. Never read the file or ask
   them to paste its contents. Do not copy another workspace's .env.
4. Clarify style and target application; save non-secret preferences in
   castsmith.project.json. Do not claim an unimplemented export profile.
5. In VS Code, select CastSmith Studio and start/trust the castsmith MCP server
   from the workspace configuration. Verify character_library can be called.
6. Start the preview only when needed:
   `.\.venv\Scripts\python.exe .\scripts\studio.py web --port 8766`.
   Run it as a user-visible long-lived service. Check /api/health before linking
   http://127.0.0.1:8766. If occupied, use another explicit port; do not kill it.

Report core readiness, generation prerequisites missing and available next steps.
Missing credentials should not prevent design-only work. No provider call is
needed to validate installation.
