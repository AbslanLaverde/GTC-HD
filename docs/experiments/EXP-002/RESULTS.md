# EXP-002 — OBJ / Sprite Provenance Preservation

Date: September 20, 2026.

**Status: IMPLEMENTED; UCRT64 DESKTOP BUILD AND FOCUSED HOST TESTS PASSED; ROM RUNTIME VALIDATION PENDING.** No ROM was loaded or executed. This implementation pass does not verify EXP-002's native framebuffer hypothesis. No commits, ADR, emulator selection, or accepted architecture changes were made.

## 1. Question, authority, and repository identity

Can a native cycle-PPU OBJ candidate retain its originating OAM object and fetched tile lineage while the original OBJ implementation remains authoritative?

The workspace is `<GTC-HD-Lab>`. Project authority remains under `docs/`. Root `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/research/BSNES_ARCHITECTURE_AUDIT.md`, and `docs/experiments/EXP-002/SPEC.md` were read before implementation. Older `project/` references in historical reports do not override that authority. The project remains Phase 0; bsnes and the interception boundary remain **INVESTIGATING**.

| Source checkout | Branch | Exact HEAD, unchanged by this task |
|---|---|---|
| Writable `experiments/bsnes-exp-002/` | `gtc-hd/exp-002-obj-provenance` | `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919` |
| Read-only `upstream/bsnes` | `master` | `7d5aa1e656b9171524d01b1b22917197d8121cb4` |
| Read-only `experiments/bsnes-exp-001/` | `gtc-hd/exp-001-passive-ppu-observation` | `ba148bedc74892722de93633ce08190dda406bf7` |
| Read-only `experiments/bsnes-exp-001-baseline/` | `gtc-hd/exp-001-runtime-harness` | `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919` |

The EXP-002 Git root is `experiments/bsnes-exp-002/`. It is a linked worktree, with administrative directory `upstream/bsnes/.git/worktrees/bsnes-exp-002` and common directory `upstream/bsnes/.git`. It started clean at the required runtime-harness commit. Source changes remain uncommitted and unstaged on that branch; HEAD still equals the starting commit. Its pre-existing harness has no BG observer. The other three source checkouts were only inspected. Canonical project state, instructions, and specifications are unchanged.

Evidence labels: **SOURCE OBSERVATION** means inspected code; **HOST TEST** means synthetic host execution with the limits below; **INFERENCE** means an implication not established through ROM execution; **UNKNOWN** means still untested. All source paths in this report are relative to the EXP-002 repository unless prefixed with `docs/` or another workspace directory.

## 2. Problem and source findings

**SOURCE OBSERVATION — evaluation.** `bsnes/sfc/ppu/object.hpp` defines decoded `OAM::Object` values and native `Object::Item {valid,index}`. `Object::scanline()` latches `io.firstSprite`, resets counters, toggles `t.active`, and clears the producer bank's item/tile validity. `Object::evaluate()` in `object.cpp` computes the seven-bit OAM slot from `latch.firstSprite + index`, calls `onScanline()`, and stores up to 32 qualifying items. The 33rd increments `itemCount` to 33 without being stored; later evaluation calls return. The observer records rejected qualification only when native code actually performed that qualification; it does not re-evaluate skipped objects.

**SOURCE OBSERVATION — fetch and identity loss.** `Object::fetch()` visits the 32 item slots in reverse. `oamItem[i].index` still names the source object. Native code derives object row, field/interlace/V-flip adjustments, character-bank address, tile width, and per-subtile row address. `Object::Tile` stores only `valid,x,priority,palette,hflip,data`. It loses the OAM index, evaluation association, character address, and source row. This is the identity gap EXP-002 bridges.

**SOURCE OBSERVATION — lifetime.** Evaluation and fetch use `t.item[t.active]` and `t.tile[t.active]`; `Object::run()` consumes `t.tile[!t.active]`. Thus a fetched tile is consumed on the following scanline. `main.cpp` schedules evaluation every eight PPU clocks through H=1016, begins OBJ fetch at H=1080, and calls `obj.run()` before `window.run()` and `screen.run()`. Render X advances from 0 to 255; the corresponding H values are 58 + 4*X. H-counter clocks, native OBJ pixels, callback indices, and framebuffer coordinates are different units.

