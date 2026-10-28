# CastSmith Agent

A local, agent-first character asset studio: **one Copilot agent, seven skills,
one CastSmith MCP server, and an optional local web workbench**.

Describe a character or a motion in chat. The agent uses the CastSmith engine to
create, inspect and iterate assets; the browser shows the character and animation.
You supply your own Tripo and SayMotion credentials.

Project-owned agent prompts, skills, confirmation wording, UI and documentation
are in English. Archived conversation excerpts are English translations, not
verbatim transcripts. Original build records and third-party engine messages
are preserved rather than rewritten by this presentation shell.

## Recorded example

[From chat to an aerobics character](docs/examples/ponytail-aerobics/README.md)
records a real session: two character candidates, appearance feedback, a free
binding test, an eight-second SayMotion animation and verified local delivery.
It includes actual UI screenshots, the production conversation and disclosed
quality warnings. [Watch the recorded MP4 on GitHub Pages](https://samguan2020.github.io/castsmith-agent/):
the video plays remotely without a local service. The site is a static archive,
not a hosted 3D viewer; original models and credentials remain local.

## Status and repository boundary

This is the first integration release, not an autonomous repair engine.
The Python execution engine is installed from an immutable commit of
[castsmith-studio](https://github.com/samguan2020/castsmith-studio).
No provider adapter, Blender worker, database implementation or 3D renderer is
copied into this repository. A small read-only presentation shell uses the
installed engine's MotionViewer and artifact APIs. Engine fixes belong upstream;
update the dependency pin only after compatibility tests.

**This product-shell repository is public; its pinned execution-engine dependency
is still private.** Installation requires authorized access to that upstream
repository. This is not yet a publicly installable distribution; the public
showcase does not grant access to the private dependency.

| Works through the existing engine | Not implemented in this release |
|---|---|
| Character library, drafts and generation | General skin-weight or cloth repair |
| Motion drafts, generation and retargeting | IK foot locking or semantic motion validation |
| Local rig tests and source-motion reprocessing | Durable independent job worker and cancellation |
| Character, RigTest and synchronized source/adapted previews | Candidate-to-candidate comparison |
| Exact-version preview URLs | General motion or skin-weight repair |
| Persisted build records and user reviews | Agent-proof approval channel or enforced budget |
| Existing GLB, preview and report downloads | New engine-specific exporters or packaging engine |

Generation MCP calls are synchronous. Build state is persisted, but a killed
process does not leave a guaranteed running job. The agent must inspect saved
state before any retry. The workspace viewer is read-only: generation,
authorization and review decisions stay in chat.

## Requirements

- Windows, Git, Python 3.11+, and VS Code with GitHub Copilot Chat.
- Your own Copilot account/authorization and network access.
- Blender **3.6.x** for processing. Other versions are rejected.
- Your own provider accounts and credits for paid generation.
- Git authentication with read access to the private engine repository.
  Use your credential manager or `gh auth setup-git` for the intended account.
  Never embed tokens in dependency URLs or paste them into chat.

Node.js/npm is needed only to install the local preview's pinned Three.js modules
with `npm ci`. Python/MCP generation does not require Node.js. A database server
and a local LLM are not required. The 3D renderer comes from the pinned engine;
no CDN or external model hosting is used.

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

### Creation and authorization handoffs

After a design, the agent proactively offers to create the character, including
the Tripo credit notice. Decisions are requested directly in chat:
Please reply 'I agree', or tell me what you would like to change.
There are no confirmation forms, numbered-answer requirements or explanations
about unavailable buttons. A clear natural-language affirmative is also valid.
The preview remains read-only; decisions stay in chat.

Character and motion requirements are captured together. The motion's name,
description, duration and loop are kept in a validated session-local request;
the paid character draft still uses `motions: []`. The agent does not ask for
an unchanged motion again at the next stage.

**Current engine limitation:** the pinned engine rejects RigTest until the
user accepts the exact character's appearance. Character generation therefore
opens an appearance question first; acceptance automatically starts/reuses the
free RigTest without a separate test-permission question. Showing character
and RigTest together *before* any appearance decision requires an upstream
engine change. The agent must not fabricate acceptance to achieve this.

The exact character-and-RigTest preview is opened with browser tools and checked
for loading and advancing animation. When automation is unavailable, an explicit
user report that the exact test is visible and playing is human evidence, not
an agent-verified result. Binding acceptance and SayMotion credit permission
use one explicitly scoped chat confirmation: before asking, the agent explains
that agreement accepts the exact binding result and disclosed risks, and
authorizes the saved motion's potential SayMotion credit use. A single
affirmative to that combined scope supplies both decisions; a partial
affirmative supplies only the named decision. Their records remain separate.
Permission already granted for an
unchanged draft is not requested again. Once both choices are affirmative, the
agent starts the saved motion immediately without another "continue" prompt.

After generation, the agent opens the pinned source/adapted comparison,
automatically copies the saved assets to a fresh `exports/` subfolder and offers
downloads plus a modification question. Delivery does not wait for final
quality acceptance or silently mark a result accepted. New paid revisions
still need permission. Restart/reselect the agent in a new chat after changing
its configuration; an existing session may retain previous instructions and tools.

An unavailable or unanswered confirmation is not permission. The agent leaves
one concise next action and pauses rather than repeating internal tool messages
or approval requests. Autopilot does not supply human review or payment consent.

### Prompt preflight (no credits)

Before saving a generation draft, validate the complete non-secret request:

```powershell
.\.venv\Scripts\python.exe .\scripts\studio.py validate-request --kind character --file request.json
.\.venv\Scripts\python.exe .\scripts\studio.py validate-request --kind motion --file motion-request.json
```

The JSON uses the engine's request fields: `asset_id`, `description`, `profile`
and `motions`. Character-first requests use `motions: []`; a motion request has
exactly one clip with `name`, `description`, `duration_seconds` and `loop`.
Keep these temporary request files in the session workspace, not in Git.

The command reuses installed engine validation without reading credentials,
creating assets or contacting providers. Tripo's 1024-character limit includes
the appended anatomy constraints; the report gives the effective description
budget. Each SayMotion description is limited to 1000 characters. Shorten
redundant wording and revalidate after edits; never silently truncate a brief.
Exit code 0 proves local request compliance, not provider authentication or
guaranteed remote acceptance.

## Local web preview

Install the viewer's locked local modules once, then start it in a separate
PowerShell terminal:

```powershell
npm ci
.\.venv\Scripts\python.exe .\scripts\studio.py web --port 8766
```

Open <http://127.0.0.1:8766>. Port 8766 avoids the existing studio's default 8765.
Use another explicit port if occupied. Stop this server with Ctrl+C.

The page contains four preview windows in a viewport-filling 2-by-2 grid:

| Top left | Top right |
|---|---|
| Character 3D preview | RigTest |
| Adapted character motion | SayMotion source motion |

RigTest and motion play automatically on repeat. Source and adapted motion stay
synchronized by normalized progress. Each window retains its title and short
introduction. RigTest explains that it raises arms and legs for inspecting joint
deformation and clothing intersections, not dancing. There are no form labels,
dropdowns, buttons, timelines, version captions or report panels; orbit/zoom
remains available directly on each window.
Empty versions and loading errors appear only when relevant, inside the windows.
Quality reports and acceptance decisions remain in chat, not hidden approvals.

Exact build IDs remain in the URL and each window's `data-build-id` attribute,
with `data-state` and animation `data-time`/`data-progress` for verification.
The server rejects POST requests; it
cannot generate assets or record a review through this UI. Empty versions and
missing/failed sources show explicit messages. Viewing does not call paid APIs.
Generation and reviews remain in the agent workflow. The footer provides
downloads for the current character GLB/PNG/manifest and selected creative
motion GLB, saved SayMotion source, quality report and motion manifest. Only
artifacts actually listed for those exact versions are linked; RigTest is
excluded. Downloads do not imply quality acceptance.

Generated files live in `.castsmith/artifacts/<build-id>/`. The final character
is `character.glb`; a creative clip uses `motion-<index>.glb` with its saved
`source-motion-<index>.glb` and `quality-<index>.json`. This local state is
untracked. The agent automatically makes a local handoff after motion generation.
The same no-paid copying command can be run manually:

```powershell
.\.venv\Scripts\python.exe .\scripts\studio.py deliver --character <character-build-id> --motion <motion-build-id> --clip 0
```

It verifies saved artifact sizes/hashes and copies the character, selected
creative clip, available source/preview, manifests and required quality report
into a new `exports/` subfolder, preserving build-specific filenames. It never
overwrites earlier deliveries or includes RigTest as a game animation.
`delivery.json` records exact IDs, clip, inventory and real review/quality state.
The command copies existing artifacts only; it is not a new exporter or repair
engine. Unreviewed generated files can be delivered with their warnings intact.

Exact-version URLs use
`/?character=<character-build-id>&rig=<rig-test-id>&motion=<motion-build-id>&clip=0&section=motion`.
The optional `section` is `character`, `rig` or `motion` and scrolls that section
into view. Invalid or mismatched IDs produce an error, not another asset's
preview. Select versions through chat/exact URLs, not dropdowns; this does not
change the working character in the engine. Existing servers must be restarted
to use server changes (HTML/JS updates only need a refresh); if an
old server occupies the port, launch on another explicit port without killing it.

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
npm test
```

The suite checks the launcher, safe initialization, dependency provenance,
customization/tool contracts, exact prompt-length boundaries, safe exact-version
delivery and the engine's appearance-before-RigTest gate, a real stdio MCP
handshake/draft/status flow, and real HTTP preview/renderer routes served against temporary state. It does not
prove agent routing quality, paid provider access or asset visual quality.
Behavioral prompts for manual agent acceptance are in
[evals/scenarios.json](evals/scenarios.json).
The initial three offline planning scenarios in [evals/evals.json](evals/evals.json)
were also exercised with and without the skills. Both passed the nine coarse
safety assertions; this is a smoke check, not evidence of a measured improvement
or a live Copilot/provider end-to-end run. It does not test automatic skill discovery.
