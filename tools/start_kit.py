#!/usr/bin/env python3
"""Tasks 006 + 007: the Devourer's start -- base kit (Rush, Anima; Concentrate left in task 015), trainers, eight starting forms.

    python tools/start_kit.py --spell-dbc <server>/data/dbc/Spell.dbc

One source for two outputs, keep them in step by running this script again after any change:
  data/sql/db-world/2026_09_30_08_devourer_start.sql   spells (spell_dbc; the client patch tool reads them from
                                                       here), form bindings, shapes, colourings, trainers
  docs/start-kit.md                                    what every spell does, ids, levels, costs

Spells are cloned from stock 3.3.5a spells (their visuals and icons) and overridden field by field with the
helpers of tools/coa/build_devourer_spells.py. The committed SQL holds only the finished rows, no Blizzard file.

Ids (all inside the Devourer's reserved spell range 9100000-9100999; 9100900+ so that 2026_09_30_02, which clears
9100000-9100899 when it runs again, never touches them):
  9100990-9100993   the base kit every Devourer has from level 1: Rush, Rush's hit, Anima (9100992 was Concentrate, removed in task 015) (the
                    hidden passive that keeps Anima from draining away out of combat)
                    (9100900-9100909 were the true-form kit, parked in commit fdf67e9: the true form comes later)
  9100910-9100989   starting forms: shape s (5-12) uses 9100910 + (s - 5) * 10 + slot
  9101000-9101099   later forms with their own block (owner, 2026-10-01): shape 13 Warp Stalker 9101000-9101009
                    (the witch sisters' intro form); the frog line (owner, 2026-10-02, canvas "to be devoured"):
                    shape 14 Biletoad 9101010-9101019 (Wren's pest chore), shape 15 Giant Marsh Frog 9101020-9101029
                    (grows out of the Biletoad)
                    slot 0 form, 1-2 abilities, 3 passive, 4-5 abilities that open at levels 10 and 20,
                    6-9 helper spells the kit casts (task 009: Pup Bite, Poised to Strike, Silken Cocoon ...)
  Task 009: a starting form is a kind of creature (devourer_shape_family: any creature of that family gives it,
  every look a colouring) with a favourite food (devourer_favourite_food); both tables are created here.
  shapes 5-12, trainer 9101200 (what the Devourer's trainers teach; the trainers themselves are the witch
  sisters of task 010, tools/witch_sisters.py)
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
FIRST, LAST = 9100900, 9101029     # 9101030-9101059: talent helpers (tools/placeholders.py), never delete them here

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
# (the module: Devourer.AnimaPerShift; devouring and own swings gather it), Rush needs no target.
RUSH, RUSH_HIT, ANIMA = 9100990, 9100991, 9100993   # 9100992 was Concentrate (task 015: replaced by the pet)
SNIFF = 9100995                     # task 013: toggle that marks prey on the client (module: DevourerSniff.cpp)
STRIDE = 9100994                    # owner, 2026-10-03: every shape runs 15% faster (the module adds it)
A_MOD_SPEED_ALWAYS = 129            # stacks with a shape's own speed bonus (MOD_INCREASE_SPEED takes the highest)
ATTR0_CANT_CANCEL = 0x80000000
A_INTERRUPT_REGEN = 94                 # the core skips rage decay out of combat while a unit has it
DUR_1S, DMG_MELEE, A_MOD_STUN, MECHANIC_STUN = b.DUR_1S, b.DMG_MELEE, b.A_MOD_STUN, b.MECHANIC_STUN

# --- task 009 (starter forms batch 1) ---------------------------------------------------------------------------
E_HEALTH_LEECH, E_JUMP_DEST, E_SANCTUARY = 9, 42, 79
A_MOD_STEALTH, A_SCHOOL_IMMUNITY, A_FEATHER_FALL = 16, 39, 144
A_SCHOOL_ABSORB, A_PROC_TRIGGER_SPELL, A_MOD_DAMAGE_PCT_DONE = b.A_SCHOOL_ABSORB, b.A_PROC_TRIGGER_SPELL, 79
T_CASTER_AREA_PARTY, T_DEST_TARGET_FRONT = 20, 64
RANGE_20, RANGE_5_15, RANGE_ANYWHERE = 3, 179, 13
RADIUS_20 = 9
DUR_3S, DUR_12S = 27, 29
SCHOOL_NONE_MASK = 0
DMG_MAGIC = b.DMG_MAGIC
# Proc flags (spell_proc.ProcFlags / Spell.ProcTypeMask) and hit masks (spell_proc.HitMask).
PROC_DONE_MELEE, PROC_TAKEN_MELEE, PROC_DONE_SPELL_MELEE, PROC_TAKEN_SPELL_MELEE = 0x4, 0x8, 0x10, 0x20
PROC_DONE_SPELL_MAGIC = 0x10000
HIT_DODGE, HIT_PARRY = 0x10, 0x20
ATTR0_NOT_IN_COMBAT = 0x10000000
CREATURE_TYPE_BEAST, CREATURE_TYPE_ELEMENTAL, CREATURE_TYPE_CRITTER = 1, 4, 8
FAMILY_WOLF, FAMILY_CAT, FAMILY_SPIDER, FAMILY_BOAR, FAMILY_CROCOLISK, FAMILY_SCORPID, FAMILY_MOTH = 1, 2, 3, 5, 6, 20, 37
FAMILY_TALLSTRIDER = 12


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
        "CastingTimeIndex": CAST_INSTANT, "DurationIndex": 0, "RangeIndex": RANGE_SELF, "Speed": 0.0,
        "SpellClassSet": 90, "SpellClassMask_1": 0x400,              # task 015: Shapeless Step shortens its cooldown
        "InterruptFlags": 0,                                         # owner, 2026-10-03: usable while running
        "ChannelInterruptFlags": 0, "AuraInterruptFlags": 0, "RecoveryTime": 8000, **GCD,
        "SpellVisualID_1": 0, **effects({"effect": E_DUMMY})},
     ("Rush", "Rush 20 yards straight ahead, even on the run. Every enemy in your path takes 50% "
      "weapon damage and is knocked down for 1 sec. Needs no target.", "")),
    (RUSH_HIT, 1, None, CHARGE_STUN, {                               # the knock-down, like Overrun's
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "SchoolMask": SCHOOL_PHYSICAL, "DefenseType": DMG_MELEE,
        "PreventionType": 2, "DurationIndex": DUR_1S, "Mechanic": MECHANIC_STUN, "RangeIndex": 13,
        **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 50, "target": T_ENEMY},
                  aura(A_MOD_STUN, target=T_ENEMY))},
     ("Rush", "", "Knocked down.")),
    (STRIDE, 1, None, 2983, {                                        # Sprint's icon; worn with every shape
        **CLEAN, **NO_MECHANICS, "Attributes": ATTR0_ABILITY | ATTR0_CANT_CANCEL, "AttributesEx": 0,
        "AttributesEx2": 0, "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
        "RecoveryTime": 0, "StartRecoveryCategory": 0, "StartRecoveryTime": 0, "InterruptFlags": 0,
        "AuraInterruptFlags": 0, "SpellVisualID_1": 0, "SpellVisualID_2": 0,    # task 016: no Sprint visual
        **effects(aura(A_MOD_SPEED_ALWAYS, 15))},
     ("Shape's Stride", "Every shape runs 15% faster.", "Movement speed increased by 15%.")),
    (SNIFF, 1, 0, 1494, {                                            # Track Beasts' icon; the module scans and marks
        **CLEAN, **NO_MECHANICS, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "AttributesEx3": 0, "Targets": 0, "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_INFINITE,
        "RangeIndex": RANGE_SELF, "RecoveryTime": 1000, "StartRecoveryCategory": 0, "StartRecoveryTime": 0,
        "InterruptFlags": 0, "ChannelInterruptFlags": 0, "AuraInterruptFlags": 0,
        **effects(aura(A_DUMMY))},
     ("Sniff", "Toggle: while on, creatures within 40 yards that would give you a new shape or colouring are "
      "marked with a gold star, and your worn shape's favourite food with a green triangle (on nameplates and "
      "the target frame).", "Sniffing out prey.")),
    (ANIMA, 1, None, 25941, {
        **CLEAN, **PASSIVE, **NO_MECHANICS, "Attributes": ATTR0_ABILITY | b.ATTR0_PASSIVE | b.ATTR0_HIDDEN,
        **effects(aura(A_INTERRUPT_REGEN))},
     ("Anima", "Your anima does not drain away while you rest.", "")),
]


# --- task 007: the eight starting forms ----------------------------------------------------------------------------
class Form:
    def __init__(self, shape, name, zone, source, display, icon, colourings, diet, skin, one, two, passive_,
                 later, family=0, food=(), extra=(), changes=(), base=0, scale=1, how="", looks=(), keep_look=False):
        self.shape, self.name, self.zone, self.source, self.display, self.icon = shape, name, zone, source, display, icon
        self.colourings = colourings          # [(creature entry, display, skin name)]
        self.diet = diet                      # [(creature type, bp)]
        self.skin = skin                      # the base look's name for .devour skin
        # passive_: (aura, amount, misc, texts) for a plain passive, or (template, overrides, texts) for a full
        # spell. later: two names (placeholders), or two (template, overrides, texts).
        self.one, self.two, self.passive, self.later = one, two, passive_, later
        self.base = base or FIRST + 10 + (shape - 5) * 10   # later forms bring their own block
        self.family = family                  # task 009: any creature of this creature_template.family gives it
        self.food = list(food)                # task 009: [(creature type, family, name part, label)] -> 2x BP
        self.extra = list(extra)              # task 009: [(slot 6-9, template, overrides, texts)] helper spells
        self.changes = list(changes)          # task 009: what changed against the canvas card, and why
        self.scale = scale                    # devourer_shape.scale (the frogs' model is critter-sized)
        self.how = how                        # how it is gained when no creature gives it (source 0)
        # Task 017 (owner, 2026-10-03: "newer models especially for the older forms"): retail models brought in with
        # the model tool (tools/modeltool, imports.json): [(display, colouring name)], the first is the new base look.
        # They come with the shape (devourer_skin.free); the old base look stays, as a colouring that comes with it too.
        self.looks = list(looks)
        self.keep_look = keep_look            # the looks are only colourings: the base look stays (the frog line)

    @property
    def look(self):
        """The base look the shape shows (devourer_shape.display_id)."""
        return self.looks[0][0] if self.looks and not self.keep_look else self.display


def sid(shape, slot):
    """A starting form's spell id: shape 5-12, slot 0-9."""
    return FIRST + 10 + (shape - 5) * 10 + slot