**SOURCE OBSERVATION — overlap.** `Object::run()` visits native fetched slots 0 through 33, stopping at the first invalid slot. Coverage uses `x - (int9)tile.x`. The four bitplanes produce a color nibble; zero is transparent. Each nonzero sample overwrites the palette and mapped priority on every enabled main/sub output. The **last nontransparent covered slot visited** survives intra-OBJ overlap. It does not select the highest raw OBJ priority. Raw priority is mapped through current `io.priority[]` for later BG/OBJ composition. A transparent later tile leaves the previous candidate intact.

**SOURCE OBSERVATION — temporal inputs.** Fetch holds `x`, adjusted `y`, `tileWidth`, `tiledataAddress`, `chrx`, and `chry` across the subtile loop. Each four-clock `ppu.step()` can yield to the CPU. Later subtiles can therefore encounter changed live OAM attributes, while their address/row calculations still use earlier locals. The observer snapshots item-wide address/row inputs before the first yield, and copies palette/priority/H-flip from each actual native tile when that tile is formed. It never labels an earlier address calculation with a character value reread after a later yield.

**SOURCE OBSERVATION — execution-visible behavior.** Evaluation updates `ppu.latch.oamAddress` after qualification, including the 33rd qualifying object; fetch updates it to `0x0200 + (item.index >> 2)`. `addressReset()` and `setFirstSprite()` maintain native address/rotation state. `io.cpp::readOAM/writeOAM` use the latch during active display; `$213e` reports `timeOver` and `rangeOver`. Native fetch performs the original conditional VRAM plane reads and two four-clock steps per retained tile, and sets overflow flags from item/tile counts. None of those operations is replaced by observation.

## 3. Strategy comparison and implementation finding

| Option | Assessment for this experiment |
|---|---|
| A. Extend native `Item`/`Tile` | Feasible if excluded from explicit serialization, but unnecessarily changes native structure layout and ownership. |
| B. Parallel item/tile storage | Matches the two banks directly and isolates provenance from native decisions. Requires clearing the same producer bank at each switch. |
| C. External fetch-slot mapping | Preserves tile ownership economically, but alone cannot identify which sample survived overlap. |
| D. Per-pixel sidecar alone | Can retain the winner only if earlier fetch identity has already survived; cannot recover it from reduced native tiles. |
| E. Small hybrid | **Selected:** parallel item/fetch ID maps plus one transient pixel sidecar, with an ordered evaluation/fetch/winner stream. |

**Implementation finding:** `Exp002::OBJObserver` owns `items_[2][32]`, `tiles_[2][34]`, a single pending pixel record, and bounded copied records. Native `Object::Item`, `Object::Tile`, `Object::State`, `Object::Output`, and `OAM::Object` are unchanged.

The provenance chain is:

1. A selected evaluation record ID is associated with its native producer-bank item slot.
2. Each fetch record links to that evaluation ID and retains the actual OAM slot, address/row/subtile context and copied native row data. Its ID is associated with the native producer-bank tile slot.
3. In the existing nonzero-color branch, the observer updates its pending winner from the consumer-bank tile ID. It follows the native traversal without changing or ranking it.
4. After `Object::run()` finishes, one winner record retains the last sample plus the actual main/sub output values, before windows or BG/OBJ composition execute.

For overlap evidence, a winner also retains the number of nontransparent covered samples and the **immediately preceding overwritten sample's** fetch ID, source X, color nibble, and palette index. Earlier losers are deliberately not exported. There is no all-sample event stream and no per-frame image-sized sidecar. This is experimental diagnostic storage, not a proposed production GTC-HD API.

## 4. Exact record and field semantics

