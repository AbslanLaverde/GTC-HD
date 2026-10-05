# bsnes Native Output Bounds — Targeted Runtime Validation and Baseline Recommendation

Date: September 23, 2026.

**Phase 4 targeted validation: PASSED FOR TESTED CONDITIONS.**

**Recommendation: Candidate A, pending Xavier's baseline decision. Neither candidate is ACCEPTED. EXP-004 implementation remains blocked and unauthorized.**

Candidate A and Candidate B each have the status:

**IMPLEMENTED FOR PROTOTYPE / HOST-TESTED / RUNTIME-TESTED FOR TESTED CONDITIONS**

## 1. Objective

Complete the bounded native-output investigation with real CPU/PPU runtime
evidence for V=240 OBJ processing, overscan-transition clearing, mixed live and
latched overscan, and both interlace fields. Preserve native execution while
comparing A's retained backing with B's presentation-bounded stores. Document the
established ordinary-game result without rerunning it, then recommend a baseline
candidate without accepting it or selecting bsnes as GTC-HD's foundation.

Labels distinguish **SOURCE OBSERVATION**, **RETAINED EVIDENCE**, **RUNTIME
EVIDENCE**, **INFERENCE**, and **UNKNOWN**. All source references below are
relative to the identified external bsnes checkout. Project authority remains
under `docs/`; the project remains Phase 0.

## 2. Prior evidence

- [EXP-004-P0](../experiments/EXP-004/P0_OUTPUT_BOUNDS_REPORT.md) established
  logical stores and transition clearing beyond the declared 245,760-entry
  output subobject. The tested layout places lightTable immediately afterward.
  A defined-storage fixture demonstrated a possible layout-sensitive effect;
  exact native undefined-behavior consequences remain unknown.
- [Phase 1 archaeology](BSNES_NATIVE_OUTPUT_BOUNDS_ARCHAEOLOGY.md) identified
  historical backing larger than presentation and the later allocation,
  scheduler and clear-boundary changes. It did not establish hardware intent
  for every late operation.
- [Phase 2 contract review](BSNES_NATIVE_OUTPUT_BOUNDS_CANDIDATE_REVIEW.md)
  separated execution, storage, presentation and clearing. Its source search
  found no intended consumer of the unpresented cycle-PPU tail.
- [Phase 3 prototype comparison](BSNES_NATIVE_OUTPUT_BOUNDS_PROTOTYPE_COMPARISON.md)
  passed all twelve host executions across O0/O3 and traced/untraced profiles,
  including bounds, state, ordering, mixed controls, interlace and transition
  checks. Both supported desktop builds passed. Those findings remain historical
  host/build evidence; this report adds runtime evidence.

No prior report, experiment result, reference hash or public/historical commit
mapping was rewritten.

## 3. Runtime identities

**SOURCE OBSERVATION:** All three runtime checkouts were clean at inspection and
remain unchanged. Native baseline U is
`7d5aa1e656b9171524d01b1b22917197d8121cb4`.

| Runtime | Worktree | Branch | Exact runtime HEAD | Prototype parent |
| --- | --- | --- | --- | --- |
| Control | `experiments/bsnes-native-output-bounds-control-runtime/` | `gtc-hd/native-output-bounds-control-runtime` | `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919` | Pristine native PPU at U plus the existing framebuffer harness |
| A | `experiments/bsnes-native-output-bounds-a-runtime/` | `gtc-hd/native-output-bounds-candidate-a-runtime` | `13e19564bd038e3767a58b9f1f1d29b1d5f4f527` | `46fa75236fa61d49d8e9424b3b44694b88aa07a9` |
| B | `experiments/bsnes-native-output-bounds-b-runtime/` | `gtc-hd/native-output-bounds-candidate-b-runtime` | `71820eaf7777bee0537ed2a9c87e01e916bae3a1` | `31094598c7c03af7f4bba758061346b5aca7143c` |

**RETAINED / RUNTIME EVIDENCE — SHA-256 of `bsnes/out/bsnes.exe`:**

