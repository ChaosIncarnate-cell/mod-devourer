# Sniff (task 013)

A toggle ability in the Devourer's base kit (level 1, spell 9100995, icon of Track Beasts). While it is on,
creatures within 40 yards are marked on the Devourer's client:

| Mark | Meaning |
|---|---|
| gold star | eating it gives a **new shape or colouring** (same test as `Mgr::Unlock`, via `Mgr::MealShape`: `devourer_shape_source`, else `devourer_shape_family` + `devourer_skin`) |
| green triangle | it is the worn shape's **favourite food** (`Mgr::IsFavouriteFood`, `devourer_favourite_food`) |

A creature that is both gets the star. Creatures already fed on (`State::Eaten`), pets, guardians, totems and
triggers are never marked. Living creatures and corpses are both marked.

## The choice: addon messages + Lua marks (option c)
- (a) a visible aura/visual only the player sees: the server cannot send one aura packet to one player without
  the aura being real on the creature, and a glow needs a client SpellVisualKit we would have to ship.
- (b) a tracking aura: `SPELL_AURA_TRACK_CREATURES` filters by creature type only, never per entry, so it cannot
  tell new prey from old.
- (c) **chosen**: works with the stock client, no exe change, and the data is exact. The client addon already
  exists (`tools/client/lua/DevourerMenu.lua`, prefix `DVR`), so nothing new is packed into the MPQ.

Limits of (c), on purpose: the marks sit on **nameplates** (the player turns them on with `V`; "show enemy names")
and on the **target frame**, and they are matched by creature **name**. Two creatures with the same name get the
same mark even if only one of them gives a new colouring (the star wins over the triangle). Nameplates only
exist for creatures the client currently draws.

## Cost
Only while the aura is on: one grid scan of 40 yards every 3 s (`SniffInterval`) per sniffing Devourer, at most
60 names sent, packed into a few addon messages. Nothing runs without the aura.

## Protocol (prefix `DVR`)
`Q` scan begins, `P:<N|F>:<name>|<name>|...` names (as many lines as fit 240 bytes), `R` scan ends (the client
takes the marks; they expire after 10 s without a refresh), `Z` Sniff is off (clear everything).

## Files
`src/DevourerSniff.cpp` (scan), `spell_devourer_sniff` + aura script in `src/DevourerScripts.cpp` (toggle:
casting with the aura on removes it; removal sends `Z`), `Mgr::OnUpdate` timer, `tools/start_kit.py` (spell row,
script name), `tools/spellbook.py` (spellbook line), `tools/client/lua/DevourerMenu.lua` (marks).
Uninstall: the spell row is inside the `spell_dbc` range the uninstall already deletes.

## Rerun after merging (the cloud session has no Spell.dbc)
`python tools/start_kit.py --spell-dbc <server>/data/dbc/Spell.dbc` and `python tools/spellbook.py ...`, then
rebuild the client patch: the spell (and its SkillLineAbility row) is only in the SQL after this.
