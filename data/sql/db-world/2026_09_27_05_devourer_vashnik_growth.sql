-- mod-devourer: the Vashnik (shape 3), what a Sethrak evolves into, and growth: Bio Points and evolution.
-- The Vashnik model (creature\vashnik) and the Ulatek snake (creature\ulateksnake, the Rising Serpents) were
-- converted by the RetroportTool; their rows are repeated here so a fresh install has them. Safe to run again.

DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 902041;
INSERT INTO `creaturemodeldata_dbc` (`ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`, `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`, `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`, `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`) VALUES (902041, 148, 'creature\\vashnik\\vashnik.mdx', 1, 1.0, 2, 4, 18.0, 12.0, 1.0, 0, 0, 5834, 0, 2.03128, 1.0, 0.0, -1.37326, -0.618815, -0.034495, 0.495563, 1.53916, 2.4973, 1.0, 1.0, 1.0, 0.0, 0.0);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991029;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991029, 902041, 6114, 0, 1.0, 255, 'vashnik', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991029;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991029, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991030;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991030, 902041, 6114, 0, 1.0, 255, 'vashnik_7473341', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991030;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991030, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991031;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991031, 902041, 6114, 0, 1.0, 255, 'vashnik_7473343', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991031;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991031, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991032;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991032, 902041, 6114, 0, 1.0, 255, 'vashnik_7473345', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991032;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991032, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991033;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991033, 902041, 6114, 0, 1.0, 255, 'vashnik_7473353', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991033;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991033, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991034;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991034, 902041, 6114, 0, 1.0, 255, 'vashnik_7473355', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991034;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991034, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991035;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991035, 902041, 6114, 0, 1.0, 255, 'vashnik_7473359', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991035;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991035, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991036;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991036, 902041, 6114, 0, 1.0, 255, 'vashnik_7493540', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991036;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991036, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991037;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991037, 902041, 6114, 0, 1.0, 255, 'vashnik_7493541', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991037;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991037, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991038;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991038, 902041, 6114, 0, 1.0, 255, 'vashnik_armor', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991038;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991038, 0.38, 1.5, 2);

-- The Ulatek snake (creature\ulateksnake, display 991008) is kept registered but unused: the Rising Serpents
-- wear the Twinfangs model (displays 991040 and 991045, registered by the RetroportTool).
-- creature\ulateksnake: The RetroportTool registered it as ulateksnake.mdx, but its file is
-- ulateksnake01.mdx; the model row is repeated here with the right name.
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 902043;
INSERT INTO `creaturemodeldata_dbc` (`ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`, `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`, `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`, `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`) VALUES (902043, 148, 'creature\\ulateksnake\\ulateksnake01.mdx', 1, 1.0, 2, 4, 18.0, 12.0, 1.0, 0, 0, 5834, 0, 2.03128, 1.0, 0.0, -1.37326, -0.618815, -0.034495, 0.495563, 1.53916, 2.4973, 1.0, 1.0, 1.0, 0.0, 0.0);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991008;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES
(991008, 902043, 0, 0, 0.6, 255, 'ulateksnake01_7485611', 'ulateksnake01_7485605', '', '', 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991008;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) VALUES (991008, 0.5, 1.5, 2, 0);

DELETE FROM `creature_template_model` WHERE `CreatureID` = 9101102;
DELETE FROM `creature_template` WHERE `entry` = 9101102;
DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;
CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 9101100;
UPDATE `devourer_tmp_ct` SET `entry` = 9101102, `name` = 'Rising Serpent', `type` = 1, `speed_walk` = 0, `speed_run` = 0;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(9101102, 0, 991040, 1, 0.5, 0),                              -- Twinfangs, purple
(9101102, 1, 991045, 1, 0.5, 0);                              -- Twinfangs, pale teal

DELETE FROM `devourer_skin` WHERE `shape_id` = 3;
INSERT INTO `devourer_skin` (`display_id`, `shape_id`, `name`, `brood_display`) VALUES (991029, 3, 'Vashnik', 0);

-- --- growth ------------------------------------------------------------------------------------------------
-- Bio Points per meal while the form is worn, by the meal's creature type (0 = anything else). The meal's
-- rarity multiplies them: normal 1, elite 3, rare 5, rare elite 8, bosses 20.
-- Creature types: 1 Beast, 2 Dragonkin, 3 Demon, 4 Elemental, 5 Giant, 6 Undead, 7 Humanoid, 8 Critter, 9 Mechanical.
DROP TABLE IF EXISTS `devourer_diet`;
CREATE TABLE `devourer_diet` (
    `shape_id` INT UNSIGNED NOT NULL,
    `creature_type` TINYINT UNSIGNED NOT NULL COMMENT '0 = anything not listed',
    `bp` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`shape_id`, `creature_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `devourer_diet` (`shape_id`, `creature_type`, `bp`) VALUES
(1, 7, 15), (1, 1, 10), (1, 2, 25), (1, 0, 3),               -- Sethrak: people and beasts of the sands, dragons best
(2, 3, 20), (2, 7, 10), (2, 1, 10), (2, 0, 5),               -- Berserker: demons most of all
(3, 7, 15), (3, 1, 10), (3, 2, 25), (3, 0, 3);               -- Vashnik

DROP TABLE IF EXISTS `devourer_evolution`;
CREATE TABLE `devourer_evolution` (
    `from_shape` INT UNSIGNED NOT NULL,
    `to_shape` INT UNSIGNED NOT NULL,
    `bp` INT UNSIGNED NOT NULL COMMENT 'Bio Points the from-form must have earned',
    `min_level` TINYINT UNSIGNED NOT NULL DEFAULT 1,
    PRIMARY KEY (`to_shape`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `devourer_evolution` (`from_shape`, `to_shape`, `bp`, `min_level`) VALUES
(1, 3, 1000, 30);                                             -- Sethrak -> Vashnik

-- Tasks, done while wearing the from-form. kind 1 kill (value = creature type, 0 any), 2 be hit by (value =
-- school mask: 1 physical, 2 holy, 4 fire, 8 nature, 16 frost, 32 shadow, 64 arcane), 3 devour at least this rare
-- (value = rarity multiplier), 4 devour a creature type.
DROP TABLE IF EXISTS `devourer_evolution_task`;
CREATE TABLE `devourer_evolution_task` (
    `to_shape` INT UNSIGNED NOT NULL,
    `task_id` INT UNSIGNED NOT NULL,
    `kind` TINYINT UNSIGNED NOT NULL,
    `value` INT UNSIGNED NOT NULL DEFAULT 0,
    `count` INT UNSIGNED NOT NULL DEFAULT 1,
    `text` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`to_shape`, `task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `devourer_evolution_task` (`to_shape`, `task_id`, `kind`, `value`, `count`, `text`) VALUES
(3, 1, 1, 7, 40, 'Kill Humanoids as a Sethrak'),
(3, 2, 2, 8, 100, 'Weather Nature strikes as a Sethrak'),
(3, 3, 3, 3, 1, 'Devour an elite or rarer as a Sethrak');
