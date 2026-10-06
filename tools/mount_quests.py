"""Task 022: the mount quests (Wren's Menagerie). Part 1: the frame and ideas 5-14.

Every quest starts at Wren's WANTED board in the In-Between and rewards the reins from the mounts thread's
"Mounts - How to get them" (9304xxx; the first colour of a family, the others come from Hagatha's Breeding Pen).
Looks for the quests' own creatures come from the mounts thread's display creatures (9302xxx) where a grown beast
is wanted. Places were checked against the world database and the map files (2026-10-06).
"""

from devourer_quests import (devour, slay, visit, touch, item, emote, ability, trail, struck, spare, among, tale,
                             carry, fish, wake, gossip, LINES, EMOTE_PET, EMOTE_ROAR, EMOTE_HUG, EMOTE_WAVE,
                             EMOTE_DANCE, EMOTE_KISS, EMOTE_BOW, EMOTE_CHEER, HAGATHA, WREN)
from devourer_quests_content import FACTION_SHY, T_BEAST, T_DRAGON, T_DEMON, T_ELEMENTAL, T_UNDEAD, T_HUMANOID

IN_BETWEEN = 35
Z_HALL = -40.1                                # the floor of the hall (the sisters stand at -40.11)
WANTED_POSTER = 2491                          # the look of the WANTED board
BONFIRE, BAIT, CANDLE, CRYSTAL = 200, 216, 4152, 2971
EGG, EGG_RAPTOR, EGG_BLACK, EGG_EASTER = 276, 321, 477, 1407
SCROLL, BOOK, HOT_COALS, LANTERN_HANGING, LANTERN_BLUE = 210, 254, 2470, 6537, 6666
BUCKET, CAULDRON, BROOM, FLOWERS, GIFT, BONES, CHEST, BANNER, GRAVE, TOMBSTONE = (239, 216, 6401, 63, 5254, 758, 10,
                                                                                 2552, 49, 193)
FISH_BOX, BRAZIER, RUNE_BLUE, ALTAR, LAMPPOST, MACHINE, MACHINE_BROKEN, GEAR, ANVIL = (6396, 201, 342, 227, 5671, 231,
                                                                                      7073, 451, 166)
SHIP_BELL, ARMOR_STAND, HELM, CAGE, PUMPKIN, SNOWPILE, FEATHER, CRATE, KEG = 4052, 7736, 8221, 3551, 60, 9037, 2630, 275, 32
EMOTE_SIT, EMOTE_SLEEP, EMOTE_WHISTLE, EMOTE_SALUTE, EMOTE_SHOO, EMOTE_LAUGH, EMOTE_NO, EMOTE_FLEX, EMOTE_STARE = (
    86, 87, 104, 78, 129, 60, 66, 41, 90)     # TEXT_EMOTE_* (SharedDefines.h)
EMOTE_KNEEL, EMOTE_GROVEL, EMOTE_SNIFF = 59, 51, 132
EMOTE_SING = 433

# Zones (AreaTable), for the quest log
Z_INBETWEEN, Z_UNGORO, Z_HINTERLANDS, Z_SHOLAZAR, Z_STORMPEAKS, Z_ASHENVALE, Z_FERALAS, Z_GRIZZLY, Z_NAGRAND = (
    0, 490, 47, 3711, 67, 331, 357, 394, 3518)
Z_MOONGLADE, Z_EPL, Z_ICECROWN, Z_DUSTWALLOW, Z_SWAMP, Z_ZANGAR, Z_TIRISFAL, Z_TEROKKAR, Z_DUSKWOOD, Z_BLOODMYST = (
    493, 139, 210, 15, 8, 3521, 85, 3519, 10, 3525)
Z_ALTERAC, Z_HELLFIRE, Z_WESTFALL, Z_STV, Z_WETLANDS, Z_DALARAN, Z_BOREAN, Z_TANARIS, Z_BADLANDS, Z_SILITHUS = (
    36, 3483, 40, 33, 11, 4395, 3537, 440, 3, 1377)

# The mounts' display creatures (tools/mounts/ascension/stage/manifest.json): "creature" of each preview number.
def mount_look(preview):
    return 9302000 + preview


class Reins:
    """The reward reins (first colour) by preview number, from "Mounts - How to get them"."""
    BY_PREVIEW = {
        16: (9304035, "Gilded Ravasaur"), 97: (9304182, "High Shaman's Aerie Gryphon"), 102: (9304195, "Reins of the Emerald Hippogryph"),
        117: (9304210, "Predatory Bloodgazer"), 336: (9304645, "Clutch of Ji-Kun"), 338: (9304650, "Reins of the Armored Skyscreamer"),
        86: (9304157, "Reins of the Autumnal Dreamweaver"), 87: (9304158, "Reins of the Tangled Dreamweaver"),
        88: (9304159, "Reins of the Wintertide Dreamweaver"), 89: (9304160, "Anu'relos's Reins"), 90: (9304161, "Lumi'ara's Reins"),
        91: (9304162, "Nyxaroth's Reins"), 92: (9304163, "Verdara's Reins"), 105: (9304198, "Reins of the Aquamarine Dreamer"),
        106: (9304199, "Reins of the Russet Dreamer"), 107: (9304200, "Reins of the Violet Dreamer"), 108: (9304201, "Reins of the Sylverian Dreamer"),
        116: (9304209, "Enchanted Fey Dragon"), 172: (9304341, "Mystic Dreamrunner"), 173: (9304342, "Bastion Dreamrunner"),
        178: (9304349, "Reins of the Goldenback Cloudstrider"), 294: (9304575, "Ochre Dreamtalon's Reins"), 295: (9304577, "Springtide Dreamtalon's Reins"),
        39: (9304070, "Reins of the Tan Riding Camel"), 40: (9304074, "Reins of the Explorer's Dunetrekker"), 48: (9304086, "Reins of the White Magical Rooster"),
        139: (9304260, "Ancient Spiritwalker"), 150: (9304283, "Treasure-Extractor G-774"), 151: (9304284, "Great Treasure-Extractor G-3000"),
        254: (9304507, "Pandaren Kite String"), 269: (9304536, "Beloved Raptor of an Ancient King"), 312: (9304604, "Fossilized Raptor"),
        313: (9304605, "Reins of the Scourgelord's Deathcharger"), 314: (9304606, "Vicious White Bonesteed"), 327: (9304625, "Bucky's Reins"),
        344: (9304672, "Golden Crocolisk"), 347: (9304686, "Prized Turkey's Saddle"), 361: (9304703, "Vulpin Hyena"), 369: (9304717, "Lightning Charged Cloud"),
        66: (9304111, "Reins of the Dusky Undying Darkhound"), 72: (9304128, "Soultwisted Deathwalker"), 73: (9304131, "Battle Gargon Vrednic"),
        80: (9304145, "Decaying Reins of the Vilebrood Vanquisher"), 131: (9304233, "Maldraxxian Corpsefly"), 218: (9304440, "Hand of Hrestimorak"),
        219: (9304442, "Reins of the Fallen Charger"), 322: (9304620, "Reins of the Soulhound"), 323: (9304621, "Wicked Soul Distorter"),
        26: (9304049, "Reins of the Subdued Bat Loa"), 33: (9304057, "Honeyback Hivemother"), 38: (9304067, "Pearlescent Butterfly's Saddle"),
        109: (9304202, "Reins of the Vulpine Familiar"), 110: (9304203, "Reins of the Golden Vulpine Familiar"), 119: (9304215, "Reins of the Undercity Plaguebat"),
        132: (9304234, "Misty Fox"), 190: (9304382, "Pale Harrower's Saddle"), 232: (9304469, "Amber Ardenmoth"),
        242: (9304488, "Dark Ranger General's Dreadwing Saddle"), 262: (9304519, "Reins of the Tamed Skitterfly"), 274: (9304542, "Reins of The Wind Raven"),
        275: (9304543, "Prophet's Great Raven"), 339: (9304651, "Reins of the Sapphire Gulper"), 340: (9304656, "Arboreal Gulper"),
        341: (9304657, "Yellow Marsh Hopper"), 342: (9304660, "Ebony Spiteful Frog"), 362: (9304705, "Reins of the Vulpine Familiar (Black)"),
        363: (9304710, "Spectral Familiar's Everlasting Echo"),
        34: (9304060, "Reins of the Bloodgorged Crawg"), 44: (9304080, "Violet Slimesaber's Reins"), 45: (9304083, "Prismatic Slimesaber's Reins"),
        49: (9304087, "Reins of the Saprophyte Amalgam"), 50: (9304088, "Reins of the Molten Cormaera"), 246: (9304494, "Wriggling Parasite"),
        311: (9304601, "Subjugated Chimeric Embryo"),
        21: (9304044, "Voidbound Bat"), 22: (9304045, "Voidbound Gryphon"), 23: (9304046, "Voidbound Hippogryph"), 24: (9304047, "Voidbound Wyvern"),
        189: (9304381, "Corridor Creeper"), 191: (9304383, "Armored Voidborne Noctivagant"), 256: (9304509, "Reins of Sha-touched Cloud Serpent"),
        263: (9304524, "Encapsulated Void Orb"), 299: (9304587, "Voidbound Force"), 309: (9304597, "Reins of the Sha-touched Spiritclaw"),
        358: (9304698, "Armored Voidwing"), 359: (9304699, "Uncorrupted Voidwing"), 360: (9304700, "Void Rat"), 367: (9304715, "Reins of the Black Warp Stalker"),
        143: (9304268, "Cutlass's Saddle"), 249: (9304501, "Charming Courier's Saddle"),
        100: (9304189, "Reins of the Alliance Electro Eel"), 211: (9304421, "Wonderous Wavewhisker"), 247: (9304496, "Depraved Underlight Shorestalker's Reins"),
        296: (9304579, "Reins of the Blue Salamanther"), 308: (9304596, "Silent Glider"), 319: (9304612, "Reins of the Serene Loyal Snapdragon"),
        320: (9304618, "Reins of the Royal Snapdragon"), 349: (9304689, "Tuskarr Shoreglider"),
        29: (9304053, "Arktos"), 113: (9304206, "Alabaster Thunderwing"), 216: (9304431, "Reins of the Blue Plainswalker Bearer"),
        284: (9304554, "Reins of the Grey Riding Yak"), 321: (9304619, "Bound Blizzard"), 331: (9304631, "Valarjar Stormwing"),
        368: (9304716, "Glacial Tidestorm"), 376: (9304737, "Winter Wilderling Harness"),
    }

    @classmethod
    def get(cls, preview):
        entry, name = cls.BY_PREVIEW[preview]
        return (entry, name, 1)


