# GTC-HD — Project State

**Last Updated:** September 18, 2026
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

bsnes will be examined first as a research target.

This does **not** mean bsnes has been selected.

## Decisions Not Yet Made

The project has NOT selected:

* an emulator/core;
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

No emulator foundation has been accepted.

No production repository architecture has been accepted.

Codex is currently being prepared for repository-aware research and source-code auditing.

## Next Research Action

Audit the bsnes PPU/rendering architecture and identify:

* how graphics state flows through the PPU;
* where BG and OBJ identity exists;
* how Mode 7 is implemented;
* where priority, windows, main/sub screens, and color math are resolved;
* how mid-frame PPU state changes are represented;
* where useful graphics semantics are lost;
* and which interception points could plausibly support GTC-HD.
