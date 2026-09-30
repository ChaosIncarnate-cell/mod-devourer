# 007 — Eight starting forms, one per starting zone

Status: open
Base: branch `integration` (can run in parallel with 006; both add SQL files, coordinate spell id ranges:
006 takes 9100810-9100899, this task takes creature/shape ids below). Branch: `task/007-starting-forms`.
Read `docs/starting-experience.md` first: the table there lists the forms, the creatures and the displays.

## Goal
Every race starts next to a creature it can devour into its first form: Wolf, Trogg, Nightsaber, Moth, Boar,
Plainstrider, Bat, Mana Wyrm. The game's own models, the existing shape system (`devourer_shape`,
`devourer_shape_source`, colourings), nothing hard-coded that the tables can hold.

## Scope
- 8 new shapes (ids after the existing ones), each with a form spell using the creature's own display, **2 abilities +
  1 passive** usable from level 1, and 2 more abilities that open by level 20 (placeholders allowed, marked
  "(placeholder)"). Kits must feel different (draft themes in the design). Numbers modest for levels 1-20.
  Visuals: reuse fitting existing 3.3.5a spell visuals (wolf howl, boar charge, bat drain...), no new assets.
- Spell ids: the shape rule "a shape's spells start at 9100100 x its shape id" does not scale to 12+ shapes; pick a
  clear scheme inside 9100000-9100899 that does not collide with 005 (9100500-9100808) and 006 (9100810-9100899),
  or propose extending the reserved range (and the uninstall) and document it in `docs/talents.md`.
- `devourer_shape_source`: the zone creature unlocks the form; the other creatures in the table add colourings
  (display -> colouring name).
- The client patch needs nothing new for models (native displays), only the spells (task 004's tool reads the SQL).
- Uninstall covers every new row.
- Devour must work on these level-1 creatures (they are normal, lootable beasts/humanoids): check `RequireLooted` and
  any level or rarity checks in the module.

## Done when (local session tests in game)
1. In each starting zone, devouring its creature unlocks the form, forces it on, and the kit appears on the bar.
2. Devouring a colouring creature (e.g. Young Scavenger) gives the Wolf form that look (`/devour skin ...`).
3. Shifting between true form and a starting form respects the shared cooldown; Hunger works in forms.
