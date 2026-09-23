# EXP-004-P0 — Native Output Destination Bounds Investigation

Date: September 22, 2026.

**Disposition — INFERENCE: STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION.**

P0 establishes the index boundary and demonstrates layout-sensitive consequences in a controlled, defined-storage host fixture. The frozen native source exceeds its declared output subobject, and the supported compiler places the light table immediately after that subobject. Destination-validity accounting can keep an observer from adding invalid accesses, but does not resolve the native accesses or their possible effect on later valid samples.

**P0 investigation completed for the documented scope; EXP-004 source implementation remains unauthorized.** No native repair, ROM run, desktop-emulator execution, EXP-004 color-math provenance implementation, commit or push occurred. The specification, original audit, AGENTS.md and PROJECT_STATE.md were not changed.

Labels distinguish **SOURCE OBSERVATION**, **HOST-TEST EVIDENCE**, **INFERENCE** and **UNKNOWN**. A host fixture with changed backing storage is not proof of native C++ undefined-behavior execution.

## Public investigation source

Public fork: [AbslanLaverde/bsnes](https://github.com/AbslanLaverde/bsnes). Public branch: [gtc-hd/exp-004-color-math-provenance](https://github.com/AbslanLaverde/bsnes/tree/gtc-hd/exp-004-color-math-provenance).

| Identity | Historical commit | Public research equivalent |
| --- | --- | --- |
| Composition baseline C | `76bdb9250befa62fcbf23fcff2ef962fe2f58215` | [f4a45d47797d4af0918768005b481f95e5ef4635](https://github.com/AbslanLaverde/bsnes/commit/f4a45d47797d4af0918768005b481f95e5ef4635) |
| P0 test tip P | `94e12628b6dc9580e61fc3322be4a011328b0fe5` | [52cd72078fdc06a51ddeaa51efe943550dec795e](https://github.com/AbslanLaverde/bsnes/commit/52cd72078fdc06a51ddeaa51efe943550dec795e) |

[Compare public C → public P0 tip](https://github.com/AbslanLaverde/bsnes/compare/f4a45d47797d4af0918768005b481f95e5ef4635...52cd72078fdc06a51ddeaa51efe943550dec795e). P records the P0 tests that were uncommitted during the investigation below; the original evidence remains tied to historical C and those test sources. The public runner separately corrects the committed-tip policy: public C must be an ancestor of HEAD on the expected branch, and committed/working native bsnes source must remain identical to public C. The public P tip need not equal the native baseline.

The public branch contains the sanitized EXP-003 foundation plus EXP-004-P0 investigation tests. It **does not contain color-math provenance implementation**. **P0 bounds investigation only / implementation blocked:** the separate native-baseline investigation must be completed, its disposition documented, and implementation explicitly re-authorized. The [specification gate](SPEC.md) and **STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION** disposition are unchanged. The [publication map](../../research/BSNES_EXPERIMENT_PUBLICATION_MAP.md) distinguishes later focused publication validation from this historical host-fixture evidence; neither is ROM validation.

## 1. Question

Can EXP-004 observe native output destinations and supplied values without changing the frozen baseline, and is the inherited apparent bounds mismatch only a diagnostic accounting concern?

P0 investigates exact logical indices, native call/store gating, overscan clearing, compiler layout, controlled store effects, and the relationship between a supplied store value and framebuffer readback. It does not investigate color-math provenance or SNES hardware output geometry.

## 2. Baseline identity

**SOURCE OBSERVATION:** The experimental worktree started clean and remained at:

```text
Repository origin: https://github.com/bsnes-emu/bsnes.git
Worktree: experiments/bsnes-exp-004/
Branch: gtc-hd/exp-004-color-math-provenance
HEAD: 76bdb9250befa62fcbf23fcff2ef962fe2f58215
Subject: Implement EXP-003 composition provenance observer
```

The GTC-HD documentation repository started clean on `main` at `5723b1697fd9f3e043082fcfc669ece23e8c8191`. The root instructions, PROJECT_STATE.md, revised EXP-004 specification and source audit were read.

**HOST-TEST EVIDENCE:** The test runner checks the branch/HEAD and compares the inspected `screen.cpp`, `screen.hpp`, `main.cpp`, `ppu.hpp` and `ppu.cpp` against `git show` at the frozen baseline before executing fixtures. It also requires no changes under `bsnes/` afterward. All checks passed.

Toolchain:

- MSYS2 UCRT64 `g++.exe (Rev3, Built by MSYS2 project) 16.2.0`.
- Windows Python 3.12.9.
- C++17 builds at `-O0` and `-O3`; assertions remain enabled.

Source-relative references below identify files in the external `experiments/bsnes-exp-004/` checkout at the branch and commit above. The P0 test files were uncommitted additions described in section 5, not files in that baseline commit. `<OUTPUT_DIR>` denotes the ignored generated evidence directory; artifact filenames and run identifiers are retained without publishing its private location.

## 3. Source observations

**SOURCE OBSERVATION — native PPU declaration (`bsnes/sfc/ppu/ppu.hpp:59`):** `PPU` declares these consecutive members:

```cpp
uint16 output[512 * 480];
uint16 lightTable[16][32768];
```

The output subobject contains **245,760 uint16 samples**, valid element indices **0–245,759**, or 491,520 bytes. `PPU::refresh()` exposes this as 512×480 with 1,024-byte pitch; it does not enlarge the allocation (`bsnes/sfc/ppu/ppu.cpp:192`).

**SOURCE OBSERVATION — Screen::scanline (`bsnes/sfc/ppu/screen.cpp:1`):** Output placement uses **latched** `display.overscan` and `display.interlace`, plus the current field. It computes pointers on every scanline before the late-scanline check in `PPU::main()`.

**SOURCE OBSERVATION — PPU::main (`bsnes/sfc/ppu/main.cpp:1`):** `screen.scanline()` executes before `if(vcounter() > 240) { step(hperiod()); return; }`. Rendering cycles are present through V=240 inclusive. `cycleRenderPixel()` runs at H=58+4x for x=0–255 (render cycles: `bsnes/sfc/ppu/main.cpp:181`).

**SOURCE OBSERVATION — Screen::run (`bsnes/sfc/ppu/screen.cpp:21`):** V=0 returns before either store. Otherwise two chained assignments write sample 0 and sample 1 through lineB and lineA. Under the tested C++17 language mode, each assignment chain stores B before A. No native bound check suppresses them.

**SOURCE OBSERVATION — below (`bsnes/sfc/ppu/screen.cpp:32`) and above (`bsnes/sfc/ppu/screen.cpp:80`):** Forced blank, or live `!io.overscan && V >= 225`, makes these functions return zero. It does **not** make `Screen::run()` return. The subsequent light-table lookup and stores still occur. Live overscan and latched placement overscan are distinct.

**SOURCE OBSERVATION — overscan clear (`bsnes/sfc/ppu/main.cpp:1`):** At V=0, when old `display.overscan` is true and new `io.overscan` is false, the loop clears pair rows 1–7 and 232–240 inclusive, each containing 1,024 samples.

## 4. Exact index arithmetic

**SOURCE OBSERVATION, expressed as integer arithmetic:** Let:

```text
N = 512 * 480 = 245760
O = latched display.overscan (0/1)
I = latched display.interlace (0/1)
F = field (0/1)
x = composition position 0..255
s = horizontal sample slot 0 or 1

pairY = V + (O ? 0 : 7)
A = 1024 * pairY + (I && F ? 512 : 0)
B = A + (I ? 0 : 512)

indexA(x,s) = A + 2*x + s
indexB(x,s) = B + 2*x + s
```

Horizontal slot 0 uses offsets 0,2,…,510; slot 1 uses 1,3,…,511. Each line's nominal range is base through base+511. Maximum index is `max(A,B)+511`.

In the ordinary scheduler path, stores are attempted only for **1 ≤ V ≤ 240**. For V=0 or V>240, the CSV reports no attempted-store maximum, while retaining nominal pointer/base arithmetic.

**INFERENCE:** Classify the integer offset before forming any observer pointer:

- `0 <= index < N`: inside the declared array.
- `index == N`: exactly at the end, **not a valid element**.
- `index > N`: beyond the end.

A one-past pointer can be formed but not dereferenced. Pointer arithmetic beyond one-past is itself outside the native array's permitted pointer range, even on a scanline with no stores. Integer accounting must therefore not derive its answer by first subtracting or dereferencing potentially invalid native pointers.

**HOST-TEST EVIDENCE:** The fixture computes these integers before evaluating the native scanline method against an oversized safe array. Actual fixture line pointers agree with the calculated bases. A separate Python row-coordinate oracle (`rowA=2*pairY+fieldOffset`, `rowB=rowA or rowA+1`, 512 columns) cross-checks the compact matrix.

## 5. Focused test method

**HOST-TEST EVIDENCE:** New isolated test files are under `tests/exp004-p0`:

| File | Purpose |
|---|---|
| `tests/exp004-p0/output-bounds-test.cpp:1` | Integer matrix; actual native Screen methods against defined oversized storage; guard/table effects; supplied-value assertions; extracted native clear condition/loop |
| `tests/exp004-p0/layout-probe.cpp:1` | Actual native PPU header ABI offsets; creates no PPU and performs no rendering |
| `tests/exp004-p0/run-tests.py:1` | Baseline pinning, source extraction, builds/runs, independent matrix cross-check, profile/result comparisons and evidence retention |
| `tests/exp004-p0/README.md:1` | Reproduction and interpretation limits |
| `.gitignore` | Ignores only this test directory's `build/` output |

The guarded fixture changes **test storage**, not native source: `output` is a pointer into one oversized `std::vector<uint16>` array. A table view gives native `lightTable[level][color]` syntax access to another region of the same array. Every executed pointer, load, store and test assertion readback remains within that single real allocation. The logical N-element output boundary is not a smaller C++ array subobject in this model.

The fixture uses the actual `screen.hpp` and original `screen.cpp`, a synthetic PPU with deterministic state, an inert EXP-003 observer, and the extracted native light-table initialization. It does not run CPU/BG/OBJ emulation or a ROM. Native Screen code still performs its own palette resolution, skip checks, below/above order and stores.

Two safe storage models are compared:

1. **Adjacent table:** light table begins at logical offset N.
2. **Inserted diagnostic gap:** 16,384 sentinel words lie between logical output and the table.

This is a controlled model of layout sensitivity. It is **not** a native PPU layout change and does not reproduce native subobject undefined behavior.

The separate layout probe includes the **unmodified complete native PPU declaration**, uses GCC's conditionally supported `offsetof` on this class with `-fno-access-control`, and constructs no PPU. Access-check suppression changes compilation access rules, not member layout.

A second generated **test-only copy** of `Screen::run()` splits each existing lookup/store expression into a typed supplied-value local, the same chained store, and a capture of that local. It does not inspect output memory or record color-math provenance. The original and supplied-value variants are compared at both optimization levels.

Reproduction from repository root (the Python version recorded above on PATH); `run-03` identifies the recorded run:

```powershell
cd experiments/bsnes-exp-004
python tests/exp004-p0/run-tests.py run-03
```

Use a fresh evidence name when repeating; the runner refuses to reuse an evidence directory. All compiler/executable commands and exit codes are retained in `<OUTPUT_DIR>/run-03/commands.json`. Representative compile settings are `-std=gnu++17 -Wall -Wextra -Werror -O0` or `-O3`; native Screen parentheses/sign-compare warnings are explicitly suppressed. The layout probe treats upstream headers as system headers and suppresses the conditional-offset warning.

**HOST-TEST EVIDENCE:** Final `run-03` exited 0. Initial `run-01` stopped at upstream header warnings under `-Werror`; `run-02` passed O0 fixtures but stopped at an O3 nall string-formatting warning. The final fixture prints SHA bytes directly, avoiding that formatting helper; no native code was changed or warning-repair patch applied. Those attempt logs remain local.

## 6. Tested matrix

**HOST-TEST EVIDENCE:**

| Check, per successful executable | Coverage |
|---|---|
| Integer/scanline-pointer matrix | V=0–311 × 2 latched overscan states × 2 interlace states × 2 fields = **2,496 cases** |
| Individual logical targets | Every x=0–255 × both horizontal slots × both line targets = **2,555,904 checks** |
| Compact exported matrix | V=0,1,224,225,232,233,239,240,241 × the eight placement combinations = **72 rows** |
| Guarded native Screen runs | Nine V values × latched/live overscan × interlace × field × forced blank × lowres/mode5/mode6/pseudo-hires × two storage layouts = **2,304 cases** |
| Out-of-logical-range store cases | **512**, including **384** where below/above return zero |
| Overscan transition checks | Old/new overscan 00,01,10,11 × two layouts = **8** |
| Build/run variants | O0 original, O0 supplied-value, O3 original, O3 supplied-value |

These four executables produced identical matrix/store/layout-effects CSVs and runtime signatures. Each fixture comparison also checks the whole backing array against the expected sequence of actual lookup-return values, so unplanned physical writes within the allocated model are detected.

The [compact machine-readable matrix](P0_OUTPUT_BOUNDS_MATRIX.csv) includes V, latched overscan, interlace, field, pairY, A/B bases and their classifications, horizontal offset range, nominal maximum, attempted-store maximum, declared size, native-store gating and in/out result. A `no_store` row can still contain invalid native pointer arithmetic; it is not a declaration that the native pointer construction is valid.

Matrix SHA-256:

```text
01470EC0A0396BFE1B98408DF5EDCD35855B984E8FF3FE1BF2250EF327F8272A
```

## 7. First/last valid destinations

**SOURCE OBSERVATION / HOST-TEST EVIDENCE:** The logical storage boundary and tested native-method matrix agree. First active and last fully in-range scanlines are:

| Latched overscan | First active V / pairY | Last in-range V / pairY |
|---|---|---|
| Off | 1 / 8 | **232 / 239** |
| On | 1 / 1 | **239 / 239** |

Within either last valid pair row:

| Interlace | Field | A range | B range | Post-line cursors |
|---|---|---|---|---|
| Off | Either | 244,736–245,247 | 245,248–245,759 | A=245,248; B=N |
| On | 0 | 244,736–245,247 | Same as A | A=B=245,248 |
| On | 1 | 245,248–245,759 | Same as A | A=B=N |

The final B/field-1 cursor exactly at N is a permissible one-past position **after** the last valid store; using it for another store would not be valid.

At the first active pair, substitute base 8,192 with overscan off or 1,024 with overscan on. Non-interlace B adds 512; interlace field 1 adds 512 to both. V=0 can produce in-range base arithmetic but performs no Screen stores.

**INFERENCE:** Field 0 interlace's last used index is 245,247, while field 1 can use 245,759. This reflects which row is written in that field, not a different allocation bound.

## 8. Out-of-range cases

**SOURCE OBSERVATION / HOST-TEST EVIDENCE:** Every entry below is at **x=0, horizontal slot=0**. Non-interlace field does not affect placement.

| Overscan | Interlace | Field | First invalid V | pairY | A index | B index | First invalid store in native execution order |
|---|---|---|---|---|---|---|---|
| Off | Off | 0 or 1 | **233** | 240 | **245,760 (N)** | **246,272** | B at **246,272**, then A at N |
| Off | On | 0 | **233** | 240 | **245,760 (N)** | **245,760 (N)** | B then A at **245,760** |
| Off | On | 1 | **233** | 240 | **246,272** | **246,272** | B then A at **246,272** |
| On | Off | 0 or 1 | **240** | 240 | **245,760 (N)** | **246,272** | B at **246,272**, then A at N |
| On | On | 0 | **240** | 240 | **245,760 (N)** | **245,760 (N)** | B then A at **245,760** |
| On | On | 1 | **240** | 240 | **246,272** | **246,272** | B then A at **246,272** |

The distinction between the smallest invalid offset N and the first executed invalid store matters: in non-interlace the B store at N+512 occurs first. Slot 1 uses each index plus one; subsequent x adds 2x. No horizontal sample on these invalid pair rows returns into range.

**SOURCE OBSERVATION / HOST-TEST EVIDENCE:**

- Overscan off attempts invalid stores on **V=233–240**. The largest index is **253,951** in non-interlace or interlace field 1; interlace field 0 reaches **253,439**.
- Overscan on attempts invalid stores on **V=240**. The largest index is **246,783** in non-interlace or interlace field 1; interlace field 0 reaches **246,271**.
- Each rendered line performs 1,024 assignment stores: two slots × two line targets × 256 positions. Non-interlace touches 1,024 distinct elements; interlace repeats stores to 512 distinct elements.
- Thus overscan-off late rendering attempts 8,192 stores outside the declared subobject per tested field interval; overscan-on attempts 1,024. These are address/store counts, not observed desktop runtime corruption counts.
- V=241 and later skip rendering but still execute `Screen::scanline()` first. Their pointer calculations are beyond the declared array. For example V=241, overscan off, non-interlace gives A=253,952, B=254,464 with **no stores**.

**INFERENCE:** A=N itself permits one-past pointer formation, but not a store. Non-interlace B=N+512 and field-1 adjustment already exceed the permitted pointer-arithmetic range on the first invalid line. Field-0 interlace has both pointers at N on that first line, then advances/dereferences them invalidly when rendering proceeds. Later no-store pointer construction is a related source issue, not cured by a store-validity flag.

## 9. Overscan-clear findings

**SOURCE OBSERVATION:** The V=0 old-overscan-on → live-overscan-off branch clears pair rows 1–7 and 232–240. The frame-control assignment occurs afterward.

**HOST-TEST EVIDENCE:** The fixture extracts the unchanged native condition and loop, executes it for all four old/new overscan combinations in both safe layouts, and checks every backing element. Only the on→off transition writes.

For that transition:

- Total cleared words: **16,384**.
- Words outside the declared logical output: **1,024**.
- First invalid cleared pair: **y=240**.
- Invalid destination interval: **245,760–246,783**.
- Last fully valid cleared pair: y=239, ending at 245,759.

The loop does not use interlace or field to change the range. It has the same declared-subobject boundary problem as the output stores, with a distinct trigger. In the adjacent model it clears the first 1,024 words of brightness row zero; in the gap model it clears the guard region instead.

**INFERENCE:** A fix limited to suppressing late Screen stores would not by itself address this clear loop or pointer formation. Choosing an intended storage/visible-height correction is outside P0.

## 10. Guarded-fixture and sanitizer findings

### Native ABI layout

**HOST-TEST EVIDENCE:** The actual unmodified PPU header compiled under UCRT64 GCC 16.2.0 reports:

```text
sizeof(PPU)                  = 1679136 bytes
offsetof(output)             = 131134 bytes
sizeof(output)               = 491520 bytes
offsetof(lightTable)          = 622654 bytes
gap after output before table = 0 bytes
```

The byte address immediately after output is the beginning of `lightTable` in this compiler's layout. This measurement used no native rendering or invalid access. It establishes the tested ABI's adjacency, not what an optimizer must do once source execution has undefined behavior.

### Defined-storage runtime effects

**HOST-TEST EVIDENCE:** In the guarded model, all 384 zero-return/outside cases still executed their stores. Sentinel words beyond the logical output changed when that region was a diagnostic gap. Zero returns therefore do not prevent the logical overflow.

A targeted active-overscan case used native no-math backdrop red `0x001f`, brightness 15, V=240, non-interlace. The native table supplied RGB555 `0x7c00` (31,744) to stores beyond the logical output. A later valid V=1 sample used brightness zero:

| Test-only layout | Table[0][31] after V=240 | Later brightness-zero native sample | Guard words changed |
|---|---|---|---|
| Adjacent table at N | **0x7c00** | **0x7c00** | 0; overflow region is the table |
| 16,384-word gap before table | **0** | **0** | **1,024** |

Only the model's layout changed. The active red stores reached the adjacent table in one case and sentinel storage in the other. Original and supplied-value variants agree at O0/O3.

**INFERENCE:** This demonstrates a concrete mechanism by which a destination outside the declared output can influence a later **in-range** output sample, and by which inserted diagnostic fields could receive writes instead. Restricting attention to valid destinations alone would miss that dependency.

**UNKNOWN:** This defined-storage model does not establish the native desktop compiler's actual handling of the invalid subobject access. It deliberately makes the writes legal in its enlarged allocation. O0/O3 agreement here is not proof that native undefined behavior is stable.

### Sanitizer availability

**HOST-TEST EVIDENCE:** Minimal link probes with `-fsanitize=address` and `-fsanitize=undefined` both failed: the existing UCRT64 toolchain cannot find `-lasan` / `-lubsan`. No sanitizer execution occurred and no sanitizer-clean claim is made. No compiler/runtime installation was attempted.

Guard evidence was used instead. The runner can execute a combined sanitized **defined-storage fixture** if both runtimes are available, but even that would not turn the fixture into an exact native-subobject test.

## 11. Actual runtime evidence versus source/arithmetic evidence

| Conclusion | Evidence and limit |
|---|---|
| Declared bound is N and source calculations exceed it | **SOURCE OBSERVATION**, independently checked by integer host tests |
| Native source gates stores differently from pointer construction and zero returns | **SOURCE OBSERVATION**; **HOST-TEST EVIDENCE** from the actual Screen methods in synthetic state and source-pinned scheduler bounds |
| All matrix pointer bases and supplied-value cases agree | **HOST-TEST EVIDENCE**, oversized defined storage only |
| Clear loop writes outside the logical boundary | **HOST-TEST EVIDENCE**, native condition/body in safe backing |
| Actual compiler puts lightTable directly after output | **HOST-TEST EVIDENCE**, unmodified native header ABI measurement |
| Adjacent writes can change later brightness-zero output; gap redirects them | **HOST-TEST EVIDENCE**, deliberately defined storage model |
| Native subobject accesses are outside C++ array bounds | **INFERENCE** from source-established indices and array rules; not a hardware claim |
| Exact desktop memory corruption, optimized native UB behavior or ROM reachability | **UNKNOWN**; no desktop/ROM execution and no exact-native invalid store was executed |

Final runtime signature, equal across all four fixture builds:

```text
4779f27c6ad70a0d8c5ff8967af7759c0fcf908f9787c8a1e856ec18b52517b5
```

The retained summary (`<OUTPUT_DIR>/run-03/summary.json`), command log (`<OUTPUT_DIR>/run-03/commands.json`), store matrix (`<OUTPUT_DIR>/run-03/O0-native-stores.csv`) and layout-effects CSV (`<OUTPUT_DIR>/run-03/O0-native-layout-effects.csv`) retain the execution evidence. They are host-fixture artifacts, not ROM framebuffer hashes.

## 12. Implications for EXP-004 instrumentation

**INFERENCE:** The proposed observer can calculate destination validity without dereferencing an invalid pointer: copy the scalar placement controls and maintain an integer horizontal offset for each native write slot. Use widened integer arithmetic, never pointer subtraction from a native pointer whose derivation is already outside the array.

**HOST-TEST EVIDENCE:** The test-only supplied-value variant preserves lookup/store order and captures values without framebuffer readback:

```cpp
// TEST-ONLY sketch; not implemented in native Screen:
const uint16 supplied0 = lightTable[brightness][firstResult];
*lineA++ = *lineB++ = supplied0;
captureSupplied(0, supplied0);

// Only after the first lookup/stores:
const uint16 supplied1 = lightTable[brightness][aboveResult];
*lineA++ = *lineB++ = supplied1;
captureSupplied(1, supplied1);
```

The generated fixture actually uses the original native expressions and a typed uint16 local. This matters because retaining a proxy/reference or delaying a lookup could read a different value. The two values, lookup counts, output/guard/table contents and signatures matched the original method in all documented cases.

**INFERENCE:** If later authorized, keep diagnostics outside the PPU native layout, copy the supplied local, record integer destination and validity, and preserve native lookup/store sequencing. A/B aliases and out-of-range logical destinations must remain explicit. The observer must not suppress a store, redirect it, resize output, move lightTable, or add output readback.

This establishes a viable **observation technique in the fixture**, not authorization to instrument an unresolved native-UB path. The original native stores would still be present.

## 13. Whether logical destination validity is sufficient

**INFERENCE:** It is sufficient to explain where a native store intends to go and to prevent **additional observer** invalid reads or fabricated callback coordinates.

It is **not sufficient** to establish passive native execution or isolate later valid samples from the bounds issue:

- the baseline still performs out-of-subobject stores and beyond-end pointer arithmetic;
- the measured adjacent object is the light table consumed by later valid rendering;
- the safe model demonstrates a later valid output changing through that table;
- changing layout can redirect the same writes into diagnostic storage;
- callback hashes cover the declared output, not arbitrary adjacent state.

No current recommendation should imply that an `inRange` flag repairs native execution. Existing EXP-003 equality remains evidence for its tested conditions; it did not exercise or settle all of these state/layout cases.

## 14. Whether a native baseline repair appears necessary

**INFERENCE:** The source has a native bounds defect, rather than only an observer coordinate mismatch. Achieving defined native C++ execution appears to require a separately scoped correction of the store/pointer/clear boundary or storage design. P0 does not select that correction.

Of the requested classifications:

- **A — only observer accounting:** not supported.
- **B — native UB with stable native behavior in the tested compiler:** source UB is supported by the index analysis, but the native stability part is **UNKNOWN**. Only the defined fixture was run at O0/O3.
- **C — native bug requiring separate baseline correction:** a separately scoped native investigation/correction appears warranted; exact repair, intended geometry and output/reference effects are not established.
- **D — most precise current description:** source bounds defect, measured zero-gap native ABI, and layout-dependent effects in a defined host model, with exact native runtime consequences still unverified.

Any repair must be independently authorized and reviewed. Do not silently enlarge output, clamp indices, stop stores or change the clear loop in this experiment. Reconsider/regenerate deterministic references if the baseline changes.

## 15. Risks and unknowns

- **UNKNOWN:** Exact optimized desktop effects and cross-compiler behavior of the native invalid subobject accesses.
- **UNKNOWN:** Which ROM/control sequences reach nonzero late stores, and their user-visible consequences. No ROM ran.
- **UNKNOWN:** Intended native storage versus callback geometry and the correct treatment of late pointer construction and overscan clearing.
- **UNKNOWN:** Effects under untested complete emulator scheduling, save/load, platform ABI and control histories. Synthetic state combinations are not proof of ROM reachability.
- **UNKNOWN:** Hardware correctness; P0 provides no SNES hardware evidence.
- **INFERENCE:** Normal non-overscan zero stores can mask visible consequences in a common physical-layout interpretation because brightness row zero starts zero. This is not proof of safety and does not explain all active-overscan or layout cases.
- **INFERENCE:** The guarded model's enlarged array and table view remove the precise native subobject UB. Its positive mechanism evidence and native ABI measurement must not be collapsed into a claim of actual desktop corruption.
- **HOST-TEST EVIDENCE:** The fixture enumerates V=0–311 and the required nine boundary values; general integer formulas remain explicit. It is not a universal whole-emulator PAL/interlace validation.

## 16. Recommendation

**INFERENCE: STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION.**

P0 succeeded in identifying the boundary, first invalid cases, clear-loop issue, native ABI adjacency, controlled layout sensitivity and a way to copy supplied values without readback. It did not establish that adding instrumentation to the frozen native undefined-behavior path is safe.

The next task should determine the intended native output/storage boundary and evaluate a narrowly scoped correction or other justified baseline disposition, with its own authorization and deterministic-reference plan. EXP-004 color-math provenance implementation should wait for that disposition and explicit authorization.

Files added by this task:

- `docs/experiments/EXP-004/P0_OUTPUT_BOUNDS_REPORT.md`.
- `docs/experiments/EXP-004/P0_OUTPUT_BOUNDS_MATRIX.csv`.
- The five isolated test files listed in section 5.
- Ignored generated test copies, executables, CSVs and logs under `<OUTPUT_DIR>/`.

**SOURCE OBSERVATION / HOST-TEST EVIDENCE:** No tracked experimental/native file was modified. The normal desktop build does not include these new test files. The worktree remains behaviorally unmodified outside standalone test instrumentation. The frozen HEAD is unchanged; no commits, native repairs, ROM execution or EXP-004 implementation occurred.
