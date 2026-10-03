# 020 — Wren's Derby: the witch race quest (concept for approval)

Status: concept, waiting for the owner's yes (2026-10-03). Builds on task 018 C and D (Bramble already joins through
"Wren's Apprentice", 9101305). Nothing here is built yet.

## The story in one breath

Wren has bet Hagatha that her "pet" can outrun Hagatha's broom. Hagatha took the bet. Wren turns the Devourer into a
big two-seat beast, Bramble climbs on its back to "navigate", and the three race across the Mulgore plains.

## Quests (IDs 9101360+)

### 9101360 Wren's Derby (from Wren, In-Between; needs Wren's Apprentice done, level 20+)

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

**Rewards** (owner, 2026-10-03: "dont reward bio points, reward actual things that are like quests"): experience,
silver, **Wren's Saddle** (the Derby Beast spell, see below) and a choice of one level-20 green:
- *Wren's Racing Goggles* (cloth head, Intellect and Stamina)
- *Hagatha's Bristle Cloak* (cloak, Agility and Stamina)
- *Bramble's Lucky Beetle* (neck, Strength and Stamina; "it might still be alive")

Wren's Saddle: a spell that lets the Devourer become the Derby Beast anywhere outdoors and carry one party member on
its back (a two-seat mount that is you).

### 9101361 Rematch! (repeatable, from Wren at the starting line, after 9101360)

> Hagatha wants a rematch. She ALWAYS wants a rematch.

Same race, Hagatha a little faster each time you win; reward: silver and a stack of *Hagatha's Sour Toffee* (food, a short run-speed buff). Owner (2026-10-03): "rematch is okay, dont make it too gigantic": the course stays short, about two minutes, and the beast stays normal mount size. Your best time is remembered and Wren
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

The reward items (goggles, cloak, beetle, toffee) are designed, balanced and implemented by the Items and balance
thread; the quest only references their item IDs once they exist. Wren's Saddle stays with the quest.

## Owner, 2026-10-03: higher level, unlocks riding

"lets set it higher for the level, and let us be able to unlock mount or riding skill." Proposal: the Derby opens at
level 20 (where 3.3.5 Apprentice Riding starts). Winning teaches Apprentice Riding for free, and Wren's Saddle is the
Devourer's first mount (the Derby Beast, two seats). Because Mulgore is a level 1-10 zone, the course moves to the open
savanna of the Northern Barrens around the Crossroads (level 10-25), still short (about two minutes). Riding and
mount items go through the Items and balance thread.

## Build note: the seat

Model scouting (2026-10-03): no candidate model has the stock passenger attachments 13/14. Because the player *is*
the beast, the plan is a transform to the chosen model plus aura 296 (set vehicle id) with **vehicle 102**, which has
one passenger seat on attachment 0 (the saddle point). That works with every candidate (Primal Tallstrider, Ardenweald
Toad, Amani Pangolin, Rocket Turtle, Broodmother shrunk to about a third) with no model edit and no client change.
Vehicle 102: one seat, 1541, on attachment 0, offset (0.15, 0, -0.08), flags 0x0200840F (no CAN_CONTROL,
CAN_ENTER_OR_EXIT). Primal Tallstrider (Creature\Tallstriderprimalmount) has its saddle at attachment 0 = (-0.29, 0, 2.36).
Still to check while building: which creature uses vehicle 102 in the DB, and how Bramble's ride pose looks in game.
Renders: Z:\ChromaticawBots\Parrot\renders\derby-beast\.

## Owner, 2026-10-03: three races, Hagatha's mount for the last win

"give Hagatha also a mount she is using for the race, we are doing 3 races, that give the suggested items, and last
win will give the mount of hagatha." This replaces the single Derby + Rematch:

| Quest | Race | Hagatha | Reward |
|---|---|---|---|
| 9101360 Wren's Derby | short loop south of the Crossroads | easy pace | Apprentice Riding, Wren's Saddle, Wren's Racing Goggles, 25 silver |
| 9101361 Hagatha Wants a Rematch | longer loop, a jump over the creek | faster | Hagatha's Bristle Cloak, Hagatha's Sour Toffee x3 |
| 9101362 The Last Lap | the full course, about two minutes | her best | Bramble's Lucky Beetle and **Hagatha's broom** as a mount |

Each race unlocks the next. Hagatha flies all three on her broom, so the reward is the mount the player raced against
all along. The items, the broom's reins and their balance belong to the Items and balance thread.

Place (owner: "pick a level around level 20 zone"): the Barrens, on the open savanna between the Crossroads and
Lushwater Oasis, where the wildlife is about level 17-22. The start line stays outside the town so the Crossroads
guards don't get involved.
