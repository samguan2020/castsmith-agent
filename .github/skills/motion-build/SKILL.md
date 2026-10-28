---
name: motion-build
description: "Create or revise a SayMotion animation and adapt it to an existing character. Use for walk, idle, attack, wave or other actual motion generation, with explicit paid consent."
---

# Build a motion

1. Resolve and pin the exact character version. Verify appearance acceptance
   and binding preflight; use rig-diagnose when needed, never bypass the gate.
2. Specify one motion name, description, duration_seconds and loop flag.
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
   authorization with the host's confirmation tool, rather than waiting for the
   user to ask. Use the workspace interpreter for all studio.py commands.
   If binding review is pending, show the RigTest first and combine independent
   binding-acceptance and paid-permission fields in one prompt. An explicit
   authorization remains valid for this unchanged draft while awaiting review;
   do not request it repeatedly. Never infer either decision from the other.
   If the user cannot respond, leave one actionable next step and pause. Do not
   echo internal unavailable-user text, auto-approve, or repeat blocker replies
   to automated continuation reminders.
5. Invoke build_generate only after permission. Inspect build_status on errors.
   A terminal provider failure requires a new draft and new permission, not
   repeated polling or automatic resubmission.
6. Preserve both source motion and adapted character output. Open the preview,
   using ?character=<character-id>&motion=<motion-build-id>&clip=0&section=motion.
   Verify both adapted and SayMotion source views load and start playback;
   state the build ID and use motion-diagnose for technical review.

Report exact character/motion IDs, outputs and pending decisions. Generation
success does not mean the user accepted the performance or the quality is clean.
