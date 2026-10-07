# GTC-HD Research Workspace

## Purpose

This workspace supports architecture and source-code research for GTC-HD.

GTC-HD is an experimental modern enhancement rendering system for SNES games.

Guiding principle:

> **Enhance the pixel art. Never erase the pixel art.**

The project is currently in:

**Phase 0 — Discovery / Research / Architecture**

Read `docs/PROJECT_STATE.md` before performing substantive GTC-HD research.

## Authority Model

Do not confuse upstream emulator repositories with GTC-HD project authority.

### GTC-HD project authority

Files under `docs/` describe GTC-HD project state, research findings, experiment definitions/results, and architectural decisions.

Do not infer an accepted GTC-HD decision unless it is explicitly documented as accepted.

### Upstream source authority

Repositories under `upstream/` are external projects being investigated.

Their checked-out source code is authoritative only for claims about that specific upstream implementation and revision.

For example:

`upstream/bsnes/` may be used to determine how the checked-out version of bsnes works.

It is NOT the GTC-HD codebase.

It is NOT evidence that GTC-HD has selected bsnes.

It is NOT authoritative for GTC-HD architectural decisions.

## Current Research Status

The SNES emulator/core foundation and PPU interception boundary are:

**INVESTIGATING**

No emulator/core has been selected.

**Current disposition — 2026-10-06:** Candidate A `46fa75236fa61d49d8e9424b3b44694b88aa07a9` is the accepted corrected **experimental** baseline. EXP-001/002/003 are **VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE**; the separately reauthorized corrected EXP-004 is **VERIFIED FOR TESTED EXP-004 CONDITIONS** at `cc8d1f0d0a67b0ee523549671b9843f67c7c7534`. See [Project State](docs/PROJECT_STATE.md) and [EXP-004 results](docs/experiments/EXP-004/RESULTS.md).

The original EXP-004/P0 registration and the pre-reauthorization checkpoint under “Accepted Candidate A Revalidation — 2026-10-05” retain their historical gate context. The later “EXP-004 Corrected Baseline — Implementation Reauthorization, 2026-10-05” section records their scoped supersession; it does not unlock the historical worktrees. Candidate A's earlier “not accepted” registration wording is likewise superseded only by its recorded experimental acceptance. All worktree permissions and protections below remain unchanged.

The diagnosed startup limitation concerns the specified Direct3D 9 desktop configuration in the restricted execution context; it is not a general failure of headless/None-driver or Windows execution. This clarification does not relax existing task-specific launch restrictions. The next [offline replay/preview contract](docs/specs/OFFLINE_REPLAY_PREVIEW.md) is **DRAFT / PROPOSED — NOT ACCEPTED; IMPLEMENTATION NOT AUTHORIZED**. This documentation reconciliation grants no source-edit, runtime, commit or publication permission.

## Upstream Repository Rules

Unless a task explicitly says otherwise:

* Treat repositories under `upstream/` as read-only research targets.
* Do not modify upstream source code.
* Do not commit changes inside upstream repositories.
* Do not implement GTC-HD inside an upstream repository.
* Record the exact Git branch and commit SHA used for substantive research.
* Ground source-code findings in actual repository paths, classes, functions, methods, and data structures.
* Clearly distinguish:

  * source-code observation;
  * inference;
  * hypothesis;
  * uncertainty.
* Never convert brainstorming or upstream implementation choices into accepted GTC-HD architecture.

## Experimental Worktrees

Directories under `experiments/` may contain intentionally writable experimental checkouts of upstream projects.

They are not production GTC-HD source code.

Modify an experimental worktree only when a task explicitly identifies that worktree as writable.

### EXP-001

The worktree:

`experiments/bsnes-exp-001/`

is writable only for:

**EXP-001 — Passive PPU Observation**

Expected branch:

`gtc-hd/exp-001-passive-ppu-observation`

Expected baseline:

`7d5aa1e656b9171524d01b1b22917197d8121cb4`

For EXP-001:

* modifications may be made inside `experiments/bsnes-exp-001/`;
* commits may be made only on its experiment branch when the task requests them;
* do not merge experimental changes into upstream `master`;
* do not modify `upstream/bsnes/`;
* preserve normal bsnes cycle-PPU behavior unless the experiment explicitly requires otherwise;
* experimental code is evidence-gathering code, not accepted GTC-HD architecture;
* a successful experiment does not select bsnes as the GTC-HD foundation.

Read the experiment specification before implementation:

