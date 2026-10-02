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

## Where it lives

This folder (mod-devourer `tools/modeltool`) is the only copy; `Z:\ChromaticawBots\modeltool.bat` starts it from
here. It needs `../client` (mpq, dbc, build_client_patch). The game folder is found as the first parent folder that
holds `WOW HD CLIENT` (override: env `CHROMATICAW_ROOT`). `staging\`, `work\` and `imports.json` hold client assets
and are never committed.

## For cloud sessions

No game client, database or MPQ files exist in the cloud: `find`, `import`, `pack` and the web page's model data
cannot run there. Work on the code, test the binary parsers with your own tiny hand-made fixtures if needed, keep
`python -m py_compile *.py` clean, and say in the PR what the owner must test locally.

## Settings: auto-bind (2026-10-03)
**Settings** (right panel) holds auto-bind rules, saved in `settings.json`: "models that have BattleRoar (first found of
a list) → these emotes play it" (default: /angry /cackle /growl /insult /roar). **Auto-bind** next to Pack applies them
to the open model (`mt autobind <model>` on the command line); with "also when importing" ticked, wow.export imports
get them too. Emotes the model has its own animation for, and links you made yourself, are left alone. Several
emotes share one animation (/angry = /insult = EmoteRude, /cackle = /laugh), so binding one binds them all.
Rules can also name **animations** (not only /emotes): e.g. "Sitting -> sleeping": SitGround, EmoteSitGround play
Sleep (or KneelLoop). 18 default rules (sit/sleep/kneel each way, eat/loot, beg/cower, cheer, talking, spell cast /
ready, stun, swim idle); "only where it would otherwise just stand" (on by default) keeps a fallback that already
plays something better. A rule's source must be a real sequence, not an alias (Voidcreeper's Cower = Sprint).
Default rules you delete stay deleted (`defaults_seen`); **+ Missing default rules** brings them back.

## Colourings with several skin slots (2026-10-03)
A model can take up to 3 skin textures (e.g. body + glow1 + glow2). `<model>_red`, `<model>_glow1_red`,
`<model>_glow2_red` are ONE colouring "red"; the manifest tells which file sits in which slot. Before this, each file
was its own colouring and the body texture was put into every slot (glow layers drawn with the body: doubled,
see-through plates).

## Parts, recolour, custom skins (2026-10-03, `parts.py`)
Click the model (or a line under **Parts**): the part pulses and a panel opens. A part = one draw call of the first
.skin. **See-through** (a constant texture-weight track on its own global loop; opaque → alpha blend), **Hide/Show**,
**How it is drawn** (the part gets its own material: blend mode, unlit, both sides, no fog, no depth write),
**Texture** (any of the model's textures), **Recolour** (hue / saturation / brightness, only where the part lies on
its texture or all of it; previewed in the page, PIL on Apply), **Size** (the clicked bone's scale keys × factor in
every sequence, .anim files too; "↑" takes the parent bone). Edited models are saved with one .skin (header 0x44 = 1).
Converted-only models must be imported first. A recoloured fixed texture becomes `<name>_rc.blp`; a recoloured skin
texture becomes a **custom skin** (`skins.json`, display ids 1010001+, textures `<Model>_skin<id>_<slot>`), packed as
a copy of the base display. **Skins** lists the client's displays of the model, imports and custom skins (right-click
a custom one: rename / delete). **Reset changes** now also resets the .skin and .anim files (imports: back to the
converted files). Test without touching work\: env `MODELTOOL_WORK=<folder>` (skins.json goes next to it).
