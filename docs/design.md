# Design: the Devourer as a real, removable class 10

Decided with the owner on 2026-09-30: the Devourer is a **real class chosen at character creation**, added
**next to** the existing classes (none replaced), built so it can be **removed without rebuilding** the server.

## Why class 10 and not a module on a base class
The owner wants it in the class menu. 3.3.5a leaves class id 10 unused; the server already sizes its class
arrays for 12 (`MAX_CLASSES`). stoneharry/WoW-Custom-Class added a 12th class ("Engineer") to 3.3.5a without
replacing one and without a client exe patch; we use the free slot 10 to keep core changes minimal.

## Four layers

| Layer | Content | Removal |
|---|---|---|
| 1. `core-patch/` | class 10 playable (`CLASSMASK_ALL_PLAYABLE`), `CLASS_DEVOURER = 10`, rage as power, stat formulas and per-class arrays for index 10 (like a warrior), playerbots never rolls class 10 | stays applied; dormant without class-10 characters |
| 2. module `src/` | the CoA gameplay: Devour, shapes (Sethrak, Berserker, Vashnik, Baby Berserker) with 4 abilities + passive each, Hunger, shared shift cooldown, colourings, growth/Bio Points/evolution, specs Glutton / Skinchanger / Brood | `Devourer.Enable = 0` or remove the folder |
| 3. SQL `data/sql` + `uninstall/` | via AzerothCore's DBC override tables: `chrclasses_dbc`, `talenttab_dbc`, `talent_dbc`, `spell_dbc`, `skillline_dbc`, `skilllineability_dbc`, `skillraceclassinfo_dbc`, `charstartoutfit_dbc`, `creaturedisplayinfo_dbc`, `creaturemodeldata_dbc`, `powerdisplay_dbc`, `gt*` rows for class 10; plus `playercreateinfo*`, `player_levelstats`, `player_class_stats`, the module's own tables | uninstall SQL; converts existing class-10 characters to warriors first |
| 4. one client MPQ | DBC rows (ChrClasses, CharBaseInfo, TalentTab, Talent, Spell, SkillLine..., CreatureDisplayInfo...), GlueXML character creation (button, MAX_CLASSES_PER_RACE, strings), FrameXML class colours/icons, models | delete the file |

## Replacing the two CoA dependencies
- `IsDevourer(player)`: `player->getClass() == CLASS_DEVOURER` (10), class id configurable.
- `SpecOf(player)`: the three specs become the class's **three talent trees**. The spec is the tree with the
  most points spent (ties: none). The spec abilities are learned/removed exactly as before (checked every 3 s).
  The Glutton talents that CoA had as CharacterAdvancement entries become real `talent_dbc` rows.

## Open questions (resolve in the tasks)
- Which races may be Devourers (CharBaseInfo + `playercreateinfo`)? Default proposal: all races.
- Starting zone/position: the race's normal start.
- Class colour and icon: from the CoA emblem, recoloured/resized locally (asset stays local).
- Talent/achievement UI crashes seen by stoneharry when class data is missing: fill all class-indexed tables.
