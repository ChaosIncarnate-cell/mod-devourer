-- The frog line (owner, 2026-10-02, Parrot\to be devoured.canvas): the Giant Marsh Frog (shape 15) grows out of the
-- Biletoad (shape 14, from Wren's chore "Pests in the Cells"). The shapes and their spells: tools/start_kit.py
-- (2026_09_30_08); Wren's chore: tools/witch_sisters.py (2026_10_01_00). Safe to run again.
-- Note: 2026_09_30_04_devourer_world.sql clears devourer_evolution(_task) when it runs; run this file after it.

-- Growth may ask for any one of its tasks instead of all of them; a task may match the meal's name.
SET @devourer_col := (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'devourer_evolution' AND COLUMN_NAME = 'any_task');
SET @devourer_sql := IF(@devourer_col = 0, 'ALTER TABLE `devourer_evolution` ADD COLUMN `any_task` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT ''1 = any one task is enough, 0 = all of them''', 'DO 0');
PREPARE devourer_stmt FROM @devourer_sql;
EXECUTE devourer_stmt;
DEALLOCATE PREPARE devourer_stmt;
SET @devourer_col := (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'devourer_evolution_task' AND COLUMN_NAME = 'name_part');
SET @devourer_sql := IF(@devourer_col = 0, 'ALTER TABLE `devourer_evolution_task` ADD COLUMN `name_part` VARCHAR(100) NOT NULL DEFAULT '''' COMMENT ''kind 5: the meal''''s name holds one of these (|-separated)''', 'DO 0');
PREPARE devourer_stmt FROM @devourer_sql;
EXECUTE devourer_stmt;
DEALLOCATE PREPARE devourer_stmt;

-- Biletoad -> Giant Marsh Frog: 550 Bio Points, level 14, any one task (kind 5 devour by name, 6 hit with a spell:
-- 9101012 Tongue Pull, 9101017 Swamp Hop's knock-down).
DELETE FROM `devourer_evolution` WHERE `to_shape` = 15;
INSERT INTO `devourer_evolution` (`from_shape`, `to_shape`, `bp`, `min_level`, `any_task`) VALUES
(14, 15, 550, 14, 1);
DELETE FROM `devourer_evolution_task` WHERE `to_shape` = 15;
INSERT INTO `devourer_evolution_task` (`to_shape`, `task_id`, `kind`, `value`, `count`, `text`, `name_part`) VALUES
(15, 1, 5, 0, 30, 'Devour murlocs or swamp beasts as a Biletoad', 'murloc|swamp|bog|marsh |mire'),
(15, 2, 6, 9101012, 40, 'Pull enemies with Tongue Pull', ''),
(15, 3, 6, 9101017, 25, 'Knock enemies down with Swamp Hop', '');