| Runtime | Executable SHA-256 |
| --- | --- |
| Control | `9CD67324BD89F80AE67DB8D49D792F970E07E443DD75FE56B4FFDC8C21AEAA0C` |
| A | `C31FD438E13DE097F9FF5864D7191EF23956C17010FC4A93D3F234F2DBCC4963` |
| B | `889F0F92A7BFCCDDC7F71C95EDFBEEA3A17DD454F6424DD47708342D8E4BEB28` |

These match the task's established ordinary-run identities and were checked
again before targeted execution. No emulator rebuild or harness change occurred.
They are historical research identities, not substituted sanitized-public SHAs.

## 4. Ordinary SMW validation

**RETAINED EVIDENCE:** The Control/A/B 1,800-callback CSVs were inspected and are
byte-identical to each other and to the preserved historical EXP-003 B/C
1,800-callback reference. All contain indices 0..1799, width 512, height 480,
pitch 1,024 bytes, scale 1, and successful completion trailers. The task records
exit **0** for all three; process exits were not re-observed by rerunning them.

Common complete-file CSV SHA-256:

`9BC5FF87FC19E52615CFFB334AD9AD75900F4C8F12818972C210479A857B99FB`

Established deterministic input identities, retained and fingerprint-checked:

| Input | SHA-256 |
| --- | --- |
| Super Mario World (U) [!].sfc | `D70C9C7716AD12C674FC7DD744736AA48D4D7B4237F58066BE620FDA26024872` |
| Preserved initial SRAM seed | `D0FF1B294B5288D1AE1421EADF5B2D38A8752B76D472FF30BED9028E25B1C5B8` |
| Preserved deterministic settings seed | `E22FBA1B0E141499C94A25652C6A2FAEBEA27ADB8A11D4EC2E84BEDA43A8FA6B` |

The established protocol uses the cycle PPU, entropy `None`, CPU 100%, normal
sprite/VRAM rules, deinterlace enabled, no controller input, run-ahead or rewind,
and disabled automatic state loading. Details remain in
[EXP-003 results](../experiments/EXP-003/RESULTS.md). The frontend rewrites settings
on exit; post-run settings are not misidentified as the original seed bytes.

**Limit:** This establishes framebuffer equality for the stated game and window,
not universal game compatibility, complete CPU-state equality, provenance
revalidation on corrected binaries, or hardware conformance. The long run was
not repeated in this task.

## 5. Targeted fixture/tooling

**SOURCE / TOOLING OBSERVATION:** Repository and local tool checks found no suitable
available SNES assembler (`asar`, `bass`, `ca65`/`ld65`, or `wla-65816`/`wlalink`).
The smallest solution used Python **3.12.9** and its standard library to emit the
specific instructions needed by one ROM. No SDK, dependency installation,
general assembler or general test framework was introduced.

Fixture sources:

- [build_fixture.py](../../tests/native-output-bounds-runtime/build_fixture.py)
- [run_validation.py](../../tests/native-output-bounds-runtime/run_validation.py)
- [settings.bml](../../tests/native-output-bounds-runtime/settings.bml)
- [fixture protocol and reproduction instructions](../../tests/native-output-bounds-runtime/README.md)

The 32,768-byte NTSC LoROM has 585 bytes of CPU code and 2,048-byte battery SRAM.
It initializes OAM/CGRAM under forced blank, executes actual CPU register reads
and writes, polls the latched V counter, runs all four scenarios, records CPU
results in SRAM, then idles. The existing harness captures sixteen native
callbacks and quits normally; the runner reads SRAM saved by native unload.
No emulator instrumentation was added.

| Artifact/input | SHA-256 |
| --- | --- |
| Generated `bounds-phase4.sfc` | `7750faacfd65860b45dde5ba43d98d4ac9ac22b4d6169e4e37e2ab7b41631bb3` |
| `build_fixture.py` used for runtime generation | `66bface6bcbad4e8fff10f3cd43503a5aa66e6916c8dfd94f21298da10988d47` |
| `run_validation.py` | `34623ab817855c011fde3422b7b3fb464d5265d527ff06718d3c7c9501e3f0e2` |
| Targeted settings seed | `66677a7e58d2e41d4e0f6916e2cb9a7a2e96a2363296ff9799b93eb59a9bb999` |
| Initial SRAM: 2,048 zero bytes | `e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad` |

