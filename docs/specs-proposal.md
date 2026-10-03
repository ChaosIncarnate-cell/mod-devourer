# Specs proposal — Glutton, Skinchanger, Brood (task 015, step 1)

Status: **proposal, nothing built.** Mark what you want in the PR (strike, edit numbers, "yes"/"no" per line); step 2 builds only what is marked.
Base: `task/006-007-devourer-start`. Everything below is buildable with stock 3.3.5a spell templates plus small SpellScripts like the ones in `src/DevourerSpecs.cpp` / `DevourerScripts.cpp`.

## Ground rules used throughout

- **Anima** (rage bar, 0-100, does not drain). Gained by: Concentrate (+30, usable in combat), devouring (+30), own swings (+2, `HungerPerSwing`), Gnash, hatchling meals (Brood). Shapes cost nothing.
- **Spenders** are "strong" abilities, spec abilities and active talents. Cost scale: **small 15, medium 25, big 40, finisher 60**. A full bar is 100, so Concentrate or one meal buys roughly one medium ability.
- Names and texts speak as Azeroth (flesh, hide, brood, hunger); no "tank/DPS/aggro/threat" in tooltips. In this document I use the role words only to explain intent.
- Layout: keep the 11-tier grid, 5 points per tier, 71 points at 80. Each tree below fills the 30 slots of task 005 (about 95 ranks against 71 points), so no tree can be taken whole and a build means real choices. The existing real talents (Glutton: Quick Devour, Devour Whole, Feast, Regurgitate, Stretched Gut, Thick Hide, Bile Coating) are kept as they are; the other placeholder slots are re-used in order (same talent ids and spell ids where possible).
- Passive numbers are "per rank" unless stated. All are first guesses for you to change.

## Which existing abilities become "strong" (cost Anima)

| Ability | Today | Proposed cost | Why |
|---|---|---|---|
| Gnash (1) | free, builds a little Anima | free (stays the builder) | the basic strike |
| Rush (1) | free, no Anima | free, 15 s cooldown (unchanged) | mobility, not damage |
| Rend Flesh (4) | "Anima spender" in the design | **25** | the bread-and-butter spender |
| Hunger Pangs (6) | heal over time | **30** | self-heal, must feel like a choice |
| Unnerving Snarl (8) | short-range hold and slow | **15** | cheap, Glutton uses it constantly |
| Concentrate (1) | +30 Anima | free, +30 Anima (cooldown: see note 5) | the way to refill |
| Devour | +30 Anima | free (a gain, never a cost) | the other way to refill |
| Form ability 2 "big" ones (Void Breath, Dragging Roar, Rising Serpents, Void Frenzy, Overrun) | free, own cooldowns | **25-30**, cooldowns kept | the strong shape abilities |
| Form abilities 1 / passives (Chain Lightning, Stomp, Smash, Gnaw...) | free | free | filler, they keep a shape playable at 0 Anima |
| Devour Whole (talent) | free | **20** | it heals and bursts an ability: strong |
| Hatch Brood (Brood, level 1) | 30 Anima already | stays **30** | already costs Anima |

Rule for future forms: the first ability of a form is free filler, the second or "signature" one costs 25-30.

---

## Glutton: the Belly (role: holds the enemy, outlasts it)

**Core.** The Glutton stands in front and eats. Every meal makes it bigger and tougher (Gorged stacks) and a meal buff follows what it ate. It cannot draw an enemy with a taunt: its presence does (the identity passive doubles how hard enemies hate it). Its hard moments are **Devour Whole** (swallow the weakened, heal, one of its abilities bursts out) and **Regurgitate** (hold that ability in, spit it out when it matters).

### Spec abilities
| Lvl | Name | Effect | Cost | Cooldown |
|---|---|---|---|---|
| 20 | **Iron Gut** | Swallow your pain: for 8 s you take 30% less damage and cannot be knocked or stunned. Each Gorged stack adds 1% more. | 25 | 45 s |
| 40 | **Devouring Challenge** | Roar at everything within 10 yd: they must turn on you for 4 s, and every enemy that strikes you in that time feeds you 5 Anima. | 30 | 2 min |
| 60 | **Last Supper** | When a blow would kill you, you survive at 20% health and every Gorged stack is eaten at once to heal 3% of your health per stack (once per 5 min, passive; the strike needs a full bar of 100 Anima and eats it). | 100 (all) | 5 min |

