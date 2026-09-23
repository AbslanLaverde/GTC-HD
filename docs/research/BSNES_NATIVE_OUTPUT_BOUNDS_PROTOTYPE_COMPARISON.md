# bsnes Native Output Bounds — Controlled A/B Prototype Comparison

Date: September 23, 2026.

**Both candidates: IMPLEMENTED FOR PROTOTYPE / HOST-TESTED / SUPPORTED DESKTOP BUILD PASSED.**

**Neither candidate is VERIFIED or accepted. No winner or corrected baseline is selected. EXP-004 remains blocked. No ROM, commit, push or ADR occurred.**

Evidence labels distinguish **SOURCE OBSERVATION**, **HOST-TEST EVIDENCE**, **BUILD EVIDENCE**, **INFERENCE** and **UNKNOWN**. Host equivalence below is limited to the controlled fixtures and the defined-storage baseline model.

## 1. Objective and baseline

Compare retention versus omission of unpresented late samples while preserving native PPU execution, valid presentation stores and the 512x480 callback.

Read alongside the [archaeology](BSNES_NATIVE_OUTPUT_BOUNDS_ARCHAEOLOGY.md), [candidate review](BSNES_NATIVE_OUTPUT_BOUNDS_CANDIDATE_REVIEW.md), and [EXP-004-P0 report](../experiments/EXP-004/P0_OUTPUT_BOUNDS_REPORT.md).

**SOURCE OBSERVATION:** Both worktrees began clean at upstream bsnes baseline U, `7d5aa1e656b9171524d01b1b22917197d8121cb4`, subject `fix horizontal offset in high-resolution offset-by-tile mode`. Their HEADs remain U; the prototypes are uncommitted working changes.

| Candidate | External research checkout | Branch |
| --- | --- | --- |
| A | `experiments/bsnes-native-output-bounds-a/` | `gtc-hd/native-output-bounds-candidate-a` |
| B | `experiments/bsnes-native-output-bounds-b/` | `gtc-hd/native-output-bounds-candidate-b` |

All source/test paths below are relative to the indicated external checkout. Those checkouts are experimental research source, not production GTC-HD source. The documentation repository began clean at `4ce822b0be73a1bae3404fb5897cdd7450bbf2d3`.

## 2. Candidate A exact design

**SOURCE OBSERVATION:** `bsnes/sfc/ppu/ppu.hpp` declares `uint16 output[512 * 496]`: **253,952 entries / 507,904 bytes**, valid indices 0..253,951. The extra 8,192 entries cost 16,384 bytes relative to U.

The capacity follows the exact current store envelope: V=240 plus seven centered pair rows reaches pair 247, requiring 248 pairs of 1,024 entries. This covers both non-interlace rows and either interlace field. It is not a claim that 496 rows should be displayed.

All existing logical Screen stores for V=1..240 remain. Pair 240 remains part of transition clearing as **unpresented backing-only storage**. Power/reset initializes the entire backing array. No framebuffer or tail data is added to serialization.

No-store-line pointers are handled independently, so the allocation does not need to cover NTSC/PAL field-end pointer offsets. A historical 512x512 allocation is neither selected nor relied upon.

## 3. Candidate B exact design

**SOURCE OBSERVATION:** The unchanged declaration remains `uint16 output[512 * 480]`: **245,760 entries / 491,520 bytes**, valid indices 0..245,759.

Screen performs native below/above and brightness computations, then stores only when both calculated destination rows belong to the array. Current geometry is aligned to complete 1,024-entry pairs, with either two rows or one aliased interlace row; the predicate therefore retains every currently valid store. It does not discard valid bottom-border zero stores based on live vdisp.

Invalid destinations are neither clamped, wrapped nor redirected. Transition clearing retains pair rows **1..7 and 232..239**. Pair 240 is rejected as an integer range before forming its pointer.

## 4. Files changed per candidate

| Source file | A | B |
| --- | --- | --- |
| `bsnes/sfc/ppu/ppu.hpp` | Exact store-envelope allocation and explanation | Unchanged |
| `bsnes/sfc/ppu/screen.cpp` | Integer eligibility, nullable cursors, computation separated from assignments | Identical change to A |
| `bsnes/sfc/ppu/main.cpp` | Explicit transition-clear extent check | Identical change to A |
| `bsnes/sfc/ppu/ppu.cpp` | Initialize actual array extent | Identical change to A |

