-- mod-devourer: the Berserker shape (shape 2). Its model is creature\berserker (and the bigger
-- creature\berserkerboss, worn as the "Ultradon" colourings; the hatchlings are creature\babyberserker), converted into Data\creature by the RetroportTool;
-- the displays below are the ones that tool registered, repeated here so a fresh install has them. Safe to run again.

DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 902038;
INSERT INTO `creaturemodeldata_dbc` (`ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`, `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`, `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`, `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`) VALUES (902038, 148, 'creature\\berserker\\berserker.mdx', 1, 1.0, 2, 4, 18.0, 12.0, 1.0, 0, 0, 5834, 0, 2.03128, 1.0, 0.0, -1.37326, -0.618815, -0.034495, 0.495563, 1.53916, 2.4973, 1.0, 1.0, 1.0, 0.0, 0.0);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991011;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991011, 902038, 6114, 0, 1.0, 255, 'berserker_blue_skin', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991011;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991011, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991010;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991010, 902038, 6114, 0, 1.0, 255, 'berserker_orange_skin', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991010;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991010, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991012;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991012, 902038, 6114, 0, 1.0, 255, 'berserker_red_skin', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991012;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991012, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991013;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991013, 902038, 6114, 0, 1.0, 255, 'berserker_teal_skin', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991013;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991013, 0.38, 1.5, 2);
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 902039;
INSERT INTO `creaturemodeldata_dbc` (`ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`, `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`, `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`, `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`) VALUES (902039, 148, 'creature\\berserkerboss\\berserkerboss.mdx', 1, 1.0, 2, 4, 18.0, 12.0, 1.0, 0, 0, 5834, 0, 2.03128, 1.0, 0.0, -1.37326, -0.618815, -0.034495, 0.495563, 1.53916, 2.4973, 1.0, 1.0, 1.0, 0.0, 0.0);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991014;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991014, 902039, 6114, 0, 1.0, 255, 'berserkerboss_blue', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991014;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991014, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991015;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991015, 902039, 6114, 0, 1.0, 255, 'berserkerboss_orange', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991015;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991015, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991016;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991016, 902039, 6114, 0, 1.0, 255, 'berserkerboss_red', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991016;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991016, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991017;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991017, 902039, 6114, 0, 1.0, 255, 'berserkerboss_teal', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991017;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991017, 0.38, 1.5, 2);

-- creature\babyberserker: the Berserker's hatchlings.
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 902045;
INSERT INTO `creaturemodeldata_dbc` (`ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`, `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`, `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`, `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`) VALUES (902045, 148, 'creature\\babyberserker\\babyberserker.mdx', 1, 1.0, 2, 4, 18.0, 12.0, 1.0, 0, 0, 5834, 0, 2.03128, 1.0, 0.0, -1.37326, -0.618815, -0.034495, 0.495563, 1.53916, 2.4973, 1.0, 1.0, 1.0, 0.0, 0.0);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991062;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991062, 902045, 6114, 0, 1.0, 255, 'babyberserker_blue_skin', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991062;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991062, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991063;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991063, 902045, 6114, 0, 1.0, 255, 'babyberserker_orange_skin', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991063;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991063, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991064;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991064, 902045, 6114, 0, 1.0, 255, 'babyberserker_red_skin', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991064;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991064, 0.38, 1.5, 2);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 991065;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (991065, 902045, 6114, 0, 1.0, 255, 'babyberserker_teal_skin', NULL, NULL, NULL, 0, 0, 0, 0, 0, 0);
DELETE FROM `creature_model_info` WHERE `DisplayID` = 991065;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES (991065, 0.38, 1.5, 2);

DELETE FROM `devourer_skin` WHERE `shape_id` = 2;
-- The Berserker is the berserkerboss model (991014-991017); the old creature\berserker model (991010-991013) is not used.
INSERT INTO `devourer_skin` (`display_id`, `shape_id`, `name`, `brood_display`) VALUES
(991015, 2, 'Orange', 991063),
(991014, 2, 'Azure', 991062),
(991016, 2, 'Crimson', 991064),
(991017, 2, 'Teal', 991065);
