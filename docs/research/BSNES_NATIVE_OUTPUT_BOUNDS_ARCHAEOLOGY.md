# bsnes Native Output Bounds — Source Archaeology and Intent Analysis

Date: September 23, 2026.

**Phase 1 complete: source archaeology only. Candidate-correction design is justified; no correction is selected or authorized by this report.**

**EXP-004 remains blocked.** Its P0 disposition remains **STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION**. This report does not close the native-baseline investigation, establish a corrected baseline, or authorize EXP-004 implementation.

## 1. Question and scope

What framebuffer geometry and late-scanline behavior was the audited bsnes cycle PPU intended to implement, and where did the mismatch between its declared storage and calculated destinations originate?

**HISTORICAL SOURCE OBSERVATION:** A concrete sequence was found:

1. A padded, dynamically allocated 512×512 framebuffer supported a smaller presentation window.
2. `a03d91882c30d9becce5a61740109d163f61287c` replaced that allocation with an inline 512×480 array and moved non-overscan centering into store placement. Existing rendering through V=239 then exceeded the array in non-overscan mode.
3. `0623d6ac2b785ccbb2b62521cb00dfe4a627b595` subsequently restricted rendering to `V < vdisp()`, avoiding those stores with stable display controls.
4. `409dd371b96e863ea626f85faa51db140307d275` backported a newer PPU scheduler that renders through V=240 regardless of overscan. This restored the stable non-overscan overrun and added an overscan-mode overrun.
5. `793f2e5bf44a421237905c6638ce05f6e2d6cb5f` later introduced the transition-clear loop through pair row 240, already outside the smaller allocation.

**INFERENCE:** The present defect combines storage/placement integration and later render-range/clear-boundary changes. Neither the +7 centering convention nor the 512×480 callback is, by itself, evidence of an incorrect presentation design.

This is local source/history analysis, not runtime or hardware validation. No emulator source, tests, experiment documentation, project state, Git refs, or baseline were changed. No tests, builds, ROMs, commits, pushes, or network fetches were performed.

Read alongside:

- [EXP-004 specification and implementation gate](../experiments/EXP-004/SPEC.md).
- [P0 output-bounds report](../experiments/EXP-004/P0_OUTPUT_BOUNDS_REPORT.md).
- [P0 output-bounds matrix](../experiments/EXP-004/P0_OUTPUT_BOUNDS_MATRIX.csv).
- [EXP-004 source audit](../experiments/EXP-004/SOURCE_AUDIT_AND_IMPLEMENTATION_PLAN.md).

Evidence labels used here:

- **SOURCE OBSERVATION:** directly inspected audited-baseline source or repository metadata.
- **HISTORICAL SOURCE OBSERVATION:** inspected historical source, diffs, comments, or commit messages.
- **INFERENCE:** a conclusion derived from those observations.
- **UNKNOWN:** not established by this investigation.

P0's existing compiler-layout and defined-storage fixture evidence is cited as prior evidence; it was not rerun or converted into a claim about exact native undefined-behavior execution.

## 2. Exact baseline

**SOURCE OBSERVATION:**

| Item | Inspected identity |
| --- | --- |
| External project | bsnes; upstream identity `https://github.com/bsnes-emu/bsnes.git` |
| Research checkout | `experiments/bsnes-native-output-bounds/` |
| Branch | `gtc-hd/investigate-native-output-bounds` |
| HEAD, abbreviated below as U | `7d5aa1e656b9171524d01b1b22917197d8121cb4` |
| Subject | `fix horizontal offset in high-resolution offset-by-tile mode` |
| Author / commit dates | May 22 / May 23, 2026 |
| Initial checkout status | Clean; non-shallow repository |
| Local upstream refs | `master`, `origin/master`, `origin/HEAD`, and `nightly` identify U |

Source paths below are relative to this external checkout. A citation such as **U, `bsnes/sfc/ppu/screen.cpp:1–33`** identifies source at U, not a tracked GTC-HD document. Historical references name their commit and path explicitly; their line numbering need not match U.

Primary inspected baseline sources:

| Source at U | Relevant functions/data |
| --- | --- |
| `bsnes/sfc/ppu/ppu.hpp:49–64` | Output, adjacent light table, display state and getters |
| `bsnes/sfc/ppu/ppu.cpp:16–40,81–85,189–212` | Light-table construction, initialization, refresh |
| `bsnes/sfc/ppu/screen.cpp:1–33,71–72` | Placement, stores, live blanking |
| `bsnes/sfc/ppu/main.cpp:1–32,180–194` | Frame latch, clearing, scheduler and sample cadence |
| `bsnes/sfc/ppu/io.cpp:639–654` | SETINI writes and vdisp update |
| `bsnes/sfc/ppu/serialization.cpp` | Separate serialization of live/display controls |
| `bsnes/sfc/ppu/background.cpp`, `object.cpp` | Live rendering controls and vdisp consumers |
| `bsnes/sfc/ppu/counter/counter.hpp:1–11`, `counter-inline.hpp:19–39` | Separate timing latch and field/region progression |
| `bsnes/sfc/cpu/timing.cpp:96–139`, `bsnes/sfc/system/system.cpp:109–110` | Frame event and refresh dispatch |
| `bsnes/target-bsnes/program/platform.cpp:205–230` | Desktop callback, crop and filter handoff |
| `bsnes/target-bsnes/program/viewport.cpp:4–32,50–72` | Display sizing and paused refresh |
| `bsnes/target-bsnes/program/filter.cpp`, `bsnes/filter/none.cpp` | Filter selection and sample consumption |

