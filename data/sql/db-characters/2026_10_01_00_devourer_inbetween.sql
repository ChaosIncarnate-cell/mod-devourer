-- mod-devourer (task 010): where the witch sisters' ritual took a Devourer from, and when it may next go back to
-- the In-Between (.inbetween). Only the module reads it. Removed (dropped) by data/sql/uninstall/characters.sql.

CREATE TABLE IF NOT EXISTS `character_devourer_inbetween` (
    `guid` INT UNSIGNED NOT NULL,
    `map` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'where "Send me back" returns it to',
    `x` FLOAT NOT NULL DEFAULT 0,
    `y` FLOAT NOT NULL DEFAULT 0,
    `z` FLOAT NOT NULL DEFAULT 0,
    `o` FLOAT NOT NULL DEFAULT 0,
    `next_visit` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'unix time .inbetween opens again',
    PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
