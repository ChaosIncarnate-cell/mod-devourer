# 020 — Wren's Derby: the witch races

Status: built on branch `quests` (2026-10-03), not installed, not tested. Builds on task 018 C and D (Bramble joins
through "Wren's Apprentice", 9101305).

Owner's decisions (2026-10-03): rematch okay, "dont make it too gigantic"; no Bio Points, "reward actual things that
are like quests"; level 20, unlocks riding; "pick a level around level 20 zone"; Hagatha rides a mount, "not a broom";
"we are doing 3 races, that give the suggested items, and last win will give the mount of hagatha"; Derby Beast:
Primal Tallstrider; "Kakapo will be the mount".

## The story

Wren bet Hagatha that her "pet" outruns Hagatha's Kakapo. At the starting line in the Barrens Wren turns the Devourer
into the Derby Beast, a saddled bird, its companion (Bramble, or any party member) climbs on its back, and they race
Hagatha through a course of witch-fires. Three races, each unlocking the next.

| Quest | Course | Hagatha's pace | Reward |
|---|---|---|---|
| 9101360 Wren's Derby (from Wren in the In-Between, after Wren's Apprentice, level 20) | ~780 yd loop toward Lushwater Oasis | 8.5 yd/s | Apprentice Riding, Wren's Saddle, Wren's Racing Goggles, 25 silver |
| 9101361 Hagatha Wants a Rematch | ~1270 yd, through the oasis shallows | 9.5 yd/s | Hagatha's Bristle Cloak, Hagatha's Sour Toffee x3, 5 silver |
| 9101362 The Last Lap | ~1450 yd, the full course (about two minutes) | 10.3 yd/s | Bramble's Lucky Beetle, Reins of Hagatha's Kakapo, 10 silver |

The race body runs 11.2 yd/s (60%, an apprentice mount), so a clean run wins and a sloppy one loses.

## How a race goes

1. Wren (9101360) waits at the starting line on the savanna west of the Crossroads (-796, -2636, map 1).
   Gossip: "I'm ready. Let's race!" (needs one of the race quests taken, the Devourer within 40 yd of the line, out
   of combat, and a party member within 30 yd to ride; Bramble is preferred).
2. Hagatha (9101361) appears beside it on her Kakapo; only this Devourer sees her. Wren's flash: the Devourer's form
   is taken off, it gets the Derby Beast's look (creature 9101362's model), a saddle seat (vehicle 102) and +60% speed
   (stock hidden aura 22590 with its amount set). The rider is put on the seat. Bramble: "I'm the navigator!"
3. Countdown (rooted): "On your marks", 3, 2, 1, GO. The witch-fires appear (gameobject 9101360), the minimap flag
   points to the next one, and Hagatha rides the course.
4. Each fire: "Checkpoint N of M". The last fire is the starting line.
5. Win: reach the last fire before Hagatha, rider still aboard. Lose: Hagatha first, rider gone, more than 250 yd off
   course, death, or leaving the map. Either way the body, the saddle and the speed come off, the old form comes back,
   and the race can be tried again right away.
6. Turn in to Wren at the line. Race 1 also teaches Apprentice Riding (33388) and Wren's Saddle (when it exists).

## Files

- `src/DevourerDerby.cpp`, `src/DevourerDerbyIds.h` (courses, paces, lines), registered in the loader.
- `data/sql/db-world/2026_10_03_20_devourer_derby.sql` and its rows in `data/sql/uninstall/world.sql`.
- Ids: quests, creatures, gossip, npc_text, gameobjects 9101360-9101379; spawn guids 9910300-9910349.

## Waiting on other threads

- **Devourer thread:** the Derby Beast display (Primal Tallstrider, `Creature\Tallstriderprimalmount`, saddle part
  shown; its own display, not the Devourer's look) to put on creature 9101362 (until then it uses the Greater
  Plainstrider). The **Wren's Saddle** spell (a spell id, client and server rows): 1.5 s cast, outdoors, cancelled
  like a mount; effects: transform to creature 9101362 (aura 56), set vehicle id 102 (aura 296), +60% run speed
  (aura 31). Then set `SpellWrensSaddle` in DevourerDerbyIds.h. Also: build, install the SQL, restart.
  The sisters' SQL must keep to 9101300-9101359 (commit b55066f on task/017), or it deletes these quests.
- **Items and balance:** item rows 9104000 goggles, 9104001 cloak, 9104002 beetle, 9104003 toffee, 9104004 Kakapo
  reins (ids assumed, to confirm).

## To check in game

- The rider sits on the saddle (vehicle 102, attachment 0) and Bramble (a playerbot) stays on.
- Hagatha's paces against a real run; the checkpoints' ground heights; the oasis water on race 2.
- The old form comes back after the race.
