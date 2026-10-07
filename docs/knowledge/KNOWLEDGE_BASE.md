# GTC-HD Knowledge Base

**Version 2.0 — proposed replacement, pending review**  
**Prepared:** October 6, 2026  
**Foundation:** Xavier's September 18, 2026 Knowledge Base v1.0, reconciled with maintained repository authority and completed research evidence.

This is a complete proposed replacement for the foundational knowledge document. It has not been installed as a GPT knowledge update. Its dated bootstrap summary helps a new reader start; [Project State](../PROJECT_STATE.md) and its linked evidence remain the maintained current-state authority. Do not treat this upload as a second project-state ledger.

## 1. Mission and identity

GTC-HD is an experimental modern enhancement rendering system for SNES games. Its guiding principle is:

> **Enhance the pixel art. Never erase the pixel art.**

The ambition is recognizable original artwork enriched by more expressive rendering, precise transformations, light, atmosphere and spatial interpretation. Improvement must preserve shapes, colors, animation, edges and readability. Prohibited outcomes include smearing source-art edges or destroying intentional pixel structure; introducing unstable or invented detail presented as original artwork; and obscuring gameplay or compromising readability.

Filtering a separate glow, shadow or other effect field is not inherently prohibited. The resulting presentation must still preserve artwork identity, intentional pixel structure and readability. This does not permit indiscriminate blurring of the source artwork.

GTC-HD supports GamingTheClassX's creative and technical identity: distinctive presentations of classic games with useful Original/Enhanced comparisons and reliable recording. It is a separate project from MVP Connect, with its own repository, research, documentation, experiments and eventual implementation lifecycle. Approved branding is not a request to redesign it.

## 2. Fidelity and fallback

The priority order is:

1. Correct game behavior.
2. Accurate SNES execution.
3. Faithful original rendering semantics.
4. Universal enhancement.
5. Optional game-specific enhancement.
6. Experimental visual effects.

Native timing, sprite limits, priority, windows and color math are not disposable obstacles to enhancement. Preserve an original/reference route and convenient comparison. When information is insufficient or an enhancement is unsupported, fall back faithfully. An observed emulator output is a valuable baseline; agreement with it alone does not establish universal SNES hardware correctness.

## 3. Approved product direction

[Product Direction](../PRODUCT_DIRECTION.md) is the canonical home of the already approved intentions. The play-first Runtime experience is to launch a compatible ROM, make optional brief first-use choices, apply compatible profiles when available, and play. Useful enhancement should not require a manual remaster of every unfamiliar game.

An eventual Studio experience supports pause/capture, select/click, inspect native information, modify authored interpretation, preview, and save/export. Shareable profiles and a long-term community library are goals. Controllers, saves where appropriate, understandable configuration, stable play, recording and OBS-related needs matter alongside visual research.

Runtime and Studio describe responsibilities and experience, not an executable boundary or selected framework. No hosting, account, moderation, trust, automatic-download or distribution system is selected. Depth, material and emission fields are illustrative, not an accepted profile schema.

## 4. Dated bootstrap state — October 6, 2026

Phase 0 — Discovery / Research / Architecture continues. A research repository and isolated experimental bsnes worktrees exist; the initialization-era assumption that there is no repository or experimental implementation is obsolete. There is still no production GTC-HD renderer, complete semantic-frame contract or Studio.

Xavier accepted Candidate A as the corrected **experimental** bsnes baseline: pointer-safe 512x496 backing, unchanged 512x480 presentation and retained native late stores. Candidate B remains a viable tested alternative, not selected. This does not select bsnes as the final core or imply upstream acceptance, universal hardware correctness or production readiness.

| Research | Current scoped conclusion | What it does not establish |
| --- | --- | --- |
| EXP-001 | VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE; BG provenance and deterministic framebuffer passivity under tested conditions | Complete BG assets, final visibility or full execution-state equivalence |
| EXP-002 | VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE; actual OAM → fetch → surviving OBJ lineage, including documented overlap evidence | Persistent game-entity identity or final framebuffer visibility |
| EXP-003 | VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE; main/sub composition winners and provenance | Complete color-math contribution or a complete semantic frame |
| EXP-004 | VERIFIED FOR TESTED EXP-004 CONDITIONS; color-math/native-sample provenance and tested passivity | Universal mode coverage, independent reconstruction or a production interface |

