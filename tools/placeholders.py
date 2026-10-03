#!/usr/bin/env python3
"""Tasks 005 + 015: the Devourer's talent trees (class 10), spec abilities and the helper spells they use.

    python tools/placeholders.py

The file keeps its task-005 name (the three outputs below are the same ones, now with real content instead of
placeholders). One source for three outputs, keep them in step by running this script again after any change:
  data/sql/db-world/2026_09_30_07_devourer_placeholders.sql   spell_dbc + talent_dbc rows, script bindings
                                                              (server; the client patch tool picks the same rows up
                                                              from this file, it reads every 2026_09_30_0*.sql)
  src/DevourerTalentIds.h                                     talent ranks and spell ids for the module
  docs/talents.md                                             the map of every slot, for the owner

The script needs no client file: it starts from the committed row of talent spell 9100031 (a passive dummy aura)
and overrides it field by field with the helpers of tools/coa/build_devourer_spells.py.

How a talent works (docs/talents.md has the full list):
  aura   a stock aura per rank (health, armour, speed ...): no code
  mod    a spell modifier on one of the Devourer's abilities (cost, cooldown, duration): no code. Abilities that
         can be modified carry SpellClassSet 90 and one bit of SpellClassMask_1 (MASK below); the talent's
         modifier names the same bits. (A modifier on family 0 would touch every spell in the game.)
  mark   a passive dummy aura per rank. The module reads the rank (Mgr::Rank) in src/DevourerTalents.cpp
  active a castable spell (one rank). The module runs it (spell_devourer_spec)
Ranks replace each other: the core builds the rank chain from talent_dbc.

Ids: talent spells 9100500-9100799 (9100050-9100069 for the four task-003 talents), spec abilities 9100800-9100808,
helper spells 9101030-9101059, talents 9020-9059 (Glutton), 9060-9119 (Skinchanger), 9120-9179 (Brood).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools" / "coa"))
import build_devourer_spells as b  # noqa: E402  (the spell DSL: effects(), aura(), hunger(), CLEAN, PASSIVE ...)
from build_devourer_spells import CLEAN, PASSIVE, NO_MECHANICS, aura, effects, hunger  # noqa: E402

SPELL_SQL = REPO / "data" / "sql" / "db-world" / "2026_09_30_02_devourer_spells.sql"
OUT_SQL = REPO / "data" / "sql" / "db-world" / "2026_09_30_07_devourer_placeholders.sql"
OUT_H = REPO / "src" / "DevourerTalentIds.h"
OUT_MD = REPO / "docs" / "talents.md"

TEMPLATE_SPELL = 9100031        # Quick Devour: a passive dummy talent, committed in 2026_09_30_02
FIRST_TALENT_SPELL, LAST_TALENT_SPELL = 9100500, 9100799
FIRST_SPEC_SPELL = 9100800
FIRST_HELPER, LAST_HELPER = 9101030, 9101059
FAMILY = 90                      # SpellClassSet of every spell a modifier may touch (no stock family uses it)

# --- enums the DSL does not have --------------------------------------------------------------------------------
E_DUMMY, E_SCHOOL_DAMAGE, E_WEAPON_PERCENT_DAMAGE = 3, 2, 31
A_PERIODIC_DAMAGE, A_MOD_TAUNT, A_MOD_STUN, A_DUMMY, A_MOD_DODGE, A_SCHOOL_ABSORB = 3, 11, 12, 4, 49, 69
A_MOD_SCALE, A_MECHANIC_IMMUNITY, A_MOD_DAMAGE_PCT_DONE, A_MOD_DAMAGE_PCT_TAKEN = 61, 77, 79, 87
A_MOD_RESISTANCE_PCT, A_ADD_FLAT_MODIFIER, A_MOD_HEALING_PCT, A_MOD_SPEED_ALWAYS = 101, 107, 118, 129
A_ADD_PCT_MODIFIER = 108
A_MOD_HEALTH_PCT, A_MOD_MELEE_HASTE, A_MOD_SPEED, A_MOD_SLOW = 133, 138, 31, 33
A_AOE_DAMAGE_AVOIDANCE, A_MECHANIC_DURATION, A_MECHANIC_DAMAGE_TAKEN = 229, 232, 255
OP_DURATION, OP_COOLDOWN, OP_COST = 1, 11, 14               # SpellModOp
MECH_SILENCE, MECH_STUN, MECH_KNOCKOUT, MECH_FEAR, MECH_SNARE, MECH_BLEED, MECH_HORROR = 9, 12, 14, 5, 11, 15, 24
T_CASTER, T_ENEMY = 1, 6
RANGE_SELF, RANGE_COMBAT, RANGE_30, RANGE_ANYWHERE = 1, 2, 4, 13
CAST_INSTANT = 1
SCHOOL_ALL = 127
DUR_INFINITE, DUR_10S, DUR_3S, DUR_4S, DUR_12S, DUR_8S, DUR_30S, DUR_6S, DUR_1S = 21, 1, 27, 35, 29, 31, 9, 32, 36
GCD = {"StartRecoveryCategory": 133, "StartRecoveryTime": 1500}
ATTR_ABILITY, ATTR_PASSIVE, ATTR_HIDDEN, ATTR_CANT_CANCEL = 0x10, 0x40, 0x80, 0x80000000

MASK = {                         # one bit per modifiable ability (SpellClassMask_1)
    "DevourWhole": 0x1, "IronGut": 0x2, "DevouringChallenge": 0x4, "MimicStrike": 0x8, "SkinSwap": 0x10,
    "FormOfMany": 0x20, "CallTheClutch": 0x40, "FeedTheYoung": 0x80, "BroodSwarm": 0x100, "HatchBrood": 0x200,
    "Rush": 0x400,
}
ICON = {"Glutton": 166, "Skinchanger": 3058, "Brood": 689}

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

# Cells already taken by real talents (task 003 / ChaosCore0.3) and the four task-003 rank chains whose spells
# are rewritten here: (tier, column) -> (talent id, name, ranks, real, first spell id)
EXISTING = {
    900: {(0, 0): (9000, "Iron Stomach", 5, False, 9100050), (0, 1): (9001, "Quick Devour", 1, True, 0),
          (0, 2): (9002, "Devour Whole", 1, True, 0), (1, 0): (9003, "Deep Hunger", 5, False, 9100055),
          (1, 1): (9004, "Feast", 1, True, 0), (1, 2): (9005, "Regurgitate", 1, True, 0),
          (2, 1): (9006, "Stretched Gut", 1, True, 0), (3, 1): (9007, "Digested: Thick Hide", 1, True, 0),
          (3, 2): (9008, "Digested: Bile Coating", 1, True, 0)},
    901: {(0, 1): (9010, "Fluid Flesh", 5, False, 9100060)},
    902: {(0, 1): (9015, "Swelling Brood", 5, False, 9100065)},
}

TREES = [
    # tab, name, first talent id, names (used in order for the free cells)
    (900, "Glutton", 9020, [
        "Thick Gullet", "Iron Maw", "Bottomless Pit", "Gristle Plating", "Heavy Belly", "Bloated Resolve",
        "Digestive Fire", "Slow Chew", "Grand Appetite", "Chewing Cud", "Swallowed Pride", "Belly of the Beast",
        "Ravenous Guard", "Fat Reserves", "Gnawing Patience", "Crushing Jaw", "Satiation", "Hunger's Wall",
        "Unending Meal", "Glutton's Bulk", "Stomach of Stone"]),
    (901, "Skinchanger", 9060, [
        "Shifting Hide", "Borrowed Claws", "Quick Molt", "Second Skin", "Mimic's Eye", "Restless Form", "Shed Skin",
        "Many Faces", "Loose Bones", "Stolen Instinct", "Changing Blood", "Flicker Shape", "Mask of Meat",
        "Shape Memory", "Wandering Skin", "Unfixed Nature", "Echo Flesh", "Living Mask", "Skin Hoard",
        "Swift Change", "Hollow Shell", "Worn Faces", "Borrowed Voice", "Soft Bones", "Shapeless Step",
        "Mirror Hunger", "Stolen Strength", "Fleeting Form", "Thousand Skins"]),
    (902, "Brood", 9120, [
        "Warm Nest", "Egg Tooth", "Many Mouths", "Nursing Hunger", "Shared Meal", "Hatching Heat", "Brood Mother",
        "Clutch Instinct", "Hungry Young", "Nest Guard", "Feeding Frenzy", "Spawning Pool", "Litter Bond",
        "Twitching Eggs", "Swarm Call", "Nest Web", "Brood Sense", "Thick Shells", "Quick Hatching", "Blood Milk",
        "Swollen Sac", "Nest Scent", "Hive Mind", "Young Teeth", "Crawling Mass", "Mother's Wrath", "Endless Clutch",
        "Swarm Tide", "Queen of the Brood"]),
]


# --- the talents ----------------------------------------------------------------------------------------------
def flat(op, amount, mask):
    """A spell modifier (flat) on the abilities carrying `mask` bits."""
    return aura(A_ADD_FLAT_MODIFIER, amount, op, mask=mask)


class Talent:
    """name, spec; `text` uses {r} (rank), {v} (per * rank), {w} (per2 * rank) and {x} (vals[rank - 1]);
    `fx(r, v)` returns the effect specs of rank r (stock auras or modifiers); no fx = a marker the module reads;
    `active` = the castable's fields (cost, cooldown ...), one rank."""
    def __init__(self, text, per=1, per2=0, vals=None, fx=None, active=None):
        self.text, self.per, self.per2, self.vals, self.fx, self.active = text, per, per2, vals, fx, active

    def kind(self):
        return "active" if self.active else "aura/mod" if self.fx else "mark"

    def describe(self, rank):
        v = self.per * rank
        w = self.per2 * rank
        x = self.vals[rank - 1] if self.vals else 0
        v, w = round(v, 2), round(w, 2)
        v = int(v) if float(v).is_integer() else v
        w = int(w) if float(w).is_integer() else w
        return self.text.format(r=rank, v=v, w=w, x=x)


