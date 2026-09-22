# EXP-004 — Color Math and Native Sample Provenance

Source audit and implementation plan, September 22, 2026.

**Recommendation — INFERENCE: revise EXP-004's diagnostic model, then proceed in stages.** Passive observation points exist in the inspected source, but current main/sub winners alone cannot explain hires samples. The model needs a carried-main operand, carried control provenance, explicit scanline seeds, and separate pre-brightness/native-output encodings. A source-discovered output-buffer bounds concern also needs a focused prerequisite check before claiming that every native store is a valid framebuffer sample.

This document is an audit and plan only. No EXP-004 implementation, new host test, build, ROM run, commit, ADR, specification change, or project-state update was performed. Existing test logs and retained runtime artifacts were inspected; their evidence is identified separately from source inspection. No emulator or production architecture is selected.

Evidence labels used throughout:

- **SOURCE OBSERVATION:** a fact read from the identified source, or an explicitly identified retained artifact. It is not a new execution result.
- **HOST-TEST EVIDENCE:** a result in retained EXP-003 host-test logs, constrained by the inspected fixture.
- **INFERENCE:** interpretation, proposed design, or a test/implementation recommendation.
- **UNKNOWN:** something this audit does not establish.

## 1. Starting state / commit / branch

**SOURCE OBSERVATION:** The research target was the clean worktree `C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004`, on branch `gtc-hd/exp-004-color-math-provenance`, at:

```text
76bdb9250befa62fcbf23fcff2ef962fe2f58215
Implement EXP-003 composition provenance observer
```

This exactly matches the requested starting commit. Its configured origin is `https://github.com/bsnes-emu/bsnes.git`. Findings refer to this experimental revision, including its EXP-003 instrumentation, not to arbitrary current bsnes versions.

**SOURCE OBSERVATION:** The GTC-HD documentation repository started clean on `main`, at `c4a4f67911af8d1f963e010cb1d0055d8ddcd62f`. The root `AGENTS.md`, `docs/PROJECT_STATE.md`, and `docs/experiments/EXP-004/SPEC.md` were read. No additional `AGENTS.md` was found within the EXP-004 worktree or documentation tree. Project state remains Phase 0; emulator selection and the interception boundary remain INVESTIGATING.

**SOURCE OBSERVATION:** A targeted comparison also confirmed that the framebuffer declaration and screen scanline/write code discussed in section 8 already exist at upstream baseline `7d5aa1e656b9171524d01b1b22917197d8121cb4`. This is an identity check of those fragments, not a separate full upstream audit.

## 2. Files inspected

Source links below refer to the EXP-004 worktree and the revision above. Line numbers are those at the audited revision. These identifiers are reused in the findings.

| ID | File / inspected responsibility |
|---|---|
| S1 | [screen.cpp][S1]: scanline initialization, run, below, above, blend, palette/direct/fixed color, power |
| S2 | [screen.hpp][S2]: Screen IO, Math, CGRAM, output pointers |
| S3 | [window.cpp][S3] and [window.hpp][S3H]: layer suppression, color outputs, masks, state |
| S4 | [io.cpp][S4]: memory access helpers, CGRAM ports, display/color/window registers |
| S5 | [serialization.cpp][S5]: PPU load reset and native window/screen serialization |
| S6 | [main.cpp][S6]: scanline/frame lifecycle, BG phases, render ordering, stepping |
| S7 | [ppu.cpp][S7] and [ppu.hpp][S7H]: light table, storage, power/reset, refresh |
| S8 | [exp003-composition.hpp][S8] and [exp003-composition.cpp][S8C]: records, lineage, resolution, bounds, export |
| S9 | [exp003-hooks.cpp][S9]: position/context and before/after-window snapshots |
| S10 | [background.cpp][S10]: fetch/plane/sample lineage, mosaic, true-hires phases |
| S11 | [object.cpp][S11]: OBJ sample/fetch lineage, palettes and output |
| S12 | [exp003-composition-window.hpp][S12]: callback controller and export lifecycle |
| S13 | [program.cpp][S13], [program.hpp][S13H], [bsnes.cpp][S13B]: controller integration, guards and CLI |
| S14 | [exp001-frame-hash.hpp][S14], [platform.cpp][S14P], [video.cpp][S14V]: callback hashing, presentation boundary, RGB interpretation |
| S15 | [composition-test.cpp][S15], [run-tests.py][S15R], [observer-window-test.cpp][S15W], [observer-window-cli-test.py][S15C]: existing fixtures and their limits |
| S16 | [system/serialization.cpp][S16], [system.cpp][S16S], [cpu/timing.cpp][S16T]: save/load and frame event boundary |
| S17 | [bsnes/GNUmakefile][S17], [nall/GNUmakefile][S17N]: supported build configuration |
| S18 | [random.hpp][S18], [counter.hpp][S18C], [counter-inline.hpp][S18I]: initialization entropy and scanline counter details |

**SOURCE OBSERVATION:** Supporting project material inspected included [EXP-003 results][D3], the EXP-001 results/runtime-harness notes, and the EXP-004 specification. Retained evidence inspected included EXP-003's `tests/exp003/build/validation-final/{composition,baseline,window,frame-hash,cli}-run.log`, the two 1,800-callback CSVs under `local/EXP-003/output`, the callback-500 summary and endpoint rows, and relevant deterministic seed settings. These were read only; ROM content was not executed.

## 3. Native color pipeline

**SOURCE OBSERVATION — S6:160–198:** BG below-phase execution occurs at H=56+4x, BG above-phase execution and `cycleRenderPixel()` at H=58+4x. `cycleRenderPixel()` executes:

```text
obj.run()
EXP-003 begin / pre-window candidates
window.run()
EXP-003 post-window candidates and color-window outputs
screen.run()
EXP-003 end
then cycle() calls step()
```

There is no native `step()` between window resolution, below, above, and the two output statements. Hooks must preserve that property.

**SOURCE OBSERVATION — S1:21–30:** `Screen::run()` returns without writes at V=0. Otherwise it computes `hires = pseudoHires || bgMode == 5 || bgMode == 6`, calls `below(hires)`, calls `above()`, then executes the first brightness lookup/write and the second brightness lookup/write. It does not call above before below.

**SOURCE OBSERVATION — S1:32–69,80–124:** Both selection paths first return zero for forced blank, or for `!ppu.io.overscan && V >= 225`. Those returns bypass selection and do not update `Screen::Math`. Otherwise:

1. Initialize local priority to zero.
2. Consider BG1, BG2, BG3, BG4, then OBJ. BG1 is accepted if nonzero; later candidates replace it only for strictly greater priority. Earlier candidates survive equal-rank ties.
3. Resolve color immediately on each native replacement, not just once after the final winner. BG1 uses direct color only when `screen.io.directColor` and mode 3, 4, or 7; other selected cases call `paletteColor()`.
4. Below marks `math.transparent = (priority == 0)` and resolves CGRAM entry zero for that backdrop case. Above also resolves entry zero if no candidate wins.
5. Existing EXP-003 `resolved()` calls copy each final selected pre-math color. Above also copies selected-source eligibility before color-window gating.

**SOURCE OBSERVATION — S1:71–77:** Below always performs active sub selection, even in low resolution. Low resolution then returns zero, which `run()` does not emit. Hires below uses *carried* Math controls and the current sub color; section 5 gives the exact dependency.

