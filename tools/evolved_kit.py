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
DONE_PROCS = PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE | PROC_DONE_SPELL_MAGIC   # the phase mask only counts for these
CREATURE_TYPE_DEMON, CREATURE_TYPE_UNDEAD, CREATURE_TYPE_HUMANOID = 3, 6, 7
FAMILY_BEAR = 4
SKILL_TAG = "|cffb87830{} form|r"        # like the starting forms: each ability says which shape it belongs to
# The form review's picks (2026-10-03): new lines from the converted models.
E_TELEPORT_UNITS, E_PERSISTENT_AREA_AURA, E_DISPEL, E_DISPEL_MECHANIC = 5, 27, 38, 108
A_MOD_UNATTACKABLE = 93
DISPEL_POISON = 4
MECHANIC_DISORIENTED = 2
T_DEST_TARGET_BACK = 65                  # behind the target (Shadowstep's destination)
FAMILY_SERPENT = 35

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
    """A form of this file. Tier 2 and up grow out of `parent` (devourer_evolution) and are not devoured; a new line's
    first form (parent 0) is devoured instead: any creature of `family` gives it, as the starting forms do."""

    def __init__(self, shape, name, parent, parent_name, creature, display, skin, one, two, gimmick, four, five,
                 diet, food, level, bp, tasks, extra=(), procs=(), scripts=(), changes=(), role="", looks=(),
                 family=0, later_level=20, scale=1, quest=0, sources=(), earned=(), brood=0):
        assert bool(parent) != bool(family or sources), f"{name}: grows out of a parent, or is devoured"
        self.family = family              # a line's first form: any creature of this family gives it
        self.later_level = later_level    # the level the fifth ability opens at
        self.scale = scale                # devourer_shape.scale (a model bigger or smaller than its looks)
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
        self.quest = quest                # task 018: its molt quest (0 = the next free one, in MOLTS order)
        # Retail models brought in with the model tool (tools/modeltool, imports.json): [(display, colouring name)],
        # the first is the base look. They come with the shape (devourer_skin.free), so does the creature's own look.
        self.looks = list(looks)
        # Creatures that give the form without a family of their own (the Dragonkin whelps): [(entry, colouring
        # display, 0 = the base look)]; `earned` are the colourings only those creatures give (devourer_skin.free 0).
        self.sources = list(sources)
        self.brood = brood                # a Brood Devourer's hatchlings while it wears this shape (0 = `display`)
        self.earned = list(earned)

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

# --- the form review's picks (2026-10-03): line 1, Viper -> Twin-Fang -> Sethrak ----------------------------------
# The owner asked for a snake line that leads to the Sethrak mage (shape 1, until now only met in Tanaris at 44-46).
# Numbers lean on attack power (spell_bonus_data, the "_bonus" key: direct, dot, ap, ap_dot) so they keep up past 20.
SERPENT_FOOD = [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, 0, "egg", "Eggs"), (0, 0, "frog", "Frogs"),
                (0, 0, "toad", "Frogs")]
SERPENTS = "serpent|snake|viper|adder|cobra|moccasin|naga|siren|myrmidon|slitherblade|coilskar"
EMERGE_STATE = 65982                     # stock "Emerge": its state kit plays the model's Emerge animation

# 25 Viper (devoured: any creature of the Serpent family; the Wailing Caverns' Deviate Adders and Vipers, 18-19)
VIPER = Evolved(
    25, "Viper", 0, "", 5755, 994052, "Rock Viper",
    (16552, ability({"RangeIndex": RANGE_25, "RecoveryTime": 3000, "SchoolMask": SCHOOL_NATURE,
                     "DurationIndex": sk.DUR_9S, "_bonus": (0, 0, 0.12, 0.03),
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 16, "spread": 6, "target": T_ENEMY},
                               aura(A_PERIODIC_DAMAGE, 5, target=T_ENEMY, period=3000), gain(10))}),
     ("Venom Spit", "Spit venom at an enemy up to 25 yards away: $s1 Nature damage, and $o2 more over 9 sec. "
      "Generates 10 Anima.", "$s2 Nature damage every 3 sec.")),
    (26234, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "CastingTimeIndex": CAST_INSTANT,
                     "RangeIndex": RANGE_SELF, "DurationIndex": DUR_2S, "RecoveryTime": 15000, "AuraInterruptFlags": 0,
                     **effects(aura(A_MOD_INCREASE_SPEED, 60), aura(A_MOD_UNATTACKABLE), aura(A_DUMMY))}),
     ("Sand Slither", "Sink into the ground for 2 sec: 60% faster, and nothing can strike you. You come up behind your "
      "target.", "Under the ground.")),
    (25941, gimmick(1987, 0, aura(A_DUMMY)),
     ("Cold Blood", "Your venom bites 20% harder into enemies that are slowed or rooted.", "")),
    (50245, ability({**hunger(10), "RangeIndex": RANGE_COMBAT, "RecoveryTime": 20000, "DurationIndex": DUR_3S,
                     "Mechanic": MECHANIC_ROOT, "SchoolMask": SCHOOL_PHYSICAL,
                     **effects(aura(A_MOD_ROOT, target=T_ENEMY))}),
     ("Coil", "Wrap your coils around an enemy in reach: it cannot move for 3 sec.", "Coiled: cannot move.")),
    (20594, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF, "DurationIndex": 0,
                     "RecoveryTime": 45000,
                     **effects({"effect": E_DISPEL, "amount": 1, "misc": DISPEL_POISON, "target": T_CASTER},
                               {"effect": E_DISPEL_MECHANIC, "misc": MECHANIC_SNARE, "target": T_CASTER},
                               {"effect": E_HEAL_PCT, "amount": 10, "target": T_CASTER})}),
     ("Shed", "Shed your skin: one poison and every slow come off with it, and you are healed for 10% of your maximum "
      "health.", "")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_CRITTER, 10), (CREATURE_TYPE_HUMANOID, 6), (0, 3)],
    SERPENT_FOOD, 18, 0, [], family=FAMILY_SERPENT,
    extra=[(6, EMERGE_STATE, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_1S, **effects(aura(A_DUMMY))}),
            ("Emerge", "", ""))],
    scripts=[(2, "spell_devourer_sand_slither")],
    looks=[(994052, "Rock Viper"), (994054, "Rock Viper Yellow"), (994051, "Rock Viper Blue"),
           (994053, "Rock Viper Red")],
    role="ranged poisoner",
    changes=[
        "A new line from the form review (2026-10-03, \"Devourer Form Picks\"): devoured from any creature of the "
        "Serpent family, the first ones are the Deviate Adders and Vipers of the Wailing Caverns (18-19).",
        "Sand Slither keeps the model's Submerge and Emerge (stock spells that play them: Submerge Visual, Emerge).",
        "Shed opens at level 20 as an ability, as the pick proposed, instead of being a passive.",
        "Venom Spit grows with attack power (12% on the hit, 3% a tick), so it keeps up past level 20.",
    ])

# --- the owner's picks (2026-10-03): "prepare babyeagle and komodo, and babywindserpent after viper (magelike)" ----
# Retail models brought in with the model tool, sized to the creatures they stand for (imports.json).
A_MOD_CRIT_PERCENT, A_MOD_SPELL_CRIT_CHANCE, A_MOD_HEALING_PCT = 52, 57, 118
FAMILY_CROCOLISK_ = 6                    # (FAMILY_CROCOLISK from start_kit is the same; named for the komodo line)
FAMILY_BIRD_OF_PREY, FAMILY_WIND_SERPENT = 26, 27
HIT_CRIT = 0x2

# 26 Baby Wind Serpent (tier 2, the Viper's: a caster)
BABY_WIND_SERPENT = Evolved(
    26, "Baby Wind Serpent", 25, "Viper", 3247, 994055, "Wind Serpent Green",
    (24844, ability({"CastingTimeIndex": CAST_1500, "RangeIndex": RANGE_30, "RecoveryTime": 0,
                     "SchoolMask": SCHOOL_NATURE, "_bonus": (0, 0, 0.25, 0),
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 24, "spread": 8, "target": T_ENEMY}, gain(10))}),
     ("Lightning Breath", "Breathe lightning at an enemy up to 30 yards away: $s1 Nature damage. Generates 10 Anima.",
      "")),
    (421, ability({**hunger(20), "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_30, "RecoveryTime": 10000,
                   "SchoolMask": SCHOOL_NATURE, "_bonus": (0, 0, 0.2, 0),
                   **effects({"effect": E_SCHOOL_DAMAGE, "amount": 20, "spread": 6, "target": T_ENEMY, "chain": 3})}),
     ("Chain Lightning", "Lightning leaps from an enemy to up to 2 more nearby: $s1 Nature damage to each.", "")),
    (25941, gimmick(62, PROC_DONE_SPELL_MAGIC, aura(A_MOD_SPELL_CRIT_CHANCE, 5),
                    aura(A_PROC_TRIGGER_SPELL, trigger=sid(26, 6))),
     ("Static Charge", "Your chance to strike critically with spells is increased by 5%, and a critical strike gives "
      "back 5 Anima.", "")),
    (61391, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_4S,
                     "RecoveryTime": 20000, "SchoolMask": SCHOOL_NATURE, "EffectMechanic_2": MECHANIC_SNARE,
                     **effects({"effect": E_KNOCK_BACK, "amount": 60, "misc": 120, "target": T_SRC_CASTER,
                                "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8},
                               around(A_MOD_DECREASE_SPEED, -30))}),
     ("Cyclone Gust", "Beat up a gust of wind: enemies within 8 yards are blown back and move 30% slower for 4 sec.",
      "Movement slowed by 30%.")),
    (16914, ability({**hunger(25), "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_30, "RecoveryTime": 25000,
                     "DurationIndex": DUR_6S, "SchoolMask": SCHOOL_NATURE, "_bonus": (0, 0, 0, 0.04),
                     "ChannelInterruptFlags": 0, "AttributesEx": 0,
                     **effects({"effect": E_PERSISTENT_AREA_AURA, "aura": A_PERIODIC_DAMAGE, "amount": 8,
                                "period": 1000, "target": T_DEST_TARGET_ANY, "radius": RADIUS_8},
                               {"effect": E_PERSISTENT_AREA_AURA, "aura": A_MOD_DECREASE_SPEED, "amount": -30,
                                "target": T_DEST_TARGET_ANY, "radius": RADIUS_8})}),
     ("Squall", "Call a squall up to 30 yards away: for 6 sec, enemies under it take $s1 Nature damage every second "
      "and move 30% slower.", "In the squall.")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_ELEMENTAL, 8), (0, 3)],
    SERPENT_FOOD, 28, 800,
    [(DEVOUR_FAMILY, FAMILY_WIND_SERPENT, 25, "Devour 25 wind serpents as a Viper", ""),
     (SPELL_CAST, sid(25, 1), 60, "Spit venom 60 times (Venom Spit)", ""),
     (DEVOUR_ENTRY, 3654, 1, "Devour Mutanus the Devourer (Wailing Caverns)", "")],
    extra=[(6, 24844, helper({"RangeIndex": RANGE_SELF, "DurationIndex": 0, "SpellVisualID_1": 0,
                              **effects(gain(5))}),
            ("Static Charge", "", ""))],
    procs=[(3, PROC_DONE_SPELL_MAGIC, 1, HIT_CRIT, 0, 0, 100)],
    looks=[(994055, "Wind Serpent Green"), (994059, "Wind Serpent Yellow"), (994056, "Wind Serpent Pink"),
           (994057, "Wind Serpent Purple"), (994058, "Wind Serpent White")],
    later_level=34,
    role="lightning caster",
    changes=[
        "The owner's pick (2026-10-03, \"babywindserpent after viper (magelike)\"): the Viper's tier 2 is a caster, "
        "in place of the Twin-Fang.",
        "Its damage grows with attack power (the Devourer has no spell power): 25% on Lightning Breath, 20% on Chain "
        "Lightning, 4% a second in the Squall.",
        "Tasks: devour wind serpents (the Thunderhawks of the Barrens, 18-24, are the first), or the Viper's Venom "
        "Spit 60 times, or Mutanus the Devourer.",
    ])