def castable(cost, cooldown, **extra):
    return {"cost": cost, "cooldown": cooldown, **extra}


TALENTS: dict[str, Talent] = {
    # ----- Glutton -----
    "Iron Stomach": Talent("Your maximum health is increased by {v}%.", 2,
                           fx=lambda r, v: [aura(A_MOD_HEALTH_PCT, v)]),
    "Deep Hunger": Talent("Every meal gives you {v} more Anima.", 2),
    "Thick Gullet": Talent("Gorged lasts {v} seconds longer once the fight is over.", 20),
    "Iron Maw": Talent("Your blows hit {v}% harder and give you {r} more Anima each.", 10),
    "Bottomless Pit": Talent("Every stack of Gorged adds {v}% to your armour.", 0.5),
    "Gristle Plating": Talent("Your armour is increased by {v}%, or by {w}% while a beast's meal is in you.", 5, 10),
    "Heavy Belly": Talent("The healing you receive is increased by {v}%.", 3,
                          fx=lambda r, v: [aura(A_MOD_HEALING_PCT, v)]),
    "Bloated Resolve": Talent("Devour Whole costs {v} less Anima.", 5,
                              fx=lambda r, v: [flat(OP_COST, -10 * v, MASK["DevourWhole"])]),
    "Digestive Fire": Talent("The ability you swallow hits {v}% harder when it comes out.", 15),
    "Slow Chew": Talent("Enemies who strike you swing {v}% slower for 6 seconds.", 2),
    "Grand Appetite": Talent("Meal buffs last 30 minutes, and the buff of your previous meal stays beside the new one."),
    "Chewing Cud": Talent("With 5 or more Gorged, every blow of yours gives you {v} more Anima.", 1),
    "Swallowed Pride": Talent("Stuns and silences on you last {v}% shorter.", 15,
                              fx=lambda r, v: [aura(A_MECHANIC_DURATION, -v, MECH_STUN),
                                               aura(A_MECHANIC_DURATION, -v, MECH_SILENCE)]),
    "Belly of the Beast": Talent("Gorged can grow {v} stack higher (up to 13).", 1),
    "Ravenous Guard": Talent("A meal eaten below half health heals you for {v}% of your health.", 5),
    "Fat Reserves": Talent("The first time a fight drops you under 30% health, a shield worth 15% of your health "
                           "forms around you. Once every 3 minutes."),
    "Gnawing Patience": Talent("Every enemy beating on you (up to 5) adds {v}% to the damage you deal.", 1),
    "Crushing Jaw": Talent("Devour Whole also stuns every enemy within 8 yards for {v} seconds.", 1.5),
    "Satiation": Talent("With 100 Anima in you, you take {v}% less damage.", 3),
    "Hunger's Wall": Talent("Iron Gut lasts {v} seconds longer.", 2),
    "Unending Meal": Talent("Devour Whole also heals you for {v}% of your health.", 5),
    "Glutton's Bulk": Talent("Your size is increased by {v}% and your maximum health by {w}%.", 5, 3,
                             fx=lambda r, v: [aura(b.A_MOD_SCALE, v), aura(A_MOD_HEALTH_PCT, 3 * r)]),
    "Stomach of Stone": Talent("Gorged can grow to 15 stacks. At 15 stacks you cannot be pulled, feared or slowed."),
    # ----- Skinchanger -----
    "Shifting Hide": Talent("After a shift your armour is {v}% higher for 6 seconds.", 3),
    "Fluid Flesh": Talent("Your shift cooldown is {v} seconds shorter (never under 1 second in all).", 0.2),
    "Borrowed Claws": Talent("After a shift you deal {v}% more damage for 8 seconds.", 4),
    "Quick Molt": Talent("After a shift you run {v}% faster for 4 seconds.", 10),
    "Second Skin": Talent("Your movement speed and your strike speed are increased by {v}%.", 1,
                          fx=lambda r, v: [aura(A_MOD_SPEED, v), aura(A_MOD_MELEE_HASTE, v)]),
    "Mimic's Eye": Talent("Your echoes hit {v}% harder.", 10),
    "Restless Form": Talent("Shifting into a shape you have not worn for a minute gives you {v} Anima.", 5),
    "Shed Skin": Talent("A shift frees you from slowing and rooting effects. Once every {x} seconds.",
                        vals=[40, 20]),
    "Many Faces": Talent("Your echoes last {v} seconds longer.", 2),
    "Loose Bones": Talent("You take {v}% less damage from area effects.", 4,
                          fx=lambda r, v: [aura(A_AOE_DAMAGE_AVOIDANCE, -v)]),
    "Stolen Instinct": Talent("Copy the passive of the shape you last left onto the shape you wear, for 12 "
                              "seconds. Costs 15 Anima. 30 second cooldown.",
                              active=castable(15, 30000, target="self")),
    "Changing Blood": Talent("Bleeds on you do {v}% less damage.", 8,
                             fx=lambda r, v: [aura(A_MECHANIC_DAMAGE_TAKEN, -v, MECH_BLEED)]),
    "Flicker Shape": Talent("Leaving a shape in a fight heals you for {v}% of your health.", 3),
    "Mask of Meat": Talent("Your maximum health is increased by {v}% in the shape of a beast, and by {r}% in any "
                           "other.", 2),
    "Shape Memory": Talent("Mimic Strike costs {v} less Anima.", 5,
                           fx=lambda r, v: [flat(OP_COST, -10 * v, MASK["MimicStrike"])]),
    "Wandering Skin": Talent("Rush carries you {v} yards further and leaves an echo behind.", 2),
    "Unfixed Nature": Talent("Every different shape worn in the last 15 seconds adds {v}% to your damage "
                             "(up to 3).", 2),
    "Echo Flesh": Talent("Call your echo to your side; it casts its shape's first ability at once. Costs 25 Anima. "
                         "20 second cooldown.", active=castable(25, 20000, target="self")),
    "Living Mask": Talent("While an echo of yours lives, you take {v}% less damage.", 5),
    "Skin Hoard": Talent("Each echo you leave gives you {v} Anima when it fades.", 4),
    "Swift Change": Talent("A shift makes your strikes {v}% faster for 4 seconds.", 10),
    "Hollow Shell": Talent("Leaving a shape above {x}% health leaves a second, smaller echo with half the power.",
                           vals=[100, 80]),
    "Worn Faces": Talent("For 10 seconds your echo eats what dies near it, as a hatchling would, and feeds you "
                         "Anima. Costs 20 Anima. 30 second cooldown.", active=castable(20, 30000, target="self")),
    "Borrowed Voice": Talent("The ability your echo casts hits {v}% harder.", 4),
    "Soft Bones": Talent("For 10 seconds after a shift you dodge {v}% more.", 3),
    "Shapeless Step": Talent("Rush recovers {v} seconds faster.", 2,
                             fx=lambda r, v: [flat(OP_COOLDOWN, -1000 * v, MASK["Rush"])]),
    "Mirror Hunger": Talent("Your echoes drain {v} mana or rage from the enemy and give it to you as Anima.", 3),
    "Stolen Strength": Talent("Every shape you know adds {v}% to your damage (up to 10 shapes).", 1),
    "Fleeting Form": Talent("A shift within 5 seconds of the last one recovers {v} seconds faster.", 0.5),
    "Thousand Skins": Talent("Every shift leaves an echo, even out of a fight. No more than three stand at once."),
    # ----- Brood -----
    "Warm Nest": Talent("Your hatchlings have {v}% more health.", 3),
    "Swelling Brood": Talent("Hatch Brood lasts {v} seconds longer.", 2,
                             fx=lambda r, v: [flat(OP_DURATION, 1000 * v, MASK["HatchBrood"])]),
    "Egg Tooth": Talent("Your hatchlings bite {v}% harder.", 5),
    "Many Mouths": Talent("Every second Hatch Brood hatches {v} more young.", 1),
    "Nursing Hunger": Talent("What a hatchling devours gives you {v} more Anima.", 1),
    "Shared Meal": Talent("When you devour, every hatchling beside you heals {v}% of its health.", 10),
    "Hatching Heat": Talent("Hatch Brood costs {v} less Anima.", 3,
                            fx=lambda r, v: [flat(OP_COST, -10 * v, MASK["HatchBrood"])]),
    "Brood Mother": Talent("Hatchlings more than {x} yards behind are called back to your side.", vals=[60, 40]),
    "Clutch Instinct": Talent("While a hatchling lives you dodge {v}% more.", 2),
    "Hungry Young": Talent("What a hatchling devours heals it for {v}% of its health.", 5),
    "Nest Guard": Talent("Your hatchlings gather at your side, and you take 25% less damage for 8 seconds. "
                         "Costs 20 Anima. 30 second cooldown.", active=castable(20, 30000, target="self")),
    "Feeding Frenzy": Talent("After a meal a hatchling runs {v}% faster for 6 seconds.", 3),
    "Spawning Pool": Talent("Hatch Brood has a {v}% chance not to start its cooldown.", 15),
    "Litter Bond": Talent("Every hatchling shares {v}% of your armour.", 2),
    "Twitching Eggs": Talent("A dying hatchling bursts: {v}% of your attack power as damage to every enemy "
                             "within 5 yards.", 30),
    "Swarm Call": Talent("Call the Clutch costs {v} less Anima.", 4,
                         fx=lambda r, v: [flat(OP_COST, -10 * v, MASK["CallTheClutch"])]),
    "Nest Web": Talent("Hatchling bites slow the enemy by {v}% (up to 5 times).", 2),
    "Brood Sense": Talent("Send every hatchling at the target you have chosen. Costs 15 Anima. 10 second "
                          "cooldown.", active=castable(15, 10000, target="enemy")),
    "Thick Shells": Talent("Your hatchlings take {v}% less damage.", 5),
    "Quick Hatching": Talent("Hatch Brood recovers {v} seconds faster.", 3,
                             fx=lambda r, v: [flat(OP_COOLDOWN, -1000 * v, MASK["HatchBrood"])]),
    "Blood Milk": Talent("Devouring a hatchling also makes your strikes {v}% faster for 10 seconds.", 10),
    "Swollen Sac": Talent("Hatch Brood hatches {v} more young.", 1),
    "Nest Scent": Talent("Mark an enemy: it takes 20% more damage for 12 seconds, and every hatchling bite on it "
                         "gives you 2 Anima. Costs 20 Anima. 20 second cooldown.",
                         active=castable(20, 20000, target="enemy")),
    "Hive Mind": Talent("You take {v}% less damage for each living hatchling (up to 5).", 1),
    "Young Teeth": Talent("Hatchlings make their bite bleed for {v}% of its damage.", 30),
    "Crawling Mass": Talent("Brood Swarm lasts {v} seconds longer.", 3),
    "Mother's Wrath": Talent("A dying hatchling gives you {v}% more damage for 8 seconds (up to 3 times).", 4),
    "Endless Clutch": Talent("A dying hatchling has a {v}% chance to hatch a new one.", 10),
    "Swarm Tide": Talent("Brood Swarm costs {v} less Anima and lasts {w} seconds longer.", 6, 4,
                         fx=lambda r, v: [flat(OP_COST, -10 * v, MASK["BroodSwarm"])]),
    "Queen of the Brood": Talent("While hatchlings fight, the brood never stays smaller than 4. Every hatchling "
                                 "grows as large as a Gorged beast and bites 20% harder."),
}