**SOURCE OBSERVATION — S1:126–141:** Above gates the selected source's eligibility with the current below color-window output, copies the current above color-window output as the primary-color permission, and either returns a clipped/unclipped main color or resolves blend/half state and calls native `blend()`.

**SOURCE OBSERVATION — S1:28–29:** Low resolution emits the current above result twice horizontally. Hires/pseudo-hires emit below result first and above result second. Both go through the native light table. The `lineA`/`lineB` stores supply vertical duplication or interlace placement; they do not represent four independent color calculations.

**INFERENCE:** Observe this sequence at its existing boundaries. A post-frame interpretation of current winners and register snapshots is insufficient because it loses both branch choices and temporal state.

## 4. Screen::Math lifetime/state analysis

**SOURCE OBSERVATION — S2:36–44; S1; S5:275–281:** Every member of `Screen::Math` is persistent native state and is explicitly serialized. None is an observer-only cache. Their semantic lifetimes differ:

| Native member | Updates and use within one composition point | Persistence / temporal significance |
|---|---|---|
| `math.above.color` | Above replaces it with the current selected **raw** main color before clipping/math. Below reads the old value when carried blend mode selects it. | Carries the last active main selection, not the previous arithmetic result. Skipped above calls leave it unchanged. |
| `math.above.colorEnable` | Above sets it from current `window.output.above.colorEnable`. Both paths use it to allow or zero their primary operand. | Below sees the permission from the last active above call. |
| `math.below.color` | Below overwrites it with the current selected sub/backdrop color. Above may consume that same value. | Persists physically, but a normal active below refreshes it before use. Skip leaves it stale, and both paths return zero. |
| `math.below.colorEnable` | Above first assigns selected-main-source eligibility, then may clear it using current below color-window output. | Below consumes the previous active above's **effective math-enable** decision. It is not sub-source eligibility. |
| `math.transparent` | Below sets it from final sub priority zero. Above uses it for requested-sub fallback. | Current-point dependency below→above; stored across points/skips but refreshed by each active below. Below does not use it to resolve its own carried blend/half controls. |
| `math.blendMode` | Above sets it only if math remains enabled; transparent requested-sub fallback sets false, otherwise copies `io.blendMode`. | Below sees carried effective operand selection. Above's no-math early return leaves this member stale. |
| `math.colorHalve` | Above sets it only if math remains enabled; fallback sets false, otherwise `io.colorHalve && math.above.colorEnable`. | Below sees carried effective half control. Above's no-math return leaves it stale. |

**SOURCE OBSERVATION:** Local `priority`, the `hires` variable in `run()`, `belowColor`/`aboveColor`, `blend()` arguments, and arithmetic intermediates are transient. They are not in `Screen::Math` and are not serialized as Screen fields. Screen IO controls persist independently and are serialized at S5:259–273. `lineA`/`lineB` and `lightTable` are not fields of the explicit Screen serializer.

**SOURCE OBSERVATION:** At above's no-math return, `math.above.color`, its permission, and effective math enable have been refreshed, while blend mode and half may describe an older arithmetic point. However, effective math enable is then false, so the following active below does not consume those stale blend/half values. Forced-blank/non-overscan skipped calls preserve the entire Math state and can extend a dependency past the immediately previous composition record.

**INFERENCE:** History should mean “last observed native state producer,” not blindly “record ID minus one.” Preserve separate validity for copied native values, the origin of carried gates, and source lineage. Record which native path ran rather than treating all physically stored fields as effective controls for every sample.

## 5. Hires/pseudo-hires temporal analysis

**SOURCE OBSERVATION — S1:65–77:** Let `Sx` be the current selected raw sub color, and let the carried state entering below be:

```text
P = math.above.color             (last active main's raw color)
allow = math.above.colorEnable   (carried primary-color permission)
enable = math.below.colorEnable  (carried effective math enable)
useMain = math.blendMode         (carried effective blend selection)
half = math.colorHalve           (carried effective half control)
```

The active hires below path has these exact meanings:

| Branch | Primary operand / result | Second operand / operation |
|---|---|---|
| `!enable` | Return `allow ? Sx : 0` | No second operand; no `blend()` call |
| `enable && useMain` | `allow ? Sx : 0` | `P`, with **current** `io.colorMode` and carried `half` |
| `enable && !useMain` | `allow ? Sx : 0` | **Current** `fixedColor()`, with **current** `io.colorMode` and carried `half` |

**SOURCE OBSERVATION:** Below does not consult current color-window outputs, current source eligibility bits, current `io.blendMode`, or current `io.colorHalve` to choose those carried controls. It does consult current color-resolution controls while selecting its sub source. Its newly calculated `math.transparent` influences the later above call, not the below sample's own operand/half selection.

**INFERENCE:** The previous main is the second operand in the carried-sub-blend case. This requires an explicit `CarriedMain` operand kind. Calling it the “current sub second operand” is wrong. Its source is a raw selected main color, not a previous final sample, so no recursive chain of earlier blended colors is required. A bounded copied history entry is sufficient for this part of the source model.

**SOURCE OBSERVATION — S10:3–5,187–240:** True hires is BG mode 5/6. BG execution consumes separate samples in the below/above phases. Pseudo-hires changes Screen emission but does not make `Background::hires()` true: the non-hires BG above phase can populate both screens from one BG sample. Main/sub winners can still differ because enabling, priorities, OBJ, and windows differ.

**SOURCE OBSERVATION:** Mode changes do not themselves reset Math in this path. A low-resolution above can seed the next hires below. A register change between composition positions can give below an old eligibility/window/half/operand-choice decision but a new add/subtract direction or fixed color. Within one normal `run()` there is no timing step allowing CPU register changes between its two writes.

**SOURCE OBSERVATION — S1:1–19:** Each `Screen::scanline()` sets both colors from one native `paletteColor(0)` call; sets both enable fields false; sets transparent true and blend mode false; and sets half using `io.colorHalve && !io.blendMode && math.above.colorEnable`, which is false after the preceding assignment. The comments say “the first hires pixel of each scanline is transparent” and explicitly say exact initializations are not confirmed on hardware.

**SOURCE OBSERVATION:** In uninterrupted native execution after that seed, the first active hires below returns zero: carried math enable and primary permission are both false. It can select a nonzero current sub color before returning zero. The result is therefore not evidence that the current sub was transparent or that CGRAM zero was black. `Screen::power()` initializes CGRAM and IO but does not explicitly seed Math; the scanline method is the explicit recurring initialization point. PPU power calls the observer reset and native screen power; load restores serialized Math independently.

**UNKNOWN:** The exact SNES hardware first-sample behavior and initialization values are not established here. Existing comments are implementation notes, not hardware measurements.

**INFERENCE:** Represent an observed seed as `NativeScanlineSeed` with exact copied values, no invented previous winner, and `hardware_initialization=UNCONFIRMED`. If activation missed the seed or preceding active above, carried provenance is UNKNOWN. Native numeric results can still be known. An observed continuous mode transition need not invalidate a known carried source; a transition with missing/unsupported producer history must not manufacture one.

## 6. Color-window and eligibility findings

**SOURCE OBSERVATION — S3:5–38:** Layer windows and color windows share window geometry but perform different work. Layer windows call `test()` for each BG/OBJ and may zero above/below candidate priorities before composition. Color windows call `test()` for `io.col`, then select:

