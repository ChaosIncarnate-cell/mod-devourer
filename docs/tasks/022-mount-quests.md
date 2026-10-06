# Task 022: the mount quests (Wren's Menagerie)

The quests behind the mounts thread's picked ideas (Parrot "Mounts - Quest Ideas", version 3, pick round 2026-10-06).
The mounts thread built the reins items (9304xxx), the Breeding Pen (9309xxx), the grown-beast quests (9308101-9308110),
the alpaca and the achievements (9308401-9308530); this task builds the quests for the other ideas, in the lantern
quests' style (task 021): every quest is something only a Devourer, or only this world, could do.

## Ids
- quests 9109000-9109399, credit creatures 9109400-9109899, own creatures 9109900-9109979
- gameobject templates 9109000-9109199, gameobject guids 9921000-9921999, creature guids 9922000-9922999
- rewards: the reins from "Mounts - How to get them" (first colour of a family; the others come from the Breeding Pen)

## The frame
Wren's WANTED board stands by the sisters in the In-Between (gameobject questgiver, spot A -98,150 nearby). Every idea
starts there; the quests run in the world and end back at the board or at the creature itself.

## What the engine learns for this (DevourerQuests.cpp v3)
- visits and touches that need **night** (game time 21:00-06:00), **dawn** (05:00-08:00), **walking** (no run, no
  mount), **no flying mount**, **a shape** (touches too), **Sniff on / Sniff off**, **standing still for N seconds**
- **followers that stay** until the quest ends (the chick, the sapling, the pups, the stable boy, the ducklings)
- **letters**: a quest completed sends server mail after a delay (the egg's chick, Bramble's crash notes)
- **fish** counted from the loot hook while the ottuk is near
- **holiday gates** through conditions (Winter Veil 2, Lunar Festival 7, Noblegarden 8, Hallow's End 12)
- **creature gossip** for the quests' own creatures (riddles, the imp's bargain, the fel machines' logic)
- the phoenix ember's achievement criteria (9308496) when it reaches the mountain's mouth without going dark
- **talking creatures count once each**: ten machines means ten machines, not one machine ten times
- **visits with a height floor** (`above`): the top of Wyrmrest, the Black Temple's cliffs, not the foot of them

## Heights
Spawns written with z 0.0 take the ground height from `tools/quest_heights.json` ("map x y" -> z). The heights come
from the server's own map files (terrain), or the nearest stock creature on the same continent when the spot is inside
a city floor the terrain does not have. The tool that measures them reads the local server data, so it runs on the
owner's PC (`tools/maps/heights.py`, with `tools/maps/wq.py` for the map files); the generator stops with a clear message when a spot
has no height yet. It also flags spots in water and on steep slopes.

## Changes after review
- Zack 2026-10-06: **ideas 39-58 are for later**. `mount_quests_c.py` stays written; `LATER = True` in
  `mount_quests.py` keeps it out of the build (105 quests in the install).
- Zack 2026-10-06: **every quest gives the Devourer a mount or a form.** The 26 steps without a mount give a colouring
  that has to be earned (`FORMS` in `mount_quests.py`), unlocked at turn-in through `Mgr::Unlock`; the generator stops
  if a mount quest gives neither.
- Idea 7: the mounts thread's finds (2,477 Sniff spots, Wren's turn-ins 9308121-9308133) hand out 13 of idea 7's
  mounts. These quests no longer reward them: two rumour quests (9109030, 9109031) teach the smell and point at the
  finds; the explorer's diary chain keeps the camels, the dunetrekker and the hyena.