# 27 Baby Eagle (devoured: any bird of prey, from the Strigid Owls of Teldrassil, 5-6, to the Fjord Hawks)
BABY_EAGLE = Evolved(
    27, "Baby Eagle", 0, "", 1995, 994061, "Eagle Brown",
    (50541, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 5000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": 0, **effects(hit(5), gain(10))}),
     ("Talon Strike", "Rake the enemy with your talons: weapon damage plus $s1. Generates 10 Anima.", "")),
    (*charge(20000, CHARGE_STUN, 10),
     ("Dive", "Dive at an enemy 8 to 25 yards away, even in the middle of a fight, and knock it down for 1.5 sec. "
      "Generates 10 Anima.", "")),
    (25941, gimmick(168, 0, aura(A_MOD_CRIT_PERCENT, 3)),
     ("Keen Eyes", "Your chance to strike critically is increased by 3%.", "")),
    (61391, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": 0,
                     "RecoveryTime": 20000, "SchoolMask": SCHOOL_PHYSICAL,
                     **effects({"effect": E_KNOCK_BACK, "amount": 50, "misc": 100, "target": T_SRC_CASTER,
                                "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_6})}),
     ("Wing Gust", "Beat your wings: enemies within 6 yards are blown back.", "")),
    (24423, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S,
                     "RecoveryTime": 20000, "SchoolMask": SCHOOL_PHYSICAL,
                     **effects(around(A_MOD_MELEE_HASTE, -10))}),
     ("Piercing Cry", "A cry that cuts to the bone: enemies within 8 yards attack 10% slower for 10 sec.",
      "Attack speed slowed by 10%.")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_CRITTER, 10), (0, 3)],
    [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, FAMILY_SERPENT, "", "Snakes")],
    5, 0, [], family=FAMILY_BIRD_OF_PREY,
    looks=[(994061, "Eagle Brown"), (994060, "Eagle Blue"), (994062, "Eagle Burgundy"), (994063, "Eagle Grey"),
           (994064, "Eagle Orange"), (994065, "Eagle Red")],
    role="diving skirmisher",
    changes=[
        "The owner's pick (2026-10-03, \"babyeagle\"): the Amani baby eagle model. Any creature of the Bird of Prey "
        "family gives it (hawks and eagles; the owls give the Owl since the owl line came).",
        "Favourite food: critters and snakes.",
    ])

# 28 Baby Komodo (devoured: any crocolisk, from Durotar's Dreadmaw Crocolisks, 9-11) -> 29 Komodo Dragon
BABY_KOMODO = Evolved(
    28, "Baby Komodo", 0, "", 3110, 994070, "Komodo Green",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_NATURE,
                     "DurationIndex": DUR_12S, "_bonus": (0, 0, 0, 0.02),
                     **effects(hit(5), aura(A_PERIODIC_DAMAGE, 3, target=T_ENEMY, period=3000), gain(10))}),
     ("Septic Bite", "A filthy bite: weapon damage plus $s1, and the wound festers for $o2 Nature damage over 12 sec. "
      "Generates 10 Anima.", "Festering: $s2 Nature damage every 3 sec.")),
    (3604, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 10000, "SchoolMask": SCHOOL_PHYSICAL,
                    "DurationIndex": DUR_6S, "EffectMechanic_2": MECHANIC_SNARE,
                    **effects(hit(3), aura(A_MOD_DECREASE_SPEED, -50, target=T_ENEMY))}),
     ("Ankle Snap", "Snap at the enemy's ankles: weapon damage plus $s1, and it moves 50% slower for 6 sec.",
      "Movement slowed by 50%.")),
    (25941, gimmick(1581, 0, aura(A_MOD_RESISTANCE_PCT, 10, 1)),
     ("Thick Scales", "Your armor is increased by 10%.", "")),
    (49966, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": 0, "RecoveryTime": 10000, "SchoolMask": SCHOOL_PHYSICAL,
                     **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 70, "target": T_SRC_CASTER,
                                "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8})}),
     ("Tail Whip", "Whip your tail around: 70% weapon damage to every enemy within 8 yards.", "")),
    (774, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S,
                   "RecoveryTime": 45000, "SchoolMask": SCHOOL_NATURE, "CastingTimeIndex": CAST_INSTANT,
                   **effects(aura(A_OBS_MOD_HEALTH, 3, period=2000))}),
     ("Bask", "Bask and let your hide knit: you regain 15% of your maximum health over 10 sec.",
      "Regaining 3% health every 2 sec.")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 6), (0, 3)],
    [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, FAMILY_BOAR, "", "")],
    9, 0, [], family=FAMILY_CROCOLISK_,
    looks=[(994070, "Komodo Green"), (994066, "Komodo Black"), (994067, "Komodo Blue"), (994068, "Komodo Brown"),
           (994069, "Komodo Dark Blue"), (994071, "Komodo Gila Orange"), (994072, "Komodo Gila Yellow"),
           (994073, "Komodo Grey"), (994074, "Komodo Bright Green"), (994075, "Komodo Orange"),
           (994076, "Komodo Purple"), (994077, "Komodo Red"), (994078, "Komodo Teal"), (994079, "Komodo White"),
           (994080, "Komodo Yellow")],
    role="festering brawler",
    changes=[
        "The owner's pick (2026-10-03, \"komodo\"): the baby komodo model. Any creature of the Crocolisk family gives "
        "it (the Dreadmaw Crocolisks of Durotar, 9-11, are the first); it grows into the Komodo Dragon.",
    ])

KOMODO_DRAGON = Evolved(
    29, "Komodo Dragon", 28, "Baby Komodo", 2476, 994086, "Komodo Dragon Green",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_NATURE,
                     "DurationIndex": DUR_12S, "_bonus": (0, 0, 0, 0.03),
                     **effects(hit(9), aura(A_PERIODIC_DAMAGE, 6, target=T_ENEMY, period=3000), gain(15))}),
     ("Septic Maw", "A deep, filthy bite: weapon damage plus $s1, and the wound festers for $o2 Nature damage over "
      "12 sec. Generates 15 Anima.", "Festering: $s2 Nature damage every 3 sec.")),
    (12809, ability({**hunger(20), "RangeIndex": RANGE_COMBAT, "RecoveryTime": 20000, "DurationIndex": DUR_2S,
                     "SchoolMask": SCHOOL_PHYSICAL, "EffectMechanic_2": MECHANIC_STUN,
                     **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 120, "target": T_ENEMY},
                               aura(A_MOD_STUN, target=T_ENEMY))}),
     ("Death Roll", "Clamp down and roll: 120% weapon damage, and the enemy is stunned for 2 sec.", "Stunned.")),
    (25941, gimmick(1581, PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE, aura(A_PROC_TRIGGER_SPELL, trigger=sid(29, 6))),
     ("Septic Saliva", "Your bites leave filth in the wound: the enemy receives 25% less healing for 6 sec.", "")),
    (*charge(20000, CHARGE_STUN, 10),
     ("Ambush Lunge", "Lunge at an enemy 8 to 25 yards away, even in the middle of a fight, and knock it down for "
      "1.5 sec. Generates 10 Anima.", "")),
    (774, ability({**hunger(20), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S,
                   "RecoveryTime": 60000, "SchoolMask": SCHOOL_NATURE, "CastingTimeIndex": CAST_INSTANT,
                   **effects(aura(A_OBS_MOD_HEALTH, 6, period=2000))}),
     ("Regenerative Hide", "Your hide closes its own wounds: you regain 30% of your maximum health over 10 sec.",
      "Regaining 6% health every 2 sec.")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 8), (0, 3)],
    [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, FAMILY_BOAR, "", "")],
    30, 800,
    [(DEVOUR_FAMILY, FAMILY_CROCOLISK_, 30, "Devour 30 crocolisks as a Baby Komodo", ""),
     (DEAL_DAMAGE, 0, 12000, "Deal 12,000 damage as a Baby Komodo", ""),
     (DEVOUR_ENTRY, 2476, 1, "Devour the Large Loch Crocolisk (Loch Modan)", "")],
    extra=[(6, 3604, helper({"RangeIndex": RANGE_ANYWHERE, "DurationIndex": DUR_6S, "SchoolMask": SCHOOL_NATURE,
                             **effects(aura(A_MOD_HEALING_PCT, -25, target=T_ENEMY))}),
            ("Septic Saliva", "", "Healing received reduced by 25%."))],
    procs=[(3, PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE, 1, 0, 0, 0, 100)],
    looks=[(994086, "Komodo Dragon Green"), (994081, "Komodo Dragon Barnacled"), (994082, "Komodo Dragon Black"),
           (994083, "Komodo Dragon Blue"), (994084, "Komodo Dragon Brown"), (994085, "Komodo Dragon Dark Blue"),
           (994087, "Komodo Dragon Gila Orange"), (994088, "Komodo Dragon Gila Yellow"),
           (994089, "Komodo Dragon Grey"), (994090, "Komodo Dragon Bright Green"), (994091, "Komodo Dragon Orange"),
           (994092, "Komodo Dragon Purple"), (994093, "Komodo Dragon Red"), (994094, "Komodo Dragon Stone"),
           (994095, "Komodo Dragon Teal"), (994096, "Komodo Dragon Yellow")],
    later_level=34,
    role="festering tank",
    changes=[
        "The grown komodo model, larger (0.55 against the baby's 0.34).",
        "Septic Saliva is the line's anti-heal: every bite leaves 25% less healing for 6 sec.",
    ])