def reins(*previews):
    return [Reins.get(p) for p in previews]


def wanted(book):
    """Wren's WANTED board: the gameobject questgiver every idea starts at (spot D of the In-Between layout)."""
    return book.lantern("wanted", "the In-Between", IN_BETWEEN, -93.0, 121.5, Z_HALL, 1.57, "Wren's WANTED board, by the trophy wall",
                        name="Wren's WANTED Board", display=WANTED_POSTER, size=1.6)


# Zack 2026-10-06: ideas 39-58 (mount_quests_c) are for later; they stay written but out of the install.
LATER = True


def build(book):
    board = wanted(book)
    import mount_quests_b
    import mount_quests_c
    egg(book, board)
    shards(book, board)
    finds(book, board)
    light(book, board)
    shapes(book, board)
    familiar(book, board)
    thin_places(book, board)
    postcards(book, board)
    lighthouses(book, board)
    peaks(book, board)
    mount_quests_b.build(book, board)
    if not LATER:
        mount_quests_c.build(book, board)
    give_forms(book)


# Zack 2026-10-06: every quest gives the Devourer something, a mount or a form. The steps that give no mount give a
# colouring that has to be earned (never one that comes free with its shape), each chosen for the quest's place.
FORMS = {
    9109010: (35, "Proto-Whelp Yellow"),   # the ravasaur egg: something else hatched nearby
    9109011: (35, "Red Whelp"),            # three fires
    9109013: (38, "Hawk Owl"),             # the gryphon egg below Aerie Peak
    9109014: (38, "Ironbeak Owl"),         # the Hinterlands' own owls
    9109016: (35, "Chromatic Whelp"),      # the roc egg in Sholazar
    9109017: (35, "Armored Whelp"),
    9109030: (6, "Rockjaw"),               # the Badlands' bones: the troggs dig there too
    9109031: (5, "Timber"),                # Goldshire: Elwynn's timber wolves
    9109032: (5, "Scavenger"),             # the desert diary
    9109090: (38, "Strigid Owl"),          # postcards: owl post
    9109100: (32, "Dragon Turtle"),        # the lighthouses
    9109140: (21, "Vampiric"),             # Caer Darrow
    9109141: (35, "Nightmare Whelp"),      # Karazhan
    9109142: (35, "Ley Whelp"),            # Dalaran
    9109143: (13, "Warp Stalker"),         # Shattrath
    9109144: (38, "Shadowwing Owl"),       # the Scarlet Monastery
    9109145: (35, "Bronze Whelp"),         # the Hall of Explorers
    9109160: (38, "Skethyl Owl"),          # the ghost knight's Plaguelands
    9109190: (7, "Lynx"),                  # the sapling's forest
    9109210: (10, "Tallstrider"),          # the giant egg ends in Mulgore
    9109220: (41, "Voidling"),             # dust bunnies from the Thin Place
    9109221: (35, "Blue Whelp"),           # hovering over the pond
    9109230: (9, "Thistle"),               # spring, Elwynn
    9109231: (35, "Green Whelp"),          # summer, Stranglethorn
    9109232: (7, "Springpaw"),             # autumn, Eversong
    9109233: (5, "Grey"),                  # winter, Dun Morogh
}


def give_forms(book):
    from devourer_quests import SHAPES
    by_id = {quest.id: quest for quest in book.quests}
    assert len(set(FORMS.values())) == len(FORMS), "a colouring twice"
    for qid, form in FORMS.items():
        quest = by_id.get(qid)
        if not quest:
            continue
        quest.form = form
        quest.story += f" Reward: the {SHAPES[form[0]][0]} form's {form[1]} colouring."


# --- 5. A Letter From the Egg ------------------------------------------------------------------------------------------

# where each chick feels its first storm: high, windy, and somewhere its level can reach
STORMS = {"ravasaur": ("the cloud-serpent mesas of the Thousand Needles", (1, -5328.3, -3056.8)),
          "gryphon": ("the razorbeak cliffs above Aerie Peak", (0, 101.9, -2265.8)),
          "roc": ("the top of the Storm Peaks", (571, 6300.0, -1050.0))}


