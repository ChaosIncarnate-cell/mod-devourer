# 013 — Sniff: find prey

Status: open. Base: branch `task/006-007-devourer-start` (6ab2366). Branch: `task/013-sniff`.
Read `CLAUDE.md` and `docs/design.md` first. Build only what is asked here.

## Goal (owner, 2026-10-03)
A toggle ability **Sniff** (base kit, level 1, in the Skinchanger tab once task 011 lands): while on, creatures
around the Devourer are marked so it can locate prey:
- creatures that would give a **new shape or colouring** (`Mgr::EatShape` logic: `devourer_shape_source`,
  `devourer_shape_family`, skins the player does not own yet);
- the worn shape's **favourite food** (`devourer_favourite_food`).
The two must look different. 3.3.5a has no outline shader: options are (a) a client-side visual only the player
sees (an aura with a SpellVisualKit glow applied via a per-player visible aura, or WXL later), (b) a tracking aura
(minimap dots, like Track Beasts, `SPELL_AURA_TRACK_CREATURES` cannot filter per entry), (c) server-sent addon
message with GUIDs + a Lua nameplate/target-frame marker. Pick the one that works without a client exe change,
explain the choice in docs, keep it cheap (scan radius, update every few seconds, only while toggled).

## Done when (local session tests in game)
With Sniff on, new-shape creatures and favourite food are visibly marked and distinguishable; off removes all marks.
