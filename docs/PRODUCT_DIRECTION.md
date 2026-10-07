# GTC-HD — Approved Product Direction

Recorded in this canonical home: **October 6, 2026**. These are Xavier's already approved product intentions, preserved from the [October 5 approval context](research/PIXELRAMP_RELATED_WORK.md). Placement here does not accept a technical architecture or authorize implementation. [Project State](PROJECT_STATE.md) governs current implementation and verification status.

## Identity and fidelity

GTC-HD is intended to be its own player-facing SNES enhancement product and a technical and creative extension of **GamingTheClassX**. It is separate from MVPConnect. Its practical purpose includes enjoyable, stable play and distinctive, reliable recording for the channel.

> **Enhance the pixel art. Never erase the pixel art.**

Correct game behavior, accurate SNES execution and faithful original rendering semantics take priority over enhancement. Preserve silhouettes, animation, intentional pixel structure and readability. Effects should support the artwork, with restrained defaults and convenient adjustment or disabling. Retain original/reference rendering and an accessible Original/Enhanced comparison.

## Play-first Runtime

The intended experience is: launch a compatible ROM, make brief first-use choices where needed, apply compatible profiles when available, and play. Ordinary play must not require prior authoring or a manual remaster.

Pursue useful universal enhancement where feasible, enriched by optional game profiles. Without a compatible profile, a game should remain playable; insufficient information should degrade faithfully toward original rendering. Compatibility breadth and the universal feature set remain research questions, not current guarantees.

Practical requirements include controllers, saves/save states where appropriate and validated, convenient configuration and presets, output-resolution controls, stable frame pacing and gameplay, reliable recording, and OBS/game-capture compatibility. These are intended capabilities, not claims that production Runtime exists.

## Eventual Studio and shared profiles

The intended authoring loop is **pause/capture → select/click → inspect native information → modify authored interpretation → preview → save/export**. Inspection should reveal what is actually known, including unknowns and match scope. Clicking a graphic does not imply that persistent object identification has already been solved.

Profiles add authored knowledge to a common foundation. They should become shareable, with a long-term community-library goal. Ordinary authoring should be practical within Studio; external tools may eventually help advanced workflows but are not a prerequisite for ordinary play.

Keep these concepts distinct:

| Concept | Meaning |
| --- | --- |
| Native facts | What the inspected/tested core actually selected, consumed and produced, including provenance, timing and reference output; not automatically hardware truth. |
| Authored meaning | Additional interpretation, such as a torch, material or approximate depth. Examples of depth/material/emission properties are illustrative, not a profile schema. |
| Renderer policy | How native evidence and optional interpretation affect the enhanced presentation. |

BG priority is not physical depth, brightness is not emission, and an OAM slot is not a persistent entity. Profiles must not masquerade as native facts or silently change game execution.

## Deliberately unresolved implementation choices

Runtime and Studio name responsibilities and experiences, not one versus multiple executables. Final core and integration boundary, production renderer/API/language, shader technology, Studio framework, semantic-frame contract, profile schema/scripting/identity, platform/hardware baseline, first showcase game, working/output scale and upscaler remain undecided. Existing C++/Python/MSYS2/Windows research tools and SMW validation inputs do not select those choices.

Hosting, accounts, moderation, trust/signing, distribution, automatic downloads and legal/content policy for a library remain undecided. No service or publication mechanism is selected here. External authoring integration, HDR, temporal interpolation, physical depth, materials, asset replacement and widescreen remain research or deferred feature directions with their own evidence requirements.

The [bounded replay/preview draft](specs/OFFLINE_REPLAY_PREVIEW.md) is a proposed research consumer, not the end product. It does not implement Runtime, Studio or universal enhancement, and it does not reduce these longer-term intentions to a glow demonstration.
