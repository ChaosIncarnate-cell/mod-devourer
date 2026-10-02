#!/usr/bin/env python3
"""Class 10 rows that can only come from the game's own DBC files, as server SQL (task 003, rules from task 006).

    python tools/build_class_dbc_sql.py --dbc <server>/data/dbc

Reads the server's DBCs (the files extracted from the client) and writes
    data/sql/db-world/2026_09_30_05_devourer_class_dbc.generated.sql
which the worldserver applies with the module's other SQL. The file holds copies of Blizzard rows, so it is
ignored by git (hard rule 2) and every install generates it again. It contains:

  * skillraceclassinfo_dbc  every row that lets the warrior have a skill (weapons, armour, languages, riding,
                            professions ...), overridden with class 10 added to its ClassMask. The warrior's
                            class skill lines (SkillLine category 7: Arms, Fury, Protection) are left out, and so
                            are the skills a Devourer never has (task 006: leather, no mail/plate/shields, no
                            swords, axes, bows, guns, crossbows or thrown; see NOT_DEVOURER).
  * skilllineability_dbc    the same for the abilities of those skills (Parry, Dual Wield ...).
  * charstartoutfit_dbc     per race and gender: the rogue's leather (races without rogues take the druid's,
                            then the hunter's), its weapons replaced by a Bent Staff, as class 10.

It also checks that the ids the committed SQL uses for class 10 are free in these DBCs (ChrClasses 10,
TalentTab 900-902, Talent 9000-9179, Spell 9100000-9101099, CreatureModelData 902038-902045,
CreatureDisplayInfo 991001-991065, SkillLine 900-902, SkillRaceClassInfo 91000-91002, SkillLineAbility 91001-91999) and
stops if one is taken.

Removal: data/sql/uninstall/world.sql deletes the rows by class 10's bit (512) and ClassID 10.
The client patch (tools/client/build_client_patch.py, task 004) imports these rules, applies them to the client's
DBCs and writes this same file from the client's copies, so both sides get the same rows.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

CLASS_ID = 10
CLASS_BIT = 1 << (CLASS_ID - 1)
WARRIOR_BIT = 1
SKILL_CATEGORY_CLASS = 7
OUTFIT_FALLBACK = (4, 11, 3)            # rogue, druid, hunter: the leather wearers
# Skills the warrior has and a Devourer does not (task 006): Mail, Plate Mail, Shield, Swords, Two-Handed Swords,
# Axes, Two-Handed Axes, Bows, Guns, Crossbows, Thrown. Kept: Leather, Cloth, Daggers, Fist Weapons, Maces,
# Two-Handed Maces, Staves, Polearms, Unarmed, Defense (weapon masters teach what the class starts without).
NOT_DEVOURER = {413, 293, 433, 43, 55, 44, 172, 45, 46, 226, 176}
OUTFIT_WEAPON = 35                      # Bent Staff (the Tauren druid's), for every race
OUTFIT_WEAPON_LOOK = (35, 472, 17)       # its display and inventory type in a stock 3.3.5a CharStartOutfit.dbc
WEAPON_INVENTORY_TYPES = {13, 14, 15, 17, 18, 21, 22, 23, 24, 25, 26, 28}   # weapons, shields, ranged, ammo, quivers
OUT_NAME = "2026_09_30_05_devourer_class_dbc.generated.sql"

# (DBC file, id ranges the committed SQL adds rows in)
RESERVED = [
    ("ChrClasses.dbc", [(CLASS_ID, CLASS_ID)]),
    ("TalentTab.dbc", [(900, 902)]),
    ("Talent.dbc", [(9000, 9179)]),
    ("Spell.dbc", [(9100000, 9101099)]),
    ("CreatureModelData.dbc", [(902038, 902045)]),
    ("CreatureDisplayInfo.dbc", [(991001, 991065)]),
    ("SkillLine.dbc", [(900, 902)]),                    # the Devourer's three spellbook tabs (tasks 008, 011, tools/spellbook.py)
    ("SkillRaceClassInfo.dbc", [(91000, 91002)]),
    ("SkillLineAbility.dbc", [(91001, 91999)]),
]
DEVOURER_SKILLS = (900, 901, 902)       # rows of these skill lines come from 2026_09_30_09, not from this file


class Dbc:
    """A WDBC file as rows of 32-bit words (every table read here is dword aligned except CharStartOutfit)."""

    def __init__(self, source: Path | bytes, name: str | None = None):
        data = source if isinstance(source, (bytes, bytearray)) else source.read_bytes()
        self.path = Path(name or getattr(source, "name", "?"))
        magic, self.count, self.fields, self.size, strings = struct.unpack_from("<4s4I", data)
        if magic != b"WDBC":
            raise SystemExit(f"{self.path}: not a WDBC file")
        self.records = [data[20 + i * self.size:20 + (i + 1) * self.size] for i in range(self.count)]

    def words(self, i: int) -> tuple[int, ...]:
        rec = self.records[i]
        return struct.unpack_from(f"<{len(rec) // 4}I", rec)

    def ids(self) -> set[int]:
        return {struct.unpack_from("<I", r)[0] for r in self.records}

    def expect(self, fields: int, size: int):
        if (self.fields, self.size) != (fields, size):
            raise SystemExit(f"{self.path.name}: {self.fields} fields / {self.size} bytes, expected {fields} / {size}"
                             " (not a 3.3.5a 12340 table?)")


def signed(v: int) -> int:
    return v - (1 << 32) if v & 0x80000000 else v


def insert(table: str, cols: list[str], rows: list) -> list[str]:
    if not rows:
        return [f"-- {table}: nothing to add"]
    return [f"INSERT INTO `{table}` (" + ", ".join(f"`{c}`" for c in cols) + ") VALUES",
            ",\n".join("(" + ", ".join(map(str, r)) + ")" for r in rows) + ";"]


# The rules, shared with the client patch (tools/client/build_client_patch.py) so both sides get the same rows.
# `load(name)` returns the Dbc of that file name.

def taken_ids(load) -> list[str]:
    """The Devourer's reserved ids that are already used in these DBCs (empty when all are free)."""
    taken = []
    for name, ranges in RESERVED:
        ids = load(name).ids()
        for lo, hi in ranges:
            clash = sorted(i for i in ids if lo <= i <= hi)
            if clash:
                taken.append(f"{name}: {clash[:10]}{' ...' if len(clash) > 10 else ''} (range {lo}-{hi})")
    return taken


