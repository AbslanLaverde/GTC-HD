# EXP-004 — Color Math and Native Sample Provenance

Date: September 22, 2026.

**Status:** P0 COMPLETE / EXP-004 IMPLEMENTATION BLOCKED / SEPARATE NATIVE-BASELINE INVESTIGATION REQUIRED

**Research target:** bsnes cycle PPU

**Experimental dependency:** EXP-003 composition provenance

**Frozen source baseline:** `76bdb9250befa62fcbf23fcff2ef962fe2f58215`

**Design evidence:** [Source audit and implementation plan](SOURCE_AUDIT_AND_IMPLEMENTATION_PLAN.md)

**Production architecture impact:** None — experimental research only

**Implementation gate:** EXP-004 color-math provenance implementation remains unauthorized. A separately scoped native-baseline investigation must determine the intended output/storage boundary and baseline disposition before the EXP-004 gate may be reconsidered. Source implementation remains blocked until that investigation is completed, its disposition is documented, and implementation is explicitly re-authorized.

This document specifies an experiment. The source audit informs its design; source inspection does not verify the EXP-004 preservation or passivity hypothesis. EXP-004 is neither implemented nor verified by this specification revision.

## 1. Purpose

EXP-001, EXP-002 and EXP-003 established preservation of tiled-BG, OBJ and main/sub composition provenance under their tested conditions. EXP-004 investigates the next semantic boundary:

> Can GTC-HD preserve the native color-math decisions, operands, operations, pre-brightness results and resulting native PPU output samples while retaining the source provenance established by EXP-003 and without replacing or disturbing authoritative cycle-PPU execution?

The experiment remains one staged investigation. It must account for current composition winners, carried native state where consumed, and both sample results emitted by `Screen::run()`.

The guiding principle remains:

> **Enhance the pixel art. Never erase the pixel art.**

Original game behavior, accurate SNES execution, faithful rendering semantics and pixel-art identity have priority over enhancement effects.

## 2. Why this matters to GTC-HD

A selected main or sub source is not necessarily equivalent to an emitted native sample. Native processing can gate math, clip an operand, select current sub or fixed color, consume carried main state, add or subtract, halve, and apply brightness and output encoding conversion.

A framebuffer alone cannot explain whether an output came from direct display, an arithmetic combination, clipping, or a temporal dependency. A future enhancement renderer could use preserved evidence to respect those distinctions when handling lighting, replacement assets, visibility or debugging.

Those product capabilities are not implemented by EXP-004. The experiment asks whether the native semantic path can survive, with an exact native numeric reference and explicit limits on what is known.

## 3. Source-grounded starting point and mandatory prerequisite

### 3.1 Audit authority

The completed source audit examined the EXP-004 worktree at the frozen EXP-003 implementation:

```text
76bdb9250befa62fcbf23fcff2ef962fe2f58215
Implement EXP-003 composition provenance observer
```

The earlier upstream baseline is `7d5aa1e656b9171524d01b1b22917197d8121cb4`. Relevant source includes `bsnes/sfc/ppu/screen.cpp`, `screen.hpp`, `window.cpp`, `io.cpp`, `serialization.cpp`, `main.cpp`, `ppu.cpp` and `ppu.hpp`, together with EXP-003's observer and runtime controller.

The [audit](SOURCE_AUDIT_AND_IMPLEMENTATION_PLAN.md) supplies exact source references and distinguishes source observations, existing host-test evidence, inferences and unknowns. Its findings are design constraints for this experiment, not new runtime verification. EXP-003's existing results retain their documented scope.

### 3.2 EXP-004-P0 — Native Output Destination Bounds Investigation

**P0 is complete for the documented investigation scope. It is a prerequisite stage of EXP-004, not a new numbered main experiment.**

**EXP-004-P0 disposition: STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION**

Durable evidence: [P0 output bounds report](P0_OUTPUT_BOUNDS_REPORT.md) and [P0 output bounds matrix](P0_OUTPUT_BOUNDS_MATRIX.csv), under `docs/experiments/EXP-004/`. The report retains the frozen baseline identity, source evidence, controlled fixture results and limitations; the matrix records the documented boundary cases.

The completed P0 findings are:

