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
   identify the tested character and ask for multi-angle human inspection.
4. Separate observed evidence from hypotheses: location, pose/time, suspected
   bones and whether the defect also occurs outside creative motion.
5. Existing screening does not establish skin-weight correctness or mesh
   collision absence. General weight repair is not implemented. An unchanged
   recheck is not a repair, and a diagnosis record is not a repaired asset.
6. Record a real acceptance/rejection using build_review only when the user has
   actually decided. Blocking errors remain blockers.
7. If needed, save binding feedback using character_feedback in binding mode.
   Explain that it records diagnosis awaiting targeted repair. Offer manual
   processing or a revised appearance brief; paid regeneration needs new consent.

Return tested IDs, evidence, uncertainty, automatic result and human decision
separately. Do not spend provider credits to diagnose binding.
