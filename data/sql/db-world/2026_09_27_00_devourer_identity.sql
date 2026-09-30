-- mod-devourer: class 20 is the Devourer. Removes what the old class (Son of Arugal / Bloodmage) left in the
-- world database. Basic mechanics every class gets (auto attack, dodge, block, weapon and armour skills,
-- Hit Rating) and the starter gear stay until the Devourer has its own kit.

-- The old class's abilities by level.
DELETE FROM `ascension_custom_class_spell` WHERE `class` = 20;

-- Old abilities new characters of class 20 started with: Bloodmoon Blast, Resilient Constitution, Sanguine Mend.
DELETE FROM `playercreateinfo_spell_custom`
 WHERE `racemask` = 0 AND `classmask` = 524288 AND `Spell` IN (500125, 552011, 802310);
