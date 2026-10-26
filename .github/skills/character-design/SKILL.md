---
name: character-design
description: "Design or revise a game character concept and production brief. Use for appearance, clothing, style, character requirements or brainstorming without submitting paid generation."
---

# Design a character

1. Read project preferences and query the library if continuing an existing
   character. Preserve identity and reference the exact source build.
2. Establish purpose, visual style, silhouette, outfit and technical constraints.
   Ask only consequential questions; label ordinary assumptions.
3. Limit this first release to one upright humanoid and the supported
   threejs-humanoid-lite GLB profile. Distinguish aspirations from guarantees.
4. Produce a concise brief: asset ID, appearance description, intended motions,
   constraints, assumptions and acceptance criteria. Prefer lowercase letters,
   digits and hyphens, at most 15 characters, for new asset and motion names.
5. Check the engine's character prompt validation rather than guessing remaining
   provider capacity: the engine adds anatomy constraints to the description.
   Never silently truncate requirements.
6. Save the agreed brief as a draft using build_create with motions=[] if the
   user wants it persisted. A draft is not a completed character and costs nothing.

Return the brief and any draft ID. Do not generate merely because a brief exists.
Move to character-build only when the user wants generation.
