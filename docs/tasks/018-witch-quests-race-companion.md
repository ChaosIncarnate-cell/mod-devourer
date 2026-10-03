# 018 — Witch quests for the evolutions, the mount race, and the witches' companion

Status: proposal (2026-10-03). Owner's asks (project chat, 2026-10-03): "We will need some new quests, for the new
forms, and some more interactions with the witches." · "also to add a bot character that is connected to the
witches." · "Add a quest where you and a companion need to win a race, with companion on devourers back (devourer is
mount, transformed by witch, companion sits on them)". Standing rule: completely new systems also get a WarcraftXL
extension where possible.
Builds on task 010 (the Hollowmoor sisters, `docs/witch-sisters.md`) and task 017 (the tier-2 forms).

## A. The molt quests (one per tier-2 form)

Today a form evolves by itself the moment its Bio Points, level and one task are done. Proposal: the sisters turn
that moment into a scene.

1. When a worn form reaches the level and Bio Points of its evolution, Wren whispers: "Your wolf smells *ready*,
   Snack. Come home." A quest appears at the sisters (offered through `.inbetween` until the proposed travel spell
   exists): **"The Molt: Bloodsnout Worg"** and so on, 9 quests (ids 9101310-9101318).
2. Objective: the evolution's "any one" task, shown in the quest log and completed by the module when that task is
   done (the tasks stay data in `devourer_evolution_task`).
3. Turn-in at the cauldron: Hagatha tells a short tale of the creature (one per form, her folklore voice), Wren
   chants, the old body tears open and the new one crawls out. The evolution happens at the turn-in instead of
   automatically (`devourer_evolution.quest`; evolutions without a quest still grow by themselves).

## B. More witch scenes

- Wren reacts to the shape you come back in (a gossip line per shape: "A worg! Sit! ...no? Fine.").
- Hagatha's lantern: ask her about any form you own and she tells its tale (the same tales as the molt quests).
- A small repeatable chore per tier: Wren needs a reagent only a certain form can fetch (Bio Points as reward).

## C. The race: "Wren's Derby"

- Wren turns the Devourer into a two-seat mount (a big beast model; the Devourer drives, a companion rides on its
  back). The companion is the witches' companion (D) or any party member.
- A course of checkpoints in an outdoor zone (proposal: the Mulgore plains, low level, wide and open), against
  Hagatha on her broom flying the course on waypoints. Win = reach the last checkpoint first; reward: a colouring
  for the race mount shape and Bio Points.
- How: the mount body is a server transform plus a vehicle kit on the player (aura "set vehicle id", a vehicle
  with a passenger seat); the companion boards with the stock "ride vehicle" spell. To check first: that this fork
  lets a player carry a passenger this way (the core has the aura; WotLK used it for player vehicles).
- WarcraftXL: a small `wxl-race` extension for the race HUD (checkpoint arrow, timer, standings), reusable for
  other races later.

## D. The witches' companion

- A bot character the sisters send with the Devourer: proposal "Bramble", Wren's apprentice (a goblin or gnome
  witch-in-training), with its own character card in mod-llm-party so it talks in character about the sisters and
  the In-Between.
- Introduced by a quest ("Wren's Apprentice"); joins the party as an addclass playerbot; rides in the race.
- To decide: one Bramble for the whole server or one per Devourer (bot names are unique server-wide).

## Order proposed

A (needs only the module and SQL) → B → D (the companion) → C (needs D and the vehicle check).
