# 011 — Three spellbook tabs, like the classic classes

Status: done (PR into task/006-007-devourer-start). Base: branch `task/006-007-devourer-start` (6ab2366). Branch: `task/011-three-spellbook-tabs`.
Read `CLAUDE.md` and `docs/design.md` first. Owner's rule: build only what is asked here, nothing extra.

## Goal
Classic classes have three class tabs in the spellbook (Warrior: Arms, Fury, Protection). The Devourer gets three
too, one per talent tree: **Glutton**, **Skinchanger**, **Brood** (names as in `docs/talents.md`).

## Scope
- Three class skill lines (SkillLine category 7, free ids reserved in `tools/build_class_dbc_sql.py`) replacing
  task 008's single skill line 900; server `skillline_dbc` rows + the client rows (`tools/spellbook.py`,
  `tools/client/build_client_patch.py`). Talent.dbc / TalentTab already name the trees: check the tab order matches.
- Which spell goes where (SkillLineAbility, ClassMask 512), default unless the owner says otherwise:
  Glutton = Devour, Quick Devour, Concentrate, Glutton spec/talent spells; Skinchanger = Rush, every form spell,
  every shape's kit + passive (all shapes, incl. Warp Stalker 13, Biletoad 14, Giant Marsh Frog 15 and their
  helpers that show), Skinchanger spec/talent spells; Brood = Brood spec/talent spells.
- **Bug:** frog spells show 2-3 times in General (spellbook.py not rerun after the frogs; check for duplicate
  SkillLineAbility rows and spells in more than one line). After this task, General holds no Devourer spell.
- Since 2026-10-03 form abilities are learned permanently (`Mgr::LearnKits`, cast only in their shape), so they
  stay in the spellbook: the Skinchanger tab will be long; keep kit spells grouped per shape (SkillLineAbility order).
- Skills for new characters (`playercreateinfo_skills`) and existing ones (`Mgr::TeachBasics`); uninstall removes all.

## Done when (local session tests in game)
1. Three Devourer tabs with the spells above; nothing doubled; General without Devourer spells.
2. New character and Taleka both have the tabs; no "invalid skill" lines in the server log.