def egg(book, board):
    book.region("5. A Letter From the Egg (levels 44-76)",
                "You find a warm egg. It hatches into a chick that cannot fly, and it writes to you. Three eggs, three "
                "families: a ravasaur in Un'Goro, a gryphon in the Hinterlands, a roc in Sholazar. Each chick follows "
                "you through its lessons and lands beside you grown.")
    s = Z_INBETWEEN
    chains = (
        ("ravasaur", 9109010, 48, "Un'Goro Crater", 1, (-7900.0, -1700.0, -275.2), EGG_RAPTOR, 6506, "a Ravasaur Chick",
         "the warm rocks east of Fire Plume Ridge", (1, -7160.0, -1140.0), "Fire Plume Ridge", (1, -7020.0, -1700.0),
         (1, -6900.0, -2100.0), 9165, "pterrordax", "Un'Goro's pterrordax", reins(16), mount_look(16), 48),
        ("gryphon", 9109013, 44, "the Hinterlands", 0, (120.0, -3300.0, 117.3), EGG, 2927, "a Gryphon Chick",
         "the hills below Aerie Peak", (0, 221.0, -2606.0), "Shindigger's Camp", (0, -28.0, -2806.0),
         (0, 311.8, -2954.5), 2924, "silvermane wolf", "the silvermane wolves by Quel'Danil Lodge", reins(97, 102), mount_look(97), 44),
        ("roc", 9109016, 75, "Sholazar Basin", 571, (6560.0, 4500.0, -50.2), EGG_BLACK, 28004, "a Roc Chick",
         "the Bonefields in the east of the basin", (571, 6596.0, 4486.0), "the Bonefields", (571, 5300.0, 5200.0),
         (571, 6300.0, -1050.0), 25464, "bloodspore moth", "the Bloodspore Plains' moths", reins(117, 336, 338), mount_look(117), 75),
    )
    for (key, qid, level, region, map_id, (ex, ey, ez), egg_look, clone, chick_name, where, fire1, fire1_name, fire2, fire3,
         moth, moth_name, moth_where, rewards, grown_look, lvl) in chains:
        storm_name, storm = STORMS[key]
        nest = book.thing(f"{key}_egg", "A Warm Egg", egg_look, [(map_id, ex, ey, ez, 0.0)], size=1.2)
        chick = book.beast(f"{key}_chick", chick_name.split(" ", 1)[1], clone, level=level, faction=FACTION_SHY, passive=True,
                           scale=0.35, subname="Cannot Fly Yet")
        hatch = book.thing(f"{key}_hatch", "The Egg, Cracking", egg_look, [(map_id, ex, ey, ez + 0.2, 0.0)], size=1.2,
                           summon=chick.entry, count=1, follow=True)
        grown = book.beast(f"{key}_grown", chick_name.split(" ", 1)[1], clone, display=grown_look, level=level + 2,
                           faction=FACTION_SHY, passive=True, scale=1.0, subname="Grown")
        a = book.quest(
            qid, f"WANTED: {chick_name}'s Egg", level, level - 2, board, board, "wren",
            f"Wren's handwriting, with a drawing of an egg:$B$BSnack! There's an egg in {region}, {where}, and it's "
            "WARM. Somebody left it. I'd sit on it myself but Hagatha says I'm not allowed to leave the cauldron and "
            "also I'd break it.$B$BGo and find it. Put your hand on it. Tell me if it's still warm.",
            f"Find the warm egg in {region}, {where}.",
            "Is it warm? Is it? Go and check!",
            "WARM! I knew it. It's alive in there. It's going to need keeping warm, Snack, and you're going to do it.",
            objectives=[touch(nest, 1, "The warm egg found")], sort=s, xp=3,
            story=f"Wren's WANTED board: find a warm egg in {region}.")
        b = book.quest(
            qid + 1, "Keep It Warm", level, level - 2, board, board, "wren",
            "Wren, serious:$B$BAn egg needs warmth from three fires, Hagatha says, or it hatches crooked. So: carry it "
            f"in your thoughts (I can't make you carry it in your hands, you'd eat it) and go and stand by three fires: "
            f"{fire1_name}, the camp at the next place, and the far one. Stand close. Let it feel the heat.$B$BThen "
            "come back to the nest and watch.",
            "Stand close to three fires for the egg, then go back to the nest and let it hatch.",
            "Three fires, Snack, and then the nest. It's getting cold!",
            "It CRACKED! A chick! It looked at you first, Snack. That means you're its mother. Don't argue, it's "
            "science.$B$BIt can't fly. It's going to follow you everywhere. It'll write to you, Hagatha says; eggs "
            "that are kept warm by witches grow up literate.",
            objectives=[visit("Warmed at the first fire", fire1[0], fire1[1], fire1[2], radius=20.0, stay=10),
                        visit("Warmed at the second fire", fire2[0], fire2[1], fire2[2], radius=25.0, stay=10),
                        visit("Warmed at the third fire", fire3[0], fire3[1], fire3[2], radius=25.0, stay=10),
                        wake(hatch, "The egg hatched")], prev=a.id, sort=s, xp=4,
            mail=("I tried to fly today", "Dear mother. I tried to fly today. I hit a tree. The tree was fine. I am "
                  "mostly fine. Wren says you will teach me. Please come back soon. Your chick. (P.S. What is a mother?)", 1800),
            story="Warm the egg at three fires, then watch it hatch; the chick follows, and writes a letter.")
        c = book.quest(
            qid + 2, "Lessons for a Chick", level + 1, level - 1, board, board, "wren",
            "Wren, reading a letter aloud:$B$B'I tried to fly today. I hit a tree.' Snack, it WROTE to you. We have to "
            "teach it. Three lessons, Hagatha says. One: glide. Take it to a high place and jump off together; it will "
            f"copy you. Two: chase. Let it chase ten of {moth_where} with you, because that is what chicks of its kind "
            f"eat, and also because it's funny. Three: a storm. Take it up to {storm_name}, where the wind is wild, and "
            "let it feel one.$B$BThen look up.",
            f"With the chick following, glide from a height, eat 10 of {moth_where} as it chases them, and stand in the "
            f"wind on {storm_name}. Then look up.",
            "Three lessons, Snack. It's writing to me as well now. The letters are getting longer.",
            "It LANDED. Next to you. Grown! Feathers and everything, or scales, I don't know, I can't see from here. "
            "Its last letter just said 'Look up.' You looked up.$B$BIt wants to carry you now. That's what grown-up "
            "chicks do for their mothers. Don't argue. Science.",
            objectives=[visit("Glided from the clutch's high rock", map_id, fire1[1], fire1[2], radius=40.0, noflying=True),
                        devour(10, f"{moth_name.capitalize()} chased and eaten", entries=[moth]),
                        visit("Stood in the storm", storm[0], storm[1], storm[2], radius=60.0, stay=15)],
            prev=b.id, sort=s, xp=6, items=rewards,
            lures=[book.thing(f"{key}_landing", "Look Up", FEATHER, [(IN_BETWEEN, -92.0, 128.0, Z_HALL, 0.0)], size=0.8,
                              summon=grown.entry, count=1)],
            story=f"Three lessons for the chick (glide, a chase, a storm); it lands beside you grown. Reward: {', '.join(n for _, n, _ in rewards)}.")


# --- 6. Five Shards in Eight Hours ---------------------------------------------------------------------------------------

def shards(book, board):
    book.region("6. Five Shards in Eight Hours (level 60+)",
                "Five dream shards lie in a zone, and only a Royal Blue Flutterer can touch them. Touch the first and "
                "you have eight hours for the other four. Five zones dream; each gives its own dreamer.")
    s = Z_INBETWEEN
    zones = (
        (9109020, "Ashenvale", 1, [(2650.0, -1430.0), (3247.0, -3724.0), (1818.0, -2786.0), (2094.0, -1172.0), (3261.0, 166.0)],
         reins(86, 105, 178), "the dreamweavers of the forest"),
        (9109021, "Feralas", 1, [(-4562.0, 889.0), (-5185.0, 1624.0), (-4428.0, 3198.0), (-5640.0, 1590.0), (-4740.0, 600.0)],
         reins(87, 106, 172), "the tangled dreamers"),
        (9109022, "the Grizzly Hills", 571, [(4162.0, -4135.0), (4718.0, -3855.0), (3897.0, -5163.0), (4156.0, -2964.0), (3800.0, -3600.0)],
         reins(88, 107, 294), "the wintertide dreamers"),
        (9109023, "Nagrand", 530, [(-781.0, 6944.0), (-2048.0, 6352.0), (-1199.0, 7148.0), (-2533.0, 7693.0), (-2200.0, 6700.0)],
         reins(89, 108, 173), "the dreamers of the floating plains"),
        (9109024, "Moonglade", 1, [(7460.0, -3123.0), (7538.0, -3029.0), (7924.0, -2638.0), (7700.0, -2900.0), (7574.5, -2215.4)],
         reins(90, 116, 295), "the fey dreamers"),
    )
    last = None
    for qid, region, map_id, points, rewards, dreamer in zones:
        shards_ = book.thing(f"shard_{qid}", "Dream Shard", CRYSTAL, [(map_id, x, y, 0.0, 0.0) for x, y in points], size=0.4)
        q = book.quest(
            qid, f"WANTED: {region[0].upper() + region[1:]} Dreams", 60, 58, board, board, "wren",
            f"Wren, whispering:$B$BSnack, {region} is dreaming this week. Five dream shards fell into it, faint blue "
            "glimmers that only a royal blue flutterer can touch; anyone else's hand goes straight through. Hagatha "
            "says once you touch the first, the dream knows you're there and the other four start to fade: eight hours, "
            "and then they're gone until the zone dreams again.$B$BWear your flutterer. Don't run at them. Dreams are shy.",
            f"As a Royal Blue Flutterer, touch all five dream shards in {region} within eight hours of the first.",
            "Five shards, Snack, in eight hours, as a flutterer. Is it still dreaming?",
            f"All five! The dream took shape, didn't it? That's {dreamer}, come out of the dream to see who was "
            "touching its shards.$B$BHere. Hagatha says the other colours of this dream come from the Breeding Pen.",
            objectives=[touch(shards_, 5, "Dream shard touched as a Flutterer", shapes=(23,))], sort=s, timed=28800,
            needs=(23,), items=rewards, xp=6, prev=last,
            story=f"As a Royal Blue Flutterer, touch five dream shards in {region} within eight hours. Reward: {', '.join(n for _, n, _ in rewards)}.")
        last = None                               # the zones are independent
    extra = book.quest(
        9109025, "Every Dream at Once", 62, 60, board, board, "hagatha",
        "Hagatha, dry:$B$BYou have touched every dream shard in five lands. Wren is beside herself. There is one more "
        "dreamer, little horror, the one that dreams the other dreams: the dreamweavers' queen, Nyxaroth. She does not "
        "fall into a zone. She comes to a flutterer that has carried all five dreams at once.$B$BWear your flutterer "
        "and come to the Thin Place in the In-Between. Sit. Dream. She will find you.",
        "As a Royal Blue Flutterer, sit at the Thin Place in the In-Between and wait for the dreamweavers' queen.",
        "Sit, little horror. Dreams come to the ones who stay still.",
        "She came. Of course she came; you smelled of five dreams at once.$B$BTake the reins. Do not ride her into a wall.",
        objectives=[visit("Dreamed at the Thin Place as a Flutterer", IN_BETWEEN, -123.0, 149.0, radius=12.0, shapes=(23,), stay=60, still=True)],
        prev=9109024, sort=s, needs=(23,), items=reins(91, 92), xp=7,
        story="After all five zones' shards: sit as a flutterer at the Thin Place until the dreamweavers' queen comes. Reward: Nyxaroth's and Verdara's reins.")
    extra.prev = 9109020