1. **SOURCE OBSERVATION:** The declared `uint16 output[512 * 480]` subobject contains 245,760 entries, with valid indices 0–245,759.
2. **SOURCE OBSERVATION / BOUNDS EVIDENCE:** Native logical stores exceed that declared subobject on the documented late scanlines: V=233–240 with latched overscan off, and V=240 with latched overscan on. Returning zero for a sample does not suppress its store.
3. **SOURCE OBSERVATION / BOUNDS EVIDENCE:** The overscan-clear path also exceeds the declared subobject; its final cleared row reaches indices 245,760–246,783.
4. **HOST-MEASURED LAYOUT:** The tested UCRT64 GCC 16.2.0 layout places `lightTable` immediately after `output`, with no gap. This is evidence for the tested compiler/layout, not a guarantee of native undefined-behavior consequences.
5. **CONTROLLED FIXTURE EVIDENCE:** A defined-storage fixture demonstrated layout-sensitive effects capable of changing a later valid output sample. The fixture kept accesses within a single backing allocation; it does not establish the exact consequences of crossing the native array-subobject boundary.
6. **UNKNOWN:** Exact native undefined-behavior/runtime consequences remain **UNKNOWN**, including compiler effects and real-ROM reachability. Neither harmlessness nor a particular native corruption effect is established.
7. **FIXTURE EVIDENCE / INFERENCE:** Capturing the value supplied to a store without framebuffer readback is feasible, but destination-validity accounting alone does not resolve the baseline defect or establish passive observation against it.

**EXP-004 color-math provenance implementation remains unauthorized.** A separately scoped native-baseline investigation must determine the intended output/storage boundary and baseline disposition before the EXP-004 gate may be reconsidered. Source implementation remains blocked until that investigation is completed, its disposition is documented, and implementation is explicitly re-authorized.

**EXP-004 instrumentation must not silently fix the native bounds issue.** No repair is proposed or selected by this specification. Any native baseline repair, if required, must be separately scoped and authorized, with its baseline and deterministic-reference implications documented.

## 4. Native color-path behavior to preserve

The following source observations come from the completed audit. Requirements describe what the future observer must preserve.

### 4.1 Native ordering

**SOURCE OBSERVATION:** `Screen::run()` evaluates `below(hires)` before `above()`, then performs the first light-table lookup and store before the second lookup and store. There is no intervening native timing step within this sequence.

Preserve that order. Do not model below and above as simultaneous, precompute the second lookup before the first store, or call native paths a second time.

### 4.2 Selected-source eligibility and color windows

**SOURCE OBSERVATION:** The final selected main source supplies pre-window math eligibility through the BG1–BG4, OBJ or backdrop enable. OBJ additionally requires `obj.output.above.palette >= 192` in `Screen::above()`. This restriction is not an OBJ overlap decision or current-sub eligibility rule.

Layer windows suppress composition candidates before winner selection. Color-window outputs later control primary-color permission/clipping and math gating. A selected winner can remain the winner even when its color is clipped.

Capture the selected-source eligibility and effective native gates separately. Reuse EXP-003's current color-window values where valid; those current values must not be substituted for carried controls consumed by hires below.

### 4.3 Effective second operand

The diagnostic model must distinguish at least:

| Kind | Meaning when actually consumed |
|---|---|
| `None` | No second operand; no native blend arithmetic occurred |
| `CurrentSub` | Current resolved sub color used by the above path |
| `FixedColor` | Current fixed-color value used by the native path |
| `CarriedMain` | Raw main color carried from the last active native main producer and used by hires below |

**SOURCE OBSERVATION:** When above math is enabled, requested sub blending with native `math.transparent` falls back to fixed color and disables halving. Here transparent means final sub priority zero, not a numerically black color. A colored backdrop can trigger fallback; a nontransparent black source need not.

Preserve configured preference and effective consumption separately. Record fallback only where the native path actually applies it. A gated-off operation has `None`, even if configuration would otherwise request sub/fixed math.

### 4.4 Native arithmetic

Capture actual native operands, operation, effective half state and typed result for passthrough/no math, add, subtract, add + half and subtract + half. Preserve clipping and skip reasons independently.

Native `blend()` remains authoritative. Do not reconstruct the runtime result from a second arithmetic implementation or infer operands backward from a saturated result. Independent per-channel arithmetic may be used only as a test oracle. Tests must distinguish native half-add from saturating addition followed by halving.

### 4.5 Brightness and encoding

**SOURCE OBSERVATION:** This path converts component positions as well as applying brightness:

```text
selected raw BGR555 source
→ native clipping / color math
→ pre-brightness BGR555 result
→ brightness level and native light-table processing
→ RGB555 value supplied to native framebuffer stores
```

Require explicit encodings at both boundaries. In the audited table initialization, maximum brightness maps red `0x001f` to `0x7c00`. Brightness 15 is not a raw-word identity conversion.

Capture the actual native table result supplied to each store. Encoding-aware tests must use actual native light-table behavior. EXP-003's identity light-table fixture is not evidence of brightness or encoding correctness.

## 5. Hires, mixed lifetimes and scanline history

### 5.1 Bounded temporal dependency

**SOURCE OBSERVATION:** In true hires or pseudo-hires, below can consume:

- the current sub source and its resolved raw color;
- the carried previous active main source;
- carried effective math-enable state;
- carried primary-color permission;
- carried effective operand-choice state;
- carried effective half state;
- the current add/subtract direction;
- the current fixed color when that operand is selected.

The carried main is the previous active main's **RAW selected color**, before clipping, blending or brightness. It is **NOT the previous final blended sample**. Therefore the required history is bounded; an unbounded recursive graph of earlier blended results is not required by this source path.

Conceptually, for active hires below:

| Effective branch | Primary | Second operand and arithmetic |
|---|---|---|
| Carried math disabled | Current sub, allowed or clipped using carried permission | `None`; no math |
| Carried math enabled, carried blend selects main | Current sub, allowed or clipped using carried permission | `CarriedMain`; current direction and carried half |
| Carried math enabled, carried blend selects fixed | Current sub, allowed or clipped using carried permission | `FixedColor` from current controls; current direction and carried half |

Current above subsequently uses current main, current eligibility/window decisions, and current sub/fixed selection. Current main must not be attached to a below sample that actually consumes carried main.

True hires changes BG sampling phases; pseudo-hires changes Screen emission without making the low-resolution BG path a true-hires producer. Test both.

### 5.2 Screen::Math lifetimes

**SOURCE OBSERVATION:** All seven `Screen::Math` fields are persistent and serialized, but they have mixed update lifetimes.

| Native field | Required lifetime distinction |
|---|---|
| `above.color` | Replaced by active above with the raw selected main color; below can consume its carried value |
| `above.colorEnable` | Set by active above from current primary-color permission; below consumes the carried permission |
| `below.color` | Refreshed by active below with current sub/backdrop color; above can consume it in the same composition point |
| `below.colorEnable` | Selected-main eligibility, then current math-window gating in above; carried effective math-enable for below |
| `transparent` | Refreshed by active below from sub priority zero; used by above for fallback |
| `blendMode` | Updated by above only when math is enabled; otherwise stored value can remain from an older arithmetic point |
| `colorHalve` | Updated by above only when math is enabled; otherwise stored value can remain from an older arithmetic point |

History tracking must follow the **last native state producer**, not blindly diagnostic record N-1. Native skips can preserve all Math state across several composition records. A no-math above updates main/color permissions while leaving blend/half stored but unused on the following no-math below.

A mode transition alone does not reset native Math. Preserve known continuity when the observer actually saw it, including a low-resolution predecessor to a hires sample. Invalidate diagnostic provenance when observation continuity or producer identity is missing; do not reset native state or invent a new producer to simplify the model.

Copied values, source-lineage validity and carried-control origin require separate validity. Retention success must not determine native history: an overflowed record is not permission to link to an unrelated last-retained record.

### 5.3 NativeScanlineSeed

Represent an observed native scanline initialization explicitly as `NativeScanlineSeed`.

**SOURCE OBSERVATION:** The audited `Screen::scanline()` initializes both Math colors from the native palette-zero lookup, clears both enable fields, sets transparent true, and leaves effective blend/half false. In uninterrupted execution from that seed, the first active hires below returns zero. This does not prove that its current sub source was transparent or black.

The source comments explicitly say the exact initializations are not confirmed on hardware. Separate:

- observed bsnes seed values and their native numeric consequences;
- an observed active predecessor source;
- unavailable history;
- **hardware initialization: UNCONFIRMED**.

Do not create a fictitious previous winner for a seed. Missing the seed on activation requires UNKNOWN history where no observed producer establishes it. The exact first-hires-sample SNES hardware behavior remains UNCONFIRMED unless later evidence establishes it.

## 6. Hypothesis

