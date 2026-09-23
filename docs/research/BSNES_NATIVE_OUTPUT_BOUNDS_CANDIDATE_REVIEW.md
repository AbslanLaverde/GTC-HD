# bsnes Native Output Bounds — Contract and Candidate-Design Review

Date: September 23, 2026.

**Phase 2 complete: source and candidate-design review only. No final correction selected or implemented.**

**Next-experiment option B: comparatively prototype two complete candidate designs in a separately authorized task.** Compare retained late-sample backing (candidate A with pointer-safe destination handling) against presentation-bounded stores (candidate B using D's execution/storage separation). Both must retain native PPU execution. This recommendation is not prototype authorization.

**EXP-004 remains blocked. No baseline disposition, architecture acceptance, or emulator selection is made here.**

## 1. Objective

Define the native behavior contract that a bounds correction must preserve, distinguish execution from storage/presentation/clearing, and assess technically plausible correction families.

**SOURCE OBSERVATION:** V=240 contains timing work and state mutations beyond framebuffer stores. In particular, OBJ evaluation can contribute to the CPU-readable range-over flag. A return that skips the entire line or Screen computation is not equivalent to preventing an invalid destination.

**INFERENCE:** The promising comparison is between two storage policies with the same native execution. Neither restoring an old allocation size nor restoring an old render limit is sufficient by itself.

The investigation performed source reads, local Git-history searches, and integer derivation of source bounds. No native code, tests or existing experiment reports were modified; no tests, builds, ROMs, commits, pushes, network fetches, ADRs or upstream contacts occurred.

## 2. Inputs and authority

Read:

- `AGENTS.md` and [project state](../PROJECT_STATE.md).
- [Phase 1 archaeology](BSNES_NATIVE_OUTPUT_BOUNDS_ARCHAEOLOGY.md).
- [EXP-004-P0 report](../experiments/EXP-004/P0_OUTPUT_BOUNDS_REPORT.md).
- [P0 bounds matrix](../experiments/EXP-004/P0_OUTPUT_BOUNDS_MATRIX.csv).
- [EXP-004 specification and implementation gate](../experiments/EXP-004/SPEC.md).

**SOURCE OBSERVATION — exact inspected baseline:**

| Item | Identity |
| --- | --- |
| External research project | bsnes, `https://github.com/bsnes-emu/bsnes.git` |
| Worktree | `experiments/bsnes-native-output-bounds/` |
| Branch | `gtc-hd/investigate-native-output-bounds` |
| Required and inspected HEAD, called U below | `7d5aa1e656b9171524d01b1b22917197d8121cb4` |
| Subject | `fix horizontal offset in high-resolution offset-by-tile mode` |
| Working state | Clean at inspection; native source remains unchanged |

Source citations identify that external checkout at U unless a historical SHA is specified. Unprefixed PPU filenames and `counter/` paths are abbreviated relative to `bsnes/sfc/ppu/`; `cpu/`, `system/` and `ppu/` prefixes are relative to `bsnes/sfc/`. Frontend `target-bsnes/` paths are relative to `bsnes/`, with unprefixed frontend `viewport.cpp` and `filter.cpp` under `bsnes/target-bsnes/program/`. Historical paths are identified separately. Historical EXP-004 evidence remains attributed to its original experiment baseline, not retrospectively to a candidate.

Labels:

- **SOURCE OBSERVATION:** source or repository metadata directly inspected.
- **HISTORICAL SOURCE OBSERVATION:** inspected historical source, diff or message.
- **INFERENCE:** proposed requirement, candidate assessment or deduction from source.
- **UNKNOWN:** not established by source review.

“Must preserve” below is a **proposed baseline-correction acceptance contract**, not a claim that every current operation has been proven necessary on SNES hardware. It excludes reproducing undefined behavior or corruption of neighboring objects. Historical evidence remains evidence for the historical source/binary and tested conditions.

## 3. Native execution contract

**SOURCE OBSERVATION:** `bsnes/sfc/ppu/main.cpp:1–32,76–194` has three distinct ranges:

| Native range | Work at U |
| --- | --- |
| V=0 | Transition clear, display latches, frame hooks, scanline hooks and cycle schedule; individual BG/Screen methods have their own V=0 returns |
| V=1..240 | Scanline hooks, cycle schedule, OBJ fetch phase and timing remainder |
| V>240 through field end | Scanline hooks still execute, including Screen initialization; then `step(hperiod())` |

The cycle schedule covers H=0,2,…,1078. OBJ fetch follows at H=1080; the remainder advances to the region/field-dependent line end. `ppu.cpp:42–58` advances counters and synchronizes with the CPU in two-clock steps. A replacement that preserves only total line duration need not preserve state changes relative to intervening CPU writes/reads.

**INFERENCE — required execution invariants:**

- **E1:** Preserve native counters, clock advancement, synchronization opportunities, order of PPU work, frame events and light-gun latching.
- **E2:** Preserve BG/mosaic, OBJ, window and Screen state updates and their live-register reads, including on non-presented lines.
- **E3:** Preserve V=0 latching and transition detection, V=0 sample skip, and no-render-line state initialization after V=240.
- **E4:** Preserve below→above evaluation, native arithmetic and palette-latch side effects, brightness conversion and retained-store order. Do not use a framebuffer eligibility check to skip those computations.
- **E5:** Preserve CPU-visible register semantics and serializer payload unless a separate reviewed requirement explicitly changes them.
- **E6:** Preserve presentation-stage blur/overlay order and callback scheduling. Host performance may change; emulated clock/state behavior must be assessed separately.

These are conservative requirements for a bounds-focused candidate. There is no source proof authorizing wholesale deletion of V=240 cycle work.

## 4. Backing-storage contract

**SOURCE OBSERVATION — `ppu.hpp:55–56`, `screen.cpp:1–29`:**

```text
Npresentation = 512 * 480 = 245760 entries
pairY = V + (latchedOverscan ? 0 : 7)
A = 1024 * pairY + (latchedInterlace && field ? 512 : 0)
B = A + (latchedInterlace ? 0 : 512)
destination = A or B + 2*x + sampleSlot
x = 0..255; sampleSlot = 0 or 1
```

The present array has exactly Npresentation entries. Its neighbor `lightTable` is a different object, not padding.

**INFERENCE — distinguish two legitimate candidate contracts:**

1. **Retain current logical stores:** all sample destinations for V=1..240 require valid backing, whether presented or not. Across current placement controls, the maximum written index is **253,951**; retaining them needs at least **253,952 entries (512×496)** relative to the current output origin. This is a derived store envelope, not a selected allocation.
2. **Retain presentation stores only:** every store whose logical destination belongs to indices 0..245,759 remains; other sample calculations still execute but do not write that array. This deliberately changes persistence of unpresented samples, and requires separate evidence that no intended consumer depends on them.

Both require independent handling of no-store-line pointer formation (section 9). A 512×512 allocation covers current stores but **does not cover all pointers currently formed**.

**SOURCE OBSERVATION:** Searches of the native cycle-PPU output consumers find Screen stores, transition clearing, power initialization, and refresh. Refresh exposes only the 512×480 rectangle to blur/controller/platform consumers (`ppu.cpp:85,189–211`). PPU serialization does not include the framebuffer or light table. No intended cycle-PPU read of an unpresented tail was found.

**INFERENCE / UNKNOWN:** This makes the retained-tail versus omitted-tail comparison useful; it does not establish universal equivalence. Native undefined behavior may affect other state, and restore/overlay/platform behavior still requires validation. Any candidate must isolate the light table from output writes rather than try to reproduce accidental adjacency effects.

## 5. Presentation contract

**SOURCE OBSERVATION — `ppu.cpp:189–211`:** The cycle path presents 512×480 uint16 samples, pitch 1,024 bytes, scale=1. Blur and controller overlays precede the callback. Fast-PPU delegation and run-ahead output suppression are separate paths.

**INFERENCE — proposed invariant P1:** Preserve the callback rectangle, pitch, sample encoding, ordering and native centering. Backing capacity need not equal that rectangle.

| Placement | Native content mapping in stable settings |
| --- | --- |
| Non-overscan | V=1..224 → pair rows 8..231 → memory rows 16..463 |
| Overscan | V=1..239 → pair rows 1..239 → memory rows 2..479 |
| Non-interlace | Each sample is duplicated into both rows of its pair |
| Interlace | Current field writes one row of each pair; A/B alias that row |

**SOURCE OBSERVATION:** `target-bsnes/program/platform.cpp:205–230` retains the original callback for refresh. The frontend overscan option can crop 16 memory rows from each end, yielding 512×448, independently of emulated SETINI. `viewport.cpp:4–32,50–72` and `filter.cpp` then size/filter the result.

**INFERENCE:** Keep pair row 0, borders, retained opposite-field contents and refresh mutations conceptually separate from active composition samples. A correction must not silently change +7, make callback height depend on backing capacity, reinterpret V=240 as an extra displayed row, or turn the frontend crop into a native execution gate.

## 6. Clearing contract

**SOURCE OBSERVATION — `main.cpp:2–12`, `ppu.cpp:83–85`:**

- Power initializes the 512×480 output rectangle.
- At V=0, old latched overscan=true and current live overscan=false clears pair rows 1..7 and 232..240, both rows per pair.
- The clear precedes assignment of the new display flags.
- The comment identifies the purpose as removing old overscan content from the region outside the new centered image.

**INFERENCE — proposed invariants C1–C3:**

- Every callback element must have a defined initial value before presentation. Any added storage that a candidate reads must likewise be initialized or previously written; pointer-only capacity does not itself require pixel initialization.
- Preserve transition timing and clear both fields' old border content before it can appear in the newly centered presentation.
- Separate clearing of **presented stale content** from an optional policy for **unpresented backing**. Do not infer one range from an allocation's size.

The presentation-relevant transition set is **pair rows 1..7 and 232..239**. Pair 240 is outside presentation. If a padded candidate retains it, its clearing can be defined as a backing-retention policy; if a presentation-only candidate omits it, no callback row is removed. These policies must be explicit and compared, not conflated with execution.

Pair 0 is already excluded by the native transition loop and by Screen stores. Its native-screen initial contents come from power; later refresh overlays can mutate it (`bsnes/sfc/controller/super-scope/super-scope.cpp:101–112`, `bsnes/sfc/controller/justifier/justifier.cpp:111–119`). Extending this task into a new pair-0/overlay clearing policy is not justified by the current bounds question.

## 7. V=240 call-graph findings

### Schedule and state

**SOURCE OBSERVATION — `main.cpp`:**

| Phase / source | What happens at V=240 | Contract significance |
| --- | --- | --- |
| Scanline entry, lines 20–27 | Mosaic, all BGs, OBJ, window and Screen scanline methods execute before the cutoff | Preserve state setup even if sample storage changes |
| H=0..1016, every 8 clocks, lines 76–77,188 | 128 calls to OBJ evaluation | Can update OAM latch, item list/count and later range-over status |
| H=0..1052, every 4 clocks, lines 80–157,189 | 264 BG fetch dispatches, with mode-dependent methods | Fetch/state work is not gated by presentation bounds |
| H=56, lines 159–164,190 | BG begin shifts cached tile data | Internal execution state changes |
| H=56..1076 and 58..1078, lines 166–193 | 256 below and 256 above BG runs; then OBJ→window→Screen at each above position | Preserve order and live-state dependencies |
| After each cycle, line 194 | Two-clock step, counter update and possible CPU resume | CPU interleaving is part of the baseline contract |
| H=1080, lines 67–69 | OBJ fetch phase, then timing remainder | Late fetch has its own gate and status finalization |

Mosaic scanline work decrements and, when needed, reloads its vertical counter according to current BG mosaic enables (`mosaic.cpp:14–21`). BG routines (`background.cpp:12–26,29–171,174–213`) reset per-line bookkeeping, read VRAM, update tile/offset caches, consume planar data, update mosaic-held samples and outputs. Their principal vertical early return is V=0, not V=240. Mode 7 dispatch (`mode7.cpp:6–67`) calculates coordinates, performs VRAM reads and updates outputs/mosaic progression.

Window work (`window.cpp:1–38`) advances x, masks BG/OBJ priorities, and computes color-window enable state. Screen scanline setup (`screen.cpp:8–18`) calls paletteColor(0), sets the CGRAM address latch and seeds math state. It is not merely pointer setup.

### OBJ effects that matter beyond the framebuffer

**SOURCE OBSERVATION — `object.cpp:17–57,94–164`:**

- Scanline entry latches firstSprite, resets counts/x/y, swaps the two OBJ banks and invalidates the new evaluation bank.
- If V equals live vdisp and forced blank is off, it resets the OAM address and first-sprite selection. V=240 is that boundary with live overscan on.
- The final return in Object::scanline does **not** disable later calls to Object::evaluate. Evaluate has a forced-blank/count gate but no vdisp/V=240 gate.
- A matching object updates `ppu.latch.oamAddress`; the 33rd match increases itemCount beyond 32.
- At V=240, Object::fetch always takes its no-tile-read path for valid items: V≥vdisp−1, since live vdisp is 225 or 240. It steps eight clocks for each such item, then still executes overflow-status accumulation.
- Consequently `io.rangeOver |= (t.itemCount > 32)` can change at V=240. Under this path no new tile fetches increment tileCount, so it does not newly create time-over from tile reads; existing time-over remains sticky.

**SOURCE OBSERVATION:** `io.cpp:169–175` exposes rangeOver/timeOver through STAT77 (`$213e`). Object::frame clears the flags at V=0 (`object.cpp:12–15`). OAM address/reset and firstSprite affect later OAM operations (`io.cpp:109–113`, `object.cpp:3–9`).

**INFERENCE:** A source-constructed state with more than 32 eligible sprites on V=240 and forced blank off supplies a concrete reason not to replace the V=240 pipeline with a timing-only skip: the final range-over result can differ. This is a logical witness, **not a newly executed test or proof of hardware accuracy**.

### Screen effects, CPU access and frame events

**SOURCE OBSERVATION:** Screen::run evaluates below before above, then performs the two brightness lookups/chained stores (`screen.cpp:21–29`). Below/above can alter carried math and call paletteColor; paletteColor updates the CGRAM address latch (`screen.cpp:32–124,147–149`). Forced blank or live non-overscan V≥225 returns zero from those functions, but the stores still follow.

CGRAM/OAM/VRAM CPU access rules use live vdisp (`io.cpp:33–69`). At V=240 the active-display CGRAM redirection condition V<vdisp is false for either live setting; do not claim that every V=240 palette-latch update directly redirects a CPU CGRAM access. Earlier invalid-destination lines V=233..239 with **latched overscan off/live overscan on** do satisfy V<vdisp. Skipping Screen wholesale there can remove a latch update used by CPU CGRAM access during H=88..1095.

CPU::scanline synchronizes processors, performs line bookkeeping, and leaves a frame event at live vdisp; the event invokes PPU::refresh (`cpu/timing.cpp:96–139`, `system/system.cpp:109–110`). CPU NMI/vblank checks also use vdisp (`cpu/irq.cpp:7–16`, `cpu/io.cpp:39–44`). Frame events are not issued by the current PPU main loop and do not permanently suppress its later execution.

CPU stepping separately polls NMI/IRQ and advances automatic joypad polling (`cpu/timing.cpp`, CPU::stepOnce and CPU::joypadEdge). Joypad polling can begin on live vdisp, including V=240 with overscan on. CPU::scanline also resets DRAM-refresh bookkeeping and gates HDMA setup by live vdisp. These CPU-side operations are not Screen work; preserving PPU synchronization prevents a storage correction from changing their relationship to native PPU state.

PPU and CPU each maintain counter state. Their timing and CPU-visible H/V latches must remain coherent (`counter/counter.hpp:1–11`, `io.cpp:1–19,147–192`). The native non-interlace NTSC field-1 V=240 line is shortened to 1,360 clocks; it cannot be replaced with an unconditional 1,364-clock line.

### What must execute, and what is separable?

**INFERENCE:** Counter progression/synchronization, event timing, OAM reset and overflow accumulation have explicit timing or CPU-visible consequences and belong in the preserved execution contract. BG/window/Screen work also mutates native and serialized state; preserve it conservatively unless a separate proof allows removal.

Only destination selection, framebuffer assignments and cursor bookkeeping are clearly storage-specific operations here. They can conceptually be separated from native sample computation and latch/math effects. This is not proof that an arbitrary store-suppression implementation is safe: retain evaluation order, valid stores, initialization, field aliasing, restore behavior and all pointer rules.

**UNKNOWN:** Source review cannot establish the hardware necessity of every BG/window/math operation at V=240, nor prove all resulting state is overwritten before observation. Serialization includes those states (`ppu/serialization.cpp:32–33,103–134,161–192,249–280`); absence from the callback does not establish unobservability.

## 8. Donor scheduler findings

**HISTORICAL SOURCE OBSERVATION:** Import commit `409dd371b96e863ea626f85faa51db140307d275` (September 21, 2019, `v109.5`) says it backports higan's newer accuracy PPU with sprite caching. It does not identify a donor SHA/tree.

Local searches included all branches/remote-tracking refs and release tags, `git log --all` for `higan/sfc/ppu/main.cpp` / `sfc/ppu/main.cpp`, full-tree `-S cycleObjectEvaluate`, and `-G` for the cycle-dispatch symbols. The introducing occurrence is the bsnes import; subsequent edits are bsnes history. No separate donor tree carrying that scheduler was established.

The available pre-rename snapshot `c25d20a8d9b5d0f25e52823818cd20f7600d7c17` (April 13, 2019, `Don't build higan on the bsnes branch.`) still contains the older `higan/sfc/ppu` implementation. It is **not identified as the donor**.

| Aspect | Available older higan-path tree at c25d20a8d9 | Imported bsnes tree at 409dd371b9 | Exact newer donor |
| --- | --- | --- | --- |
| Allocation | Dynamic uint32 512×512, output origin +16×512 | Inline uint16 512×480 | UNKNOWN |
| Placement | V×1024, row/field offset; centering at refresh origin | (V+7 when non-overscan)×1024, row/field offset | UNKNOWN |
| Render cutoff | V≤239 | V≤240 | UNKNOWN independently of imported result |
| Pointer formation | Screen::scanline before render gate | Screen::scanline before V>240 gate | UNKNOWN |
| Transition loop through pair 240 | Absent | Absent; introduced later in 793f2e5bf4 | UNKNOWN |
| Presentation | 512×480, pitch 512 samples, non-overscan origin −14 rows | 512×480, pitch 512 samples, no origin subtraction | UNKNOWN |

Sources are the respective trees' `ppu.cpp`, `ppu.hpp`, `screen.cpp` and imported `main.cpp`. The later clear commit is `793f2e5bf44a421237905c6638ce05f6e2d6cb5f`.

**UNKNOWN:** No exact or defensibly “most likely” donor SHA can be assigned from these local records. The import's allocation cannot be attributed to the donor merely because its scheduler was backported. No remote fetch or upstream contact occurred.

## 9. NTSC/PAL/interlace analysis

**SOURCE OBSERVATION — `counter/counter-inline.hpp:19–39,78–84`:** Reset/field rollover establishes 262 NTSC or 312 PAL lines. At V=128, timing interlace is sampled from the PPU display latch; interlace field 0 adds one line. Field toggles on rollover.

The table derives the last ordinary scanline-entry pointers for valid counter progression. I is frame-latched placement interlace; O is frame-latched overscan. P is the larger A/B base **formed**, not a dereferenced sample on these late lines.

| Region | I | Field | Last V | P, O=on | P, O=off |
| --- | --- | --- | --- | --- | --- |
| NTSC | 0 | 0 or 1 | 261 | 267,776 | 274,944 |
| NTSC | 1 | 0 | 262 | 268,288 | 275,456 |
| NTSC | 1 | 1 | 261 | 267,776 | 274,944 |
| PAL | 0 | 0 or 1 | 311 | 318,976 | 326,144 |
| PAL | 1 | 0 | 312 | 319,488 | **326,656** |
| PAL | 1 | 1 | 311 | 318,976 | 326,144 |

For every row, A=1024×(lastV+(O?0:7))+(I&&field?512:0), B=A+(I?0:512). No Screen stores or cursor increments occur at those last V values because all exceed 240.

**INFERENCE — three distinct maxima:**

- **Actual store envelope:** all current stores still end at index 253,951 (253,952 entries). Region does not enlarge the V≤240 store interval. Maximum post-store cursor is 253,952; that may legally be one-past an adequately sized array.
- **Current no-store pointer envelope:** maximum formed offset is 326,656 under ordinary PAL interlace field-0 progression. A pointer at offset N may be one-past a real N-element array without being dereferenced. This does not require all nominal samples after that pointer to exist, because no stores follow.
- **Conservative independent-control envelope:** if a design elects to admit any I/field pairing with V≤312 without relying on the normal period/field correlation, max formed offset becomes 327,168. A full nominal pair through pairY=319 would end at 327,679, but those hypothetical samples are **not** current late stores. Do not confuse these three bounds or present them as a chosen allocation.

A candidate retaining all native pointer formation must prove a capacity against its supported state domain. A candidate delaying/removing no-store-line pointer formation need only back the destinations it actually forms/uses, while still performing Screen's non-pointer initialization.

**SOURCE OBSERVATION:** Normal H periods are 1,364 clocks. NTSC non-interlace field 1 V=240 uses 1,360; PAL interlace field 1 V=311 uses 1,368. V=312 in PAL interlace field 0 is a real additional source-supported case beyond P0's reported V=0..311 enumeration. This task derives it; it did not run an expanded matrix.

**UNKNOWN:** Arbitrarily malformed serialized counters are outside these ordinary-progression bounds. Valid save/restore and transitions still need coverage; a candidate must state its supported state domain instead of assuming every decoded combination matches a steady-state table.

## 10. Mixed-control analysis

**SOURCE OBSERVATION:** SETINI updates live interlace, independent OBJ interlace, overscan, pseudo-hires and extbg, then updates live-derived vdisp (`io.cpp:639–654`). Placement overscan/interlace latch at V=0 (`main.cpp:11–12`). Counter interlace samples that display latch at V=128. BG hires coordinate construction uses live `io.interlace` (`background.cpp:40–45`), while OBJ uses its own live interlace setting.

| Latched O | Live O | Native destination/value behavior | Consequence for candidate design |
| --- | --- | --- | --- |
| Off | Off | +7 placement; zero-return samples at V≥225; valid border writes through V=232 | Do not discard valid border clearing merely because vdisp=225 |
| Off | On | +7 placement but live active logic/vdisp=240; V=233..239 can have nonzero calculations and CGRAM-latch effects | A live vdisp gate alone still permits invalid stores |
| On | Off | Unshifted placement; V=225..239 are valid destinations supplied from zero-return paths | Omitting those stores can retain old displayed pixels |
| On | On | Unshifted placement; V=240 computes/stores beyond presentation | Keep computation distinct from storage eligibility |

**INFERENCE:** Eligibility must be derived from the latched destination geometry and chosen backing contract, not from live overscan alone. A frame-start latch is not permission to freeze live register values for the rest of that frame.

Interlace transition requirements include preserving which A/B rows alias, opposite-field retention, field toggling, live BG/OBJ interlace semantics, and V=128 timing sampling. Do not substitute live interlace into placement or collapse all interlace state into one boolean.

**SOURCE OBSERVATION:** Display/live flags, counters, BG/OBJ/window/math state are serialized, but framebuffer, lightTable and Screen line pointers are not (`ppu/serialization.cpp`, `counter/serialization.cpp`). `system/serialization.cpp:1–6,25–47,90–96` distinguishes synchronized saves from stack-based deterministic saves; synchronized load powers the system before deserialization.

**INFERENCE / UNKNOWN:** New cursor/eligibility state must be reconstructed correctly for supported restore modes. Keeping the serialized field list unchanged is desirable but does not alone prove save-state compatibility. Reallocation, transient pointer lifetime and mid-line stack restoration need explicit validation.

## 11. Candidate A — restore padded backing storage

**INFERENCE — family:** Preserve all native logical Screen stores while presenting the unchanged 512×480 subregion.

Two variants are plausible: enough backing for all existing formed pointers, or smaller store-covering backing plus D-style delayed pointer formation on no-store lines. **Simply declaring 512×512 and changing nothing else is incomplete.** Restoring the old +16-row output-origin offset without adapting placement would also change coordinates; current centering is already in Screen placement.

| Review dimension | Assessment |
| --- | --- |
| Preserved behavior | Cycle execution, native calculations, horizontal/field store order, logical late stores, callback geometry and +7 centering |
| Changed behavior | Allocation/layout and defined location of previously invalid writes; initialization/padding policy must be stated |
| Pointer formation | Safe only with a proved capacity including no-store pointers, or separate formation eligibility; store capacity alone is insufficient |
| Screen stores | Can all become defined inside one actual backing array |
| Transition clear | Existing pair 240 can become a valid unpresented backing clear; its retention is a policy choice, not a displayed-row requirement |
| Presentation | Same rectangle and intended mapping; actual historical hashes may still change if native UB previously affected valid samples |
| Timing/execution risk | Low conceptual semantic scope if only storage and pointer bookkeeping change; host cost/layout and restore effects remain |
| Mixed overscan/interlace | Capacity must cover latched geometry independently of live rendering; retain alias/field behavior and state generations |
| Reference impact | New executable identity and targeted verification, then revalidation of experiments migrated to it; existing-reference equality UNKNOWN |
| Complexity/invasiveness | Low to moderate; extra memory and lifetime/init considerations, potentially a small pointer-formation change |
| Supporting evidence | Historical backing exceeded presentation; current consumers do not intentionally read the tail |
| Unknowns | Best capacity/lifetime policy, donor assumptions, native UB effects, restore compatibility and whether keeping all unpresented persistence is useful |

This family has the strongest direct historical precedent, but historical size is not its safety proof.

## 12. Candidate B — suppress/bound Screen stores

**INFERENCE — family:** Keep the 512×480 array and native execution, but commit only samples whose full destination belongs to that array. Retain every currently valid store, including non-overscan border zero-return stores.

| Review dimension | Assessment |
| --- | --- |
| Preserved behavior | E1–E6 native work, valid sample values/order, callback geometry, centering and field aliasing |
| Changed behavior | Unpresented sample persistence is omitted instead of given extra backing |
| Pointer formation | Must classify scalar offsets before any pointer exists, including no-store lines; checking an already-invalid pointer is insufficient |
| Screen stores | Can become defined if whole row/sample spans and post-increments are proved valid |
| Transition clear | Must be handled separately with a valid presentation clear set; a Screen-only guard leaves the defect |
| Presentation | Intended valid pixels unchanged if initialization, refresh, mixed controls and valid zero writes are preserved |
| Timing/execution risk | Low for a narrow store decision after native computation; high if implemented as an early Screen/line return or reordered math |
| Mixed overscan/interlace | Supported when eligibility follows latched destinations; live vdisp is not the bound |
| Reference impact | Same staged revalidation requirement as A; suppression cannot promise equality with a UB baseline |
| Complexity/invasiveness | Moderate; cursor/eligibility representation, increments, clear endpoints and restore reconstruction all need review |
| Supporting evidence | Output tail has no found intended reader; computation/latches and final assignments are separable in source |
| Unknowns | Full native state equivalence, unexamined consumers/control histories and performance impact |

No clamping, wrapping or “nearest valid pixel” substitution is implied. Such redirection could overwrite legitimate callback content and would violate the proposed presentation contract.

## 13. Candidate C — restore a vdisp-like store/render gate

**HISTORICAL SOURCE OBSERVATION:** `0623d6ac2b785ccbb2b62521cb00dfe4a627b595` changed V≤239 to V<vdisp(). `409dd371b96e863ea626f85faa51db140307d275` replaced that gate. History demonstrates stable-mode behavior, not general correction safety.

**INFERENCE — C-render:** Restoring the entire render gate changes BG fetch/run, OBJ evaluation/fetch, windows and Screen work. Even if a timing remainder preserves line length, the V=240 range-over witness and internal state/interleaving remain different. This fails the proposed conservative execution contract without separate hardware/state evidence.

**INFERENCE — C-store:** Applying V<vdisp() only to final stores is less intrusive but still insufficient:

- Latched O=off/live O=on permits V=233..239, whose +7 destinations exceed the array.
- Latched O=on/live O=off omits valid V=225..239 zero-return stores.
- Stable non-overscan also omits valid bottom-border stores V=225..232.
- Pointer setup and the transition clear remain independently invalid.

| Review dimension | Assessment |
| --- | --- |
| Preserved behavior | Callback metadata/centering expressions can remain; C-store can keep computation |
| Changed behavior | C-render changes native state; C-store changes some valid stores and may leave stale content |
| Defined pointers/stores/clear | None is guaranteed by vdisp alone; all need additional destination/clear provisions |
| Presentation effect | Potential stale border/old-field pixels; not merely omission of unpresented samples |
| Timing/execution risk | High for C-render; lower but incomplete for C-store |
| Mixed/interlace behavior | Live vdisp does not encode latched placement or field row; stable-mode assumptions are inadequate |
| Reference impact | Broad execution/semantic revalidation for C-render; at least full migrated-scope validation for C-store |
| Complexity/invasiveness | Superficially small, but a complete mixed-mode/storage correction expands beyond the gate |
| Supporting evidence | Historical stable-mode reduction of late stores |
| Unknowns | Hardware justification for deleting native work, correct compensating clearing and mixed-state policy |

C is useful as a historical contrast, not a leading standalone prototype. Adding true destination eligibility moves its memory-safety reasoning toward B/D; a remaining vdisp filter would still be an additional behavioral change requiring justification.

## 14. Candidate D / other candidates

### D — separate execution from storage

**INFERENCE:** D is a design discipline that can complete A or B, rather than an independent claim that late execution is unnecessary:

1. Preserve all native scanline/cycle/sample computation and latches.
2. Describe logical destinations with integer geometry and horizontal progress.
3. Form/use real pointers only when the chosen backing policy permits.
4. Preserve valid sample order and A/B field aliasing.
5. Give transition clearing and initialization their own explicit bounds.

| Review dimension | Assessment |
| --- | --- |
| Preserved behavior | Execution contract, actual native computation, geometry and valid sample order |
| Changed behavior | Representation/decision of storage eligibility and cursor state |
| Pointer/store safety | Can cover both, including V>240; depends on the selected destination policy and increments |
| Transition clearing | Must be a separate explicit operation; D alone does not choose its range |
| Presentation | Can preserve it exactly in the intended defined model |
| Timing/mixed/interlace | Strongest separation of concerns; preserve live evaluation and latched placement independently |
| References | New binary and migrated-experiment verification; expected scope follows A or B |
| Complexity/invasiveness | Moderate; avoid turning a narrow bounds patch into a renderer refactor |
| Supporting evidence | Stateful work occurs before the final assignments; no-store scanline initialization also has effects |
| Unknowns | Safest minimal representation, restore reconstruction, performance and complete equivalence |

**INFERENCE:** A+D and B+D are the strongest comparative candidates. Their principal deliberate difference is retaining versus omitting unpresented sample persistence. A source-preserving A variant with sufficiently large backing may need less representation change; B naturally requires a separate eligibility decision.

### E — bounded scratch destination for unpresented samples

**INFERENCE:** A valid scratch row/pair could receive otherwise unpresented stores while native calculations and assignment order continue. This is source-justified as a third family because no intended consumer of the unpresented tail was found.

It changes persistent logical late destinations into disposable scratch contents. Pointer formation must select a real scratch object before arithmetic and reset cursors within its capacity; A/B must retain the required non-interlace separation/interlace alias. No-store lines need no usable cursor. The transition clear remains a separate presentation operation.

Its presentation and execution goals resemble B/D, with low-to-moderate conceptual timing risk but additional storage lifetime/alias/restore complexity. A new executable and the same targeted/migrated-experiment validation are required. Whether scratch adds any benefit over direct store omission is UNKNOWN. It is not a priority comparative prototype.

Clamping/wrapping late writes into valid presentation rows, moving the callback rectangle, or changing +7 solely to make arithmetic fit lacks supporting evidence and risks visible corruption/geometry changes; those are not supported correction families here.

## 15. Clear-loop treatment

**INFERENCE — compare the four relevant regions:**

| Pair rows | Presented? | Current/new-frame behavior | Required policy |
| --- | --- | --- | --- |
| 0 | Yes | Screen skips V=0; initialized at power; refresh overlays may mutate it | Preserve current policy; any new blanket clear needs separate rationale |
| 1..7 | Yes | May contain old overscan content; new centered Screen content does not overwrite them | Clear both rows on the documented on→off transition |
| 8..231 | Yes | Centered V=1..224 content, with opposite-field retention in interlace | Do not erase as a side effect of fixing border bounds |
| 232..239 | Yes | Outside new centered content; later V=225..232 makes valid zero-return stores in stable off mode | Clear at transition; later overwriting is not a substitute for correct timing/field coverage |
| 240 | No | Invalid in U; could belong to padded candidate backing | A may retain a defined backing clear; B excludes it from presentation clearing |
| 241..247 | No | Used by some late non-overscan Screen stores if retained | Backing policy only; not part of the existing transition loop |

The CPU can deliver the non-overscan frame event at V=225, before the remainder of the newly centered frame's bottom-border zero stores. Clearing both fields at V=0 avoids depending on those later stores, and avoids stale opposite-field border content. Exact callback-relative sequencing should be included in future validation rather than inferred from a final framebuffer alone.

The clear's primary contract follows **presentation content that became stale**, with a separately stated optional tail policy. It should not automatically follow total allocation size, live vdisp, or the scheduler's inclusive V=240 endpoint. Enlarging backing can make the existing loop defined without proving pair 240 visually necessary; removing Screen's late stores cannot repair the clear by itself.

## 16. Pointer-safety requirements

**INFERENCE — acceptance requirements for this defect, not a claim of whole-emulator C++ safety:**

- **M1:** Each output/scratch/backing pointer must originate in its actual array object. Adjacent members, allocator slack and accessible addresses are not array capacity.
- **M2:** Compute eligibility using sufficiently wide scalar offsets before pointer addition. Do not form an invalid pointer and then compare it, subtract it from output, or cast it to an integer to “validate” it.
- **M3:** A formed pointer may equal one-past the array, but no read/write may use that position and no increment may advance beyond it.
- **M4:** Prove A and B bases, optional field adjustment, all 512 horizontal samples per row and final cursor positions. In non-interlace both rows must fit; in interlace A/B are separate cursor variables pointing into the same selected row.
- **M5:** Prevent invalid formation even on V=0 or V>240 no-store paths. Preserve Screen math/CGRAM initialization when changing only its pointer setup.
- **M6:** Prove each clear range and every fill address/extent independently of Screen eligibility.
- **M7:** Valid retained stores must keep their native order: first sample's lookup and B/A assignments precede the second sample's lookup and assignments. Do not add output readback.
- **M8:** Initialize all storage that can be read/presented; reconstruct transient cursor/eligibility state correctly after supported save/load/reset paths.
- **M9:** Keep framebuffer storage disjoint from lightTable and other native state. A layout-dependent neighbor write is a defect to eliminate, not a compatibility target.

Source arithmetic yields complete row alignment for the present geometry, but that does not authorize unchecked arithmetic or reliance on a particular compiler layout. Any narrower eligibility check must document why it covers all intermediate pointers and increments.

## 17. Candidate comparison matrix

**INFERENCE:** “Capable” means a complete design could meet the requirement; no implementation has been verified. A means a completed capacity/formation design, B means destination-bounded stores after computation, and D includes an explicit A or B storage policy. Clear handling is required in every complete design.

| Family | Defined formation / stores / clear | V=240 execution | Callback + centering | Mixed controls | Interlace |
| --- | --- | --- | --- | --- | --- |
| A, complete padded design | Capable; 512×512 alone fails pointer envelope | Preserved | Preserved | Capable from latched geometry | Preserve field alias/retention |
| B, complete bounded design | Capable with scalar-first eligibility + separate clear | Preserved | Preserve all valid writes | Capable; independent of live vdisp | Must prove both/aliased rows |
| C-render alone | Fails completeness | Changes state/work | Metadata same; content risk | Unsupported assumptions | Changes execution/retention |
| C-store alone | Fails mixed-state stores, pointers and clear | Can preserve | Some valid writes omitted | Insufficient | Border/old-field risk |
| D + explicit A/B policy | Capable | Preserved by construction goal | Preserved | Explicit separation | Explicit separation |
| E, scratch + clear policy | Capable with bounded scratch lifetime | Preserved | Intended to preserve | Capable | Extra alias/lifetime work |

| Family | Native semantic scope | Testability of intended difference | Reference impact | Hardware assumptions unresolved |
| --- | --- | --- | --- | --- |
| A | Retains late persistence; changes allocation/UB effects | Bounds, output/tail, state and callback comparisons | New binary; targeted then migrated experiments | Why late work exists; tail necessity |
| B/D | Omits unpresented persistence; retains computation | Compare full native state and callback against A | Same staged requirement; equality not promised | Whether any intended consumer needs omitted tail |
| C-render | Deletes work with demonstrated state effects | Requires timing/register/hardware comparisons, not hashes alone | Potentially broad baseline change | Hardware legitimacy of deleted execution |
| C-store | Deletes some valid writes in addition to tail | Mixed-mode and stale-border counterexamples | Targeted plus migrated-scope validation | Correct alternate visibility/clear policy |
| E | Redirects unpresented persistence to scratch | State/callback comparison; scratch/lifetime checks | Similar to B/D | Tail lifetime/consumer assumptions |

A/D and B/D merit controlled comparison. C does not become acceptable merely by producing matching framebuffer hashes in a stable-mode game.

## 18. Deterministic-reference implications

**INFERENCE — applies to every implemented candidate:** A source change creates a new executable/baseline identity. Record source revision/diff, compiler/configuration, binary hash, input/settings/SRAM identities and exact validation boundary. Do not relabel an old run as if it used that candidate.

| Family | First necessary validation if later authorized | EXP-001/002/003 implications |
| --- | --- | --- |
| A / A+D | Complete pointer/store/clear envelope, initialization and layout isolation; execution-state and callback comparisons | Rebuild/revalidate each experiment whose claim is carried onto the new baseline |
| B / B+D | Same, plus preservation of valid border writes, all computation/latches, mixed modes and omitted-tail effects | Same migrated-scope requirement; compare to original references before deciding whether new sequences are necessary |
| C-render | Broad timing, OBJ flags/OAM, memory-port behavior, internal state, borders and hardware-oriented evidence | More extensive execution/semantic revalidation likely; amount UNKNOWN |
| C-store | Prove mixed-mode safety and explain changed valid stores/clearing before treating it as a viable baseline | Original scopes plus targeted changed-presentation histories; amount beyond that UNKNOWN |
| E | Scratch alias/lifetime/reset/restore and all B/D comparisons | Same staged requirement as B/D |

Existing EXP-001/002/003 results remain historical evidence for their original binaries and tested conditions. They do not become invalid automatically, and they do not automatically validate a new baseline.

Do **not** regenerate expected hashes first and call the result a pass. Preserve original reference sequences, compare each candidate against them and against the other candidate, and investigate differences. If sequences remain identical, record the new binary's successful comparison without pretending the old artifact came from that binary. If a difference is justified, retain the old evidence and publish a separately attributed new reference/disposition.

Targeted host regression may justify continued candidate exploration. It is not sufficient by itself to transfer real-ROM framebuffer/passivity/provenance conclusions to a corrected baseline. Before EXP-004 resumes on such a baseline, rerun the relevant previously documented EXP-001/002/003 scopes and focused new cases; exact scope beyond that depends on observed differences. No such validation occurred in this task.

## 19. Upstream-review considerations

**INFERENCE:** A narrowly reviewable upstream-style change is plausible if it separates a source-proven bounds correction from broader rendering semantics. A small change in source-line count is not enough: it must cover stores, no-store pointers, transition clearing and initialization/restore implications.

Before considering an issue or PR, assemble:

- Exact upstream revision and minimal source/arithmetic reproduction of each failing path, including PAL V=312.
- The allocation/render/clear introduction history and a clear statement that the exact donor is unknown.
- A defined-memory demonstration and, where available, suitable sanitizer evidence for the real candidate. P0's defined-storage fixture does not prove exact native UB behavior.
- Execution-state evidence, especially V=240 OBJ range-over/OAM behavior, mixed-mode CGRAM-latch effects, cycle/event timing and both interlace fields.
- Callback/reference comparisons with documented inputs, plus expected versus unexpected differences.
- A clear policy for unpresented backing and transition clearing; performance/memory and serializer/restore implications.
- A separate statement of unsupported hardware claims and any outstanding source-consumer assumptions.

No issue, PR or message was opened or sent. Any future upstream submission needs its own authorization.

## 20. Remaining unknowns

- Exact donor higan revision and its storage/execution contract.
- Hardware correctness/necessity of the complete V=240 pipeline, although CPU-visible source consequences are established.
- Exact native optimized UB behavior, actual affected ROM/control histories and compiler/layout sensitivity.
- Whether retaining versus omitting unpresented samples has any intended consumer effect outside the inspected cycle-PPU presentation path.
- Candidate behavior under live overscan/interlace changes, force-blank changes, brightness/hires changes and CPU I/O interleaving.
- Complete save/load, stack-restored mid-line state, rewind/run-ahead and opposite-field retention behavior.
- Performance cost and the minimal maintainable representation for safe pointers/eligibility.
- Whether historical deterministic references will match a candidate and how much broader validation any differences require.
- Any newer upstream fix/discussion not represented by the available local history.

## 21. Recommended next experiment

**INFERENCE — next-experiment option B: comparative prototypes are warranted in a separately authorized task; no final fix is accepted.**

The leading comparison is:

1. **A with complete pointer safety:** keep logical late stores in valid backing while preserving presentation and native execution. Prove capacity or avoid unnecessary late pointer formation; do not assume 512×512 solves everything.
2. **B using D:** keep identical computation, timing, latches and all valid presentation stores, but omit stores outside that explicit contract; use scalar-first eligibility and a defined transition clear.

Hold all other semantics constant. This isolates whether unpresented persistence matters, instead of confounding a memory correction with deleting PPU execution. E is optional only if a concrete need for scratch arises. A wholesale vdisp render gate is not a leading comparator.

The smallest useful first stage would be a **controlled host comparison**, separately authorized, with no need to begin by executing native invalid accesses. It should cover:

- Source-derived NTSC/PAL counters through V=312, both fields and all placement controls, including no-store pointer formation and post-store cursors.
- The source-constructed V=240 >32-eligible-OBJ witness, address resets, forced blank and CPU-readable status; validate that storage policy leaves these effects unchanged.
- Live/latched overscan divergence, interlace transitions and CPU CGRAM accesses on valid-active but out-of-output V=233..239.
- On→off border clearing before frame presentation, both field rows, power/reset, and supported serialization/restore paths.
- Both native sample slots, hires/lowres, brightness lookup order, carried Screen math, and comparison of native state independently of pointer addresses/storage-layout differences.
- Guard/sanitizer evidence appropriate to the actual candidate, then staged deterministic runtime comparisons only if separately authorized.

Identical candidate outputs/states would support further review, not prove hardware correctness or universal compatibility. Differences require diagnosis before either baseline is accepted. A smaller “run the undefined baseline and see whether it crashes” experiment is not a prerequisite for this controlled comparison and would not settle the contract.

## 22. EXP-004 impact

**EXP-004 color-math provenance implementation remains unauthorized.**

Its disposition remains **STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION**. Phase 2 supplies a candidate-review contract and a recommendation for the next experiment; it does not complete the native-baseline disposition or authorize prototypes.

The gate remains: complete the separately scoped native-baseline investigation, document its disposition, and explicitly re-authorize implementation. No EXP-004 worktree or experiment rule was changed. No native source/test changes, builds, tests, ROM runs, ADR, commit or push occurred; `PROJECT_STATE.md` remains untouched.
