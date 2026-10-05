# EXP-004 — Color Math and Final-Native-Sample Provenance

**Current status: VERIFIED FOR TESTED EXP-004 CONDITIONS — 2026-10-05.**

The corrected cycle-PPU observer preserves the tested chain from BG/OBJ composition winners through native color-math operands, pre-brightness color and the values supplied to native stores. The deterministic observer-disabled and observer-enabled runs match the accepted corrected control and historical framebuffer reference byte-for-byte. This supports a bounded semantic-representation experiment; it does not establish a complete semantic frame, universal compatibility, hardware conformance or an accepted renderer architecture.

## Question and authorized baseline

Can the native main/sub winners remain traceable through clipping, color-math operands and controls, brightness conversion and the values supplied to native framebuffer stores without changing native execution?

Xavier explicitly reauthorized implementation after the completed accepted-baseline transfers. The new isolated checkout is `experiments/bsnes-exp-004-corrected/`, branch `gtc-hd/exp-004-color-math-provenance-corrected`, rooted at corrected EXP-003 commit `c929e19a8583e388b0f8bf53d2d0a796c0d91386`. Accepted experimental correction `46fa75236fa61d49d8e9424b3b44694b88aa07a9` retains 512x496 backing, pointer safety, late stores and V=240 execution with unchanged 512x480 presentation.