# Names whose rank chains are read by the module (Mgr::Rank): constant name = "Tal" + CamelCase of the name.
# --- spec abilities (learned with the spec at the level shown) -----------------------------------------------
# constant, spec, level, name, tooltip, power cost (Anima), cooldown ms, target ("self"/"enemy"/None = passive), kind
SPEC_ABILITIES = [
    ("SpellIronGut", "Glutton", 20, "Iron Gut",
     "Swallow your pain: for 8 seconds you take 30% less damage, and every stack of Gorged adds 1% more. You "
     "cannot be stunned or knocked out. Costs 25 Anima. 45 second cooldown.", 25, 45000, "self"),
    ("SpellDevouringChallenge", "Glutton", 40, "Devouring Challenge",
     "Roar at every enemy within 10 yards: they must turn on you for 4 seconds, and each one that strikes you in "
     "that time feeds you 5 Anima. Costs 30 Anima. 2 minute cooldown.", 30, 120000, "self"),
    ("SpellLastSupper", "Glutton", 60, "Last Supper",
     "When a blow would kill you, you survive with 20% health and every stack of Gorged is eaten at once, "
     "healing you for 3% of your health each. Needs a full 100 Anima, which it eats. Once every 5 minutes.",
     0, 0, None),
    ("SpellMimicStrike", "Skinchanger", 20, "Mimic Strike",
     "Strike with the blow of the shape you last left: 150% weapon damage. Costs 25 Anima. 12 second cooldown.",
     25, 12000, "weapon"),
    ("SpellSkinSwap", "Skinchanger", 40, "Skin Swap",
     "Swap places with your echo. The enemy you struck last turns on the echo for 4 seconds. Costs 30 Anima. "
     "30 second cooldown.", 30, 30000, "self"),
    ("SpellFormOfMany", "Skinchanger", 60, "Form of Many",
     "For 12 seconds every shift is instant, and each echo you leave lasts 14 seconds and casts its ability "
     "twice. Costs 60 Anima. 3 minute cooldown.", 60, 180000, "self"),
    ("SpellCallTheClutch", "Brood", 20, "Call the Clutch",
     "Call every hatchling within 40 yards to your target; they strike 30% harder for 10 seconds. Costs 20 "
     "Anima. 30 second cooldown.", 20, 30000, "enemy"),
    ("SpellFeedTheYoung", "Brood", 40, "Feed the Young",
     "Spend 15% of your health: every hatchling heals for 25% of its health and strikes 10% faster for 10 "
     "seconds. Costs 25 Anima. 20 second cooldown.", 25, 20000, "self"),
    ("SpellBroodSwarm", "Brood", 60, "Brood Swarm",
     "Hatch six hatchlings at once for 20 seconds, each striking with half your attack power. Costs 50 Anima. "
     "3 minute cooldown.", 50, 180000, "self"),
]
SPEC_MASK = {"Iron Gut": "IronGut", "Devouring Challenge": "DevouringChallenge", "Mimic Strike": "MimicStrike",
             "Skin Swap": "SkinSwap", "Form of Many": "FormOfMany", "Call the Clutch": "CallTheClutch",
             "Feed the Young": "FeedTheYoung", "Brood Swarm": "BroodSwarm"}

