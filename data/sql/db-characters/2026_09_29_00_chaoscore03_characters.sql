-- ChaosCore0.3 (Copus55, 2026-09-28): Devour Whole (9100020) is a Glutton talent now. Until 0.2 the module
-- handed it to every Glutton; a character that still knew it would look as if it had the talent for free.
-- It is taken away once here; a Glutton gets it back by taking the Devour Whole talent.
DELETE FROM `character_spell` WHERE `spell` = 9100020;