There is one CSV stream, schema `exp002_obj_version=1`, with three `kind` values: **1 Evaluation (E), 2 Fetch (F), 3 Winner (W)**. Records have monotonically increasing one-based IDs within one capture batch. All numeric columns are unsigned decimal. Inapplicable fields are zero, **not evidence that a real hardware value was zero**. Use `kind`, links, and validity fields to interpret them. No native pointers are exported.

| Exported field(s) | Applies | Exact meaning |
|---|---|---|
| `id` | E/F/W | One-based retained-record ID. Zero is reserved for absent/unknown references. IDs restart after clear; do not join separate CSV batches by ID. |
| `kind` | E/F/W | 1 evaluation, 2 fetched row, 3 surviving nontransparent sample. |
| `frame` | E/F/W | Observer-owned count of cycle-PPU V=0 boundaries since power/reset/load; first is 1. Not a callback index or persistent game frame ID. |
| `evaluation_id` | F/W | F links to the selected evaluation; W copies that link from its fetch. Zero means unavailable (e.g. activation mid-pipeline or overflow). |
| `fetch_id` | W | Link to the actual fetched row that supplied the surviving sample. |
| `previous_fetch_id` | W | Link to the immediately preceding nontransparent sample overwritten at this X. Zero means no preceding sample or unavailable lineage; consult `nontransparent_samples`. |
| `row_data` | F | Copied native 32-bit fetched-row data: plane bytes 0/1 from the first word in bits 0..15; plane bytes 2/3 from the second word in bits 16..31. Never an additional VRAM read. Interpret partial reads with `read_mask`. |
| `h`, `v` | E/F/W | Native PPU horizontal counter in master-clock units and vertical scanline. E at qualification; F immediately before the first plane-read condition for this tile; W at completion of `Object::run()`. F is appended after the second read condition, before the final four-clock step, but retains its start timing. |
| `field` | E/F/W | Native PPU field bit at that stage, not callback parity. |
| `screen_x` | F/W | F: native nine-bit tile origin 0..511; native coverage interprets it as signed `int9`, so 508 means -4. W: current native OBJ screen X 0..255. Neither is the doubled 512-wide framebuffer sample index. |
| `object_x`, `object_y` | E/F | Raw decoded OAM X 0..511 and Y 0..255. E snapshots qualification time. F snapshots item-wide input before any tile-fetch yield; these are not reconstructed from output coordinates. |
| `row_address` | F | Sixteen-bit **VRAM word address**, `(pos & 0xfff0) + (adjusted_y & 7)`, before the VRAM mask. Not a byte address or OAM address. |
| `vram_mask` | F | Native word-address mask at tile fetch (normally 32767). Effective plane-pair addresses are `(row_address + 0) & mask` and `(row_address + 8) & mask`; multiply by two for byte addresses. |
| `tile_character` | F | Adjusted character index `chry + ((chrx + source_tile_x) & 15)`, 0..255 within the selected bank. Includes source row's tile subdivision and horizontal tile selection. It is not the raw OAM character or an immutable asset ID. |
| `object_row` | F | Native local `y` after vertical flip/rectangular-size rules, interlace scaling, field adjustment, and final `&255`. Source coordinate, not screen Y. |
| `buffer` | E/F/W | Native bank 0 or 1: producer `t.active` for E/F, consumer `!t.active` for W. Reused every other scanline; IDs disambiguate lifetimes. |
| `slot` | F/W | Native fetched-tile slot 0..33 in that bank. W names the surviving slot. |
| `oam_index` | E/F/W | Seven-bit hardware OAM slot 0..127. W copies the captured F value; meaningful only with a nonzero fetch link. Zero alone cannot distinguish valid OAM slot 0 from unavailable lineage. |
| `evaluation_order` | E | Native evaluation argument 0..127 before addition of the latched first sprite. |
| `item_slot` | E/F | E: itemCount before native increment, 0..32; only `selected=1` gives a valid selected slot 0..31. F: actual selected item slot 0..31 consumed by fetch. |
| `first_sprite` | E/F | Latched first OAM slot determining priority rotation for that scanline. Captures the ordering input, not a persistent entity order. |
| `qualified`, `selected` | E | Result of the single native `onScanline()` call, and whether qualification fits the first 32 items. The 33rd qualifying evaluation has `qualified=1, selected=0`. No records are invented for early-returned evaluations. |
| `character`, `nameselect` | E/F | Raw eight-bit OAM character and one-bit OAM character-bank selector. F copies the item-wide inputs used to calculate held character/bank locals, before yields. Resolved bank location is represented by `row_address`. |
| `size`, `base_size` | E/F | Raw OAM size bit and three-bit OBJ base-size configuration at qualification/item preparation. These select native size tables; they are not dimensions. |
| `palette_group` | E/F | Three-bit OBJ palette group 0..7. F is derived from the actual native tile's palette base, so changes between subtiles are represented. |
| `palette_base` | F | Native `128 + 16*palette_group` in CGRAM entry units, 128..240. No CGRAM lookup is made. |
| `raw_priority` | E/F | Raw two-bit OAM priority 0..3. F copies the actual native tile priority. It does not decide intra-OBJ overlap. |
| `resolved_priority` | F/W | Numeric bsnes mode-dependent rank from `io.priority[raw_priority]`. F observes it at tile construction; W observes the actual pixel-time mapping. These need not match after an intervening mode change. W's source raw priority is found through F. |
| `hflip`, `vflip` | E/F | E snapshots raw OAM flags. F H-flip is copied from the native tile (per-tile input); V-flip is the earlier item-wide input used for held row calculations. |
| `interlace` | E/F | Native OBJ interlace flag at qualification/item preparation. Distinct from the overall display interlace flag. |
| `tile_width` | F | Native item-wide sprite width divided by 8: number of horizontal 8-pixel subtiles, not pixels. Captured from `tileWidth`. |
| `tile_x`, `source_tile_x` | F | `tile_x` is left-to-right screen subdivision `tx`; `source_tile_x` is native `mx`, reversed within the held width when H-flipped. They are not VRAM coordinates. |
| `source_x` | W | Source pixel 0..7 within the fetched character row, left-to-right in the unflipped tile. Computed as `7-shift` from the already decoded native bit selection; H-flip is reflected in this coordinate. |
| `source_y` | F | Character-row source Y 0..7, equal to `object_row & 7`; already V-flip/interlace/field adjusted. W obtains it through F. |
| `read_mask` | F | Bit 0: first native plane-pair read executed; bit 1: second executed. 3 means both. A skipped read may leave zero or reused native data; the observer copies that native result but does not claim a complete fresh source row. |
| `color` | W | Nonzero decoded four-bit OBJ color 1..15 before CGRAM resolution. Transparent color 0 never produces or replaces an observer winner. |
| `palette_index` | W | Actual winning tile palette base plus color, in CGRAM entry units, before palette lookup or color math. |
| `nontransparent_samples` | W | Number of covered nonzero samples visited at this X, 1..34. Greater than one establishes native intra-OBJ competition. |
| `previous_source_x`, `previous_color`, `previous_palette_index` | W | Source pixel, color nibble, and CGRAM index for the immediately preceding overwritten sample. Same units as the winning fields. Valid as a losing sample when `nontransparent_samples>1`; its source lineage requires a nonzero `previous_fetch_id`. |
| `source_known` | W | True only if the winning fetch record exists, links to an evaluation record, and has both read bits set. False avoids silently assigning source identity to reused/partial/uncaptured data. |
| `main_enabled`, `sub_enabled` | W | OBJ screen enables at native pixel production, before window masking. If both are false, W describes the surviving sample only; no enabled-screen candidate was supplied. |
| `main_priority`, `sub_priority` | W | Actual native output priority after the complete OBJ loop. Zero means no candidate on that screen. |
| `main_palette`, `sub_palette` | W | Actual native palette index on an enabled screen. Disabled-screen entries are explicitly recorded as zero because native palette storage there can be stale. Consult enable/priority fields. |
| `bg_mode`, `forced_blank` | W | Current native BG mode and display-disable flag at this output stage. They describe context, not final visibility. |

