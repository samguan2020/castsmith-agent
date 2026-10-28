---
name: character-build
description: "Generate or revise a Tripo character from an agreed brief. Use when the user requests actual character creation, appearance regeneration or continuation of a character build."
---

# Build a character

1. Query the library and exact source/draft status. Resolve which character is
   intended; do not replace the working selection silently.
2. Check redacted readiness with the workspace interpreter:
   .\.venv\Scripts\python.exe .\scripts\studio.py doctor --require-generation character.
   Do not use global Python; it may resolve a different engine.
   Run studio.py validate-request --kind character --file <request.json> before
   saving. The 1024-character limit includes automatically appended anatomy
   constraints. Require a passing local preflight, not a failed generation call.
3. For a new character create a character-only draft using build_create,
   motions=[]. For revisions use character_feedback in appearance mode with
   the user-reviewed replacement description. Preserve lineage and old versions.
4. Present the exact brief, provider and potential credit use. Obtain explicit
   permission for this generation before calling build_generate with
   paid_confirmed=true. Proactively offer this authorization; reuse a creation
   approval already given after the same brief/provider/credit notice.
   Ask directly in chat: 请输入“同意”，或告诉我需要修改什么。
   Do not mention confirmation buttons or require a form.
   Do not invent an exact price. Missing/unavailable-user responses are not
   approval: leave one next action and pause, without repeated blocker messages.
5. The tool waits for completion. On interruption inspect build_status and
   provider journal data before considering a retry. Never generate a new
   version just to recover a polling failure.
6. Automatically open the local viewer with browser tools and identify the exact
   build. Ask the user to inspect anatomy, appearance and clothing, then use
   the same concise chat wording. Record their real decision using
   character_review with decision=accepted or rejected; confirmed=true is only
   for an explicit human decision. Use ?character=<build-id>&section=character,
   bring the preview into view and verify the model loaded before requesting
   review. Do not equate opening an invisible tab with displaying the asset.
7. If accepted, select the intended working build explicitly and immediately use
   rig-diagnose to run/reuse the free test, without another permission question.
   Preserve the initially saved motion specification for the next handoff.
   The pinned engine blocks RigTest before appearance acceptance; do not mark
   appearance accepted automatically to bypass this limitation. A successful
   rig operation is not proof of correct anatomy or good weights.

Report build ID, preview address, execution result and pending review.
Rig-incompatible assets need a revised brief, not an unchanged rerig retry.
