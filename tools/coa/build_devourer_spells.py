#!/usr/bin/env python3
"""Every Devourer spell, described once, for both sides of the wire.

    python build_devourer_spells.py --spell-dbc <Spell.dbc to start from> --out <folder>

Starts from a client Spell.dbc (the stock 3.3.5a one works: it only lends template rows), removes every row in
the Devourer's range (9100000-9100899) and adds the spells defined below. Writes:
    <out>/DBFilesClient/Spell.dbc          not needed any more: tools/client/build_client_patch.py builds the
                                           client's Spell.dbc from the committed SQL
    <out>/devourer_spells.sql              the same rows for the server's `spell_dbc`, plus script bindings,
                                           proc rules, custom attributes, the shape table and the unlock item
                                           (committed as data/sql/db-world/2026_09_30_02_devourer_spells.sql,
                                           with a short header on top)
    <out>/DevourerSpellIds.h               the ids for the C++ module

Each spell is cloned from a stock spell (sane flags, visuals, icons) and overridden field by field.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
_COLS = json.loads((HERE / "spell_dbc_columns.json").read_text())
COLUMNS = [n for n, _ in _COLS]
TYPES = [t for _, t in _COLS]
COL = {n: i for i, n in enumerate(COLUMNS)}
assert len(COLUMNS) == 234
LOCALES = ["enUS", "enGB", "koKR", "frFR", "deDE", "enCN", "zhCN", "enTW", "zhTW", "esES", "esMX",
           "ruRU", "ptPT", "ptBR", "itIT", "Unk"]
STRING_GROUPS = ["Name_Lang", "NameSubtext_Lang", "Description_Lang", "AuraDescription_Lang"]
STRING_COLS = {COL[f"{g}_{l}"] for g in STRING_GROUPS for l in LOCALES}
FLOAT_COLS = {i for i, t in enumerate(TYPES) if t == "float"}
UNSIGNED_COLS = {i for i, t in enumerate(TYPES) if t.endswith("unsigned")}
RANGE = (9100000, 9100899)

# --- ids (the generated header keeps the C++ module in step) --------------------------------------------
IDS = {
    "SpellDevour": 9100001,
    "SpellUnlockSethrak": 9100009,
    "SpellUnlockBerserker": 9100010,
    "SpellIdentityGlutton": 9100011,
    "SpellIdentitySkinchanger": 9100012,
    "SpellIdentityBrood": 9100013,
    "SpellDevourWhole": 9100020,
    "SpellGorged": 9100021,
    "SpellMealMeat": 9100022,
    "SpellMealFlesh": 9100023,
    "SpellMealEssence": 9100024,
    "SpellSated": 9100025,
    "SpellHatchBrood": 9100040,
    "SpellSethrakForm": 9100100,
    "SpellSethrakChainLightning": 9100101,
    "SpellSethrakCoilStrike": 9100102,
    "SpellSethrakCoilStrikeHit": 9100103,
    "SpellSethrakSandstormShroud": 9100104,
    "SpellSethrakSnakeCharm": 9100105,
    "SpellSethrakRainOfToads": 9100106,
    "SpellSethrakRainOfToadsHit": 9100107,
    "SpellSethrakPlague": 9100108,
    "SpellVashnikForm": 9100300,
    "SpellVashnikStormChain": 9100301,
    "SpellVashnikCoilingWhirl": 9100302,
    "SpellVashnikCoilingWhirlHit": 9100303,
    "SpellVashnikSerpentsGaze": 9100305,
    "SpellVashnikPlagueSwarm": 9100306,
    "SpellVashnikPlagueSwarmHit": 9100307,
    "SpellVashnikRisingSerpents": 9100308,
    "SpellBerserkerForm": 9100200,
    "SpellBerserkerVoidBreath": 9100201,
    "SpellBerserkerStomp": 9100202,
    "SpellBerserkerRoar": 9100203,
    "SpellBerserkerRoarStun": 9100204,
    "SpellBerserkerSmash": 9100205,
    "SpellBerserkerBloodScent": 9100206,
    "SpellBerserkerBloodScentBuff": 9100207,
    # --- ChaosCore0.3 (Copus55, 2026-09-28): the Glutton's meals and talents -----------------------------
    "SpellMealGrave": 9100026,
    "SpellMealDragon": 9100027,
    "SpellMealDragonBreath": 9100028,
    "SpellMealDemon": 9100029,
    "SpellIndigestion": 9100030,
    "SpellTalentQuickDevour": 9100031,
    "SpellDevourQuick": 9100032,
    "SpellTalentRegurgitate": 9100033,
    "SpellRegurgitate": 9100034,
    "SpellTalentFeast": 9100035,
    "SpellTalentStretchedGut": 9100036,
    "SpellTalentThickHide": 9100037,
    "SpellTalentBileCoating": 9100038,
    "SpellDigestedThickHide": 9100039,
    "SpellDigested": 9100041,
    "SpellDigestedBileCoating": 9100042,
    # --- ChaosCore0.3: the Baby Berserker (shape 4) ----------------------------------------------------------
    "SpellBabyForm": 9100400,
    "SpellBabyOverrun": 9100401,
    "SpellBabyOverrunHit": 9100402,
    "SpellBabyGnaw": 9100403,
    "SpellBabyGnawBleed": 9100404,
    "SpellBabyPitifulWail": 9100405,
    "SpellBabyVoidFrenzy": 9100406,
    "SpellBabyVoidFrenzyHit": 9100407,
    "SpellBabyTeething": 9100408,
    "SpellBabyChewed": 9100409,
    # --- class 10: placeholder talents (5 ranks each) so every tree can be opened tier by tier ------------------
    **{f"SpellTalentIronStomach{r}": 9100049 + r for r in range(1, 6)},
    **{f"SpellTalentDeepHunger{r}": 9100054 + r for r in range(1, 6)},
    **{f"SpellTalentFluidFlesh{r}": 9100059 + r for r in range(1, 6)},
    **{f"SpellTalentSwellingBrood{r}": 9100064 + r for r in range(1, 6)},
}
I = IDS
SHAPE_SETHRAK = 1
SHAPE_BERSERKER = 2
SHAPE_VASHNIK = 3
VASHNIK_DISPLAY = 991029         # creature\\vashnik (RetroportTool); every texture is baked into the model
ITEM_BERSERKER_IDOL = 9100101
BERSERKER_DISPLAY = 991015       # creature\berserkerboss (orange); colourings in devourer_skin
BERSERKER_BROOD_DISPLAY = 991063 # hatchlings: creature\\babyberserker (orange; each colouring has its own)
ITEM_SETHRAK_IDOL = 9100100
SHAPE_CATEGORY = 4001            # every form spell shares it: one cooldown for all shapes
SHIFT_COOLDOWN = 8000
FORM_PLACEHOLDER_ENTRY = 299     # what a form shows for a tick before the module puts the body on
SETHRAK_DISPLAY = 200004         # CoA's Sethrak (melee, cat-incarnation model): it has a jump
SETHRAK_BROOD_DISPLAY = 4312     # Deviate Viper: a serpent pet model for a Sethrak's hatchlings
SNAKE_ENTRY = 2914               # Snake critter: Snake Charm's victim
NPC_HATCHLING = 9101100          # Brood hatchling (guardian; the module gives it the worn shape's pet model)
NPC_ECHO = 9101101               # Skinchanger's echo of a shape just left
NPC_RISING_SERPENT = 9101102     # Vashnik: a serpent risen from the ground; it repeats the Vashnik's spells
SUMMON_GUARDIAN_COUNTED = 1161   # SummonProperties: a guardian, as many as the effect's points say

# --- enums -------------------------------------------------------------------------------------------------
E_SCHOOL_DAMAGE, E_DUMMY, E_APPLY_AURA, E_ENERGIZE, E_TRIGGER_SPELL, E_CHARGE = 2, 3, 6, 30, 64, 96
A_DUMMY, A_PERIODIC_DAMAGE, A_MOD_ROOT, A_PROC_TRIGGER_SPELL, A_TRANSFORM = 4, 3, 26, 42, 56
A_DMG_TAKEN_PCT, A_HEALING_DONE_PCT, A_MELEE_HIT_TAKEN, A_RANGED_HIT_TAKEN = 87, 136, 184, 185
A_OBS_MOD_HEALTH, A_MOD_SCALE, A_MOD_DAMAGE_PCT_DONE, A_MOD_RESISTANCE_PCT = 20, 61, 79, 101
A_MOD_HEALTH_PCT, A_MOD_ATTACK_POWER_PCT = 133, 166
E_SUMMON = 28
SCHOOL_MAGIC_ALL = 126
T_CASTER, T_ENEMY, T_ANY = 1, 6, 25
POWER_RAGE = 1
SCHOOL_PHYSICAL, SCHOOL_NATURE, SCHOOL_ALL = 1, 8, 127
DUR_2S, DUR_3S, DUR_12S, DUR_INFINITE = 39, 27, 29, 21
DUR_10S, DUR_20S, DUR_5MIN, DUR_10MIN = 1, 18, 5, 6
DUR_4S = 35
DUR_1S, DUR_8S, DUR_9S, DUR_30S = 36, 31, 105, 9          # ChaosCore0.3
SHAPE_BABY = 4
CLASS_ID = 10                    # CLASS_DEVOURER (core-patch/)
CLASS_MASK = 1 << (CLASS_ID - 1)
BABY_DISPLAY = 991063            # creature\\babyberserker, orange; colourings 991062/991064/991065 in devourer_skin
A_MOD_FEAR, A_PERIODIC_ENERGIZE, A_MOD_RESISTANCE, A_MOD_DISARM, A_SCHOOL_ABSORB, A_MOD_THREAT = 7, 24, 22, 67, 69, 10
MECHANIC_STUN, MECHANIC_FEAR, MECHANIC_BLEED, MECHANIC_DISARM = 12, 5, 15, 3
SCHOOL_FIRE = 4
RADIUS_5 = 8
RANGE_25 = 34
PROC_DONE_MELEE_AUTO = 0x4
NO_MECHANICS = {"Mechanic": 0, "EffectMechanic_1": 0, "EffectMechanic_2": 0, "EffectMechanic_3": 0}
RANGE_30 = 4
RADIUS_8, RADIUS_12 = 14, 32
T_SRC_CASTER, T_SRC_AREA_ENEMY = 22, 15
A_MOD_STUN, A_MOD_DECREASE_SPEED, A_MOD_INCREASE_SPEED, A_MOD_MELEE_HASTE, A_PERIODIC_DUMMY = 12, 33, 31, 138, 226
E_WEAPON_PERCENT_DAMAGE, E_PULL_TOWARDS = 31, 124
SCHOOL_SHADOW = 32
SCHOOL_NATURE_INDEX = 3            # damage shields take the school index, not the mask
CAST_INSTANT = 1
RANGE_SELF, RANGE_COMBAT = 1, 2
ATTR0_ABILITY, ATTR0_PASSIVE, ATTR0_HIDDEN = 0x10, 0x40, 0x80
ATTR1_CHANNELED = 0x4
ATTR2_CAN_TARGET_DEAD = 0x1
DMG_MAGIC, DMG_MELEE = 1, 2
PROC_DONE_SPELL_MELEE, PROC_DONE_SPELL_MAGIC_NEG = 0x10, 0x10000


def hunger(points: int) -> dict:
    """Hunger is the rage bar: rage costs are stored times ten."""
    return {"PowerType": POWER_RAGE, "ManaCost": points * 10}


def effects(*specs):
    out = {}
    for n in range(1, 4):
        s = specs[n - 1] if n <= len(specs) else None
        amount = s.get("amount", 0) if s else 0
        spread = s.get("spread", 0) if s else 0
        out.update({
            f"Effect_{n}": s["effect"] if s else 0,
            f"EffectAura_{n}": s.get("aura", 0) if s else 0,
            # BasePoints + 1..DieSides: amount..amount+spread
            f"EffectDieSides_{n}": (spread + 1) if s else 0,
            f"EffectBasePoints_{n}": (amount - 1) if s else 0,
            f"ImplicitTargetA_{n}": s.get("target", T_CASTER) if s else 0,
            f"ImplicitTargetB_{n}": s.get("targetB", 0) if s else 0,
            f"EffectMiscValue_{n}": s.get("misc", 0) if s else 0,
            f"EffectMiscValueB_{n}": s.get("miscB", 0) if s else 0,
            f"EffectAuraPeriod_{n}": s.get("period", 0) if s else 0,
            f"EffectTriggerSpell_{n}": s.get("trigger", 0) if s else 0,
            f"EffectRadiusIndex_{n}": s.get("radius", 0) if s else 0,
            f"EffectChainTargets_{n}": s.get("chain", 0) if s else 0,
            f"EffectRealPointsPerLevel_{n}": 0.0,
            f"EffectMultipleValue_{n}": 0.0,
            f"EffectBonusMultiplier_{n}": 1.0 if s else 0.0,
            f"EffectChainAmplitude_{n}": 1.0 if s else 0.0,
        })
        for mask in "ABC":
            out[f"EffectSpellClassMask{mask}_{n}"] = 0
    return out


def aura(kind, amount=0, misc=0, target=T_CASTER, **kw):
    return {"effect": E_APPLY_AURA, "aura": kind, "amount": amount, "misc": misc, "target": target, **kw}


# Fields every Devourer spell resets: no class family (so no other class's talents touch it), no stock
# cooldown category, no stance requirement, no proc flags unless given.
CLEAN = {
    "SpellClassSet": 0, "SpellClassMask_1": 0, "SpellClassMask_2": 0, "SpellClassMask_3": 0,
    "Category": 0, "CategoryRecoveryTime": 0, "ShapeshiftMask": 0, "ShapeshiftExclude": 0,
    "ProcTypeMask": 0, "ProcChance": 101, "ProcCharges": 0, "ManaCost": 0, "PowerType": 0,
    "ManaCostPct": 0, "ManaCostPerLevel": 0, "ManaPerSecond": 0, "ManaPerSecondPerLevel": 0,
    "Reagent_1": 0, "ReagentCount_1": 0, "Totem_1": 0, "Totem_2": 0, "RequiresSpellFocus": 0,
    "EquippedItemClass": -1, "EquippedItemSubclass": 0, "EquippedItemInvTypes": 0,
    "CasterAuraState": 0, "TargetAuraState": 0, "CasterAuraSpell": 0, "TargetAuraSpell": 0,
    "ExcludeCasterAuraSpell": 0, "ExcludeTargetAuraSpell": 0, "MaxLevel": 0, "BaseLevel": 1, "SpellLevel": 1,
}


# --- ChaosCore0.3 (Copus55, 2026-09-28, designed with Zack) ---------------------------------------------------
PASSIVE = {"Attributes": ATTR0_ABILITY | ATTR0_PASSIVE, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
           "CastingTimeIndex": CAST_INSTANT, "RecoveryTime": 0}


def talent_passive(key, icon, name, text):
    """A Glutton talent: learned through the talent tree, a marker the module checks."""
    return (I[key], 25941, {**CLEAN, **PASSIVE, **NO_MECHANICS, "SpellIconID": icon, **effects(aura(A_DUMMY))},
            (name, text, ""))


def chaoscore03_glutton():
    """The Glutton (Zack, 28.9.): meals by what was eaten, Gorged only through the fight, and the talents:
    Quick Devour, Devour Whole, Regurgitate, Feast, Stretched Gut, and the choice of what Digested does."""
    d = []
    # Meals. Beast/Critter = Meal: Beast, Humanoid/Giant = Meal: Flesh, Elemental and the rest = Meal: Essence
    # (all three unchanged); new: Undead, Dragonkin, Demon; a Mechanical meal gives Indigestion instead.
    d.append((I["SpellMealGrave"], 22812, {
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "RecoveryTime": 0, "SpellVisualID_1": 0, "DurationIndex": DUR_10MIN, "SpellIconID": 1611,
        "ProcTypeMask": PROC_DONE_MELEE_AUTO | PROC_DONE_SPELL_MELEE, "ProcChance": 100,
        **effects(aura(A_DUMMY, 5)),
    }, ("Meal: Grave", "", "$s1% of the melee damage you deal heals you.")))
    d.append((I["SpellMealDragon"], 22812, {
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "RecoveryTime": 0, "SpellVisualID_1": 0, "DurationIndex": DUR_10MIN, "SpellIconID": 2598,
        **effects(aura(A_MOD_RESISTANCE, 75, SCHOOL_FIRE)),
    }, ("Meal: Dragonkin", "", "Fire resistance increased by $s1.")))
    d.append((I["SpellMealDragonBreath"], 11113, {                      # Blast Wave: fire bursts out of you
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "AttributesEx": 0, "RecoveryTime": 0, "SchoolMask": SCHOOL_FIRE,
        "SpellIconID": 2598, "DurationIndex": 0,
        **effects({"effect": E_SCHOOL_DAMAGE, "amount": 350, "spread": 70, "target": T_SRC_CASTER,
                   "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8}),
    }, ("Dragon's Fire", "The dragon you ate breathes out of you: $s1 Fire damage to enemies within 8 yards.", "")))
    d.append((I["SpellMealDemon"], 22812, {
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "RecoveryTime": 0, "SpellVisualID_1": 0, "DurationIndex": DUR_10MIN, "SpellIconID": 90,
        **effects(aura(A_PERIODIC_ENERGIZE, 20, POWER_RAGE, period=3000)),
    }, ("Meal: Fel", "", "Generating 2 Anima every 3 sec.")))
    d.append((I["SpellIndigestion"], 22812, {
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "RecoveryTime": 0, "SpellVisualID_1": 0, "DurationIndex": DUR_30S, "SpellIconID": 353,
        **effects(aura(A_MOD_DECREASE_SPEED, -10)),
    }, ("Indigestion", "", "Gears and bolts do not agree with you. Movement slowed by 10%.")))

    # Talents (their tree nodes are written by build_glutton_talents.py).
    d.append(talent_passive("SpellTalentQuickDevour", 1903, "Quick Devour",
        "Devour takes 1 sec instead of 3, and taking damage no longer interrupts it: you can eat mid-fight."))
    d.append((I["SpellDevourQuick"], 20578, {                            # Devour, 1 sec, not broken by damage
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": ATTR1_CHANNELED, "AttributesEx2": ATTR2_CAN_TARGET_DEAD,
        "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_1S, "RangeIndex": RANGE_COMBAT,
        "InterruptFlags": 0, "ChannelInterruptFlags": 0x0C08, "RecoveryTime": 0,   # no damage/melee breaks
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1000, "SpellVisualID_1": 5724, "SpellIconID": 166,
        **effects({"effect": E_DUMMY, "target": T_ANY}, aura(A_DUMMY)),
    }, ("Devour", "Channel for 1 sec to devour the corpse of a creature you have slain. Taking damage does not "
        "stop you. Its shape becomes yours and the meal feeds your Anima.", "Devouring.")))
    d.append(talent_passive("SpellTalentRegurgitate", 636, "Regurgitate",
        "Devour Whole holds the swallowed enemy's ability in: for 10 sec Devour Whole becomes Regurgitate, which "
        "releases it when you choose. If you wait too long, it bursts out anyway and you are Digested: the meal "
        "buff of what you ate is doubled for 10 sec."))
    d.append((I["SpellRegurgitate"], 20578, {
        **CLEAN, **NO_MECHANICS, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "CastingTimeIndex": CAST_INSTANT, "DurationIndex": 0, "RangeIndex": RANGE_SELF, "InterruptFlags": 0,
        "ChannelInterruptFlags": 0, "RecoveryTime": 0, "StartRecoveryCategory": 133, "StartRecoveryTime": 1000,
        "SpellIconID": 636, "SpellVisualID_1": 0, **effects({"effect": E_DUMMY}),
    }, ("Regurgitate", "Release the ability of the enemy you swallowed, at your current target.", "")))
    d.append(talent_passive("SpellTalentFeast", 1840, "Feast",
        "Devour eats every slain creature within 10 yards at once. Each one is a meal."))
    d.append(talent_passive("SpellTalentStretchedGut", 1685, "Stretched Gut",
        "Gorged stacks are no longer digested out of combat for 5 min, and Regurgitate waits 20 sec instead of "
        "10."))
    d.append(talent_passive("SpellTalentThickHide", 2323, "Digested: Thick Hide",
        "Choice. When Regurgitate runs out you are not Digested: your hide thickens instead, and all damage you "
        "take is reduced by 20% for 10 sec."))
    d.append(talent_passive("SpellTalentBileCoating", 198, "Digested: Bile Coating",
        "Choice. When Regurgitate runs out you are not Digested: a coat of bile absorbs damage equal to 5% of "
        "your maximum health for every stack of Gorged (at least 5%) for 10 sec."))
    d.append((I["SpellDigested"], 22812, {
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "RecoveryTime": 0, "SpellVisualID_1": 0, "DurationIndex": DUR_10S, "SpellIconID": 2046,
        **effects(aura(A_DUMMY)),
    }, ("Digested", "", "Your meal buff is doubled.")))
    d.append((I["SpellDigestedThickHide"], 22812, {
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "RecoveryTime": 0, "DurationIndex": DUR_10S, "SpellIconID": 2323,
        "SpellVisualID_1": 0, **effects(aura(A_DMG_TAKEN_PCT, -20, SCHOOL_ALL)),
    }, ("Thick Hide", "", "Damage taken reduced by 20%.")))
    d.append((I["SpellDigestedBileCoating"], 22812, {
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "RecoveryTime": 0, "DurationIndex": DUR_10S, "SpellIconID": 198,
        "SpellVisualID_1": 0, **effects(aura(A_SCHOOL_ABSORB, 1, SCHOOL_ALL)),
    }, ("Bile Coating", "", "Absorbs $s1 damage.")))
    return d


def chaoscore03_baby():
    """The Baby Berserker (shape 4; Zack, 28.9.): a small, fast skirmisher that grows into the Berserker.
    Visuals chosen to play the model's own animations: Gnaw -> EmoteEat (channel of 'Voracious Appetite'),
    Pitiful Wail -> SpellCastOmni ('Wailing Dead'), Void Frenzy -> BattleRoar (the roar of Psychic Scream), its
    hits -> AttackUnarmed with a heavy impact. Overrun's wind-up (ReadySpellOmni) is played by the module."""
    d = []
    d.append((I["SpellBabyForm"], 16591, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
        "Category": SHAPE_CATEGORY, "RecoveryTime": 0, "CategoryRecoveryTime": SHIFT_COOLDOWN,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1000, "InterruptFlags": 0, "AuraInterruptFlags": 0,
        "SpellIconID": 311, **effects(aura(A_TRANSFORM, 0, FORM_PLACEHOLDER_ENTRY)),
    }, ("Baby Berserker Form", "Take the shape of a young Berserker from the Voidstorm: Overrun, Gnaw, Pitiful "
        "Wail and Void Frenzy, and its teeth wear down what it bites. It grows into a Berserker. All shapes share "
        "one cooldown.", "Wearing the Baby Berserker's shape.")))

    d.append((I["SpellBabyOverrun"], 20578, {                          # a self dummy: the module does the run
        **CLEAN, **NO_MECHANICS, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "CastingTimeIndex": 3, "DurationIndex": 0, "RangeIndex": RANGE_SELF, "InterruptFlags": 0x0F,
        "ChannelInterruptFlags": 0, "RecoveryTime": 12000, "StartRecoveryCategory": 133, "StartRecoveryTime": 1000,
        "SpellIconID": 4925, "SpellVisualID_1": 0, **effects({"effect": E_DUMMY}),
    }, ("Overrun", "Wind up for 0.5 sec, then run down your target (up to 25 yards), or charge 20 yards straight ahead when "
        "you have none. Every enemy in your path takes 120% weapon damage and is knocked down for 1 sec.", "")))
    d.append((I["SpellBabyOverrunHit"], 7922, {                        # Charge Stun: the knockdown impact
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "SchoolMask": SCHOOL_PHYSICAL, "DefenseType": DMG_MELEE,
        "PreventionType": 2, "DurationIndex": DUR_1S, "Mechanic": MECHANIC_STUN, "RangeIndex": 13,
        **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 120, "target": T_ENEMY},
                  aura(A_MOD_STUN, target=T_ENEMY)),
    }, ("Overrun", "", "Knocked down.")))

    d.append((I["SpellBabyGnaw"], 15407, {                             # a channel: Voracious Appetite's EmoteEat
        **CLEAN, **NO_MECHANICS, "SchoolMask": SCHOOL_PHYSICAL, "DefenseType": DMG_MELEE, "PreventionType": 2,
        "RangeIndex": RANGE_COMBAT, "DurationIndex": DUR_3S, "RecoveryTime": 18000, "SpellIconID": 3010,
        "ChannelInterruptFlags": 0x0C0C,                                # moving breaks it, own swings do not
        "SpellVisualID_1": 11611, "EffectMechanic_2": MECHANIC_STUN, "EffectMechanic_3": MECHANIC_DISARM,
        **effects(aura(A_PERIODIC_DUMMY, target=T_ENEMY, period=1000), aura(A_MOD_STUN, target=T_ENEMY),
                  aura(A_MOD_DISARM, target=T_ENEMY)),
    }, ("Gnaw", "Grapple an enemy and gnaw on it for 3 sec: it is held and disarmed, and it bleeds for 9 sec. "
        "Every bite heals you for 4% of your maximum health (twice as much on an enemy Chewed 5 times) and gives "
        "5 Anima.", "Held and disarmed.")))
    d.append((I["SpellBabyGnawBleed"], 772, {                          # Rend's bleed, without Rend's swing
        **CLEAN, "SchoolMask": SCHOOL_PHYSICAL, "DurationIndex": DUR_9S, "RangeIndex": 13, "SpellVisualID_1": 0,
        "Mechanic": MECHANIC_BLEED, "EffectMechanic_1": MECHANIC_BLEED, "EffectMechanic_2": 0, "EffectMechanic_3": 0,
        "Attributes": 0,
        **effects(aura(A_PERIODIC_DAMAGE, 90, target=T_ENEMY, period=3000, spread=10)),
    }, ("Gnawed", "", "Bleeding for $s1 every 3 sec.")))

    d.append((I["SpellBabyPitifulWail"], 10890, {                      # Psychic Scream, with a wailing SpellCastOmni
        **CLEAN, **hunger(20), "RecoveryTime": 20000, "DurationIndex": DUR_4S, "SpellIconID": 89,
        "SpellVisualID_1": 745, "Mechanic": MECHANIC_FEAR, "EffectMechanic_1": 0, "EffectMechanic_2": 0,
        "EffectMechanic_3": 0, "MaxTargets": 5,
        **effects(aura(A_MOD_FEAR, target=T_SRC_CASTER, targetB=T_SRC_AREA_ENEMY, radius=RADIUS_8)),
    }, ("Pitiful Wail", "A wail so pitiful that up to 5 enemies within 8 yards flee in fear for 4 sec. Damage may "
        "break the fear.", "Fleeing in fear.")))

    d.append((I["SpellBabyVoidFrenzy"], 25225, {                       # starts with a BattleRoar
        **CLEAN, **NO_MECHANICS, **hunger(40), "RecoveryTime": 8000, "RangeIndex": RANGE_COMBAT,
        "SchoolMask": SCHOOL_PHYSICAL, "SpellIconID": 95, "SpellVisualID_1": 247, "AttributesEx3": 0, "CumulativeAura": 0,
        **effects({"effect": E_DUMMY, "target": T_ENEMY}),
    }, ("Void Frenzy", "Roar, then tear into an enemy with 5 fast strikes over 2 sec, each dealing 70% weapon "
        "damage.", "")))
    d.append((I["SpellBabyVoidFrenzyHit"], 25225, {                    # AttackUnarmed + a heavy impact
        **CLEAN, **NO_MECHANICS, "Attributes": 0, "RecoveryTime": 0, "RangeIndex": 13, "SchoolMask": SCHOOL_PHYSICAL,
        "SpellIconID": 95, "SpellVisualID_1": 2069, "AttributesEx3": 0, "StartRecoveryCategory": 0, "CumulativeAura": 0,
        "StartRecoveryTime": 0,
        **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 70, "target": T_ENEMY}),
    }, ("Void Frenzy", "", "")))

    d.append((I["SpellBabyTeething"], 25941, {
        **CLEAN, **PASSIVE, **NO_MECHANICS, "SpellIconID": 2865,
        "ProcTypeMask": PROC_DONE_MELEE_AUTO | PROC_DONE_SPELL_MELEE, "ProcChance": 100,
        **effects(aura(A_PROC_TRIGGER_SPELL, trigger=I["SpellBabyChewed"])),
    }, ("Teething", "Every attack you land chews on the enemy: Chewed lowers its armor by 2%, stacking up to 5 "
        "times. Gnaw heals twice as much on an enemy Chewed 5 times.", "")))
    d.append((I["SpellBabyChewed"], 172, {
        **CLEAN, **NO_MECHANICS, "SchoolMask": SCHOOL_PHYSICAL, "DispelType": 0, "DurationIndex": DUR_10S,
        "CumulativeAura": 5, "SpellIconID": 2865, "SpellVisualID_1": 0, "RangeIndex": 13, "Attributes": 0,
        "InterruptFlags": 0,
        **effects(aura(A_MOD_RESISTANCE_PCT, -2, 1, target=T_ENEMY)),
    }, ("Chewed", "", "Armor reduced by $s1%.")))
    return d