**Lineage example:** W → `fetch_id` F → `evaluation_id` E. W supplies screen position, winning source X, color/index and native outputs; F supplies OAM identity, selected source row, adjusted character, VRAM word addresses and copied row data; E supplies qualification and selection order. No link is reconstructed from current OAM or current VRAM. F and E may legitimately differ in attributes because native fetch can occur after OAM changes.

## 5. Passivity, state isolation, and bounds

**SOURCE OBSERVATION:** Added hooks copy decoded objects, native locals, completed native tile data, and native outputs. There are no added `OAM::read()`, `readOAM()`, VRAM index operations, CGRAM lookups, bus reads, calls to `ppu.step()`, or scheduler calls for observation. The native qualification call still executes once. The native plane reads, clipping tests, limits, iteration directions, transparent branch, palette/priority assignments and latch/status updates remain authoritative.

`object.hpp` and `oam.cpp` are unchanged. The complete native `Object::serialize()` body is unchanged. The observer lives outside PPU native structures and contributes **zero bytes** to emulator save state. At PPU power/reset the observer disables and clears, including the V=0 counter. At PPU deserialize (`serializer::Load`) it also disables and clears, before native state loading, to avoid attaching old provenance to restored tiles. Save/size modes add no observer work or serialization fields. Serialization was not redesigned.