# Task 009: creatures of a form's family that are not that body (another model, or a ghost). They give no shape:
# devourer_shape_source rows with shape 0. (entry, why)
NOT_THAT_BODY = [
    (21952, "Lobo (Wolf family): a translucent ghost wolf"),
    (29452, "Vargul Blighthound (Wolf family): a mage hunter model, not a wolf"),
    (29889, "Vargul Blighthound (Wolf family): a mage hunter model, not a wolf"),
    (19023, "Stabled Tallstrider (Cat family): a tallstrider model"),
    (19024, "Stabled Boar (Cat family): a boar model"),
    (19025, "Stabled Bear (Cat family): a bear model"),
    (19026, "Stabled Raptor (Cat family): a raptor model"),
]

# spell_proc rows of the batch-1 kits: (spell, proc flags, spell type mask, hit mask, cooldown ms, charges)
PROCS = [
    (sid(5, 3), PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE, 1, 0, 15000, 0),                     # Pack Prowess
    (sid(7, 3), PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, 0, HIT_DODGE | HIT_PARRY, 20000, 0),  # Shadow Reflexes
    (sid(7, 6), PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE | PROC_DONE_SPELL_MAGIC, 1, 0, 0, 1),   # Poised to Strike
    (sid(9, 3), PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, 1, 0, 0, 0),                       # Barbed Bristles
]
# The module's scripts on them (src/DevourerForms.cpp).
SCRIPTS = [
    (sid(5, 3), "spell_devourer_pack_prowess"),
    (sid(5, 5), "spell_devourer_ravaging_feast"),
    (sid(7, 1), "spell_devourer_anima_shred"),
    (sid(7, 2), "spell_devourer_phase_prowl"),
    (sid(8, 3), "spell_devourer_cocoon"),
    (sid(9, 3), "spell_devourer_barbed_bristles"),
]


def proc_passive(icon, procs, *effs):
    """A batch-1 gimmick: a passive whose aura procs (spell_proc above) or is scripted."""
    return {**CLEAN, **PASSIVE, **NO_MECHANICS, "SpellIconID": icon, "ProcTypeMask": procs, "ProcChance": 100,
            **effects(*effs)}


def helper(fields: dict) -> dict:
    """A spell the kit casts by itself: instant, no cooldown, no global cooldown."""
    return {**CLEAN, **NO_MECHANICS, "Attributes": 0, "AttributesEx": 0, "AttributesEx2": 0,
            "CastingTimeIndex": CAST_INSTANT, "RecoveryTime": 0, "StartRecoveryCategory": 0, "StartRecoveryTime": 0,
            "AuraInterruptFlags": 0, "InterruptFlags": 0, "ChannelInterruptFlags": 0, **fields}


