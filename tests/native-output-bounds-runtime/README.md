# Native output-bounds Phase 4 runtime fixture

One experiment-specific ROM tests the existing Control/A/B runtime binaries.
It does not modify bsnes, install an SDK, or implement EXP-004. The results and
baseline recommendation are in the [Phase 4 report](../../docs/research/BSNES_NATIVE_OUTPUT_BOUNDS_RUNTIME_VALIDATION.md).

## Files and invocation

- `build_fixture.py`: Python-standard-library opcode emitter with checked
  labels, branches, LoROM header and checksum; emits one 32 KiB ROM, a resolved
  instruction listing and a fingerprint manifest.
- `run_validation.py`: fingerprint preflight, independent expected framebuffer
  patterns, fresh per-binary inputs, bounded process execution, SRAM checks and
  exact Control/A/B comparison. No automatic retry or reference replacement.
- `settings.bml`: portable deterministic settings seed. Video/audio/input
  drivers are `None`; the existing hash harness captures native callbacks
  before the video driver. No controller input is supplied.

Run from the research repository root using Python 3.12.9 and the existing
Windows UCRT64 runtime dependencies. Use a new ignored/local output directory:

```powershell
python -B tests/native-output-bounds-runtime/run_validation.py --control experiments/bsnes-native-output-bounds-control-runtime/bsnes/out/bsnes.exe --candidate-a experiments/bsnes-native-output-bounds-a-runtime/bsnes/out/bsnes.exe --candidate-b experiments/bsnes-native-output-bounds-b-runtime/bsnes/out/bsnes.exe --dll-dir "<UCRT64_BIN>" --output "<OUTPUT_DIR>/phase4-01"
```

`--dll-dir` can be omitted if the existing runtime dependencies are on PATH.
The executable hashes are deliberately pinned to the reported builds. Changing
the identities requires a separately reviewed validation setup.

To generate the ROM without launching an emulator:

```powershell
python -B tests/native-output-bounds-runtime/build_fixture.py --output "<OUTPUT_DIR>/static-fixture"
```

The runner records expected frame hashes **before** starting Control. It then
runs Control, A and B sequentially, each for 16 callbacks, and stops immediately
on an unexpected Control result or a candidate difference. Process timeout is
45 seconds; only that process is terminated on timeout. Each run gets a ROM
copy, identical settings and 2,048 zero SRAM bytes. bsnes saves SRAM on normal
unload. The runner reads that file as the CPU-result channel, separately from
the unmodified framebuffer harness. `summary.json` retains commands, exit codes,
hashes, CPU checks and any first discrepancy. Generated files stay local.

## ROM sequence and predeclared expectations

The fixture disables interrupts and DMA, initializes OAM and palette entries
under forced blank, then polls the latched nine-bit V counter. All 128 small
sprites have X=0 and Y=240; none wraps into earlier lines. All BG/OBJ screen
enables and color math are disabled, so the visible patterns are backdrops.

1. Enable overscan and brightness 15 at V=250. On the next frame, read STAT77
   at V=239 and V=241: overflow bits must change from `$00` to `$40`, proving
   rangeOver with timeOver clear after V=240 processing.
2. At V=250, change the backdrop to blue and turn overscan off. The actual
   V=0 transition clear must leave blue in memory rows 16..463 and black borders.
3. Start a green frame with placement latched off. At V=233, set live overscan
   on, request CGRAM address 1 (`$1234`), and read CGRAM while active. The native
   palette latch supplies address 0 (`$03e0`) instead. Continue through V=239
   and read STAT77 at V=241. Changing live vdisp from 225 to 240 after V=233
   produces an additional native callback in that frame; both images stay green
   in rows 16..463 with black borders.
4. At V=250, enable overscan and screen interlace with a yellow backdrop. Save
   the next two fields' STAT78 bit 7 values; their XOR must be `$80`. The first
   field changes its row parity, retaining the opposite rows; the second fills
   the remaining rows. Pair zero remains black. Idle after marking completion.

Native brightness-15 callback encoding swaps SNES BGR555's red/blue groups.
Expected frame words are generated directly from colors and row placement,
without taking a captured Control frame as the expected image:

| Callback index | Expected 512x480 image |
| --- | --- |
| 0 | Black initialization |
| 1 | Red in rows 2..479 |
| 2 | Blue in rows 16..463, black borders |
| 3, 4 | Green in rows 16..463, black borders |
| 5 | Yellow in the first interlaced field's rows; opposite rows retained |
| 6..15 | Yellow in rows 2..479 |

The two allowed first-field images are computed before execution; SRAM's field
bit selects the corresponding expectation. The subsequent field must be its
opposite. This is a smoke check, not exhaustive interlace validation.

## SRAM result format

All offsets are decimal from `$70:0000`; values occupy one byte unless stated.

| Offset | Meaning |
| --- | --- |
| 0..3 | ASCII `GTC4` |
| 4 | Format version 1 |
| 5 | `$a5` only after all four stages complete |
| 6 | Zero on success; `$e1`..`$e6` identifies the first ROM assertion failure |
| 7 | Reserved, zero |
| 8 | Raw STAT77 before V=240 |
| 9, 10 | Raw STAT77 after V=240; its masked overflow bits |
| 11, 12 | OBJ stage and overscan-transition stage completion flags |
| 13, 14 | Observed mixed-state V low and latched pre-read H-dot low |
| 15, 16 | Mixed-state CGRAM low and raw high byte (mask high with `$7f`) |
| 17, 18 | Mixed-state STAT77 and completion flag |
| 19, 20, 21 | First field bit, second field bit, interlace completion flag |
| 22..2047 | Untouched zero seed |

The completion markers establish execution progress; the framebuffer oracle and
register checks establish the associated results. They do not imply complete
execution-state equality, hardware conformance or sanitizer coverage. The mixed
case observes one palette-latch value at V=233, not every late-line side effect.
