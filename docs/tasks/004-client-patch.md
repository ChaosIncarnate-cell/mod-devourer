# 004 — Client patch tooling

Status: done in cloud (PR), waiting for local build/test. Tool and test plan: `tools/client/README.md`

## Goal
One command, run locally, that builds `patch-Devourer.MPQ` (name to be chosen so it loads after the HD patches)
for the owner's HD 3.3.5a client, containing everything the client needs for class 10.

## Scope
- Adapt `tools/coa/*` to a standard 3.3.5a base: read the DBCs the client actually uses (the HD patches may
  override some, e.g. CreatureDisplayInfo; the tool must merge into those, not into a clean copy), append the
  Devourer rows, write the MPQ.
- DBCs: ChrClasses, CharBaseInfo, TalentTab, Talent, Spell (+ SpellIcon if new icons), SkillLine,
  SkillLineAbility, SkillRaceClassInfo, CharStartOutfit, CreatureDisplayInfo, CreatureModelData.
- Interface: GlueXML CharacterCreate (new class button, texcoords, MAX_CLASSES_PER_RACE, GlueStrings),
  FrameXML class colours / class-indexed tables, class icon. Write them as small patch scripts that modify the
  client's own files at build time; never commit Blizzard's files.
- Models/textures are copied locally from the CoA folders (paths as parameters), never committed.
- Output also the server-side DBC rows as SQL (to stay identical to task 003).

## Done when
Local session builds the MPQ, the character creation screen shows the Devourer with icon and description,
and selecting it does not throw Lua errors.