```text
array = {true, value, !value, false}
window.output.above.colorEnable = array[col.aboveMask]
window.output.below.colorEnable = array[col.belowMask]
```

The geometry tests use inclusive left/right bounds, inversions, and OR/AND/XOR/XNOR selection. `Window::run()` increments its x counter and mutates candidate priorities as well as outputs; the helper `test()` alone is a pure boolean expression in this implementation.

**SOURCE OBSERVATION — S4:517–565,610–627:** `$2125` configures color-window enables/inversions, `$212B` its combination operator, and `$2130` supplies above/below masks. `$2131` supplies source math-enable bits, halve, and add/subtract. Above color-window output controls clipping to zero; below color-window output gates math. It does not directly choose or suppress the current sub winner.

**SOURCE OBSERVATION — S1:84–124:** The selected main winner sets pre-window eligibility as follows:

| Main source | Native eligibility assignment |
|---|---|
| BG1 | `screen.io.bg1.colorEnable` |
| BG2 | `screen.io.bg2.colorEnable` |
| BG3 | `screen.io.bg3.colorEnable` |
| BG4 | `screen.io.bg4.colorEnable` |
| OBJ | `screen.io.obj.colorEnable && obj.output.above.palette >= 192` |
| Backdrop | `screen.io.back.colorEnable` |

**SOURCE OBSERVATION — S11:82–91,148:** OBJ fetched palette base is `128 + (sprite.palette << 4)`, and the nontransparent sample adds its color index. The restriction is applied at **main selection in `Screen::above()`**, not during OBJ overlap selection or palette lookup. In ordinary native OBJ production it excludes OAM palette groups 0–3 and allows 4–7 when the OBJ enable bit is set. Tests should distinguish the literal threshold 191/192 from valid nontransparent producer values 191/193; index 192 corresponds to the group's transparent index in normal production.

**SOURCE OBSERVATION:** There is no analogous source-specific eligibility test on the current sub selection. In hires below, eligibility is inherited from the previous active main path, even if the current sub is OBJ from a palette that would be ineligible as a main source.

**INFERENCE:** Reuse EXP-003's `mainMathEligible` at S1:124 and `colorWindowMain/Sub` captured by `exp003AfterWindow()`. Add the actual effective decision after S1:126–127 and capture carried decisions before below changes anything relevant. No runtime rerun of window logic is needed. Rename/export explanatory labels such as `current_primary_color_allowed` and `current_math_window_allowed` to avoid interpreting the old field names as current main/sub winner visibility.

## 7. Fixed/sub operand findings

**SOURCE OBSERVATION — S1:128–141:** Above has three meaningful cases:

| Effective execution | Second operand | Half behavior |
|---|---|---|
| Math gated off | None; no blend call | Not applicable; stored half may be stale |
| Math enabled, `io.blendMode == 0` | Current fixed color | `io.colorHalve && primary_allowed` |
| Math enabled, requested sub and `!math.transparent` | Current resolved raw sub color | `io.colorHalve && primary_allowed` |
| Math enabled, requested sub and `math.transparent` | Current fixed color; fallback reason is sub priority zero | Forced false, even if halve was requested |

**SOURCE OBSERVATION:** “Transparent sub” means the native final sub priority is zero. It does not mean the resolved color numerically equals zero. A nontransparent source producing black remains a source operand; a backdrop can have a nonzero CGRAM color and still cause fixed fallback in above. Below's backdrop color remains the primary operand in hires if its carried permission allows it.

**SOURCE OBSERVATION:** `fixedColor()` packs `colorBlue << 10 | colorGreen << 5 | colorRed`; `$2132` selectively updates channels. No source fetch lineage is implied for fixed color. It is an explicit register-derived operand.

**INFERENCE:** Preserve configuration only to explain discrepancies: requested fixed/sub, requested half, current add/subtract, and the native fallback decision. The authoritative operand record must come from the actual branch and actual `blend()` arguments. The full operand-kind set needs `None`, `CurrentSub`, `FixedColor`, and `CarriedMain`, with a separate primary-source reference and clipping flag. Record fallback at the point above actually applies it; it is not an effective fallback merely because the register requests sub while the sub winner is backdrop and math is disabled.

## 8. Arithmetic and brightness findings

**SOURCE OBSERVATION — S1:144–162:** `blend(uint x, uint y) const -> uint15` receives both effective operands simultaneously. `io.colorMode` selects addition/subtraction; `math.colorHalve` selects the half branch. The exact return expressions are:

| Native branch | Native calculation |
|---|---|
| Add | `sum=x+y; carry=(sum-((x^y)&0x0421))&0x8420; return (sum-carry)|(carry-(carry>>5));` |
| Add + half | `return (x+y-((x^y)&0x0421))>>1;` |
| Subtract | `diff=x-y+0x8420; borrow=(diff-((x^y)&0x8420))&0x8420; return (diff-borrow)&(borrow-(borrow>>5));` |
| Subtract + half | Same diff/borrow, then `(((diff-borrow)&(borrow-(borrow>>5)))&0x7bde)>>1` |
| No math | No call to `blend()`; below/above returns its allowed source or zero |

**INFERENCE:** Addition saturates channels in the unhalved branch. Half-add computes the channel average without first saturating the sum; it is not “saturate addition, then divide by two.” Subtraction clamps underflow and its half branch truncates after clamping. Saturation, rounding, clipping, and brightness are many-to-one; inversion cannot recover operands or identity. Test oracles may use independent per-channel arithmetic. Runtime observation must copy the native arguments, selected branch, and typed returned result without a second calculation.

**INFERENCE:** The strongest arithmetic hook is inside each existing return branch of `blend()`, assigning the native expression once to a `uint15` local, reporting that local with x/y and the chosen operation, then returning it. An enabled diagnostic context identifies below/above; the native signature can stay unchanged. Preserve the existing no-math return branches separately. A hook only after `run()` cannot recover below's consumed carried state after above overwrites it.

**SOURCE OBSERVATION — S7:26–38; S1:28–29; S14V:73–76:** The light table is initialized for 16 levels and 32 values per component, with `luma = level / 15.0` and component conversion `uint(luma * component + 0.5)`. The actual lookup **also reverses the high and low five-bit component placement**. Screen input is BGR555 (red low); the emitted framebuffer value is RGB555 (red high), as also consumed by the frontend palette builder. At maximum brightness, `0x001f` maps to `0x7c00`, not `0x001f`. A schema must name both encodings explicitly.

**SOURCE OBSERVATION:** `belowColor`/`aboveColor` are pre-brightness native returns; the actual table element is the native 16-bit storage value. Brightness comes from current `ppu.io.displayBrightness` (`$2100` low four bits). Keep the two lookups/stores in original sequence; do not precompute the second lookup before the first native store.

**SOURCE OBSERVATION — S1:1–6:** Put `pairY = V + (display.overscan ? 0 : 7)`. Base offsets are `pairY*1024`, with `lineB` another 512 samples below when non-interlaced. With interlace, A/B alias the same row, and field 1 adds 512. Horizontal samples at composition x occupy offsets `2*x` and `2*x+1`. Each statement stores through B then A under the chained assignment; non-interlace writes two rows, interlace writes the same location twice. `display.overscan/interlace` are frame-latched placement controls; screen suppression uses live `io.overscan`.

