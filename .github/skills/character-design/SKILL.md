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
5. Before saving, run studio.py validate-request --kind character --file
   <request.json> with the complete character-only request, using the workspace
   interpreter. It checks the 1024-character final prompt INCLUDING the engine's
   anatomy constraints. Compact redundant wording and revalidate until it
   passes; never silently truncate or use paid generation to test length.
6. Save the agreed brief as a draft using build_create with motions=[] if the
   user wants it persisted. A draft is not a completed character and costs nothing.

7. Return the brief and any draft ID, then proactively offer to start creation
   with the host's confirmation tool. Include Tripo and potential API credit use
   so an explicit yes can authorize this exact brief; do not invent a price.
   If the user asked for design only or no payment, respect that scope instead.
8. Move to character-build after the user's actual creation decision. A saved
   brief or an unanswered form is not consent. If the user is unavailable,
   leave one concise next action and pause without repeating the request.
