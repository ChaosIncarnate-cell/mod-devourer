-- mod-devourer: the module's own world tables. Static data, refilled by the files after this one.
-- Removed (last) by data/sql/uninstall/world.sql.

-- One row per shape: its form spell, base look, the four abilities and the passive.
CREATE TABLE IF NOT EXISTS `devourer_shape` (
    `shape_id` INT UNSIGNED NOT NULL,
    `name` VARCHAR(64) NOT NULL,
    `form_spell` INT UNSIGNED NOT NULL COMMENT 'the spellbook spell that shifts into it',
    `display_id` INT UNSIGNED NOT NULL COMMENT 'base look',
    `scale` FLOAT NOT NULL DEFAULT 1,
    `spell_1` INT UNSIGNED NOT NULL DEFAULT 0,
    `spell_2` INT UNSIGNED NOT NULL DEFAULT 0,
    `spell_3` INT UNSIGNED NOT NULL DEFAULT 0,
    `spell_4` INT UNSIGNED NOT NULL DEFAULT 0,
    `passive` INT UNSIGNED NOT NULL DEFAULT 0,
    `brood_display` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'a Brood''s spawn while this shape is worn (pet model)',
    PRIMARY KEY (`shape_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Creatures whose corpse grants a shape (and, with display_id, one of its colourings).
CREATE TABLE IF NOT EXISTS `devourer_shape_source` (
    `creature_entry` INT UNSIGNED NOT NULL,
    `shape_id` INT UNSIGNED NOT NULL,
    `display_id` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'colouring granted, 0 = the base look',
    PRIMARY KEY (`creature_entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Named colourings: display -> shape. `.devour skin <name>` wears one.
CREATE TABLE IF NOT EXISTS `devourer_skin` (
    `display_id` INT UNSIGNED NOT NULL,
    `shape_id` INT UNSIGNED NOT NULL,
    `name` VARCHAR(32) NOT NULL COMMENT 'what .devour skin takes',
    `brood_display` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'a Brood''s hatchlings while it is worn; 0 = the shape''s',
    PRIMARY KEY (`display_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Growth: Bio Points per meal while a form is worn, by the meal's creature type (0 = anything else).
CREATE TABLE IF NOT EXISTS `devourer_diet` (
    `shape_id` INT UNSIGNED NOT NULL,
    `creature_type` TINYINT UNSIGNED NOT NULL COMMENT '0 = anything not listed',
    `bp` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`shape_id`, `creature_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Growth: which form evolves into which, with the Bio Points and level it needs.
CREATE TABLE IF NOT EXISTS `devourer_evolution` (
    `from_shape` INT UNSIGNED NOT NULL,
    `to_shape` INT UNSIGNED NOT NULL,
    `bp` INT UNSIGNED NOT NULL COMMENT 'Bio Points the from-form must have earned',
    `min_level` TINYINT UNSIGNED NOT NULL DEFAULT 1,
    PRIMARY KEY (`to_shape`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Growth: tasks done while wearing the from-form. kind 1 kill (value = creature type, 0 any), 2 be hit by
-- (value = school mask), 3 devour at least this rare (value = rarity multiplier), 4 devour a creature type.
CREATE TABLE IF NOT EXISTS `devourer_evolution_task` (
    `to_shape` INT UNSIGNED NOT NULL,
    `task_id` INT UNSIGNED NOT NULL,
    `kind` TINYINT UNSIGNED NOT NULL,
    `value` INT UNSIGNED NOT NULL DEFAULT 0,
    `count` INT UNSIGNED NOT NULL DEFAULT 1,
    `text` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`to_shape`, `task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
