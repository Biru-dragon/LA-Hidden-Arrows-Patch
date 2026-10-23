import os
import re
import struct
import sys
from pathlib import Path

EXE_NAME = "Logic Arrows.exe"
BACKUP_NAME = "Logic Arrows.original.exe"
MAX_ID = 43

# Toolbar filter: cmp reg8,0x19 ; setae ; cmp reg8,0x15 ; sete   (keep an arrow only if ID-1 < 25 and ID != 21)
TOOLBAR_FILTER = re.compile(
    rb"([\x40-\x4f]\x80[\xf8-\xff])\x19"
    rb"([\x40-\x4f]\x0f\x93[\xc0-\xc7])"
    rb"([\x40-\x4f]\x80[\xf8-\xff])\x15"
    rb"([\x40-\x4f]\x0f\x94[\xc0-\xc7])",
    re.DOTALL,
)

# Guide filter: lea r32,[reg-0x1a] ; cmp r8,0xe7 ; setae ; cmp r8,0x15 ; setne   (available if 1 <= ID <= 25 and ID != 21)
GUIDE_FILTER = re.compile(
    rb"([\x40-\x4f]?\x8d[\x40-\x7f])\xe6"
    rb"(\x3c|[\x40-\x4f]?\x80[\xf8-\xff])\xe7"
    rb"[\x40-\x4f]?\x0f\x93[\xc0-\xc7]"
    rb"([\x40-\x4f]?\x80[\xf8-\xff])\x15"
    rb"[\x40-\x4f]?\x0f\x95[\xc0-\xc7]",
    re.DOTALL,
)

# Source/Target filter: in the function that cleans the toolbar rows, "test r8b,r8b ; je <path that removes IDs 22 and 23>".
# Replacing the 2-byte `je` (74 57) with two nops always takes the path that keeps every ID.
SOURCE_TARGET_FILTER = re.compile(
    rb"\x45\x84\xc0\x74\x57\x4c\x8b\x3d....\x4c\x89\xf5\x4d\x89\xf5\xeb\x1f",
    re.DOTALL,
)
SOURCE_TARGET_JE_OFFSET = 3


def executable_ranges(data: bytes) -> list[tuple[int, int]]:
    try:
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[:2] != b"MZ" or data[pe:pe + 4] != b"PE\0\0":
            raise ValueError
        section_count = struct.unpack_from("<H", data, pe + 6)[0]
        optional_size = struct.unpack_from("<H", data, pe + 20)[0]
        if struct.unpack_from("<H", data, pe + 24)[0] != 0x20B:
            raise ValueError
        ranges = []
        for index in range(section_count):
            fields = struct.unpack_from("<8sIIIIIIHHI", data, pe + 24 + optional_size + 40 * index)
            raw_size, raw_pointer, characteristics = fields[3], fields[4], fields[9]
            if characteristics & 0x20000000 or characteristics & 0x20:
                ranges.append((raw_pointer, raw_pointer + raw_size))
        return ranges
    except (struct.error, ValueError):
        sys.exit(f'Error: "{EXE_NAME}" is not a valid 64-bit Windows executable.')


def main() -> None:
    folder = Path(__file__).resolve().parent
    exe, backup = folder / EXE_NAME, folder / BACKUP_NAME
    if not exe.is_file():
        sys.exit(f'Error: "{EXE_NAME}" not found next to this script.')

    data = bytearray(exe.read_bytes())
    code = executable_ranges(bytes(data))
    toolbar = [(m.end(1), m.end(3)) for a, b in code for m in TOOLBAR_FILTER.finditer(data, a, b)]
    guide = [(m.end(1), m.end(2), m.end(3)) for a, b in code for m in GUIDE_FILTER.finditer(data, a, b)]
    source_target = [m.start() + SOURCE_TARGET_JE_OFFSET for a, b in code for m in SOURCE_TARGET_FILTER.finditer(data, a, b)]
    if not toolbar and not guide and not source_target:
        sys.exit("Nothing to patch: the game is already patched, or this is a different version.")

    for limit_offset, exclude_offset in toolbar:
        data[limit_offset], data[exclude_offset] = MAX_ID, 0x00
    for lea_offset, cmp_offset, exclude_offset in guide:
        data[lea_offset] = (-(MAX_ID + 1)) & 0xFF
        data[cmp_offset] = (256 - MAX_ID) & 0xFF
        data[exclude_offset] = 0xFF
    for je_offset in source_target:
        data[je_offset:je_offset + 2] = b"\x90\x90"

    temp = exe.with_name(exe.name + ".tmp")
    try:
        temp.write_bytes(data)
    except OSError as error:
        sys.exit(f"Error: could not write {temp.name} ({error}). Nothing was changed.")
    if toolbar:
        os.replace(exe, backup)
    try:
        os.replace(temp, exe)
    except OSError as error:
        if toolbar:
            os.replace(backup, exe)
        temp.unlink(missing_ok=True)
        sys.exit(f"Error: could not replace {EXE_NAME} ({error}). Nothing was changed.")
    print(f"Done: {len(toolbar)} toolbar, {len(guide)} guide and {len(source_target)} source/target filters patched.")
    if toolbar:
        print(f'The original was renamed "{BACKUP_NAME}".')


if __name__ == "__main__":
    main()
