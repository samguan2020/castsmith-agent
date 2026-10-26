# Engine integration contract

The installed castsmith package is the only asset execution implementation.
requirements.txt pins commit 4c6b0f903d61cd273e63b1e83f8cf926ef4187ef.
Do not copy its source into this repository.

## Interfaces

scripts/studio.py delegates directly to castsmith.server.main,
castsmith.web.main and castsmith.cli.main. Its init and doctor commands only
initialize configuration and inspect installation prerequisites.
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
