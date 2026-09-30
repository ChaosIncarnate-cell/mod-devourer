-- mod-devourer uninstall, characters database. Run with the worldserver stopped, BEFORE world.sql and before the
-- core patch is reverted (the core refuses to load a class-10 character without the Devourer's class data).
--
--   mysql acore_characters < data/sql/uninstall/characters.sql
--
-- Every Devourer becomes a warrior of the same race, level and gear. At its next login the core resets its
-- spells and talents (at_login flags), so it relearns what a warrior of its level knows.

-- 1. Devourers become warriors.
UPDATE `characters` SET `class` = 1, `at_login` = `at_login` | 0x02 | 0x04   -- AT_LOGIN_RESET_SPELLS, _RESET_TALENTS
 WHERE `class` = 10;

-- 2. Nothing of the Devourer's spells, talents, auras, cooldowns or buttons stays behind (spells 9100000-9100899).
DELETE FROM `character_talent`         WHERE `spell` BETWEEN 9100000 AND 9100899;
DELETE FROM `character_spell`          WHERE `spell` BETWEEN 9100000 AND 9100899;
DELETE FROM `character_aura`           WHERE `spell` BETWEEN 9100000 AND 9100899;
DELETE FROM `character_spell_cooldown` WHERE `spell` BETWEEN 9100000 AND 9100899;
DELETE FROM `character_action`         WHERE `type` = 0 AND `action` BETWEEN 9100000 AND 9100899;

-- 3. The idols (items 9100100, 9100101) disappear with their item template: from bags, bank and mail.
DELETE `ci` FROM `character_inventory` AS `ci`
  JOIN `item_instance` AS `ii` ON `ii`.`guid` = `ci`.`item`
 WHERE `ii`.`itemEntry` IN (9100100, 9100101);
DELETE `mi` FROM `mail_items` AS `mi`
  JOIN `item_instance` AS `ii` ON `ii`.`guid` = `mi`.`item_guid`
 WHERE `ii`.`itemEntry` IN (9100100, 9100101);
DELETE FROM `item_instance` WHERE `itemEntry` IN (9100100, 9100101);

-- 4. The module's own tables, last.
DROP TABLE IF EXISTS `character_devourer_bar`, `character_devourer_task`, `character_devourer_growth`,
    `character_devourer_worn`, `character_devourer_skin`, `character_devourer_shape`;

-- 5. Forget that the install file ran, so a later reinstall runs it again.
DELETE FROM `updates` WHERE `name` = '2026_09_30_00_devourer_characters.sql';
