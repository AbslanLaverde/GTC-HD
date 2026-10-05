# GTC-HD — Project State

**Last Updated:** October 5, 2026
**Current Phase:** Phase 0 — Discovery / Research / Architecture

## Vision

GTC-HD is an experimental modern enhancement rendering system for SNES games.

Guiding principle:

> **Enhance the pixel art. Never erase the pixel art.**

Original game behavior, accurate SNES execution, faithful rendering semantics, and pixel-art identity take priority over enhancement effects.

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

**EXP-004: NATIVE-BASELINE GATE SATISFIED / READY FOR EXPLICIT IMPLEMENTATION REAUTHORIZATION.** The separate investigation has an accepted experimental baseline disposition and all three transfers passed. EXP-004 color-math provenance remains unimplemented, unverified and unauthorized until Xavier explicitly reauthorizes implementation.

These bsnes runtime tests require the **normal desktop execution context**. In the diagnosed restricted context, Direct3D 9 initialization failed and blocked in the video-driver error dialog before ROM loading; that limitation does not establish an emulator/runtime defect. The exact Direct3D HRESULT remains unknown.

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

EXP-001/002/003 retain their historical tested-condition results and have now reproduced the specified framebuffer/provenance claims on the accepted corrected experimental baseline. Broader execution-state equivalence and universal compatibility remain unproven; no production renderer or semantic interface has been accepted.

## Next Research Action

Obtain Xavier's explicit EXP-004 implementation reauthorization, using the completed corrected-baseline transfer results and preserved historical P0/design evidence. The satisfied native-baseline gate does not itself authorize source changes or select a final core/architecture.
