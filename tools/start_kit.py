#!/usr/bin/env python3
"""Tasks 006 + 007: the Devourer's start -- base kit (Rush, Concentrate, Anima), trainers, eight starting forms.

    python tools/start_kit.py --spell-dbc <server>/data/dbc/Spell.dbc

One source for two outputs, keep them in step by running this script again after any change:
  data/sql/db-world/2026_09_30_08_devourer_start.sql   spells (spell_dbc; the client patch tool reads them from
                                                       here), form bindings, shapes, colourings, trainers
  docs/start-kit.md                                    what every spell does, ids, levels, costs

Spells are cloned from stock 3.3.5a spells (their visuals and icons) and overridden field by field with the
helpers of tools/coa/build_devourer_spells.py. The committed SQL holds only the finished rows, no Blizzard file.

Ids (all inside the Devourer's reserved spell range 9100000-9100999; 9100900+ so that 2026_09_30_02, which clears
9100000-9100899 when it runs again, never touches them):
  9100990-9100993   the base kit every Devourer has from level 1: Rush, Rush's hit, Concentrate, Anima (the
                    hidden passive that keeps Anima from draining away out of combat)
                    (9100900-9100909 were the true-form kit, parked in commit fdf67e9: the true form comes later)
  9100910-9100989   starting forms: shape s (5-12) uses 9100910 + (s - 5) * 10 + slot
                    slot 0 form, 1-2 abilities, 3 passive, 4-5 abilities that open at levels 10 and 20
  shapes 5-12, creatures 9101200-9101215 (trainers), spawns 9910101-9910116, trainer 9101200,
  gossip menu / npc_text 9101200-9101201
Removed by data/sql/uninstall/world.sql.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools" / "coa"))
import build_devourer_spells as b  # noqa: E402  (the spell DSL: effects(), aura(), hunger(), CLEAN, PASSIVE ...)
from build_devourer_spells import (  # noqa: E402
    CLEAN, PASSIVE, NO_MECHANICS, aura, effects, hunger,
    E_DUMMY, E_SCHOOL_DAMAGE, E_ENERGIZE, E_TRIGGER_SPELL, E_CHARGE, E_WEAPON_PERCENT_DAMAGE,
    A_DUMMY, A_PERIODIC_DAMAGE, A_TRANSFORM, A_DMG_TAKEN_PCT, A_OBS_MOD_HEALTH, A_MOD_RESISTANCE_PCT,
    A_MOD_ATTACK_POWER_PCT, A_MOD_DECREASE_SPEED, A_MOD_INCREASE_SPEED, A_MOD_MELEE_HASTE,
    T_CASTER, T_ENEMY, T_SRC_CASTER, T_SRC_AREA_ENEMY, POWER_RAGE,
    SCHOOL_PHYSICAL, SCHOOL_NATURE, SCHOOL_SHADOW, SCHOOL_ALL, SCHOOL_MAGIC_ALL,
    DUR_INFINITE, DUR_10S, DUR_20S, DUR_4S, DUR_9S,
    RADIUS_5, RADIUS_8, CAST_INSTANT, RANGE_SELF, RANGE_COMBAT, ATTR0_ABILITY,
    MECHANIC_BLEED, SHAPE_CATEGORY, SHIFT_COOLDOWN, FORM_PLACEHOLDER_ENTRY,
)

OUT_SQL = REPO / "data" / "sql" / "db-world" / "2026_09_30_08_devourer_start.sql"
OUT_MD = REPO / "docs" / "start-kit.md"
FIRST, LAST = 9100900, 9100999

# --- enums the DSL does not have yet ---------------------------------------------------------------------------
E_WEAPON_DAMAGE, E_THREAT = 58, 63
A_MOD_DODGE_PERCENT, A_MOD_CRIT_PERCENT, A_PERIODIC_LEECH, A_MOD_HIT_CHANCE = 49, 52, 53, 54
A_MOD_ATTACK_POWER, A_MOD_TOTAL_STAT_PERCENTAGE = 99, 137
SCHOOL_ARCANE = 64
STAT_STAMINA = 2
MECHANIC_SNARE = 11
DUR_15S, DUR_5S, DUR_6S = 8, 28, 32
CAST_1500 = 16
RANGE_30 = 4
GCD = {"StartRecoveryCategory": 133, "StartRecoveryTime": 1500}
# Attribute bits a template may carry that make no sense for a Devourer: "not while shapeshifted", "only in
# stealth", "needs combo points" (both kinds).
ATTR0_DROP = 0x00010000 | 0x00020000
ATTR1_DROP = 0x00100000 | 0x00400000
CHARGE_STUN = 7922                     # stock "Charge Stun": the knock-down after a charge
# The base kit (owner, 2026-09-30): Anima is the Devourer's resource (the rage bar, renamed); shifting costs it
# (the module: Devourer.AnimaPerShift), Concentrate gathers it, Rush needs no target.
RUSH, RUSH_HIT, CONCENTRATE, ANIMA = 9100990, 9100991, 9100992, 9100993
A_INTERRUPT_REGEN = 94                 # the core skips rage decay out of combat while a unit has it
DUR_1S, DMG_MELEE, A_MOD_STUN, MECHANIC_STUN = b.DUR_1S, b.DMG_MELEE, b.A_MOD_STUN, b.MECHANIC_STUN


def hit(amount, spread=0):
    """Weapon damage plus a flat amount, on the enemy."""
    return {"effect": E_WEAPON_DAMAGE, "amount": amount, "spread": spread, "target": T_ENEMY}


def gain(points):
    """Hunger for the caster (stored times ten)."""
    return {"effect": E_ENERGIZE, "amount": points * 10, "misc": POWER_RAGE, "target": T_CASTER}


def around(kind, amount=0, misc=0, radius=RADIUS_8, **kw):
    """An aura on every enemy around the caster."""
    return aura(kind, amount, misc, target=T_SRC_CASTER, targetB=T_SRC_AREA_ENEMY, radius=radius, **kw)


def ability(fields: dict) -> dict:
    """An instant, on the global cooldown, no class family: `fields` override."""
    return {**CLEAN, **NO_MECHANICS, "CastingTimeIndex": CAST_INSTANT, **GCD, **fields}


def passive(kind, amount, misc=0, icon=0):
    return {**CLEAN, **PASSIVE, **NO_MECHANICS, "SpellIconID": icon, **effects(aura(kind, amount, misc))}


def placeholder(level, icon):
    """A castable dummy: opens at `level`, does nothing yet."""
    return (20578, {**CLEAN, **NO_MECHANICS, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
                    "CastingTimeIndex": CAST_INSTANT, "DurationIndex": 0, "RangeIndex": RANGE_SELF,
                    "InterruptFlags": 0, "ChannelInterruptFlags": 0, "RecoveryTime": 6000, **GCD,
                    "SpellVisualID_1": 0, "SpellIconID": icon, "SpellLevel": level, "BaseLevel": level,
                    **effects({"effect": E_DUMMY})})


# --- the base kit: every Devourer from level 1 -------------------------------------------------------------------
# (id, level, trainer cost in copper or None = not on the trainer, template, overrides, (name, description, aura))
BASE = [
    (RUSH, 1, 0, 100, {                                              # Charge: its icon; the module does the run
        **CLEAN, **NO_MECHANICS, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "AttributesEx3": 0, "Targets": 0, "FacingCasterFlags": 0, "ExcludeCasterAuraState": 0,
        "CastingTimeIndex": 3, "DurationIndex": 0, "RangeIndex": RANGE_SELF, "Speed": 0.0, "InterruptFlags": 0x0F,
        "ChannelInterruptFlags": 0, "AuraInterruptFlags": 0, "RecoveryTime": 15000, **GCD,
        "SpellVisualID_1": 0, **effects({"effect": E_DUMMY})},
     ("Rush", "Gather yourself for 0.5 sec, then rush 20 yards straight ahead. Every enemy in your path takes 50% "
      "weapon damage and is knocked down for 1 sec. Needs no target.", "")),
    (RUSH_HIT, 1, None, CHARGE_STUN, {                               # the knock-down, like Overrun's
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "SchoolMask": SCHOOL_PHYSICAL, "DefenseType": DMG_MELEE,
        "PreventionType": 2, "DurationIndex": DUR_1S, "Mechanic": MECHANIC_STUN, "RangeIndex": 13,
        **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 50, "target": T_ENEMY},
                  aura(A_MOD_STUN, target=T_ENEMY))},
     ("Rush", "", "Knocked down.")),
    (CONCENTRATE, 1, 0, 2687, {                                      # Bloodrage: the surge of power
        **CLEAN, **NO_MECHANICS, "Targets": 0, "CastingTimeIndex": CAST_INSTANT, "DurationIndex": 0,
        "RangeIndex": RANGE_SELF, "RecoveryTime": 30000, **effects(gain(30))},
     ("Concentrate", "Draw the anima scattered through your body together: gain 30 Anima. Usable in combat.", "")),
    (ANIMA, 1, None, 25941, {
        **CLEAN, **PASSIVE, **NO_MECHANICS, "Attributes": ATTR0_ABILITY | b.ATTR0_PASSIVE | b.ATTR0_HIDDEN,
        **effects(aura(A_INTERRUPT_REGEN))},
     ("Anima", "Your anima does not drain away while you rest.", "")),
]


# --- task 007: the eight starting forms ----------------------------------------------------------------------------
class Form:
    def __init__(self, shape, name, zone, source, display, icon, colourings, diet, skin, one, two, passive_,
                 later):
        self.shape, self.name, self.zone, self.source, self.display, self.icon = shape, name, zone, source, display, icon
        self.colourings = colourings          # [(creature entry, display, skin name)]
        self.diet = diet                      # [(creature type, bp)]
        self.skin = skin                      # the base look's name for .devour skin
        self.one, self.two, self.passive, self.later = one, two, passive_, later
        self.base = FIRST + 10 + (shape - 5) * 10


FORMS = [
    Form(5, "Wolf", "Northshire", 299, 31049, 1573, [(69, 31048, "Timber"), (1508, 447, "Scavenger")],
         [(1, 10), (0, 3)], "Grey",
         (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                         **effects(hit(4), gain(5))}),
          ("Savage Bite", "Bite the enemy: weapon damage plus $s1. Generates 5 Anima.", "")),
         (24604, ability({**hunger(10), "RangeIndex": RANGE_SELF, "DurationIndex": DUR_20S, "RecoveryTime": 30000,
                         **effects(aura(A_MOD_MELEE_HASTE, 10))}),
          ("Pack Howl", "Howl like the pack before the kill: attack speed increased by 10% for 20 sec.",
           "Attack speed increased by 10%.")),
         (A_MOD_CRIT_PERCENT, 2, 0, ("Pack Instinct", "Your critical strike chance is increased by 2%.", "")),
         ("Rip Throat", "Call of the Pack")),
    Form(6, "Trogg", "Coldridge Valley", 707, 606, 93, [], [(7, 10), (0, 3)], "Rockjaw",
         (6552, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                        **effects(hit(5), gain(5))}),
          ("Stone Fist", "Hammer the enemy with a fist of stone: weapon damage plus $s1. Generates 5 Anima.", "")),
         (20594, ability({**hunger(10), "RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S, "RecoveryTime": 30000,
                         **effects(aura(A_DMG_TAKEN_PCT, -10, SCHOOL_ALL))}),
          ("Stoneskin", "Your hide turns to stone: damage taken reduced by 10% for 10 sec.", "Damage taken reduced by 10%.")),
         (A_MOD_RESISTANCE_PCT, 10, 1, ("Thick Skull", "Your armor is increased by 10%.", "")),
         ("Rock Hurl", "Tunnel Rage")),
    Form(7, "Nightsaber", "Shadowglen", 2031, 11454, 103, [(15366, 15507, "Springpaw"), (15372, 15506, "Lynx")],
         [(1, 10), (0, 3)], "Nightsaber",
         (1822, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                        "DurationIndex": DUR_9S, "Mechanic": MECHANIC_BLEED, "EffectMechanic_2": MECHANIC_BLEED,
                        **effects({"effect": E_SCHOOL_DAMAGE, "amount": 3, "target": T_ENEMY},
                                  aura(A_PERIODIC_DAMAGE, 2, target=T_ENEMY, period=3000), gain(5))}),
          ("Rake", "Rake the enemy for $s1 damage; it bleeds for $o2 over 9 sec. Generates 5 Anima.",
           "Bleeding for $s2 every 3 sec.")),
         (5215, {**CLEAN, "RecoveryTime": 10000, **GCD},             # Prowl keeps its own effects and rules
          ("Prowl", "Slip into the shadows, unseen but slower. Cannot be used in combat.", "Stealthed.")),
         (A_MOD_ATTACK_POWER_PCT, 5, 0, ("Hunter's Poise", "Your attack power is increased by 5%.", "")),
         ("Ambush Leap", "Shadow Stalk")),
    Form(8, "Moth", "Ammen Vale", 16520, 17574, 109, [], [(1, 10), (0, 3)], "Vale",
         (1449, ability({"Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "RecoveryTime": 6000,
                        "SchoolMask": SCHOOL_NATURE,
                        **effects({"effect": E_SCHOOL_DAMAGE, "amount": 5, "spread": 2, "target": T_SRC_CASTER,
                                   "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_5}, gain(5))}),
          ("Dusty Wings", "Beat your wings: $s1 Nature damage to enemies within 5 yards. Generates 5 Anima.", "")),
         (770, ability({**hunger(10), "RangeIndex": RANGE_30, "DurationIndex": DUR_10S, "RecoveryTime": 10000,
                       "SchoolMask": SCHOOL_NATURE, **effects(aura(A_MOD_HIT_CHANCE, -10, target=T_ENEMY))}),
          ("Blinding Dust", "Throw wing dust into the enemy's eyes: its chance to hit is reduced by 10% for 10 sec.",
           "Chance to hit reduced by 10%.")),
         (A_MOD_DODGE_PERCENT, 3, 0, ("Fluttering", "Your chance to dodge is increased by 3%.", "")),
         ("Luring Glow", "Silken Cocoon")),
    Form(9, "Boar", "Valley of Trials", 3098, 503, 1578, [(1984, 8869, "Thistle"), (113, 0, "")],
         [(1, 10), (0, 3)], "Mottled",
         (35290, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                         **effects(hit(5), gain(5))}),
          ("Gore", "Gore the enemy with your tusks: weapon damage plus $s1. Generates 5 Anima.", "")),
         (100, {**CLEAN, **NO_MECHANICS, "RecoveryTime": 15000, **GCD,
                **effects({"effect": E_CHARGE, "target": T_ENEMY}, gain(10),
                          {"effect": E_TRIGGER_SPELL, "target": T_ENEMY, "trigger": CHARGE_STUN})},
          ("Boar Charge", "Charge an enemy 8 to 25 yards away and knock it down. Generates 10 Anima. "
           "Cannot be used in combat.", "")),
         (A_MOD_TOTAL_STAT_PERCENTAGE, 5, STAT_STAMINA, ("Bristling Hide", "Your stamina is increased by 5%.", "")),
         ("Tusk Toss", "Wallow")),
    Form(10, "Plainstrider", "Camp Narache", 2955, 1219, 516, [(2956, 1220, "Tallstrider")], [(1, 10), (0, 3)],
         "Plainstrider",
         (1766, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 8000, "SchoolMask": SCHOOL_PHYSICAL,
                        "DurationIndex": DUR_4S, "EffectMechanic_2": MECHANIC_SNARE,
                        **effects(hit(4), aura(A_MOD_DECREASE_SPEED, -30, target=T_ENEMY), gain(5))}),
          ("Hind Kick", "Kick back hard: weapon damage plus $s1, and the enemy is slowed by 30% for 4 sec. "
           "Generates 5 Anima.", "Movement slowed by 30%.")),
         (2983, ability({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_15S, "RecoveryTime": 60000,
                        **effects(aura(A_MOD_INCREASE_SPEED, 40))}),
          ("Long Stride", "Run on long legs: movement speed increased by 40% for 15 sec.", "Movement speed increased by 40%.")),
         (A_MOD_INCREASE_SPEED, 8, 0, ("Long Legs", "Your movement speed is increased by 8%.", "")),
         ("Peck", "Stampede")),
    Form(11, "Bat", "Deathknell", 1512, 4732, 1579, [], [(1, 10), (6, 10), (0, 3)], "Duskbat",
         (24423, ability({"Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S,
                         "RecoveryTime": 8000, "SchoolMask": SCHOOL_NATURE,
                         **effects({"effect": E_SCHOOL_DAMAGE, "amount": 4, "spread": 2, "target": T_SRC_CASTER,
                                    "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8},
                                   around(A_MOD_ATTACK_POWER, -10), gain(5))}),
          ("Screech", "A piercing screech: $s1 Nature damage to enemies within 8 yards, and their attack power is "
           "reduced by 10 for 10 sec. Generates 5 Anima.", "Attack power reduced by 10.")),
         (689, ability({**hunger(10), "RangeIndex": RANGE_30, "RecoveryTime": 10000, "SchoolMask": SCHOOL_SHADOW,
                       "Attributes": 0x10000 & 0, **effects(aura(A_PERIODIC_LEECH, 3, target=T_ENEMY, period=1000)),
                       "EffectMultipleValue_1": 1.0, "StartRecoveryCategory": 133, "StartRecoveryTime": 1500}),
          ("Blood Drain", "Drink the enemy's blood: $s1 Shadow damage every second for 5 sec, healing you for the same.",
           "Losing $s1 health every second.")),
         (A_MOD_HIT_CHANCE, 2, 0, ("Echolocation", "Your chance to hit is increased by 2%.", "")),
         ("Sonic Burst", "Night Swarm")),
    Form(12, "Mana Wyrm", "Sunstrider Isle", 15274, 16217, 1485, [], [(1, 10), (4, 10), (0, 3)], "Wyrm",
         (13901, ability({"Attributes": 0, "CastingTimeIndex": CAST_1500, "RangeIndex": RANGE_30, "RecoveryTime": 0,
                         "SchoolMask": SCHOOL_ARCANE,
                         **effects({"effect": E_SCHOOL_DAMAGE, "amount": 7, "spread": 3, "target": T_ENEMY}, gain(5))}),
          ("Arcane Bolt", "Spit a bolt of raw arcane: $s1 Arcane damage. Generates 5 Anima.", "")),
         (1449, ability({"Attributes": ATTR0_ABILITY, **hunger(10), "RangeIndex": RANGE_SELF, "RecoveryTime": 8000,
                        "SchoolMask": SCHOOL_ARCANE,
                        **effects({"effect": E_SCHOOL_DAMAGE, "amount": 8, "spread": 4, "target": T_SRC_CASTER,
                                   "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8})}),
          ("Arcane Pulse", "Release the mana in you: $s1 Arcane damage to enemies within 8 yards.", "")),
         (A_DMG_TAKEN_PCT, -3, SCHOOL_MAGIC_ALL, ("Mana Sheath", "Magic damage taken reduced by 3%.", "")),
         ("Mana Tap", "Arcane Coil")),
]


def form_spells(f: Form):
    """(id, level, template, overrides, texts) for one form: form, 2 abilities, passive, 2 later abilities."""
    one_t, one_o, one_x = f.one
    two_t, two_o, two_x = f.two
    p_kind, p_amount, p_misc, p_x = f.passive
    later = [(f.base + 4, 10, f.later[0]), (f.base + 5, 20, f.later[1])]
    out = [
        (f.base, 1, 16591, {
            **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
            "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
            "Category": SHAPE_CATEGORY, "RecoveryTime": 0, "CategoryRecoveryTime": SHIFT_COOLDOWN,
            "StartRecoveryCategory": 133, "StartRecoveryTime": 1000, "InterruptFlags": 0, "AuraInterruptFlags": 0,
            "SpellIconID": f.icon, **effects(aura(A_TRANSFORM, 0, FORM_PLACEHOLDER_ENTRY))},
         (f"{f.name} Form", f"Take the shape of the {f.name.lower()} you devoured: {one_x[0]}, {two_x[0]} and "
          f"{p_x[0]}; {later[0][2]} opens at level 10, {later[1][2]} at 20. All shapes share one cooldown.",
          f"Wearing the {f.name.lower()}'s shape.")),
        (f.base + 1, 1, one_t, one_o, one_x),
        (f.base + 2, 1, two_t, two_o, two_x),
        (f.base + 3, 1, 25941, passive(p_kind, p_amount, p_misc, f.icon), p_x),
    ]
    for sid, level, name in later:
        t, o = placeholder(level, f.icon)
        out.append((sid, level, t, o, (f"{name} (placeholder)",
                                       f"Placeholder {f.name} ability (level {level}): not designed yet.", "")))
    return out


# --- trainers (task 006) ----------------------------------------------------------------------------------------
TRAINER = 9101200
MENU = 9101200
TEXT_DEVOURER, TEXT_OTHER = 9101200, 9101201
# (entry, spawn guid, name, stands next to (creature entry), looks like (creature entry), where)
TRAINERS = [
    (9101200, 9910101, "Aldric Vane", 911, 918, "Northshire"),
    (9101201, 9910102, "Corwin Gloam", 914, 915, "Stormwind"),
    (9101202, 9910103, "Thorvik Gnashbeard", 912, 5166, "Coldridge Valley"),
    (9101203, 9910104, "Brunn Deepmaw", 1901, 916, "Ironforge"),
    (9101204, 9910105, "Ilyssa Moonhunger", 3593, 4163, "Shadowglen"),
    (9101205, 9910106, "Faelan Nightmaw", 4087, 3594, "Darnassus"),
    (9101206, 9910107, "Oronaar", 16503, 16771, "Ammen Vale"),
    (9101207, 9910108, "Vesheel", 17120, 16503, "The Exodar"),
    (9101208, 9910109, "Grak", 3153, 3327, "Valley of Trials"),
    (9101209, 9910110, "Throg Bloodjaw", 3353, 3155, "Orgrimmar"),
    (9101210, 9910111, "Mahka Hollowhorn", 3059, 3034, "Camp Narache"),
    (9101211, 9910112, "Tarn Hungerhoof", 3043, 3060, "Thunder Bluff"),
    (9101212, 9910113, "Agatha Crane", 2119, 4582, "Deathknell"),
    (9101213, 9910114, "Silas Marrow", 4593, 2122, "Undercity"),
    (9101214, 9910115, "Lyriel Sunhunger", 15285, 16685, "Sunstrider Isle"),
    (9101215, 9910116, "Caelis Emberthirst", 16684, 15285, "Silvermoon City"),
]
BESIDE = 2.5            # yards to the right of the class trainer it stands next to


def q(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


def spell_rows(dbc, defs):
    rows = []
    for sid, level, template, overrides, (name, desc, tip) in defs:
        assert FIRST <= sid <= LAST, sid
        row = dbc.row(template)
        row[b.COL["ID"]] = sid
        for key, value in overrides.items():
            row[b.COL[key]] = b.to_u32(value, b.COL[key])
        if "Attributes" not in overrides:
            row[b.COL["Attributes"]] &= ~ATTR0_DROP
        if "AttributesEx" not in overrides:
            row[b.COL["AttributesEx"]] &= ~ATTR1_DROP
        if "SpellLevel" not in overrides:
            row[b.COL["SpellLevel"]] = row[b.COL["BaseLevel"]] = level
        texts = {"Name_Lang_enUS": name, "Description_Lang_enUS": desc, "AuraDescription_Lang_enUS": tip,
                 "NameSubtext_Lang_enUS": ""}
        for g in b.STRING_GROUPS:
            row[b.COL[f"{g}_Mask"]] = 0x00FF01FE
        rows.append("(" + ",".join(b.sql_value(row[i], i, texts.get(b.COLUMNS[i])) for i in range(234)) + ")")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--spell-dbc", required=True, type=Path, help="a stock 3.3.5a Spell.dbc (lends template rows)")
    a = ap.parse_args()
    dbc = b.Dbc(a.spell_dbc)

    true_defs = [(sid, lvl, t, o, x) for sid, lvl, cost, t, o, x in BASE]
    form_defs = [d for f in FORMS for d in form_spells(f)]
    ids = [d[0] for d in true_defs + form_defs]
    assert len(ids) == len(set(ids)), "duplicate spell id"
    rows = spell_rows(dbc, true_defs + form_defs)
    forms = [f.base for f in FORMS]

    sql = [
        "-- Generated by tools/start_kit.py (tasks 006 + 007). Do not edit by hand: change the script and run it again.",
        "-- The Devourer's start: true-form kit, Devourer Trainers, eight starting forms. Safe to run again;",
        "-- removed by uninstall/world.sql.",
        "",
        f"DELETE FROM `spell_dbc` WHERE `ID` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_dbc` (" + ",".join(f"`{c}`" for c in b.COLUMNS) + ") VALUES",
        ",\n".join(rows) + ";",
        "",
        "-- Form spells: the module puts the body on and hands out the kit; never saved with the character.",
        f"DELETE FROM `spell_script_names` WHERE `spell_id` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES",
        ",\n".join([f"({s}, 'spell_devourer_form')" for s in forms]
                   + [f"({RUSH}, 'spell_devourer_rush')"]) + ";",
        f"DELETE FROM `spell_custom_attr` WHERE `spell_id` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_custom_attr` (`spell_id`, `attributes`) VALUES",
        ",\n".join(f"({s}, 0x01000000)" for s in forms) + ";",
        "",
        "-- Shapes 5-12: one per starting zone. spell_3 and spell_4 open at levels 10 and 20 (their spell level).",
        "DELETE FROM `devourer_shape` WHERE `shape_id` BETWEEN 5 AND 12;",
        "INSERT INTO `devourer_shape` (`shape_id`, `name`, `form_spell`, `display_id`, `scale`, `spell_1`, `spell_2`,"
        " `spell_3`, `spell_4`, `passive`, `brood_display`) VALUES",
        ",\n".join(f"({f.shape}, {q(f.name)}, {f.base}, {f.display}, 1, {f.base + 1}, {f.base + 2}, {f.base + 4},"
                   f" {f.base + 5}, {f.base + 3}, {f.display})" for f in FORMS) + ";",
        "",
        "-- Who gives them: the zone's creature the base look, its kin elsewhere a colouring (0 = the base look).",
        "DELETE FROM `devourer_shape_source` WHERE `shape_id` BETWEEN 5 AND 12;",
        "INSERT INTO `devourer_shape_source` (`creature_entry`, `shape_id`, `display_id`) VALUES",
        ",\n".join([f"({f.source}, {f.shape}, 0)" for f in FORMS]
                   + [f"({e}, {f.shape}, {d})" for f in FORMS for e, d, _ in f.colourings]) + ";",
        "DELETE FROM `devourer_skin` WHERE `shape_id` BETWEEN 5 AND 12;",
        "INSERT INTO `devourer_skin` (`display_id`, `shape_id`, `name`, `brood_display`) VALUES",
        ",\n".join([f"({f.display}, {f.shape}, {q(f.skin)}, 0)" for f in FORMS]
                   + [f"({d}, {f.shape}, {q(n)}, {d})" for f in FORMS for _, d, n in f.colourings if d]) + ";",
        "DELETE FROM `devourer_diet` WHERE `shape_id` BETWEEN 5 AND 12;",
        "INSERT INTO `devourer_diet` (`shape_id`, `creature_type`, `bp`) VALUES",
        ",\n".join(f"({f.shape}, {t}, {bp})" for f in FORMS for t, bp in f.diet) + ";",
        "",
        "-- --- Devourer Trainers --------------------------------------------------------------------------------",
        "-- The class trainer (class 10) and what it teaches.",
        f"DELETE FROM `trainer` WHERE `Id` = {TRAINER};",
        "INSERT INTO `trainer` (`Id`, `Type`, `Requirement`, `Greeting`, `VerifiedBuild`) VALUES",
        f"({TRAINER}, 0, 10, 'Hungry again? Then learn to eat better.', 0);",
        f"DELETE FROM `trainer_spell` WHERE `TrainerId` = {TRAINER};",
        "INSERT INTO `trainer_spell` (`TrainerId`, `SpellId`, `MoneyCost`, `ReqSkillLine`, `ReqSkillRank`,"
        " `ReqAbility1`, `ReqAbility2`, `ReqAbility3`, `ReqLevel`, `VerifiedBuild`) VALUES",
        ",\n".join(f"({TRAINER}, {sid}, {cost}, 0, 0, 0, 0, 0, {lvl}, 0)" for sid, lvl, cost, *_ in BASE
                   if cost is not None) + ";",
        "",
        "-- What they say, and \"I require training\" only for a Devourer (class mask 512); others are sent away.",
        f"DELETE FROM `npc_text` WHERE `ID` IN ({TEXT_DEVOURER}, {TEXT_OTHER});",
        "INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES",
        f"({TEXT_DEVOURER}, 'You smell of the hunt and of the feast. Good. There is more to hunger than chewing.',"
        " 'You smell of the hunt and of the feast. Good. There is more to hunger than chewing.', 1),",
        f"({TEXT_OTHER}, 'Keep walking. What I teach would only sicken you.',"
        " 'Keep walking. What I teach would only sicken you.', 1);",
        f"DELETE FROM `gossip_menu` WHERE `MenuID` = {MENU};",
        "INSERT INTO `gossip_menu` (`MenuID`, `TextID`) VALUES",
        f"({MENU}, {TEXT_DEVOURER}), ({MENU}, {TEXT_OTHER});",
        f"DELETE FROM `gossip_menu_option` WHERE `MenuID` = {MENU};",
        "INSERT INTO `gossip_menu_option` (`MenuID`, `OptionID`, `OptionIcon`, `OptionText`, `OptionBroadcastTextID`,"
        " `OptionType`, `OptionNpcFlag`, `ActionMenuID`, `ActionPoiID`, `BoxCoded`, `BoxMoney`, `BoxText`,"
        " `BoxBroadcastTextID`, `VerifiedBuild`) VALUES",
        f"({MENU}, 0, 3, 'I require training.', 0, 5, 16, 0, 0, 0, 0, '', 0, 0),",
        f"({MENU}, 1, 0, 'I wish to unlearn my talents.', 62295, 16, 16, 4461, 0, 0, 0, '', 0, 0),",
        f"({MENU}, 2, 0, 'I wish to know about Dual Talent Specialization.', 33762, 20, 1, 10371, 0, 0, 0, '', 0, 0);",
        f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` IN (14, 15) AND `SourceGroup` = {MENU};",
        "INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`,"
        " `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`,"
        " `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES",
        f"(14, {MENU}, {TEXT_DEVOURER}, 0, 0, 15, 0, 512, 0, 0, 0, 0, 0, '', 'Devourer Trainer: text for a Devourer'),",
        f"(14, {MENU}, {TEXT_OTHER}, 0, 0, 15, 0, 512, 0, 0, 1, 0, 0, '', 'Devourer Trainer: text for everyone else'),",
        f"(15, {MENU}, 0, 0, 0, 15, 0, 512, 0, 0, 0, 0, 0, '', 'Devourer Trainer: training only for a Devourer'),",
        f"(15, {MENU}, 1, 0, 0, 15, 0, 512, 0, 0, 0, 0, 0, '', 'Devourer Trainer: unlearn talents only for a Devourer'),",
        f"(15, {MENU}, 2, 0, 0, 15, 0, 512, 0, 0, 0, 0, 0, '', 'Devourer Trainer: dual spec only for a Devourer');",
        "",
        "-- The NPCs: each a copy of the class trainer it stands beside (faction, level, flags), made at install time",
        "-- from this database, so no creature data is written into this file. Its look is another trainer's of the",
        "-- same people.",
        "DROP TEMPORARY TABLE IF EXISTS `devourer_trainer_map`;",
        "CREATE TEMPORARY TABLE `devourer_trainer_map` (`entry` INT UNSIGNED PRIMARY KEY, `guid` INT UNSIGNED,"
        " `name` VARCHAR(100), `beside` INT UNSIGNED, `looks` INT UNSIGNED);",
        "INSERT INTO `devourer_trainer_map` VALUES",
        ",\n".join(f"({e}, {g}, {q(n)}, {bs}, {lk})" for e, g, n, bs, lk, _ in TRAINERS) + ";",
        "",
        f"DELETE FROM `creature` WHERE `guid` BETWEEN {TRAINERS[0][1]} AND {TRAINERS[-1][1]};",
        f"DELETE FROM `creature_default_trainer` WHERE `CreatureId` BETWEEN {TRAINERS[0][0]} AND {TRAINERS[-1][0]};",
        f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {TRAINERS[0][0]} AND {TRAINERS[-1][0]};",
        f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {TRAINERS[0][0]} AND {TRAINERS[-1][0]};",
        "DROP TEMPORARY TABLE IF EXISTS `devourer_trainer_ct`;",
        "CREATE TEMPORARY TABLE `devourer_trainer_ct` AS SELECT `ct`.* FROM `creature_template` AS `ct`"
        " JOIN `devourer_trainer_map` AS `m` ON `m`.`beside` = `ct`.`entry`;",
        "UPDATE `devourer_trainer_ct` AS `ct` JOIN `devourer_trainer_map` AS `m` ON `m`.`beside` = `ct`.`entry`"
        f" SET `ct`.`entry` = `m`.`entry`, `ct`.`name` = `m`.`name`, `ct`.`subname` = 'Devourer Trainer',"
        f" `ct`.`gossip_menu_id` = {MENU}, `ct`.`npcflag` = 49, `ct`.`AIName` = '', `ct`.`ScriptName` = '',"
        " `ct`.`lootid` = 0, `ct`.`VerifiedBuild` = 0;",
        "INSERT INTO `creature_template` SELECT * FROM `devourer_trainer_ct`;",
        "DROP TEMPORARY TABLE `devourer_trainer_ct`;",
        "",
        "INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`,"
        " `VerifiedBuild`)",
        "SELECT `m`.`entry`, 0, `ctm`.`CreatureDisplayID`, `ctm`.`DisplayScale`, 1, 0 FROM `devourer_trainer_map` AS `m`",
        "JOIN `creature_template_model` AS `ctm` ON `ctm`.`CreatureID` = `m`.`looks` AND `ctm`.`Idx` = 0;",
        "",
        "INSERT INTO `creature_default_trainer` (`CreatureId`, `TrainerId`)",
        f"SELECT `entry`, {TRAINER} FROM `devourer_trainer_map`;",
        "",
        f"-- Spawned {BESIDE} yards to the right of the class trainer, facing the same way.",
        "INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `equipment_id`,"
        " `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`,"
        " `currentwaypoint`, `curhealth`, `curmana`, `MovementType`, `npcflag`, `unit_flags`, `dynamicflags`,"
        " `ScriptName`, `VerifiedBuild`, `CreateObject`, `Comment`)",
        "SELECT `m`.`guid`, `m`.`entry`, `c`.`map`, `c`.`zoneId`, `c`.`areaId`, `c`.`spawnMask`, `c`.`phaseMask`, 0,",
        f"    `c`.`position_x` + {BESIDE} * COS(`c`.`orientation` - PI() / 2),"
        f" `c`.`position_y` + {BESIDE} * SIN(`c`.`orientation` - PI() / 2),",
        "    `c`.`position_z`, `c`.`orientation`, 300, 0, 0, `c`.`curhealth`, `c`.`curmana`, 0, 0, 0, 0, '', 0, 0,",
        "    'mod-devourer: Devourer Trainer'",
        "FROM `devourer_trainer_map` AS `m`",
        "JOIN `creature` AS `c` ON `c`.`guid` = (SELECT MIN(`c2`.`guid`) FROM `creature` AS `c2` WHERE `c2`.`id` = `m`.`beside`);",
        "DROP TEMPORARY TABLE `devourer_trainer_map`;",
        "",
    ]
    OUT_SQL.write_text("\n".join(sql), encoding="utf-8")

    md = ["# The Devourer's start: kit, trainers, starting forms",
          "",
          "Generated by `tools/start_kit.py` (tasks 006 + 007) — edit the script, not this file. Design: "
          "`docs/starting-experience.md`. Numbers are a first pass for levels 1-20.",
          "",
          f"Spell ids {FIRST}-{LAST}: base kit 9100990-9100993, starting forms 9100910-9100989 "
          "(shape s: 9100910 + (s-5)*10 + slot; slot 0 form, 1-2 abilities, 3 passive, 4-5 open at 10 and 20).",
          "",
          "## Base kit (every Devourer from level 1; the trainers list it too)",
          "",
          "| Level | Spell | Name | Cost | What it does |",
          "|---|---|---|---|---|"]
    for sid, lvl, cost, t, o, (name, desc, _) in BASE:
        md.append(f"| {lvl} | {sid} | {name} | {'-' if cost is None else f'{cost // 100}s {cost % 100}c'} | {desc} |")
    md += ["", "Known from creation; bars: Attack, Rush, Concentrate, Devour. Shifting into a shape costs Anima "
           "(Devourer.AnimaPerShift, default 25).", "",
           "## Trainers", "", "| Entry | Name | Where | Stands beside | Looks like |", "|---|---|---|---|---|"]
    for e, g, n, bs, lk, where in TRAINERS:
        md.append(f"| {e} | {n} | {where} | creature {bs} | creature {lk} |")
    md += ["", "## Starting forms", ""]
    for f in FORMS:
        md.append(f"### {f.name} (shape {f.shape}, {f.zone})")
        md.append(f"Devour **{f.source}** for the base look ({f.display}, skin `{f.skin}`)"
                  + ("; colourings: " + ", ".join(f"{e} → {d or 'base look'}" + (f" (`{n}`)" if n else "")
                                                  for e, d, n in f.colourings) if f.colourings else "") + ".")
        md.append("")
        md.append("| Spell | Level | Name | What it does |")
        md.append("|---|---|---|---|")
        for sid, lvl, t, o, (name, desc, _) in form_spells(f):
            md.append(f"| {sid} | {lvl} | {name} | {desc} |")
        md.append("")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"{len(rows)} spells ({min(ids)}-{max(ids)}), {len(FORMS)} forms, {len(TRAINERS)} trainers")
    print(f"wrote {OUT_SQL.relative_to(REPO)}, {OUT_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