History inspection used `git blame`, `git log --follow`, `git log -S`, `git log -G`, `git show`, historical trees, ref enumeration and ancestry queries. Representative searches, run from the research checkout, were:

```text
git blame -L 49,64 -- bsnes/sfc/ppu/ppu.hpp
git blame -L 1,35 -- bsnes/sfc/ppu/screen.cpp
git blame -L 1,32 -- bsnes/sfc/ppu/main.cpp
git blame -L 189,212 -- bsnes/sfc/ppu/ppu.cpp
git log --follow -- bsnes/sfc/ppu/ppu.hpp
git log --follow -- bsnes/sfc/ppu/ppu.cpp
git log --follow -- bsnes/sfc/ppu/screen.cpp
git log --follow -- bsnes/sfc/ppu/main.cpp
git log -S "512 * 512" -- "**/ppu/ppu.cpp"
git log -S "512 * 478" -- "**/ppu/*"
git log -S "512 * 482" -- "**/ppu/*"
git log -G "output.*512.*(480|478|482|512)|output.*new" -- "**/ppu/ppu.cpp" "**/ppu/ppu.hpp"
git log -G "vcounter.*239|vcounter.*240" -- bsnes/sfc/ppu/ppu.cpp bsnes/sfc/ppu/main.cpp
git log -S "center image onscreen" -- "**/video.cpp"
git show a03d91882c -- bsnes/sfc/ppu/ppu.hpp bsnes/sfc/ppu/ppu.cpp bsnes/sfc/ppu/screen.cpp
git show 0623d6ac2b -- bsnes/sfc/ppu/ppu.cpp
git show 409dd371b9 -- bsnes/sfc/ppu/ppu.cpp bsnes/sfc/ppu/main.cpp
git show 793f2e5bf4 -- bsnes/sfc/ppu/main.cpp
git log --ancestry-path --all HEAD..
git for-each-ref --contains HEAD
```

The historical path searches also included `asnes/ppu/`, `snes/ppu/`, `bsnes/snes/ppu/`, `higan/sfc/ppu/`, and `sfc/ppu/`. Local README/documentation and commit-message searches covered overscan, interlace, 224/225/239/240, 448/478/480, framebuffer/output buffers, centering, cropping and vdisp. Current prose documentation supplied no explicit bounds rationale; historical comments and commit messages supplied the strongest intent evidence.

## 3. Current framebuffer geometry

**SOURCE OBSERVATION — U, `ppu.hpp:55–56`:** The declaration is `uint16 output[512 * 480]`, followed by `uint16 lightTable[16][32768]`. The output contains 245,760 entries, indexed 0–245,759. Array extent is not enlarged by the following member.

**SOURCE OBSERVATION — U, `screen.cpp:1–29`:** With V the native vertical counter, O the latched overscan flag, I latched interlace, F the current field, x=0..255 and s=0 or 1:

```text
pairY = V + (O ? 0 : 7)
A = 1024 * pairY + (I && F ? 512 : 0)
B = A + (I ? 0 : 512)
indexA = A + 2*x + s
indexB = B + 2*x + s
```

A pair row means two 512-sample memory rows. It is not another native scanline counter.

- The 256 composition positions emit 512 horizontal samples. Low-resolution output repeats the above/main result in both slots; hires/pseudo-hires uses below then above.
- Non-interlace writes identical samples to adjacent rows A/B, separated by 512 entries.
- Interlace aliases A/B within the selected field row. F=1 adds 512 entries; successive fields populate alternate rows of the same 480-row image.
- Non-overscan shifts the destination down seven pair rows. Overscan uses V directly.
- `Screen::run()` returns at V=0. The scheduler invokes rendering through V=240; only V>240 takes the late-line bypass.
- Forced blank or live non-overscan at V≥225 returns zero from below/above, but does not suppress the stores.
- `screen.scanline()` runs before the V>240 check, including on lines with no stores.

**INFERENCE — presentation geometry:** In stable non-overscan mode, native V=1..224 maps to pair rows 8..231, or callback rows 16..463: 448 rows of content, with 16 rows of border at each end of a 480-row presentation. Seven added pair rows suffice because V=0 is skipped. Adding eight to V would shift this established mapping.

In stable overscan mode, V=1..239 maps to pair rows 1..239, or callback rows 2..479. Pair row 0 is skipped by Screen and initialized by power. V=240 maps to rows 480/481, outside the callback and array. The 480-row presentation does not prove that 240 nonzero-V source lines belong in it.

**SOURCE OBSERVATION / INFERENCE — late-line meaning:**

