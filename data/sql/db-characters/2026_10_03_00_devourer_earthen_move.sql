-- Task 017 (2026-10-03): the earth proto-drake looks (displays 994155-994159) moved from the Proto-Drake (shape 36)
-- to the Earthen Proto-Drake (shape 44). A Proto-Drake that owned or wore one of them goes back to its base look;
-- the Earthen Proto-Drake gives them again when it is unlocked (they come with that shape). Safe to run again.
DELETE FROM `character_devourer_skin` WHERE `shape_id` = 36 AND `display_id` BETWEEN 994155 AND 994159;
UPDATE `character_devourer_shape` SET `display_id` = 0 WHERE `shape_id` = 36 AND `display_id` BETWEEN 994155 AND 994159;