**HYPOTHESIS:** The cycle PPU permits passive preservation of native color decisions, actual operands, effective operation, pre-brightness result and native store values, with current and carried source provenance, without changing authoritative execution.

The source audit identifies plausible observation points. Implementation, focused tests and runtime evidence must still determine whether this hypothesis is supported under particular conditions. P0 is complete with the STOP disposition in section 3.2; the separate native-baseline investigation and explicit implementation re-authorization remain required.

## 7. Primary research questions

EXP-004 must answer:

1. Can current main/sub and carried-main source identities remain linked to actual contributing operands?
2. Can the observer preserve eligibility, color-window gates, clipping, fallback, operation and half state as actually consumed, including their different ages?
3. Can it capture actual native BGR555 results and RGB555 store values without rerunning math, memory operations or brightness lookup?
4. Can both emitted sample descriptions preserve the correct path, destination and validity?
5. Can seeds, discontinuities and incomplete lineage remain explicit without discarding known numeric evidence?
6. Can deterministic comparison support passivity for the captured paths?
7. What limits remain for hires, hardware initialization and store-to-callback association?

## 8. Required diagnostic representation and EXP-003 reuse

### 8.1 Preferred unit and shared context

Prefer **one diagnostic record per native composition position with two native sample-result descriptions**. Any alternative must have a documented semantic reason and preserve the pair's ordering and dependencies.

The shared record must carry:

- diagnostic epoch and attempted composition sequence, independent of retained-array index;
- callback/composition-interval identity, capture-relative frame, x, PPU H/V and field;
- BG mode, explicit pseudo-hires and effective hires state;
- live blank/overscan controls, latched placement/interlace controls and skip reason;
- owned current main/sub winners and selected pre-math BGR555 colors;
- current selected-main eligibility and current color-window outputs;
- copied carried native state, its producer identity/origin and validity;
- an owned carried-main winner/provenance snapshot where known, plus relevant carried-control and fallback origins.

This is an **experimental diagnostic representation**, not an accepted production semantic-frame format. Do not optimize away required distinctions or indiscriminately record all PPU state.

### 8.2 Two sample-result descriptions

Each sample must describe, where applicable:

| Required information | Meaning |
|---|---|
| Emission path and reason | Above, below, duplicated above, skipped zero or another source-established case |
| Primary source/reference | Current main, current sub or explicit non-source case |
| Raw source color | Selected BGR555 value before clipping |
| Clipping | Permission consumed, whether clipped, and effective primary operand |
| Second operand | `None`, `CurrentSub`, `FixedColor` or `CarriedMain`; reference, actual value and fallback reason |
| Math operation | Actual no-math/add/subtract branch and effective half state |
| Native result | Actual pre-brightness BGR555 return |
| Brightness | Level consumed and native light-table processing boundary |
| Store value | Actual native RGB555 value supplied to the store |
| Logical destination | Integer sample/row offsets for the native A/B writes, with aliasing or duplication identified |
| Destination validity | Inside/outside the declared callback buffer, or not established; distinguish later callback association |
| Semantic validity | Source/control history known or UNKNOWN, seed status and hardware uncertainty separately |

Copied history should remain interpretable if its producer record was not retained. Optional links must not be the sole evidence for a missing predecessor. Retained records must contain no live mutable native pointers.

### 8.3 Reuse EXP-003

Reuse EXP-003's BG provenance, OBJ provenance, current main/sub winners, selected pre-math colors, effective current color-window values, and callback-window/runtime infrastructure wherever semantically valid. Do not duplicate BG/OBJ provenance tracking or reconstruct winners from colors.

**SOURCE OBSERVATION:** EXP-003 resolves winners while its current record is private and pending; it appends only after `screen.run()`. A narrow copied-value/pending handoff is permitted where that lifecycle is insufficient. Using the last retained record as the current winner is not valid.

Preserve the distinction between EXP-003's current pre-window main eligibility/current windows and EXP-004's effective or carried decisions. Coordinate observer activation, clear, reset and export so a second controller cannot invalidate shared lineage mid-capture.

## 9. Native sample emission and callback association

**SOURCE OBSERVATION:** For composition positions where `Screen::run()` writes, ordinary low-resolution output supplies the above result to both horizontal sample slots. Hires/pseudo-hires supplies below first and above second. A/B destinations add native vertical duplication or interlace aliasing; they are not separate color calculations. V=0 returns without writes.

