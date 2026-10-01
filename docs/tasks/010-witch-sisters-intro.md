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
the owner picks; until then use placeholder names `Witch Sister (Folklore)` / `Witch Sister (Tasks)`, defined in one
place so renaming is one change.

## Scope
- **The In-Between:** a small place on an existing map nobody uses (no new client map), dark and void-like, with the
  sisters, a cage and their trappings (existing game objects). Name the map and coordinates in the PR.
- **Level 5, the ritual:** when a Devourer reaches level 5 (or logs in at 5+ without having done it), a ritual
  summons it: a short visual, teleport to the In-Between, it wakes **caged**. The sisters talk (Folklore sister:
  ominous folklore; Tasks sister: manic, chores, turning people into animals). Placeholder texts allowed, marked.
- **Transformation:** the Tasks sister turns the Devourer into a **Baby Berserker**: unlock shape 4 (+ its base
  colouring) through the module (`Mgr::Unlock`, shift now). Then a short custom quest chain (2-3 small tasks in the
  In-Between, the Tasks sister's style); at its end the cage opens and both sisters become the Devourer's trainers.
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