### Talents (30)
| Tier | Talent | Ranks | Effect | Anima |
|---|---|---|---|---|
| 0 | **Iron Stomach** | 5 | +2% maximum health per rank | - |
| 0 | **Quick Devour** *(real)* | 1 | Devour takes 1 s and is not broken by damage | - |
| 0 | **Devour Whole** *(real)* | 1 | (as today) | 20 |
| 1 | **Deep Hunger** | 5 | Every meal gives +2 more Anima per rank | - |
| 1 | **Feast** *(real)* | 1 | Devour eats every corpse within 10 yd | - |
| 1 | **Regurgitate** *(real)* | 1 | (as today) | - |
| 1 | **Thick Gullet** | 3 | Gorged lasts 20 s longer out of combat per rank | - |
| 2 | **Iron Maw** | 2 | Gnash hits 10% harder per rank and gives +2 Anima | - |
| 2 | **Stretched Gut** *(real)* | 1 | (as today) | - |
| 2 | **Bottomless Pit** | 5 | Each Gorged stack adds +0.5% armour per rank | - |
| 3 | **Digested: Thick Hide** *(real)* | 1 | one of two, as today | - |
| 3 | **Digested: Bile Coating** *(real)* | 1 | the other of the two | - |
| 3 | **Gristle Plating** | 3 | +5% armour per rank; +10% with a beast meal buff | - |
| 4 | **Heavy Belly** | 5 | Healing taken +3% per rank | - |
| 4 | **Bloated Resolve** | 2 | Hunger Pangs costs 5 less per rank | - |
| 4 | **Digestive Fire** | 3 | Regurgitate's ability hits for +15% per rank | - |
| 5 | **Slow Chew** | 5 | Unnerving Snarl also lowers the enemy's strikes by 2% per rank | - |
| 5 | **Grand Appetite** | 1 | Your meal buff lasts 30 min instead of 10 and a second buff (from the previous meal) stays beside it | - |
| 5 | **Chewing Cud** | 3 | Rend Flesh bleeds feed you 1 Anima per tick per rank | - |
| 6 | **Swallowed Pride** | 3 | Stuns and silences against you last 15% shorter per rank | - |
| 6 | **Belly of the Beast** | 3 | Gorged can grow +1 stack higher per rank (cap 10 → 13) | - |
| 6 | **Ravenous Guard** | 2 | While under 50% health, you gain 10% more health from every meal per rank | - |
| 7 | **Fat Reserves** | 1 | The first time you drop below 30% health in a fight, absorb 15% max health; 3 min | - |
| 7 | **Gnawing Patience** | 5 | Each enemy beating on you adds +1% damage dealt back to them per rank (max 5 stacks) | - |
| 8 | **Crushing Jaw** | 2 | Devour Whole also stuns for 1.5 s per rank | - |
| 8 | **Satiation** | 3 | A full bar (100 Anima) cuts damage taken by 3% per rank | - |
| 8 | **Hunger's Wall** | 3 | Iron Gut lasts 2 s longer per rank | - |
| 9 | **Unending Meal** | 5 | Devour Whole heals +5% more per rank | - |
| 9 | **Glutton's Bulk** | 3 | +5% size and +3% health per rank | - |
| 10 | **Stomach of Stone** *(capstone, needs Unending Meal 5/5)* | 1 | Gorged can reach 15 stacks; at 15 stacks you cannot be pulled, feared or slowed | - |

> If 30 is too many, suggested cuts: Heavy Belly, Slow Chew, Hunger's Wall, Glutton's Bulk (same idea for the other trees: thin the 5-rank filler talents first).

---

## Skinchanger: the Many (role: balanced, damage, fast)

**Core.** The Skinchanger lives in the shift. Its cooldown between shapes is 3 s (others 8 s). Leaving a shape in a fight leaves an **Echo** for 8 s: a translucent copy that fights the target and casts that shape's Ability 1 once. Play is a chain: begin in one shape, shift out (echo), shift in another, shift out. Anima comes from striking and from the echoes it leaves.

### Spec abilities
| Lvl | Name | Effect | Cost | Cooldown |
|---|---|---|---|---|
| 20 | **Mimic Strike** | Strike the target with the weapon blow of the last shape you left: 150% weapon damage plus that shape's school, ignores 20% armour. | 25 | 12 s |
| 40 | **Skin Swap** | Swap places with your Echo (it takes your place and you take its). The enemy you struck last is turned to follow the Echo for 4 s. | 30 | 30 s |
| 60 | **Form of Many** | For 12 s every shift is instant (no shift cooldown) and each Echo you leave lasts 14 s and casts Ability 1 twice. | 60 | 3 min |

