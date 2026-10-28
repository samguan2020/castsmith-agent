# Engine integration contract

The installed castsmith package is the only asset execution implementation.
requirements.txt pins commit 4c6b0f903d61cd273e63b1e83f8cf926ef4187ef.
Do not copy its source into this repository.

## Interfaces

scripts/studio.py delegates directly to castsmith.server.main and
castsmith.cli.main. Its web command runs scripts/preview.py, a read-only
presentation adapter over the engine's HTTP handlers and installed MotionViewer
module. It serves the workspace layout and pinned local Three.js modules; it
does not copy or replace rendering/asset execution algorithms. POST requests
are rejected, so generation and reviews remain in the agent workflow.
Its init and doctor commands only initialize configuration and inspect
installation prerequisites. validate-request reuses the installed
BuildWorkflow._validate_request and character_generation_prompt functions
without opening a store or contacting providers. Their availability and exact
1024/1000-character boundaries are covered by compatibility tests.
The MCP configuration explicitly selects the workspace interpreter and state.
Web and MCP share SQLite and artifacts; do not write their internals from skills.

| Engine MCP tool | Intended use |
|---|---|
| build_create | Save an unpaid brief; character-first uses motions=[] |
| character_library / character_select | Inspect and explicitly select a working version |
| character_review | Record actual user appearance acceptance/rejection |
| character_feedback | Appearance revision draft or binding diagnosis |
| motion_create | Save a motion pinned to an exact character build |
| motion_feedback | Source revision draft or adaptation diagnosis |
| build_generate | Synchronous paid start/resume after explicit permission |
| build_reprocess | Local-only new version; rig_test=true for binding exercise |
| build_review | Record actual whole-build human quality decision |
| build_status / build_list | Recover persistent facts before deciding next action |
| character_rerig | Deprecated/disabled; do not use as a repair mechanism |

The new wrapper does not register a second MCP server or invent additional
engine tools. Doctor exposes a local capability summary, not a new MCP API.

## Review and generation

Check appearance approval and binding preflight before paid motions.
Automatic screening and human acceptance remain separate.
No skill may supply a human decision based on its own assessment.
Binding/adaptation feedback may create an awaiting-repair record; it is not a
successful repair. Reprocessing reuses inputs and does not promise improvement.

Offer creation immediately after a design (unless design-only was requested).
Before paid motions, display the exact free binding exercise and proactively
offer the saved motion's SayMotion authorization. Review and permission are
independent; retain permission already provided for the unchanged request.
An unavailable-user response is no decision. Pause once, without repeated
internal error text or automated-continuation loops.

## Preview and prompt contracts

The workspace preview has three semantic sections in a preview-only 2-by-2 grid:
character and RigTest above, adapted and source motion below. There are no
form labels, selection or playback controls. Each window retains a title and
short introduction; RigTest explains its arm/leg lifts and inspection purpose.
All animation loops automatically;
the motion pair stays at the same normalized progress. Screen-reader names and
error/empty-state overlays are retained. Quality/review details stay in chat.
Exact IDs and readiness/time evidence are available in viewport data attributes.
GET APIs and artifact access delegate to the engine;
the adapter does not read or write SQLite internals. Version URLs pin character,
rig, motion and clip, with an optional section to scroll into view. A requested
version from another character is an explicit error. Merely opening a tab or
receiving /api/health is not proof that the intended preview loaded visibly.

Prompt preflight precedes draft creation and credit requests. Validate the final
Tripo prompt, including engine-appended constraints, not just description length.
For SayMotion validate the single motion description and schema. Preflight does
not submit provider tasks, reserve credits, truncate input or replace remote
validation. All changed requirements are revalidated before generation.

The current approval flags are not an agent-proof boundary. A future operation
record/approval channel must be implemented in the engine, not simulated in prose.

## Lifecycle and failures

MCP generation blocks until completion. State/provider IDs survive in the store,
but execution runs in the caller process. Closing the browser does not itself
cancel work; killing the worker process is different from disconnecting a viewer.
On interruption inspect existing task journals. Never automatically resubmit an
uncertain paid request. Durable workers, reconciled submission and cancellation
remain future engine work.

## Compatibility changes

When updating requirements.txt:

1. Inspect upstream MCP schemas, runtime requirements, web routes and migrations.
2. Run bootstrap, doctor and the no-paid integration suite on the new commit.
3. Exercise the manual scenarios in a clean state directory.
4. Document new capabilities/limitations before skills rely on them.
5. Do not migrate an existing user's data as part of merely opening the workspace.