def class_skill_lines(load) -> set[int]:
    skill_line = load("SkillLine.dbc")
    skill_line.expect(56, 224)
    return {w[0] for w in map(skill_line.words, range(skill_line.count)) if w[1] == SKILL_CATEGORY_CLASS}


def race_class_rows(load, class_lines: set[int]) -> list[tuple]:
    """SkillRaceClassInfo: ID, SkillID, RaceMask, ClassMask, Flags, MinLevel, SkillTierID, SkillCostIndex."""
    rci = load("SkillRaceClassInfo.dbc")
    rci.expect(8, 32)
    rows = []
    for i in range(rci.count):
        w = rci.words(i)
        if w[3] & WARRIOR_BIT and not w[3] & CLASS_BIT and w[1] not in class_lines and w[1] not in NOT_DEVOURER:
            rows.append((w[0], w[1], signed(w[2]), signed(w[3] | CLASS_BIT), w[4], w[5], w[6], w[7]))
    return rows


def ability_rows(load, class_lines: set[int]) -> list[list]:
    """SkillLineAbility: ID, SkillLine, Spell, RaceMask, ClassMask, ExcludeRace, ExcludeClass, MinSkillLineRank,
    SupercededBySpell, AcquireMethod, TrivialSkillLineRankHigh, TrivialSkillLineRankLow, CharacterPoints_1, _2."""
    sla = load("SkillLineAbility.dbc")
    sla.expect(14, 56)
    rows = []
    for i in range(sla.count):
        w = sla.words(i)
        if w[4] & WARRIOR_BIT and not w[4] & CLASS_BIT and w[1] not in class_lines and w[1] not in NOT_DEVOURER:
            r = list(w)
            r[3], r[4], r[5], r[6] = signed(w[3]), signed(w[4] | CLASS_BIT), signed(w[5]), signed(w[6])
            rows.append(r)
    return rows