### Talents (30 slots, built in order)
| Tier | Talent | Ranks | Effect | Anima |
|---|---|---|---|---|
| 0 | **Shifting Hide** | 5 | After a shift, +3% armour per rank for 6 s | - |
| 0 | **Fluid Flesh** | 5 | -0.2 s per rank off the shift cooldown (min 1 s total) | - |
| 0 | **Borrowed Claws** | 3 | +4% damage per rank for 8 s after any shift | - |
| 1 | **Quick Molt** | 3 | A shift costs no turn: you keep moving while it happens | - |
| 1 | **Second Skin** | 5 | +1% movement and +1% speed of strikes per rank | - |
| 1 | **Mimic's Eye** | 2 | Echoes gain your crit chance, +5% per rank | - |
| 1 | **Restless Form** | 3 | Shifting into a shape you have not worn for a minute gives 5 Anima per rank | - |
| 2 | **Shed Skin** | 2 | Shifting frees you from one slowing or rooting effect, 20 s per rank apart | - |
| 2 | **Many Faces** | 3 | Echo lasts 2 s longer per rank | - |
| 2 | **Loose Bones** | 5 | -4% damage from area effects per rank | - |
| 3 | **Stolen Instinct** | 1 | **Active:** copy the passive of the last shape you left onto the shape you wear, 12 s | 15 |
| 3 | **Changing Blood** | 5 | Bleeds on you are 8% weaker per rank | - |
| 3 | **Flicker Shape** | 3 | Echo hits take 5% of the enemy's health back to you per rank (cap per echo) | - |
| 4 | **Mask of Meat** | 5 | +2% maximum health per rank in shapes of beasts, +1% elsewhere | - |
| 4 | **Shape Memory** | 2 | Mimic Strike costs 5 less per rank | - |
| 4 | **Wandering Skin** | 3 | +2 yd reach on Rush per rank; Rush leaves an Echo | - |
| 5 | **Unfixed Nature** | 5 | Each different shape worn in 15 s gives +2% damage per rank (max 3 stacks) | - |
| 5 | **Echo Flesh** | 1 | **Active:** call your Echo to your side and it casts Ability 1 at once | 25 |
| 5 | **Living Mask** | 3 | Echoes draw 20% of the attention of the enemy per rank | - |
| 6 | **Skin Hoard** | 3 | Echoes you leave refill 4 Anima per rank when they die | - |
| 6 | **Swift Change** | 3 | Shifting grants 10% haste for 4 s per rank (no stacking) | - |
| 6 | **Hollow Shell** | 2 | Leaving a shape at full health leaves a second, smaller Echo (50% power) | - |
| 7 | **Worn Faces** | 1 | **Active:** your Echo counts as a hatchling and a meal source for 10 s (a corpse near it can be eaten by it for Anima) | 20 |
| 7 | **Borrowed Voice** | 5 | Echo casts +4% stronger spell effect per rank | - |
| 8 | **Soft Bones** | 2 | Dodge +3% per rank while in a shape you have worn for under 10 s | - |
| 8 | **Shapeless Step** | 3 | Rush has a shorter cooldown, -2 s per rank | - |
| 8 | **Mirror Hunger** | 3 | Echoes drain 3 Anima per rank from the target's mana or rage and give it to you | - |
| 9 | **Stolen Strength** | 5 | +1% damage per rank per distinct shape you know (max 10) | - |
| 9 | **Fleeting Form** | 3 | Shift cooldown 0.5 s shorter per rank when the last shift was within 5 s | - |
| 10 | **Thousand Skins** *(capstone, needs Stolen Strength 5/5)* | 1 | Every shift leaves an Echo, even out of a fight; echoes never overlap more than three | - |

---

## Brood: the Mother (role: damage through summons)

**Core.** Brood hatches young that fight and eat. When something dies near a hatchling it devours it: +10 Anima, +3% health, and it counts as a meal for shapes and colourings. The mother can feed on her own young (Devour on a hatchling: +15% health, +15 Anima). Anima is the egg bar: spend it on more eggs and louder calls.