`docs/experiments/EXP-001/SPEC.md`

## Research and Experiment Outputs

Write durable GTC-HD research and experiment documentation outside upstream repositories.

Preferred locations:

`docs/research/`

`docs/experiments/`

Research and experiment reports should normally include:

* repository identity;
* branch and commit SHA;
* question investigated;
* source-code or experimental evidence;
* findings;
* uncertainties;
* implications for GTC-HD;
* experiments still required;
* recommended next research step.

### Public Documentation Portability

Tracked GTC-HD documentation is written for public repository visitors browsing or cloning the repository.

- Use repository-relative or source-relative references. Link only to tracked repository files or public resources; identify external checkout source with textual paths and its branch/commit.
- Do not include personal absolute filesystem paths or expose ignored/private input, configuration, capture, build or output locations.
- Use placeholders such as `<GTC-HD-Lab>`, `<ROM_PATH>`, `<OUTPUT_DIR>` and `<PYTHON>` when machine-specific values are unavoidable.
- Retain hashes, tool/compiler versions, commit SHAs, branches, commands and other reproducibility evidence; portability cleanup must not change historical findings or statuses.
- Normalize local source paths returned by research tools before committing documentation.
- Apply this rule to future specifications, results, research reports, session handoffs and README changes.

## Accuracy Priority

GTC-HD prioritizes:

1. Correct game behavior.
2. Accurate SNES execution.
3. Faithful original rendering semantics.
4. Universal enhancement.
5. Optional game-specific enhancement.
6. Experimental visual effects.

Do not recommend compromising SNES execution merely to simplify enhanced rendering.

## Current Primary Research Question

Determine which SNES emulation architecture provides the strongest foundation for GTC-HD and where sufficiently rich PPU state can be intercepted to support a modern enhancement renderer without compromising accurate SNES execution.

### EXP-002

The worktree:

`experiments/bsnes-exp-002/`

is writable only for:

**EXP-002 — OBJ / Sprite Provenance Preservation**

Expected branch:

`gtc-hd/exp-002-obj-provenance`

Expected baseline:

`906f74b6e`

For EXP-002:

* modifications may be made inside `experiments/bsnes-exp-002/`;
* commits may be made only on its experiment branch when explicitly requested;
* do not merge experimental changes into upstream `master`;
* do not modify `upstream/bsnes/`;
* do not modify the EXP-001 worktrees;
* preserve normal bsnes cycle-PPU OBJ behavior;
* preserve sprite limits, OAM behavior, overlap rules, priority, and execution-visible PPU side effects;
* experimental provenance code is evidence-gathering code, not accepted GTC-HD architecture;
* a successful experiment does not select bsnes as the GTC-HD foundation.

Read the experiment specification before implementation:

`docs/experiments/EXP-002/SPEC.md`

### EXP-003

The worktree:

`experiments/bsnes-exp-003/`

is writable only for:

**EXP-003 — Main/Sub Composition and Winner Provenance**

Expected branch:

`gtc-hd/exp-003-composition-provenance`

Expected baseline:

`906f74b6e5f4f2f4e62bb960d01aa68c9f55f919`

For EXP-003:

- modifications may be made inside `experiments/bsnes-exp-003/`;
- commits may be made only on its experiment branch when explicitly requested;
- do not modify `upstream/bsnes/`;
- do not modify any EXP-001 or EXP-002 worktree;
- preserve native bsnes cycle-PPU window, priority, main-screen, and sub-screen behavior;
- experimental provenance code is evidence-gathering code, not accepted GTC-HD architecture;
- a successful experiment does not select bsnes as the GTC-HD foundation.

Read the experiment specification before implementation:

`docs/experiments/EXP-003/SPEC.md`

### EXP-004

The worktree:

`experiments/bsnes-exp-004/`

is writable only for:

**EXP-004 — Color Math and Native Sample Provenance**

Expected branch:

`gtc-hd/exp-004-color-math-provenance`

Expected baseline:

`76bdb9250befa62fcbf23fcff2ef962fe2f58215`

For EXP-004:

