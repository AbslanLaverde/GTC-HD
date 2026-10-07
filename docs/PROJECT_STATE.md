# GTC-HD — Project State

**Last Updated:** October 6, 2026
**Current Phase:** Phase 0 — Discovery / Research / Architecture

## Vision

GTC-HD is an experimental modern enhancement rendering system for SNES games.

Guiding principle:

> **Enhance the pixel art. Never erase the pixel art.**

Original game behavior, accurate SNES execution, faithful rendering semantics, and pixel-art identity take priority over enhancement effects.

[Approved Product Direction](PRODUCT_DIRECTION.md) records Xavier's play-first Runtime, eventual Studio authoring, shareable-profile and GamingTheClassX intentions. These are product goals; core, renderer, schema and service architecture remain undecided.

## Current Objective

Determine the most appropriate technical foundation and rendering architecture for GTC-HD.

The highest-priority research question is:

> Which SNES emulation architecture provides the strongest foundation for GTC-HD, and where can sufficiently rich PPU state be intercepted to support a modern enhancement renderer without compromising accurate SNES execution?

## Current Investigation

**INVESTIGATING — SNES emulator/core foundation and PPU interception boundary**

Initial candidates include:

* bsnes
* bsnes-HD
* Snes9x
* higan-related work
* other strong candidates discovered during research

bsnes has been investigated first as a research target.

This does **not** mean bsnes has been selected.

The experiments below establish useful interception evidence for bounded native paths. The strategic question remains open; the initial question of whether any such provenance can be preserved has narrower positive evidence now.

## Accepted Experimental Baseline — 2026-10-05

**ACCEPTED:** Xavier accepted Candidate A as the corrected experimental bsnes baseline for continued GTC-HD research.

Native source: `46fa75236fa61d49d8e9424b3b44694b88aa07a9` — pointer-safe 512x496 backing, unchanged 512x480 presentation, retained native late stores and backing-only pair-240 transition clearing, with no invalid no-store-line pointers.

Candidate A passed the documented prior host, ordinary-runtime and targeted-runtime validation for tested conditions; see the [runtime report and decision addendum](research/BSNES_NATIVE_OUTPUT_BOUNDS_RUNTIME_VALIDATION.md). Candidate B remains a viable tested alternative, not selected.

This acceptance covers the **experimental research baseline only**. It does not select bsnes as the final core, establish universal hardware correctness, imply upstream acceptance, or replace historical experiment evidence. The semantic-preservation architecture remains a hypothesis.