**SOURCE OBSERVATION — bounds concern, S7H:59–60; S6:21–32; S1:1–6,21–33:** `output` is declared as `uint16 output[512 * 480]`, or 245,760 samples. Rendering cycles run through V=240 inclusive; only V>240 bypasses them. In non-overscan placement, V=233 yields `pairY=240`, whose first offset is 245,760, already outside the declared array. V=233–240 therefore request stores beyond that array; with overscan placement, V=240 begins outside it. The early returns in below/above return zero but do not suppress `run()`'s stores. `screen.scanline()` also constructs line pointers before the V>240 skip. The overscan-area clear loop at S6:6–9 includes pair index 240 too.

**INFERENCE:** This is an inherited native bounds/undefined-behavior concern. `lightTable` is declared immediately after `output`, but this audit does not assume a particular overwrite effect or prove compiler/runtime behavior. Instrumentation that changes PPU layout or adds readback through these pointers could change or compound that risk. Record integer logical destination offsets and whether they fall within the callback buffer; do not silently label every native store a valid callback pixel. Capture the value supplied to the native store rather than adding a framebuffer readback in rendering hooks.

**UNKNOWN:** Actual memory effects, any undocumented reliance on layout, and compiler sensitivity of this bounds issue have not been tested. A focused bounds check belongs before strong output-placement claims. It must not silently fix native code as part of EXP-004; any corrective baseline change requires a separately scoped task and new deterministic reference.

**SOURCE OBSERVATION — S7:192–215; S14P:205–238:** `PPU::refresh()` can blur the native buffer in place and let a controller draw an overlay before `platform->videoFrame()`. Hashing occurs at the start of `Program::videoFrame()`, before frontend cropping/filtering, but after those PPU refresh modifications. The EXP-004 store sample and callback sample coincide only where no later mutation occurred and the destination belongs to the callback buffer. Disable blur/controller overlays in controlled runs and state this boundary explicitly.

## 9. EXP-003 reuse assessment

**SOURCE OBSERVATION — S8/S8C/S9:** Existing machinery already carries the following and should be reused:

| Needed information | Existing implementation | EXP-004 interpretation / gap |
|---|---|---|
| Current main/sub identity | `Record::winner[0/1]`, native `select()` branches | Selection truth; not necessarily an emitted operand |
| BG provenance | `bgFetch/bgPlane/bgSample/bgHold/bgOutput`, copied `Lineage` | Retains tiled fetch and mosaic lifetimes; incomplete or Mode 7 lineage remains unknown |
| OBJ provenance | `objFetch/objPlane/objSample`, bank invalidation | Retains fetched object lineage after native overlap |
| Selected raw colors | `resolved(1/0)` into `Winner::color` | Already computed BGR555, before clipping/math/brightness |
| Source eligibility | `mainMathEligible` at above resolution | Pre-color-window only; current main, not carried below eligibility |
| Effective color windows | `windows()` after native `Window::run()` | Current values; below uses carried values instead |
| Position and modes | `begin()` via `exp003BeginComposition()` | x before window increment, V/H/field, bgMode and combined hires; add explicit pseudo-hires and placement controls |
| Callback capture/export | `Exp003CompositionWindow` plus `Exp001FrameHash` | Reuse sequencing, guards, exclusive paths, bounded capture, after-run export |

**SOURCE OBSERVATION:** EXP-003's `current_` is private; no public pending-record snapshot exists. `end()` assigns record ID and appends only after `screen.run()`. `copyRecord()` accesses retained records, so using “last retained record” inside Screen is incorrect and fails under overflow. `clear()` resets tokens and invalidates producer history; re-enabling also invalidates source caches. `reset()` disables capture. Unknown-winner counts count retained selected BG/OBJ winners; backdrop/skipped are separate categories.

**INFERENCE:** Add a narrow copied-value pending-winner/record handoff, or pass the existing resolved winner by value to the EXP-004 consumer. Reuse the same producer sidecars and native branch tags. Do not duplicate BG/OBJ tracking or infer lineage from colors. Commit an EXP-004 composition record after its two sample results are available; assign a diagnostic sequence independently of retained-array index.

**INFERENCE:** Initially allow the existing bounded EXP-003 buffer to remain for regression evidence, with EXP-004 using its shared live producer data. Avoid a broad observer-framework rewrite in this experiment. Ensure one controller owns enabling/clearing both layers and rejects conflicting simultaneous EXP-003/EXP-004 capture requests. Any later removal of redundant retained composition storage can be measured separately.

**HOST-TEST EVIDENCE — retained logs, not rerun:** EXP-003 `validation-final` reports passing native composition, producer-lineage, window, callback-controller, hash, and 26 CLI rejection tests. Baseline/instrumented signatures match:

```text
native_composition_signature=f8952120fe226387b07fc3c6f8d1e3c931e0b44a145cc7c37b436e03810dc2f1
native_pipeline_signature=03df6a8c62befa48a4edb6f39dbe72d8c730338aedd10e80469482e698e4fe5b
```

**SOURCE OBSERVATION — S15:72–85,113–130,259–272:** The fixture uses actual native methods in a synthetic PPU and compares output, serialized component state, CGRAM/OAM latches, clocks, and VRAM-read counts. It exercises hires sequencing but sets `lightTable[level][color] = color` for every level. Its arithmetic controls in passivity fixtures do not establish explicit operand/result correctness for EXP-004. Load/power hook presence is checked by the runner; that is not a whole-core load/rewind test.

**INFERENCE:** Reuse these tests as regressions, but add actual light-table initialization and explicit math/temporal assertions. Existing test passes cannot be relabeled as EXP-004 verification.

## 10. Passivity hazards

| Operation | Evidence classification and consequence | Required observer discipline — INFERENCE |
|---|---|---|
| `paletteColor()` | **SOURCE OBSERVATION:** assigns `ppu.latch.cgramAddress`; `readCGRAM/writeCGRAM` redirect accesses through this latch during the active H/V range (S1:164–167; S4:56–69). Even losing native candidates can cause palette lookups. | Never add, remove, defer, or reorder a lookup. Copy existing resolved color. |
| `directColor()` | **SOURCE OBSERVATION:** pure bit packing; no mutation seen (S1:169–175). | Repeating it is not an established side-effect hazard, but duplicates truth and can use wrong-phase controls. Capture the original result. |
| `fixedColor()` | **SOURCE OBSERVATION:** pure IO packing (S1:178–180). | Capture actual argument; do not independently reconstruct an effective operand from later registers. |
| Window processing | **SOURCE OBSERVATION:** `run()` increments x, zeroes priorities, writes color outputs; `test()` alone has no mutation (S3). | Never rerun `run()`. Avoid duplicate `test()` logic as runtime authority; copy outputs. |
| PPU memory reads | **SOURCE OBSERVATION:** raw VRAM indexing returns a masked reference; memory helpers apply access restrictions/redirects; IO reads synchronize and may advance address/latch/MDR state (S4; S7H:53–57). Not every raw read is intrinsically stateful. | Do not reread VRAM/OAM/CGRAM for lineage. It may describe a later memory version; never query via IO for observation. |
| Timing/scheduling | **SOURCE OBSERVATION:** `step()` advances counters/clock and can resume CPU (S7:44–60); IO synchronizes (S4:72,200). | No added step, synchronization, emulation run, memory port access, or callback in a hook. |
| Native Math | **SOURCE OBSERVATION:** below/above mutate persistent state, including conditional writes and skipped paths (sections 4–5). | Never call either twice or “normalize” stale state; diagnostic history is separate. |
| Serializer | **SOURCE OBSERVATION:** all Math fields are serialized; System serialization may run to a save boundary, and unsynchronized saves include coroutine stacks (S5/S16). | No new payload fields, no per-pixel saves; reset diagnostics on load only, not save/size. Do not use raw cross-build stack bytes as a deterministic oracle. |
| Output ordering / layout | **SOURCE OBSERVATION:** two sequential lookup/store statements; A/B may alias; declared-array bounds concern (section 8). | Preserve both statements' order, lookup count and pointer increments; no speculative second lookup, no extra output readback, no PPU layout changes for diagnostics. |
| Diagnostic allocation/export | **INFERENCE:** unbounded allocation, I/O, exceptions or retained live references can disrupt host execution or make copied evidence stale. | Preallocated bounded owned values; no hook I/O; explicit overflow; export after return. |
| Host-time interaction | **INFERENCE:** instrumentation costs can interact with live input/presentation even without emulated timing changes. | Deterministic neutral/scripted input and unchanged controls/settings; measure host overhead separately from passivity. |

