# cutest-picture-01 entry v2 (Python 3.13, standard library only).
#
# The picture is entry.png beside this file: two tiny round baby penguins
# cuddling cheek to cheek in soft snow, huge bright blue eyes, one wearing
# a tiny red beanie. The program copies it to /output/entry.png (or
# $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).
#
# Deterministic: the same bytes in, the same bytes out, every run.

import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"

MAX_BYTES = 1_048_576
MAX_SIDE = 1_024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def jpeg_dimensions(data: bytes) -> tuple:
    """Read width/height from the first SOF0/SOF2 marker of a JPEG."""
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg_len
    raise SystemExit("JPEG has no SOF marker: cannot verify dimensions")


def check_gate(path: Path) -> None:
    """Fail loudly if the output would not pass the competition gate:
    a whole PNG (or JPEG) of at most 1 MiB and 1024x1024 px."""
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit(f"entry.png is {len(data)} bytes, over the 1 MiB gate")
    if data[:8] == PNG_MAGIC:
        width, height = struct.unpack(">II", data[16:24])
    elif data[:2] == b"\xff\xd8":
        width, height = jpeg_dimensions(data)
    else:
        raise SystemExit("entry.png is neither PNG nor JPEG")
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit(f"entry.png is {width}x{height}, over the 1024x1024 gate")
    if data != SOURCE.read_bytes():
        raise SystemExit("output bytes differ from entry.png: copy is not exact")
    print(f"wrote {path} ({width}x{height}, {len(data)} bytes)", file=sys.stderr)


def main() -> None:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(SOURCE, dest)
    check_gate(dest)


if __name__ == "__main__":
    main()