**Transfer revalidation complete for tested conditions:** the existing corrected EXP-001/002/003 integrations passed focused host/source checks, observer-disabled/enabled framebuffer comparisons, callback-500 provenance capture and the targeted bounds runtime fixture in the normal desktop execution context. The historical claims transferred to the accepted experimental baseline for these tested inputs and windows. See the [resumed transfer results](research/BSNES_ACCEPTED_BASELINE_REVALIDATION.md#resumed-transfer-results--2026-10-05); the original startup stop and its diagnosis remain preserved there.

| Experiment | Current status | Corrected source commit |
| --- | --- | --- |
| EXP-001 | VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE | `ab04d023b728f08f7cbfaa38e75dcf8031a04158` |
| EXP-002 | VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE | `94238480bd11a0ca3b873da1d70c208ca2f9326c` |
| EXP-003 | VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE | `c929e19a8583e388b0f8bf53d2d0a796c0d91386` |
| EXP-004 | VERIFIED FOR TESTED EXP-004 CONDITIONS | `cc8d1f0d0a67b0ee523549671b9843f67c7c7534` |

**EXP-004: VERIFIED FOR TESTED EXP-004 CONDITIONS.** Following Xavier's explicit reauthorization, the isolated corrected implementation passed focused/affected host tests, Candidate A bounds regression, the targeted runtime fixture and the deterministic 1,800-callback disabled/enabled/control comparison. Callback 500 captured 61,440 records with no drops, overflow or unknown provenance, including real CurrentSub and FixedColor addition; hires/carried-main, subtraction and halving remain host-tested only. All positions in that real-ROM capture were lowres, with zero-valued main backdrop operands on math-enabled samples; this does not demonstrate general two-nonzero-operand addition or saturation in that slice. See [EXP-004 results](experiments/EXP-004/RESULTS.md). The historical P0 stop remains preserved; this result does not accept a production semantic-frame format or select a final core/renderer architecture.

The specified SMW desktop configuration failed Direct3D 9 initialization in the diagnosed restricted execution context and blocked in the video-driver error dialog before ROM loading. The corresponding normal-desktop launches succeeded. This demonstrates a limitation of that driver/configuration/context combination, not of all headless/None-driver runs or all Windows execution; the exact Direct3D HRESULT remains unknown. Existing task-specific launch restrictions remain applicable.

The [publication map](research/BSNES_EXPERIMENT_PUBLICATION_MAP.md) preserves the September 23 public-source snapshot. The corrected integrations above are separate local source identities, not equivalent publication rewrites or claims of current public availability.

## Decisions Not Yet Made

The project has NOT selected:

* a final emulator/core;
* a production architecture;
* a final hardware baseline;
* an implementation language;
* a graphics API;
* a renderer architecture;
* a shader language;
* a game-profile format;
* an initial production platform;
* a proof-of-concept game;
* a modern upscaling/reconstruction system;
* a distribution model.

## Architecture Direction Under Investigation

A currently attractive hypothesis is:

SNES Execution Core
→ GTC-HD Graphics / PPU Interface
→ GTC-HD Scene Representation
→ GTC-HD Renderer
→ Modern GPU

This is a **HYPOTHESIS**, not an accepted architecture.

## Research Principle

Upstream emulator repositories are research targets.

Their source code is authoritative for determining how those particular emulator revisions work.

They are not authoritative for GTC-HD architectural decisions.

## Implementation Status

No production GTC-HD implementation currently exists.

No final emulator/core foundation has been accepted; the experimental baseline disposition above has narrower scope.

No production repository architecture has been accepted.

EXP-001/002/003 retain their historical tested-condition results and have now reproduced the specified framebuffer/provenance claims on the accepted corrected experimental baseline; EXP-004 subsequently completed its scoped implementation and validation. Broader execution-state equivalence and universal compatibility remain unproven; no production renderer or semantic interface has been accepted.

## Documentation Milestone — 2026-10-06

The [bounded post-EXP-004 comparative audit](research/RELATED_WORK_SURVEY.md) is complete for its inspected revisions and scope. Current-status reconciliation is prepared, approved product intentions have a canonical home, and complete [Knowledge Base v2.0](knowledge/KNOWLEDGE_BASE.md) and [Custom GPT Instructions v2.0](knowledge/CUSTOM_GPT_INSTRUCTIONS.md) replacements are **proposed, pending review**. They have not been installed in a GPT.

This milestone records prior decisions and corrects stale current-status wording. It does not accept a new architecture. Historical outcomes, source/public identities and measured conditions remain preserved.

## Immediate Next Decision — Contract Review

Xavier's document review and scope approval are next. The [offline replay and frozen source-selection/glow preview contract](specs/OFFLINE_REPLAY_PREVIEW.md) is **DRAFT / PROPOSED — NOT ACCEPTED; IMPLEMENTATION NOT AUTHORIZED**. No experiment number has been assigned and no consumer implementation has begun.

The proposal asks whether an independent consumer can reconstruct a supported lowres/noninterlaced captured interval from operands, controls and history, then enable one honest capture-bound authored edit. Captured output is an oracle, not the reconstruction input. Approval must resolve the interval/crop, raster/epoch and alias ownership, seed policy, selection-mask meaning, annotation and temporary implementation/sampling choices. Actual retained capture identity/schema/producer verification is a prerequisite for a future run; private captures were not inspected in this reconciliation.

Near-term sequence: completed baseline/EXP-001–004 → completed comparative audit → this reconciliation → contract approval → separately authorized bounded consumer. Complete hires/history ownership, a deterministic hires-transition witness and Mode 7 lineage remain later candidates, not automatic prerequisites for a restricted proposal that excludes them. Do not reopen completed experiments without a specific contradiction or concrete consumer requirement.
