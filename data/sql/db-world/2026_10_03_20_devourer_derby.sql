-- mod-devourer task 020: Wren's Derby, the witch races (src/DevourerDerby.cpp, src/DevourerDerbyIds.h).
-- Three races in the Barrens for a level-20 Devourer and its companion. Ids: 9101360-9101379 (quests, creatures,
-- gossip, npc_text, gameobjects), spawn guids 9910300-9910349. Safe to run again.
--
-- Needs, from other threads (the quests still load without them, the server only logs the missing parts):
--   Items and balance: reward items 9104000-9104004 (goggles, cloak, beetle, toffee, Kakapo reins).
--   Devourer thread: the Derby Beast's own display (Primal Tallstrider with its saddle shown) for creature 9101362,
--   and the Wren's Saddle spell (DevourerDerbyIds.h SpellWrensSaddle).
--   The sisters' SQL must keep to 9101300-9101359 (tools/witch_sisters.py Q_LAST, commit b55066f on task/017).

DELETE FROM `creature` WHERE `guid` BETWEEN 9910300 AND 9910349;
DELETE FROM `creature_template_addon` WHERE `entry` BETWEEN 9101360 AND 9101379;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9101360 AND 9101379;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9101360 AND 9101379;
DELETE FROM `creature_text` WHERE `CreatureID` BETWEEN 9101360 AND 9101379;
DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 9101360 AND 9101379;
DELETE FROM `creature_queststarter` WHERE `quest` BETWEEN 9101360 AND 9101379;
DELETE FROM `creature_questender` WHERE `quest` BETWEEN 9101360 AND 9101379;
DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN 9101360 AND 9101379;
DELETE FROM `quest_request_items` WHERE `ID` BETWEEN 9101360 AND 9101379;
DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN 9101360 AND 9101379;
DELETE FROM `quest_template` WHERE `ID` BETWEEN 9101360 AND 9101379;
DELETE FROM `gossip_menu_option` WHERE `MenuID` BETWEEN 9101360 AND 9101379;
DELETE FROM `gossip_menu` WHERE `MenuID` BETWEEN 9101360 AND 9101379;
DELETE FROM `npc_text` WHERE `ID` BETWEEN 9101360 AND 9101379;

-- --- creatures --------------------------------------------------------------------------------------------------
-- Copies of stock creatures, like the sisters' (Wren: Windfury Wind Witch 2963; Hagatha: Myranda the Hag 11872;
-- the Derby Beast: Greater Plainstrider 3244 until the Devourer thread's Primal Tallstrider display exists).
DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;
CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 2963;
UPDATE `devourer_tmp_ct` SET `entry` = 9101360, `name` = 'Wren Hollowmoor', `subname` = 'Derby Bookmaker',
    `minlevel` = 80, `maxlevel` = 80, `faction` = 35, `npcflag` = 3, `unit_flags` = 768, `gossip_menu_id` = 9101360,
    `AIName` = '', `ScriptName` = 'npc_devourer_derby_wren', `lootid` = 0, `KillCredit1` = 0, `KillCredit2` = 0,
    `MovementType` = 0, `VerifiedBuild` = 0;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;

CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 11872;
UPDATE `devourer_tmp_ct` SET `entry` = 9101361, `name` = 'Hagatha Hollowmoor', `subname` = '',
    `minlevel` = 80, `maxlevel` = 80, `faction` = 35, `npcflag` = 0, `unit_flags` = 768, `gossip_menu_id` = 0,
    `AIName` = '', `ScriptName` = 'npc_devourer_derby_hagatha', `lootid` = 0, `KillCredit1` = 0, `KillCredit2` = 0,
    `MovementType` = 0, `VerifiedBuild` = 0;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;

CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 3244;
UPDATE `devourer_tmp_ct` SET `entry` = 9101362, `name` = 'Derby Beast', `subname` = '', `faction` = 35,
    `npcflag` = 0, `gossip_menu_id` = 0, `AIName` = '', `ScriptName` = '', `lootid` = 0, `KillCredit1` = 0,
    `KillCredit2` = 0, `VerifiedBuild` = 0;
INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;
DROP TEMPORARY TABLE `devourer_tmp_ct`;

INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`)
SELECT `m`.`entry`, 0, `ctm`.`CreatureDisplayID`, `ctm`.`DisplayScale`, 1, 0 FROM (
    SELECT 9101360 AS `entry`, 2963 AS `looks` UNION ALL SELECT 9101361, 11872 UNION ALL SELECT 9101362, 3244
) AS `m` JOIN `creature_template_model` AS `ctm` ON `ctm`.`CreatureID` = `m`.`looks` AND `ctm`.`Idx` = 0;

-- Hagatha rides the Kakapo (creature 9301049's look, display 980033; owner: "Kakapo will be the mount").
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES
(9101361, 0, 980033, 0, 1, 0, 0, '');

-- Wren at the starting line: the Barrens, on the savanna west of the Crossroads.
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(9910300, 9101360, 1, 1, 1, -796.0, -2636.0, 93.6, 3.6, 300, 0, 0, 'mod-devourer: Wren Hollowmoor, Wren''s Derby');

-- A checkpoint: a witch-fire (the sisters' ritual brazier look).
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`, `unk1`, `size`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES
(9101360, 5, 197, 'Witch-fire', '', '', '', 1.5, '', '', 0);

-- --- Wren's gossip ------------------------------------------------------------------------------------------------
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(9101360, 'Snack! You came! Hagatha''s been polishing that bird all morning. Ready when you are. Bring somebody to sit on you, or it doesn''t count.', 'Snack! You came! Hagatha''s been polishing that bird all morning. Ready when you are. Bring somebody to sit on you, or it doesn''t count.', 1);
INSERT INTO `gossip_menu` (`MenuID`, `TextID`) VALUES (9101360, 9101360);
INSERT INTO `gossip_menu_option` (`MenuID`, `OptionID`, `OptionIcon`, `OptionText`, `OptionBroadcastTextID`, `OptionType`, `OptionNpcFlag`, `ActionMenuID`, `ActionPoiID`, `BoxCoded`, `BoxMoney`, `BoxText`, `BoxBroadcastTextID`, `VerifiedBuild`) VALUES
(9101360, 0, 0, 'I''m ready. Let''s race!', 0, 1, 1, 0, 0, 0, 0, '', 0, 0);

-- --- the races ----------------------------------------------------------------------------------------------------
-- Won by the script (an "event happens" objective). Class 10 only (AllowableClasses 512).
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `QuestInfoID`, `RewardNextQuest`, `RewardXPDifficulty`, `RewardMoney`, `Flags`, `AllowableRaces`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `ObjectiveText1`, `VerifiedBuild`) VALUES
(9101360, 2, 20, 20, 17, 0, 0, 5, 2500, 0, 0, 9104000, 1, 0, 0, 'Wren''s Derby',
 'Meet Wren at the starting line west of the Crossroads in the Barrens and win her race with a companion on your back.',
 'Snack! Big news. I told Hagatha you could beat her Kakapo in a race. She laughed. She laughed for a LONG time. So now it''s a bet, and if we lose I have to clean the cauldron. With my hands.$B$BGo to the Barrens, the grass west of the Crossroads. I''ll meet you at the starting line and do the rest. Bring Bramble, she knows the way. She says she does.',
 '', 'Return to Wren Hollowmoor at the starting line.', 'Win Wren''s Derby', 0),
(9101361, 2, 20, 20, 17, 0, 0, 5, 500, 0, 0, 9104001, 1, 9104003, 3, 'Hagatha Wants a Rematch',
 'Win the second race against Hagatha, through the shallows of Lushwater Oasis, with a companion on your back.',
 'Hagatha wants a rematch. She ALWAYS wants a rematch. This time the course goes through the oasis, because she says her bird "has never once been afraid of water". The bird looked afraid of water.$B$BSame rules: somebody on your back, and get to the last fire before she does.',
 '', 'Return to Wren Hollowmoor at the starting line.', 'Win the rematch', 0),
(9101362, 2, 20, 20, 17, 0, 0, 5, 1000, 0, 0, 9104002, 1, 9104004, 1, 'The Last Lap',
 'Win the full course against Hagatha, with a companion on your back.',
 'One more, Snack. The whole course this time, all the way round. Hagatha says if she loses this one she''ll give you the bird.$B$BShe doesn''t think she''ll lose. I think she''s already sad about it.',
 '', 'Return to Wren Hollowmoor at the starting line.', 'Win the last lap', 0);

INSERT INTO `quest_template_addon` (`ID`, `AllowableClasses`, `PrevQuestID`, `SpecialFlags`) VALUES
(9101360, 512, 9101305, 2),
(9101361, 512, 9101360, 2),
(9101362, 512, 9101361, 2);

INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`, `VerifiedBuild`) VALUES
(9101360, 1, 1, 'Hagatha is already polishing her bird. Back to the line, Snack!', 0),
(9101361, 1, 1, 'She''s doing stretches. Birds don''t do stretches. Go on!', 0),
(9101362, 1, 1, 'The whole course, Snack. Every fire.', 0);

INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(9101360, 4, 'WE WON! Hagatha, the cauldron is yours! Both hands!$B$BSnack, you were magnificent. And you know what that means: you can ride now. Real riding, on real mounts. And when you want to carry a friend, you know the saddle trick. Bramble, stop waving, it''s over.', 0),
(9101361, 4, 'Two for two! Listen. Hear that muttering? That''s Hagatha. It''s the best sound in the world.$B$BHere, something warm for the road, and some of her toffee. Don''t eat it all at once. Don''t ask what''s in it.', 0),
(9101362, 4, 'THREE! A bet''s a bet, Hagatha. Hand over the bird.$B$BShe''s yours, Snack. Feed her twice a day and never at midnight. And Bramble gets the beetle, because she says it''s lucky and I''m not arguing with her today.', 0);

INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(9101301, 9101360),                                -- Wren in the In-Between sends it to the races
(9101360, 9101361), (9101360, 9101362);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(9101360, 9101360), (9101360, 9101361), (9101360, 9101362);

-- --- lines --------------------------------------------------------------------------------------------------------
-- Wren whispers (type 15: she reaches the Devourer anywhere on the course); Hagatha says (type 12).
INSERT INTO `creature_text` (`CreatureID`, `GroupID`, `ID`, `Text`, `Type`, `Language`, `Probability`, `Emote`, `Duration`, `Sound`, `BroadcastTextId`, `TextRange`, `comment`) VALUES
(9101360, 0, 0, 'Hagatha! Your challenger is here! Snack, hold still. This tickles.', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: challenger'),
(9101360, 1, 0, 'Legs, feathers, a saddle... and done! Up you get, rider!', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: transform'),
(9101360, 2, 0, 'On your marks! Follow the fires, Snack!', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: marks'),
(9101360, 3, 0, 'WE WON! Come back to the line, Snack, I have to see Hagatha''s face up close!', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: won race 1'),
(9101360, 4, 0, 'Oh, Snack. She''s never going to let me forget that. Again! Talk to me when you''re ready.', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: lost'),
(9101360, 5, 0, 'You dropped your rider! That doesn''t count, Snack. Again!', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: rider fell off'),
(9101360, 6, 0, 'You need somebody on your back, Snack. Where''s Bramble? Bring her, or any friend from your party.', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: no rider'),
(9101360, 7, 0, 'Sign-ups are open, Snack, but you''re not signed up. Ask me in the In-Between first. Or win the last one first.', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: no race quest'),
(9101360, 8, 0, 'Two for two! Hagatha is muttering. Come and hear it!', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: won race 2'),
(9101360, 9, 0, 'THREE! Come back, Snack, Hagatha has something to hand over!', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: won race 3'),
(9101360, 10, 0, 'Snack, the course is THIS way! Back to the line!', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: off the course'),
(9101360, 11, 0, 'Not now, Snack. Catch your breath, come to the line, and get off whatever you''re sitting on.', 15, 0, 100, 0, 0, 0, 0, 0, 'Wren derby: not ready'),
(9101361, 0, 0, 'So this is the beast that will beat me? It has a passenger. How sweet.', 12, 0, 100, 0, 0, 0, 0, 0, 'Hagatha derby: arrives'),
(9101361, 1, 0, 'Try to keep up, little horror!', 12, 0, 100, 0, 0, 0, 0, 0, 'Hagatha derby: go'),
(9101361, 2, 0, 'Ha! The old bird still has it.', 12, 0, 100, 0, 0, 0, 0, 0, 'Hagatha derby: she wins'),
(9101361, 3, 0, 'Bah. The bird had a cramp.', 12, 0, 100, 0, 0, 0, 0, 0, 'Hagatha derby: she loses'),
(9101361, 4, 0, 'Fine. FINE. The bird is yours, little horror. Wren will hand her over. I cannot watch.', 12, 0, 100, 0, 0, 0, 0, 0, 'Hagatha derby: loses the Kakapo');
