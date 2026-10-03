#!/usr/bin/env python3
"""Task 017: the evolved forms, tier 2 of the owner's canvas lines ("Canvas Evolutions for Devourer", Section 1).

    python tools/evolved_kit.py --spell-dbc <server>/data/dbc/Spell.dbc

One source for two outputs, keep them in step by running this script again after any change:
  data/sql/db-world/2026_10_03_00_devourer_tier2.sql   spells (spell_dbc; the client patch tool reads them from here),
                                                       script bindings, procs, shapes 16-24, colourings, diet,
                                                       favourite food, the evolutions and their tasks
  docs/tier2-kit.md                                    what every spell does, ids, levels, and the changes against
                                                       the canvas cards

Batch 1 (owner, 2026-10-03: "evolutions for the already implemented ones"): one tier-2 form per beast line, the
canvas "A" branch, plus the Warp Stalker's. They are not devoured: they grow out of their line's form
(`devourer_evolution`, Bio Points + level + any one of three tasks, the canvas rule).

Ids: spells 9102000-9102999 (the old range 9100000-9101099 is full): shape s (16+) uses 9102000 + (s - 16) * 10 + slot;
slot 0 form, 1-2 abilities, 3 passive (the card's gimmick), 4 ability, 5 ability that opens at level 20, 6-9 helper
spells the kit casts. Like tools/start_kit.py, spells are cloned from stock 3.3.5a spells (visuals, icons) and
overridden field by field; the committed SQL holds only the finished rows, no Blizzard file.
Removed by data/sql/uninstall/world.sql.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import start_kit as sk  # noqa: E402  (the starting forms: their helpers and enums)
from start_kit import (  # noqa: E402
    b, CLEAN, PASSIVE, NO_MECHANICS, aura, effects, hunger, ability, hit, gain, around, helper, proc_passive, q,
    E_DUMMY, E_SCHOOL_DAMAGE, E_ENERGIZE, E_TRIGGER_SPELL, E_CHARGE, E_WEAPON_PERCENT_DAMAGE, E_HEALTH_LEECH, E_HEAL_PCT,
    E_PULL_TOWARDS,
    A_DUMMY, A_PERIODIC_DAMAGE, A_DMG_TAKEN_PCT, A_OBS_MOD_HEALTH, A_MOD_RESISTANCE_PCT, A_MOD_DECREASE_SPEED,
    A_MOD_INCREASE_SPEED, A_MOD_MELEE_HASTE, A_MOD_STUN, A_MOD_HIT_CHANCE, A_MOD_DODGE_PERCENT, A_PROC_TRIGGER_SPELL,
    A_SCHOOL_ABSORB, A_MOD_DAMAGE_PCT_DONE, A_MOD_STEALTH,
    T_CASTER, T_ENEMY, T_SRC_CASTER, T_SRC_AREA_ENEMY,
    SCHOOL_PHYSICAL, SCHOOL_NATURE, SCHOOL_SHADOW, SCHOOL_ARCANE, SCHOOL_ALL, SCHOOL_MAGIC_ALL,
    DUR_INFINITE, DUR_1S, DUR_2S, DUR_3S, DUR_4S, DUR_5S, DUR_6S, DUR_10S, DUR_12S, DUR_15S,
    RADIUS_5, RADIUS_6, RADIUS_8, RADIUS_20, CAST_INSTANT, CAST_1500, RANGE_SELF, RANGE_COMBAT, RANGE_20, RANGE_25,
    RANGE_30, RANGE_ANYWHERE, RANGE_5_15, ATTR0_ABILITY, ATTR0_CANT_CANCEL, ATTR0_DROP, ATTR1_DROP,
    MECHANIC_BLEED, MECHANIC_SNARE, MECHANIC_STUN, SHAPE_CATEGORY, SHIFT_COOLDOWN, FORM_PLACEHOLDER_ENTRY,
    PROC_DONE_MELEE, PROC_TAKEN_MELEE, PROC_DONE_SPELL_MELEE, PROC_TAKEN_SPELL_MELEE, PROC_DONE_SPELL_MAGIC,
    HIT_DODGE, CHARGE_STUN, GCD, DMG_MAGIC,
    CREATURE_TYPE_BEAST, CREATURE_TYPE_ELEMENTAL, CREATURE_TYPE_CRITTER,
    FAMILY_SPIDER, FAMILY_BOAR, FAMILY_CROCOLISK, FAMILY_SCORPID, FAMILY_CAT,
)

OUT_SQL = REPO / "data" / "sql" / "db-world" / "2026_10_03_00_devourer_tier2.sql"
OUT_MD = REPO / "docs" / "tier2-kit.md"
FIRST, LAST = 9102000, 9102999
FIRST_SHAPE = 16
MOLT_QUEST_FIRST = 9101310               # task 018: the molt quests (tools/witch_sisters.py), one per form, in order

# --- enums the other tools do not have yet ------------------------------------------------------------------------
E_INTERRUPT_CAST, E_KNOCK_BACK = 68, 98
A_DAMAGE_SHIELD, A_MOD_ROOT, A_MOD_FEAR, A_MOD_SILENCE = 15, 26, 7, 27
MECHANIC_FEAR, MECHANIC_ROOT, MECHANIC_SILENCE, MECHANIC_SLEEP, MECHANIC_KNOCKOUT = 5, 7, 9, 10, 14
SCHOOL_NATURE_INDEX = 3                  # damage shields take the school index, not the mask
DUR_1500 = 65                            # 1.5 sec (the stock Charge Stun's)
DUR_8S = 31
RANGE_15 = 11
RADIUS_12 = 32
T_DEST_TARGET_ANY, T_DEST_AREA_ENEMY = 53, 16
AURA_INTERRUPT_DAMAGE = 0x2              # breaks when the victim takes damage (gouge, sleep)
PROC_HIT_CRIT = 0x2
CREATURE_TYPE_DEMON, CREATURE_TYPE_UNDEAD, CREATURE_TYPE_HUMANOID = 3, 6, 7
FAMILY_BEAR = 4
SKILL_TAG = "|cffb87830{} form|r"        # like the starting forms: each ability says which shape it belongs to

# Growth task kinds (src/Devourer.h TaskKind): 1 kill type, 2 hit by school, 3 devour rarity, 4 devour type,
# 5 devour by name, 6 hit with a spell (scripted), and new in task 017:
KILL, HIT_BY, DEVOUR_RARITY, DEVOUR_TYPE, DEVOUR_NAME, SPELL_HIT = 1, 2, 3, 4, 5, 6
DEVOUR_FAMILY, DEVOUR_ENTRY, SPELL_CAST, DEAL_DAMAGE, TAKE_DAMAGE, HEAL = 7, 8, 9, 10, 11, 12

# The parents' spells the tasks count (tools/start_kit.py: shape s 5-12 = 9100910 + (s-5)*10 + slot).
PLAINSTRIDER_HIND_KICK = sk.sid(10, 1)
WOLF_RAVAGING_FEAST = sk.sid(5, 5)
BOAR_PRIMAL_CHARGE = sk.sid(9, 2)
SABER_ANIMA_SHRED = sk.sid(7, 1)
BAT_BLOOD_DRAIN = sk.sid(11, 2)
MOTH_BLINDING_SPORES = sk.sid(8, 4)
MOTH_SILKEN_COCOON = sk.sid(8, 6)        # the module counts it when the cocoon wraps the moth (TryCocoon)
WARP_STALKER_WARP = 9101002

PLANTS = ("lasher", "treant", "sapling", "shrub", "vine", "thorn", "petal", "root", "moss", "spore", "thistle")


def sid(shape, slot):
    """An evolved form's spell id: shape 16+, slot 0-9."""
    assert shape >= FIRST_SHAPE and 0 <= slot <= 9
    return FIRST + (shape - FIRST_SHAPE) * 10 + slot