Settings select the cycle PPU, entropy `None`, CPU 100%, deinterlace **false**,
normal sprite/VRAM rules, no cheats/hotfixes, no run-ahead/rewind/state loading,
and `None` video/audio/input drivers. No controller input is supplied. Hashing
occurs before frontend cropping/filtering/driver output, so the driver choice
does not remove native framebuffer capture. This is a deliberately different
settings seed from the ordinary SMW condition.

Commands used, with machine-specific locations normalized:

```powershell
python -B tests/native-output-bounds-runtime/build_fixture.py --output "<OUTPUT_DIR>/static-fixture"
python -B tests/native-output-bounds-runtime/run_validation.py --control experiments/bsnes-native-output-bounds-control-runtime/bsnes/out/bsnes.exe --candidate-a experiments/bsnes-native-output-bounds-a-runtime/bsnes/out/bsnes.exe --candidate-b experiments/bsnes-native-output-bounds-b-runtime/bsnes/out/bsnes.exe --dll-dir "<UCRT64_BIN>" --output "<OUTPUT_DIR>/phase4-01"
```

For each runtime, the runner invoked:

```text
<RUNTIME_EXE> --settings=<RUN_DIR>/settings.bml --exp001-frame-hash=<RUN_DIR>/frames.csv --exp001-frame-count=16 <RUN_DIR>/bounds-phase4.sfc
```

Each received fresh identical ROM/settings/SRAM copies. Executable fingerprints
were checked before launch. Expected frame hashes were generated from fixed
colors and row geometry and saved before Control ran; no observed frame was
promoted to an expected image. Both possible first-field images were precomputed;
the independently checked SRAM field bit selects one. Control must pass before
A runs; A must pass before B runs. The runner stops on any expectation failure
or first comparison discrepancy, with no retry or expected-result regeneration.

## 6. V=240 OBJ/STAT77 result

**RUNTIME EVIDENCE — Control = A = B:** All 128 small sprites have X=0, Y=240;
none wraps or qualifies earlier. Forced blank is off and live/latched overscan
is on. Raw STAT77 is **`0x11` at V=239**, then **`0x51` at V=241** after native
V=240 processing. Masking with `0xc0` gives **`0x00` → `0x40`**:
rangeOver becomes true and timeOver remains false. Each ROM assertion passes.

**SOURCE OBSERVATION:** `bsnes/sfc/ppu/object.cpp` still evaluates the 33rd
eligible sprite and accumulates rangeOver in `Object::fetch()`. At this late
line, its native fetch path steps without reading tiles; no earlier line raised
timeOver. `ppu/io.cpp` exposes those flags through `$213e`. The other raw bits
are version/open-bus state, not extra overflow flags.

The SRAM result channel carries the CPU observations. Callback 1 also matches
the independent red-backdrop pattern in valid rows 2..479; rows 0..1 stay black.
This is native-behavior preservation evidence, not a new hardware claim.

## 7. Overscan-transition result

**RUNTIME EVIDENCE — Control = A = B:** A CPU write at V=250 changes SETINI from
overscan on to off and sets a blue backdrop. Native `PPU::main()` detects that
transition at the next V=0. Callback 2 exactly matches blue in valid rows
**16..463**, black in **0..15 and 464..479**. The previously red border is gone.
There is no crash or observed presentation/result corruption; all exits are 0.

**SOURCE + HOST EVIDENCE:** A clears backing pair 240; B has no such pair and
clears only valid pairs 1..7 and 232..239. The matching runtime oracle shows B
does not need pair-240 storage for this presentation, and A's backing-only pair
does not leak into it. No runtime tail readback or general memory-safety claim
is inferred from matching image hashes.

## 8. Mixed live/latched result

