# 009 — Starter forms, first batch (Wolf, Saber, Boar, Moth): general kinds, canvas kits

Status: open. Base: branch `task/006-007-devourer-start`. Branch: `task/009-starter-forms-batch1`.
Read `CLAUDE.md`, `docs/design.md`, `docs/start-kit.md`, `tools/start_kit.py`.
**Source of the design:** the owner's Obsidian canvas "Canvas Evolutions for Devourer", Section 1 (Regional Race
Starter Lines); the four cards are summarised below. The canvas belongs to the owner/Canvas session: don't change it.
Owner's rule: build only what is asked; anything else goes into the PR text as a proposal.

## Owner's words (2026-10-01)
"The single forms should not be THAT specific, the 'Anima-Stalked Wolf' should be reworked into wolf, or allow many
many wolf-like creatures, to be overall less specific. Also go through the abilities and make changes to the
abilities that are weird, do not make sense, or you think might be better differently. Let's start with only a
first batch." Canvas prep decisions: names not too important; if a creature/model doesn't exist, take the most
fitting existing one. Favourite food gives 2x Bio Points for everyone, matched by creature type and family.

## 1. A form is a kind of creature
Today a starting form comes from one creature entry (+ listed colouring creatures) in `devourer_shape_source`.
New: a shape names a **creature family** (`creature_template.family`); devouring **any** creature of that family
unlocks it, and every different look (display id) is a **colouring**, named after the creature eaten.

| Shape (new name) | Canvas card | Today | Family | Spawned creatures / looks |
|---|---|---|---|---|
| **Wolf** | Anima-Stalked Wolf | Wolf (shape 5) | 1 | 114 / 69 |
| **Saber** | Shadow-Gorged Saber | Nightsaber (7) | 2 | 102 / 67 |
| **Boar** | Gore-Tusk Boar | Boar (9) | 5 | 32 / 22 |
| **Moth** | Luminescent Vale Moth | Moth (8) | 37 | 11 / 10 |

- Data, not code: e.g. `devourer_shape_family (shape_id, family)` (+ uninstall); explicit `devourer_shape_source`
  rows still work and win. Colouring names/displays are built at startup from the world DB (like `Mgr::BuildHints`);
  `.devour skin`, the menu's colouring button and the gallery hints ("Devour any wolf, e.g. Prairie Wolf (Mulgore)")
  keep working; existing characters keep what they own. Same shape ids, new names ("Wolf Form", "Saber Form" ...).
- Leave out looks that are not that body (ghost/spirit/other models) and list them in the PR.
- Favourite food per card (below) as data; 2x Bio Points for everyone when it matches (type or family).
- After it, `source/wxl/own/wxl-incarnations/tools/build_chromaticaw_data.py` must run again locally (say so in the PR).

## 2. The kits: the canvas cards, with these fixes (Claude's review)
Each form: 4 abilities + the gimmick as its passive. Numbers modest for levels 1-20 (the owner: strong is fine for
later forms, but starters must play at level 1). Anima: builders give it, shifting costs 25. Visuals: stock 3.3.5.

**Wolf** (Pack Assassin & Low-Health Executioner) · food: family Boar / Crocolisk
- Tear Throat (+15 Anima, bleed) · Hungering Lunge (15 yd leap & slow) · Howl of the Pack · Ravaging Feast (eats bleed to heal)
- Gimmick Pack Prowess: hitting targets below 30% summons spectral pups that bite for extra bleeds.
- Fix: "Howl of the Pack (AoE disorient & haste)" mixes two jobs: make it one. Proposal: a haste howl (fits an
  executioner); the disorient goes.

**Saber** (Stealth Infiltration & Critical Ambush Assassin) · food: family Cat / Spider
- Phase Prowl (stealth, +50% opener) · Anima Shred (+20 Anima, from behind) · Essence Rend (bleed finisher) · Flicker Step (20 yd shadowstep)
- Gimmick: dodge/parry resets Phase Prowl in combat.
- Fix: an in-combat stealth reset on every dodge/parry is too strong: give it an internal cooldown (e.g. 20 s).
  Phase Prowl: an own spell (the stock druid Prowl may need cat form); check it with the Devourer's shapes.

**Boar** (Knockdown Charge Tank & Spiked Reflector) · food: type Critter or family Scorpid
- Gore (armour sunder) · Primal Charge (knockdown) · Thick Hide (-30% damage taken, short) · Tusk Sweep (cleave 3)
- Gimmick Barbed Bristles: reflects 15% physical damage as Nature thorns; charging builds Anima.
- Fixes: "Thickened Rind" renamed Thick Hide (a rind is fruit peel). Primal Charge usable in combat (not a copy of
  the warrior's Charge; Rush already covers moving out of combat). The -30% only for a few seconds.

**Moth** (Support Healer & Emergency Chrysalis Shielder) · food: Beast or plant-like creatures
- Siphon Proboscis (nature heal) · Blinding Spores · Flutter Dash (glide sprint) · Luminescent Pulse (AoE)
- Gimmick Cocoon Metamorphosis: below 25% wraps you in an invulnerable cocoon regenerating 30% max HP.
- Fixes: "Blinding Spores (60% miss chance)" is far too strong at level 1: about 20-25% for a few seconds.
  "Luminescent Pulse (Holy/Nature AoE)": the owner's older moth idea is lunar magic: make it moonlight (Arcane)
  with a matching visual. Cocoon once per fight (internal cooldown), or the moth cannot die. "Elemental [Plant]"
  does not exist in 3.3.5 (no plant type): use name/family rules or drop it; say what you chose.

**General (all cards):** "[Arcane]", "[Plant]", "[Lesser]" subtypes don't exist in 3.3.5 data: use type +
family/name rules. A Devourer has no taunt (the Glutton doubles threat instead): no taunts in kits. Mana/energy
drains must give the Devourer Anima (it has no mana). Every text a player reads: Anima, no game jargon.
Write each change and its reason into `docs/start-kit.md` and the PR text.

Later batches (not now): Strider (Plainstrider Chick), Trogg (Flesheater Trogg), Bat (Blight-Wing Bat), Wyrm (Anima
Siphon Wyrm), Owl (Strigid Moon-Owl, a new starter), and the tier 2/3 lines of Section 1.

## Done when (local session tests in game)
1. Devouring a different wolf (e.g. a Prairie Wolf) gives the Wolf form if new, else a new colouring; the menu shows it.
2. The same for one saber, one boar, one moth that were not sources before.
3. Taleka keeps her Moth and colourings; Nightsaber is now Saber with the same id.
4. The four kits play at levels 1-20 and read right; no server log errors; the uninstall covers the new table.
