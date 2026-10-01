# 009 — General forms, first batch: Wolf, Cat, Boar, Moth (+ fix their abilities)

Status: open. Base: branch `task/006-007-devourer-start` (after 008, or in parallel; both add SQL, keep ids apart).
Branch: `task/009-general-forms-batch1`. Read `CLAUDE.md`, `docs/design.md`, `docs/start-kit.md`, `tools/start_kit.py`.
Owner's rule: build only what is asked here; anything else goes into the PR text as a proposal.

## Owner's words (2026-10-01)
"The single forms should not be THAT specific ... reworked into wolf, or allow many many wolf like creatures, to be
overall less specific. Also go through the abilities and make changes to the abilities that are weird, do not make
sense, or you think might be better differently. Let's start with only a first batch of those creatures."

## 1. A form is a kind of creature, not one creature
Today a starting form is unlocked by one creature entry (+ a few listed colouring creatures) in `devourer_shape_source`.
New: a shape can name a **creature family** (`creature_template.family`, beasts): devouring **any** creature of that
family unlocks the shape, and each different look (display id) unlocks a **colouring**, named after the creature it
came from (e.g. "Prairie Wolf"). Spawned creatures of the families (stock DB, counted locally):
| Shape | Was | Family | Creatures | Looks |
|---|---|---|---|---|
| Wolf | Wolf (Diseased Young Wolf) | 1 | 114 | 69 |
| Cat | Nightsaber (Young Nightsaber) | 2 | 102 | 67 |
| Boar | Boar (Mottled Boar) | 5 | 32 | 22 |
| Moth | Moth (Vale Moth) | 37 | 11 | 10 |
- Data, not code: e.g. a table `devourer_shape_family (shape_id, family)` (+ uninstall). Explicit `devourer_shape_source`
  rows keep working and win over the family rule. Colouring names and the display list are built at startup from
  the world DB (like `Mgr::BuildHints`); `.devour skin <name>`, the menu (colouring button, gallery hints: "Devour any
  wolf, e.g. ... (zone)") and `character_devourer_skin` keep working; existing characters keep what they have.
- Leave out looks that are not that body (ghosts/spirits, other models: compare the display's model with the family's
  usual ones) and bosses' unique looks if they break the shape; say in the PR what was left out and why.
- Shape names become the kind: "Wolf Form", "Cat Form", "Boar Form", "Moth Form" (rename Nightsaber; same shape id).
- Bat, Strider, Trogg, Mana Wyrm stay as they are (later batches).
- If incarnations data is affected: note in the PR that `source\wxl\own\wxl-incarnations\tools\build_chromaticaw_data.py`
  must be run again locally.

## 2. Their abilities: fix what is weird
Claude's review of the four kits (tools/start_kit.py), to be done:
- **All four**: the two level-10/20 abilities are empty placeholders: make them real, fitting the kind and level
  (names in the script: Wolf "Rip Throat", "Call of the Pack"; Cat "Ambush Leap", "Shadow Stalk"; Boar "Tusk Toss",
  "Wallow"; Moth "Luring Glow", "Silken Cocoon"). Modest numbers for levels 10-20; a level-10 ability may cost Anima.
- **Moth**: "Dusty Wings" is Nature damage with Arcane Explosion's visual (mismatch); the owner's older idea for moths
  is **lunar magic**: make the moth's damage lunar/arcane and its visuals match (moonlight, dust).
- **Cat**: "Prowl" is the stock druid spell: check it works outside druid cat form (stealth, speed, breaks on
  damage) and with the Devourer's shapes; if not, an own stealth spell.
- **Boar**: "Boar Charge" duplicates the warrior's Charge (out of combat only) and Rush already exists in the base
  kit: give the boar something of its own instead (e.g. a short charge usable in combat, or a knock-back gore).
- **Wolf**: fine as is ("Savage Bite", "Pack Howl", passive crit), only the two placeholders.
- Every text a player reads: Anima, no game jargon in names, the spell's own tooltip numbers ($s1...).
Write each change and its reason into `docs/start-kit.md` (generated) and the PR text.

## Done when (local session tests in game)
1. Devouring a different wolf (e.g. a Prairie Wolf) gives the Wolf form (if new) and a new colouring; the menu shows it.
2. Same for one cat, one boar, one moth that were not sources before.
3. Taleka keeps her Moth and colourings; the Nightsaber shape is now "Cat" with the same id.
4. The reworked abilities work and read right; no server log errors; uninstall covers the new table.
