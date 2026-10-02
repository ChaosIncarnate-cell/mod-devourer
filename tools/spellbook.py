#!/usr/bin/env python3
"""Tasks 008 + 011: the Devourer's three spellbook tabs (class skill lines, like Arms / Fury / Protection).

    python tools/spellbook.py

Reads the committed SQL (no client files needed) and writes
    data/sql/db-world/2026_09_30_09_devourer_spellbook.sql
Run it again whenever a Devourer spell, shape or talent is added (e.g. new forms in 2026_09_30_08).

What it writes:
  skillline_dbc            900-902   "Glutton", "Skinchanger", "Brood", SkillLine category 7 (class), in the order
                                     of the talent trees (TalentTab 900-902, OrderIndex 0-2); each tab's icon is
                                     its TalentTab icon
  skillraceclassinfo_dbc   91000-91002  class 10 may have skills 900-902 (all races), always at their maximum
  skilllineability_dbc     91001+    one row per Devourer spell, ClassMask 512, AcquireMethod 0 (the skills teach
                                     nothing by themselves; the module and the talents teach the spells). Ids are
                                     given in spellbook order: a shape's form spell, kit and passive stay together
  playercreateinfo_skills            skills 900-902 for every new Devourer (the module adds them at login when missing)

Which tab: Glutton = Devour, Quick Devour, Concentrate, the Glutton spec/talent spells. Skinchanger = Rush, every
shape's form spell, kit and passive, the Skinchanger spec/talent spells. Brood = the Brood spec/talent spells.
A spell is in exactly one tab (checked); effect helpers (hits, buffs, meals) and the hidden Anima passive are
never in the spellbook and stay out, so General holds no Devourer spell.

The client patch (tools/client/build_client_patch.py) puts the same SkillLine, SkillRaceClassInfo and
SkillLineAbility rows into the client's DBCs (it reads every committed 2026_09_30_0*.sql), which is what makes the
client show the tabs. tools/build_class_dbc_sql.py checks these ids are free (RESERVED).
Removed by data/sql/uninstall/world.sql (ids above, ClassMask 512) and uninstall/characters.sql (skills 900-902).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools" / "client"))
import sqlrows  # noqa: E402

SQL_DIR = REPO / "data" / "sql" / "db-world"
OUT_SQL = SQL_DIR / "2026_09_30_09_devourer_spellbook.sql"

SKILL_CATEGORY_CLASS = 7
# (tab name, SkillLine id = TalentTab id) in tab order; src/Devourer.h SkillGlutton etc. use the same ids
TABS = [("Glutton", 900), ("Skinchanger", 901), ("Brood", 902)]
RCI_FIRST = 91000                    # SkillRaceClassInfo 91000-91002
SLA_FIRST, SLA_LAST = 91001, 91999   # SkillLineAbility
CLASS_MASK = 512                     # class 10
RCI_FLAGS = 0x10                     # SKILL_FLAG_ALWAYS_MAX_VALUE: the bar is always full, like a class skill

# Spells outside devourer_shape and talent_dbc that a Devourer has in its spellbook: {spell: (tab skill, what)}.
BASE_AND_SPEC = {
    9100001: (900, "Devour"),
    9100032: (900, "Devour (Quick Devour talent)"),
    9100992: (900, "Concentrate"),
    9100011: (900, "Bottomless Appetite (Glutton)"),
    9100020: (900, "Devour Whole (Glutton)"),
    9100034: (900, "Regurgitate (Glutton talent)"),
    9100990: (901, "Rush"),
    9100012: (901, "Restless Skin (Skinchanger)"),
    9100013: (902, "Mother of the Brood (Brood)"),
    9100040: (902, "Hatch Brood (Brood)"),
    **{9100800 + i: (900 + i // 3, "spec ability (placeholder)") for i in range(9)},   # 3 per spec, in tab order
}
ICON_SPELL = 9100001                 # fallback tab icon


def committed() -> list[Path]:
    return sorted(p for p in SQL_DIR.glob("2026_09_30_0*.sql") if ".generated." not in p.name and p != OUT_SQL)


def spellbook_spells(files: list[Path]) -> dict[int, tuple[int, str]]:
    """{spell id: (tab skill, where it comes from)} in spellbook order, for every Devourer spell on a tab."""
    want: dict[int, tuple[int, str]] = {}

    def put(spell: int, skill: int, what: str):
        if spell in want and want[spell][0] != skill:
            print(f"spell {spell} ({what}) is in tabs {want[spell][0]} and {skill}; keeping {want[spell][0]}",
                  file=sys.stderr)
        want.setdefault(spell, (skill, what))

    for spell, (skill, what) in BASE_AND_SPEC.items():
        put(spell, skill, what)
    tables = [x for f in files for x in sqlrows.inserts(f.read_text(encoding="utf-8"))]
    for t, cols, rows in tables:                 # Skinchanger: every shape's spells, one shape after the other
        if t == "devourer_shape":
            for r in rows:
                d = dict(zip(cols, r))
                for c in ("form_spell", "spell_1", "spell_2", "spell_3", "spell_4", "passive"):
                    if d.get(c):
                        put(int(d[c]), 901, f"shape {d['shape_id']} {d['name']}: {c}")
    for t, cols, rows in tables:                 # talents: the tab of their tree, by tier and column
        if t == "talent_dbc":
            for d in sorted((dict(zip(cols, r)) for r in rows), key=lambda d: (int(d["TierID"]), int(d["ColumnIndex"]))):
                for c in cols:
                    if c.startswith("SpellRank_") and d[c]:
                        put(int(d[c]), int(d["TabID"]), f"talent {d['ID']}")
    return want


def q(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


def main() -> int:
    files = committed()
    spells = sqlrows.table_rows(files, "spell_dbc")
    tabs = sqlrows.table_rows(files, "talenttab_dbc")
    want = spellbook_spells(files)
    for s in sorted(s for s in want if s not in spells):
        print(f"skipped {s} ({want[s][1]}): no spell_dbc row in the committed SQL", file=sys.stderr)
    # spellbook order: tab by tab, each tab in the order the spells were found (a shape's spells stay together)
    ids = [s for _, skill in TABS for s, (k, _) in want.items() if k == skill and s in spells]
    if len(ids) > SLA_LAST - SLA_FIRST + 1:
        print(f"{len(ids)} spells do not fit SkillLineAbility {SLA_FIRST}-{SLA_LAST}", file=sys.stderr)
        return 1
    if len(set(ids)) != len(ids):
        print("a spell is on a tab twice", file=sys.stderr)
        return 1
    for name, skill in TABS:                      # the tab order must be the talent tree order
        if skill not in tabs or tabs[skill]["Name_Lang_enUS"] != name or int(tabs[skill]["OrderIndex"]) != skill - 900:
            print(f"TalentTab {skill} is not '{name}' at order {skill - 900}", file=sys.stderr)
            return 1
    icons = {skill: int(tabs[skill]["SpellIconID"]) for _, skill in TABS}
    skills = [s for _, s in TABS]

    sql = [
        "-- Generated by tools/spellbook.py (tasks 008, 011). Do not edit by hand: change the script and run it again.",
        "-- The Devourer's three spellbook tabs: class skill lines 900-902 (Glutton, Skinchanger, Brood) and their",
        "-- spells. Safe to run again; removed by uninstall/world.sql (skills 900-902, SkillRaceClassInfo 91000-91002,",
        f"-- SkillLineAbility {SLA_FIRST}-{SLA_LAST}) and uninstall/characters.sql.",
        "-- The client patch tool copies the three *_dbc tables into the client's DBCs.",
        "",
        f"DELETE FROM `skillline_dbc` WHERE `ID` BETWEEN {skills[0]} AND {skills[-1]};",
        "INSERT INTO `skillline_dbc` (`ID`, `CategoryID`, `SkillCostsID`, `DisplayName_Lang_enUS`, "
        "`DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_Mask`, `SpellIconID`, "
        "`AlternateVerb_Lang_enUS`, `AlternateVerb_Lang_Mask`, `CanLink`) VALUES",
        ",\n".join(f"({skill}, {SKILL_CATEGORY_CLASS}, 0, {q(name)}, 16712190, '', 16712190, {icons[skill]}, '', "
                   f"16712190, 0)" for name, skill in TABS) + ";",
        "",
        f"DELETE FROM `skillraceclassinfo_dbc` WHERE `ID` BETWEEN {RCI_FIRST} AND {RCI_FIRST + len(TABS) - 1};",
        "INSERT INTO `skillraceclassinfo_dbc` (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, `MinLevel`, "
        "`SkillTierID`, `SkillCostIndex`) VALUES",
        ",\n".join(f"({RCI_FIRST + i}, {skill}, 0, {CLASS_MASK}, {RCI_FLAGS}, 0, 0, 0)"
                   for i, (_, skill) in enumerate(TABS)) + ";",
        "",
        f"DELETE FROM `skilllineability_dbc` WHERE `ID` BETWEEN {SLA_FIRST} AND {SLA_LAST};",
        "INSERT INTO `skilllineability_dbc` (`ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, "
        "`ExcludeClass`, `MinSkillLineRank`, `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`, "
        "`TrivialSkillLineRankLow`, `CharacterPoints_1`, `CharacterPoints_2`) VALUES",
        ",\n".join(f"({SLA_FIRST + i}, {want[s][0]}, {s}, 0, {CLASS_MASK}, 0, 0, 0, 0, 0, 0, 0, 0, 0)"
                   for i, s in enumerate(ids)) + ";",
        "",
        "-- The skills at creation (the module also adds them at login to a Devourer without them).",
        f"DELETE FROM `playercreateinfo_skills` WHERE `classMask` = {CLASS_MASK} AND `skill` BETWEEN "
        f"{skills[0]} AND {skills[-1]};",
        "INSERT INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES",
        ",\n".join(f"(0, {CLASS_MASK}, {skill}, 0, {q('Devourer: class skill, spellbook tab ' + name)})"
                   for name, skill in TABS) + ";",
        "",
    ]
    with open(OUT_SQL, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sql))
    counts = ", ".join(f"{name} {sum(1 for s in ids if want[s][0] == skill)}" for name, skill in TABS)
    print(f"wrote {OUT_SQL.relative_to(REPO)}: {len(ids)} spells on the Devourer tabs ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
