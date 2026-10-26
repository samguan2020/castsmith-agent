# CastSmith Agent

A local, agent-first character asset studio: **one Copilot agent, seven skills,
one CastSmith MCP server, and an optional local web workbench**.

Describe a character or a motion in chat. The agent uses the CastSmith engine to
create, inspect and iterate assets; the browser shows the character and animation.
You supply your own Tripo and SayMotion credentials.

## Status and repository boundary

This is the first integration release, not an autonomous repair engine.
The Python execution engine is installed from an immutable commit of
[castsmith-studio](https://github.com/samguan2020/castsmith-studio).
No provider adapter, Blender worker, database implementation or viewer is copied
into this repository. Engine fixes belong upstream; update the dependency pin
only after compatibility tests.

**Both repositories are currently private.** Installation requires access to both.
This is not yet a publicly installable distribution. Making this repository
public alone will not make its private dependency available.

| Works through the existing engine | Not implemented in this release |
|---|---|
| Character library, drafts and generation | General skin-weight or cloth repair |
| Motion drafts, generation and retargeting | IK foot locking or semantic motion validation |
| Local rig tests and source-motion reprocessing | Durable independent job worker and cancellation |
| Character and source/adapted motion previews | Candidate side-by-side view and version deep links |
| Persisted build records and user reviews | Agent-proof approval channel or enforced budget |
| Existing GLB, preview and report downloads | New engine-specific exporters or packaging engine |

Generation MCP calls are synchronous. Build state is persisted, but a killed
process does not leave a guaranteed running job. The agent must inspect saved
state before any retry. The inherited web workbench still has generation forms;
it has not yet been reduced to a read-only preview interface.

## Requirements

- Windows, Git, Python 3.11+, and VS Code with GitHub Copilot Chat.
- Your own Copilot account/authorization and network access.
- Blender **3.6.x** for processing. Other versions are rejected.
- Your own provider accounts and credits for paid generation.
- Git authentication with read access to the private engine repository.
  Use your credential manager or `gh auth setup-git` for the intended account.
  Never embed tokens in dependency URLs or paste them into chat.

Node.js, npm, a database server and a local LLM are not required for this wrapper.
The engine includes the prebuilt browser viewer.

## Install

Clone this repository and open PowerShell in its root:

```powershell
.\scripts\bootstrap.ps1
```

If PowerShell blocks local scripts, use a process-scoped execution policy only
if permitted by your organization's policy. Do not change machine-wide policy.

For development with an existing engine clone:

```powershell
.\scripts\bootstrap.ps1 -EngineRepository D:\Repos\castsmith-studio
```

This still installs the **pinned commit**, not the clone's current working tree.
It does not copy that clone's credentials, database or generated assets.
Bootstrap creates an isolated .venv and an empty .env template. Re-running it
preserves an existing .env and local asset state.

Edit .env locally with your provider credentials and Blender executable path.
Never paste it into the agent. Set the SayMotion API host for your account;
the portal URL is not necessarily an API URL.

```powershell
.\.venv\Scripts\python.exe .\scripts\studio.py doctor
.\.venv\Scripts\python.exe .\scripts\studio.py doctor --require-generation character
.\.venv\Scripts\python.exe .\scripts\studio.py doctor --require-generation motion
```

Doctor reports presence, not secret values. It does not authenticate with
providers or submit tasks. Default success means the Python/engine installation
is valid, not that paid generation is ready. The generation modes additionally
require Blender 3.6.x and the relevant configuration.

## Use in VS Code

1. Open **this folder**, not the engine folder, in VS Code.
2. Trust the workspace only if you trust its code and configuration.
3. Select **CastSmith Studio** in the chat agent picker.
4. Start/trust the `castsmith` server from the workspace MCP configuration when
   prompted. Confirm its tools are listed.
5. Describe your goal, for example:

   > Design a low-poly young traveler with a blue jacket. First show me the brief;
   > do not spend credits yet.

   > Generate the agreed character, then help me inspect the binding before we
   > create a walk animation.

   > Inspect the selected walk's right arm around two seconds. Compare source and
   > adapted motion. Do not regenerate anything.

The agent uses the current model selected by the user; no model is hard-coded.
The initial configuration targets VS Code Copilot on Windows, not every agent
host. Claude Code and other platforms need separate integration testing.

## Local web preview

In a separate PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe .\scripts\studio.py web --port 8766
```

Open <http://127.0.0.1:8766>. Port 8766 avoids the existing studio's default 8765.
Use another explicit port if occupied. Stop this server with Ctrl+C.

The existing viewer supports textured characters, orbit/zoom, animation playback,
the SayMotion source/adapted-character switch, versions, reports and downloads.
Confirm displayed build IDs before reviewing. No guarantee of per-version deep
links or side-by-side comparison is made in this release.
Viewing existing assets does not call paid generation services.

MCP and the web launcher use the same workspace-local .env and .castsmith store.
Launchers default to this repository regardless of terminal working directory;
explicit CASTSMITH environment overrides are advanced configuration and apply
only to the process receiving them. Set them consistently for both interfaces.
Do not point a new workspace at old state without understanding engine compatibility.

## Skills

| Skill | Responsibility |
|---|---|
| studio-setup | Install/configure/check the workspace |
| character-design | Develop and save an unpaid character brief |
| character-build | Consent-gated character generation and review |
| rig-diagnose | Free binding tests, evidence and limits |
| motion-build | Pinned-character motion creation and generation |
| motion-diagnose | Source/target diagnosis and supported local processing |
| asset-deliver | Exact-version inventory and existing downloads |

Skills guide decisions; they do not implement missing processing algorithms.
See [the engine contract](docs/engine-contract.md) for the actual tool boundary.

## Safety and data

- .env, .castsmith, .venv and exports are untracked. Updates must not overwrite
  user credentials or assets. Existing character/motion versions remain preserved.
- Paid operations require an actual user decision for the exact request. The
  current engine accepts a boolean confirmation: this is **not** a tamper-proof
  authorization system. Skills are guidance, not a security boundary.
- Copilot and terminal tools may access local files. Ignoring .env in Git is not
  credential isolation from the host. Do not treat this workspace as a sandbox.
- Local processing does not imply offline operation. Providers receive submitted
  requests/assets; cloud agent services receive context according to host policy.
- Report screening limitations and user acceptance separately. A generated file
  is not proof of correct anatomy, skinning, motion semantics or engine fitness.

## Validation

No paid credentials or existing user assets are needed:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The suite checks the launcher, safe initialization, dependency provenance,
customization contracts, a real stdio MCP handshake/draft/status flow, and a
real HTTP viewer/static bundle served against temporary state. It does not
prove agent routing quality, paid provider access or asset visual quality.
Behavioral prompts for manual agent acceptance are in
[evals/scenarios.json](evals/scenarios.json).
The initial three offline planning scenarios in [evals/evals.json](evals/evals.json)
were also exercised with and without the skills. Both passed the nine coarse
safety assertions; this is a smoke check, not evidence of a measured improvement
or a live Copilot/provider end-to-end run. It does not test automatic skill discovery.
