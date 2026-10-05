# Accepted Candidate A revalidation tooling

These finite checks accompany the [2026-10-05 transfer report](../../docs/research/BSNES_ACCEPTED_BASELINE_REVALIDATION.md), including the initial startup stop, its diagnosis and resumed transfer evidence. The commands do not authorize automatic continuation after a failure.

The four expected isolated worktrees and source identities are registered in `AGENTS.md`. Original worktrees, historical references, seeds and test expectations must remain unchanged. Use fresh output directories, the supported UCRT64 environment and authorized local ROM input. Substitute placeholders; do not publish private paths or artifacts.

## Build and original focused checks

Build from each new checkout with UCRT64 compiler/MSYS utilities on PATH and `TMPDIR` pointing to a writable generated-output directory:

```sh
make -j4 -C bsnes local=false
```

From `experiments/bsnes-exp-001-corrected/`, with `<OUTPUT_DIR>` already created:

```sh
g++ -std=gnu++17 -O0 -g -Wall -Wextra -Werror -isystem . tests/exp001/observer-test.cpp bsnes/sfc/ppu/exp001-observer.cpp -o "<OUTPUT_DIR>/storage.exe"
"<OUTPUT_DIR>/storage.exe" "<OUTPUT_DIR>/storage.csv"
g++ -std=gnu++17 -O0 -g -Wall -Wextra -Werror -isystem . tests/exp001-runtime/observer-window-test.cpp bsnes/sfc/ppu/exp001-observer.cpp -o "<OUTPUT_DIR>/window.exe"
"<OUTPUT_DIR>/window.exe" "<OUTPUT_DIR>/window"
g++ -std=gnu++17 -O0 -g -Wall -Wextra -Werror -isystem . tests/exp001-runtime/frame-hash-test.cpp -o "<OUTPUT_DIR>/frame-hash.exe"
"<OUTPUT_DIR>/frame-hash.exe" "<OUTPUT_DIR>/hash"
python -B tests/exp001-runtime/observer-window-cli-test.py bsnes/out/bsnes.exe "<OUTPUT_DIR>/cli"
```

From `experiments/bsnes-exp-002-corrected/` and `experiments/bsnes-exp-003-corrected/`, respectively (choose a new evidence name for each invocation):

```sh
python -B tests/exp002/run-tests.py <FRESH_EVIDENCE_NAME>
python -B tests/exp003/run-tests.py <FRESH_EVIDENCE_NAME>
```

Those are the unchanged historical tests. Their bounded fixture assumptions do not alone establish the expanded native output envelope.

## Additional correction checks

From GTC-HD-Lab:

```sh
python -B tests/accepted-baseline-revalidation/run_host.py --compiler "<UCRT64_GXX>" --output "<OUTPUT_DIR>/bounds-host"
```

This checks the exact native source delta against Candidate A and the unchanged observer/tests, then compiles the existing native bounds fixture against all four actual PPU declarations/methods at `-O0` and `-O3`. Generated host copies add only observer includes/namespace wiring and retain all original assertions. Observers remain disabled through native reset. Presentation/native-field-state/screen streams must match across all eight configurations.

The older Phase-3 driver pins pre-commit candidate branches and permits only four modified native files. It cannot be used unchanged on integrated descendants. This separate driver preserves its native fixture while applying source-identity checks appropriate to these descendants; it does not edit the historical driver or relax native expectations.

## Finite runtime comparison

**Normal desktop execution context is required for every bsnes runtime launch.** In the diagnosed restricted context, Direct3D 9 initialization failed and blocked in a video-driver error dialog before ROM loading. Zero callbacks from that environment are not evidence of a native-emulation defect. The exact Direct3D HRESULT remains unknown. Keep the deterministic settings unchanged; the runner's hidden/no-console flags also worked in the normal desktop context.

```sh
python -B tests/accepted-baseline-revalidation/run_runtime.py \
  --baseline experiments/bsnes-candidate-a-revalidation-baseline/bsnes/out/bsnes.exe \
  --exp001 experiments/bsnes-exp-001-corrected/bsnes/out/bsnes.exe \
  --exp002 experiments/bsnes-exp-002-corrected/bsnes/out/bsnes.exe \
  --exp003 experiments/bsnes-exp-003-corrected/bsnes/out/bsnes.exe \
  --rom "<ROM_PATH>" --sram "<SRAM_SEED>" --settings "<SETTINGS_SEED>" \
  --historical-600 "<HISTORICAL_600_CSV>" \
  --historical-1800 "<HISTORICAL_1800_CSV>" \
  --historical-bg "<HISTORICAL_BG_CSV>" \
  --historical-obj "<HISTORICAL_OBJ_CSV>" \
  --historical-composition "<HISTORICAL_COMPOSITION_CSV>" \
  --dll-dir "<UCRT64_BIN>" --output "<OUTPUT_DIR>/runtime"
```

Inputs and historical files must match the fixed digests recorded in the driver/report. Each run gets a private copy of the exact seed bytes and a fresh CSV destination. Executable hashes are recorded before launch and checked again before each process starts. The observer runs use callback start 500/count 1; frame counts are 600 for EXP-001/002 and 1,800 for EXP-003. The driver checks summary fields, semantic records/lineage, full provenance bytes and full frame CSVs against preserved references and the newly built control. It imports the existing Phase-4 builder, independent oracle and result inspector; the old fixture and executable fingerprints remain unchanged.

Default order: corrected control 600/1,800/bounds, then each observer disabled/enabled/bounds. Stop immediately on failure or timeout; no retry or expected-result regeneration. The initial 2026-10-05 attempt reached only the first launch; the diagnostic and resumed results are recorded separately in the report.

When the corrected control's short/600/1,800/bounds prerequisite is already verified for the same executable and inputs, append both options to the command above:

```sh
  --control-600 "<VERIFIED_CORRECTED_600_CSV>" \
  --control-1800 "<VERIFIED_CORRECTED_1800_CSV>"
```

This resumes directly at the observer disabled/enabled/bounds runs. The driver reads and records the retained corrected-control CSVs, verifies them byte-for-byte against the fixed historical references, and compares each new observer run with both. It does not rerun the control or claim to re-execute its bounds fixture. Verify the retained control's executable identity, completion records and bounds result before selecting this mode; the startup-diagnosis evidence supplied those prerequisites for the resumed task.

On Windows ordinary runs have a 180-second timeout and bounds runs 45 seconds. Launch the runner itself in the normal desktop context so its child processes inherit that context. Changing driver settings to obtain a run would change the required seed and must not be silently treated as the established comparison.

Host/source checks under the desktop account may encounter Git ownership checks when a worktree was created by another local execution account. After confirming the exact registered checkout, use process-scoped `safe.directory` entries for those specific paths if needed. Do not add a wildcard exception or change global Git settings. This does not change emulator behavior or test expectations.
