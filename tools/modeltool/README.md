# modeltool

Look into WotLK creature models, see which animation plays for what, re-link animations, import models, put
changes into the client. Start: **`Z:\ChromaticawBots\modeltool.bat`** (opens a window; commands start with `mt`).

| Command | Does |
|---|---|
| `mt find frog` | creatures (with display ids) and model paths matching a name |
| `mt anims 20025` | every animation sequence of a model, the aliases, and what each `/emote` really plays (`--all` for all emotes) |
| `mt link 20025 EmoteRoar BattleRoar` | `/roar` plays the model's BattleRoar (adds an alias sequence, like Blizzard's Fall → Jump) |
| `mt rename 20025 31 EmoteRoar` | sequence #31 becomes another animation (its other variations follow) |
| `mt reset 20025` | throw away your changes to that model |
| `mt import <model> --from <MPQ / Data folder / loose folder>` | copy a model + skins + .anim files + textures into `work\` |
| `mt work` | what is in `work\` |
| `mt pack` | put `work\` into `WOW HD CLIENT\Data\patch-Z.MPQ` (WoW must be closed; backup in `Devourer patch backups`) |

`<model>` = display id, `c:<creature entry>`, or a path like `Creature\Frog\Frog.m2`. Animation names come from
AnimationData.dbc (or use the number).

How it works: the client finds an animation through a hash table in the model (slot = id % size) and checks the
sequence's id, then falls back along AnimationData's fallback chain (most emotes end at Stand). So a missing
animation can't just be pointed elsewhere: `link` appends an alias sequence and gives every animated track an empty
entry for it. Changed models live in `work\` until `pack`. The Devourer client patch tool rebuilds patch-Z from
scratch: run `mt pack` again after it.

Not yet: 3D preview (use WoW Model Viewer / wow.export to look), texture/skin editing, model scale (for Devourer
shapes the scale is `devourer_shape.scale` on the server).

## The page (2026-10-02)
`Z:\ChromaticawBots\modeltool.bat` starts `server.py` and opens http://localhost:8765: search on the left, the
model in 3D (drag to turn, wheel to zoom), animations on the right (click to play, **rename**), the emote table
(what each `/emote` wants and what this model really plays; **link** buttons), **Reset changes** and **Pack into
game**. `viewer.html` is the page (three.js), `server.py` serves the model data and calls `modeltool.py`.

## From wow.export (2026-10-02)
Models wow.export saved as RAW (`C:\Users\Anwender\wow.export`, newer MD21 format) show in the page's left list
**From wow.export**. Steps on the right: **1. Convert & show** (`convert.py`: our client's format into `staging\`,
colourings `<model>_<colour>.blp/.png` become DXT5 BLPs; the page lists what had to change), **2. Import**
(`imports.py`: copies into `work\`, model data 904001+, one display 994001+ per colouring, size, sounds borrowed from
a display; kept in `imports.json`), **3. Pack into game** (adds the displays to the client's CreatureModelData /
CreatureDisplayInfo inside patch-Z and to the server's `*_dbc` tables; restart the server). Effects: particle emitters are converted (gravity unpacked, first texture of multi-texture emitters), ribbons kept;
emitters that spawn little models are left out. Newer shaders: classic shader instead. The 3D view does not draw effects.

## Devourer forms (2026-10-02)
The page's second tab, **Devourer forms**, edits the Devourer's forms (shapes 5-15) and the base kit: pick a form on
the left, its model shows in the middle, the editor is on the right.

- **The form**: name, look (display id; *Look at it* shows it), size, the base colouring's name, icon.
- **Each spell** (click to open): name, level, icon, Anima cost, cooldown, cast time, range, duration, stacks,
  school, its three effects (effect, aura, amount, targets, radius, tick, misc values, spell it casts, mechanic),
  tooltip and buff text, and every other `spell_dbc` field under *Every field*.
- **Animation**: what the form plays while casting, when cast and while channelling. The list shows which
  animations the model has (green: its own; yellow: the model falls back to another). ▶ plays it on the model.
- **Look from another spell**: find any spell by name and use its visual effects or its icon.
- **Icons**: pick one of the game's (search by name), or add your own image (it becomes a 64x64
  `Interface\Icons\Devourer_<name>.blp` in `work\`).
- Spells marked *"Part of what it does is in the module's code"* have a script (`src/Devourer*.cpp`): the numbers
  here still apply, but what the script does stays the same.

**Save** writes your changes into `tools/form_edits.json` (commit it: it is the record of your changes) and runs
`tools/start_kit.py` again (its SQL and `docs/start-kit.md`). Only what differs from the code is kept; *Back to the
code's version* drops a spell's changes. **Pack into game** (WoW closed) then puts into `patch-Z.MPQ` the
Devourer's spells from that SQL, an own visual for every spell whose animation changed (SpellVisual 91000-91199,
SpellVisualKit 91000-91599: copies of the template's, so its glows and sounds stay), your icons (SpellIcon
91000-91999), and runs the SQL on the world database. Restart the worldserver and delete the client's Cache.

`forms.py` is the editor's side of the server, `spell_enums.json` the effect / aura / target names
(`make_spell_enums.py` reads them from the core's headers). The stock spells the abilities copy come from the
server's `Spell.dbc` when the tool finds it (`server\data\dbc` below the game folder, or env
`CHROMATICAW_SPELL_DBC`), else from the client's. `python selftest_forms.py` checks the editor against a made-up
client (needs Pillow).

The Devourer client patch tool rebuilds patch-Z from scratch: run Pack again after it (it puts the animations and
icons back). Shapes 1-4 (the CoA forms in `tools/coa/build_devourer_spells.py`) are not in the editor.

## Where it lives

This folder (mod-devourer `tools/modeltool`) is the only copy; `Z:\ChromaticawBots\modeltool.bat` starts it from
here. It needs `../client` (mpq, dbc, build_client_patch). The game folder is found as the first parent folder that
holds `WOW HD CLIENT` (override: env `CHROMATICAW_ROOT`). `staging\`, `work\` and `imports.json` hold client assets
and are never committed.

## For cloud sessions

No game client, database or MPQ files exist in the cloud: `find`, `import`, `pack` and the web page's model data
cannot run there (`selftest_forms.py` can: it makes up its own client). Work on the code, test the binary parsers with your own tiny hand-made fixtures if needed, keep
`python -m py_compile *.py` clean, and say in the PR what the owner must test locally.