WOLF = Form(
    5, "Wolf", "Northshire", 299, 31049, 1573, [(69, 31048, "Timber"), (1508, 447, "Scavenger")],
    [(1, 10), (0, 3)], "Grey",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_9S, "EffectMechanic_2": MECHANIC_BLEED,
                     **effects(hit(3), aura(A_PERIODIC_DAMAGE, 2, target=T_ENEMY, period=3000), gain(15))}),
     ("Tear Throat", "Tear at the enemy's throat: weapon damage plus $s1, and it bleeds for $o2 over 9 sec. "
      "Generates 15 Anima.", "Bleeding for $s2 every 3 sec.")),
    (49376, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_5_15, "RecoveryTime": 15000,
                     "DurationIndex": DUR_4S, "SchoolMask": SCHOOL_PHYSICAL, "AuraInterruptFlags": 0,
                     "InterruptFlags": 0, "EffectMechanic_2": MECHANIC_SNARE,
                     **effects({"effect": E_JUMP_DEST, "target": T_DEST_TARGET_FRONT, "misc": 5, "miscB": 150},
                               aura(A_MOD_DECREASE_SPEED, -50, target=T_ENEMY)),
                     "EffectMultipleValue_1": 4.0}),
     ("Hungering Lunge", "Leap at an enemy 5 to 15 yards away and bite at its legs: its movement is slowed by 50% "
      "for 4 sec.", "Movement slowed by 50%.")),
    (25941, proc_passive(1573, PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE, aura(A_DUMMY)),
     ("Pack Prowess", "Your strikes on an enemy below 30% health call two spectral wolf pups to your side for "
      "6 sec. Their bites open bleeding wounds. Once every 15 sec.", "")),
    [(24604, ability({**hunger(10), "RangeIndex": RANGE_SELF, "DurationIndex": DUR_15S, "RecoveryTime": 60000,
                      **effects(aura(A_MOD_MELEE_HASTE, 10, target=T_CASTER_AREA_PARTY, radius=RADIUS_20))}),
      ("Howl of the Pack", "Howl for the hunt: you and your group within 20 yards attack 10% faster for 15 sec.",
       "Attack speed increased by 10%.")),
     (6785, ability({"AttributesEx": 0, "RangeIndex": RANGE_COMBAT, "RecoveryTime": 12000,
                     "SchoolMask": SCHOOL_PHYSICAL, **effects({"effect": E_DUMMY, "target": T_ENEMY})}),
      ("Ravaging Feast", "Feast on the enemy's open wounds: your bleeds on it close at once, and you are healed for "
       "all the damage they had left to do, plus 3% of your maximum health for each.", ""))],
    family=FAMILY_WOLF,
    food=[(0, FAMILY_BOAR, "", ""), (0, FAMILY_CROCOLISK, "", "")],
    extra=[(6, 17253, helper({"RangeIndex": RANGE_20, "DurationIndex": DUR_6S, "CumulativeAura": 2,
                              "SchoolMask": SCHOOL_PHYSICAL, "EffectMechanic_1": MECHANIC_BLEED,
                              **effects(aura(A_PERIODIC_DAMAGE, 2, target=T_ENEMY, period=2000))}),
            ("Pup Bite", "", "Bleeding for $s1 every 2 sec."))],
    changes=[
        "Any wolf-like creature (creature family Wolf: wolves, worgs, dire wolves) gives the form; every look is a "
        "colouring named after the creature (owner, 2026-10-01).",
        "Howl of the Pack is only a haste howl now: the card had \"AoE disorient & haste\", two jobs in one button. "
        "The disorient went, the haste fits an executioner. It reaches the group (\"of the Pack\"), 10% for 15 sec.",
        "Tear Throat is the builder: +15 Anima as on the card, with a short bleed.",
        "Ravaging Feast needs bleeds to eat (Tear Throat, the pups' bites): it closes them and heals for what they "
        "had left, plus 3% health each, so it rewards bleeding first instead of being a free heal.",
        "Pack Prowess pups are short (6 sec) with a 15 sec rest, so a level-1 wolf cannot keep a pack up.",
        "Hungering Lunge: a 15 yard leap (5-15 yards) and a 50% slow for 4 sec; usable in combat.",
    ])

SABER = Form(
    7, "Saber", "Shadowglen", 2031, 11454, 103, [(15366, 15507, "Springpaw"), (15372, 15506, "Lynx")],
    [(1, 10), (0, 3)], "Nightsaber",
    (5221, ability({"AttributesEx": 0, "RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000,
                    "SchoolMask": SCHOOL_PHYSICAL, **effects(hit(4), gain(10))}),
     ("Anima Shred", "Shred the enemy: weapon damage plus $s1. Generates 10 Anima, 20 when you strike from behind.",
      "")),
    (5215, {**CLEAN, "RecoveryTime": 10000, **GCD},                 # Prowl keeps its stealth, slow and rules
     ("Phase Prowl", "Slip between shadow and anima: unseen, but 30% slower. Your first strike out of it deals "
      "50% more damage. Cannot be used in combat.", "Unseen.")),
    (25941, proc_passive(103, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE,
                         aura(A_PROC_TRIGGER_SPELL, trigger=sid(7, 7))),
     ("Shadow Reflexes", "When you dodge or parry an attack, you slip out of the fight and back into Phase Prowl. "
      "Once every 20 sec.", "")),
    [(1079, ability({**hunger(30), "AttributesEx": 0, "RangeIndex": RANGE_COMBAT, "RecoveryTime": 0,
                     "DurationIndex": DUR_12S, "SchoolMask": SCHOOL_PHYSICAL, "EffectMechanic_1": MECHANIC_BLEED,
                     **effects(aura(A_PERIODIC_DAMAGE, 5, target=T_ENEMY, period=2000))}),
      ("Essence Rend", "A finishing rend that spends your stored anima: the enemy bleeds for $o1 over 12 sec.",
       "Bleeding for $s1 every 2 sec.")),
     (36563, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": RANGE_20, "RecoveryTime": 20000,
                      "DurationIndex": 0, "SchoolMask": SCHOOL_PHYSICAL,
                      **effects({"effect": 5, "target": T_CASTER, "targetB": 65, "radius": 7})}),
      ("Flicker Step", "Flicker through the shadows to an enemy within 20 yards and appear behind it.", ""))],
    family=FAMILY_CAT,
    looks=[(994036, "Dreamsaber"), (994037, "Dreamsaber Green"), (994038, "Lynx Black"), (994039, "Lynx Brown"),
           (994040, "Lynx Pale"), (994041, "Sabertooth Beige"), (994042, "Sabertooth Brown"),
           (994043, "Sabertooth Dark"), (994044, "Sabertooth Light"), (994045, "Sabertooth Red"),
           (994046, "Sabertooth Spotted"), (994047, "Sabertooth Striped Grey"),
           (994048, "Sabertooth Striped Orange"), (994049, "Sabertooth Striped White"),
           (994050, "Sabertooth Striped Yellow"), (994190, "Haranir Cat Tan"),
           (994191, "Haranir Cat Black"), (994192, "Haranir Cat Blue"), (994193, "Haranir Cat Purple"),
           (994194, "Haranir Cat Red")],
    food=[(0, FAMILY_CAT, "", ""), (0, FAMILY_SPIDER, "", "")],
    extra=[(6, 25941, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_5S, "SpellIconID": 103,
                              "ProcTypeMask": PROC_DONE_MELEE | PROC_DONE_SPELL_MELEE | PROC_DONE_SPELL_MAGIC,
                              "ProcChance": 100, "ProcCharges": 1,
                              **effects(aura(A_MOD_DAMAGE_PCT_DONE, 50, SCHOOL_ALL), aura(A_DUMMY))}),
            ("Poised to Strike", "", "Your next strike deals 50% more damage.")),
           (7, 1856, helper({"RangeIndex": RANGE_SELF, "DurationIndex": 0,
                             **effects({"effect": E_SANCTUARY, "target": T_CASTER},
                                       {"effect": E_TRIGGER_SPELL, "target": T_CASTER, "trigger": sid(7, 2)})}),
            ("Shadow Reflexes", "", ""))],
    changes=[
        "Nightsaber is now Saber (same shape id 7): any creature of the Cat family gives it (sabers, lynxes, "
        "lions, tigers); every look is a colouring.",
        "Phase Prowl is an own spell (stealth and slow from Prowl, no cat-form requirement); its opener bonus is "
        "\"Poised to Strike\": 50% more damage on the first strike out of it, for up to 5 sec.",
        "Shadow Reflexes (the dodge/parry reset) has a 20 sec rest: on every dodge it would make the saber "
        "untouchable. It leaves the fight like a vanish, then prowls again.",
        "Anima Shred works from any side (a level-1 builder that needs the enemy's back cannot be used alone: "
        "the enemy always faces you); from behind it gives the card's 20 Anima, else 10.",
        "Essence Rend has no combo points (the Devourer has none): it is the Anima spender, 30 Anima.",
        "Flicker Step: 20 yards, appears behind the enemy (sets up the 20-Anima Shred).",
    ])