| Stable live/latched mode | V=225..232 | V=233..239 | V=240 |
| --- | --- | --- | --- |
| Non-overscan | Zero-return samples stored in valid bottom-border pairs 232..239 | Zero-return stores outside output, pairs 240..246 | Zero-return stores outside output, pair 247 |
| Overscan | No non-overscan blanking return; destinations within callback | Same, through pair 239 | No non-overscan blanking return; destination pair 240 outside output |

Interlace changes which row in a pair is written, not the first invalid pair. Forced blank changes supplied values, not destination validity. These are source-path descriptions, not proof of particular real-ROM values.

The [P0 matrix](../experiments/EXP-004/P0_OUTPUT_BOUNDS_MATRIX.csv) supplies detailed indices for all placement combinations. Maximum attempted indices are 253,951 with non-overscan placement and 246,783 with overscan placement, in non-interlace or field-1 interlace. No-store late lines still require separate pointer-formation analysis.

## 4. Historical timeline

All dates below are recorded author dates. Subjects are reproduced as commit identities. Each row is **HISTORICAL SOURCE OBSERVATION**; the last column distinguishes explicit rationale from inference. Changes unrelated to geometry are omitted.

| Commit / date / subject | Affected source and before → after | Intent evidence |
| --- | --- | --- |
| `165f1e74b5b136f42b219c7905a00438abd1f3e9` — 2010-08-09 — First version split into asnes and bsnes. | `asnes/ppu/ppu.cpp`, `screen/screen.cpp`: oldest directly followed snapshot already has 512×512 dynamic storage, output offset by 16×512, V×1024 placement, field offset and frame-latched display controls. | Observation at a PPU-lineage root, not a demonstrated introduction relative to a parent. |
| `378b78dad744464217da82fc9c2a6857ec1da816` — 2011-04-27 — Update to v077r05 release. | `bsnes/snes/ppu/screen/screen.cpp`: adds V=0 return in Screen::run. | Source establishes the skip; no inspected bounds rationale. |
| `0a3d6e4c531721f929542e535eda4f820b6787f6` — 2011-04-30 — Update to v078 release. | `bsnes/snes/ppu/ppu.cpp`, `screen/screen.cpp`: mode-dependent render limit becomes V≤239; non-overscan V≥225 returns zero inside get_pixel. | Message explicitly says the accuracy PPU clears the overscan region on every frame when disabled. |
| `82a17ac0f5b460d92407068e1a92cf1fc7fd7345` — 2011-09-24 — Update to v082r21 release. | `bsnes/snes/ppu/ppu.cpp`: dynamic surface element type changes uint16→uint32; 512×512 extent and +16-row offset persist. | Type conversion observed; no smaller-allocation claim. |
| `689fc490476263e19b55cd47989205c0937d6b91` — 2012-05-08 — Update to v088r15 release. | `bsnes/sfc/system/video.cpp`: callback uses output minus 7×1024 when non-overscan instead of the surface base. | Comment explicitly describes centering by scrolling the video buffer up; message says overscan-off centers the image. |
| `d9400084c2a18949925d88a2247dc3c1cbab2f91` — 2013-01-23 — Update to v092r02 release. | `higan/sfc/ppu/screen/screen.cpp`: separate sub/main calculations with carried color-math state; retains two horizontal samples and live V≥225 blanking. | Message credits AWJ's hires color-blending improvements. Not an allocation change. |
| `cec33c1d0f49d97c2d4b361fa43d59c2fd463aa8` — 2016-01-15 — Update to v096r07 release. | `higan/sfc/ppu/ppu.cpp`, `system/video.cpp`: PPU output becomes an unshifted 512×512 allocation; separate Video output owns padded 512×512 storage and an accuracy-profile 512×480 callback. | Source demonstrates backing storage and presentation as distinct layers. |
| `a2d3b8ba157f00136e2df62662169e2a6fe829de` — 2016-04-12 — Update to v098r04 release. | `higan/sfc/ppu/ppu.cpp`: restores +16×512 offset on PPU allocation; integrates Emulator::video callback with −14×512 non-overscan origin, interlace-dependent pitch and 240/480 height. | Message explicitly introduces a common video layer between cores and UIs. |
| `e2ee6689a0b913cdb05f63aaedcbe2436383629f` — 2016-04-22 — Update to v098r06 release. | `higan/sfc/ppu/ppu.cpp`: callback moves from scanline handling into PPU::refresh; geometry retained. | Message explicitly says video refresh moved to the host thread to fix a crash. |
| `7f3cfa17b9b6a2f2443131ec862179971ee52715` — 2016-05-26 — Update to v098r12 release. | `higan/sfc/ppu/ppu.cpp`, `screen/screen.cpp`: pitch becomes 512 and height always 480; lineA/lineB replace one output cursor and duplicate rows outside interlace. | Message explicitly identifies 512×480 output, higher-resolution light-gun cursors and avoiding sprite-scaling logic. |
| `51e3fcd3fa45dbc0d7992e12873f5a2bbc010c49` — 2018-05-28 — Update to v106r31 release. | `higan/sfc/ppu/ppu.cpp`: frame event moves V=241→240; render limit remains V≤239. | Source change; message discusses fast-PPU development, not this event's rationale. |
| `77ac5f9e88fb06ac2f171f51e5e7b40076fadd6b` — 2018-06-03 — Update to v106r35 release. | `higan/sfc/ppu/ppu.cpp`: callback height 480→478 and non-overscan origin −14→−12 rows; backing stays 512×512. | Message explicitly discusses 223/239 versus 224/240 presentation, the unrendered line 0 and border symmetry. |
| `f70a20bc42780b4419692dbf6d682a57880f5ca0` — 2018-06-24 — Update to v106r41 release. | Same source: callback height 478→480 and origin −12→−14 rows. | Message explicitly reverts the earlier 223/239 presentation to 224/240. |
| `5b97fa24157a168487d1db692f0a4fec9216887e` — 2018-06-26 — Update to v106r42 release. | `higan/sfc/ppu/ppu.hpp`, `io.cpp`: display.vdisp caches live overscan's 225/240 boundary; getter returns it. | Source observation; membership in display does not make vdisp a V=0 latch. |
| `d87a0f633daba1e199974689b0eb1af1e71f780a` — 2019-07-07 — Update to bsnes v107r4 beta release. | `bsnes/sfc/ppu/ppu.cpp`, `ppu.hpp`, `screen.cpp`: uint32→uint16 dynamic 512×512 storage; adds lightTable and direct uint16 platform callback. | Message describes restored video filters; source establishes conversion details. |
| `a03d91882c30d9becce5a61740109d163f61287c` — 2019-07-10 — Update to bsnes v107r5 beta release. | Same PPU files: padded dynamic 512×512→inline 512×480; callback origin adjustment removed; +7 moves into Screen::scanline. V≤239 unchanged. | Message discusses improved overscan masking, especially HD mode 7; no explicit justification for discarding backing capacity. |
| `52f34ea4704fc36a4dcb603d97d4c813b94ca492` — 2019-07-12 — Update to bsnes v107r6 beta release. | `bsnes/sfc/ppu/ppu.hpp`: uint16_t spelling becomes uint16; extent unchanged. | Message explicitly describes integer-type conversion. This is the current blame attribution, not the allocation-size origin. |
| `0623d6ac2b785ccbb2b62521cb00dfe4a627b595` — 2019-07-19 — v107.9 | `bsnes/sfc/ppu/ppu.cpp`: V≤239→V<vdisp(); display latch moves inline into V=0 scanline handling. | Source change; message does not identify this as a bounds fix. |
| `409dd371b96e863ea626f85faa51db140307d275` — 2019-09-21 — v109.5 | `bsnes/sfc/ppu/ppu.cpp`, new `main.cpp`: replaces V<vdisp() loop with cycle scheduler bypassing only V>240; output allocation and +7 unchanged. | Message explicitly identifies a backport of higan's newer accuracy PPU with sprite caching; V=240 destination intent is unstated. |
| `e78aca34b9454328b2de445806a28076ca21023b` — 2019-10-07 — v111.3 | `bsnes/sfc/ppu/main.cpp`: frame event V=240→vdisp(); store cutoff unchanged. | Message discusses save-state improvements; no bounds rationale. |
| `fb95d5b59f2661b698987072c0545620ec686751` — 2019-10-12 — v111.5 | `bsnes/sfc/ppu/main.cpp`, `cpu/timing.cpp`: frame event moves to CPU::scanline with PPU synchronization; store cutoff unchanged. | Message and comment explicitly explain PPU/NMI input-polling race avoidance. |
| `793f2e5bf44a421237905c6638ce05f6e2d6cb5f` — 2019-12-30 — v113.4 | `bsnes/sfc/ppu/main.cpp`: adds overscan-on→off clear for pairs 1..7 and 232..240. | Message explicitly names clearing overscan to fix World Class Service SNES Tester; neither message nor comment justifies inclusive pair 240. |

