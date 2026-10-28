---
name: rig-diagnose
description: "Check character binding and investigate shoulder, sleeve, elbow, knee or skin-weight deformation. Use before motion creation or when a character deforms incorrectly; this is not a paid regeneration request."
---

# Diagnose binding

1. Identify the exact character build and whether the user approved appearance.
   Do not record appearance approval just to unlock the test.
2. Reuse an applicable existing rig test if available. Otherwise call
   build_reprocess on the character with rig_test=true for a free local test.
3. Inspect its status and quality report. Open the viewer's isolated-joint test,
   using ?character=<character-id>&rig=<rig-test-id>&section=rig.
   Bring the RigTest window (top right) into view and verify its model loaded
   and automatic looping advances data-time (use a screenshot if available).
   The preview-only UI retains introductions, but no playback controls or quality labels; read
   exact IDs/readiness from its data-build-id/data-state attributes and report
   warnings, times and human decisions in chat.
   Identify the tested character, risk times and machine result, then proactively
   request multi-angle human inspection. Do not request approval of an unseen
   test or treat a healthy endpoint/hidden tab as successful display.
4. Separate observed evidence from hypotheses: location, pose/time, suspected
   bones and whether the defect also occurs outside creative motion.
5. Existing screening does not establish skin-weight correctness or mesh
   collision absence. General weight repair is not implemented. An unchanged
   recheck is not a repair, and a diagnosis record is not a repaired asset.
6. Record a real acceptance/rejection using build_review only when the user has
   actually decided, with decision=accepted or rejected and confirmed=true.
   Appearance acceptance and generation permission do not imply this review.
   If motion generation is next, combine this review request with the exact
   saved motion's SayMotion credit authorization as independent fields.
   Retain any permission already granted. If no real response is available,
   pause once with a concise next action; do not loop on unavailable-user text.
   Blocking errors remain blockers.
7. If needed, save binding feedback using character_feedback in binding mode.
   Explain that it records diagnosis awaiting targeted repair. Offer manual
   processing or a revised appearance brief; paid regeneration needs new consent.

Return tested IDs, evidence, uncertainty, automatic result and human decision
separately. Do not spend provider credits to diagnose binding.
