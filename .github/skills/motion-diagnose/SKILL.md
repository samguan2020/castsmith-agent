---
name: motion-diagnose
description: "Investigate motion defects such as foot sliding, body contact, jitter, wrong heading or loop seams. Use to compare SayMotion source and adapted motion before choosing local reprocessing or regeneration."
---

# Diagnose a motion

1. Resolve the exact motion build, pinned character, clip index and reported
   time/frame. Query status and reports; do not reason from a stale selection.
2. Compare SayMotion source with the adapted result at matching normalized
   progress in the preview's side-by-side motion section. Pin the exact versions
   with character/motion/clip query parameters and use section=motion to bring
   it into view. Inspect the separate RigTest section if binding is relevant.
3. Classify evidence: source problem, character deformation, adaptation problem,
   heuristic false positive or unresolved cause. Record uncertainty.
4. For implemented heading calibration/reprocessing, use build_reprocess with
   rig_test=false. It creates a local version using saved sources, not a paid
   motion. Re-running unchanged processing does not guarantee improvement.
5. For adaptation feedback use motion_feedback mode=adaptation to preserve a
   diagnosis. This does not implement arbitrary IK, contact or curve repairs.
6. Compare the candidate with the baseline across the clip, not just one frame.
   Report target improvement, regressions and checks not performed. Respect the
   project's candidate limit; stop if no useful processing is available.
7. Source changes go to motion-build with fresh paid permission. Binding
   evidence goes to rig-diagnose. Record build_review only for a user's real
   whole-build decision, never to suppress machine blockers.

Return IDs, time markers, evidence, likely cause, candidate outcome and next step.
Possible foot slide/body proximity are heuristics, not proof of a defect.
