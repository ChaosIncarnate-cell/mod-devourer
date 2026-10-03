# 017 — Evolutions for the forms we have: tier 2 of the canvas lines

Status: batch 1 written (2026-10-03, branch `task/017-tier2-evolutions`): `tools/evolved_kit.py` -> `2026_10_03_00_devourer_tier2.sql` + `docs/tier2-kit.md`, task kinds 7-12, gimmick scripts in `src/DevourerEvolved.cpp`. Not built, not in the client patch yet.
Source of the design: the owner's canvas "Canvas Evolutions for Devourer", Section 1 (Regional Race Starter Lines)
and its decided rules (2A/2B both unlockable, the second bought with Bio Points; any 1 of 3 tasks; canvas BP
multipliers). The canvas belongs to the owner: don't change it.

## What exists today (live world DB, 2026-10-03)

| Id | Form | Gained by | Evolves into |
|---|---|---|---|
| 1 | Sethrak | idol | Vashnik (3), 1000 BP, level 30 |
| 2 | Berserker | grows from Baby Berserker | nothing yet |
| 3 | Vashnik | grows from Sethrak | nothing yet |
| 4 | Baby Berserker | CoA | Berserker (2), 600 BP, level 20 |
| 5 | Wolf | any wolf (Northshire) | nothing yet |
| 6 | Trogg | Rockjaw Trogg (Coldridge) | nothing yet |
| 7 | Saber | any cat (Shadowglen) | nothing yet |
| 8 | Moth | any moth (Ammen Vale) | nothing yet |
| 9 | Boar | any boar (Valley of Trials) | nothing yet |
| 10 | Plainstrider | Plainstrider (Mulgore) | nothing yet |
| 11 | Bat | Duskbat (Deathknell) | nothing yet |
| 12 | Mana Wyrm | Mana Wyrm (Sunstrider Isle) | nothing yet |
| 13 | Warp Stalker | witch sisters' ritual, any warp stalker | nothing yet |
| 14 | Biletoad | Wren's chore | Giant Marsh Frog (15), 550 BP, level 14 |
| 15 | Giant Marsh Frog | grows from Biletoad | nothing yet |

(Twinfangs is not a form: it is the Vashnik's Rising Serpent summon look. Voidcreeper is a model in the model tool,
not a form.)

## Proposal: every form we have gets its canvas evolutions

Every creature below exists in our world DB and is placed (checked 2026-10-03: entry, display, spawns).

### Batch 1 (build first): one tier-2 per line, the canvas "A" branch, plus the Warp Stalker's

| From | Tier 2 | Creature (entry / display) | Level, BP | Role |
|---|---|---|---|---|
| Plainstrider | Greater Plainstrider | 3244 / 178 | 12, 500 | bleed skirmisher |
| Wolf | Bloodsnout Worg | 1923 / 741 | 14, 550 | flanking assassin |
| Boar | Raging Agam'ar | 4514 / 2453 | 12, 500 | stun tank |
| Saber | Shadowclaw | 2175 / 3030 | 14, 550 | silencing assassin |
| Trogg | Rockjaw Backbreaker | 1118 / 723 | 12, 500 | armor tank, cleave |
| Bat | Vampiric Duskbat | 1554 / 8808 | 14, 550 | leech, silence |
| Mana Wyrm | Arcane Wraith | 15273 / 15438 | 14, 550 | buff-stealing caster |
| Moth | Royal Blue Flutterer | 17350 / 17711 | 12, 500 | sleep/root controller |
| Warp Stalker | Void Terror | 19980 / 19368 | 16, 600 | shadow DoT controller |

### Batch 2: the "B" branches (the second choice, bought with Bio Points in the menu)

Plainstrider → Bloodtalon Scythemaw (raptor) · Wolf → Black Bear Patriarch · Boar → Venomtail Scorpid ·
Saber → Frostsaber Pride Watcher · Trogg → Irradiated Pillager · Bat → Rotten Ghoul · Mana Wyrm → Crazed
Dragonhawk · Moth → Talbuk Stag.

### Batch 3: tier 3 and the forms outside the canvas

- The canvas tier-3 forms of each line (Lupos, Ursius, Agathelos, King Mosh, Netherspite, Al'ar, Patchwerk ...),
  the Giant Marsh Frog → Huge Toad, Void Terror → Dimensius.
- Berserker → Devourer Worldeater: on the canvas's "To design" list, no model yet.
- Vashnik: no next stage on the canvas. Proposal: leave it until the Ascending port's Vashnik caster model is in.

### New lines (after batch 1, or in parallel if wanted)

- Strigid Owl (Teldrassil, a new starter) → Moonkin → Moontouched Owlbeast.
- Felstalker (Durotar, demon line) → Felhound → Brutallus.

## What batch 1 needs on the server

1. **New task kinds** for the canvas options: devour a creature family (worgs, crocolisks), devour one named
   creature (Mazzranache, Grik'nir), deal an amount of damage of a school, take an amount of damage. Options the
   game cannot count cheaply (run 2,000 yards) become "land N hits with <the form's ability>" (kind 6).
2. **Spell range** for evolved forms: 9102000-9102999 (shape s: 9102000 + (s - 16) x 10 + slot), uninstall
   extended. The old 9100000-9101099 range is full.
3. **Kits**: like the starters (`tools/start_kit.py`), a new `tools/evolved_kit.py`: 4 abilities + the gimmick,
   cloned from stock 3.3.5 spells, numbers for levels 12-20. Each card's kit gets the same review as task 009
   (one job per button, no taunts, Anima instead of mana, levels that play).
4. **Shapes 16-24**, their evolutions (`any_task = 1`), diets, favourite foods.
5. The client patch (`patch-Z`) has to be rebuilt for the new spells. The "Port Ascending into Chromatica" thread
   is adding models to patch-Z at the same time: rebuild only after checking with it, back up first.
   2026-10-03: the Skrill mount thread has a staged patch-Z (two creature tables changed, creature 9300101) and a
   new patch-Y waiting for the owner's OK: before rebuilding patch-Z, compare with the live file and keep their rows.

## Done when (tested in game)
1. A level-14 Wolf with 550 BP that devoured 30 humanoids becomes a Bloodsnout Worg; the Wolf stays available.
2. `.devour` / the menu shows the growth progress of each line ("any one of").
3. The nine kits play at levels 12-20; no server log errors; uninstall covers the new rows.
