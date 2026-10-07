# Bounded Offline Replay and Source-Aware Preview

**Status: DRAFT / PROPOSED — NOT ACCEPTED; IMPLEMENTATION NOT AUTHORIZED**

Draft date: **October 6, 2026**. No EXP number is assigned. This is a proposed contract derived from the [completed comparative audit](../research/RELATED_WORK_SURVEY.md#5-which-next-build-buys-the-most-information) and [EXP-004 evidence](../experiments/EXP-004/RESULTS.md), pending Xavier's review. No consumer, worktree or test scaffolding has been created.

## Question and bounded result

Can one independent consumer reconstruct supported captured native samples and enable an honest source-aware authored edit?

Propose one offline build with two stages: native-sample replay, then a frozen selection/inspection and restrained glow preview. It consumes already selected native winners and operands; it does not rerender hidden candidates or decode complete assets. The [approved product direction](../PRODUCT_DIRECTION.md) remains broader than this experiment.

## Input prerequisite and ownership

Before a future authorized run, verify the actual retained capture and summary hashes, producer commit, schema/encoding, completeness, drops/overflow and required lineage against EXP-004's report. This documentation task has not inspected or validated the private captures. The reported evidence is not a substitute for that preflight.

Propose a contiguous lowres, noninterlaced tiled-BG/OBJ interval inside one native raster period. The exact crop, epoch, sequence bounds, relative frame/field and included source occurrences require approval after input verification. The import manifest must identify those bounds, supported modes, units and capture identity. A callback window is not a complete presented frame.

Define ordered slot-to-destination ownership, horizontal duplication, physical A/B stores and aliases. Distinguish 512x480 presentation destinations from Candidate A's retained backing. Exclude unowned borders, clear writes and other-field contents; do not silently fill them and claim reconstruction. Duplicate descriptions are not independent physical writes. Require a documented native scanline seed or explicit boundary snapshot with known origins, and track subsequent history in order. Missing initialization, gaps or discontinuities must not be guessed from later state or adjacent retained records.

## Independent native reconstruction

Use captured raw winner colors, operand scalars, controls and required history to determine/verify the effective path and calculate its result independently. Preserve selection versus clipping, None/CurrentSub/FixedColor choice, gating, arithmetic ordering and BGR555-to-RGB555 brightness conversion. Fixed-color scalar input is an operand, not invented sub lineage.

**Captured `preBrightness` and `stored` outputs are oracles, not reconstruction inputs.** Before/after Math snapshots may validate state evolution; apart from the declared initial state, they must not replace evolving the supported state. Do not copy a recorded result and label that replay.

The initial proposed arithmetic scope is NoMath and unhalved CurrentSub/FixedColor addition already observed in the lowres capture. In that real-ROM evidence, all math-enabled main colors were backdrop zero; this does not prove two-nonzero-color addition, saturation, subtraction or halving coverage. Hires/pseudo-hires/carry and other unsupported paths retain explicitly labeled reference-only fallback, with no enhancement. Missing required ownership/initialization rejects the affected import/crop. Unsupported or unknown samples must never count as replay passes.

## One honest authored interaction

Select a pixel, inspect its source and processing, and apply one small annotation bound to the exact capture/epoch and an explicitly displayed set of BG/OBJ source occurrences. Define grouping/selection extent in the approved contract; do not silently expand a fetch token into a complete sprite, asset or entity.

Keep three facts distinct:

- **Composition selection:** a main/sub source won its native selection path.
- **Operand consumption:** that source's allowed value was actually used in the supported passthrough/arithmetic path; an unconsumed sub winner is not an operand.
- **Numerical contribution:** the operand's effect on the result can be zero or altered by clipping, quantization or saturation. Consumption alone is not proof of a nonzero effect or physical energy.

The proposed binary **consumption-membership mask** includes known selected occurrences used as an unclipped primary or an actually consumed CurrentSub operand in validated owned samples. It excludes skipped, clipped, unknown and unconsumed sources. FixedColor fallback must not select the retained sub winner. Membership can include a zero-valued operand and must be labeled accordingly; it is not a numerical-contribution map, entity mask or emitter detector.

The author explicitly assigns glow with adjustable strength/radius to that shown membership. This is aesthetic interpretation, not inferred emission or physical illumination. Mismatched capture/epoch or unknown selection disables the annotation. No annotation is required for reference/replay viewing and inspection.

## Views, fallback and sampling

Provide Reference, Replayed, Enhanced and replay-difference views of the same owned crop. Recorded RGB555 may supply Reference and visibly labeled unsupported fallback only. Enhancement requires successful replay of the affected samples. Zero strength or disabling enhancement must restore the reference exactly before display conversion. Unowned areas remain outside the claim; no later mutable emulator memory may fill missing evidence.

Keep artwork sampling, categorical masks, smooth effect-field sampling and final viewport policy distinct. Never interpolate source IDs into new identities. Trial resolutions, filters, display conversion and backend require approval; no uniform multiplier or 8x precedent is selected.

## Proposed acceptance and stop conditions

1. Validate identity/schema/producer, ownership, seed/history and completeness. Reject corrupt/truncated inputs, mismatched annotations and missing required provenance; make unsupported coverage inspectable.
2. Match every supported owned RGB555 reference sample through independent reconstruction. Report path counts and witnesses. Perturbed operand/control inputs must change an appropriate computed result or trigger a consistency failure; altered oracle values must fail comparison rather than affect replay.
3. Show selection, consumption and numerical limits separately. Demonstrate NoMath, CurrentSub and FixedColor handling without false sub attribution; no complete-object/depth claims.
4. Demonstrate restrained adjustable preview, exact zero-strength restoration and repeatable annotation save/reload for the bound capture. Original/reference viewing must remain usable without an annotation.
5. Measure import time, peak/retained memory and preview latency with hardware/backend/sampling conditions recorded. Do not infer live throughput or production suitability.

An unexplained replay mismatch, incomplete ownership or missing required history stops the affected claim. Diagnose or narrow scope; do not change historical expectations, repair the emulator or launch a new capture campaign under this draft.

## Non-goals and approval boundary

Exclude full Studio, live integration, persistent asset/entity identity, complete assets/frames, Mode 7 enhancement, physical shadows/depth, HDR, interpolation, a sharing service, universal compatibility and production frame/profile schemas. Complete hires/history ownership remains a concrete later candidate, not an extra prerequisite for this restricted proposal.

Xavier must approve the scope/crop and retained-input use, initialization/ownership rules, mask/grouping semantics, temporary language/backend, sampling/display policy and task-specific annotation representation, plus a separate implementation handoff and allowed output location. These choices do not automatically select a production stack, core, showcase game or schema. This draft provides no source-edit, build, ROM-run or implementation authorization.