At a scanline switch, only the new producer bank's ID maps are cleared; the consumer bank remains available for the native tile lifetime. Capture clear invalidates both banks and pending pixel state, resets IDs/counts/drop status, and preserves enable state and frame count. Each pixel begins with a cleared pending sidecar. Arming starts with disable/clear/enable. If native tiles predate arming, their samples have unknown source instead of stale references. A reset/load during an observed run disarms the observer and the window fails; general interactive lifecycle capture is not supported.

The stream capacity is **131,072 records**, each **104 bytes** on the tested UCRT64 compiler: **13,631,488 bytes (13 MiB)** reserved for records, plus small maps/counters. Count/volume refer to retained records, not CSV text size. Append retains the prefix, returns zero for a dropped link, saturates the 64-bit dropped counter, and sets overflow explicitly. There is no overwrite or automatic capacity increase. The stream is intentionally diagnostic and has no pointers to later mutable native data.

PPU hooks perform no file I/O, allocation, external callback, or cross-thread access. All export happens after a core run returns. Host cost, worst-case actual callback volume, and native behavior under real workloads remain **UNKNOWN**. A successful host build does not prove runtime passivity.

## 6. Runtime window and diagnostic output

The original `exp001-frame-hash.hpp`, SHA-256 algorithm, and `Program::videoFrame()` hook are unchanged. EXP-002 uses that same harness for both B and C. The frontend window controller adapts the EXP-001 implementation without bringing in its BG observer.

Required together for C:

```text
--exp002-obj-csv=<NEW_OUTPUT_PATH>
--exp002-obj-start-callback=<N>
--exp002-obj-callback-count=<M>
```

The frame-hash output option must also be present. N is a nonnegative decimal uint64; M is positive. The checked half-open interval `[N,N+M)` must fit the requested hash callback count. Duplicate, incomplete, malformed, overflowing, unknown EXP-002 options and out-of-range intervals fail before emulation. No EXP-002 options means no observation, provenance output, summary, or extra settings guard.

`beforeRun()` observes the hasher's completed-callback count immediately before the ordinary `emulator->run()`. When it equals N, it disables/clears/enables capture. `afterRun()` requires exactly one new callback; after callback N+M-1 it disables and exports, before another run. Activation/export never happens inside `videoFrame()`. For N=500/M=1, arming precedes the run producing callback 500; that callback raises the completed count to 501; disarming/export follows that run's return.