# --- 7. Finds of the World --------------------------------------------------------------------------------------------

def finds(book, board):
    book.region("7. Finds of the World (any level)",
                "Azeroth is full of hidden things: buried bones, Wren's buttons, map scraps. Two rumours teach your nose "
                "the smell; Wren trades runners for the finds. A lost explorer's diary sends you to silly places; her camels and hyenas are still "
                "out there.")
    s = Z_INBETWEEN
    # The finds themselves (bones, buttons, map scraps) are the mounts thread's: 2,477 worldforged spots that only Sniff
    # shows, turned in to Wren (quests 9308121-9308133). These two quests are only the rumours that send you to them.
    a = book.quest(
        9109030, "WANTED: Bones That Remember", 38, 35, board, board, "hagatha",
        "Hagatha, in Wren's wanted notice, crossed out and rewritten:$B$BBones remember how to run, little horror. "
        "They just need reminding. Old runners lie buried all over the world, in pieces, and no map marks them. Your "
        "nose does. Go to the Badlands, where the dragon bones are, turn on your Sniff, and stand among them until "
        "you smell it: disturbed earth, everywhere, under everything.$B$BThen you will know what to look for. Every "
        "fossil fragment you dig up after that, Wren will take; she trades runners for them.",
        "With Sniff on, stand still among the dragon bones in the Badlands until you smell the buried fragments.",
        "Sniff, little horror. Stand still and sniff.",
        "You smelled it. Now you will smell it everywhere: buried fragments, buttons, map scraps, all over the world, "
        "wherever Sniff shows a glint.$B$BDig them up as you go. Wren keeps the tally and pays in runners.",
        objectives=[visit("Smelled the buried fragments among the dragon bones", 0, -6690.0, -3130.0, radius=60.0,
                          sniff=True, stay=20, still=True)], sort=s, xp=4,
        story="A rumour: sniff among the Badlands' dragon bones and learn to smell the world's buried finds (Wren's fossil, button and map-scrap trades).")
    b = book.quest(
        9109031, "WANTED: Wren's Buttons", 20, 15, board, board, "wren",
        "Wren, mortified:$B$BSnack. My good cloak. The one with the frogs on. The buttons came off. ALL of them. They "
        "fell off everywhere I've ever been, which is everywhere.$B$BThey're tiny. You'll never see them. Your nose "
        "will. Go to the Lion's Pride in Goldshire, where I lost the first one, turn on your Sniff and find the glint. "
        "Then you'll know what they smell like, and you can find the rest wherever you go.",
        "With Sniff on, find the glint of Wren's first lost button by the Lion's Pride Inn in Goldshire.",
        "The Lion's Pride, Snack. Sniff. Tiny glint.",
        "That's it, that's one of mine! Now you know the smell. Bring me the rest whenever you find them; I've got "
        "prizes from the fair for every handful, and a turkey for the first lot.",
        objectives=[visit("Sniffed out the first button at the Lion's Pride", 0, -9462.0, 22.0, radius=20.0, sniff=True)],
        sort=s, xp=3,
        story="A rumour: sniff out Wren's first lost button in Goldshire and learn what the rest smell like (Wren's button trades).")
    # The explorer's diary: silly places, then the scorpid nest
    diary = book.thing("find_diary", "A Lost Explorer's Diary", BOOK, [(0, -6273.0, -2940.0, 0.0, 0.0)], size=0.8)
    c = book.quest(
        9109032, "WANTED: The Lost Explorer", 52, 50, board, board, "wren",
        "Wren, worried:$B$BSnack, an explorer went missing in the desert and her diary turned up at the Badlands dig. "
        "Hagatha read it. She says the diary is LYING, on purpose, so nobody follows her. It sends you to Uldaman, "
        "then to Tanaris, then to Silithus, each page sillier than the last.$B$BRead it. Go where it says. Work out "
        "where she really went. Her camels know; they always go home.",
        "Read the lost explorer's diary at the Badlands dig, then go where it sends you: Uldaman's door, Gadgetzan, "
        "and the hives of Silithus.",
        "Three silly places, Snack. Then think.",
        "Silithus. Of course. She went where the diary said NOT to go, three times over. Hagatha says the scorpids have "
        "her. Hagatha says it like it's funny.",
        objectives=[touch(diary, 1, "The explorer's diary read"),
                    visit("Uldaman's door, as the diary said", 0, -6273.0, -2940.0, radius=60.0),
                    visit("Gadgetzan, as the diary said", 1, -7187.0, -3839.0, radius=60.0),
                    visit("The hives of Silithus, as the diary said", 1, -6814.0, 10.0, radius=80.0)],
        sort=s, xp=4,
        story="The lost explorer's diary lies on purpose: follow it to three silly places and work out where she really went.")
    explorer = book.beast("explorer", "Dunetrekker Jo", 7057, level=42, faction=35, passive=True, scale=1.0,
                          subname="Had It Under Control")
    nest = book.thing("find_nest", "A Scorpid Nest", GRAVE, [(1, -6590.0, 255.0, 0.0, 0.0)], size=1.0,
                      summon=explorer.entry, count=1, follow=True)
    d = book.quest(
        9109033, "Under Control", 55, 52, board, board, "wren",
        "Wren, firmly:$B$BShe's in a scorpid nest in the north of Silithus. Pull her out. Eat the scorpids if they "
        "argue. She will tell you she had it under control. She did not.$B$BHer camels wandered off when the scorpids "
        "came; their tracks lead north from the nest. Follow them with Sniff. They come home with whoever finds them.",
        "Pull the explorer out of the scorpid nest in Silithus, eat 4 stonelash scorpids, then follow the camels' "
        "tracks with Sniff.",
        "Is she out? Are the camels home? Did she say 'under control'?",
        "'Under control.' She said it! Hagatha owes me a spoon.$B$BThe camels came home with you. One of them is "
        "yours now; the explorer says she can't afford to feed three. Here's its reins, and her dunetrekker's, which "
        "she's lending you forever.",
        objectives=[wake(nest, "The explorer pulled out of the nest"),
                    devour(4, "Stonelash scorpid devoured", entries=[11735]),
                    trail("The camels' tracks followed", "the camels", 1,
                          [(-6560.0, 400.0), (-6480.0, 600.0), (-6400.0, 780.0), (-6300.0, 950.0)], summon=0)],
        prev=c.id, sort=s, items=reins(39, 40), xp=6,
        story="Pull the explorer out of a scorpid nest and follow her camels' tracks home. Reward: the Tan Riding Camel and the Explorer's Dunetrekker.")
    e = book.quest(
        9109034, "The Guide's Hyenas", 56, 53, board, board, "wren",
        "Wren, reading the diary's last page:$B$BShe had a guide. A vulpera, with hyenas. The hyenas ran when the "
        "scorpids came too, and they're still out there, laughing at the desert. The guide says they come to anyone "
        "who can laugh louder than they can.$B$BSniff out their tracks south of Gadgetzan, find the pack leader, and "
        "laugh at it. Properly. Until it stops.",
        "Follow the hyenas' tracks south of Gadgetzan with Sniff, then /laugh at the guide's hyena when you find it.",
        "Laugh LOUDER, Snack.",
        "They stopped laughing. Then one of them came and sat on your foot. That's a hyena saying yes.$B$BHere's its "
        "reins. It still laughs in its sleep.",
        objectives=[trail("The hyenas' tracks followed", "the guide's hyenas", 1,
                          [(-7300.0, -3600.0), (-7420.0, -3750.0), (-7560.0, -3900.0)],
                          summon=book.beast("guide_hyena", "The Guide's Hyena", 5425, display=mount_look(361), level=43,
                                            faction=FACTION_SHY, passive=True, scale=0.9, subname="Laughs at the Desert").entry),
                    emote(1, "The guide's hyena out-laughed", EMOTE_LAUGH, entries=[book.beasts[-1].entry])],
        prev=d.id, sort=s, items=reins(361), xp=5,
        story="Sniff out the vulpera guide's hyenas and out-laugh them. Reward: Vulpin Hyena.")


