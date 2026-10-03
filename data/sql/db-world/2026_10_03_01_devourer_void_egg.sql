-- Task 019 A: the void egg a kill leaves in the voidcreeper line (src/DevourerVoid.cpp). Creature 9101103, a plain
-- summon the module puts where the creature fell: it cannot be attacked or selected, stands still, and is replaced by
-- a voidling hatchling after 3 sec. Cloned from the Hatchling's row like the other module creatures (04_devourer_world).
-- Removed by uninstall/world.sql (its creature_template and model ranges cover 9101103).
-- Run after 2026_09_30_04_devourer_world.sql. Safe to run again.
DELETE FROM `creature_template_model` WHERE `CreatureID` = 9101103;
DELETE FROM `creature_template` WHERE `entry` = 9101103;
CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 9101100;
UPDATE `devourer_tmp_ct` SET `entry` = 9101103, `name` = 'Void Egg', `type` = 10, `speed_walk` = 0, `speed_run` = 0,
    `unit_flags` = 33554434, `flags_extra` = 0, `MovementType` = 0;   -- NON_ATTACKABLE | NOT_SELECTABLE
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;
-- The look: the voidling's model, small, until the owner picks the stock egg display to use (change CreatureDisplayID).
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(9101103, 0, 994176, 0.35, 1, 0);