**RUNTIME EVIDENCE — Control = A = B:** Placement is latched non-overscan at V=0.
The CPU observes V=**233** and writes SETINI overscan on during that line. Live
vdisp becomes 240 while placement retains its +7-pair offset. Execution continues
through V=233..239, whose logical destinations are outside the presentation.

The CPU requests CGRAM address 1, initialized to `0x1234`. With forced blank off
and live active-display access, reads instead return **low `0xe0`, raw high
`0x83`**, i.e. **`0x03e0`** after masking the open-bus high bit: the backdrop at
native palette latch 0. The pre-read latched H-dot is **207**. STAT77 at V=241
is again **`0x51`**. All assertions and stage-completion checks pass.

Callback 3 occurs at the original V=225 boundary. Changing live vdisp after that
boundary causes another native callback at V=240, index 4. Both exactly match
green in rows 16..463 with black borders; this additional callback was predicted
from `cpu/timing.cpp::CPU::scanline()` and included in the oracle before execution.

**Scope:** This proves the constructed mixed-control history and its tested
CPU-visible CGRAM/status result through real bus transactions. The CGRAM witness
observes one latch value at V=233; it does not independently identify every
late-line palette update or all internal state. Phase 3 supplies the broader
late-line execution/order evidence. Output eligibility must remain separate
from native computation and live vdisp; the passing comparison does not license
a new early-return correction.

## 9. Interlace smoke result

**RUNTIME EVIDENCE — Control = A = B:** SETINI enables overscan and screen
interlace at V=250; OBJ interlace stays off. With deinterlace disabled, consecutive
STAT78 field bits are **`0x00`, `0x80`**, XOR **`0x80`**.

Callback 5 writes yellow into even rows 2..478 and retains the preceding contents
of odd rows. Callback 6 fills the opposite parity; callbacks 6..15 are yellow
through rows 2..479, with pair zero black. Every callback equals the independently
constructed expected image. Both real field placements were exercised without
observed presentation corruption or a process failure.

This is the requested smoke case, not exhaustive interlace, PAL, restore or
memory-sanitizer validation. Runtime output observations complement Phase 3's
actual candidate-array bounds and opposite-field host checks.

## 10. Control/A/B comparison

**RUNTIME EVIDENCE — first and only targeted attempt `phase4-01`:**

| Scenario/result | Control | A | B |
| --- | --- | --- | --- |
| V=240 STAT77 | `11` → `51`; range=1, time=0 | Same; PASS | Same; PASS |
| Overscan on → off | Exact blue center / black borders; PASS | Same; PASS | Same; PASS |
| Mixed controls | V=233; CGRAM `e0 83`; STAT77 `51`; two expected green callbacks; PASS | Same; PASS | Same; PASS |
| Interlace | Fields `00`, `80`; exact parity/retention patterns; PASS | Same; PASS | Same; PASS |
| Process exit | 0 | 0 | 0 |
| Native callbacks | 16 complete | 16 complete | 16 complete |
| SRAM completion / failure code | `a5` / `00` | Same | Same |
| First Control or A/B divergence | None | None | None |

Every callback is 512x480, pitch 1,024 bytes, scale 1. Complete CSV files and all
2,048 SRAM bytes are equal, not just selected fields. Common SHA-256 values:

| Captured result | SHA-256 |
| --- | --- |
| Complete 16-callback CSV | `69416871a6eaf2541a684a352c4a7e13972cb49470ccc8b0f436ca9866fd04de` |
| Final 2,048-byte SRAM | `75d6febfa8370ea0969e9ab06312552e60479803d090d44e781531e4f7932acc` |

Common per-frame native sample hashes:

| Callback | SHA-256 |
| --- | --- |
| 0: black | `be4481ff8d6cf5d03132fe333186ff65057ce36871b4e216889a48b0181a2681` |
| 1: red overscan | `9eac03c29a282fa0a302eda03e7fba9cd697c6dc342c6584a931464a49f00ede` |
| 2: blue centered | `aec82c1d0aa9c61467959ad8c07865a132e079b399ead1a0764fad2cf8011584` |
| 3, 4: green centered | `604080a4c9fd80512b2dd8ccebd2efd2cf5ba399d0c6dee74813807fe3b1efbb` |
| 5: first yellow field | `2da2d0d7a5f605ae6b463cdcf4fb7d77affc72a570232a78295dbd84414dcf72` |
| 6..15: both yellow fields | `2ed252c020ff2424713b14ea7a8c790fa6385f53b8c36bd0deaaab435355e591` |

