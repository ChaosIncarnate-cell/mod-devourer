-- mod-devourer uninstall, characters database. Run with the worldserver stopped, BEFORE world.sql and before the
-- core patch is reverted (the core refuses to load a class-10 character without the Devourer's class data).
--
--   mysql acore_characters < data/sql/uninstall/characters.sql
--
-- Every Devourer becomes a warrior of the same race, level and gear. At its next login the core resets its
-- spells and talents (at_login flags), so it relearns what a warrior of its level knows.

-- 0. A Devourer still in the In-Between (map 35, task 010) goes to its home first: without the module that room
--    has no way out.
UPDATE `characters` AS `c` JOIN `character_homebind` AS `h` ON `h`.`guid` = `c`.`guid`
   SET `c`.`map` = `h`.`mapId`, `c`.`zone` = `h`.`zoneId`, `c`.`position_x` = `h`.`posX`,
       `c`.`position_y` = `h`.`posY`, `c`.`position_z` = `h`.`posZ`
 WHERE `c`.`class` = 10 AND `c`.`map` = 35;

-- 0b. Task 015: the Devourer's pets (hunter-style: tamed beasts, stabled ones too) go with the class; a warrior
--     cannot keep them. Before the class is changed, while the owners can still be found.
DELETE `d` FROM `character_pet_declinedname` AS `d` JOIN `character_pet` AS `cp` ON `cp`.`id` = `d`.`id`
  JOIN `characters` AS `c` ON `c`.`guid` = `cp`.`owner` WHERE `c`.`class` = 10;
DELETE `x` FROM `pet_aura` AS `x` JOIN `character_pet` AS `cp` ON `cp`.`id` = `x`.`guid`
  JOIN `characters` AS `c` ON `c`.`guid` = `cp`.`owner` WHERE `c`.`class` = 10;
DELETE `x` FROM `pet_spell` AS `x` JOIN `character_pet` AS `cp` ON `cp`.`id` = `x`.`guid`
  JOIN `characters` AS `c` ON `c`.`guid` = `cp`.`owner` WHERE `c`.`class` = 10;
DELETE `x` FROM `pet_spell_cooldown` AS `x` JOIN `character_pet` AS `cp` ON `cp`.`id` = `x`.`guid`
  JOIN `characters` AS `c` ON `c`.`guid` = `cp`.`owner` WHERE `c`.`class` = 10;
DELETE `cp` FROM `character_pet` AS `cp` JOIN `characters` AS `c` ON `c`.`guid` = `cp`.`owner` WHERE `c`.`class` = 10;

-- 1. Devourers become warriors.
UPDATE `characters` SET `class` = 1, `at_login` = `at_login` | 0x02 | 0x04   -- AT_LOGIN_RESET_SPELLS, _RESET_TALENTS
 WHERE `class` = 10;

-- 2. Nothing of the Devourer's spells, talents, auras, cooldowns or buttons stays behind (spells 9100000-9101099).
--    (The stock pet spells it learned, Tame Beast and the rest, go with the reset of spells at the next login.)
DELETE FROM `character_talent`         WHERE `spell` BETWEEN 9100000 AND 9101099;
DELETE FROM `character_spell`          WHERE `spell` BETWEEN 9100000 AND 9101099;
DELETE FROM `character_aura`           WHERE `spell` BETWEEN 9100000 AND 9101099;
DELETE FROM `character_spell_cooldown` WHERE `spell` BETWEEN 9100000 AND 9101099;
DELETE FROM `character_action`         WHERE `type` = 0 AND `action` BETWEEN 9100000 AND 9101099;
DELETE FROM `character_skills`         WHERE `skill` BETWEEN 900 AND 902;       -- the Devourer's three spellbook tabs

-- 3. The idols (items 9100100, 9100101) disappear with their item template: from bags, bank and mail.
DELETE `ci` FROM `character_inventory` AS `ci`
  JOIN `item_instance` AS `ii` ON `ii`.`guid` = `ci`.`item`
 WHERE `ii`.`itemEntry` IN (9100100, 9100101);
DELETE `mi` FROM `mail_items` AS `mi`
  JOIN `item_instance` AS `ii` ON `ii`.`guid` = `mi`.`item_guid`
 WHERE `ii`.`itemEntry` IN (9100100, 9100101);
DELETE FROM `item_instance` WHERE `itemEntry` IN (9100100, 9100101);

-- 4. The witch sisters' chores (quests 9101301-9101303, task 010) leave the quest logs.
DELETE FROM `character_queststatus`          WHERE `quest` BETWEEN 9101301 AND 9101303;
DELETE FROM `character_queststatus_rewarded` WHERE `quest` BETWEEN 9101301 AND 9101303;

-- 5. The module's own tables, last.
DROP TABLE IF EXISTS `character_devourer_inbetween`, `character_devourer_bar`, `character_devourer_task`,
    `character_devourer_growth`, `character_devourer_worn`, `character_devourer_skin`, `character_devourer_shape`;

-- 6. Forget that the install files ran, so a later reinstall runs them again.
DELETE FROM `updates` WHERE `name` IN ('2026_09_30_00_devourer_characters.sql', '2026_10_01_00_devourer_inbetween.sql');