# 30 Water Salamander (the Biletoad's second branch; owner, 2026-10-03: "b1 Good second branch very good")
E_HEAL = 10
A_WATER_BREATHING, A_MOD_SWIM_SPEED, A_MECHANIC_IMMUNITY = 82, 30, 77
SCHOOL_FIRE = 4
WATER_SALAMANDER = Evolved(
    30, "Water Salamander", 14, "Biletoad", 0, 994122, "Salamander Green",
    (34889, ability({"RangeIndex": RANGE_25, "RecoveryTime": 3000, "SchoolMask": SCHOOL_FIRE, "DurationIndex": 0,
                     "_bonus": (0, 0, 0.15, 0),
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 16, "spread": 6, "target": T_ENEMY}, gain(10))}),
     ("Steam Spit", "Spit scalding steam at an enemy up to 25 yards away: $s1 Fire damage, half again as much if it "
      "stands in water. Generates 10 Anima.", "")),
    (36398, ability({**hunger(10), "RangeIndex": RANGE_20, "RecoveryTime": 12000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_4S, "EffectMechanic_2": MECHANIC_SNARE,
                     **effects({"effect": E_PULL_TOWARDS, "misc": 200, "target": T_ENEMY},
                               aura(A_MOD_DECREASE_SPEED, -40, target=T_ENEMY))}),
     ("Undertow", "Drag an enemy up to 20 yards away to you like a current: it moves 40% slower for 4 sec.",
      "Movement slowed by 40%.")),
    (25941, gimmick(2287, 0, aura(A_WATER_BREATHING), aura(A_MOD_SWIM_SPEED, 60)),
     ("Amphibious", "You breathe under water and swim 60% faster.", "")),
    (52127, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_6S,
                     "RecoveryTime": 30000, "SchoolMask": SCHOOL_NATURE,
                     **effects(aura(A_MECHANIC_IMMUNITY, 0, MECHANIC_SNARE), aura(A_MECHANIC_IMMUNITY, 0, MECHANIC_ROOT))}),
     ("Slick Skin", "Your skin turns slick: for 6 sec nothing can slow or root you.", "Cannot be slowed or rooted.")),
    (11113, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": 0, "RecoveryTime": 15000, "SchoolMask": SCHOOL_FIRE, "_bonus": (0, 0, 0.12, 0),
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 14, "spread": 6, "target": T_SRC_CASTER,
                                "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8},
                               {"effect": E_KNOCK_BACK, "amount": 50, "misc": 80, "target": T_SRC_CASTER,
                                "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8})}),
     ("Scalding Burst", "Boil off a burst of steam: $s1 Fire damage to enemies within 8 yards, and they are blown "
      "back.", "")),
    [(CREATURE_TYPE_CRITTER, 10), (CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 6), (0, 3)],
    sk.INSECTS, 14, 550,
    [(DEVOUR_NAME, 0, 25, "Devour 25 water creatures as a Biletoad",
      "murloc|naga|crab|turtle|eel|makrura|crocolisk|fish|snapjaw|tide|water"),
     (SPELL_CAST, 9101011, 40, "Spit 40 poison darts (Poison Dart Spit)", ""),
     (DEVOUR_ENTRY, 391, 1, "Devour Old Murk-Eye (Westfall)", "")],
    scripts=[(1, "spell_devourer_steam_spit")],
    looks=[(994122, "Salamander Green"), (994121, "Salamander Blue"), (994123, "Salamander Orange"),
           (994124, "Salamander Pink"), (994125, "Salamander Purple")],
    quest=9101322,
    role="water skirmisher",
    changes=[
        "The Biletoad's second branch (the canvas's 2B), beside the Giant Marsh Frog: both can be grown, each with "
        "its own tasks and molt quest. Buying the second one with Bio Points in the menu comes later.",
        "Slick Skin makes you unable to be slowed or rooted for 6 sec (the pick's \"-30% from snares\" was unclear).",
        "Steam Spit's \"extra on wet enemies\": half again as much on an enemy standing or swimming in water.",
    ])

# 31 Snapjaw -> 32 Spikeshell (owner, 2026-10-03: "Snapjaw -> Spikeshell (think about other model)": the primal turtle,
# then the giant dragon turtle, whose spikes are in the model)
A_MOD_PACIFY = 25
FAMILY_TURTLE = 21
SNAPJAW = Evolved(
    31, "Snapjaw", 0, "", 3461, 994129, "Primal Turtle Green",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_10S,
                     **effects(hit(5), aura(A_MOD_MELEE_HASTE, -10, target=T_ENEMY), gain(10))}),
     ("Snap", "Snap your jaws shut on the enemy: weapon damage plus $s1, and it attacks 10% slower for 10 sec. "
      "Generates 10 Anima.", "Attack speed slowed by 10%.")),
    (871, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_4S,
                   "RecoveryTime": 25000, "SchoolMask": SCHOOL_PHYSICAL,
                   **effects(aura(A_DMG_TAKEN_PCT, -60, SCHOOL_ALL), aura(A_MOD_ROOT), aura(A_MOD_PACIFY))}),
     ("Withdraw", "Pull into your shell for 4 sec: damage taken reduced by 60%, but you cannot move or attack.",
      "In the shell: damage taken reduced by 60%.")),
    (25941, gimmick(1581, 0, aura(A_MOD_RESISTANCE_PCT, 15, 1), aura(A_DMG_TAKEN_PCT, -5, SCHOOL_MAGIC_ALL)),
     ("Hard Shell", "Your armor is increased by 15%, and magic hurts you 5% less.", "")),
    (1680, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                    "DurationIndex": 0, "RecoveryTime": 12000, "SchoolMask": SCHOOL_PHYSICAL,
                    "CastingTimeIndex": CAST_INSTANT,
                    **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 60, "target": T_SRC_CASTER,
                               "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8})}),
     ("Shell Spin", "Spin in your shell: 60% weapon damage to every enemy within 8 yards.", "")),
    (*charge(20000, sid(31, 6), 10),
     ("Tidal Surge", "Surge at an enemy 8 to 25 yards away like a wave, even in the middle of a fight, and knock it "
      "back. Generates 10 Anima.", "")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_CRITTER, 8), (0, 3)],
    [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, 0, "crab", "Crabs"), (0, 0, "fish", "Fish")],
    15, 0, [], family=FAMILY_TURTLE,
    extra=[(6, 6343, helper({"RangeIndex": RANGE_ANYWHERE, "DurationIndex": 0, "SchoolMask": SCHOOL_PHYSICAL,
                             **effects({"effect": E_KNOCK_BACK, "amount": 60, "misc": 120, "target": T_ENEMY})}),
            ("Tidal Surge", "", ""))],
    looks=[(994129, "Primal Turtle Green"), (994126, "Primal Turtle Blue"), (994127, "Primal Turtle Brown"),
           (994128, "Primal Turtle Dark"), (994130, "Primal Turtle Red")],
    role="shell tank",
    changes=[
        "The pick's first turtle: any creature of the Turtle family gives it (the Oasis Snapjaws of the Barrens, 15, "
        "first); the primal turtle model.",
        "Withdraw lasts its 4 sec (no second press to end it early).",
        "Hard Shell is armor and a little less magic damage: \"deflect from the front\" has no partial chance in this "
        "core (Deterrence's deflect is all or nothing).",
        "Tidal Surge is the fifth ability (level 20): a charge that knocks back.",
    ])

SPIKESHELL = Evolved(
    32, "Spikeshell", 31, "Snapjaw", 0, 994131, "Dragon Turtle",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_10S,
                     **effects(hit(9), aura(A_MOD_MELEE_HASTE, -15, target=T_ENEMY), gain(15))}),
     ("Spiked Snap", "Snap with a spiked beak: weapon damage plus $s1, and the enemy attacks 15% slower for 10 sec. "
      "Generates 15 Anima.", "Attack speed slowed by 15%.")),
    (50245, ability({**hunger(15), "RangeIndex": RANGE_COMBAT, "RecoveryTime": 18000, "DurationIndex": DUR_3S,
                     "Mechanic": MECHANIC_ROOT, "SchoolMask": SCHOOL_PHYSICAL,
                     **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 80, "target": T_ENEMY},
                               aura(A_MOD_ROOT, target=T_ENEMY))}),
     ("Snapping Lock", "Bite and hold: 80% weapon damage, and the enemy cannot move for 3 sec.", "Held fast.")),
    (25941, gimmick(1581, 0, aura(A_OBS_MOD_HEALTH, 1, period=3000)),
     ("Barnacled", "Barnacles and old scars close your wounds: you regain 1% of your maximum health every 3 sec.",
      "")),
    (6343, ability({**hunger(20), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                    "DurationIndex": DUR_8S, "RecoveryTime": 20000, "SchoolMask": SCHOOL_NATURE,
                    **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 70, "target": T_SRC_CASTER,
                               "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8},
                              aura(A_DAMAGE_SHIELD, 12, SCHOOL_NATURE_INDEX))}),
     ("Spike Burst", "Spikes burst from your shell: 70% weapon damage to enemies within 8 yards, and for 8 sec melee "
      "attackers take $s2 Nature damage.", "Spiked: attackers take $s2 Nature damage.")),
    (871, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_5S,
                   "RecoveryTime": 40000, "SchoolMask": SCHOOL_PHYSICAL,
                   **effects(aura(A_DMG_TAKEN_PCT, -70, SCHOOL_ALL), aura(A_MOD_ROOT), aura(A_MOD_PACIFY))}),
     ("Fortress Shell", "Lock yourself in for 5 sec: damage taken reduced by 70%, but you cannot move or attack.",
      "In the shell: damage taken reduced by 70%.")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 6), (0, 3)],
    [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, 0, "crab", "Crabs"), (0, 0, "fish", "Fish")],
    35, 900,
    [(DEVOUR_NAME, 0, 30, "Devour 30 turtles or crabs as a Snapjaw", "turtle|snapjaw|tortoise|crab|crawler|shell"),
     (TAKE_DAMAGE, 0, 15000, "Weather 15,000 damage as a Snapjaw", ""),
     (DEVOUR_ENTRY, 7977, 1, "Devour Gammerita (The Hinterlands)", "")],
    later_level=38,
    role="spiked tank",
    changes=[
        "The giant dragon turtle model (one look: its textures are built in).",
        "Barnacled is a slow heal all the time (the pick's \"Withdraw heals 2% a second\" would need a script on "
        "Withdraw; the steady heal does the same job for a tank).",
        "Fortress Shell is the stronger Withdraw, at level 38.",
    ])

