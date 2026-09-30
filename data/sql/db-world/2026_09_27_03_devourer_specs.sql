-- mod-devourer: the creatures the specializations summon. Safe to run again.
--   9101100 Hatchling  Brood's Hatch Brood (guardian; the module gives it the worn shape's pet model and stats)
--   9101101 Echo       a Skinchanger's shape, left behind for a few seconds (guardian, translucent)
DELETE FROM `creature_template_model` WHERE `CreatureID` IN (9101100, 9101101);
DELETE FROM `creature_template` WHERE `entry` IN (9101100, 9101101);
DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;
CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 9101001;
UPDATE `devourer_tmp_ct` SET `name` = 'Hatchling', `subname` = NULL, `minlevel` = 1, `maxlevel` = 80, `faction` = 35,
    `npcflag` = 0, `unit_flags` = 0, `lootid` = 0, `skinloot` = 0, `pickpocketloot` = 0, `mingold` = 0, `maxgold` = 0,
    `ExperienceModifier` = 0, `KillCredit1` = 0, `KillCredit2` = 0, `AIName` = '', `ScriptName` = '', `flags_extra` = 0,
    `type` = 1, `family` = 0, `unit_class` = 1, `HealthModifier` = 1, `DamageModifier` = 1, `BaseAttackTime` = 2000,
    `MovementType` = 0, `entry` = 9101100;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
UPDATE `devourer_tmp_ct` SET `entry` = 9101101, `name` = 'Echo', `type` = 6, `speed_run` = 1.3;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(9101100, 0, 4312, 1, 1, 0),
(9101101, 0, 200004, 1, 1, 0);
INSERT IGNORE INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) VALUES
(4312, 0.5, 1.5, 2, 0);