See the [corrected-baseline transfer report](../research/BSNES_ACCEPTED_BASELINE_REVALIDATION.md) and [EXP-004 results](../experiments/EXP-004/RESULTS.md) for exact commits, binary/input identities, measurements and conditions. Historical P0 stops and startup failures remain evidence of their recorded checkpoints; the blocker was dispositioned, transfers passed, explicit EXP-004 reauthorization occurred and the experiment completed.

EXP-004's real-ROM evidence is lowres and includes CurrentSub and FixedColor addition with zero-valued main backdrop operands on math-enabled samples. It does not demonstrate general two-nonzero-operand addition or saturation in that ROM slice. Hires/history, subtraction, halving and other specified branches have focused host evidence, not equivalent real-ROM coverage. The callback capture crosses a raster/frame boundary and includes backing-only stores; it is not a complete displayed frame. Broader execution-state equivalence and universal compatibility remain unproven.

The [bounded comparative audit](../research/RELATED_WORK_SURVEY.md) is complete for its inspected revisions and scope. The next documentation milestone is review of these proposed replacements and the [draft offline replay/preview contract](../specs/OFFLINE_REPLAY_PREVIEW.md). No next implementation is authorized.

## 5. Architectural hypothesis and research question

The strategic question remains which emulation architecture and interception boundary can supply sufficiently rich graphics information without compromising accurate execution. The experiments provide useful narrow interception evidence; this is no longer an entirely untested idea.

A candidate flow is:

```text
Accurate SNES execution → preserved PPU facts → graphics representation
                       → enhancement renderer → modern presentation
```

That flow remains a hypothesis. It is not a selected core adapter, scene model, GPU API or production interface. BG/OBJ coordinates, fetch origins, palettes, windows, priorities, composition decisions, operands and timing may help, but available winner records do not automatically contain all asset bytes, hidden candidates, persistent identities or complete frame ownership. Capture what a demonstrated consumer needs; indiscriminate collection is not the goal.

## 6. Facts, meaning and rendering policy

Keep three categories distinct:

| Category | Examples | Authority |
| --- | --- | --- |
| Native facts | Observed fetch, selected source, palette value, operand, control, raster position | Inspected implementation and scoped evidence |
| Authored meaning | This occurrence is a torch; a surface may emit; a region has a depth hint | Explicit author/profile interpretation |
| Renderer policy | Glow radius, blend, sampling, fallback and display conversion | Chosen rendering behavior, still subject to validation |

A capture occurrence is not automatically a reusable asset, and an asset is not automatically a persistent game entity. A composition winner may be clipped, skipped or consumed differently by later math. Selection, arithmetic consumption and nonzero numerical contribution are different claims. Priority is not physical depth; brightness is not emission; a sprite is not a light source by definition. Preserve uncertainty instead of manufacturing a complete scene.

## 7. Universal enhancement and profiles

The approved goal combines a useful universal foundation with optional game-specific profiles. Profiles may enrich depth, lighting, material response, room/level behavior, asset recognition, camera rules, replacement art and widescreen handling. These examples do not select fields, serialization or scripting.

Prefer understandable authored data when it suffices; justify scripting if a concrete need emerges. Missing or incompatible profiles must preserve playable reference behavior. Asset identity is difficult because VRAM, tile arrangements, palettes, animation and context change. Any identity method needs demonstrated validity over its claimed scope, including version/context mismatches and faithful fallback.

## 8. Light, materials and visual restraint

Potential work includes ambient, point and directional lighting; controlled falloff; restrained bloom; emissive art; normal/emissive maps; atmospheric effects; shadows and richer material response. Original torch pixels, for example, might remain intact while authored meaning controls surrounding glow. None of this means every bright pixel should become a light.