# 33 Borer -> 34 Deep Borer (the form review's line 3, owner: "3 is good"): the retail rock worm (Rockwormlight; the
# Deep Borer wears a larger copy of it, displays of its own). Burrow sinks it (the stock Submerge visual), Erupt only
# works from under the ground and brings it up (Emerge).
A_MOD_STEALTH_DETECT = 17
FAMILY_WORM = 42
AURA_INTERRUPT_CAST = 0x4                # ends when the caster casts anything (Erupt, or any other ability)
AURA_STATE_HEALTHLESS_35 = 13            # the target is below 35% health


def burrow(shape, cooldown, speed):
    return (26234, ability({"Attributes": ATTR0_ABILITY, "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_SELF,
                            "DurationIndex": DUR_6S, "RecoveryTime": cooldown,
                            "AuraInterruptFlags": AURA_INTERRUPT_CAST,
                            **effects(aura(A_MOD_INCREASE_SPEED, speed), aura(A_MOD_UNATTACKABLE), aura(A_DUMMY))}))


def erupt(shape, weapon_pct, cooldown):
    return (66947, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "CastingTimeIndex": CAST_INSTANT,
                            "RangeIndex": RANGE_SELF, "RecoveryTime": cooldown, "DurationIndex": 0,
                            "SchoolMask": SCHOOL_PHYSICAL, "CasterAuraSpell": sid(shape, 2),
                            **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": weapon_pct,
                                       "target": T_SRC_CASTER, "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_6},
                                      {"effect": E_KNOCK_BACK, "amount": 80, "misc": 0, "target": T_SRC_CASTER,
                                       "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_6},
                                      {"effect": E_TRIGGER_SPELL, "target": T_CASTER, "trigger": sid(25, 6)})}))


BORER = Evolved(
    33, "Borer", 0, "", 11320, 994132, "Rock Worm Purple",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": sk.DUR_9S, "EffectMechanic_2": MECHANIC_BLEED,
                     **effects(hit(5), bleed(3), gain(10))}),
     ("Grinding Bite", "Grind your teeth into the enemy: weapon damage plus $s1, and it bleeds for $o2 over 9 sec. "
      "Generates 10 Anima.", "Bleeding for $s2 every 3 sec.")),
    (*burrow(33, 15000, 30),
     ("Burrow", "Sink into the ground for up to 6 sec: 30% faster, and nothing can strike you. Using any ability "
      "brings you up.", "Under the ground.")),
    (25941, gimmick(1137, 0, aura(A_MOD_STEALTH_DETECT, 30)),
     ("Tremor Sense", "You feel what walks above you: you see stealthed enemies more easily.", "")),
    (*erupt(33, 80, 6000),
     ("Erupt", "Only from under the ground: burst up and throw every enemy within 6 yards into the air for 80% "
      "weapon damage.", "")),
    (17253, ability({**hunger(10), "RangeIndex": RANGE_COMBAT, "RecoveryTime": 30000, "DurationIndex": DUR_3S,
                     "TargetAuraState": AURA_STATE_HEALTHLESS_35, "Mechanic": MECHANIC_STUN,
                     "SchoolMask": SCHOOL_PHYSICAL,
                     **effects(aura(A_MOD_STUN, target=T_ENEMY),
                               aura(A_PERIODIC_DAMAGE, 10, target=T_ENEMY, period=1000), gain(15))}),
     ("Earthen Maw", "Swallow an enemy below 35% health for 3 sec: it cannot act and takes $s2 damage every second. "
      "Generates 15 Anima.", "Swallowed.")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 8), (0, 3)],
    [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, 0, "kobold", "Kobolds")],
    13, 0, [], family=FAMILY_WORM,
    scripts=[(2, "spell_devourer_burrow")],
    looks=[(994132, "Rock Worm Purple"), (994133, "Rock Worm Green"), (994134, "Rock Worm Red")],
    role="burrowing ambusher",
    changes=[
        "The form review's line 3: any creature of the Worm family gives it (the Wetlands' Earthborers, 13, first); "
        "the retail rock worm.",
        "Burrow ends when you use any ability (Erupt is only usable from under the ground); its Submerge and Emerge "
        "are the stock spells that play the model's animations.",
        "Earthen Maw works on any enemy below 35% health (\"non-elite\" left out: the game cannot check it without a "
        "script).",
        "Tremor Sense sees stealth better at all times (\"while burrowed\" would need a script).",
    ])

DEEP_BORER = Evolved(
    34, "Deep Borer", 33, "Borer", 11789, 994136, "Deep Borer Green",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_NATURE,
                     "DurationIndex": DUR_15S, "CumulativeAura": 2,
                     **effects(hit(9), aura(A_MOD_RESISTANCE_PCT, -10, 1, target=T_ENEMY), gain(15))}),
     ("Acid Gnash", "Gnash with acid-wet teeth: weapon damage plus $s1, and the enemy's armor is eaten by 10% for "
      "15 sec, twice over. Generates 15 Anima.", "Armor reduced by 10% for each wound.")),
    (*burrow(34, 12000, 40),
     ("Burrow", "Sink into the ground for up to 6 sec: 40% faster, and nothing can strike you. Using any ability "
      "brings you up.", "Under the ground.")),
    (25941, gimmick(1137, 0, aura(A_MOD_RESISTANCE_PCT, 20, 1), aura(A_MOD_STEALTH_DETECT, 30)),
     ("Bedrock Hide", "Your armor is increased by 20%, and you see stealthed enemies more easily.", "")),
    (*erupt(34, 110, 6000),
     ("Erupt", "Only from under the ground: burst up and throw every enemy within 6 yards into the air for 110% "
      "weapon damage.", "")),
    (6343, ability({**hunger(20), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                    "DurationIndex": DUR_1500, "RecoveryTime": 30000, "Mechanic": MECHANIC_STUN,
                    "SchoolMask": SCHOOL_NATURE, "_bonus": (0, 0, 0.15, 0),
                    **effects({"effect": E_SCHOOL_DAMAGE, "amount": 20, "spread": 8, "target": T_SRC_CASTER,
                               "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8}, around(A_MOD_STUN, radius=RADIUS_8))}),
     ("Quake", "Shake the ground: $s1 Nature damage to enemies within 8 yards, and they are stunned for 1.5 sec.",
      "Stunned.")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 8), (0, 3)],
    [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, 0, "kobold", "Kobolds")],
    40, 1000,
    [(DEVOUR_FAMILY, FAMILY_WORM, 25, "Devour 25 worms as a Borer", ""),
     (TAKE_DAMAGE, 0, 20000, "Weather 20,000 damage as a Borer", ""),
     (DEVOUR_ENTRY, 14237, 1, "Devour the Oozeworm (Dustwallow Marsh)", "")],
    scripts=[(2, "spell_devourer_burrow")],
    looks=[(994136, "Deep Borer Green"), (994135, "Deep Borer Purple"), (994137, "Deep Borer Red")],
    later_level=43,
    role="burrowing bruiser",
    changes=[
        "A larger copy of the rock worm (its own displays: one look cannot belong to two forms).",
        "Quake (level 43) replaces the pick's \"tunnel line\" (a damaging line needs a script); the Jormungar step "
        "comes later with the stock Northrend jormungar.",
    ])

# --- the form review's line 4 (owner: "4 is good, maybe switch to models we already have ready"): the dragons --------
# 35 Whelp -> 36 Proto-Drake -> 37 Storm Dragon, all retail models from the owner's wow.export folder. Whelps are
# Dragonkin without a family: each whelp of the world is named (sources), and gives the colouring of its flight.
T_CONE_ENEMY = 24                        # TARGET_UNIT_CONE_ENEMY_24 (in front; spell_custom_attr 0x2 turns it behind)
CONE_BACK = 0x2                          # SPELL_ATTR0_CU_CONE_BACK
RADIUS_10, RADIUS_15 = 13, 18
CREATURE_TYPE_DRAGONKIN = 2
DRAGON_FOOD = [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, 0, "sheep", "Sheep"), (0, 0, "goat", "Goats"),
               (0, 0, "kodo", "Kodos")]
DRAGON_DIET = [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 8), (CREATURE_TYPE_DRAGONKIN, 12), (0, 3)]
W_BLACK, W_RED, W_GREEN, W_BLUE, W_BRONZE, W_PURPLE, W_WHITE, W_GEM_BLUE, W_GEM_GREEN = range(994138, 994147)
W_ARMORED, W_ARMORED_BLUE, W_NIGHTMARE = 994147, 994148, 994149
W_PROTO_RED, W_PROTO_GREEN, W_PROTO_YELLOW, W_PROTO_WHITE, W_PROTO_DARK = range(994150, 994155)


def breath(template, school, amount, spread, cooldown, anima_cost, ap, radius=RADIUS_10, **extra):
    """A cone in front of the dragon."""
    return (template, ability({**hunger(anima_cost), "Attributes": ATTR0_ABILITY, "AttributesEx": 0,
                               "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_SELF, "DurationIndex": 0,
                               "RecoveryTime": cooldown, "SchoolMask": school, "_bonus": (0, 0, ap, 0), **extra,
                               **effects({"effect": E_SCHOOL_DAMAGE, "amount": amount, "spread": spread,
                                          "target": T_CONE_ENEMY, "radius": radius})}))