# --- helper spells (the module casts them; never in the spellbook) -----------------------------------------------
HIDDEN = {"Attributes": ATTR_HIDDEN | ATTR_PASSIVE | ATTR_ABILITY, "AttributesEx": 1024,
          "AttributesEx2": 0x80000000, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
          "CastingTimeIndex": CAST_INSTANT, "RecoveryTime": 0}
BUFF = {"Attributes": 0, "AttributesEx": 0, "RangeIndex": RANGE_SELF, "CastingTimeIndex": CAST_INSTANT,
        "RecoveryTime": 0}
HELPERS = [
    # constant, name, description, extra fields, effects
    ("SpellNatureA", "Devourer's Nature", "Armour, damage taken and damage done, set by your talents and your state.",
     HIDDEN, [aura(A_MOD_RESISTANCE_PCT, 0, 1), aura(A_MOD_DAMAGE_PCT_TAKEN, 0, SCHOOL_ALL),
              aura(A_MOD_DAMAGE_PCT_DONE, 0, SCHOOL_ALL)]),
    ("SpellNatureB", "Devourer's Nature", "Dodge, strike speed and healing taken, set by your talents and your state.",
     HIDDEN, [aura(A_MOD_DODGE, 0), aura(A_MOD_MELEE_HASTE, 0), aura(A_MOD_HEALING_PCT, 0)]),
    ("SpellNatureC", "Devourer's Nature", "Speed, blow damage and health, set by your talents and your state.",
     HIDDEN, [aura(A_MOD_SPEED_ALWAYS, 0), aura(A_MOD_DAMAGE_PCT_DONE, 0, 1), aura(A_MOD_HEALTH_PCT, 0)]),
    ("SpellHide", "Devourer's Hide", "Hidden: the module decides what a blow takes from you.",
     {**HIDDEN, "Attributes": ATTR_HIDDEN | ATTR_PASSIVE | ATTR_ABILITY | ATTR_CANT_CANCEL},
     [aura(A_SCHOOL_ABSORB, 0, SCHOOL_ALL)]),
    ("SpellStoneStomach", "Stomach of Stone", "You cannot be pulled, feared or slowed.", BUFF,
     [aura(A_MECHANIC_IMMUNITY, 0, MECH_FEAR), aura(A_MECHANIC_IMMUNITY, 0, MECH_SNARE),
      aura(A_MECHANIC_IMMUNITY, 0, MECH_HORROR)]),
    ("SpellIronGutBuff", "Iron Gut", "You take 30% less damage and cannot be stunned or knocked out.",
     {**BUFF, "DurationIndex": DUR_8S},
     [aura(A_MOD_DAMAGE_PCT_TAKEN, -30, SCHOOL_ALL), aura(A_MECHANIC_IMMUNITY, 0, MECH_STUN),
      aura(A_MECHANIC_IMMUNITY, 0, MECH_KNOCKOUT)]),
    ("SpellChallenged", "Devouring Challenge", "Must turn on the Devourer.", {**BUFF, "DurationIndex": DUR_4S},
     [aura(A_MOD_TAUNT, 0, target=T_ENEMY)]),
    ("SpellCrushingJaw", "Crushing Jaw", "Stunned.",
     {**BUFF, "DurationIndex": DUR_1S, "Mechanic": MECH_STUN, "EffectMechanic_1": MECH_STUN},
     [aura(A_MOD_STUN, 0, target=T_ENEMY)]),
    ("SpellSlowChew", "Slow Chew", "Strikes slowed.", {**BUFF, "DurationIndex": DUR_6S},
     [aura(A_MOD_MELEE_HASTE, -2, target=T_ENEMY)]),
    ("SpellFatReserves", "Fat Reserves", "A shield of stored fat.", {**BUFF, "DurationIndex": DUR_30S},
     [aura(A_SCHOOL_ABSORB, 100, SCHOOL_ALL)]),
    ("SpellClutchCall", "Call the Clutch", "Strikes 30% harder.", {**BUFF, "DurationIndex": DUR_10S},
     [aura(A_MOD_DAMAGE_PCT_DONE, 30, SCHOOL_ALL)]),
    ("SpellFedYoung", "Fed Young", "Strikes 10% faster.", {**BUFF, "DurationIndex": DUR_10S},
     [aura(A_MOD_MELEE_HASTE, 10)]),
    ("SpellNestWeb", "Nest Web", "Movement slowed.", {**BUFF, "DurationIndex": DUR_8S, "CumulativeAura": 5},
     [aura(A_MOD_SLOW, -2, target=T_ENEMY)]),
    ("SpellNestScentMark", "Nest Scent", "Takes 20% more damage.", {**BUFF, "DurationIndex": DUR_12S},
     [aura(A_MOD_DAMAGE_PCT_TAKEN, 20, SCHOOL_ALL, target=T_ENEMY)]),
    ("SpellYoungTeeth", "Young Teeth", "Bleeding.",
     {**BUFF, "DurationIndex": DUR_3S, "Mechanic": MECH_BLEED, "EffectMechanic_1": MECH_BLEED},
     [aura(A_PERIODIC_DAMAGE, 1, target=T_ENEMY, period=1000)]),
    ("SpellEggburst", "Eggburst", "A hatchling bursts.",
     {"Attributes": 0, "AttributesEx": 0, "RangeIndex": RANGE_30, "CastingTimeIndex": CAST_INSTANT,
      "RecoveryTime": 0, "DurationIndex": 0},
     [{"effect": E_SCHOOL_DAMAGE, "amount": 1, "target": T_ENEMY}]),
    ("SpellThickShells", "Thick Shells", "Takes less damage.", HIDDEN,
     [aura(A_MOD_DAMAGE_PCT_TAKEN, 0, SCHOOL_ALL)]),
    # Task 015: the hunter's pet spells (stock) may cost mana, and a Devourer has none. This hidden passive is a
    # spell modifier on the hunter's own spell family (9; an empty mask = every one of them): their cost is -100%.
    # No Devourer ability is in family 9, so nothing else changes.
    ("SpellPetBond", "Pet Bond", "The hunter's pet spells cost a Devourer nothing.", {**HIDDEN, "SpellClassSet": 9},
     [aura(A_ADD_PCT_MODIFIER, -100, OP_COST)]),
]


