# The Devourer's start: levels 1-20

Decided with the owner on 2026-09-30. Problem: a new Devourer had only auto attack and Devour, and its only shapes
came from level-44 CoA content (the Sethrak camp in Tanaris). It must start like any classic class.

## Decisions
- **Trainers, the classic way**: a Devourer trainer in every starting zone and every capital, teaching true-form
  abilities for coin every 2 levels. *Replaced 2026-10-01 (task 010):* the trainers are the two Hollowmoor witch
  sisters in the In-Between, met at level 5 (`docs/witch-sisters.md`); the 16 zone and capital trainers are gone.
- **Leather** armour (not mail). Weapons proposal: daggers, fist weapons, one-handed maces, staves, polearms,
  two-handed maces (no shields, no swords/axes). The trainer teaches the usual weapon skills where classic does.
- **One starting form per starting zone** (8 forms), each unlocked by devouring that zone's iconic creature, using
  the creature's own model (no new assets). Creatures of the same kind elsewhere add colourings (the CoA
  "colouring" system: shape = the kind of creature, colouring = the display of the creature eaten).

## True form (no shape): the class kit
Hunger is the rage bar (gained by melee hits and by Devour). A first draft, to be refined in play:

| Level | Ability | Idea |
|---|---|---|
| 1 | Devour (exists) | channel on a looted corpse: Hunger, shapes, colourings |
| 1 | Gnash | instant weapon strike, builds a little Hunger |
| 4 | Rend Flesh | Hunger spender, bleed |
| 6 | Hunger Pangs | spend Hunger to heal a little over time |
| 8 | Unnerving Snarl | short-range threat and slow (tank tool for the Glutton later) |
| 10 | talents open (task 005 placeholders), spec abilities from the chosen tree |
| 12-20 | every 2 levels a new rank or ability (draft names in task 006, may be placeholders) |

## The 8 starting forms

| Starting zone (race) | Form | Unlocked by devouring (entry, level) | Model (display) | Colourings from |
|---|---|---|---|---|
| Northshire (Human) | Wolf | Diseased Young Wolf (299, 1) | 31049 | Diseased Timber Wolf (69) 31048, Young Scavenger (1508, Deathknell) 447 |
| Coldridge Valley (Dwarf, Gnome) | Trogg | Rockjaw Trogg (707, 1-2) | 606 | |
| Shadowglen (Night Elf) | Nightsaber | Young Nightsaber (2031, 1) | 11454 | Springpaw Cub (15366) 15507, Springpaw Lynx (15372) 15506 |
| Ammen Vale (Draenei) | Moth | Vale Moth (16520, 1) | 17574 | |
| Valley of Trials (Orc, Troll) | Boar | Mottled Boar (3098, 1-2) | 503 | Young Thistle Boar (1984) 8869, Stonetusk Boar (113) 503 |
| Camp Narache (Tauren) | Plainstrider | Plainstrider (2955, 1-2) | 1219 | Adult Plainstrider (2956) 1220 |
| Deathknell (Undead) | Bat | Duskbat (1512, 1-2) | 4732 | |
| Sunstrider Isle (Blood Elf) | Mana Wyrm | Mana Wyrm (15274, 1) | 16217 | |

Each form follows the Devourer's shape rules (form spell, kit only while worn, shared shift cooldown, Hunger).
At the start a form has **2 abilities + 1 passive** (levels 1-10), and **2 more abilities** by level 20 (may be
placeholders at first). Every form must feel different: e.g. Wolf = pack pressure, Trogg = stone toughness,
Nightsaber = stealth and bleeds, Moth = dust and blinding, Boar = charges, Plainstrider = speed and kicks, Bat =
sonic and life drain, Mana Wyrm = arcane bolts. Draft kits are in task 007.

## Out of scope for now
Class quests (the classic level-10 quest per class), more forms per zone, forms for levels 10-40 (between the
starting forms and the Sethrak at 44).