Depth hints, masks and material maps may be manually authored, procedurally assisted or generated offline with human review. Pixel-art readability, temporal stability and coherent artistic direction determine value. Effects should be independently understandable and adjustable; avoid a pile of unrelated effects that erases the original composition. Physical lighting and shadows need information the current captures do not establish.

## 9. Depth, layers and spatial interpretation

Layer priority, scroll relationships, parallax and Mode 7 behavior offer clues, not a universal physical world model. Separate observed relationships from inferred depth and explicit profile authoring. Room-specific interpretation may be useful where universal inference fails. Unknown depth should not corrupt native occlusion or require fabricated geometry.

Reflection, fog, particles and other spatial effects remain exploratory goals. Their data requirements, visual worth and compatibility must be established separately; they are not prerequisites for a restricted first consumer.

## 10. Resolution, motion, Mode 7 and widescreen

Higher-resolution rendering can mean improved component reconstruction, supersampling, more precise transformation or scrolling, cleaner gradients and transparency, rather than merely scaling a completed framebuffer. Artwork sampling, categorical masks, effect fields and final viewport scaling have different needs and should be evaluated separately.

Mode 7 and related prior work are research subjects, not a core selection. Complete Mode 7 lineage remains a gap. Widescreen may encounter unloaded offscreen content, object spawning, camera assumptions, garbage graphics or changed gameplay. Game-specific rules or patches require deliberate scope and authorization. Interpolation, subpixel motion, HDR and reconstruction systems remain unresolved; avoid temporal instability and invented artwork.

## 11. Assets, AI and reconstruction

Optional higher-resolution BG, sprite, tile, UI or effect replacements and material maps remain long-term possibilities. They require reliable enough identity and context, authoring/validation workflows and an original fallback. A provenance token alone is not a complete replacement-asset contract.

An offline workflow of candidate generation, human review and approved deterministic runtime assets is a useful AI hypothesis. It is not a selection of runtime generative AI or a model/provider. DLSS-like reconstruction is an inspiration, not an architecture: motion, depth, camera and temporal-history requirements must first be shown to exist or have honest substitutes. Do not hallucinate per-frame visual detail or confuse aesthetic examples with implemented output.

## 12. Foundation and technology choices

Evaluate possible cores using execution accuracy, PPU access, maintainability, modularity, performance, documentation, license, platform/tooling fit and ability to preserve reference behavior. bsnes, bsnes-HD, Snes9x and higan-related work have been candidates; the bounded audit and current evidence should guide additional questions rather than an endless broad survey.

Production language, graphics API, shader language, platform/hardware baseline, Studio framework, profile format and distribution remain undecided. C++, Python, MSYS2 and Windows were used in research; that does not select a production stack. Vulkan, Direct3D, Rust or any abstraction layer require their own tradeoffs. Prove a useful path before extracting a stable interface; do not build speculative multi-core infrastructure.

## 13. Performance and practical use

Measure CPU/GPU cost, memory, capture size, serialization, frame pacing, latency, synchronization, asset loading and shader compilation when relevant. Stable gameplay and recording matter more than an isolated visual demonstration. State hardware, build, input and execution context with measurements; current experiment instrumentation is not proof of acceptable production cost.

Controls, saves, configuration and reliable OBS capture belong in product evaluation. A supported build, a passing host fixture, framebuffer passivity and complete execution-state equivalence are separate claims. The documented restricted-context Direct3D 9 startup failure concerned the specified driver/configuration; it is not evidence that all headless/None-driver runs or Windows executions fail.

## 14. Authority, maturity and history

Use this hierarchy: maintained canonical current state; active accepted ADRs/current specifications; verified repository reality; recent relevant session records; older records; brainstorming. An unaccepted draft specification remains a proposal despite its location. Recency breaks ties only among comparable authority; an attractive recent idea cannot overrule an accepted decision. Repository behavior may expose a contradiction with intent and should trigger explicit reconciliation.