# --- 8. Carrying the Light ----------------------------------------------------------------------------------------------

def light(book, board):
    book.region("8. Carrying the Light (levels 60-80)",
                "The cauldron needs light to wake the dead steeds. Soul-lanterns lie in the Plaguelands and Icecrown; "
                "carrying one slows you, and it dims on the way. Bring enough of them and a steed climbs out with the "
                "name of someone it once carried.")
    s = Z_INBETWEEN
    small = book.thing("light_small", "Soul-Lantern", LANTERN_BLUE,
                       [(0, 2300.0, -5300.0, 0.0, 0.0), (0, 1870.0, -3210.0, 0.0, 0.0), (0, 2692.0, -4029.0, 0.0, 0.0)], size=0.8,
                       shared=True)
    big = book.thing("light_big", "Great Soul-Lantern", LANTERN_HANGING, [(571, 7260.0, 1177.0, 0.0, 0.0)], size=1.2)
    chain = [
        (9109050, "WANTED: A Lantern for the Cauldron", 60, "Hagatha:$B$BThe dead steeds in my cauldron want light, little horror, "
         "and not the kind a candle gives. Soul-light. It gathers in lanterns where many died: Light's Hope, the Marris Stead, "
         "the Argent camp in the Plaguelands. Pick one up. It will weigh on you, and it dims as you walk; walk steadily and "
         "bring it to the cauldron before it goes out.$B$BIf it goes out, you start again. The dead are patient. I am not.",
         "Carry a soul-lantern from Light's Hope Chapel to Hagatha's cauldron in the In-Between before it goes out.",
         "The lantern is dark? Then pick up another. Steadily, this time.",
         "Light. The cauldron drinks it. Something stirs at the bottom, little horror. It will need more.",
         small, 0, 2300.0, -5300.0, 900, 25, reins(322), "Soul-light delivered"),
        (9109051, "A Second Lantern", 62, "Hagatha:$B$BOne lantern woke one. There are more steeds down there, and the next "
         "wants the light from the Marris Stead, where the Blightcaller keeps his hounds. Carry it the same way. The road is "
         "longer; the light is not.",
         "Carry the soul-lantern from the Marris Stead to Hagatha's cauldron before it goes out.",
         "Dark again? The road is long. Walk it steadily.",
         "It climbed out. Did you see its eyes? It remembers the one it carried, and it has decided you will do.",
         small, 0, 1870.0, -3210.0, 900, 25, reins(66, 219), "Soul-light delivered"),
        (9109052, "The Argent Lantern", 64, "Hagatha:$B$BThe Argent camp's lantern is the heaviest of the three; the light in "
         "it is the kind that fought back. Carry it. Your companions may carry one too, if you ask them (they walk slower as "
         "well; it is only fair).",
         "Carry the soul-lantern from the Argent Dawn's camp to Hagatha's cauldron before it goes out.",
         "The Argent light is stubborn. So are you.",
         "Three lights. Three steeds. The cauldron is nearly full; one more and it opens.",
         small, 0, 2692.0, -4029.0, 900, 35, reins(72, 80), "Soul-light delivered"),
        (9109053, "The Great Lantern of Icecrown", 78, "Hagatha, very quietly:$B$BThe last lantern hangs in the Valley of "
         "Lost Hope in Icecrown, and it is great: five lanterns' worth of light, and five lanterns' weight. It dims fast. "
         "There are braziers on the road that will feed it; stop at them. Bring it to the cauldron, and the cauldron will "
         "open.",
         "Carry the Great Soul-Lantern from the Valley of Lost Hope to Hagatha's cauldron, feeding it at the braziers on the "
         "way, before it goes out.",
         "The great light is dark? Then Icecrown keeps it a while longer. Go back.",
         "The cauldron opened. They climbed out, all of them, with the names of the ones they carried. They are yours now, "
         "little horror. Wren says they are not scary. Wren is wrong, and right.",
         big, 571, 7260.0, 1177.0, 1200, 50, reins(73, 131, 218, 323), "The great soul-light delivered"),
    ]
    prev = None
    for qid, title, level, text, log, undone, done, thing, map_id, x, y, seconds, slow, rewards, objtext in chain:
        q = book.quest(
            qid, title, level, level - 2, board, board, "hagatha", text, log, undone, done,
            objectives=[carry(thing, objtext, IN_BETWEEN, -98.0, 157.0, radius=10.0, seconds=seconds, slow=slow,
                              dips=[(7190.0, 1140.0), (7000.0, 1400.0)] if map_id == 571 else [],
                              picked="The soul-lantern is yours to carry. It is heavier than it looks, and it is already dimming.",
                              warning="The soul-lantern dims.", refreshed="The brazier feeds the lantern. It burns brighter.",
                              lost="The soul-lantern has gone out. Pick up another.",
                              delivered="The cauldron drinks the light.")],
            prev=prev, sort=s, items=rewards, xp=7,
            story=f"Carry a soul-lantern (it slows you and dims) to the cauldron. Reward: {', '.join(n for _, n, _ in rewards)}.")
        prev = q.id


# --- 9. Wear the Right Shape --------------------------------------------------------------------------------------------

