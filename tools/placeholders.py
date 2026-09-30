#!/usr/bin/env python3
"""Task 005: placeholder talent trees and spec abilities for the Devourer (class 10).

One source for three outputs, keep them in step by running this script again after any change:
  data/sql/db-world/2026_09_30_07_devourer_placeholders.sql   spell_dbc + talent_dbc rows (server; the client patch
                                                              tool picks the same rows up from this file)
  src/DevourerPlaceholderIds.h                                the spec-ability spell ids the module teaches
  docs/talents.md                                             the map of every slot, for the owner to fill

Placeholders are copies of the task-003 placeholder talent spell 9100050 (a passive dummy aura without effect);
"ability" talents and the spec abilities become castable dummy spells instead. Real talents (Glutton, task 003)
and the two existing one-cell placeholders (9010 Fluid Flesh, 9015 Swelling Brood) keep their cells.

Ids: talent spells 9100500-9100799, spec abilities 9100800-9100808, talents 9020-9059 (Glutton),
9060-9119 (Skinchanger), 9120-9179 (Brood).
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPELL_SQL = REPO / "data" / "sql" / "db-world" / "2026_09_30_02_devourer_spells.sql"
OUT_SQL = REPO / "data" / "sql" / "db-world" / "2026_09_30_07_devourer_placeholders.sql"
OUT_H = REPO / "src" / "DevourerPlaceholderIds.h"
OUT_MD = REPO / "docs" / "talents.md"

TEMPLATE_SPELL = 9100050
FIRST_TALENT_SPELL, LAST_TALENT_SPELL = 9100500, 9100799
FIRST_SPEC_SPELL = 9100800

# (tier, column, ranks, kind) kind: "" = passive talent, "ability" = 1-rank castable, "capstone" = the 51-point talent
LAYOUT = [
    (0, 0, 5, ""), (0, 1, 5, ""), (0, 2, 3, ""),
    (1, 0, 3, ""), (1, 1, 5, ""), (1, 2, 2, ""), (1, 3, 3, ""),
    (2, 0, 2, ""), (2, 1, 3, ""), (2, 2, 5, ""),
    (3, 1, 1, "ability"), (3, 2, 5, ""), (3, 3, 3, ""),
    (4, 0, 5, ""), (4, 1, 2, ""), (4, 2, 3, ""),
    (5, 1, 5, ""), (5, 2, 1, "ability"), (5, 3, 3, ""),
    (6, 0, 3, ""), (6, 1, 3, ""), (6, 2, 2, ""),
    (7, 1, 1, "ability"), (7, 2, 5, ""),
    (8, 0, 2, ""), (8, 1, 3, ""), (8, 3, 3, ""),
    (9, 1, 5, ""), (9, 2, 3, ""),
    (10, 1, 1, "capstone"),
]
CAPSTONE_PREREQ = (9, 1)   # the capstone needs the tier-9 middle talent at full rank

# Cells already taken by real talents or earlier placeholders (task 003): (tier, column) -> (talent id, name, ranks, real)
EXISTING = {
    900: {(0, 0): (9000, "Iron Stomach", 5, False), (0, 1): (9001, "Quick Devour", 1, True),
          (0, 2): (9002, "Devour Whole", 1, True), (1, 0): (9003, "Deep Hunger", 5, False),
          (1, 1): (9004, "Feast", 1, True), (1, 2): (9005, "Regurgitate", 1, True),
          (2, 1): (9006, "Stretched Gut", 1, True), (3, 1): (9007, "Digested: Thick Hide", 1, True),
          (3, 2): (9008, "Digested: Bile Coating", 1, True)},
    901: {(0, 1): (9010, "Fluid Flesh", 5, False)},
    902: {(0, 1): (9015, "Swelling Brood", 5, False)},
}

TREES = [
    # tab, name, first talent id, icon, names (used in order for the free cells)
    (900, "Glutton", 9020, 166, [
        "Thick Gullet", "Iron Maw", "Bottomless Pit", "Gristle Plating", "Heavy Belly", "Bloated Resolve",
        "Digestive Fire", "Slow Chew", "Grand Appetite", "Chewing Cud", "Swallowed Pride", "Belly of the Beast",
        "Ravenous Guard", "Fat Reserves", "Gnawing Patience", "Crushing Jaw", "Satiation", "Hunger's Wall",
        "Unending Meal", "Glutton's Bulk", "Stomach of Stone", "Last Bite", "Endless Feast"]),
    (901, "Skinchanger", 9060, 3058, [
        "Shifting Hide", "Borrowed Claws", "Quick Molt", "Second Skin", "Mimic's Eye", "Restless Form", "Shed Skin",
        "Many Faces", "Loose Bones", "Stolen Instinct", "Changing Blood", "Flicker Shape", "Mask of Meat",
        "Shape Memory", "Wandering Skin", "Unfixed Nature", "Echo Flesh", "Living Mask", "Skin Hoard",
        "Swift Change", "Hollow Shell", "Worn Faces", "Borrowed Voice", "Soft Bones", "Shapeless Step",
        "Mirror Hunger", "Stolen Strength", "Fleeting Form", "Thousand Skins"]),
    (902, "Brood", 9120, 689, [
        "Warm Nest", "Egg Tooth", "Many Mouths", "Nursing Hunger", "Shared Meal", "Hatching Heat", "Brood Mother",
        "Clutch Instinct", "Hungry Young", "Nest Guard", "Feeding Frenzy", "Spawning Pool", "Litter Bond",
        "Twitching Eggs", "Swarm Call", "Nest Web", "Brood Sense", "Thick Shells", "Quick Hatching", "Blood Milk",
        "Swollen Sac", "Nest Scent", "Hive Mind", "Young Teeth", "Crawling Mass", "Mother's Wrath", "Endless Clutch",
        "Swarm Tide", "Queen of the Brood"]),
]

SPEC_ABILITIES = [
    # constant name, spec name, level, spell name
    ("SpellPlaceholderGlutton20", "Glutton", 20, "Iron Gut"),
    ("SpellPlaceholderGlutton40", "Glutton", 40, "Devouring Challenge"),
    ("SpellPlaceholderGlutton60", "Glutton", 60, "Last Supper"),
    ("SpellPlaceholderSkinchanger20", "Skinchanger", 20, "Mimic Strike"),
    ("SpellPlaceholderSkinchanger40", "Skinchanger", 40, "Skin Swap"),
    ("SpellPlaceholderSkinchanger60", "Skinchanger", 60, "Form of Many"),
    ("SpellPlaceholderBrood20", "Brood", 20, "Call the Clutch"),
    ("SpellPlaceholderBrood40", "Brood", 40, "Feed the Young"),
    ("SpellPlaceholderBrood60", "Brood", 60, "Brood Swarm"),
]


def split_values(row: str) -> list[str]:
    """Split one SQL VALUES tuple into its raw values (strings keep their quotes)."""
    body = row.strip().rstrip(",;")
    assert body.startswith("(") and body.endswith(")"), row[:60]
    body = body[1:-1]
    out, cur, quote, i = [], [], False, 0
    while i < len(body):
        c = body[i]
        if quote:
            cur.append(c)
            if c == "\\" and i + 1 < len(body):
                cur.append(body[i + 1]); i += 1
            elif c == "'":
                if i + 1 < len(body) and body[i + 1] == "'":
                    cur.append("'"); i += 1
                else:
                    quote = False
        elif c == "'":
            quote = True; cur.append(c)
        elif c == ",":
            out.append("".join(cur).strip()); cur = []
        else:
            cur.append(c)
        i += 1
    out.append("".join(cur).strip())
    return out


def load_template() -> tuple[list[str], list[str]]:
    text = SPELL_SQL.read_text(encoding="utf-8")
    header = re.search(r"INSERT INTO `spell_dbc` \((.*?)\) VALUES", text, re.S)
    if not header:
        raise SystemExit(f"no spell_dbc INSERT header in {SPELL_SQL}")
    cols = [c.strip().strip("`") for c in header.group(1).split(",")]
    row = next((l for l in text.splitlines() if l.startswith(f"({TEMPLATE_SPELL},")), None)
    if not row:
        raise SystemExit(f"template spell {TEMPLATE_SPELL} not found in {SPELL_SQL}")
    vals = split_values(row)
    if len(vals) != len(cols):
        raise SystemExit(f"template has {len(vals)} values for {len(cols)} columns")
    for needed in ("ID", "Attributes", "AttributesEx", "Effect_1", "EffectAura_1", "ImplicitTargetA_1",
                   "DurationIndex", "RecoveryTime", "SpellIconID", "Name_Lang_enUS", "NameSubtext_Lang_enUS",
                   "Description_Lang_enUS"):
        if needed not in cols:
            raise SystemExit(f"column {needed} missing in {SPELL_SQL}")
    return cols, vals


def q(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


def spell_row(cols, tmpl, spell_id, name, subtext, desc, icon, castable):
    v = dict(zip(cols, tmpl))
    v["ID"] = str(spell_id)
    v["Name_Lang_enUS"] = q(name)
    v["NameSubtext_Lang_enUS"] = q(subtext)
    v["Description_Lang_enUS"] = q(desc)
    v["SpellIconID"] = str(icon)
    if castable:
        v["Attributes"] = "0"          # not passive: shows up as an ability in the spellbook
        v["AttributesEx"] = "0"
        v["Effect_1"] = "3"            # SPELL_EFFECT_DUMMY on the caster, no effect
        v["EffectAura_1"] = "0"
        v["ImplicitTargetA_1"] = "1"
        v["DurationIndex"] = "0"
        v["RecoveryTime"] = "6000"
    return "(" + ", ".join(v[c] for c in cols) + ")"


def main():
    cols, tmpl = load_template()
    spell_rows, talent_rows, md, spec_rows = [], [], [], []
    next_spell = FIRST_TALENT_SPELL

    md.append("# Devourer talents and spec abilities\n")
    md.append("Generated by `tools/placeholders.py` (task 005) — edit the script, not this file. "
              "**(placeholder)** = no effect yet, waiting for a real design. Tiers open at 5 points per tier; "
              "a level-80 character has 71 points.\n")
    md.append(f"Ids: talent spells {FIRST_TALENT_SPELL}-{LAST_TALENT_SPELL}, spec abilities "
              f"{FIRST_SPEC_SPELL}-{FIRST_SPEC_SPELL + len(SPEC_ABILITIES) - 1}; talents 9000-9179 "
              "(Glutton 9000-9059, Skinchanger 9060-9119 plus 9010, Brood 9120-9179 plus 9015). "
              "Task 006 uses spells 9100810-9100899.\n")

    for tab, tree, first_talent, icon, names in TREES:
        existing = EXISTING.get(tab, {})
        names = iter(names)
        talent_id = first_talent
        cells: dict[tuple[int, int], int] = {cid[:2]: v[0] for cid, v in ((k, v) for k, v in existing.items())}
        md.append(f"\n## {tree} (tab {tab})\n")
        md.append("| Tier | Col | Talent | Ranks | Name | State | Needs |")
        md.append("|---|---|---|---|---|---|---|")
        rows_md = []
        for (tid, (t_id, t_name, t_ranks, real)) in sorted(existing.items()):
            rows_md.append((tid[0], tid[1], t_id, t_ranks, t_name, "real" if real else "placeholder (task 003)", ""))
        for tier, col, ranks, kind in LAYOUT:
            if (tier, col) in existing:
                continue
            base = next(names)
            label = f"{base} (placeholder)"
            castable = kind in ("ability", "capstone") and kind == "ability"
            desc = ("Placeholder ability: not designed yet." if castable
                    else "Placeholder talent: it has no effect yet.")
            spells = []
            for r in range(ranks):
                if next_spell > LAST_TALENT_SPELL:
                    raise SystemExit("talent spell range exhausted")
                spell_rows.append(spell_row(cols, tmpl, next_spell, label, f"Rank {r + 1}" if ranks > 1 else "",
                                            desc, icon, castable))
                spells.append(next_spell)
                next_spell += 1
            prereq, prereq_rank = 0, 0
            if kind == "capstone":
                prereq = cells.get(CAPSTONE_PREREQ, 0)
                prereq_rank = 4
            ranks5 = (spells + [0] * 5)[:5]
            talent_rows.append(f"({talent_id}, {tab}, {tier}, {col}, {', '.join(map(str, ranks5))}, "
                               f"{prereq}, {prereq_rank}, 0)")
            cells[(tier, col)] = talent_id
            state = {"ability": "placeholder ability", "capstone": "placeholder capstone"}.get(kind, "placeholder")
            rows_md.append((tier, col, talent_id, ranks, base, state, f"talent {prereq} (5/5)" if prereq else ""))
            talent_id += 1
        for tier, col, t_id, ranks, name, state, needs in sorted(rows_md):
            md.append(f"| {tier} | {col} | {t_id} | {ranks} | {name} | {state} | {needs} |")
        total = sum(r[3] for r in rows_md)
        md.append(f"\n{len(rows_md)} talents, {total} ranks.")

    md.append("\n## Spec abilities (learned with the spec, from the level shown)\n")
    md.append("| Spec | Level | Spell | Name | State |")
    md.append("|---|---|---|---|---|")
    md.append("| Glutton / Skinchanger / Brood | 1 | 9100011 / 9100012 / 9100013 | identity passives | real |")
    md.append("| Brood | 1 | 9100040 | Hatch Brood | real |")
    header_consts = []
    for i, (const, spec, level, name) in enumerate(SPEC_ABILITIES):
        sid = FIRST_SPEC_SPELL + i
        icon = next(t[3] for t in TREES if t[1] == spec)
        spec_rows.append(spell_row(cols, tmpl, sid, f"{name} (placeholder)", "",
                                   f"Placeholder {spec} ability (level {level}): not designed yet.", icon, True))
        header_consts.append(f"    constexpr uint32_t {const:<30} = {sid};   // {spec}, level {level}: {name}")
        md.append(f"| {spec} | {level} | {sid} | {name} | placeholder |")

    col_list = ", ".join(f"`{c}`" for c in cols)
    sql = [
        "-- Generated by tools/placeholders.py (task 005). Do not edit by hand: change the script and run it again.",
        "-- Placeholder talents (full trees, 11 tiers) and spec abilities for the Devourer. Safe to run again;",
        "-- removed by uninstall/world.sql (spells 9100000-9100899, talents 9000-9179).",
        f"DELETE FROM `spell_dbc` WHERE `ID` BETWEEN {FIRST_TALENT_SPELL} AND {FIRST_SPEC_SPELL + len(SPEC_ABILITIES) - 1};",
        f"INSERT INTO `spell_dbc` ({col_list}) VALUES",
        ",\n".join(spell_rows + spec_rows) + ";",
        "",
        "DELETE FROM `talent_dbc` WHERE `ID` BETWEEN 9020 AND 9059 OR `ID` BETWEEN 9060 AND 9179;",
        "INSERT INTO `talent_dbc` (`ID`, `TabID`, `TierID`, `ColumnIndex`, `SpellRank_1`, `SpellRank_2`, `SpellRank_3`,",
        "    `SpellRank_4`, `SpellRank_5`, `PrereqTalent_1`, `PrereqRank_1`, `Flags`) VALUES",
        ",\n".join(talent_rows) + ";",
        "",
    ]
    OUT_SQL.write_text("\n".join(sql), encoding="utf-8")
    OUT_H.write_text("\n".join([
        "// Generated by tools/placeholders.py (task 005) -- keep in step with 2026_09_30_07_devourer_placeholders.sql.",
        "#ifndef DEVOURER_PLACEHOLDER_IDS_H",
        "#define DEVOURER_PLACEHOLDER_IDS_H",
        "",
        "#include <cstdint>",
        "",
        "namespace Devourer",
        "{",
        *header_consts,
        "}",
        "",
        "#endif",
        "",
    ]), encoding="utf-8")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"talent spells {FIRST_TALENT_SPELL}-{next_spell - 1} ({next_spell - FIRST_TALENT_SPELL}), "
          f"talents {len(talent_rows)}, spec abilities {len(spec_rows)}")
    print(f"wrote {OUT_SQL.relative_to(REPO)}, {OUT_H.relative_to(REPO)}, {OUT_MD.relative_to(REPO)}")


if __name__ == "__main__":
    main()