Both also add identical `tests/native-output-bounds/run-tests.py`, `native-fixture.cpp`, `README.md`, and `.gitignore`. The ignore file covers only that test family's generated `build/` directory. No other native source or existing experiment test is changed.

The three shared changed C++ files are byte-identical between candidates. Their behavior differs through the output array extent, keeping the comparison narrow.

| Working-source SHA-256 | A | B |
| --- | --- | --- |
| `main.cpp` | `601d66427a8fe309e9a9e1e8b9b34157254dfa44ffea20f12b75333ed966efbc` | Same |
| `ppu.cpp` | `e07f479d7d3699a0d187dde7ee6010a31e8bd4007bb80fdd0a2d9c7de4068e09` | Same |
| `screen.cpp` | `c77ca6043d9a8593fe556041216b0220db0bd63239125d0f720177a7ce66c33b` | Same |
| `ppu.hpp` | `45991260ad9849acbba9e9694dfc6da2ffa21d19190e71ec36b664c4329dbf0d` | `6388b4458d49113ed0f827a9da324caed838879cc5815928381f32fa2af437e6` |

These fingerprint the retained working-file bytes, including their line endings; they are not new commit identities.

## 5. Pointer-safety strategy

**SOURCE OBSERVATION:** Screen::scanline sets both cursors to null, then considers pointer formation only for V=1..240. It computes row offsets as integers using the unchanged centered/field geometry and checks each complete 512-sample span against the actual array extent before adding any offset to output.

Screen scanline math and palette initialization execute on every native scanline, including V=0 and V>240. No V<vdisp render gate or V=240 pipeline skip is introduced.

For an eligible row, exactly 512 increments advance each cursor to its row end, which remains within the array or exactly one-past. For an ineligible row, neither cursor is formed or incremented. The unchanged V=0 return still precedes sample computation/stores.

The transition clear independently checks `(y + 1) * 1024` against array capacity before constructing the fill pointer. Screen eligibility is not used as a substitute for clear bounds.

**INFERENCE:** This proves the relevant pointer/store bounds for the reviewed native scheduling and placement domain. It is not a proof of whole-emulator C++ safety or arbitrary corrupted save-state inputs.

## 6. Storage/clear policy

| Operation | A | B |
| --- | --- | --- |
| Callback | 512x480, pitch 1,024 bytes, scale 1 | Same |
| Non-overscan placement | +7 pair rows | Same |
| Logical late Screen stores | Retained in defined backing through pair 247 | Omitted outside presentation |
| Transition clear | Pair rows 1..7 and 232..240 | Pair rows 1..7 and 232..239 |
| Transition pair 0 and 8..231 | Preserved | Preserved |
| Power/reset | Zero all 253,952 entries | Zero all 245,760 entries |
| Native framebuffer serialization | None | None |

Pair 240 clearing is a deliberate storage-policy difference. A's later pairs 241..247 are not added to the transition loop. Callback geometry, cropping, blur and controller-overlay code remain unchanged.

## 7. V=240 execution preservation

**SOURCE OBSERVATION:** Everything in PPU::main after the transition-clear block, including frame latches, scanline hooks, cycle dispatch, OBJ fetch and timing remainder, matches U. BG, Mode 7, OBJ/OAM, mosaic, window, counters, CPU synchronization code and native below/above/color-math methods are unchanged.

The native sequence remains below, above, first brightness lookup, first B/A chained store if eligible, second brightness lookup, second B/A chained store if eligible. Brightness lookups remain outside store eligibility. No native framebuffer readback or semantic observer is added.

**HOST-TEST EVIDENCE:** Native cycle-method execution, state payloads and synchronization-opportunity counts match the safe U model in the tested scenarios. The fixture records opportunities; it does not execute a real CPU or coroutine scheduler.

## 8. Test fixture design

The identical runner in either candidate compares three models:

- **U:** original native methods and PPU declaration, with only the test output extent enlarged to 512x640. This safely covers even conservative field-end pointer formation. It does not execute U's original undersized output subobject or model its native undefined behavior.
- **A/B:** candidate methods and their actual output array extents.

The fixture includes actual native PPU/subcomponent declarations, scheduler, BG/Mode 7, OBJ/OAM, window, mosaic, Screen, counters and PPU serializers. Complete native constructor, power, step, refresh, video-mode and CGRAM methods are extracted without body rewrites. Host thread creation, bus registration, deterministic random input, CPU coroutine boundary and presentation receiver are controlled substitutes.

