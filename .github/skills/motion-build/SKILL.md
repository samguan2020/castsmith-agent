---
name: motion-build
description: "Create or revise a SayMotion animation and adapt it to an existing character. Use for walk, idle, attack, wave or other actual motion generation, with explicit paid consent."
---

# Build a motion

1. Resolve and pin the exact character version. Verify appearance acceptance
   and binding preflight; use rig-diagnose when needed, never bypass the gate.
2. Specify one motion name, description, duration_seconds and loop flag.
   Reuse the initial session-local motion request when already supplied. Do not
   ask the user to repeat an unchanged action or reconfirm its requirements.
   State ordinary assumptions such as in-place versus travelling; ask only when
   the choice materially changes the user's intent.
   Before saving, run the workspace interpreter's studio.py validate-request
   --kind motion --file <request.json> on the complete request. Each SayMotion
   description must contain 1-1000 characters. Use a concise motion-only prompt,
   preserve requirements and require exit code 0; revalidate after edits.
3. For a new clip call motion_create with character_build_id. For a source
   revision use motion_feedback, index and mode=source with a reviewed motion
   specification. Keep the original clip's character pinned.
4. Check studio.py doctor --require-generation motion. Present the saved motion
   request and potential SayMotion credit use, then proactively offer explicit
   authorization directly in chat, rather than waiting for the user to ask.
   Use the workspace interpreter for all studio.py commands.
   If binding review is pending, show the RigTest and warnings first. Use one
   scoped confirmation explaining that agreement both accepts this binding
   result with its stated risks and authorizes the exact saved SayMotion
   request's potential credit use. End with:
   Please reply 'I agree', or tell me what you would like to change.
   Do not mention confirmation buttons, require a form or numbered answers.
   One affirmative to this explicitly combined scope records both decisions.
   A partial affirmative records only its stated scope. An existing explicit
   authorization remains valid for this unchanged draft while awaiting review;
   do not request it repeatedly. Never infer either decision from the other.
   If the user cannot respond, leave one actionable next step and pause. Do not
   echo internal tool messages, auto-approve, or repeat blocker replies
   to automated continuation reminders.
5. Invoke build_generate only after permission. Inspect build_status on errors.
   When binding acceptance and payment permission are already present, start
   immediately; do not ask for a further "continue" or repeat the motion brief.
   A terminal provider failure requires a new draft and new permission, not
   repeated polling or automatic resubmission.
6. Preserve both source motion and adapted character output. Open the preview,
   using ?character=<character-id>&motion=<motion-build-id>&clip=0&section=motion.
   Verify both adapted and SayMotion source views load and start playback;
   state the build ID and use motion-diagnose for technical review.
7. Automatically use asset-deliver for a local copy and direct download links,
   even when final motion quality review is pending. Do not equate delivery
   with acceptance. Explain that agreement keeps the result, then use the
   standard chat wording; do not block access to files on this decision.

Report exact character/motion IDs, outputs and pending decisions. Generation
success does not mean the user accepted the performance or the quality is clean.
