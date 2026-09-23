# EXP-001 — Runtime validation harness

## Current context

**Harness:** IMPLEMENTED / SUPPORTED BUILD PASSED / EXERCISED IN COMPLETED EXP-001 RUNTIME VALIDATION.

The [current EXP-001 result](RESULTS.md#current-result) is **VERIFIED FOR TESTED EXP-001 CONDITIONS**: retained deterministic real-ROM A1/A2/B/B2/C native-frame CSVs agree across 600 completed callbacks. This establishes the tested framebuffer comparison, not complete execution-state equivalence or universal harness correctness. The September 19 record below describes the earlier harness implementation pass, when no native callbacks had yet been captured in that task.

## Public implementation

Public fork: [AbslanLaverde/bsnes](https://github.com/AbslanLaverde/bsnes). This branch provides shared validation infrastructure, independently of the BG observer branch.

| Identity | Commit / source |
| --- | --- |
| Historical runtime-harness commit H | `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919` |
| Public research equivalent H | [ac488fe85289642bfedc6b5001146cc3effe6d8a](https://github.com/AbslanLaverde/bsnes/commit/ac488fe85289642bfedc6b5001146cc3effe6d8a) |
| Public branch | [gtc-hd/exp-001-runtime-harness](https://github.com/AbslanLaverde/bsnes/tree/gtc-hd/exp-001-runtime-harness) |
| Unchanged upstream baseline U | `7d5aa1e656b9171524d01b1b22917197d8121cb4` |

[Compare upstream U → public harness H](https://github.com/AbslanLaverde/bsnes/compare/7d5aa1e656b9171524d01b1b22917197d8121cb4...ac488fe85289642bfedc6b5001146cc3effe6d8a). The [publication map](../../research/BSNES_EXPERIMENT_PUBLICATION_MAP.md) explains the historical/public identities.

H records the historical harness implementation; the report below preserves its earlier uncommitted implementation-pass context. Its executable hash and build evidence remain historical and do not identify a public rebuild. Focused publication checks remain separate from the historical real-ROM comparison summarized in the current EXP-001 result.

## Historical harness implementation record — September 19, 2026

All pending/unverified statements, zero-callback counts and next-step recommendations below refer to this implementation pass, not the later completed experiment. Its build hashes and evidence remain unchanged.

**Date:** September 19, 2026  
**Status:** IMPLEMENTED / SUPPORTED BUILD PASSED / NATIVE RUNTIME VALIDATION PENDING  
**Native callbacks captured in this task:** 0  
**A/B/C comparison:** Not performed; EXP-001 has not passed.  
**Architecture impact:** None. bsnes remains a research target.

## Repository and authority

Workspace: `<GTC-HD-Lab>`.

| Repository | Branch | HEAD at start and completion |
| --- | --- | --- |
| Writable: `experiments/bsnes-exp-001-baseline/` | `gtc-hd/exp-001-runtime-harness` | `7d5aa1e656b9171524d01b1b22917197d8121cb4` |
| Read-only: `experiments/bsnes-exp-001/` | `gtc-hd/exp-001-passive-ppu-observation` | `0f946d112f045d5cf29a9e09876b15a592180b62` |
| Read-only: `upstream/bsnes` | `master` | `7d5aa1e656b9171524d01b1b22917197d8121cb4` |

The writable repository root is `experiments/bsnes-exp-001-baseline/`. It is a linked Git worktree using `upstream/bsnes/.git/worktrees/bsnes-exp-001-baseline` and the shared Git directory `upstream/bsnes/.git`. Normal Git commands work; its pointers use Windows-compatible paths. All three source worktrees were clean before implementation. The baseline ancestry check passed. No commits, branch changes, merges, or worktree-metadata repairs were made.

Read before editing: root `AGENTS.md`, `project/GTC-HD_PROJECT_STATE.md`, the EXP-001 specification, and `project/experiments/EXP-001_RESULTS.md`. The specification exists at `project/expies/EXP-001_PASSIVE_PPU_OBSERVATION.md`; the requested `project/experiments/EXP-001_PASSIVE_PPU_OBSERVATION.md` is absent. The existing specification was read without moving or changing it. The older results report describes an earlier toolchain state; it was not rewritten.

Project authority remains under `project/`. Experimental source and successful builds do not establish accepted GTC-HD architecture. Root instructions, canonical project state, existing experiment documents, and both read-only source checkouts remain unchanged. Root `.gitignore` was already modified before this task and remains unchanged by it; `project/experiments/` already contained untracked reports/logs. Only this report is newly authored outside the writable bsnes worktree.

## Files changed

Source paths below are relative to the writable repository.

| File | Change |
| --- | --- |
| `bsnes/target-bsnes/program/exp001-frame-hash.hpp` | New opt-in option parser, streaming SHA-256/CSV capture, count/status, checked file I/O |
| `bsnes/target-bsnes/program/program.hpp` | Include and own the frontend capture object |
| `bsnes/target-bsnes/bsnes.cpp` | Parse diagnostic options before initialization, reject invalid requests, open the output |
| `bsnes/target-bsnes/program/platform.cpp` | Hash at entry to `Program::videoFrame()`; reject fast-PPU configuration |
| `bsnes/target-bsnes/program/program.cpp` | Detect load failure; stop on the frontend after a capture limit/error; finalize before existing shutdown |
| `tests/exp001-runtime/frame-hash-test.cpp` | Focused synthetic host tests; no ROM or emulator execution |
| `tests/exp001-runtime/.gitignore` | Ignore this test's `/build/` outputs |

The new document is `project/experiments/EXP-001_RUNTIME_HARNESS_RESULTS.md`. Source changes are **uncommitted**, leaving the baseline worktree dirty for review. No `exp001-observer.cpp`, `exp001-observer.hpp`, BG provenance collection/export, or observer controls were added. `bsnes/sfc/` and `nall/` have no changes. The harness has not been applied to the observer branch.

## Source observations: startup, capture, shutdown

At the recorded baseline, `bsnes/target-bsnes/bsnes.cpp::nall::main()` parses `--fullscreen`, `--locale=`, `--settings=`, existing ROM paths, and the existing `option;path` syntax. Recognized games enter `Program::gameQueue`. Settings and frontend instances are initialized, a `SuperFamicom::Interface` is constructed, and `Program::create()` installs `Program::main()` as the application callback before `Application::run()` enters its event loop.

`program/game.cpp::Program::load()` configures the core, loads media, applies per-game compatibility settings, powers the system, optionally loads an automatic state, loads cheats, and updates video effects. `program/program.cpp::Program::main()` polls input, handles inactive/paused execution, processes rewind/run-ahead, and invokes `emulator->run()`.

`bsnes/sfc/system/system.cpp::System::run()` returns from the scheduler and dispatches a frame event. `System::frameEvent()` calls `PPU::refresh()`. The cycle implementation in `bsnes/sfc/ppu/ppu.cpp` supplies `platform->videoFrame(output, pitch * sizeof(uint16), width, height, 1)` at **512 x 480**, **1024-byte pitch**, **scale 1**. The core's optional blur and controller drawing occur **before** that call. `PPU::power()` clears the cycle output buffer. Interlaced output can retain the previous field's pixels; the harness preserves the complete supplied layout.

The chosen interception point is the **entry to `Program::videoFrame()`** in `program/platform.cpp`, before any existing statements. This precedes the screenshot pointer assignment, pitch conversion, overscan crop, `viewportSize()`, `filterSelect()`, palette conversion through `filterRender()`, and video presentation. `Program::viewportRefresh()` redraws a paused image separately and does not call the capture hook.

**Implication:** this boundary captures native callback samples before frontend transformation, provided core blur and cursor overlays are disabled. It is not a hook before all optional core-side processing. A fast-PPU configuration is explicitly rejected at the hook using `emulator->configuration("Hacks/PPU/Fast")`. For the prescribed cold-start runs, `Program::hackCompatibility()` has already set that configuration before `System::power()` latches the PPU implementation. Do not reconfigure or reset during a capture.

After the Nth row is successfully written and flushed, the capture object sets its frontend `stop` flag. It does not terminate from the callback or PPU. `Program::main()` checks the flag after core execution returns, before autosave work, and calls the existing `Program::quit()`; a check at main-loop entry also handles requests made during other frontend operations.

`Program::quit()` explicitly finishes/closes the capture and removes the main-loop callback before processing shutdown events. It then retains normal hide/unload/settings-save/driver-reset behavior. On Windows, the existing frontend uses `TerminateProcess` after that cleanup; the harness therefore does not rely on destructors to save its result. Successful capture exits 0; an incomplete or failed capture exits 1. Early argument/output failures print to stderr and exit 1 before settings load/frontend initialization. Normal game-load failure also requests the existing frontend shutdown with incomplete status.

## Hash and output contract

`Exp001FrameHash` uses the existing `nall::Hash::SHA256` from `nall/hash/sha256.hpp`. No crypto dependency or core modification is introduced.

For each callback, starting at row zero:

1. Locate row `y` at `reinterpret_cast<const uint8_t*>(data) + size_t(y) * pitch`.
2. Read exactly `width` native 16-bit samples using `memcpy` into a `uint16_t` value.
3. Feed each sample's low byte and then high byte to SHA-256: `sample & 0xff`, `sample >> 8`.
4. Append one CSV row and flush it; increment `actual` only after a successful write/flush.

The digest covers exactly `width * height * 2` bytes in top-to-bottom, left-to-right order. It excludes row padding, C++ object padding, metadata, frontend RGB output, and screenshots. Native 512 x 480 callbacks contain 491,520 hashed bytes. Dimensions, pitch, and scale must be compared separately alongside the digest. No ROM contents or pixel payload are written.

Options:

```text
--exp001-frame-hash=<OUTPUT_PATH>
--exp001-frame-count=120
```

The output option enables capture. Count defaults to **120** and accepts only positive decimal integers through `18446744073709551615`; it is invalid without the output option. Empty values, zero, malformed/overflowing counts, duplicate options, and unknown `--exp001-` options are errors. An existing game path must be supplied through the normal argument handling. The harness is not an interactive arm-later mode.

The output is created **exclusively**: an existing file is never overwritten. Its parent directory must exist. Windows paths use nall's UTF-16 conversion with `_wfopen`. Do not reuse the same output filename for successive runs. With no harness options, no capture file is opened, samples are not hashed, and there is no automatic capture shutdown. Existing `--settings=` handling remains available; default-settings lookup is deferred until after diagnostic argument checks.

CSV format, with `# key=value` metadata/comment lines:

```text
# exp001_frame_hash_version=1
# requested_callbacks=120
# index_base=0
index,width,height,pitch,scale,sha256
0,512,480,1024,1,<64 lowercase hexadecimal characters>
...
119,512,480,1024,1,<64 lowercase hexadecimal characters>
# actual_callbacks=120
# completed=true
# reason=count_reached
```

This is a **schema illustration**, not real capture evidence. Callback indexing begins at **0**, so a successful N-callback run contains indices `0..N-1`. Counts refer to delivered video callbacks, not inferred game frames, paired interlaced fields, or observer frame identifiers. There is no warm-up skip.

For parsing, separate the `# ` metadata lines and parse the remaining lines as ordinary CSV. Require the expected version, six named columns, consecutive indices, correct metadata, `actual_callbacks == requested_callbacks == row count`, `completed=true`, `reason=count_reached`, and **process exit 0**. Compare the entire ordered row sequence across runs.

A user quit before the limit writes `completed=false`, `reason=interrupted`, and the actual number of flushed rows. Detected failures use a fixed reason token such as `cycle_ppu_required`, `game_load_failed`, `invalid_callback_metadata`, or `output_write_failed`. The finalization method is idempotent. A crash/forced termination or write failure can leave a partial file without a usable footer; never interpret it as success. Close failure can occur after the footer was written, which is why checking exit status as well as the file is necessary.

## Deterministic-run requirements

The harness measures output; it does not make arbitrary gameplay deterministic. Except for rejecting fast PPU, these are **operator requirements**, not settings silently forced by the harness. No bsnes settings file was loaded or rewritten during this task's non-ROM checks. The existing hiro static destructor did create a local window-metrics cache, as recorded below.

Use a dedicated settings file via `--settings=`, keep an untouched starting copy, and restore equivalent starting conditions for every A/A, A/B, and B/C run. The normal frontend writes settings at load/shutdown and saves game memory on unload; that existing behavior is retained.

| Condition | Frontend setting / source reason |
| --- | --- |
| Cycle PPU | `Emulator/Hack/PPU/Fast=false`; maps to core `Hacks/PPU/Fast`. This defaults to true upstream, so explicitly disable it before starting. No live PPU changes. |
| No run-ahead | `Emulator/RunAhead/Frames=0`; speculative runs suppress some callbacks and serialize/restore state. |
| No rewind | `Rewind/Frequency=0`; no rewind hotkey. Rewind serializes and can emit extra callbacks during synchronization. |
| No cheats | `Emulator/Cheats/Enable=false`; keep cheat files fixed/empty. Cheat activation can patch memory, and `System::frameEvent()` applies codes. |
| No frame skipping / fast-forward | `FastForward/FrameSkip=0`, no fast-forward hotkey, normal speed. The fast-PPU path implements skipping; do not rely on any skipped sequence. |
| No native blur | `Video/Blur=false`; `Program::updateVideoEffects()` maps it to core `Video/BlurEmulation`, which changes the buffer before the callback. |
| No cursor overlay | Use `Gamepad` or `None` on controller ports, especially port 2. The frontend paths are `SuperFamicom/ControllerPort1` and `SuperFamicom/ControllerPort2`. Avoid mouse/light-gun devices; controller drawing precedes the hook. |
| Deterministic initialization | For the initial framebuffer repeatability test, use `Emulator/Hack/Entropy=None` on every run; default Low entropy initializes memory from a clock-seeded RNG. `bsnes/emulator/random.hpp` still contains a time-dependent hidden RNG state even with None, so this does not establish serialized-state equality. |
| Cold starts, no state operations | `Emulator/AutoLoadStateOnLoad=false`, `Emulator/AutoSaveStateOnUnload=false`; no manual save/load/reset/power/reload during capture. Synchronized serialization can execute frame events. |
| Identical persistent data | Restore the same SRAM, RTC, auxiliary media, state files, firmware, patches, and configuration before each run. Use isolated copies/paths; normal unload saves memory. Optionally disable `Emulator/AutoSaveMemory/Enable` to avoid periodic host I/O, consistently across runs. |
| Identical region/core settings | Same game/region selection, PPU revisions, CPU/coprocessor/compatibility options, build flags, firmware, and patch set. Record game identity and SHA-256 separately once a ROM is supplied. |
| Identical input | For initial neutral-input runs, `Input/Driver=None` avoids live device input. Use identical standard-gamepad connections and no UI actions. A later input-driven test needs an identical prerecorded/scripted input sequence; this harness does not add one. |
| Stable frontend operation | A focus-loss Pause setting or dialog can stall capture. For neutral-input runs, `Input/Defocus=Block` avoids pausing without accepting unfocused input. Keep audio/video drivers and timing settings fixed; rendering filters/cropping are after the hash but can change host timing. |

Source evidence for these requirements is in `program/game.cpp`, `program/program.cpp`, `program/hacks.cpp`, `program/video.cpp`, `program/rewind.cpp`, `program/states.cpp`, `program/platform.cpp`, `input/hotkeys.cpp`, `settings/settings.cpp`, `presentation/presentation.cpp`, `bsnes/sfc/system/system.cpp`, and `bsnes/emulator/random.hpp`. Start with non-RTC SNES test content once supplied; clock-dependent cartridge behavior requires additional control. First demonstrate A/A repeatability before drawing conclusions from A/B/C.

Exact 120-callback command template, from the writable repository in **MSYS2 UCRT64**, after preparing a dedicated `<SETTINGS_PATH>` with the conditions above:

```sh
"<BSNES_EXE>" --settings="<SETTINGS_PATH>" --exp001-frame-hash="<OUTPUT_PATH>" --exp001-frame-count=120 "<ROM_PATH>"
```

Use an existing authorized `<ROM_PATH>`, a new `<OUTPUT_PATH>`, and quote paths containing spaces. This command was not run with a ROM in this task. The application remains the normal desktop frontend; this is not a headless emulator target.

## Build environment and measured results

Supported environment: **MSYS2 UCRT64**, with `g++` and GNU `make` on PATH.

Actual `g++ --version` output:

```text
g++.exe (Rev3, Built by MSYS2 project) 16.2.0
Copyright (C) 2026 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

Build working directory: `experiments/bsnes-exp-001-baseline/`.

```sh
export PATH=/ucrt64/bin:/usr/bin:$PATH
make -j4 -C bsnes local=false
```

**Result: exit 0.** A complete desktop build compiled the core, frontend, hiro, ruby, and supporting objects from the initially empty object directory. The final small argument-handling adjustment was rebuilt and relinked with the same command, also exit 0. Configuration remained upstream `target=bsnes`, `binary=application`, `build=performance` (`-O3`), OpenMP enabled, and `local=false` (no `-march=native`). No dependencies were downloaded or installed.

The complete build emitted **77 warnings in unchanged upstream code**: 27 `-Wcast-user-defined` diagnostics in `nall/string/markup/bml.hpp`, 49 unsupported visibility-attribute diagnostics in Game Boy core code, and one `-Woverflow` diagnostic at `gb/Core/save_state.c:1531`. The final incremental build repeated one BML diagnostic. **No full-build diagnostics point to the added harness code.** No warning fixes or compiler workarounds were made to upstream sources. An initial shell launch lacked make on PATH and exited 127 before compilation; setting the UCRT64/MSYS paths as above resolved it.

Executable: `<BSNES_EXE>` (the built desktop executable; private output location omitted)\
Size: **7,082,253 bytes**  
Final executable SHA-256: `77c88b940b132e030d8e9a809f807422dd123572509f464483b2ebea153d50b9`

Generated evidence is under `<OUTPUT_DIR>/` (an ignored directory whose private location is omitted): `desktop-build.log`, `desktop-final-build.log`, `compiler-version.txt`, `test-build.log`, `test-run.log`, `cli-results.json`, per-case CLI stderr/stdout logs, the test executable, and synthetic CSV files. The desktop executable and object/dependency files are covered by existing bsnes ignore rules. The existing destructor in `hiro/windows/settings.cpp` generated `hiro/windows.bml` during CLI exit; this new 171-byte window-metrics cache was moved into the ignored evidence directory as `cli-windows.bml` so it is not left among source changes.

## Tests actually performed

Standalone host-test command templates, from `experiments/bsnes-exp-001-baseline/` in UCRT64; replace `<OUTPUT_DIR>` with the generated evidence directory:

```sh
g++ -std=gnu++17 -O0 -g -Wall -Wextra -Werror -isystem . tests/exp001-runtime/frame-hash-test.cpp -o "<OUTPUT_DIR>/frame-hash-test.exe"
"<OUTPUT_DIR>/frame-hash-test.exe" "<OUTPUT_DIR>/run-1"
```

Create the ignored build directory first. Use a fresh output prefix on reruns because captures use exclusive creation. Assertions were enabled. **Build and test both exited 0; the final test build emitted no warnings.** An exploratory `-O2 -Werror` test compilation reported `-Wmaybe-uninitialized` inside the unchanged nall adaptive string allocator while constructing test paths; the passing focused check used `-O0 -g`, while the actual desktop build still used its normal `-O3` profile.

| Test | Actual result |
| --- | --- |
| Known LE16 byte vector | `0x1234, 0xabcd, 0x0000, 0xffff` hashes as bytes `34 12 cd ab 00 00 ff ff`; matches independently computed .NET SHA-256 `70c4c3aba1f41ffeb14f469d4aa682cacfae3ff7b25fcf655b55baf96fb074c5` |
| Pitch/padding | Two padded rows match packed rows; changing every padding sample leaves the digest unchanged |
| Callback metadata | Exact index, width, height, byte pitch, and scale values written; scale does not alter sample encoding |
| Count and disabled operation | Explicit count 3 and default 120 stop at their exact limits; later capture calls add nothing; disabled object produces no captures or stop request |
| Completion/errors | Complete and interrupted summaries, invalid row metadata, idempotent finalization, exclusive file creation, and existing-content preservation passed |
| Argument bounds | Empty/zero/negative/signed/nondecimal/overflow counts rejected; maximum uint64 accepted; missing output, duplicate count, empty path, unknown option rejected |
| Independent CSV verification | PowerShell parsed all 120 synthetic rows; verified indices 0..119, all metadata, and the independent .NET digest |
| Built desktop CLI, no ROM | Six cases passed: zero, overflow, count-only, empty output, unknown option, output without ROM. Each exited 1 with the expected `EXP-001:` stderr reason. No result file was generated for missing ROM. Final executable's missing-ROM path was rechecked after the last rebuild. |
| Source/scope review | Only the permitted frontend/test paths changed; no core/nall diff or provenance observer source; protected files and read-only repository identities/statuses checked |

Synthetic CSV records are not native PPU frames. The host tests do not execute the PPU, exercise a real game load, demonstrate frontend shutdown after real frame callbacks, or establish passivity.

## Unverified behavior, risks, and next step

No ROM was supplied, searched for, opened, downloaded, or used. Native framebuffer capture, native callback counts/termination, frontend behavior with capture disabled during gameplay, fast-PPU rejection during real gameplay, load-failure integration, disk-full/close-error behavior, and A/B/C output equality remain **runtime-unverified**. There are no ROM identity/hash, real frame digests, provenance findings, state-comparison results, or runtime performance measurements to report.

Source review indicates that capture reads callback memory without modifying native samples or emulated state. That is an inference from the implementation, not experimental proof of unchanged SNES execution. Per-byte SHA-256, configuration inspection, and per-row-of-CSV flushing add host overhead and can affect uncontrolled real-time input. No asynchronous writer or generalized telemetry system was added.

The capture has no watchdog: paused/modal execution or a game that produces no callbacks can wait indefinitely. A controlled manual quit produces incomplete status. The normal frontend may prompt about unverified content or missing firmware. Do not disable prompts indiscriminately; resolve expected content/initialization before comparative runs. File errors may leave incomplete output. Validate both footer and process status. Only Windows/UCRT64 was built/tested.

No serializer changes were made. Pixel equality is necessary evidence for EXP-001 but does not prove equality of CPU-visible PPU side effects or complete emulator state. Existing state-comparison concerns, including clock-seeded hidden RNG state and coroutine-stack serialization, remain documented in `RESULTS.md`.

Next step: after the user supplies a ROM path, establish controlled cold-start conditions and repeat the baseline 120-callback run with two distinct output paths. Verify A/A equality first. Then apply this same frontend harness unchanged to an explicitly authorized observer worktree and compare A/B/C at every callback while separately validating provenance and any trustworthy state checkpoints. No architecture decision follows from the build or these synthetic tests.