A low-resolution below return is not an emitted zero sample. Skipped selection can still produce native zero stores; preserve that distinction and P0's destination findings.

Describe the capture as a **native callback interval / composition interval**, not necessarily one simple 256×240 visual frame. The audited existing interval can include skipped tail positions from the previous capture-relative frame and visible positions from the next. Capture-relative frame, callback index and output destination must remain separate.

This precision does not invalidate EXP-003's tested composition result. It prevents using a record count alone as proof of complete one-to-one sample ownership in the callback buffer.

**SOURCE OBSERVATION:** PPU refresh can modify the buffer through blur or controller overlays before callback hashing. Claimed store-to-callback equivalence requires valid destinations and control of those later modifications. Invalid destinations must be explicit, not silently mapped into valid pixels.

## 10. Passivity constraints

The native cycle PPU remains authoritative. EXP-004 must not:

- repeat `paletteColor()`, skip a native lookup, or change lookup order;
- repeat stateful PPU memory operations or reread VRAM/OAM/CGRAM to reconstruct operands or lineage;
- rerun `Window::run()` or duplicate window tests as runtime truth;
- rerun winner selection or invoke below/above a second time;
- replace native `blend()` arithmetic or make observer recomputation authoritative;
- add timing steps, synchronization or emulation execution inside hooks;
- change the native serializer payload or normalize native Math state;
- alter lookup/store ordering, pointer increments, A/B aliasing or native memory layout for instrumentation;
- add framebuffer readback in hooks merely to reconstruct values;
- introduce per-pixel file I/O or live mutable pointers in retained diagnostics;
- silently repair the output-bounds concern.

`paletteColor()` changes the CGRAM address latch, which participates in execution-visible behavior. Pure helpers such as the audited `directColor()` are not established mutation hazards, but their results should still be captured from native execution rather than redundantly derived.

Prefer already calculated operands, branch decisions, typed return values and values supplied to stores. Capture first lookup/store before second lookup/store exactly as native execution does.

## 11. Observer lifecycle and unknown-provenance rules

The observer must be disabled by default, use bounded owned storage, retain explicit dropped-record and overflow status, and export only after emulation execution has returned. Reset, power, load, rewind and other discontinuities must invalidate diagnostic history; they must not change native state or add diagnostic data to native save payloads. Save/Size operations must not invalidate diagnostics merely because serialization is inspected.

Use separate validity for numeric evidence, source lineage and control origin:

| Situation | Required treatment |
|---|---|
| Activation without observed predecessor or seed | UNKNOWN carried provenance/control origin; copied numeric Math values may still be known |
| Reset/power/load/rewind discontinuity | Invalidate/disarm diagnostic history and establish a new epoch; restored native Math does not restore lineage |
| Missing producer provenance or incomplete source lineage | Preserve known source category/color; required lineage remains UNKNOWN |
| Unsupported Mode 7 lineage | Do not fabricate tiled-BG lineage; retain observed color/source category separately |
| Missing carried-control origin or invalid/missing predecessor history | UNKNOWN for the missing dependency; do not infer from current registers, color equality or record adjacency |
| Observed native scanline initialization | `NativeScanlineSeed` with exact observed values; no invented previous winner |
| Hardware seed behavior | UNCONFIRMED independently of whether native seed values are known |
| No second operand or unused control | `None` / `NotApplicable`, not UNKNOWN |
| Primary clipped by native decision | Known clipped zero, with underlying source validity separately retained |
| Continuous observed mode transition | Preserve actual native producer history; invalidate only unsupported or missing dependencies |
| Skipped path | Explicit skip/zero result; preserve history where native Math persists |
| Overflow or absent retained link | Use owned known history if available; otherwise UNKNOWN; capture remains incomplete |
| Invalid destination or unestablished callback association | Preserve observed store value and report destination/association limitation explicitly |

Do not discard a known numeric native result merely because its semantic lineage is unknown. Seed markers and hardware uncertainty must not be erased to make a success flag pass. Distinguish export completion, coverage, lineage completeness and hardware confirmation.

## 12. Experimental checkout and staged progression

Registered experimental worktree:

```text
C:\Users\User\Documents\GTC-HD-Lab\experiments\bsnes-exp-004
```

Branch: `gtc-hd/exp-004-color-math-provenance`

Frozen baseline: `76bdb9250befa62fcbf23fcff2ef962fe2f58215`

