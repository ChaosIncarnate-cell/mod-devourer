-- mod-devourer: Sethrak colourings. Each is the Sethrak shape's model (display 200004) with another body texture
-- (client patch-T: creature\sethrak_melee\devourer_sethrak_*.blp). Devouring a creature of that colouring
-- unlocks it; .devour skin <name> wears it. Safe to run again.

DROP TABLE IF EXISTS `devourer_skin`;                  -- static data, all refilled below and by the shape files
CREATE TABLE `devourer_skin` (
    `display_id` INT UNSIGNED NOT NULL,
    `shape_id` INT UNSIGNED NOT NULL,
    `name` VARCHAR(32) NOT NULL COMMENT 'what .devour skin takes',
    `brood_display` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'a Brood''s hatchlings while it is worn; 0 = the shape''s',
    PRIMARY KEY (`display_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DELETE FROM `devourer_skin` WHERE `shape_id` = 1;
INSERT INTO `devourer_skin` (`display_id`, `shape_id`, `name`) VALUES
(200004, 1, 'Black'),
(991001, 1, 'Diamondback'),
(991002, 1, 'Green'),
(991003, 1, 'Ember'),
(991004, 1, 'Viper'),
(991005, 1, 'Dusk'),
(991006, 1, 'Gilded'),
(991007, 1, 'Blood');

-- The displays, for the server (the client has the same rows in patch-T).
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` BETWEEN 991001 AND 991009;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES
(991001, 402214, 0, 0, 1, 255, 'devourer_sethrak_diamondback', 'sethrak_melee_red', '', '', 0, 0, 0, 0, 0, 0),
(991002, 402214, 0, 0, 1, 255, 'devourer_sethrak_green', 'sethrak_melee_red', '', '', 0, 0, 0, 0, 0, 0),
(991003, 402214, 0, 0, 1, 255, 'devourer_sethrak_ember', 'sethrak_melee_red', '', '', 0, 0, 0, 0, 0, 0),
(991004, 402214, 0, 0, 1, 255, 'devourer_sethrak_viper', 'sethrak_melee_red', '', '', 0, 0, 0, 0, 0, 0),
(991005, 402214, 0, 0, 1, 255, 'devourer_sethrak_dusk', 'sethrak_melee_red', '', '', 0, 0, 0, 0, 0, 0),
(991006, 402214, 0, 0, 1, 255, 'devourer_sethrak_gilded', 'sethrak_melee_red', '', '', 0, 0, 0, 0, 0, 0),
(991007, 402214, 0, 0, 1, 255, 'devourer_sethrak_blood', 'sethrak_melee_red', '', '', 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` BETWEEN 991001 AND 991009;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) VALUES
(991001, 0.5, 1.5, 2, 0), (991002, 0.5, 1.5, 2, 0), (991003, 0.5, 1.5, 2, 0), (991004, 0.5, 1.5, 2, 0),
(991005, 0.5, 1.5, 2, 0), (991006, 0.5, 1.5, 2, 0), (991007, 0.5, 1.5, 2, 0);

-- The camp's own Sethrak give their colouring: the Sandstalkers the Diamondback, the Venomcallers the Green.
UPDATE `devourer_shape_source` SET `display_id` = 991001 WHERE `creature_entry` = 9101001;
UPDATE `devourer_shape_source` SET `display_id` = 991002 WHERE `creature_entry` = 9101002;

-- One rarer Sethrak for each new colouring, wandering the same dunes (level 45-46, 10 min respawn).
DELETE FROM `creature` WHERE `guid` BETWEEN 9910009 AND 9910020;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9101003 AND 9101009;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9101003 AND 9101009;
DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;
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
(9101003, 0, 991003, 1, 1, 0),
(9101004, 0, 991004, 1, 1, 0),
(9101005, 0, 991005, 1, 1, 0),
(9101006, 0, 991006, 1, 1, 0),
(9101007, 0, 991007, 1, 1, 0);
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`) VALUES
(9910009, 9101003, 1, 1, 1, -7649.1, -3530.3, 22.6, 4.3, 600, 5, 1),
(9910010, 9101004, 1, 1, 1, -7503.1, -3555.6, 11.2, 3.5, 600, 5, 1),
(9910011, 9101005, 1, 1, 1, -7310.6, -3219.5, 9.5, 0.9, 600, 5, 1),
(9910012, 9101006, 1, 1, 1, -7046.6, -3358.0, 9.3, 4.0, 600, 5, 1),
(9910013, 9101007, 1, 1, 1, -6890.4, -2955.4, 9.6, 5.8, 600, 5, 1);

DELETE FROM `devourer_shape_source` WHERE `creature_entry` BETWEEN 9101003 AND 9101009;
INSERT INTO `devourer_shape_source` (`creature_entry`, `shape_id`, `display_id`) VALUES
(9101003, 1, 991003),
(9101004, 1, 991004),
(9101005, 1, 991005),
(9101006, 1, 991006),
(9101007, 1, 991007);