def definitions():
    """(id, template, overrides, texts). Numbers are a first pass, to be tuned in play."""
    d = []
    d.append((I["SpellDevour"], 20578, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": ATTR1_CHANNELED, "AttributesEx2": ATTR2_CAN_TARGET_DEAD,
        "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_3S, "RangeIndex": RANGE_COMBAT,
        "InterruptFlags": 0x0F, "ChannelInterruptFlags": 15374, "RecoveryTime": 0,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1500, "SpellVisualID_1": 5724, "SpellIconID": 166,
        **effects({"effect": E_DUMMY, "target": T_ANY}, aura(A_DUMMY)),
    }, ("Devour", "Channel for 3 sec to devour the corpse of a creature you have slain. Its shape becomes yours "
        "and the meal feeds your Anima.", "Devouring.")))

    d.append((I["SpellUnlockSethrak"], 20578, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "CastingTimeIndex": 16, "DurationIndex": 0, "RangeIndex": RANGE_SELF, "InterruptFlags": 0x0F,
        "ChannelInterruptFlags": 0, "RecoveryTime": 0, "StartRecoveryCategory": 133, "StartRecoveryTime": 1500,
        "SpellIconID": 3058, **effects({"effect": E_DUMMY, "misc": SHAPE_SETHRAK}),
    }, ("Devour the Idol", "Devour the idol's memory of the Sethrak. Their shape becomes yours.", "")))

    # --- spec identities: the free passive each spec's talent tree starts with (level 10) -----------------
    # The client's talent system needs one per spec (ChrSpecs identity entry); the module gives them teeth.
    for key, icon, name, text in (
        ("SpellIdentityGlutton", 166, "Bottomless Appetite",
         "Every meal makes you larger and tougher, and what you eat decides how. Your size draws the enemy: "
         "threat you cause is increased by 100%."),
        ("SpellIdentitySkinchanger", 3058, "Restless Skin",
         "Your shapes answer faster: the shared shift cooldown is shorter. A shape you leave in combat lingers "
         "for 8 sec as an echo that fights your target and casts the shape's Ability 1."),
        ("SpellIdentityBrood", 689, "Mother of the Brood",
         "What you have eaten can be born again: your hatchlings fight and devour for you."),
    ):
        d.append((I[key], 25941, {
            **CLEAN, "Attributes": ATTR0_ABILITY | ATTR0_PASSIVE, "DurationIndex": DUR_INFINITE,
            "RangeIndex": RANGE_SELF, "CastingTimeIndex": CAST_INSTANT, "SpellIconID": icon,
            # ChaosCore0.3: the Glutton tanks without a taunt, so its identity passive doubles its threat.
            **(effects(aura(A_DUMMY), aura(A_MOD_THREAT, 100, SCHOOL_ALL)) if key == "SpellIdentityGlutton"
               else effects(aura(A_DUMMY))),
        }, (name, text, "")))

    # --- Glutton: Devour Whole, Gorged, meals --------------------------------------------------------------
    d.append((I["SpellDevourWhole"], 20578, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "CastingTimeIndex": CAST_INSTANT, "DurationIndex": 0, "RangeIndex": RANGE_COMBAT, "InterruptFlags": 0,
        "ChannelInterruptFlags": 0, "RecoveryTime": 20000, "StartRecoveryCategory": 133, "StartRecoveryTime": 1000,
        "SpellIconID": 166, "SpellVisualID_1": 5724, **effects({"effect": E_DUMMY, "target": T_ENEMY}),
    }, ("Devour Whole", "Swallow a weakened enemy whole: one below 25% health, or far below your level. It dies, "
        "you regain health, and one of its own abilities bursts out of you (with Regurgitate you hold it in "
        "instead). Counts as a meal.", "")))

    # ChaosCore0.3: Gorged lasts while you fight; the module digests a stack every few seconds out of combat
    # (Stretched Gut holds them). +5% size per stack (was 4%), so the growth shows.
    d.append((I["SpellGorged"], 22812, {
        **CLEAN, "Attributes": 0, "RecoveryTime": 0, "DurationIndex": DUR_INFINITE, "CumulativeAura": 10,
        "SpellIconID": 166,
        **effects(aura(A_MOD_HEALTH_PCT, 3), aura(A_MOD_SCALE, 5)),
    }, ("Gorged", "", "Maximum health increased by $s1% and size by $s2%. Digested out of combat.")))

    for key, name, eff, tip in (
        ("SpellMealMeat", "Meal: Beast", aura(A_MOD_RESISTANCE_PCT, 15, 1), "Armor increased by $s1%."),
        ("SpellMealFlesh", "Meal: Flesh", aura(A_MOD_ATTACK_POWER_PCT, 10), "Attack power increased by $s1%."),
        ("SpellMealEssence", "Meal: Essence", aura(A_MOD_DAMAGE_PCT_DONE, 10, SCHOOL_MAGIC_ALL),
         "Magic damage increased by $s1%."),
    ):
        d.append((I[key], 22812, {
            **CLEAN, "Attributes": 0, "RecoveryTime": 0, "DurationIndex": DUR_10MIN, "SpellIconID": 166,
            **effects(eff),
        }, (name, "", tip)))

    d.append((I["SpellSated"], 22812, {
        **CLEAN, "Attributes": 0, "RecoveryTime": 0, "DurationIndex": DUR_10S, "SpellIconID": 166,
        **effects(aura(A_OBS_MOD_HEALTH, 4, period=2000)),
    }, ("Sated", "", "Regaining $s1% of maximum health every 2 sec.")))

    d += chaoscore03_glutton()

    # --- Brood: Hatch Brood ------------------------------------------------------------------------------
    d.append((I["SpellHatchBrood"], 51533, {
        **CLEAN, **hunger(30), "Attributes": ATTR0_ABILITY, "RecoveryTime": 30000, "DurationIndex": DUR_20S,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1500, "SpellIconID": 689,
        **effects({"effect": E_SUMMON, "misc": NPC_HATCHLING, "miscB": SUMMON_GUARDIAN_COUNTED, "amount": 2,
                   "target": 47, "targetB": 1, "radius": 7}),
    }, ("Hatch Brood", "Two hatchlings break out of what you have eaten and fight for you for 20 sec, wearing the shape of "
        "your worn body's kin. What they kill, they devour for you. Devour one of your own hatchlings to eat it back.",
        "")))

    d.append((I["SpellUnlockBerserker"], 20578, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "CastingTimeIndex": 16, "DurationIndex": 0, "RangeIndex": RANGE_SELF, "InterruptFlags": 0x0F,
        "ChannelInterruptFlags": 0, "RecoveryTime": 0, "StartRecoveryCategory": 133, "StartRecoveryTime": 1500,
        "SpellIconID": 3058, **effects({"effect": E_DUMMY, "misc": SHAPE_BERSERKER}),
    }, ("Devour the Idol", "Devour the idol's memory of the Berserker. Its shape becomes yours.", "")))

    # --- the Berserker (void-touched brute). Visuals chosen to play the model's own animations:
    #     Void Breath -> ChannelCastDirected, Stomp -> DragonStomp, Roar -> BattleRoar, Smash -> AttackUnarmed.
    d.append((I["SpellBerserkerForm"], 16591, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
        "Category": SHAPE_CATEGORY, "RecoveryTime": 0, "CategoryRecoveryTime": SHIFT_COOLDOWN,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1000, "InterruptFlags": 0, "AuraInterruptFlags": 0,
        "SpellIconID": 2028, **effects(aura(A_TRANSFORM, 0, FORM_PLACEHOLDER_ENTRY)),
    }, ("Berserker Form", "Take the shape of a void-touched Berserker: Void Breath, Stomp, Dragging Roar and Smash, "
        "and it grows faster the more blood is in the air. All shapes share one cooldown.",
        "Wearing the Berserker's shape.")))

    d.append((I["SpellBerserkerVoidBreath"], 15407, {                  # Mind Flay: a directed channel
        **CLEAN, **hunger(20), "RecoveryTime": 10000, "DurationIndex": DUR_3S, "RangeIndex": RANGE_30,
        "SchoolMask": SCHOOL_SHADOW, "SpellIconID": 2028,
        **effects(aura(A_PERIODIC_DAMAGE, 180, target=T_ENEMY, period=1000, spread=20),
                  aura(A_MOD_DECREASE_SPEED, -30, target=T_ENEMY)),
    }, ("Void Breath", "Breathe the void at an enemy for 3 sec: $o1 Shadow damage over the channel, and it is "
        "slowed by 30% while it lasts.", "Slowed. Taking Shadow damage every second.")))

    d.append((I["SpellBerserkerStomp"], 55821, {                       # Massive Stomp: DragonStomp
        **CLEAN, **hunger(15), "Attributes": ATTR0_ABILITY, "RecoveryTime": 12000, "DurationIndex": DUR_4S,
        "RangeIndex": RANGE_SELF, "SchoolMask": SCHOOL_PHYSICAL, "DefenseType": DMG_MELEE,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1000,
        **effects({"effect": E_SCHOOL_DAMAGE, "amount": 300, "spread": 60, "target": T_SRC_CASTER,
                   "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8},
                  aura(A_MOD_DECREASE_SPEED, -50, target=T_SRC_CASTER, targetB=T_SRC_AREA_ENEMY, radius=RADIUS_8)),
    }, ("Stomp", "Stomp the ground: $s1 Physical damage to enemies within 8 yards, and they are slowed by 50% for "
        "4 sec.", "Slowed.")))

    d.append((I["SpellBerserkerRoar"], 64825, {                        # Staggering Roar: BattleRoar
        **CLEAN, **hunger(25), "Attributes": ATTR0_ABILITY, "RecoveryTime": 30000, "DurationIndex": 0,
        "RangeIndex": RANGE_SELF, "SchoolMask": SCHOOL_PHYSICAL, "StartRecoveryCategory": 133,
        "StartRecoveryTime": 1000,
        **effects({"effect": E_PULL_TOWARDS, "misc": 200, "target": T_SRC_CASTER, "targetB": T_SRC_AREA_ENEMY,
                   "radius": RADIUS_12},
                  {"effect": E_DUMMY, "target": T_SRC_CASTER, "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_12}),
    }, ("Dragging Roar", "Roar and drag every enemy within 12 yards to you. When they land they are stunned for "
        "2 sec.", "")))

    d.append((I["SpellBerserkerRoarStun"], 7922, {
        **CLEAN, "Attributes": 0, "DurationIndex": DUR_2S, "Mechanic": 12, "SchoolMask": SCHOOL_PHYSICAL,
        **effects(aura(A_MOD_STUN, target=T_ENEMY)),
    }, ("Dragging Roar", "", "Stunned.")))

    d.append((I["SpellBerserkerSmash"], 18944, {                       # Smash: AttackUnarmed
        **CLEAN, "Attributes": ATTR0_ABILITY, "RecoveryTime": 6000, "RangeIndex": RANGE_COMBAT,
        "SchoolMask": SCHOOL_PHYSICAL, "DefenseType": DMG_MELEE, "StartRecoveryCategory": 133,
        "StartRecoveryTime": 1000, "CastingTimeIndex": CAST_INSTANT,
        **effects({"effect": E_WEAPON_PERCENT_DAMAGE, "amount": 200, "target": T_ENEMY},
                  {"effect": E_ENERGIZE, "amount": 150, "misc": POWER_RAGE}),
    }, ("Smash", "Smash an enemy for $s1% weapon damage, 50% more if it is stunned. Generates 15 Anima.", "")))

    d.append((I["SpellBerserkerBloodScent"], 25941, {
        **CLEAN, "Attributes": ATTR0_ABILITY | ATTR0_PASSIVE, "DurationIndex": DUR_INFINITE,
        "RangeIndex": RANGE_SELF, "CastingTimeIndex": CAST_INSTANT, "SpellIconID": 2028,
        **effects(aura(A_PERIODIC_DUMMY, period=1000)),
    }, ("Blood Scent", "You smell blood in the air: for every unit near you below 50% health, movement speed is "
        "increased by 5% and attack speed by 10%, stacking, until the blood is gone.", "")))

    d.append((I["SpellBerserkerBloodScentBuff"], 22812, {
        **CLEAN, "Attributes": 0, "RecoveryTime": 0, "DurationIndex": DUR_INFINITE, "CumulativeAura": 10,
        "SpellIconID": 2028,
        **effects(aura(A_MOD_INCREASE_SPEED, 5), aura(A_MOD_MELEE_HASTE, 10)),
    }, ("Scent of Blood", "", "Movement speed increased by $s1% and attack speed by $s2%.")))

    # --- the Vashnik: what a Sethrak grows into. Its model has a real Whirlwind, spell casts and a roar. ------
    d.append((I["SpellVashnikForm"], 16591, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
        "Category": SHAPE_CATEGORY, "RecoveryTime": 0, "CategoryRecoveryTime": SHIFT_COOLDOWN,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1000, "InterruptFlags": 0, "AuraInterruptFlags": 0,
        "SpellIconID": 3058, **effects(aura(A_TRANSFORM, 0, FORM_PLACEHOLDER_ENTRY)),
    }, ("Vashnik Form", "Take the shape of a Vashnik, a Sethrak grown great: Storm Chain, Coiling Whirl, Rising "
        "Serpents and Serpent's Gaze, and a plague swarm follows your strikes. All shapes share one cooldown.",
        "Wearing the Vashnik's shape.")))

    d.append((I["SpellVashnikStormChain"], 10605, {                     # SpellCastDirected
        **CLEAN, **hunger(15), "RecoveryTime": 6000,
        **effects({"effect": E_SCHOOL_DAMAGE, "amount": 560, "spread": 80, "target": T_ENEMY, "chain": 5}),
    }, ("Storm Chain", "Hurls a storm bolt at the enemy, dealing $s1 Nature damage and jumping to additional nearby "
        "enemies. Affects up to $x1 total targets.", "")))

    d.append((I["SpellVashnikCoilingWhirl"], 100, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RecoveryTime": 12000,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1000,
        **effects({"effect": E_CHARGE, "target": T_ENEMY},
                  {"effect": E_ENERGIZE, "amount": 150, "misc": POWER_RAGE},
                  {"effect": E_TRIGGER_SPELL, "target": T_ENEMY, "trigger": I["SpellVashnikCoilingWhirlHit"]}),
    }, ("Coiling Whirl", "Lunge at an enemy and whirl your coils around you: Nature damage to every enemy within 8 "
        "yards, and they are rooted for 3 sec. Generates 15 Anima.", "")))

    d.append((I["SpellVashnikCoilingWhirlHit"], 1680, {                 # Whirlwind
        **CLEAN, "Attributes": 0, "SchoolMask": SCHOOL_NATURE, "DefenseType": DMG_MELEE, "DurationIndex": DUR_3S,
        "Mechanic": 7, "RangeIndex": RANGE_SELF,
        **effects({"effect": E_SCHOOL_DAMAGE, "amount": 340, "spread": 60, "target": T_SRC_CASTER,
                   "targetB": T_SRC_AREA_ENEMY, "radius": RADIUS_8},
                  aura(A_MOD_ROOT, target=T_SRC_CASTER, targetB=T_SRC_AREA_ENEMY, radius=RADIUS_8)),
    }, ("Coiling Whirl", "Coiled: rooted.", "Rooted.")))

    d.append((I["SpellVashnikRisingSerpents"], 51533, {                # summons two guardians
        **CLEAN, **hunger(20), "Attributes": ATTR0_ABILITY, "RecoveryTime": 45000, "DurationIndex": DUR_20S,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1500, "SpellIconID": 3058,
        **effects({"effect": E_SUMMON, "misc": NPC_RISING_SERPENT, "miscB": SUMMON_GUARDIAN_COUNTED, "amount": 2,
                   "target": 47, "targetB": 1, "radius": 7}),
    }, ("Rising Serpents", "Two serpents rise from the ground beside you for 20 sec. They do not move, but every "
        "spell you cast at an enemy, they cast too.", "")))

    d.append((I["SpellVashnikSerpentsGaze"], 51514, {                   # SpellCastOmni
        **CLEAN, **hunger(25), "RecoveryTime": 45000,
        **effects(aura(A_TRANSFORM, 0, SNAKE_ENTRY, target=T_ENEMY), aura(60, -1, target=T_ENEMY)),
    }, ("Serpent's Gaze", "Your gaze turns the enemy into a snake for up to 30 sec. Charmed, it cannot attack or "
        "cast; damage breaks the charm. Your risen serpents each charm another enemy near it.",
        "Charmed into a snake.")))

    d.append((I["SpellVashnikPlagueSwarm"], 25941, {
        **CLEAN, "Attributes": ATTR0_ABILITY | ATTR0_PASSIVE, "DurationIndex": DUR_INFINITE,
        "RangeIndex": RANGE_SELF, "CastingTimeIndex": CAST_INSTANT,
        "ProcTypeMask": PROC_DONE_SPELL_MELEE | PROC_DONE_SPELL_MAGIC_NEG, "ProcChance": 20,
        **effects(aura(A_PROC_TRIGGER_SPELL, trigger=I["SpellVashnikPlagueSwarmHit"])),
    }, ("Plague Swarm", "Storm Chain and Coiling Whirl have a 20% chance to call down a plague swarm on up to 5 "
        "enemies near the target: healing they do is reduced by 50%, and they suffer Nature damage over 12 sec, "
        "stacking up to 5 times. Cannot happen more than once every 6 sec.", "")))

    d.append((I["SpellVashnikPlagueSwarmHit"], 20578, {
        **CLEAN, "Attributes": 0, "AttributesEx": 0, "AttributesEx2": 0, "CastingTimeIndex": CAST_INSTANT,
        "DurationIndex": 0, "RangeIndex": 13, "ChannelInterruptFlags": 0, "InterruptFlags": 0,
        "SchoolMask": SCHOOL_NATURE, "SpellVisualID_1": 0,
        **effects({"effect": E_DUMMY, "target": T_ENEMY}),
    }, ("Plague Swarm", "", "")))

    # --- the Sethrak ------------------------------------------------------------------------------------
    d.append((I["SpellSethrakForm"], 16591, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "AttributesEx2": 0,
        "CastingTimeIndex": CAST_INSTANT, "DurationIndex": DUR_INFINITE, "RangeIndex": RANGE_SELF,
        "Category": SHAPE_CATEGORY, "RecoveryTime": 0, "CategoryRecoveryTime": SHIFT_COOLDOWN,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1000, "InterruptFlags": 0, "AuraInterruptFlags": 0,
        "SpellIconID": 3058, **effects(aura(A_TRANSFORM, 0, FORM_PLACEHOLDER_ENTRY)),
    }, ("Sethrak Form", "Take the shape of a Sethrak: Chain Lightning, Coil Strike, Sandstorm Shroud and Snake Charm, "
        "and toads rain on those you strike. All shapes share one cooldown.", "Wearing the Sethrak's shape.")))

    d.append((I["SpellSethrakChainLightning"], 10605, {
        **CLEAN, **hunger(15), "RecoveryTime": 6000,
        **effects({"effect": E_SCHOOL_DAMAGE, "amount": 420, "spread": 60, "target": T_ENEMY, "chain": 3}),
    }, ("Chain Lightning", "Hurls a lightning bolt at the enemy, dealing $s1 Nature damage and then jumping to "
        "additional nearby enemies. Affects up to $x1 total targets.", "")))

    d.append((I["SpellSethrakCoilStrike"], 100, {
        **CLEAN, "Attributes": ATTR0_ABILITY, "AttributesEx": 0, "RecoveryTime": 12000,
        "StartRecoveryCategory": 133, "StartRecoveryTime": 1000,
        **effects({"effect": E_CHARGE, "target": T_ENEMY},
                  {"effect": E_ENERGIZE, "amount": 100, "misc": POWER_RAGE},
                  {"effect": E_TRIGGER_SPELL, "target": T_ENEMY, "trigger": I["SpellSethrakCoilStrikeHit"]}),
    }, ("Coil Strike", "Lunge at an enemy, striking for Nature damage and coiling around it: rooted for 2 sec. "
        "Generates 10 Anima.", "")))

    d.append((I["SpellSethrakCoilStrikeHit"], 7922, {
        **CLEAN, "Attributes": 0, "SchoolMask": SCHOOL_NATURE, "DefenseType": DMG_MELEE,
        "DurationIndex": DUR_2S, "Mechanic": 7,
        **effects({"effect": E_SCHOOL_DAMAGE, "amount": 260, "spread": 40, "target": T_ENEMY},
                  aura(A_MOD_ROOT, target=T_ENEMY)),
    }, ("Coil Strike", "Coiled: rooted.", "Rooted.")))

    d.append((I["SpellSethrakSandstormShroud"], 22812, {
        **CLEAN, **hunger(20), "RecoveryTime": 60000, "DurationIndex": DUR_12S,
        **effects(aura(A_DMG_TAKEN_PCT, -20, SCHOOL_ALL), aura(A_MELEE_HIT_TAKEN, -20), aura(A_RANGED_HIT_TAKEN, -20)),
    }, ("Sandstorm Shroud", "A howling sandstorm wraps around you for 12 sec: damage taken reduced by 20%, and "
        "attacks against you are 20% more likely to miss.", "Damage taken reduced by 20%. Attacks against you miss "
        "20% more often.")))

    d.append((I["SpellSethrakSnakeCharm"], 51514, {
        **CLEAN, **hunger(20), "RecoveryTime": 45000,
        **effects(aura(A_TRANSFORM, 0, SNAKE_ENTRY, target=T_ENEMY), aura(60, -1, target=T_ENEMY)),
    }, ("Snake Charm", "Transforms the enemy into a snake for up to 30 sec. While charmed it cannot attack or cast. "
        "Damage breaks the charm.", "Charmed into a snake.")))

    d.append((I["SpellSethrakRainOfToads"], 25941, {
        **CLEAN, "Attributes": ATTR0_ABILITY | ATTR0_PASSIVE, "DurationIndex": DUR_INFINITE,
        "RangeIndex": RANGE_SELF, "CastingTimeIndex": CAST_INSTANT,
        "ProcTypeMask": PROC_DONE_SPELL_MELEE | PROC_DONE_SPELL_MAGIC_NEG, "ProcChance": 15,
        **effects(aura(A_PROC_TRIGGER_SPELL, trigger=I["SpellSethrakRainOfToadsHit"])),
    }, ("Rain of Toads", "Chain Lightning and Coil Strike have a 15% chance to call down plague toads around "
        "the target. They plague up to 3 nearby enemies: healing they do is reduced by 50%, and they suffer "
        "Nature damage over 12 sec, stacking up to 5 times. Cannot happen more than once every 6 sec.", "")))

    d.append((I["SpellSethrakRainOfToadsHit"], 20578, {
        **CLEAN, "Attributes": 0, "AttributesEx": 0, "AttributesEx2": 0, "CastingTimeIndex": CAST_INSTANT,
        "DurationIndex": 0, "RangeIndex": 13, "ChannelInterruptFlags": 0, "InterruptFlags": 0,
        "SchoolMask": SCHOOL_NATURE, "SpellVisualID_1": 0,
        **effects({"effect": E_DUMMY, "target": T_ENEMY}),
    }, ("Rain of Toads", "", "")))

    d.append((I["SpellSethrakPlague"], 172, {
        **CLEAN, "SchoolMask": SCHOOL_NATURE, "DispelType": 3, "DurationIndex": DUR_12S, "CumulativeAura": 5,
        **effects(aura(A_PERIODIC_DAMAGE, 45, target=T_ENEMY, period=3000),
                  aura(A_HEALING_DONE_PCT, -50, target=T_ENEMY)),
    }, ("Plague", "", "Healing done reduced by 50%. $s1 Nature damage every 3 sec.")))
    d += chaoscore03_baby()
    d += talent_placeholders()
    return d


