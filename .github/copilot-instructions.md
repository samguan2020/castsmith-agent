# CastSmith workspace

This is an agent-first product shell, not a fork of the execution engine.
Use CastSmith Studio for asset-production tasks and load relevant project skills.
Execution belongs to the dependency pinned in requirements.txt.

Never read or reveal .env, copy credentials or generated assets from other
workspaces, or submit paid operations without the user's explicit approval.
Keep local assets in .castsmith and exports in exports; both are untracked.
Read castsmith.project.json for project preferences. Preserve existing versions.
Current generation is synchronous; general-purpose automatic repair and durable
background operation management are not shipped in this version.

Proactively offer creation after a design and SayMotion authorization when a
motion is ready. Keep paid consent and human review separate; an unanswered or
unavailable-user response is not approval. Pause once instead of repeating
blocker messages. Use the workspace interpreter's studio.py validate-request
before saving generation drafts; Tripo's limit includes engine-added constraints.
The web command serves only character, RigTest and source/adapted motion previews.