### Spec abilities
| Lvl | Name | Effect | Cost | Cooldown |
|---|---|---|---|---|
| 20 | **Call the Clutch** | Call every hatchling within 40 yd to the target; they strike 30% harder for 10 s. | 20 | 30 s |
| 40 | **Feed the Young** | Spend 15% of your health to give each hatchling a heal of 25% of its health and +10% haste for 10 s. | 25 | 20 s |
| 60 | **Brood Swarm** | Hatch six hatchlings at once for 20 s (the worn shape's kin), each with 50% of your attack power. | 50 | 3 min |

### Talents (30 slots, built in order)
| Tier | Talent | Ranks | Effect | Anima |
|---|---|---|---|---|
| 0 | **Warm Nest** | 5 | Hatchlings have +3% health per rank | - |
| 0 | **Swelling Brood** | 5 | Hatch Brood lasts 2 s longer per rank | - |
| 0 | **Egg Tooth** | 3 | Hatchlings bite for +5% damage per rank | - |
| 1 | **Many Mouths** | 3 | +1 hatchling every other Hatch Brood per rank (up to 4) | - |
| 1 | **Nursing Hunger** | 5 | Hatchling meals give +1 Anima per rank | - |
| 1 | **Shared Meal** | 2 | You share a meal with every hatchling next to you: +2 health to each per rank | - |
| 1 | **Hatching Heat** | 3 | Hatch Brood costs 3 less Anima per rank | - |
| 2 | **Brood Mother** | 2 | Hatchlings follow you across the zone (no leashing) | - |
| 2 | **Clutch Instinct** | 3 | Hatchlings warn you: +2% dodge per rank while one lives | - |
| 2 | **Hungry Young** | 5 | A hatchling's meal heals it for 5% per rank | - |
| 3 | **Nest Guard** | 1 | **Active:** your hatchlings stand around you and take 40% of your damage for 8 s | 20 |
| 3 | **Feeding Frenzy** | 5 | Hatchlings are 3% faster per rank after a meal for 6 s | - |
| 3 | **Spawning Pool** | 3 | Hatch Brood has a 15% chance per rank not to start its cooldown | - |
| 4 | **Litter Bond** | 5 | Share 2% of your armour with each hatchling per rank | - |
| 4 | **Twitching Eggs** | 2 | Hatchlings die in an eggburst: 30% attack power damage per rank in 5 yd | - |
| 4 | **Swarm Call** | 3 | Call the Clutch costs 4 less Anima per rank | - |
| 5 | **Nest Web** | 5 | Hatchlings slow the enemy 2% per rank per strike (max 5 stacks) | - |
| 5 | **Brood Sense** | 1 | **Active:** see where every hatchling is; tell them to strike a chosen target at once | 15 |
| 5 | **Thick Shells** | 3 | Hatchlings take 5% less damage per rank | - |
| 6 | **Quick Hatching** | 3 | Hatch Brood cooldown 3 s shorter per rank | - |
| 6 | **Blood Milk** | 3 | Devour on a hatchling also gives +10% haste for 10 s per rank | - |
| 6 | **Swollen Sac** | 2 | One more hatchling at once per rank (max 4 + 2) | - |
| 7 | **Nest Scent** | 1 | **Active:** mark an enemy; hatchlings deal +20% damage to it for 12 s and gain Anima for you when they hit it | 20 |
| 7 | **Hive Mind** | 5 | You take 1% less damage per rank per living hatchling (max 5) | - |
| 8 | **Young Teeth** | 2 | Hatchlings bleed their target for 30% of their damage per rank | - |
| 8 | **Crawling Mass** | 3 | Swarm summons last 3 s longer per rank | - |
| 8 | **Mother's Wrath** | 3 | Dying hatchlings give you a 4% damage buff per rank for 8 s (stacks to 3) | - |
| 9 | **Endless Clutch** | 5 | 10% chance per rank a dying hatchling hatches a new one | - |
| 9 | **Swarm Tide** | 3 | Brood Swarm costs 6 less Anima and its young last 4 s longer per rank | - |
| 10 | **Queen of the Brood** *(capstone, needs Endless Clutch 5/5)* | 1 | The brood is never smaller than 4; every hatchling is as large as a Gorged beast and bites 20% harder | - |

---

## Things I noticed while drafting (decide or ignore)

1. **Tree size.** Each tree has 30 slots (task 005 layout) and I filled all of them. If you want ~25, name the talents to drop.
2. **Last Supper (Glutton, 60)** is a once-per-5-min death save that eats the full bar. It needs a SpellScript hook on lethal damage (`SPELL_AURA_SCHOOL_ABSORB`-style or `OnPlayerDamageTaken`) and is the riskiest to build. Safer variant: a big 60-Anima heal that scales with Gorged stacks.
3. **Skin Swap (Skinchanger, 40)** needs the Echo as a tracked creature (it is already a creature in `DevourerSpecs.cpp`, so a teleport swap is a few lines).
4. **Anima gain tuning.** With free shapes and costs of 15-30, the bar refills mainly by swings (2 each) and meals; a fight of 10 s without Concentrate gives roughly one spender per 20 s. If that feels dry, raise `HungerPerSwing` to 3 or make Gnash +5 instead of +2 (config only).
5. **Concentrate cooldown.** Concentrate currently has no cooldown noted in the docs; I suggest 30 s so it is a refill, not a faucet.
6. **Role words.** Tooltips should say "turn on you", "draw their attention", "the hunt" instead of "taunt/threat".
7. **Playerbots.** Nothing here changes bots; class 10 is never rolled.

## How step 2 would work (for your approval)

- Talent spells and spec abilities replace the placeholders **in place** (same ids): edit `tools/placeholders.py` into real definitions, regenerate SQL 07, `DevourerPlaceholderIds.h` and the client rows with the existing tools; real effects are SpellScripts or stock aura templates.
- Anima costs go on the spells as rage power cost (cost x10 in the spell row) and the existing power-cost check handles refusal, so no new engine code is needed for them.
- `docs/talents.md` is regenerated, uninstall SQL keeps working (same id ranges).
