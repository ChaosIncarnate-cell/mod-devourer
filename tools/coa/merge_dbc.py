#!/usr/bin/env python3
"""Merges the Devourer's creature models and displays into an existing DBC, keeping everything else in it.

    python merge_dbc.py <target.dbc> <source.dbc>

Rows of the source whose id is in a range the Devourer owns replace the target's; any other source row is
added only if the target does not have that id yet (models added later by other tools stay as they are).
Only CreatureDisplayInfo.dbc and CreatureModelData.dbc are supported (their string fields are known).
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

STRING_FIELDS = {
    "creaturedisplayinfo.dbc": (6, 7, 8, 9),
    "creaturemodeldata.dbc": (2,),
}
OWNED = {
    "creaturedisplayinfo.dbc": [(980001, 980999), (991001, 991009)],
    "creaturemodeldata.dbc": [(902001, 902037), (902043, 902043)],   # 902043: the snake's right file name
}


def load(path: Path):
    data = path.read_bytes()
    magic, count, fields, size, strsize = struct.unpack_from("<4s4I", data)
    if magic != b"WDBC" or size % 4:
        raise SystemExit(f"{path}: not a WDBC file")
    rows = [list(struct.unpack_from(f"<{size // 4}I", data, 20 + i * size)) for i in range(count)]
    strings = bytearray(data[20 + count * size:20 + count * size + strsize])
    return fields, size, rows, strings


def text(strings: bytearray, offset: int) -> bytes:
    if offset <= 0 or offset >= len(strings):
        return b""
    return bytes(strings[offset:strings.index(b"\0", offset)])


def main():
    target, source = Path(sys.argv[1]), Path(sys.argv[2])
    kind = target.name.lower()
    if kind not in STRING_FIELDS:
        raise SystemExit(f"{target.name}: not a table this tool merges")
    t_fields, t_size, t_rows, t_strings = load(target)
    s_fields, s_size, s_rows, s_strings = load(source)
    if (t_fields, t_size) != (s_fields, s_size):
        raise SystemExit(f"{target.name}: different layouts, not merged")

    cache: dict[bytes, int] = {}

    def add(value: bytes) -> int:
        if not value:
            return 0
        if value not in cache:
            cache[value] = len(t_strings)
            t_strings.extend(value + b"\0")
        return cache[value]

    owned = OWNED[kind]
    by_id = {row[0]: i for i, row in enumerate(t_rows)}
    added = replaced = 0
    for row in s_rows:
        rid = row[0]
        mine = any(lo <= rid <= hi for lo, hi in owned)
        if rid in by_id and not mine:
            continue
        if rid in by_id:
            old = t_rows[by_id[rid]]
            same = all(old[i] == row[i] for i in range(len(row)) if i not in STRING_FIELDS[kind]) and all(
                text(t_strings, old[f]) == text(s_strings, row[f]) for f in STRING_FIELDS[kind])
            if same:
                continue
        new = list(row)
        for field in STRING_FIELDS[kind]:
            new[field] = add(text(s_strings, row[field]))
        if rid in by_id:
            t_rows[by_id[rid]] = new
            replaced += 1
        else:
            by_id[rid] = len(t_rows)
            t_rows.append(new)
            added += 1

    if added or replaced:
        body = b"".join(struct.pack(f"<{t_size // 4}I", *row) for row in t_rows)
        target.write_bytes(struct.pack("<4s4I", b"WDBC", len(t_rows), t_fields, t_size, len(t_strings))
                           + body + bytes(t_strings))
    print(f"  {target.name}: {added} added, {replaced} updated")


if __name__ == "__main__":
    main()