class Evolved:
    """A tier-2 form: grows out of `parent` (devourer_evolution), not devoured."""

    def __init__(self, shape, name, parent, parent_name, creature, display, skin, one, two, gimmick, four, five,
                 diet, food, level, bp, tasks, extra=(), procs=(), scripts=(), changes=(), role="", looks=()):
        self.shape, self.name, self.parent, self.parent_name = shape, name, parent, parent_name
        self.creature, self.display, self.skin = creature, display, skin   # the creature the look comes from
        self.one, self.two, self.gimmick, self.four, self.five = one, two, gimmick, four, five
        self.diet = diet                  # [(creature type, bp)]
        self.food = food                  # [(creature type, family, name part, label)] -> 2x Bio Points
        self.level, self.bp = level, bp
        self.tasks = tasks                # [(kind, value, count, text, name parts)] any one is enough
        self.extra = list(extra)          # [(slot 6-9, template, overrides, texts)]
        self.procs = list(procs)          # [(slot, proc flags, spell type mask, hit mask, cooldown ms, charges, chance)]
        self.scripts = list(scripts)      # [(slot, ScriptName)]
        self.changes = list(changes)
        self.role = role
        self.base = sid(shape, 0)
        self.quest = 0                    # task 018: its molt quest (set below, in FORMS order)
        # Retail models brought in with the model tool (tools/modeltool, imports.json): [(display, colouring name)],
        # the first is the base look. They come with the shape (devourer_skin.free), so does the creature's own look.
        self.looks = list(looks)

    @property
    def look(self):
        return self.looks[0][0] if self.looks else self.display


# A passive whose aura procs (spell_proc below) or is scripted, worn while the shape is.
def gimmick(icon, procs, *effs):
    return proc_passive(icon, procs, *effs)


def stun_helper(template, duration, mechanic=MECHANIC_STUN, **fields):
    """A short stun the kit casts on an enemy."""
    return (template, helper({"DurationIndex": duration, "Mechanic": mechanic, "RangeIndex": RANGE_ANYWHERE,
                              "SchoolMask": SCHOOL_PHYSICAL, **fields,
                              **effects(aura(A_MOD_STUN, target=T_ENEMY))}))


def charge(cooldown, stun_spell, anima):
    """A charge usable in combat (the Boar's Primal Charge): knocks the enemy down with `stun_spell`."""
    return (100, {**CLEAN, **NO_MECHANICS, "Attributes": 0x20040010, "RecoveryTime": cooldown, **GCD,
                  **effects({"effect": E_CHARGE, "target": T_ENEMY}, gain(anima),
                            {"effect": E_TRIGGER_SPELL, "target": T_ENEMY, "trigger": stun_spell})})


def bleed(points, period=3000):
    return aura(A_PERIODIC_DAMAGE, points, target=T_ENEMY, period=period)


# --- 16 Greater Plainstrider (Plainstrider -> Tier 2A) ------------------------------------------------------------
GREATER_PLAINSTRIDER = Evolved(
    16, "Greater Plainstrider", 10, "Plainstrider", 3244, 178, "Greater Plainstrider",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": sk.DUR_9S, "EffectMechanic_2": MECHANIC_BLEED,
                     **effects(hit(6), bleed(3), gain(10))}),
     ("Rupturing Peck", "Peck a deep wound: weapon damage plus $s1, and the enemy bleeds for $o2 over 9 sec. "
      "Generates 10 Anima.", "Bleeding for $s2 every 3 sec.")),
    (1776, ability({**hunger(10), "RangeIndex": RANGE_COMBAT, "RecoveryTime": 15000, "DurationIndex": DUR_3S,
                    "SchoolMask": SCHOOL_PHYSICAL, "Mechanic": MECHANIC_KNOCKOUT,
                    "AuraInterruptFlags": AURA_INTERRUPT_DAMAGE,
                    **effects(hit(2), aura(A_MOD_STUN, target=T_ENEMY))}),
     ("Gouge & Talon", "Gouge the enemy with a talon: weapon damage plus $s1, and it is incapacitated for 3 sec. "
      "Any damage wakes it.", "Incapacitated.")),
    (25941, gimmick(516, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, aura(A_MOD_DODGE_PERCENT, 3), aura(A_DUMMY)),
     ("Gale Flurry", "Your chance to dodge is increased by 3%. When you dodge an attack, the wind of your wings "
      "blows the attacker 5 yards back and Windrunner Burst is ready again. Once every 6 sec.", "")),
    (2983, ability({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_4S, "RecoveryTime": 20000,
                    **effects(aura(A_MOD_INCREASE_SPEED, 60))}),
     ("Windrunner Burst", "Burst into a sprint: movement speed increased by 60% for 4 sec.",
      "Movement speed increased by 60%.")),
    (24423, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_6S,
                     "RecoveryTime": 20000, "SchoolMask": SCHOOL_NATURE,
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 8, "spread": 4, "target": T_SRC_CASTER,
                                "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8},
                               around(A_MOD_HIT_CHANCE, -15))}),
     ("Sandstorm Screech", "A screech that whips up dust: $s1 Nature damage to enemies within 8 yards, and they "
      "miss 15% more often for 6 sec.", "Chance to hit reduced by 15%.")),
    [(CREATURE_TYPE_BEAST, 10), (0, 3)],
    [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, FAMILY_SCORPID, "", ""), (0, FAMILY_SPIDER, "", "")],
    12, 500,
    [(DEVOUR_TYPE, CREATURE_TYPE_BEAST, 25, "Devour 25 beasts as a Plainstrider", ""),
     (SPELL_CAST, PLAINSTRIDER_HIND_KICK, 40, "Kick 40 times with Hind Kick", ""),
     (DEVOUR_ENTRY, 3068, 1, "Devour Mazzranache (Mulgore)", "")],
    extra=[(6, 6343, helper({"RangeIndex": RANGE_ANYWHERE, "DurationIndex": 0, "SchoolMask": SCHOOL_PHYSICAL,
                             **effects({"effect": E_KNOCK_BACK, "amount": 50, "misc": 100, "target": T_ENEMY})}),
            ("Gale Flurry", "", ""))],
    procs=[(3, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, 0, HIT_DODGE, 6000, 0, 100)],
    scripts=[(3, "spell_devourer_gale_flurry")],
    role="bleed skirmisher and disabler",
    changes=[
        "Gouge & Talon keeps the card's 3 sec incapacitate; any damage breaks it (a gouge), so it sets up a "
        "breather or a sprint, not a free hit.",
        "Windrunner Burst is a 4 sec sprint; Gale Flurry's \"resetting sprint dash\" makes it ready again.",
        "Gale Flurry has a 6 sec rest and a 3% dodge to go with it, so it shows up without stacking dodge gear.",
        "Task \"Run 2,000 yards with Sprint\" became \"Kick 40 times with Hind Kick\": the server does not count "
        "distance run. The two other options are the card's.",
    ])

