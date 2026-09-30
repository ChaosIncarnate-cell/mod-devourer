# 005 â€” Placeholders: full talent trees and spec abilities

Status: open
Base: branch `integration` (001-004 merged and built locally, Ulatek snake removed). Branch: `task/005-placeholder-talents-and-specs`.

## Goal (owner, 2026-09-30: "place in some placeholders for the class specializations and talent tree")
The Devourer is unfinished and will be designed piece by piece. It needs a **complete, playable skeleton** now:
three full talent trees and the spec abilities, all as clearly marked placeholders, so the class can be levelled
and tested end to end, and so the owner can later replace one slot at a time with a real design.

## Today (task 003)
Trees 900 Glutton / 901 Skinchanger / 902 Brood. Glutton has the real CoA talents (Quick Devour, Devour Whole,
Feast, Regurgitate, Stretched Gut, Digested: Thick Hide / Bile Coating) plus 2 placeholders; Skinchanger and Brood
have one placeholder each. No tree can be completed (3.3.5a: 5 points per tier, 71 points at level 80).

## Scope
### Talent trees
- Each tree gets a WotLK-like layout: 11 tiers (0-10), 4 columns, roughly 25-30 talents and **at least 61 ranks**,
  a 1-rank capstone at tier 10 (the "51-point talent"), and a few 1-rank "ability" talents in the middle tiers
  (like WotLK's tier 4/6 abilities), with some prerequisite arrows. Every tier must be reachable.
- **Keep all real Glutton talents where they are** (ids 9000-9008); build the placeholders around them.
- Placeholder talents: names in the Devourer's theme with the suffix "(placeholder)" (e.g. "Thick Gullet
  (placeholder)"), description "Not designed yet.", a dummy aura (SPELL_AURA_DUMMY) with no effect, a generic but
  fitting icon. Ranks as normal WotLK talents (1-5).
- Ids: keep talent ids in 9000-9199 (per tree a block: 9000-9059, 9060-9119, 9120-9179) and placeholder spells in a
  free sub-range of 9100000-9100899 (document the range in `docs/talents.md`; move the task-003 placeholders
  9100050-9100069 there if that keeps it simpler).

### Spec abilities
- Each spec gets placeholder abilities that it learns with the spec (like Hatch Brood / Devour Whole today): **three
  per spec**, at levels 20, 40 and 60, names "(placeholder)", visible in the spellbook, castable with no effect
  beyond a short visual/log line, so learning/unlearning with the spec can be tested.
- Keep the existing real spec abilities and identity passives.

### Docs for the owner
- `docs/talents.md`: one table per tree with every slot (tier, column, id, ranks, name, real or placeholder,
  prerequisite) and the spec abilities per level. This is the map the owner will fill with ideas; keep it in sync.

### Everything must follow
SQL in the install (`data/sql/db-world`, new file), the same rows in the client patch (task 004's tool picks up
the SQL: check `dbc_layouts.json` covers them), and the uninstall removes them by id range.

## Done when (local session tests in game)
1. `.levelup 79` on a Devourer: all 71 points can be spent, every tier of every tree opens, the capstone is
   reachable, the talent window shows no empty or broken buttons.
2. Switching spec (resetting talents and filling another tree) learns/removes the right spec abilities.
3. Uninstall + install leaves the DB identical, as in task 003.