MOTH = Form(
    8, "Moth", "Ammen Vale", 16520, 17574, 109, [], [(1, 10), (0, 3)], "Vale",
    (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_NATURE,
                     **effects({"effect": E_HEALTH_LEECH, "amount": 6, "spread": 2, "target": T_ENEMY}, gain(10)),
                     "EffectMultipleValue_1": 1.0}),
     ("Siphon Proboscis", "Pierce the enemy and drink its life: $s1 Nature damage, and you are healed for as much. "
      "Generates 10 Anima.", "")),
    (8921, ability({"Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": 0, "RecoveryTime": 8000,
                    "SchoolMask": SCHOOL_ARCANE,
                    **effects({"effect": E_SCHOOL_DAMAGE, "amount": 6, "spread": 3, "target": T_SRC_CASTER,
                               "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8}, gain(5))}),
     ("Luminescent Pulse", "Your wings flare with moonlight: $s1 Arcane damage to enemies within 8 yards. "
      "Generates 5 Anima.", "")),
    (25941, proc_passive(109, 0, aura(A_SCHOOL_ABSORB, 0, SCHOOL_ALL)),
     ("Cocoon Metamorphosis", "When a blow would drop you below 25% health, silk wraps you in a cocoon: for 3 sec "
      "nothing can harm you and you regain 30% of your maximum health, but you cannot act. Once per fight.", "")),
    [(770, ability({**hunger(10), "AttributesEx": 0, "RangeIndex": RANGE_20, "DurationIndex": DUR_6S,
                    "RecoveryTime": 30000, "SchoolMask": SCHOOL_NATURE,
                    **effects(aura(A_MOD_HIT_CHANCE, -20, target=T_ENEMY))}),
      ("Blinding Spores", "Shake blinding spores into the enemy's eyes: it misses 20% more often for 6 sec.",
       "Chance to hit reduced by 20%.")),
     (2983, ability({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_6S, "RecoveryTime": 30000,
                     **effects(aura(A_MOD_INCREASE_SPEED, 60), aura(A_FEATHER_FALL))}),
      ("Flutter Dash", "Beat your wings and glide: movement speed increased by 60%, and you fall slowly, for 6 sec.",
       "Movement speed increased by 60%. Falling slowly."))],
    family=FAMILY_MOTH,
    looks=[(994007, "Underlight Teal"), (994001, "Underlight Orange"), (994002, "Underlight Pink"),
           (994003, "Underlight Red"), (994004, "Underlight Rockblue"), (994005, "Underlight Rockbrown"),
           (994006, "Underlight Rockred")],
    food=[(CREATURE_TYPE_BEAST, 0, "", "")]
         + [(CREATURE_TYPE_ELEMENTAL, 0, part, "Plants") for part in
            ("lasher", "treant", "sapling", "shrub", "vine", "thorn", "petal", "root", "moss", "spore", "thistle")],
    extra=[(6, 28622, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_3S, "SchoolMask": SCHOOL_NATURE,
                              **effects(aura(A_MOD_STUN), aura(A_SCHOOL_IMMUNITY, 0, SCHOOL_ALL),
                                        aura(A_OBS_MOD_HEALTH, 10, period=1000))}),
            ("Silken Cocoon", "", "Wrapped in silk: nothing can harm you, and you regain 10% health every second."))],
    changes=[
        "Any creature of the Moth family gives the form; every look is a colouring.",
        "Blinding Spores: 20% more misses for 6 sec instead of the card's 60% (far too strong at level 1).",
        "Luminescent Pulse is moonlight (Arcane), with Moonfire's beam on every enemy hit (the owner's older moth "
        "idea), instead of Holy/Nature.",
        "Cocoon Metamorphosis works once per fight (it resets when you leave combat): every time, it would make the "
        "moth unkillable. It also catches a killing blow.",
        "Favourite food \"Elemental [Plant] OR Beast\": 3.3.5 has no plant type. Chosen: any Beast, plus "
        "Elementals whose name says plant (lasher, treant, sapling, shrub, vine, thorn, petal, root, moss, spore, "
        "thistle: Bloodpetal, Withervine, Thistleshrub, Warpwood Treant ...).",
        "Siphon Proboscis is the builder: it drinks (damage that heals you) and gives 10 Anima.",
    ])

BOAR = Form(
    9, "Boar", "Valley of Trials", 3098, 503, 1578, [(1984, 8869, "Thistle"), (113, 0, "")],
    [(1, 10), (0, 3)], "Mottled",
    (35290, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_15S, "CumulativeAura": 5,
                     **effects(hit(3), aura(A_MOD_RESISTANCE_PCT, -4, 1, target=T_ENEMY), gain(10))}),
     ("Gore", "Gore the enemy with your tusks: weapon damage plus $s1, and its armor is torn by 4% for 15 sec, "
      "up to 5 times. Generates 10 Anima.", "Armor reduced by 4% for each wound.")),
    (100, {**CLEAN, **NO_MECHANICS, "Attributes": 0x20040010, "RecoveryTime": 20000, **GCD,
           **effects({"effect": E_CHARGE, "target": T_ENEMY}, gain(15),
                     {"effect": E_TRIGGER_SPELL, "target": T_ENEMY, "trigger": CHARGE_STUN})},
     ("Primal Charge", "Charge an enemy 8 to 25 yards away, even in the middle of a fight, and knock it down for "
      "1.5 sec. Generates 15 Anima.", "")),
    (25941, proc_passive(1578, PROC_TAKEN_MELEE | PROC_TAKEN_SPELL_MELEE, aura(A_DUMMY)),
     ("Barbed Bristles", "Your barbed bristles return 15% of the melee damage you take to the attacker as Nature "
      "damage.", "")),
    [(22812, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_4S,
                      "RecoveryTime": 45000, "SchoolMask": SCHOOL_PHYSICAL,
                      **effects(aura(A_DMG_TAKEN_PCT, -30, SCHOOL_ALL))}),
      ("Thick Hide", "Your hide hardens: damage taken reduced by 30% for 4 sec.", "Damage taken reduced by 30%.")),
     (845, ability({**hunger(10), "Attributes": ATTR0_ABILITY, "RangeIndex": RANGE_COMBAT, "RecoveryTime": 8000,
                    "SchoolMask": SCHOOL_PHYSICAL, **effects({**hit(4), "chain": 3})}),
      ("Tusk Sweep", "Sweep your tusks: weapon damage plus $s1 to the enemy and up to 2 others beside it.", ""))],
    family=FAMILY_BOAR,
    food=[(CREATURE_TYPE_CRITTER, 0, "", ""), (0, FAMILY_SCORPID, "", "")],
    extra=[(6, 17253, helper({"RangeIndex": RANGE_ANYWHERE, "DurationIndex": 0, "SchoolMask": SCHOOL_NATURE,
                              "DefenseType": DMG_MAGIC, "SpellVisualID_1": 0,
                              **effects({"effect": E_SCHOOL_DAMAGE, "amount": 1, "target": T_ENEMY})}),
            ("Barbed Bristles", "", ""))],
    changes=[
        "Any creature of the Boar family gives the form; every look is a colouring.",
        "\"Thickened Rind\" is now Thick Hide (a rind is fruit peel); -30% damage only for 4 sec.",
        "Primal Charge is usable in combat (not a copy of the warrior's Charge; Rush already covers moving out of "
        "combat). It carries the gimmick's \"charging builds Anima\": 15 Anima.",
        "Gore is the builder (+10 Anima) and tears armor (4% a wound, up to 5).",
        "Barbed Bristles answers melee hits only (\"physical damage\" from a level-1 enemy is melee).",
    ])


