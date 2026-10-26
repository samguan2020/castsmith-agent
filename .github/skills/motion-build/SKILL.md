---
name: motion-build
description: "Create or revise a SayMotion animation and adapt it to an existing character. Use for walk, idle, attack, wave or other actual motion generation, with explicit paid consent."
---

# Build a motion

1. Resolve and pin the exact character version. Verify appearance acceptance
   and binding preflight; use rig-diagnose when needed, never bypass the gate.
2. Specify one motion name, description, duration_seconds and loop flag.
   Clarify in-place versus travelling intent when it affects the result.
3. For a new clip call motion_create with character_build_id. For a source
   revision use motion_feedback, index and mode=source with a reviewed motion
   specification. Keep the original clip's character pinned.
4. Check studio.py doctor --require-generation motion. Present the saved motion
   request and potential SayMotion credit use, then obtain explicit permission.
5. Invoke build_generate only after permission. Inspect build_status on errors.
   A terminal provider failure requires a new draft and new permission, not
   repeated polling or automatic resubmission.
6. Preserve both source motion and adapted character output. Open the preview,
   state the build ID and use motion-diagnose for technical review.

Report exact character/motion IDs, outputs and pending decisions. Generation
success does not mean the user accepted the performance or the quality is clean.