The window is a **callback-producing run interval**, not an assumed V=0-to-V=0 period. The cycle callback occurs at display boundary `vdisp()`. A run can contain trailing nonvisible scanlines from one observer frame and visible work from the next; its CSV can legitimately contain multiple `frame` values. The summary provides callback identity, while records provide native frame/field/scanline timing.

Observation rejects automatic state loading, fast PPU, run-ahead, rewind recording/rewinding, and fast-forward. Use cold starts, no UI/state/reset/reload operations, fixed neutral input, identical settings/SRAM/ROM seeds, cycle PPU, no cheats, no blur or cursor overlays, and the EXP-001 deterministic-run settings. The tool does not silently change settings. These remain operator requirements for the later ROM runs.

Output is protected by exclusive file creation and a private sibling `<OUTPUT_PATH>.exp002-tmp` staging directory, followed by copy-without-replacement publication. Existing output, summary, staging directory, frame-output aliases and late collisions are rejected. The summary is `<OUTPUT_PATH>.summary.txt`. Export checks write/close and publication failures. The narrow staging filename API has only been tested with ordinary ASCII output paths; no general Unicode-path claim is made.

The summary contains requested start/count/end, started/completed, observed/total native callbacks, total/evaluation/fetch/winner retained counts, record size and retained bytes, capacity, dropped count, overflow, unknown winners, observer frame/enabled status, export attempted/succeeded, completeness and reason. `window_completed` is distinct from `capture_complete`: completeness also requires successful export, no drop/overflow, no unknown winning source, and no controller error. It does **not** mean the experiment is verified or that the callback contained sprites.

Overflow/unknown-source results can finish the native hash sequence but exit nonzero for incomplete provenance. Export/callback errors stop the run. Early quit exports a partial started window, or no CSV if it never started, with incomplete status. Require both process exit status and final CSV/summary status; a disk failure can leave an incomplete file. No file or summary is created for B.

## 7. Build and tests actually performed

Toolchain: existing **MSYS2 UCRT64**, **g++ 16.2.0 (Rev3, Built by MSYS2 project)**. No tools or dependencies were installed. A complete desktop build from this checkout and subsequent incremental rebuilds succeeded with exit **0**.

From `experiments/bsnes-exp-002/` in a non-login UCRT64 shell (replace `<OUTPUT_DIR>` with the absolute generated evidence directory; `<BSNES_EXE>` below denotes the built desktop executable):

```sh
export PATH=/ucrt64/bin:/usr/bin:$PATH
mkdir -p "<OUTPUT_DIR>"
export TMPDIR="<OUTPUT_DIR>"
make -j4 -C bsnes local=false
python tests/exp002/run-tests.py validation-final
```

The desktop build retains upstream performance/O3, C++17, OpenMP and `local=false` settings. The full build emitted **77 warnings in unchanged upstream code** (BML casts, Game Boy visibility attributes, and an existing Game Boy overflow warning). The final incremental PPU build emitted one existing BML cast warning. **Zero warnings were attributable to EXP-002 source.** The final focused tests build with `-Wall -Wextra -Werror`; the native OBJ fixture explicitly suppresses existing upstream parenthesis, unused-variable, and signed-comparison diagnostics. The added observer/window code has no such suppressions.

Executable: `<BSNES_EXE>`, **9,740,170 bytes**.

SHA-256: `9817AE51988FCF85B50642DEA82498E142D68734981E183F42F5E22CEA5FBBB0`.

