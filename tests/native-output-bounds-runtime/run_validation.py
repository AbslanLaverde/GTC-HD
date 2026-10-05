"""Run this fixture Control -> A -> B; stop on the first failed expectation.

No emulator source changes, rebuilding, reference replacement or automatic retry.
The output directory must be new. Generated artifacts are private/local evidence.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

from build_fixture import build, COLORS, SRAM_SIZE

COUNT = 16
EXE_HASHES = {
    "CONTROL": "9cd67324bd89f80ae67db8d49d792f970e07e443dd75fe56b4ffdc8c21aeaa0c",
    "A": "c31fd438e13de097f9ff5864d7191ef23956c17010fc4a93d3f234f2dbcc4963",
    "B": "889f0f92a7bfccddc7f71c95edfbeea3a17dd454f6424dd47708342d8e4beb28",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def native_color(color):
    # Brightness 15 maps SNES BGR555 to the callback's RGB555 words.
    return ((color & 31) << 10) | (color & 0x3E0) | ((color >> 10) & 31)


def frame(color, first=2, last=480, previous=None, parity=None):
    rows = list(previous) if previous is not None else [bytes(1024) for _ in range(480)]
    for y in range(first, last):
        if parity is None or y % 2 == parity:
            rows[y] = struct.pack("<H", native_color(color)) * 512
    return rows


def oracle():
    black = frame(0)
    red = frame(COLORS["obj"])
    blue = frame(COLORS["transition"], 16, 464)
    green = frame(COLORS["mixed"], 16, 464)
    yellow = frame(COLORS["interlace"])
    hash_frame = lambda rows: digest(b"".join(rows))
    # Field parity is independently checked in the CPU result; the first
    # interlaced field may be either parity. All other expected rows are fixed.
    return {
        "fixed": [hash_frame(x) for x in (black, red, blue, green, green)]
                 + [None] + [hash_frame(yellow)] * (COUNT - 6),
        "first_interlace_by_field": [hash_frame(frame(COLORS["interlace"],
                                                     previous=green, parity=p)) for p in (0, 1)],
    }


def inspect_result(run, expected):
    problems = []
    if run["exit_code"] != 0:
        problems.append(f"process exit {run['exit_code']}")
    path = Path(run["directory"])
    sram_path = path / "bounds-phase4.srm"
    sram = sram_path.read_bytes()
    run["sram_sha256"] = digest(sram)
    run["sram_first_32_hex"] = sram[:32].hex(" ")
    if len(sram) != SRAM_SIZE:
        problems.append(f"SRAM size {len(sram)}, expected {SRAM_SIZE}")
    if sram[:8] != b"GTC4\x01\xa5\0\0":
        problems.append(f"ROM incomplete/assertion failed: SRAM header {sram[:8].hex()}")
    checks = {
        "STAT77_before_mask": (sram[8] & 0xC0, 0),
        "STAT77_after_mask": (sram[9] & 0xC0, 0x40),
        "STAT77_saved_mask": (sram[10], 0x40),
        "OBJ_complete": (sram[11], 1), "transition_complete": (sram[12], 1),
        "mixed_observed_V": (sram[13], 233),
        "mixed_CGRAM_low": (sram[15], 0xE0),
        "mixed_CGRAM_high_mask": (sram[16] & 0x7F, 3),
        "mixed_STAT77_mask": (sram[17] & 0xC0, 0x40),
        "mixed_complete": (sram[18], 1),
        "field_xor": (sram[19] ^ sram[20], 0x80),
        "interlace_complete": (sram[21], 1),
    }
    for name, (actual, wanted) in checks.items():
        if actual != wanted:
            problems.append(f"{name}: observed {actual:#04x}, expected {wanted:#04x}")
    if not 22 <= sram[14] <= 230:
        problems.append(f"mixed CGRAM pre-read H-dot outside planned active window: {sram[14]}")
    if sram[19] not in (0, 128) or sram[20] not in (0, 128):
        problems.append("invalid field values")
    if any(sram[22:]):
        problems.append("unexpected nonzero SRAM outside result record")
    run["cpu_checks"] = {k: {"observed": a, "expected": w} for k, (a, w) in checks.items()}
    run["mixed_pre_read_hdot_low"] = sram[14]

    csv_path = path / "frames.csv"
    if not csv_path.exists():
        problems.append("missing framebuffer CSV")
        return problems
    data = csv_path.read_bytes()
    run["csv_sha256"] = digest(data)
    lines = data.decode("ascii").splitlines()
    trailer = [f"# actual_callbacks={COUNT}", "# completed=true", "# reason=count_reached"]
    if lines[-3:] != trailer:
        problems.append("incomplete framebuffer CSV trailer")
    rows = list(csv.DictReader(line for line in lines if not line.startswith("#")))
    run["frames"] = rows
    if len(rows) != COUNT:
        problems.append(f"callback count {len(rows)}, expected {COUNT}")
    for i, row in enumerate(rows[:COUNT]):
        wanted = expected["fixed"][i]
        if i == 5:
            wanted = expected["first_interlace_by_field"][int(sram[19] == 128)]
        if [row[x] for x in ("index", "width", "height", "pitch", "scale")] != [str(i), "512", "480", "1024", "1"]:
            problems.append(f"callback {i}: unexpected metadata {row}")
            break
        if row["sha256"] != wanted:
            problems.append(f"first framebuffer mismatch at callback {i}: observed {row['sha256']}, expected {wanted}")
            break
    return problems


def main(args):
    output = args.output.resolve()
    # Preflight all executable fingerprints before launching any process.
    executables = {"CONTROL": args.control.resolve(), "A": args.candidate_a.resolve(), "B": args.candidate_b.resolve()}
    for name, exe in executables.items():
        if digest(exe.read_bytes()) != EXE_HASHES[name]:
            raise ValueError(f"Unexpected executable identity: {name}")
    output.mkdir(parents=True, exist_ok=False)
    manifest = build(output / "fixture")
    expected = oracle()
    save_json(output / "expected-before-run.json", expected)
    settings = Path(__file__).with_name("settings.bml").read_bytes()
    (output / "settings-seed.bml").write_bytes(settings)
    summary = {"status": "NOT_STARTED", "fixture": manifest,
               "settings_seed_sha256": digest(settings), "callback_count": COUNT, "runs": []}
    env = os.environ.copy()
    if args.dll_dir:
        env["PATH"] = str(args.dll_dir.resolve()) + os.pathsep + env.get("PATH", "")
    for name, exe in executables.items():
        folder = output / name
        folder.mkdir()
        rom = folder / "bounds-phase4.sfc"
        shutil.copyfile(output / "fixture" / rom.name, rom)
        (folder / "bounds-phase4.srm").write_bytes(bytes(SRAM_SIZE))
        config = folder / "settings.bml"
        config.write_bytes(settings)
        command = [str(exe), f"--settings={config}", f"--exp001-frame-hash={folder / 'frames.csv'}",
                   f"--exp001-frame-count={COUNT}", str(rom)]
        run = {"name": name, "directory": str(folder), "executable_sha256": EXE_HASHES[name],
               "command": command, "exit_code": None}
        summary["runs"].append(run)
        save_json(output / "summary.json", summary)
        startup = None
        flags = 0
        if os.name == "nt":
            startup = subprocess.STARTUPINFO()
            startup.dwFlags = subprocess.STARTF_USESHOWWINDOW
            startup.wShowWindow = 0
            flags = subprocess.CREATE_NO_WINDOW
        try:
            with (folder / "stdout.log").open("wb") as out, (folder / "stderr.log").open("wb") as err:
                completed = subprocess.run(command, cwd=folder, env=env, stdout=out, stderr=err,
                                           startupinfo=startup, creationflags=flags, timeout=45)
            run["exit_code"] = completed.returncode
            problems = inspect_result(run, expected)
            if name != "CONTROL":
                # Compare exact bytes, retaining the first offset if they differ.
                for filename in ("frames.csv", "bounds-phase4.srm"):
                    ref = (output / "CONTROL" / filename).read_bytes()
                    actual = (folder / filename).read_bytes()
                    if actual != ref:
                        offset = next((i for i, (a, b) in enumerate(zip(ref, actual)) if a != b), min(len(ref), len(actual)))
                        problems.append(f"{filename}: first Control difference at byte {offset}")
        except (OSError, subprocess.TimeoutExpired, ValueError, IndexError, KeyError) as error:
            problems = [f"fixture execution/capture incomplete: {error}"]
        run["problems"] = problems
        print(json.dumps({"name": name, "exit": run["exit_code"], "problems": problems,
                          "csv_sha256": run.get("csv_sha256"), "sram": run.get("sram_first_32_hex")}), flush=True)
        if problems:
            summary["status"] = "STOP_CONTROL_FIXTURE_INVALID_OR_INCOMPLETE" if name == "CONTROL" else "STOP_CANDIDATE_DIVERGENCE"
            save_json(output / "summary.json", summary)
            return 1
        summary["status"] = f"{name}_PASSED"
        save_json(output / "summary.json", summary)
    summary["status"] = "ALL_TARGETED_SCENARIOS_PASSED"
    save_json(output / "summary.json", summary)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate-a", type=Path, required=True)
    parser.add_argument("--candidate-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dll-dir", type=Path)
    raise SystemExit(main(parser.parse_args()))
