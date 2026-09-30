# 006 — Class kit, leather and trainers (levels 1-20)

Status: open
Base: branch `integration`. Branch: `task/006-class-kit-and-trainers`. Read `docs/starting-experience.md` first.

## Goal
A new Devourer plays like a classic class from level 1: true-form abilities, learned from trainers every 2 levels,
leather armour, fitting weapons, starting gear and action bars.

## Scope
- **Armour/weapons**: replace the warrior's skills from task 003 (mail, shields, swords, axes ...) with leather and
  the weapons in the design (`playercreateinfo_skills`, the SkillRaceClassInfo rows written by
  `tools/build_class_dbc_sql.py`, so the client agrees). Keep the class's power type rage (Hunger).
- **Starting outfit** per race: leather (take the rogue's or druid's starting armour of that race) plus a fitting
  starting weapon, via the CharStartOutfit path in `build_class_dbc_sql.py` (client + server stay identical).
- **True-form abilities** levels 1-20 (draft names and ideas in the design; final numbers are yours, kept modest,
  WotLK-like for those levels): Gnash (1), Rend Flesh (4), Hunger Pangs (6), Unnerving Snarl (8), then every 2 levels a
  new rank or ability up to 20 (placeholders allowed from 12 on, marked "(placeholder)"). Spells in a free part of
  9100000-9100899 (task 005 uses 9100500-9100808; take e.g. 9100810-9100899 and document it in `docs/talents.md`).
- **Trainers**: one "Devourer Trainer" NPC per starting zone (Northshire, Coldridge Valley, Shadowglen, Ammen Vale,
  Valley of Trials, Camp Narache, Deathknell, Sunstrider Isle) and per capital (Stormwind, Ironforge, Darnassus,
  Exodar, Orgrimmar, Thunder Bluff, Undercity, Silvermoon), placed near the other class trainers, right faction,
  class trainer for class 10 (use this fork's trainer tables: check `trainer`, `trainer_spell`,
  `creature_default_trainer` or whatever the Playerbot branch uses). Costs like other classes at those levels.
  Creature entries in 9101200-9101299, spawns with their own guid range; add both to the uninstall.
- **Action bars** at creation: Attack, Gnash, Devour.
- Remove the level-1 "Idol of the Sethrak" from new characters if task 003 gives it (the Sethrak stays reachable at
  its level through its idol/camp).

## Done when (local session tests in game)
1. Create a Devourer of any race: leather gear, a weapon, Gnash + Devour on the bars, no Lua errors.
2. `.levelup 3`: the trainer in the starting zone offers Rend Flesh at 4 (greyed until then) and teaches it for coin.
3. Mail and shields can't be equipped; leather can.
4. Uninstall + install: DB identical, as in task 003.