- modifications may be made inside `experiments/bsnes-exp-004/` only when explicitly authorized by the task;
- **EXP-004-P0 — Native Output Destination Bounds Investigation** completed with disposition **STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION**;
- EXP-004 source implementation remains blocked until the separate native-baseline investigation is completed, its disposition is documented, and implementation is explicitly re-authorized;
- worktree registration does not authorize source changes during a documentation-only task;
- commits may be made only on its experiment branch when explicitly requested;
- do not modify `upstream/bsnes/`;
- do not modify any EXP-001, EXP-002 or EXP-003 worktree;
- preserve native bsnes cycle-PPU color math, timing, execution-visible side effects, serializer payload and output-store ordering;
- do not silently repair native output bounds or change native memory layout as part of instrumentation;
- experimental provenance code is evidence-gathering code, not accepted GTC-HD architecture;
- a successful experiment does not select bsnes as the GTC-HD foundation.

Read the experiment specification and source audit before implementation:

`docs/experiments/EXP-004/SPEC.md`

`docs/experiments/EXP-004/SOURCE_AUDIT_AND_IMPLEMENTATION_PLAN.md`

### bsnes Native Output-Bounds Investigation

The worktree:

`experiments/bsnes-native-output-bounds/`

is writable only for:

**Separate native-baseline investigation of the inherited bsnes output-buffer / late-scanline destination issue discovered by EXP-004-P0**

Expected branch:

`gtc-hd/investigate-native-output-bounds`

Expected baseline:

`7d5aa1e656b9171524d01b1b22917197d8121cb4`

For this investigation:

- this checkout is NOT an EXP-004 implementation worktree;
- it is NOT production GTC-HD source;
- it begins from the pristine audited upstream bsnes baseline specified above;
- modifications are permitted only when a task explicitly authorizes them;
- the initial investigation phase is **SOURCE ARCHAEOLOGY ONLY**;
- do not repair, resize, clamp, suppress or otherwise alter native output behavior unless a later task explicitly authorizes a controlled candidate correction;
- do not modify `upstream/bsnes/`;
- do not modify any EXP-001, EXP-002, EXP-003 or EXP-004 worktree;
- do not merge this branch into upstream `master`;
- any successful correction still requires separate GTC-HD review and revalidation; it does not select bsnes as the project foundation.

Read the P0 report before investigation:

`docs/experiments/EXP-004/P0_OUTPUT_BOUNDS_REPORT.md`

### bsnes Native Output-Bounds Candidate A

The worktree:

`experiments/bsnes-native-output-bounds-a/`

is writable only for:

**Prototype retained late-sample backing with complete pointer safety while preserving native PPU execution and the 512x480 presentation contract**

Expected branch:

`gtc-hd/native-output-bounds-candidate-a`

Expected baseline:

`7d5aa1e656b9171524d01b1b22917197d8121cb4`

For Candidate A:

- this checkout is an isolated experimental native-baseline candidate, NOT an accepted repair;
- it is NOT production GTC-HD source;
- registration does not authorize EXP-004 implementation;
- modifications are permitted only when explicitly authorized by the task;
- do not modify `upstream/bsnes/`;
- do not modify any EXP-001, EXP-002, EXP-003 or EXP-004 worktree;
- do not modify `experiments/bsnes-native-output-bounds/`;
- do not merge this candidate into `master`;
- candidate comparison must preserve native PPU execution unless the approved prototype specification explicitly says otherwise;
- a successful prototype does not select bsnes or accept a corrected baseline.

Read the candidate review before implementation:

`docs/research/BSNES_NATIVE_OUTPUT_BOUNDS_CANDIDATE_REVIEW.md`

### bsnes Native Output-Bounds Candidate B

The worktree:

`experiments/bsnes-native-output-bounds-b/`

is writable only for:

**Prototype presentation-bounded stores using explicit execution/storage separation while preserving native PPU execution and all valid 512x480 stores**

Expected branch:

`gtc-hd/native-output-bounds-candidate-b`

Expected baseline:

`7d5aa1e656b9171524d01b1b22917197d8121cb4`

For Candidate B:

- this checkout is an isolated experimental native-baseline candidate, NOT an accepted repair;
- it is NOT production GTC-HD source;
- registration does not authorize EXP-004 implementation;
- modifications are permitted only when explicitly authorized by the task;
- do not modify `upstream/bsnes/`;
- do not modify any EXP-001, EXP-002, EXP-003 or EXP-004 worktree;
- do not modify `experiments/bsnes-native-output-bounds/`;
- do not merge this candidate into `master`;
- candidate comparison must preserve native PPU execution unless the approved prototype specification explicitly says otherwise;
- a successful prototype does not select bsnes or accept a corrected baseline.

Read the candidate review before implementation:

`docs/research/BSNES_NATIVE_OUTPUT_BOUNDS_CANDIDATE_REVIEW.md`

### bsnes Native Output-Bounds Runtime Control