def talent_placeholders():
    """Class 10: every talent tier needs 5 points in its tree, so each tree has 5-rank talents that do nothing yet
    (Glutton: Iron Stomach in tier 0 and Deep Hunger in tier 1; Skinchanger and Brood: one each). The talent rows
    are in data/sql/db-world/2026_09_30_01_devourer_class.sql."""
    d = []
    for key, icon, name in (("SpellTalentIronStomach", 166, "Iron Stomach"), ("SpellTalentDeepHunger", 166, "Deep Hunger"),
                            ("SpellTalentFluidFlesh", 3058, "Fluid Flesh"),
                            ("SpellTalentSwellingBrood", 689, "Swelling Brood")):
        for rank in range(1, 6):
            d.append(talent_passive(f"{key}{rank}", icon, name, "Placeholder talent: it has no effect yet."))
    return d


# --- server-side data that belongs to these spells ----------------------------------------------------------
def world_sql() -> list[str]:
    forms = [I["SpellSethrakForm"], I["SpellBerserkerForm"], I["SpellVashnikForm"], I["SpellBabyForm"]]
    return [
        "-- Script bindings.",
        f"DELETE FROM `spell_script_names` WHERE `spell_id` BETWEEN {RANGE[0]} AND {RANGE[1]};",
        "INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES",
        f"    ({I['SpellDevour']}, 'spell_devourer_devour'),",
        f"    ({I['SpellDevourQuick']}, 'spell_devourer_devour'),",
        f"    ({I['SpellRegurgitate']}, 'spell_devourer_regurgitate'),",
        f"    ({I['SpellMealGrave']}, 'spell_devourer_meal_grave'),",
        f"    ({I['SpellDigested']}, 'spell_devourer_digested'),",
        f"    ({I['SpellDigestedBileCoating']}, 'spell_devourer_bile_coating'),",
        f"    ({I['SpellBabyOverrun']}, 'spell_devourer_baby_overrun'),",
        f"    ({I['SpellBabyGnaw']}, 'spell_devourer_baby_gnaw'),",
        f"    ({I['SpellBabyVoidFrenzy']}, 'spell_devourer_baby_void_frenzy'),",
        f"    ({I['SpellUnlockSethrak']}, 'spell_devourer_unlock'),",
        f"    ({I['SpellUnlockBerserker']}, 'spell_devourer_unlock'),",
        f"    ({I['SpellBerserkerRoar']}, 'spell_devourer_berserker_roar'),",
        f"    ({I['SpellBerserkerSmash']}, 'spell_devourer_berserker_smash'),",
        f"    ({I['SpellBerserkerBloodScent']}, 'spell_devourer_blood_scent'),",
        f"    ({I['SpellVashnikRisingSerpents']}, 'spell_devourer_rising_serpents'),",
        f"    ({I['SpellDevourWhole']}, 'spell_devourer_devour_whole'),",
        f"    ({I['SpellHatchBrood']}, 'spell_devourer_hatch_brood'),",
        *[f"    ({f}, 'spell_devourer_form')," for f in forms],
        f"    ({I['SpellSethrakRainOfToads']}, 'spell_devourer_rain_of_toads_passive'),",
        f"    ({I['SpellSethrakRainOfToadsHit']}, 'spell_devourer_rain_of_toads'),",
        f"    ({I['SpellVashnikPlagueSwarm']}, 'spell_devourer_rain_of_toads_passive'),",
        f"    ({I['SpellVashnikPlagueSwarmHit']}, 'spell_devourer_rain_of_toads');",
        "",
        "-- Forms are put back by the module at login and after resurrection, never saved with the character.",
        f"DELETE FROM `spell_custom_attr` WHERE `spell_id` BETWEEN {RANGE[0]} AND {RANGE[1]};",
        "INSERT INTO `spell_custom_attr` (`spell_id`, `attributes`) VALUES",
        ",\n".join(f"    ({f}, 0x01000000)" for f in forms) + ";",
        "",
        "-- Rain of Toads: 15% from Chain Lightning / Coil Strike (the script checks which), at most every 6 sec.",
        f"DELETE FROM `spell_proc` WHERE `SpellId` BETWEEN {RANGE[0]} AND {RANGE[1]};",
        "INSERT INTO `spell_proc` (`SpellId`, `SchoolMask`, `SpellFamilyName`, `SpellFamilyMask0`, `SpellFamilyMask1`,"
        " `SpellFamilyMask2`, `ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`, `HitMask`, `AttributesMask`,"
        " `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`) VALUES",
        f"    ({I['SpellSethrakRainOfToads']}, 0, 0, 0, 0, 0, {PROC_DONE_SPELL_MELEE | PROC_DONE_SPELL_MAGIC_NEG},"
        " 1, 2, 0, 0, 0, 15, 6000, 0),",
        f"    ({I['SpellVashnikPlagueSwarm']}, 0, 0, 0, 0, 0, {PROC_DONE_SPELL_MELEE | PROC_DONE_SPELL_MAGIC_NEG},"
        " 1, 2, 0, 0, 0, 20, 6000, 0),",
        "    -- ChaosCore0.3: Teething chews on every landed attack; Meal: Grave heals from melee damage done.",
        f"    ({I['SpellBabyTeething']}, 0, 0, 0, 0, 0, {PROC_DONE_MELEE_AUTO | PROC_DONE_SPELL_MELEE},"
        " 1, 2, 0, 0, 0, 100, 0, 0),",
        f"    ({I['SpellMealGrave']}, 0, 0, 0, 0, 0, {PROC_DONE_MELEE_AUTO | PROC_DONE_SPELL_MELEE},"
        " 1, 2, 0, 0, 0, 100, 0, 0);",
    ]