# --- 17 Bloodsnout Worg (Wolf -> Tier 2A) --------------------------------------------------------------------------
BLOODSNOUT_WORG = Evolved(
    17, "Bloodsnout Worg", 5, "Wolf", 1923, 741, "Bloodsnout",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_6S, "EffectMechanic_2": MECHANIC_SNARE,
                     **effects(hit(6), aura(A_MOD_DECREASE_SPEED, -40, target=T_ENEMY), gain(15))}),
     ("Hamstring Bite", "Bite at the enemy's legs: weapon damage plus $s1, and its movement is slowed by 40% for "
      "6 sec. Generates 15 Anima.", "Movement slowed by 40%.")),
    (*charge(20000, CHARGE_STUN, 10),
     ("Savage Pounce", "Pounce on an enemy 8 to 25 yards away, even in the middle of a fight, and knock it down for "
      "1.5 sec. Generates 10 Anima.", "")),
    (25941, gimmick(1573, PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE, aura(A_DUMMY)),
     ("Hamstring Cripple", "Your strikes from behind cripple the enemy: its movement is slowed by 70% for 1.5 sec. "
      "Once every 4 sec.", "")),
    (24604, ability({**hunger(20), "RangeIndex": RANGE_SELF, "DurationIndex": DUR_12S, "RecoveryTime": 60000,
                     **effects(aura(A_MOD_MELEE_HASTE, 25))}),
     ("Blood Frenzy", "Work yourself into a blood frenzy: you attack 25% faster for 12 sec.",
      "Attack speed increased by 25%.")),
    (5782, ability({**hunger(10), "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_20, "RecoveryTime": 30000,
                    "DurationIndex": DUR_4S, "Mechanic": MECHANIC_FEAR, "SchoolMask": SCHOOL_SHADOW,
                    "AuraInterruptFlags": 0, **effects(aura(A_MOD_FEAR, target=T_ENEMY))}),
     ("Terrifying Snarl", "Snarl at an enemy within 20 yards: it flees in terror for 4 sec.", "Fleeing in terror.")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 8), (0, 3)],
    [(0, FAMILY_BOAR, "", ""), (0, FAMILY_CROCOLISK, "", "")],
    14, 550,
    [(DEVOUR_TYPE, CREATURE_TYPE_HUMANOID, 30, "Devour 30 humanoids as a Wolf", ""),
     (SPELL_CAST, WOLF_RAVAGING_FEAST, 40, "Feast on bleeds 40 times (Ravaging Feast)", ""),
     (DEVOUR_ENTRY, 4274, 1, "Devour Fenrus the Devourer (Shadowfang Keep)", "")],
    extra=[(6, 1715, helper({"RangeIndex": RANGE_ANYWHERE, "DurationIndex": DUR_1500, "SchoolMask": SCHOOL_PHYSICAL,
                             "Mechanic": MECHANIC_SNARE, **effects(aura(A_MOD_DECREASE_SPEED, -70, target=T_ENEMY))}),
            ("Hamstring Cripple", "", "Movement slowed by 70%."))],
    procs=[(3, PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE, 1, 0, 4000, 0, 100)],
    scripts=[(3, "spell_devourer_hamstring_cripple")],
    role="flanking assassin and crippler",
    changes=[
        "Hamstring Cripple slows by 70% for 1.5 sec as on the card; \"prevents turning\" is left out (the game "
        "cannot stop a creature from turning). 4 sec rest so it is not a permanent root.",
        "Blood Frenzy is attack speed only (25% for 12 sec): the card's \"haste & leech\" were two jobs in one "
        "button, and the Vampiric Duskbat is the leech form.",
        "Savage Pounce knocks down like the Boar's Primal Charge (8-25 yards, in combat).",
        "Task \"Consume 40 bleeds\" counts the Wolf's Ravaging Feast (the spell that eats bleeds); \"Devour Named "
        "Worg Leader\" is Fenrus the Devourer (Shadowfang Keep, a worg boss).",
    ])

# --- 18 Raging Agam'ar (Boar -> Tier 2A) --------------------------------------------------------------------------
TREMOR_STACKS = 10
RAGING_AGAMAR = Evolved(
    18, "Raging Agam'ar", 9, "Boar", 4514, 2453, "Agam'ar",
    (35290, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_15S, "CumulativeAura": 3,
                     **effects(hit(6), aura(A_MOD_RESISTANCE_PCT, -5, 1, target=T_ENEMY), gain(10))}),
     ("Crushing Gore", "Gore the enemy: weapon damage plus $s1, and its armor is crushed by 5% for 15 sec, up to 3 "
      "times. Generates 10 Anima.", "Armor reduced by 5% for each wound.")),
    (*charge(20000, sid(18, 8), 15),
     ("Tremor Charge", "Charge an enemy 8 to 25 yards away, even in the middle of a fight, and knock it down for "
      "2 sec. Generates 15 Anima.", "")),
    (25941, gimmick(1578, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, aura(A_DUMMY)),
     ("Kinetic Tremor", f"Blows you take charge your plating. At {TREMOR_STACKS} charges it bursts: enemies within "
      "8 yards take Physical damage and are knocked down for 1.5 sec.", "")),
    (467, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": sk.DUR_9S,
                   "RecoveryTime": 45000, "SchoolMask": SCHOOL_NATURE,
                   **effects(aura(A_DMG_TAKEN_PCT, -20, SCHOOL_ALL), aura(A_DAMAGE_SHIELD, 6, SCHOOL_NATURE_INDEX))}),
     ("Spiked Carapace", "Raise your spikes: damage taken reduced by 20% for 9 sec, and melee attackers take $s2 "
      "Nature damage.", "Damage taken reduced by 20%. Attackers take $s2 Nature damage.")),
    (16552, ability({"RangeIndex": RANGE_20, "RecoveryTime": 12000, "SchoolMask": SCHOOL_NATURE,
                     "DurationIndex": DUR_6S, "EffectMechanic_2": MECHANIC_SNARE,
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 10, "spread": 4, "target": T_ENEMY},
                               aura(A_MOD_DECREASE_SPEED, -50, target=T_ENEMY))}),
     ("Bile Spit", "Spit bile at an enemy within 20 yards: $s1 Nature damage, and its movement is slowed by 50% "
      "for 6 sec.", "Movement slowed by 50%.")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 8), (0, 3)],
    [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, FAMILY_SCORPID, "", "")],
    12, 500,
    [(DEVOUR_NAME, CREATURE_TYPE_HUMANOID, 30, "Devour 30 quilboar as a Boar", "razorfen|quilboar|bristleback"),
     (TAKE_DAMAGE, 0, 8000, "Weather 8,000 damage as a Boar", ""),
     (SPELL_CAST, BOAR_PRIMAL_CHARGE, 25, "Charge 25 times with Primal Charge", "")],
    extra=[(6, 22812, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_15S, "CumulativeAura": TREMOR_STACKS,
                              **effects(aura(A_DUMMY))}),
            ("Tremor Plating", "", "Charged plating.")),
           (7, 6343, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_1500, "Mechanic": MECHANIC_STUN,
                             "SchoolMask": SCHOOL_PHYSICAL,
                             **effects({"effect": E_SCHOOL_DAMAGE, "amount": 12, "spread": 6, "target": T_SRC_CASTER,
                                        "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8},
                                       around(A_MOD_STUN, radius=RADIUS_8))}),
            ("Kinetic Tremor", "", "Knocked down.")),
           (8, *stun_helper(CHARGE_STUN, DUR_2S), ("Tremor Charge", "", "Knocked down."))],
    procs=[(3, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, 1, 0, 0, 0, 100)],
    scripts=[(3, "spell_devourer_kinetic_tremor")],
    role="stun tank and sunderer",
    changes=[
        f"Kinetic Tremor counts blows taken ({TREMOR_STACKS} charges, kept 15 sec) instead of absorbed damage: the "
        "Devourer has no absorb shield to measure.",
        "Spiked Carapace is the card's spikes with a short -20% damage taken (the Boar already has the -30% Thick "
        "Hide); melee attackers take Nature damage while it lasts.",
        "Bile Spit opens at level 20 (ranged slow); Tremor Charge knocks down for 2 sec (the Boar's 1.5).",
        "Task \"Mitigate 8,000 damage\" counts damage taken as a Boar; \"Stun 25 with Charge\" counts Primal Charges.",
    ])

