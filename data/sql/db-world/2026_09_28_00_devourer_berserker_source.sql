-- mod-devourer: the Berserker can be devoured (Copus55, 2026-09-28, with Zack's yes).
-- One "Voidstorm Berserker" per colouring, copied from the Sethrak source creature 9101001 (level, faction,
-- AI), with the berserkerboss look. Devouring one unlocks the Berserker shape (shape 2) and that colouring.
-- No world spawns: they come through rift events later; for testing, spawn them (Cantrips or .npc add temp).
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9101020 AND 9101023;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9101020 AND 9101023;
DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;
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
DROP TEMPORARY TABLE `devourer_tmp_ct`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(9101020, 0, 991015, 1, 1, 0),
(9101021, 0, 991014, 1, 1, 0),
(9101022, 0, 991016, 1, 1, 0),
(9101023, 0, 991017, 1, 1, 0);

DELETE FROM `devourer_shape_source` WHERE `creature_entry` BETWEEN 9101020 AND 9101023;
INSERT INTO `devourer_shape_source` (`creature_entry`, `shape_id`, `display_id`) VALUES
(9101020, 2, 991015),
(9101021, 2, 991014),
(9101022, 2, 991016),
(9101023, 2, 991017);