Final SRAM's first 22 bytes are:

```text
47 54 43 34 01 a5 00 00 11 51 40 01 01 e9 cf e0 83 51 01 00 80 01
```

All remaining bytes retain the zero seed. The fixture README defines each
offset. Raw ROM/listing/manifest, settings seed and post-run settings, expected
hashes, commands, logs, CSVs, SRAM and summary are retained locally under
`<OUTPUT_DIR>/phase4-01/`; they are not public links or a redistributed game.

## 11. Unexpected differences

**None observed.** Control met the predeclared fixture expectations; A and B
then met those expectations and exact Control equality. No stop condition fired,
no candidate was repaired, no expected result was regenerated, and no additional
runtime phase was opened. The extra mixed-state callback is expected native
scheduling behavior, not a divergence.

## 12. Candidate A assessment

**INFERENCE:** A is the more conservative bounds correction for this task. Its
512x496 backing provides defined destinations for existing logical late stores,
including the derived maximum index 253,951. Presentation remains 512x480. It
also fixes pointer formation on no-store lines; merely enlarging the allocation
would not do that.

Native computation, sample-store ordering and unpresented persistence are
preserved within the documented contract. Historical larger backing supports
the separation of backing and presentation, though it does not prove an author
intended precisely 496 rows. The implementation adds an extent/init change to
the shared pointer-safe approach, with a **16 KiB** storage increase and extra
tail initialization. There is no measured performance claim.

Maintenance requires keeping the 512x480 presentation boundary explicit and
updating the derived backing envelope if native execution/placement changes.
For upstream review, the bounded change and preserved store policy provide a
straightforward rationale; upstream acceptance has not been sought or assumed.
Host and runtime evidence support this assessment for the tested conditions.

## 13. Candidate B assessment

**INFERENCE:** B is also supported by the completed host and runtime evidence.
It keeps 512x480 backing, preserves native computation and every valid store,
and deliberately omits unpresented persistence and pair-240 clearing. No intended
tail consumer was found, and no tested CPU/presentation difference resulted.

Its capacity matches the presentation boundary and avoids A's extra allocation;
explicit separation of computation from storage is clear. Both candidates use
similar integer destination checks and pointer-safe handling, so B does not
eliminate that logic. Future edits must keep arithmetic, palette activity and
timing outside the conditional store path.

The additional policy choice is that computed tail samples need not persist.
That is plausible given the inspected consumers but a larger semantic departure
than A's retained-store policy. It deserves explicit upstream discussion if B
is proposed. The saved memory/store traffic has not been benchmarked, and no
material speed advantage is established.

## 14. Baseline recommendation

**RECOMMEND CANDIDATE A for Xavier's corrected-baseline decision. NOT ACCEPTED.**

All requested targeted scenarios passed, ordinary SMW output matches the
established historical reference, and no intended tail consumer was found.
The comparison has enough evidence for a concrete recommendation: retain native
logical stores in defined 512x496 backing, preserve the 512x480 presentation
contract, and retain complete pointer-safety handling. A's 16 KiB cost buys the
smaller persistence-policy change and aligns with the historical distinction
between storage and presentation. The available evidence identifies no
performance or memory constraint that outweighs that conservative choice.

B remains a viable tested alternative; this recommendation does not identify a
B failure. No observed contradiction requires another general investigation or
additional edge-case phase. Absolute hardware proof is not a prerequisite for
this bounded recommendation. The final baseline decision belongs to **Xavier**;
successful research does not select bsnes as GTC-HD's foundation.

## 15. Remaining risks

- The original Control still contains the inherited C++ subobject/pointer
  defects. Matching its outputs in these binaries cannot predict arbitrary
  compiler/layout consequences or make native UB safe.
