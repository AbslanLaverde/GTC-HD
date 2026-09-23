# EXP-001 — Passive PPU Observation: implementation results

## Current result

**Status:** VERIFIED FOR TESTED EXP-001 CONDITIONS

**Implementation:** Passive tiled-BG observation and runtime callback-window controls are implemented. **Supported build:** The MSYS2 UCRT64 desktop build passed, as recorded in section 12.5.

**Deterministic real-ROM framebuffer passivity:** The retained Super Mario World title-sequence runs A1, A2, B, B2 and C have byte-identical native-frame hash CSVs, each with 600 callbacks and a successful completion footer. The completed B2/C evidence supersedes the pending checkpoint in section 12; this is framebuffer passivity under those tested conditions, not universal execution equivalence.

**BG provenance preservation:** The retained C summary records successful capture of callback 500, with one observed callback, 23,760 records, no drops or overflow, and the observer disabled after export. The real capture retains BG, map-entry, tile/character, source-coordinate, palette, priority and timing information from the native fetch path. This supports preservation of tiled-BG source provenance under the tested conditions; a fetch record does not establish final-pixel visibility.

**Limits and architectural implication:** Complete CPU-visible PPU-side-effect equality, whole-emulator serialized-state equality and runtime overhead are not established by matching framebuffer hashes. Mode 7, complete final-pixel provenance and universal game/PPU-mode coverage remain outside this result. Semantic preservation remains an architectural **HYPOTHESIS** supported by this experiment, not an accepted GTC-HD architecture or selection of bsnes.