def shape_sql() -> list[str]:
    return [
        "-- Shapes: the form spell, the base look and the kit.",
        "DELETE FROM `devourer_shape` WHERE `shape_id` IN (1, 2, 3, 4);",
        "INSERT INTO `devourer_shape` (`shape_id`, `name`, `form_spell`, `display_id`, `scale`, `spell_1`, `spell_2`,"
        " `spell_3`, `spell_4`, `passive`, `brood_display`) VALUES",
        f"    ({SHAPE_SETHRAK}, 'Sethrak', {I['SpellSethrakForm']}, {SETHRAK_DISPLAY}, 1, {I['SpellSethrakChainLightning']},"
        f" {I['SpellSethrakCoilStrike']}, {I['SpellSethrakSandstormShroud']}, {I['SpellSethrakSnakeCharm']},"
        f" {I['SpellSethrakRainOfToads']}, {SETHRAK_BROOD_DISPLAY}),",
        f"    ({SHAPE_BERSERKER}, 'Berserker', {I['SpellBerserkerForm']}, {BERSERKER_DISPLAY}, 1,"
        f" {I['SpellBerserkerVoidBreath']}, {I['SpellBerserkerStomp']}, {I['SpellBerserkerRoar']},"
        f" {I['SpellBerserkerSmash']}, {I['SpellBerserkerBloodScent']}, {BERSERKER_BROOD_DISPLAY}),",
        f"    ({SHAPE_VASHNIK}, 'Vashnik', {I['SpellVashnikForm']}, {VASHNIK_DISPLAY}, 1,"
        f" {I['SpellVashnikStormChain']}, {I['SpellVashnikCoilingWhirl']}, {I['SpellVashnikRisingSerpents']},"
        f" {I['SpellVashnikSerpentsGaze']}, {I['SpellVashnikPlagueSwarm']}, {SETHRAK_BROOD_DISPLAY}),",
        f"    ({SHAPE_BABY}, 'Baby Berserker', {I['SpellBabyForm']}, {BABY_DISPLAY}, 1,"
        f" {I['SpellBabyOverrun']}, {I['SpellBabyGnaw']}, {I['SpellBabyPitifulWail']},"
        f" {I['SpellBabyVoidFrenzy']}, {I['SpellBabyTeething']}, {BABY_DISPLAY});",
        "",
        "-- Until Sethrak can be devoured in the world, an idol teaches the shape. The module gives one to every",
        "-- Devourer that has no shape yet.",
        f"DELETE FROM `item_template` WHERE `entry` IN ({ITEM_SETHRAK_IDOL}, {ITEM_BERSERKER_IDOL});",
        "INSERT INTO `item_template` (`entry`, `class`, `subclass`, `name`, `displayid`, `Quality`, `Flags`,"
        " `BuyCount`, `AllowableClass`, `AllowableRace`, `ItemLevel`, `RequiredLevel`, `stackable`, `bonding`,"
        " `spellid_1`, `spelltrigger_1`, `spellcharges_1`, `spellcooldown_1`, `spellcategorycooldown_1`, `description`)"
        " VALUES",
        f"    ({ITEM_SETHRAK_IDOL}, 15, 0, 'Idol of the Sethrak', 34955, 3, 0, 1, {CLASS_MASK}, -1, 1, 1, 1, 1,"
        f" {I['SpellUnlockSethrak']}, 0, -1, -1, -1, 'A serpent idol from the dunes. A Devourer can taste what it remembers.'),",
        f"    ({ITEM_BERSERKER_IDOL}, 15, 0, 'Idol of the Berserker', 34955, 3, 0, 1, {CLASS_MASK}, -1, 1, 1, 1, 1,"
        f" {I['SpellUnlockBerserker']}, 0, -1, -1, -1, 'A void-scarred fang. A Devourer can taste what it remembers.');",
    ]


