-- mod-devourer (Copus55, 2026-09-28): where a Devourer keeps each shape's abilities on the action bars.
-- Only the Devourer reads it. Remove with: DROP TABLE IF EXISTS character_devourer_bar;
CREATE TABLE IF NOT EXISTS `character_devourer_bar` (
    `guid` INT UNSIGNED NOT NULL,
    `shape_id` INT UNSIGNED NOT NULL,
    `spell` INT UNSIGNED NOT NULL,
    `slot` TINYINT UNSIGNED NOT NULL COMMENT 'action button 0-143, 255 = taken off the bars',
    PRIMARY KEY (`guid`, `shape_id`, `spell`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