Use IDEA, HYPOTHESIS, INVESTIGATING, ACCEPTED, IMPLEMENTED, VERIFIED, REJECTED and SUPERSEDED precisely. Implementation is not verification; verification has conditions; acceptance has scope. Do not label an unselected alternative REJECTED without an actual decision.

The GTC-HD `docs/` tree governs project decisions. Upstream code governs claims about that implementation/revision, not GTC-HD architecture. Experimental worktrees are research, not production. Historical evidence-producing commits, sanitized public equivalents and later corrected integrations are distinct identities. The [publication map](../research/BSNES_EXPERIMENT_PUBLICATION_MAP.md) records the dated public snapshot; do not imply corrected source publication from local availability.

## 15. Evidence and experiment discipline

Ground claims in inspected source paths/symbols/revisions, hardware or vendor documentation, primary research and reproducible experiments. Label source observation, inference, hypothesis and uncertainty. An external project's feature or success does not establish transferability, licensing suitability or acceptance here.

Use small falsifiable experiments: question, method, inputs/identity, expected discriminating evidence, result, limitations and next decision. Report unsupported cases and failures. Preserve dated sections, raw measurements and hashes rather than retroactively making earlier records know later outcomes. Do not reopen completed work without a contradiction or concrete consumer requirement. Broad compatibility claims need broader representative evidence than one game/window.

## 16. Collaboration, decisions and documentation

Xavier owns direction and acceptance. The GPT acts as a technical partner: challenge assumptions, explain alternatives, recommend bounded work and interpret evidence. Codex inspects actual repository state and executes specifically authorized work, reporting files, validation, deviations and remaining uncertainty. A prompt or completion report is not itself an accepted architectural decision or independently verified result.

Recommend ADRs for foundational, cross-cutting or costly-to-reverse choices, including core, interception, representation, renderer or profile architecture. Record context, alternatives, rationale, consequences, validation and supersession when a decision is made; do not manufacture retrospective acceptance or assign speculative ADR numbers. Keep routine research in focused reports.

Maintain lean current state, specifications, results and useful session handoffs. A handoff should convey the objective, findings, decisions made/not made, evidence, deviations, risks and next action. Update canonical state for material milestones and decisions, not every thought; explicitly say whether it changed. Use portable public references and keep private inputs, captures and machine paths private.

## 17. Roadmap and proposed next consumer

Long-term areas remain foundation, graphics information, independent rendering, universal enhancement, profiles, depth, lighting, assets and showcase experiences. Their ordering is provisional. The present sequence is completed baseline/EXP-001–004 → completed comparative audit → this reconciliation → contract review → separately authorized bounded consumer.

The proposed offline consumer would independently reconstruct a supported captured lowres interval, compare against native output as an oracle, and provide one capture-bound source annotation with restrained adjustable glow. Reference/Replayed/Enhanced/difference views, honest operand-membership semantics, explicit ownership/history and exact zero-strength restoration would test whether the data is useful. This is a DRAFT, not demonstrated reconstruction or accepted architecture. Verify actual retained input identity/schema before any future run; this reconciliation did not inspect private captures.

Complete hires/history ownership remains a later candidate. Persistent identity, complete assets/frames, Mode 7, physical depth/shadows and a full Studio are outside this proposed slice; they are not automatic prerequisites for it. The draft does not reduce the product vision to glow.

## 18. Open decisions and success

Unresolved questions include final core/interception, sufficient graphics contracts, asset/entity identity, universal-versus-authored interpretation, lighting/depth methods, API/language/platform, profile trust/distribution, reconstruction/scaling and an initial product showcase. Historically discussed game candidates include The Legend of Zelda: A Link to the Past, Super Mario World, F-Zero and Chrono Trigger. None is selected as the product showcase; SMW's validation role does not select it. Choose useful graphical behaviors to investigate without designing the universal system around one game's quirks.

Success combines accurate familiar gameplay, preserved artwork, coherent added visual life, useful authoring and reliable GamingTheClassX presentation. Progress is both working capability and eliminated uncertainty. Architecture earns acceptance through evidence and explicit decisions; the immediate action is document and scope review, not unapproved implementation.
