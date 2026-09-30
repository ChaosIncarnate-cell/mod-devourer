#!/usr/bin/env python3
"""ChaosCore0.3 (Copus55, 2026-09-28): the Glutton's talent tree, as rows of CharacterAdvancement.dbc.

    python build_glutton_talents.py --dbc <CharacterAdvancement.dbc> --out <new CharacterAdvancement.dbc>

The CoA talent frame (client) and the CoA talent service (server) both read CharacterAdvancement.dbc: a node is
one row with its spell(s), cost, tab, position and the nodes it hangs from. Taking a node teaches its spell;
mod-devourer reads the spells to know which talents a Devourer has. The same file goes to the server's
Data\\dbc, to identity\\server-dbc (the package copy) and into the client's patch-T.MPQ.

Rows 139010-139019 are the Glutton's (139001-139003 are the three spec identities). Safe to run again: the
rows in that range are replaced, nothing else is touched. Each row is copied from a CoA talent of the same shape
(5744 "Decapitate", a square = an ability; 6744 "Beheader", a circle = a passive), so every field this script
does not set keeps a value the client already knows.

Layout (tab Glutton, x 0-9, y downwards; the identity passive sits in the free column x=10):

        Quick Devour (3,0)          Devour Whole (5,0) [ability]
              |                            |
          Feast (3,2)                Regurgitate (5,2)
                 \\                        /
                     Stretched Gut (4,4)
                            |
         Digested: Thick Hide / Bile Coating (5,6)   [choice: one of the two]
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

CLASS_TYPE = 22              # CharacterAdvancementClassTypes row of class 20 (Devourer)
TAB_GLUTTON = 95             # CharacterAdvancementTabTypes "Glutton"
RANGE = (139010, 139019)
TEMPLATE_SQUARE, TEMPLATE_CIRCLE = 5744, 6744

# dword fields
F_ID, F_REQUIRED, F_SPELLS, F_AE, F_TE, F_LEVEL, F_GROUP, F_CLASS_TYPE, F_TAB = 0, 2, 5, 14, 15, 26, 29, 32, 33
F_TAB_TE_GATE, F_NAME, F_ICON = 39, 47, 64
# byte offsets inside a record (these sit 2 bytes off the dword grid)
B_X, B_Y, B_LINKS, B_LINKS_END = 398, 402, 411, 471

# (entry, name, icon, spell, square?, x, y, links, choice group, TE gate)
NODES = [
    (139010, "Quick Devour", "inv_misc_food_14", 9100031, False, 3, 0, [], 0, 0),
    (139011, "Devour Whole", "ability_devour", 9100020, True, 5, 0, [], 0, 0),
    (139012, "Feast", "inv_misc_organ_01", 9100035, False, 3, 2, [139010], 0, 0),
    (139013, "Regurgitate", "spell_nature_acid_01", 9100033, False, 5, 2, [139011], 0, 0),
    (139014, "Stretched Gut", "inv_misc_organ_03", 9100036, False, 4, 4, [139012, 139013], 0, 0),
    (139015, "Digested: Thick Hide", "inv_qiraj_ourohide", 9100037, False, 5, 6, [139014], 9100037, 4),
    (139016, "Digested: Bile Coating", "spell_nature_spiritarmor", 9100038, False, 5, 6, [139014], 9100037, 4),
]


class Dbc:
    def __init__(self, path: Path):
        d = path.read_bytes()
        magic, self.n, self.f, self.rs, ss = struct.unpack_from("<4s4I", d)
        assert magic == b"WDBC" and self.rs == 692, f"{path}: not the CharacterAdvancement layout ({self.f}, {self.rs})"
        self.recs = [bytearray(d[20 + i * self.rs:20 + (i + 1) * self.rs]) for i in range(self.n)]
        self.strings = bytearray(d[20 + self.n * self.rs:20 + self.n * self.rs + ss])

    def find(self, rid: int) -> bytearray | None:
        return next((r for r in self.recs if struct.unpack_from("<I", r)[0] == rid), None)

    def add(self, text: str) -> int:
        at = self.strings.find(b"\0" + text.encode() + b"\0")
        if at >= 0:
            return at + 1
        at = len(self.strings)
        self.strings += text.encode() + b"\0"
        return at

    def save(self, path: Path):
        body = b"".join(bytes(r) for r in self.recs)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(struct.pack("<4s4I", b"WDBC", len(self.recs), self.f, self.rs, len(self.strings))
                         + body + bytes(self.strings))


def put(rec: bytearray, field: int, value: int):
    struct.pack_into("<I", rec, field * 4, value)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dbc", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()

    db = Dbc(a.dbc)
    before = len(db.recs)
    db.recs = [r for r in db.recs if not RANGE[0] <= struct.unpack_from("<I", r)[0] <= RANGE[1]]
    removed = before - len(db.recs)
    templates = {True: db.find(TEMPLATE_SQUARE), False: db.find(TEMPLATE_CIRCLE)}
    assert all(templates.values()), "template talents 5744/6744 missing"
    assert db.find(139001), "the Glutton identity entry 139001 is missing: install the Devourer identity first"

    for entry, name, icon, spell, square, x, y, links, group, gate in NODES:
        rec = bytearray(templates[square])
        put(rec, F_ID, entry)
        for i in range(3):
            put(rec, F_REQUIRED + i, 0)
        for i in range(5):
            put(rec, F_SPELLS + i, spell if i == 0 else 0)
        put(rec, F_AE, 0)
        put(rec, F_TE, 1)
        put(rec, F_LEVEL, 0)
        put(rec, F_GROUP, group)
        put(rec, F_CLASS_TYPE, CLASS_TYPE)
        put(rec, F_TAB, TAB_GLUTTON)
        put(rec, F_TAB_TE_GATE, gate)
        put(rec, F_NAME, db.add(name))
        put(rec, F_ICON, db.add(icon))
        struct.pack_into("<f", rec, B_X, float(x))
        struct.pack_into("<f", rec, B_Y, float(y))
        rec[B_LINKS:B_LINKS_END] = bytes(B_LINKS_END - B_LINKS)
        for i, link in enumerate(links):
            struct.pack_into("<I", rec, B_LINKS + 4 * i, link)
        db.recs.append(rec)

    db.save(a.out)
    print(f"Glutton talents: {len(NODES)} nodes written ({removed} old ones replaced) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