Each model runs at `-O0` and `-O3`, with both original methods and a generated test-only tracing copy of Screen: **12 successful executables**. Trace hooks check below-before-above and first lookup/stores before second lookup, including suppressed destinations. The C++17 native chained assignment is retained and source-checked for B-before-A assignment ordering.

Portable invocation from a candidate checkout, with an existing compiler on PATH or selected by `CXX`:

```text
python tests/native-output-bounds/run-tests.py --candidate-a <CANDIDATE_A> --candidate-b <CANDIDATE_B> --run phase3-03
```

Use a fresh name for a repeat. Toolchain: **Python 3.12.9**, **MSYS2 UCRT64 g++ 16.2.0 (Rev3, Built by MSYS2 project)**. Compile options include GNU C++17, `-O0`/`-O3`, `-g`, `-Wall -Wextra -Werror`, `-fno-access-control`, system-header treatment for upstream headers, and explicit parentheses/sign-comparison warning suppression. Native included implementations locally suppress misleading-indentation, unused-variable and maybe-uninitialized warnings. No native warning-repair changes were made.

Runner SHA-256: `c81136e1fdef084198c68a089571d0a053f9896c5cf02b7dd5361f2d2586cd6f`.
Fixture SHA-256: `a0e5141030d560b3ad9b848a440f74949b88edd6b5fb471e66f906490b9d6c54`.

## 9. Geometry/bounds results

**HOST-TEST EVIDENCE — per successful executable:**

| Check | Count / scope |
| --- | --- |
| Native scanline geometry | 4,596 cases: both regions, overscan states, interlace states, fields, V through ordinary field end |
| No-store scanline cases | 756, including V=0 and V>240 |
| Native counter progression | Eight complete fields across NTSC/PAL and interlace on/off |
| Screen/color cases | 1,536 |
| Pipeline scenarios | 84, plus two extra forced-blank/time-over witness cases |
| Transition combinations | 16 |
| Callback checks | 82 |

PAL interlace field 0 reaches V=312. Native counter checks also cover NTSC's 1,360-clock line and PAL's 1,368-clock line. Pointer bases, row aliasing and post-store cursors agree with an independent row-coordinate oracle. No candidate pointer is constructed on no-store lines.

Per-element destination/sentinel checks total **1,557,233,664 for A** and **1,507,000,320 for B** in the geometry/Screen sweep. These counts include repeated checks of unchanged array elements; they are not counts of unique pixels or game frames.

## 10. Valid presentation comparison

**HOST-TEST EVIDENCE:** Every byte of each emitted presentation stream matches U, A and B, across both optimizations and both tracing profiles. Every controlled Screen case also checks its entire output array against expected samples and unchanged sentinels, so non-target writes and opposite-field changes fail the fixture.

The streams are compared directly before hashing; equality is not inferred only from matching hashes.

| Equal stream across all 12 runs | Bytes | SHA-256 |
| --- | --- | --- |
| Presentation | 58,867,712 | `2dd1e3030a36dedb7b86542a4baa3b835c3de2f2aa52d815b9e366e7cbb0bbe6` |
| Logical native state | 7,538,570 | `43127ca951178b5d5d7d09f446bcc69515da9464f8b8f8dfd241c665f265c515` |
| Screen IO/math and CGRAM-address latch | 11,796,480 | `0de76830b0eb3ef88286aad1dc2148c1d30f2c26ceb0b0987b6e59f44b68b374` |

These are synthetic host-evidence fingerprints, not ROM framebuffer reference hashes.

## 11. Deliberate tail difference

**HOST-TEST EVIDENCE:** U's safe model and A each retain **663,552 unpresented sample-target assignments** in the geometry/Screen checks; B retains **zero**. These count logical row targets, including aliased interlace assignments, rather than unique tail elements. Per-element checks confirm the supplied values in A's valid backing. B leaves every non-target presentation element unchanged.

The native refresh callback remains 512x480 for all models. A's pair-240 transition clear is also defined and retained; B forms no pair-240 clear pointer and performs no such clear. These expected differences do not count as comparison failures.

## 12. OBJ/rangeOver witness

**HOST-TEST EVIDENCE:** Eighteen V=240 witness cases cover live/latched overscan and interlace/field combinations, plus initially false timeOver and forced blank.

