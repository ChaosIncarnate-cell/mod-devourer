# 002 — Port the module code

Status: open (can run in parallel with 001; assume `CLASS_DEVOURER = 10` exists or define it locally)

## Goal
`src/` compiles as a normal AzerothCore module on the Playerbot fork with no CoA engine code, and keeps the
CoA gameplay (see `docs/coa-original/README.md`).

## Scope
- Remove `#include "AscensionSpecialization.h"`; replace `SpecOf()` with the talent-tree rule from the design
  (tree with most points; `Player` talent APIs of this fork).
- `IsDevourer()`: class id from config (`Devourer.ClassId`, default 10) instead of 20.
- Remove CoA-only assumptions (CoA hands out starting items: here the module or `playercreateinfo_item`
  gives the Idol of the Sethrak; CharacterAdvancement ids).
- Loader function must match the folder name: `Addmod_devourerScripts()`.
- Keep `Devourer.Enable` as the master switch; with it off the module does nothing.
- Keep spell ids 9100001-9100899 unless there is a collision in the standard 3.3.5a Spell.dbc (check the
  upstream `spell_dbc` / DBC documentation).

## Done when
Compile-check passes against upstream headers; local build passes; with `Devourer.Enable = 0` the server runs
unchanged.
