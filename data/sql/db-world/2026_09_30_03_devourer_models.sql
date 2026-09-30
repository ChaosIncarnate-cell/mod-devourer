-- mod-devourer: the models and looks the Devourer's shapes and creatures use, for the server (the client
-- patch carries the same rows in CreatureModelData.dbc / CreatureDisplayInfo.dbc, task 004). Safe to run again.
--
--   902038-902045  CreatureModelData: creature\berserker, berserkerboss, vashnik, babyberserker (902043 unused)
--                  (converted by the RetroportTool; the model files come with the client patch)
--   991001-991065  CreatureDisplayInfo: Sethrak colourings, Berserker, Vashnik, Baby Berserker, snakes
--
-- Not here: the Sethrak itself (display 200004, model 402214) and the Sethrak camp's looks (80018, 80305,
-- 280018), and the Twinfangs serpents (991040, 991045). On CoA those were in the client's own DBCs; here they
-- come from the client patch tooling (task 004), which writes their rows for the server as well.

-- --- Sethrak colourings (the Sethrak model with other body textures, patch textures devourer_sethrak_*) ---
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

-- --- the Berserker (berserkerboss 991014-991017 are worn; berserker 991010-991013 are registered, unused) ---
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

-- --- the Vashnik (the Rising Serpents wear the Twinfangs; the Ulatek snake is not planned, owner 2026-09-30) ---
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

-- A creature can only use a model that has a creature_model_info row. These looks come from task 004's
-- display rows; their creature_model_info rows are the module's own.
DELETE FROM `creature_model_info` WHERE `DisplayID` IN (80018, 80305, 200004, 280018, 991040, 991045);
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) VALUES
(80018, 0.5, 1.5, 2, 0), (80305, 0.5, 1.5, 2, 0), (200004, 0.5, 1.5, 2, 0), (280018, 0.5, 1.5, 2, 0),
(991040, 0.5, 1.5, 2, 0), (991045, 0.5, 1.5, 2, 0);