# Owner, 2026-10-01: a new form for the witch sisters' intro (the Baby Berserker's ported model crashes the client).
# The Warp Stalker: any creature of the warp stalker family (32, all 20 wear its model) gives it.
WARP = Form(13, "Warp Stalker", "the In-Between (the witch sisters' ritual), or any warp stalker in Outland", 18464,
            20025, 1499, [], [(1, 10), (0, 3)], "Warp Stalker",
            (17253, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                             **effects(hit(4), gain(5))}),
             ("Warp Bite", "Bite through the space between: weapon damage plus $s1. Generates 5 Anima.", "")),
            (1953, {**CLEAN, "RecoveryTime": 15000, **GCD},                 # Blink keeps its own effects and rules
             ("Warp", "Blink up to 20 yards forward, slipping out of stuns and roots, then run 50% faster for "
                      "3 sec.", "")),
            (A_MOD_DODGE_PERCENT, 3, 0, ("Phasing Hide", "Your body is never quite where it seems: chance to dodge "
                                         "increased by 3%.", "")),
            ("Tail Lash", "Warp Ambush"), family=32, base=9101000,
            # Owner, 2026-10-03: a speed boost after the blink (spell_devourer_warp casts it).
            extra=[(6, 2983, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_3S,
                                     **effects(aura(A_MOD_INCREASE_SPEED, 50))}),
                    ("Warp Surge", "", "Movement speed increased by 50%."))])

# --- the frog line (owner, 2026-10-02, Parrot\to be devoured.canvas): Tier 1 and 2 now, the Huge Toad later ---------
E_HEAL_PCT, E_PULL_TOWARDS, DUR_2S = 136, b.E_PULL_TOWARDS, b.DUR_2S
RADIUS_6 = 29
RANGE_15, RANGE_25, RANGE_8_25 = 11, 34, 95
MECHANIC_DAZE = 27
SWAMP_HOP_SPLASH, SWAMP_HOP_KNOCKDOWN = 9101016, 9101017      # Biletoad slots 6-7: cast by Swamp Hop on landing
BELLY_FLOP_SLAM = 9101026                                     # Giant Marsh Frog slot 6: cast by Belly Flop on landing
INSECTS = [(CREATURE_TYPE_CRITTER, 0, "", "")] + \
    [(CREATURE_TYPE_BEAST, fam, "", "Insects") for fam in (FAMILY_SPIDER, FAMILY_SCORPID, FAMILY_MOTH)] + \
    [(CREATURE_TYPE_BEAST, 0, part, "Insects") for part in ("beetle", "scarab", "roach", "locust", "fly")]


def leap(template, range_index, cooldown, school):
    """A leap at an enemy, as Hungering Lunge's; the module's script splashes where it lands."""
    return (template, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RangeIndex": range_index,
                               "RecoveryTime": cooldown, "SchoolMask": school, "AuraInterruptFlags": 0,
                               "InterruptFlags": 0,
                               **effects({"effect": E_JUMP_DEST, "target": T_DEST_TARGET_FRONT, "misc": 5,
                                          "miscB": 150}),
                               "EffectMultipleValue_1": 4.0}))


BILETOAD = Form(
    14, "Biletoad", "the In-Between (Wren Hollowmoor's chore \"Pests in the Cells\")", 0, 1924, 1987, [],
    [(CREATURE_TYPE_CRITTER, 10), (CREATURE_TYPE_BEAST, 10), (0, 3)], "Biletoad",
    (16552, ability({"RangeIndex": RANGE_25, "RecoveryTime": 6000, "SchoolMask": SCHOOL_NATURE,
                     "DurationIndex": DUR_9S,
                     **effects({"effect": E_SCHOOL_DAMAGE, "amount": 5, "spread": 2, "target": T_ENEMY},
                               aura(A_PERIODIC_DAMAGE, 2, target=T_ENEMY, period=3000), gain(5))}),
     ("Poison Dart Spit", "Spit a poisoned dart: $s1 Nature damage, and $o2 more over 9 sec. Generates 5 Anima.",
      "$s2 Nature damage every 3 sec.")),
    (36398, ability({"RangeIndex": RANGE_20, "RecoveryTime": 12000, "SchoolMask": SCHOOL_PHYSICAL,
                     "DurationIndex": DUR_4S, "EffectMechanic_2": MECHANIC_SNARE,
                     **effects({"effect": E_PULL_TOWARDS, "misc": 200, "target": T_ENEMY},
                               aura(A_MOD_DECREASE_SPEED, -50, target=T_ENEMY))}),
     ("Tongue Pull", "Shoot your sticky tongue at an enemy up to 20 yards away and pull it to you: its movement is "
      "slowed by 50% for 4 sec.", "Movement slowed by 50%.")),
    None,
    [(*leap(49376, RANGE_5_15, 15000, SCHOOL_NATURE),
      ("Swamp Hop", "Hop onto an enemy 5 to 15 yards away. Where you land, poison splashes over every enemy within "
       "5 yards: Nature damage, more over 6 sec, and they are knocked down for 1 sec.", "")),
     (22686, ability({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_6S, "RecoveryTime": 20000,
                      "Mechanic": MECHANIC_DAZE, **effects(around(A_MOD_DECREASE_SPEED, -50, radius=RADIUS_8))}),
      ("Croak of Disorientation", "A deep, booming croak: enemies within 8 yards are dazed, their movement slowed by "
       "50% for 6 sec.", "Dazed."))],
    food=INSECTS,
    extra=[(6, 10251, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_6S, "SchoolMask": SCHOOL_NATURE,
                              **effects({"effect": E_SCHOOL_DAMAGE, "amount": 4, "spread": 2, "target": T_SRC_CASTER,
                                         "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_5},
                                        around(A_PERIODIC_DAMAGE, 2, radius=RADIUS_5, period=2000))}),
            ("Swamp Hop", "", "$s2 Nature damage every 2 sec.")),
           (7, CHARGE_STUN, helper({"DurationIndex": DUR_1S, "Mechanic": MECHANIC_STUN, "RangeIndex": RANGE_ANYWHERE,
                                    "SchoolMask": SCHOOL_PHYSICAL, **effects(aura(A_MOD_STUN, target=T_ENEMY))}),
            ("Swamp Hop", "", "Knocked down."))],
    base=9101010, scale=5.5,
    # Owner, 2026-10-03 ("use the coloring we have models from"): retail frogs as colourings that come with it.
    looks=[(994099, "Dart Frog Green"), (994097, "Dart Frog Blue"), (994098, "Dart Frog Gold"),
           (994100, "Dart Frog Red"), (994101, "Dart Frog Yellow"), (994104, "Swamp Toad Green"),
           (994102, "Swamp Toad Blue"), (994103, "Swamp Toad Dark"), (994105, "Swamp Toad Light"),
           (994106, "Swamp Toad Orange"), (994107, "Swamp Toad Yellow")], keep_look=True,
    how="Not given by devouring: **Wren Hollowmoor's chore \"Pests in the Cells\"** (In-Between, after the three "
        "intro chores) turns the Devourer into a Biletoad when it is accepted.",
    changes=[
        "No passive: the card lists four abilities, and its signature (Sticky Tongue Grapple) is Tongue Pull.",
        "Swamp Hop knocks down for 1 sec where it lands: the Giant Marsh Frog's growth task \"Land 25 Hop "
        "knockdowns\" needs a knockdown to count.",
        "Swamp Hop opens at level 10 and Croak at 20, like every form's third and fourth ability.",
        "Not given by devouring Biletoads in the world: the canvas says Wren's chore gives it.",
    ])

