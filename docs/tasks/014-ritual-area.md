# 014 — The In-Between: a ritual casting area instead of a summoning circle

Status: open. Base: branch `task/006-007-devourer-start` (6ab2366). Branch: `task/014-ritual-area`.
Read `CLAUDE.md`, `docs/witch-sisters.md` first. Build only what is asked here.

## Goal (owner, 2026-10-03)
"The summoning circle isn't quite right, make it a ritual spell casting area." Where the Devourer arrives in the
In-Between (map 35, around -98, 150, -40.2; gameobject 9101309 now, spawned by `tools/witch_sisters.py`), build a
ritual place with stock 3.3.5a gameobjects: a ritual circle/rune decal, candles, braziers, standing stones or
totems, a cauldron, ritual books; the sisters stand at it and **channel** a spell at the Devourer while it is
pulled in (stock channel visuals, e.g. ritual/summoning beams). Keep within the room, nothing floating or clipping.
List every gameobject entry used with its display/model so the owner can check it in game.

## Done when (local session tests in game)
The arrival spot looks like a witch's ritual being cast; the sisters channel at the Devourer on arrival.
