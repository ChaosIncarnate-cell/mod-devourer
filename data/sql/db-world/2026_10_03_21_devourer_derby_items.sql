-- mod-devourer task 020: the witch race rewards (Items and balance thread, owner's OK 2026-10-03).
-- Ids: item_template 9104000-9104004, spell_dbc / skilllineability_dbc 9104050. Safe to run again.
-- Each item is a copy of a Blizzard item of the same slot and level, then changed. All use stock displays.
--   9104000 Wren's Racing Goggles    race 1  cloth head, ilvl 25, req 20: 32 armor, +6 Int +5 Sta (cf. Shadow Goggles)
--   9104001 Hagatha's Bristle Cloak  race 2  back, ilvl 25, req 20: 19 armor, +4 Agi +2 Sta (cf. Heavy Runed Cloak)
--   9104002 Bramble's Lucky Beetle   race 3  neck, ilvl 25, req 20: +4 Str +2 Sta (cf. Brilliant Necklace)
--   9104003 Hagatha's Sour Toffee    race 2  x3, Tricky Treat's effect (+4% speed 30 s, 1 in 5 Upset Tummy), spoils in a day
--   9104004 Reins of Hagatha's Kakapo race 3 level-20 ground mount, 60% (spell 9104050 on creature 9301049, display 980033)
-- Client: patch-Z needs Item.dbc rows for 9104000-9104004 and Spell.dbc + SkillLineAbility.dbc rows for 9104050.

DELETE FROM `item_template` WHERE `entry` BETWEEN 9104000 AND 9104004;
DROP TEMPORARY TABLE IF EXISTS `derby_tmp_item`;

CREATE TEMPORARY TABLE `derby_tmp_item` SELECT * FROM `item_template` WHERE `entry` = 4368;   -- Flying Tiger Goggles
UPDATE `derby_tmp_item` SET `entry` = 9104000, `name` = 'Wren''s Racing Goggles', `Quality` = 2, `ItemLevel` = 25,
    `RequiredLevel` = 20, `RequiredSkill` = 0, `RequiredSkillRank` = 0, `BagFamily` = 0, `bonding` = 1, `armor` = 32,
    `stat_type1` = 5, `stat_value1` = 6, `stat_type2` = 7, `stat_value2` = 5, `MaxDurability` = 40,
    `BuyPrice` = 4300, `SellPrice` = 860, `RequiredDisenchantSkill` = 25, `DisenchantID` = 3,
    `description` = 'Wren says they make you faster. They do not.', `VerifiedBuild` = 0;
INSERT INTO `item_template` SELECT * FROM `derby_tmp_item`;
DROP TEMPORARY TABLE `derby_tmp_item`;

CREATE TEMPORARY TABLE `derby_tmp_item` SELECT * FROM `item_template` WHERE `entry` = 3018;   -- Hide of Lupos
UPDATE `derby_tmp_item` SET `entry` = 9104001, `name` = 'Hagatha''s Bristle Cloak', `Quality` = 2, `ItemLevel` = 25,
    `RequiredLevel` = 20, `bonding` = 1, `armor` = 19, `stat_type1` = 3, `stat_value1` = 4, `stat_type2` = 7,
    `stat_value2` = 2, `BuyPrice` = 4100, `SellPrice` = 820, `RequiredDisenchantSkill` = 25, `DisenchantID` = 3,
    `description` = 'Smells faintly of swamp and old broom.', `VerifiedBuild` = 0;
INSERT INTO `item_template` SELECT * FROM `derby_tmp_item`;
DROP TEMPORARY TABLE `derby_tmp_item`;

CREATE TEMPORARY TABLE `derby_tmp_item` SELECT * FROM `item_template` WHERE `entry` = 30419;  -- Brilliant Necklace
UPDATE `derby_tmp_item` SET `entry` = 9104002, `name` = 'Bramble''s Lucky Beetle', `displayid` = 34156, `Quality` = 2,
    `ItemLevel` = 25, `RequiredLevel` = 20, `bonding` = 1, `stat_type1` = 4, `stat_value1` = 4, `stat_type2` = 7,
    `stat_value2` = 2, `stat_type3` = 0, `stat_value3` = 0, `stat_type4` = 0, `stat_value4` = 0, `stat_type5` = 0,
    `stat_value5` = 0, `BuyPrice` = 4000, `SellPrice` = 800,
    `description` = 'It might still be alive.', `VerifiedBuild` = 0;
INSERT INTO `item_template` SELECT * FROM `derby_tmp_item`;
DROP TEMPORARY TABLE `derby_tmp_item`;

CREATE TEMPORARY TABLE `derby_tmp_item` SELECT * FROM `item_template` WHERE `entry` = 33226;  -- Tricky Treat
UPDATE `derby_tmp_item` SET `entry` = 9104003, `name` = 'Hagatha''s Sour Toffee', `displayid` = 16837, `Quality` = 1,
    `ItemLevel` = 20, `Flags` = 0, `maxcount` = 0, `stackable` = 20, `BuyPrice` = 100, `SellPrice` = 25,
    `duration` = 86400, `flagsCustom` = 1,
    `description` = 'Hagatha''s own recipe. Wren will not touch it.', `VerifiedBuild` = 0;
INSERT INTO `item_template` SELECT * FROM `derby_tmp_item`;
DROP TEMPORARY TABLE `derby_tmp_item`;

CREATE TEMPORARY TABLE `derby_tmp_item` SELECT * FROM `item_template` WHERE `entry` = 5656;   -- Brown Horse Bridle
UPDATE `derby_tmp_item` SET `entry` = 9104004, `name` = 'Reins of Hagatha''s Kakapo', `displayid` = 17608,
    `AllowableRace` = -1, `AllowableClass` = -1, `spellid_2` = 9104050, `maxcount` = 1, `BuyPrice` = 0, `SellPrice` = 0,
    `description` = 'Hagatha swears she won it fair. Bramble swears she didn''t.', `VerifiedBuild` = 0;
INSERT INTO `item_template` SELECT * FROM `derby_tmp_item`;
DROP TEMPORARY TABLE `derby_tmp_item`;

-- The Kakapo at apprentice speed: Wren's Kakapo spell 9301149 with 60% instead of 100%.
DELETE FROM `spell_dbc` WHERE `ID` = 9104050;
INSERT INTO `spell_dbc` (`ID`,`Category`,`DispelType`,`Mechanic`,`Attributes`,`AttributesEx`,`AttributesEx2`,`AttributesEx3`,`AttributesEx4`,`AttributesEx5`,`AttributesEx6`,`AttributesEx7`,`ShapeshiftMask`,`unk_320_2`,`ShapeshiftExclude`,`unk_320_3`,`Targets`,`TargetCreatureType`,`RequiresSpellFocus`,`FacingCasterFlags`,`CasterAuraState`,`TargetAuraState`,`ExcludeCasterAuraState`,`ExcludeTargetAuraState`,`CasterAuraSpell`,`TargetAuraSpell`,`ExcludeCasterAuraSpell`,`ExcludeTargetAuraSpell`,`CastingTimeIndex`,`RecoveryTime`,`CategoryRecoveryTime`,`InterruptFlags`,`AuraInterruptFlags`,`ChannelInterruptFlags`,`ProcTypeMask`,`ProcChance`,`ProcCharges`,`MaxLevel`,`BaseLevel`,`SpellLevel`,`DurationIndex`,`PowerType`,`ManaCost`,`ManaCostPerLevel`,`ManaPerSecond`,`ManaPerSecondPerLevel`,`RangeIndex`,`Speed`,`ModalNextSpell`,`CumulativeAura`,`Totem_1`,`Totem_2`,`Reagent_1`,`Reagent_2`,`Reagent_3`,`Reagent_4`,`Reagent_5`,`Reagent_6`,`Reagent_7`,`Reagent_8`,`ReagentCount_1`,`ReagentCount_2`,`ReagentCount_3`,`ReagentCount_4`,`ReagentCount_5`,`ReagentCount_6`,`ReagentCount_7`,`ReagentCount_8`,`EquippedItemClass`,`EquippedItemSubclass`,`EquippedItemInvTypes`,`Effect_1`,`Effect_2`,`Effect_3`,`EffectDieSides_1`,`EffectDieSides_2`,`EffectDieSides_3`,`EffectRealPointsPerLevel_1`,`EffectRealPointsPerLevel_2`,`EffectRealPointsPerLevel_3`,`EffectBasePoints_1`,`EffectBasePoints_2`,`EffectBasePoints_3`,`EffectMechanic_1`,`EffectMechanic_2`,`EffectMechanic_3`,`ImplicitTargetA_1`,`ImplicitTargetA_2`,`ImplicitTargetA_3`,`ImplicitTargetB_1`,`ImplicitTargetB_2`,`ImplicitTargetB_3`,`EffectRadiusIndex_1`,`EffectRadiusIndex_2`,`EffectRadiusIndex_3`,`EffectAura_1`,`EffectAura_2`,`EffectAura_3`,`EffectAuraPeriod_1`,`EffectAuraPeriod_2`,`EffectAuraPeriod_3`,`EffectMultipleValue_1`,`EffectMultipleValue_2`,`EffectMultipleValue_3`,`EffectChainTargets_1`,`EffectChainTargets_2`,`EffectChainTargets_3`,`EffectItemType_1`,`EffectItemType_2`,`EffectItemType_3`,`EffectMiscValue_1`,`EffectMiscValue_2`,`EffectMiscValue_3`,`EffectMiscValueB_1`,`EffectMiscValueB_2`,`EffectMiscValueB_3`,`EffectTriggerSpell_1`,`EffectTriggerSpell_2`,`EffectTriggerSpell_3`,`EffectPointsPerCombo_1`,`EffectPointsPerCombo_2`,`EffectPointsPerCombo_3`,`EffectSpellClassMaskA_1`,`EffectSpellClassMaskA_2`,`EffectSpellClassMaskA_3`,`EffectSpellClassMaskB_1`,`EffectSpellClassMaskB_2`,`EffectSpellClassMaskB_3`,`EffectSpellClassMaskC_1`,`EffectSpellClassMaskC_2`,`EffectSpellClassMaskC_3`,`SpellVisualID_1`,`SpellVisualID_2`,`SpellIconID`,`ActiveIconID`,`SpellPriority`,`Name_Lang_enUS`,`Name_Lang_enGB`,`Name_Lang_koKR`,`Name_Lang_frFR`,`Name_Lang_deDE`,`Name_Lang_enCN`,`Name_Lang_zhCN`,`Name_Lang_enTW`,`Name_Lang_zhTW`,`Name_Lang_esES`,`Name_Lang_esMX`,`Name_Lang_ruRU`,`Name_Lang_ptPT`,`Name_Lang_ptBR`,`Name_Lang_itIT`,`Name_Lang_Unk`,`Name_Lang_Mask`,`NameSubtext_Lang_enUS`,`NameSubtext_Lang_enGB`,`NameSubtext_Lang_koKR`,`NameSubtext_Lang_frFR`,`NameSubtext_Lang_deDE`,`NameSubtext_Lang_enCN`,`NameSubtext_Lang_zhCN`,`NameSubtext_Lang_enTW`,`NameSubtext_Lang_zhTW`,`NameSubtext_Lang_esES`,`NameSubtext_Lang_esMX`,`NameSubtext_Lang_ruRU`,`NameSubtext_Lang_ptPT`,`NameSubtext_Lang_ptBR`,`NameSubtext_Lang_itIT`,`NameSubtext_Lang_Unk`,`NameSubtext_Lang_Mask`,`Description_Lang_enUS`,`Description_Lang_enGB`,`Description_Lang_koKR`,`Description_Lang_frFR`,`Description_Lang_deDE`,`Description_Lang_enCN`,`Description_Lang_zhCN`,`Description_Lang_enTW`,`Description_Lang_zhTW`,`Description_Lang_esES`,`Description_Lang_esMX`,`Description_Lang_ruRU`,`Description_Lang_ptPT`,`Description_Lang_ptBR`,`Description_Lang_itIT`,`Description_Lang_Unk`,`Description_Lang_Mask`,`AuraDescription_Lang_enUS`,`AuraDescription_Lang_enGB`,`AuraDescription_Lang_koKR`,`AuraDescription_Lang_frFR`,`AuraDescription_Lang_deDE`,`AuraDescription_Lang_enCN`,`AuraDescription_Lang_zhCN`,`AuraDescription_Lang_enTW`,`AuraDescription_Lang_zhTW`,`AuraDescription_Lang_esES`,`AuraDescription_Lang_esMX`,`AuraDescription_Lang_ruRU`,`AuraDescription_Lang_ptPT`,`AuraDescription_Lang_ptBR`,`AuraDescription_Lang_itIT`,`AuraDescription_Lang_Unk`,`AuraDescription_Lang_Mask`,`ManaCostPct`,`StartRecoveryCategory`,`StartRecoveryTime`,`MaxTargetLevel`,`SpellClassSet`,`SpellClassMask_1`,`SpellClassMask_2`,`SpellClassMask_3`,`MaxTargets`,`DefenseType`,`PreventionType`,`StanceBarOrder`,`EffectChainAmplitude_1`,`EffectChainAmplitude_2`,`EffectChainAmplitude_3`,`MinFactionID`,`MinReputation`,`RequiredAuraVision`,`RequiredTotemCategoryID_1`,`RequiredTotemCategoryID_2`,`RequiredAreasID`,`SchoolMask`,`RuneCostID`,`SpellMissileID`,`PowerDisplayID`,`EffectBonusMultiplier_1`,`EffectBonusMultiplier_2`,`EffectBonusMultiplier_3`,`SpellDescriptionVariableID`,`SpellDifficultyID`) VALUES
(9104050,0,0,21,269844752,0,0,536870912,0,0,131072,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,0,0,31,0,0,0,101,0,0,0,1,21,0,0,0,0,0,1,0.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,6,6,0,0,1,0,0.0,0.0,0.0,0,59,0,0,0,0,1,1,0,0,0,0,0,0,0,78,32,0,0,0,0,0.0,0.0,0.0,0,0,0,0,0,0,9301049,0,0,0,0,0,0,0,0,0.0,0.0,0.0,0,0,0,0,0,0,0,0,0,1708,0,836,0,0,'Hagatha''s Kakapo','','','','','','','','','','','','','','','',16712190,'','','','','','','','','','','','','','','','',16712190,'Summons and dismisses a rideable Kakapo. This is a ground mount.','','','','','','','','','','','','','','','',16712190,'Increases speed by $s2%.','','','','','','','','','','','','','','','',16712190,0,330,0,0,0,0,0,0,0,0,0,0,1.0,1.0,1.0,0,0,0,0,0,0,1,0,0,0,0.0,0.0,0.0,0,0);
DELETE FROM `skilllineability_dbc` WHERE `ID` = 9104050;
INSERT INTO `skilllineability_dbc` (`ID`,`SkillLine`,`Spell`,`RaceMask`,`ClassMask`,`ExcludeRace`,`ExcludeClass`,`MinSkillLineRank`,`SupercededBySpell`,`AcquireMethod`,`TrivialSkillLineRankHigh`,`TrivialSkillLineRankLow`,`CharacterPoints_1`,`CharacterPoints_2`) VALUES
(9104050,777,9104050,0,0,0,0,1,0,0,0,0,0,0);
