-- mod-devourer uninstall, world database. Run with the worldserver stopped, AFTER characters.sql.
--
--   mysql acore_world < data/sql/uninstall/world.sql
--
-- Deletes every row the install added (by the Devourer's id ranges), puts the class-10 gt rows back as they were,
-- then drops the module's tables. Afterwards remove the module folder (or set Devourer.Enable = 0 and keep it
-- out of the build); otherwise the next worldserver start installs it again.

-- --- spells and items (2026_09_30_02) --------------------------------------------------------------------------
DELETE FROM `spell_dbc`          WHERE `ID`       BETWEEN 9100000 AND 9100899;
DELETE FROM `spell_script_names` WHERE `spell_id` BETWEEN 9100000 AND 9100899;
DELETE FROM `spell_custom_attr`  WHERE `spell_id` BETWEEN 9100000 AND 9100899;
DELETE FROM `spell_proc`         WHERE `SpellId`  BETWEEN 9100000 AND 9100899;
DELETE FROM `item_template`      WHERE `entry` IN (9100100, 9100101);

-- --- creatures, spawns and looks (2026_09_30_03, _04) ------------------------------------------------------------
DELETE FROM `creature`                WHERE `guid` BETWEEN 9910001 AND 9910020 OR `id` BETWEEN 9101000 AND 9101199;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9101000 AND 9101199;
DELETE FROM `creature_template`       WHERE `entry` BETWEEN 9101000 AND 9101199;
DELETE FROM `creature_model_info`     WHERE `DisplayID` BETWEEN 991001 AND 991065 OR `DisplayID` IN (80018, 80305, 200004, 280018);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` BETWEEN 991001 AND 991065;
DELETE FROM `creaturemodeldata_dbc`   WHERE `ID` BETWEEN 902038 AND 902045;
-- Looks the client patch tool copied from the CoA client (the generated _06); it lists them in devourer_client_rows.
CREATE TABLE IF NOT EXISTS `devourer_client_rows` (`tbl` VARCHAR(64) NOT NULL, `ID` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`tbl`, `ID`)) ENGINE=InnoDB;
DELETE `t` FROM `creaturedisplayinfo_dbc` AS `t` JOIN `devourer_client_rows` AS `r` ON `r`.`tbl` = 'creaturedisplayinfo_dbc' AND `r`.`ID` = `t`.`ID`;
DELETE `t` FROM `creaturemodeldata_dbc` AS `t` JOIN `devourer_client_rows` AS `r` ON `r`.`tbl` = 'creaturemodeldata_dbc' AND `r`.`ID` = `t`.`ID`;
DELETE `t` FROM `creaturedisplayinfoextra_dbc` AS `t` JOIN `devourer_client_rows` AS `r` ON `r`.`tbl` = 'creaturedisplayinfoextra_dbc' AND `r`.`ID` = `t`.`ID`;
-- The spawns' explicit guids raised the counter; this sets it back to the highest guid left + 1.
ALTER TABLE `creature` AUTO_INCREMENT = 1;

-- --- the class (2026_09_30_01, and the generated _05) ----------------------------------------------------------
DELETE FROM `chrclasses_dbc`                WHERE `ID` = 10;
DELETE FROM `talenttab_dbc`                 WHERE `ID` BETWEEN 900 AND 902;
DELETE FROM `talent_dbc`                    WHERE `ID` BETWEEN 9000 AND 9019;
DELETE FROM `player_class_stats`            WHERE `Class` = 10;
DELETE FROM `playercreateinfo`              WHERE `class` = 10;
DELETE FROM `playercreateinfo_action`       WHERE `class` = 10;
DELETE FROM `playercreateinfo_skills`       WHERE `classMask` = 512;
DELETE FROM `playercreateinfo_spell_custom` WHERE `classmask` = 512;
DELETE FROM `skillraceclassinfo_dbc`        WHERE `ClassMask` & 512;
DELETE FROM `skilllineability_dbc`          WHERE `ClassMask` & 512;
DELETE FROM `charstartoutfit_dbc`           WHERE `ClassID` = 10;

-- The class-10 gt rows: back to what they were before the install (saved in devourer_backup_gt). Rows the
-- install created (none on a stock database) are deleted.
UPDATE `gtchancetomeleecrit_dbc` AS `t` JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtchancetomeleecrit_dbc' AND `b`.`ID` = `t`.`ID` SET `t`.`Data` = `b`.`Data`;
UPDATE `gtchancetospellcrit_dbc` AS `t` JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtchancetospellcrit_dbc' AND `b`.`ID` = `t`.`ID` SET `t`.`Data` = `b`.`Data`;
UPDATE `gtoctregenhp_dbc` AS `t` JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtoctregenhp_dbc' AND `b`.`ID` = `t`.`ID` SET `t`.`Data` = `b`.`Data`;
UPDATE `gtregenhpperspt_dbc` AS `t` JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtregenhpperspt_dbc' AND `b`.`ID` = `t`.`ID` SET `t`.`Data` = `b`.`Data`;
UPDATE `gtregenmpperspt_dbc` AS `t` JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtregenmpperspt_dbc' AND `b`.`ID` = `t`.`ID` SET `t`.`Data` = `b`.`Data`;
UPDATE `gtchancetomeleecritbase_dbc` AS `t` JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtchancetomeleecritbase_dbc' AND `b`.`ID` = `t`.`ID` SET `t`.`Data` = `b`.`Data`;
UPDATE `gtchancetospellcritbase_dbc` AS `t` JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtchancetospellcritbase_dbc' AND `b`.`ID` = `t`.`ID` SET `t`.`Data` = `b`.`Data`;
UPDATE `gtoctclasscombatratingscalar_dbc` AS `t` JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtoctclasscombatratingscalar_dbc' AND `b`.`ID` = `t`.`ID` SET `t`.`Data` = `b`.`Data`;

DELETE `t` FROM `gtchancetomeleecrit_dbc` AS `t` LEFT JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtchancetomeleecrit_dbc' AND `b`.`ID` = `t`.`ID` WHERE `t`.`ID` BETWEEN 900 AND 999 AND `b`.`ID` IS NULL;
DELETE `t` FROM `gtchancetospellcrit_dbc` AS `t` LEFT JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtchancetospellcrit_dbc' AND `b`.`ID` = `t`.`ID` WHERE `t`.`ID` BETWEEN 900 AND 999 AND `b`.`ID` IS NULL;
DELETE `t` FROM `gtoctregenhp_dbc` AS `t` LEFT JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtoctregenhp_dbc' AND `b`.`ID` = `t`.`ID` WHERE `t`.`ID` BETWEEN 900 AND 999 AND `b`.`ID` IS NULL;
DELETE `t` FROM `gtregenhpperspt_dbc` AS `t` LEFT JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtregenhpperspt_dbc' AND `b`.`ID` = `t`.`ID` WHERE `t`.`ID` BETWEEN 900 AND 999 AND `b`.`ID` IS NULL;
DELETE `t` FROM `gtregenmpperspt_dbc` AS `t` LEFT JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtregenmpperspt_dbc' AND `b`.`ID` = `t`.`ID` WHERE `t`.`ID` BETWEEN 900 AND 999 AND `b`.`ID` IS NULL;
DELETE `t` FROM `gtchancetomeleecritbase_dbc` AS `t` LEFT JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtchancetomeleecritbase_dbc' AND `b`.`ID` = `t`.`ID` WHERE `t`.`ID` = 9 AND `b`.`ID` IS NULL;
DELETE `t` FROM `gtchancetospellcritbase_dbc` AS `t` LEFT JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtchancetospellcritbase_dbc' AND `b`.`ID` = `t`.`ID` WHERE `t`.`ID` = 9 AND `b`.`ID` IS NULL;
DELETE `t` FROM `gtoctclasscombatratingscalar_dbc` AS `t` LEFT JOIN `devourer_backup_gt` AS `b` ON `b`.`tbl` = 'gtoctclasscombatratingscalar_dbc' AND `b`.`ID` = `t`.`ID` WHERE `t`.`ID` BETWEEN 289 AND 320 AND `b`.`ID` IS NULL;

-- --- the module's own tables, last -------------------------------------------------------------------------------
DROP TABLE IF EXISTS `devourer_evolution_task`, `devourer_evolution`, `devourer_diet`, `devourer_skin`,
    `devourer_shape_source`, `devourer_shape`, `devourer_backup_gt`, `devourer_client_rows`;

-- Forget that the install files ran, so a later reinstall runs them again.
DELETE FROM `updates` WHERE `name` IN ('2026_09_30_00_devourer_tables.sql', '2026_09_30_01_devourer_class.sql',
    '2026_09_30_02_devourer_spells.sql', '2026_09_30_03_devourer_models.sql', '2026_09_30_04_devourer_world.sql',
    '2026_09_30_05_devourer_class_dbc.generated.sql', '2026_09_30_06_devourer_coa_looks.generated.sql');
