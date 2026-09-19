# EXP-001 — Passive PPU Observation: implementation results

**Date:** September 18, 2026  
**Status:** IMPLEMENTED / RUNTIME VALIDATION PENDING  
**Desktop build:** BLOCKED by the available toolchain  
**Experiment outcome:** Not established. EXP-001 has not passed.  
**Architecture impact:** None; bsnes remains a research target, not a selected dependency.

The observer and its host-only tests are implemented. The standalone observer compiled and its storage/export tests passed. The complete emulator has not built or run in this environment, so production of records by the actual cycle PPU, native-output equality, execution-state equality, and runtime overhead remain unverified.

## 1. Authority, repository, and working-tree identity

Workspace root: `C:/Users/User/Documents/GTC-HD-Lab`.

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

Local generated files, all under the ignored `experiments/bsnes-exp-001/tests/exp001/build/` directory: `observer-test.exe`, `observer-test.obj`, `exp001-observer.obj`, `observer-test.csv`, `observer-msvc.log`, `ppu-msvc.log`, and `baseline-ppu-msvc.log`. The CSV contains **synthetic host-test records**, not captured SNES activity. Failed PPU compilation produced no PPU object or desktop executable.

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

Working directory: `C:/Users/User/Documents/GTC-HD-Lab/experiments/bsnes-exp-001`.

`bsnes/GNUmakefile` selects the desktop `target=bsnes`, `binary=application`, `build=performance`, and OpenMP by default. `local=false` removes the default `-march=native`. For Windows, `nall/GNUmakefile` selects GNU `g++`, GNU C++17, Windows/MinGW libraries, and `windres`; the performance profile uses `-O3`. A debugger build can use `make -j4 -C bsnes local=false build=debug` once the supported toolchain is present.

**Actual attempt:** failed before compilation because PowerShell could not find `make` (exit 1). GNU make, g++, GCC, windres, and Clang were not available in the examined tool locations/PATH. WSL listed only Docker Desktop, not a general development distribution. No toolchain, dependency, ROM, or container image was installed/downloaded. There is no GNU compiler version or completed desktop build to report.

### Strongest available build validation

Visual Studio's existing **MSVC 19.50.35728 x64** compiler was available through its developer environment. The standalone observer was compiled and linked with its tests under C++17, warnings-as-errors, disabled optimization, and runtime checks.

Commands below are `cmd.exe` syntax, executed in `experiments/bsnes-exp-001/tests/exp001/build` through PowerShell's `ComSpec`. Compiler output was captured in `observer-msvc.log`.

```bat
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
cl /std:c++17 /EHsc /W4 /WX /Od /RTC1 /Fe:observer-test.exe /Fd:observer-test.pdb ../observer-test.cpp ../../../bsnes/sfc/ppu/exp001-observer.cpp
observer-test.exe observer-test.csv
```

Both build and test exited 0. **No warnings** were emitted by this observer-only build. Assertions were enabled. Output:

```text
PASS: copy ownership, ordering, disabled capture, bounds, overflow, reset, CSV
record_bytes=48 capacity=32768
```

A direct native PPU translation-unit probe was also attempted with MSVC:

```bat
cl /nologo /std:c++17 /EHsc /c /I../../../bsnes /I../../.. /Fo:ppu-msvc.obj ../../../bsnes/sfc/ppu/ppu.cpp
```

It exited 2 in pre-existing headers before the observer integration could be type-checked. A matching read-only probe of the pristine source used absolute include/source paths and `/Fo:baseline-ppu-msvc.obj` in the experiment's build directory:

```bat
cl /nologo /std:c++17 /EHsc /c /IC:/Users/User/Documents/GTC-HD-Lab/upstream/bsnes/bsnes /IC:/Users/User/Documents/GTC-HD-Lab/upstream/bsnes /Fo:baseline-ppu-msvc.obj C:/Users/User/Documents/GTC-HD-Lab/upstream/bsnes/bsnes/sfc/ppu/ppu.cpp
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
