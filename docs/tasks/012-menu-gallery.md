# 012 — Menu: gallery models, colourings, Bio Points, unlock requirements

Status: open. Base: branch `task/006-007-devourer-start` (6ab2366). Branch: `task/012-menu-gallery`.
Read `CLAUDE.md`, `docs/design.md`, `docs/menu.md` (if present) first. Build only what is asked here.

## Goal (owner, 2026-10-03)
1. **Gallery colourings:** the gallery lists no colouring options; show every colouring a shape has (owned ones
   usable, others greyed with how to get them).
2. **Gallery models:** a 3D preview (`DressUpModel`/`PlayerModel` with `SetDisplayInfo` or `SetCreature`) of a
   shape and its colourings, **only once the shape is unlocked**; locked shapes show a silhouette/placeholder.
3. **Bio Points per form** in the menu (shapes tab and gallery): current BP and what the next growth needs
   (`character_devourer_growth`, `devourer_evolution`).
4. **Unlock requirements in the menu and infos:** for every shape (gallery + tooltip): where to find it
   (`_hints`/zone), favourite food, its abilities, and the exact requirement (devour X / quest / evolution: BP,
   level, tasks). GM/admin "unlock all forms" already exists (`A` message): keep it.
- Server: `Mgr::SendMenu` (DevourerMgr.cpp, messages C/A/G/H/B/S/K/E); client: `tools/client/lua/DevourerMenu.lua`
  (built into patch-Z.MPQ by `tools/client/build_client_patch.py`). Add message types as needed; addon messages
  are max 255 bytes, split long lists.

## Done when (local session tests in game)
Gallery shows colourings, previews of unlocked shapes only, BP per form, and requirements for every shape.