GIANT_MARSH_FROG = Form(
    15, "Giant Marsh Frog", "grows out of the Biletoad", 0, 21950, 2379, [],
    [(CREATURE_TYPE_CRITTER, 10), (CREATURE_TYPE_BEAST, 10), (0, 3)], "Giant Marsh Frog",
    (32906, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 8000, "SchoolMask": SCHOOL_PHYSICAL,
                     **effects(hit(6), {"effect": E_HEAL_PCT, "amount": 8, "target": T_CASTER}, gain(5))}),
     ("Gorging Chomp", "Chomp down on the enemy: weapon damage plus $s1, and you are healed for 8% of your maximum "
      "health. Generates 5 Anima.", "")),
    (*leap(49376, RANGE_8_25, 20000, SCHOOL_PHYSICAL),
     ("Belly Flop", "Leap at an enemy 8 to 25 yards away and slam down belly first: every enemy within 6 yards takes "
      "damage equal to 10% of your maximum health and is knocked down for 2 sec.", "")),
    None,
    [(27807, ability({"RangeIndex": RANGE_15, "RecoveryTime": 12000, "SchoolMask": SCHOOL_NATURE,
                      "DurationIndex": DUR_15S,
                      **effects({"effect": E_SCHOOL_DAMAGE, "amount": 10, "spread": 4, "target": T_ENEMY},
                                aura(A_MOD_RESISTANCE_PCT, -25, 1, target=T_ENEMY))}),
      ("Acid Vomit", "Vomit burning acid over an enemy: $s1 Nature damage, and its armor is reduced by 25% for "
       "15 sec.", "Armor reduced by 25%.")),
     (49822, ability({"Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0, "AttributesEx3": 0,
                      "DispelType": 0, "RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S, "RecoveryTime": 60000,
                      **effects(aura(A_SCHOOL_ABSORB, 4000, SCHOOL_ALL))}),
      ("Inflate", "Puff yourself up: absorbs 4000 damage for 10 sec.", "Absorbs damage."))],
    extra=[(6, 27862, helper({"RangeIndex": RANGE_SELF, "DurationIndex": DUR_2S, "Mechanic": MECHANIC_STUN,
                              "SchoolMask": SCHOOL_PHYSICAL,
                              **effects({"effect": E_SCHOOL_DAMAGE, "amount": 1, "target": T_SRC_CASTER,
                                         "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_6},
                                        around(A_MOD_STUN, radius=RADIUS_6))}),
            ("Belly Flop", "", "Knocked down."))],
    base=9101020, scale=5.5,
    looks=[(994111, "Primal Toad Green"), (994108, "Primal Toad Black"), (994109, "Primal Toad Blue"),
           (994110, "Primal Toad Gold"), (994112, "Primal Toad Orange"), (994113, "Primal Toad Red"),
           (994114, "Ardenweald Toad Black"), (994115, "Ardenweald Toad Blue"),
           (994116, "Ardenweald Toad Dark Blue"), (994117, "Ardenweald Toad Fawn"), (994118, "Ardenweald Toad Teal"),
           (994119, "Ardenweald Toad Violet"), (994120, "Frogduck")], keep_look=True,
    how="Grows out of the **Biletoad** (`devourer_evolution`): 550 Bio Points, level 14, and any one of its three "
        "tasks (devour 30 murlocs or swamp beasts, pull 40 enemies with Tongue Pull, land 25 Swamp Hop knockdowns).",
    changes=[
        "No passive: the card lists four abilities, and its signature is Belly Flop.",
        "Belly Flop deals 10% of maximum health (the card: \"damage based on max HP\").",
        "Inflate keeps the card's 4,000 absorb: a lot at level 14-20, for the owner to tune.",
    ])

FORMS = [
    WOLF,
    Form(6, "Trogg", "Coldridge Valley", 707, 606, 93, [], [(7, 10), (0, 3)], "Rockjaw",
         (6552, ability({"RangeIndex": RANGE_COMBAT, "RecoveryTime": 6000, "SchoolMask": SCHOOL_PHYSICAL,
                        **effects(hit(5), gain(5))}),
          ("Stone Fist", "Hammer the enemy with a fist of stone: weapon damage plus $s1. Generates 5 Anima.", "")),
         (20594, ability({**hunger(10), "RangeIndex": RANGE_SELF, "DurationIndex": DUR_10S, "RecoveryTime": 30000,
                         **effects(aura(A_DMG_TAKEN_PCT, -10, SCHOOL_ALL))}),
          ("Stoneskin", "Your hide turns to stone: damage taken reduced by 10% for 10 sec.", "Damage taken reduced by 10%.")),
         (A_MOD_RESISTANCE_PCT, 10, 1, ("Thick Skull", "Your armor is increased by 10%.", "")),
         ("Rock Hurl", "Tunnel Rage")),
    SABER,
    MOTH,
    BOAR,
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
         ("Peck", "Stampede"), family=FAMILY_TALLSTRIDER,    # 2026-10-03: every strider, each look a colouring
         looks=[(994015, "Primal Pink"), (994012, "Primal Black"), (994013, "Primal Blue"), (994014, "Primal Green"),
                (994016, "Primal Red"), (994017, "Primal White"), (994180, "Hawkstrider Black"),
                (994181, "Hawkstrider Blue"), (994182, "Hawkstrider Green"), (994183, "Hawkstrider Purple"),
                (994184, "Hawkstrider Red"), (994185, "Hawkstrider White")]),
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
         ("Sonic Burst", "Night Swarm"),
         looks=[(994025, "Vampire Purple"), (994024, "Vampire Green"), (994026, "Vampire Red"),
                (994027, "Vampire Stone")]),
    WARP,
    BILETOAD,
    GIANT_MARSH_FROG,
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
         ("Mana Tap", "Arcane Coil"),
         looks=[(994018, "Wyrm Blue"), (994019, "Wyrm Green"), (994020, "Wyrm Purple"), (994021, "Wyrm Red"),
                (994022, "Wyrm Void"), (994023, "Wyrm White")]),
]

# The frog line's scripts (src/DevourerFrogs.cpp).
SCRIPTS += [
    (BILETOAD.base + 2, "spell_devourer_tongue_pull"),
    (BILETOAD.base + 4, "spell_devourer_frog_leap"),
    (SWAMP_HOP_SPLASH, "spell_devourer_swamp_hop_splash"),
    (GIANT_MARSH_FROG.base + 2, "spell_devourer_frog_leap"),
    (BELLY_FLOP_SLAM, "spell_devourer_belly_flop_slam"),
    (WARP.base + 2, "spell_devourer_warp"),
]


