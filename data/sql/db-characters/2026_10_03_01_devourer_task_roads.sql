-- Multi-branch evolution (owner, 2026-10-03): several forms can grow into the same form, and each road counts its own
-- tasks. Task progress is keyed by the road (from_shape, to_shape). Rows from before this keep from_shape 0: the
-- module reads them as the road that existed then (each form had one parent), and saves them under it from then on.
-- Safe to run again.
SET @devourer_col := (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'character_devourer_task' AND COLUMN_NAME = 'from_shape');
SET @devourer_sql := IF(@devourer_col = 0, 'ALTER TABLE `character_devourer_task` ADD COLUMN `from_shape` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT ''the form it grows out of (0 = from before the roads)'' AFTER `guid`, DROP PRIMARY KEY, ADD PRIMARY KEY (`guid`, `from_shape`, `to_shape`, `task_id`)', 'DO 0');
PREPARE devourer_stmt FROM @devourer_sql;
EXECUTE devourer_stmt;
DEALLOCATE PREPARE devourer_stmt;