The [final-validation addendum](#13-final-validation-addendum--retained-real-rom-evidence) documents the retained artifacts, input fingerprints, executable-identity limits and completed result. This summary is based on that EXP-001 evidence and the accompanying session record; no new emulation run is claimed. The dated implementation checkpoints below remain historical records.

## Public implementation

Public fork: [AbslanLaverde/bsnes](https://github.com/AbslanLaverde/bsnes). The observer tip includes the runtime-window controls described in section 12.

| Identity | Commit / source |
| --- | --- |
| Historical implementation commit | `ba148bedc74892722de93633ce08190dda406bf7` |
| Public research equivalent | [5ba4d2a8b12a82a09db1f76640e659303aef7e22](https://github.com/AbslanLaverde/bsnes/commit/5ba4d2a8b12a82a09db1f76640e659303aef7e22) |
| Public branch | [gtc-hd/exp-001-passive-ppu-observation](https://github.com/AbslanLaverde/bsnes/tree/gtc-hd/exp-001-passive-ppu-observation) |
| Unchanged upstream baseline U | `7d5aa1e656b9171524d01b1b22917197d8121cb4` |

[Compare upstream U → public observer tip](https://github.com/AbslanLaverde/bsnes/compare/7d5aa1e656b9171524d01b1b22917197d8121cb4...5ba4d2a8b12a82a09db1f76640e659303aef7e22). See the [specification](SPEC.md) for scope and the [publication map](../../research/BSNES_EXPERIMENT_PUBLICATION_MAP.md) for rewrite details.

The dated implementation passes below retain their original HEADs, uncommitted-source fingerprints, executable hashes and runtime evidence. Those builds are not reattributed to the public equivalent. The historical runtime-harness identity and its public equivalent remain separate in the [runtime-harness report](RUNTIME_HARNESS_RESULTS.md#public-implementation). Publication validation does not change EXP-001's recorded verification status.

## Historical implementation checkpoints — September 18–19, 2026

The following opening notes and sections 1–11 describe the September 18 implementation pass; section 12 records the September 19 runtime-controls pass. Build blockers, pending validation, proposed commands and statements that EXP-001 had not passed describe those points in time. The [current result](#current-result) above incorporates the later completed runtime evidence.

**Latest update — September 19, 2026:** Observer runtime callback-window controls are implemented and the supported UCRT64 build passed. B2/C ROM validation remains pending. See [section 12](#12-runtime-observer-window-controls--september-19-2026). Sections 1–11 below retain the historical September 18 implementation-pass results, including its then-current build blocker; they are not the current build status.

**Date:** September 18, 2026  
**Status:** IMPLEMENTED / RUNTIME VALIDATION PENDING  
**Desktop build:** BLOCKED by the available toolchain  
**Experiment outcome:** Not established. EXP-001 has not passed.  
**Architecture impact:** None; bsnes remains a research target, not a selected dependency.

The observer and its host-only tests are implemented. The standalone observer compiled and its storage/export tests passed. The complete emulator has not built or run in this environment, so production of records by the actual cycle PPU, native-output equality, execution-state equality, and runtime overhead remain unverified.

## 1. Authority, repository, and working-tree identity

Workspace root: `<GTC-HD-Lab>`.

The task's AGENTS.md, project state, architecture audit, and experiment specification were read before implementation. The requested specification path, `project/experiments/EXP-001_PASSIVE_PPU_OBSERVATION.md`, does not exist. The existing specification was found and read at `project/expies/EXP-001_PASSIVE_PPU_OBSERVATION.md`; it has not been moved or edited. This report uses the requested results location.

| Item | Verified identity |
| --- | --- |
| Audited baseline | `7d5aa1e656b9171524d01b1b22917197d8121cb4` |
| Writable experiment | `experiments/bsnes-exp-001/` |
| Experiment branch | `gtc-hd/exp-001-passive-ppu-observation` |
| Experiment HEAD | `7d5aa1e656b9171524d01b1b22917197d8121cb4` plus the uncommitted changes listed below |
| Ancestry check | `git merge-base --is-ancestor 7d5aa1e656b9171524d01b1b22917197d8121cb4 HEAD` succeeded before editing |
| Pristine reference | `upstream/bsnes/`, branch `master`, same baseline SHA |
| Initial state | Both bsnes worktrees and the GTC-HD-Lab repository were clean |
| Final state | Experiment dirty; GTC-HD-Lab has this new report and one ignore-rule correction; pristine upstream clean and unchanged |

The experiment is a linked Git worktree: its `.git` file points to `upstream/bsnes/.git/worktrees/bsnes-exp-001`. It shares repository metadata with the pristine checkout but has its own branch and working files. No commit, branch move, merge, or reference update was performed. There is no new experimental commit SHA to report.

AGENTS.md, canonical project state, the approved specification, and the architecture audit remain unchanged. No ADR or accepted architectural decision was created.

### Durable files changed

Paths in this table are relative to the experiment worktree.

| File | Change |
| --- | --- |
| `bsnes/sfc/ppu/background.cpp` | Add a frame-boundary counter hook and a copied-value name-table observation hook |
| `bsnes/sfc/ppu/ppu.cpp` | Include the observer implementation and reset diagnostics on cycle-PPU power/reset |
| `bsnes/sfc/ppu/exp001-observer.hpp` | New record, status, bounded storage, and diagnostic control interface |
| `bsnes/sfc/ppu/exp001-observer.cpp` | New storage, overflow, copy-out, and explicit CSV export implementation |
| `tests/exp001/observer-test.cpp` | New host-only storage/export tests; no SNES content |
| `tests/exp001/.gitignore` | Ignore this test's `/build/` directory |

GTC-HD-Lab changes: new `project/experiments/EXP-001_RESULTS.md` and a one-line correction to root `.gitignore`. The existing unanchored `experiments/` pattern also ignored this report's directory; changing it to `/experiments/` keeps root experimental checkouts ignored while exposing project experiment documentation for review. No other ignore rule was changed.

Local generated files, all under the ignored `<OUTPUT_DIR>/` directory: `observer-test.exe`, `observer-test.obj`, `exp001-observer.obj`, `observer-test.csv`, `observer-msvc.log`, `ppu-msvc.log`, and `baseline-ppu-msvc.log`. The CSV contains **synthetic host-test records**, not captured SNES activity. Failed PPU compilation produced no PPU object or desktop executable.

### Uncommitted source fingerprint

SHA-256 of the six durable experiment files, as bytes on disk at completion:

```text
19c774b74a8b2a1c662b78b4965c466397600f8d267735076e3738ec51d5cda8  bsnes/sfc/ppu/background.cpp
89e4ea31299fed910c7404630b15d748a0b3e653a1e601c9ec05f8ca64fa0323  bsnes/sfc/ppu/ppu.cpp
74e6764f1506116ced205cab1c8663668285224a8f72fdbbf19c199f73348ccb  bsnes/sfc/ppu/exp001-observer.hpp
f0d38d665f90a27be93893b740c903ace0ed5cad730df73c3729792b61b44b26  bsnes/sfc/ppu/exp001-observer.cpp
020c2606e8ed484089c2083e0be438b9d0736bee1558a6b76af0d58bd23f69cf  tests/exp001/.gitignore
5ccfd1c20dfc96c027161cd1c691ae6ee2367b9debe65aeca685e02e66304655  tests/exp001/observer-test.cpp
```

## 2. Observation point and scope

**Source observation:** `PPU::Background::fetchNameTable()` in `bsnes/sfc/ppu/background.cpp` already computes the map coordinates and address, reads the tilemap word, selects and adjusts the character, resolves priority and palette base, and computes the first character-row address.

The new hook follows the existing assignment to `tile.palette` and precedes `nameTableIndex++`. At this point, `address`, `attributes`, `hoffset`, `voffset`, `htile`, `vtile`, `nameTableIndex`, and the populated native `tile` are still available together. The record copies those values and existing flags. It does not independently repeat the lookup.

Selection requires observation enabled and `io.mode <= Background::Mode::BPP8`. It includes naturally scheduled 2/4/8-bpp tiled fetches in modes 0–6. The existing native scheduler determines when the function executes; the observer does not schedule fetches. Inactive BGs and Mode 7 are excluded. The scope is name-table provenance, not every VRAM access: offset-per-tile reads and subsequent character bitplane reads are not separately observed.

Main/sub-screen-disabled and forced-blank fetches are retained when they occur naturally, with flags. The native cycle path runs BG work through V=240; a record therefore does not establish that its tile produced a visible pixel. Transparent pixels, windows, composition, color math, and final visibility are not represented.

There are only two supporting changes outside `fetchNameTable()`:

1. The existing `Background::frame()` callback advances an observer-owned counter for BG1 only. `PPU::main()` already calls all four BG callbacks at V=0, H=0.
2. `PPU::power()` resets diagnostics after the fast-PPU early return, before the existing cycle-PPU initialization. `ppu.cpp` includes the observer implementation once, following the repository's included-implementation style. It needs no additional make object.

Fast PPU, OBJ, Mode 7, windows, color math, serialization, frontend rendering, and GPU code are unmodified.

## 3. Record schema and exact semantics

`SuperFamicom::Exp001::BGFetchRecord` contains copied integer values only. Its measured size with MSVC x64 is **48 bytes**, including padding. Do not hash or persist its raw object bytes as a portable format; CSV writes fields explicitly.

| Field | Type | Meaning at the hook |
| --- | --- | --- |
| `frame` | u64 | Observer count of BG1's V=0/H=0 callbacks since cycle-PPU power/reset; starts at 0 and the first boundary makes it 1. Counts native vertical periods, including each interlaced field period; not a game-level or paired display-frame number. Assigned by append. |
| `h` | u16 | `PPUcounter::hcounter()` in PPU counter clocks, not dots or framebuffer X. |
| `v` | u16 | `PPUcounter::vcounter()` scanline. The native function returns without fetching at V=0. |
| `mapAddress` | u16 | Native `address` local: 16-bit **word** address of the tilemap entry before VRAM's mask. |
| `mapEntry` | u16 | Native `attributes` local: the tilemap word already read by the normal path. |
| `character` | u16 | Native 10-bit `tile.character`, after 16x16/hires sub-tile selection and native 10-bit wrapping; before adding the character-data base. The original map character remains recoverable offline from `mapEntry & 0x03ff`. |
| `characterRowAddress` | u16 | Native `tile.address`: **word** address for the selected character row's first bitplane pair, after base/mask and vertical-row selection. It is not the map address, a byte address, or a record of all character-plane reads. |
| `sourceX` | u16 | Native wrapped `hoffset` in source-pixel coordinates, after scroll/offset-per-tile handling. Horizontal pixel mirroring is not applied to this coordinate. |
| `sourceYAfterVflip` | u16 | Native wrapped `voffset` after scroll/mosaic/interlace/offset-per-tile handling and, when vertically flipped, the native `voffset ^= 7`. Includes the full coordinate with those low three bits changed; not merely a row number. |
| `mapTileX`, `mapTileY` | u16 each | Native `htile`/`vtile` before tilemap quadrant addressing and before the vertical low-bit XOR. Derived by native code using its tile-width/height shifts; hires uses a horizontal shift of 4. These are not framebuffer coordinates. |
| `vramMask` | u16 | Native VRAM word-address mask, normally `0x7fff` or extended `0xffff`. An effective map address can be interpreted offline as `mapAddress & vramMask`. |
| `tileCacheIndex` | u16 | Native cache slot before its increment. Distinguishes hires repeats, which can share H/V while writing consecutive slots. |
| `field` | u8 | Native `PPUcounter::field()` Boolean, copied as 0 or 1; retained even without interlace. |
| `bg` | u8 | Native BG ID, 0=BG1 through 3=BG4. |
| `bgMode` | u8 | Native global `ppu.io.bgMode` (0–6 for selected tiled events). |
| `tileMode` | u8 | Native BG mode enum: 0=2bpp, 1=4bpp, 2=8bpp. |
| `paletteGroup` | u8 | Native tilemap palette group, bits 10–12 of the map word. |
| `paletteBase` | u8 | Native `tile.palette`, including mode-0 BG offset and native palette-group shift/wrapping. It is not a fetched CGRAM color or a final pixel palette index; 8bpp/direct-color interpretation still requires native rendering context. |
| `priority` | u8 | Native mode-resolved `tile.priority` rank selected through `io.priority[]`, not raw map attribute bit 13. |
| `hflip`, `vflip` | u8 each | Native tile mirror flags, 0 or 1. |
| `mainEnabled`, `subEnabled` | u8 each | Native BG main/sub-screen enable flags at fetch time. They do not describe later windows, transparency, or composition. |
| `forcedBlank` | u8 | Native `ppu.io.displayDisable` at fetch time. |
| `tileSize` | u8 | Native BG tile-size bit; does not by itself express hires horizontal tile width. |
| `screenSize` | u8 | Native two-bit BG map-size value; native code uses bit 0 for horizontal and bit 1 for vertical map expansion. |

The record intentionally omits final pixel color, palette lookup results, character bitplane contents, per-pixel visibility, and stable game-object identity. Those values either arise later in `fetchCharacter()`, `Background::run()`, and composition or are not native identities. Obtaining them here would require extra reads, helper calls, reconstruction, or carrying additional information. There is no asynchronous pointer back to a tile cache, register block, or VRAM.

`hcounter()`, `vcounter()`, and `field()` are direct const getters in `bsnes/sfc/ppu/counter/counter-inline.hpp`; they do not latch counters or advance execution. Added integer narrowing casts cover values whose native ranges fit the record.

## 4. Buffering, control, and retrieval

The single `SuperFamicom::Exp001::observer` owns a fixed array of **32,768 records**, or **1,572,864 bytes / 1.5 MiB** of record storage on the tested compiler, plus small bookkeeping. Append performs no allocation, I/O, locking, or PPU call. Native cycle execution order defines append order. The array is a retained prefix, not a circular queue.

When full, further enabled events are dropped. `Status::dropped` increments with saturation at `UINT64_MAX`, and `Status::overflow` becomes true. Existing records are never overwritten. Reaching capacity alone is not overflow until another record is attempted. No automatic drain or frame clear exists; the caller must retrieve status and records before clearing. Capacity is a bound, not a guarantee of complete capture for arbitrary run intervals.

Control is a deliberately small runtime diagnostic interface, allowing B and C to use the same executable:

| Method | Effect |
| --- | --- |
| `setEnabled(false)` | Default after power/reset. Stops appending; preserves existing capture and overflow status. |
| `setEnabled(true)` | Enables appending; does not implicitly clear old records. |
| `status()` | Returns copied frame/count/capacity/dropped/enabled/overflow values. |
| `copyRecord(index, destination)` | Copies one valid record out; false for an invalid index without modifying destination. |
| `writeCsv(path)` | Explicit diagnostic export, including metadata, index, and all 27 record fields. Opens the caller-selected path for replacement; returns success/failure; does not clear storage. |
| `clear()` | Clears count and dropped/overflow; preserves enable and frame counter. Old array bytes become inaccessible through the retrieval API. |
| `reset()` | Clears capture, disables, and resets frame count to zero. Called on cycle-PPU power/reset. |

Use these methods from a diagnostic host or debugger **while core execution is stopped between `run()` calls**. There is no UI preference or automatic dump. The interface is not thread-safe and is not intended for concurrent polling of a live PPU. A symbol-bearing desktop build (`build=debug`) is appropriate for debugger invocation; that integration has not been exercised here.

Example host/debugger sequence, after loading/powering with `Hacks/PPU/Fast=false`:

```cpp
// Core stopped on its host, outside the emulation cothread.
SuperFamicom::Exp001::observer.clear();
SuperFamicom::Exp001::observer.setEnabled(true);
// Resume a controlled run; regain host control before inspecting/exporting.
auto status = SuperFamicom::Exp001::observer.status();
bool exported = SuperFamicom::Exp001::observer.writeCsv("exp001-capture.csv");
// Preserve/check status and exported before deliberately clearing this batch.
SuperFamicom::Exp001::observer.setEnabled(false);
```

Disabled capture adds an enable check at the name-table hook and observer frame bookkeeping once per native vertical period. It does not construct or append a record. The frame counter advances even while disabled, so toggling capture does not renumber subsequent native periods. Enabling mid-period yields a partial period and is not labeled a complete capture.

Observer state is not serialized. Synchronized state loading invokes power and therefore resets/disables it; unsynchronized state loading can rewind native counters without rewinding diagnostics. For initial validation, use cold starts with rewind/run-ahead disabled and explicitly rearm after any reset/load. Fast-PPU power follows its untouched early-return path and does not clear an old cycle capture: disable/clear before changing PPU implementation, and do not interpret old records as fast-PPU activity.

## 5. Passivity analysis

**Source evidence:** The native-file diff contains 37 added lines and no removed native lines. Existing map reads, cache updates, increment/repeat control flow, counter advancement, synchronization, and rendering logic remain in their original order. The added hook copies native locals/fields and calls only the observer and the three pure counter getters. There is no extra VRAM indexing, `paletteColor()` call, OAM/CGRAM operation, CPU access, scheduling call, or observer-dependent rendering branch.

The observer lives outside the PPU's serialized structure. Frame counting and reset change only diagnostic storage. CSV export is explicitly invoked outside core execution, never from a fetch or an automatic frame callback. Native timing counters are not changed by observation.

**Inference:** This structure should preserve emulated PPU semantics. It necessarily adds host instructions and memory traffic, so it is not a claim of zero host overhead or unchanged real-time input sampling under an uncontrolled frontend.

**Unverified hypothesis:** A/B/C native output and relevant execution state remain equal under controlled input. Source inspection and host buffer tests do not establish that result. Integration/compiler behavior, provenance correspondence, observer cost, and all emulation-visible effects still require the runtime experiment.

## 6. Build method and actual results

### Normal desktop build

The checked-out `.github/workflows/build.yml` invokes:

```text
make -j4 -C bsnes local=false
```

Working directory: `experiments/bsnes-exp-001/`.

`bsnes/GNUmakefile` selects the desktop `target=bsnes`, `binary=application`, `build=performance`, and OpenMP by default. `local=false` removes the default `-march=native`. For Windows, `nall/GNUmakefile` selects GNU `g++`, GNU C++17, Windows/MinGW libraries, and `windres`; the performance profile uses `-O3`. A debugger build can use `make -j4 -C bsnes local=false build=debug` once the supported toolchain is present.

**Actual attempt:** failed before compilation because PowerShell could not find `make` (exit 1). GNU make, g++, GCC, windres, and Clang were not available in the examined tool locations/PATH. WSL listed only Docker Desktop, not a general development distribution. No toolchain, dependency, ROM, or container image was installed/downloaded. There is no GNU compiler version or completed desktop build to report.

### Strongest available build validation

Visual Studio 18 Community's existing **MSVC 19.50.35728 x64** compiler was available through its developer environment. The standalone observer was compiled and linked with its tests under C++17, warnings-as-errors, disabled optimization, and runtime checks.

Commands below use `cmd.exe` syntax through PowerShell's `ComSpec`, with machine-local paths normalized. `<GTC-HD-Lab>` is the repository root, `<OUTPUT_DIR>` is the ignored evidence directory used for that run, and `<VCVARS64_BAT>` is the Visual Studio 18 Community x64 environment script. Replace placeholders before invocation. Compiler output was captured in `observer-msvc.log`.

```bat
call "<VCVARS64_BAT>"
cd /d "<OUTPUT_DIR>"
cl /std:c++17 /EHsc /W4 /WX /Od /RTC1 /Fe:observer-test.exe /Fd:observer-test.pdb "<GTC-HD-Lab>/experiments/bsnes-exp-001/tests/exp001/observer-test.cpp" "<GTC-HD-Lab>/experiments/bsnes-exp-001/bsnes/sfc/ppu/exp001-observer.cpp"
observer-test.exe observer-test.csv
```

Both build and test exited 0. **No warnings** were emitted by this observer-only build. Assertions were enabled. Output:

```text
PASS: copy ownership, ordering, disabled capture, bounds, overflow, reset, CSV
record_bytes=48 capacity=32768
```

A direct native PPU translation-unit probe was also attempted with MSVC:

```bat
cl /nologo /std:c++17 /EHsc /c /I"<GTC-HD-Lab>/experiments/bsnes-exp-001/bsnes" /I"<GTC-HD-Lab>/experiments/bsnes-exp-001" /Fo:ppu-msvc.obj "<GTC-HD-Lab>/experiments/bsnes-exp-001/bsnes/sfc/ppu/ppu.cpp"
```

It exited 2 in pre-existing headers before the observer integration could be type-checked. A matching read-only probe of the pristine source used absolute include/source paths and `/Fo:baseline-ppu-msvc.obj` in the experiment's build directory:

```bat
cl /nologo /std:c++17 /EHsc /c /I"<GTC-HD-Lab>/upstream/bsnes/bsnes" /I"<GTC-HD-Lab>/upstream/bsnes" /Fo:baseline-ppu-msvc.obj "<GTC-HD-Lab>/upstream/bsnes/bsnes/sfc/ppu/ppu.cpp"
```

That probe also exited 2. After removing path prefixes, the 75 diagnostic codes/messages match in sequence: **62 errors, 12 warnings, 1 fatal error**. The existing incompatibilities include GCC `__attribute__` declarations and zero-sized arrays in SameBoy headers, eleven unknown-GCC-pragma warnings, one `interface` macro-redefinition warning, and fatal missing `utime.h` in `nall/platform.hpp`. Complete outputs are preserved in `ppu-msvc.log` and `baseline-ppu-msvc.log`.

These probes demonstrate the same unsupported-toolchain blockers in both trees, not successful integration compilation. No native-header compatibility workaround was made. New integration warnings remain unknown until the supported desktop build runs. Git also reports LF-to-CRLF conversion notices for the two edited native files; these are Git notices, not compiler warnings.

## 7. Tests actually performed and not performed

| Validation | Result / boundary of evidence |
| --- | --- |
| Branch, baseline, ancestry, initial cleanliness | Verified before edits |
| Native diff and source review | Additions only; native operations retained; no new stateful PPU access in additions |
| Observer-only build | Passed MSVC C++17 `/W4 /WX /Od /RTC1`; no warnings |
| Copied-value ownership | Passed synthetic test: changing input and retrieved copies leaves stored values intact |
| Order and control | Passed synthetic frame/order checks, disabled append, enable, clear, and reset |
| Bounds and overflow | Passed invalid-index checks, exact 32,768-record fill, two additional dropped events, preserved first/last records, explicit overflow, clear/reset behavior |
| CSV export | Passed metadata/data checks and null-path rejection; independently parsed all 32,768 synthetic rows, 28 columns each, verifying indices and map-address sequence |
| Native PPU MSVC probe | Blocked by the same pre-existing diagnostics as pristine source |
| Full desktop build | Blocked by absent GNU toolchain; no emulator binary produced |
| Real PPU provenance | **Not performed** |
| Native A/B/C frame comparisons | **Not performed; 0 frames compared** |
| Emulator state comparison | **Not performed**; source investigation below |
| Runtime count/bytes per frame, overhead, overflow pressure | **Not measured** |
| Final pristine-source and protected-document checks | Clean/unchanged; `git diff --check` passed |

No appropriate legal test ROM was found in the searched workspace, Documents, Downloads, or attachment staging locations. Only a commercial candidate appeared; its content was not opened or used. No ROM was downloaded or invented. **ROM identifier/hash: none used.** This is a searched-location limitation, not a claim to have inventoried every drive.

The measured 48-byte record size and fixed 1.5-MiB capacity are host implementation facts. The synthetic 32,768-row CSV is not a sample provenance finding, record-per-frame measurement, or evidence that scrolling/VRAM/register changes were observed correctly in bsnes.

## 8. Exact native-frame comparison: identified next-step method

**Source observation:** Cycle `PPU::refresh()` in `bsnes/sfc/ppu/ppu.cpp` supplies the `uint16` native output to `platform->videoFrame(...)` at **512 x 480**, pitch **1024 bytes**, scale 1. Before that callback it can apply blur in place and draw a controller cursor. `Program::videoFrame()` in `bsnes/target-bsnes/program/platform.cpp` then performs frontend crop/filter/palette/output work.

Minimal comparison method: collect or hash the callback's native `uint16` rows at the entry to `Program::videoFrame()` (or an equivalent small diagnostic platform callback), before that frontend transformation. Disable native blur and use standard gamepads with no cursor overlay; disable run-ahead, rewind, frame skipping, and cheats. Enforce the cycle PPU after any per-game hack configuration. Record actual dimensions, pitch, scale, region, interlace/overscan state, and full configuration on every run.

Hash `width` words per row, using the supplied pitch to locate rows. Encode each word explicitly little-endian into SHA-256, and record dimensions alongside the digest. Do not hash row padding or a frontend RGB screenshot. At this cycle output size the payload is 491,520 bytes per callback. Compare every matching callback index, not a visual screenshot or only the final image. Keep the 512x480 native layout intact for the first test, including initialized unused/duplicated rows, rather than inventing a crop/deinterlace normalization.

The callback occurs after native controller drawing, so matching the no-overlay/blur configuration is essential. If that cannot be guaranteed, capture immediately before those optional operations instead and apply the same diagnostic hook to each comparison build. Interlace can preserve previous-field data; start identically and retain it rather than dropping alternate rows.

No frame hashing hook was added in this pass. The stage and byte sequence are identified concretely, but executing this requires a working desktop build and controlled host harness. Adding a frontend validation path here would not resolve the missing toolchain/test-content blockers and would enlarge the instrumentation diff. This method is proposed, not a completed comparison.

## 9. Serialization investigation and recommendation

**Source evidence:** `bsnes/sfc/system/serialization.cpp`, `bsnes/sfc/sfc.hpp` (`Thread::serializeStack()`), `bsnes/sfc/ppu/serialization.cpp`, `bsnes/sfc/cpu/serialization.cpp`, `bsnes/sfc/system/system.cpp`, `bsnes/emulator/random.hpp`, `nall/serializer.hpp`, and `libco/amd64.c`.

`System::serialize(bool synchronize)` writes a signature, size, serializer version, zero-initialized description, synchronize flag, fast-PPU flag, and the serialized components. `serializeAll()` includes RNG state, cartridge, CPU/SMP/PPU/DSP, present coprocessors, and connected controllers/expansion devices. Cycle PPU serialization covers VRAM, CGRAM/OAM-related state, latches, IO, counters, timing/thread clocks, BG/OBJ pipeline/cache state, windows, and color-math state. CPU serialization includes CPU registers, WRAM, interrupt/IO and DMA/HDMA state. The native output framebuffer and this observer are not serialized.

The integer serializer writes explicit little-endian fields rather than arbitrary struct padding, which makes logical-state byte comparison promising under controlled conditions. This does **not** make every save format a portable deterministic checksum:

* With `synchronize=false` on a libco backend that supports it, the serializer additionally copies raw coroutine stack storage. It can include host addresses, saved registers/return addresses, stack residue, and build-dependent call layout. Instrumentation can change that layout. Raw stack-inclusive saves are unsuitable for cross-build/process A/B/C equality, despite the source comment calling the restore mechanism deterministic.
* With `synchronize=true`, `runToSave()` advances/synchronizes execution before serialization and can process frame events. It is not a side-effect-free snapshot of the exact pre-call frame boundary. The selected Fast/Strict synchronization method must match across runs, and comparison checkpoints must account for execution it performs.
* Startup entropy seeds RNG state from `clock()`. Even `Entropy::None`, which makes returned random initialization values deterministic, still initializes a time-dependent hidden RNG state that is serialized. Entropy=None alone is therefore insufficient for raw state-byte equality. A harness can combine Entropy=None with an explicit identical RNG seed/sequence after power and before the first run, or establish an identical synchronized starting state; either approach must first demonstrate repeatability.
* Configuration, serializer version, build/platform, region, cartridge memory/persistent saves, controllers, RTC-bearing content, and input must match. Floating fields in other components and state not included by a component's serializer need case-specific review. Choose a simple non-RTC test cartridge initially.
* Loading a synchronized state powers the core and resets this observer. Loading other states can leave diagnostics out of step. The framebuffer is not restored by this serializer, so a common save alone does not establish an identical displayed starting image.

**Recommendation / inference:** Use synchronized logical-state saves as supplementary evidence only after repeated A/A and B/B runs show identical bytes under the chosen initialization and checkpoint procedure. Then compare A/B and B/C with the same save schedule. Preserve and investigate mismatches; do not mask unexplained bytes or claim framebuffer equality proves every latch/CPU-visible effect. Separate runs without serialization can keep the frame-comparison schedule simple. Targeted logical CPU/PPU state checks are a possible follow-up if whole-state comparison proves unstable; no serializer redesign or targeted-state hook was implemented.

**Actual result:** Source investigation only. No state was captured, hashed, compared, or restored during this pass.

## 10. Deviations, risks, and unresolved questions

The task explicitly narrowed this pass to instrumentation/build validation. The approved runtime experiment remains pending. The existing worktree was reused rather than recreated. The spec's directory discrepancy and the root ignore-rule correction needed to expose the results for review are recorded above. Runtime control/export is a debugger/host diagnostic API rather than a new frontend preference, keeping B/C switching small. Additional flags, VRAM mask, tile mode, and cache index disambiguate native values; no renderer or generalized telemetry system was introduced.

Remaining risks and limits:

* Native PPU integration has not compiled with its supported compiler. Standalone tests cannot catch integration-only type, macro, linkage, or optimizer issues.
* The selected point describes name-table fetch decisions. It does not prove which tile bits, palette values, or pixels are eventually consumed after later raster activity. Cache reuse, hires, flips, offset-per-tile, mosaic, and mid-frame changes need actual provenance checks.
* Frame identity is a native vertical-period counter; partial captures, reset/load, and interlaced output require explicit interpretation. Counter wrap is theoretically possible after 2^64 periods and is outside practical runs.
* Fixed storage has a host memory/cache cost even in an executable whose observer is disabled. Enabled copying and per-fetch checks can alter wall-clock speed. No performance measurements exist yet.
* Long capture intervals can fill the buffer. Overflow is explicit, but the discarded suffix cannot be recovered. Dumping/clearing once per host return is only adequate if measured event counts and boundary alignment support it.
* Export pauses host progress and can affect uncontrolled real-time input. Use prerecorded or explicitly scripted input. A failed export may leave a partial file; check its return value and preserve buffer/status before clearing.
* No real capture yet validates record-field semantics against a legal ROM. Synthetic copy tests establish value ownership, not PPU correctness.
* Serialized-state byte equality remains conditional, especially around RNG initialization and save synchronization. Native-frame equality alone is necessary but insufficient for full passivity.

## 11. Smallest next validation action

Use a supported GNU/MinGW toolchain to build the experiment and a baseline from the audited revision in a separate disposable build checkout, leaving `upstream/bsnes/` pristine. Record exact compiler versions/commands and all warnings. Start with a symbol-bearing build so the diagnostic API can be invoked safely.

With an authorized legal tiled-BG test ROM already supplied for testing, record its identifier, license/source, and SHA-256. Use fixed configuration, cycle PPU, deterministic startup/RNG, persistent-memory contents, and scripted input. Begin with a short repeatability run, then compare **120 consecutive native video callbacks** across A (baseline), B (same experimental executable disabled), and C (enabled). Hash the documented native stage at every callback; require A=B=C for the sequence. Record actual callback dimensions and configuration.

Retrieve C's status/records between runs, export before clearing, and treat any overflowed batch as incomplete. Measure records and 48-byte record volume per native period, dropped count, and approximate B/C host time separately from export time. Inspect real records for order, map/character changes during scrolling, palette/priority/flip correspondence to native values, hires repeat identity where exercised, and preservation across subsequent VRAM/register changes.

In supplementary repeatable runs, perform the synchronized-state checks described above, including A/A and B/B controls. Report a state-comparison limitation if trustworthy equality cannot be established. Stop and preserve evidence if native frames or relevant state diverge; do not change native semantics to force a pass.

Only these runtime results can support the EXP-001 passivity hypothesis for the tested slice. They would still not select bsnes or accept a GTC-HD rendering architecture.

## 12. Runtime observer window controls — September 19, 2026

**Historical checkpoint:** The pending status and proposed B2/C runs in this section describe the September 19 implementation pass. See the [current result](#current-result) for the later completed runtime conclusion.

**Status: IMPLEMENTED / SUPPORTED BUILD PASSED / B2 AND C RUNTIME VALIDATION PENDING.** No ROM was loaded or executed during this implementation pass. EXP-001 is not marked verified, and no GTC-HD architecture decision has been made.

### 12.1 Starting evidence, authority, and repository identity

The user reports completed deterministic 600-callback Super Mario World title-sequence runs A1, A2, and B, with identical native-frame CSV files and common SHA-256:

```text
92B098CF30A4171F707185B2A32918B8F361EDF30AC8BA6AA3F1FEAD39BAE96F
```

This is user-provided prior runtime evidence. It was not independently rerun here and does not establish C equivalence. The earlier reports document their own historical implementation passes. Current project authority is under `docs/`; the former `project/` references above are historical.

Read before this change: `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/experiments/EXP-001/SPEC.md`, this report, and `docs/experiments/EXP-001/RUNTIME_HARNESS_RESULTS.md`.

| Worktree | Branch | HEAD at start and completion |
| --- | --- | --- |
| Writable: `experiments/bsnes-exp-001/` | `gtc-hd/exp-001-passive-ppu-observation` | `2e0eeaa1580487f277e60f6ef55b9c74ca1026ae` |
| Read-only harness baseline: `experiments/bsnes-exp-001-baseline/` | `gtc-hd/exp-001-runtime-harness` | `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919` |
| Read-only audited source: `upstream/bsnes` | `master` | `7d5aa1e656b9171524d01b1b22917197d8121cb4` |

All three worktrees and GTC-HD-Lab were clean at the beginning. The writable branch descends from the audited baseline. Only the observer worktree and this results document were changed. Both read-only worktrees remain clean; canonical project state, instructions, specification, and runtime-harness report remain unchanged. Nothing was committed or staged.

Durable source changes, relative to `experiments/bsnes-exp-001/`:

| File | Change |
| --- | --- |
| `bsnes/target-bsnes/program/exp001-observer-window.hpp` | New experimental argument validation, callback-window lifecycle, checked export, and summary |
| `bsnes/target-bsnes/bsnes.cpp` | Route observer options before the existing EXP-001 parser; validate/preflight both outputs before normal startup |
| `bsnes/target-bsnes/program/program.hpp` | Own the frontend window controller |
| `bsnes/target-bsnes/program/program.cpp` | Arm/disarm around ordinary core runs; reject ambiguous execution modes for C; finalize before unload/shutdown |
| `tests/exp001-runtime/observer-window-test.cpp` | New synthetic host tests using the existing observer and frame hasher |
| `tests/exp001-runtime/observer-window-cli-test.py` | New desktop parser/preflight rejection tests; no ROM content |

Outside that worktree, only `docs/experiments/EXP-001/RESULTS.md` is modified. Generated binaries, logs, synthetic outputs, and the CLI test's hiro cache remain under already-ignored build/output locations.

### 12.2 Options and validation

All three options are required together:

```text
--exp001-observer-csv=<NEW_PROVENANCE_OUTPUT_PATH>
--exp001-observer-start-callback=<N>
--exp001-observer-callback-count=<M>
```

They are valid only with `--exp001-frame-hash=<NEW_HASH_OUTPUT_PATH>`. `N` is an unsigned decimal integer including zero; `M` is a positive unsigned decimal integer. Empty, signed, fractional, nondecimal, duplicate, and uint64-overflow values are rejected. The half-open range `[N, N+M)` must fit within the requested native callback count. Addition is checked before computing the exclusive end. A window starting at or beyond the run limit, or extending beyond it, is rejected before emulation rather than silently shortened. The existing hash count default remains 120 when its option is absent.

No observer options means B2: the observer remains disabled by its existing initialization/power lifecycle; the new controller does no capture, export, summary creation, or configuration enforcement. The normal no-EXP-001 path also remains inert. The original frame hasher, its algorithm/schema, and the `Program::videoFrame()` hook are byte-for-byte unchanged from the starting HEAD.

C requires ordinary cycle-PPU execution: automatic state loading is rejected, as are run-ahead, active rewind/history recording, and a fast-PPU configuration. These checks reject incompatible settings rather than changing them. Existing deterministic-run operator requirements still apply: fixed settings/input/persistent memory, no reset, manual save/load, reload, rewind, or other UI actions during the run. No additional guard is imposed on B2 or ordinary use.

### 12.3 Callback semantics and off-by-one proof

`Exp001FrameHash::actual` is the number of successfully hashed callbacks. Immediately before the next ordinary `emulator->run()`, it is therefore the zero-based index that the next callback will receive.

`Program::main()` calls `Exp001ObserverWindow::beforeRun()` immediately before that ordinary run. When `actual == N`, it executes the required diagnostic sequence: disable, clear records/drop status, enable. No new observer activation takes place inside `Program::videoFrame()`.

After `emulator->run()` returns normally to `Program::main()`, `afterRun()` checks that exactly one callback was successfully added. Unexpected callback counts, out-of-bracket callbacks detected at the next run, or an observer reset/disarm during an observed run cause failure. The controller tracks the expected next callback from zero; it never derives callback indices from the observer's native frame counter.

When the returned count equals `N+M`, the callback just delivered was `N+M-1`. The controller disables the observer, copies its status, and exports before another emulation run can begin. This occurs even if the hash harness's stop flag was set by the final callback. Normal hash-limit shutdown is checked afterward.

For N=500, M=1:

| Frontend point | Hash `actual` | Observer action |
| --- | --- | --- |
| Before runs producing callbacks 0–499 | 0–499 | Remains disabled |
| Before the run producing callback 500 | 500 | Disable, clear, enable |
| Inside callback 500 | Becomes 501 after successful hashing | No observer control or export in callback |
| After that run returns | 501 | Disable, preserve status, export |
| Before runs producing callbacks 501–599 | 501–599 | Remains disabled |

For N=0, arming occurs after game power and before the first run, so the first callback-producing interval is observed. For M>1, the observer stays enabled across exactly M such intervals, with one clear at the beginning and one export at the end. It is not cleared per callback. Buffer capacity remains 32,768, so a multi-callback window may overflow.

**Native timing distinction:** `CPU::scanline()` in `bsnes/sfc/cpu/timing.cpp` synchronizes the PPU and leaves a frame event at `vcounter() == ppu.vdisp()`. Cycle `PPU::writeIO()` sets `vdisp` to 225 or 240 depending on overscan. The existing observer's `frame` instead counts V=0 boundaries, and native BG fetch scheduling continues through V=240. Therefore a callback-producing run interval can include offscreen fetches after the preceding callback, before V=0, as well as the selected frame's visible rendering. A one-callback CSV can legitimately contain more than one observer `frame` ID. The implemented window is exactly the requested **callback-producing run interval**, not a fabricated V=0-to-V=0 interval or a filter on record `frame`. No PPU scheduling or BG-selection change was made to hide this distinction.

### 12.4 Export, overflow, summary, and termination

The runtime reuses `SuperFamicom::Exp001::observer` and its existing `setEnabled`, `clear`, `status`, and `writeCsv` methods. Observer source, record schema, capacity, and BG hook are unchanged.

The requested output must not exist. A new sidecar is reserved exclusively at `<PROVENANCE_OUTPUT_PATH>.summary.txt`. Direct path conflicts with the frame-hash output, including the generated summary/staging names, are rejected. Existing files/directories/symlinks at the provenance path and existing summary files are not overwritten.

The legacy observer exporter itself opens files with replacement semantics. To reuse it safely, the frontend creates a private sibling directory `<PROVENANCE_OUTPUT_PATH>.exp001-tmp`, exports to its `capture.csv`, then publishes with `std::filesystem::copy_file(..., copy_options::none)`. Publication fails if another file has appeared at the requested path meanwhile. Export and publication results are checked separately; export failure or a late collision cannot be reported as success. Cleanup removes only the owned staging file/directory, never recursively. The output parent must already exist. Use ordinary ASCII paths for the initial validation commands because the unchanged observer exporter retains its narrow filename API; no broader filename-encoding guarantee was established here.

All export and summary writes occur during frontend control, outside emulation execution. There is no new file I/O or threading in PPU work. The original provenance CSV schema is preserved.

The summary starts with `# exp001_observer_window_version=1` and, on explicit finalization before shutdown, records:

```text
requested_start_callback
requested_callback_count
end_callback_exclusive
window_started
window_completed
observed_callbacks
actual_native_callbacks
record_count
capacity
dropped_count
overflow
observer_frame
observer_enabled
export_attempted
export_succeeded
capture_complete
reason
```

Status is frozen after disabling at export; later unobserved runs do not replace it. `window_completed=true` means the requested callback interval finished. `capture_complete=true` additionally requires successful export/publication, no controller error, and no overflow. These are intentionally separate: an overflowed window may complete and export its retained prefix, with explicit dropped count, but is never called a complete capture.

Overflow does not shorten native hashing: subsequent callbacks continue through the requested hash count. The summary reports `reason=observer_overflow`, and the process exits nonzero because provenance is incomplete. This enables frame comparison even when buffer capacity proves insufficient. Capacity is not automatically enlarged.

On normal early quit before N, no provenance CSV is created; the summary reports that the window never started, zero observed callbacks, and no export. Early quit during a window disables and exports the partial capture with `window_completed=false` and `capture_complete=false`. Export/preflight/callback errors also produce a nonzero exit; after a runtime export error the frontend stops rather than pretending capture succeeded. Finalization is idempotent and occurs before `unload()` and before the existing Windows `TerminateProcess` path.

Check **both** the frame-hash footer/process exit and the complete observer summary. A crash, forced kill, summary write/close failure, or disk error can leave incomplete files. Successful provenance capture alone does not establish a completed 600-callback hash run. Invalid command-line requests may fail before a sidecar is created; their reason is written to stderr.

### 12.5 Build and focused tests actually performed

Supported environment: existing MSYS2 UCRT64; **g++ 16.2.0 (Rev3, Built by MSYS2 project)**. No toolchain or ROM was installed/downloaded.

From the observer worktree in UCRT64:

```sh
export PATH=/ucrt64/bin:/usr/bin:$PATH
make -j4 -C bsnes local=false
```

**Result: exit 0.** This was an incremental desktop rebuild of six affected frontend translation units and a successful relink, using existing core objects. Configuration remained the supported desktop performance build (`-O3`), GNU C++17, OpenMP enabled, `local=false`. It emitted **six pre-existing `-Wcast-user-defined` warnings at `nall/string/markup/bml.hpp:153`**, one through each affected frontend unit. No diagnostic points to the added runtime controller. This is not a claim that the entire upstream project is warning-free.

The first sandbox shell attempt failed before compilation because the MSYS login setup/GCC temporary directory was outside writable locations. The successful build used a non-login MSYS bash and set `TMPDIR` to the ignored worktree test build directory. No global Git configuration or toolchain repair was needed.

Built executable: `<BSNES_EXE>`

Size: **9,729,667 bytes**

SHA-256: `0DEB112ECC1DDD44667A4355C68D00C6F54B84FCE19B0367ABCB750D440BC9FA`

Focused test command templates, from the observer worktree in UCRT64 (create `<OUTPUT_DIR>`, replace placeholders, and use fresh prefixes). `<BSNES_EXE>` denotes the desktop executable identified above:

```sh
g++ -std=gnu++17 -O0 -g -Wall -Wextra -Werror -isystem . \
  tests/exp001-runtime/observer-window-test.cpp bsnes/sfc/ppu/exp001-observer.cpp \
  -o "<OUTPUT_DIR>/observer-window-test.exe"
"<OUTPUT_DIR>/observer-window-test.exe" "<OUTPUT_DIR>/window-run-1"

g++ -std=gnu++17 -O0 -g -Wall -Wextra -Werror -isystem . \
  tests/exp001-runtime/frame-hash-test.cpp \
  -o "<OUTPUT_DIR>/frame-hash-regression.exe"
"<OUTPUT_DIR>/frame-hash-regression.exe" "<OUTPUT_DIR>/window-hash-regression-1"

python tests/exp001-runtime/observer-window-cli-test.py \
  "<BSNES_EXE>" "<OUTPUT_DIR>/window-cli-1"
```

Both C++ test builds passed with **no warnings**, assertions enabled. Both executables and the Python CLI test exited 0.

| Test | Actual result |
| --- | --- |
| No observer options, inactive harness, B2 | Controller inert, observer disabled, no provenance/summary creation |
| Synthetic B2/C 600-callback runs | Full native-hash-format CSV bytes identical; C captured only the synthetic work before callback 500, then disabled before 501 |
| Boundary ranges | Passed start=0, one callback, multiple callbacks, last callback, and full-run windows; clear at start and export only after return |
| Arithmetic/parser | Passed all six partial option combinations, no harness, duplicate/empty/malformed/signed values, zero count, uint64 overflow, outside-run ranges, and valid maximum exclusive-end arithmetic |
| Early termination | Passed not-started/no-CSV and partially observed/exported-incomplete cases; finalization idempotent |
| Overflow | Synthetic one-window 32,770 events retained 32,768 and dropped 2; exported prefix and explicit incomplete status; later hash callback still completed |
| Output protection | Existing provenance, existing summary, direct hash-path alias, and a file appearing after preflight all rejected/preserved |
| Export failure | A deliberately blocked staging file caused checked export failure, preserved count/status, and incomplete summary |
| Callback discipline | Zero or multiple callbacks per simulated run and an out-of-bracket callback were rejected |
| Existing hash regression suite | Known LE16 SHA-256 vector, row pitch/padding, count/metadata, disabled path, limits, errors, and exclusive output all passed unchanged |
| Built desktop CLI | **26 rejection cases passed** before settings/frontend initialization, using a plain text argument-existence sentinel; no ROM loaded or generated |
| Source protection | Hash implementation, callback hook, and all `bsnes/sfc/` source unchanged from starting HEAD; whitespace checks passed |

The 600-callback tests above use small synthetic pixel arrays and synthetic observer events. They are **not** 600 emulated SNES frames, do not establish the native window's PPU provenance, and do not supersede the user's required B2/C ROM runs. No runtime state comparison, native C record-count measurement, or performance measurement was performed here.

Evidence is retained under `<OUTPUT_DIR>/`: `observer-window-desktop-build.log`, `observer-window-compiler.txt`, `observer-window-test-build.log`, `observer-window-test-run.log`, `window-hash-regression-build.log`, `window-hash-regression-run.log`, synthetic `window-run-1-*`/`window-hash-regression-1-*` files, and `window-cli-1/results.json` with per-case stderr/stdout. The existing hiro destructor wrote a window-metrics cache under `window-cli-1/hiro/windows.bml`, inside the ignored evidence directory; normal bsnes settings were not initialized by those rejected invocations.

### 12.6 Exact recommended B2 and C command templates

Run each template from the GTC-HD repository root in **MSYS2 UCRT64**, using the newly built observer executable (`<BSNES_EXE>`) for both runs. Replace all placeholders before invocation. Supply the same authorized ROM and deterministic starting settings/persistent memory used for A1/A2/B. Restore equivalent starting conditions before each run because the normal frontend can save settings/game memory. Use distinct, new output paths with existing parent directories. No ROM path was supplied to this implementation task, so these commands were not executed here.

B2 — observer disabled, 600 native callbacks:

```sh
cd experiments/bsnes-exp-001
"<BSNES_EXE>" --settings="<SETTINGS_PATH>" \
  --exp001-frame-hash="<OUTPUT_DIR>/B2-600-frames.csv" \
  --exp001-frame-count=600 "<AUTHORIZED_ROM_PATH>"
echo "B2 exit: $?"
```

C — the same executable, observe the interval producing callback 500 only:

```sh
cd experiments/bsnes-exp-001
"<BSNES_EXE>" --settings="<SETTINGS_PATH>" \
  --exp001-frame-hash="<OUTPUT_DIR>/C-600-frames.csv" \
  --exp001-frame-count=600 \
  --exp001-observer-csv="<OUTPUT_DIR>/C-callback-500-provenance.csv" \
  --exp001-observer-start-callback=500 \
  --exp001-observer-callback-count=1 "<AUTHORIZED_ROM_PATH>"
echo "C exit: $?"
```

C also creates `C-callback-500-provenance.csv.summary.txt`. Require requested start 500/count 1/end 501, started/completed true, observed callbacks 1, total native callbacks 600, successful export, disabled observer at export, and explicit count/drop/overflow values. If overflow occurs, preserve that evidence and treat provenance as incomplete even if native hashes match. Do not preemptively increase capacity.

Compare the entire B2 and C frame-hash files to each other and to the prior A1/A2/B evidence, including all 600 ordered rows and completion footers. Their expected common digest is the user-provided value in section 12.1 **only if the actual reruns establish equality**. Inspect real provenance separately for meaningful BG/map/tile activity, timing/order, field interpretation, and bounded-buffer pressure. Emulator-state and performance questions remain open; matching framebuffer hashes alone cannot prove every CPU-visible side effect is unchanged.

## 13. Final-validation addendum — retained real-ROM evidence

**Documentation reconciliation:** September 23, 2026. **Result:** VERIFIED FOR TESTED EXP-001 CONDITIONS.

This addendum records the completed historical B2/C validation from retained artifacts and the user's validation-session record. It supersedes the pending outcome of section 12 without changing that dated implementation record. Artifact inspection and fingerprinting during documentation reconciliation did not run a test suite, rebuild an executable or execute a ROM. The evidence below comes from EXP-001's own captures.

### 13.1 Source and executable identity

| Identity | Historical reference |
| --- | --- |
| Harness baseline H / A reference | `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919` on `gtc-hd/exp-001-runtime-harness` |
| Observer with runtime controls / B2 and C source | `ba148bedc74892722de93633ce08190dda406bf7` on `gtc-hd/exp-001-passive-ppu-observation` |
| Earlier observer/harness stage recorded in section 12.1 | `2e0eeaa1580487f277e60f6ef55b9c74ca1026ae` |

The retained historical harness and observer checkouts were clean at H and the observer tip above when inspected. Their public equivalents remain separately identified in [Public implementation](#public-implementation); public commits did not produce these historical captures.

| Executable fingerprint | Bytes | SHA-256 |
| --- | --- | --- |
| Retained harness executable; matches the historical harness build fingerprint | 7,082,253 | `77C88B940B132E030D8E9A809F807422DD123572509F464483B2EBEA153D50B9` |
| Retained EXP-001 executable at reconciliation | 9,729,667 | `498E96F2643E87E73E6C2E63DF1EA1F396F74309DDD92B5FBB9C40A0C3AE0AC8` |
| Earlier runtime-controls implementation build, preserved from section 12.5 | 9,729,667 | `0DEB112ECC1DDD44667A4355C68D00C6F54B84FCE19B0367ABCB750D440BC9FA` |

**Identity limit:** The retained observer executable differs from the earlier documented build. The frame/provenance CSVs do not embed an executable hash, source commit or per-run input manifest. The source/run association above follows the historical experiment and session record; the exact executable-to-capture binding cannot be established from these artifacts alone. The retained fingerprint is not retroactively assigned to the earlier B run or substituted for section 12.5's build evidence.

### 13.2 Retained deterministic inputs

The session identifies the Super Mario World title-sequence validation described in section 12.1. The retained input files have these fingerprints:

| Input | SHA-256 |
| --- | --- |
| `Super Mario World (U) [!].sfc` | `D70C9C7716AD12C674FC7DD744736AA48D4D7B4237F58066BE620FDA26024872` |
| Deterministic settings seed | `E22FBA1B0E141499C94A25652C6A2FAEBEA27ADB8A11D4EC2E84BEDA43A8FA6B` |
| Deterministic SRAM seed | `D0FF1B294B5288D1AE1421EADF5B2D38A8752B76D472FF30BED9028E25B1C5B8` |

The retained settings seed specifies cycle PPU (`Fast=false`), `Entropy=None`, zero run-ahead frames, rewind frequency zero, automatic state loading off and blur off. These are retained input bytes, not a newly reconstructed command line. The mutable working settings differ from the seed; the CSVs alone do not establish seed restoration or live input for each historical process. The session's deterministic-run attribution and this evidence limit are both retained. ROM, settings and SRAM contents and their private storage locations are not published.

### 13.3 Completed framebuffer comparison

The five retained files `A1_LONG_FRAME_HASHES.csv`, `A2_LONG_FRAME_HASHES.csv`, `B_LONG_FRAME_HASHES.csv`, `B2_LONG_FRAME_HASHES.csv` and `C_LONG_FRAME_HASHES.csv` are byte-identical. Each contains callback indices 0–599, layout 512×480, pitch 1,024 bytes, scale 1, and the footer `actual_callbacks=600`, `completed=true`, `reason=count_reached`.

Their common complete-file SHA-256 is:

```text
92B098CF30A4171F707185B2A32918B8F361EDF30AC8BA6AA3F1FEAD39BAE96F
```

Thus the completed B2/C runs match each other and the established A1/A2/B reference. This extends the earlier reference digest in section 12.1 with actual retained B2/C evidence; it is not an assumption that a recommended command succeeded. It verifies native framebuffer passivity for this deterministic slice.

### 13.4 Completed BG capture and provenance

`C_CALLBACK_500_PROVENANCE.csv.summary.txt` records:

| Recorded field | Value |
| --- | --- |
| Requested callback start / count / exclusive end | 500 / 1 / 501 |
| Window started / completed; observed callbacks | true / true; 1 |
| Total native callbacks | 600 |
| Retained records / capacity | 23,760 / 32,768 |
| Dropped records / overflow | 0 / false |
| Observer enabled at export | false |
| Export attempted / succeeded; capture complete | true / true; true |
| Reason | `window_complete` |

The retained CSV contains those 23,760 BG-fetch records, including BG IDs 0–2 in BG mode 1, with actual map entries, character-row addresses, source coordinates, palette/priority values and native timing. Its observer frame IDs include 500 and 501. This is consistent with the callback-producing run interval in section 12.3; callback 500 is not redefined as one V=0-to-V=0 PPU period. The capture includes naturally scheduled fetch work, not only final visible pixels.

| Retained artifact | SHA-256 |
| --- | --- |
| `C_CALLBACK_500_PROVENANCE.csv` | `BCC8E15D28C2A7918E65ED03BA467F33A767EA7EDB3837B8BBF60C4E95B03964` |
| `C_CALLBACK_500_PROVENANCE.csv.summary.txt` | `AEFA348E6DBEBF3704A8307B58EEA7FCDC125D2E91BA1F473D04E907ABFF1D1A` |

### 13.5 Conclusion and remaining limits

**BG provenance preservation and native framebuffer passivity are VERIFIED FOR TESTED EXP-001 CONDITIONS.** Implementation and the supported build are complete, and the previously pending B2/C comparison is complete for the recorded slice.

This does not prove every CPU-visible side effect unchanged, complete emulator-state equality, unmeasured runtime cost, universal game/mode compatibility, Mode 7 provenance or final framebuffer visibility of each BG fetch. The executable/input binding limits in sections 13.1–13.2 remain explicit. Semantic preservation remains an architectural hypothesis requiring further experiments; no production architecture or emulator foundation is accepted by this result.
