# mod-devourer

**A shapeshifter class that becomes what it eats.** An AzerothCore module for the CoA repack, living in
class slot 20. The class is built new: nothing of the old slot-20 class is kept, only the number (every
one of the 32 class ids is taken). The identity patch (`source-overlay`, `identity\server-dbc`, the
client `patch-T.MPQ` and the loose Interface files) names the class, its specs and its talent tabs.

## How it plays

- **Devour** (channel) a slain, looted creature: Hunger +`HungerPerMeal`. A creature listed in
  `devourer_shape_source` unlocks its shape (and the colouring it grants); a new shape is forced on you.
- Every shape is a **"<Shape> Form"** spell. Wearing it sets the model, and teaches its **four
  abilities and passive** for as long as it is worn (placed on action buttons 60-63, the bottom-left bar).
- **One shift cooldown** for all shapes: the form spells share spell category 4001 (8 s). A Skinchanger's
  recovers faster (`SkinchangerShiftCooldown`).
- **Hunger** runs on the rage bar and is the only resource.
- The worn shape is saved at logout and put back at login and after resurrection.

## Specs

The spec abilities are learned and removed automatically when the specialization changes (checked every
3 s). Each spec's talent tree starts with an identity passive (CharacterAdvancement 139001-139003, spells
9100011-9100013); the client needs one per spec.

| Spec (ChrSpecs id) | Role | What it adds |
|---|---|---|
| Glutton (25) | tank | *(ChaosCore0.3)* No taunt: the identity passive **doubles threat**. Every meal adds a stack of **Gorged** (+3% health, +5% size, up to 10; digested out of combat, a stack every 3 s after 6 s) and a **meal buff** for 10 min by what was eaten: beasts +15% armor, humanoids/giants +10% attack power, undead heal 5% of melee damage, dragonkin +75 fire resistance and a burst of fire, demons 2 Hunger every 3 s, anything else +10% magic damage; machines give Indigestion. The worn shape's **favourite food** (its best diet type) counts twice (Gorged and Bio Points). **Talents** (CharacterAdvancement 139010-139016, `tools/build_glutton_talents.py`): Quick Devour (1 s Devour, not broken by damage), Devour Whole (20 s: kill an enemy below 25% health or a non-elite 5+ levels below you, heal, one of its abilities bursts out), Feast (Devour eats every corpse within 10 yd), Regurgitate (Devour Whole holds the ability in for 10 s and becomes Regurgitate; left too long it bursts out and you are **Digested**: the meal buff doubled for 10 s), Stretched Gut (Gorged held 5 min out of combat, Regurgitate 20 s), and a choice of what Digested does instead: Thick Hide (-20% damage taken) or Bile Coating (absorbs 5% max health per Gorged stack) |
| Skinchanger (26) | balanced / damage | shift cooldown 3 s; leaving a shape in combat leaves its **Echo** for 8 s: a translucent copy that fights your target and casts the shape's **Ability 1** once (for the Sethrak, Chain Lightning) |
| Brood (27) | damage + summons | **Hatch Brood** (30 Hunger, 30 s): two hatchlings for 20 s in the worn shape's kin (the Sethrak's are serpents). When something dies near them, a hatchling devours it: +10 Hunger, 3% health, and it counts as a meal for shapes and colourings. **Devour** on your own hatchling eats it back: 15% health and 15 Hunger |