**SOURCE OBSERVATION — S18:** Entropy=None produces deterministic initialization values but the RNG seed can still originate from `clock()` and its state is serialized. **INFERENCE:** Logical-state equality tests need controlled RNG state and appropriate synchronized payloads; framebuffer equality is not universal CPU-visible equivalence.

## 11. Proposed hook points

All hooks below are **INFERENCE — proposed**, not implemented. Source line anchors describe current code, not a patch.

| Hook / location | Information available and native state read | Information already lost / duplication | Lifecycle and hires implications |
|---|---|---|---|
| After `Screen::scanline()` initialization, S1:18 | Copied Math seed, V/field and latched placement controls; already resolved seed color | No real predecessor source exists. No extra palette lookup. | Start a diagnostic scanline-seed origin; only claim seed observed when capture was active. |
| Existing begin/after-window boundary, S6:183–185; S9 | Existing context, candidates, current effective window outputs | Earlier fetch identities only through EXP-003. No window replay. | Start pending composition and snapshot carried Math before below mutates it. |
| After below `resolved()`, S1:65–69 | Current sub winner/color and native `transparent` | Prior Math still available, but superseded earlier selection candidates' colors need not be recovered. No extra selection/lookup. | Hand off copied sub provenance before any hires blend. |
| Below's native return branches, S1:33,71–77 | Skipped, low-res-not-emitted, passthrough/clipped, or blend path; carried gates/choice | Current main is not selected yet. Use actual branch tags, not current-main assumptions. | Distinguish not-emitted below from a genuinely emitted zero sample; skipped path must not refresh history. |
| Existing above resolution, S1:124 | Current main Winner and selected-source eligibility | Still before color-window/math; no result yet. | Copy actual current main for the next carried history generation. |
| Above post-window/operand branches, S1:126–141 | Effective gate, clip permission, requested controls, actual fallback, effective blend/half | A final-only hook would lose the pre-window eligibility and fallback cause. No replay. | Update diagnostic history at the same native writes, even when no math occurs; preserve old blend/half origin when native leaves them stale. |
| Each native `blend()` return, S1:144–162 | Actual x/y, current direction, consumed half, native typed result | Source identity only through pending context; no source reads inside blend. | Tag below/above call; captures carried-main arithmetic without recomputation. |
| Each native lookup/store in `run()`, S1:28–29 | Pre-brightness return, brightness used, actual table value supplied to stores, sample slot | Blend temporaries and previous source would be lost without preceding hooks. No second lookup/readback. | Preserve first lookup→stores→second lookup→stores; pair sample results with logical integer destination offsets and in-buffer validity. |
| End after screen, S6:187 | Both sample results plus EXP-003 pending composition | Lost history must remain unknown. No native action duplicated. | Append owned record; advance history even if retention overflows. |
| PPU power/reset/load, S7:79; S5:2 | Discontinuity notification | Serialized native values do not serialize provenance. | Clear/disarm both observers and invalidate history; Save/Size unchanged. |

**INFERENCE:** Keep hooks out of the templated per-cycle body; use existing non-template render functions. An observer-enabled context can identify a `blend()` call without changing the native Screen layout or introducing live native pointers into retained data.

## 12. Proposed diagnostic representation

**INFERENCE:** Prefer **one record per composition position with two emitted-sample results**, the reused current main/sub winners, and one owned carried-state descriptor. This fits the existing capture unit, preserves the below-before-above relationship, and avoids doubling current-winner storage. It is not an accepted production frame format.

| Record part | Minimum semantic content |
|---|---|
| Identity/context | Diagnostic epoch and attempted composition sequence; callback-window identity; capture-relative frame, x/V/H/field; bgMode, explicit pseudo-hires and effective hires; live blank/overscan and latched placement/interlace; skip reason |
| Current composition | Owned reused EXP-003 main/sub Winner values; source color BGR555; current pre-window eligibility and effective color-window booleans. Candidate diagnostics may remain in the existing EXP-003 companion record. |
| Carried state | Copy of the seven pre-below Math members; predecessor kind/epoch/sequence/coordinates; owned carried-main Winner when known; origin of carried eligibility/window controls; last effective blend/half resolution and fallback reason when relevant |
| Sample 0 / sample 1 | Emission path (`Above`, `Below`, `AboveDuplicate`, `SkippedZero`); native branch/reason; primary source reference and raw color; effective x after clipping; second-operand kind/reference/value or None; effective operation/half; actual pre-brightness BGR555 return; brightness and actual RGB555 store value; integer A/B destination offsets and whether each is within the declared callback buffer |
| Validity | Native values observed separately from source-lineage-known, control-history-known, seed observed, hardware initialization unconfirmed, missing producer/history reason |

**INFERENCE:** Source references within a record can index `CurrentMain`, `CurrentSub`, or the owned `CarriedMain` snapshot. Fixed color and clipped zero are explicit constants with causes, not fabricated BG/OBJ sources. A source clipped to zero can retain its selected identity while being marked as contributing no color value. A no-math sample has no second operand even if unused Math fields still hold old colors/controls.

**INFERENCE:** Do not require pointer links into another record. Pure linked records save bytes but fail at activation, clear, overflow, and skipped-record gaps unless separately guarded. A copied history descriptor provides bounded, self-contained evidence; optional predecessor IDs help inspection without being required for interpretation. Keep histories by native update, not retention success. Low-resolution sample 0 can alias sample 1's arithmetic description diagnostically while recording both actual native stores.

**INFERENCE:** A per-emitted-sample stream is also viable, but duplicates context and complicates atomic retention of a pair. The composition-pair form is the smaller conceptual extension of EXP-003. Size it after correctness tests, publish `sizeof(record)` and total allocation, and retain a fixed prefix with saturating drop count and explicit overflow. Capacity 65,536 composition records is a reasonable initial target for a one-callback window, not a promise for arbitrary captures.

## 13. Unknown-provenance rules

These rules are **INFERENCE — proposed**. UNKNOWN concerns the missing semantic part; it must not discard a genuinely observed numeric result or label a known constant as an unknown source.

