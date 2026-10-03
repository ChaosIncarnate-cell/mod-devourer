#!/usr/bin/env python3
"""Task 010: the Hollowmoor witch sisters -- the Devourer's trainers and its level-5 intro in the In-Between.

    python tools/witch_sisters.py

Needs no client or server files. One source for three outputs; run it again after any change:
  data/sql/db-world/2026_10_01_00_devourer_witch_sisters.sql   the sisters, the cage and their trappings, the
                                                                quests, texts, gossip, the trainer link
  src/DevourerSistersIds.h                                      the same ids and places for the module code
  docs/witch-sisters.md                                         who says what, the quests, ids and places

The names live here once (HAGATHA, WREN); every line that names a sister is built from them.

The In-Between: map 35 "StormwindPrison" (in Map.dbc as "<unused>StormwindPrison"), a non-instanced map that
no player content uses: one dark round hall of the old prison, with nothing outside its walls. The cage stands
in the middle of the hall, at the stock `game_tele` point "JailAlliance" (-98.0, 149.8, -40.4). The other
spots were picked from the server's navigation mesh for that map (floor heights included).

Ids (all removed by data/sql/uninstall/world.sql and characters.sql):
  creature_template      9101300 Hagatha, 9101301 Wren, 9101302 Wren's Snack (the rats of the first chore),
                         9101303 the void under the cage, 9101310-9101312 quest credit (never spawned),
                         9101313-9101314 the anima pests of Wren's fourth chore, 9101315 its credit
  creature (spawns)      9910200-9910202
  gameobject_template    9101300-9101309      gameobject (spawns) 9910200-9910229
  quest                  9101301-9101305 (9101305: Wren's apprentice, task 018), 9101310-9101399 the molt quests (task 018: one per evolution that has one,
                         tools/evolved_kit.py gives each evolution its quest id), 9101391-9101393 Wren's daily
                         chores (task 019: one per tier of form)
  item_template          9100110-9100112 the reagents of those chores (9100100-9100101 are the idols)
  gossip_menu / npc_text 9101300-9101301 / 9101300-9101305 (conditions on the same menus)
  creature_default_trainer: both sisters -> trainer 9101200 (its spells: tools/start_kit.py)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import evolved_kit  # noqa: E402  (task 018: the evolved forms, their molt quest ids)
OUT_SQL = REPO / "data" / "sql" / "db-world" / "2026_10_01_00_devourer_witch_sisters.sql"
OUT_H = REPO / "src" / "DevourerSistersIds.h"
OUT_MD = REPO / "docs" / "witch-sisters.md"

# --- the sisters' names: change them here, nowhere else ---------------------------------------------------------
HAGATHA, HAGATHA_SHORT = "Hagatha Hollowmoor", "Hagatha"
WREN, WREN_SHORT = "Wren Hollowmoor", "Wren"
N = {"hagatha": HAGATHA_SHORT, "wren": WREN_SHORT, "Hagatha": HAGATHA, "Wren": WREN}

# --- ids --------------------------------------------------------------------------------------------------------
NPC_HAGATHA, NPC_WREN, NPC_SNACK, NPC_VOID = 9101300, 9101301, 9101302, 9101303
CREDIT_DEVOURED, CREDIT_ROAR, CREDIT_TALE = 9101310, 9101311, 9101312
# Owner, 2026-10-02 (Parrot\to be devoured.canvas): Wren's fourth chore, the frog line's way in.
NPC_PEST, NPC_PEST_PERCHED, CREDIT_PEST = 9101313, 9101314, 9101315
PEST_SCRIPT = "npc_devourer_anima_pest"
SHAPE_BILETOAD = 14                                  # tools/start_kit.py: the form Wren's spell puts on
NPC_FIRST, NPC_LAST = 9101300, 9101399
SPAWN_FIRST, SPAWN_LAST = 9910200, 9910299
GO_FIRST, GO_LAST = 9101300, 9101399
GO_CAGE = 9101300                                   # the Devourer's own cage: summoned per player, opens at the end
Q_FEEDING, Q_TRICK, Q_TALE, Q_PESTS = 9101301, 9101302, 9101303, 9101304
Q_APPRENTICE = 9101305                              # task 018: Wren sends her apprentice along (the companion)
COMPANION = "Bramble"                               # the default of Devourer.WitchCompanion (the bot's name)
Q_FIRST, Q_LAST = 9101301, 9101399                   # every quest of the sisters (molt quests: 9101310+)
# Task 019 C (task 018 B's last bullet: "a small repeatable chore per tier"): Wren's daily chores, one per tier of form
# (1 = a starter form, 2 = a form grown out of one, 3 = grown out of that). Each wants a reagent that only comes out of
# a meal eaten in a form of that tier (module: Mgr::ChoreDrop), the reward is Bio Points for the worn form
# (module: Mgr::ChoreReward). The ids sit at the top of the range, the molt quests fill it from below.
Q_CHORE_FIRST = 9101391
ITEM_CHORE_FIRST, ITEM_CHORE_LAST = 9100110, 9100119
CHORE_COUNT = 3                                      # reagents each chore asks for
CHORE_CHANCE = 40                                    # % of meals (in the right tier) that leave one
CHORE_BP = (60, 150, 300)                            # Bio Points per tier
MENU_HAGATHA, MENU_WREN = 9101300, 9101301
TRAINER = 9101200                                    # tools/start_kit.py: the class trainer and what it teaches
CLASS_MASK = 512                                     # class 10
SCRIPT = "npc_devourer_witch_sister"

# Options the module answers (gossip_menu_option.OptionID); the rest the core handles.
OPT_TRAIN, OPT_UNLEARN, OPT_DUALSPEC, OPT_TALE, OPT_BACK, OPT_VENDOR = 0, 1, 2, 3, 4, 5
OPT_SHAPE_TALE = 6                                  # task 018: Hagatha tells the tale of the worn shape
OPT_MOUNTS = 7                                      # Wren sells the mounts the Skrill thread made (its own vendor rows)

# --- the In-Between ----------------------------------------------------------------------------------------------
MAP = 35
CAGE = (-98.0, 150.0, -40.28, math.pi / 2)          # the Devourer wakes here, facing the sisters
ARRIVE = (-98.0, 143.5, -40.21, math.pi / 2)        # where a freed Devourer comes back to (.inbetween), outside it
CAGE_RADIUS = 2.0                                    # yards it may stray from the middle before being put back


def facing(x, y, at=CAGE):
    return math.atan2(at[1] - y, at[0] - x) % (2 * math.pi)


SISTERS = [  # (entry, spawn guid, name, menu, looks like (creature entry), x, y, z)
    (NPC_HAGATHA, 9910200, HAGATHA, MENU_HAGATHA, 11872, -100.4, 153.4, -40.11),   # Myranda the Hag
    (NPC_WREN, 9910201, WREN, MENU_WREN, 2963, -95.6, 153.4, -40.11),              # Windfury Wind Witch (a harpy)
]
VOID_SPAWN = (9910202, CAGE[0], CAGE[1], CAGE[2])

# Task 014: the ritual area. These displays are stock 3.3.5a GameObjectDisplayInfo ids picked WITHOUT a client to
# look at: the owner checks each in game (README of PR) and changes the number here, then runs this script again.
# Task 016: the rune circle object (9101309, display 7881) is gone: it showed as a big blue crystal in the middle that
# the player got stuck on. The circle is the Void Zone visual under the cage now, shown smaller (VOID_SCALE).
VOID_SCALE = 0.6
BRAZIER_DISPLAY = 197      # standing brazier (the most used "Brazier"; 1291 does not exist in this client)
STONE_DISPLAY = 7017       # "Glyph Inscribed Obelisk", a rune-carved standing stone (1431 does not exist)
CHANNEL = 40671            # stock channelled beam the sisters hold on the Devourer; fallbacks: 59551, 31725
RITUAL_RADIUS = 4.5        # yards from the middle of the circle: where candles, braziers and stones stand

# Game objects: (entry, type, display, name, size, flags). Type 0 = door (the cage opens), 5 = decoration.
GO_TEMPLATES = [
    (GO_CAGE, 0, 4154, "Wren's Cage", 1.2, 0x10),           # the larger stock cage (G_Cage 03), not clickable
    (9101301, 5, 1787, "Wren's Cage", 1.0, 0),               # G_Cage 02: her cages everywhere, empty
    (9101302, 5, 216, "Bubbling Cauldron", 1.0, 0),
    (9101303, 5, 6038, "Hagatha's Lantern", 1.0, 0),
    (9101304, 5, 187, "Bookshelf", 1.0, 0),
    (9101305, 5, 107, "Book of Monster Tales", 1.0, 0),
    (9101306, 5, 6328, "Skull Pile", 1.0, 0),
    (9101310, 5, 4152, "Ritual Candle", 1.0, 0),
    (9101311, 5, BRAZIER_DISPLAY, "Ritual Brazier", 1.0, 0),
    (9101312, 5, STONE_DISPLAY, "Ritual Standing Stone", 1.0, 0),
    (9101313, 5, 107, "Ritual Book", 1.0, 0),
]
# Task 014: eight candles round the rune circle, four braziers and four standing stones on a ring outside them,
# two ritual books on the sisters' side. Floor height is the cage's: the hall floor is flat there (-40.28 .. -40.2).
RITUAL_SPAWNS = []
for _i in range(8):
    _a = _i * math.pi / 4 + math.pi / 8
    RITUAL_SPAWNS.append((9101310, round(CAGE[0] + 3.0 * math.cos(_a), 2), round(CAGE[1] + 3.0 * math.sin(_a), 2),
                          -40.28, None))
for _i in range(4):
    _a = _i * math.pi / 2 + math.pi / 4
    RITUAL_SPAWNS.append((9101311, round(CAGE[0] + RITUAL_RADIUS * math.cos(_a), 2),
                          round(CAGE[1] + RITUAL_RADIUS * math.sin(_a), 2), -40.28, None))
    _a += math.pi / 4
    RITUAL_SPAWNS.append((9101312, round(CAGE[0] + RITUAL_RADIUS * math.cos(_a), 2),
                          round(CAGE[1] + RITUAL_RADIUS * math.sin(_a), 2), -40.28, None))
RITUAL_SPAWNS += [(9101313, -99.2, 155.6, -40.1, None), (9101313, -96.8, 155.6, -40.1, None)]
# nothing stands within 2 yards of a sister (the ring would put a brazier in Hagatha)
RITUAL_SPAWNS = [r for r in RITUAL_SPAWNS if all(math.hypot(r[1] - sx, r[2] - sy) >= 2.0 for sx, sy in ((-100.4, 153.4), (-95.6, 153.4)))]
GO_SPAWNS = [  # (entry, x, y, z, orientation or None = facing the cage)
    (9101302, -98.0, 157.0, -39.93, None),                  # the cauldron behind the sisters
    (9101303, -101.9, 155.0, -40.03, None),                 # Hagatha's lantern of trapped anima
    (9101305, -102.7, 152.6, -40.15, None),
    (9101304, -105.5, 160.5, -40.21, None),
    (9101306, -103.5, 157.5, -40.02, None),
    *RITUAL_SPAWNS,
    (9101301, -92.0, 157.0, -39.93, None),                  # Wren's cages: one beside her, four along the walls
    (9101301, -108.0, 160.0, -40.12, None),
    (9101301, -88.0, 160.0, -40.11, None),
    (9101301, -108.0, 140.0, -40.31, None),
    (9101301, -88.0, 140.0, -40.24, None),
]

# Wren's pests (the fourth chore): by each of her five cages one on the floor (2.5 yards towards the middle of the
# hall) and one hovering 5 yards above it, out of reach of teeth: only a tongue gets it down. (x, y, z, perched)
PEST_HEIGHT = 5.0
PEST_SPOTS = []
for _e, _x, _y, _z, _o in [g for g in GO_SPAWNS if g[0] == 9101301]:
    _d = math.hypot(CAGE[0] - _x, CAGE[1] - _y)
    PEST_SPOTS.append((round(_x + (CAGE[0] - _x) * 2.5 / _d, 2), round(_y + (CAGE[1] - _y) * 2.5 / _d, 2), _z, 0))
    PEST_SPOTS.append((_x, _y, round(_z + PEST_HEIGHT, 2), 1))

# Stock visual-only spells the module casts (3.3.5a Spell.dbc, no effect but the look):
VISUAL_PULL = 52233        # Teleport Visual (Evil): the ritual takes hold
VISUAL_ARRIVE = 61456      # Evil Teleport Visual Only: arriving in the In-Between
VISUAL_SLEEP = 55474       # Cosmetic - Sleep Zzz: asleep in the cage
VISUAL_TRANSFORM = 24085   # Transform Visual: Wren's spell
VOID_AURA = 64469          # Void Zone Visual: the void under the cage (on the hidden creature 9101303)

# --- what they say ------------------------------------------------------------------------------------------------
# creature_text: (creature, group, line, emote, draft). All lines are first drafts in the owner's descriptions of the
# two sisters (task 010); PLACEHOLDER marks the ones written only to make the flow work. Type 12 = say.
SAY, WHISPER = 12, 15
EMOTE_TALK, EMOTE_EXCLAMATION, EMOTE_LAUGH, EMOTE_CHEER, EMOTE_POINT, EMOTE_NO = 1, 5, 11, 4, 25, 274
DRAFT, PLACEHOLDER = "draft", "PLACEHOLDER"

TEXTS = [
    # Wren, 0: heard from nowhere when the ritual takes hold (sent by the module as her whisper)
    (NPC_WREN, 0, "Found you! Hold still, Snack. This tickles. Mostly.", 0, DRAFT),
    # Hagatha, 0: the Devourer lies asleep in the summoning circle
    (NPC_HAGATHA, 0, "Hush, sister. Let it wake slowly. The ones that wake fast bite the hand that feeds them.",
     EMOTE_TALK, DRAFT),
    # Wren, 1: it wakes
    (NPC_WREN, 1, "It's awake! {hagatha}, it's AWAKE! Hello, hello, Project #9! Don't smudge the circle, the chalk is new.",
     EMOTE_EXCLAMATION, DRAFT),
    # Hagatha, 1
    (NPC_HAGATHA, 1, "So. Another hungry thing out of the In-Between. They always come back here in the end, my little "
     "horror. Back to the dark between the stars and the world.", EMOTE_TALK, DRAFT),
    # Wren, 2: before the spell
    (NPC_WREN, 2, "You eat what you kill and wear what you eat? Messy, messy! Let's give you something with proper "
     "teeth. Hold still... no, the other still!", EMOTE_LAUGH, DRAFT),
    # Wren, 3: the Warp Stalker (owner, 2026-10-01: a new form instead of the Baby Berserker)
    (NPC_WREN, 3, "Ha! Look at you! Now you see it, now you don't! Blink, blink! I'm calling you Fluffy. No, Snack. "
     "No... both!", EMOTE_CHEER, DRAFT),
    # Hagatha, 2
    (NPC_HAGATHA, 2, "A warp stalker. In the villages they tell of a beast that was never quite where you looked, and "
     "ate the shadows off the walls. Mind which stories you become.", EMOTE_TALK, DRAFT),
    # Wren, 4: the chores begin (she offers the first task)
    (NPC_WREN, 4, "Chores, Fluffy! Every pet in this house has chores. I made a list. It's a long list. It's a lovely "
     "list!", EMOTE_POINT, DRAFT),
    # Wren, 5: the snacks are tossed into the circle
    (NPC_WREN, 5, "Snacks incoming! Catch!", EMOTE_EXCLAMATION, DRAFT),
    # Wren, 6: the roar
    (NPC_WREN, 6, "THAT'S my monster! Again! No, don't, the ceiling's loose.", EMOTE_CHEER, DRAFT),
    # Hagatha, 3-6: the tale of the hungry thing (the third task)
    (NPC_HAGATHA, 3, "Listen, then. Before the villages had walls, something crawled out of the In-Between. It had no "
     "shape of its own.", EMOTE_TALK, DRAFT),
    (NPC_HAGATHA, 4, "It ate a wolf and ran on four legs. It ate a man and learned to lie. It ate a king and wore his "
     "crown, and no one noticed for a year.", EMOTE_TALK, DRAFT),
    (NPC_HAGATHA, 5, "When there was nothing left it had not been, it came back here, starving, and began to eat "
     "itself.", EMOTE_TALK, DRAFT),
    (NPC_HAGATHA, 6, "That is what you are, my little horror. Not the wolf, not the man. The hunger underneath. Never "
     "let it eat the last of you.", EMOTE_TALK, DRAFT),
    # The circle lets go (the third task handed in)
    (NPC_WREN, 7, "Out you go! Come back when you've eaten something interesting. Or someone. I'm joking! Mostly. Ha!",
     EMOTE_LAUGH, DRAFT),
    (NPC_HAGATHA, 7, "The circle lets you go. A circle is worse than a cage, hungry thing: you step out of it "
     "yourself, and choose what you become. Come back to us when you need teaching.", EMOTE_TALK, DRAFT),
    # Wren, 8: the Devourer died in the circle and is put back on its feet
    (NPC_WREN, 8, "No dying in my circle! Up you get, Snack. I haven't finished my list.", EMOTE_NO, PLACEHOLDER),
    # Wren, 9: it tried to leave the circle
    (NPC_WREN, 9, "Ah-ah-ah! The circle holds you until the chores are done.", EMOTE_NO, PLACEHOLDER),
    # Wren, 10: a freed Devourer comes back (.inbetween)
    (NPC_WREN, 10, "Project #9 is back! Did you bring me anything? No? ...Fine. Lessons, then!", EMOTE_CHEER,
     PLACEHOLDER),
    # Wren, 11-13: the fourth chore (owner, 2026-10-02): her spell on accepting it, the frog, the last pest eaten
    (NPC_WREN, 11, "Hold still, Snack! A little swamp, a little croak... there!", EMOTE_EXCLAMATION, DRAFT),
    (NPC_WREN, 12, "Ha! A toad! The best kind of pet. Now go and eat my bugs. And look up: some of them hide where "
     "only a tongue can reach!", EMOTE_LAUGH, DRAFT),
    (NPC_WREN, 13, "Was that the last one? I think that was the last one! Come here and let me count.", EMOTE_CHEER,
     DRAFT),
    # Task 018, the molt quests: Wren peels the old body (14), and calls from afar when one is ready (15, a whisper
    # the module sends wherever the Devourer is); Hagatha tells the tale of the new form (8 + its index, MOLT_TALES).
    (NPC_WREN, 14, "Ooh, here it comes! Hold still, Snack, the old skin's coming off! ...Eww. Wonderful!", EMOTE_CHEER,
     DRAFT),
    (NPC_WREN, 15, "Snack! I can smell it from here: that body of yours is fit to burst. Come home and let me peel it!",
     0, DRAFT),
]

# Task 018: Hagatha's tale of each evolved form, said when its molt quest is handed in (creature_text group
# HAGATHA_MOLT_FIRST + the molt's index in evolved_kit.MOLTS). Keyed by the shape it grows into.
MOLT_TALES = {
    16: "In Mulgore they tell of a chick that never stopped running. The wind caught up with it once, and has been "
        "chasing it ever since.",
    17: "Every pack has one that runs behind the others. Not out of fear, my little horror. It is choosing which leg "
        "to take first.",
    18: "The quilboar have a word for a boar that has been struck so often it forgot how to fall. They pray to it.",
    19: "On Darkshore they say a black cat once swallowed a scream, and it has hunted in silence ever since. Mind your "
        "voice near it.",
    20: "The dwarves tell of a trogg that gnawed on a stone giant's toe. It never stopped growing harder. Neither did "
        "its hunger.",
    21: "In Tirisfal the bats grew fat on what the plague left behind. Then the plague left nothing, and they came for "
        "the living.",
    22: "When the elves spill their magic, something always laps it up. That something does not stop when the cup is "
        "empty.",
    23: "The draenei say the bluest moths dream for the ones they put to sleep. Never ask them what they dream about.",
    24: "Out where the world thins, the warp stalkers grow until they forget which side of the dark they belong to.",
    26: "A snake that swallows enough storms grows wings to carry them. The tauren say the thunder is only the wind "
        "serpents clearing their throats.",
    1: "Every serpent that sheds long enough stands up one day and starts to pray. The sand people began like you, "
       "my little horror: as something that would not stop eating.",
    43: "A broodmother never eats alone, and never shares. She keeps her little ones close, and her food closer.",
    42: "Voidcreepers dig where the world is thin. If you hear scratching under your bed, dear, it is only family.",
    40: "When the moon is full, the owlbeasts of Winterspring sit very still and listen. Nobody knows what it tells "
        "them. Now you can ask.",
    39: "The moonkin pray to Elune with their whole feathered hearts. She has never asked them to stop eating "
        "people, I notice.",
    37: "Storm dragons were born in the sky over the sea, and the sea never forgave them. This one was born in the "
        "void as well. Mind the weather when you are angry, dear.",
    36: "Proto-drakes are what dragons were before the Titans tidied them. Wild, hungry, and proud of it. You will "
        "fit right in.",
    34: "Below the deepest mine there are tunnels no pick ever cut. The deep borers made them, looking for the heart "
        "of the world. They are still hungry, so it is still there.",
    32: "Old turtles grow spikes because the world kept biting them. You will understand that, little horror.",
    30: "Toads stay in the swamp. The salamander is the one that crawled into the hot springs and liked it. Do "
        "not let it near my cauldron.",
    29: "On the islands of the south they say a bite from the great lizards never heals. They are wrong, my little "
        "horror. It heals inside the lizard.",
}
HAGATHA_MOLT_FIRST = 8
for i, molt in enumerate(evolved_kit.MOLTS):
    TEXTS.append((NPC_HAGATHA, HAGATHA_MOLT_FIRST + i, MOLT_TALES[molt.shape], EMOTE_TALK, DRAFT))
WREN_MOLT, WREN_MOLT_READY = 14, 15

# Task 018 B: "Tell me about the shape I wear" at Hagatha's lantern. The evolved forms use their molt tale, the
# Warp Stalker the line she says at the intro (group 2); these are the others (shape id -> tale), then a fallback.
SHAPE_TALES = {
    1: "The sand people of the far south shed their skins to grow wiser. You shed theirs to grow hungrier. They "
       "would not approve.",
    2: "Some hungers come back from the In-Between with teeth of their own. The berserker is what happens when "
       "nothing ever tells them no.",
    3: "A serpent that learned to pray, and a prayer that learned to bite. Its echoes rise from the ground because "
       "the ground remembers it.",
    4: "Every terror was small once. This one still squeaks when it is hungry. Enjoy that while it lasts.",
    5: "In Elwynn they tell of a wolf that followed a shepherd for a whole year and never touched a sheep. It was "
       "waiting for the shepherd.",
    6: "The troggs came up out of the stone hungry, and they have not been full since. You will understand them "
       "better than the dwarves ever did.",
    7: "The night elves say their sabers walk between the moonbeams. They never say what the sabers eat there.",
    8: "Moths fly to the light because they remember the In-Between: the only bright thing they ever saw there was "
       "the way out.",
    9: "The orcs say a boar charges because it never learned how to stop. Neither have you, my little horror.",
    10: "The tauren children race the striders across the plains, and the striders let them win. Mostly.",
    11: "In Tirisfal the bats listen at the windows of the dead. They learn the name of everyone who is buried, and "
        "they never forget a meal.",
    12: "The elves made a well of magic, and the wyrms came to drink from it. Then the well was gone, and the wyrms "
        "were still thirsty.",
    14: "A toad in a cell eats the bugs, the bugs eat the crumbs, and the crumbs were the last prisoner. Everything "
        "in here eats something.",
    15: "The swamp folk say a frog that eats enough flies will one day swallow the swamp. You are halfway there.",
    25: "The snakes of the Wailing Caverns drank the sickness of a dreaming druid and grew clever. Clever things in "
        "the dark are the worst kind.",
    27: "The trolls of Zul'Aman raised their eagles on the hearts of their enemies. This one has not yet decided whose "
        "heart it wants.",
    41: "A voidling is a hole in the world that learned to be hungry. Sounds like someone I know.",
    38: "An owl sees what hides in the dark and says nothing. Learn the second part, little horror.",
    35: "Every dragon was a whelp once, and every whelp thinks it is a dragon already. Eat the little ones of every "
        "flight, and you will wear their colours.",
    33: "The kobolds say: you no take candle. They say it because of the worms. In the dark, a worm finds you by "
        "your heartbeat, and a candle only shows you its mouth.",
    31: "The sailors say a snapjaw once bit the anchor off a ship and slept with it for a hundred years. Turtles "
        "are very good at keeping what they bite.",
    28: "Small lizards learn patience in the mud. They wait, they bite once, and then they simply follow until the "
        "bite does the rest.",
}
NO_TALE = "That shape has no story yet. Eat a little more of the world, and the world will write you one."
HAGATHA_SHAPE_FIRST = HAGATHA_MOLT_FIRST + len(evolved_kit.MOLTS)
for i, (shape, tale) in enumerate(SHAPE_TALES.items()):
    TEXTS.append((NPC_HAGATHA, HAGATHA_SHAPE_FIRST + i, tale, EMOTE_TALK, DRAFT))
HAGATHA_NO_TALE = HAGATHA_SHAPE_FIRST + len(SHAPE_TALES)
TEXTS.append((NPC_HAGATHA, HAGATHA_NO_TALE, NO_TALE, EMOTE_TALK, DRAFT))
HAGATHA_TALE_OF = {**{molt.shape: HAGATHA_MOLT_FIRST + i for i, molt in enumerate(evolved_kit.MOLTS)},
                   **{shape: HAGATHA_SHAPE_FIRST + i for i, shape in enumerate(SHAPE_TALES)}, 13: 2}

# Task 018 B: Wren's word on the shape a freed Devourer comes back in (.inbetween), after her welcome back.
WREN_REACTIONS = [  # (line, shapes)
    ("Fluffy! Actually fluffy this time! Can I brush you? No? I'm brushing you.", (5, 7, 9, 17, 18, 19)),
    ("Look at those legs! You could outrun {hagatha}'s temper. Almost.", (10, 16)),
    ("Ooh, wings! Don't fly near the candles, Snack. We've talked about the candles.", (8, 23, 27)),
    ("Upside down, please, that's how I like my bats. No? Fine. Rightside up.", (11, 21)),
    ("My toad! Hello, my toad! Did you eat any bugs? Of course you did.", (14, 15)),
    ("You're all sparkly and wrong-looking. I love it. Don't touch the cauldron.", (2, 4, 12, 13, 22, 24)),
    ("Ew. EW! You smell like a cave. A good cave! But a cave.", (6, 20, 33, 34)),
    ("A shell! Can I live in it? No? Can I knock? Hello in there!", (31, 32)),
    ("Is it... wriggling? Inside you? Oh no. Oh, I love it.", (41, 42, 43)),
    ("Hoo! Hoo! ... Sorry. Does it hurt when I hoot? It hurts my sister.", (38, 39, 40)),
    ("A DRAGON! A real one! Can I ride you? Can I name you? Can I name you Sir Flaps?", (35, 36, 37)),
    ("Sssso fancy! Sorry. I had to.", (1, 3, 25, 26)),
    ("A lizard! Do you want a warm rock? I keep a warm rock for lizards. Don't bite it.", (28, 29, 30)),
]
WREN_REACTION_FIRST = 16
for i, (line, _) in enumerate(WREN_REACTIONS):
    TEXTS.append((NPC_WREN, WREN_REACTION_FIRST + i, line, EMOTE_LAUGH, DRAFT))
WREN_REACTION_OF = {shape: WREN_REACTION_FIRST + i for i, (_, shapes) in enumerate(WREN_REACTIONS) for shape in shapes}

# Task 018 D: Wren's apprentice joins the Devourer (the quest is handed in).
WREN_APPRENTICE = WREN_REACTION_FIRST + len(WREN_REACTIONS)
TEXTS.append((NPC_WREN, WREN_APPRENTICE, "Bramble! Out from behind the cauldron, you're going with Snack! Take your "
              "good boots. And the bucket. No, not that bucket.", EMOTE_EXCLAMATION, DRAFT))

# npc_text: (id, text, draft). Shown on the sisters' gossip; conditions pick one.
NPC_TEXTS = [
    (9101300, "Sit still, hungry thing. The circle is for your sake, not ours.", DRAFT),
    (9101301, "You smell of new meals, my little horror. Sit by the lantern, and I will teach you what the dark "
     "already knows about you.", DRAFT),
    (9101302, "You are not one of mine. Go back the way the dark let you in, and do not look into the lantern.", DRAFT),
    (9101303, "Chores first, then out of the circle! Or circle first, then chores, then out. I wrote it down somewhere.", DRAFT),
    (9101304, "Project #9! Back already? Lessons! I LOVE lessons. Hold still while I find the list.", DRAFT),
    (9101305, "Ooh, a visitor! You'd make a lovely toad. No? Then shoo! {hagatha} says I can't keep everyone.", DRAFT),
]
# (menu, Devourer still caged, Devourer freed, anyone else)
MENU_TEXTS = {MENU_HAGATHA: (9101300, 9101301, 9101302), MENU_WREN: (9101303, 9101304, 9101305)}

# --- the chores ------------------------------------------------------------------------------------------------------
QUESTS = [
    dict(id=Q_FEEDING, giver=NPC_WREN, ender=NPC_WREN, prev=0, next=Q_TRICK, xp=4,
         title="Feeding Time",
         log="Kill 3 of {wren}'s snacks and devour one of them.",
         details="Fluffy! No, Snack. Project #9! You'll answer to all of them, I've decided.$B$BFirst chore on the "
                 "list: feeding time! I keep the snacks in the little cages, see? Squeaky ones. I toss them into "
                 "your circle, you catch them. And don't just bite them. EAT one. Properly, the way you do. I want to watch!",
         objectives=[(NPC_SNACK, 3, ""), (CREDIT_DEVOURED, 1, "Snack devoured")],
         incomplete="Still squeaking in there? Somebody's not done.",
         reward="Crunchy! {hagatha}, did you see? It ate it whole! Well. Mostly whole.$B$BGold star, Snack. Next "
                "chore!",
         complete="Return to {Wren}."),
    dict(id=Q_TRICK, giver=NPC_WREN, ender=NPC_WREN, prev=Q_FEEDING, next=0, xp=4,
         title="A Trick for {wren}",
         log="Roar at {Wren}.",
         details="Every good pet knows a trick. The toad knows 'sit'. The other toad knows 'sit' too, but louder.$B$B"
                 "You, Fluffy, are going to ROAR. Big and scary, right at me. Go on! I'll pretend to be frightened. "
                 "I'm very good at it.",
         objectives=[(CREDIT_ROAR, 1, "Roar at {wren}")],
         incomplete="I'm waiting! Rooooar. Like that, but you.",
         reward="Eek! Ha! Oh, that was GOOD. That goes on the list of things you're good at. It's a short list. It's "
                "a new list!$B$BNow go and sit nicely for {hagatha}. She's been dying to frighten you back.",
         complete="Return to {Wren}."),
    dict(id=Q_TALE, giver=NPC_HAGATHA, ender=NPC_HAGATHA, prev=Q_TRICK, next=0, xp=5,
         title="What the Dark Remembers",
         log="Ask {Hagatha} for the tale of the hungry thing, and listen to its end.",
         details="My sister teaches you tricks. I will teach you what you are.$B$BEvery village has a story about "
                 "something that came out of the dark and ate until it became something else. Sit, hungry thing. Ask "
                 "me for the tale, and listen to the end of it. The ones who do not listen end up in it.",
         objectives=[(CREDIT_TALE, 1, "Hear {hagatha}'s tale")],
         incomplete="The tale is not finished with you yet.",
         reward="Now you know the shape beneath all your shapes. Remember it when you wear someone else's.$B$B"
                "{wren}, break the circle. Our little horror has lessons to carry into the world, and it will come back "
                "to us for more.",
         complete="Return to {Hagatha}."),
    # Owner, 2026-10-02 (Parrot\to be devoured.canvas): accepting it, Wren turns the Devourer into a Biletoad.
    dict(id=Q_PESTS, giver=NPC_WREN, ender=NPC_WREN, prev=Q_TALE, next=0, xp=5,
         title="Pests in the Cells",
         log="Devour every anima-fat pest around {wren}'s cages. Some of them can only be reached with your tongue.",
         details="Snack, I have a teeny problem. The bugs I test my spells on? They got out. All of them. They "
                 "crawled off around the cells and found {hagatha}'s store of anima, and they've been feasting on it, "
                 "and now they MULTIPLY. Every time I catch one and squash it, there are more! I can't cage the anima "
                 "that comes flowing out of them.$B$BBut an ancient horror like you is made for exactly this. Just "
                 "eat them. They might not be tasty... hmm, maybe you'll learn to like them. Here, I'll help you "
                 "with it. Hold still!",
         objectives=[(CREDIT_PEST, len(PEST_SPOTS), "Anima pest devoured")],
         incomplete="I can still hear crunching, and it isn't you. Keep eating!",
         reward="All of them? ALL of them? Oh, you lovely, horrible thing. {hagatha}'s anima is safe and nothing is "
                "multiplying any more.$B$BKeep the frog. It suits you.",
         complete="Return to {Wren}."),
    # Task 018 D (owner, 2026-10-03: "a bot character that is connected to the witches"): Wren's apprentice.
    dict(id=Q_APPRENTICE, giver=NPC_WREN, ender=NPC_WREN, prev=Q_TALE, next=0, xp=3,
         title="{wren}'s Apprentice",
         log="Let {wren} introduce her apprentice, and take her with you into the world.",
         details=f"Snack, meet {COMPANION}! She's my apprentice. Well, SHE says she's my apprentice. I say she's a gnome "
                 "who followed a cat into the In-Between and never found the way out again.$B$BShe wants to see the "
                 "world, and you need somebody to tell you which mushrooms not to eat. Take her with you! Bring her "
                 "back with all her fingers.",
         objectives=[],
         incomplete="Well? She's right there, pretending to be a coat stand.",
         reward=f"There! Now you're a pack. A very small, very odd pack.$B$B{COMPANION}, don't let Snack eat you. "
                "Snack, don't let her set you on fire. Again.",
         complete="Return to {Wren}."),
]

# Task 018: the molt quests. Nobody offers them: the module puts one in the log, done, the moment a form has
# everything its evolution needs (Bio Points, level, one task); handing it in to Wren is the evolution.
MOLT_QUESTS = [
    dict(id=molt.quest, ender=NPC_WREN, shape=molt.shape, level=molt.level, xp=5,
         title=f"The Molt: {molt.name}",
         log=f"Go back to {{Wren}} in the In-Between and let her peel your {molt.parent_name.lower()} body. "
             f"A {molt.name.lower()} is waiting under the old skin.",
         details=f"Your {molt.parent_name.lower()} body has eaten enough. It itches, it pulls, it does not fit any more. "
                 "The sisters can feel it from the In-Between.",
         reward="There you are! Look how it bulges. Lie down in the circle, Snack, and don't wriggle. "
                "{hagatha}, the bucket!",
         complete="Return to {Wren}.")
    for molt in evolved_kit.MOLTS]
assert all(Q_FIRST <= qd["id"] <= Q_LAST for qd in MOLT_QUESTS)

# Task 019 C: the daily chores. Nobody but Wren offers them, once the circle has let the Devourer go (like the molt
# quests). The reagent's icon is a placeholder (the idols' display): the owner picks better ones.
REAGENT_DISPLAY = 34955
CHORES = [
    dict(tier=1, level=5, xp=3, item="Gristle of the Hunt",
         flavour="Wren swears it is a reagent. Only a beast-body can tell it from the rest of the meal.",
         title="A Pinch of Gristle",
         log="Bring {wren} 3 Gristle of the Hunt, left when you eat in a starter form. (Daily)",
         details="Snack, I'm out of gristle! The proper kind, the kind a first body picks out of its teeth. Only a "
                 "young shape can fetch it: the older ones are far too refined, they swallow it whole.$B$BEat a "
                 "few things as you are, I mean as one of your first shapes, and bring me what's left over. I'll "
                 "pay in Bio Points. I've been saving them in a jar.",
         incomplete="Not yet three? Keep chewing, Snack. Chew with your first face.",
         reward="Gristle! Beautiful, disgusting gristle! Here, a jar of points. Don't tell {hagatha} which jar."),
    dict(tier=2, level=12, xp=4, item="Molted Husk Flake",
         flavour="A flake of a body outgrown. Wren needs the ones a grown-out form leaves behind.",
         title="Husks for {wren}",
         log="Bring {wren} 3 Molted Husk Flakes, left when you eat in a form that has grown out of another. (Daily)",
         details="Snack! You've molted, which means you're properly interesting now, and I need husk flakes for my "
                 "potions. They only fall off a body that has grown out of an older one. Not a first body, not a "
                 "last one. The in-between ones!$B$BEat in a grown-out form, and bring me the flakes.",
         incomplete="I can smell your first body. Or your last one. Change into the middle one, Snack!",
         reward="Flakes! Ooh, they crunch! Here: Bio Points, for the middle child of all my pets."),
    dict(tier=3, level=40, xp=5, item="Heartstring of the Great",
         flavour="A thread of sinew from something that has grown all the way. Only the greatest bodies leave it.",
         title="The Greatest Thread",
         log="Bring {wren} 3 Heartstrings of the Great, left when you eat in the last form of a line. (Daily)",
         details="Snack, the great forms leave a thread behind when they eat. Heartstrings, I call them. I need three "
                 "for a very large knot.$B$BOnly a form at the end of its line can fetch one: the last step of a "
                 "long molt. Eat as the greatest you are, and bring them home.",
         incomplete="Three heartstrings, Snack. From the biggest body you've got.",
         reward="Heartstrings! You really are a big one. I'm very proud. And a little scared. Bio Points for you!"),
]
for _i, _c in enumerate(CHORES):
    _c.update(id=Q_CHORE_FIRST + _i, item_id=ITEM_CHORE_FIRST + _i, bp=CHORE_BP[_i],
              complete="Return to {Wren}.")
assert Q_CHORE_FIRST + len(CHORES) - 1 <= Q_LAST
assert max(qd["id"] for qd in MOLT_QUESTS) < Q_CHORE_FIRST, "the molt quests ran into the daily chores' ids"
assert ITEM_CHORE_FIRST + len(CHORES) - 1 <= ITEM_CHORE_LAST

OPTIONS = {  # menu -> [(OptionID, icon, text, broadcast text, type, npcflag, action menu, who sees it)]
    # who: "trained" = a Devourer whose cage is open, "tale" = a Devourer on the third task
    MENU_HAGATHA: [
        (OPT_TRAIN, 3, "I require training.", 0, 5, 16, 0, "trained"),
        (OPT_UNLEARN, 0, "I wish to unlearn my talents.", 62295, 16, 16, 4461, "trained"),
        (OPT_DUALSPEC, 0, "I wish to know about Dual Talent Specialization.", 33762, 20, 1, 10371, "trained"),
        (OPT_VENDOR, 1, "I have things to sell.", 0, 3, 128, 0, "trained"),   # owner, 2026-10-03
        (OPT_TALE, 0, "Tell me the tale of the hungry thing.", 0, 1, 1, 0, "tale"),
        (OPT_SHAPE_TALE, 0, "Tell me about the shape I wear.", 0, 1, 1, 0, "trained"),   # task 018
        (OPT_BACK, 0, "Send me back to where you found me.", 0, 1, 1, 0, "trained"),
    ],
    MENU_WREN: [
        (OPT_TRAIN, 3, "I require training.", 0, 5, 16, 0, "trained"),
        (OPT_UNLEARN, 0, "I wish to unlearn my talents.", 62295, 16, 16, 4461, "trained"),
        (OPT_DUALSPEC, 0, "I wish to know about Dual Talent Specialization.", 33762, 20, 1, 10371, "trained"),
        (OPT_BACK, 0, "Send me back to where you found me.", 0, 1, 1, 0, "trained"),
        (OPT_MOUNTS, 1, "Show me the mounts you made.", 0, 3, 128, 0, "trained"),   # the Skrill thread's wares
    ],
}

# The 16 Devourer Trainers of task 006 (gone; the owner disliked them). Removed from databases that have them.
OLD_TRAINERS = (9101200, 9101215)
OLD_TRAINER_SPAWNS = (9910101, 9910116)
OLD_MENU, OLD_TEXTS = 9101200, (9101200, 9101201)


def f(text: str) -> str:
    return text.format(**N)


def q(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"


def rot(o: float) -> tuple[float, float]:
    return round(math.sin(o / 2), 6), round(math.cos(o / 2), 6)


def cond(menu_type, group, entry, ctype, value, negative, comment, else_group=0):
    return (f"({menu_type}, {group}, {entry}, 0, {else_group}, {ctype}, 0, {value}, 0, 0, {negative}, 0, 0, '',"
            f" {q(comment)})")


CONDITION_QUESTREWARDED, CONDITION_QUESTTAKEN, CONDITION_CLASS = 8, 9, 15
QUEST_FLAG_DAILY = 0x1000


def build_sql() -> str:
    s = [
        "-- Generated by tools/witch_sisters.py (task 010). Do not edit by hand: change the script and run it again.",
        f"-- The Hollowmoor sisters ({HAGATHA}, {WREN}): the Devourer's trainers in the In-Between (map {MAP}), their",
        "-- cage and trappings, the three chores of the level-5 intro. Safe to run again; removed by uninstall/world.sql.",
        "",
        "-- --- the 16 Devourer Trainers of task 006 are gone (tools/start_kit.py no longer makes them) ------------------",
        f"DELETE FROM `creature` WHERE `guid` BETWEEN {OLD_TRAINER_SPAWNS[0]} AND {OLD_TRAINER_SPAWNS[1]};",
        f"DELETE FROM `creature_default_trainer` WHERE `CreatureId` BETWEEN {OLD_TRAINERS[0]} AND {OLD_TRAINERS[1]};",
        f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {OLD_TRAINERS[0]} AND {OLD_TRAINERS[1]};",
        f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {OLD_TRAINERS[0]} AND {OLD_TRAINERS[1]};",
        f"DELETE FROM `gossip_menu_option` WHERE `MenuID` = {OLD_MENU};",
        f"DELETE FROM `gossip_menu` WHERE `MenuID` = {OLD_MENU};",
        f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` IN (14, 15) AND `SourceGroup` = {OLD_MENU};",
        f"DELETE FROM `npc_text` WHERE `ID` IN ({OLD_TEXTS[0]}, {OLD_TEXTS[1]});",
        "",
        "-- --- clean slate for this file's ids ---------------------------------------------------------------------------",
        f"DELETE FROM `creature` WHERE `guid` BETWEEN {SPAWN_FIRST} AND {SPAWN_LAST};",
        f"DELETE FROM `gameobject` WHERE `guid` BETWEEN {SPAWN_FIRST} AND {SPAWN_LAST};",
        f"DELETE FROM `creature_text` WHERE `CreatureID` BETWEEN {NPC_FIRST} AND {NPC_LAST};",
        f"DELETE FROM `creature_template_addon` WHERE `entry` BETWEEN {NPC_FIRST} AND {NPC_LAST};",
        f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {NPC_FIRST} AND {NPC_LAST};",
        f"DELETE FROM `creature_default_trainer` WHERE `CreatureId` BETWEEN {NPC_FIRST} AND {NPC_LAST};",
        f"DELETE FROM `creature_queststarter` WHERE `id` BETWEEN {NPC_FIRST} AND {NPC_LAST};",
        f"DELETE FROM `creature_questender` WHERE `id` BETWEEN {NPC_FIRST} AND {NPC_LAST};",
        f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {NPC_FIRST} AND {NPC_LAST};",
        f"DELETE FROM `gameobject_template_addon` WHERE `entry` BETWEEN {GO_FIRST} AND {GO_LAST};",
        f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {GO_FIRST} AND {GO_LAST};",
        f"DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `quest_request_items` WHERE `ID` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `quest_template` WHERE `ID` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `item_template` WHERE `entry` BETWEEN {ITEM_CHORE_FIRST} AND {ITEM_CHORE_LAST};",
        f"DELETE FROM `gossip_menu_option` WHERE `MenuID` IN ({MENU_HAGATHA}, {MENU_WREN});",
        f"DELETE FROM `gossip_menu` WHERE `MenuID` IN ({MENU_HAGATHA}, {MENU_WREN});",
        f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` IN (14, 15) AND `SourceGroup` IN ({MENU_HAGATHA},"
        f" {MENU_WREN});",
        f"DELETE FROM `npc_text` WHERE `ID` BETWEEN {NPC_TEXTS[0][0]} AND {NPC_TEXTS[-1][0]};",
        "",
        "-- --- the sisters ------------------------------------------------------------------------------------------------",
        "-- Copies of a friendly stock NPC (made at install time, so no creature data is written here), as Devourer",
        "-- Trainers, quest givers and gossip; the module's AI (ScriptName) answers the options it owns. Looks: a",
        "-- stock creature's model each (Hagatha: Myranda the Hag 11872; Wren: Windfury Wind Witch 2963, a harpy).",
        "DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;",
        "CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 11872;",
        "UPDATE `devourer_tmp_ct` SET `subname` = 'Devourer Trainer', `minlevel` = 80, `maxlevel` = 80, `faction` = 35,",
        f"    `npcflag` = 51, `unit_flags` = 768, `AIName` = '', `ScriptName` = {q(SCRIPT)}, `lootid` = 0,"
        " `KillCredit1` = 0,",
        "    `KillCredit2` = 0, `MovementType` = 0, `VerifiedBuild` = 0;",
    ]
    for entry, _, name, menu, _, *_ in SISTERS:
        s.append(f"UPDATE `devourer_tmp_ct` SET `entry` = {entry}, `name` = {q(name)}, `gossip_menu_id` = {menu};")
        s.append("INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;")
    s += [
        f"UPDATE `creature_template` SET `npcflag` = `npcflag` | 128 WHERE `entry` IN ({NPC_HAGATHA}, {NPC_WREN});"
        "  -- Hagatha buys (owner, 2026-10-03); Wren sells mounts (task 018: their npc_vendor rows belong to the"
        " mounts SQL, data/sql/custom/db_world/2026_10_03_10_mounts_adding.sql; this file never touches them)",
        "-- A vendor window only opens with something on sale: plain food and water (the owner may pick other wares).",
        f"DELETE FROM `npc_vendor` WHERE `entry` = {NPC_HAGATHA};",
        "INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`, `VerifiedBuild`) VALUES",
        ", ".join(f"({NPC_HAGATHA}, {i}, {item}, 0, 0, 0, 0)" for i, item in enumerate((159, 4540, 2678))) + ";",
        "DROP TEMPORARY TABLE `devourer_tmp_ct`;",
        "INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`,"
        " `VerifiedBuild`)",
        "SELECT `m`.`entry`, 0, `ctm`.`CreatureDisplayID`, `ctm`.`DisplayScale`, 1, 0 FROM (",
        "    " + " UNION ALL ".join(f"SELECT {e} AS `entry`, {lk} AS `looks`" for e, _, _, _, lk, *_ in SISTERS),
        ") AS `m` JOIN `creature_template_model` AS `ctm` ON `ctm`.`CreatureID` = `m`.`looks` AND `ctm`.`Idx` = 0;",
        "INSERT INTO `creature_default_trainer` (`CreatureId`, `TrainerId`) VALUES",
        ", ".join(f"({e}, {TRAINER})" for e, *_ in SISTERS) + ";",
        "",
        "-- --- Wren's snacks (the first chore): rats, hostile, worth no experience; summoned into the cage by the module",
        "CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 4075;   -- Rat",
        f"UPDATE `devourer_tmp_ct` SET `entry` = {NPC_SNACK}, `name` = {q(f("{wren}'s Snack"))},"
        " `subname` = NULL, `minlevel` = 2, `maxlevel` = 3,",
        "    `faction` = 14, `type` = 1, `npcflag` = 0, `unit_flags` = 0, `lootid` = 0, `skinloot` = 0,"
        " `pickpocketloot` = 0,",
        "    `mingold` = 0, `maxgold` = 0, `ExperienceModifier` = 0, `DamageModifier` = 0.5, `AIName` = '',"
        " `ScriptName` = '',",
        "    `KillCredit1` = 0, `KillCredit2` = 0, `VerifiedBuild` = 0;",
        "INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;",
        "DROP TEMPORARY TABLE `devourer_tmp_ct`;",
        f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`,"
        " `Probability`, `VerifiedBuild`)",
        f"SELECT {NPC_SNACK}, 0, `CreatureDisplayID`, `DisplayScale`, 1, 0 FROM `creature_template_model`"
        " WHERE `CreatureID` = 4075 AND `Idx` = 0;",
        "",
        "-- --- Wren's anima pests (the fourth chore): critters, hostile, never fight back, worth no experience;",
        "-- --- summoned around the cages by the module, for each Devourer its own (beetles below, fireflies above)",
        "CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 15475;  -- Beetle",
        f"UPDATE `devourer_tmp_ct` SET `entry` = {NPC_PEST}, `name` = 'Anima-Fat Beetle', `subname` = NULL,"
        " `minlevel` = 5, `maxlevel` = 5,",
        "    `faction` = 14, `type` = 8, `npcflag` = 0, `unit_flags` = 0, `lootid` = 0, `skinloot` = 0,"
        " `pickpocketloot` = 0,",
        "    `mingold` = 0, `maxgold` = 0, `ExperienceModifier` = 0, `DamageModifier` = 0, `AIName` = '',"
        f" `ScriptName` = '{PEST_SCRIPT}',",
        "    `KillCredit1` = 0, `KillCredit2` = 0, `MovementType` = 0, `VerifiedBuild` = 0;",
        "INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;",
        f"UPDATE `devourer_tmp_ct` SET `entry` = {NPC_PEST_PERCHED}, `name` = 'Anima-Fat Firefly';",
        "INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;",
        "DROP TEMPORARY TABLE `devourer_tmp_ct`;",
        "INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`,"
        " `VerifiedBuild`)",
        f"SELECT {NPC_PEST}, 0, `CreatureDisplayID`, `DisplayScale`, 1, 0 FROM `creature_template_model`"
        " WHERE `CreatureID` = 15475 AND `Idx` = 0",
        f"UNION ALL SELECT {NPC_PEST_PERCHED}, 0, `CreatureDisplayID`, `DisplayScale`, 1, 0 FROM `creature_template_model`"
        " WHERE `CreatureID` = 21076 AND `Idx` = 0;   -- Firefly",
        "",
        "-- --- the void under the cage: an unseen, unselectable creature wearing the Void Zone visual ------------------",
        "-- --- and the three quest credits (never spawned; their names are what the quest log would show) ------------",
        "CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = 15384;"
        "  -- OLDWorld Trigger",
        f"UPDATE `devourer_tmp_ct` SET `entry` = {NPC_VOID}, `name` = 'The In-Between', `subname` = NULL,"
        " `faction` = 35, `npcflag` = 0,",
        f"    `unit_flags` = 33554434, `flags_extra` = 0, `AIName` = '', `ScriptName` = '', `VerifiedBuild` = 0;",
        "INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;",
        f"UPDATE `devourer_tmp_ct` SET `entry` = {CREDIT_DEVOURED}, `name` = 'Snack devoured';",
        "INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;",
        f"UPDATE `devourer_tmp_ct` SET `entry` = {CREDIT_ROAR}, `name` = {q(f('Roar at {wren}'))};",
        "INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;",
        f"UPDATE `devourer_tmp_ct` SET `entry` = {CREDIT_TALE}, `name` = {q(f("{hagatha}'s tale heard"))};",
        "INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;",
        f"UPDATE `devourer_tmp_ct` SET `entry` = {CREDIT_PEST}, `name` = 'Anima pest devoured';",
        "INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;",
        "DROP TEMPORARY TABLE `devourer_tmp_ct`;",
        "INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`,"
        " `VerifiedBuild`) VALUES",
        ",\n".join(f"({e}, 0, 11686, {VOID_SCALE if e == NPC_VOID else 1}, 1, 0)"   # this fork: size = DisplayScale
                   for e in (NPC_VOID, CREDIT_DEVOURED, CREDIT_ROAR, CREDIT_TALE, CREDIT_PEST))
        + ";   -- the invisible stalker model",
        "INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`,"
        " `visibilityDistanceType`, `auras`) VALUES",
        f"({NPC_VOID}, 0, 0, 0, 0, 0, 0, '{VOID_AURA}');",
        "",
        f"-- --- spawns in the In-Between (map {MAP}) ------------------------------------------------------------------",
        "INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`,"
        " `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES",
        ",\n".join(
            [f"({g}, {e}, {MAP}, 1, 1, {x}, {y}, {z}, {facing(x, y):.4f}, 300, 0, 0, {q('mod-devourer: ' + n)})"
             for e, g, n, _, _, x, y, z in SISTERS]
            + [f"({VOID_SPAWN[0]}, {NPC_VOID}, {MAP}, 1, 1, {VOID_SPAWN[1]}, {VOID_SPAWN[2]}, {VOID_SPAWN[3]}, 0, 300,"
               f" 0, 0, 'mod-devourer: the void under the cage')"]) + ";",
        "",
        "-- --- game objects: the Devourer's cage (a door: it opens), and the sisters' trappings -------------------------",
        "INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`,"
        " `unk1`, `size`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES",
        ",\n".join(f"({e}, {t}, {d}, {q(n)}, '', '', '', {sz}, '', '', 0)" for e, t, d, n, sz, _ in GO_TEMPLATES) + ";",
        "INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`, `mingold`, `maxgold`) VALUES",
        ",\n".join(f"({e}, 0, {fl}, 0, 0)" for e, t, d, n, sz, fl in GO_TEMPLATES) + ";",
        "INSERT INTO `gameobject` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`,"
        " `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`,"
        " `animprogress`, `state`, `Comment`) VALUES",
    ]
    rows = []
    for i, (e, x, y, z, o) in enumerate(GO_SPAWNS):
        o = facing(x, y) if o is None else o
        r2, r3 = rot(o)
        rows.append(f"({SPAWN_FIRST + i}, {e}, {MAP}, 1, 1, {x}, {y}, {z}, {o:.4f}, 0, 0, {r2}, {r3}, 300, 0, 1,"
                    " 'mod-devourer: the In-Between')")
    assert SPAWN_FIRST + len(GO_SPAWNS) - 1 <= SPAWN_LAST
    s += [",\n".join(rows) + ";", ""]

    # quests
    s += ["-- --- the three chores (class 10 only; each opens after the one before) ------------------------------------",
          "INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `QuestInfoID`,"
          " `RewardNextQuest`, `RewardXPDifficulty`, `Flags`, `AllowableRaces`, `LogTitle`, `LogDescription`,"
          " `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGo2`,"
          " `RequiredNpcOrGoCount1`, `RequiredNpcOrGoCount2`, `ObjectiveText1`, `ObjectiveText2`, `ObjectiveText3`,"
          " `ObjectiveText4`, `VerifiedBuild`) VALUES"]
    rows = []
    for qd in QUESTS:
        obj = qd["objectives"] + [(0, 0, "")] * (2 - len(qd["objectives"]))
        rows.append(f"({qd['id']}, 2, 5, 5, 0, 0, {qd['next']}, {qd['xp']}, 0, 0, {q(f(qd['title']))},"
                    f" {q(f(qd['log']))}, {q(f(qd['details']))}, '', {q(f(qd['complete']))},"
                    f" {obj[0][0]}, {obj[1][0]}, {obj[0][1]}, {obj[1][1]}, {q(f(obj[0][2]))}, {q(f(obj[1][2]))}, '', '',"
                    " 0)")
    s += [",\n".join(rows) + ";",
          "INSERT INTO `quest_template_addon` (`ID`, `AllowableClasses`, `PrevQuestID`) VALUES",
          ",\n".join(f"({qd['id']}, {CLASS_MASK}, {qd['prev']})" for qd in QUESTS) + ";",
          "INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`,"
          " `VerifiedBuild`) VALUES",
          ",\n".join(f"({qd['id']}, 1, 1, {q(f(qd['incomplete']))}, 0)" for qd in QUESTS) + ";",
          "INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES",
          ",\n".join(f"({qd['id']}, 1, {q(f(qd['reward']))}, 0)" for qd in QUESTS) + ";",
          "INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES",
          ", ".join(f"({qd['giver']}, {qd['id']})" for qd in QUESTS) + ";",
          "INSERT INTO `creature_questender` (`id`, `quest`) VALUES",
          ", ".join(f"({qd['ender']}, {qd['id']})" for qd in QUESTS) + ";",
          ""]

    # task 018: the molt quests (no giver: the module puts them in the log, already done; Wren takes them)
    s += ["-- --- the molt quests (task 018): the module hands one out when a form is ready to evolve; Wren takes it ---",
          "INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `QuestInfoID`,"
          " `RewardNextQuest`, `RewardXPDifficulty`, `Flags`, `AllowableRaces`, `LogTitle`, `LogDescription`,"
          " `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `VerifiedBuild`) VALUES",
          ",\n".join(f"({qd['id']}, 2, {qd['level']}, {qd['level']}, 0, 0, 0, {qd['xp']}, 0, 0, {q(f(qd['title']))},"
                     f" {q(f(qd['log']))}, {q(f(qd['details']))}, '', {q(f(qd['complete']))}, 0)"
                     for qd in MOLT_QUESTS) + ";",
          "INSERT INTO `quest_template_addon` (`ID`, `AllowableClasses`, `PrevQuestID`) VALUES",
          ",\n".join(f"({qd['id']}, {CLASS_MASK}, {Q_TALE})" for qd in MOLT_QUESTS) + ";",
          "INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES",
          ",\n".join(f"({qd['id']}, 1, {q(f(qd['reward']))}, 0)" for qd in MOLT_QUESTS) + ";",
          "INSERT INTO `creature_questender` (`id`, `quest`) VALUES",
          ", ".join(f"({qd['ender']}, {qd['id']})" for qd in MOLT_QUESTS) + ";",
          ""]

    # task 019: the daily chores (Wren gives and takes them; the reagents drop by the module's hook)
    s += ["-- --- the daily chores (task 019): a reagent only a form of the right tier leaves (Mgr::ChoreDrop), Bio Points ---",
          "INSERT INTO `item_template` (`entry`, `class`, `subclass`, `name`, `displayid`, `Quality`, `Flags`,"
          " `BuyCount`, `AllowableClass`, `AllowableRace`, `ItemLevel`, `RequiredLevel`, `stackable`, `bonding`,"
          " `description`) VALUES",
          ",\n".join(f"({c['item_id']}, 12, 0, {q(c['item'])}, {REAGENT_DISPLAY}, 1, 0, 1, {CLASS_MASK}, -1, 1, 1,"
                     f" {CHORE_COUNT * 2}, 4, {q(c['flavour'])})" for c in CHORES) + ";",
          "INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `QuestInfoID`,"
          " `RewardNextQuest`, `RewardXPDifficulty`, `Flags`, `AllowableRaces`, `LogTitle`, `LogDescription`,"
          " `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredItemId1`, `RequiredItemCount1`,"
          " `VerifiedBuild`) VALUES",
          ",\n".join(f"({c['id']}, 2, {c['level']}, {c['level']}, 0, 0, 0, {c['xp']}, {QUEST_FLAG_DAILY}, 0,"
                     f" {q(f(c['title']))}, {q(f(c['log']))}, {q(f(c['details']))}, '', {q(f(c['complete']))},"
                     f" {c['item_id']}, {CHORE_COUNT}, 0)" for c in CHORES) + ";",
          "INSERT INTO `quest_template_addon` (`ID`, `AllowableClasses`, `PrevQuestID`) VALUES",
          ",\n".join(f"({c['id']}, {CLASS_MASK}, {Q_TALE})" for c in CHORES) + ";",
          "INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`,"
          " `VerifiedBuild`) VALUES",
          ",\n".join(f"({c['id']}, 1, 1, {q(f(c['incomplete']))}, 0)" for c in CHORES) + ";",
          "INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES",
          ",\n".join(f"({c['id']}, 1, {q(f(c['reward']))}, 0)" for c in CHORES) + ";",
          "INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES",
          ", ".join(f"({NPC_WREN}, {c['id']})" for c in CHORES) + ";",
          "INSERT INTO `creature_questender` (`id`, `quest`) VALUES",
          ", ".join(f"({NPC_WREN}, {c['id']})" for c in CHORES) + ";",
          ""]

    # texts
    s += ["-- --- what they say (creature_text; the module calls the groups at the right moments) ---------------------",
          "INSERT INTO `creature_text` (`CreatureID`, `GroupID`, `ID`, `Text`, `Type`, `Language`, `Probability`,"
          " `Emote`, `Duration`, `Sound`, `BroadcastTextId`, `TextRange`, `comment`) VALUES",
          ",\n".join(f"({c}, {g}, 0, {q(f(t))}, {WHISPER if (c, g) == (NPC_WREN, 0) else SAY}, 0, 100, {em}, 0, 0, 0,"
                     f" 0, {q(('Hagatha' if c == NPC_HAGATHA else 'Wren') + f' {g} ({d})')})"
                     for c, g, t, em, d in TEXTS) + ";",
          "",
          "-- --- gossip: the text depends on who asks; training only for a Devourer whose cage is open ---------------",
          "INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES",
          ",\n".join(f"({i}, {q(f(t))}, {q(f(t))}, 1)" for i, t, _ in NPC_TEXTS) + ";",
          "INSERT INTO `gossip_menu` (`MenuID`, `TextID`) VALUES",
          ",\n".join(f"({m}, {t})" for m, ts in MENU_TEXTS.items() for t in ts) + ";",
          "INSERT INTO `gossip_menu_option` (`MenuID`, `OptionID`, `OptionIcon`, `OptionText`, `OptionBroadcastTextID`,"
          " `OptionType`, `OptionNpcFlag`, `ActionMenuID`, `ActionPoiID`, `BoxCoded`, `BoxMoney`, `BoxText`,"
          " `BoxBroadcastTextID`, `VerifiedBuild`) VALUES",
          ",\n".join(f"({m}, {o}, {ic}, {q(t)}, {bc}, {ty}, {nf}, {am}, 0, 0, 0, '', 0, 0)"
                     for m, opts in OPTIONS.items() for o, ic, t, bc, ty, nf, am, _ in opts) + ";"]
    conds = []
    for m, (caged, freed, other) in MENU_TEXTS.items():
        who = "Hagatha" if m == MENU_HAGATHA else "Wren"
        conds += [cond(14, m, caged, CONDITION_CLASS, CLASS_MASK, 0, f"{who}: a caged Devourer"),
                  cond(14, m, caged, CONDITION_QUESTREWARDED, Q_TALE, 1, f"{who}: a caged Devourer"),
                  cond(14, m, freed, CONDITION_CLASS, CLASS_MASK, 0, f"{who}: a freed Devourer"),
                  cond(14, m, freed, CONDITION_QUESTREWARDED, Q_TALE, 0, f"{who}: a freed Devourer"),
                  cond(14, m, other, CONDITION_CLASS, CLASS_MASK, 1, f"{who}: anyone else is sent away")]
        for o, _, t, _, _, _, _, seen in OPTIONS[m]:
            conds.append(cond(15, m, o, CONDITION_CLASS, CLASS_MASK, 0, f"{who}: {t} (Devourer)"))
            if seen == "trained":
                conds.append(cond(15, m, o, CONDITION_QUESTREWARDED, Q_TALE, 0, f"{who}: {t} (cage open)"))
            else:
                conds.append(cond(15, m, o, CONDITION_QUESTTAKEN, Q_TALE, 0, f"{who}: {t} (on the third chore)"))
    s += ["INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`,"
          " `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`,"
          " `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES",
          ",\n".join(conds) + ";", ""]
    return "\n".join(s)


def build_header() -> str:
    c = CAGE
    a = ARRIVE
    return "\n".join([
        "// Generated by tools/witch_sisters.py (task 010) -- change the script and run it again.",
        "#ifndef DEVOURER_SISTERS_IDS_H",
        "#define DEVOURER_SISTERS_IDS_H",
        "",
        "#include <cstdint>",
        "",
        "namespace Devourer::Sisters",
        "{",
        f"    constexpr uint32_t NpcHagatha = {NPC_HAGATHA};",
        f"    constexpr uint32_t NpcWren = {NPC_WREN};",
        f"    constexpr uint32_t NpcSnack = {NPC_SNACK};",
        f"    constexpr uint32_t CreditDevoured = {CREDIT_DEVOURED};",
        f"    constexpr uint32_t CreditRoar = {CREDIT_ROAR};",
        f"    constexpr uint32_t CreditTale = {CREDIT_TALE};",
        f"    constexpr uint32_t NpcPest = {NPC_PEST};",
        f"    constexpr uint32_t NpcPestPerched = {NPC_PEST_PERCHED};",
        f"    constexpr uint32_t CreditPest = {CREDIT_PEST};",
        f"    constexpr uint32_t ShapeBiletoad = {SHAPE_BILETOAD};",
        f"    constexpr uint32_t GoCage = {GO_CAGE};",
        f"    constexpr uint32_t QuestFeeding = {Q_FEEDING};",
        f"    constexpr uint32_t QuestTrick = {Q_TRICK};",
        f"    constexpr uint32_t QuestTale = {Q_TALE};",
        f"    constexpr uint32_t QuestPests = {Q_PESTS};",
        f"    constexpr uint32_t QuestApprentice = {Q_APPRENTICE};   // task 018: the companion joins",
        f"    constexpr uint32_t QuestMoltFirst = {MOLT_QUESTS[0]['id']};   // task 018: one per evolved form, in order",
        f"    constexpr uint32_t QuestMoltLast = {MOLT_QUESTS[-1]['id']};",
        f"    constexpr uint32_t QuestChoreFirst = {CHORES[0]['id']};   // task 019: Wren's daily chores, one per tier",
        f"    constexpr uint32_t QuestChoreLast = {CHORES[-1]['id']};",
        f"    constexpr uint32_t ItemChoreFirst = {ITEM_CHORE_FIRST};   // their reagents, in the same order",
        f"    constexpr uint32_t ChoreCount = {CHORE_COUNT};            // reagents a chore asks for",
        f"    constexpr uint32_t ChoreChance = {CHORE_CHANCE};          // % of meals in the right tier that leave one",
        f"    constexpr uint32_t ChoreBp[] = {{ {', '.join(map(str, CHORE_BP))} }};   // Bio Points per tier",
        f"    constexpr uint32_t MenuHagatha = {MENU_HAGATHA};",
        f"    constexpr uint32_t MenuWren = {MENU_WREN};",
        f"    constexpr uint32_t OptionTale = {OPT_TALE};",
        f"    constexpr uint32_t OptionBack = {OPT_BACK};",
        f"    constexpr uint32_t OptionShapeTale = {OPT_SHAPE_TALE};   // task 018",
        f"    constexpr uint32_t InBetweenMap = {MAP};",
        f"    constexpr float CageX = {c[0]}f, CageY = {c[1]}f, CageZ = {c[2]}f, CageO = {c[3]:.4f}f;",
        f"    constexpr float ArriveX = {a[0]}f, ArriveY = {a[1]}f, ArriveZ = {a[2]}f, ArriveO = {a[3]:.4f}f;",
        f"    constexpr float CageRadius = {CAGE_RADIUS}f;",
        f"    constexpr uint32_t VisualPull = {VISUAL_PULL};",
        f"    constexpr uint32_t VisualArrive = {VISUAL_ARRIVE};",
        f"    constexpr uint32_t VisualSleep = {VISUAL_SLEEP};",
        f"    constexpr uint32_t VisualTransform = {VISUAL_TRANSFORM};",
        f"    constexpr uint32_t SpellChannel = {CHANNEL};",
        "",
        "    // Wren's pests: x, y, z, perched (1 = hovering out of reach, only a tongue gets it down)",
        "    struct PestSpot { float X, Y, Z; bool Perched; };",
        "    constexpr PestSpot PestSpots[] =",
        "    {",
        *[f"        {{ {x}f, {y}f, {z}f, {'true' if p else 'false'} }}," for x, y, z, p in PEST_SPOTS],
        "    };",
        "",
        "    // creature_text groups",
        "    enum Line : uint8_t",
        "    {",
        "        WrenFoundYou = 0, WrenAwake = 1, WrenBeforeSpell = 2, WrenBaby = 3, WrenChores = 4, WrenSnacks = 5,",
        "        WrenRoar = 6, WrenCageOpen = 7, WrenNoDying = 8, WrenStayIn = 9, WrenWelcomeBack = 10,",
        "        WrenPestSpell = 11, WrenPestToad = 12, WrenPestsGone = 13,",
        "        HagathaHush = 0, HagathaAnother = 1, HagathaBerserker = 2, HagathaTale1 = 3, HagathaTale2 = 4,",
        "        HagathaTale3 = 5, HagathaTale4 = 6, HagathaCageOpen = 7,",
        f"        WrenMolt = {WREN_MOLT}, WrenMoltReady = {WREN_MOLT_READY}, HagathaMoltFirst = {HAGATHA_MOLT_FIRST},"
        "   // task 018 (+ the quest's index)",
        f"        HagathaNoTale = {HAGATHA_NO_TALE}, WrenApprentice = {WREN_APPRENTICE},",
        "    };",
        "",
        "    // Task 018: Hagatha's tale of a shape (\"Tell me about the shape I wear\"), Wren's word on a shape she sees.",
        "    struct ShapeLine { uint32_t Shape; uint8_t Group; };",
        "    constexpr ShapeLine HagathaShapeTales[] =",
        "    {",
        *[f"        {{ {s}, {g} }}," for s, g in sorted(HAGATHA_TALE_OF.items())],
        "    };",
        "    constexpr ShapeLine WrenShapeReactions[] =",
        "    {",
        *[f"        {{ {s}, {g} }}," for s, g in sorted(WREN_REACTION_OF.items())],
        "    };",
        "}",
        "",
        "#endif",
        "",
    ])


def build_md() -> str:
    md = ["# The Hollowmoor sisters: the Devourer's trainers and its level-5 intro",
          "",
          "Generated by `tools/witch_sisters.py` (task 010) — edit the script, not this file. Lines marked *draft* are "
          "first drafts in the owner's descriptions of the sisters; *PLACEHOLDER* lines only make the flow work.",
          "",
          f"- **{HAGATHA}**: the folklore sister. Looks like creature 11872 (Myranda the Hag).",
          f"- **{WREN}**: the task sister. Looks like creature 2963 (Windfury Wind Witch, a harpy: half feather, half "
          "girl).",
          "",
          "## The In-Between",
          "",
          f"Map **{MAP}** (`StormwindPrison`, unused, not instanced): the round hall of the old prison, nothing outside "
          f"its walls. Cage (where the Devourer wakes): **{CAGE[0]}, {CAGE[1]}, {CAGE[2]}**. A freed Devourer that "
          f"comes back (`.inbetween`) arrives at {ARRIVE[0]}, {ARRIVE[1]}, {ARRIVE[2]}. "
          "GM: `.go xyz -98 150 -40.3 35`.",
          "",
          "| Spawn | What | Where |",
          "|---|---|---|"]
    for e, g, n, _, _, x, y, z in SISTERS:
        md.append(f"| creature {g} | {n} ({e}) | {x}, {y}, {z} |")
    md.append(f"| creature {VOID_SPAWN[0]} | the void under the cage ({NPC_VOID}) | the cage |")
    names = {e: n for e, _, _, n, _, _ in GO_TEMPLATES}
    for i, (e, x, y, z, _) in enumerate(GO_SPAWNS):
        md.append(f"| gameobject {SPAWN_FIRST + i} | {names[e]} ({e}) | {x}, {y}, {z} |")
    md += ["", f"The Devourer's own cage ({GO_CAGE}, display 4154) is summoned by the module for each Devourer, and "
           "opens when the third chore is handed in.", "",
           "## How it goes", "",
           "1. A Devourer reaches level 5 (or logs in at 5+ without having finished): Wren's whisper, a dark flash, "
           "and it is pulled into the In-Between (not from a dungeon, battleground, flight or fight: the module waits).",
           "2. It wakes asleep in the cage; the sisters talk; Wren turns it into a **Baby Berserker** (shape 4, base "
           "colouring, worn at once) and offers the first chore.",
           "3. Three chores (below). Until the last is handed in, the cage holds it (it is put back if it strays).",
           "4. The cage opens; both sisters train it from now on. \"Send me back to where you found me\" returns it to "
           "where the ritual took it.",
           "5. Later, `.inbetween` (a stopgap until the proposed spell, see the PR) brings a freed Devourer back here.",
           "", "## The chores", ""]
    for qd in QUESTS:
        giver = HAGATHA if qd["giver"] == NPC_HAGATHA else WREN
        md += [f"### {qd['id']} {f(qd['title'])} ({giver})", "",
               f"*Objective:* {f(qd['log'])}", "",
               f"> {f(qd['details']).replace('$B$B', ' / ')}", "",
               f"*Not done yet:* {f(qd['incomplete'])}  ", f"*Handed in:* {f(qd['reward']).replace('$B$B', ' / ')}", ""]
    md += ["## The molt quests (task 018)", "",
           "When a form has everything its evolution needs (Bio Points, level, any one task), the module puts its molt "
           "quest in the log, already done, and Wren calls from afar. Handing it in to Wren in the In-Between is the "
           "evolution: she peels the old body, Hagatha tells the tale of the new one. The earlier form stays.", "",
           "| Quest | Title | Hagatha's tale |", "|---|---|---|"]
    md += [f"| {qd['id']} | {f(qd['title'])} | {MOLT_TALES[qd['shape']]} |" for qd in MOLT_QUESTS]
    md += ["", "## The daily chores (task 019)", "",
           "Three daily quests at Wren, one per tier of form (1 = a starter form, 2 = a form grown out of one, 3 = "
           "grown out of that), open once the circle has let the Devourer go. Each asks for "
           f"{CHORE_COUNT} of a reagent that only comes out of a meal eaten in a form of that tier: each meal in the "
           f"right tier leaves one with a {CHORE_CHANCE}% chance (`Mgr::ChoreDrop`, only while the quest is in the "
           "log). Handing it in gives Bio Points to the form worn (`Mgr::ChoreReward`).", "",
           "| Quest | Tier | Level | Title | Reagent (item) | Bio Points |", "|---|---|---|---|---|---|"]
    md += [f"| {c['id']} | {c['tier']} | {c['level']} | {f(c['title'])} | {c['item']} ({c['item_id']}) | {c['bp']} |"
           for c in CHORES]
    md += ["", "## Lines (creature_text)", "", "| Who | Group | When | Line | |", "|---|---|---|---|---|"]
    when = {(NPC_WREN, 0): "the ritual takes hold (whisper)", (NPC_HAGATHA, 0): "asleep in the cage",
            (NPC_WREN, 1): "it wakes", (NPC_HAGATHA, 1): "", (NPC_WREN, 2): "before the spell",
            (NPC_WREN, 3): "it is a Baby Berserker", (NPC_HAGATHA, 2): "", (NPC_WREN, 4): "first chore offered",
            (NPC_WREN, 5): "snacks tossed in", (NPC_WREN, 6): "it roared at her", (NPC_HAGATHA, 3): "the tale 1/4",
            (NPC_HAGATHA, 4): "the tale 2/4", (NPC_HAGATHA, 5): "the tale 3/4", (NPC_HAGATHA, 6): "the tale 4/4",
            (NPC_WREN, 7): "the cage opens", (NPC_HAGATHA, 7): "the cage opens", (NPC_WREN, 8): "died in the cage",
            (NPC_WREN, 9): "strayed from the cage", (NPC_WREN, 10): "came back with .inbetween",
            (NPC_WREN, WREN_MOLT): "a molt quest handed in", (NPC_WREN, WREN_MOLT_READY): "a form is ready (whisper)",
            (NPC_HAGATHA, HAGATHA_NO_TALE): "a shape with no tale yet",
            (NPC_WREN, WREN_APPRENTICE): "her apprentice joins the Devourer",
            **{(NPC_HAGATHA, g): f"the tale of shape {s}" for s, g in HAGATHA_TALE_OF.items() if g >= HAGATHA_SHAPE_FIRST},
            **{(NPC_WREN, WREN_REACTION_FIRST + i): "back in shape " + ", ".join(map(str, shapes))
               for i, (_, shapes) in enumerate(WREN_REACTIONS)},
            **{(NPC_HAGATHA, HAGATHA_MOLT_FIRST + i): f"the {m.name} molt" for i, m in enumerate(evolved_kit.MOLTS)}}
    for c, g, t, _, d in TEXTS:
        md.append(f"| {HAGATHA_SHORT if c == NPC_HAGATHA else WREN_SHORT} | {g} | {when.get((c, g), '')} | {f(t)} | {d} |")
    md += ["", "## Gossip texts", "", "| npc_text | Shown to | Text | |", "|---|---|---|---|"]
    shown = {}
    for m, (a, b_, c) in MENU_TEXTS.items():
        who = HAGATHA_SHORT if m == MENU_HAGATHA else WREN_SHORT
        shown[a], shown[b_], shown[c] = f"{who}: a caged Devourer", f"{who}: a freed Devourer", f"{who}: anyone else"
    for i, t, d in NPC_TEXTS:
        md.append(f"| {i} | {shown[i]} | {f(t)} | {d} |")
    md += ["", "Options: training, unlearn talents, dual spec, \"Send me back\" and Hagatha's \"Tell me about the shape "
           "I wear\" (task 018) only for a freed Devourer; Hagatha's \"Tell me the tale\" only during the third chore.",
           "", "Task 018: when a freed Devourer comes back (`.inbetween`), Wren has a word on the shape it wears; Hagatha "
           "tells the tale of the worn shape on request (the evolved forms' molt tales, the Warp Stalker's intro line).",
           ""]
    return "\n".join(md)


def main() -> int:
    # Plain "\n" line ends on every system, so the output is the same wherever the script runs.
    OUT_SQL.write_text(build_sql(), encoding="utf-8", newline="\n")
    OUT_H.write_text(build_header(), encoding="utf-8", newline="\n")
    OUT_MD.write_text(build_md(), encoding="utf-8", newline="\n")
    print(f"{len(SISTERS)} sisters, {len(QUESTS)} chores, {len(MOLT_QUESTS)} molt quests, {len(TEXTS)} lines, "
          f"{len(GO_SPAWNS)} objects in the In-Between")
    for p in (OUT_SQL, OUT_H, OUT_MD):
        print(f"wrote {p.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