Any slain creature can be devoured now (Hunger, and the Glutton's meal); only the ones in
`devourer_shape_source` give shapes or colourings. A corpse with loot left stays until it is looted.

## Shapes

| Shape | Unlock | Abilities | Passive |
|---|---|---|---|
| Sethrak (display 200004; colourings Diamondback, Green, Ember, Viper, Dusk, Gilded, Blood) | Idol of the Sethrak (every new Devourer gets one); the Tanaris camp, 44-46 | Chain Lightning, Coil Strike (lunge + 2 s root), Sandstorm Shroud (-20% damage taken, -20% enemy hit), Snake Charm | Rain of Toads: 15%, 6 s ICD, Plague on up to 3 enemies (-50% healing done, stacking DoT) |
| Berserker (display 991010, `creature\berserker`; colourings Orange, Azure, Crimson, Teal and the bigger Ultradon, Ultradon-Azure, Ultradon-Crimson, Ultradon-Teal) | Idol of the Berserker (item 9100101) | Void Breath (3 s channel, Shadow damage + 30% slow), Stomp (8 yd damage + 50% slow), Dragging Roar (pulls enemies within 12 yd, stuns them 2 s when they land), Smash (200% weapon damage, +50% on stunned targets, +15 Hunger) | Blood Scent: +5% movement and +10% attack speed for every unit within 30 yd below 50% health, up to 10 stacks |
| Vashnik (display 991029, `creature\vashnik`) | Evolves from the Sethrak (below) | Storm Chain (5 targets), Coiling Whirl (lunge, then a real Whirlwind: 8 yd damage + 3 s root), Rising Serpents (two stationary snakes for 20 s that cast every spell you cast at an enemy; a charm goes to another enemy each), Serpent's Gaze | Plague Swarm: 20%, up to 5 enemies |
| Baby Berserker (display 991063, `creature\babyberserker`; colourings OrangeWhelp, AzureWhelp, CrimsonWhelp, TealWhelp) | Voidstorm Whelps 9101024-9101027 (one per colour); grows into the Berserker (600 BP, level 20, 50 kills, 3 demons devoured; keeps its colour) | Overrun (0.5 s wind-up, then a charge at the target or 20 yd ahead: 120% weapon damage and a 1 s knockdown to everything in the path), Gnaw (3 s grapple: held, disarmed, bleeding; each bite heals 4% and gives 5 Hunger), Pitiful Wail (fear, 5 enemies within 8 yd, 4 s), Void Frenzy (roar, then 5 strikes of 70% weapon damage) | Teething: every hit stacks Chewed (-2% armor, up to 5); Gnaw heals twice on a target chewed 5 times |

## Data

| Where | What |
|---|---|
| `devourer_shape` (world) | one row per shape: form spell, display, scale, the four kit spells, passive |
| `devourer_shape_source` (world) | creature entry -> shape (+ colouring granted) |
| `devourer_skin` (world) | display -> shape and colouring name (Sethrak: displays 991001-991007, textures `creature\sethrak_melee\devourer_sethrak_*.blp` in patch-T) |
| `tools/skins/` | `recolor.py` (the Sethrak colourings from the diamondback texture: eyes, glow stripes, scale tint) and `blp.py` (BLP2 DXT5 writer) |
| `character_devourer_shape` / `_skin` / `_worn` | unlocked shapes, colourings, the shape worn |
| `tools/build_devourer_spells.py` | the single source for every Devourer spell: writes the client `Spell.dbc`, the SQL and `src/DevourerSpellIds.h` together |

Spell ids 9100001-9100207 (a shape's spells start at 9100100 x its shape id) (the range 9100000-9100899 is reserved; the build script clears it first).
Adding a shape: its spells in `build_devourer_spells.py`, a `devourer_shape` row, source rows, then rebuild
the client patch with `tools/build_devourer_identity.py --extra-client`.

## Commands

`.devour` lists your shapes and colourings, `.devour skin <name>` wears a colouring (`black` = base). GM: `.devour unlock <shape>`;
admin: `.devour reload` (re-reads the shape tables). The `/devour` addon command sends the same.

## Not yet

Hunger thresholds, more shapes
(the Worgen among them) and skins, bots playing Devourers.

## Models from other tools

The Berserker's models come from the RetroportTool (`Data\creature\berserker`, `berserkerboss`), which also writes
Data\dbc and loose tables into the client's Data\DBFilesClient. A loose table wins over patch-T, so the installer
merges the Devourer's rows into those copies (`tools/merge_dbc.py`, rows 902001-902037 / 980001-980999 /
991001-991009 are the Devourer's own) instead of replacing them, and moves aside old loose copies of the tables
patch-T carries (Spell, ChrSpecs, CharacterAdvancement...). Models added later by the tool stay.

## Growth: Bio Points and evolution

A worn form earns **Bio Points (BP)** from every meal (Devour, Devour Whole, a hatchling's meal): its diet's
points for the meal's creature type (`devourer_diet`, type 0 = anything else) times the meal's rarity (normal 1,
elite 3, rare 5, rare elite 8, bosses 20). An evolution (`devourer_evolution`) needs BP, a level and its tasks
(`devourer_evolution_task`: kill a creature type, be hit by a school, devour something rare, devour a type), all
done while wearing the earlier form. Then the next form is unlocked and forced on; the earlier one stays.
`/devour` shows the progress.

| Line | Needs |
|---|---|
| Sethrak -> Vashnik | 1000 BP (Humanoids 15, Beasts 10, Dragonkin 25, others 3), level 30, kill 40 Humanoids, take 100 Nature hits, devour an elite or rarer |