# --- row building ---------------------------------------------------------------------------------------------
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


def load_template() -> tuple[list[str], dict[str, str]]:
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
    return cols, dict(zip(cols, vals))


def q(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


def lit(v) -> str:
    if isinstance(v, str):
        return q(v)
    if isinstance(v, float):
        return repr(v)
    return str(int(v))


def row_sql(cols, tmpl, spell_id, fields: dict, name: str, subtext: str, desc: str, icon: int, aura_desc: str = "",
            masks: dict | None = None) -> str:
    """One spell_dbc row: the template, then `fields` (DSL output), then the texts."""
    v = dict(tmpl)
    for k, val in fields.items():
        if k not in v:
            raise SystemExit(f"spell {spell_id}: unknown column {k}")
        v[k] = lit(val)
    v["ID"] = str(spell_id)
    v["SpellIconID"] = str(icon)
    v["Name_Lang_enUS"] = q(name)
    v["NameSubtext_Lang_enUS"] = q(subtext)
    v["Description_Lang_enUS"] = q(desc)
    v["AuraDescription_Lang_enUS"] = q(aura_desc)
    for n, m in (masks or {}).items():
        v[f"EffectSpellClassMaskA_{n}"] = str(m)
    return "(" + ", ".join(v[c] for c in cols) + ")"


def effect_fields(specs):
    """effects() for a list of specs; `mask` on a spec becomes EffectSpellClassMaskA_n, done by the caller."""
    return effects(*[{k: val for k, val in s.items() if k != "mask"} for s in specs])


def masks_of(specs):
    return {i + 1: s["mask"] for i, s in enumerate(specs) if s.get("mask")}


def passive_fields(specs, affected=False):
    f = {**CLEAN, **PASSIVE, **NO_MECHANICS, **effect_fields(specs)}
    if affected or any(s.get("mask") for s in specs):
        f["SpellClassSet"] = FAMILY
    return f


def castable_fields(cost, cooldown, target, mask_name):
    f = {**CLEAN, **NO_MECHANICS, "Attributes": ATTR_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
         "CastingTimeIndex": CAST_INSTANT, "DurationIndex": 0, "InterruptFlags": 0, "ChannelInterruptFlags": 0,
         "RecoveryTime": cooldown, **GCD, "SpellVisualID_1": 0, "SchoolMask": 1}
    if cost:
        f.update(hunger(cost))
    if target == "enemy":
        f.update({"RangeIndex": RANGE_30})
        f.update(effects({"effect": E_DUMMY, "target": T_ENEMY}))
    elif target == "weapon":
        f.update({"RangeIndex": RANGE_COMBAT, "AttributesEx3": 0, "DefenseType": 2, "PreventionType": 2})  # melee
        f.update(effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 150, "target": T_ENEMY}))
    else:
        f.update({"RangeIndex": RANGE_SELF})
        f.update(effects({"effect": E_DUMMY}))
    if mask_name:
        f["SpellClassSet"] = FAMILY
        f["SpellClassMask_1"] = MASK[mask_name]
    return f