# --- 19 Shadowclaw (Saber -> Tier 2A) -----------------------------------------------------------------------------
SHADOWCLAW = Evolved(
    19, "Shadowclaw", 7, "Saber", 2175, 3030, "Shadowclaw",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": sk.DUR_9S, "EffectMechanic_2": MECHANIC_BLEED,
                     **effects(hit(5), bleed(3), gain(15))}),
     ("Throat Crush", "Crush the enemy's throat: weapon damage plus $s1, and it bleeds for $o2 over 9 sec. "
      "Generates 15 Anima.", "Bleeding for $s2 every 3 sec.")),
    (5215, {**CLEAN, "RecoveryTime": 10000, **GCD},                 # Prowl keeps its stealth, slow and rules
     ("Phase Prowl", "Slip between shadow and anima: unseen, but 30% slower. Your first strike out of it deals 50% "
      "more damage and silences the enemy for 2 sec. Cannot be used in combat.", "Unseen.")),
    (25941, gimmick(103, 0, aura(A_MOD_DODGE_PERCENT, 3)),
     ("Shadow Melancholy", "Your chance to dodge is increased by 3%. The first strike out of Phase Prowl silences "
      "the enemy for 2 sec.", "")),
    (5221, ability({**hunger(25), "AttributesEx": 0, "RangeIndex": RANGE_COMBAT, "RecoveryTime": 10000,
                    "SchoolMask": SCHOOL_PHYSICAL,
                    **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 60, "target": T_ENEMY},
                              {"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 60, "target": T_ENEMY},
                              {"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 60, "target": T_ENEMY})}),
     ("Flurry of Claws", "Three quick claws: three times 60% weapon damage.", "")),
    (17253, ability({**hunger(10), "RangeIndex": RANGE_COMBAT, "RecoveryTime": 10000, "SchoolMask": SCHOOL_SHADOW,
                     "DefenseType": DMG_MAGIC,
                     **effects({"effect": E_HEALTH_LEECH, "amount": 14, "spread": 6, "target": T_ENEMY}, gain(15)),
                     "EffectMultipleValue_1": 1.0}),
     ("Anima Drain Bite", "Bite through to the anima: $s1 Shadow damage, and you are healed for as much. "
      "Generates 15 Anima.", "")),
    [(CREATURE_TYPE_BEAST, 10), (0, 3)],
    [(0, FAMILY_CAT, "", ""), (0, FAMILY_SPIDER, "", "")],
    14, 550,
    [(SPELL_CAST, SABER_ANIMA_SHRED, 60, "Shred 60 times with Anima Shred", ""),
     (DEVOUR_NAME, 0, 20, "Devour 20 satyrs", "satyr|felsworn|hellcaller|trickster"),
     (DEVOUR_ENTRY, 2175, 1, "Devour Shadowclaw (Darkshore)", "")],
    extra=[(6, 15487, helper({"RangeIndex": RANGE_ANYWHERE, "DurationIndex": DUR_2S, "Mechanic": MECHANIC_SILENCE,
                              "SchoolMask": SCHOOL_SHADOW, **effects(aura(A_MOD_SILENCE, target=T_ENEMY))}),
            ("Shadow Melancholy", "", "Silenced.")),
           (7, 25941, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_5S, "SpellIconID": 103,
                              "ProcTypeMask": PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE | PROC_DONE_SPELL_MAGIC,
                              "ProcChance": 100, "ProcCharges": 1,
                              **effects(aura(A_MOD_DAMAGE_PCT_DONE, 50, SCHOOL_ALL),
                                        aura(A_PROC_TRIGGER_SPELL, trigger=sid(19, 6)))}),
            ("Poised to Strike", "", "Your next strike deals 50% more damage and silences the enemy."))],
    procs=[(7, PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE | PROC_DONE_SPELL_MAGIC, 1, 0, 0, 1, 100)],
    scripts=[(2, "spell_devourer_phase_prowl")],
    role="ambush assassin and silencer",
    looks=[(994028, "Shadowstalker Blue"), (994029, "Shadowstalker Bluepink"), (994030, "Shadowstalker Fel"),
           (994031, "Shadowstalker Purplegreen"), (994032, "Shadowstalker Purpleyellow"),
           (994033, "Shadowstalker Redblue"), (994034, "Shadowstalker Whiteblue"), (994035, "Shadowstalker Yellowgreen")],
    changes=[
        "The card's kit has no stealth, but its gimmick needs one: the Shadowclaw keeps the Saber's Phase Prowl; "
        "its opener (+50%) also silences for 2 sec. The card's \"Shadow Melancholy (40% dodge)\" button went for it "
        "(a 40% dodge button at level 14 is too strong); the passive gives 3% dodge.",
        "\"Stealth attacks ignore 50% armor\" is the +50% opener (the game has no per-strike armor ignore).",
        "Flurry of Claws is the Anima spender (25): three 60% claws.",
        "Task \"Kill 35 from stealth\" became \"Shred 60 times with Anima Shred\"; \"Dodge 30 melee attacks\" became "
        "\"Devour Shadowclaw\", the rare panther the form is named after (Darkshore).",
    ])

# --- 20 Rockjaw Backbreaker (Trogg -> Tier 2A) --------------------------------------------------------------------
ROCKJAW_BACKBREAKER = Evolved(
    20, "Rockjaw Backbreaker", 6, "Trogg", 1118, 723, "Backbreaker",
    (12809, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 10000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_1S, "EffectMechanic_2": MECHANIC_STUN,
                     **effects(hit(6), aura(A_MOD_STUN, target=T_ENEMY), gain(10))}),
     ("Bone Crusher", "Bring a fist down on the enemy: weapon damage plus $s1, and it is stunned for 1 sec. "
      "Generates 10 Anima.", "Stunned.")),
    (6343, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                    "DurationIndex": 0, "RecoveryTime": 10000, "SchoolMask": SCHOOL_PHYSICAL,
                    **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 70, "target": T_SRC_CASTER,
                               "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8})}),
     ("Whirlwind Slam", "Swing around and slam the ground: 70% weapon damage to every enemy within 8 yards.", "")),
    (25941, gimmick(93, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, aura(A_PROC_TRIGGER_SPELL, trigger=sid(20, 6))),
     ("Stone Skin Hardening", "Blows against you harden your skin: each hit has a 20% chance to raise your armor by "
      "10% for 10 sec, stacking 3 times.", "")),
    (20594, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": DUR_6S, "RecoveryTime": 45000,
                     **effects(aura(A_DMG_TAKEN_PCT, -25, SCHOOL_ALL))}),
     ("Stone Hide", "Your hide turns to stone: damage taken reduced by 25% for 6 sec.", "Damage taken reduced by 25%.")),
    (22812, ability({**hunger(20), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S,
                     "RecoveryTime": 60000, **effects(aura(A_OBS_MOD_HEALTH, 5, period=2000))}),
     ("Cannibalize", "Gnaw on what you have eaten: you regain 25% of your maximum health over 10 sec.",
      "Regaining 5% health every 2 sec.")),
    [(CREATURE_TYPE_HUMANOID, 10), (CREATURE_TYPE_BEAST, 6), (0, 3)],
    [(0, FAMILY_BEAR, "", ""), (CREATURE_TYPE_HUMANOID, 0, "", "")],
    12, 500,
    [(DEVOUR_NAME, CREATURE_TYPE_HUMANOID, 30, "Devour 30 troggs or dwarves as a Trogg", "trogg|dwarf|dwarven|ironforge|dark iron|frostmane"),
     (TAKE_DAMAGE, 0, 5000, "Weather 5,000 damage as a Trogg", ""),
     (DEVOUR_ENTRY, 808, 1, "Devour Grik'nir the Cold (Coldridge Valley)", "")],
    extra=[(6, 20594, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S, "CumulativeAura": 3,
                              **effects(aura(A_MOD_RESISTANCE_PCT, 10, 1))}),
            ("Stone Skin Hardening", "", "Armor increased by 10% for each stack."))],
    procs=[(3, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, 1, 0, 0, 0, 20)],
    role="armored tank and cleaver",
    changes=[
        "Stone Skin Hardening answers any hit with a 20% chance (crits against a level-12 Devourer are rare, so the "
        "card's \"critical hits\" would almost never fire), +10% armor per stack (the card's 25% x3 is +75%).",
        "Stone Hide is -25% for 6 sec (the card's -40% is a raid cooldown at level 12).",
        "Cannibalize Corpse needs no corpse (the Devourer already eats corpses with Devour): a heal over time, "
        "25% in 10 sec.",
        "Task \"Absorb 5,000 damage\" counts damage taken as a Trogg.",
    ])