Later line blame for `lineA/lineB` points to the June 2016 naming cleanup `ae5b4c3bb30112b13312a575f555424fb9b83e26` (“Update to v099r01 release.”, June 14, 2016). Parent inspection shows the two-row behavior already introduced by `7f3cfa17b9`. The `io` spelling for live blanking comes from `82293c95aef4f8c6322b3d090b32282cf5a354c4` (“Update to v099r14 release.”, July 1, 2016); the behavior predates that rename.

## 5. Output allocation history

**HISTORICAL SOURCE OBSERVATION:** Along the directly followed cycle-PPU lineage, the important extents are 512×512 dynamic backing and, from July 10, 2019, 512×480 inline backing. Historical sample types vary; sample count and byte count must not be conflated.

The January 2016 transition moved presentation padding into a separate Video allocation without shrinking the PPU's 512×512 allocation. April 2016 returned the padded origin to the PPU. July 7, 2019 changed element type and output encoding while retaining the larger backing. July 10 changed storage extent and origin handling.

No 512×478 or 512×482 **cycle-PPU backing allocation** was found in the inspected lineage/pattern searches. The documented 478 value was a callback-height experiment. A power-time fill of `512 * 480` also existed while allocation remained `512 * 512`; a fill length is not an allocation declaration.

**HISTORICAL SOURCE OBSERVATION — immediate parent of the shrink, `d87a0f633d`:**

