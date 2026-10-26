---
name: character-build
description: "Generate or revise a Tripo character from an agreed brief. Use when the user requests actual character creation, appearance regeneration or continuation of a character build."
---

# Build a character

1. Query the library and exact source/draft status. Resolve which character is
   intended; do not replace the working selection silently.
2. Check redacted readiness with studio.py doctor --require-generation character.
3. For a new character create a character-only draft using build_create,
   motions=[]. For revisions use character_feedback in appearance mode with
   the user-reviewed replacement description. Preserve lineage and old versions.
4. Present the exact brief, provider and potential credit use. Obtain explicit
   permission for this generation before calling build_generate with
   paid_confirmed=true. Do not invent an exact price.
5. The tool waits for completion. On interruption inspect build_status and
   provider journal data before considering a retry. Never generate a new
   version just to recover a polling failure.
6. Open the local viewer and identify the exact build. Ask the user to inspect
   anatomy, appearance and clothing. Record their real decision using
   character_review; confirmed=true is only for an explicit human decision.
7. If accepted, select the intended working build explicitly and use rig-diagnose
   before paid motion generation. A successful rig operation is not proof of
   correct anatomy or good weights.

Report build ID, preview address, execution result and pending review.
Rig-incompatible assets need a revised brief, not an unchanged rerig retry.