WHELP = Evolved(
    35, "Whelp", 0, "", 441, 387, "Black Dragon Whelp",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 5000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": 0, **effects(hit(5), gain(10))}),
     ("Whelp Bite", "Bite with needle teeth: weapon damage plus $s1. Generates 10 Anima.", "")),
    (18500, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF, "DurationIndex": 0,
                     "RecoveryTime": 15000, "SchoolMask": SCHOOL_PHYSICAL, "CastingTimeIndex": CAST_INSTANT,
                     **effects({"effect": E_KNOCK_BACK, "amount": 60, "misc": 80, "target": T_CONE_ENEMY,
                                "radius": RADIUS_10})}),
     ("Wing Flap", "Beat your little wings: enemies in front of you within 10 yards are blown back.", "")),
    (25941, gimmick(11, 0, aura(A_MOD_DAMAGE_PCT_DONE, 5, SCHOOL_FIRE)),
     ("Dragon's Blood", "Fire answers you: your Fire damage is increased by 5%.", "")),
    (*breath(20712, SCHOOL_FIRE, 14, 6, 8000, 15, 0.15),
     ("Flame Breath", "Breathe fire on the enemies in front of you within 10 yards: $s1 Fire damage.", "")),
    (18431, ability({**hunger(20), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": DUR_3S, "RecoveryTime": 45000, "Mechanic": MECHANIC_FEAR,
                     "CastingTimeIndex": CAST_INSTANT, "SchoolMask": SCHOOL_PHYSICAL,
                     **effects(around(A_MOD_FEAR, radius=RADIUS_8))}),
     ("Tiny Roar", "A roar far bigger than you: enemies within 8 yards flee for 3 sec.", "Fleeing.")),
    DRAGON_DIET, DRAGON_FOOD, 18, 0, [],
    sources=[(441, 0), (4324, 0), (21387, 0), (22108, 0), (22130, 0), (10161, 0),
             (1042, W_RED), (1043, W_RED), (1069, W_RED), (1044, W_RED), (14022, W_RED),
             (740, W_GREEN), (741, W_GREEN), (14023, W_GREEN), (14024, W_BLUE), (14025, W_BRONZE),
             (21721, W_PURPLE), (27636, W_GEM_BLUE), (10442, W_GEM_GREEN), (2725, W_ARMORED),
             (10659, W_ARMORED_BLUE), (8319, W_NIGHTMARE), (23688, W_PROTO_RED), (23882, W_PROTO_YELLOW)],
    looks=[(W_BLACK, "Black Whelp"), (W_WHITE, "White Whelp"), (W_PROTO_GREEN, "Proto-Whelp Green"),
           (W_PROTO_WHITE, "Proto-Whelp White"), (W_PROTO_DARK, "Proto-Whelp Dark")],
    earned=[(W_RED, "Red Whelp"), (W_GREEN, "Green Whelp"), (W_BLUE, "Blue Whelp"), (W_BRONZE, "Bronze Whelp"),
            (W_PURPLE, "Netherwing Whelp"), (W_GEM_BLUE, "Ley Whelp"), (W_GEM_GREEN, "Chromatic Whelp"),
            (W_ARMORED, "Armored Whelp"), (W_ARMORED_BLUE, "Cobalt Whelp"), (W_NIGHTMARE, "Nightmare Whelp"),
            (W_PROTO_RED, "Proto-Whelp Red"), (W_PROTO_YELLOW, "Proto-Whelp Yellow")],
    later_level=24,
    role="fire-breathing skirmisher",
    changes=[
        "The form review's line 4, on the owner's ready models: the Dragonflight whelp (9 flights), the armored "
        "Cataclysm whelp, the Nightmare whelp and the proto-whelp.",
        "Whelps are Dragonkin without a family, so each whelp of the world is named: the Black Dragon Whelps of "
        "Redridge (17-18) give the form, and every other whelp gives its flight's colouring (red in the Wetlands, "
        "green in the Swamp of Sorrows, the Nightmare Whelp in the Sunken Temple, the Corrupted Whelps of Blackwing "
        "Lair, the Netherwing, Ley and Proto-Whelps ...).",
    ])

PROTO_DRAKE = Evolved(
    36, "Proto-Drake", 35, "Whelp", 0, 994158, "Proto-Drake Red",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": sk.DUR_9S, "EffectMechanic_2": MECHANIC_BLEED,
                     **effects(hit(9), bleed(5), gain(15))}),
     ("Rending Bite", "Tear into the enemy: weapon damage plus $s1, and it bleeds for $o2 over 9 sec. Generates 15 "
      "Anima.", "Bleeding for $s2 every 3 sec.")),
    (18500, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": 0, "RecoveryTime": 15000, "SchoolMask": SCHOOL_PHYSICAL,
                     "CastingTimeIndex": CAST_INSTANT,
                     **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 60, "target": T_CONE_ENEMY,
                                "radius": RADIUS_10},
                               {"effect": E_KNOCK_BACK, "amount": 80, "misc": 100, "target": T_CONE_ENEMY,
                                "radius": RADIUS_10})}),
     ("Wing Buffet", "Buffet the enemies in front of you within 10 yards: 60% weapon damage, and they are blown "
      "back.", "")),
    (25941, gimmick(1618, 0, aura(A_MOD_RESISTANCE_PCT, 15, 1), aura(A_DMG_TAKEN_PCT, -10, SCHOOL_MAGIC_ALL)),
     ("Proto Hide", "Your armor is increased by 15%, and magic hurts you 10% less.", "")),
    (*breath(16396, SCHOOL_FIRE, 30, 10, 10000, 20, 0.25, RADIUS_15),
     ("Fire Breath", "Breathe fire on the enemies in front of you within 15 yards: $s1 Fire damage.", "")),
    (15847, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": 0, "RecoveryTime": 20000, "SchoolMask": SCHOOL_PHYSICAL, "_custom": CONE_BACK,
                     "CastingTimeIndex": CAST_INSTANT,
                     **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 70, "target": T_CONE_ENEMY,
                                "radius": RADIUS_10},
                               {"effect": E_KNOCK_BACK, "amount": 80, "misc": 100, "target": T_CONE_ENEMY,
                                "radius": RADIUS_10})}),
     ("Tail Sweep", "Sweep your tail through the enemies behind you within 10 yards: 70% weapon damage, and they "
      "are knocked back.", "")),
    DRAGON_DIET, DRAGON_FOOD, 35, 1000,
    [(DEVOUR_NAME, 0, 30, "Devour 30 dragonkin as a Whelp", "whelp|drake|dragon|wyrm|scalebane|dragonspawn"),
     (DEAL_DAMAGE, 0, 15000, "Deal 15,000 damage as a Whelp", ""),
     (DEVOUR_ENTRY, 4066, 1, "Devour Nal'taszar, the rare drake of Stonetalon", "")],
    looks=[(994158, "Proto-Drake Red"), (994155, "Proto-Drake Brown"), (994156, "Proto-Drake Grey"),
           (994157, "Proto-Drake Pale"), (994159, "Proto-Drake Yellow"), (994160, "Proto-Drake Storm"),
           (994161, "Proto-Drake Fire Blue"), (994162, "Proto-Drake Fire Dark")],
    later_level=43,
    role="drake bruiser",
    changes=[
        "The retail proto-drakes (earth, air and fire models) as one form, about 7 yards long: a big mount's size, "
        "not the 20-yard drakes of the Howling Fjord.",
        "One breath (Fire) for every colouring: \"the colouring picks the element\" would need a script; later.",
        "Tail Sweep hits the cone behind the drake (spell_custom_attr 0x2).",
    ])

