---
name: asset-deliver
description: "Deliver or download generated character and motion assets, including automatic handoff after motion generation. Use for GLB export, game-project handoff, manifests, quality reports and selecting exact versions for delivery; delivery does not imply acceptance."
---

# Deliver assets

1. Resolve the exact character and requested creative motion versions. Exclude
   rig-test animations and unrelated clips.
2. Read status, machine checks and actual user decisions. Distinguish generated,
   screened and accepted. If blocked or unreviewed, explain what remains;
   do not fabricate acceptance or describe an unchecked export as certified.
3. Use the engine's existing artifact URLs
   /api/builds/<build-id>/artifacts/<filename> and manifests. The simplified
   preview footer links the currently shown character and creative motion's
   saved artifacts, excluding RigTest. Provide exact download links and local
   .castsmith/artifacts/<build-id>/ paths in chat as well; do not imply that
   files were copied to exports unless an explicit handoff was performed.
   The first release delivers existing exports, not a new packaging engine.
4. Include character GLB, selected adapted motion GLB, requested source motion,
   preview, relevant manifest and quality reports. Preserve filenames/lineage.
5. Explain profile and limitations. The current GLB profile is not a guarantee
   of validated Unity/Unreal/Godot import or production-ready skinning.
6. After motion generation, automatically copy the exact selected files to a
   fresh exports subfolder with the workspace interpreter:
   `.\.venv\Scripts\python.exe .\scripts\studio.py deliver --character <character-id> --motion <motion-id> --clip 0`.
   This copies existing engine artifacts, verifies recorded sizes and hashes,
   and preserves build IDs, review state and quality limitations in delivery.json.
   It does not generate, repair, approve or convert assets. Report failure
   explicitly; never claim an export exists when the command failed.
   A character-only handoff can use direct downloads; do not invent a motion.
   Never overwrite an existing delivery or modify a game project automatically.
7. Provide the local folder, direct downloads and a short modification offer.
   Explain that agreement keeps the result, then ask directly in chat:
   Please reply 'I agree', or tell me what you would like to change.
   Do not mention confirmation buttons or require a form.
   Files remain available before the final quality decision. Revised paid
   requests need fresh consent; preserve all earlier versions.

Return a delivery inventory with build IDs, local links and known limitations.
Opening a preview or downloading an existing artifact never requires paid calls.
