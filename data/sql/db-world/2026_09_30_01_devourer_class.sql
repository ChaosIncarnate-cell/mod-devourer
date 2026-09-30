-- mod-devourer: class 10, the Devourer. Server-side class data. Safe to run again.
-- Needs the class-10 core patch (core-patch/). Removed by data/sql/uninstall/world.sql.
--
-- Everything the Devourer takes from the warrior is copied from the warrior's rows in this database at install
-- time, so no Blizzard data is written into this file. What only exists in the client's DBC files
-- (SkillRaceClassInfo, SkillLineAbility, CharStartOutfit) is written by tools/build_class_dbc_sql.py.

-- --- ChrClasses: the class itself. Hunger is the rage bar (DisplayPower 1). -----------------------------------
DELETE FROM `chrclasses_dbc` WHERE `ID` = 10;
INSERT INTO `chrclasses_dbc` (`ID`, `Field01`, `DisplayPower`, `PetNameToken`,
    `Name_Lang_enUS`, `Name_Lang_Mask`, `Name_Female_Lang_enUS`, `Name_Female_Lang_Mask`,
    `Name_Male_Lang_enUS`, `Name_Male_Lang_Mask`, `Filename`, `SpellClassSet`, `Flags`, `CinematicSequenceID`,
    `Required_Expansion`) VALUES
(10, 0, 1, 0, 'Devourer', 16712190, 'Devourer', 16712190, 'Devourer', 16712190, 'DEVOURER', 0, 0, 0, 0);