STORM_DRAGON = Evolved(
    37, "Storm Dragon", 36, "Proto-Drake", 0, 994163, "Void Storm Dragon",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_NATURE,
                     "DurationIndex": 0, "_bonus": (0, 0, 0.1, 0),
                     **effects(hit(12), {"effect": E_SCHOOL_DAMAGE, "amount": 10, "spread": 4, "target": T_ENEMY},
                               gain(15))}),
     ("Storm Claw", "Claws crackling with lightning: weapon damage plus $s1, and $s2 Nature damage. Generates 15 "
      "Anima.", "")),
    (24844, ability({"CastingTimeIndex": CAST_1500, "RangeIndex": RANGE_30, "RecoveryTime": 0,
                     "SchoolMask": SCHOOL_NATURE, "_bonus": (0, 0, 0.3, 0),
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 40, "spread": 10, "target": T_ENEMY}, gain(10))}),
     ("Lightning Lance", "Hurl lightning at an enemy up to 30 yards away: $s1 Nature damage. Generates 10 Anima.",
      "")),
    (25941, gimmick(62, 0, aura(A_MOD_SPELL_CRIT_CHANCE, 5), aura(A_DMG_TAKEN_PCT, -5, SCHOOL_ALL)),
     ("Void-Touched Storm", "Your spells strike critically 5% more often, and all damage hurts you 5% less.", "")),
    (*breath(22539, SCHOOL_SHADOW, 45, 15, 12000, 25, 0.3, RADIUS_15),
     ("Void Breath", "Breathe the void on the enemies in front of you within 15 yards: $s1 Shadow damage.", "")),
    (7803, ability({**hunger(25), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                    "DurationIndex": DUR_2S, "RecoveryTime": 40000, "Mechanic": MECHANIC_STUN,
                    "SchoolMask": SCHOOL_NATURE, "_bonus": (0, 0, 0.2, 0), "CastingTimeIndex": CAST_INSTANT,
                    **effects({"effect": E_SCHOOL_DAMAGE, "amount": 35, "spread": 10, "target": T_SRC_CASTER,
                               "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8}, around(A_MOD_STUN, radius=RADIUS_8))}),
     ("Thunderous Roar", "Roar like the storm: $s1 Nature damage to enemies within 8 yards, and they are stunned for "
      "2 sec.", "Stunned.")),
    DRAGON_DIET, DRAGON_FOOD, 55, 1400,
    [(DEVOUR_NAME, 0, 25, "Devour 25 dragonkin as a Proto-Drake", "whelp|drake|dragon|wyrm|scalebane|dragonspawn"),
     (SPELL_CAST, sid(36, 4), 80, "Breathe fire 80 times (Fire Breath)", ""),
     (DEVOUR_ENTRY, 2447, 1, "Devour Narillasanz (Alterac Mountains)", "")],
    later_level=60,
    role="storm caster",
    changes=[
        "The retail void storm dragon (one look, its textures are built in), about 9 yards long.",
        "Void Breath is a Shadow cone (the Devourer's void), Lightning Lance its ranged spell.",
    ])

# --- the form review's line 5 (owner: "5. good"): Owl -> Moonkin -> Moontouched Owlbeast, the canvas's line -------
# Owls are Birds of Prey like the Baby Eagle's hawks: they are named here (sources), so they give the Owl instead.
OWL_FOOD = [(CREATURE_TYPE_CRITTER, 0, "", ""), (0, 0, "rat", "Rats"), (0, 0, "mouse", "Mice"),
            (0, 0, "squirrel", "Squirrels"), (0, 0, "rabbit", "Rabbits")]

OWL = Evolved(
    38, "Owl", 0, "", 1995, 10832, "Strigid Owl",
    (50541, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 5000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": 0, **effects(hit(4), gain(10))}),
     ("Talon Rake", "Rake the enemy with your talons: weapon damage plus $s1. Generates 10 Anima.", "")),
    (1850, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_6S,
                    "RecoveryTime": 25000, "CastingTimeIndex": CAST_INSTANT, **effects(aura(A_MOD_INCREASE_SPEED, 40))}),
     ("Silent Wings", "Glide without a sound: 40% faster for 6 sec.", "40% faster.")),
    (25941, gimmick(1579, 0, aura(A_MOD_STEALTH_DETECT, 30), aura(A_MOD_CRIT_PERCENT, 2)),
     ("Night Eyes", "Nothing hides from an owl: you see stealthed enemies more easily, and your chance to strike "
      "critically is increased by 2%.", "")),
    (24423, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": DUR_10S, "RecoveryTime": 20000, "SchoolMask": SCHOOL_PHYSICAL,
                     **effects(around(A_MOD_DAMAGE_PCT_DONE, -10, SCHOOL_ALL))}),
     ("Screech", "A screech in the night: enemies within 8 yards deal 10% less damage for 10 sec.",
      "Damage dealt reduced by 10%.")),
    (*charge(20000, CHARGE_STUN, 10),
     ("Swoop", "Swoop at an enemy 8 to 25 yards away, even in the middle of a fight, and knock it down for 1.5 sec. "
      "Generates 10 Anima.", "")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_CRITTER, 10), (0, 3)], OWL_FOOD, 5, 0, [],
    sources=[(1995, 0), (7553, 0), (7555, 6299), (7097, 4877), (7455, 6212), (22265, 10831), (21450, 20293)],
    earned=[(6299, "Hawk Owl"), (4877, "Ironbeak Owl"), (6212, "Winterspring Owl"), (10831, "Shadowwing Owl"),
            (20293, "Skethyl Owl")],
    role="night hunter",
    changes=[
        "The canvas's line (Strigid Owl -> Moonkin -> Moontouched Owlbeast). Owls are named creatures here: the "
        "Strigid Owls of Teldrassil (5-6) give the form, the other owls of the world their own colouring.",
        "The game's owl model (no retail owl was exported); the Moonkin and the Owlbeast are retail models.",
    ])

MOONKIN = Evolved(
    39, "Moonkin", 38, "Owl", 10158, 994164, "Moonkin Violet",
    (5176, ability({"CastingTimeIndex": CAST_1500, "RangeIndex": RANGE_30, "RecoveryTime": 0,
                    "SchoolMask": SCHOOL_NATURE, "_bonus": (0, 0, 0.25, 0),
                    **effects({"effect": E_SCHOOL_DAMAGE, "amount": 20, "spread": 6, "target": T_ENEMY}, gain(10))}),
     ("Wrath", "Hurl the wrath of the wild at an enemy up to 30 yards away: $s1 Nature damage. Generates 10 Anima.",
      "")),
    (8921, ability({**hunger(10), "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_30, "RecoveryTime": 6000,
                    "SchoolMask": SCHOOL_ARCANE, "DurationIndex": DUR_12S, "_bonus": (0, 0, 0.12, 0.03),
                    **effects({"effect": E_SCHOOL_DAMAGE, "amount": 12, "spread": 4, "target": T_ENEMY},
                              aura(A_PERIODIC_DAMAGE, 4, target=T_ENEMY, period=3000))}),
     ("Moonfire", "Burn an enemy with moonlight: $s1 Arcane damage, and $o2 more over 12 sec.",
      "$s2 Arcane damage every 3 sec.")),
    (25941, gimmick(111, 0, aura(A_MOD_SPELL_CRIT_CHANCE, 5), aura(A_MOD_RESISTANCE_PCT, 20, 1)),
     ("Moonkin Aura", "The moon looks after its own: your spells strike critically 5% more often, and your armor is "
      "increased by 20%.", "")),
    (2912, ability({**hunger(25), "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_30, "RecoveryTime": 10000,
                    "SchoolMask": SCHOOL_ARCANE, "_bonus": (0, 0, 0.35, 0),
                    **effects({"effect": E_SCHOOL_DAMAGE, "amount": 32, "spread": 10, "target": T_ENEMY})}),
     ("Starsurge", "Call a star down on an enemy up to 30 yards away: $s1 Arcane damage.", "")),
    (50516, ability({**hunger(20), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": 0, "RecoveryTime": 20000, "SchoolMask": SCHOOL_NATURE,
                     "CastingTimeIndex": CAST_INSTANT, "_bonus": (0, 0, 0.15, 0),
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 18, "spread": 6, "target": T_CONE_ENEMY,
                                "radius": RADIUS_15},
                               {"effect": E_KNOCK_BACK, "amount": 80, "misc": 60, "target": T_CONE_ENEMY,
                                "radius": RADIUS_15})}),
     ("Typhoon", "A gale in front of you: enemies within 15 yards take $s1 Nature damage and are blown back.", "")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 6), (0, 3)], OWL_FOOD, 20, 700,
    [(DEVOUR_NAME, 0, 25, "Devour 25 owls, owlkin or moonkin as an Owl", "owl|moonkin|wildkin"),
     (SPELL_CAST, sid(38, 4), 40, "Screech 40 times", ""),
     (DEVOUR_ENTRY, 10157, 1, "Devour the Moonkin Oracle (Darkshore)", "")],
    looks=[(994164, "Moonkin Violet"), (994165, "Moonkin Dusk"), (994166, "Moonkin Dawn"), (994167, "Moonkin Moss"),
           (994168, "Moonkin Ash")],
    later_level=26,
    role="moon caster",
    changes=[
        "Tindral's moonkin from the owner's exports, with its five colourings (body and eyes paired).",
        "A caster like the Baby Wind Serpent: its numbers grow with attack power.",
    ])

MOONTOUCHED_OWLBEAST = Evolved(
    40, "Moontouched Owlbeast", 39, "Moonkin", 7453, 994169, "Owlbeast Brown",
    (6807, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 5000, "SchoolMask": SCHOOL_PHYSICAL,
                    "DurationIndex": 0, **effects(hit(10), gain(15))}),
     ("Moonclaw", "A heavy, moonlit swipe: weapon damage plus $s1. Generates 15 Anima.", "")),
    (99, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                  "DurationIndex": DUR_10S, "RecoveryTime": 15000, "SchoolMask": SCHOOL_PHYSICAL,
                  **effects(around(A_MOD_MELEE_HASTE, -15))}),
     ("Lunar Roar", "Roar at the moon: enemies within 8 yards attack 15% slower for 10 sec.",
      "Attack speed slowed by 15%.")),
    (25941, gimmick(1562, 0, aura(A_MOD_RESISTANCE_PCT, 25, 1), aura(A_OBS_MOD_HEALTH, 1, period=3000)),
     ("Moontouched Hide", "Your armor is increased by 25%, and you regain 1% of your maximum health every 3 sec.",
      "")),
    (779, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                   "DurationIndex": 0, "RecoveryTime": 8000, "SchoolMask": SCHOOL_PHYSICAL,
                   **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 70, "target": T_SRC_CASTER,
                              "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8})}),
     ("Swipe", "Swipe at everything around you: 70% weapon damage to every enemy within 8 yards.", "")),
    (22842, ability({**hunger(20), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": 0, "RecoveryTime": 60000, "SchoolMask": SCHOOL_ARCANE,
                     **effects({"effect": E_HEAL_PCT, "amount": 25, "target": T_CASTER})}),
     ("Moonlit Mend", "Let the moon close your wounds: you are healed for 25% of your maximum health.", "")),
    [(CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 8), (0, 3)], OWL_FOOD, 45, 1200,
    [(DEVOUR_NAME, 0, 30, "Devour 30 owlbeasts, wildkin or moonkin as a Moonkin", "owlbeast|wildkin|moonkin"),
     (SPELL_CAST, sid(39, 1), 100, "Cast Wrath 100 times", ""),
     (DEVOUR_ENTRY, 7453, 1, "Devour a Moontouched Owlbeast (Winterspring)", "")],
    looks=[(994169, "Owlbeast Brown"), (994170, "Owlbeast Black"), (994171, "Owlbeast Blue"),
           (994172, "Owlbeast Green"), (994173, "Owlbeast White")],
    later_level=52,
    role="moon bruiser",
    changes=[
        "The canvas's tier 3. The retail owlbear model (five colourings) in place of the old upright owlbeast.",
    ])

# --- the form review's line 7 (owner: "Voidcreeper make its own branch, and brood themed") -----------------------
# 41 Voidling -> 42 Voidcreeper -> 43 Voidcreeper Broodmother. A Brood Devourer's hatchlings are voidlings in every
# step; the creepers burrow and erupt like the borers (the same Burrow script).
CREATURE_TYPE_DEMON_ = 3
VOIDLING_LOOK = 994176
VOID_NAMES = "void|nether|voidwalker|voidspawn|voidcaller|voidwraith"
VOID_DIET = [(CREATURE_TYPE_DEMON_, 12), (CREATURE_TYPE_BEAST, 10), (CREATURE_TYPE_HUMANOID, 8), (0, 3)]
VOID_FOOD = [(CREATURE_TYPE_DEMON_, 0, "", ""), (0, 0, "void", "Void creatures"), (0, 0, "nether", "Nether creatures")]