def form_spells(f: Form):
    """(id, level, template, overrides, texts) for one form: form, 2 abilities, passive, 2 later abilities, then
    the helper spells (task 009)."""
    one_t, one_o, one_x = f.one
    two_t, two_o, two_x = f.two
    if f.passive is None:                                            # the frog cards have no passive
        p_t = p_o = p_x = None
    elif len(f.passive) == 4:
        p_kind, p_amount, p_misc, p_x = f.passive
        p_t, p_o = 25941, passive(p_kind, p_amount, p_misc, f.icon)
    else:
        p_t, p_o, p_x = f.passive
    designed = not isinstance(f.later[0], str)
    later_names = [l[2][0] for l in f.later] if designed else list(f.later)
    if f.family:                                                     # task 009: a kind of creature
        what = f"Take the shape of a {f.name.lower()} you have devoured"
    elif not f.source:
        what = f"Take the shape of the {f.name.lower()}"
    else:
        what = f"Take the shape of the {f.name.lower()} you devoured"
    out = [
        (f.base, 1, 16591, {
            **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
            "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
            "Category": SHAPE_CATEGORY, "RecoveryTime": 0, "CategoryRecoveryTime": SHIFT_COOLDOWN,
            "StartRecoveryCategory": 133, "StartRecoveryTime": 1000, "InterruptFlags": 0, "AuraInterruptFlags": 0,
            "SpellIconID": f.icon, **effects(aura(A_TRANSFORM, 0, FORM_PLACEHOLDER_ENTRY))},
         (f"{f.name} Form", f"{what}: {one_x[0]}" + (f", {two_x[0]} and {p_x[0]}" if p_x else f" and {two_x[0]}") +
          f"; {later_names[0]} opens at level 10, {later_names[1]} at 20. All shapes share one cooldown.",
          f"Wearing the {f.name.lower()}'s shape.")),
        (f.base + 1, 1, one_t, one_o, one_x),
        (f.base + 2, 1, two_t, two_o, two_x),
    ] + ([(f.base + 3, 1, p_t, p_o, p_x)] if p_x else [])
    for slot, level, entry in ((4, 10, f.later[0]), (5, 20, f.later[1])):
        if designed:
            t, o, x = entry                                          # the level opens it (Mgr::KitSpellOpen)
            out.append((f.base + slot, level, t, {**o, "SpellLevel": level, "BaseLevel": level}, x))
        else:
            t, o = placeholder(level, f.icon)
            out.append((f.base + slot, level, t, o, (f"{entry} (placeholder)",
                                                     f"Placeholder {f.name} ability (level {level}): not designed yet.",
                                                     "")))
    for slot, t, o, x in f.extra:
        assert 6 <= slot <= 9, slot
        out.append((f.base + slot, 1, t, o, x))
    # 2026-10-03: the abilities stay in the spellbook, so each one says which shape it belongs to.
    tag = f"|cffb87830{f.name} form|r"
    # 2026-10-03: the passive is an aura while the shape is worn, shown on the buff bar (not cancellable).
    for i, (sid_, lvl, t, o, x) in enumerate(out):
        if sid_ == f.base + 3 and isinstance(o, dict):
            attrs = (o.get("Attributes", ATTR0_ABILITY) & ~(b.ATTR0_PASSIVE | b.ATTR0_HIDDEN)) | ATTR0_CANT_CANCEL
            out[i] = (sid_, lvl, t, {**o, "Attributes": attrs, "DurationIndex": DUR_INFINITE}, (x[0], x[1], x[2] or x[1]))
    return [(sid_, lvl, t, o, (x[0], f"{x[1]}$B$B{tag}" if x[1] else tag, x[2]))
            if f.base < sid_ <= f.base + 5 else (sid_, lvl, t, o, x) for sid_, lvl, t, o, x in out]


