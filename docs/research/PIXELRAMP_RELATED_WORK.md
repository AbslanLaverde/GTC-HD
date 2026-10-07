# PixelRamp Related Work and GTC-HD Product/Roadmap Implications

Review date: October 5, 2026. Scope: public-source research synthesis and product-direction record.

**Reconciliation notice — October 6, 2026:** [Product Direction](../PRODUCT_DIRECTION.md) now provides the canonical home for the already approved intentions recorded here. [Project State](../PROJECT_STATE.md) records the accepted experimental baseline and completed EXP-004; [the draft next contract](../specs/OFFLINE_REPLAY_PREVIEW.md) awaits review and separate implementation authorization. The approval context, earlier blocked checkpoints and later refresh below remain historical evidence, not current gate instructions. No external-source refresh was performed for this reconciliation.

**Later post-EXP-004 refresh, October 5, 2026:** [section 20](#20-post-exp-004-source-availability-refresh) records the new availability check and current GTC-HD status. Earlier blocked-EXP-004 and project-state statements below retain their historical checkpoint context; they are not the current gate.

**PixelRamp is significant contemporary related work. Its published description is relevant to GTC-HD; this report is not an audit of its unpublished implementation.**

**ACCEPTED PRODUCT DIRECTION:** Xavier has explicitly approved GTC-HD as its own player-facing product, a play-first Runtime, a future Studio with pause/select/inspect/modify/live-preview authoring, shareable profiles and a long-term community library, and usable universal enhancement enriched by optional authored knowledge. These are intended product outcomes, not implemented features or accepted implementation architecture.

**No emulator/core, renderer architecture, API, language, Studio framework, profile schema or baseline is accepted here. EXP-004 remains blocked.** Canonical-state placement is deferred to the planned post-EXP-004 reconciliation; `PROJECT_STATE.md` is unchanged.

## 1. Sources, revision and authority

The strongest public PixelRamp source is its [official repository](https://github.com/Artificial-Age/PixelRamp-SNES-Remaster-Toolkit). The inspected branch is `main`, commit [`89099c1e5d3b97f0408b36ffe2fae955e49234a5`](https://github.com/Artificial-Age/PixelRamp-SNES-Remaster-Toolkit/commit/89099c1e5d3b97f0408b36ffe2fae955e49234a5), dated September 2, 2026. The public tree contains only `.gitignore` and `README.md`; that is an independently inspectable publication fact, not evidence about private capabilities. The README calls this a placeholder with implementation publication pending. [Pinned tree](https://github.com/Artificial-Age/PixelRamp-SNES-Remaster-Toolkit/tree/89099c1e5d3b97f0408b36ffe2fae955e49234a5).

External sources used:

- **S1:** [Official README at the inspected revision](https://github.com/Artificial-Age/PixelRamp-SNES-Remaster-Toolkit/blob/89099c1e5d3b97f0408b36ffe2fae955e49234a5/README.md).
- **S2:** [Creator's r/snes discussion](https://www.reddit.com/r/snes/comments/1w5g4jj/i_built_a_realtime_snes_remaster_toolkit_on_a/), including the post and visible replies by `ArtificialAGE` and community members.
- **S3:** [Creator's r/RetroArch discussion](https://www.reddit.com/r/RetroArch/comments/1w5g7dz/snes_remastering_toolkit_fork_of_snes9x/), including the authoring, community-library and depth-buffer replies by `ArtificialAGE`.

The September creator discussions are historical statements, not a release schedule or independently verified demonstration of completeness. The linked videos were not independently evaluated in this review; demonstration details below are attributed to the creator's accompanying text.

GTC-HD repository context: branch `main`, HEAD `5e12ae48338321d329e10f95453deb25aaef5960`. Inputs were [workspace instructions](../../AGENTS.md), [README](../../README.md), [project state](../PROJECT_STATE.md), [research index](README.md), [bsnes architecture audit](BSNES_ARCHITECTURE_AUDIT.md), current EXP-001/002/003 result summaries and the EXP-004 specification. No dedicated product/design authority document was found in the tracked documentation.

Evidence labels:

| Label | Meaning here |
| --- | --- |
| DOCUMENTED PIXELRAMP CLAIM | Official documentation describes a capability or intended implementation; its working code was not inspected. |
| CREATOR STATEMENT | The creator describes a technique, demonstration or ambition in discussion. |
| COMMUNITY OBSERVATION | A participant's reaction or question; neither a benchmark nor a verified defect. |
| GTC-HD INFERENCE | A reasoned implication for GTC-HD, not an external implementation fact. |
| GTC-HD IDEA / INVESTIGATING / DEFERRED | A possible future experiment or design option, not selected architecture. |
| ACCEPTED PRODUCT DIRECTION | Xavier's explicit approval of a product goal in this task; no implementation choice follows automatically. |
| UNKNOWN | Available evidence does not establish the answer; absence of published code is not absence of capability. |

## 2. What PixelRamp publicly describes

**DOCUMENTED PIXELRAMP CLAIM — S1:** PixelRamp describes a research/prototype enhancement path inside patched Snes9x 1.63 on Windows/D3D11. Its palette-aware 2x/8x processing combines bloom, light-cast effects, optional layer-Z and object-specific sprite rules. It names `native/pixelramp_gpu/` for shared analysis/compute and a viewer, and `csharp/` for the C# / Avalonia Remaster Studio direction. Python supports experiments and golden references rather than the shipping runtime. These paths describe the creator's larger local project, not published source directories. [Official README](https://github.com/Artificial-Age/PixelRamp-SNES-Remaster-Toolkit/blob/89099c1e5d3b97f0408b36ffe2fae955e49234a5/README.md).

**CREATOR STATEMENT — S2:** The approach is described as PPU interception with game/ROM-specific configuration, rather than ROM modification. Exact hook locations remain unknown. [Creator post](https://www.reddit.com/r/snes/comments/1w5g4jj/i_built_a_realtime_snes_remaster_toolkit_on_a/).

Public statements about a functioning prototype do not establish a public release, universal correctness or complete compatibility. No PixelRamp emulator/filter/Studio internals were audited.

## 3. Creator-described techniques and their limits

The following are **CREATOR STATEMENT**, not audited implementation facts:

| Topic | Publicly described behavior | Source |
| --- | --- | --- |
| Working canvas | An 8x example expands 256x224 to 2048x1792, retaining silhouettes while allowing finer lighting/shadow calculations. | [S2](https://www.reddit.com/r/snes/comments/1w5g4jj/i_built_a_realtime_snes_remaster_toolkit_on_a/) |
| Depth and lighting | Layer Z-planes, screen-space shadows, and sprite/tile-hash-selected point lights with radius/falloff and neighboring-surface illumination. | [S2](https://www.reddit.com/r/snes/comments/1w5g4jj/i_built_a_realtime_snes_remaster_toolkit_on_a/) |
| Profiles | Per-game rules matched by ROM checksum. | [S2](https://www.reddit.com/r/snes/comments/1w5g4jj/i_built_a_realtime_snes_remaster_toolkit_on_a/) |
| Presentation | 120 Hz sub-frame interpolation using background scroll registers and OAM motion vectors. | [S2](https://www.reddit.com/r/snes/comments/1w5g4jj/i_built_a_realtime_snes_remaster_toolkit_on_a/) |
| Comparison | Live original/enhanced A/B toggles described for Mega Man X and Cybernator. | [S2](https://www.reddit.com/r/snes/comments/1w5g4jj/i_built_a_realtime_snes_remaster_toolkit_on_a/) |
| Authoring | Pause the game and modify it live. | [S3, author reply about real-time editing](https://www.reddit.com/r/RetroArch/comments/1w5g7dz/snes_remastering_toolkit_fork_of_snes9x/) |
| Sharing | Downloadable profiles and a community remaster library are ambitions. | [S3, profile/library replies](https://www.reddit.com/r/RetroArch/comments/1w5g7dz/snes_remastering_toolkit_fork_of_snes9x/) |
| Evolving depth work | The creator reports moving toward a depth buffer while tuning separation/shadow behavior. | [S3, depth-buffer reply](https://www.reddit.com/r/RetroArch/comments/1w5g7dz/snes_remastering_toolkit_fork_of_snes9x/) |

**UNKNOWN:** These descriptions do not establish BG/OBJ depth rules, arbitrary pixel-group selection, a complete glow/shadow property schema, selector hashing details, interpolation correctness, or the final depth-buffer design. Preserve the narrower supported claims rather than filling gaps with an imagined implementation.

## 4. Similarities to GTC-HD

**GTC-HD INFERENCE:** The descriptions above overlap substantially with GTC-HD's goals: runtime enhancement, access to graphics meaning near the PPU, preserved pixel-art silhouettes, modern lighting/depth, optional authored game knowledge, original/enhanced comparison, creator tooling and reusable profiles. This is useful related work, not a competitive ranking or evidence that either project has solved universal enhancement. PixelRamp's stack choices do not select GTC-HD's stack.

The relevant GTC-HD foundation is the [README's rendering hypothesis and product direction](../../README.md): retain useful native graphics context, preserve faithful original output, and enrich games without demanding a manual remaster of every title.

## 5. GTC-HD evidence and PixelRamp unknowns

GTC-HD makes native SNES execution authoritative and explicitly tests observation/passivity. Its existing research establishes the following bounded results:

| GTC-HD evidence | Current conclusion and limit |
| --- | --- |
| [EXP-001](../experiments/EXP-001/RESULTS.md) | VERIFIED FOR TESTED EXP-001 CONDITIONS: tiled-BG fetch provenance and deterministic framebuffer passivity. A fetch record is not final visibility; complete execution-state equivalence is unproven. |
| [EXP-002](../experiments/EXP-002/RESULTS.md) | VERIFIED FOR TESTED EXP-002 CONDITIONS: OAM evaluation → actual fetch → surviving OBJ candidate lineage, including documented overlap, with tested framebuffer passivity. OAM slots are not persistent game entities. |
| [EXP-003](../experiments/EXP-003/RESULTS.md) | VERIFIED FOR TESTED EXP-003 CONDITIONS: native main/sub composition winners and provenance. This does not establish final color or physical depth. |
| [EXP-004](../experiments/EXP-004/SPEC.md) | Color-math/native-sample provenance is the research frontier, not a completed capability. P0 is complete; implementation remains blocked pending native-baseline disposition and explicit reauthorization. |

The [bsnes audit](BSNES_ARCHITECTURE_AUDIT.md) explains why graphics computation can affect CPU-visible latches and status. Its observations concern its recorded bsnes revision; they are not findings about PixelRamp or proof that every GTC-HD side effect has been validated. An accurate original/native reference path remains a durable GTC-HD requirement. Native composition priority must not be treated as physical scene depth.

**UNKNOWN — PixelRamp implementation questions, not alleged defects:**

| Area | Not established by available public implementation evidence |
| --- | --- |
| Interception and passivity | Exact PPU hook locations, retained native work, timing and execution passivity. |
| Composition | Native color math, windows, hires/pseudo-hires and Mode 7 treatment. |
| Raster behavior | HDMA/mid-frame changes and temporal resource consistency. |
| Identity | Dynamic VRAM/OAM reuse, animation identity and multi-sprite conceptual objects. |
| Lifecycle | Save-state, rewind and run-ahead behavior. |
| Presentation cost | End-to-end latency and measured performance across named hardware/settings. |
| Contracts | Exact profile schema, renderer architecture and representation boundaries beyond the high-level public descriptions. |

GTC-HD's measured emphasis is a difference in available research evidence. It does not show that PixelRamp lacks these capabilities or has weaker correctness.

## 6. Core lesson: native truth, interpretation and renderer policy

**GTC-HD INFERENCE:** PixelRamp materially reinforces the value of combining automatic/native semantic information, optional authored interpretation and a modern renderer. GTC-HD should maintain three distinct concepts:

| Concept | Meaning | Example |
| --- | --- | --- |
| Native truth | What native execution actually did: fetched provenance, composition decisions, timing/raster semantics and reference output. | A captured OBJ candidate supplied the winning main-screen source at a recorded time. |
| Authored interpretation | An author's additional meaning, material, approximate physical depth, emission or artistic rules. | This graphic depicts a torch; this surface is stone. |
| Renderer policy | How available evidence and interpretation produce lighting, shadows, materials or depth-aware effects. | A selected preset determines the torch's light response. |

**ACCEPTED PRODUCT DIRECTION:** Profiles add interpretation; they must not masquerade as native emulation truth. The table establishes a conceptual distinction, not three selected APIs, modules, processes or file formats. Unknown semantic meaning should remain identifiable as unknown.

## 7. Universal enhancement plus optional profiles

**ACCEPTED PRODUCT DIRECTION:** A handcrafted profile must not be required simply to run a game in GTC-HD. A game without a compatible profile should still have a usable universal enhancement path and be playable. Compatibility breadth and universal enhancement quality remain open engineering questions, not guarantees established by current experiments.

```text
ROM -> identify game/version
       |
       +-- no compatible profile -> universal enhancement -> play
       |
       +-- compatible profile -> universal enhancement
                                 + authored game knowledge
                                 -> richer enhancement -> play
```

A profile means “we know more about this game,” not that the profile is the only reason enhancement can work. Profiles enrich the common foundation; they do not become an authoring prerequisite for players.

## 8. Runtime: an independent, play-first GTC-HD product

**ACCEPTED PRODUCT DIRECTION:** GTC-HD should ultimately be its own player-facing product, not merely “bsnes plus.” That identity does not decide whether an emulator is embedded, how it is integrated, or which core is chosen.

The desired Runtime experience combines ROM launch/identification, accurate SNES execution, a semantic bridge, faithful original/native rendering, a modern enhancement renderer, and an accessible Original/Enhanced comparison or toggle. It should offer universal fallback, optional game profiles, convenient visual presets/configuration, usable controllers, appropriate save-state support, stable gameplay, output-resolution controls and recording/OBS-friendly behavior. These are product requirements and goals, not present implementation claims or guarantees about untested save-state integration.

```text
Launch GTC-HD -> choose ROM -> identify game/version
             -> load universal renderer -> apply compatible profile if available
             -> a few first-launch preferences if needed -> PLAY
```

Ordinary play should not require lengthy content production or an external authoring step. Reliable configuration should support that experience. “Semantic bridge” names a desired role, not an accepted transport or semantic-frame contract.

## 9. Studio: inspect native meaning while authoring

**ACCEPTED PRODUCT DIRECTION:** GTC-HD should eventually provide a Studio/authoring experience:

```text
Run game -> pause/capture -> click/select object or asset
         -> inspect semantic/provenance information
         -> assign or modify authored interpretation
         -> preview immediately -> save profile
```

Ideally, selection exposes what GTC-HD actually knows: native provenance, graphics/tile identity, palette/context, BG or OBJ lineage, composition information and any current profile match. Authors should be able to work from that evidence instead of only a flattened screenshot. Resolving a clicked visual group into a persistent conceptual object is still research, not an already solved consequence of EXP-001/002/003.

Possible authored properties include semantic asset identity, approximate physical depth, material category, receives-light/emits-light behavior, light color/intensity/radius/falloff, shadow behavior and enhancement metadata. **GTC-HD IDEA:** These are examples, not an accepted schema. Native facts and author-supplied meanings should remain distinguishable in inspection and preview.

No decision is made about one executable versus several, Runtime/Studio communication, UI framework or process ownership.

## 10. Shareable profiles and a future community library

**ACCEPTED PRODUCT DIRECTION:** Profiles/configurations should be designed to become shareable. The long-term goal is a community library of game enhancement profiles:

```text
Author profile -> export/publish -> another user obtains it
               -> identify matching ROM/version -> apply profile -> play
```

This approves the experience, not a service design. Hosting, cloud architecture, accounts, moderation, a package registry, distribution protocol, signing/trust, automatic downloads and legal/distribution policy are all deferred research/design choices. This task neither selects those mechanisms nor authorizes publication or distribution of content.

## 11. Semantic selectors

**GTC-HD IDEA / FUTURE RESEARCH:** The described hash-based matching motivates repeatable asset recognition. Investigate whether GTC-HD's captured provenance can support selectors more informative than a visual hash; do not assume that it already does.

Candidate inputs include ROM/game identity, graphics source and tile/character identity, palette identity, BG provenance, OBJ/OAM lineage, native priority/composition context, VRAM source, animation context and temporal identity. Different combinations may address different ambiguities:

- Identical graphics can serve different semantic roles.
- Palette variants and animated tile sequences can change appearance without changing intended meaning.
- Reused OAM slots and dynamic VRAM uploads can change meaning without changing the storage address.
- Several hardware sprites can form one conceptual object, and BG content can depict an apparent object.

No persistent asset-identity scheme, matching algorithm or hashing contract is selected. Profile selectors must not claim stable game-entity identity merely because native storage identity is available.

## 12. Native composition is not physical depth

**GTC-HD INFERENCE / DESIGN GUIDANCE:**

> **SNES COMPOSITION PRIORITY != PHYSICAL SCENE DEPTH**

Native evidence can establish “this source won over that source.” It does not establish that a surface is three meters behind an object. Conceptually distinguish `NativeOcclusion` / `NativeComposition` from `SceneDepthHint` / physical-depth interpretation; these names are explanatory, not accepted schema fields.

Physical depth may eventually come from cautious inference, game profiles, author input or optional advanced tooling. When it is unknown, enhancement should degrade gracefully rather than impose strong unsupported spatial assumptions. The original/native path remains the reference for native composition even when enhancement intentionally adds artistic depth.

## 13. Integer working canvas

**GTC-HD IDEA / INVESTIGATING:** A larger integer working representation may preserve native pixel geometry while allowing smoother light, shadow and material calculations:

```text
Native semantic pixel grid -> integer-expanded working representation
                          -> continuous/subpixel effects -> final presentation
```

This is an experiment concept inspired by the described approach, not a chosen renderer. GTC-HD has not selected 2x, 4x, 8x, dynamic scale, a reconstruction/upscaling algorithm or a final output-scaling method. A larger canvas alone does not supply missing identity, composition or physical depth.

## 14. Visual restraint and user control

**COMMUNITY OBSERVATION:** The discussions contain enthusiasm alongside concerns about distracting glow, spatially confusing shadows, interpolation preferences and the burden of per-game adjustment. Those are subjective reactions and usability questions, not verified technical defects. [r/RetroArch feedback](https://www.reddit.com/r/RetroArch/comments/1w5g7dz/snes_remastering_toolkit_fork_of_snes9x/), [r/snes feedback](https://www.reddit.com/r/snes/comments/1w5g4jj/i_built_a_realtime_snes_remaster_toolkit_on_a/).

**GTC-HD PRODUCT-DIRECTION GUIDANCE:** “Enhance the pixel art. Never erase the pixel art.” Effects should support the artwork, not dominate it. Strength should eventually be adjustable through controls/presets, Original mode must remain available, and defaults should not showcase every effect simply because it exists.

**GTC-HD IDEA:** Original, Faithful, Enhanced and Rich/Custom illustrate a possible range of presets. The names and specific presets are not accepted.

## 15. Deferred and optional features

**GTC-HD IDEA / DEFERRED:** HDR and 120 Hz/higher-refresh semantic interpolation are outside the current critical path. Neither is necessary to prove the core renderer. Temporal interpolation additionally needs trustworthy identity and discontinuity handling for teleports, animation replacements, despawns, wraparound, camera cuts, sprite reuse and raster changes. A creator's interpolation claim does not validate those cases for GTC-HD.

**GTC-HD IDEA ONLY:** Blender or similar tools might later support complex depth layouts, normals, scene geometry, lighting authoring and asset preparation. Blender is not required by Runtime and should not be required for normal Studio work. Common authoring should remain possible within Studio. Blender integration is unselected; Unreal Engine is unselected; attractive external-engine effects do not constitute an architecture decision.

## 16. Roadmap implication: semantic-to-visual vertical slice

**RECOMMENDATION / PLANNED DISCUSSION — not accepted architecture or implementation authorization.** After the native-output-bounds investigation has a concluded disposition, EXP-004 is completed, and the planned project-state/foundational-document reconciliation is performed, strongly consider moving quickly to a **semantic-to-visual vertical slice**.

The smallest useful slice should aim to:

1. Define a minimal semantic-frame contract justified by EXP-001 through EXP-004 evidence.
2. Preserve the original/native rendering path.
3. Feed captured meaning into a minimal independent GTC-HD renderer.
4. Support one tiny optional authored profile while retaining a profile-free path.
5. Demonstrate at least one real depth/light interaction and live Original/Enhanced comparison.
6. Identify what information that renderer actually lacks.

Use those observed needs to prioritize focused PPU/semantic experiments:

```text
Prove semantics -> build smallest renderer using them -> observe missing information
                -> design focused experiment -> improve semantics -> improve renderer
```

The recommendation is to test whether semantic research helps an actual enhancement renderer before starting another long speculative research chain. It does not bypass the baseline gate, claim EXP-004 completion, choose a proof-of-concept game, select bsnes, or replace the README roadmap in this task.

## 17. Technical choices deliberately unresolved

The following remain **UNRESOLVED**, regardless of product-direction approval:

- Final SNES emulator/core and final bsnes disposition.
- Renderer language, graphics API, renderer architecture and semantic-frame/interface contract.
- Runtime/Studio communication and single/multiple executable packaging.
- Studio technology/framework; no Avalonia choice is imported from PixelRamp.
- Profile format/schema, scripting language, persistent asset identity and matching algorithm.
- Profile hosting/distribution, server/cloud implementation and the ecosystem mechanisms listed in section 10.
- First proof-of-concept game, modern upscaler, working/output scale and final hardware baseline.
- Blender/external-engine integration, HDR and 120 Hz interpolation.

The Runtime and Studio labels name product experiences. They do not resolve implementation boundaries.

## 18. PixelRamp follow-up when source is published

**PLANNED FOLLOW-UP NOTE:** When the actual Snes9x/filter/Studio implementation becomes public, pin an exact revision and conduct a separately scoped source audit. This is a documented follow-up trigger, not a scheduled monitoring service.

Focus that audit on exact PPU interception points; preservation of native execution and timing/passivity; graphics/asset identity; profile representation; layer/depth representation; renderer integration; hires/pseudo-hires; windows; color math; Mode 7; HDMA/raster behavior; save-state interaction; and lessons relevant to GTC-HD's emulator/core choice. Revisit the unknowns in section 5 from source and evidence. Do not infer answers before publication.

## 19. Documentation fit and reconciliation notes

This report is linked from the existing research index. It records the explicit product approval now without creating a new canonical product-document hierarchy or changing project state.

| Existing documentation | Fit, tension or future action |
| --- | --- |
| README: universal enhancement plus optional profiles is a preferred direction | Consistent in substance. This task explicitly approves that product goal; future reconciliation should align its authority wording. |
| README: provisional phases place independent rendering, profiles, depth and lighting in separate stages | The proposed small vertical slice spans parts of those stages. Discuss sequencing after the stated prerequisites; no roadmap rewrite or phase change is made now. |
| PROJECT_STATE: September 18 next action is the initial bsnes audit | That checkpoint predates the completed audit and EXP-001/002/003 evidence. This known chronology gap remains for the planned reconciliation, not a reason to rewrite history here. |
| Historical bsnes audit refers to the older `project/` authority location | Preserve the historical wording; current authority is `docs/` under AGENTS.md. New references use the current tracked paths. |
| No dedicated product/design authority document | Runtime, Studio, live authoring and community-library approval have no established canonical product home. Keep them here pending authorized post-EXP-004 placement. Do not mistake their temporary research-document location for unapproved goals. |
| Current experiment results and EXP-004 gate | Product approval does not alter tested scopes, accept a baseline or unblock EXP-004. |

No substantive conflict was found with GTC-HD's fidelity priorities or existing universal-plus-profile aim. The discrepancies are authority wording, stale chronology and a proposed sequencing change that still requires discussion. PixelRamp's unpublished implementation also prevents any claim that the two projects have equivalent internals.

`PROJECT_STATE.md`, AGENTS.md and historical experiment documents remain unchanged. No ADR, architecture acceptance, source/worktree modification, build, test, ROM execution, commit or push occurred in this task.

## 20. Post-EXP-004 source-availability refresh

**SOURCE OBSERVATION — October 5, 2026, subsequent comparative audit:** the public `main` revision remains `89099c1e5d3b97f0408b36ffe2fae955e49234a5`. Its [pinned tree](https://github.com/Artificial-Age/PixelRamp-SNES-Remaster-Toolkit/tree/89099c1e5d3b97f0408b36ffe2fae955e49234a5) still contains only `.gitignore` and `README.md`; the [README](https://github.com/Artificial-Age/PixelRamp-SNES-Remaster-Toolkit/blob/89099c1e5d3b97f0408b36ffe2fae955e49234a5/README.md) still describes a placeholder pending implementation publication. No public implementation was available to audit. Earlier documentation/creator claims remain attributed claims; the community discussions and videos were not newly validated by this refresh.

**DOCUMENTED CLAIM — current GTC-HD authority:** [PROJECT_STATE](../PROJECT_STATE.md) now records Candidate A as the accepted corrected experimental baseline, completed corrected EXP-001/002/003 revalidation and [EXP-004 VERIFIED FOR TESTED EXP-004 CONDITIONS](../experiments/EXP-004/RESULTS.md). This supersedes the earlier blocked/status descriptions in this note, without changing their historical evidence or selecting a final core, renderer or profile schema. The approved product direction above remains intact.

The [post-EXP-004 comparative audit](RELATED_WORK_SURVEY.md) recommends a bounded offline replay plus frozen authoring preview before live integration or physical-depth effects. That recommendation narrows the first proposed build; it does not revoke the eventual Runtime/Studio/profile goals or authorize implementation. PixelRamp's unpublished internals do not block this next consumer experiment.