def shadow_bite(points, dot, anima, duration=DUR_12S):
    return ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_SHADOW,
                    "DurationIndex": duration, "_bonus": (0, 0, 0, 0.02),
                    **effects(hit(points), aura(A_PERIODIC_DAMAGE, dot, target=T_ENEMY, period=3000), gain(anima))})


VOIDLING = Evolved(
    41, "Voidling", 0, "", 17887, VOIDLING_LOOK, "Voidling",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 5000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": 0, **effects(hit(4), gain(10))}),
     ("Void Nibble", "Nibble at the enemy with a mouth that should not be there: weapon damage plus $s1. Generates "
      "10 Anima.", "")),
    (1850, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                    "DurationIndex": DUR_2S, "RecoveryTime": 20000, "CastingTimeIndex": CAST_INSTANT,
                    **effects(aura(A_MOD_INCREASE_SPEED, 50), aura(A_MOD_UNATTACKABLE))}),
     ("Phase Shift", "Slip halfway out of the world for 2 sec: 50% faster, and nothing can strike you.",
      "Out of phase.")),
    (25941, gimmick(213, 0, aura(A_MOD_DAMAGE_PCT_DONE, 5, SCHOOL_SHADOW)),
     ("Hungry Void", "The void in you is hungry too: your Shadow damage is increased by 5%.", "")),
    (7588, ability({"CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_25, "RecoveryTime": 4000,
                    "SchoolMask": SCHOOL_SHADOW, "_bonus": (0, 0, 0.12, 0),
                    **effects({"effect": E_SCHOOL_DAMAGE, "amount": 14, "spread": 4, "target": T_ENEMY}, gain(10))}),
     ("Void Spit", "Spit a gob of void at an enemy up to 25 yards away: $s1 Shadow damage. Generates 10 Anima.", "")),
    (50245, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": DUR_3S, "RecoveryTime": 25000, "Mechanic": MECHANIC_ROOT,
                     "SchoolMask": SCHOOL_SHADOW, **effects(around(A_MOD_ROOT, radius=RADIUS_8))}),
     ("Void Tendrils", "Tendrils of void hold every enemy within 8 yards in place for 3 sec.", "Held by the void.")),
    VOID_DIET, VOID_FOOD, 5, 0, [],
    sources=[(17887, 0), (17550, 0), (17981, 0)],
    role="void imp",
    changes=[
        "The form review's line 7, its own Brood-themed branch: the retail baby voidwalker. The Void Critters of "
        "Bloodmyst Isle (3) give it, and so do the Void Anomalies there and the Voidspawn of Outland.",
        "A Brood Devourer's hatchlings are voidlings in every step of this line (devourer_shape.brood_display).",
        "The pick's void eggs and growing voidlings need module code: later.",
    ])

VOIDCREEPER = Evolved(
    42, "Voidcreeper", 41, "Voidling", 0, 994177, "Voidcreeper Blue",
    (17253, shadow_bite(7, 4, 15),
     ("Creeper Fang", "Sink void-wet fangs into the enemy: weapon damage plus $s1, and $o2 Shadow damage over "
      "12 sec. Generates 15 Anima.", "$s2 Shadow damage every 3 sec.")),
    (*burrow(42, 15000, 30),
     ("Burrow", "Sink into the ground for up to 6 sec: 30% faster, and nothing can strike you. Using any ability "
      "brings you up.", "Under the ground.")),
    (25941, gimmick(213, 0, aura(A_DMG_TAKEN_PCT, -5, SCHOOL_ALL), aura(A_MOD_DAMAGE_PCT_DONE, 5, SCHOOL_ALL)),
     ("Brood Bond", "The brood is one body: you take 5% less damage and deal 5% more.", "")),
    (*erupt(42, 90, 6000),
     ("Ambush from Below", "Only from under the ground: burst up and throw every enemy within 6 yards into the air "
      "for 90% weapon damage.", "")),
    (50245, ability({**hunger(15), "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_SELF,
                     "DurationIndex": DUR_3S, "RecoveryTime": 20000, "Mechanic": MECHANIC_ROOT,
                     "SchoolMask": SCHOOL_SHADOW,
                     **effects(aura(A_MOD_ROOT, target=T_CONE_ENEMY, radius=RADIUS_10))}),
     ("Void Web", "Spray void webbing: enemies in front of you within 10 yards cannot move for 3 sec.", "Webbed.")),
    VOID_DIET, VOID_FOOD, 20, 700,
    [(DEVOUR_NAME, 0, 25, "Devour 25 void creatures as a Voidling", VOID_NAMES),
     (SPELL_CAST, sid(41, 4), 60, "Spit void 60 times (Void Spit)", ""),
     (DEVOUR_ENTRY, 17550, 1, "Devour a Void Anomaly (Bloodmyst Isle)", "")],
    scripts=[(2, "spell_devourer_burrow")],
    looks=[(994177, "Voidcreeper Blue"), (994178, "Voidcreeper Red"), (994179, "Voidcreeper Yellow")],
    brood=VOIDLING_LOOK,
    later_level=28,
    role="void ambusher",
    changes=[
        "The retail voidcreeper (three colourings); Burrow and Ambush from Below work like the Borer's.",
    ])

VOIDCREEPER_BROODMOTHER = Evolved(
    43, "Voidcreeper Broodmother", 42, "Voidcreeper", 0, 994174, "Broodmother Blue",
    (17253, shadow_bite(11, 7, 15),
     ("Rending Mandibles", "Tear with mandibles of void: weapon damage plus $s1, and $o2 Shadow damage over 12 sec. "
      "Generates 15 Anima.", "$s2 Shadow damage every 3 sec.")),
    (*burrow(43, 12000, 40),
     ("Burrow", "Sink into the ground for up to 6 sec: 40% faster, and nothing can strike you. Using any ability "
      "brings you up.", "Under the ground.")),
    (25941, gimmick(1581, 0, aura(A_MOD_RESISTANCE_PCT, 20, 1), aura(A_OBS_MOD_HEALTH, 1, period=3000)),
     ("Broodmother's Carapace", "Your armor is increased by 20%, and you regain 1% of your maximum health every "
      "3 sec.", "")),
    (*erupt(43, 120, 6000),
     ("Brood Eruption", "Only from under the ground: burst up and throw every enemy within 6 yards into the air for "
      "120% weapon damage.", "")),
    (16914, ability({**hunger(25), "CastingTimeIndex": CAST_INSTANT, "RangeIndex": RANGE_30, "RecoveryTime": 30000,
                     "DurationIndex": DUR_6S, "SchoolMask": SCHOOL_SHADOW, "_bonus": (0, 0, 0, 0.05),
                     "ChannelInterruptFlags": 0, "AttributesEx": 0,
                     **effects({"effect": E_PERSISTENT_AREA_AURA, "aura": A_PERIODIC_DAMAGE, "amount": 12,
                                "period": 1000, "target": T_DEST_TARGET_ANY, "radius": RADIUS_8})}),
     ("Call the Swarm", "A swarm of voidlings boils out of the ground up to 30 yards away: for 6 sec, enemies there "
      "take $s1 Shadow damage every second.", "In the swarm.")),
    VOID_DIET, VOID_FOOD, 40, 1200,
    [(DEVOUR_NAME, 0, 30, "Devour 30 void creatures as a Voidcreeper", VOID_NAMES),
     (TAKE_DAMAGE, 0, 20000, "Weather 20,000 damage as a Voidcreeper", ""),
     (DEVOUR_ENTRY, 2337, 1, "Devour a Dark Strand Voidcaller (Ashenvale)", "")],
    scripts=[(2, "spell_devourer_burrow")],
    looks=[(994174, "Broodmother Blue"), (994175, "Broodmother Orange")],
    brood=VOIDLING_LOOK,
    later_level=48,
    role="brood tank",
    changes=[
        "The retail vicious voidcreeper with its saddle hidden (model tool, Parts), two colourings.",
        "Broodmother's Call (voidlings that fixate and explode) needs module code: Call the Swarm stands in for it.",
    ])

# The forms of this file, in molt-quest order (the tier-2 forms keep the quest ids they were given first).
FORMS = [GREATER_PLAINSTRIDER, BLOODSNOUT_WORG, RAGING_AGAMAR, SHADOWCLAW, ROCKJAW_BACKBREAKER, VAMPIRIC_DUSKBAT,
         ARCANE_WRAITH, ROYAL_BLUE_FLUTTERER, VOID_TERROR, VIPER, BABY_WIND_SERPENT, BABY_EAGLE, BABY_KOMODO,
         KOMODO_DRAGON, WATER_SALAMANDER, SNAPJAW, SPIKESHELL, BORER, DEEP_BORER, WHELP, PROTO_DRAKE, STORM_DRAGON,
         OWL, MOONKIN, MOONTOUCHED_OWLBEAST, VOIDLING, VOIDCREEPER, VOIDCREEPER_BROODMOTHER]


class Growth:
    """An evolution into a form made elsewhere (e.g. into the CoA Sethrak, shape 1)."""

    def __init__(self, parent, parent_name, shape, name, level, bp, tasks):
        self.parent, self.parent_name, self.shape, self.name = parent, parent_name, shape, name
        self.level, self.bp, self.tasks = level, bp, tasks
        self.quest = 0


# Owner, 2026-10-03: "Viper -> wind serpent -> Sethrak -> xxx" (a fourth step later).
EXTRA_GROWTH = [
    Growth(26, "Baby Wind Serpent", 1, "Sethrak", 44, 1400,
           [(DEVOUR_NAME, 0, 20, "Devour 20 Sandfury trolls or sand beasts as a Baby Wind Serpent",
             "sandfury|basilisk|dune|sand "),
            (SPELL_CAST, sid(26, 1), 80, "Breathe lightning 80 times (Lightning Breath)", ""),
            (DEVOUR_ENTRY, 7273, 1, "Devour Gahz'rilla (Zul'Farrak)", "")]),
]

EXTRA_GROWTH[0].quest = 9101324          # the Sethrak's molt quest, given before the dragons came (keep it)

