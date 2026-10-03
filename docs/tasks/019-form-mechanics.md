# 019 — Form mechanics the kits left out (cloud task)

Status: open (2026-10-03). Owner: "Make this the clouds job if you can" — the code-only parts of the new form lines
go to a cloud session; models, client patch and restarts stay with the local session.
Builds on task 017 (`tools/evolved_kit.py`, `docs/tier2-kit.md`, `src/DevourerEvolved.cpp`) and task 018
(`tools/witch_sisters.py`, `docs/witch-sisters.md`). Branch from `task/017-tier2-evolutions`.

Rules: change the generators, never their SQL by hand, unless the generator needs a file you do not have
(`tools/evolved_kit.py` needs a stock 3.3.5a Spell.dbc): then edit the generator AND its committed SQL output the
same way, row for row. Keep spell ids inside a form's block (`sid(shape, slot)`, helpers in slots 6-9). No new
models, no client patch: only spells that reuse stock visuals. Write in the PR what the owner tests in game.

## A. Voidcreeper line (shapes 41-43): the brood mechanics

The pick ("Voidcreeper as its own Brood line") asked for more than the kits do today:

1. **Void Eggs** (Voidling, passive or proc): a kill made in a voidcreeper-line shape leaves a void egg (a short-lived
   gameobject or creature with the stock egg look) that hatches a voidling guardian a few seconds later. A Brood
   Devourer (spec 3) gets two. Reuse the Brood hatchling summon (`NpcHatchling`, `OnBroodHatched`, `TuneHatchling`
   in `src/Devourer.h` / the Brood code) so limits, despawn and AI stay the same; the hatchling wears the shape's
   `brood_display` (the voidling, display 994176).
2. **Feed the Swarm** (Voidcreeper): the voidlings devour corpses near them and grow (scale and damage up a step,
   a cap of 3 steps) for the rest of the fight.
3. **Broodmother's Call** (Broodmother, replaces "Call the Swarm" in slot 5 or becomes its effect): every voidling
   fixates on the Broodmother's target and, when it dies, explodes for Shadow damage around it.
Put the scripts in `src/DevourerEvolved.cpp` (or a new `src/DevourerVoid.cpp` registered in the loader).

## B. Proto-Drake (shape 36): the colouring picks the breath

Fire Breath (`sid(36, 4)`) uses Fire for every colouring today. Make the worn colouring pick the element: earth
looks (994155-994157, 994159) Nature, the storm look (994160) Nature with a short slow, the blue fire looks
(994161-994162) Frost with a slow, the red look (994158) Fire. A spell script on the breath that reads the
player's current display and casts one of four helper spells (slots 6-9) is enough.

## C. Witch chores part 2 (task 018 B, last bullet)

"A small repeatable chore per tier: Wren needs a reagent only a certain form can fetch (Bio Points as reward)."
Three daily quests at Wren, one per tier (starter forms, tier 2, tier 3), each asking for an item that only drops
for a Devourer wearing a form of that tier (loot condition on the form aura or a module hook), reward Bio Points via
the module. Generate them in `tools/witch_sisters.py` like the molt quests (quest ids from the free part of
9101301-9101399; check `Q_FIRST`/`Q_LAST` and what is taken).

Create branch `task/019-form-mechanics`, commit per part, push it, and open a pull request into
`task/017-tier2-evolutions` titled "Task 019: brood mechanics, proto-drake breaths, witch chores".