# --- 21 Vampiric Duskbat (Bat -> Tier 2A) -------------------------------------------------------------------------
VAMPIRIC_DUSKBAT = Evolved(
    21, "Vampiric Duskbat", 11, "Bat", 1554, 8808, "Vampiric",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_12S, "EffectMechanic_2": MECHANIC_BLEED, "CumulativeAura": 3,
                     **effects(hit(4), bleed(2), gain(10))}),
     ("Exsanguinate", "Open a vein: weapon damage plus $s1, and the enemy bleeds for $o2 over 12 sec, up to 3 "
      "times. Generates 10 Anima.", "Bleeding for $s2 every 3 sec.")),
    (15487, ability({**hunger(10), "RangeIndex": RANGE_20, "RecoveryTime": 20000, "DurationIndex": DUR_3S,
                     "Mechanic": MECHANIC_SILENCE, "SchoolMask": SCHOOL_PHYSICAL,
                     **effects(aura(A_MOD_SILENCE, target=T_ENEMY))}),
     ("Deafening Screech", "Screech at an enemy within 20 yards: it is silenced for 3 sec.", "Silenced.")),
    (25941, gimmick(1579, PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE, aura(A_DUMMY)),
     ("Exsanguinating Frenzy", "Your melee hits heal you for 10% of their damage for each of your bleeds on the "
      "enemy.", "")),
    (6343, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                    "DurationIndex": 0, "RecoveryTime": 20000, "SchoolMask": SCHOOL_PHYSICAL,
                    **effects({"effect": E_KNOCK_BACK, "amount": 50, "misc": 100, "target": T_SRC_CASTER,
                               "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_6})}),
     ("Wing Buffet", "Beat your wings: enemies within 6 yards are knocked back.", "")),
    (17253, ability({**hunger(25), "RangeIndex": RANGE_COMBAT, "RecoveryTime": 15000, "SchoolMask": SCHOOL_SHADOW,
                     "DefenseType": DMG_MAGIC,
                     **effects({"effect": E_HEALTH_LEECH, "amount": 20, "spread": 6, "target": T_ENEMY}),
                     "EffectMultipleValue_1": 1.0}),
     ("Blood Feast", "Feast on the enemy's blood: $s1 Shadow damage, and you are healed for as much.", "")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 10), (CREATURE_TYPE_UNDEAD, 8), (0, 3)],
    [(CREATURE_TYPE_HUMANOID, 0, "", ""), (CREATURE_TYPE_UNDEAD, 0, "", "")],
    14, 550,
    [(DEVOUR_NAME, CREATURE_TYPE_HUMANOID, 25, "Devour 25 of the Scarlet Crusade as a Bat", "scarlet"),
     (HEAL, 0, 6000, "Drink 6,000 health as a Bat", ""),
     (SPELL_CAST, BAT_BLOOD_DRAIN, 30, "Drain blood 30 times (Blood Drain)", "")],
    scripts=[(3, "spell_devourer_exsanguinating_frenzy")],
    role="leech and silencer",
    changes=[
        "Exsanguinating Frenzy heals on melee hits only (10% of the hit per bleed): \"life leech on all attacks\" "
        "would let the leech spells heal twice.",
        "Exsanguinate stacks 3 times so the frenzy has bleeds to count.",
        "Task \"Interrupt 15 spells\" became \"Drain blood 30 times\" (the Bat's Blood Drain): the Bat has no "
        "interrupt; \"Leech 6,000 health\" counts all healing the Devourer does to itself as a Bat.",
    ])