| Focused verification | Result and scope |
|---|---|
| Actual `object.cpp`/`oam.cpp` host fixture | Passed OAM retention, native reverse fetch/order, lower-priority overlap winner, priority rotation, later-transparent nonreplacement, double-bank lifetime/reuse, no stale IDs after clear/reset, and main/sub gating. |
| Temporal mutation fixtures | Passed mutation of OAM/VRAM after fetch, mutation across a plane-read yield, and mutation between larger-sprite subtiles. Held item inputs remain held; native per-tile changes are represented. Partial fetch cannot claim complete lineage. |
| Limits and source coordinates | Passed native 33rd-item/35th-tile overflow, 34 actual tile fetches, 68 VRAM reads/272 clocks, wrapped X, H/V flips, larger subtiles, and an interlaced-row case. These are synthetic cases, not comprehensive hardware validation. |
| Native-state comparison | Same fixture compiled against unmodified HEAD `object.cpp` and instrumented code has identical serialized OBJ/latch/read/clock signature for the overlap scenario. Observer-disabled/enabled versions also match native serialized state/read/latch/clock values for overlap and overflow fixtures. |
| Window tests | Passed synthetic B/C identical hash CSVs across 600 callbacks, capture 500 only, start=0, one/multiple/last/full windows, partial/never-started quit, exactly-one-callback guards, clear-at-arm, and reset/disabled behavior. |
| Bounds and incomplete evidence | Passed capacity+2 drop reporting with retained prefix, explicit overflow, continued native hashing, and unknown-source capture reported incomplete. |
| Parser/output behavior | Passed arithmetic bounds, partial/duplicate/invalid options, existing output/summary, alias, late collision and export failure. **26 desktop CLI rejection cases** passed before settings/frontend initialization, using a plain text argument-existence sentinel. |
| Existing frame hasher | Unchanged regression tests passed known LE16 hashing, padding, metadata/counts, disabled behavior and exclusive output. The header and native callback hook are byte-for-byte unchanged after newline normalization. |
| CSV and lineage export | Parsed exported record widths, IDs and kinds; joined the synthetic actual-OBJ winner to fetch/evaluation, and decoded copied bitplanes to reproduce winning and preceding losing color/index values. |

The OBJ fixture compiles actual OBJ/OAM methods with a small substitute PPU timing/memory host, not a full CPU/PPU execution. It extracts the native `Object::serialize()` body verbatim for comparison. Native serialized-state signature for its overlap scenario is `4e5d2fad085fe9c09ce91e1ae01174f77b5b171d406f2c3cfc775d2a9af97364`. This is **not** a framebuffer, ROM, or complete emulator-state digest.

Logs, executables, synthetic CSVs and CLI evidence remain ignored under `<OUTPUT_DIR>/`, including `desktop-build.log`, `desktop-final-build.log`, and `validation-final/`. The test runner requires a fresh evidence directory name. No raw artifacts are added to project documentation or committed.

## 8. Architectural learning, product relevance, and limits

**HOST TEST / INFERENCE:** The tested native OBJ pipeline exposes sufficient earlier information to carry an explicit OAM → selected item → fetched row → surviving nontransparent sample relationship without asking later OAM/VRAM to reconstruct it. The bank association and overwrite order are essential. A late palette/priority pair alone cannot supply this lineage.

This could support later sprite-aware enhancement, asset identification, lighting/emissive interpretation, materials, replacement graphics, spatial reasoning and debugging by providing source rows, palettes, placement and hardware ownership. None of those future systems is implemented. Asset meaning, lighting intent and persistent identity would require additional evidence and interpretation.

An **OAM slot is reusable hardware identity**, not Mario, an enemy, a torch, or a stable game entity. A fetched-row ID is unique only within this diagnostic batch. Source tile numbers and VRAM addresses can also be reused or mutated.

A **native OBJ winner is not final framebuffer visibility**. The record is captured before `window.run()` and `screen.run()`. Windows may reject it; BG priority may beat it; main/sub composition, palette resolution, OBJ color-math eligibility, blending and brightness may change the eventual output. No BG, Mode 7, compositor, or GPU instrumentation is added.

**UNKNOWN / limitations:** real-game A/B/C framebuffer equality; complete CPU-visible PPU-side-effect equality; actual record volume and host cost; broad sprite-size/interlace/rotation/range/time-limit cases; dynamic mode/forced-blank/OAM changes across real raster timing; save/load and rewind interaction beyond deliberate invalidation; PAL/overscan transitions; start-of-window pre-existing tiles; Unicode export paths; and persistent scene/asset identity. The observer does not continue lineage across a state load and deliberately excludes capture with speculative/rewind execution.