| Situation | Required representation |
|---|---|
| Activation without observed seed/predecessor | Native Math values can be copied; carried origin/control provenance UNKNOWN. Do not match them to a current winner by color. |
| Reset/power/load/rewind | New diagnostic epoch, invalid caches/history, disarmed capture. Restored serialized Math is native numeric state, not restored lineage. |
| First hires sample after an observed scanline seed | `NativeScanlineSeed`; actual native result/gates known; no predecessor Winner; hardware seed semantics UNCONFIRMED. Missing seed remains UNKNOWN. |
| Missing/partial BG or OBJ producer lineage | Preserve observed source category/color but lineage UNKNOWN, following existing EXP-003 validity. |
| Mode 7 or unsupported source path | Source/color may be known; tiled lineage UNKNOWN. Do not recast it as a known tiled BG fetch. |
| Mode/control transition with continuous observation | Preserve the actual carried origin, including a low-res predecessor. A transition alone is not proof of lost history. Mark UNKNOWN only where producer/control tracking cannot establish continuity. |
| Forced blank / non-overscan skip | Known zero return with explicit skipped reason; no invented current winner. Preserve diagnostic history exactly as native Math persists. If history was already unknown it stays unknown. |
| Missing retained predecessor due to overflow | Owned copied history may still be known; a bare missing link must be UNKNOWN. Mark capture incomplete regardless. |
| Clear/disarm/rearm or counter discontinuity | Invalidate lineage/history and use a new epoch. Never reuse token IDs as cross-epoch identity. |
| Unused operand/state | `None` / `NotApplicable`, not UNKNOWN. A clipped primary is known zero with a known or unknown underlying source recorded separately. |
| Store outside declared framebuffer / refresh mutation | Store value can be observed, but do not claim a corresponding unmodified callback pixel. Explicit destination-invalid or later-stage limitation. |

**INFERENCE:** Split summary counts for unknown current winners, unknown carried source, unknown carried gate origin, scanline seeds, unsupported sources, and invalid output destinations. Distinguish capture completion from semantic coverage. Expected seed markers do not make a technically completed capture a failed export, and hardware uncertainty must never be erased to make a success flag pass.

## 14. Focused test plan

All tests in this section are **INFERENCE — planned, not run**. Use actual checked-out `Screen`, `Window`, BG/OBJ, register, and serializer code where practical. Reuse EXP-003's bounded synthetic host approach, but do not substitute an identity light table. Extract the actual PPU light-table initialization body or run the real constructor in a suitable fixture. An independent oracle belongs only in tests.

| Order / test family | Concrete cases and required assertions |
|---|---|
| 0. Native destination bounds | Evaluate the actual scanline/run path for V=0,1,224,225,232,233,239,240,241, with latched overscan/interlace/field variants. Establish logical indices before dereferencing out-of-range destinations. Use a separately controlled instrumented fixture/sanitizer or guarded storage for any store experiment. Check the overscan clear loop too; retain source/native-layout evidence. No silent baseline repair. |
| 1. No math / clipping / skip | Distinct nonzero main/sub colors; all six main source classes; source enable off/on and both color-window gates. Assert original main vs clipped zero, no blend invocation, second operand None, forced-blank and live overscan skip reasons. V=0 creates no sample/record. |
| 2. Native arithmetic | Actual `blend()` plus normal above path: fixed add/subtract, fixed half-add/half-subtract, sub add/subtract and halves. Per-channel inputs 0,1,15,16,30,31; equal, carry/borrow, odd sum/difference, asymmetric channels. Explicitly distinguish half-add-before-saturation: 31+31 with half gives 31, not 15. Compare actual native returned value and observer result to a per-channel oracle. |
| 3. Operand choice | Requested fixed, requested sub with a nontransparent winner, black nontransparent sub, colored backdrop, transparent-sub fallback with requested half, and gating off before fallback. Assert native `transparent`, actual operand kind/value and effective half; no fixed operand claim on a no-math branch. |
| 4. Eligibility | BG1–BG4 independently enabled/disabled; backdrop enabled/disabled; OBJ enable false/true with literal palette threshold 191/192 and actual nontransparent palette groups below/above the boundary (191/193). Confirm eligibility is set by final main winner after priority competition, not a losing candidate or current sub. |
| 5. Window interaction | Drive real `Window::run()` across left/right inclusive edges, inversions, OR/AND/XOR/XNOR, and all four above/below color masks. Combine layer suppression with independent color clipping/math gating. Assert selection survives color clipping, and copied native output booleans match the controls actually consumed. |
| 6. Brightness / encoding / stores | Levels 0,15 and an intermediate such as 7; asymmetric channel colors and rounding boundaries. Assert BGR555→RGB555 conversion, including red `0x001f`→`0x7c00` at 15. Compare captured store values to actual writes in valid destinations, two horizontal samples, duplicated non-interlace rows and aliased interlace stores. Preserve first lookup/store before second. |
| 7. True hires and pseudo-hires | Modes 5 and 6 and pseudo-hires in a low-res BG mode; distinct native BG phase samples and distinct main/sub Winners. Assert sample 0 uses current sub as primary and carried main or current fixed color as secondary; sample 1 uses current main and current sub/fixed. Ensure low-res below return zero is not counted as an emitted zero. |
| 8. History / scanline / skip | Two or more points with different source tokens/colors; prior main differs from current main. Exercise eligible/ineligible predecessor, previous clipped main, previous transparent-sub fallback, and native skips between state producer and consumer. Assert raw previous main, not its prior blended output, is used. At scanline start assert exact native seed/zero first below and hardware-unconfirmed marker. Activate midline and assert unknown carried origin until a native producer reestablishes it. |
| 9. Mid-stream registers / modes | Use actual `$2100/$2105/$2130/$2131/$2132/$2133` write handlers where practical with controlled synchronization stubs. Change add/subtract, fixed channels, half request, blend request, source enable, window masks, brightness and lowres/hires between positions. Assert mixed-age below controls vs refreshed above controls; continuous transitions retain valid history. Do not inject impossible CPU steps between normal below/above calls. |
| 10. Passivity / palette latch | Build fixtures from frozen `76bdb9250` and proposed implementation; compare baseline, new disabled, new enabled native output and logical-state signatures. Include all Math fields, actual light table, CGRAM latch and relevant CPU-visible memory-port behavior, counters, read counts and native stores. Include losing candidates' palette lookups and BG1 direct color, not just final winner lookup. |
| 11. Serializer / reset / load | Compare explicit native Size/Save layout and controlled bytes against frozen baseline; Save/Size must not clear diagnostics. Exercise actual PPU load hook, power/reset and synchronized/unsynchronized load paths where supported; ensure epoch invalidation/disarm and unknown provenance on reactivation. Do not compare uncontrolled RNG/raw coroutine addresses across processes/builds. |
| 12. Bounds / controller / export | Exactly capacity, capacity+1, repeated drops, saturation strategy, copy ownership, export while enabled rejection, missing/partial window, activation at 0/500, last window, callback sequence errors, unexpected disarm, path collisions and export errors. Overflow must not change native execution or replace known history with an incorrect retained-record link. |
| 13. End-to-end fixtures / regressions | Run existing EXP-003 producer/composition/window/hash/CLI regressions plus new source→operand→native-sample assertions with real BG/OBJ producer lineage. Manually seeded candidates alone cannot prove lineage preservation. |