-- --- Talent trees: tab page 0 Glutton, 1 Skinchanger, 2 Brood (the module's spec = the tree with most points).
-- Ids 900-902 (stock 3.3.5a TalentTab ends at 410).
DELETE FROM `talenttab_dbc` WHERE `ID` BETWEEN 900 AND 902;
INSERT INTO `talenttab_dbc` (`ID`, `Name_Lang_enUS`, `Name_Lang_Mask`, `SpellIconID`, `RaceMask`, `ClassMask`,
    `PetTalentMask`, `OrderIndex`, `BackgroundFile`) VALUES
(900, 'Glutton', 16712190, 166, 0, 512, 0, 0, 'WarriorProtection'),
(901, 'Skinchanger', 16712190, 3058, 0, 512, 0, 1, 'DruidFeralCombat'),
(902, 'Brood', 16712190, 689, 0, 512, 0, 2, 'HunterBeastMastery');

-- Talents 9000-9019 (stock 3.3.5a Talent ends near 2300). Every tier needs 5 points spent in the tree before
-- it opens (server and client both check), so each tree has 5-rank placeholder talents (spells 9100050-9100069,
-- no effect yet) until it gets real ones. Glutton, as designed on CoA (the CoA layout, squeezed into 4 columns):
--   tier 0  Iron Stomach (5)   Quick Devour        Devour Whole [ability]
--   tier 1  Deep Hunger (5)    Feast <-Quick       Regurgitate <-Devour Whole
--   tier 2                     Stretched Gut
--   tier 3                     Thick Hide <-Gut    Bile Coating <-Gut      (CoA: a choice of one; here both can
--                                                                           be taken until the module enforces it)
DELETE FROM `talent_dbc` WHERE `ID` BETWEEN 9000 AND 9019;
INSERT INTO `talent_dbc` (`ID`, `TabID`, `TierID`, `ColumnIndex`, `SpellRank_1`, `SpellRank_2`, `SpellRank_3`,
    `SpellRank_4`, `SpellRank_5`, `PrereqTalent_1`, `PrereqRank_1`, `Flags`) VALUES
(9000, 900, 0, 0, 9100050, 9100051, 9100052, 9100053, 9100054, 0, 0, 0),      -- Iron Stomach (placeholder)
(9001, 900, 0, 1, 9100031, 0, 0, 0, 0, 0, 0, 0),                              -- Quick Devour
(9002, 900, 0, 2, 9100020, 0, 0, 0, 0, 0, 0, 1),                              -- Devour Whole (ability: spellbook)
(9003, 900, 1, 0, 9100055, 9100056, 9100057, 9100058, 9100059, 0, 0, 0),      -- Deep Hunger (placeholder)
(9004, 900, 1, 1, 9100035, 0, 0, 0, 0, 9001, 0, 0),                           -- Feast
(9005, 900, 1, 2, 9100033, 0, 0, 0, 0, 9002, 0, 0),                           -- Regurgitate
(9006, 900, 2, 1, 9100036, 0, 0, 0, 0, 0, 0, 0),                              -- Stretched Gut
(9007, 900, 3, 1, 9100037, 0, 0, 0, 0, 9006, 0, 0),                           -- Digested: Thick Hide
(9008, 900, 3, 2, 9100038, 0, 0, 0, 0, 9006, 0, 0),                           -- Digested: Bile Coating
(9010, 901, 0, 1, 9100060, 9100061, 9100062, 9100063, 9100064, 0, 0, 0),      -- Fluid Flesh (placeholder)
(9015, 902, 0, 1, 9100065, 9100066, 9100067, 9100068, 9100069, 0, 0, 0);      -- Swelling Brood (placeholder)

-- --- Stats: a warrior's --------------------------------------------------------------------------------------
-- Base health/mana and stats per level.
DELETE FROM `player_class_stats` WHERE `Class` = 10;
INSERT INTO `player_class_stats` (`Class`, `Level`, `BaseHP`, `BaseMana`, `Strength`, `Agility`, `Stamina`,
    `Intellect`, `Spirit`)
SELECT 10, `Level`, `BaseHP`, `BaseMana`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_class_stats` WHERE `Class` = 1;

-- Crit, regeneration and combat-rating tables. The core reads them by class: (class-1) * 100 + level-1 for the
-- per-level tables, class-1 for the base tables, (class-1) * 32 + rating+1 for the rating scalars. The stock
-- class-10 rows hold unusable values (0 for every rating). The rows found here are saved once in
-- `devourer_backup_gt`, then overwritten with the warrior's (rows 0-99, 0, 1-32); the uninstall puts them back.
CREATE TABLE IF NOT EXISTS `devourer_backup_gt` (
    `tbl` VARCHAR(64) NOT NULL,
    `ID` INT NOT NULL,
    `Data` FLOAT NOT NULL,
    PRIMARY KEY (`tbl`, `ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='mod-devourer: the class-10 gt rows as they were before the install (read by the uninstall)';

INSERT IGNORE INTO `devourer_backup_gt` SELECT 'gtchancetomeleecrit_dbc', `ID`, `Data` FROM `gtchancetomeleecrit_dbc` WHERE `ID` BETWEEN 900 AND 999
    AND NOT EXISTS (SELECT 1 FROM (SELECT `tbl` FROM `devourer_backup_gt` WHERE `tbl` = 'installed') AS `b`);
INSERT IGNORE INTO `devourer_backup_gt` SELECT 'gtchancetospellcrit_dbc', `ID`, `Data` FROM `gtchancetospellcrit_dbc` WHERE `ID` BETWEEN 900 AND 999
    AND NOT EXISTS (SELECT 1 FROM (SELECT `tbl` FROM `devourer_backup_gt` WHERE `tbl` = 'installed') AS `b`);
INSERT IGNORE INTO `devourer_backup_gt` SELECT 'gtoctregenhp_dbc', `ID`, `Data` FROM `gtoctregenhp_dbc` WHERE `ID` BETWEEN 900 AND 999
    AND NOT EXISTS (SELECT 1 FROM (SELECT `tbl` FROM `devourer_backup_gt` WHERE `tbl` = 'installed') AS `b`);
INSERT IGNORE INTO `devourer_backup_gt` SELECT 'gtregenhpperspt_dbc', `ID`, `Data` FROM `gtregenhpperspt_dbc` WHERE `ID` BETWEEN 900 AND 999
    AND NOT EXISTS (SELECT 1 FROM (SELECT `tbl` FROM `devourer_backup_gt` WHERE `tbl` = 'installed') AS `b`);
INSERT IGNORE INTO `devourer_backup_gt` SELECT 'gtregenmpperspt_dbc', `ID`, `Data` FROM `gtregenmpperspt_dbc` WHERE `ID` BETWEEN 900 AND 999
    AND NOT EXISTS (SELECT 1 FROM (SELECT `tbl` FROM `devourer_backup_gt` WHERE `tbl` = 'installed') AS `b`);
INSERT IGNORE INTO `devourer_backup_gt` SELECT 'gtchancetomeleecritbase_dbc', `ID`, `Data` FROM `gtchancetomeleecritbase_dbc` WHERE `ID` = 9
    AND NOT EXISTS (SELECT 1 FROM (SELECT `tbl` FROM `devourer_backup_gt` WHERE `tbl` = 'installed') AS `b`);
INSERT IGNORE INTO `devourer_backup_gt` SELECT 'gtchancetospellcritbase_dbc', `ID`, `Data` FROM `gtchancetospellcritbase_dbc` WHERE `ID` = 9
    AND NOT EXISTS (SELECT 1 FROM (SELECT `tbl` FROM `devourer_backup_gt` WHERE `tbl` = 'installed') AS `b`);
INSERT IGNORE INTO `devourer_backup_gt` SELECT 'gtoctclasscombatratingscalar_dbc', `ID`, `Data` FROM `gtoctclasscombatratingscalar_dbc` WHERE `ID` BETWEEN 289 AND 320
    AND NOT EXISTS (SELECT 1 FROM (SELECT `tbl` FROM `devourer_backup_gt` WHERE `tbl` = 'installed') AS `b`);

-- The marker: the backup is taken on the first run only, so running this file again never saves rows the install
-- itself wrote. Rows that did not exist before the install have no backup row; the uninstall deletes them.
INSERT IGNORE INTO `devourer_backup_gt` VALUES ('installed', 0, 0);

INSERT INTO `gtchancetomeleecrit_dbc` (`ID`, `Data`) SELECT `ID` + 900, `Data` FROM `gtchancetomeleecrit_dbc` AS `w` WHERE `w`.`ID` BETWEEN 0 AND 99 ON DUPLICATE KEY UPDATE `Data` = VALUES(`Data`);
INSERT INTO `gtchancetospellcrit_dbc` (`ID`, `Data`) SELECT `ID` + 900, `Data` FROM `gtchancetospellcrit_dbc` AS `w` WHERE `w`.`ID` BETWEEN 0 AND 99 ON DUPLICATE KEY UPDATE `Data` = VALUES(`Data`);
INSERT INTO `gtoctregenhp_dbc` (`ID`, `Data`) SELECT `ID` + 900, `Data` FROM `gtoctregenhp_dbc` AS `w` WHERE `w`.`ID` BETWEEN 0 AND 99 ON DUPLICATE KEY UPDATE `Data` = VALUES(`Data`);
INSERT INTO `gtregenhpperspt_dbc` (`ID`, `Data`) SELECT `ID` + 900, `Data` FROM `gtregenhpperspt_dbc` AS `w` WHERE `w`.`ID` BETWEEN 0 AND 99 ON DUPLICATE KEY UPDATE `Data` = VALUES(`Data`);
INSERT INTO `gtregenmpperspt_dbc` (`ID`, `Data`) SELECT `ID` + 900, `Data` FROM `gtregenmpperspt_dbc` AS `w` WHERE `w`.`ID` BETWEEN 0 AND 99 ON DUPLICATE KEY UPDATE `Data` = VALUES(`Data`);
INSERT INTO `gtchancetomeleecritbase_dbc` (`ID`, `Data`) SELECT 9, `Data` FROM `gtchancetomeleecritbase_dbc` AS `w` WHERE `w`.`ID` = 0 ON DUPLICATE KEY UPDATE `Data` = VALUES(`Data`);
INSERT INTO `gtchancetospellcritbase_dbc` (`ID`, `Data`) SELECT 9, `Data` FROM `gtchancetospellcritbase_dbc` AS `w` WHERE `w`.`ID` = 0 ON DUPLICATE KEY UPDATE `Data` = VALUES(`Data`);
INSERT INTO `gtoctclasscombatratingscalar_dbc` (`ID`, `Data`) SELECT `ID` + 288, `Data` FROM `gtoctclasscombatratingscalar_dbc` AS `w` WHERE `w`.`ID` BETWEEN 1 AND 32 ON DUPLICATE KEY UPDATE `Data` = VALUES(`Data`);

-- --- A new Devourer --------------------------------------------------------------------------------------------
-- Every race, starting where the race's first class starts (not the Death Knight's Ebon Hold).
DELETE FROM `playercreateinfo` WHERE `class` = 10;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT `p`.`race`, 10, `p`.`map`, `p`.`zone`, `p`.`position_x`, `p`.`position_y`, `p`.`position_z`, `p`.`orientation`
FROM `playercreateinfo` AS `p`
WHERE `p`.`class` = (SELECT MIN(`q`.`class`) FROM (SELECT `race`, `class` FROM `playercreateinfo`) AS `q`
                     WHERE `q`.`race` = `p`.`race` AND `q`.`class` NOT IN (6, 10));