```text
backing allocation: 512 * 512 entries
PPU output origin:  backing + 16 * 512
screen destination: PPU output + V * 1024, with row/field offsets
callback origin:    PPU output - (overscan ? 0 : 14 * 512)
callback geometry:  512 * 480, pitch 512 entries
rendered V:         1..239
```

**INFERENCE — bounds of those historical stores:** Non-interlace V=239 used physical backing rows 494 and 495, safely below row 512. With non-overscan presentation, the callback began at physical row 2 and ended at row 481; V=233..239 stores were outside the presented image but inside the allocation. With overscan presentation, the callback began at row 16 and ended at row 495.

At `a03d91882c`, the same non-overscan callback-relative destinations became indices in the actual smaller array: V=233..239 occupied rows 480..493 and exceeded it. This establishes a specific storage regression for these stores without requiring a ROM run.

**UNKNOWN / qualification:** This is not a claim that the old implementation was universally memory-safe. It also formed scanline pointers before deciding whether to render, including later counters that could exceed even the historical backing. The identified regression concerns the documented store destinations; pointer-only defects have a broader history.

## 6. Placement arithmetic history

**HISTORICAL SOURCE OBSERVATION:** The V×1024 stride and 512-entry field offset already exist in the 2010 `asnes/ppu/screen/screen.cpp` snapshot. They represent a two-row slot per native line. The renderer emitted two horizontal samples for a composition position before the later fixed-height callback.

The 2012 centering change has unusually direct intent evidence: `689fc49047`, `bsnes/sfc/system/video.cpp`, comments that disabling overscan shifts the image down by scrolling the video buffer up, and that memory before PPU output contains black scanlines.

In 2016, `7f3cfa17b9` made the two-row storage representation the regular 480-row callback representation even outside interlace. It writes both rows in non-interlace; in interlace both cursors point to the current field's row.

**INFERENCE:** The July 2019 move from callback-relative origin adjustment to destination adjustment is algebraically consistent for presented coordinates:

```text
old non-overscan: rendered row 2*V relative to PPU output,
                 callback begins 14 rows before that origin
                 => callback row 2*V + 14
new non-overscan: pairY = V + 7
                 => callback row 2*V + 14
```

Thus +7 preserves established placement. The unsafe change was applying those coordinates to a smaller allocation without maintaining a compatible destination boundary. This does not select a remedy for that incompatibility.

## 7. Render-range history

**HISTORICAL SOURCE OBSERVATION:** The 2010 snapshot renders V≤224 or V≤239 according to live overscan. The April 2011 change extends non-overscan execution to V≤239 and returns black samples at V≥225, with an explicit clearing rationale. The later below/above implementation retains this distinction between returning black and suppressing a store.

The intervening July 2019 restriction must not be omitted:

| Revision/interval | Scheduler render condition | Consequence with stable live/latched controls |
| --- | --- | --- |
| `d87a0f633d`, immediately before shrink | V≤239 | Stores fit the padded allocation |
| `a03d91882c`, after shrink | V≤239 | Non-overscan V=233..239 outside output; overscan V=1..239 fits |
| `0623d6ac2b` through inspected pre-backport parent `18d2ab6435fd79d55b3c8b2895d570618afbfe93` | V<vdisp(), where vdisp is live 225/240 | Stable non-overscan stops at 224; stable overscan at 239 |
| `409dd371b9` through U | V≤240, independently of vdisp | Non-overscan V=233..240 outside; overscan V=240 outside |

**INFERENCE:** July 19 avoided the stable-mode store failure, but is not evidence of a complete repair: pointer construction still preceded gating, and live vdisp could disagree with latched placement. Its commit message does not call it a bounds correction. September 21 is the concrete regression from the immediately preceding stable-mode behavior to today's wider store range.

**UNKNOWN:** The backport message does not explain why V=240 needed to execute the complete cycle pipeline, or whether the original donor used compatible backing storage. The exact donor revision is not identified by that message. Do not equate a potentially necessary execution/timing range with a proven necessary framebuffer-store range.

## 8. Overscan-clear history

**SOURCE OBSERVATION — U, `main.cpp:2–12`:** At V=0, old latched overscan=true and live overscan=false triggers:

```cpp
for(uint y = 1; y <= 240; y++) {
  if(y >= 8 && y <= 231) continue;
  auto output = ppu.output + y * 1024;
  memory::fill<uint16>(output, 1024);
}
```

The display flags are updated after this clear.

**HISTORICAL SOURCE OBSERVATION:** The exact loop first appears in `793f2e5bf4`, December 30, 2019. The commit identifies a stale-overscan fix for World Class Service SNES Tester. Its comment says to clear the overscan area that will not be rendered to after overscan is disabled. The same commit adds a similar loop to the fast PPU; that parallel addition does not establish the cycle PPU's storage contract.

**INFERENCE:** The excluded pairs 8..231 are exactly the centered V=1..224 non-overscan content. Clearing surrounding old overscan content is therefore consistent with the presentation design. “Won't be rendered to” should be understood in that content context: the cycle PPU at U also makes later zero-return stores in the bottom border, sometimes after the current frame event.