- Idea 38: no daily quests (a daily cannot be a chain's previous quest); one petal a season instead.

## The ideas, chain by chain
Status: D = designed here, B = built in tools/mount_quests_*.py, X = deferred to another system (noted).

| Idea | Quests | Status | Needs |
|---|---|---|---|
| 5 A Letter From the Egg | 9109010-9109016 | B | letters (mail with delay); the chick follows |
| 6 Five Shards in Eight Hours | 9109020-9109025 | B | shard objects touched as a Flutterer, 8-hour quests |
| 7 Finds of the World | 9109030-9109034 | B | Sniff-only finds, the explorer's diary chain, camels and hyenas on tracks; rumours from the LLM thread later |
| 8 Carrying the Light | 9109050-9109054 | B | lantern objects, a carried state that slows, the cauldron |
| 9 Wear the Right Shape | 9109060-9109069 | B | among (shape), hold still, feed, the oldest follows |
| 10 Hagatha's Patchwork Familiar | 9109070-9109076 | B | devour parts, the cauldron picks the result |
| 11 Hagatha's Thin Places | 9109080-9109085 | B | five candles, a void creature each |
| 12 Postcards That Talk Back | 9109090-9109091 | B | six visits, the companions asked |
| 13 The Lighthouse Line | 9109100-9109105 | B | night touches, the pier |
| 14 Ring the Peaks | 9109110-9109115 | B | bells with no flying, one hour for all four |
| 18 Otto Would Be Proud | 9109120-9109123 | B | fish counted with the ottuk near |
| 19 Lost Kittens of Dalaran | 9109130-9109131 | B | eight hidden kittens that mew |
| 20 Wren's Crow and the Torn Spelltome | 9109140-9109147 | B | seven pages, riddles, Pilfer (extras 9108002) |
| 23 Junk Into Jets | 9109150-9109154 | B | machines with three bolts (gossip), knockback |
| 26 The Knight Without a Horse | 9109160-9109167 | B | armour pieces, dawn at the chapel, the knight rides |
| 27 The Undead Stable Boy | 9109170-9109175 | B | the boy follows to the stalls; Hallow's End riddle |
| 28 Fel Rehab | 9109180-9109189 | B | fel beasts eaten clean (a credit on hit, not kill), the machines' gossip debates |
| 29 The Wandering Ancient | 9109190-9109195 | B | the sapling follows, grows at each rest |
| 31 Winter Veil | 9109200-9109204 | B | holiday-gated; chimneys, five cooks, /shoo Wren |
| 34 Noblegarden: The Giant Egg | 9109210-9109212 | B | an egg that hops when nobody looks (facing check) |
| 36 Wren's Broom Lessons | 9109220-9109224 | B | dust bunnies, hover still over the pond, the loop |
| 38 The Snail That Eats the Seasons | 9109230-9109235 | B | four daily petal quests, the last petal decides |
| 39 The Elemental Kit | 9109240-9109245 | B | four carries with a timer, the shelf |
| 41 Ragnaros's Lost Pups | 9109250-9109256 | B | coals, the walk, the mothers, the ember (achievement 9308496) |
| 44 The Dragon Pilgrimage | 9109260-9109267 | B | one test per shrine, the egg dive |
| 45 Blessing of the Loa | 9109270-9109275 | B | ten spiders' bites, the fall, the footrace, the roar |
| 47 Hagatha's Trials of Craft | 9109280-9109285 | B | the glide, footprints with Sniff off, the apron, the imp |
| 48 The Faire | 9109290-9109299 | B | one game per prize, first versions in the hall; the full Faire when the pocket exists |
| 49 Bramble's Salvage Yard | 9109300-9109309 | B | parts at the wrecks, a test lap each |
| 50 Silithid Secrets | 9109310-9109312 | B | the scent from devouring, walking only, four stones |
| 53 The Moon Remembers | 9109320-9109326 | B | night, the reflection's three emotes, five moonwells |
| 54 Wren's Duck Pond | 9109330-9109332 | B | /whistle the eggs, walk the line home |
| 55 Lunar Festival | 9109340-9109343 | B | holiday-gated; carry the spirits with your back to the wind |
| 57 Banners of the Old Horde | 9109350-9109356 | B | four banners, four camps, the ogre waves |
| 58 Bramble's Maiden Flights | 9109360-9109366 | B | a letter per flight, the wreck, the ride home |
| 4 The Witch's Labyrinth | - | X | the cellar rooms behind gate G (terrain thread); doors by shape are easy once the rooms exist |
| 15 The Skyriding Gauntlet | - | X | Derby courses in the sky (DevourerDerby.cpp, second step) |
| 21 Wren's Derby: new courses | - | X | Derby courses (DevourerDerby.cpp, second step) |
| 24 The Pet Battle Circuit | - | X | the pet-battle mod's win hook |
| 56 The Rat Race | - | X | a Derby course where you must lose (second step) |
