# 010 — The witch sisters: the Devourer's trainers and its level-5 intro (Baby Berserker)

Status: open. Base: branch `task/006-007-devourer-start`. Branch: `task/010-witch-sisters`.
Owner's rule: build only what is asked here; anything else goes into the PR text as a proposal.

## Owner's words (2026-10-01)
Canvas note: "Make the class trainers a duo of two crazy Witches, one themed about the chosen folklore, monstrosity
theme, and the other being a crazy person, too much into the fact of giving the player tasks, while turning them
into animals -> quests custom." Only for the Devourer class (other classes keep their trainers).
"Make Baby Berserker be able to be obtained by the 'Crazy Witch' through a 'kidnapping quest' where you get
kidnapped, transformed and first meet the sisters." Answers: **at level 5**, "you will be summoned through a ritual,
and be caged"; the place: **the In-Between**. Names and personalities: Obsidian note "Devourer Witch Sisters.md",
the owner **chose (2026-10-01): the Hollowmoor sisters** (names defined in one place, so renaming stays one change):

- **Hagatha Hollowmoor** (the folklore sister): a hunched crone with a lantern of trapped anima, a collector of
  monster tales; calm, ominous, every sentence sounds like a warning. Feared in village stories ("Hagatha takes the
  children who don't come home"). She keeps the stories of every monster that crawled out of the In-Between and
  treats the Devourer as one of them: "my little horror" or "the hungry thing in the dark". Teaches the dark side:
  what you are, what you may become.
- **Wren Hollowmoor** (the task sister): the younger sister, wild-eyed, half feather, half girl from her own failed
  spells; obsessed with "tasks" and "lessons", sends the Devourer out with lists, cheers loudly at every
  transformation, sulks when you come back empty-handed. Laughs at her own jokes, has a list of chores that never
  ends, cages everywhere, nicknames for everyone ("Snack", "Fluffy", "Project #9"); her tasks are absurd and specific.
  She is the one who summons the Devourer and turns it into the Baby Berserker.

These are the owner's descriptions: write their lines in these voices (marked placeholders are fine where unsure).

## Scope
- **The In-Between:** a small place on an existing map nobody uses (no new client map), dark and void-like, with the
  sisters, a cage and their trappings (existing game objects). Name the map and coordinates in the PR.
- **Level 5, the ritual:** when a Devourer reaches level 5 (or logs in at 5+ without having done it), a ritual
  summons it: a short visual, teleport to the In-Between, it wakes **caged**. The sisters talk (Hagatha:
  ominous folklore; Wren: manic, chores, turning people into animals). Placeholder texts allowed, marked.
- **Transformation:** Wren turns the Devourer into a **Baby Berserker**: unlock shape 4 (+ its base
  colouring) through the module (`Mgr::Unlock`, shift now). Then a short custom quest chain (2-3 small tasks in the
  In-Between, Wren's style); at its end the cage opens and both sisters become the Devourer's trainers.
- **Trainers:** the two sisters are the Devourer's class trainers (`trainer` / `trainer_spell` like the current
  Devourer Trainer 9101200, class 10 only). The 16 placeholder Devourer Trainers in starting zones and capitals go
  (the owner disliked them): remove them and their uninstall lines. The Devourer needs a way back to the sisters
  later (e.g. a "Return to the In-Between" spell or item with a long cooldown, and back to where it came from):
  propose it in the PR before building anything bigger.
- Removable: creatures, quests, gossip and spawns in the module's id ranges, all in the uninstall.
- The Baby Berserker's other sources (Voidstorm Whelps) stay as they are.

## Done when (local session tests in game)
1. A level-4 Devourer gains a level: summoned, caged, meets both sisters, becomes a Baby Berserker.
2. The small quests can be done; the cage opens; the sisters train it (Devourer only; other classes are sent away).
3. The way back works; the old 16 trainers are gone; uninstall + install leaves the DB identical.
