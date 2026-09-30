-- mod-devourer: what a Devourer has eaten, wears and has grown into. Only the module reads these tables.
-- Removed (last) by data/sql/uninstall/characters.sql.

CREATE TABLE IF NOT EXISTS `character_devourer_shape` (
    `guid` INT UNSIGNED NOT NULL,
    `shape_id` INT UNSIGNED NOT NULL,
    `eaten` INT UNSIGNED NOT NULL DEFAULT 0,
    `display_id` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'chosen colouring, 0 = the shape''s base look',
    PRIMARY KEY (`guid`, `shape_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `character_devourer_skin` (
    `guid` INT UNSIGNED NOT NULL,
    `shape_id` INT UNSIGNED NOT NULL,
    `display_id` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`guid`, `shape_id`, `display_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `character_devourer_worn` (
    `guid` INT UNSIGNED NOT NULL,
    `shape_id` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'shape worn at logout, 0 = own body',
    PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Growth: Bio Points per form, and evolution task progress.
CREATE TABLE IF NOT EXISTS `character_devourer_growth` (
    `guid` INT UNSIGNED NOT NULL,
    `shape_id` INT UNSIGNED NOT NULL,
    `bp` INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`guid`, `shape_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `character_devourer_task` (
    `guid` INT UNSIGNED NOT NULL,
    `to_shape` INT UNSIGNED NOT NULL,
    `task_id` INT UNSIGNED NOT NULL,
    `progress` INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`guid`, `to_shape`, `task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Where a Devourer keeps each shape's abilities on the action bars.
CREATE TABLE IF NOT EXISTS `character_devourer_bar` (
    `guid` INT UNSIGNED NOT NULL,
    `shape_id` INT UNSIGNED NOT NULL,
    `spell` INT UNSIGNED NOT NULL,
    `slot` TINYINT UNSIGNED NOT NULL COMMENT 'action button 0-143, 255 = taken off the bars',
    PRIMARY KEY (`guid`, `shape_id`, `spell`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