In the unblanked constructed state, evaluation counts **33 eligible OBJ entries**, raises rangeOver, preserves the expected OAM latch, and leaves tileCount zero on the native no-tile-read fetch path. The controlled priority-rotation case latches firstSprite=11 before reset, finishes evaluation with OAM latch=43, and resets OAM address/firstSprite to 84/21 when live overscan places vdisp at 240; otherwise they remain 44/11.

Initially true timeOver stays true; initially false timeOver stays false. Forced blank prevents evaluation/rangeOver in its case. Clock advancement and two-clock synchronization opportunities match the safe model. Storage policy changes none of these observations.

This is native-method evidence under constructed state, not a hardware claim about V=240.

## 13. Mixed-control results

**HOST-TEST EVIDENCE:** All four live/latched overscan combinations pass. The Screen sweep includes every V from **233 through 239**, plus V=1,224,225,232,240.

For latched-off/live-on active samples, **28,672 CGRAM access checks** verify that native Screen palette activity updates the latch used by native readCGRAM during active H timing. A retains the resulting out-of-presentation samples; B omits their destinations while producing equal math/latch state.

Four pipeline histories also change live overscan and live interlace at H=400, enter forced blank at H=800, and leave it at H=1000 through the fixture's synchronization hook. They preserve latched placement and yield matching presentation/state. This directly mutates the corresponding live controls and calls native updateVideoMode; it is not a CPU-executed SETINI bus transaction.

## 14. Interlace results

**HOST-TEST EVIDENCE:** Both field placements and A/B cursor aliasing pass. Non-interlace stores both rows; interlace writes only its selected row and leaves the opposite row's sentinels intact. OBJ interlace is enabled/disabled in the pipeline scenarios. Transition tests clear both rows of each selected pair, preserve pairs 8..231, and change the live-to-display interlace latch at V=0.

Native V=128 timing sampling and field-length progression are exercised separately. Some constructed PAL V=312 pipeline cases intentionally cover independent control combinations beyond the ordinary field table; ordinary counter progression is verified in the geometry/counter sweep.

## 15. Screen/math/latch results

**HOST-TEST EVIDENCE:** The 1,536 Screen scenarios cover low resolution, modes 5 and 6, pseudo-hires, forced blank, every brightness level, addition/subtraction and halving configurations, live/latched controls, fields, and carried math across each row.

Expected supplied samples are calculated by replaying native below/above from the same math/latch state before the actual run. Each actual result, palette latch and carried math is checked, and comparison streams match all three models. The tracing profile records **786,432 brightness lookups** and **229,376 palette calls** in this sweep; first-sample stores precede the second lookup when destinations exist.

Low-resolution slots duplicate above output; hires/pseudo-hires preserve below/above slot order. No color-math provenance infrastructure is implemented.

## 16. Initialization/reset/serialization results

**SOURCE OBSERVATION:** Native PPU and counter serializer files and Screen declaration remain identical to U. Framebuffer, tail, lightTable and cursor pointers remain outside the native serializer payload.

**HOST-TEST EVIDENCE:** The fixture's native PPU field payload is **72,982 bytes** for its configured VRAM/state domain, equal across U/A/B. This is not the size of a full-system save state. Logical state comparisons include native OBJ, BG, window, Screen, latches, counters, clocks and controls, plus temporary BG pixels and synchronization counts. Raw pointers, allocation addresses and framebuffer/tail contents are excluded.

A field-serialization round trip reproduces the saved payload after deliberate state mutation. The next scanline reconstructs the correct cursors. Both native power(reset=false) and power(reset=true) initialize the full respective candidate array, then reconstruct null V=0 cursors on scanline entry. Callback geometry remains fixed.

**UNKNOWN:** Arbitrary mid-line coroutine-stack restoration, full-system load, rewind and run-ahead correctness are not tested. These results do not transfer save-state compatibility to a new binary automatically.

## 17. Sanitizer/guard evidence

**HOST-TEST EVIDENCE:** Existing UCRT64 link probes fail for `-fsanitize=address` and `-fsanitize=undefined`: missing `-lasan` and `-lubsan`. No runtime was installed and no sanitizer-clean claim is made.

The safe baseline model has enough actual array capacity for every exercised pointer. Candidate integer eligibility is checked against independent expected geometry, real cursors and post-increments. Tests check all output elements in each controlled Screen case, pair-0 sentinels, light-table boundary sentinels, and the entire light table at completion. Test readback stays inside actual arrays; the original undersized native baseline is never executed.