This is an experimental checkout, not production GTC-HD source. Registration does not bypass the implementation gate or authorize source changes during a documentation task.

The required progression is:

1. **P0 COMPLETE:** Disposition **STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION**, as recorded in section 3.2.
2. **Separate prerequisite:** Complete the separately scoped native-baseline investigation and document its disposition, including the intended output/storage boundary, before reconsidering the EXP-004 gate.
3. **Only after explicit implementation re-authorization:** Define owned records/history and the narrow EXP-003 handoff.
4. Add passive hooks at native seed, selection, effective-decision, arithmetic-result and store-value boundaries; implement lifecycle handling.
5. Extend the existing callback-window infrastructure and focused native-method tests.
6. Complete the supported UCRT64 desktop build and deterministic runtime comparison.
7. Write curated results, with separate conclusions for the paths actually supported.

Do not modify upstream or other experiment worktrees. A baseline repair, if necessary, is a separate task rather than an instrumentation stage.

## 13. Focused host-test requirements

Except for the completed P0 evidence linked in section 3.2, these are planned tests, not completed evidence. EXP-004 implementation tests remain subject to the implementation gate. Use actual native methods where practical and retain the scope of synthetic surrounding state. Native math remains the runtime authority; independent calculations are test oracles only.

| Stage / test family | Required coverage |
|---|---|
| **Stage/Test 0 — P0 bounds (complete; STOP disposition)** | Completed scope and limitations are recorded in the report and matrix linked in section 3.2: frozen logical destinations, relevant V/overscan/interlace/field boundaries, skipped stores, A/B aliasing, pointer construction and overscan clear; declared-buffer validity and passive observation strategy |
| No math / clipping | Enabled/disabled source eligibility, allowed/clipped primary, no second operand, explicit skip reason, V=0 no write |
| Fixed-color arithmetic | Add, subtract, half add/subtract; zero/max channels, odd values, saturation and borrow boundaries; actual native operands and returned result captured |
| Sub-screen arithmetic | Add/subtract and halves; distinct main/sub provenance and actual operand values |
| Transparent-sub fallback | Priority-zero backdrop versus black nontransparent source; actual fixed fallback and half suppression; no false fallback claim when math is gated off |
| Source eligibility | BG1–BG4, backdrop, OBJ enable and palette restriction; final winner eligibility rather than losing-candidate eligibility |
| Color windows | Native primary permission, clipping, math allow/suppress, combinations with layer suppression; window boundaries, inversion and combination modes |
| Brightness / encoding | Actual native light table at 0, max and intermediate brightness; rounding and asymmetric channels; BGR555 → RGB555 conversion; no identity-table shortcut |
| Actual output | Both horizontal sample slots; valid A/B destinations, interlace aliasing/non-interlace duplication, logical destination validity, exact lookup/store order |
| True hires / pseudo-hires | Modes 5/6 and pseudo-hires; current sub primary, carried-main or fixed secondary, current above result and lowres duplicate distinction |
| Temporal producer history | Raw carried main rather than previous blended sample; previous active producer not equal to previous record; skipped positions, stale-but-unused controls and lowres-to-hires transition |
| Mixed-age controls | Register/control changes between native composition positions: current direction/fixed color versus carried enable/permission/choice/half; current above decisions; no artificial steps within native run |
| Scanline seed / missing history | Actual seed values and first native hires result, `NativeScanlineSeed`, hardware UNCONFIRMED, activation without seed/predecessor yielding UNKNOWN semantic origin |
| Lifecycle | Reset/power/load/rewind invalidation, clear/disarm/rearm, incomplete/Mode 7 lineage, missing control origin and copied ownership |
| Passivity | Frozen baseline versus new disabled/enabled native output and logical-state signatures; CGRAM latch, relevant memory-port effects, timing/read counts and Math state |
| Serialization | Native Size/Save layout/payload stability, actual load invalidation; no diagnostic payload; no uncontrolled cross-build coroutine-stack or RNG bytes treated as an equality oracle |
| Bounded capture / controller | Exact capacity, overflow/drops, history continuity independent of retention, callback boundaries, disarm/export timing, malformed options, collision/error/partial-run handling |
| Regressions / complete provenance chain | Reuse EXP-003 BG/OBJ/composition/window/hash/controller coverage; actual source fetch → winner → operand → result → valid native sample assertions |

