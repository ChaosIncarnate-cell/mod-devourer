-- The Vashnik's Rising Serpents (creature 9101102) had walk and run speed 0, which makes the core log
-- "MoveSplineInitArgs::Validate: velocity > 0.01f" whenever something moves them. They keep normal speeds now and
-- stay put through creature_template_movement.Rooted instead. Safe to run again.
-- (2026_09_30_04_devourer_world.sql still writes speed 0; this file runs after it.)
UPDATE `creature_template` SET `speed_walk` = 1, `speed_run` = 1.14286 WHERE `entry` = 9101102;
DELETE FROM `creature_template_movement` WHERE `CreatureId` = 9101102;
INSERT INTO `creature_template_movement` (`CreatureId`, `Ground`, `Swim`, `Flight`, `Rooted`) VALUES (9101102, 1, 0, 0, 1);
