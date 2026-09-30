"""Devourer content: Feat buttons, the Scaled Tree (lizards, basilisks, salamanders, warp stalkers)
and the signature feats and Instincts of the beast families.

Imported by build_devourer_spells.py. Every entry is (id, template spell, overrides, text); the
template lends its visual and icon, everything that matters is overridden here.

Numbers scale with level through EffectRealPointsPerLevel (SpellLevel 1, MaxLevel 80), unlike the
creatures' own spells, which keep the values of the level they were made for.

Durations (SpellDuration): 2s 39, 3s 27, 4s 35, 5s 28, 6s 32, 8s 31, 10s 1, 12s 29, 15s 8, inf 21
Ranges (SpellRange): self 1, melee 2, 20yd 3, 30yd 4, 25yd 34
Radius (SpellRadius): 8yd 14, 10yd 13
"""

# --- enums ---------------------------------------------------------------------------------------
E_SCHOOL_DAMAGE, E_DUMMY, E_TELEPORT, E_AURA = 2, 3, 5, 6
E_WEAPON_PCT, E_CHARGE, E_KNOCKBACK, E_LEAP_BACK = 31, 96, 98, 138

A_PERIODIC_DAMAGE, A_CONFUSE, A_FEAR, A_STUN, A_DAMAGE_SHIELD = 3, 5, 7, 12, 15
A_STEALTH, A_STEALTH_DETECT, A_RESISTANCE, A_ROOT = 16, 17, 22, 26
A_SPEED, A_SLOW, A_PROC_TRIGGER, A_DODGE = 31, 33, 42, 49
A_PERIODIC_LEECH, A_SWIM_SPEED, A_DISARM, A_MECH_IMMUNITY = 53, 58, 67, 77
A_DMG_DONE_PCT, A_WATER_BREATHING, A_DMG_TAKEN_PCT = 79, 82, 87
A_FEATHER_FALL, A_HEALING_PCT, A_HEALTH_PCT, A_MELEE_HASTE = 105, 118, 133, 138
A_ARMOR_PCT, A_SAFE_FALL, A_ATTACKER_MELEE_HIT = 142, 144, 184
A_DUMMY, A_PERIODIC_DUMMY = 4, 226
A_PERIODIC_TRIGGER, A_HIT_CHANCE, A_ATTACK_POWER, A_RESISTANCE_PCT = 23, 54, 99, 101
E_INTERRUPT = 68
T_CASTER_AREA_PARTY = 20
MECHANIC_SLEEP = 10
AURA_INTERRUPT_DAMAGE = 0x2

T_CASTER, T_ENEMY, T_AREA_ENEMY, T_SRC_CASTER, T_CONE, T_DEST_BEHIND = 1, 6, 15, 22, 104, 65

PHYSICAL, HOLY, FIRE, NATURE, FROST, SHADOW, ARCANE = 1, 2, 4, 8, 16, 32, 64
MELEE, MAGIC = 2, 1
MECHANIC_ROOT, MECHANIC_BLEED = 7, 15

PROC_DONE_MELEE = 0x04 | 0x10          # auto attack + melee-class spells
PROC_TAKEN_MELEE = 0x08 | 0x20
PROC_KILL = 0x02

# --- the ids the C++ module knows ----------------------------------------------------------------
EVOLVE, FEAT_I, FEAT_II = 9100046, 9100050, 9100051
RUN_DOWN_CHASE, VENOM_GLANDS_POISON, PARALYZED = 9100260, 9100261, 9100262
BLOODLUST_STACK, STUBBORN_BUFF, KILLING_RHYTHM_BUFF = 9100263, 9100264, 9100265
TIME_WARP_SLOW = 9100122
STANCE_PREDATOR, STANCE_HULK, ECHO = 9100270, 9100271, 9100280
E_HEAL_PCT, E_DISPEL_MECHANIC, A_SHAPESHIFT = 136, 108, 36
FORM_CAT, FORM_BEAR, MECHANIC_SNARE = 1, 5, 11


