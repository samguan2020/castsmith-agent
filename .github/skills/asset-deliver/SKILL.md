---
name: asset-deliver
description: "Deliver or download accepted character and motion assets. Use for GLB export, game-project handoff, manifests, quality reports and selecting exact versions for delivery."
---

# Deliver assets

1. Resolve the exact character and requested creative motion versions. Exclude
   rig-test animations and unrelated clips.
2. Read status, machine checks and actual user decisions. Distinguish generated,
   screened and accepted. If blocked or unreviewed, explain what remains;
   do not fabricate acceptance or describe an unchecked export as certified.
3. Use the engine's existing artifact URLs
   /api/builds/<build-id>/artifacts/<filename> and manifests. The simplified
   preview has no delivery forms; provide exact download links in chat instead.
   The first release delivers existing exports, not a new packaging engine.
4. Include character GLB, selected adapted motion GLB, requested source motion,
   preview, relevant manifest and quality reports. Preserve filenames/lineage.
5. Explain profile and limitations. The current GLB profile is not a guarantee
   of validated Unity/Unreal/Godot import or production-ready skinning.
6. If the user asks for a local handoff folder, copy only the exact selected
   files to a new exports subfolder after verifying paths. Never overwrite an
   existing delivery without approval. Do not modify a game project automatically.

Return a delivery inventory with build IDs, local links and known limitations.
Opening a preview or downloading an existing artifact never requires paid calls.