# --- DBC --------------------------------------------------------------------------------------------------
class Dbc:
    def __init__(self, path: Path):
        data = path.read_bytes()
        magic, self.count, self.fields, self.rsize, ss = struct.unpack_from("<4s4I", data)
        assert magic == b"WDBC" and self.fields == 234, path
        self.records = bytearray(data[20:20 + self.count * self.rsize])
        self.strings = bytearray(data[20 + self.count * self.rsize:20 + self.count * self.rsize + ss])
        self._interned: dict[str, int] = {}
        self.reindex()

    def reindex(self):
        self.index = {struct.unpack_from("<I", self.records, i * self.rsize)[0]: i for i in range(self.count)}

    def row(self, rid: int) -> list[int]:
        return list(struct.unpack_from(f"<{self.fields}I", self.records, self.index[rid] * self.rsize))

    def drop_range(self, lo: int, hi: int) -> int:
        keep = bytearray()
        kept = 0
        for i in range(self.count):
            rec = self.records[i * self.rsize:(i + 1) * self.rsize]
            if not lo <= struct.unpack_from("<I", rec)[0] <= hi:
                keep += rec
                kept += 1
        dropped = self.count - kept
        self.records, self.count = keep, kept
        self.reindex()
        return dropped

    def intern(self, text: str) -> int:
        if not text:
            return 0
        if text not in self._interned:
            self._interned[text] = len(self.strings)
            self.strings += text.encode("utf-8") + b"\0"
        return self._interned[text]

    def put(self, row: list[int]):
        packed = struct.pack(f"<{self.fields}I", *row)
        if row[0] in self.index:
            i = self.index[row[0]]
            self.records[i * self.rsize:(i + 1) * self.rsize] = packed
        else:
            self.index[row[0]] = self.count
            self.records += packed
            self.count += 1

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        head = struct.pack("<4s4I", b"WDBC", self.count, self.fields, self.rsize, len(self.strings))
        path.write_bytes(head + bytes(self.records) + bytes(self.strings))