The worktree:

`experiments/bsnes-native-output-bounds-control-runtime/`

is writable only for:

**Pristine-runtime control using the existing framebuffer hash harness**

Expected branch:

`gtc-hd/native-output-bounds-control-runtime`

Native PPU baseline:

`7d5aa1e656b9171524d01b1b22917197d8121cb4`

Runtime harness commit:

`906f74b6e5f4f2f4e62bb960d01aa68c9f55f919`

For the runtime control:

- preserve the pristine native PPU behavior while using the existing framebuffer hash harness;
- modifications and runtime validation require explicit task authorization;
- this is an isolated research checkout, NOT production GTC-HD source or an accepted baseline;
- do not modify upstream, original investigation, prototype or EXP-001/002/003/004 worktrees as part of work in this checkout;
- do not merge this branch into `master`;
- registration does not authorize EXP-004 implementation or select bsnes as the project foundation.

Read the prototype comparison before runtime validation:

`docs/research/BSNES_NATIVE_OUTPUT_BOUNDS_PROTOTYPE_COMPARISON.md`

### bsnes Native Output-Bounds Candidate A Runtime

The worktree:

`experiments/bsnes-native-output-bounds-a-runtime/`

is writable only for:

**Runtime comparison of Candidate A's retained late-sample backing using the existing framebuffer hash harness**

Expected branch:

`gtc-hd/native-output-bounds-candidate-a-runtime`

Prototype parent:

`46fa75236fa61d49d8e9424b3b44694b88aa07a9`

Runtime harness commit:

`13e19564bd038e3767a58b9f1f1d29b1d5f4f527`

For Candidate A runtime:

- preserve the registered prototype's native execution and storage policy unless a task explicitly authorizes changes;
- modifications and runtime validation require explicit task authorization;
- this is an isolated research checkout, NOT production GTC-HD source or an accepted repair;
- do not modify upstream, original investigation, prototype or EXP-001/002/003/004 worktrees as part of work in this checkout;
- do not merge this branch into `master`;
- registration does not authorize EXP-004 implementation; successful runtime validation does not select bsnes or accept a corrected baseline.

Read the prototype comparison before runtime validation:

`docs/research/BSNES_NATIVE_OUTPUT_BOUNDS_PROTOTYPE_COMPARISON.md`

### bsnes Native Output-Bounds Candidate B Runtime

The worktree:

`experiments/bsnes-native-output-bounds-b-runtime/`

is writable only for:

**Runtime comparison of Candidate B's presentation-bounded stores using the existing framebuffer hash harness**

Expected branch:

`gtc-hd/native-output-bounds-candidate-b-runtime`

Prototype parent:

`31094598c7c03af7f4bba758061346b5aca7143c`

Runtime harness commit:

`71820eaf7777bee0537ed2a9c87e01e916bae3a1`

For Candidate B runtime:

- preserve the registered prototype's native execution and storage policy unless a task explicitly authorizes changes;
- modifications and runtime validation require explicit task authorization;
- this is an isolated research checkout, NOT production GTC-HD source or an accepted repair;
- do not modify upstream, original investigation, prototype or EXP-001/002/003/004 worktrees as part of work in this checkout;
- do not merge this branch into `master`;
- registration does not authorize EXP-004 implementation; successful runtime validation does not select bsnes or accept a corrected baseline.

Read the prototype comparison before runtime validation:

`docs/research/BSNES_NATIVE_OUTPUT_BOUNDS_PROTOTYPE_COMPARISON.md`

### Accepted Candidate A Revalidation — 2026-10-05

Xavier accepted native source `46fa75236fa61d49d8e9424b3b44694b88aa07a9` as the corrected **experimental research baseline**. This dated disposition supersedes Candidate A's pre-acceptance registration wording above; historical prototype/runtime worktrees remain protected during revalidation. It does not select a final core or authorize EXP-004.

The following isolated worktrees are writable only for the authorized accepted-baseline integration and finite EXP-001/002/003 transfer revalidation:

| Worktree | Expected branch | Purpose |
| --- | --- | --- |
| `experiments/bsnes-candidate-a-revalidation-baseline/` | `gtc-hd/candidate-a-revalidation-baseline` | Fresh corrected harness-only build and deterministic control |
| `experiments/bsnes-exp-001-corrected/` | `gtc-hd/exp-001-corrected-baseline` | Reintegrate and revalidate the established EXP-001 observer |
| `experiments/bsnes-exp-002-corrected/` | `gtc-hd/exp-002-corrected-baseline` | Reintegrate and revalidate the established EXP-002 observer |
| `experiments/bsnes-exp-003-corrected/` | `gtc-hd/exp-003-corrected-baseline` | Reintegrate and revalidate the established EXP-003 observer |