**INFERENCE:** Screen arithmetic tests should log enough per-case context to diagnose operand or temporal mismatch. Retain baseline/enabled/disabled signatures and representative branch records. Passing a fixture establishes only that fixture, not universal SNES or hardware correctness.

## 15. Runtime validation assessment

**INFERENCE:** Keep the proposed **1,800 callbacks**, B disabled, C the **exact same executable** enabled, initial semantic **callback 500**, and restored deterministic settings/SRAM/input. No source finding requires a different initial callback. Whether callback 500 has useful math activity must be measured after EXP-004 capture.

**SOURCE OBSERVATION — retained artifacts inspected, no new ROM run:** Both existing EXP-003 B/C framebuffer CSVs are present and have SHA-256:

```text
9BC5FF87FC19E52615CFFB334AD9AD75900F4C8F12818972C210479A857B99FB
```

The B file contains 1,800 ordered indices 0–1799 and a completed footer. The common file hash establishes identity of the retained reference files. The settings and SRAM seed hashes match those documented in EXP-003 results:

```text
settings: E22FBA1B0E141499C94A25652C6A2FAEBEA27ADB8A11D4EC2E84BEDA43A8FA6B
SRAM:     D0FF1B294B5288D1AE1421EADF5B2D38A8752B76D472FF30BED9028E25B1C5B8
```

**SOURCE OBSERVATION — S12:103–139; S14:71–94:** Callback indices are zero-based. Before the run producing index 500, `frames.actual==500`; clear/enable occurs there. After that run returns, the count is 501, and capture is disabled/exported. There must be exactly one callback per ordinary run. The callback itself must not enable, clear, export, or tear down the observer.

**SOURCE OBSERVATION — retained composition endpoints and S16T:132–138:** The previous capture contains 61,440 positions but is not one monotonically increasing capture-frame image. Its first record is frame 0, V=225, x=0, H=58, field 1, skipped; its last is frame 1, V=224, x=255, H=1078, field 0. Frame events occur at `ppu.vdisp()`, and the capture interval spans the old frame's skipped tail and the next visible frame. The summary reports 4,096 skipped positions per screen. Do not equate `capture-relative frame` or the complete 256×240 record count with one-to-one ownership of every callback-buffer sample.

**INFERENCE:** Necessary implementation refinements, without changing the run length or initial callback:

1. Arm shared EXP-003 lineage and EXP-004 math history together. Keep seed/history invalidation explicit; no automatic unreported warm-up. An observed scanline seed can establish the native first-sample origin; activation without one remains unknown.
2. Preserve existing cycle-PPU, cold-start, no-run-ahead, no-rewind and no-fast-forward guards. Restore seeds before each process; require no UI reset/load/input changes. Confirm blur is off and no controller overlay modifies the callback buffer. Record ROM/settings/SRAM/executable hashes and build identity.
3. Address the section-8 bounds concern in focused work before claiming valid framebuffer destination association. Until resolved, export invalid-destination counts and restrict sample-to-callback claims to proven valid positions. If a native fix changes the baseline, regenerate/review A; do not force equality with a superseded native implementation.
4. Reuse the hash format and compare all ordered A/B/C rows and metadata, completion footers and process status. B=C is mandatory; retained A is available for comparison. Equal final-file hashes alone are not a substitute for checking complete intended runs and identities.
5. Distinguish transport/capture completion, semantic lineage completeness, actual arithmetic coverage, and hardware uncertainty. EXP-003's single `successful()` predicate rejects unknown winners but does not express all of those dimensions.
6. Inspect actual operation/operand/clip/brightness/hires counts only after callback 500 is captured. If arithmetic coverage is absent, label it VALID CAPTURE, INSUFFICIENT COVERAGE and select another deterministic window. Use deterministic gameplay-state infrastructure only if the no-input sequence is inadequate.

**UNKNOWN:** No EXP-004 runtime passivity, arithmetic activity, meaningful hires coverage, or source-to-final-sample preservation has yet been measured. Existing EXP-003 framebuffer equality and pre-math records do not establish those results.

## 16. Staged implementation plan

All stages are **INFERENCE — proposed future work**, contingent on an implementation task authorizing source changes.

| Stage | Concrete work / likely files | Exit evidence |
|---|---|---|
| 0. Freeze audit and resolve prerequisites | Review proposed schema changes and native output bounds concern. Use a narrowly scoped bounds fixture; decide whether valid-destination restriction suffices or a separate native-baseline task is needed. Keep upstream and other experiment worktrees read-only. | Baseline SHA, exact source anchors, bounds result and documented decision; no silent native fix |
| 1. Owned diagnostic model | New `bsnes/sfc/ppu/exp004-color-math.hpp/.cpp`; define composition pairs, per-sample paths/operands/results, history/epoch/seed validity, fixed-capacity retention, status and export. No native structure or serializer payload extension. | Model/history/bounds tests; measured record/allocation sizes |
| 2. Reuse EXP-003 handoff | Small changes to `exp003-composition.hpp/.cpp` for copied pending winner/record access; reuse `exp003-hooks.cpp` context. Integrate through `ppu.cpp`, `main.cpp`, and declarations in `ppu.hpp` only as needed; optional new `exp004-hooks.cpp` for glue. BG/OBJ/window/IO production algorithms should require no changes. | Existing EXP-003 tests pass; one lineage authority, including under overflow |
| 3. Native hook sequence | `screen.cpp`: scanline seed → pending carried snapshot → existing sub resolution → below branch/blend result → existing main eligibility → current gates/fallback → above blend result → first lookup/store → second lookup/store → pair completion. Retain native expression types, actions and order. Keep native Screen/PPU data layout unchanged. | Explicit lowres, hires, fallback, no-math, clip and output assertions; native baseline/disabled/enabled signatures |
| 4. Lifecycle | Extend diagnostic reset calls in `ppu.cpp` power and `serialization.cpp` load. Coordinate enable/clear/disarm and capture epochs; skips preserve native-equivalent history, scanline hooks install seed origin, load never restores lineage from Math values. | Save/Size unchanged; actual load/reset invalidation tests; no stale or fabricated provenance |
| 5. Runtime controller | New `target-bsnes/program/exp004-color-math-window.hpp`, based on the existing controller. Integrate `program.hpp/.cpp` and `target-bsnes/bsnes.cpp`; preserve `exp001-frame-hash.hpp` and `platform.cpp` hashing behavior. Proposed CLI: `--exp004-color-math-csv`, `--exp004-color-math-start-callback`, `--exp004-color-math-callback-count`. Reject conflicting capture modes. | Synthetic callback windows, collision/CLI/error tests, no export until core return |
| 6. Focused validation | New `tests/exp004/color-math-test.cpp`, controller/CLI tests and runner; use frozen `76bdb9250` as the new comparison baseline, actual native math and actual light-table construction. Execute section 14 in order, then EXP-003/hash regressions. | Per-case assertions, native signatures, serializer checks, test logs and retained representative records |
| 7. Supported desktop build | MSYS2 UCRT64, existing GCC/G++; from the EXP-004 worktree run `make -j4 -C bsnes local=false`. Defaults are desktop application, performance/O3, GNU C++17 and OpenMP. Record actual compiler version rather than assuming the previous version remains installed. | Full build log, executable SHA-256, exact commit/diff and supported configuration |
| 8. Deterministic runtime | Restore seeds; 1,800-callback B and same-binary C; capture callback 500; compare retained A/B/C; inspect coverage before choosing any additional deterministic window. | Complete hash sequences, comparison results, semantic summary, no drops/overflow for claimed capture, traceable arithmetic examples |
| 9. Curated findings | Write EXP-004 results outside experimental source; leave raw capture, ROM/SRAM and transient artifacts local. State host-only vs real-ROM evidence and unresolved hires/hardware/bounds limitations. | Reviewable results and next research recommendation; no automatic architecture acceptance |

