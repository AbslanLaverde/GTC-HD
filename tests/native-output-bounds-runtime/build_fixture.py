"""One experiment-specific 32 KiB LoROM; Python stdlib, no external assembler.

Only the instructions needed by this fixture are emitted. Labels/relocations
are checked; this is not a general SNES assembler or test framework.
Generated ROM/listing/manifest belong in an ignored/local output directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

TITLE = b"GTC BOUNDS PHASE4 V1 ".ljust(21, b" ")
SRAM_SIZE = 2048
COLORS = {"obj": 0x001F, "transition": 0x7C00, "mixed": 0x03E0, "interlace": 0x03FF}


class Code:
    def __init__(self):
        self.data = bytearray()
        self.labels = {}
        self.fixups = []
        self.listing = []

    def emit(self, note, *values):
        self.listing.append((len(self.data), len(values), note))
        self.data.extend(values)

    def label(self, name):
        assert name not in self.labels
        self.labels[name] = 0x8000 + len(self.data)
        self.listing.append(name + ":")

    def ref(self, opcode, name, relative=False):
        self.emit(("branch " if relative else "call/jump ") + name, opcode, 0, *([] if relative else [0]))
        self.fixups.append((len(self.data) - (1 if relative else 2), name, relative))

    def absolute(self, opcode, address, note):
        self.emit(note, opcode, address & 255, address >> 8)

    def lda(self, value):
        self.emit(f"LDA #${value:02X} (A8)", 0xA9, value)

    def write(self, address, value):
        self.lda(value)
        self.absolute(0x8D, address, f"STA ${address:04X}")

    def read(self, address):
        self.absolute(0xAD, address, f"LDA ${address:04X}")

    def save(self, offset):
        self.emit(f"STA $700000+{offset}", 0x8F, offset, 0, 0x70)

    def mark(self, offset, value=1):
        self.lda(value)
        self.save(offset)

    def wait(self, v):
        self.emit(f"LDX #{v} (X16)", 0xA2, v & 255, v >> 8)
        self.ref(0x20, "wait_v")

    def color(self, value):
        self.write(0x2121, 0)
        self.write(0x2122, value & 255)
        self.write(0x2122, value >> 8)

    def expect(self, value, failcode):
        label = f"assert_{failcode:02X}"
        self.emit(f"CMP #${value:02X}", 0xC9, value)
        self.ref(0xF0, label, True)
        self.mark(6, failcode)
        self.ref(0x4C, "failed")
        self.label(label)

    def finish(self):
        for position, label, relative in self.fixups:
            target = self.labels[label]
            if relative:
                delta = target - (0x8000 + position + 1)
                assert -128 <= delta <= 127, (label, delta)
                self.data[position] = delta & 255
            else:
                self.data[position:position + 2] = struct.pack("<H", target)
        assert len(self.data) < 0x7FC0
        return bytes(self.data)


def build(output):
    c = Code()
    c.label("reset")
    c.emit("SEI; CLC; XCE; REP #$30 (native A16/X16)", 0x78, 0x18, 0xFB, 0xC2, 0x30)
    c.emit("LDX #$1FFF; TXS; LDA #0; TCD; SEP #$20 (A8)", 0xA2, 0xFF, 0x1F, 0x9A,
           0xA9, 0, 0, 0x5B, 0xE2, 0x20)
    c.write(0x2100, 0x80)  # Forced blank during all setup.
    for reg in (0x4200, 0x420B, 0x420C, 0x2101, 0x2102, 0x2103, 0x2105,
                0x212C, 0x212D, 0x2130, 0x2131, 0x2133):
        c.absolute(0x9C, reg, f"STZ ${reg:04X}")
    c.write(0x4201, 0x80)  # Enable software H/V latching.
    for offset, value in enumerate(b"GTC4\x01\x00\x00\x00"):
        c.mark(offset, value)

    # All 128 small sprites: x=0, y=240, tile=0, attributes=0. None wraps to
    # V=0 and none is eligible before V=240; no earlier overflow can mask it.
    c.emit("LDX #0", 0xA2, 0, 0)
    c.label("oam_low")
    for value in (0, 240, 0, 0):
        c.write(0x2104, value)
    c.emit("INX; CPX #128", 0xE8, 0xE0, 128, 0)
    c.ref(0xD0, "oam_low", True)
    c.emit("LDX #0", 0xA2, 0, 0)
    c.lda(0)
    c.label("oam_high")
    c.absolute(0x8D, 0x2104, "STA $2104")
    c.emit("INX; CPX #32", 0xE8, 0xE0, 32, 0)
    c.ref(0xD0, "oam_high", True)
    c.color(COLORS["obj"])
    c.write(0x2122, 0x34)  # CGRAM[1] = $1234: distinguish CPU addr from latch 0.
    c.write(0x2122, 0x12)

    c.wait(250)
    c.write(0x2133, 4)
    c.write(0x2100, 15)
    c.wait(1)  # V=0 has latched overscan on.
    c.wait(239)
    c.read(0x213E)
    c.save(8)
    c.emit("AND #$C0", 0x29, 0xC0)
    c.expect(0, 0xE1)
    c.wait(241)  # After the V=240 OBJ fetch/status accumulation phase.
    c.read(0x213E)
    c.save(9)
    c.emit("AND #$C0", 0x29, 0xC0)
    c.save(10)
    c.expect(0x40, 0xE2)
    c.mark(11)

    # Change at V=250: actual on->off transition clear at the following V=0.
    c.wait(250)
    c.color(COLORS["transition"])
    c.write(0x2133, 0)
    c.wait(1)
    c.wait(241)
    c.mark(12)

    c.wait(250)
    c.color(COLORS["mixed"])
    c.wait(1)  # Placement latched off, centered by +7 pairs.
    c.wait(233)
    c.emit("LDA $00 (observed V low)", 0xA5, 0)
    c.save(13)
    c.write(0x2133, 4)  # Live overscan on; centered destinations are outside output.
    c.write(0x2121, 1)  # CPU requests palette 1, but active access uses latch 0.
    c.read(0x213F)
    c.read(0x2137)
    c.read(0x213C)
    c.save(14)  # H-dot low before the two CGRAM reads.
    c.read(0x213C)
    c.read(0x213B)
    c.save(15)
    c.expect(COLORS["mixed"] & 255, 0xE3)
    c.read(0x213B)
    c.save(16)
    c.emit("AND #$7F", 0x29, 0x7F)
    c.expect(COLORS["mixed"] >> 8, 0xE4)
    c.wait(241)
    c.read(0x213E)
    c.save(17)
    c.emit("AND #$C0", 0x29, 0xC0)
    c.expect(0x40, 0xE5)
    c.mark(18)

    c.wait(250)
    c.color(COLORS["interlace"])
    c.write(0x2133, 5)  # Overscan + screen interlace; OBJ interlace stays off.
    c.wait(1)
    c.wait(241)
    c.read(0x213F)
    c.emit("AND #$80", 0x29, 0x80)
    c.save(19)
    c.wait(1)
    c.wait(241)
    c.read(0x213F)
    c.emit("AND #$80", 0x29, 0x80)
    c.save(20)
    c.emit("EOR $700013", 0x4F, 19, 0, 0x70)
    c.expect(0x80, 0xE6)
    c.mark(21)
    c.mark(5, 0xA5)
    c.label("idle")
    c.ref(0x4C, "idle")
    c.label("failed")
    c.ref(0x4C, "failed")

    # Poll a latched 9-bit V counter. STAT78 resets both read flip-flops;
    # both OPVCT bytes are consumed. SEP #$20 preserves CMP's Z flag.
    c.label("wait_v")
    c.emit("STX $02 (X16 target)", 0x86, 2)
    c.label("wait_v_loop")
    c.read(0x213F)
    c.read(0x2137)
    c.read(0x213D)
    c.emit("STA $00", 0x85, 0)
    c.read(0x213D)
    c.emit("AND #1; STA $01; REP #$20; LDA $00; CMP $02; SEP #$20",
           0x29, 1, 0x85, 1, 0xC2, 0x20, 0xA5, 0, 0xC5, 2, 0xE2, 0x20)
    c.ref(0xD0, "wait_v_loop", True)
    c.emit("RTS", 0x60)
    c.label("interrupt")
    c.emit("RTI (interrupts are disabled)", 0x40)
    code = c.finish()

    rom = bytearray([0xFF] * 32768)
    rom[:len(code)] = code
    assert len(TITLE) == 21
    rom[0x7FC0:0x7FD5] = TITLE
    rom[0x7FD5:0x7FDC] = bytes([0x20, 0x02, 0x05, 0x01, 0x01, 0x00, 0x00])
    rom[0x7FDC:0x7FE0] = b"\0" * 4
    for vector in range(0x7FE0, 0x8000, 2):
        rom[vector:vector + 2] = struct.pack("<H", c.labels["interrupt"])
    rom[0x7FFC:0x7FFE] = struct.pack("<H", c.labels["reset"])
    checksum = (sum(rom) + 510) & 65535
    rom[0x7FDC:0x7FE0] = struct.pack("<HH", checksum ^ 65535, checksum)
    assert sum(rom) & 65535 == checksum
    assert len(rom) == 32768
    output.mkdir(parents=True, exist_ok=False)
    (output / "bounds-phase4.sfc").write_bytes(rom)
    listing = [entry if isinstance(entry, str) else
               f"{0x8000 + entry[0]:04X}  " +
               code[entry[0]:entry[0] + entry[1]].hex(" ") + "  " + entry[2]
               for entry in c.listing]
    (output / "fixture-listing.txt").write_text("\n".join(listing) + "\n")
    manifest = {"rom_sha256": hashlib.sha256(rom).hexdigest(), "rom_bytes": len(rom),
                "code_bytes": len(code), "sram_seed_sha256": hashlib.sha256(bytes(SRAM_SIZE)).hexdigest(),
                "colors_snes_bgr555": COLORS, "labels": c.labels,
                "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(build(parser.parse_args().output), indent=2))