- The target is one NTSC synthetic register history plus one deterministic SMW
  window. PAL runtime, broad games/modes, hardware accuracy and complete
  execution-state equivalence are not established. The mixed witness observes
  one CGRAM value; it is not a trace of all late-line effects.
- This task captures native framebuffer samples with video/audio drivers `None`;
  it does not validate display-driver presentation, audio equality, overlays or
  every filter configuration. The ordinary SMW evidence has its own settings.
- Runtime memory sanitizers were not used. Phase 3's unavailable ASan/UBSan
  runtimes remain a coverage limit; source bounds reasoning and guard/geometry
  checks are the supporting safety evidence.
- Full-system save/load, arbitrary coroutine-stack restoration, rewind,
  run-ahead and cross-binary save-state compatibility remain unvalidated. The
  earlier equal native-field serializer payload is not a full-state guarantee.
- Performance is unmeasured. A changes PPU object layout and adds 16 KiB; future
  scheduler/placement changes must be checked against its backing envelope.
  Exact historical hardware necessity and upstream acceptance remain unknown.
- Existing EXP-001/002/003 captures belong to their original binaries. This
  result alone does not transfer their provenance/passivity claims to a
  corrected experiment build.

These limits constrain claims; none is an observed contradiction preventing
the recommendation in section 14.

## 16. Required revalidation if accepted

After Xavier explicitly accepts a corrected baseline, record that exact commit,
build/toolchain identity and executable hash. Reintegrate each observer under
explicit authorization without silently substituting public SHAs or rewriting
historical references. Rebuild on the supported toolchain and rerun the affected
focused host/observer checks, including bounds, native execution/state/order,
capture windows, drop/overflow handling and disabled behavior.

Minimum evidence before reconsidering EXP-004:

| Experiment | Required corrected-baseline runtime revalidation |
| --- | --- |
| EXP-001 | Same deterministic ROM/settings/SRAM seeds; baseline/harness and observer-disabled/enabled 600-callback comparisons. Capture callback 500; verify the established 23,760 BG records, actual fetch provenance, no drops/overflow, and native framebuffer equality. |
| EXP-002 | Same seeds and 600-callback disabled/enabled comparisons. Capture callback 500; verify evaluation → fetch → surviving OBJ lineage, 29,772 records including 687 winners, no unknown winners/drops/overflow, and the 12 documented real-overlap witnesses. |
| EXP-003 | Same seeds and 1,800-callback disabled/enabled comparisons against the established reference. Capture callback 500; verify the 61,440 main/sub composition records, winner/window/priority/backdrop semantics, provenance completeness and no drops/overflow. |

Compare newly built observer-enabled and disabled sequences with a harness-only
build of the accepted correction, and with the preserved historical references
where applicable. Record exact identities and first divergences; do not replace
an expected digest or count to obtain a pass. Confirm that integrating observers
retains the correction's targeted CPU/presentation results and destination
bounds. Any difference requires specific diagnosis before transferring claims.

This is finite regression revalidation of existing experiment claims, not a new
general baseline-investigation phase. It is a requirement for a later authorized
task, not work performed here. Unsupported save-state/features stay outside the
transferred claims unless separately tested.

## 17. EXP-004 disposition

**EXP-004 COLOR-MATH PROVENANCE IMPLEMENTATION REMAINS BLOCKED AND UNAUTHORIZED.**

The native-baseline investigation now has a completed tested recommendation for
decision. It has not established an accepted corrected baseline. Xavier must
document the baseline disposition; the necessary experiment revalidation must
be completed, and EXP-004 implementation must be explicitly re-authorized before
its gate is reconsidered. Neither runtime success nor worktree registration
supplies that authorization.

`PROJECT_STATE.md`, `AGENTS.md`, existing research/experiment evidence and all
emulator worktrees remain untouched. Only this report and the new fixture source
files were added. No emulator source/harness change, emulator rebuild, ADR,
baseline acceptance, EXP-004 implementation, commit, push or merge occurred.
The only new ROM executions were the three short targeted runs reported here.