**INFERENCE:** Summary metrics should include attempted/retained composition pairs; physical sample slots versus unique arithmetic evaluations; skip/not-emitted/duplicate paths; passthrough and clipped samples; effective fixed/sub/carried-main operands; requested-sub fallback count; add/subtract/half; brightness distribution; hires versus pseudo-hires; known/unknown current and carried lineage; carried-control validity; observed seeds; invalid output destinations; drops/overflow; callback range and export completion. Define denominators explicitly so lowres duplicate writes do not masquerade as twice the arithmetic coverage.

**INFERENCE:** Retain exact source/build/executable identity, seed hashes, commands, test/bounds logs, full ordered framebuffer comparisons and semantic capture summary. Curated examples should identify both source lineage and actual numeric operands/result, not merely present visually plausible colors. Performance measurements must separate native execution cost from after-run export time.

## 17. Architectural discoveries / contradictions

1. **SOURCE OBSERVATION:** Current main/sub provenance is insufficient for both hires outputs. **INFERENCE:** Extend the experiment's model; do not reinterpret EXP-003 as complete sample provenance.
2. **SOURCE OBSERVATION:** The hires second operand can be carried main, and controls have mixed lifetimes. **INFERENCE:** `none / sub / fixed` and a single current-point “math enabled” flag cannot express the path faithfully.
3. **SOURCE OBSERVATION:** Carried color is raw main color, not previous arithmetic output. **INFERENCE:** Hires needs a bounded source/control history entry, not an unbounded graph of accumulated blended results.
4. **SOURCE OBSERVATION:** Skips preserve Math; no-math above leaves blend/half stale; continuous mode changes do not reset it. **INFERENCE:** A naive previous-record link or unconditional history reset on every mode change is misleading.
5. **SOURCE OBSERVATION:** Scanline initialization produces a known native seed and the source disclaims hardware confirmation. **INFERENCE:** Native implementation provenance and hardware truth require separate status.
6. **SOURCE OBSERVATION:** Brightness lookup converts BGR555 to RGB555; EXP-003 host light tables are identity stubs. **INFERENCE:** Add encoding-aware output tests before any brightness claim.
7. **SOURCE OBSERVATION:** The native declared framebuffer bounds do not cover all computed write destinations. **UNKNOWN:** Runtime consequences and baseline sensitivity. **INFERENCE:** This needs focused investigation; it is not something an observer should silently fix or conceal.
8. **SOURCE OBSERVATION:** Callback intervals include skipped tail positions from the preceding capture-relative frame; refresh may mutate the buffer. **INFERENCE:** Composition count alone does not prove a complete, direct mapping to callback samples.
9. **INFERENCE:** Source inspection identifies passive-value capture points for operands, decisions, results and stores. No inherent need to rerun math or PPU memory access was found. Actual passivity remains to be demonstrated by host/runtime evidence.
10. **INFERENCE:** A single EXP-004 can cover lowres and hires in stages. The bounds investigation may warrant a separate native-baseline task, but the color-math boundary itself does not require a forced architectural split. If hires validation remains incomplete, report lowres support and hires INVESTIGATING separately.

## 18. Open questions

- **UNKNOWN:** What are the actual runtime/compiler consequences of the source-discovered output-pointer/buffer bounds mismatch, including overscan clearing and late scanline pointer construction?
- **UNKNOWN:** Does callback 500 contain actual arithmetic, fallback, clipping, nontrivial brightness, true hires or pseudo-hires? Existing pre-math evidence cannot establish the effective operations.
- **UNKNOWN:** Do proposed copied history and shared producer handoffs remain correct across all tested mode/blanking/window changes, partial fetches, overflow and reactivation? Tests must answer this.
- **UNKNOWN:** What reset/load/rewind behaviors beyond the controlled cold-start run are supported by complete native-method evidence? Existing hook-presence checks are insufficient.
- **UNKNOWN:** What is the exact hardware first-hires-sample behavior? It remains outside this source audit's authority.
- **UNKNOWN:** What allocation size and host execution cost result from the correct record format? Measure after defining semantics.
- **INFERENCE:** No need to solve Mode 7 lineage, renderer design, graphics API selection, or universal compatibility to answer the scoped experiment. Unsupported lineage must remain explicit.

## 19. Recommendation: proceed, revise EXP-004, or split the experiment

**INFERENCE — REVISE EXP-004, then proceed with staged implementation.** Keep the color-math/native-sample question and the 1,800-callback B/C design with initial callback 500. Before implementation, adopt carried-main operands, copied native/control history, explicit seed/unknown semantics, separate BGR555/RGB555 values, and valid-destination accounting. Investigate the inherited bounds concern as the first focused prerequisite; if it requires native repair, handle that in a separate authorized baseline task and regenerate the reference as necessary.

**UNKNOWN:** EXP-004's preservation/passivity hypothesis is not yet verified. The next authorized action should be the focused prerequisite and implementation/test stages above, not production renderer work or emulator selection. Successful experimental results would remain evidence for the semantic-preservation hypothesis, not accepted GTC-HD architecture.

[S1]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/screen.cpp:1
[S2]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/screen.hpp:1
[S3]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/window.cpp:5
[S3H]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/window.hpp:1
[S4]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/io.cpp:1
[S5]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/serialization.cpp:1
[S6]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/main.cpp:1
[S7]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/ppu.cpp:18
[S7H]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/ppu.hpp:53
[S8]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/exp003-composition.hpp:1
[S8C]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/exp003-composition.cpp:1
[S9]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/exp003-hooks.cpp:1
[S10]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/background.cpp:1
[S11]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/object.cpp:61
[S12]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/target-bsnes/program/exp003-composition-window.hpp:1
[S13]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/target-bsnes/program/program.cpp:113
[S13H]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/target-bsnes/program/program.hpp:1
[S13B]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/target-bsnes/bsnes.cpp:20
[S14]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/target-bsnes/program/exp001-frame-hash.hpp:1
[S14P]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/target-bsnes/program/platform.cpp:205
[S14V]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/target-bsnes/program/video.cpp:65
[S15]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/tests/exp003/composition-test.cpp:1
[S15R]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/tests/exp003/run-tests.py:1
[S15W]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/tests/exp003/observer-window-test.cpp:1
[S15C]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/tests/exp003/observer-window-cli-test.py:1
[S16]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/system/serialization.cpp:1
[S16S]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/system/system.cpp:11
[S16T]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/cpu/timing.cpp:132
[S17]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/GNUmakefile:1
[S17N]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/nall/GNUmakefile:53
[S18]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/emulator/random.hpp:12
[S18C]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/counter/counter.hpp:1
[S18I]: C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-004/bsnes/sfc/ppu/counter/counter-inline.hpp:1
[D3]: C:/Users/User/Documents/GTC-HD-Lab/docs/experiments/EXP-003/RESULTS.md:391
