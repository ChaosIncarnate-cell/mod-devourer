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

## This copy

Mirror of the live tool in `Z:\ChromaticawBots\tools\modeltool` (paths in `modeltool.py` are relative to that
location: `ROOT = ..\..`). `staging\` and `work\` hold client assets and are never committed. `modeltool.bat` belongs
in `Z:\ChromaticawBots\` (it `cd`s into `tools\modeltool`).