The [P0 stop](P0_OUTPUT_BOUNDS_REPORT.md) remains historical evidence. The [completed transfer](../../research/BSNES_ACCEPTED_BASELINE_REVALIDATION.md#resumed-transfer-results--2026-10-05) and this explicit authorization resolve its implementation gate; they do not select bsnes or accept a production renderer architecture. The [historical specification](SPEC.md), [source audit](SOURCE_AUDIT_AND_IMPLEMENTATION_PLAN.md), P0 report and [matrix](P0_OUTPUT_BOUNDS_MATRIX.csv) are unchanged. Their earlier blocked status has not been rewritten retroactively.

| Final identity | Value |
| --- | --- |
| Local source commit | `cc8d1f0d0a67b0ee523549671b9843f67c7c7534` |
| Author and committer | Xavier Laverde &lt;xavier0286@gmail.com&gt; |
| Supported build | Windows, existing MSYS2 UCRT64 GCC 16.2.0 Rev3, GNU make 4.4.1; GNU++17, O3/OpenMP, `local=false` |
| Executable size | 47,016,355 bytes |
| Executable SHA-256 | `B84CDBB52CAE47D80524CCFC2FBF5BA48FF454FC780B5B8B6ECB9DF191A6075B` |

Only this new source branch was committed locally. No push, merge, upstream modification or public-history rewrite occurred.

## Observer storage decision before validation

**SOURCE OBSERVATION / COMPILE-TIME MEASUREMENT:** the finalized owned record is 392 bytes on the existing UCRT64 compiler. Capacity is 65,536 positions, derived from 256x240 = 61,440 scheduled composition positions per ordinary callback interval plus 4,096 positions of margin. The record array reserves **25,690,112 bytes (24.5 MiB)**. The complete observer is 25,690,840 bytes. Keeping EXP-003's existing observer intact for regression adds 11,551,528 bytes, for **37,242,368 bytes combined**. The completed runtime capture used **24,084,480 record bytes**. These are diagnostic object sizes, not process working-set or production-performance measurements.

This is a material diagnostic cost, explicitly recorded before finalizing the design. Each position owns current main/sub and carried raw-main winner snapshots, three groups of native-producer origins, seven Math fields at three boundaries, and two sample descriptions. Samples refer to those shared winners by operand category rather than duplicating lineage per sample. The bounded copied carried winner remains interpretable even if its producer falls outside retained storage. A deduplicated production frame format is outside this experiment; the existing EXP-003 storage is retained to avoid changing its diagnostic behavior during the first integration.

Fields distinguish None, CurrentSub, FixedColor and CarriedMain, consumed arithmetic operands, no-math/add/subtract and applicable half state, native skip/clip/fallback, BGR555 pre-brightness result, brightness level, RGB555 supplied store value, integer A/B destinations, backing/presentation membership and interlace aliasing. Native Math histories separately track main color/permissions, sub color/transparency, and choice/half producers. No native pointers or observer fields enter serialization.

Position metadata includes epoch, attempted sequence, callback, relative frame, x/V/H/field, mode, pseudo/effective hires, live/latched overscan, latched interlace and native skip reason. Capture metadata reports retained count, capacity, saturating dropped count, overflow, unknown winners/history, requested/completed window and export/completeness. This capacity does not promise arbitrary multi-callback capture.

## Native Screen findings and observer design

**SOURCE OBSERVATION:** inspection of the corrected parent's `bsnes/sfc/ppu/screen.cpp`, `screen.hpp`, `ppu.cpp`, `main.cpp` and EXP-003 sidecars confirms the audit's semantic model. Candidate A's accepted storage policy is the expected baseline difference; no material semantic contradiction was found.

`Screen::run()` computes below, then above, then the first brightness lookup/store, then the second lookup/store. Lowres stores above twice; modes 5/6 and pseudo-hires store below followed by above. Each native store expression writes B then A, including the interlace alias case. The implementation preserves this sequence.

`Exp004::ColorMathObserver` is a fixed-capacity sidecar, disabled by default and on power/reset or serializer Load. Save/Size neither serialize it nor clear an active observation. EXP-003's producer sidecars supply owned winner snapshots through a read-only `copyPending()` handoff; no BG/OBJ producer algorithm is duplicated or changed.

Overflow preserves the retained prefix and continues updating native-producer history. Enabling/clearing starts a new lineage epoch; unexplained counter discontinuity invalidates history. Missing handoffs or unknown consumed history make a capture incomplete instead of substituting the last retained record. File export occurs after the core returns, with no file I/O in the hot PPU path. Simultaneous EXP-003/004 capture is explicitly rejected.

## Operand semantics

**SOURCE OBSERVATION:** four categories suffice; no additional category was required.

| Operand | Native meaning |
| --- | --- |
| None | No blend call for this stored sample; the result is the allowed selected color or a clipped/skipped zero. Half is not applicable. |
| CurrentSub | Above blends with the current below-selected raw color. The record's sub winner supplies its lineage. |
| FixedColor | The blend consumes the existing `fixedColor()` result, including transparent-sub fallback. It does not claim sub-screen provenance. |
| CarriedMain | Hires below blends with the previous active above-selected **raw main** color. Owned carried lineage and producer origins describe that dependency. |

Composition source and arithmetic operand are separate. A current sub winner can be unused. Priority zero triggers fixed-color fallback even if the palette color is nonzero; numeric black with a nonzero winning priority remains a usable sub operand. Retaining an independent sub winner in a FixedColor record does not label it as the consumed second color.

## Hires carry and mixed Math lifetimes

**SOURCE OBSERVATION / HOST-TEST EVIDENCE:** hires carry is bounded raw-main history, not the previous blended or brightness-converted sample. A host witness carries raw main 12 after the previous above path produced blended 15, then checks that below consumes 12. No recursive color graph is needed.

The observer tracks native producers rather than assuming record N-1 wrote every field:

- `sourceOrigin`: the most recent active above path producing raw main, main permission and math eligibility.
- `controlOrigin`: the potentially older above path that actually wrote blend choice and halve. No-math above leaves these controls unchanged.
- `subOrigin`: the last active below path producing sub color/transparency. Current below consumption also has its owned sub snapshot and after-below Math state.

Skipped paths preserve all seven Math fields. Lowres still executes below selection and above updates, so a later hires transition can consume meaningful history. Hires below uses carried permissions/choice/half with the current native add/subtract direction and fixed-color value when applicable. Above's transparent-sub fallback selects fixed color and inhibits halving; main clipping also inhibits above halving through the native permission condition.

`Screen::scanline()` performs its existing palette-0 read and initializes Math; the observer copies the completed state as `NativeScanlineSeed`. This describes bsnes. Exact hardware initialization remains **UNKNOWN**, as the native source itself warns.

## Brightness, encoding and passivity boundary

**SOURCE OBSERVATION / HOST-TEST EVIDENCE:** operands and blend results are BGR555. The native light table produces RGB555; even brightness 15 can change the integer through channel reordering. The observer captures the existing typed blend result and existing `first`/`second` lookup values immediately before the stores. It never rereads output to infer a stored value.

Native `blend()`, `paletteColor()`, `directColor()`, `fixedColor()` and Screen power helper bodies are unchanged. No extra CGRAM/VRAM/OAM reads, stateful helper calls, native PPU fields, serializer payload fields, brightness lookups or output writes were added. Scalar destination accounting does not form or subtract native pointers. Candidate A cursor formation, storage size, clearing policy and no-store-line execution remain intact.

## Host evidence and supported build

**HOST-TEST EVIDENCE:** all final required checks passed. Python 3.12.9 drove the existing toolchain. Commands use the corrected EXP-004 checkout as working directory and fresh output names; `<UCRT64_BIN>` must be on PATH and compiler temporary output must be writable.

```text
python -B tests/exp004/run-tests.py host-release-01
make -j4 -C bsnes local=false
python -B tests/exp003/run-tests.py exp004-regression-01
python -B tests/exp004/observer-window-cli-test.py bsnes/out/bsnes.exe <FRESH_CLI_OUTPUT>
python -B tests/exp004/bounds-tests.py --compiler <UCRT64_GXX> --output <FRESH_BOUNDS_OUTPUT>
```

| Check | Final result |
| --- | --- |
| Native Screen/window/passivity at O0 and O3 | 1,024 matrix cases per optimization plus focused history/lineage/lifecycle cases; PASS |
| Native constructor brightness table | All 524,288 entries against an independent channel/brightness oracle per optimization; PASS |
| Native blend arithmetic | 4,096 vectors per optimization covering addition/subtraction, saturation/borrow and native halve ordering; PASS |
| Window controller | 600-callback synthetic B/C equality; start 0/500, one/multiple/last/full windows, early termination, overflow, reset, unknown lineage, range/callback guards and export/collision failures; PASS |
| EXP-004 desktop CLI | 27 rejection cases before ROM/settings initialization, including simultaneous EXP-003/004 capture; PASS |
| Affected EXP-003 suite | Existing composition, lineage, window and frame-hash checks; 26 CLI rejections and 15 exported CSV schema checks; PASS |
| Supported desktop build | Full and final incremental builds PASS; full build emitted 77 inherited warnings; final incremental build emitted one existing BML warning |

The native fixture exercises lowres, modes 5/6 and pseudo-hires; all operand kinds; clip/math-window combinations; transparent fallback versus nontransparent black; direct-color modes 3/4/7; OBJ palette eligibility; real fetched BG/OBJ lineage; mixed-age controls; seed and lowres-to-hires transitions; V=0; midline enable; discontinuity; and overflow followed by history consumption. Literal palette 191/192 Screen inputs are distinguished from separately exercised valid native OBJ producer palettes.

Disabled/enabled comparisons cover native output, available serialized field state, VRAM-read counts, CGRAM latch and palette-call counts. Bounds-host tracing additionally checks lookup/store order. This is not complete coroutine/CPU-state equivalence.

EXP-003's original assertions and expected signatures were preserved; its two test-file edits only include/link the new observer and recognize the additional Load-only reset hook:

```text
native_composition_signature=f8952120fe226387b07fc3c6f8d1e3c931e0b44a145cc7c37b436e03810dc2f1
native_pipeline_signature=03df6a8c62befa48a4edb6f39dbe72d8c730338aedd10e80469482e698e4fe5b
```

## Candidate A regression and targeted runtime

**HOST-TEST EVIDENCE:** the unchanged accepted-baseline oracle passed for harness-only control and EXP-004 at O0/O3. Each configuration covered 4,596 geometry cases, 1,536 Screen cases, 84 pipeline cases, 16 clear cases, three restore cases and 18 witness cases; 28,672 mixed-CGRAM checks, eight counter fields, 756 no-store lines and 82 callbacks. Backing remained 253,952 uint16 entries; native serializer payload remained 72,982 bytes. The checker recorded 1,557,233,664 sample checks and 663,552 retained-tail samples per configuration.

Fixed historical streams stayed identical across all four configurations:

| Stream | Bytes | SHA-256 |
| --- | --- | --- |
| Presentation | 58,867,712 | `2dd1e3030a36dedb7b86542a4baa3b835c3de2f2aa52d815b9e366e7cbb0bbe6` |
| State | 7,538,570 | `43127ca951178b5d5d7d09f446bcc69515da9464f8b8f8dfd241c665f265c515` |
| Screen | 11,796,480 | `0de76830b0eb3ef88286aad1dc2148c1d30f2c26ceb0b0987b6e59f44b68b374` |

The EXP-004 fixture also passed 112 enabled/disabled scanline pairs (seven V values, both live/latched overscan values, interlace values and fields), with 256 captured positions per line. Full backing/state equality, palette/lookup counts and B/A store order, late backing-only indices and interlace aliases passed. Actual PPU Save/Size retained observation without changing payload; Load and power/reset disabled and cleared both observers. Available tooling did not provide ASan/UBSan; these source/guard/trace checks are not a whole-program undefined-behavior proof.

**RUNTIME EVIDENCE:** the final executable passed the existing 16-callback targeted fixture, exit 0, including all four established scenarios:

- V=240 OBJ/STAT77: overflow mask transitioned 0 to 64 and remained observable to CPU code.
- Overscan on to off: expected presentation border/transition samples matched the fixed oracle.
- Mixed live/latched overscan: CPU read at V=233, pre-read H dot 207, CGRAM bytes E0/83 and STAT77 mask 64 matched the established witness.
- Interlace smoke: field XOR 128 and expected frame samples matched.

Fixture ROM SHA-256: `7750faacfd65860b45dde5ba43d98d4ac9ac22b4d6169e4e37e2ab7b41631bb3`; settings seed: `66677a7e58d2e41d4e0f6916e2cb9a7a2e96a2363296ff9799b93eb59a9bb999`. Frame CSV: `69416871a6eaf2541a684a352c4a7e13972cb49470ccc8b0f436ca9866fd04de`; resulting SRAM: `75d6febfa8370ea0969e9ab06312552e60479803d090d44e781531e4f7932acc`. This fixture retains its established no-driver settings; the commercial-ROM comparison retains its established desktop drivers.

## Deterministic real-ROM passivity

**RUNTIME EVIDENCE:** launches used the normal desktop execution context, isolated fresh input copies and bounded execution. No launch used the diagnosed restricted-context Direct3D initialization failure as emulator evidence.

| Input/reference | SHA-256 |
| --- | --- |
| Super Mario World ROM | `D70C9C7716AD12C674FC7DD744736AA48D4D7B4237F58066BE620FDA26024872` |
| SRAM seed | `D0FF1B294B5288D1AE1421EADF5B2D38A8752B76D472FF30BED9028E25B1C5B8` |
| Settings seed | `E22FBA1B0E141499C94A25652C6A2FAEBEA27ADB8A11D4EC2E84BEDA43A8FA6B` |
| Preserved EXP-003 callback-500 composition | `c8084c47f39a9ef17b22f40f804ed30a02628f940c9caa299495f29a52381ee8` |
| Retained corrected harness-only executable | `3F1C09FC603EFD8AC29E4FBD480ACA362C981819EA50991FB9B2D9F12B70B48F` |

The corrected control source is harness descendant `13e19564bd038e3767a58b9f1f1d29b1d5f4f527` of accepted correction `46fa75236fa61d49d8e9424b3b44694b88aa07a9`; its completed normal-desktop 1,800-callback result was reused. Historical references retain their original identities. Expectations were not regenerated.

B and C used the same final EXP-004 executable and settings: cycle PPU, deterministic entropy, no input, no auto-load/rewind/run-ahead, no blur, Direct3D 9 video and waveOut audio. Both ran 1,800 native callbacks. C captured only callback 500 via:

```text
--exp001-frame-hash=<NEW_FRAME_CSV>
--exp001-frame-count=1800
--exp004-color-math-csv=<NEW_PROVENANCE_CSV>
--exp004-color-math-start-callback=500
--exp004-color-math-callback-count=1
```

B omitted the three EXP-004 options. The tracked finite driver checks input/reference hashes, restores isolated seeds, launches the executable, compares complete CSV bytes, checks lineage/sample semantics and invokes the unchanged targeted-fixture oracle:

```text
python -B tests/exp004/run-runtime.py --lab-root <GTC_HD_LAB> --exe <BSNES_EXE> --rom <ROM_PATH> --sram <SRAM_SEED> --settings <SETTINGS_SEED> --historical <HISTORICAL_1800_CSV> --control <CORRECTED_CONTROL_1800_CSV> --composition <HISTORICAL_CALLBACK_500_COMPOSITION_CSV> --dll-dir <UCRT64_BIN> --output <FRESH_OUTPUT_DIR>
```

**B = C = accepted corrected control = historical reference**, byte-for-byte across all 1,800 callbacks. All frame CSVs have SHA-256 `9BC5FF87FC19E52615CFFB334AD9AD75900F4C8F12818972C210479A857B99FB`. Both processes exited 0. **First divergence: none.** This establishes framebuffer passivity for these tested inputs, settings and interval, not arbitrary execution-state equivalence.

Final wall times were B 31.782 s, C 31.953 s and targeted fixture 1.359 s. These include desktop cadence, startup and export; they are not a production overhead benchmark or process-memory measurement.

## Real-ROM semantic evidence

**RUNTIME EVIDENCE:** callback 500 retained **61,440 records / 122,880 sample descriptions**, capacity 65,536, drops 0, overflow false, unknown current winners 0, unknown consumed history 0, completed window true and capture/export complete. Every applicable main/sub lineage field matched the preserved EXP-003 composition capture; every supplied sample passed an independent arithmetic/brightness/destination check.

| Per-sample semantic category | Observed count |
| --- | ---: |
| None / NoMath | 77,534 |
| CurrentSub | 25,440 |
| FixedColor | 19,906 |
| CarriedMain | 0 |
| Add | 45,346 |
| Subtract | 0 |
| Halved math | 0 |
| Non-halved math | 45,346 |
| Half not applicable | 77,534 |

All 61,440 positions were lowres. Main winners were BG1 11,969, BG3 22,015, OBJ 687, backdrop 22,673 and skipped 4,096. All **34,671 BG/OBJ main winners** had known lineage. Sub winners were BG2 39,087, backdrop 18,257 and skipped 4,096; all **25,440 CurrentSub sample descriptions** had known BG2 provenance. FixedColor correctly supplied its scalar operand without claiming sub lineage.

There were 57,344 active positions, 3,894 forced-blank positions and 202 non-overscan-blank positions. Transparent-sub fallback occurred at 9,953 positions / 19,906 samples. Brightness was 15 at 57,546 positions and 0 at 3,894. Of the sample descriptions, 118,784 addressed presentation storage and 4,096 addressed only valid retained backing. These count two semantic store slots per position, not every physical A/B write.

Representative slot-0 witnesses, with decimal BGR555 operands/results and decimal RGB555 stored values:

| Sequence; native position | Explanation | Consumed arithmetic | Pre-brightness → stored |
| --- | --- | --- | --- |
| 4,097; x=0, V=1, H=58 | None; known BG3 main, token 1,585, map 20,480, entry 11,352, row 17,089, character 88, source (0,1), palette 14 | No blend; raw main 12,923 | 12,923 → 28,268 at brightness 15 |
| 4,101; x=4, V=1, H=74 | FixedColor; backdrop main/sub, transparent fallback, no false CurrentSub lineage | 0 + fixed 29,587, no half | 29,587 → 20,380; A/B 8,200/8,712 |
| 7,941; x=4, V=16, H=74 | CurrentSub; backdrop main plus known BG2 sub, token 3,071, fetch H=4/V=16, map 13,123, entry 4,411, row 5,040, character 315, source (7,0), palette 70 | 0 + sub 32,661, no half | 32,661 → 22,431; A/B 23,560/24,072 |

These are real executed addition paths with a contributing second operand. All math-enabled main colors in this slice were backdrop zero; it does not demonstrate two-nonzero-color addition, saturation, subtraction or halving in the ROM. Hires, pseudo-hires, CarriedMain, clipping and direct-color branches were host-tested, not exercised by this selected callback. No alternate commercial ROM was chosen to manufacture coverage.

The first record is epoch 3, sequence 1, relative frame 0, x=0/V=225/H=58/field=1; the last is sequence 61,440, relative frame 1, x=255/V=224/H=1078/field=0. A callback interval crosses native vertical periods; it is not itself a complete ownership map of a displayed frame.

Provenance CSV SHA-256: `a7c0119e6a43f91a8d83b7e58557bfe2d4c36cfafb823508a23d5264caa3050d`; capture-summary SHA-256: `93618b2d170d9db386f0c403412222b459700aee8d7b6736553ee50db46c8731`. Raw inputs, captures and build logs remain private; source drivers and this report preserve portable reproduction instructions and conclusions.

## Deviations and remaining unknowns

No semantic deviation from the source audit was needed. The historical P0 implementation stop was resolved through the separately accepted corrected baseline, not silently bypassed or repaired within instrumentation. The owned record trades material bounded storage for independent interpretation; it is not a selected production representation.

Initial shell PATH/temp setup and fixture integration attempts failed during development. The fixture was adjusted to reuse the existing host without its unrelated test main; synthetic overflow/history and missing-handoff inputs were corrected to represent intended native preconditions. Native expectations were not weakened. A final missing-handoff guard was followed by the passing complete host suite, rebuilt executable and repeated finite runtime campaign. No framebuffer/reference or Candidate A semantic divergence was observed.

**UNKNOWN / NOT ESTABLISHED:** full CPU/coroutine-state equivalence; arbitrary state restoration during capture; all games, regions and raster transitions; complete Mode 7 lineage; runtime hires/carried-main/subtract/halve coverage; universal hardware accuracy; a complete presented-frame ownership model including other-field contents, borders and clear writes; and production memory/performance suitability. Native occlusion/provenance does not establish scene depth, persistent game-entity identity, material or lighting information.

## Product implication, disposition and next semantic boundary

**INFERENCE:** together with corrected EXP-001/002/003, EXP-004 supplies enough evidence to begin a **bounded semantic representation and replay experiment** for the tested tiled-BG/OBJ chain: fetched source → main/sub winner → consumed operands/controls → BGR555 result → RGB555 native reference sample. It does not yet justify a complete semantic-frame interface. Callback ownership and broader mode/history coverage remain concrete gaps.

**Disposition: VERIFIED FOR TESTED EXP-004 CONDITIONS.** Implementation, supported build, focused/affected host checks, Candidate A regression, targeted runtime and deterministic real-ROM passivity/semantic evidence passed. Historical P0 evidence and protected source branches remain intact. bsnes remains a research target with an accepted experimental correction, not the selected final GTC-HD core.

**Recommended next research step:** define a small offline replay experiment reconstructing captured native samples from owned provenance and controls, with explicit raster/history and presentation ownership. Add a deterministic hires/transition witness to test bounded raw-main carry end-to-end and expose what a complete presentation interval still lacks. Treat Mode 7 lineage as a separately identified gap. This recommendation does not implement or authorize a renderer, production API or new experiment.

## Exact change inventory

Source paths below are relative to the corrected bsnes checkout and identify local commit `cc8d1f0d0a67b0ee523549671b9843f67c7c7534` on the branch above. It is not yet a published source link.

| Files | Change |
| --- | --- |
| `bsnes/sfc/ppu/exp004-color-math.hpp`, `bsnes/sfc/ppu/exp004-color-math.cpp` | New bounded observer, schema, history and CSV export |
| `bsnes/sfc/ppu/exp003-composition.hpp` | Read-only pending winner handoff |
| `bsnes/sfc/ppu/screen.cpp` | Passive producer/consumer/store hooks |
| `bsnes/sfc/ppu/ppu.cpp`, `bsnes/sfc/ppu/serialization.cpp` | Include and power/Load lifecycle hooks |
| `bsnes/target-bsnes/program/exp004-color-math-window.hpp` | New bounded frontend controller |
| `bsnes/target-bsnes/bsnes.cpp`, `bsnes/target-bsnes/program/program.cpp`, `bsnes/target-bsnes/program/program.hpp` | Options, lifecycle and capture-window integration |
| `tests/exp003/composition-test.cpp`, `tests/exp003/run-tests.py` | Integration-only regression-fixture wiring |
| `tests/exp004/.gitignore`, `tests/exp004/README.md` | Ignore generated outputs and document protocol |
| `tests/exp004/native-test.cpp`, `tests/exp004/observer-window-test.cpp`, `tests/exp004/observer-window-cli-test.py`, `tests/exp004/run-tests.py` | Focused host and CLI validation |
| `tests/exp004/bounds-tests.py`, `tests/exp004/run-runtime.py` | Accepted-baseline and finite runtime comparison drivers |

GTC-HD-Lab documentation changes are limited to `AGENTS.md` (worktree authorization/current disposition), this new report and the authorized narrow `docs/PROJECT_STATE.md` update. The pre-existing edit to the native bounds runtime report was preserved byte-for-byte. GTC-HD-Lab documentation remains uncommitted; only the authorized corrected EXP-004 source commit was created.
