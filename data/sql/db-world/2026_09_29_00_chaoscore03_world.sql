-- ChaosCore0.3 (Copus55, 2026-09-28, designed with Zack). Run by Build-ChaosCore0.3.bat, after the generated
-- spell file (2026_09_29_01_chaoscore03_spells.sql: every Devourer spell, the script bindings and the shape rows,
-- including the new shape 4). Safe to run again.
--
-- The Baby Berserker (shape 4): its colourings, the creatures that grant it, its diet and its growth into the
-- Berserker. The model is the BabyBerserker that is already in the game (displays 991062-991065); nothing new
-- is added to the model tables.

-- 1. Colourings. The names are what ".devour skin <name>" takes, so they differ from the Berserker's.
--    brood_display: a Brood's hatchlings keep the same colour.
DELETE FROM `devourer_skin` WHERE `shape_id` = 4;
INSERT INTO `devourer_skin` (`display_id`, `shape_id`, `name`, `brood_display`) VALUES
(991063, 4, 'OrangeWhelp', 991063),
(991062, 4, 'AzureWhelp', 991062),
(991064, 4, 'CrimsonWhelp', 991064),
(991065, 4, 'TealWhelp', 991065);

-- A creature can only use a model that has a creature_model_info row; added only where missing.
INSERT IGNORE INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) VALUES
(991062, 0.38, 1.5, 2, 0),
(991063, 0.38, 1.5, 2, 0),
(991064, 0.38, 1.5, 2, 0),
(991065, 0.38, 1.5, 2, 0);

-- 2. Voidstorm Whelps 9101024-9101027: copies of the Voidstorm Berserker 9101020 (same faction and AI), level
--    18-20, one per colour. Devouring one unlocks the Baby Berserker and that colouring. No world spawns (they
--    come with the rift events later); for testing: .npc add temp 9101024 (or Cantrips).
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9101024 AND 9101027;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9101024 AND 9101027;
DROP TEMPORARY TABLE IF EXISTS `cc03_tmp_ct`;
CREATE TEMPORARY TABLE `cc03_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 9101020;
UPDATE `cc03_tmp_ct` SET `subname` = 'Voidstorm', `minlevel` = 18, `maxlevel` = 20;
UPDATE `cc03_tmp_ct` SET `entry` = 9101024, `name` = 'Voidstorm Whelp';
INSERT INTO `creature_template` SELECT * FROM `cc03_tmp_ct`;
UPDATE `cc03_tmp_ct` SET `entry` = 9101025, `name` = 'Azure Voidstorm Whelp';
INSERT INTO `creature_template` SELECT * FROM `cc03_tmp_ct`;
UPDATE `cc03_tmp_ct` SET `entry` = 9101026, `name` = 'Crimson Voidstorm Whelp';
INSERT INTO `creature_template` SELECT * FROM `cc03_tmp_ct`;
UPDATE `cc03_tmp_ct` SET `entry` = 9101027, `name` = 'Teal Voidstorm Whelp';
INSERT INTO `creature_template` SELECT * FROM `cc03_tmp_ct`;
DROP TEMPORARY TABLE `cc03_tmp_ct`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(9101024, 0, 991063, 1, 1, 0),
(9101025, 0, 991062, 1, 1, 0),
(9101026, 0, 991064, 1, 1, 0),
(9101027, 0, 991065, 1, 1, 0);

DELETE FROM `devourer_shape_source` WHERE `creature_entry` BETWEEN 9101024 AND 9101027;
INSERT INTO `devourer_shape_source` (`creature_entry`, `shape_id`, `display_id`) VALUES
(9101024, 4, 991063),
(9101025, 4, 991062),
(9101026, 4, 991064),
(9101027, 4, 991065);

-- 3. Diet (Bio Points per meal while worn). Like the Berserker: demons most of all, so demons are its favourite
--    food (a Glutton gets two Gorged stacks and twice the Bio Points from them).
DELETE FROM `devourer_diet` WHERE `shape_id` = 4;
INSERT INTO `devourer_diet` (`shape_id`, `creature_type`, `bp`) VALUES
(4, 3, 20), (4, 1, 10), (4, 7, 10), (4, 0, 5);

-- 4. Growth: a Baby Berserker grows into a Berserker (600 BP, level 20, two tasks). It keeps its colour.
DELETE FROM `devourer_evolution` WHERE `to_shape` = 2;
INSERT INTO `devourer_evolution` (`from_shape`, `to_shape`, `bp`, `min_level`) VALUES (4, 2, 600, 20);
DELETE FROM `devourer_evolution_task` WHERE `to_shape` = 2;
INSERT INTO `devourer_evolution_task` (`to_shape`, `task_id`, `kind`, `value`, `count`, `text`) VALUES
(2, 1, 1, 0, 50, 'Kill 50 creatures as a Baby Berserker'),
(2, 2, 4, 3, 3, 'Devour 3 Demons as a Baby Berserker');