def to_u32(value, col):
    if col in FLOAT_COLS:
        return struct.unpack("<I", struct.pack("<f", float(value)))[0]
    return int(value) & 0xFFFFFFFF


def sql_value(raw: int, col: int, text: str | None):
    if col in STRING_COLS:
        return "'" + (text or "").replace("\\", "\\\\").replace("'", "''") + "'"
    if col in FLOAT_COLS:
        return repr(struct.unpack("<f", struct.pack("<I", raw))[0])
    if col in UNSIGNED_COLS:
        return str(raw)
    return str(struct.unpack("<i", struct.pack("<I", raw))[0])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spell-dbc", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()

    spells = Dbc(a.spell_dbc)
    dropped = spells.drop_range(*RANGE)
    rows = []
    for sid, template, overrides, (name, desc, tip) in definitions():
        assert RANGE[0] <= sid <= RANGE[1]
        row = spells.row(template)
        row[COL["ID"]] = sid
        for g in STRING_GROUPS:
            for l in LOCALES:
                row[COL[f"{g}_{l}"]] = 0
        for key, value in overrides.items():
            row[COL[key]] = to_u32(value, COL[key])
        texts = {"Name_Lang_enUS": name, "Description_Lang_enUS": desc, "AuraDescription_Lang_enUS": tip,
                 "NameSubtext_Lang_enUS": ""}
        for key, value in texts.items():
            row[COL[key]] = spells.intern(value)
        for g in STRING_GROUPS:
            row[COL[f"{g}_Mask"]] = 0x00FF01FE
        spells.put(row)
        rows.append("(" + ",".join(sql_value(row[i], i, texts.get(COLUMNS[i])) for i in range(234)) + ")")

    spells.save(a.out / "DBFilesClient" / "Spell.dbc")
    sql = ["-- Generated by mod-devourer/tools/build_devourer_spells.py -- do not edit by hand.",
           f"DELETE FROM `spell_dbc` WHERE `ID` BETWEEN {RANGE[0]} AND {RANGE[1]};",
           "INSERT INTO `spell_dbc` (" + ",".join(f"`{c}`" for c in COLUMNS) + ") VALUES",
           ",\n".join(rows) + ";", "", *world_sql(), "", *shape_sql(), ""]
    (a.out / "devourer_spells.sql").write_text("\n".join(sql), encoding="utf-8")

    header = ["// Generated by tools/build_devourer_spells.py -- keep in step with the client patch.",
              "#ifndef DEVOURER_SPELL_IDS_H", "#define DEVOURER_SPELL_IDS_H", "", "#include <cstdint>", "",
              "namespace Devourer", "{"]
    width = max(len(k) for k in IDS)
    header += [f"    constexpr uint32_t {k:<{width}} = {v};" for k, v in IDS.items()]
    header += ["}", "", "#endif", ""]
    (a.out / "DevourerSpellIds.h").write_text("\n".join(header), encoding="utf-8")
    print(f"{len(rows)} Devourer spells written, {dropped} old rows in {RANGE[0]}-{RANGE[1]} removed -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
