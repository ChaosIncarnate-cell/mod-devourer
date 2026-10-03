# 020 — Wren's Derby: the witch race quest (concept for approval)

Status: concept, waiting for the owner's yes (2026-10-03). Builds on task 018 C and D (Bramble already joins through
"Wren's Apprentice", 9101305). Nothing here is built yet.

## The story in one breath

Wren has bet Hagatha that her "pet" can outrun Hagatha's broom. Hagatha took the bet. Wren turns the Devourer into a
big two-seat beast, Bramble climbs on its back to "navigate", and the three race across the Mulgore plains.

## Quests (IDs 9101360+)

### 9101360 Wren's Derby (from Wren, In-Between; needs Wren's Apprentice done, level 10+)

> Snack! Big news. I told Hagatha you could beat her broom in a race. She laughed. She laughed for a LONG time. So now
> it's a bet, and if we lose I have to clean the cauldron. With my hands. / Go to the plains of Mulgore, south of
> Bloodhoof. I'll meet you at the starting line. Bring Bramble, she knows the way. She says she does.

Objective: *Win Wren's Derby with Bramble on your back.*

1. At the starting line (Mulgore, the open grass south of Bloodhoof) Wren and Hagatha wait, Hagatha on her broom.
   The Devourer talks to Wren: "Ready to race".
2. Wren chants and the Devourer becomes the **Derby Beast**, a big beast with a seat on its back. Bramble hops on
   ("I'm the navigator! Left! No, the other left!").
3. Countdown 3, 2, 1. Eight glowing checkpoints across the plains (a ring of witch-fire marks each one). Hagatha flies
   the same course on her broom at a set pace.
4. Win: reach the last checkpoint before Hagatha with Bramble still on your back. Lose (Hagatha first, Bramble falls
   off, or you leave the course): Wren sighs, you can try again right away.
5. The Derby Beast lasts until the finish, then you are your normal shape again.

Not done yet: *Hagatha is already polishing her broom. Go on, Snack, back to the line!*

Handed in (to Wren, at the finish): *WE WON! Hagatha, the cauldron is yours! Both hands! / Snack, you were magnificent.
Bramble, stop waving, it's over.* Hagatha: *The broom is old. Next year, little horror.*

**Rewards:** Bio Points, some experience and silver, and **Wren's Saddle**: a spell that lets the Devourer become the
Derby Beast anywhere outdoors and carry one party member on its back (a two-seat mount that is you).

### 9101361 Rematch! (repeatable, from Wren at the starting line, after 9101360)

> Hagatha wants a rematch. She ALWAYS wants a rematch.

Same race, Hagatha a little faster each time you win; small Bio Points reward. Owner (2026-10-03): "rematch is okay, dont make it too gigantic": the course stays short, about two minutes, and the beast stays normal mount size. Your best time is remembered and Wren
tells you when you beat it.

## How it works (for the build)

- **The Derby Beast** is the player's own body as a mount: a transform to the beast model plus the stock "player is
  a vehicle" aura with a stock two-seat vehicle, so the passenger sits on the beast's back. Bramble is put on the
  seat by the script. The server core already supports both; first job of the build is to try it in game.
- **The beast's look needs your approval first** (render + concept). Candidates from models the client already has,
  with a back seat that fits: a mammoth, a kodo, or a big riding wolf. I will render the picks for you.
- **Course:** 8 invisible checkpoint markers with a witch-fire ring visual, Hagatha on waypoints, Wren as a race copy
  at the start/finish. New creatures, gossip and texts all inside 9101360-9101379, in a new script file
  (`DevourerDerby.cpp`), so the sisters' script is not touched.
- **On screen:** checkpoint count and timer through the stock world-state counters (no client change). Optional
  later: a `wxl-race` WarcraftXL extension (arrow to the next checkpoint, standings), reusable for other races. That
  one goes into the client, so it needs your yes separately.
- **Any party member** can ride instead of Bramble on Rematch; the first race needs Bramble.

## To decide

1. The beast: mammoth, kodo or wolf (renders follow).
2. Course place: Mulgore plains (proposed) or somewhere else.
3. Wren's Saddle as a permanent reward: yes or no.