**Architectural implication:** source inspection plus focused host tests support the feasibility of carrying this bounded OBJ lineage slice alongside native work. They do not establish universal capture sufficiency, a production graphics-state interface, a final semantic-preservation architecture, or bsnes as the selected foundation.

## 9. Recommended next validation and exact command templates

The next step is user-run deterministic A/B/C ROM validation. A is the harness-only executable at baseline `906f74b6e`; B and C must use the same EXP-002 executable identified above. Restore identical settings seed, SRAM seed, ROM, and input conditions before each run. Record their hashes privately as reproducibility metadata; do not commit ROM/SRAM contents. Use a fresh output filename for every run. Run each template below from the GTC-HD repository root and replace all placeholders before invocation.

B — observer disabled, 600 native callbacks:

```sh
cd experiments/bsnes-exp-002
"<BSNES_EXE>" --settings="<SETTINGS_PATH>" \
  --exp001-frame-hash="<OUTPUT_DIR>/EXP002-B-600-frames.csv" \
  --exp001-frame-count=600 "<AUTHORIZED_ROM_PATH>"
echo "B exit: $?"
```

C — same executable, observe only the interval producing callback 500:

```sh
cd experiments/bsnes-exp-002
"<BSNES_EXE>" --settings="<SETTINGS_PATH>" \
  --exp001-frame-hash="<OUTPUT_DIR>/EXP002-C-600-frames.csv" \
  --exp001-frame-count=600 \
  --exp002-obj-csv="<OUTPUT_DIR>/EXP002-C-callback-500-obj.csv" \
  --exp002-obj-start-callback=500 \
  --exp002-obj-callback-count=1 "<AUTHORIZED_ROM_PATH>"
echo "C exit: $?"
```

Require A=B=C for the entire ordered callback metadata/hash sequence and valid completion footers. For C require start=500/count=1/end=501, one observed callback, complete export, no dropped records/overflow/unknown winners, and the expected 600 total callbacks. Separately inspect actual E/F/W links, nonzero sprite activity, and overlap witnesses; a complete empty capture does not answer the sprite question. Callback 500 is an initial proposed window, not a claim that it contains suitable OBJ overlap in every ROM/state.

Measure bytes/records per observed callback and approximate B/C host time separately from CSV export cost. Expand to deterministic gameplay and adversarial sprite tests only after the first evidence is reviewed. Matching frame hashes alone would still not prove every CPU-visible side effect or final sprite visibility claim.

## 10. Uncommitted review surface

Modified existing EXP-002 files:

- `bsnes/sfc/ppu/main.cpp`: observer frame count.
- `bsnes/sfc/ppu/object.cpp`: passive evaluation/fetch/winner hooks.
- `bsnes/sfc/ppu/ppu.cpp`: observer compilation and reset hook.
- `bsnes/sfc/ppu/serialization.cpp`: observer-only invalidation on native load; no payload changes.
- `bsnes/target-bsnes/bsnes.cpp`: EXP-002 option parsing/preflight.
- `bsnes/target-bsnes/program/program.cpp`: window lifecycle and guards.
- `bsnes/target-bsnes/program/program.hpp`: own the frontend controller.

New EXP-002 files:

- `bsnes/sfc/ppu/exp002-obj-observer.hpp`
- `bsnes/sfc/ppu/exp002-obj-observer.cpp`
- `bsnes/target-bsnes/program/exp002-obj-window.hpp`
- `tests/exp002/.gitignore`
- `tests/exp002/obj-pipeline-test.cpp`
- `tests/exp002/observer-window-test.cpp`
- `tests/exp002/observer-window-cli-test.py`
- `tests/exp002/run-tests.py`

The sole project-document addition is this `docs/experiments/EXP-002/RESULTS.md`. No read-only checkout or canonical project-state file was modified. All implementation and documentation changes are left for review without staging or commits.