def shapes(book, board):
    book.region("9. Wear the Right Shape (levels 20-70)",
                "Some creatures only show themselves to one of their own. Come as a toad to the toads, as a bat to the "
                "bats, as a moth to the moths, as an owl to the ravens, as a wolf to the fox familiars. Hold still while "
                "they sniff you; feed them; the oldest follows you out.")
    s = Z_INBETWEEN
    kinds = (
        ("toads", 9109060, 22, "Dustwallow Marsh", 1, (-4227.0, -3261.0), LINES["toad"], "Biletoad (or what it grew into)",
         1420, "Toad", "the toads of the Dragonmurk", "flies", "Hagatha's Fly Jar", reins(341, 339), 23979, mount_look(341)),
        ("frogs", 9109061, 26, "the Swamp of Sorrows", 0, (-10618.0, -3667.0), LINES["toad"], "Biletoad (or what it grew into)",
         6653, "Huge Toad", "the huge toads of the swamp", "flies", "Hagatha's Fly Jar", reins(342, 340), 6653, mount_look(342)),
        ("marshfrogs", 9109062, 62, "Zangarmarsh", 530, (-279.0, 5405.0), LINES["toad"], "Biletoad (or what it grew into)",
         13321, "Frog", "the frogs of Cenarion Refuge", "flies", "Hagatha's Fly Jar", reins(38, 262), 13321, mount_look(38)),
        ("bats", 9109063, 24, "Tirisfal Glades", 0, (2292.0, 292.0), LINES["bat"], "Bat (or what it grew into)",
         10716, "Belfry Bat", "the belfry bats of Brill", "fruit", "A Bowl of Bruised Fruit", reins(119, 26), 1554, mount_look(119)),
        ("deepbats", 9109064, 66, "Terokkar Forest", 530, (-2788.0, 5451.0), LINES["owl"], "Owl (or what it grew into)",
         21324, "Spirit Raven", "the spirit ravens of the Bone Wastes", "shiny things", "A Dish of Shiny Things", reins(274, 275, 242), 21324, mount_look(274)),
        ("moths", 9109065, 64, "Terokkar Forest", 530, (-2727.0, 3275.0), LINES["moth"], "Moth (or what it grew into)",
         18468, "Teromoth", "the teromoths of the forest", "twenty glowing motes and a wish", "A Jar of Glowing Motes", reins(232, 190, 33), 18468, mount_look(232)),
        ("foxes", 9109066, 44, "Feralas", 1, (-4740.0, 600.0), LINES["wolf"], "Wolf (or what it grew into)",
         5286, "Longtooth Runner", "the fox familiars of the Woodpaw Hills", "something the wolves do not eat", "A Saucer of Cream",
         reins(109, 110, 132, 363), 5286, mount_look(109)),
    )
    for key, qid, level, region, map_id, (x, y), shape_line, shape_name, clone, clone_name, who, food, food_name, rewards, pack_clone, look in kinds:
        kind = who.split(" of ")[0][4:]           # "the toads of the Dragonmurk" -> "toads"
        elder = book.beast(f"{key}_elder", f"The Oldest of the {kind.title()}", clone, display=look, level=level,
                           faction=FACTION_SHY, passive=True, scale=1.0, subname="Only Shows Itself to Its Own")
        feed = book.thing(f"{key}_food", food_name, BUCKET, [(map_id, x - 4.0, y - 4.0, 0.0, 0.0)], size=0.6,
                          summon=elder.entry, count=1, follow=True, shapes=shape_line)
        q = book.quest(
            qid, f"WANTED: One of the {kind.title()}", level, level - 2, board, board, "hagatha",
            f"Hagatha:$B$BSome things only show themselves to their own kind, little horror. {who.capitalize()} are like "
            f"that. Go there wearing your {shape_name.split(' (')[0].lower()}, and stand among them. They will crowd round "
            "and sniff you; hold the shape and keep still, or they scatter. When they have decided you belong, put down "
            f"the {food} I have left there ({food_name}, by the water), and the oldest one will follow you out.$B$B"
            "Of course they trust you. You look like dinner. Their dinner.",
            f"As {'an' if shape_name[0] in 'AEIOU' else 'a'} {shape_name}, stand still among {who} until they accept you, then put down {food_name}; the oldest "
            "follows you home.",
            "Hold the shape. Keep still. Let them sniff.",
            "The oldest of them followed you out, and it is still following. It thinks you are its young. Let it.$B$B"
            "Take the reins. The other colours come from the Breeding Pen, as always.",
            objectives=[visit(f"Stood still among the {kind}", map_id, x, y, radius=20.0, shapes=shape_line, stay=20, still=True),
                        wake(feed, f"{food_name} put down; the oldest came")],
            sort=s, needs=shape_line, items=rewards, xp=6,
            story=f"As {'an' if shape_name[0] in 'AEIOU' else 'a'} {shape_name.split(' (')[0]}: stand still among {who} until they accept you, feed them, and the oldest follows you out. Reward: {', '.join(n for _, n, _ in rewards)}.")
        if key == "foxes":                         # a fifth fox, the black familiar, as the quest's one choice
            q.choices = [(e, n) for e, n, _ in reins(362)]
            q.story = q.story[:-1] + ", and the black Vulpine Familiar."


# --- 10. Hagatha's Patchwork Familiar -----------------------------------------------------------------------------------

def familiar(book, board):
    book.region("10. Hagatha's Patchwork Familiar (levels 30-70)",
                "Build a creature from parts you devoured: a body, a skin, a spark. What you put in decides what comes "
                "out. Stir the cauldron and see.")
    s = Z_INBETWEEN
    cauldron = book.thing("familiar_cauldron", "Hagatha's Cauldron (stir)", CAULDRON, [(IN_BETWEEN, -98.0, 158.6, Z_HALL, 0.0)],
                          size=0.5, shared=True)
    recipes = (
        (9109070, "Three Oozes Make a Cat", 52, "three oozes of Un'Goro", [devour(3, "Un'Goro ooze devoured", entries=[6556, 6557, 6559])],
         reins(44), "a Slimesaber"),
        (9109071, "A Crocolisk and the Void", 56, "a Wetlands crocolisk and a void anomaly", [devour(2, "Giant Wetlands Crocolisk devoured", entries=[2089]), devour(2, "Void Anomaly devoured", entries=[17550])],
         reins(246), "a parasite that wriggles"),
        (9109072, "Bones and Fire", 54, "ember worgs and a fire elemental", [devour(3, "Ember worg devoured", entries=[9690, 9694, 9697]), devour(2, "Flamekin devoured", entries=[9778, 9779])],
         reins(50), "a cormaera, still smouldering"),
        (9109073, "Scale and Spore", 64, "a craghide basilisk and the sporebats of Zangarmarsh", [devour(2, "Craghide Basilisk devoured", entries=[20607]), devour(3, "Sporebat devoured", family=33)],
         reins(49), "a saprophyte amalgam"),
        (9109074, "Blood and Thunder", 66, "a felboar and a thunder lizard", [devour(2, "Felboar devoured", entries=[21878, 21195]), devour(2, "Thunder lizard devoured", entries=[3240, 3239, 3238])],
         reins(34), "a bloodgorged crawg"),
        (9109075, "Everything At Once", 68, "a nether drake, a warp chaser and a sporebat", [devour(1, "Nether drake devoured", entries=[18877]), devour(2, "Warp chaser devoured", entries=[18884]), devour(2, "Sporebat devoured", family=33)],
         reins(311), "a chimeric embryo"),
        (9109076, "All the Colours of Ooze", 70, "nine oozes: Un'Goro's, the Hinterlands' jade, Dustwallow's", [devour(3, "Un'Goro ooze devoured", entries=[6556, 6557, 6559]), devour(3, "Jade Ooze devoured", entries=[2656]), devour(3, "Swamp ooze devoured", entries=[4393, 4394])],
         reins(45), "the prismatic slimesaber"),
    )
    prev = None
    for qid, title, level, parts, objectives, rewards, result in recipes:
        q = book.quest(
            qid, ("WANTED: " if not prev else "") + title, level, level - 2, board, board, "hagatha",
            f"Hagatha, stirring:$B$BA body, a skin, a spark, little horror. That is all a creature is, and you carry "
            f"hundreds of each. This one wants {parts}. Eat them; what you eat, you carry. Then come and stir the "
            "cauldron, and we will see what crawls out.$B$BWren wants to keep it. It is YOURS. That is the problem.",
            f"Devour {parts}, then stir Hagatha's cauldron in the In-Between.",
            "The cauldron is waiting. So is Wren, with a name ready.",
            f"It crawled out. {result.capitalize()}, and it has already decided it is yours. Wren named it. I will not "
            "repeat the name.",
            objectives=objectives + [touch(cauldron, 1, "The cauldron stirred")], prev=prev, sort=s, items=rewards, xp=6,
            story=f"Devour {parts}, stir the cauldron: {result}. Reward: {', '.join(n for _, n, _ in rewards)}.")
        prev = q.id if qid == 9109070 else prev


# --- 11. Hagatha's Thin Places -----------------------------------------------------------------------------------------