# --- 22 Arcane Wraith (Mana Wyrm -> Tier 2A) ----------------------------------------------------------------------
ARCANE_WRAITH = Evolved(
    22, "Arcane Wraith", 12, "Mana Wyrm", 15273, 15438, "Arcane Wraith",
    (30451, ability({"Attributes": 0, "CastingTimeIndex": CAST_1500, "RangeIndex": RANGE_30, "RecoveryTime": 0,
                     "SchoolMask": SCHOOL_ARCANE, "DurationIndex": 0,
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 12, "spread": 6, "target": T_ENEMY}, gain(5))}),
     ("Nether Torrent", "Pour raw nether at the enemy: $s1 Arcane damage. Generates 5 Anima.", "")),
    (2139, ability({**hunger(10), "RangeIndex": RANGE_30, "RecoveryTime": 20000, "DurationIndex": DUR_2S,
                    "Mechanic": MECHANIC_SILENCE, "SchoolMask": SCHOOL_ARCANE,
                    **effects({"effect": E_INTERRUPT_CAST, "target": T_ENEMY},
                              aura(A_MOD_SILENCE, target=T_ENEMY), gain(20))}),
     ("Swallow Spell", "Swallow the spell an enemy is casting: it is interrupted and silenced for 2 sec. "
      "Generates 20 Anima.", "Silenced.")),
    (25941, gimmick(1485, PROC_DONE_SPELL_MAGIC | PROC_DONE_MELEE, aura(A_DUMMY)),
     ("Spell Devour", "Your attacks tear one magic buff off the enemy and devour it: your magic damage is increased "
      "by 10% for 15 sec, stacking 3 times. Once every 6 sec.", "")),
    (1953, {**CLEAN, "RecoveryTime": 20000, **GCD},                 # Blink keeps its own effects and rules
     ("Phase Warp", "Warp up to 20 yards forward, slipping out of stuns and roots.", "")),
    (1449, ability({**hunger(20), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "RecoveryTime": 15000,
                    "SchoolMask": SCHOOL_ARCANE,
                    **effects({"effect": E_SCHOOL_DAMAGE, "amount": 18, "spread": 8, "target": T_SRC_CASTER,
                               "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8})}),
     ("Arcane Rupture", "Rupture the arcane in you: $s1 Arcane damage to enemies within 8 yards.", "")),
    [(CREATURE_TYPE_ELEMENTAL, 10), (CREATURE_TYPE_HUMANOID, 6), (0, 3)],
    [(CREATURE_TYPE_ELEMENTAL, 0, "", "")],
    14, 550,
    [(DEAL_DAMAGE, SCHOOL_ARCANE, 5000, "Deal 5,000 Arcane damage as a Mana Wyrm", ""),
     (DEVOUR_NAME, 0, 25, "Devour 25 Wretched or elementals", "wretched|elemental|wraith|mana"),
     (TAKE_DAMAGE, SCHOOL_MAGIC_ALL, 3000, "Weather 3,000 magic damage as a Mana Wyrm", "")],
    extra=[(6, 30451, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_15S, "CumulativeAura": 3,
                              "SchoolMask": SCHOOL_ARCANE, **effects(aura(A_MOD_DAMAGE_PCT_DONE, 10, SCHOOL_MAGIC_ALL))}),
            ("Devoured Magic", "", "Magic damage increased by 10% for each stack."))],
    procs=[(3, PROC_DONE_SPELL_MAGIC | PROC_DONE_MELEE, 1, 0, 6000, 0, 100)],
    scripts=[(3, "spell_devourer_spell_devour")],
    role="buff-stealing caster",
    changes=[
        "Nether Torrent is a 1.5 sec cast instead of a channel (a channel would need its own tick spell).",
        "The card's ability \"Spell Devour (Silence & steal)\" is Swallow Spell (interrupt + 2 sec silence + 20 "
        "Anima, the Devourer has no mana to steal); the name Spell Devour stays with the gimmick.",
        "Phase Warp is a blink without the decoy (one job).",
        "Tasks: \"Drain 5,000 mana/energy\" became \"Deal 5,000 Arcane damage\" (the Mana Wyrm drains no mana); "
        "\"Reflect 10 spells\" became \"Weather 3,000 magic damage\" (the Mana Wyrm reflects nothing).",
    ])

# --- 23 Royal Blue Flutterer (Moth -> Tier 2A) --------------------------------------------------------------------
ROYAL_BLUE_FLUTTERER = Evolved(
    23, "Royal Blue Flutterer", 8, "Moth", 17350, 17711, "Royal Blue",
    (8921, ability({"RangeIndex": RANGE_25, "RecoveryTime": 6000, "SchoolMask": SCHOOL_ARCANE, "DurationIndex": 0,
                    **effects({"effect": E_SCHOOL_DAMAGE, "amount": 10, "spread": 4, "target": T_ENEMY}, gain(10))}),
     ("Starlight Sting", "Sting with starlight from up to 25 yards: $s1 Arcane damage. Generates 10 Anima.", "")),
    (2637, ability({**hunger(10), "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_20, "RecoveryTime": 30000,
                    "DurationIndex": DUR_6S, "Mechanic": MECHANIC_SLEEP, "TargetCreatureType": 0,
                    "SchoolMask": SCHOOL_NATURE, "AuraInterruptFlags": AURA_INTERRUPT_DAMAGE,
                    **effects(aura(A_MOD_STUN, target=T_ENEMY))}),
     ("Sleep Spores", "Puff sleeping spores at an enemy within 20 yards: it falls asleep for 6 sec. Any damage "
      "wakes it.", "Asleep.")),
    (25941, gimmick(109, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, aura(A_PROC_TRIGGER_SPELL, trigger=sid(23, 6))),
     ("Sleep Spore Powder", "Your wings shed a sleeping powder: a melee attacker has a 20% chance to fall asleep "
      "for 3 sec. Once every 8 sec.", "")),
    (339, ability({**hunger(10), "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_20, "RecoveryTime": 20000,
                   "DurationIndex": DUR_4S, "Mechanic": MECHANIC_ROOT, "SchoolMask": SCHOOL_NATURE,
                   "AuraInterruptFlags": 0, **effects(aura(A_MOD_ROOT, target=T_ENEMY))}),
     ("Silk Bind", "Bind an enemy within 20 yards in silk: it cannot move for 4 sec.", "Rooted.")),
    (5185, ability({**hunger(20), "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_SELF, "RecoveryTime": 30000,
                    "SchoolMask": SCHOOL_ARCANE, **effects({"effect": E_HEAL_PCT, "amount": 20, "target": T_CASTER})}),
     ("Lunar Heal", "Bathe in moonlight: you are healed for 20% of your maximum health.", "")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_ELEMENTAL, 8), (0, 3)],
    [(CREATURE_TYPE_BEAST, 0, "", "")] + [(CREATURE_TYPE_ELEMENTAL, 0, part, "Plants") for part in PLANTS],
    12, 500,
    [(DEVOUR_NAME, 0, 25, "Devour 25 plants or naga as a Moth",
      "|".join(PLANTS + ("naga", "siren", "myrmidon", "wrathtail", "slitherblade", "tidehunter"))),
     (SPELL_CAST, MOTH_BLINDING_SPORES, 30, "Blind 30 times with Blinding Spores", ""),
     (SPELL_CAST, MOTH_SILKEN_COCOON, 5, "Be saved by your cocoon 5 times", "")],
    extra=[(6, 2637, helper({"RangeIndex": RANGE_ANYWHERE, "DurationIndex": DUR_3S, "Mechanic": MECHANIC_SLEEP,
                             "TargetCreatureType": 0, "SchoolMask": SCHOOL_NATURE,
                             "AuraInterruptFlags": AURA_INTERRUPT_DAMAGE, **effects(aura(A_MOD_STUN, target=T_ENEMY))}),
            ("Sleep Spore Powder", "", "Asleep."))],
    procs=[(3, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, 0, 0, 8000, 0, 20)],
    role="sleep and root controller",
    looks=[(994008, "Ardenweald Blue"), (994009, "Ardenweald Dark"), (994010, "Ardenweald Mint"),
           (994011, "Ardenweald Red")],
    changes=[
        "Sleep Spore Powder has an 8 sec rest: at 20% per hit, a pack hitting the moth would sleep in turns forever.",
        "Lunar Heal is 20% (the card's 25%) and costs 20 Anima: it is the line's support heal, not a full refill.",
        "Starlight Sting is the builder; the Moth's Arcane theme (moonlight) carries on.",
        "Task \"Trigger Cocoon 5 times\" counts the Moth's Cocoon Metamorphosis when it wraps the moth.",
    ])