def outfit_rows(load) -> list[tuple]:
    """CharStartOutfit: uint32 ID, uint8 race, class, gender, outfit, then 24 items, 24 displays, 24 inventory
    types. A leather wearer's outfit (OUTFIT_FALLBACK) without its weapons, plus OUTFIT_WEAPON, as class 10, new
    ids after the file's highest."""
    cso = load("CharStartOutfit.dbc")
    cso.expect(77, 296)
    outfits = {}
    weapon = None                                       # (item, display, inventory type) as some outfit has it
    for rec in cso.records:
        rid, race, cls, gender, outfit = struct.unpack_from("<I4B", rec)
        values = struct.unpack_from("<72i", rec, 8)
        outfits[(race, cls, gender)] = (outfit, values)
        for i in range(24):
            if values[i] == OUTFIT_WEAPON:
                weapon = (values[i], values[24 + i], values[48 + i])
    if weapon is None:                                  # a client with replaced outfits (the HD patches)
        weapon = OUTFIT_WEAPON_LOOK
    next_id = max(cso.ids()) + 1
    rows = []
    for race, gender in sorted({(r, g) for r, _, g in outfits}):
        if (race, CLASS_ID, gender) in outfits:
            continue
        source = next((c for c in OUTFIT_FALLBACK if (race, c, gender) in outfits), None)
        if source is None:
            continue
        outfit, values = outfits[(race, source, gender)]
        kept = [(values[i], values[24 + i], values[48 + i]) for i in range(24)
                if values[i] > 0 and values[48 + i] not in WEAPON_INVENTORY_TYPES]
        slots = ([weapon] + kept + [(-1, -1, -1)] * 24)[:24]
        rows.append((next_id, race, CLASS_ID, gender, outfit,
                     *(s[0] for s in slots), *(s[1] for s in slots), *(s[2] for s in slots)))
        next_id += 1
    return rows


def sql_lines(rci_rows: list, sla_rows: list, cso_rows: list,
              source: str = "tools/build_class_dbc_sql.py from this server's") -> list[str]:
    out = [f"-- Generated by {source} DBC files -- do not edit, do not commit.",
           "-- Class 10 (the Devourer): the warrior's skills minus mail, shields, swords, axes and ranged weapons,",
           "-- and a leather starting outfit with a staff. Removed by uninstall/world.sql.", ""]
    out += ["DELETE FROM `skillraceclassinfo_dbc` WHERE `ClassMask` & %d AND `SkillID` NOT IN (%d, %d, %d);" % ((CLASS_BIT,) + DEVOURER_SKILLS),
            *insert("skillraceclassinfo_dbc", ["ID", "SkillID", "RaceMask", "ClassMask", "Flags", "MinLevel",
                                               "SkillTierID", "SkillCostIndex"], rci_rows), ""]
    out += ["DELETE FROM `skilllineability_dbc` WHERE `ClassMask` & %d AND `SkillLine` NOT IN (%d, %d, %d);" % ((CLASS_BIT,) + DEVOURER_SKILLS),
            *insert("skilllineability_dbc", ["ID", "SkillLine", "Spell", "RaceMask", "ClassMask", "ExcludeRace",
                                             "ExcludeClass", "MinSkillLineRank", "SupercededBySpell", "AcquireMethod",
                                             "TrivialSkillLineRankHigh", "TrivialSkillLineRankLow",
                                             "CharacterPoints_1", "CharacterPoints_2"], sla_rows), ""]
    cols = (["ID", "RaceID", "ClassID", "SexID", "OutfitID"] + [f"ItemID_{i}" for i in range(1, 25)]
            + [f"DisplayItemID_{i}" for i in range(1, 25)] + [f"InventoryType_{i}" for i in range(1, 25)])
    out += [f"DELETE FROM `charstartoutfit_dbc` WHERE `ClassID` = {CLASS_ID};",
            *insert("charstartoutfit_dbc", cols, cso_rows), ""]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dbc", required=True, type=Path, help="the server's dbc folder (…/data/dbc)")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "data" / "sql" / "db-world" / OUT_NAME)
    a = ap.parse_args()

    def load(name: str) -> Dbc:
        path = a.dbc / name
        if not path.exists():
            raise SystemExit(f"missing {path}")
        return Dbc(path)

    taken = taken_ids(load)
    if taken:
        print("These ids used by the Devourer are already taken in your DBCs:\n  " + "\n  ".join(taken), file=sys.stderr)
        return 1

    class_lines = class_skill_lines(load)
    rci_rows = race_class_rows(load, class_lines)
    sla_rows = ability_rows(load, class_lines)
    cso_rows = outfit_rows(load)
    print(f"SkillRaceClassInfo: {len(rci_rows)} rows get class {CLASS_ID}")
    print(f"SkillLineAbility: {len(sla_rows)} rows get class {CLASS_ID}")
    print(f"CharStartOutfit: {len(cso_rows)} outfits for class {CLASS_ID} (ids {cso_rows[0][0]}-{cso_rows[-1][0]})"
          if cso_rows else "CharStartOutfit: nothing to add")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text("\n".join(sql_lines(rci_rows, sla_rows, cso_rows)), encoding="utf-8")
    print(f"-> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
