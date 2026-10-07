# Candidate A Accepted-Baseline Transfer Revalidation

**Current-disposition notice — 2026-10-06:** EXP-001/002/003 are **VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE**. See [resumed transfer results](#resumed-transfer-results--2026-10-05). The initial stop and diagnosis below are historical and remain unchanged. Later explicit reauthorization and completed [EXP-004 results](../experiments/EXP-004/RESULTS.md) supersede this report's pre-reauthorization EXP-004 gate; current EXP-004 is **VERIFIED FOR TESTED EXP-004 CONDITIONS**. No new implementation is authorized by this notice.

## Historical initial transfer stop

Date: 2026-10-05.

**Disposition: STOPPED / BUILDS AND FOCUSED HOST CHECKS PASSED / RUNTIME TRANSFERS INCOMPLETE.**

**EXP-004 remains blocked because the fresh corrected harness-only control did not complete startup/runtime capture.** It timed out after 180 seconds before producing its first native framebuffer row. No corrected observer ROM run or targeted bounds ROM run followed. There is no new runtime evidence transferring EXP-001/002/003 claims and no basis to advance the EXP-004 gate.

## Decision and identities

Xavier accepted `46fa75236fa61d49d8e9424b3b44694b88aa07a9` (Candidate A, `Prototype padded output backing for native bounds`) as the corrected **experimental research baseline**. It retains pointer-safe 512x496 backing, 512x480 presentation, native late stores and defined pair-240 transition clearing. Candidate B remains a viable tested alternative, not selected. This acceptance does not select bsnes as the final core, establish universal hardware correctness, imply upstream acceptance, or authorize EXP-004.

The accepted correction's existing harness descendant `13e19564bd038e3767a58b9f1f1d29b1d5f4f527` is the starting commit of all four new worktrees. The established harness derives from `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919`. The harness commit is not the accepted native correction identity.

GTC-HD-Lab began clean on `main` at `bc689967bee964b29d1ab4dd6c5e9f6643a61262`. The external repository is bsnes. Its protected upstream checkout remains on `master` at `7d5aa1e656b9171524d01b1b22917197d8121cb4`. All pre-existing experiment/prototype/runtime branches and working files were preserved.

| Build | New worktree | Branch |
| --- | --- | --- |
| Corrected harness control | `experiments/bsnes-candidate-a-revalidation-baseline/` | `gtc-hd/candidate-a-revalidation-baseline` |
| EXP-001 | `experiments/bsnes-exp-001-corrected/` | `gtc-hd/exp-001-corrected-baseline` |
| EXP-002 | `experiments/bsnes-exp-002-corrected/` | `gtc-hd/exp-002-corrected-baseline` |
| EXP-003 | `experiments/bsnes-exp-003-corrected/` | `gtc-hd/exp-003-corrected-baseline` |

No new source commit was created because runtime revalidation is incomplete. The control is clean at the harness descendant. The three observer integrations remain staged and uncommitted at that same HEAD; the following Git **tree objects**, not commits, identify their exact built source snapshots:

| Integration | Historical observer source reused | Built/staged tree object |
| --- | --- | --- |
| EXP-001 | `ba148bedc74892722de93633ce08190dda406bf7` | `61d75f7afbaaf45d6b023ef057e2ca3a0d5fd276` |
| EXP-002 | `f0f90ee799969b735ca90b6dd9491219f0b9cc92` | `d7394a2f38942ee3e5990dced3111c8300baa9d8` |
| EXP-003 | `76bdb9250befa62fcbf23fcff2ef962fe2f58215` | `07f80649ff9681fb0e566a12d549082e1203330b` |

The historical harness-to-observer changes were applied with Git's three-way merge to each fresh corrected checkout. Direct application first rejected EXP-001's changed `ppu.cpp` context; it made no partial edit. All three three-way applications completed without conflict. There was no observer redesign, semantic-field addition, manual source repair or test-expectation change.

## Fresh builds

All four complete desktop builds passed using existing **MSYS2 UCRT64, g++ 16.2.0 (Rev3, Built by MSYS2 project)**. From each new checkout, in a non-login UCRT64 environment with the compiler and MSYS utilities on PATH and `TMPDIR` set to a writable evidence directory:

```sh
make -j4 -C bsnes local=false
```

The inherited desktop/performance configuration uses GNU C++17, `-O3` and OpenMP; `local=false` avoids `-march=native`. Each build emitted the same 77 inherited upstream warnings in `nall/string/markup/bml.hpp` and Game Boy sources. No warning location was in observer code. No toolchain/dependency was installed.

| Build | Executable bytes | Executable SHA-256 |
| --- | ---: | --- |
| Corrected harness control | 7,082,253 | `3F1C09FC603EFD8AC29E4FBD480ACA362C981819EA50991FB9B2D9F12B70B48F` |
| EXP-001 | 9,729,667 | `D69B064DD54D233F013BA283390A832DD9ECAF6729C9447AF0043627B84C6299` |
| EXP-002 | 9,740,170 | `F78FD4EFB4699483DEE4AD86F89EC2554AB38460E5F19F96DB0EC7B97B488735` |
| EXP-003 | 21,295,974 | `9F59FD335261A7D7CF15FF43E22EA8C4EB56258E1EBCAB9CE7FA1B65B51B359F` |

## Focused observer checks

All original focused tests were retained unchanged and passed. Exact command templates are in the [revalidation tooling instructions](../../tests/accepted-baseline-revalidation/README.md).

| Experiment | New-build host result |
| --- | --- |
| EXP-001 | Storage ownership/order, default-disabled/reset behavior, fixed 32,768-record capacity, 48-byte records, overflow/drop reporting and CSV passed. Callback-window tests, synthetic B/C 600-callback equality, unchanged frame hasher and all 26 desktop CLI rejection cases passed. |
| EXP-002 | Actual OBJ/OAM evaluation/fetch/winner lineage, native overlap/rotation, transparent nonreplacement, double-bank lifetime/reuse, 32-item/34-tile limits, partial fetch, flips/interlace, reset/gating and native-state comparison passed. Window/hasher tests, all 26 CLI cases and 14 CSV schemas passed; records remain 104 bytes. |
| EXP-003 | Actual native BG/OBJ/composition lineage, independent main/sub decisions, priority/ties, backdrop/skipped, windows, hires, native-state passivity and CSV passed. Window/hasher tests, all 26 CLI cases and 15 CSV schemas passed; records remain 176 bytes, capacity 65,536. |

EXP-002's native OBJ signature remained `4e5d2fad085fe9c09ce91e1ae01174f77b5b171d406f2c3cfc775d2a9af97364`. EXP-003's composition and pipeline signatures remained `f8952120fe226387b07fc3c6f8d1e3c931e0b44a145cc7c37b436e03810dc2f1` and `03df6a8c62befa48a4edb6f39dbe72d8c730338aedd10e80469482e698e4fe5b`.

These original fixtures use bounded synthetic hosts. In particular, EXP-003's original composition fixture still uses its historical 512x480 substitute array and valid-row scenarios; its pass alone does not test Candidate A's expanded backing. The additional native-declaration fixture below covers that boundary.

## Candidate A correction regression

The new [host driver](../../tests/accepted-baseline-revalidation/run_host.py) first checked each integrated `bsnes/` tree against its original observer revision: the only differing files were `bsnes/sfc/ppu/{ppu.hpp,ppu.cpp,main.cpp,screen.cpp}`, and their exact added/deleted source lines matched upstream-to-Candidate-A correction lines. Every other native/frontend/observer file matched its historical observer counterpart. Existing experiment tests were also unchanged. This checks retention of backing extent/initialization, guarded pointer formation, +7 centering, 512x480 callback, pair-240 clearing, lookup/store order and native V=240 scheduling.

It then reused Candidate A's `tests/native-output-bounds/native-fixture.cpp` assertions with actual integrated PPU declarations/methods, adding only observer includes and namespace wiring in generated host copies. Eight configurations (control and three integrations at `-O0`/`-O3`, lookup/palette tracing enabled) passed and had equal case counts and byte-identical presentation, native-field-state and screen streams. Observers were disabled by normal reset; these checks do not claim enabled-capture coverage of every bounds scenario.

Each configuration retained 253,952 output entries and passed 4,596 geometry cases, 1,536 screen cases, 84 pipeline cases, 16 transition-clear cases, 756 no-store-line checks, 28,672 mixed-CGRAM checks, 8 counter fields and 18 late-effect witnesses; 663,552 late-tail samples were retained. Callback assertions kept width=512, height=480, pitch=1024 and scale=1. The fixture also covered three controlled native-field restore cases, not full-system/coroutine save-state compatibility.

| Equal host stream across all eight configurations | Bytes | SHA-256 |
| --- | ---: | --- |
| Presentation | 58,867,712 | `2dd1e3030a36dedb7b86542a4baa3b835c3de2f2aa52d815b9e366e7cbb0bbe6` |
| Native-field state | 7,538,570 | `43127ca951178b5d5d7d09f446bcc69515da9464f8b8f8dfd241c665f265c515` |
| Screen | 11,796,480 | `0de76830b0eb3ef88286aad1dc2148c1d30f2c26ceb0b0987b6e59f44b68b374` |

Runtime sanitizers were not used. No original undersized output buffer was executed by these host checks.

## Runtime preflight and first stop

The [finite runtime driver](../../tests/accepted-baseline-revalidation/run_runtime.py) verified the retained inputs and historical references before launching anything. It imported the existing [targeted bounds fixture](../../tests/native-output-bounds-runtime/README.md) builder/oracle without editing them and generated the same short fixture. Expected output/counts were fixed before execution; none was regenerated from a new executable.

| Input | SHA-256 |
| --- | --- |
| Super Mario World (U) [!].sfc | `D70C9C7716AD12C674FC7DD744736AA48D4D7B4237F58066BE620FDA26024872` |
| SRAM seed | `D0FF1B294B5288D1AE1421EADF5B2D38A8752B76D472FF30BED9028E25B1C5B8` |
| Settings seed | `E22FBA1B0E141499C94A25652C6A2FAEBEA27ADB8A11D4EC2E84BEDA43A8FA6B` |

The first launch restored these bytes into a fresh isolated run directory. The settings retained cycle PPU, deterministic entropy, normal sprite/VRAM rules and the established Direct3D 9.0 / waveOut / input-None configuration. Windows launch requested a hidden window and no console; that launch detail is part of this attempt, not a new validation condition silently substituted for a historical run.

Actual command template:

```text
<CORRECTED_BASELINE_EXE> --settings=<OUTPUT_DIR>/A-600/settings.bml --exp001-frame-hash=<OUTPUT_DIR>/A-600/frames.csv --exp001-frame-count=600 <OUTPUT_DIR>/A-600/game.sfc
```

**Observed:** the process did not complete within 180 seconds and was terminated by the runner. It produced a 109-byte CSV containing only its version/request/index/header lines: **zero native callback rows, no completion trailer**. CSV SHA-256: `236f8dc5c020027ff82efefe208dc473608cd08981658797cbf4c589a60ffb63`. stdout and stderr were empty. This is an incomplete file, not a 600-frame digest or a differing native-frame sequence. There was no normal emulator exit code.

The disposable SRAM remained byte-identical to the seed. The disposable settings file had `General/Crashed: true` afterward (SHA-256 `2a8cc470d5f3569ea09cb8124da95c16c22bc73eb20ba959bc2cd3db1acd93d4`); it also reflected the frontend's recent-list normalization. The retained seed itself was untouched.

**Source observation:** at harness commit `13e19564bd038e3767a58b9f1f1d29b1d5f4f527`, `bsnes/target-bsnes/bsnes.cpp` calls the frame hasher's `start()` before frontend initialization. `Program::create()` in `program/program.cpp` saves the crash sentinel as true before video/audio/input driver setup, clears/saves it after that setup, and only then calls `load()`. Video/audio initialization can show modal error dialogs. **Inference:** the artifacts are consistent with incomplete frontend/driver initialization before ROM execution. The exact driver, wait or dialog cause is **UNKNOWN**; no live stack or dialog text was captured. The timeout does not establish a Candidate A PPU defect or a native framebuffer divergence.

No retry, settings workaround, reference replacement or observer/runtime continuation occurred after this stop. No bsnes process remained afterward.

As a read-only tooling check, the new semantic parser was subsequently run against the retained historical BG, OBJ and composition CSVs/summaries. It accepted the established 23,760 / 29,772 / 61,440 records and required lineage/counts. This validates the parser against existing evidence; it is not a runtime transfer result for any new binary.

| Required runtime evidence | This attempt |
| --- | --- |
| Corrected harness 600 callbacks vs historical reference | Incomplete: zero rows; equality UNKNOWN |
| Corrected harness 1,800 callbacks | Not launched |
| EXP-001 disabled/enabled, callback 500, 23,760 BG records | Not launched; not reproduced |
| EXP-002 disabled/enabled, 29,772 records, 687 known winners, 12 overlaps | Not launched; not reproduced |
| EXP-003 disabled/enabled, 61,440 records and established main/sub counts | Not launched; not reproduced |
| Short V=240 / overscan transition / mixed live-latched / interlace fixture against all four builds | Generated and oracle prepared; no targeted ROM run launched |

Preserved historical frame digests remain `92B098CF30A4171F707185B2A32918B8F361EDF30AC8BA6AA3F1FEAD39BAE96F` (600) and `9BC5FF87FC19E52615CFFB334AD9AD75900F4C8F12818972C210479A857B99FB` (1,800). No native first-divergence index exists: callback 0 was never captured.

## Result, limits and next action

The corrected integrations are **implemented / supported-build passed / focused-host checks passed / runtime transfer incomplete**. Their historical BG/OBJ/composition conclusions and public commit mappings remain attributed to the original binaries. In particular, the historical 12 OBJ overlap winners and EXP-003's 155 competitions / 47,391 main-sub source disagreements were not newly observed here. Window suppression remains implemented/host-tested but unexercised by the selected historical real-ROM callback; this task adds no real-ROM coverage.

Candidate A remains the accepted experimental baseline on the prior documented evidence and Xavier's decision. EXP-004's P0 recommendation has a documented baseline disposition, but **the transfer gate is not satisfied**. EXP-004 color-math provenance remains unimplemented and unauthorized.

The next narrowly scoped action is to diagnose the corrected control's frontend startup with the exact binary and preserved seeds, document any justified launcher/environment change, then resume fresh finite comparisons after review of this stop. Do not change the expected frame/provenance data or attribute this timeout to native execution without evidence.

Even a later complete pass would remain limited to tested inputs, windows and host scenarios. Complete execution-state equivalence, universal compatibility, Mode 7 provenance, persistent game-entity identity, final-color/framebuffer visibility, full-system save/load and performance remain outside these transferred claims. Final core, production/renderer architecture, graphics API, implementation language, profile format, proof-of-concept game and final hardware baseline remain unresolved.

No commits, pushes, merges, historical/public rewrites, ADR or EXP-004 implementation occurred. New source changes exist only in the three registered corrected observer worktrees; the new harness control has no source changes. Raw inputs, captures, generated fixture ROM, build logs and host outputs remain private/untracked.

## Review surface and commit disposition

Main GTC-HD-Lab files changed or added:

- `AGENTS.md` — new isolated checkout registrations and stopped-transfer disposition.
- `docs/PROJECT_STATE.md` — accepted experimental baseline, incomplete transfer and blocked EXP-004 gate.
- `docs/research/BSNES_NATIVE_OUTPUT_BOUNDS_RUNTIME_VALIDATION.md` — dated decision/outcome addendum only.
- `docs/research/BSNES_ACCEPTED_BASELINE_REVALIDATION.md` — this consolidated evidence report.
- `docs/experiments/EXP-001/RESULTS.md`, `docs/experiments/EXP-002/RESULTS.md`, `docs/experiments/EXP-003/RESULTS.md` — current-scope notes and dated incomplete-transfer addenda.
- `docs/experiments/EXP-004/SPEC.md`, `docs/experiments/EXP-004/SOURCE_AUDIT_AND_IMPLEMENTATION_PLAN.md` — current blocked gate and explicit historical scope.
- `tests/accepted-baseline-revalidation/README.md`, `run_host.py`, `run_runtime.py` — commands and finite regression tooling.

The corrected harness-only worktree has **no source changes**. Below are the exact staged integration paths in each new observer worktree, relative to that external bsnes checkout. Existing tests are imported unchanged from their historical observer revisions; the accepted native correction is already in the common parent.

### EXP-001 integration paths

```text
bsnes/sfc/ppu/background.cpp
bsnes/sfc/ppu/exp001-observer.cpp
bsnes/sfc/ppu/exp001-observer.hpp
bsnes/sfc/ppu/ppu.cpp
bsnes/target-bsnes/bsnes.cpp
bsnes/target-bsnes/program/exp001-observer-window.hpp
bsnes/target-bsnes/program/program.cpp
bsnes/target-bsnes/program/program.hpp
tests/exp001-runtime/observer-window-cli-test.py
tests/exp001-runtime/observer-window-test.cpp
tests/exp001/.gitignore
tests/exp001/observer-test.cpp
```

### EXP-002 integration paths

```text
bsnes/sfc/ppu/exp002-obj-observer.cpp
bsnes/sfc/ppu/exp002-obj-observer.hpp
bsnes/sfc/ppu/main.cpp
bsnes/sfc/ppu/object.cpp
bsnes/sfc/ppu/ppu.cpp
bsnes/sfc/ppu/serialization.cpp
bsnes/target-bsnes/bsnes.cpp
bsnes/target-bsnes/program/exp002-obj-window.hpp
bsnes/target-bsnes/program/program.cpp
bsnes/target-bsnes/program/program.hpp
tests/exp002/.gitignore
tests/exp002/obj-pipeline-test.cpp
tests/exp002/observer-window-cli-test.py
tests/exp002/observer-window-test.cpp
tests/exp002/run-tests.py
```

### EXP-003 integration paths

```text
bsnes/sfc/ppu/background.cpp
bsnes/sfc/ppu/exp003-composition.cpp
bsnes/sfc/ppu/exp003-composition.hpp
bsnes/sfc/ppu/exp003-hooks.cpp
bsnes/sfc/ppu/main.cpp
bsnes/sfc/ppu/object.cpp
bsnes/sfc/ppu/ppu.cpp
bsnes/sfc/ppu/ppu.hpp
bsnes/sfc/ppu/screen.cpp
bsnes/sfc/ppu/serialization.cpp
bsnes/target-bsnes/bsnes.cpp
bsnes/target-bsnes/program/exp003-composition-window.hpp
bsnes/target-bsnes/program/program.cpp
bsnes/target-bsnes/program/program.hpp
tests/exp003/.gitignore
tests/exp003/composition-test.cpp
tests/exp003/observer-window-cli-test.py
tests/exp003/observer-window-test.cpp
tests/exp003/run-tests.py
```

**Commits created: none.** All four branch HEADs remain `13e19564bd038e3767a58b9f1f1d29b1d5f4f527`; only the three staged observer trees differ. No main-repository commit or push was made. The 12 pre-existing bsnes checkouts retained their branch/HEAD and clean working status, and all four freshly built executable hashes were rechecked after the stopped run. Historical/public links and hashes were preserved; `git diff --check` passed for the documentation and staged source diffs.

## Startup diagnosis addendum — 2026-10-05

**Current diagnostic disposition: STARTUP BLOCKER IDENTIFIED / FRESH CORRECTED CONTROL VERIFIED FOR THE TESTED WINDOWS / OBSERVER TRANSFERS NOT RESUMED.** The preceding stopped-run evidence is retained unchanged. This addendum supersedes its startup uncertainty, not its incomplete EXP-001/002/003 transfer status. EXP-004 remains blocked and unauthorized.

### Source and executable identity

The fresh control is `experiments/bsnes-candidate-a-revalidation-baseline/`, branch `gtc-hd/candidate-a-revalidation-baseline`. The historical control is `experiments/bsnes-native-output-bounds-a-runtime/`, branch `gtc-hd/native-output-bounds-candidate-a-runtime`. Both are clean at `13e19564bd038e3767a58b9f1f1d29b1d5f4f527`, whose parent is accepted correction `46fa75236fa61d49d8e9424b3b44694b88aa07a9`, whose parent is audited upstream `7d5aa1e656b9171524d01b1b22917197d8121cb4`.

Direct comparison found **all 2,192 tracked files byte-identical**, including harness, native PPU, frontend/platform and build files; no line-ending-only differences, staged changes, untracked files or ignored compilation-source files were found in either control. Ignored objects and executables were inspected separately.

| Executable | Bytes | SHA-256 |
| --- | ---: | --- |
| Historical Candidate A runtime | 7,082,253 | `C31FD438E13DE097F9FF5864D7191EF23956C17010FC4A93D3F234F2DBCC4963` |
| Fresh corrected control | 7,082,253 | `3F1C09FC603EFD8AC29E4FBD480ACA362C981819EA50991FB9B2D9F12B70B48F` |

The only binary differences are bytes within the PE timestamp and checksum fields. Normalizing those fields in memory yields identical complete files, SHA-256 `b3f2b78d6aab63a01772125169de78cf73db2326ca2f4cfb1fcb20f11bf646e9`; neither executable was edited. Both embed `GCC: (Rev3, Built by MSYS2 project) 16.2.0` and have identical Windows/UCRT DLL imports, including Direct3D 9 and WinMM, without separate MinGW libgcc/libstdc++ runtime imports. The fresh build command/configuration is recorded above. The historical binary's exact build command/environment was not recovered; it is not inferred from the compiler string.

### Differential launches and first failing stage

Each SMW case restored the exact ROM, SRAM and settings seed hashes listed above into a new disposable directory. Manual cases used Xavier's supplied PowerShell call-operator invocation and argument order, repository-root cwd, and separate ROM/config/output directories, with the callback count reduced to 16. Runner cases reproduced the finite driver's preparation, absolute argument list, run-directory cwd, UCRT64 PATH prefix, redirected stdout/stderr, `STARTF_USESHOWWINDOW`/`SW_HIDE` and `CREATE_NO_WINDOW`.

| Case | Binary | Invocation and execution context | Native process result | Callback rows / CSV lines |
| --- | --- | --- | --- | ---: |
| 1 | Historical | Supplied PowerShell form, normal desktop context | Exit 0; historical prefix equal | 16 / 23 |
| 2 | Historical | New runner procedure, restricted execution context | 25-second deadline; terminated, no normal exit | 0 / 4 |
| 3 | Fresh | Supplied PowerShell form, normal desktop context | Exit 0; historical prefix equal | 16 / 23 |
| 4 | Fresh | New runner procedure, restricted execution context | 25-second deadline; terminated, no normal exit | 0 / 4 |

All four created a process and CSV; stdout/stderr were empty. Failed cases created frontend windows and left `General/Crashed: true`, with post-settings SHA-256 `2a8cc470d5f3569ea09cb8124da95c16c22bc73eb20ba959bc2cd3db1acd93d4`, matching the original stopped attempt. Window inspection extended observed elapsed time to about 27.3 seconds. Their incomplete 16-callback CSV hash was `91626f9083b8753983b1c0c5b56a908aad7b028e82cb2933bd313ed51818ad48`. Every ordinary SMW run preserved SRAM bytes; successful settings cleared the crash sentinel and updated recent paths. Seed/post-run diffs showed no changed video/audio/input, pause, run-ahead, rewind or auto-load setting explaining the failure.

Preliminary direct launches and subsequent exact PowerShell launches also stalled when run inside the restricted context; those failures were retained. Thus the manual syntax alone is not the remedy. Windows PowerShell returned before the GUI child finished and the immediately sampled `$LASTEXITCODE` was null. Cases 1 and 3 therefore waited on the actual owned native process handle and recorded its exit code, independently of shell exit status.

An existing GDB 17.2 attachment to the stalled historical binary captured this main-thread call chain:

```text
Program::create()
  Program::updateVideoDriver(hiro::Window)
    hiro::MessageDialog::error(...)
      hiro::MessageDialog::_run()
        hiro::mWindow::setModal(bool)
          hiro::pWindow::setModal(bool)
```

At the shared source revision, `bsnes/target-bsnes/program/video.cpp`, `Program::updateVideoDriver()`, opens this modal when `video.ready()` is false: `Error: failed to initialize [Direct3D 9.0] video driver.` The driver name comes from the unchanged seed; the message follows from this source branch and stack, not a captured dialog-text screenshot. `Program::create()` in `program/program.cpp` has not yet reached audio/input setup, cartridge/manifest/SRAM loading or PPU execution. The fallback to video `None` occurs only after the modal returns. A fresh-binary stack was not captured; its matching failure artifacts and identical executable code support the same diagnosis.

**Established cause/layer:** frontend video initialization fails in the restricted launch context and blocks in a modal error before ROM loading. This explains zero callbacks without implicating the accepted PPU correction. The precise Direct3D failing API/HRESULT and underlying Windows restriction remain unknown.

### Invocation correction and control reconfirmation

The minimal correction is to run the finite GUI validation in the normal desktop execution context, outside the restricted sandbox, while preserving its deterministic inputs and launch procedure. No emulator, harness, observer, settings seed or finite-driver source change was needed. A fresh-control 16-callback comparison retained the runner's hidden/no-console flags and exactly matched the failed case's recorded `PATH`, `MSYSTEM`, `TMPDIR`, `DISPLAY` and `SESSIONNAME`; it exited 0 and matched the historical prefix. This also excludes the initially observed extra shell-directory PATH entry as the explanation. Quoting, argument order, renamed disposable ROM, cwd policy and output redirection remained viable in the successful runner-style launches.

Only the fresh harness control was then reconfirmed; expectations were retained, not regenerated from its output:

| Control run | Result | CSV SHA-256 |
| --- | --- | --- |
| SMW, 16 callbacks | Exit 0; 23 lines; exact historical row prefix | `a504724210c01f0a78cc713c5a8f67706b9ff0df55dd11fb44403a2268475022` |
| SMW, 600 callbacks | Exit 0; 607 lines; complete CSV byte-identical to historical reference | `92B098CF30A4171F707185B2A32918B8F361EDF30AC8BA6AA3F1FEAD39BAE96F` |
| SMW, 1,800 callbacks | Exit 0; 1,807 lines; complete CSV byte-identical to historical/accepted runtime reference | `9BC5FF87FC19E52615CFFB334AD9AD75900F4C8F12818972C210479A857B99FB` |
| Existing targeted bounds fixture, 16 callbacks | Exit 0; unchanged CPU/frame oracle passed | `69416871a6eaf2541a684a352c4a7e13972cb49470ccc8b0f436ca9866fd04de` |

The bounds run reused the existing builder/oracle and its established `None`-driver fixture settings; SMW retained Direct3D 9.0. It passed V=240 OBJ/STAT77, overscan transition, mixed live/latched CGRAM and both interlace-field checks. SRAM SHA-256 remained the expected `75d6febfa8370ea0969e9ab06312552e60479803d090d44e781531e4f7932acc`. These are control-only results, not observer transfer evidence.

**The corrected-control prerequisite is now satisfied for the tested conditions. The finite EXP-001/002/003 transfer is ready to resume after this diagnostic report-back, using the validated desktop execution context; it has not resumed in this task.** EXP-004 still requires completed transfers and explicit reauthorization. No universal execution-state equivalence or new architecture acceptance follows.

This diagnosis appended only this report in the public documentation. Exact local commands, environment records, process results, debugger output and disposable captures are retained privately. Original stopped evidence, staged observer integrations, all source/test files, executable bytes and `docs/PROJECT_STATE.md` were preserved. No emulator rebuild, observer ROM run, EXP-004 implementation, ADR, commit or push occurred.

## Resumed transfer results — 2026-10-05

**Current disposition: EXP-001 / EXP-002 / EXP-003 VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE.** All three disabled/enabled framebuffer comparisons, callback-500 provenance captures, focused host/source checks and short targeted bounds fixtures passed. **EXP-004: NATIVE-BASELINE GATE SATISFIED / READY FOR EXPLICIT IMPLEMENTATION REAUTHORIZATION.** It remains unimplemented and unauthorized pending Xavier's explicit instruction.

This is a later execution record. The initial stopped attempt and diagnostic addendum above remain unchanged; their incomplete statuses describe those earlier stages. Historical experiment commits, public mappings, captures and expectations retain their original attribution.

### Existing integrations and source commits

Preflight found all four revalidation checkouts still at corrected harness descendant `13e19564bd038e3767a58b9f1f1d29b1d5f4f527`. The control was clean. EXP-001/002/003 retained exactly their previously built staged trees, with 12/15/19 staged paths respectively, no unstaged source changes and no untracked source files. Branch, HEAD, status, full index and integration patches were recorded before execution. No branch or observer integration was recreated.

The accepted native correction remains `46fa75236fa61d49d8e9424b3b44694b88aa07a9`, parent of the harness descendant. Source checks proved that each observer's native differences from its historical implementation remain exactly Candidate A's four-file correction: 512x496 backing, 512x480 presentation, pointer-safe destinations, retained late stores, pair-240 transition clearing and native V=240 execution. Observer/frontend semantics and existing tests were not changed.

Only after every required check passed, the existing staged integrations were committed locally:

| Experiment | Worktree | Branch | New source commit |
| --- | --- | --- | --- |
| EXP-001 | `experiments/bsnes-exp-001-corrected/` | `gtc-hd/exp-001-corrected-baseline` | `ab04d023b728f08f7cbfaa38e75dcf8031a04158` |
| EXP-002 | `experiments/bsnes-exp-002-corrected/` | `gtc-hd/exp-002-corrected-baseline` | `94238480bd11a0ca3b873da1d70c208ca2f9326c` |
| EXP-003 | `experiments/bsnes-exp-003-corrected/` | `gtc-hd/exp-003-corrected-baseline` | `c929e19a8583e388b0f8bf53d2d0a796c0d91386` |

| Experiment | Unchanged built/staged tree, now commit tree | Executable SHA-256 |
| --- | --- | --- |
| EXP-001 | `61d75f7afbaaf45d6b023ef057e2ca3a0d5fd276` | `D69B064DD54D233F013BA283390A832DD9ECAF6729C9447AF0043627B84C6299` |
| EXP-002 | `d7394a2f38942ee3e5990dced3111c8300baa9d8` | `F78FD4EFB4699483DEE4AD86F89EC2554AB38460E5F19F96DB0EC7B97B488735` |
| EXP-003 | `07f80649ff9681fb0e566a12d549082e1203330b` | `9F59FD335261A7D7CF15FF43E22EA8C4EB56258E1EBCAB9CE7FA1B65B51B359F` |

Each new commit has the harness descendant as its direct parent and exactly the previously tested tree. Author and committer are both Xavier Laverde <xavier0286@gmail.com>. Executables were reused without rebuilding and rehashed after validation. All three corrected observer checkouts are now clean. No main-repository commit, push or merge was made.

### Execution and retained control

**Every emulator launch used the normal desktop execution context.** The restricted-context Direct3D 9 modal limitation from the diagnosis was not used to judge runtime correctness. The exact failing Direct3D API/HRESULT remains unknown. Deterministic Direct3D 9.0 / waveOut / input-None SMW settings were preserved; no source or settings workaround was introduced.

The fresh corrected control's already completed 16/600/1,800/bounds evidence was verified and reused; no new control campaign ran. Its executable remains `3F1C09FC603EFD8AC29E4FBD480ACA362C981819EA50991FB9B2D9F12B70B48F`. The finite runner gained only an optional pair of retained-control CSV arguments, documented in the [tooling instructions](../../tests/accepted-baseline-revalidation/README.md). It records those inputs, checks their full bytes against fixed historical references, and compares each observer against both. Expectations and historical artifacts were not regenerated.

Each observer launch copied the same ROM/SRAM/settings seed hashes recorded above into a new private run directory. The existing runner used an argument list, that directory as cwd, the UCRT64 DLL PATH prefix, hidden-window/no-console flags, and captured stdout/stderr. Ordinary runs had a 180-second bound; fixture runs had 45 seconds. All nine exited normally with code 0 and empty stdout/stderr. Each enabled run used start callback 500, callback count 1; each bounds run left the observer disabled.

### Framebuffer and provenance transfer

| Experiment | Disabled / enabled actual callbacks | Comparison with corrected control and historical sequence | Enabled capture |
| --- | ---: | --- | --- |
| EXP-001 | 600 / 600 | Both complete CSVs byte-identical | 23,760 BG records; capacity 32,768 |
| EXP-002 | 600 / 600 | Both complete CSVs byte-identical | 29,772 records; capacity 131,072 |
| EXP-003 | 1,800 / 1,800 | Both complete CSVs byte-identical | 61,440 records; capacity 65,536 |

The 600-callback digest remains `92B098CF30A4171F707185B2A32918B8F361EDF30AC8BA6AA3F1FEAD39BAE96F`; the 1,800-callback digest remains `9BC5FF87FC19E52615CFFB334AD9AD75900F4C8F12818972C210479A857B99FB`. Full CSV equality includes ordered hashes, callback indices, dimensions/pitch/scale and successful completion trailers. **First divergence: none.**

All enabled captures observed exactly one callback, completed/exported successfully, disabled the observer after export, and reported zero drops and no overflow. Provenance CSVs were also byte-identical to their respective historical captures. Summary metadata was checked field-by-field and its new digest recorded separately:

| Experiment | Provenance CSV SHA-256, equal to historical capture | New summary SHA-256 |
| --- | --- | --- |
| EXP-001 | `BCC8E15D28C2A7918E65ED03BA467F33A767EA7EDB3837B8BBF60C4E95B03964` | `AEFA348E6DBEBF3704A8307B58EEA7FCDC125D2E91BA1F473D04E907ABFF1D1A` |
| EXP-002 | `7974E49DEE1EF8110453938B54201042BA79AFB3A1BFA57260EC220C93FC49C8` | `7F043C2BECACB9492BED24775BDB7E735CE41F63A6ADB284C4E42128841BBC0A` |
| EXP-003 | `C8084C47F39A9EF17B22F40F804ED30A02628F940C9CAA299495F29A52381EE8` | `EF67AFB4B798F16E4A1ED27046A70BB9A4DA2A0EFB3FB26F71FFB00997654366` |

**EXP-001:** BG IDs 0–2 in mode 1, native map/tile/source/palette/priority/timing fields and ordered records were retained. Frame IDs 500/501 retain the established callback-window meaning, including naturally scheduled fetches; they do not identify final visible pixels.

**EXP-002:** 28,909 evaluation records, 176 fetch records and 687 winner records; unknown winners 0. All 687 winners retained ordered Evaluation → Fetch → Winner links, matching OAM indices and valid decoded source color/palette. The same 12 real overlap witnesses satisfied `nontransparent_samples > 1` and `previous_fetch_id != 0`: `22993, 22994, 23175, 23177, 23178, 23180, 23347, 23349, 23350, 23352, 23507, 23509`. OAM identity remains hardware provenance, not persistent game-entity identity or final framebuffer visibility.

**EXP-003:** main counts were BG1 11,969; BG3 22,015; OBJ 687; backdrop 22,673; skipped 4,096. Sub counts were BG2 39,087; backdrop 18,257; skipped 4,096. Other source counts were zero. Unknown provenance was 0; all applicable winner tokens were known/nonzero and candidate outcomes matched native winner decisions. BG/OBJ competitions were 155 and main/sub source disagreements 47,391. Candidate window suppressions were 0: the selected real-ROM callback still does not exercise suppression, although the focused host fixtures do. Final color remains outside EXP-003.

### Accepted-correction regression and deviations

All original focused observer, window, frame-hasher and desktop CLI checks passed again, including 26 CLI rejection cases per integration and the existing 14 OBJ / 15 composition CSV schemas. The additional actual-native-declaration fixture passed all eight control/integration `-O0`/`-O3` configurations. Each retained 253,952 entries and passed 4,596 geometry, 1,536 screen, 84 pipeline, 16 clear, 756 no-store-line and 28,672 mixed-CGRAM cases, eight counter fields, three native-field restore cases and 18 late-effect witnesses. Presentation/native-field-state/screen streams matched each other and the previously recorded stream digests above. This is bounded host coverage, not full-system save/load or runtime-sanitizer evidence.

The unchanged short bounds ROM builder/oracle passed against all three integrations with observers disabled: V=240 OBJ/STAT77, overscan on → off, mixed live/latched overscan and interlace smoke. All produced 16 callbacks, normal exit and the corrected-control frame CSV digest `69416871a6eaf2541a684a352c4a7e13972cb49470ccc8b0f436ca9866fd04de`; SRAM/result digest was `75d6febfa8370ea0969e9ab06312552e60479803d090d44e781531e4f7932acc`. CPU checks retained the expected STAT77 mask, V=233/H=207 mixed read, CGRAM result and alternating fields. The fixture retained its established None-driver settings, distinct from the SMW seed.

One tooling deviation occurred before source assertions: desktop-account Git refused ownership of sandbox-created checkouts. The refusal logs were retained, then the exact four inspected checkout paths were trusted through process-scoped `safe.directory` entries. No global configuration, source assertion, test expectation or emulator setting changed. EXP-001's already passed checks were retained; the affected checks then passed. There was no emulator/provenance divergence, integration repair or semantic serialization difference.

### Current gate and limits

All three transfer prerequisites are satisfied for the specified deterministic windows and bounded host/runtime scenarios. Current experiment results and project state now record **VERIFIED FOR TESTED CONDITIONS ON ACCEPTED CORRECTED BASELINE**. EXP-004's current specification/audit status is **NATIVE-BASELINE GATE SATISFIED / READY FOR EXPLICIT IMPLEMENTATION REAUTHORIZATION**. Historical P0 evidence and the frozen historical design revision remain intact.

No EXP-004 implementation, acceptance of a final core/renderer architecture, universal compatibility claim, new persistent object identity or complete execution-state equivalence follows. Broad game/mode/raster coverage, Mode 7 provenance, final-color semantics and full-system save/load remain outside these results. Xavier's explicit EXP-004 implementation reauthorization is the next step.

Updated review surface: this report, EXP-001/002/003 `RESULTS.md` current notes and appended results, `docs/PROJECT_STATE.md`, EXP-004 specification/audit current gates, the current AGENTS revalidation disposition, and the finite runner/tooling instructions. Original historical/public identities and dated evidence were preserved. Local raw evidence remains private. No ADR, source redesign, push or merge occurred.