# --- 24 Void Terror (Warp Stalker -> Tier 2) ----------------------------------------------------------------------
GRAVITY_STACKS = 10
VOID_TERROR = Evolved(
    24, "Void Terror", 13, "Warp Stalker", 19980, 19368, "Void Terror",
    (686, ability({"Attributes": 0, "CastingTimeIndex": CAST_1500, "RangeIndex": RANGE_30, "RecoveryTime": 0,
                   "SchoolMask": SCHOOL_SHADOW, "DurationIndex": DUR_12S,
                   **effects({"effect": E_SCHOOL_DAMAGE, "amount": 10, "spread": 4, "target": T_ENEMY},
                             aura(A_PERIODIC_DAMAGE, 3, target=T_ENEMY, period=3000), gain(10))}),
     ("Nether Bolt", "Hurl a bolt of nether: $s1 Shadow damage, and $o2 more over 12 sec. Generates 10 Anima.",
      "$s2 Shadow damage every 3 sec.")),
    (36398, ability({**hunger(20), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "RecoveryTime": 30000,
                     "SchoolMask": SCHOOL_SHADOW, "MaxTargets": 4, "DurationIndex": 0,
                     **effects({"effect": E_PULL_TOWARDS, "misc": 150, "target": T_SRC_CASTER,
                                "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_12},
                               {"effect": E_SCHOOL_DAMAGE, "amount": 8, "spread": 4, "target": T_SRC_CASTER,
                                "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_12})}),
     ("Void Singularity", "Open a singularity: up to 4 enemies within 12 yards are pulled to you and take $s2 "
      "Shadow damage.", "")),
    (25941, gimmick(1499, 0, aura(A_DUMMY)),
     ("Gravitational Shadows", f"Every tick of Nether Bolt slows the enemy by 5%. At {GRAVITY_STACKS} ticks it "
      "collapses into an anima whirlpool: Shadow damage to every enemy within 8 yards of it.", "")),
    (17, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S,
                  "RecoveryTime": 30000, "SchoolMask": SCHOOL_SHADOW,
                  **effects(aura(A_SCHOOL_ABSORB, 300, SCHOOL_ALL))}),
     ("Dark Embrace", "Wrap yourself in darkness: absorbs 300 damage for 10 sec.", "Absorbs damage.")),
    (17253, ability({**hunger(20), "RangeIndex": RANGE_COMBAT, "RecoveryTime": 15000, "SchoolMask": SCHOOL_SHADOW,
                     "DefenseType": DMG_MAGIC,
                     **effects({"effect": E_HEALTH_LEECH, "amount": 22, "spread": 6, "target": T_ENEMY}),
                     "EffectMultipleValue_1": 1.0}),
     ("Shadow Drain", "Drain the enemy's life: $s1 Shadow damage, and you are healed for as much.", "")),
    [(CREATURE_TYPE_DEMON, 15), (CREATURE_TYPE_BEAST, 10), (0, 3)],
    [(CREATURE_TYPE_DEMON, 0, "", "")],
    16, 600,
    [(DEVOUR_NAME, 0, 25, "Devour 25 voidwalkers or void creatures", "void|nether|ethereal"),
     (SPELL_CAST, WARP_STALKER_WARP, 40, "Warp 40 times", ""),
     (DEAL_DAMAGE, 0, 15000, "Deal 15,000 damage as a Warp Stalker", "")],
    extra=[(6, 1715, helper({"RangeIndex": RANGE_ANYWHERE, "DurationIndex": DUR_6S, "CumulativeAura": GRAVITY_STACKS,
                             "Mechanic": MECHANIC_SNARE, "SchoolMask": SCHOOL_SHADOW,
                             **effects(aura(A_MOD_DECREASE_SPEED, -5, target=T_ENEMY))}),
            ("Gravitational Shadows", "", "Movement slowed by 5% for each stack.")),
           (7, 1449, helper({"RangeIndex": RANGE_ANYWHERE, "DurationIndex": 0, "SchoolMask": SCHOOL_SHADOW,
                             **effects({"effect": E_SCHOOL_DAMAGE, "amount": 20, "spread": 8,
                                        "target": T_DEST_TARGET_ANY, "targetB": T_DEST_AREA_ENEMY,
                                        "radius": RADIUS_8})}),
            ("Anima Whirlpool", "", ""))],
    scripts=[(1, "spell_devourer_gravitational_shadows")],
    role="shadow damage-over-time controller",
    changes=[
        "Dark Embrace is a shield only (the card's \"Shield & blind\" were two jobs).",
        "Void Singularity pulls up to 4 enemies within 12 yards (the card's 4 foes).",
        "Task \"Devour 25 Voidwalkers\" accepts void creatures by name (void, nether, ethereal); \"Land 40 "
        "Blink Strikes\" counts the Warp Stalker's Warp; \"Deal 15,000 Shadow dmg\" counts any damage: the Warp "
        "Stalker's kit is physical.",
    ])

FORMS = [GREATER_PLAINSTRIDER, BLOODSNOUT_WORG, RAGING_AGAMAR, SHADOWCLAW, ROCKJAW_BACKBREAKER, VAMPIRIC_DUSKBAT,
         ARCANE_WRAITH, ROYAL_BLUE_FLUTTERER, VOID_TERROR]
for _i, _form in enumerate(FORMS):
    _form.quest = MOLT_QUEST_FIRST + _i


def form_spells(f: Evolved, dbc):
    """(id, level, template, overrides, texts): form, abilities 1-2, passive, abilities 4-5, helpers."""
    one, two, gim, four, five = f.one, f.two, f.gimmick, f.four, f.five
    icon = dbc.row(one[0])[b.COL["SpellIconID"]] if gim[1].get("SpellIconID", 0) == 0 else gim[1]["SpellIconID"]
    names = [x[2][0] for x in (one, two, four)]
    out = [
        (f.base, 1, 16591, {
            **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
            "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
            "Category": SHAPE_CATEGORY, "RecoveryTime": 0, "CategoryRecoveryTime": SHIFT_COOLDOWN,
            "StartRecoveryCategory": 133, "StartRecoveryTime": 1000, "InterruptFlags": 0, "AuraInterruptFlags": 0,
            "SpellIconID": icon, **effects(aura(sk.A_TRANSFORM, 0, FORM_PLACEHOLDER_ENTRY))},
         (f"{f.name} Form", f"Take the shape of the {f.name.lower()}, grown out of your {f.parent_name.lower()}: "
          f"{names[0]}, {names[1]}, {names[2]} and {gim[2][0]}; {five[2][0]} opens at level 20. All shapes share "
          "one cooldown.", f"Wearing the {f.name.lower()}'s shape.")),
        (f.base + 1, 1, *one),
        (f.base + 2, 1, *two),
        (f.base + 3, 1, *gim),
        (f.base + 4, 1, *four),
        (f.base + 5, 20, five[0], {**five[1], "SpellLevel": 20, "BaseLevel": 20}, five[2]),
    ]
    for slot, t, o, x in f.extra:
        assert 6 <= slot <= 9, slot
        out.append((f.base + slot, 1, t, o, x))
    tag = SKILL_TAG.format(f.name)
    # The passive is an aura while the shape is worn, shown on the buff bar (not cancellable), like the starters'.
    for i, (spell, lvl, t, o, x) in enumerate(out):
        if spell == f.base + 3:
            attrs = (o.get("Attributes", ATTR0_ABILITY) & ~(b.ATTR0_PASSIVE | b.ATTR0_HIDDEN)) | ATTR0_CANT_CANCEL
            out[i] = (spell, lvl, t, {**o, "Attributes": attrs, "DurationIndex": DUR_INFINITE}, (x[0], x[1], x[2] or x[1]))
    return [(spell, lvl, t, o, (x[0], f"{x[1]}$B$B{tag}" if x[1] else tag, x[2]))
            if f.base < spell <= f.base + 5 else (spell, lvl, t, o, x) for spell, lvl, t, o, x in out]


def spell_rows(dbc, defs):
    rows = []
    for spell, level, template, overrides, (name, desc, tip) in defs:
        assert FIRST <= spell <= LAST, spell
        row = dbc.row(template)
        row[b.COL["ID"]] = spell
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

    defs = [d for f in FORMS for d in form_spells(f, dbc)]
    ids = [d[0] for d in defs]
    assert len(ids) == len(set(ids)), "duplicate spell id"
    shapes = [f.shape for f in FORMS]
    assert len(shapes) == len(set(shapes)), "duplicate shape id"
    rows = spell_rows(dbc, defs)
    lo, hi = FIRST_SHAPE, max(shapes)

    scripts = [(f.base, "spell_devourer_form") for f in FORMS] + \
        [(f.base + slot, name) for f in FORMS for slot, name in f.scripts]
    procs = [(f.base + slot, flags, types, hits, cd, charges, chance)
             for f in FORMS for slot, flags, types, hits, cd, charges, chance in f.procs]

    sql = [
        "-- Generated by tools/evolved_kit.py (task 017). Do not edit by hand: change the script and run it again.",
        "-- The evolved forms, tier 2 of the canvas lines: spells 9102000-9102999, shapes 16-24, their evolutions.",
        "-- Safe to run again; removed by uninstall/world.sql.",
        "-- Note: 2026_09_30_04_devourer_world.sql clears devourer_evolution(_task) when it runs; run this file after it.",
        "",
        f"DELETE FROM `spell_dbc` WHERE `ID` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_dbc` (" + ",".join(f"`{c}`" for c in b.COLUMNS) + ") VALUES",
        ",\n".join(rows) + ";",
        "",
        f"DELETE FROM `spell_script_names` WHERE `spell_id` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES",
        ",\n".join(f"({s}, '{n}')" for s, n in scripts) + ";",
        f"DELETE FROM `spell_custom_attr` WHERE `spell_id` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_custom_attr` (`spell_id`, `attributes`) VALUES",
        ",\n".join(f"({f.base}, 0x01000000)" for f in FORMS) + ";",
        "-- The gimmicks that answer to hits (Cooldown = their rest, Chance = how often).",
        f"DELETE FROM `spell_proc` WHERE `SpellId` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_proc` (`SpellId`, `SchoolMask`, `SpellFamilyName`, `SpellFamilyMask0`, `SpellFamilyMask1`,"
        " `SpellFamilyMask2`, `ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`, `HitMask`, `AttributesMask`,"
        " `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`) VALUES",
        ",\n".join(f"({s}, 0, 0, 0, 0, 0, {flags}, {types}, 2, {hits}, 0, 0, {chance}, {cd}, {charges})"
                   for s, flags, types, hits, cd, charges, chance in procs) + ";",
        "",
        f"-- Shapes {lo}-{hi}: spell_3 is the fourth ability, spell_4 the fifth (opens at level 20, its spell level).",
        f"DELETE FROM `devourer_shape` WHERE `shape_id` BETWEEN {lo} AND {hi};",
        "INSERT INTO `devourer_shape` (`shape_id`, `name`, `form_spell`, `display_id`, `scale`, `spell_1`, `spell_2`,"
        " `spell_3`, `spell_4`, `passive`, `brood_display`) VALUES",
        ",\n".join(f"({f.shape}, {q(f.name)}, {f.base}, {f.look}, 1, {f.base + 1}, {f.base + 2}, {f.base + 4},"
                   f" {f.base + 5}, {f.base + 3}, {f.display})" for f in FORMS) + ";",
        f"DELETE FROM `devourer_skin` WHERE `shape_id` BETWEEN {lo} AND {hi};",
        "-- free = 1: comes with the shape (the retail looks, and the creature's own look beside them).",
        "INSERT INTO `devourer_skin` (`display_id`, `shape_id`, `name`, `brood_display`, `free`) VALUES",
        ",\n".join([f"({f.display}, {f.shape}, {q(f.skin)}, 0, {1 if f.looks else 0})" for f in FORMS]
                   + [f"({d}, {f.shape}, {q(n)}, 0, 1)" for f in FORMS for d, n in f.looks]) + ";",
        f"DELETE FROM `devourer_diet` WHERE `shape_id` BETWEEN {lo} AND {hi};",
        "INSERT INTO `devourer_diet` (`shape_id`, `creature_type`, `bp`) VALUES",
        ",\n".join(f"({f.shape}, {t}, {bp})" for f in FORMS for t, bp in f.diet) + ";",
        "-- Favourite food (2x Bio Points for everyone): the line's, from the base form's canvas card.",
        f"DELETE FROM `devourer_favourite_food` WHERE `shape_id` BETWEEN {lo} AND {hi};",
        "INSERT INTO `devourer_favourite_food` (`shape_id`, `creature_type`, `family`, `name_part`, `label`) VALUES",
        ",\n".join(f"({f.shape}, {t}, {fam}, {q(part)}, {q(label)})" for f in FORMS for t, fam, part, label in f.food)
        + ";",
        "",
        "-- Growth: each grows out of its line's form with the Bio Points, the level and ANY ONE of its tasks.",
        "-- Task kinds (src/Devourer.h TaskKind): 3 devour rarity, 4 devour type, 5 devour by name (name_part),",
        "-- 7 devour family, 8 devour one creature (value = entry), 9 use a spell (value = spell id), 10 deal damage,",
        "-- 11 take damage (value = school mask, 0 = any; count = damage), 12 heal yourself (count = health).",
        "-- Task 018: an evolution with a molt quest waits for it: the module puts the quest in the log when the form",
        "-- is ready, and handing it in to Wren (tools/witch_sisters.py) is the evolution.",
        "SET @devourer_col := (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()",
        "    AND TABLE_NAME = 'devourer_evolution' AND COLUMN_NAME = 'quest');",
        "SET @devourer_sql := IF(@devourer_col = 0, 'ALTER TABLE `devourer_evolution` ADD COLUMN `quest` INT UNSIGNED "
        "NOT NULL DEFAULT 0 COMMENT ''molt quest; 0 = it grows by itself''', 'DO 0');",
        "PREPARE devourer_stmt FROM @devourer_sql;",
        "EXECUTE devourer_stmt;",
        "DEALLOCATE PREPARE devourer_stmt;",
        f"DELETE FROM `devourer_evolution` WHERE `to_shape` BETWEEN {lo} AND {hi};",
        "INSERT INTO `devourer_evolution` (`from_shape`, `to_shape`, `bp`, `min_level`, `any_task`, `quest`) VALUES",
        ",\n".join(f"({f.parent}, {f.shape}, {f.bp}, {f.level}, 1, {f.quest})" for f in FORMS) + ";",
        "-- The name lists of the devour-by-name tasks need more room than the frog line's 100 characters.",
        "ALTER TABLE `devourer_evolution_task` MODIFY COLUMN `name_part` VARCHAR(255) NOT NULL DEFAULT '' COMMENT "
        "'kind 5: the meal''s name holds one of these (|-separated)';",
        f"DELETE FROM `devourer_evolution_task` WHERE `to_shape` BETWEEN {lo} AND {hi};",
        "INSERT INTO `devourer_evolution_task` (`to_shape`, `task_id`, `kind`, `value`, `count`, `text`, `name_part`)"
        " VALUES",
        ",\n".join(f"({f.shape}, {i}, {kind}, {value}, {count}, {q(text)}, {q(parts)})"
                   for f in FORMS for i, (kind, value, count, text, parts) in enumerate(f.tasks, 1)) + ";",
        "",
    ]
    OUT_SQL.write_bytes("\n".join(sql).encode("utf-8"))

    md = ["# Evolved forms, tier 2 (task 017)",
          "",
          "Generated by `tools/evolved_kit.py` — edit the script, not this file. Design: the owner's canvas \"Canvas "
          "Evolutions for Devourer\", Section 1 (the \"A\" branch of each starter line) and the Warp Stalker's line. "
          "Numbers are a first pass for levels 12-20.",
          "",
          f"Spell ids {FIRST}-{LAST}: shape s uses {FIRST} + (s-16)*10 + slot (slot 0 form, 1-2 abilities, 3 passive, "
          "4 ability, 5 ability that opens at level 20, 6-9 spells the kit casts).",
          "",
          "A tier-2 form is not devoured: it grows out of its line's form (`devourer_evolution`) once that form has "
          "the Bio Points, the Devourer the level, and **any one** of the three tasks is done (the canvas rule). "
          "Then the molt quest (task 018) comes into the log: handing it in to Wren in the In-Between is the "
          "evolution. The earlier form stays.",
          "",
          "| Shape | Form | Grows out of | Level | Bio Points | Role |",
          "|---|---|---|---|---|---|"]
    md += [f"| {f.shape} | {f.name} | {f.parent_name} | {f.level} | {f.bp} | {f.role} |" for f in FORMS]
    md.append("")
    for f in FORMS:
        md.append(f"### {f.name} (shape {f.shape}, grows out of the {f.parent_name})")
        if f.looks:
            md.append(f"Look: a retail model, base {f.look} (`{f.looks[0][1]}`); its other colourings come with the "
                      "shape: " + ", ".join(f"{d} `{n}`" for d, n in f.looks[1:]) + f". The creature's own look "
                      f"(creature {f.creature}, display {f.display}, `{f.skin}`) comes with it too. Any one task:")
        else:
            md.append(f"Look: creature {f.creature}, display {f.display} (skin `{f.skin}`). Any one task:")
        md.append("")
        md += [f"- {text}" for kind, value, count, text, parts in f.tasks]
        md.append("")
        md.append("| Spell | Level | Name | What it does |")
        md.append("|---|---|---|---|")
        for spell, lvl, t, o, (name, desc, tip) in form_spells(f, dbc):
            md.append(f"| {spell} | {lvl} | {name} | {desc.replace('$B$B', ' ') or '(cast by the kit) ' + tip} |")
        md.append("")
        if f.changes:
            md.append("Changes against the canvas card, and why:")
            md.append("")
            md += [f"- {c}" for c in f.changes]
            md.append("")
    OUT_MD.write_bytes("\n".join(md).encode("utf-8"))
    print(f"{len(rows)} spells ({min(ids)}-{max(ids)}), {len(FORMS)} forms (shapes {lo}-{hi})")
    print(f"wrote {OUT_SQL.relative_to(REPO)}, {OUT_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