-- The base kit from the start (spells in 2026_09_30_08; the module also teaches them at login, and the hidden
-- Anima passive). Bars: Attack, Rush, Concentrate, Devour.
DELETE FROM `playercreateinfo_spell_custom` WHERE `classmask` = 512;
INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES
(0, 512, 9100001, 'Devourer: Devour'),
(0, 512, 9100990, 'Devourer: Rush'),
(0, 512, 9100992, 'Devourer: Concentrate'),
(0, 512, 9100993, 'Devourer: Anima');

DELETE FROM `playercreateinfo_action` WHERE `class` = 10;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT `race`, 10, 0, 6603, 0 FROM `playercreateinfo` WHERE `class` = 10;          -- Attack
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT `race`, 10, 1, 9100990, 0 FROM `playercreateinfo` WHERE `class` = 10;       -- Rush
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT `race`, 10, 2, 9100992, 0 FROM `playercreateinfo` WHERE `class` = 10;       -- Concentrate
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT `race`, 10, 3, 9100001, 0 FROM `playercreateinfo` WHERE `class` = 10;       -- Devour

-- Weapon and armour skills at creation (task 006): leather, maces, two-handed maces, daggers, staves. Cloth,
-- Defense and Unarmed come with every class (classMask 0). Fist weapons and polearms are taught by the weapon
-- masters. No mail, plate, shields, swords, axes or ranged weapons. They only take effect with the
-- SkillRaceClassInfo rows from tools/build_class_dbc_sql.py.
DELETE FROM `playercreateinfo_skills` WHERE `classMask` = 512;
INSERT INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES
(0, 512, 414, 0, 'Devourer: Leather'),
(0, 512, 54, 0, 'Devourer: Maces'),
(0, 512, 160, 0, 'Devourer: Two-Handed Maces'),
(0, 512, 173, 0, 'Devourer: Daggers'),
(0, 512, 136, 0, 'Devourer: Staves');
