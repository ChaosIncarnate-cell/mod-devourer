# 008 — A Devourer tab in the spellbook

Status: open. Base: branch `task/006-007-devourer-start` (625eea7). Branch: `task/008-spellbook-tab`.
Read `CLAUDE.md` and `docs/design.md` first. Owner's rule: build only what is asked here, nothing extra.

## Goal
Classic classes have their own spellbook tab (their class skill line); the Devourer's spells all sit in "General".
The Devourer gets its own tab, like the classic classes.

## Scope
- A class skill line for class 10 ("Devourer", SkillLine category 7) with a free id (check the stock SkillLine.dbc;
  reserve it in `tools/build_class_dbc_sql.py` RESERVED): `skillline_dbc` row (server) + the same row in the client
  patch (`tools/client/dbc_layouts.json` needs a SkillLine layout; `build_client_patch.py` writes rows of the
  committed SQL into the client DBCs).
- `skilllineability_dbc` rows linking the Devourer's own spells to it (Devour, Quick Devour, Rush, Concentrate,
  every form spell, every shape's kit and passive, the spec and talent spells), ClassMask 512.
- `skillraceclassinfo_dbc` row so class 10 may have the skill (all races, ClassMask 512), and the skill at
  creation (`playercreateinfo_skills`) plus for existing characters (the module sets it at login if missing).
- Uninstall removes every new row.

## Done when (local session tests in game)
1. The spellbook shows a "Devourer" tab with the Devourer's spells; General keeps only the general ones.
2. A new character and an existing one (Taleka) both have the tab; no "invalid skill" lines in the server log.
3. Uninstall + install leaves the DB identical.