# --- trainers (task 006; task 010: the trainers are the witch sisters, tools/witch_sisters.py) -----------------
# The trainer row and what it teaches live here, next to the spells; the sisters link to it.
TRAINER = 9101200


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
        "-- The Devourer's start: true-form kit, what its trainers teach, eight starting forms. Safe to run again;",
        "-- removed by uninstall/world.sql.",
        "",
        "-- Task 009: a starting form is a kind of creature, and has a favourite food. (Module tables, created here",
        "-- because this file is the one that fills them; dropped by uninstall/world.sql.)",
        "CREATE TABLE IF NOT EXISTS `devourer_shape_family` (",
        "    `family` INT UNSIGNED NOT NULL COMMENT 'creature_template.family: any creature of it gives the shape',",
        "    `shape_id` INT UNSIGNED NOT NULL,",
        "    PRIMARY KEY (`family`)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
        "CREATE TABLE IF NOT EXISTS `devourer_favourite_food` (",
        "    `shape_id` INT UNSIGNED NOT NULL,",
        "    `creature_type` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 = any',",
        "    `family` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 = any',",
        "    `name_part` VARCHAR(32) NOT NULL DEFAULT '' COMMENT 'the creature name contains it; empty = any',",
        "    `label` VARCHAR(32) NOT NULL DEFAULT '' COMMENT 'shown in the menu; empty = the type or family name',",
        "    PRIMARY KEY (`shape_id`, `creature_type`, `family`, `name_part`)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
        "-- Task 017: a colouring that comes with its shape (free = 1), e.g. the retail looks of the older forms.",
        "SET @devourer_col := (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()",
        "    AND TABLE_NAME = 'devourer_skin' AND COLUMN_NAME = 'free');",
        "SET @devourer_sql := IF(@devourer_col = 0, 'ALTER TABLE `devourer_skin` ADD COLUMN `free` TINYINT UNSIGNED "
        "NOT NULL DEFAULT 0 COMMENT ''1 = comes with the shape''', 'DO 0');",
        "PREPARE devourer_stmt FROM @devourer_sql;",
        "EXECUTE devourer_stmt;",
        "DEALLOCATE PREPARE devourer_stmt;",
        "",
        f"DELETE FROM `spell_dbc` WHERE `ID` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_dbc` (" + ",".join(f"`{c}`" for c in b.COLUMNS) + ") VALUES",
        ",\n".join(rows) + ";",
        "",
        "-- Form spells: the module puts the body on and hands out the kit; never saved with the character.",
        f"DELETE FROM `spell_script_names` WHERE `spell_id` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES",
        ",\n".join([f"({s}, 'spell_devourer_form')" for s in forms]
                   + [f"({RUSH}, 'spell_devourer_rush')", f"({SNIFF}, 'spell_devourer_sniff')"]
                   + [f"({s}, '{n}')" for s, n in SCRIPTS]) + ";",
        f"DELETE FROM `spell_custom_attr` WHERE `spell_id` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_custom_attr` (`spell_id`, `attributes`) VALUES",
        ",\n".join(f"({s}, 0x01000000)" for s in forms) + ";",
        "-- Task 009: the gimmicks that answer to hits (HitMask 48 = dodge or parry; Cooldown = their rest).",
        f"DELETE FROM `spell_proc` WHERE `SpellId` BETWEEN {FIRST} AND {LAST};",
        "INSERT INTO `spell_proc` (`SpellId`, `SchoolMask`, `SpellFamilyName`, `SpellFamilyMask0`, `SpellFamilyMask1`,"
        " `SpellFamilyMask2`, `ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`, `HitMask`, `AttributesMask`,"
        " `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`) VALUES",
        ",\n".join(f"({s}, 0, 0, 0, 0, 0, {flags}, {types}, 2, {hits}, 0, 0, 100, {cd}, {charges})"
                   for s, flags, types, hits, cd, charges in PROCS) + ";",
        "",
        "-- Shapes 5-13: one per starting zone; 14-15 the frog line. spell_3 and spell_4 open at levels 10 and 20 (their spell level).",
        "DELETE FROM `devourer_shape` WHERE `shape_id` BETWEEN 5 AND 15;",
        "INSERT INTO `devourer_shape` (`shape_id`, `name`, `form_spell`, `display_id`, `scale`, `spell_1`, `spell_2`,"
        " `spell_3`, `spell_4`, `passive`, `brood_display`) VALUES",
        ",\n".join(f"({f.shape}, {q(f.name)}, {f.base}, {f.look}, {f.scale}, {f.base + 1}, {f.base + 2},"
                   f" {f.base + 4}, {f.base + 5}, {f.base + 3 if f.passive else 0}, {f.display})" for f in FORMS) + ";",
        "",
        "-- Who gives them: the zone's creature the base look, its kin elsewhere a colouring (0 = the base look).",
        "-- Shape 0: a creature of a form's family that is not that body (task 009); it gives no shape.",
        "DELETE FROM `devourer_shape_source` WHERE `shape_id` BETWEEN 5 AND 15 OR `creature_entry` IN ("
        + ", ".join(str(e) for e, _ in NOT_THAT_BODY) + ");",
        "INSERT INTO `devourer_shape_source` (`creature_entry`, `shape_id`, `display_id`) VALUES",
        ",\n".join([f"({f.source}, {f.shape}, 0)" for f in FORMS if f.source]
                   + [f"({e}, {f.shape}, {d})" for f in FORMS for e, d, _ in f.colourings]
                   + [f"({e}, 0, 0)" for e, _ in NOT_THAT_BODY]) + ";",
        "-- Task 009: any creature of the family gives the shape; each of its looks (displays) is a colouring named",
        "-- after the creature. The module builds those colourings at startup from creature_template(_model).",
        "DELETE FROM `devourer_shape_family` WHERE `shape_id` BETWEEN 5 AND 15;",
        "INSERT INTO `devourer_shape_family` (`family`, `shape_id`) VALUES",
        ",\n".join(f"({f.family}, {f.shape})" for f in FORMS if f.family) + ";",
        "-- Task 009: favourite food, 2x Bio Points for everyone. A row matches when every field it sets matches.",
        "DELETE FROM `devourer_favourite_food` WHERE `shape_id` BETWEEN 5 AND 15;",
        "INSERT INTO `devourer_favourite_food` (`shape_id`, `creature_type`, `family`, `name_part`, `label`) VALUES",
        ",\n".join(f"({f.shape}, {t}, {fam}, {q(part)}, {q(label)})" for f in FORMS for t, fam, part, label in f.food)
        + ";",
        "DELETE FROM `devourer_skin` WHERE `shape_id` BETWEEN 5 AND 15;",
        "-- free = 1: comes with the shape (task 017: the retail looks, and the old base look beside them).",
        "INSERT INTO `devourer_skin` (`display_id`, `shape_id`, `name`, `brood_display`, `free`) VALUES",
        ",\n".join([f"({f.display}, {f.shape}, {q(f.skin)}, 0, {1 if f.looks else 0})" for f in FORMS]
                   + [f"({d}, {f.shape}, {q(n)}, 0, 1)" for f in FORMS for d, n in f.looks]
                   + [f"({d}, {f.shape}, {q(n)}, {d}, 0)" for f in FORMS for _, d, n in f.colourings if d]) + ";",
        "DELETE FROM `devourer_diet` WHERE `shape_id` BETWEEN 5 AND 15;",
        "INSERT INTO `devourer_diet` (`shape_id`, `creature_type`, `bp`) VALUES",
        ",\n".join(f"({f.shape}, {t}, {bp})" for f in FORMS for t, bp in f.diet) + ";",
        "",
        "-- --- what the Devourer's trainers teach -----------------------------------------------------------------",
        "-- The class trainer (class 10) and its spells. The NPCs that train are the witch sisters (task 010,",
        "-- tools/witch_sisters.py -> 2026_10_01_00_devourer_witch_sisters.sql).",
        f"DELETE FROM `trainer` WHERE `Id` = {TRAINER};",
        "INSERT INTO `trainer` (`Id`, `Type`, `Requirement`, `Greeting`, `VerifiedBuild`) VALUES",
        f"({TRAINER}, 0, 10, 'Hungry again? Then learn to eat better.', 0);",
        f"DELETE FROM `trainer_spell` WHERE `TrainerId` = {TRAINER};",
        "INSERT INTO `trainer_spell` (`TrainerId`, `SpellId`, `MoneyCost`, `ReqSkillLine`, `ReqSkillRank`,"
        " `ReqAbility1`, `ReqAbility2`, `ReqAbility3`, `ReqLevel`, `VerifiedBuild`) VALUES",
        ",\n".join(f"({TRAINER}, {sid}, {cost}, 0, 0, 0, 0, 0, {lvl}, 0)" for sid, lvl, cost, *_ in BASE
                   if cost is not None) + ";",
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
    md += ["", "Known from creation; bars: Attack, Rush, Call Pet, Devour (Concentrate is gone since task 015: the pet replaced it). Shifting into a shape is free "
           "(Devourer.AnimaPerShift, default 0 since 2026-10-03).", "",
           "## Trainers", "",
           f"Trainer {TRAINER} teaches the base kit above. The Devourer's trainers are the Hollowmoor witch sisters "
           "in the In-Between (task 010): see `docs/witch-sisters.md`."]
    families = {FAMILY_TALLSTRIDER: "Tallstrider", FAMILY_WOLF: "Wolf", FAMILY_CAT: "Cat", FAMILY_SPIDER: "Spider", FAMILY_BOAR: "Boar",
                FAMILY_CROCOLISK: "Crocolisk", FAMILY_SCORPID: "Scorpid", FAMILY_MOTH: "Moth", 32: "Warp Stalker"}
    types = {CREATURE_TYPE_BEAST: "Beast", CREATURE_TYPE_ELEMENTAL: "Elemental", CREATURE_TYPE_CRITTER: "Critter"}

    def food_text(f):
        parts, names = [], {}
        for t, fam, part, label in f.food:
            if part:
                names.setdefault(t, []).append(part)
            else:
                parts.append(f"family {families[fam]}" if fam else f"type {types[t]}")
        for t, named in names.items():
            parts.append(f"{types[t]}s named *{'*, *'.join(named)}*")
        return " or ".join(parts)

    md += ["", "## Starting forms", "",
           "Task 009 (batch 1: Wolf, Saber, Moth, Boar): a form is a **kind of creature**. Devouring any creature of "
           "its creature family (`devourer_shape_family`) gives the form; every different look (display id) of that "
           "family is a colouring, named after the creature that wears it (the most common one). The module builds "
           "them at startup from the world database; explicit `devourer_shape_source` rows still win. Favourite "
           "food (`devourer_favourite_food`) gives 2x Bio Points for every Devourer.",
           "",
           "Creatures of those families that are not that body give nothing (`devourer_shape_source` shape 0):",
           ""]
    md += [f"- {e}: {why}" for e, why in NOT_THAT_BODY]
    md.append("")
    for f in FORMS:
        md.append(f"### {f.name} (shape {f.shape}, {f.zone})")
        if f.looks:
            md.append(f"Look (task 017): a retail model, base {f.look} (`{f.looks[0][1]}`); its other colourings come "
                      "with the shape: " + ", ".join(f"{d} `{n}`" for d, n in f.looks[1:]) +
                      f". The old look {f.display} (`{f.skin}`) comes with it too.")
        if f.family:
            md.append(f"Devour **any creature of the {families[f.family]} family** (e.g. {f.source} for the base look "
                      f"{f.display}, skin `{f.skin}`); each look is a colouring. Favourite food: {food_text(f)}.")
            if f.colourings:
                md.append("Named colourings kept from task 007: " + ", ".join(
                    f"{e} → {d or 'base look'}" + (f" (`{n}`)" if n else "") for e, d, n in f.colourings) + ".")
        elif f.how:
            md.append(f.how + (f" Favourite food: {food_text(f)}." if f.food else ""))
        else:
            md.append(f"Devour **{f.source}** for the base look ({f.display}, skin `{f.skin}`)"
                      + ("; colourings: " + ", ".join(f"{e} → {d or 'base look'}" + (f" (`{n}`)" if n else "")
                                                      for e, d, n in f.colourings) if f.colourings else "") + ".")
        md.append("")
        md.append("| Spell | Level | Name | What it does |")
        md.append("|---|---|---|---|")
        for spell, lvl, t, o, (name, desc, tip) in form_spells(f):
            md.append(f"| {spell} | {lvl} | {name} | {desc or '(cast by the kit) ' + tip} |")
        md.append("")
        if f.changes:
            md.append("Changes against the canvas card (task 009), and why:")
            md.append("")
            md += [f"- {c}" for c in f.changes]
            md.append("")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"{len(rows)} spells ({min(ids)}-{max(ids)}), {len(FORMS)} forms, trainer {TRAINER}")
    print(f"wrote {OUT_SQL.relative_to(REPO)}, {OUT_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