Test arithmetic branch boundaries explicitly: native half-add must not be validated using an oracle that saturates the sum before halving. Test OBJ's literal palette threshold and valid nontransparent producer palettes.

Use actual native light-table construction or its extracted native initialization body. The EXP-003 fixture's identity table supports neither brightness nor output-encoding claims.

## 14. Runtime validation plan

Only after the separate native-baseline investigation and its documented disposition, explicit EXP-004 implementation re-authorization, and completed implementation/build/host validation, use the established deterministic Super Mario World environment first.

| Run | Required configuration |
|---|---|
| A — retained reference | Preserved EXP-003 1,800-callback sequence, where the baseline and configuration remain valid |
| B — EXP-004 disabled | EXP-004 binary, observer disabled, 1,800 framebuffer callbacks |
| C — EXP-004 enabled | **Exact same executable as B**, observer enabled for the initial semantic window at **callback 500**, 1,800 framebuffer callbacks |

Restore identical deterministic ROM, settings, SRAM and input conditions before each comparative process. Record their identities/hashes, the actual build/compiler and executable hash. If a separately authorized baseline repair invalidates A, reconsider/regenerate the reference before comparison.

Reuse zero-based callback-window semantics: arm before the ordinary run that produces callback 500, then disarm/export only after that run returns with completed-callback count 501. Require the expected one-callback-per-run sequence. No observer control/export occurs inside the framebuffer callback.

Use the cycle PPU and controlled cold-start conditions, with no run-ahead, rewind, fast-forward or interactive reset/load/input changes. Disable blur and controller overlays for direct store-to-callback comparisons. Keep callback interval, capture-relative frame and logical destination identities distinct.

Compare all ordered callback hashes and metadata, completion footers and process status:

```text
A == B == C     where retained A remains valid
B == C         mandatory
```

Matching framebuffer sequences supports passivity only for the tested output conditions; it does not establish universal CPU-visible state equivalence or hardware truth.

## 15. Runtime capture must contain meaningful color-math evidence

Keep callback 500 as the initial semantic observation window. Do not choose another callback in advance merely because its arithmetic coverage is UNKNOWN.

After capture, inspect actual operations, operands, clipping, brightness, source validity and hires history. A claimed color-math result requires actual arithmetic and at least one traceable contributing-source-to-native-result example. Useful coverage includes fixed, current-sub and carried-main operands, fallback, addition, subtraction, halving, clipping and brightness conversion.

Not every category must occur in one interval. If callback 500 lacks useful math evidence, record:

**VALID CAPTURE, INSUFFICIENT COVERAGE**

Then select another deterministic window. If the 1,800-callback no-input sequence is inadequate, use planned deterministic gameplay-state infrastructure rather than manual nondeterministic input.

## 16. Evidence summary requirements

Summaries must establish coverage and limits rather than maximize telemetry volume. Report:

- attempted and retained composition pairs, drops, overflow and bounded allocation size;
- emitted sample slots separately from unique arithmetic evaluations and duplicated above results;
- skip, no-math, clipped, fixed/current-sub/carried-main and effective fallback counts;
- addition, subtraction, effective halving and brightness distribution;
- true-hires/pseudo-hires coverage;
- current-source and carried-source validity, carried-control origin validity, seeds and unknown reasons;
- valid/invalid logical destinations and limits on callback association;
- callback interval, export completion and semantic completeness separately.

Expected seeds and hardware initialization uncertainty are not fabricated missing sources. A technically complete export with inadequate arithmetic coverage is not experimental verification.

## 17. Verification criteria

EXP-004 may eventually be marked **VERIFIED FOR TESTED CONDITIONS** only for explicitly scoped paths supported by implementation, focused tests and runtime evidence.

Required evidence includes:

1. P0 completion plus a completed separate native-baseline investigation, its documented disposition (including destination constraints and any baseline/reference implications), and explicit EXP-004 implementation re-authorization.
2. Focused native-method tests passed, including actual light-table behavior and the claimed temporal paths.
3. Supported UCRT64 desktop build succeeded with exact source/build/executable identity retained.
4. Disabled execution matched the valid deterministic reference, and B/C ordered native framebuffer sequences matched over all 1,800 callbacks.
5. Targeted real-ROM capture completed with no dropped records or overflow in the claimed interval.
6. Required source and control provenance was known, or an explicitly appropriate native-seed/constant origin was recorded, for the samples used to support each claim.
7. Actual arithmetic occurred, and at least one arithmetic result remained traceable to its contributing provenance.
8. Claimed framebuffer associations used established valid destinations and accounted for later refresh modifications.
9. Results distinguished source inspection, host-test evidence and real-ROM evidence, and retained hardware initialization as UNCONFIRMED absent separate evidence.