Pairs 1..7 are seven top-border pairs other than skipped pair 0. Pairs 232..239 are eight bottom-border pairs within the callback. Including 240 adds a ninth bottom pair outside both array and callback. P0 documents 16,384 cleared entries, of which 1,024 are outside output.

**HISTORICAL SOURCE OBSERVATION / INFERENCE:** Pair 240 could fit in the old padded allocation: relative to its +16-row output origin it would occupy physical rows 496/497. However, **this clear loop did not originate with that larger allocation**. It was introduced more than five months after the inline 512×480 declaration, which is present in the introducing commit. There is no inspected older copy of this exact cycle-PPU transition loop to justify treating it as a retained valid old boundary.

The clear failure is a separate later boundary error with the same pair-index convention as the Screen failure. Its trigger is the overscan transition, and it is not cured merely by explaining late Screen stores.

**UNKNOWN:** Why the author selected inclusive 240 instead of a boundary consistent with the declared array is not documented. It may reflect confusion between a count, counter value and pair index, but that explanation remains an inference, not a recorded maintainer decision.

## 9. Refresh/frontend contract

**SOURCE OBSERVATION — U:** The relevant desktop path is:

```text
CPU::scanline at live vdisp()
  -> synchronize PPU; leave Frame event
  -> System::frameEvent()
  -> PPU::refresh()
  -> platform->videoFrame(output, 1024 bytes, 512, 480, scale=1)
  -> Program::videoFrame()
  -> optional frontend crop
  -> software filter / palette conversion
  -> video output and viewport sizing
```

Sources: `cpu/timing.cpp:132–139`, `system/system.cpp:109–110`, `ppu/ppu.cpp:189–211`, `target-bsnes/program/platform.cpp:205–230`.

PPU::refresh delegates to the fast PPU when configured and skips run-ahead output. For the cycle path it may modify output with blur emulation, then draw a controller overlay, before calling the platform. The callback is therefore a presentation-stage buffer, not necessarily a direct snapshot of each Screen store.

The desktop callback saves its original pointer/dimensions for subsequent refresh. If frontend `settings.video.overscan` is false, height/240=2: it advances 16 memory rows and reduces height by 32, yielding 512×448 from original rows 16..463. With the option true, it passes the full 512×480 onward. This UI option is separate from emulated SETINI overscan.

`viewport.cpp` sizes presentation around 256×224 or 256×240 with optional aspect correction. `filter.cpp` selects a compatible filter; `filter/none.cpp` reads the supplied rectangle and converts samples through the palette. None of these operations grants Screen permission to write beyond its backing array. This report traces the normal desktop frontend, not every possible platform implementation.

**HISTORICAL SOURCE OBSERVATION:** There are explicit examples of backing and callback sizes differing: the padded PPU allocation before July 2019, and the separate padded Video output in January 2016. The 2018 478-row experiment changed the exposed window, not the allocation. July 2019 did **not** reduce callback height from 512 to 480; 480 was already established. It reduced backing storage to match the existing callback extent.

**INFERENCE:** Callback timing also matters. At U the frame event is based on live vdisp (225 or 240); this does not halt subsequent emulation of late scanlines when execution resumes. A late store need not belong to the same callback interval as the visible content preceding it. A correction design must preserve this distinction rather than infer store suppression from callback dimensions or event timing.

## 10. Older bsnes/higan ancestry

**HISTORICAL SOURCE OBSERVATION:** `git log --follow --name-status` traces the PPU header through actual renames:

| Commit | Path transition |
| --- | --- |
| `1a32ed7cfac56ef1ce7bed16b7ae1b7304231f15` | `asnes/ppu/ppu.hpp` → `snes/ppu/ppu.hpp` |
| `a59ecb3dd4a8d8bdbbb1ba2fb92da576e23599e0` | `snes/ppu/ppu.hpp` → `bsnes/snes/ppu/ppu.hpp` |
| `bb4db22a7df2cce9d002ada2f95e93a04a8a5055` | `bsnes/snes/ppu/ppu.hpp` → `bsnes/sfc/ppu/ppu.hpp` |
| `94b2538af5849f7e194b35c0e823a266eee182ea` | `bsnes/sfc/ppu/ppu.hpp` → `higan/sfc/ppu/ppu.hpp` |
| `4e2eb23835228477859f4d9de69e8cd27a4eeea6` | `higan/sfc/ppu/ppu.hpp` → `sfc/ppu/ppu.hpp` |
| `47d4bd4d811ac0f314462f33feb3dc36c1c56948` | `sfc/ppu/ppu.hpp` → `higan/sfc/ppu/ppu.hpp` |
| `922a0e420ca85ffe710f28274c71fd6c44f05fb5` | `higan/sfc/ppu/ppu.hpp` → `bsnes/sfc/ppu/ppu.hpp` |

Screen and PPU implementation history follows these generations as well; the old nested `screen/screen.cpp` later becomes `screen.cpp`. The current scheduler is additionally identified by its introducing message as a newer higan accuracy-PPU backport.

This supports actual code continuity from older bsnes through higan-era code and back to bsnes. It is not a conclusion based on similarly named directories or on the current README alone.