def thin_places(book, board):
    book.region("11. Hagatha's Thin Places (levels 50-70)",
                "Light Hagatha's candle where the world is thin. For a moment the In-Between bleeds through, and "
                "something looks at you. The fifth one does not leave.")
    s = Z_INBETWEEN
    places = (
        (9109080, "Raven Hill Cemetery", 0, -10500.0, 165.0, 50, "the graves of Raven Hill in Duskwood", 17550, reins(360)),
        (9109081, "the Warp Piston", 530, -1220.0, -11810.0, 52, "the Warp Piston on Bloodmyst Isle", 17550, reins(367)),
        (9109082, "Dalaran Crater", 0, 430.0, 205.0, 54, "the crater where Dalaran stood, in Alterac", 2359, reins(263, 189)),
        (9109083, "Fire Plume Ridge", 1, -7160.0, -1140.0, 56, "Fire Plume Ridge in Un'Goro", 6521, reins(191, 358)),
        (9109084, "the Throne of Kil'jaeden", 530, 903.0, 2317.0, 62, "the Throne of Kil'jaeden in Hellfire", 18977, reins(299, 359)),
    )
    prev = None
    for qid, name, map_id, x, y, level, where, watcher_clone, rewards in places:
        watcher = book.beast(f"thin_{qid}", "Something From Between", watcher_clone, display=9302000 + 263, level=level,
                             faction=14, scale=0.8, subname="It Looked at You")
        candle = book.thing(f"thin_candle_{qid}", "Hagatha's Candle", CANDLE, [(map_id, x, y, 0.0, 0.0)], size=0.8,
                            summon=watcher.entry, count=1)
        q = book.quest(
            qid, ("WANTED: " if not prev else "") + f"A Candle at {name}", level, level - 2, board, board, "hagatha",
            f"Hagatha, low:$B$BThe world is thin at {where}, little horror; worn through like cloth at the elbow. I have "
            "left a candle there. Light it at night, and for a moment the In-Between bleeds through. Something will look "
            "at you. Do not answer if it asks your name.$B$BEat it, if it stays. Things from between are the one meal "
            "you were made for.",
            f"At night, light Hagatha's candle at {where}, and devour what looks through.",
            "The candle is not lit? It only burns at night, little horror.",
            "It looked at you, and you looked back, and you ate it. Good. The thin place is a little thicker now, and "
            "you are a little thinner.$B$BTake what it left.",
            objectives=[wake(candle, f"The candle lit at {name}", night=True), devour(1, "The watcher devoured", entries=[watcher.entry])],
            prev=prev, sort=s, items=rewards, xp=6,
            story=f"Light Hagatha's candle at night at {where}; something looks through; eat it. Reward: {', '.join(n for _, n, _ in rewards)}.")
        prev = q.id
    book.quest(
        9109085, "The Fifth One Stays", 64, 62, board, board, "hagatha",
        "Hagatha:$B$BFive candles, five looks. The fifth one did not go back, little horror; it followed you through, "
        "and it is sitting at the Thin Place in the In-Between, waiting. Things that live between worlds follow "
        "candles. So do the sha-touched beasts and the voidwings; they have been drifting in behind you all week.$B$B"
        "Go and stand at the Thin Place. Let them come. They are yours.",
        "Stand at the Thin Place in the In-Between and let what followed the candles come to you.",
        "They are waiting at the Thin Place.",
        "They came: the bat, the gryphon, the hippogryph, the wyvern, and the one that would not go home. Voidbound, "
        "all of them, and bound to you now.$B$BRide carefully. They remember the other side.",
        objectives=[visit("Stood at the Thin Place for what followed", IN_BETWEEN, -123.0, 149.0, radius=12.0, stay=30)],
        prev=prev, sort=s, items=reins(21, 22, 23, 24), xp=7,
        story="After the five candles: stand at the Thin Place; the voidbound beasts that followed come to you. Reward: the four Voidbound mounts.")
    book.quest(
        9109086, "What the Candles Called", 66, 64, board, board, "hagatha",
        "Hagatha:$B$BMore followed than I counted. A cloud serpent with the sha in it, and a spiritclaw, and a force of "
        "the void that has not decided what shape to be. They are out past the Thin Place, circling. Go and eat "
        "something there, anything, so they see what you are. Then they will settle.",
        "Devour anything within sight of the Thin Place in the In-Between.",
        "They are circling. Eat something where they can see.",
        "They settled. Everything settles, once it has seen you eat.$B$BTake the reins.",
        objectives=[devour(1, "Something devoured at the Thin Place", any_meal=True)], prev=9109085, sort=s,
        items=reins(256, 309), xp=6,
        story="Eat in sight of the Thin Place so the last followers settle. Reward: the Sha-touched Cloud Serpent and Spiritclaw.")


# --- 12. Postcards That Talk Back ---------------------------------------------------------------------------------------

def postcards(book, board):
    book.region("12. Postcards That Talk Back (levels 40-70)",
                "Hagatha will not leave the cauldron but wants to see the world. Sketch six places with a Witch's Eye; "
                "your companions pick their favourites.")
    s = Z_INBETWEEN
    a = book.quest(
        9109090, "WANTED: Six Postcards", 42, 40, board, board, "hagatha",
        "Hagatha, not looking up:$B$BI do not leave the cauldron, little horror. The cauldron does not leave me. But I "
        "would like to see the world, and you are my eyes. Go and stand at six places and LOOK at them, properly, for "
        "a while: the lifts of Thunder Bluff, the Dark Portal, the top of Wyrmrest, the fountain in Dalaran, Booty Bay "
        "at sunset, and the Throne of the Elements. I will see what you see.$B$BAsk your companions which one they liked. "
        "They will have opinions. They always do.",
        "Stand and look for a while at six famous places: Thunder Bluff's lifts, the Dark Portal, Wyrmrest's top, the "
        "Dalaran fountain, Booty Bay, the Throne of the Elements.",
        "Six places, and look properly. I can tell when you are not looking.",
        "I saw them. Booty Bay. Hm. Smells like that from here.$B$BWren pinned them up over the cauldron. The courier "
        "that brought your companions' letters about them wants to stay. So does the pirate's horse from the bay; it "
        "followed the smell.",
        objectives=[visit("Thunder Bluff's lifts, looked at", 1, -1270.0, 45.0, radius=40.0, stay=20),
                    visit("The Dark Portal, looked at", 0, -11905.0, -3207.0, radius=60.0, stay=20),
                    visit("The top of Wyrmrest, looked at", 571, 3546.0, 287.0, radius=40.0, stay=20, above=200.0),
                    visit("Dalaran's fountain, looked at", 571, 5807.0, 683.0, radius=25.0, stay=20)],
        sort=s, xp=5,
        story="Stand and look at six famous places for Hagatha, who never leaves the cauldron (first four).")
    book.quest(
        9109091, "Two More Postcards", 44, 42, board, board, "hagatha",
        "Hagatha:$B$BTwo more, little horror. Booty Bay at sunset, from the pier. And the Throne of the Elements, where "
        "the four of them argue. Look properly.",
        "Look for a while at Booty Bay from the pier at sunset, and at the Throne of the Elements in Nagrand.",
        "Two more. The bay at sunset; the throne any time, they never stop arguing.",
        "Six postcards. Wren has pinned them up and is drawing on them. The courier and the cutlass's horse are "
        "yours; I have no use for a horse, and the courier eats too much.",
        objectives=[visit("Booty Bay at sunset, looked at", 0, -14281.0, 552.0, radius=40.0, stay=20, night=True),
                    visit("The Throne of the Elements, looked at", 530, -781.0, 6944.0, radius=40.0, stay=20)],
        prev=a.id, sort=s, items=reins(143, 249), xp=6,
        story="The last two postcards (Booty Bay at dusk, the Throne of the Elements). Reward: Cutlass's Saddle and the Charming Courier's Saddle.")


# --- 13. The Lighthouse Line ----------------------------------------------------------------------------------------------