Sentinel evidence and source bounds reasoning complement each other. Sentinels alone cannot establish absence of C++ undefined behavior in arbitrary executions.

## 18. Desktop build results

**BUILD EVIDENCE:** Both supported UCRT64 desktop builds ran only after the complete host comparison passed. Both exited **0**.

From each candidate checkout in the existing UCRT64 environment:

```sh
make -j4 -C bsnes local=false
```

Toolchain: g++ 16.2.0 (Rev3, MSYS2), GNU Make 4.4.1. Native defaults select the desktop target, application binary, performance (`-O3`) build and OpenMP; `local=false` disables `-march=native`. No dependencies were installed. Neither desktop executable was launched.

Each build reports the same **77 warning diagnostics**: 49 `-Wattributes`, 27 `-Wcast-user-defined`, and one `-Woverflow`. They occur in unchanged source, including nall BML casts and `bsnes/gb/Core/save_state.c`'s `fseek` conversion. The prototypes do not repair these warnings.

## 19. Executable fingerprints

**BUILD EVIDENCE — SHA-256 of the completed `bsnes.exe` files:**

| Candidate | Bytes | SHA-256 |
| --- | --- | --- |
| A | 7,074,994 | `4c2e3befc6d6044dc1172a8f3f56e829d30f7e979ffaa9714afc18cb824933c6` |
| B | 7,074,994 | `d338703b7b0c8efd59cf026e68e1ad03a3191f38bb09aa7a449a1690b7016d66` |

The build fingerprints identify these artifacts; equal file size does not imply equal binaries or emulator behavior.

## 20. Deviations/risks

- Initial `phase3-01` stopped at upstream warning diagnostics promoted to errors. `phase3-02` passed all six O0 comparisons, then stopped on an inherited Mode 7 maybe-uninitialized warning at O3. Local diagnostic scoping in the fixture resolved compilation without modifying that native code. Final `phase3-03` passed all twelve runs. No candidate contract assertion failed.
- CPU/coroutine/host services are modeled, so identical state streams do not establish full emulator timing, frontend or restore equivalence.
- Real methods are exercised with synthetic settings and data, not real-ROM histories. The Screen sweep is focused coverage, not exhaustive PPU register or color-math verification.
- The exact donor scheduler revision and complete hardware necessity of late execution remain unknown; this task preserves native execution conservatively.
- Historical native UB consequences remain unknown. A safe U storage model cannot predict every effect of the original undersized array or compiler optimization.
- The completed desktop builds establish integration/buildability, not runtime passivity or compatibility. Performance impact is unmeasured.

Raw logs, command records, generated models, comparison streams, manifests and summary for `phase3-03` are retained under `<OUTPUT_DIR>/phase3-03/`; desktop logs are retained as `<DESKTOP_OUTPUT_DIR>/build.log` for each candidate. These private artifacts are not public links or replacements for the durable findings here.

## 21. Comparative assessment

**INFERENCE:** Both narrowly scoped designs satisfy the tested host contract. The intended tail-persistence difference produced no observed valid-presentation or logical-state difference in these fixtures. A provides defined storage for late samples with a 16 KiB increase; B omits those unpresented stores. Neither observation establishes a preferred correction.

No historical EXP-001/002/003 measurement, evidence-producing SHA or deterministic reference was rewritten or invalidated. Their existing evidence remains attributed to its original binaries. It does not automatically validate these prototypes.

## 22. Recommendation for next stage

**INFERENCE:** Proceed, only under a separately authorized task, to controlled A/B runtime comparisons with fixed input/settings/SRAM identities and existing deterministic references. Compare candidates against each other and against preserved historical references before considering any new reference. Include timing/state evidence and targeted live-control, interlace, power/load, rewind/run-ahead and opposite-field cases; investigate differences before baseline disposition.

Do not select a winner or accept a corrected baseline from these host results. Any experiment claims transferred to a later accepted baseline need explicit revalidation.

**EXP-004 remains blocked; color-math provenance implementation remains unauthorized.** The separate native-baseline investigation still needs a documented disposition and explicit implementation reauthorization.

Protected upstream, original investigation and EXP-001/002/003/004 worktrees remain unchanged. `AGENTS.md`, `PROJECT_STATE.md`, and prior research/experiment evidence remain untouched. No ROM, ADR, commit or push occurred.