**SOURCE OBSERVATION / limit:** The directly followed PPU lineage reaches the root snapshot `165f1e74b5b136f42b219c7905a00438abd1f3e9`, which has no parent. Local older release tags and `graft-point` also exist. The latter identifies `81f43a4d015ea0aafccb2df9961353f951b32e70`, whose message describes the dot-based/scanline-based core split. It is not connected as the parent of that PPU root in the inspected graph. No graft or replacement was installed. Earlier tagged code was not silently treated as proven ancestry.

**INFERENCE:** The broader design predates the storage defect: padded backing and field layout are present in 2010, centering is explicit in 2012, and the two-row fixed presentation is explicit in 2016. The small-array integration and subsequent boundary changes are demonstrated in the 2019 bsnes history. This report does not assign the entire defect to the original renderer or prove the exact donor higan revision responsible for V=240 execution.

## 11. Newer-history findings

**SOURCE OBSERVATION:** The local upstream branch, remote-tracking refs and nightly tag stop at U. An ancestry-path query over all local refs finds only seven GTC-HD experimental commits descending from U: observer implementations, runtime harness/window controls, and P0 tests. Those are research descendants, not later upstream fixes.

Relevant geometry lines at U still blame to the 2019 changes. Local history from their introduction through U contains no later allocation/placement/cutoff/clear repair for the cycle PPU described here.

**UNKNOWN:** There is no newer upstream descendant available locally to assess for a fix. No remote fetch, issue search or online upstream check was performed. The finding is **no later upstream fix in the available local history**, not “no fix exists anywhere.”

## 12. Live-vs-latched overscan analysis

**SOURCE OBSERVATION — U:**

| State | Updated/used where | Lifetime |
| --- | --- | --- |
| `io.overscan` | SETINI write, `io.cpp:639–646`; below/above blanking | Live register value |
| `display.overscan` | `main.cpp:2–12`; `screen.cpp:2` placement | Updated at V=0 after transition clear |
| `display.vdisp` | `updateVideoMode()`, `io.cpp:653–654` | Derived from live io.overscan, despite its struct name |
| `display.interlace` | `main.cpp:11`; `screen.cpp:5–6` | V=0 placement latch |
| Counter `time.interlace` | `counter-inline.hpp:20–23` | Separately sampled at V=128 for counter timing |

The frame latch already exists in the 2010 PPU snapshot. Live blanking is explicit from 2011; the current below/above form dates to 2013. The 2019 clear condition deliberately compares the previous display value to the new live value before updating the latch. Both generations are separately serialized at U.

**INFERENCE:** This split is a longstanding, deliberate source-level frame-boundary arrangement: keep placement consistent across the frame while register-dependent rendering behavior can change. The transition-clear branch would make little sense if both fields were always identical. This establishes implementation intent, not exact hardware latch timing.

| Latched overscan | Live overscan | U late-source behavior |
| --- | --- | --- |
| Off | Off | Placement adds 7; V≥225 returns zero; invalid stores still start V=233 |
| Off | On | Placement still adds 7; non-overscan blanking no longer applies; invalid stores still start V=233 |
| On | Off | Placement has no +7; V≥225 returns zero; V=240 still stores outside |
| On | On | No +7 and no non-overscan blanking; V=240 still stores outside |

**INFERENCE:** Mixed generations can explain nonzero candidates at late destinations even with centered placement. They are **not necessary** to explain the baseline storage mismatch: stable off/off and on/on already calculate invalid stores. In the July 19 restricted scheduler, live overscan/vdisp changes could reopen late rendering while placement remained latched, so the stable-mode improvement must not be called a complete mixed-mode fix.

**UNKNOWN:** The precise hardware rationale for each separate latch, complete mid-frame reachability, and all save/load or PAL/interlace histories were not established. The counter comment explains its own V=128 timing latch; it does not establish that display.overscan has the same purpose or hardware behavior.

## 13. Candidate root causes

Each assessment below is **INFERENCE** grounded in the cited history; no row selects a repair.

| Candidate explanation | Evidence for | Evidence against / qualification | Unknowns |
| --- | --- | --- | --- |
| Backing allocation became too small for existing stores | July 10 replaces 512×512 padded backing with 512×480; V=233..239 changes from allocated but unpresented to outside the array | Allocation alone does not explain the later V=240 extension or new clear loop | Whether shrinking was intended to rely on a different render gate |
| Rendering continues too late for the present destination layout | September backport replaces V<vdisp() with V≤240 while keeping the small array | Earlier execution through 239 had an explicit black-border clearing purpose; rendering also carries execution-visible work | Which late operations must execute, and which destinations/results should persist |
| +7 placement is inconsistent with storage | It moves V=233..240 past the 240-pair capacity | +7 preserves the old callback-relative centering exactly; active V=1..224 fits and matches frontend crop | Whether all mixed-mode destinations were considered during integration |
| Clear loop retained an old valid boundary | Pair 240 would fit the former larger backing; the value matches the scheduler's endpoint | The exact loop was added after the shrink, not carried forward from the old larger allocation | Why inclusive 240 was chosen |
| Callback reduction left larger-buffer assumptions behind | Historically callback and backing extents differed; 2018 experimented with height 478 | The actual 2019 defect did not follow a callback reduction: callback stayed 480 while backing shrank | Whether presentation/storage concepts were conflated by the author |
| Mixed live/latched overscan is the sole cause | Mixed controls allow live rendering past the latched centered image | Stable modes already fail at U; cannot be the sole cause | Real software/control histories and resulting values |
| Several changes combined | Allocation/origin transition, temporary live gate, PPU backport and later clear loop have separate introducing commits | Does not supply a unique correction or hardware specification | Donor backport contract and acceptable baseline/reference changes |