def camel(name: str) -> str:
    return "".join(w for w in re.sub(r"[^A-Za-z ]", "", name).title().split())


def main():
    cols, tmpl = load_template()
    spell_rows, talent_rows, md, script_rows = [], [], [], []
    ids_h: list[str] = []
    marks: list[str] = []
    next_spell = FIRST_TALENT_SPELL
    used_names = set()

    md.append("# Devourer talents and spec abilities\n")
    md.append("Generated by `tools/placeholders.py` (tasks 005 and 015): edit the script, not this file. "
              "Tiers open at 5 points per tier; a level-80 character has 71 points, each tree has about 95 ranks, "
              "so no tree can be taken whole. Cost = Anima. *How* says how it works: **aura** (stock aura, no "
              "code), **mod** (spell modifier on an ability, no code), **mark** (the module reads the rank, "
              "`src/DevourerTalents.cpp`), **active** (a castable spell, `spell_devourer_spec`), **real** (task 003 "
              "/ ChaosCore0.3, in `DevourerScripts.cpp`).\n")
    md.append(f"Ids: talent spells {FIRST_TALENT_SPELL}-{LAST_TALENT_SPELL} (and 9100050-9100069 for Iron Stomach, "
              f"Deep Hunger, Fluid Flesh, Swelling Brood), spec abilities {FIRST_SPEC_SPELL}-"
              f"{FIRST_SPEC_SPELL + len(SPEC_ABILITIES) - 1}, helper spells {FIRST_HELPER}-{LAST_HELPER}; talents "
              "9000-9179 (Glutton 9000-9059, Skinchanger 9060-9119 plus 9010, Brood 9120-9179 plus 9015). "
              f"Modifiable abilities carry spell family {FAMILY}.\n")

    def make_talent(tab, tree, tier, col, tid, name, ranks, kind, first_spell, prereq=0, prereq_rank=0):
        nonlocal next_spell
        t = TALENTS[name]
        icon = ICON[tree]
        spells = []
        first = first_spell or next_spell
        for r in range(1, ranks + 1):
            sid = first + r - 1
            if first_spell == 0:
                next_spell += 1
                if sid > LAST_TALENT_SPELL:
                    raise SystemExit("talent spell range exhausted")
            if t.active:
                a = t.active
                fields = castable_fields(a["cost"], a["cooldown"], a["target"], None)
                fields["SpellClassSet"] = 0
                spell_rows.append(row_sql(cols, tmpl, sid, fields, name, "", t.describe(r), icon))
                script_rows.append((sid, "spell_devourer_spec"))
            elif t.fx:
                specs = t.fx(r, t.per * r if not float(t.per * r).is_integer() else int(t.per * r))
                spell_rows.append(row_sql(cols, tmpl, sid, passive_fields(specs), name,
                                          f"Rank {r}" if ranks > 1 else "", t.describe(r), icon,
                                          masks=masks_of(specs)))
            else:
                spell_rows.append(row_sql(cols, tmpl, sid, {**CLEAN, **PASSIVE, **NO_MECHANICS,
                                                           **effects(aura(A_DUMMY))}, name,
                                          f"Rank {r}" if ranks > 1 else "", t.describe(r), icon))
            spells.append(sid)
        const = "Tal" + camel(name)
        if const in used_names:
            raise SystemExit(f"duplicate constant {const}")
        used_names.add(const)
        if t.active:
            ids_h.append(f"    constexpr uint32_t Spell{camel(name):<28} = {spells[0]};   // active talent: {name}")
        else:
            marks.append(f"    constexpr TalentRef {const:<24} {{ {spells[0]}, {ranks} }};   // {name}")
        ranks5 = (spells + [0] * 5)[:5]
        if tid is not None:
            talent_rows.append(f"({tid}, {tab}, {tier}, {col}, {', '.join(map(str, ranks5))}, "
                               f"{prereq}, {prereq_rank}, 0)")
        return spells

    for tab, tree, first_talent, names in TREES:
        existing = EXISTING.get(tab, {})
        names_iter = iter(names)
        talent_id = first_talent
        cells = {k: v[0] for k, v in existing.items()}
        rows_md = []
        for (tier, col), (t_id, t_name, t_ranks, real, first) in sorted(existing.items()):
            if real:
                rows_md.append((tier, col, t_id, t_ranks, t_name, "real", "", "", ""))
                continue
            make_talent(tab, tree, tier, col, None, t_name, t_ranks, "", first)
            rows_md.append((tier, col, t_id, t_ranks, t_name, TALENTS[t_name].kind(),
                            TALENTS[t_name].describe(t_ranks), "", ""))
        for tier, col, ranks, kind in LAYOUT:
            if (tier, col) in existing:
                continue
            name = next(names_iter)
            prereq, prereq_rank = 0, 0
            if kind == "capstone":
                prereq = cells.get(CAPSTONE_PREREQ, 0)
                prereq_rank = 4
            make_talent(tab, tree, tier, col, talent_id, name, ranks, kind, 0, prereq, prereq_rank)
            t = TALENTS[name]
            cost = t.active["cost"] if t.active else ""
            rows_md.append((tier, col, talent_id, ranks, name, t.kind(), t.describe(ranks),
                            cost, f"talent {prereq} (5/5)" if prereq else ""))
            cells[(tier, col)] = talent_id
            talent_id += 1
        leftover = list(names_iter)
        if leftover:
            raise SystemExit(f"{tree}: names not used: {leftover}")
        md.append(f"\n## {tree} (tab {tab})\n")
        md.append("| Tier | Col | Talent | Ranks | Name | How | Text (last rank) | Cost | Needs |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        for tier, col, t_id, ranks, name, how, text, cost, needs in sorted(rows_md):
            md.append(f"| {tier} | {col} | {t_id} | {ranks} | {name} | {how} | {text} | {cost} | {needs} |")
        md.append(f"\n{len(rows_md)} talents, {sum(r[3] for r in rows_md)} ranks.")

    missing = set(TALENTS) - used_names_by_title(TREES, EXISTING)
    if missing:
        raise SystemExit(f"talents defined but not placed: {sorted(missing)}")

    # spec abilities
    md.append("\n## Spec abilities (learned with the spec, from the level shown)\n")
    md.append("| Spec | Level | Spell | Name | Cost | Cooldown | Text |")
    md.append("|---|---|---|---|---|---|---|")
    md.append("| Glutton / Skinchanger / Brood | 1 | 9100011 / 9100012 / 9100013 | identity passives | | | real |")
    md.append("| Brood | 1 | 9100040 | Hatch Brood | 30 | 30 s | real |")
    spec_consts = []
    for i, (const, spec, level, name, text, cost, cooldown, target) in enumerate(SPEC_ABILITIES):
        sid = FIRST_SPEC_SPELL + i
        icon = ICON[spec]
        if target:
            fields = castable_fields(cost, cooldown, target, SPEC_MASK.get(name))
        else:                                              # Last Supper: a passive marker
            fields = {**CLEAN, **PASSIVE, **NO_MECHANICS, **effects(aura(A_DUMMY))}
        fields["SpellLevel"] = fields["BaseLevel"] = level
        spell_rows.append(row_sql(cols, tmpl, sid, fields, name, "", text, icon))
        if target and target != "weapon":
            script_rows.append((sid, "spell_devourer_spec"))
        spec_consts.append(f"    constexpr uint32_t {const:<30} = {sid};   // {spec}, level {level}: {name}")
        md.append(f"| {spec} | {level} | {sid} | {name} | {cost or '(all 100)'} | "
                  f"{cooldown // 1000 if cooldown else ''}{' s' if cooldown else ''} | {text} |")

    md.append("\n## Anima costs (task 015; the bar is 0-100, it does not drain)\n")
    md.append("Shapes cost nothing (`Devourer.AnimaPerShift = 0`). Gained by: devouring (30, `Devourer.HungerPerMeal`), "
              "every blow (3, `Devourer.HungerPerSwing`), the pet's kills (5), hatchling meals (10), Deep Hunger, Iron "
              "Maw and the other talents above. Concentrate is gone (the pet replaced it, `docs/pet.md`).\n")
    md.append("| Ability | Cost | Note |")
    md.append("|---|---|---|")
    for row in [
        ("Rush", "free", "8 s cooldown, unchanged"),
        ("Devour", "free", "a gain, never a cost"),
        ("Devour Whole (Glutton talent)", "20", "was free; Bloated Resolve lowers it"),
        ("Hatch Brood (Brood)", "30", "unchanged; Hatching Heat lowers it"),
        ("Void Breath, Rising Serpents", "25", "were 20"),
        ("Dragging Roar", "25", "unchanged"),
        ("Overrun (Baby Berserker)", "25", "was free"),
        ("Void Frenzy", "30", "was 40"),
        ("other form abilities", "as before", "the first ability of a form is filler (free or 15), the second 10-20 on the "
         "starter forms; only the ones above were moved to the proposal's scale"),
        ("spec abilities 20/40/60", "25 / 30 / 0 (Last Supper eats a full bar) etc.", "see the table above"),
        ("active talents", "15-25", "see the trees"),
    ]:
        md.append("| " + " | ".join(row) + " |")
    md.append("\nThe proposal's Rend Flesh (25), Hunger Pangs (30) and Unnerving Snarl (15) do not exist in this repo (they "
              "were CoA kit abilities), so nothing was priced for them; Gnash is read as the Devourer's own blow "
              "(Iron Maw changes it).")

    # helper spells
    helper_consts = []
    helper_id = FIRST_HELPER
    md.append("\n## Helper spells (the module casts them; not in the spellbook)\n")
    md.append("| Spell | Name |")
    md.append("|---|---|")
    for const, name, desc, extra, specs in HELPERS:
        if helper_id > LAST_HELPER:
            raise SystemExit("helper spell range exhausted")
        fields = {**CLEAN, **NO_MECHANICS, **extra, **effect_fields(specs)}
        if any(sp.get("target") == T_ENEMY for sp in specs):       # cast at an enemy from wherever the module stands
            fields["RangeIndex"] = RANGE_ANYWHERE
        spell_rows.append(row_sql(cols, tmpl, helper_id, fields, name, "", "", 1, desc))
        helper_consts.append(f"    constexpr uint32_t {const:<30} = {helper_id};   // {name}")
        md.append(f"| {helper_id} | {name} ({const}) |")
        helper_id += 1
    script_rows.append((9101033, "spell_devourer_hide"))
    assert helper_consts[3].startswith("    constexpr uint32_t SpellHide")

    col_list = ", ".join(f"`{c}`" for c in cols)
    last_spec = FIRST_SPEC_SPELL + len(SPEC_ABILITIES) - 1
    sql = [
        "-- Generated by tools/placeholders.py (tasks 005 and 015). Do not edit by hand: change the script and run it again.",
        "-- The Devourer's talent trees (11 tiers), spec abilities and helper spells. Safe to run again; removed by",
        "-- uninstall/world.sql (spells 9100000-9101099, talents 9000-9179). The four rank chains of task 003",
        "-- (9100050-9100069) are replaced here, so 2026_09_30_02 no longer defines them.",
        f"DELETE FROM `spell_dbc` WHERE `ID` BETWEEN 9100050 AND 9100069 OR `ID` BETWEEN {FIRST_TALENT_SPELL} AND {last_spec}",
        f"    OR `ID` BETWEEN {FIRST_HELPER} AND {LAST_HELPER};",
        f"INSERT INTO `spell_dbc` ({col_list}) VALUES",
        ",\n".join(spell_rows) + ";",
        "",
        "DELETE FROM `talent_dbc` WHERE `ID` BETWEEN 9020 AND 9059 OR `ID` BETWEEN 9060 AND 9179;",
        "INSERT INTO `talent_dbc` (`ID`, `TabID`, `TierID`, `ColumnIndex`, `SpellRank_1`, `SpellRank_2`, `SpellRank_3`,",
        "    `SpellRank_4`, `SpellRank_5`, `PrereqTalent_1`, `PrereqRank_1`, `Flags`) VALUES",
        ",\n".join(talent_rows) + ";",
        "",
        "-- Script bindings: the castable talents and spec abilities, and the hidden absorb (Devourer's Hide).",
        "DELETE FROM `spell_script_names` WHERE `ScriptName` IN ('spell_devourer_spec', 'spell_devourer_hide');",
        "INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES",
        ",\n".join(f"    ({sid}, '{name}')" for sid, name in sorted(script_rows)) + ";",
        "",
    ]
    OUT_SQL.write_text("\n".join(sql), encoding="utf-8")
    OUT_H.write_text("\n".join([
        "// Generated by tools/placeholders.py (tasks 005, 015) -- keep in step with 2026_09_30_07_devourer_placeholders.sql.",
        "#ifndef DEVOURER_TALENT_IDS_H",
        "#define DEVOURER_TALENT_IDS_H",
        "",
        "#include <cstdint>",
        "",
        "namespace Devourer",
        "{",
        "    // A talent's rank spells are consecutive: rank r is First + r - 1 (Mgr::Rank).",
        "    struct TalentRef { uint32_t First; uint8_t Ranks; };",
        "",
        "    // spec abilities",
        *spec_consts,
        "",
        "    // active talents",
        *[l for l in ids_h],
        "",
        "    // helper spells",
        *helper_consts,
        "",
        "    // marker talents (the module reads their rank)",
        *marks,
        "}",
        "",
        "#endif",
        "",
    ]), encoding="utf-8")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"talent spells {FIRST_TALENT_SPELL}-{next_spell - 1} ({next_spell - FIRST_TALENT_SPELL}), "
          f"talents {len(talent_rows)}, spec abilities {len(SPEC_ABILITIES)}, helpers {len(HELPERS)}")
    print(f"wrote {OUT_SQL.relative_to(REPO)}, {OUT_H.relative_to(REPO)}, {OUT_MD.relative_to(REPO)}")


def used_names_by_title(trees, existing):
    names = set()
    for _tab, _tree, _first, ns in trees:
        names |= set(ns)
    for cells in existing.values():
        for (_tid, name, _ranks, real, _first) in cells.values():
            if not real:
                names.add(name)
    return names


if __name__ == "__main__":
    main()