No source observation or existing EXP-003 test pass is, by itself, EXP-004 runtime verification. Real-ROM support for low resolution must not be generalized to unexercised hires paths.

## 18. Failure and partial-result conditions

| Condition | Required conclusion / response |
|---|---|
| B/C framebuffer mismatch | **PASSIVITY FAILURE**; stop architectural interpretation until explained |
| Native result observed but required source/control origin unavailable | **SEMANTIC-PRESERVATION LIMIT DISCOVERED**; retain numeric evidence and document the missing dependency |
| Lowres evidence sufficient, hires evidence incomplete | **LOW-RES SUPPORTED FOR TESTED CONDITIONS** and **HIRES INVESTIGATING**, reported separately |
| Completed capture lacks useful arithmetic | **VALID CAPTURE, INSUFFICIENT COVERAGE**; choose another deterministic window after review |
| Case only exercised in host tests | **IMPLEMENTED / HOST-TESTED, NOT REAL-ROM EXERCISED**, if and when those stages actually occur |
| P0 complete: **STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION** | EXP-004 implementation blocked until the separate native-baseline investigation is completed, its disposition is documented, and implementation is explicitly re-authorized |
| Invalid or unestablished output association | Restrict the claim and expose destination validity; never silently repair or remap native behavior |
| Unknown history or incomplete lineage | Explicit UNKNOWN for the missing semantic part, not inferred provenance or discarded known result |
| Hardware first-sample behavior unestablished | **UNCONFIRMED**; native-source/host evidence does not settle hardware behavior |

## 19. Non-goals

EXP-004 does not design a production renderer or semantic-frame format, select an emulator/graphics API/upscaler, implement lighting/HDR/shaders/asset replacement/AI enhancement, infer game-object identity or physical depth, solve Mode 7 lineage or widescreen, optimize record size prematurely, or establish universal compatibility.

It does not silently repair the native baseline or claim hardware truth from implementation comments.

Its scope remains preservation and validation of the semantic path from EXP-003 sources and relevant carried state through native color processing to native sample values and established output destinations.

## 20. Expected architectural value

If supported, the experiment would extend the tested provenance chain:

```text
BG / OBJ provenance
→ main/sub composition provenance
→ current and carried native operands / effective controls
→ native arithmetic result
→ brightness and encoding conversion
→ native sample value / validated destination
```

A future renderer could receive an explanation of which original source contributed, what native operation occurred, which controls were current or carried, and the exact native reference sample. It could then evaluate enhancements against native semantics rather than guessing backward from a flattened image.

This is expected research value, not a claim that an enhancement renderer or production interface exists.

## 21. Architectural status

Even a successful EXP-004 result does not automatically accept architecture:

| Topic | Status |
|---|---|
| Semantic-preservation architecture | **HYPOTHESIS** |
| bsnes foundation | **INVESTIGATING** |
| Production renderer interface | **UNDECIDED** |
| Semantic-frame format | **UNDECIDED** |
| Graphics API | **UNDECIDED** |
| Game-profile format | **UNDECIDED** |

Experimental evidence and accepted GTC-HD decisions remain separate.

## 22. Results-document expectation

A future `RESULTS.md` must explain what was learned, why it matters, what a renderer gains, what remains unknown and the implications for GTC-HD. It must not become a raw telemetry dump.

It should answer:

1. What native semantic problem and prerequisite were investigated?
2. What did source inspection establish, and what remained uncertain?
3. What did focused tests establish, including destination bounds and temporal/encoding behavior?
4. What did real-ROM execution actually exercise?
5. Was framebuffer passivity preserved for the claimed conditions?
6. Which source-to-result relationships survived, and what does that give a future renderer?
7. Which lineage, hires, destination, hardware or coverage limits remain?
8. What are the implications for GTC-HD, without accepting architecture?
9. What should be investigated next?

Raw captures remain local by default. Preserve curated evidence, reproducibility metadata, representative examples and architectural learning in the project documentation. The durable result is what GTC-HD learned about preserving native rendering meaning, not the volume of collected records.