## 14. Documented facts vs inference

**HISTORICAL SOURCE OBSERVATION — explicit intent:**

- The 2011 release message identifies ongoing non-overscan border clearing.
- The 2012 source comment and message identify vertical centering.
- The May 2016 message identifies fixed 512×480 output for high-resolution cursors and simpler sprite handling.
- The June 2018 messages discuss border symmetry, line-zero omission, presentation tradeoffs, and reverting to 224/240 height.
- The July 2019 message identifies overscan-masking improvements, but does not justify losing backing capacity.
- The September 2019 message identifies a PPU backport.
- The October 2019 message/comment identifies frame-event synchronization intent.
- The December 2019 message identifies the overscan-transition visual defect being addressed.

**SOURCE OBSERVATION / HISTORICAL SOURCE OBSERVATION:** Array declarations, pointer expressions, callback dimensions, gates, rename continuity and before/after diffs are directly inspectable. They establish the native mismatch and its historical transitions.

**INFERENCE:** Centered 224-line content in a 240-pair presentation is coherent; preserving callback-relative coordinates while removing unpresented backing capacity exposed existing late stores. Later widening and clearing independently exceed the small array.

**UNKNOWN:** No inspected message says the author knowingly intended out-of-array writes, reliance on light-table adjacency, a sacrificial row, or a particular correction. A blank/zero supplied value does not make the store defined.

The existing [P0 report](../experiments/EXP-004/P0_OUTPUT_BOUNDS_REPORT.md) records zero-gap output/lightTable layout for its tested compiler and layout-sensitive effects in a defined-storage fixture. **UNKNOWN:** Exact native runtime consequences remain unknown. This archaeology adds source/history evidence, not new runtime evidence.

## 15. Remaining unknowns

- The exact higan donor revision and original execution/storage contract behind the September 2019 V=240 backport.
- Whether V=240 cycle work is necessary for native timing or execution-visible side effects independently of sample storage.
- Hardware-grounded treatment of late lines and mid-frame overscan/interlace changes; historical UI-height choices are not a hardware specification.
- The intended lifetime and contents of unpresented samples, including border initialization and old-field retention.
- Why the transition clear includes pair 240 despite its introducing revision's 480-row allocation.
- Exact optimized native effects, compiler sensitivity, ROM reachability and whether any valid later sample changes in the real emulator.
- Complete pointer-formation requirements over NTSC/PAL fields, including scanlines that perform no Screen stores.
- Reset, serialization/load, rewind/run-ahead and frame-event interactions of any future candidate.
- Whether an upstream correction or discussion exists beyond the locally available history.

## 16. Readiness for candidate correction

**INFERENCE: Yes, a separately scoped candidate-correction design is now justified. Implementation or selection of a correction is not justified by archaeology alone.**

The established contract is strong enough to constrain design: the normal cycle-PPU callback is 512×480; centered non-overscan content occupies rows 16..463; field placement and horizontal sample order are explicit; backing storage historically exceeded presentation; and concrete source revisions explain how late destinations lost valid backing.

The inconsistent aspect is **the relationship between permitted native pointer/store/clear destinations and the actual allocated object**, not an unexplained need to change presentation size. A design must address all three producers of invalid destinations—scanline pointer construction, Screen stores, and transition clearing—while distinguishing execution work from presentation storage.

It must also account for live/latched control combinations and callback timing. Restoring an old gate or matching an old allocation cannot be declared correct solely because it existed historically. No buffer size, cutoff, clamp, suppression, or other repair is selected here.

**UNKNOWN:** A candidate's behavioral correctness, deterministic-reference impact, supported-toolchain behavior and passivity implications remain unvalidated.

## 17. Recommendation for the next stage

**INFERENCE:** Commission a separate native-baseline **contract and candidate-design review** using this history. Its smallest unresolved source question is the need for V=240 cycle work and the donor scheduler's storage assumptions. Identify the exact donor revision if available; otherwise retain that uncertainty and derive explicit requirements from the current cycle call graph and execution-visible state.

That review should state the intended boundaries for storage, visible presentation, execution and clearing, including stable/mixed overscan, both fields, NTSC/PAL late pointer formation and frame-event timing. It should compare candidate approaches against those requirements and specify the evidence needed before choosing one. Any controlled candidate implementation and validation require a later task's explicit authorization.

The eventual native-baseline disposition must state what baseline is accepted for continued experiments and whether deterministic references require revalidation. This Phase 1 report does not make that disposition.

**EXP-004 color-math provenance implementation remains unauthorized.** It remains blocked until the separate native-baseline investigation is completed, its disposition is documented, and implementation is explicitly re-authorized. No emulator/core is selected for GTC-HD, and no architecture decision is accepted by this report.
