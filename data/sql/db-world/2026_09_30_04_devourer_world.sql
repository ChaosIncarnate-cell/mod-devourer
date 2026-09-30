-- mod-devourer: the creatures that grant shapes, the summoned helpers, the colourings and growth. Safe to run again.
-- Ported from the CoA files (ChaosCore0.3). Ids: creatures 9101001-9101102, spawns 9910001-9910013.
-- Removed by data/sql/uninstall/world.sql.

-- --- the Sethrak camp in the southern Tanaris dunes (levels 44-46) -----------------------------------------
-- 9101001 Sandstalker / 9101002 Venomcaller, and one rarer Sethrak per colouring (9101003-9101007, 10 min respawn).
DELETE FROM `creature` WHERE `guid` BETWEEN 9910001 AND 9910020;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9101001 AND 9101009;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9101001 AND 9101009;
DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;
CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 5615;   -- Wastewander Rogue
UPDATE `devourer_tmp_ct` SET `entry` = 9101001, `name` = 'Sethrak Sandstalker', `subname` = NULL,
    `minlevel` = 44, `maxlevel` = 46, `AIName` = '', `ScriptName` = '', `KillCredit1` = 0, `KillCredit2` = 0,
    `pickpocketloot` = 0, `VerifiedBuild` = 0;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101002, `name` = 'Sethrak Venomcaller', `unit_class` = 2, `ManaModifier` = 1;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;

CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 9101001;
UPDATE `devourer_tmp_ct` SET `minlevel` = 45, `maxlevel` = 46, `HealthModifier` = `HealthModifier` * 1.5;
UPDATE `devourer_tmp_ct` SET `entry` = 9101003, `name` = 'Emberscale Sethrak';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101004, `name` = 'Viperfang Sethrak';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101005, `name` = 'Duskcoil Sethrak';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101006, `name` = 'Gilded Sethrak';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101007, `name` = 'Bloodscale Sethrak';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;

INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(9101001, 0, 80305, 1, 1, 0),
(9101002, 0, 80018, 1, 1, 0),
(9101003, 0, 991003, 1, 1, 0),
(9101004, 0, 991004, 1, 1, 0),
(9101005, 0, 991005, 1, 1, 0),
(9101006, 0, 991006, 1, 1, 0),
(9101007, 0, 991007, 1, 1, 0);

INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`) VALUES
(9910001, 9101001, 1, 1, 1, -7652.1, -3533.3, 22.6, 1.2, 300, 5, 1),
(9910002, 9101002, 1, 1, 1, -7575.8, -3205.5, 37.5, 2.1, 300, 5, 1),
(9910003, 9101001, 1, 1, 1, -7506.1, -3558.6, 11.2, 0.4, 300, 5, 1),
(9910004, 9101002, 1, 1, 1, -7384.2, -2887.3, 8.9, 3.3, 300, 5, 1),
(9910005, 9101001, 1, 1, 1, -7313.6, -3222.5, 9.5, 4.0, 300, 5, 1),
(9910006, 9101002, 1, 1, 1, -7202.6, -3407.1, 11.7, 5.1, 300, 5, 1),
(9910007, 9101001, 1, 1, 1, -7049.6, -3361.0, 9.3, 0.9, 300, 5, 1),
(9910008, 9101002, 1, 1, 1, -6893.4, -2958.4, 9.6, 2.7, 300, 5, 1),
(9910009, 9101003, 1, 1, 1, -7649.1, -3530.3, 22.6, 4.3, 600, 5, 1),
(9910010, 9101004, 1, 1, 1, -7503.1, -3555.6, 11.2, 3.5, 600, 5, 1),
(9910011, 9101005, 1, 1, 1, -7310.6, -3219.5, 9.5, 0.9, 600, 5, 1),
(9910012, 9101006, 1, 1, 1, -7046.6, -3358.0, 9.3, 4.0, 600, 5, 1),
(9910013, 9101007, 1, 1, 1, -6890.4, -2955.4, 9.6, 5.8, 600, 5, 1);

-- --- Voidstorm Berserkers 9101020-9101023 and Whelps 9101024-9101027: one per colouring. No world spawns yet
-- (rift events later); for testing: .npc add temp 9101020.
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9101020 AND 9101027;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9101020 AND 9101027;
CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 9101001;
UPDATE `devourer_tmp_ct` SET `subname` = 'Voidstorm', `type` = 1;
UPDATE `devourer_tmp_ct` SET `entry` = 9101020, `name` = 'Voidstorm Berserker';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101021, `name` = 'Azure Voidstorm Berserker';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101022, `name` = 'Crimson Voidstorm Berserker';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101023, `name` = 'Teal Voidstorm Berserker';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `minlevel` = 18, `maxlevel` = 20;
UPDATE `devourer_tmp_ct` SET `entry` = 9101024, `name` = 'Voidstorm Whelp';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101025, `name` = 'Azure Voidstorm Whelp';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101026, `name` = 'Crimson Voidstorm Whelp';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101027, `name` = 'Teal Voidstorm Whelp';
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(9101020, 0, 991015, 1, 1, 0),
(9101021, 0, 991014, 1, 1, 0),
(9101022, 0, 991016, 1, 1, 0),
(9101023, 0, 991017, 1, 1, 0),
(9101024, 0, 991063, 1, 1, 0),
(9101025, 0, 991062, 1, 1, 0),
(9101026, 0, 991064, 1, 1, 0),
(9101027, 0, 991065, 1, 1, 0);

-- --- what the specs summon ------------------------------------------------------------------------------------
--   9101100 Hatchling       Brood's Hatch Brood (guardian; the module gives it the worn shape's pet model and stats)
--   9101101 Echo            a Skinchanger's shape, left behind for a few seconds (guardian, translucent)
--   9101102 Rising Serpent  Vashnik: stationary serpents that repeat its spells (Twinfangs looks)
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9101100 AND 9101102;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9101100 AND 9101102;
CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 9101001;
UPDATE `devourer_tmp_ct` SET `name` = 'Hatchling', `subname` = NULL, `minlevel` = 1, `maxlevel` = 80, `faction` = 35,
    `npcflag` = 0, `unit_flags` = 0, `lootid` = 0, `skinloot` = 0, `pickpocketloot` = 0, `mingold` = 0, `maxgold` = 0,
    `ExperienceModifier` = 0, `KillCredit1` = 0, `KillCredit2` = 0, `AIName` = '', `ScriptName` = '', `flags_extra` = 0,
    `type` = 1, `family` = 0, `unit_class` = 1, `HealthModifier` = 1, `DamageModifier` = 1, `BaseAttackTime` = 2000,
    `MovementType` = 0, `entry` = 9101100;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101101, `name` = 'Echo', `type` = 6, `speed_run` = 1.3;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101102, `name` = 'Rising Serpent', `type` = 1, `speed_walk` = 0, `speed_run` = 0;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(9101100, 0, 4312, 1, 1, 0),                                  -- Deviate Viper (stock), until a shape dresses it
(9101101, 0, 200004, 1, 1, 0),
(9101102, 0, 991040, 1, 0.5, 0),                              -- Twinfangs, purple
(9101102, 1, 991045, 1, 0.5, 0);                              -- Twinfangs, pale teal

-- --- which creatures grant which shape and colouring ------------------------------------------------------------
DELETE FROM `devourer_shape_source`;
INSERT INTO `devourer_shape_source` (`creature_entry`, `shape_id`, `display_id`) VALUES
(9101001, 1, 991001), (9101002, 1, 991002), (9101003, 1, 991003), (9101004, 1, 991004),
(9101005, 1, 991005), (9101006, 1, 991006), (9101007, 1, 991007),
(9101020, 2, 991015), (9101021, 2, 991014), (9101022, 2, 991016), (9101023, 2, 991017),
(9101024, 4, 991063), (9101025, 4, 991062), (9101026, 4, 991064), (9101027, 4, 991065);

-- --- colourings (the names are what ".devour skin <name>" takes) -----------------------------------------------
DELETE FROM `devourer_skin`;
INSERT INTO `devourer_skin` (`display_id`, `shape_id`, `name`, `brood_display`) VALUES
(200004, 1, 'Black', 0), (991001, 1, 'Diamondback', 0), (991002, 1, 'Green', 0), (991003, 1, 'Ember', 0),
(991004, 1, 'Viper', 0), (991005, 1, 'Dusk', 0), (991006, 1, 'Gilded', 0), (991007, 1, 'Blood', 0),
(991015, 2, 'Orange', 991063), (991014, 2, 'Azure', 991062), (991016, 2, 'Crimson', 991064), (991017, 2, 'Teal', 991065),
(991029, 3, 'Vashnik', 0),
(991063, 4, 'OrangeWhelp', 991063), (991062, 4, 'AzureWhelp', 991062), (991064, 4, 'CrimsonWhelp', 991064),
(991065, 4, 'TealWhelp', 991065);

-- --- growth ------------------------------------------------------------------------------------------------------
-- Bio Points per meal while the form is worn, by the meal's creature type (0 = anything else). The meal's rarity
-- multiplies them: normal 1, elite 3, rare 5, rare elite 8, bosses 20.
-- Creature types: 1 Beast, 2 Dragonkin, 3 Demon, 4 Elemental, 5 Giant, 6 Undead, 7 Humanoid, 8 Critter, 9 Mechanical.
DELETE FROM `devourer_diet`;
INSERT INTO `devourer_diet` (`shape_id`, `creature_type`, `bp`) VALUES
(1, 7, 15), (1, 1, 10), (1, 2, 25), (1, 0, 3),               -- Sethrak: people and beasts of the sands, dragons best
(2, 3, 20), (2, 7, 10), (2, 1, 10), (2, 0, 5),               -- Berserker: demons most of all
(3, 7, 15), (3, 1, 10), (3, 2, 25), (3, 0, 3),               -- Vashnik
(4, 3, 20), (4, 1, 10), (4, 7, 10), (4, 0, 5);               -- Baby Berserker: like the Berserker

DELETE FROM `devourer_evolution`;
INSERT INTO `devourer_evolution` (`from_shape`, `to_shape`, `bp`, `min_level`) VALUES
(1, 3, 1000, 30),                                             -- Sethrak -> Vashnik
(4, 2, 600, 20);                                              -- Baby Berserker -> Berserker (keeps its colour)

DELETE FROM `devourer_evolution_task`;
INSERT INTO `devourer_evolution_task` (`to_shape`, `task_id`, `kind`, `value`, `count`, `text`) VALUES
(3, 1, 1, 7, 40, 'Kill Humanoids as a Sethrak'),
(3, 2, 2, 8, 100, 'Weather Nature strikes as a Sethrak'),
(3, 3, 3, 3, 1, 'Devour an elite or rarer as a Sethrak'),
(2, 1, 1, 0, 50, 'Kill 50 creatures as a Baby Berserker'),
(2, 2, 4, 3, 3, 'Devour 3 Demons as a Baby Berserker');