# Task 018: every evolution of this file gets a molt quest, in this order (tools/witch_sisters.py builds them).
MOLTS = [f for f in FORMS if f.parent] + EXTRA_GROWTH
_taken = {m.quest for m in MOLTS if m.quest}
_next = MOLT_QUEST_FIRST
for _m in MOLTS:                         # quests already given keep their ids (they may sit in quest logs)
    while not _m.quest:
        if _next not in _taken:
            _m.quest = _next
        _next += 1
MOLTS.sort(key=lambda m: m.quest)
assert [m.quest for m in MOLTS] == list(range(MOLT_QUEST_FIRST, MOLT_QUEST_FIRST + len(MOLTS))), "molt quests must be in one run"


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
         (f"{f.name} Form", (f"Take the shape of the {f.name.lower()}, grown out of your {f.parent_name.lower()}: "
                             if f.parent else f"Take the shape of a {f.name.lower()} you have devoured: ") +
          f"{names[0]}, {names[1]}, {names[2]} and {gim[2][0]}; {five[2][0]} opens at level {f.later_level}. All "
          "shapes share one cooldown.", f"Wearing the {f.name.lower()}'s shape.")),
        (f.base + 1, 1, *one),
        (f.base + 2, 1, *two),
        (f.base + 3, 1, *gim),
        (f.base + 4, 1, *four),
        (f.base + 5, f.later_level, five[0], {**five[1], "SpellLevel": f.later_level, "BaseLevel": f.later_level},
         five[2]),
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
            if key.startswith("_"):                  # "_bonus": spell_bonus_data, not a Spell.dbc column
                continue
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
    bonus = [(spell, *o["_bonus"]) for spell, _, _, o, _ in defs if "_bonus" in o]
    custom = [(f.base, 0x01000000) for f in FORMS] + \
        [(spell, o["_custom"]) for spell, _, _, o, _ in defs if "_custom" in o]   # e.g. 0x2: a cone behind
    others = sorted({m.shape for m in MOLTS if not FIRST_SHAPE <= m.shape})   # growth into older shapes (Sethrak)
    other_sql = f" OR `to_shape` IN ({', '.join(map(str, others))})" if others else ""

    sql = [
        "-- Generated by tools/evolved_kit.py (task 017). Do not edit by hand: change the script and run it again.",
        f"-- The evolved forms and new lines: spells {FIRST}-{LAST}, shapes {lo}-{hi}, their evolutions (and the ones",
        "-- into older shapes).",
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
        ",\n".join(f"({spell}, {attrs:#010x})" for spell, attrs in custom) + ";",
        "-- The gimmicks that answer to hits (Cooldown = their rest, Chance = how often).",
        f"DELETE FROM `spell_proc` WHERE `SpellId` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_proc` (`SpellId`, `SchoolMask`, `SpellFamilyName`, `SpellFamilyMask0`, `SpellFamilyMask1`,"
        " `SpellFamilyMask2`, `ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`, `HitMask`, `AttributesMask`,"
        " `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`) VALUES",
        ",\n".join(f"({s}, 0, 0, 0, 0, 0, {flags}, {types}, {2 if flags & DONE_PROCS else 0}, {hits}, 0, 0, {chance},"
                   f" {cd}, {charges})" for s, flags, types, hits, cd, charges, chance in procs) + ";",
        "-- Abilities that grow with attack power (the form review, 2026-10-03: numbers that keep up past level 20).",
        f"DELETE FROM `spell_bonus_data` WHERE `entry` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_bonus_data` (`entry`, `direct_bonus`, `dot_bonus`, `ap_bonus`, `ap_dot_bonus`, `comments`)"
        " VALUES",
        ",\n".join(f"({s}, {d}, {dot}, {ap}, {apdot}, 'mod-devourer')" for s, d, dot, ap, apdot in bonus) + ";",
        "",
        f"-- Shapes {lo}-{hi}: spell_3 is the fourth ability, spell_4 the fifth (opens at its spell level: 20, or later for later forms).",
        f"DELETE FROM `devourer_shape` WHERE `shape_id` BETWEEN {lo} AND {hi};",
        "INSERT INTO `devourer_shape` (`shape_id`, `name`, `form_spell`, `display_id`, `scale`, `spell_1`, `spell_2`,"
        " `spell_3`, `spell_4`, `passive`, `brood_display`) VALUES",
        ",\n".join(f"({f.shape}, {q(f.name)}, {f.base}, {f.look}, {f.scale}, {f.base + 1}, {f.base + 2}, {f.base + 4},"
                   f" {f.base + 5}, {f.base + 3}, {f.brood or f.display})" for f in FORMS) + ";",
        "-- A new line's first form is devoured: any creature of its family gives it (each look a colouring).",
        f"DELETE FROM `devourer_shape_family` WHERE `shape_id` BETWEEN {lo} AND {hi};",
        "INSERT INTO `devourer_shape_family` (`family`, `shape_id`) VALUES",
        ",\n".join(f"({f.family}, {f.shape})" for f in FORMS if f.family) + ";",
        "-- ...or named creatures give it (a kind without a family: the Dragonkin whelps), each with its colouring.",
        f"DELETE FROM `devourer_shape_source` WHERE `shape_id` BETWEEN {lo} AND {hi};",
        "INSERT INTO `devourer_shape_source` (`creature_entry`, `shape_id`, `display_id`) VALUES",
        ",\n".join(f"({entry}, {f.shape}, {display})" for f in FORMS for entry, display in f.sources) + ";",
        f"DELETE FROM `devourer_skin` WHERE `shape_id` BETWEEN {lo} AND {hi};",
        "-- free = 1: comes with the shape (the retail looks, and the creature's own look beside them).",
        "INSERT INTO `devourer_skin` (`display_id`, `shape_id`, `name`, `brood_display`, `free`) VALUES",
        ",\n".join([f"({f.display}, {f.shape}, {q(f.skin)}, 0, {1 if f.looks else 0})" for f in FORMS]
                   + [f"({d}, {f.shape}, {q(n)}, 0, 1)" for f in FORMS for d, n in f.looks if d != f.display]
                   + [f"({d}, {f.shape}, {q(n)}, 0, 0)" for f in FORMS for d, n in f.earned]) + ";",
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
        f"DELETE FROM `devourer_evolution` WHERE `to_shape` BETWEEN {lo} AND {hi}{other_sql};",
        "INSERT INTO `devourer_evolution` (`from_shape`, `to_shape`, `bp`, `min_level`, `any_task`, `quest`) VALUES",
        ",\n".join(f"({m.parent}, {m.shape}, {m.bp}, {m.level}, 1, {m.quest})" for m in MOLTS) + ";",
        "-- The name lists of the devour-by-name tasks need more room than the frog line's 100 characters.",
        "ALTER TABLE `devourer_evolution_task` MODIFY COLUMN `name_part` VARCHAR(255) NOT NULL DEFAULT '' COMMENT "
        "'kind 5: the meal''s name holds one of these (|-separated)';",
        f"DELETE FROM `devourer_evolution_task` WHERE `to_shape` BETWEEN {lo} AND {hi}{other_sql};",
        "INSERT INTO `devourer_evolution_task` (`to_shape`, `task_id`, `kind`, `value`, `count`, `text`, `name_part`)"
        " VALUES",
        ",\n".join(f"({m.shape}, {i}, {kind}, {value}, {count}, {q(text)}, {q(parts)})"
                   for m in MOLTS for i, (kind, value, count, text, parts) in enumerate(m.tasks, 1)) + ";",
        "",
    ]
    OUT_SQL.write_bytes("\n".join(sql).encode("utf-8"))

    md = ["# Evolved forms and new lines (tasks 017-018)",
          "",
          "Generated by `tools/evolved_kit.py` — edit the script, not this file. Design: the owner's canvas \"Canvas "
          "Evolutions for Devourer\", Section 1 (the \"A\" branch of each starter line) and the Warp Stalker's line; "
          "the form review's picks (2026-10-03) for the new lines. Numbers are a first pass.",
          "",
          f"Spell ids {FIRST}-{LAST}: shape s uses {FIRST} + (s-16)*10 + slot (slot 0 form, 1-2 abilities, 3 passive, "
          "4 ability, 5 ability that opens later, 6-9 spells the kit casts).",
          "",
          "A tier-2 form is not devoured: it grows out of its line's form (`devourer_evolution`) once that form has "
          "the Bio Points, the Devourer the level, and **any one** of the three tasks is done (the canvas rule). "
          "Then the molt quest (task 018) comes into the log: handing it in to Wren in the In-Between is the "
          "evolution. The earlier form stays. A new line's first form is devoured, from any creature of its family.",
          "",
          "| Shape | Form | Comes from | Level | Bio Points | Role |",
          "|---|---|---|---|---|---|"]
    md += [f"| {f.shape} | {f.name} | {f.parent_name or (f'devouring (family {f.family})' if f.family else 'devouring')} | {f.level} | {f.bp or '-'} "
           f"| {f.role} |" for f in FORMS]
    md += [f"| {m.shape} | {m.name} | {m.parent_name} | {m.level} | {m.bp} | (an older form) |" for m in EXTRA_GROWTH]
    md.append("")
    for m in EXTRA_GROWTH:
        md.append(f"### {m.name} (shape {m.shape}, now also grows out of the {m.parent_name}, quest {m.quest})")
        md.append("")
        md += [f"- {text}" for kind, value, count, text, parts in m.tasks]
        md.append("")
    for f in FORMS:
        md.append(f"### {f.name} (shape {f.shape}, " + (f"grows out of the {f.parent_name})" if f.parent else
                                                        f"devoured: any creature of family {f.family})" if f.family
                                                        else f"devoured: {len(f.sources)} kinds of creature)"))
        if f.looks:
            md.append(f"Look: a retail model, base {f.look} (`{f.looks[0][1]}`); its other colourings come with the "
                      "shape: " + ", ".join(f"{d} `{n}`" for d, n in f.looks[1:]) + f". The creature's own look "
                      f"(creature {f.creature}, display {f.display}, `{f.skin}`) comes with it too. Any one task:")
        else:
            md.append(f"Look: creature {f.creature}, display {f.display} (skin `{f.skin}`). Any one task:")
        if f.earned:
            md.append("Colourings to earn, each from devouring its creature: " +
                      ", ".join(f"{d} `{n}`" for d, n in f.earned) + ".")
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
