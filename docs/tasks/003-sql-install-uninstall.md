# 003 — SQL: install and uninstall the class

Status: open (after 001/002 are drafted)

## Goal
All server-side data for class 10 and the Devourer content, as SQL that installs cleanly on a stock
Chromaticaw database and is fully undone by an uninstall script.

## Scope
- Rework the CoA SQL in `data/sql/` (it targets CoA's schema and class 20): class 20 → 10, drop anything that
  only made sense on CoA (CharacterAdvancement, CoA spec ids), keep shapes, sources, skins, diet, evolution.
- Class data via DBC override tables (see design): chrclasses_dbc (name "Devourer", power type rage), talenttab
  (3 tabs), talent (Glutton from `tools/coa/build_glutton_talents.py`, plus placeholders for the others),
  spell_dbc for 9100001+ (regenerate with the correct AzerothCore `spell_dbc` columns; `tools/coa/
  spell_dbc_columns.json` describes CoA's layout), skill lines, charstartoutfit, powerdisplay, gt* rows.
- `playercreateinfo` (+ `_spell_custom`, `_action`, `_item`), `player_levelstats`, `player_class_stats` for
  class 10 (warrior-like numbers).
- `uninstall/`: convert class-10 characters to warriors (and reset their talents/spells), then delete every
  row the install added (by id ranges), module tables last.

## Done when
Local session: install on a copy of the DB → server starts clean; uninstall → server starts clean and the
tables match the pre-install dump.