def definitions(template_row, COL, effects, aura, PASSIVE_BUFF):
    defs = []

    CLEAN = {
        "Category": 0, "DispelType": 0, "Mechanic": 0, "ShapeshiftMask": 0, "unk_320_2": 0,
        "ShapeshiftExclude": 0, "unk_320_3": 0, "Targets": 0, "TargetCreatureType": 0,
        "RequiresSpellFocus": 0, "FacingCasterFlags": 0, "CasterAuraState": 0, "TargetAuraState": 0,
        "ExcludeCasterAuraState": 0, "ExcludeTargetAuraState": 0, "CasterAuraSpell": 0,
        "TargetAuraSpell": 0, "ExcludeCasterAuraSpell": 0, "ExcludeTargetAuraSpell": 0,
        "ManaCostPerLevel": 0, "ManaPerSecond": 0, "ManaPerSecondPerLevel": 0, "Speed": 0.0,
        "ModalNextSpell": 0, "CumulativeAura": 0, "Totem_1": 0, "Totem_2": 0,
        **{f"Reagent_{i}": 0 for i in range(1, 9)}, **{f"ReagentCount_{i}": 0 for i in range(1, 9)},
        "EquippedItemClass": -1, "EquippedItemSubclass": 0, "EquippedItemInvTypes": 0,
        "ManaCostPct": 0, "MaxTargetLevel": 0, "SpellClassSet": 0, "SpellClassMask_1": 0,
        "SpellClassMask_2": 0, "SpellClassMask_3": 0, "MaxTargets": 0, "PreventionType": 0,
        "StanceBarOrder": 0, "MinFactionID": 0, "MinReputation": 0, "RequiredAuraVision": 0,
        "RequiredTotemCategoryID_1": 0, "RequiredTotemCategoryID_2": 0, "RequiredAreasID": 0,
        "RuneCostID": 0, "SpellMissileID": 0, "PowerDisplayID": 0, "SpellDescriptionVariableID": 0,
        "SpellDifficultyID": 0, "SpellPriority": 0,
    }

    PASSIVE_BUFF = {k: v for k, v in PASSIVE_BUFF.items() if not k.startswith("SpellVisualID")}

    def active(school, dmg_class, rng, cooldown, cast=1, duration=0, **extra):
        return {**PASSIVE_BUFF, **CLEAN, "Attributes": 0x10, "CastingTimeIndex": cast,
                "DurationIndex": duration, "RangeIndex": rng, "RecoveryTime": cooldown,
                "SchoolMask": school, "DefenseType": dmg_class, "MaxLevel": 80,
                "InterruptFlags": 0x0F if cast != 1 else 0, **extra}

    def passive(**extra):
        return {**PASSIVE_BUFF, **CLEAN, "MaxLevel": 80, **extra}

    def copy_effect(spell, n):
        """An effect slot exactly as the stock spell has it (charge, leap and knockback carry values
        that are easier to borrow than to guess)."""
        row = template_row(spell)
        keys = ["Effect", "EffectDieSides", "EffectBasePoints", "ImplicitTargetA", "ImplicitTargetB",
                "EffectRadiusIndex", "EffectAura", "EffectAuraPeriod", "EffectMiscValue", "EffectMiscValueB",
                "EffectTriggerSpell", "EffectChainTargets", "EffectMechanic"]
        raw = {k: row[COL[f"{k}_{n}"]] for k in keys}
        raw["EffectBasePoints"] = raw["EffectBasePoints"] - (1 << 32) if raw["EffectBasePoints"] >= 1 << 31 else raw["EffectBasePoints"]
        raw["EffectMiscValue"] = raw["EffectMiscValue"] - (1 << 32) if raw["EffectMiscValue"] >= 1 << 31 else raw["EffectMiscValue"]
        return {"effect": raw["Effect"], "raw": raw}

    def strike(pct, **kw):
        return {"effect": E_WEAPON_PCT, "amount": pct, "target": T_ENEMY, **kw}

    def bolt(amount, ppl, **kw):
        return {"effect": E_SCHOOL_DAMAGE, "amount": amount, "ppl": ppl, "target": T_ENEMY, **kw}

    def debuff(aura_type, amount=0, misc=0, **kw):
        return {"effect": E_AURA, "aura": aura_type, "amount": amount, "misc": misc, "target": T_ENEMY, **kw}

    def buff(aura_type, amount=0, misc=0, **kw):
        return {"effect": E_AURA, "aura": aura_type, "amount": amount, "misc": misc, "target": T_CASTER, **kw}

    def add(sid, template, fields, effs, name, desc, tip=""):
        # The template lends its visual unless the entry names one.
        visual = {"SpellVisualID_1": template_row(template)[COL["SpellVisualID_1"]]}
        defs.append((sid, template, {**visual, **fields, **effects(*effs)},
                     {"name": name, "desc": desc, "tip": tip or desc}))

    # --- Feat buttons and the evolution flourish --------------------------------------------------
    add(EVOLVE, 47241, passive(Attributes=0x10 | 0x80, DurationIndex=36, SpellIconID=2851),
        [buff(A_DUMMY)], "Evolution", "")
    add(FEAT_I, 25941, active(PHYSICAL, 0, 1, 0, StartRecoveryCategory=133, StartRecoveryTime=1000, SpellIconID=1534),
        [{"effect": E_DUMMY, "target": T_CASTER}], "Feat I",
        "Use the first Feasted Feat of the body you are wearing, on your target. Open the Devourer window to see it.")
    add(FEAT_II, 25941, active(PHYSICAL, 0, 1, 0, StartRecoveryCategory=133, StartRecoveryTime=1000, SpellIconID=2961),
        [{"effect": E_DUMMY, "target": T_CASTER}], "Feat II",
        "Use the second Feasted Feat of the body you are wearing, on your target. Open the Devourer window to see it.")

    # --- The Scaled Tree: custom feats and Instincts ----------------------------------------------
    add(9100100, 6730, active(PHYSICAL | NATURE, MELEE, 2, 8000, duration=32),
        [strike(100), debuff(A_SLOW, -30)], "Crackling Tail",
        "A charged tail lash for 100% weapon damage that slows the target by 30% for 6 sec.",
        "Movement slowed by 30%.")
    add(9100101, 25941, passive(SchoolMask=NATURE, SpellIconID=19),
        [buff(A_DAMAGE_SHIELD, 3, ppl=0.5)], "Static Hide",
        "Your scales crackle: melee attackers take $s1 Nature damage.")
    add(9100102, 25941, passive(SchoolMask=NATURE, SpellIconID=19),
        [buff(A_DAMAGE_SHIELD, 8, ppl=1.0), buff(A_RESISTANCE, 20, NATURE, ppl=2)], "Storm Hide",
        "Melee attackers take $s1 Nature damage. Nature resistance increased by $s2.")
    add(9100103, 25941, passive(SchoolMask=NATURE, SpellIconID=19),
        [buff(A_DAMAGE_SHIELD, 10, ppl=1.5), buff(A_DMG_DONE_PCT, 15, NATURE), buff(A_SPEED, 20)],
        "Primal Storm", "Melee attackers take $s1 Nature damage. Nature damage +$s2%. Movement speed +$s3%.")
    add(9100104, 3635, active(NATURE, MAGIC, 3, 25000, cast=4, duration=27),
        [debuff(A_STUN)], "Stone Gaze",
        "A petrifying stare that stuns the target for 3 sec.", "Stunned.")
    add(9100105, 25941, passive(SpellIconID=1708),
        [buff(A_ARMOR_PCT, 20, PHYSICAL)], "Stone Scales", "Armor increased by $s1%.")
    add(9100106, 25941, passive(SpellIconID=1708),
        [buff(A_ARMOR_PCT, 30, PHYSICAL), buff(A_DAMAGE_SHIELD, 5, ppl=1.0)], "Crystalline Hide",
        "Armor increased by $s1%. Melee attackers take $s2 damage from the crystals.")
    add(9100107, 51723, active(PHYSICAL, MELEE, 1, 15000),
        [{"effect": E_SCHOOL_DAMAGE, "amount": 20, "ppl": 4, "target": T_SRC_CASTER,
          "targetB": T_AREA_ENEMY, "radius": 14}], "Bladespine Volley",
        "Launches your spines, dealing $s1 Physical damage to all enemies within 8 yards.")
    add(9100108, 25941, passive(SpellIconID=1708),
        [buff(A_ARMOR_PCT, 30, PHYSICAL), buff(A_DAMAGE_SHIELD, 10, ppl=2.0)], "Bladespine Hide",
        "Armor increased by $s1%. Melee attackers take $s2 damage.")
    add(9100110, 8056, active(FROST, MAGIC, 34, 6000, duration=35),
        [bolt(10, 3), debuff(A_SLOW, -40)], "Slick Spit",
        "Spits icy slime for $s1 Frost damage and slows the target by 40% for 4 sec.", "Slowed.")
    add(9100111, 1953, active(PHYSICAL, 0, 1, 20000, duration=35),
        [buff(A_SPEED, 40), buff(A_MECH_IMMUNITY, 0, MECHANIC_ROOT)], "Slippery",
        "Slip free of roots and move 40% faster for 4 sec.", "Slippery: immune to roots, 40% faster.")
    add(9100112, 25941, passive(SpellIconID=2851),
        [buff(A_SWIM_SPEED, 60), buff(A_WATER_BREATHING)], "Amphibious",
        "Swim speed increased by $s1%. You can breathe underwater.")
    add(9100113, 100, active(FROST, MELEE, 34, 15000),
        [copy_effect(100, 1), bolt(15, 3)], "Tidal Lunge",
        "Lunge at the target in a rush of water, dealing $s2 Frost damage.")
    add(9100114, 25941, passive(SpellIconID=2851),
        [buff(A_SWIM_SPEED, 80), buff(A_WATER_BREATHING), buff(A_DMG_DONE_PCT, 10, FROST)], "Amphibious",
        "Swim speed +$s1%. You breathe underwater. Frost damage +$s3%.")
    add(9100115, 25941, passive(SchoolMask=FIRE, SpellIconID=816),
        [buff(A_DAMAGE_SHIELD, 15, ppl=2.0), buff(A_DMG_DONE_PCT, 10, FIRE)], "Molten Blood",
        "Melee attackers take $s1 Fire damage. Fire damage +$s2%.")

    # Warp, as the Wrath-era warp stalker had it: teleport to an enemy up to 30 yards away, then a
    # 50% chance to avoid the next 3 melee attacks for 4 sec. 15 sec cooldown.
    add(9100120, 35346, active(ARCANE, MAGIC, 4, 15000, duration=35,
                                ProcTypeMask=PROC_TAKEN_MELEE, ProcChance=100, ProcCharges=3),
        [{"effect": E_TELEPORT, "target": T_CASTER, "targetB": T_DEST_BEHIND},
         buff(A_ATTACKER_MELEE_HIT, -50)], "Warp",
        "Teleports to an enemy up to 30 yards away and gives you a 50% chance to avoid the next 3 melee attacks. Lasts 4 sec.",
        "50% chance to avoid melee attacks.")
    # Time Warp, the later warp stalker slow, as a passive: melee hits warp time around the target.
    add(9100121, 25941, passive(SchoolMask=ARCANE, SpellIconID=1711, ProcTypeMask=PROC_DONE_MELEE, ProcChance=100),
        [buff(A_PROC_TRIGGER, trigger=TIME_WARP_SLOW)], "Time Warp",
        "Your melee attacks warp time around the target, slowing its movement by 50% for 6 sec. This cannot happen more often than once every 15 sec.")
    add(TIME_WARP_SLOW, 32922, active(ARCANE, MAGIC, 4, 0, duration=32),
        [debuff(A_SLOW, -50)], "Time Warp", "", "Movement slowed by 50%.")
    add(9100123, 32939, active(ARCANE, 0, 1, 20000, duration=27),
        [buff(A_DODGE, 50), buff(A_SPEED, 30)], "Phase Shimmer",
        "Flicker between worlds: +50% dodge and +30% movement speed for 3 sec.", "Phasing: +50% dodge, +30% speed.")
    add(9100124, 32942, active(ARCANE, 0, 1, 30000, duration=32, AuraInterruptFlags=0x1007),
        [buff(A_STEALTH, 5, ppl=5)], "Phasing",
        "Slip out of phase and become invisible for up to 6 sec. Taking damage, attacking or casting brings you back.",
        "Out of phase.")

    # --- Beast family signatures: (feat id, instinct id) = 9100200 + 2i, 9100201 + 2i ----------
    fam = 9100200

    # Wolf: Run Down / Pack Scent
    add(fam + 0, 3604, active(PHYSICAL, MELEE, 2, 10000, duration=32),
        [strike(110), debuff(A_SLOW, -50)], "Run Down",
        "A hamstringing bite for 110% weapon damage that slows the target by 50% for 6 sec. If the target was already slowed, you gain 30% movement speed for 3 sec.",
        "Movement slowed by 50%.")
    add(fam + 1, 25941, passive(SpellIconID=1573), [buff(A_DMG_DONE_PCT, 5, PHYSICAL)], "Pack Scent",
        "Physical damage increased by $s1%.")
    # Cat: Pounce / Landing Paws
    add(fam + 2, 39449, active(PHYSICAL, MELEE, 34, 20000, duration=39),
        [copy_effect(100, 1), strike(100), debuff(A_STUN)], "Pounce",
        "Leap at a target up to 25 yards away for 100% weapon damage and stun it for 2 sec.", "Stunned.")
    add(fam + 3, 25941, passive(SpellIconID=493), [buff(A_SAFE_FALL, 200), buff(A_DODGE, 3)], "Landing Paws",
        "You take no damage from ordinary falls. Dodge +$s2%.")
    # Crab: Pincer Grip / Hard Shell
    add(fam + 4, 676, active(PHYSICAL, MELEE, 2, 30000, duration=28),
        [strike(50), debuff(A_DISARM)], "Pincer Grip",
        "Clamps the target's weapon arm: 50% weapon damage and disarm for 5 sec.", "Disarmed.")
    add(fam + 5, 25941, passive(SpellIconID=1580), [buff(A_ARMOR_PCT, 15, PHYSICAL), buff(A_SLOW, -10)], "Hard Shell",
        "Armor increased by $s1%, movement speed reduced by 10%.")
    # Tallstrider: Kick Off / Long Legs
    add(fam + 6, 781, active(PHYSICAL, MELEE, 2, 20000),
        [{"effect": E_KNOCKBACK, "amount": 50, "misc": 200, "target": T_ENEMY}, copy_effect(781, 1)], "Kick Off",
        "Kick the target away and spring backwards.")
    add(fam + 7, 25941, passive(SpellIconID=1587), [buff(A_SPEED, 10)], "Long Legs", "Movement speed increased by $s1%.")
    # Owl: Talon Dive / Night Eyes
    add(fam + 8, 3242, active(PHYSICAL, MELEE, 2, 10000), [strike(130)], "Talon Dive",
        "Strike with your talons for 130% weapon damage. Double damage while you are falling or jumping.")
    add(fam + 9, 25941, passive(SpellIconID=1583), [buff(A_STEALTH_DETECT, 30)], "Night Eyes",
        "You detect stealthed enemies from further away.")
    # Crocolisk: Death Roll / River Ambusher
    add(fam + 10, 15652, active(PHYSICAL, MELEE, 2, 20000, duration=39), [strike(100), debuff(A_STUN)], "Death Roll",
        "Seize and roll the target: 100% weapon damage and a 2 sec stun. 50% more damage while you are in water.",
        "Stunned.")
    add(fam + 11, 25941, passive(SpellIconID=1581), [buff(A_SWIM_SPEED, 50), buff(A_WATER_BREATHING)],
        "River Ambusher", "Swim speed increased by $s1%. You breathe underwater.")
    # Hyena: Cackle / Scavenger
    add(fam + 12, 5246, active(SHADOW, MAGIC, 1, 30000, duration=27),
        [{"effect": E_AURA, "aura": A_FEAR, "target": T_SRC_CASTER, "targetB": T_AREA_ENEMY, "radius": 13}],
        "Cackle", "A maddening cackle: enemies within 10 yards that are below 30% health flee in terror for 3 sec.",
        "Fleeing.")
    add(fam + 13, 25941, passive(SpellIconID=1565), [buff(A_DUMMY)], "Scavenger",
        "Consuming a corpse also restores 20% of your health.")
    # Wind Serpent: Storm Breath / Coil
    add(fam + 14, 20543, active(NATURE, MAGIC, 4, 10000), [bolt(15, 4, chain=2)], "Storm Breath",
        "Breathes lightning for $s1 Nature damage that arcs to a second enemy.")
    add(fam + 15, 25941, passive(SpellIconID=1589), [buff(A_DMG_TAKEN_PCT, -5, 127)], "Coil",
        "Damage taken reduced by 5%.")
    # Bear: Rearing Maul / Thick Hide
    add(fam + 16, 15793, active(PHYSICAL, MELEE, 2, 12000),
        [strike(150), {"effect": E_KNOCKBACK, "amount": 40, "misc": 100, "target": T_ENEMY}], "Rearing Maul",
        "Rear up and crash down for 150% weapon damage, knocking the target back.")
    add(fam + 17, 25941, passive(SpellIconID=1559), [buff(A_HEALTH_PCT, 10)], "Thick Hide",
        "Maximum health increased by $s1%.")
    # Boar: Gore Charge / Stubborn to the End
    add(fam + 18, 100, active(PHYSICAL, MELEE, 34, 15000, duration=36),
        [copy_effect(100, 1), strike(80), debuff(A_STUN)], "Gore Charge",
        "Charge the target, goring it for 80% weapon damage and knocking it down for 1 sec.", "Knocked down.")
    add(fam + 19, 25941, passive(SpellIconID=1578), [buff(A_PERIODIC_DUMMY, period=1000)], "Stubborn to the End",
        "While below 25% health you deal 20% more damage.")
    # Spider: Web Spit / Venom Glands
    add(fam + 20, 745, active(NATURE, MAGIC, 34, 20000, duration=35), [debuff(A_ROOT, mechanic=MECHANIC_ROOT)],
        "Web Spit", "Spits a web that roots the target in place for 4 sec.", "Rooted.")
    add(fam + 21, 25941, passive(SpellIconID=1586, ProcTypeMask=PROC_DONE_MELEE, ProcChance=10),
        [buff(A_PROC_TRIGGER, trigger=VENOM_GLANDS_POISON)], "Venom Glands",
        "Your melee attacks have a 10% chance to poison the target.")
    # Bat: Blood Drain / Echolocation
    add(fam + 22, 689, active(SHADOW, MAGIC, 2, 15000, duration=27, AttributesEx=0x4, ChannelInterruptFlags=15374),
        [debuff(A_PERIODIC_LEECH, 8, period=1000, ppl=1.5)], "Blood Drain",
        "Drain the target's blood for 3 sec, stealing $s1 health every second.", "Drained.")
    add(fam + 23, 25941, passive(SpellIconID=1577), [buff(A_STEALTH_DETECT, 20)], "Echolocation",
        "You sense stealthed enemies around you.")
    # Scorpid: Paralytic Sting / Chitin
    add(fam + 24, 5416, active(NATURE, MELEE, 2, 20000, duration=27),
        [debuff(A_PERIODIC_DAMAGE, 5, period=1000, ppl=1.0), debuff(A_DUMMY)], "Paralytic Sting",
        "Poison the target for $s1 Nature damage per second. When it runs its 3 sec, the target is paralyzed for 2 sec.",
        "Paralytic poison.")
    add(fam + 25, 25941, passive(SpellIconID=1585), [buff(A_RESISTANCE, 20, NATURE, ppl=2)], "Chitin",
        "Nature resistance increased by $s1.")
    # Raptor: Savage Rip / Killing Rhythm
    add(fam + 26, 13443, active(PHYSICAL, MELEE, 2, 6000, duration=31, CumulativeAura=3),
        [strike(60), debuff(A_PERIODIC_DAMAGE, 4, period=2000, ppl=1.0, mechanic=MECHANIC_BLEED)], "Savage Rip",
        "Rip the target for 60% weapon damage and make it bleed for 8 sec. Stacks up to 3 times.", "Bleeding.")
    add(fam + 27, 25941, passive(SpellIconID=1584, ProcTypeMask=PROC_DONE_MELEE, ProcChance=100),
        [buff(A_PROC_TRIGGER, trigger=KILLING_RHYTHM_BUFF)], "Killing Rhythm",
        "Your critical strikes increase your attack speed by 10% for 5 sec.")
    # Carrion Bird: Pick the Bones / Glide
    add(fam + 28, 3242, active(PHYSICAL, MELEE, 2, 12000), [strike(110)], "Pick the Bones",
        "Tear at the target for 110% weapon damage. Against targets below 35% health it deals 50% more and heals you for half the damage.")
    add(fam + 29, 25941, passive(SpellIconID=1579), [buff(A_FEATHER_FALL)], "Glide", "You fall slowly.")
    # Ravager: Frenzied Slash / Bloodlust
    add(fam + 30, 20605, active(PHYSICAL, MELEE, 2, 10000), [strike(55), strike(55), strike(55)], "Frenzied Slash",
        "Three frenzied slashes, each for 55% weapon damage.")
    add(fam + 31, 25941, passive(SpellIconID=2538, ProcTypeMask=PROC_KILL, ProcChance=100),
        [buff(A_PROC_TRIGGER, trigger=BLOODLUST_STACK)], "Bloodlust",
        "Each kill increases your damage by 5% for 10 sec, stacking up to 3 times.")
    # Dragonhawk: Fire Breath / Hot-Blooded
    add(fam + 32, 9573, active(FIRE, MAGIC, 1, 12000, duration=35),
        [{"effect": E_SCHOOL_DAMAGE, "amount": 12, "ppl": 3, "target": T_CONE, "radius": 14},
         {"effect": E_AURA, "aura": A_PERIODIC_DAMAGE, "amount": 3, "ppl": 0.6, "period": 1000,
          "target": T_CONE, "radius": 14}], "Fire Breath",
        "Breathes fire in a cone for $s1 Fire damage, burning the victims for $s2 more every second for 4 sec.",
        "Burning.")
    add(fam + 33, 25941, passive(SpellIconID=2328), [buff(A_RESISTANCE, 20, FIRE, ppl=2)], "Hot-Blooded",
        "Fire resistance increased by $s1.")
    # Moth: Wing Dust / Drawn to Light
    add(fam + 34, 29117, active(NATURE, MAGIC, 1, 30000, duration=27),
        [{"effect": E_AURA, "aura": A_CONFUSE, "target": T_CONE, "radius": 14}], "Wing Dust",
        "Beat your wings in the enemies' faces, disorienting everything in front of you for 3 sec.", "Disoriented.")
    add(fam + 35, 25941, passive(SpellIconID=3278), [buff(A_HEALING_PCT, 5)], "Drawn to Light",
        "Healing received increased by $s1%.")

    # --- The three shapes of the first Devourer: stances, Sethrak feats, Echo ----------------------
    # A worn body moves like a cat (Energy, combo points, the feral cat abilities) or a bear (Rage, the
    # feral bear abilities). The stance rides under the Take Form transform, so the body keeps its look.
    add(STANCE_PREDATOR, 768, passive(SpellIconID=template_row(768)[COL["SpellIconID"]]),
        [buff(A_SHAPESHIFT, 0, FORM_CAT)], "Predator's Poise",
        "Your body moves like a hunting cat: you fight with Energy and combo points and can use the feral cat abilities.",
        "Moving like a predator: Energy, combo points, feral cat abilities.")
    add(STANCE_HULK, 5487, passive(SpellIconID=template_row(5487)[COL["SpellIconID"]]),
        [buff(A_SHAPESHIFT, 0, FORM_BEAR)], "Hulking Mass",
        "Your body fights like a bear: you use Rage and can use the feral bear abilities.",
        "Hulking: Rage, feral bear abilities.")
    # Sethrak: Constricting Coils / Shed Skin / Scaled Ward
    add(9100290, 6730, active(PHYSICAL, MELEE, 2, 12000, duration=35),
        [strike(120), debuff(A_ROOT, mechanic=MECHANIC_ROOT)], "Constricting Coils",
        "Wrap the target in your coils for 120% weapon damage and hold it in place for 4 sec.", "Constricted.")
    add(9100291, 25941, active(NATURE, 0, 1, 45000, duration=31),
        [{"effect": E_HEAL_PCT, "amount": 15, "target": T_CASTER},
         {"effect": E_DISPEL_MECHANIC, "misc": MECHANIC_SNARE, "target": T_CASTER},
         buff(A_DMG_TAKEN_PCT, -10, 127)], "Shed Skin",
        "Shed your skin: heal 15% of your health, slough off slowing effects and take 10% less damage for 8 sec.",
        "Damage taken reduced by 10%.")
    add(9100292, 25941, passive(SpellIconID=1708),
        [buff(A_ARMOR_PCT, 20, PHYSICAL), buff(A_HEALTH_PCT, 5)], "Scaled Ward",
        "Armor increased by $s1%. Maximum health increased by $s2%.")
    # Moth: Moonlight Lance / Moonfall / Moonborn -- lunar magic
    add(9100295, 8921, active(ARCANE, MAGIC, 4, 6000),
        [bolt(20, 5)], "Moonlight Lance",
        "A lance of moonlight strikes the target for $s1 Arcane damage.")
    add(9100296, 48505, active(ARCANE, MAGIC, 1, 15000, duration=35),
        [{"effect": E_SCHOOL_DAMAGE, "amount": 15, "ppl": 4, "target": T_SRC_CASTER,
          "targetB": T_AREA_ENEMY, "radius": 13},
         {"effect": E_AURA, "aura": A_SLOW, "amount": -30, "target": T_SRC_CASTER,
          "targetB": T_AREA_ENEMY, "radius": 13}], "Moonfall",
        "Moonlight crashes down around you, dealing $s1 Arcane damage to enemies within 10 yards and slowing them by 30% for 4 sec.",
        "Slowed by moonlight.")
    add(9100297, 25941, passive(SchoolMask=ARCANE, SpellIconID=template_row(8921)[COL["SpellIconID"]]),
        [buff(A_DMG_DONE_PCT, 10, ARCANE), buff(A_DODGE, 5), buff(A_FEATHER_FALL)], "Moonborn",
        "Arcane damage increased by $s1%. Dodge increased by $s2%. You drift down gently when falling.")

    # --- Every beast family as a form: the second feat of the 16 older families ----------------------
    def area(spec):
        return {**spec, "target": T_SRC_CASTER, "targetB": T_AREA_ENEMY, "radius": 13}

    add(9100300, 24604, active(PHYSICAL, 0, 1, 40000, duration=1),
        [{"effect": E_AURA, "aura": A_ATTACK_POWER, "amount": 20, "ppl": 3, "target": T_CASTER_AREA_PARTY, "radius": 13}],
        "Furious Howl", "A howl that drives you and your group on: attack power increased by $s1 for 10 sec.",
        "Attack power increased by $s1.")
    add(9100301, 1822, active(PHYSICAL, MELEE, 2, 8000, duration=1),
        [strike(80), debuff(A_PERIODIC_DAMAGE, 5, period=2000, ppl=1.0, mechanic=MECHANIC_BLEED)], "Raking Claws",
        "Rake the target for 80% weapon damage and make it bleed for $s2 every 2 sec for 10 sec.", "Bleeding.")
    add(9100302, 50245, active(PHYSICAL, MELEE, 2, 30000, duration=35),
        [debuff(A_ROOT, mechanic=MECHANIC_ROOT), debuff(A_PERIODIC_DAMAGE, 4, period=1000, ppl=0.8)], "Pin",
        "Pin the target under your claws: it cannot move and takes $s2 damage every second for 4 sec.", "Pinned.")
    add(9100303, 50285, active(NATURE, MAGIC, 1, 30000, duration=31),
        [area(debuff(A_HIT_CHANCE, -20))], "Dust Cloud",
        "Kick up a cloud of dust: enemies within 10 yards have a 20% lower chance to hit for 8 sec.", "Chance to hit reduced by 20%.")
    add(9100304, 50541, active(PHYSICAL, MELEE, 2, 30000, duration=35),
        [bolt(8, 2), debuff(A_DISARM)], "Snatch",
        "Snatch at the target's weapon with your talons: $s1 damage and disarmed for 4 sec.", "Disarmed.")
    add(9100305, 50433, active(PHYSICAL, 0, 1, 45000, duration=1),
        [buff(A_DAMAGE_SHIELD, 8, ppl=1.5), buff(A_DMG_TAKEN_PCT, -10, 127)], "Bad Attitude",
        "For 10 sec, melee attackers take $s1 damage and you take 10% less damage.", "Snapping at attackers.")
    add(9100306, 50271, active(PHYSICAL, MELEE, 2, 12000, duration=32),
        [strike(100), debuff(A_SLOW, -50)], "Tendon Rip",
        "Rip the target's tendons for 100% weapon damage, slowing it by 50% for 6 sec.", "Movement slowed by 50%.")
    add(9100307, 26094, active(NATURE, MAGIC, 1, 20000),
        [area(bolt(12, 3)), area({"effect": E_KNOCKBACK, "amount": 60, "misc": 100})], "Crackling Gust",
        "Beat the air into a storm: $s1 Nature damage to enemies within 10 yards, hurling them back.")
    add(9100308, 5229, active(PHYSICAL, 0, 1, 60000, duration=31),
        [{"effect": E_HEAL_PCT, "amount": 10, "target": T_CASTER}, buff(A_DMG_TAKEN_PCT, -25, 127)], "Enduring Roar",
        "Roar defiance: heal 10% of your health and take 25% less damage for 8 sec.", "Damage taken reduced by 25%.")
    add(9100309, 35290, active(PHYSICAL, MELEE, 2, 10000, duration=31),
        [strike(120), debuff(A_PERIODIC_DAMAGE, 4, period=2000, ppl=1.0, mechanic=MECHANIC_BLEED)], "Gore",
        "Gore the target with your tusks for 120% weapon damage; it bleeds $s2 every 2 sec for 8 sec.", "Gored.")
    add(9100310, 744, active(NATURE, MAGIC, 2, 10000, duration=1),
        [bolt(8, 2), debuff(A_PERIODIC_DAMAGE, 3, period=2000, ppl=0.8)], "Venom Bite",
        "A venomous bite: $s1 Nature damage, then $s2 more every 2 sec for 10 sec.", "Envenomed.")
    add(9100311, 50519, active(NATURE, MAGIC, 3, 40000, duration=39),
        [bolt(8, 2), debuff(A_STUN)], "Sonic Blast",
        "A piercing shriek: $s1 Nature damage and the target is stunned for 2 sec.", "Stunned.")
    add(9100312, 56626, active(PHYSICAL, MELEE, 2, 12000, duration=1),
        [strike(120), debuff(A_RESISTANCE_PCT, -10, PHYSICAL)], "Crushing Pincers",
        "Crush the target for 120% weapon damage and crack its armor by 10% for 10 sec.", "Armor reduced by 10%.")
    add(9100313, 24423, active(PHYSICAL, 0, 1, 20000, duration=1),
        [area(bolt(5, 1.5)), area(debuff(A_DMG_DONE_PCT, -15, 127))], "Demoralizing Screech",
        "A carrion shriek: $s1 damage to enemies within 10 yards, and they deal 15% less damage for 10 sec.",
        "Damage dealt reduced by 15%.")
    add(9100314, 50518, active(PHYSICAL, MELEE, 2, 30000, duration=39),
        [strike(100), debuff(A_STUN)], "Ravage",
        "Ravage the target for 100% weapon damage and stun it for 2 sec.", "Stunned.")
    add(9100315, 34889, active(FIRE, MAGIC, 4, 8000, duration=32),
        [bolt(20, 5), debuff(A_PERIODIC_DAMAGE, 3, period=2000, ppl=0.8)], "Searing Bolt",
        "Spit a bolt of dragonfire for $s1 Fire damage; the target burns for $s2 every 2 sec for 6 sec.", "Burning.")

    # --- The six families that had nothing yet: Feat I, Feat II, Instinct ---------------------------
    # Gorilla
    add(9100320, 26090, active(PHYSICAL, MELEE, 2, 20000),
        [strike(60), {"effect": E_INTERRUPT, "target": T_ENEMY}], "Pummel",
        "Pummel the target for 60% weapon damage and interrupt its spellcasting.")
    add(9100321, 26094, active(NATURE, MAGIC, 1, 12000),
        [area(bolt(15, 3.5))], "Thunderstomp", "Stomp the ground: $s1 Nature damage to enemies within 10 yards.")
    add(9100322, 25941, passive(SpellIconID=1582),
        [buff(A_HEALTH_PCT, 8), buff(A_ARMOR_PCT, 10, PHYSICAL)], "Silverback",
        "Maximum health increased by $s1%. Armor increased by $s2%.")
    # Turtle
    add(9100323, 26064, active(PHYSICAL, 0, 1, 60000, duration=29),
        [buff(A_DMG_TAKEN_PCT, -40, 127)], "Shell Shield",
        "Withdraw into your shell: damage taken reduced by 40% for 12 sec.", "Damage taken reduced by 40%.")
    add(9100324, 17253, active(PHYSICAL, MELEE, 2, 10000, duration=35),
        [strike(130), debuff(A_SLOW, -30)], "Snapping Bite",
        "A crushing bite for 130% weapon damage that slows the target by 30% for 4 sec.", "Movement slowed by 30%.")
    add(9100325, 25941, passive(SpellIconID=1588),
        [buff(A_ARMOR_PCT, 20, PHYSICAL), buff(A_SWIM_SPEED, 40), buff(A_WATER_BREATHING)], "Ancient Shell",
        "Armor increased by $s1%. Swim speed increased by $s2%. You breathe underwater.")
    # Serpent
    add(9100326, 35387, active(NATURE, MAGIC, 4, 10000, duration=31),
        [debuff(A_PERIODIC_DAMAGE, 6, period=2000, ppl=1.2)], "Poison Spit",
        "Spit venom at a target up to 30 yards away: $s1 Nature damage every 2 sec for 8 sec.", "Poisoned.")
    add(9100327, 100, active(PHYSICAL, MELEE, 34, 15000),
        [copy_effect(100, 1), strike(90)], "Venomous Lunge",
        "Lunge at a target up to 25 yards away and strike it for 90% weapon damage.")
    add(9100328, 25941, passive(SpellIconID=68),
        [buff(A_DODGE, 5), buff(A_RESISTANCE, 15, NATURE, ppl=2)], "Sinuous",
        "Dodge increased by $s1%. Nature resistance increased by $s2.")
    # Wasp
    add(9100329, 56626, active(NATURE, MAGIC, 2, 6000, duration=8),
        [bolt(6, 1.5), debuff(A_RESISTANCE_PCT, -5, PHYSICAL)], "Barbed Sting",
        "Sting the target for $s1 Nature damage; the barb weakens its armor by 5% for 15 sec.", "Armor reduced by 5%.")
    add(9100330, 53401, active(PHYSICAL, 0, 1, 45000, duration=31),
        [buff(A_MELEE_HASTE, 30)], "Swarming Frenzy",
        "Attack speed increased by 30% for 8 sec.", "Attack speed increased by 30%.")
    add(9100331, 25941, passive(SpellIconID=110),
        [buff(A_SPEED, 8), buff(A_FEATHER_FALL)], "Buzzing Wings",
        "Movement speed increased by $s1%. You fall slowly.")
    # Sporebat
    add(9100332, 50274, active(NATURE, MAGIC, 1, 20000, duration=31),
        [area(debuff(A_PERIODIC_DAMAGE, 4, period=2000, ppl=0.8))], "Spore Cloud",
        "Release a cloud of spores: enemies within 10 yards take $s1 Nature damage every 2 sec for 8 sec.", "Choking on spores.")
    add(9100333, 55749, active(NATURE, MAGIC, 4, 6000),
        [bolt(18, 4.5)], "Spore Bolt", "Hurl a burst of spores for $s1 Nature damage.")
    add(9100334, 25941, passive(SchoolMask=NATURE, SpellIconID=2681),
        [buff(A_DMG_DONE_PCT, 10, NATURE), buff(A_HEALING_PCT, 5)], "Fungal Bloom",
        "Nature damage increased by $s1%. Healing received increased by $s2%.")
    # Nether Ray
    add(9100335, 50479, active(ARCANE, MAGIC, 3, 20000),
        [bolt(12, 3), {"effect": E_INTERRUPT, "target": T_ENEMY}], "Nether Shock",
        "A jolt of nether energy: $s1 Arcane damage and the target's spellcasting is interrupted.")
    add(9100336, 1449, active(ARCANE, MAGIC, 1, 12000),
        [area(bolt(12, 3))], "Nether Pulse", "A pulse of nether energy: $s1 Arcane damage to enemies within 10 yards.")
    add(9100337, 25941, passive(SchoolMask=ARCANE, SpellIconID=2027),
        [buff(A_DMG_DONE_PCT, 10, ARCANE), buff(A_FEATHER_FALL)], "Void Glide",
        "Arcane damage increased by $s1%. You glide down gently when falling.")

    # --- The fey moth line: Moth -> Ardenmoth -> Fey Moth -> Moon Empress ------------------------------
    add(9100340, 770, active(NATURE, MAGIC, 4, 30000, duration=32, AuraInterruptFlags=AURA_INTERRUPT_DAMAGE),
        [debuff(A_STUN, mechanic=MECHANIC_SLEEP)], "Faerie Dust",
        "Sprinkle faerie dust on a target up to 30 yards away: it falls asleep for 6 sec. Any damage wakes it.",
        "Asleep.")
    add(9100341, 1953, active(ARCANE, 0, 1, 15000, duration=27),
        [copy_effect(1953, 1), buff(A_DODGE, 30)], "Fey Blink",
        "Blink forward in a shimmer of fey light and gain 30% dodge for 3 sec.", "Shimmering: +30% dodge.")
    add(9100342, 48505, active(ARCANE, MAGIC, 1, 15000, duration=35),
        [area(bolt(25, 6)), area(debuff(A_SLOW, -40))], "Greater Moonfall",
        "Moonlight crashes down around you: $s1 Arcane damage to enemies within 10 yards, slowing them by 40% for 4 sec.",
        "Slowed by moonlight.")
    add(9100343, 48505, active(ARCANE, MAGIC, 1, 60000, duration=28),
        [buff(A_PERIODIC_TRIGGER, period=1000, trigger=9100344)], "Starfall",
        "Call down falling stars for 5 sec: every second, enemies within 10 yards take Arcane damage.", "Calling the stars.")
    add(9100344, 50288, active(ARCANE, MAGIC, 1, 0),
        [area(bolt(10, 2.5))], "Starfall", "")
    add(9100345, 25941, passive(SchoolMask=ARCANE, SpellIconID=template_row(8921)[COL["SpellIconID"]]),
        [buff(A_DMG_DONE_PCT, 15, ARCANE), buff(A_DODGE, 8), buff(A_FEATHER_FALL)], "Fey-Touched",
        "Arcane damage increased by $s1%. Dodge increased by $s2%. You drift down gently when falling.")

    # --- The model pack's mounts (devourer_models.MOUNTS), taught by Valla in Stormwind and Orgrimmar ---
    import devourer_models as models
    icons = {"dh": 61996, "raven": 41252, "kakapo": 41252}
    for i, (name, model, _scale, _tex, flying) in enumerate(models.MOUNTS):
        template = 59568 if flying else 41252            # Blue Drake (280% flying) / Raven Lord (ground)
        effs = [copy_effect(template, n) if template_row(template)[COL[f"Effect_{n}"]] else None for n in (1, 2, 3)]
        effs[0]["raw"]["EffectMiscValue"] = models.MOUNT_CREATURE_BASE + i
        icon_from = icons["dh"] if model.startswith("dh") else icons["raven"] if model.startswith("raven") \
            else icons["kakapo"] if model == "kakapo" else template
        add(models.MOUNT_SPELL_BASE + i, template,
            {"SpellIconID": template_row(icon_from)[COL["SpellIconID"]]}, effs, name,
            ("Summons and dismisses a rideable " + name + ". This is a very fast mount that can fly."
             if flying else "Summons and dismisses a rideable " + name + ". This is a very fast mount."),
            "Riding a " + name + ".")

    # Echo: a spectral copy of the body you wear fights beside you.
    add(ECHO, 51533, active(NATURE, 0, 1, 120000, StartRecoveryCategory=133, StartRecoveryTime=1500),
        [{"effect": E_DUMMY, "target": T_CASTER}], "Echo of the Hunt",
        "Call an echo of the body you are wearing (or of your chosen body) to fight at your side for 30 sec.")

    # --- helpers the feats and Instincts trigger ---------------------------------------------------
    add(RUN_DOWN_CHASE, 5118, active(PHYSICAL, 0, 1, 0, duration=27), [buff(A_SPEED, 30)], "Run Down",
        "", "On the chase: 30% faster.")
    add(VENOM_GLANDS_POISON, 744, active(NATURE, MAGIC, 2, 0, duration=29),
        [debuff(A_PERIODIC_DAMAGE, 3, period=3000, ppl=0.7)], "Venom Glands", "", "Poisoned.")
    add(PARALYZED, 5416, active(NATURE, MAGIC, 13, 0, duration=39), [debuff(A_STUN)], "Paralyzed", "", "Paralyzed.")
    add(BLOODLUST_STACK, 3019, active(PHYSICAL, 0, 1, 0, duration=1, CumulativeAura=3),
        [buff(A_DMG_DONE_PCT, 5, 127)], "Bloodlust", "", "Damage increased by 5% per stack.")
    add(STUBBORN_BUFF, 3019, active(PHYSICAL, 0, 1, 0, duration=39), [buff(A_DMG_DONE_PCT, 20, 127)],
        "Stubborn to the End", "", "Damage increased by 20%.")
    add(KILLING_RHYTHM_BUFF, 3019, active(PHYSICAL, 0, 1, 0, duration=28), [buff(A_MELEE_HASTE, 10)],
        "Killing Rhythm", "", "Attack speed increased by 10%.")
    return defs


# Beast families -> (feat, instinct). The C++ side reads the same pairs from `devourer_family_feat`.
FAMILIES = {1: 0, 2: 1, 8: 2, 12: 3, 26: 4, 6: 5, 25: 6, 27: 7, 4: 8, 5: 9, 3: 10, 24: 11, 20: 12,
            11: 13, 7: 14, 31: 15, 30: 16, 37: 17}
