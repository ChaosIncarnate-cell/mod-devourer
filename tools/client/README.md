# Client patch (task 004)

One command builds `patch-Z.MPQ`, the only client file the Devourer needs, from the owner's own 3.3.5a client
(with its HD patches) and the local CoA files. Nothing Blizzard- or CoA-made is committed: the tool reads those
files at build time, and its output goes to `tools/client/out/` (git-ignored), the client's `Data` folder and two
git-ignored SQL files.

```
.\tools\client\build-client-patch.ps1 -SelfTest
.\tools\client\build-client-patch.ps1 -Client "C:\WoW" -Coa "D:\CoA\Data" -ClassIcon "D:\art\devourer.png" -Install
```

or directly `python tools/client/build_client_patch.py --client C:\WoW --coa D:\CoA\Data --install` (Python 3.9+
and Pillow 9.1+; no StormLib, `mpq.py` reads and writes MPQs). Then delete the client's `Cache` folder and restart
the worldserver, so it applies the generated SQL.

| Option | |
|---|---|
| `--client` | the folder with `Wow.exe` |
| `--coa` | where the CoA models, textures and looks are: its `Data` folder (MPQs, read in load order, `patch-T`-style names included), one MPQ, or a folder of loose extracted files. Repeat it; later ones win. Without it the patch is built anyway, but the looks that only CoA has are missing (warnings list them) |
| `--class-icon` | the class icon (an image, made from the CoA emblem, or a ready `.blp`); default: a placeholder drawn by `blp.py` |
| `--name` | default `patch-Z.MPQ`. It must be one letter or digit: the 3.3.5a client loads `Data\patch-<x>.MPQ` |
| `--install` | copy it into `Data` (an earlier Devourer patch, found by its `Devourer\patch.txt`, is replaced) |

## What it builds

Every file is read from the client's archives in the client's load order, so the tool changes what the game
really uses: an HD patch's `CreatureDisplayInfo.dbc` is extended, not replaced by a clean copy.

- **DBCs** (`DBFilesClient`)
  - Rows of the committed SQL, the same values the server gets: `ChrClasses` 10 (Hunger = rage), `TalentTab`
    900-902, `Talent` 9000-9019, `Spell` 9100000-9100899, `CreatureModelData` 902038-902045, `CreatureDisplayInfo`
    991001-991065, the spellbook tab (`SkillLine` 900, `SkillRaceClassInfo` 91000, `SkillLineAbility` 91001-91999,
    task 008). `dbc_layouts.json` maps AzerothCore's `*_dbc` columns onto the DBC fields (same order). The
    client reads the string of its own locale, so empty locale slots get the enUS text.
  - `SkillRaceClassInfo`, `SkillLineAbility`, `CharStartOutfit`: the warrior's skills and starting outfit for class
    10, by the rules in `tools/build_class_dbc_sql.py` (imported, not copied), and the same SQL file that script
    writes: `2026_09_30_05_devourer_class_dbc.generated.sql`.
  - `CharBaseInfo`: every race may be a Devourer. The gt tables: class 10 = the warrior, as the server install does.
  - Looks the SQL uses that neither the SQL nor the client has (the Sethrak 200004, the Sethrak camp 80018, 80305,
    280018, the Twinfangs 991040, 991045) are copied from the CoA DBCs, with their models (402214 ...), also as
    server SQL: `2026_09_30_06_devourer_coa_looks.generated.sql` (the uninstall removes them through
    `devourer_client_rows`).
- **Models and textures**: for every display the patch adds, its `.m2`, `.skin`, `.anim` files and textures (from
  the model's own texture table and the display's texture variations) are copied from the CoA sources unless the
  client already has them. Files found nowhere are listed as warnings (e.g. a Sethrak colouring that
  `tools/coa/skins/recolor.py` has not made yet).
- **Interface** (`interface.py`, applied to the client's own files):
  - `GlueXML\CharacterCreate.xml`: an 11th class button (the 3.3.5a screen has one per class, 10).
  - `GlueXML\CharacterCreate.lua`: `MAX_CLASSES_PER_RACE` 11 and the Devourer's own icon
    (`Interface\Glues\CharacterCreate\UI-CharacterCreate-Devourer.blp`) on its button and in the class panel.
  - `GlueXML\GlueStrings.lua`: description, role lines, the "not for this race" tooltip.
  - `FrameXML\Constants.lua`, `WorldStateFrame.lua`: class colour (bronze) and icon coordinates, so lookups by
    class (who list, chat, LFG, arena, score board) find the Devourer. In game frames its icon is an empty cell
    of Blizzard's class icon sheet for now.
  - `AddOns\Blizzard_RaidUI`, `AddOns\Blizzard_Calendar`: both keep one list per class and failed on a class they
    do not know (a Lua error on every raid roster update with a Devourer in the raid). The Devourer gets a list
    of its own; it has no class button there (see below).

## Checked in the cloud

`selftest.py` builds a made-up client (invented DBC rows in the real layouts, stand-in GlueXML files, an HD patch, a
locale patch, an earlier Devourer patch, a CoA folder and MPQ) and checks every DBC row against the SQL, the class
10 rules, the load order, the CoA copies and the MPQ; it runs the patched character creation Lua under Lua 5.1 with
mocked frames. `mpq.py` was cross-checked with StormLib both ways (all flags: zlib, bzip2, PKWARE, encrypted,
single unit, sector CRC, v1/v2). The SQL (install twice, uninstall) was run on MariaDB with AzerothCore's tables.

## Assumptions the local test must confirm

1. **Load order**: `Data\patch-*.MPQ` beats `Data\<locale>\patch-<locale>-*.MPQ` (AzerothCore's extractor loads
   them that way). The tool warns when a locale patch holds a file it patches; if the game then shows the old
   version, the assumption is wrong.
2. The HD patches do not replace the character creation screen. If they do, the tool stops with "not found" and
   `interface.py` needs their version.
3. The CoA DBCs have the stock 3.3.5a layouts (the tool stops if not).

## Not done yet (follow-ups)

- Class icon in game frames (raid, arena, score board): needs the icon painted into the free cell of Blizzard's
  class icon sheets. `CLASS_SORT_ORDER` is left alone: the raid and calendar frames make one class button per
  entry and have no 11th, so Devourers are not counted on a class button there.
- Other locales' texts, the achievement frame (stoneharry saw it fail
  for a new class).