def lighthouses(book, board):
    book.region("13. The Lighthouse Line (levels 30-60)",
                "Light the four lighthouses on the coasts at night. When all four burn, something from the deep follows "
                "the light to the Booty Bay pier.")
    s = Z_INBETWEEN
    lamps = book.thing("lighthouse_lamps", "A Lighthouse Lamp", LAMPPOST,
                       [(0, -11060.0, 1580.0, 0.0, 0.0), (0, -3697.0, -817.0, 0.0, 0.0), (1, -3664.0, -4751.0, 0.0, 0.0),
                        (0, -14430.2, 411.0, 0.0, 0.0)], size=0.7, shared=True)
    a = book.quest(
        9109100, "WANTED: Four Lighthouses", 32, 30, board, board, "wren",
        "Wren, lighting a match:$B$BSnack, fish like lights. So do I. There are four lighthouses on the coasts, Westfall's, "
        "Menethil's, Theramore's and Booty Bay's, and nobody lights them any more. Light them. At night, because that's "
        "when lighthouses mean anything. Each one needs a spark; you're a spark, mostly, so just touch the lamp.$B$BWhen "
        "all four burn, go and stand on the Booty Bay pier and watch the water.",
        "At night, light the lamps of the lighthouses at Westfall, Menethil Harbour, Theramore and Booty Bay.",
        "Four lamps, Snack, at night. Fish are watching.",
        "All four! The whole coast is winking. Now the pier. Go and watch.",
        objectives=[touch(lamps, 4, "Lighthouse lamp lit at night", night=True)], sort=s, xp=5,
        story="Light the four lighthouses of the Eastern Kingdoms' coasts at night.")
    deep = book.beast("deep_eel", "Something From the Deep", 2173, display=mount_look(100), level=40, faction=FACTION_SHY,
                      passive=True, scale=1.0, subname="Followed the Light")
    pier = book.thing("lighthouse_pier", "The End of the Pier", FISH_BOX, [(0, -14281.0, 552.0, 8.9, 0.0)], size=0.8,
                      summon=deep.entry, count=1, follow=True)
    b = book.quest(
        9109101, "What Followed the Light", 36, 34, board, board, "wren",
        "Wren, holding her breath:$B$BStand on the end of the Booty Bay pier at night. The lights are all burning. "
        "Something's coming up the coast, following them. Don't eat it. Pat it. It's been in the dark a long time.",
        "At night, stand at the end of the Booty Bay pier and /pet what comes out of the water.",
        "Watch the water, Snack. At night.",
        "An EEL. With lightning in it! And it let you pat it! And it followed you home!$B$BHere's its reins. Hagatha "
        "says there are more down there, and they'll come if you keep the lights lit.",
        objectives=[wake(pier, "Waited at the pier's end at night", night=True),
                    emote(1, "The eel patted", EMOTE_PET, entries=[deep.entry])],
        prev=a.id, sort=s, items=reins(100, 211), xp=6,
        story="Wait at the Booty Bay pier at night; an electro eel follows the light; pat it. Reward: the Electro Eel and the Wavewhisker.")
    more = book.beast("deep_more", "A Snapdragon From the Deep", 2173, display=mount_look(319), level=50, faction=FACTION_SHY,
                      passive=True, scale=1.0, subname="Followed the Light")
    pier2 = book.thing("lighthouse_pier2", "The End of the Pier, Again", FISH_BOX, [(0, -14281.0, 552.0, 8.9, 0.0)], size=0.8,
                       summon=more.entry, count=3, follow=False)
    c = book.quest(
        9109102, "More From the Deep", 50, 46, board, board, "wren",
        "Wren:$B$BKeep the lights lit, Snack: light all four again, at night, and go back to the pier. Hagatha says the "
        "deep has gliders and snapdragons and a salamanther and a shorestalker in it, and they all like lights. Pat the "
        "ones that come. Eat none. I mean it.",
        "At night, light the four lighthouses again and wait at the Booty Bay pier; /pet 3 of what comes.",
        "Lights, then the pier, then patting. No eating.",
        "Three of them, patted, and they all followed you home. The pier's going to need a bigger pier.$B$BHere: the "
        "snapdragon's reins and the others'. The salamanther is pink. Don't tell Hagatha it's pink.",
        objectives=[touch(lamps, 4, "Lighthouse lamp lit again at night", night=True),
                    wake(pier2, "Waited at the pier's end again", night=True),
                    emote(3, "A deep thing patted", EMOTE_PET, entries=[more.entry])],
        prev=b.id, sort=s, items=reins(319, 320, 296, 247), xp=7,
        story="Light the lighthouses again and pat three more things from the deep. Reward: the Snapdragons, the Salamanther, the Shorestalker.")
    book.quest(
        9109103, "The Glider and the Tuskarr", 58, 55, board, board, "hagatha",
        "Hagatha:$B$BThe deep has one more thing in it that follows lights, little horror: a silent glider the tuskarr "
        "of the north talk about, and the tuskarr's own shoreglider that goes with it. The Booty Bay light will not "
        "reach that far. Go to the Howling Fjord, to the Longtusk fishermen's beach, and light a fire there at night. "
        "Then eat what it brings; gliders are not for patting.",
        "At night, stand a while on the Longtusk fishermen's beach in the Howling Fjord and devour 3 of what the fire brings.",
        "The fjord is cold. The glider is colder. Wait.",
        "It came, and you ate it, and the tuskarr's shoreglider came to see what ate it. Both are yours.$B$BTake the reins.",
        objectives=[visit("Waited on the Longtusk beach at night", 571, 717.0, -2838.0, radius=40.0, night=True, stay=20),
                    devour(3, "Fjord thing devoured", family=38)],
        prev=c.id, sort=s, items=reins(308, 349), xp=6,
        story="Wait on the Longtusk beach at night and eat what the fire brings. Reward: Silent Glider and the Tuskarr Shoreglider.")


# --- 14. Ring the Peaks ---------------------------------------------------------------------------------------------------

def peaks(book, board):
    book.region("14. Ring the Peaks (level 77+)",
                "Four bells hang on the Storm Peaks' heights. Climb to them on foot, no flying, and ring them; each bell "
                "wakes a herd. Ring all four within an hour and the storm itself answers.")
    s = Z_INBETWEEN
    bells = (
        (9109110, "Frosthold", 571, 6665.0, -252.0, 962.0, "the bears", 29562, 29, reins(29), "Arktos, the great bear"),
        (9109111, "Dun Niffelem", 571, 7267.0, -2753.8, 870.9, "the yaks", 29562, 284, reins(284, 376), "a grey riding yak and a wilderling"),
        (9109112, "Thunderfall", 571, 7706.0, -3346.0, 890.0, "the mammoths", 25487, 216, reins(216), "a plainswalker bearer"),
        (9109113, "the Terrace of the Makers", 571, 7854.0, -1408.0, 1534.0, "the storm", 29753, 113, reins(113), "an alabaster thunderwing"),
    )
    prev = None
    for qid, name, map_id, x, y, z, herd, clone, look, rewards, what in bells:
        beast = book.beast(f"bell_{qid}", f"One of {herd.capitalize()}", clone, display=mount_look(look),
                           level=78, faction=FACTION_SHY, passive=True, scale=1.0, subname="Came to See Who Rang")
        bell = book.thing(f"bell_thing_{qid}", f"The Bell of {name[0].upper() + name[1:]}", SHIP_BELL, [(map_id, x, y, z, 0.0)], size=1.0,
                          summon=beast.entry, count=1, follow=True)
        q = book.quest(
            qid, ("WANTED: " if not prev else "") + f"The Bell of {name[0].upper() + name[1:]}", 77, 76, board, board, "hagatha",
            f"Hagatha:$B$BA bell hangs at {name}, little horror, high in the Storm Peaks. Climb to it on your own feet, "
            "or on four, or six; no flying mount. If you fall, fall quietly. Ring it, and "
            f"{herd} will come out to see who rang.$B$BOne of them will follow you down.",
            f"Without a flying mount, climb to the bell at {name} and ring it; one of {herd} follows you down.",
            "The bell is not rung. Climb.",
            f"Rung, and {herd} came. {what.capitalize()} followed you down, and it is yours.$B$BTake the reins.",
            objectives=[wake(bell, f"The bell of {name} rung on foot", noflying=True)], prev=prev, sort=s, items=rewards, xp=7,
            story=f"Climb to the bell at {name} without flying and ring it; {what} follows you down. Reward: {', '.join(n for _, n, _ in rewards)}.")
        prev = q.id
    allbells = book.thing("bell_all", "The Four Bells, Again", SHIP_BELL,
                          [(571, 6665.0, -252.0, 962.0, 0.0), (571, 7267.0, -2753.8, 870.9, 0.0),
                           (571, 7706.0, -3346.0, 890.0, 0.0), (571, 7854.0, -1408.0, 1534.0, 0.0)], size=1.0)
    book.quest(
        9109114, "The Storm Answers", 79, 78, board, board, "hagatha",
        "Hagatha, and thunder in the flame:$B$BFour bells, four herds. Now ring all four within one hour, on foot, and "
        "the storm itself gathers over the peaks and comes down to see what is making all that noise.$B$BIt is "
        "yours if you are standing there when it lands. Fall quietly.",
        "Without a flying mount, ring all four bells of the Storm Peaks within one hour.",
        "An hour, little horror. All four. On foot.",
        "The storm came down. A blizzard with a will, a tidestorm, and the Valarjar's own stormwing, all three, to see "
        "who rang. They saw. They stayed.$B$BTake the reins. Ride the storm quietly.",
        objectives=[touch(allbells, 4, "A bell rung on foot within the hour", noflying=True)], prev=prev, sort=s, timed=3600,
        items=reins(321, 368, 331), xp=8,
        story="Ring all four bells within an hour, on foot; the storm answers. Reward: Bound Blizzard, Glacial Tidestorm, Valarjar Stormwing.")
