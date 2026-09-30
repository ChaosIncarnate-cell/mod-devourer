-- ChaosCore0.2 (Copus55, 2026-09-28, with Zack's yes). Run by Build-ChaosCore0.2.bat.
-- (The Smash spell fix is left for a later update, as Zack decided.)

-- 1. Rising Serpents (Vashnik) wear the working Twinfangs models 991040 (purple) and 991045 (pale teal).
--    The creature is made only if it is missing (a copy of the Brood hatchling 9101100, rooted).
DROP TEMPORARY TABLE IF EXISTS `cc02_tmp_ct`;
CREATE TEMPORARY TABLE `cc02_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 9101100
    AND NOT EXISTS (SELECT 1 FROM (SELECT `entry` FROM `creature_template` WHERE `entry` = 9101102) AS `x`);
UPDATE `cc02_tmp_ct` SET `entry` = 9101102, `name` = 'Rising Serpent', `type` = 1, `speed_walk` = 0, `speed_run` = 0;
INSERT INTO `creature_template` SELECT * FROM `cc02_tmp_ct`;
DROP TEMPORARY TABLE `cc02_tmp_ct`;

DELETE FROM `creature_template_model` WHERE `CreatureID` = 9101102;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(9101102, 0, 991040, 1, 0.5, 0),
(9101102, 1, 991045, 1, 0.5, 0);

-- A creature can only use a model that has a creature_model_info row; added only where missing.
INSERT IGNORE INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) VALUES
(991040, 0.5, 1.5, 2, 0),
(991045, 0.5, 1.5, 2, 0);