Starting harness descendant: `13e19564bd038e3767a58b9f1f1d29b1d5f4f527`. The accepted native correction is its parent `46fa75236fa61d49d8e9424b3b44694b88aa07a9`, not the harness commit. Historical harness: `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919`.

For these checkouts:

- preserve Candidate A storage, pointer safety, native execution and 512x480 presentation;
- reuse existing observers without redesign or new semantic fields; stop and report unexpected regressions;
- do not modify upstream, original EXP-001/002/003/004, investigation, prototype or historical runtime worktrees;
- local commits on these new branches are permitted only after the relevant implementation/tests pass, using Xavier Laverde <xavier0286@gmail.com> as author and committer;
- do not merge into `master`, rewrite historical/public identities, or push;
- these are research checkouts, not production GTC-HD source; EXP-004 implementation requires Xavier's explicit reauthorization after successful transfer revalidation.

Read the relevant experiment specification/results and `docs/research/BSNES_NATIVE_OUTPUT_BOUNDS_RUNTIME_VALIDATION.md` before revalidation.

Current revalidation disposition: EXP-001/002/003 are **VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE** after focused host/source checks, normal-desktop framebuffer/provenance transfers and targeted bounds fixtures passed. EXP-004 is **NATIVE-BASELINE GATE SATISFIED / READY FOR EXPLICIT IMPLEMENTATION REAUTHORIZATION**; source implementation remains unauthorized until Xavier explicitly reauthorizes it. Runtime validation must use the normal desktop execution context; the diagnosed restricted-context Direct3D 9 modal failure is a validation-environment limitation, with exact HRESULT unknown. See `docs/research/BSNES_ACCEPTED_BASELINE_REVALIDATION.md`.

### EXP-004 Corrected Baseline — Implementation Reauthorization, 2026-10-05

Xavier explicitly reauthorized EXP-004 color-math / final-native-sample provenance implementation after the completed corrected-baseline transfers. This dated authorization supersedes the pending reauthorization gate above; historical P0 findings and protected worktrees retain their original scope.

The worktree:

`experiments/bsnes-exp-004-corrected/`

is writable only for:

**EXP-004 — Color Math and Final-Native-Sample Provenance on the accepted corrected experimental baseline**

Expected branch:

`gtc-hd/exp-004-color-math-provenance-corrected`

Required parent:

`c929e19a8583e388b0f8bf53d2d0a796c0d91386`

Accepted native correction:

`46fa75236fa61d49d8e9424b3b44694b88aa07a9`

For this checkout:

- preserve Candidate A's 512x496 backing, pointer safety, native late stores, V=240 execution and 512x480 presentation;
- preserve native composition, color-math lifetimes, stateful reads, lookup/store ordering and serialization semantics;
- do not modify upstream, historical EXP-004/P0, prior experiment/corrected-baseline, Candidate A or public source branches;
- validate focused host behavior, affected EXP-003 behavior, Candidate A bounds and deterministic runtime passivity; emulator launches must use the normal desktop execution context;
- stop and report unexpected native/provenance divergence or intended-window overflow; do not change expectations to obtain a pass;
- a local source commit is authorized only after required validation passes, with Xavier Laverde <xavier0286@gmail.com> as author and committer; do not push or merge;
- this remains experimental research, not production source, a final semantic-frame format or selection of bsnes.

Read `docs/experiments/EXP-004/SPEC.md`, `docs/experiments/EXP-004/SOURCE_AUDIT_AND_IMPLEMENTATION_PLAN.md`, the preserved P0 evidence and `docs/research/BSNES_ACCEPTED_BASELINE_REVALIDATION.md` before implementation.

Current disposition: **VERIFIED FOR TESTED EXP-004 CONDITIONS** at local source commit `cc8d1f0d0a67b0ee523549671b9843f67c7c7534`, following focused/affected host checks, Candidate A regression, targeted runtime and deterministic framebuffer/provenance validation. See `docs/experiments/EXP-004/RESULTS.md` for tested coverage and remaining limitations. This supersedes the earlier pending implementation status only for this authorized corrected checkout; historical P0 evidence and protected worktree permissions remain unchanged. No push, merge, final core selection or production semantic-frame acceptance is authorized by this result.
