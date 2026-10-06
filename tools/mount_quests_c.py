"""Task 022: the mount quests, part 3: ideas 39-58 (the elemental kit, Ragnaros's pups, the dragon pilgrimage, the
loa, Hagatha's trials, the Faire, the salvage yard, the silithid hives, the moonwells, the duck pond, Lunar Festival,
the old Horde's banners, Bramble's maiden flights)."""

from devourer_quests import (devour, slay, visit, touch, emote, struck, carry, wake, gossip, LINES, WREN,
                             EMOTE_PET, EMOTE_ROAR, EMOTE_HUG, EMOTE_DANCE, EMOTE_BOW)
from devourer_quests_content import FACTION_SHY
from mount_quests import (Reins, reins, mount_look, IN_BETWEEN, Z_HALL, Z_INBETWEEN, HOT_COALS, BANNER, CHEST, SCROLL,
                          EGG, EGG_BLACK, BUCKET, FLOWERS, GEAR, MACHINE_BROKEN, ANVIL, CRATE, BONES, LANTERN_HANGING,
                          LANTERN_BLUE, FEATHER, RUNE_BLUE, ALTAR, CAGE, KEG, PUMPKIN, EMOTE_WHISTLE, EMOTE_SLEEP,
                          EMOTE_KNEEL, EMOTE_NO)

Reins.BY_PREVIEW.update({
    184: (9304372, "Living Infernal Core"), 281: (9304551, "Inferno Armoredon's Saddle"), 282: (9304552, "Hailstorm Armoredon's Saddle"),
    301: (9304589, "Farseer's Raging Tempest (Wind)"), 302: (9304590, "Farseer's Raging Tempest (Felfire)"),
    303: (9304591, "Farseer's Raging Tempest (Fire)"), 304: (9304592, "Farseer's Raging Tempest (Ice)"),
    305: (9304593, "Farseer's Raging Tempest (Arcane)"), 306: (9304594, "Farseer's Raging Tempest (Earth)"),
    307: (9304595, "Farseer's Raging Tempest (Water)"),
    57: (9304095, "Core Hound"), 58: (9304096, "Void Borne Core Hound"), 60: (9304098, "Arcane Bound Core Hound"),
    65: (9304110, "Dark Iron Hound"), 67: (9304119, "Dark Iron Core Hound"), 70: (9304125, "Darkwell Phoenix"),
    118: (9304214, "Heart of the Everlasting Cinderstalker"), 126: (9304228, "Primal Flamesaber"),
    196: (9304395, "Reins of the Magmatic Steed"), 213: (9304427, "Reins of the Blue Magmammoth"),
    214: (9304428, "Reins of the Orange Magmammoth"), 215: (9304429, "Reins of the Red Magmammoth"),
    255: (9304508, "Reins of the Emerald Pandaren Phoenix"), 260: (9304517, "Sigil of the Crimson Skyblazer"),
    53: (9304091, "Azure Sky Stalker's Reins"), 54: (9304092, "Cadmium Sky Stalker's Reins"), 55: (9304093, "Violet Sky Stalker's Reins"),
    56: (9304094, "Stygian Sky Stalker's Reins"), 85: (9304150, "Reins of the Azure Drake"), 111: (9304204, "Obsidian Worldbreaker"),
    185: (9304376, "Redeemed Timereaver's Saddle"), 240: (9304480, "Reins of the Onyx Netherwing Drake"),
    241: (9304486, "Reins of the Arcane Infused Great-Wyrm"), 243: (9304489, "Smoldering Ember Wyrm"), 264: (9304525, "Spawn of Galakras"),
    315: (9304608, "Essence of the Blue Flight"), 316: (9304609, "Essence of Madrigosa"), 317: (9304610, "Essence of Kalecgos"),
    318: (9304611, "Essence of Anveena"), 385: (9304772, "Armored Obsidian Drake"),
    36: (9304062, "Reins of the Mighty Caravan Brutosaur"), 144: (9304269, "Skittering Shadowfang"),
    238: (9304477, "Reins of the Ashhide Mushan Beast"), 324: (9304622, "Royalfang Widow"),
    337: (9304646, "Reins of the Black Longhorn Thunderspine"), 345: (9304676, "Reins of the Cobalt Primordial Direhorn"),
    388: (9304775, "Bloodbowl Direhorn"),
    75: (9304139, "Reins of the Betrayer's Unscarred Spire Terror"), 76: (9304140, "Reins of the Betrayer's Supreme Spire Terror"),
    77: (9304141, "Reins of the Betrayer's Savage Spire Terror"), 78: (9304142, "Reins of the Betrayer's Felsworn Spire Terror"),
    181: (9304359, "Huntmaster's Fierce Wolfhawk"), 289: (9304570, "Razor-Lined Reins of Dark Portent"),
    364: (9304711, "Netherlord's Chaotic Wrathsteed"), 365: (9304712, "Reins of the Accursed Wrathsteed"),
    17: (9304037, "Blue Gnomish Terratransformer"), 18: (9304039, "Red Goblin Terratransformer"),
    20: (9304043, "Great Magic Azzar Faire Ticket"), 31: (9304055, "Darkmoon Bear"), 47: (9304085, "Crestchroma Chameleon"),
    64: (9304109, "Azzar Faire Bear"), 68: (9304120, "Darkmoon Harlequin's Charger"), 96: (9304175, "Black Faire Nestling"),
    112: (9304205, "Discarded Aerial Attraction: Series X"), 227: (9304459, "Lu-Wu, The Tiger of Fortune"),
    389: (9304776, "Darkmoon Dirigible"),
    103: (9304196, "Meat Wagon"), 104: (9304197, "Necrolord's Meat Wagon's Keys"), 157: (9304299, "Obsidian Shredder Tank"),
    188: (9304379, "Kor'kron Juggernaut"), 193: (9304389, "G.M.O.D"), 204: (9304407, "Bullet Romper Warframe"),
    221: (9304451, "Flarendo the Furious"), 225: (9304457, "High Tinker Mekkatorque's Suit"),
    377: (9304738, "Armored Alliance Wonka"), 378: (9304739, "Gizmo's Wonka"), 379: (9304740, "Armored Horde Wonka"),
    380: (9304741, "Felsteel Wonka"), 381: (9304742, "Void Wonka"), 382: (9304743, "Insignia Red Wonka"),
    10: (9304014, "Malevolent Drone"), 297: (9304584, "Vigilant Guardian"), 346: (9304684, "Rubyshell Krolusk"),
    383: (9304755, "Bloody Carrion Worm's Saddle"),
    71: (9304126, "Ash'adar, Harbinger of the Dawn"), 134: (9304240, "Reins of the Striped Frostsaber"),
    239: (9304479, "Runemaster's Manasaber"), 293: (9304574, "Mystic Runesaber"), 300: (9304588, "Reins of The Chaotic Runesaber"),
    387: (9304774, "Azure Spiritclaw"),
    94: (9304169, "Hateful Duck"), 95: (9304174, "Golden Spectral Duck"),
    207: (9304412, "Scorching Valor's Reins"), 208: (9304413, "Ethereal Might"), 209: (9304414, "Lucky Lunar Rocket"),
    30: (9304054, "Big Battle Bear"), 74: (9304132, "Rabid Worg (White)"), 141: (9304262, "Umberhoof Warboar"),
    142: (9304263, "Blacksteel Battleboar"), 186: (9304377, "Armored Irontusk"), 187: (9304378, "Ironclad War Wolf"),
    202: (9304405, "Reins of the Sunhide Gronnling"), 212: (9304424, "Blisterback Bloodtusk"), 217: (9304435, "Darkmaul"),
    372: (9304724, "Horn of Fenrir"), 374: (9304728, "Riding Harness"), 375: (9304733, "Garn Steelmaw"),
    2: (9304002, "Luxurious Goblin Combat Cruiser"), 3: (9304003, "Void Combat Airship"), 5: (9304005, "Personal Skyship"),
    180: (9304355, "Navy Anti-gravity Office"), 200: (9304402, "Miniature Legion Ship"),
})
EVENT_LUNAR = 7
SHELF = (-98.0, 157.0)                        # Hagatha's shelf, by the cauldron
BOOTY_DOCK = (0, -14281.0, 552.0)
BOOTY_LAP = ((-14281.0, 552.0, "Round the dock"), (-14430.2, 411.0, "Past the scrapyard"), (-14361.9, 372.2, "Up to the bank"))


def build(book, board):
    elements(book, board)
    pups(book, board)
    pilgrimage(book, board)
    loa(book, board)
    trials(book, board)
    faire(book, board)
    salvage(book, board)
    silithid(book, board)
    moonwells(book, board)
    ducks(book, board)
    lunar(book, board)
    banners(book, board)
    flights(book, board)


def _story(text, rewards):
    return text + (" Reward: " + ", ".join(n for _, n, _ in rewards) + "." if rewards else "")


# --- 39. The Elemental Kit -------------------------------------------------------------------------------------------

def elements(book, board):
    book.region("39. The Elemental Kit (level 60+)",
                "Bottle the four elements for Hagatha's shelf. They don't want to be bottled: fire burns through the "
                "jar, air slips out, water freezes your feet, earth makes you slow. Each one has to reach its jar "
                "before it escapes.")
    s = Z_INBETWEEN
    kinds = (
        (9109240, "Fire", "the lava pools of the Searing Gorge, where the magma elementals live", 0,
         (-7213.9, -1624.9), (-7142.7, -1523.5), 30, 0, "it burns through glass in thirty heartbeats",
         "The fire is in your hands. It is not happy. Run.", "It is burning through.", "Fire",
         reins(303, 184)),
        (9109241, "Air", "the Twilight camp's wind-stones in Silithus", 1,
         (-6386.7, 180.9), (-6420.0, 30.0), 40, 0, "it slips out of anything that is not moving",
         "The air is in your hands. Your feet keep leaving the ground. Run before it lifts you away.",
         "It is slipping out.", "Air", reins(301)),
        (9109242, "Water", "the surf by the Twin Colossals in Feralas", 1,
         (-3385.9, 2495.8), (-3129.6, 2257.5), 60, 30, "it freezes whoever carries it, from the feet up",
         "The water is in your hands, and it is cold, colder, your feet are going numb. Keep walking.",
         "Your knees are freezing.", "Water", reins(307)),
        (9109243, "Earth", "the Elemental Plateau in Nagrand", 530,
         (-850.6, 6517.2), (-867.5, 6614.4), 60, 50, "it gets heavier with every step",
         "The earth is in your hands. It weighs as much as a hill and wants to go back to being one.",
         "It is pulling you down.", "Earth", reins(306)),
    )
    prev = None
    for n, (qid, element, where, map_id, src, jar, seconds, slow, trick, picked, warning, word, rewards) in enumerate(kinds):
        source = book.thing(f"element_{element.lower()}", f"Loose {element}", HOT_COALS if element == "Fire" else RUNE_BLUE,
                            [(map_id, src[0], src[1], 0.0, 0.0)], size=0.8)
        jar_spot = book.thing(f"element_jar_{element.lower()}", f"Hagatha's Jar ({element})", KEG,
                              [(map_id, jar[0], jar[1], 0.0, 0.0)], size=0.6)
        q = book.quest(
            qid, ("WANTED: " if not prev else "") + f"Bottled {element}", 60 + n, 58, board, board, "hagatha",
            f"Hagatha, holding up an empty jar:$B$BMy shelf is missing four jars, little horror, and I want them full. "
            f"{element} first" + ("" if not prev else ", now") + f". It lives at {where}. Pick it up and put it in the jar "
            f"I have left nearby. Do not shake the jar. Do not let it shake you.$B$BOne thing: {trick}. Be quick.",
            f"Pick up the loose {element.lower()} at {where.split(',')[0]} and get it into Hagatha's jar before it "
            "escapes.",
            f"Is it in the jar? Is the jar still a jar?",
            f"{element}, bottled, and the jar still in one piece. On the shelf it goes.$B$BIt left something behind "
            "in your hands, little horror. A tempest's worth. Keep it.",
            objectives=[touch(jar_spot, 1, f"The jar for the {element.lower()} found"),
                        carry(source, f"{element} bottled before it escaped", map_id, jar[0], jar[1], radius=6.0,
                              seconds=seconds, slow=slow, picked=picked, warning=warning, lost=f"The {element.lower()} got away.",
                              delivered=f"The {element.lower()} is in the jar.")],
            prev=prev, sort=s, items=rewards, xp=6,
            story=_story(f"Carry loose {element.lower()} from {where.split(',')[0]} to Hagatha's jar before it escapes.", rewards))
        prev = q.id
    shelf = book.quest(
        9109244, "Four Jars on a Shelf", 64, 60, board, board, "hagatha",
        "Hagatha:$B$BFour jars on my shelf, and they argue, little horror. Fire hates water, air hates earth, and all "
        "of them hate me. Stand by the shelf a while and listen; when they have argued themselves out, the tempest "
        "they make between them will choose a colour for you. Possibly three.",
        "Stand by Hagatha's shelf a while and listen to the four jars argue.",
        "Listen. They will tire before you do.",
        "There. They argued until the glass sang, and three tempests came out of the noise: fel, ice and arcane, "
        "the colours of what they called each other.$B$BTake them. My shelf is quiet at last.",
        objectives=[visit("Listened to the jars argue", IN_BETWEEN, SHELF[0], SHELF[1], radius=8.0, stay=30)],
        prev=prev, sort=s, items=reins(302, 304, 305), xp=6,
        story=_story("Stand by the shelf while the four jars argue; the tempest picks colours.", reins(302, 304, 305)))
    book.quest(
        9109245, "Hot Bath, Cold Bath", 66, 62, board, board, "hagatha",
        "Hagatha:$B$BTwo armoredons followed the jars home, little horror, one hot, one cold, and both sulking. The hot "
        "one wants to be cold, the cold one wants to be hot. Stand in the heat of Fire Plume Ridge in Un'Goro, then "
        "in the snow of Winterspring, and let them feel both through you.",
        "Stand a while in the heat of Fire Plume Ridge, then in the snow by Frostsaber Rock in Winterspring.",
        "Hot, then cold. They are watching.",
        "Both armoredons have stopped sulking. One is steaming, one is frosted, both are yours.",
        objectives=[visit("Stood in the heat of Fire Plume Ridge", 1, -7160.0, -1140.0, radius=30.0, stay=20),
                    visit("Stood in the snow of Winterspring", 1, 6915.4, -4129.6, radius=30.0, stay=20)],
        prev=shelf.id, sort=s, items=reins(281, 282), xp=6,
        story=_story("Stand in the heat of Un'Goro and the snow of Winterspring for two sulking armoredons.", reins(281, 282)))


# --- 41. Ragnaros's Lost Pups ------------------------------------------------------------------------------------------

def pups(book, board):
    book.region("41. Ragnaros's Lost Pups (levels 50-60)",
                "Core hound puppies wander the Burning Steppes and burn everything they love. Feed them coals without "
                "hands, walk them home without lighting the grass, meet their mothers, and carry a dying phoenix "
                "ember out of Blackrock.")
    s = Z_INBETWEEN
    den = (-7800.0, -2100.0)
    pup = book.beast("core_pup", "A Lost Core Hound Pup", 385, display=mount_look(57), level=52, faction=FACTION_SHY,
                     passive=True, scale=0.35, subname="Burns Everything It Loves",
                     spawns=[(0, den[0], den[1], 0.0, 1.0), (0, den[0] + 8.0, den[1] - 5.0, 0.0, 2.0),
                             (0, den[0] - 6.0, den[1] + 7.0, 0.0, 4.0)])
    coals = book.thing("pup_coals", "A Heap of Hot Coals", HOT_COALS, [(0, -7723.0, -2055.3, 0.0, 0.0)], size=0.8)
    a = book.quest(
        9109250, "WANTED: Hot Coals for Hot Pups", 52, 50, board, board, "wren",
        "Wren, with a blister on each finger:$B$BSnack, there are PUPPIES in the Burning Steppes. Core hound puppies! "
        "Ragnaros lost them, or they lost him, and they're hungry and they only eat coal and they burn everything they "
        "love, which is everything, which is me.$B$BThere's a heap of hot coals by the old war reavers. Carry one to "
        "the pups. Not in your hands. In your mouth. It's fine, you're a Devourer. Then pet them. Quickly.",
        "Carry a hot coal in your mouth from the heap to the pups' den, then /pet the 3 pups.",
        "Did they eat? Did you keep your eyebrows?",
        "They ATE. And they purred, which for a core hound sounds like a forge. Your eyebrows are mostly there.",
        objectives=[carry(coals, "A hot coal carried to the pups (no hands)", 0, den[0], den[1], radius=15.0, seconds=40,
                          picked="You take the coal in your mouth. No hands. It is very, very hot.",
                          warning="The coal is cooling.", lost="The coal went cold. Get another.",
                          delivered="The pups fall on the coal and crunch it like a biscuit."),
                    emote(3, "Core hound pup petted", EMOTE_PET, entries=[pup.entry])],
        sort=s, xp=5, story="Carry a hot coal in your mouth to three hungry core hound pups, then pet them.")
    walk = book.thing("pup_den", "The Pups' Den", HOT_COALS, [(0, den[0] + 3.0, den[1] + 3.0, 0.0, 0.0)], size=1.0,
                      summon=pup.entry, count=3, follow=True)
    b = book.quest(
        9109251, "Don't Light the Grass", 54, 52, board, board, "wren",
        "Wren:$B$BThey can't stay in a den by the Dark Irons, Snack. Walk them to Morgan's Vigil; the dwarves there have "
        "a forge they can sleep by. Walk. WALK. If you run, they run, and when they run they set the grass on fire, "
        "and the dwarves will blame us.",
        "Call the pups from their den and walk them to Morgan's Vigil without running.",
        "Walking, Snack. Slowly. Everything here is flammable.",
        "Morgan's Vigil, and only one small fire, which the dwarves say was already there. The pups are asleep by the "
        "forge. They glow when they snore.",
        objectives=[wake(walk, "The pups called out of their den"),
                    visit("Walked the pups to Morgan's Vigil", 0, -8378.5, -2748.9, radius=30.0, walking=True)],
        prev=a.id, sort=s, xp=5, story="Walk the pups across the Burning Steppes to Morgan's Vigil without running.")
    mother = book.beast("core_mother", "A Core Hound Mother", 385, display=mount_look(57), level=58, faction=FACTION_SHY,
                        passive=True, scale=1.1, subname="Came Looking")
    howl = book.thing("pup_howl", "The Pups' Bed by the Forge", HOT_COALS, [(0, -8370.0, -2740.0, 0.0, 0.0)], size=0.8,
                      summon=mother.entry, count=1)
    c = book.quest(
        9109252, "Their Mothers Come Looking", 56, 54, board, board, "hagatha",
        "Hagatha:$B$BPups that are warm and fed howl for their mothers, little horror, and their mothers come. Big "
        "ones. Go to the forge at Morgan's Vigil, wake the pups, and when the mother comes, bow. Low. Do not fight her; "
        "she would win, and then she would eat you, and then I would have to find another Devourer.",
        "Wake the pups by the forge at Morgan's Vigil, and /bow to their mother when she comes.",
        "Bow, little horror. Lower than that.",
        "She sniffed you, and the pups, and you again, and decided you were family. Core hounds share their family. "
        "Three of her older pups are yours now; one of them has been somewhere strange and come back glowing.",
        objectives=[wake(howl, "The pups woken; their mother came"),
                    emote(1, "Bowed to the core hound mother", EMOTE_BOW, entries=[mother.entry])],
        prev=b.id, sort=s, items=reins(57, 58, 60), xp=6,
        story=_story("The pups howl; their mother comes to Morgan's Vigil. Bow, don't fight.", reins(57, 58, 60)))
    chains = book.thing("hound_chains", "A Hound's Chain", CAGE,
                        [(0, -7829.9, -2139.0, 0.0, 0.0), (0, -7760.0, -2180.0, 0.0, 0.0), (0, -7690.0, -2110.0, 0.0, 0.0),
                         (0, -7860.0, -2050.0, 0.0, 0.0)], size=0.7)
    book.quest(
        9109253, "The Chained Ones", 56, 54, board, board, "hagatha",
        "Hagatha:$B$BThe mother says she is missing more than pups. The Dark Irons chain hounds in the ruins of "
        "Thaurissan, little horror, to guard their scrap. Four chains. Break them, and the hounds go home to her, and "
        "something else comes with them: a flamesaber that has been hunting the hounds and has decided it would rather "
        "be one.",
        "Break the 4 hounds' chains in the ruins of Thaurissan in the Burning Steppes.",
        "Four chains. The Dark Irons will not like it. Do it anyway.",
        "Four hounds free, and a flamesaber trotting behind them pretending it was always a hound. They are all "
        "yours.",
        objectives=[touch(chains, 4, "A hound's chain broken")], prev=c.id, sort=s, items=reins(65, 67, 118, 126), xp=6,
        story=_story("Break four hounds' chains in the ruins of Thaurissan.", reins(65, 67, 118, 126)))
    ember = book.thing("phoenix_ember", "A Dying Phoenix Ember", HOT_COALS, [(0, -7575.1, -1290.0, 278.3, 0.0)], size=0.6)
    e = book.quest(
        9109254, "Never Let It Go Out", 58, 56, board, board, "hagatha",
        "Hagatha, quietly:$B$BDeep in Blackrock Mountain, in the great hall above the lava, a phoenix ember is dying, "
        "little horror. Carry it out. It dims as you walk; dip it into the lava pools on the way and it brightens. "
        "At the mountain's mouth, where the Burning Steppes begin, it will rise.$B$BIf it goes dark, pick it up again. "
        "But it will remember that it went dark, and so will I.",
        "Carry the dying phoenix ember from Blackrock Mountain's great hall to the mountain's mouth in the Burning "
        "Steppes, dipping it in lava on the way.",
        "Is it still lit? Dip it, little horror. Dip it.",
        "It rose. Out of your hands, over the Steppes, on fire and laughing. It came back down when it had finished "
        "laughing, and it brought two friends.$B$BThey are yours. All three of them.",
        objectives=[carry(ember, "The phoenix ember carried out of the mountain", 0, -7699.6, -1444.3, radius=20.0,
                          seconds=45, dips=[(-7550.0, -1260.0), (-7600.0, -1330.0), (-7640.0, -1390.0)], dip_radius=10.0,
                          achievement=9308496,
                          picked="The ember is barely warm. It is dimming already.",
                          warning="The ember is going dark. Find lava.", refreshed="The ember flares in the lava.",
                          lost="The ember went dark. It is still there, cold. Pick it up again.",
                          delivered="At the mountain's mouth, the ember rises.")],
        prev=c.id, sort=s, items=reins(70, 255, 260), xp=7,
        story=_story("Carry a dying phoenix ember out of Blackrock, dipping it in lava; at the mountain's mouth it "
                     "rises. Never letting it go dark counts for the mounts thread's achievement.", reins(70, 255, 260)))
    book.quest(
        9109255, "Learn the Heat", 58, 56, board, board, "hagatha",
        "Hagatha:$B$BThe magmammoths of the Searing Gorge will not carry anyone who flinches from heat, little horror. "
        "Let five magma elementals burn you, and do not flinch, and do not kill them first. Then the mammoths and the "
        "molten steed will come to see who smells of their home.",
        "Let 5 magma elementals in the Searing Gorge burn you (be struck by their fire).",
        "Five burns. No flinching.",
        "You smell like the inside of a volcano. The mammoths approve, and the molten steed came too.",
        objectives=[struck(5, "Burned by a magma elemental", entries=[5855])], prev=e.id, sort=s,
        items=reins(196, 213, 214, 215), xp=6,
        story=_story("Let five magma elementals burn you without flinching.", reins(196, 213, 214, 215)))


# --- 44. The Dragon Pilgrimage ------------------------------------------------------------------------------------------

def pilgrimage(book, board):
    book.region("44. The Dragon Pilgrimage (levels 60-80)",
                "Each dragonflight tests a pilgrim differently: heal a whelp, wait without moving, sleep until a dream "
                "comes, refuse a whisper, walk the blue memories, catch a falling egg. The flights decide your drake.")
    s = Z_INBETWEEN
    whelp = book.beast("wounded_whelp", "A Wounded Whelp", 26925, level=70, faction=FACTION_SHY, passive=True, scale=0.3,
                       subname="Fell Off the Temple", spawns=[(571, 3560.0, 392.0, 0.0, 3.0)])
    moss = book.thing("ruby_moss", "Ruby Moss", FLOWERS, [(571, 3743.8, 955.3, 0.0, 0.0)], size=0.6)
    tests = []
    tests.append(book.quest(
        9109260, "WANTED: The Red Test", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BDragons like gifts, little horror. And grovelling. But each flight has its own test for a pilgrim, "
        "and the red one is kindness. A whelp fell off Wyrmrest Temple and is lying at its foot. Fetch ruby moss from "
        "the Ruby Dragonshrine and pet the whelp with it. Gently. Reds notice gently.",
        "Pick ruby moss at the Ruby Dragonshrine, then /pet the wounded whelp at the foot of Wyrmrest Temple.",
        "The whelp is waiting. It is trying not to cry.",
        "The whelp is up and flying again, badly. The reds saw. One test.",
        objectives=[touch(moss, 1, "Ruby moss picked"), emote(1, "The wounded whelp tended", EMOTE_PET, entries=[whelp.entry])],
        sort=s, xp=5, story="The red test: tend a whelp that fell off Wyrmrest, with ruby moss."))
    tests.append(book.quest(
        9109261, "The Bronze Test", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BThe bronze test is time, little horror. Go to the Caverns of Time in Tanaris and wait. Exactly one "
        "minute. Do not move. The bronzes count every heartbeat you waste.",
        "Stand still for one minute in the Caverns of Time.",
        "Sixty heartbeats. Still.",
        "A minute, exactly. A bronze dragon nodded at you, and she does not nod. Two tests.",
        objectives=[visit("Waited one minute, unmoving", 1, -8294.5, -4586.8, radius=25.0, stay=60, still=True)],
        prev=tests[-1].id, sort=s, xp=5, story="The bronze test: wait one minute in the Caverns of Time without moving."))
    dreamer = book.beast("dreaming_whelp", "A Dreaming Whelp", 26925, level=70, faction=FACTION_SHY, passive=True,
                         scale=0.3, subname="Asleep for a Hundred Years", spawns=[(0, -10425.0, -395.0, 0.0, 1.0)])
    tests.append(book.quest(
        9109262, "The Green Test", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BThe green test is sleep. By the dream portal in Duskwood's Twilight Grove, a whelp of the green "
        "flight sleeps and has slept a hundred years. Lie down beside it and sleep too, until a dream comes.",
        "/sleep beside the dreaming whelp at the dream portal in Duskwood's Twilight Grove.",
        "Sleep, little horror. Dream something.",
        "You dreamed of a field that grew dragons instead of wheat. The whelp dreamed it too. The greens are "
        "pleased. Three tests.",
        objectives=[emote(1, "Slept beside the dreaming whelp", EMOTE_SLEEP, entries=[dreamer.entry]),
                    visit("Stayed by the dream portal", 0, -10425.0, -395.0, radius=15.0, stay=30, still=True)],
        prev=tests[-1].id, sort=s, xp=5, story="The green test: sleep beside a dreaming whelp until a dream comes."))
    whisper = book.beast("grim_whisper", "A Whisper From Grim Batol", 11686, level=70, faction=35, passive=True,
                         scale=0.6, subname="Promises Things",
                         spawns=[(0, -3597.0, -2714.8, 0.0, 0.0), (0, -3620.0, -2690.0, 0.0, 1.0), (0, -3575.0, -2740.0, 0.0, 2.0)],
                         gossip=("The shadow leans close. 'Power, Devourer. Every shape you will ever want. Only say yes.'",
                                 [("No.", "The shadow flinches, as if no one had ever said it before. It thins and goes out.", True),
                                  ("What would it cost?", "'Nothing. Everything. Does it matter? Say yes.'", False),
                                  ("Yes.", "Something cold settles in your stomach. You feel like you just ate a lie. The shadow laughs.", False)], 0))
    tests.append(book.quest(
        9109263, "The Black Test", 70, 68, board, board, "hagatha",
        "Hagatha, without a smile:$B$BThe black test is the one they never mean you to pass. At the gate of Grim Batol "
        "in the Wetlands, three shadows will whisper to you. They will offer everything. Say no. Three times, to three "
        "of them.",
        "Refuse the 3 whispers at the gate of Grim Batol in the Wetlands.",
        "Three times, little horror. No.",
        "Three nos. The blacks will hate you for it, and respect you, which with blacks is the same thing. Four tests.",
        objectives=[gossip(whisper, "A whisper refused")], prev=tests[-1].id, sort=s, xp=6,
        story="The black test: refuse three whispers at the gate of Grim Batol."))
    tests[-1].objectives[0].count = 3
    memories = book.thing("blue_memories", "A Blue Memory", RUNE_BLUE,
                          [(530, 12559.3, -6790.0, 0.0, 0.0), (530, 12848.6, -7040.7, 0.0, 0.0), (530, 13276.3, -7148.3, 0.0, 0.0),
                           (530, 12700.0, -6900.0, 0.0, 0.0)], size=0.8)
    tests.append(book.quest(
        9109264, "The Blue Memories", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BThe blue flight does not test, little horror. It remembers. On the Isle of Quel'Danas four "
        "memories hang in the air: Madrigosa, who fell; Kalecgos, who loved; Anveena, who was the well; and the flight "
        "itself, all of them, a long time ago. Walk through each one. Each leaves an essence behind.",
        "Walk through the 4 blue memories on the Isle of Quel'Danas.",
        "Four memories. Walk slowly through them; they are old.",
        "Four essences, and you smell faintly of the Sunwell. The blues have given you what they remember. Five "
        "tests.",
        objectives=[touch(memories, 4, "A blue memory walked through")], prev=tests[-1].id, sort=s,
        items=reins(315, 316, 317, 318), xp=7,
        story=_story("Walk through four blue memories on Quel'Danas.", reins(315, 316, 317, 318))))
    egg = book.thing("netherwing_egg", "A Netherwing Egg, Rolling", EGG_BLACK, [(530, -5240.3, 682.0, 0.0, 0.0)], size=0.8)
    tests.append(book.quest(
        9109265, "Catch It Before the Ground", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BOn the Netherwing Ledge in Shadowmoon a netherwing has laid an egg on the very top, and the egg is "
        "rolling, little horror. Climb up without flying (they will not let a flier near). Pick it up. It will hatch in "
        "your hands. Then come down the way you went up.",
        "Climb to the top of the Netherwing Ledge without flying, take the rolling egg, and come back down to the "
        "mines.",
        "Up, egg, down. No wings.",
        "It hatched on the way down and bit you on the nose, and grew a little every time you passed another flight's "
        "test. It is not little any more. It is yours, and so is its cousin.",
        objectives=[touch(egg, 1, "The rolling egg caught, on foot", noflying=True),
                    visit("Back down at the mines with the hatchling", 530, -5165.2, 757.3, radius=40.0, noflying=True)],
        prev=tests[-1].id, sort=s, items=reins(240, 264), xp=7,
        story=_story("Climb the Netherwing Ledge on foot and catch a rolling egg; it hatches as you come down.", reins(240, 264))))
    book.quest(
        9109266, "The Flights Decide", 75, 70, board, board, "hagatha",
        "Hagatha:$B$BYou have done every test, little horror. Go to the top of Wyrmrest Temple and stand there while "
        "the flights talk about you. The one you impressed most will send you a drake. You choose which one you "
        "impressed most; they will argue, but you choose.",
        "Stand at the top of Wyrmrest Temple while the dragonflights decide.",
        "At the top. Wait. Let them argue.",
        "They argued for a long time, and then they let you pick. Of course they did. Dragons like being picked.",
        objectives=[visit("Stood at the top of Wyrmrest while they decided", 571, 3546.0, 287.0, radius=30.0, stay=20,
                          above=200.0)],
        prev=tests[-1].id, sort=s, choices=[(e, n) for e, n, _ in reins(85, 185, 111, 243, 241, 385)], xp=8,
        story="Stand atop Wyrmrest while the flights decide; choose the drake of the flight you impressed most "
              "(Azure Drake, Timereaver, Worldbreaker, Ember Wyrm, Great-Wyrm or Armored Obsidian Drake).")
    book.quest(
        9109267, "Race the Sky Stalkers", 78, 74, board, board, "hagatha",
        "Hagatha:$B$BFour sky stalkers circle Wyrmrest and they are bored, little horror. They will race anyone round "
        "the four dragonshrines of the Dragonblight: ruby, emerald, azure, obsidian. Touch each shrine. If you keep up, "
        "they keep you.",
        "Visit the Ruby, Emerald, Azure and Obsidian Dragonshrines in the Dragonblight.",
        "Four shrines. They are already ahead of you.",
        "You kept up. Mostly. They have decided you are interesting, which is the highest thing a sky stalker can say.",
        objectives=[visit("The Ruby Dragonshrine", 571, 3743.8, 955.3, radius=40.0),
                    visit("The Emerald Dragonshrine", 571, 2791.3, -6.0, radius=40.0),
                    visit("The Azure Dragonshrine", 571, 3373.6, 2584.3, radius=40.0),
                    visit("The Obsidian Dragonshrine", 571, 4473.3, 1655.5, radius=40.0)],
        prev=9109266, sort=s, items=reins(53, 54, 55, 56), xp=7,
        story=_story("Race four bored sky stalkers round the Dragonblight's shrines.", reins(53, 54, 55, 56)))


# --- 45. Blessing of the Loa ---------------------------------------------------------------------------------------------

def loa(book, board):
    book.region("45. Blessing of the Loa (levels 30-80)",
                "Four loa, four strange asks: Shadra wants you bitten, Hir'eek wants you up all night, Gonk wants a "
                "race, Akali wants a roar. Then the altars of Zul'Drak.")
    s = Z_INBETWEEN
    book.quest(
        9109270, "WANTED: Shadra's Ten Bites", 34, 30, board, board, "hagatha",
        "Hagatha, with a spider on her shoulder:$B$BShadra, the spider loa, wants a Devourer who has been bitten by ten "
        "different spiders and kept walking, little horror. Ten. Different ones. Let them bite. Then eat them, if you "
        "like; Shadra does not mind what happens after.",
        "Be bitten by 10 different spiders (let them strike you).",
        "Ten bites. Count them. I am.",
        "Ten bites, and you only swelled up a little. Shadra's spiders have decided you are one of them. Two came with "
        "the blessing.",
        objectives=[struck(10, "Bitten by a spider", family=3)], sort=s, items=reins(144, 324), xp=5,
        story=_story("Let ten different spiders bite you for Shadra.", reins(144, 324)))
    book.quest(
        9109271, "Hir'eek's Long Night", 40, 36, board, board, "hagatha",
        "Hagatha:$B$BHir'eek, the bat loa, sleeps all day and wants company all night, little horror. Go to the belfry "
        "bats in Tirisfal and keep still with them through the dark. A minute of a bat's night is an hour of yours. "
        "Do not fidget.",
        "At night, stay still among the belfry bats in Tirisfal for a minute.",
        "Still. Bats do not fidget.",
        "Hir'eek liked you. Bats like anyone who does not fidget. The thunderspine came on Hir'eek's word; it is "
        "black and long and does not like daylight either.",
        objectives=[visit("Kept still through the bats' night", 0, 2296.0, 296.0, radius=20.0, night=True, stay=60, still=True)],
        sort=s, items=reins(337), xp=5,
        story=_story("Keep still with Hir'eek's bats through a night in Tirisfal.", reins(337)))
    feather = book.thing("gonk_feather", "Gonk's Feather", FEATHER, [(0, -11981.3, -289.6, 0.0, 0.0)], size=0.6)
    book.quest(
        9109272, "Gonk's Footrace", 38, 34, board, board, "hagatha",
        "Hagatha:$B$BGonk, the raptor loa, wants a race, little horror. In Stranglethorn, where the lashtails run, a "
        "feather lies on the start line. Pick it up and the raptors start running. Get the feather to the finish "
        "before they do. They are fast. You are a Devourer. Be faster.",
        "Pick up Gonk's feather in Stranglethorn and race it to the finish before the raptors.",
        "Faster, little horror.",
        "You won! Barely. The raptors are pretending they let you. Gonk sent two direhorns, which do not race, "
        "because direhorns do not need to.",
        objectives=[carry(feather, "Gonk's feather raced to the finish", 0, -12010.5, -238.9, radius=10.0, seconds=25,
                          fail_lost=True, picked="The lashtails scream and start running. Go!",
                          warning="They are catching up!", lost="The raptors got there first.",
                          delivered="First! Gonk laughs somewhere.")],
        sort=s, items=reins(345, 388), xp=5,
        story=_story("Race Gonk's feather against the lashtail raptors in Stranglethorn.", reins(345, 388)))
    book.quest(
        9109273, "Out-Roar a Rhino", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BAkali, the rhino loa, wants to hear you roar louder than a rhino, little horror. The wooly rhinos "
        "of the Borean Tundra roar when they charge. Roar back. Three of them, until they stop.",
        "/roar at 3 wooly rhinos in the Borean Tundra.",
        "Louder, little horror.",
        "Three rhinos stopped dead and looked embarrassed. Akali sent a mushan, which roars even louder than you. "
        "It will teach you.",
        objectives=[emote(3, "A wooly rhino out-roared", EMOTE_ROAR, entries=[25489, 25487, 25488], flee=True)],
        sort=s, items=reins(238), xp=6,
        story=_story("Out-roar three wooly rhinos for Akali.", reins(238)))
    book.quest(
        9109274, "The Altars of Zul'Drak", 76, 72, board, board, "hagatha",
        "Hagatha:$B$BAll four loa have spoken for you, little horror, and now the old altars of Zul'Drak want to see "
        "you: Har'koa's, Quetz'lun's, Sseratus's and Mam'toth's. Stand at each. The loa there are dying, and they "
        "will be glad of a visitor. Be kind.",
        "Visit the altars of Har'koa, Quetz'lun, Sseratus and Mam'toth in Zul'Drak.",
        "Four altars. Be kind to the old ones.",
        "Four altars, four tired loa, and every one of them blessed you. The brutosaur is the blessing of all four "
        "at once. It is enormous. It has a shop on its back.",
        objectives=[visit("Har'koa's altar", 571, 5746.5, -3608.8, radius=40.0),
                    visit("Quetz'lun's altar", 571, 5716.3, -4369.3, radius=40.0),
                    visit("Sseratus's altar", 571, 6391.7, -2615.0, radius=40.0),
                    visit("Mam'toth's altar", 571, 6320.9, -4130.4, radius=60.0)],
        prev=9109270, sort=s, items=reins(36), xp=8,
        story=_story("Visit the four dying loa at the altars of Zul'Drak.", reins(36)))


# --- 47. Hagatha's Trials of Craft ------------------------------------------------------------------------------------

def trials(book, board):
    book.region("47. Hagatha's Trials of Craft (level 70+)",
                "A Devourer eats everyone's lessons. Hagatha tests you in other classes' arts: a demon hunter's leap, a "
                "hunter's tracking without Sniff, a rogue's theft from Wren's apron, a warlock's bargain with an imp.")
    s = Z_INBETWEEN
    a = book.quest(
        9109280, "WANTED: The Demon Hunter's Leap", 70, 70, board, board, "hagatha",
        "Hagatha:$B$BShow me what you stole from them, little horror. Demon hunters leap from high places and glide. "
        "Go to the cliffs above the Black Temple in Shadowmoon, on foot, and leap. Land by the Sanctum of the Stars. "
        "No mount, no wings that are not your own.",
        "Climb the cliffs above the Black Temple on foot, then leap and land by the Sanctum of the Stars.",
        "Leap, little horror. Glide if you can. Fall if you must.",
        "You leapt. You did not exactly glide, but you landed, which is most of it. The spire terrors saw; they "
        "follow anyone who jumps off things on purpose.",
        objectives=[visit("Stood on the cliffs above the Black Temple", 530, -3307.9, 291.8, radius=30.0, noflying=True,
                          above=100.0),
                    visit("Landed by the Sanctum of the Stars", 530, -3559.7, 637.6, radius=40.0, noflying=True)],
        sort=s, items=reins(75, 76, 77, 78), xp=7,
        story=_story("The demon hunter's trial: leap from the Black Temple's cliffs.", reins(75, 76, 77, 78)))
    prints = book.thing("trial_prints", "Faint Footprints", BONES,
                        [(1, -4700.0, 650.0, 0.0, 0.0), (1, -4660.0, 700.0, 0.0, 0.0), (1, -4620.0, 760.0, 0.0, 0.0),
                         (1, -4590.0, 820.0, 0.0, 0.0), (1, -4570.0, 870.0, 0.0, 0.0)], size=0.5)
    book.quest(
        9109281, "The Hunter's Eyes", 70, 70, board, board, "hagatha",
        "Hagatha:$B$BHunters track with their eyes, little horror. You track with your nose, which is cheating. In "
        "Feralas a beast has left five footprints through the forest by the Woodpaw camp. Follow them with Sniff "
        "OFF. I will know if you sniff.",
        "With Sniff off, follow the 5 footprints in Feralas.",
        "Eyes, little horror. Not nose.",
        "Five footprints, and not one sniff. The wolfhawk at the end of them has decided you are a hunter.",
        objectives=[touch(prints, 5, "A footprint found by eye (no Sniff)", sniff=False)], prev=a.id, sort=s,
        items=reins(181), xp=6,
        story=_story("The hunter's trial: follow footprints in Feralas without Sniff.", reins(181)))
    apron = book.thing("wren_apron", "Wren's Apron Pocket", CHEST, [(IN_BETWEEN, -94.0, 155.0, Z_HALL, 0.0)], size=0.4)
    book.quest(
        9109282, "The Rogue's Fingers", 70, 70, board, board, "hagatha",
        "Hagatha, whispering:$B$BWren naps at night. In her apron pocket is a key. Take it. A rogue would hide in the "
        "shadows; you have a saber's shape that does the same. Wear it, wait for the dark, and be quick. If she wakes, "
        "I was never here.",
        "At night, as a Saber (or what it grew into), take the key from Wren's apron pocket.",
        "Night. Saber. Quiet.",
        "You took it and she never woke. The key opens nothing, by the way. It was the taking. The razor-lined reins "
        "are your prize; a rogue's horse, for a rogue's fingers.",
        objectives=[touch(apron, 1, "The key taken from Wren's apron", shapes=LINES["saber"], night=True)], prev=a.id,
        sort=s, needs=LINES["saber"], items=reins(289), xp=6,
        story=_story("The rogue's trial: take the key from Wren's apron at night, as a saber.", reins(289)))
    imp = book.beast("bargain_imp", "Snitch the Imp", 19136, level=70, faction=35, passive=True, scale=1.0,
                     subname="Has a Deal for You", spawns=[(IN_BETWEEN, -105.0, 146.0, Z_HALL, 0.5)],
                     gossip=("The imp rubs its hands. 'A deal, a deal! Your shadow for a horse. Fair? Fair!'",
                             [("Read the contract first.", "The small print says 'and your soul, and your hat'. The imp sighs and offers a better deal: a horse for a joke. You tell one. It laughs.", True),
                              ("Deal!", "Your hat catches fire. 'Ha! Read first, Devourer, always read first!'", False),
                              ("Eat the imp.", "It hops out of reach and sets your boots on fire.", False)], 0))
    book.quest(
        9109283, "The Warlock's Bargain", 70, 70, board, board, "hagatha",
        "Hagatha:$B$BWarlocks bargain with demons, little horror. I have trapped a small one in the corner of the "
        "hall for the purpose. It will offer you a deal. Wrong answers set you on fire. Right answers get you what you "
        "want. Think like a warlock: what does a warlock always do first?",
        "Strike the right bargain with Snitch the imp in the In-Between.",
        "What does a warlock always do first, little horror?",
        "You read the contract. Of course. The imp is furious and delighted. The wrathsteeds came as its payment, "
        "and it had to pay twice because you read the part about payment.",
        objectives=[gossip(imp, "The right bargain struck with the imp")], prev=a.id, sort=s, items=reins(364, 365), xp=6,
        story=_story("The warlock's trial: out-bargain an imp.", reins(364, 365)))


# --- 48. The Faire Comes to the In-Between ------------------------------------------------------------------------------

def faire(book, board):
    book.region("48. The Faire Comes to the In-Between (any level)",
                "The Faire comes to the In-Between for a night. No tickets: every prize comes from its own game. The "
                "first versions stand in the hall; the full Faire comes when its own pocket of the In-Between exists.")
    s = Z_INBETWEEN

    def spot(dx, dy):
        return (IN_BETWEEN, -93.0 + dx, 128.0 + dy, Z_HALL, 0.0)
    bucket = book.thing("faire_bucket", "Wren's Bucket", BUCKET, [spot(6.0, -2.0)], size=1.2)
    book.quest(
        9109290, "WANTED: Land in the Bucket", 10, 1, board, board, "wren",
        "Wren, in a striped hat:$B$BStep right up, Snack! The Faire's come to the In-Between! Game one: the cannon. "
        "There's no cannon. I couldn't find one. So: jump off the trophy wall and land in my bucket and stand in it "
        "and count to five. If you stay in, you win the dirigible!",
        "Land in Wren's bucket by the WANTED board and stand in it for five seconds.",
        "In the bucket, Snack! Count!",
        "Five! You win! The dirigible's yours. It's also a bit like a bucket.",
        objectives=[touch(bucket, 1, "Climbed into Wren's bucket"),
                    visit("Stayed in the bucket for five", IN_BETWEEN, -87.0, 126.0, radius=1.5, stay=5, still=True)],
        sort=s, items=reins(389), xp=3,
        story=_story("The Faire's cannon (there is no cannon): land in Wren's bucket.", reins(389)))
    charger = book.beast("harlequin_charger", "The Harlequin's Charger", 385, display=mount_look(68), level=20, faction=FACTION_SHY,
                         passive=True, scale=1.0, subname="Threw Its Harlequin")
    bell = book.thing("faire_joust", "The Joust Bell", LANTERN_HANGING, [spot(-6.0, -2.0)], size=0.8, summon=charger.entry,
                      count=1)
    book.quest(
        9109291, "The Joust", 12, 1, board, board, "wren",
        "Wren:$B$BGame two: the joust! Ring the bell and the harlequin comes charging out on his charger! Well. The "
        "charger comes charging out. The harlequin fell off at the Thin Place. Calm it down and you win it, Snack. "
        "Pet it. It likes being petted. It's had a hard night.",
        "Ring the joust bell and /pet the harlequin's runaway charger.",
        "Pet the horse, Snack!",
        "It's calm! It's yours! The harlequin can walk home.",
        objectives=[wake(bell, "The joust bell rung"), emote(1, "The harlequin's charger calmed", EMOTE_PET, entries=[charger.entry])],
        sort=s, items=reins(68), xp=3,
        story=_story("The joust: the harlequin fell off, so calm his charger instead.", reins(68)))
    strong = book.thing("faire_strongman", "The Strongman's Bell", ANVIL, [spot(-6.0, 4.0)], size=1.0)
    book.quest(
        9109292, "Ring the Bell", 20, 15, board, board, "wren",
        "Wren:$B$BGame three: the strongman! Hit the bell as hard as you can. Only it won't ring for anyone small. Be a "
        "bear. The bear always wins the bear.",
        "As a Bear (or what it grew into), ring the strongman's bell.",
        "Be a bear, Snack!",
        "DING! The bear wins the bear! Two bears, actually. I lost count of the bears.",
        objectives=[touch(strong, 1, "The strongman's bell rung as a bear", shapes=LINES["bear"])],
        sort=s, needs=LINES["bear"], items=reins(31, 64), xp=4,
        story=_story("The strongman: ring the bell as a bear.", reins(31, 64)))
    stalls = book.thing("faire_chameleon", "A Stall That Blinked", CRATE,
                        [spot(-8.0, 8.0), spot(8.0, 8.0), spot(-10.0, -6.0), spot(10.0, -6.0), spot(0.0, 10.0), spot(0.0, -8.0)],
                        size=0.8)
    book.quest(
        9109293, "Find the Chameleon", 10, 1, board, board, "wren",
        "Wren:$B$BGame four: find the chameleon! It hides on the stalls. Any colour. When you find it, it runs to "
        "another stall. Find it three times and it gives up and lets you ride it.",
        "Find the chameleon on 3 of the Faire's stalls.",
        "It's the stall that blinked, Snack!",
        "Three times! It's sulking in your colours now. That's how you know it likes you.",
        objectives=[touch(stalls, 3, "The chameleon found on a stall")], sort=s, items=reins(47), xp=3,
        story=_story("Find the hiding chameleon on the Faire's stalls three times.", reins(47)))
    pegs = book.thing("faire_rings", "A Ring-Toss Peg", KEG, [spot(3.0, 6.0), spot(-3.0, 6.0), spot(3.0, -6.0),
                                                                    spot(-3.0, -6.0), spot(0.0, 3.0)], size=0.5)
    book.quest(
        9109294, "The Ring Toss", 10, 1, board, board, "wren",
        "Wren:$B$BGame five: the ring toss! Five pegs. Get a ring on each. The prize is a nestling, a black one, it "
        "fell out of the Faire's nest and nobody's claimed it.",
        "Get a ring on all 5 ring-toss pegs.",
        "Five pegs, Snack!",
        "Five rings, five pegs, one nestling! It's already asleep in your hat.",
        objectives=[touch(pegs, 5, "A ring on a peg")], sort=s, items=reins(96), xp=3,
        story=_story("The ring toss: five rings, five pegs.", reins(96)))
    book.quest(
        9109295, "The Old Ride", 10, 1, board, board, "wren",
        "Wren, nervously:$B$BGame six: the old ride. It goes round the hall. It creaks. It's called the Aerial "
        "Attraction and the sign says DISCARDED but I think that's its name. Ride it round: the board, the pond, the "
        "cauldron, the Thin Place. If you get off at the end, it's yours.",
        "Go round the old ride: the WANTED board, the duck pond, the cauldron and the Thin Place.",
        "Round you go, Snack!",
        "You survived! The ride's yours. It really should be discarded. Please don't let it near the cauldron.",
        objectives=[visit("Round the WANTED board", IN_BETWEEN, -93.0, 121.5, radius=6.0),
                    visit("Round the duck pond", IN_BETWEEN, -90.5, 138.5, radius=6.0),
                    visit("Round the cauldron", IN_BETWEEN, -98.0, 157.0, radius=6.0),
                    visit("Round the Thin Place", IN_BETWEEN, -123.0, 149.0, radius=8.0)],
        sort=s, items=reins(112), xp=3,
        story=_story("Ride the discarded old ride round the hall.", reins(112)))
    gnome = book.beast("whack_gnome", "A Whack-a-Gnome Gnome", 1211, level=1, faction=14, scale=0.8, subname="Pops Up")
    holes = book.thing("faire_whack", "The Whack-a-Gnome Board", MACHINE_BROKEN, [spot(8.0, 2.0)], size=1.0,
                       summon=gnome.entry, count=8)
    book.quest(
        9109296, "Whack-a-Gnome", 10, 1, board, board, "wren",
        "Wren:$B$BGame seven: whack-a-gnome! Pull the lever and gnomes pop up. Whack them. They're volunteers! "
        "Mostly! There's a goblin in there too, somewhere. Eight whacks and you win their walking machines.",
        "Pull the whack-a-gnome lever and whack 8 gnomes.",
        "Whack, Snack!",
        "Eight! The gnomes are fine. They're laughing. Their machines are yours; they'll build new ones by Tuesday.",
        objectives=[wake(holes, "The whack-a-gnome lever pulled"), slay(8, "A gnome whacked", entries=[gnome.entry])],
        sort=s, items=reins(17, 18), xp=3,
        story=_story("Whack-a-gnome: eight whacks for the gnomes' and goblins' terratransformers.", reins(17, 18)))
    teller = book.beast("fortune_cat", "Madame Whiskers", 6368, level=10, faction=35, passive=True, scale=1.5,
                        subname="Tells Fortunes", spawns=[spot(-10.0, 2.0)],
                        gossip=("The cat looks into your eyes for a long time. 'Choose a card,' she says, which a cat should not "
                                "be able to say.",
                                [("The tiger.", "'A tiger waits for you where the jungle meets the sea. Not yet. Later.' She yawns.", True),
                                 ("The fish.", "She eats the card.", False),
                                 ("The empty card.", "'Nothing? Brave. Choose again.'", False)], 0))
    fortune = book.quest(
        9109297, "The Fortune Teller", 10, 1, board, board, "wren",
        "Wren:$B$BGame eight isn't a game. It's Madame Whiskers. She's a cat. She tells fortunes. They come true, "
        "Snack, every time, that's the scary part. Ask her yours.",
        "Have your fortune told by Madame Whiskers at the Faire.",
        "Ask the cat, Snack.",
        "A tiger? Where the jungle meets the sea? That's Stranglethorn! Not yet, she said. Wait for it.",
        objectives=[gossip(teller, "Fortune told")], sort=s, xp=2,
        mail=("Your fortune", "Devourer,$B$BThe tiger is waiting on the beach below Booty Bay, where the jungle meets "
                              "the sea. Go and bow to it.$B$B- Madame Whiskers (a cat)", 3600),
        story="Madame Whiskers the cat tells your fortune; it comes true later, by letter.")
    tiger = book.beast("fortune_tiger", "The Tiger of Fortune", 6368, display=mount_look(227), level=40, faction=FACTION_SHY,
                       passive=True, scale=1.0, subname="Was Told You Would Come", spawns=[(0, -14645.5, 258.3, 0.0, 1.0)])
    book.quest(
        9109298, "It Came True", 35, 30, board, board, "wren",
        "Wren, holding a letter:$B$BSnack. SNACK. Madame Whiskers wrote. The tiger's on the beach below Booty Bay. "
        "It's real. Go and bow to it. Properly. It's a fortune; you have to be polite.",
        "/bow to the Tiger of Fortune on the beach below Booty Bay.",
        "Bow, Snack. Fortunes like manners.",
        "It came true. It always comes true. The tiger's yours; it says it knew you'd come, which is very smug for a "
        "tiger.",
        objectives=[emote(1, "Bowed to the Tiger of Fortune", EMOTE_BOW, entries=[tiger.entry])], prev=fortune.id, sort=s,
        items=reins(227), xp=5,
        story=_story("The fortune comes true: bow to the tiger on the beach below Booty Bay.", reins(227)))
    lonely = (
        ("lonely_dwarf", "Lonely Bruk", 5111, "Wants Someone Who Likes Ale",
         "Bruk sighs into his tankard. 'Nobody at this Faire appreciates a good stout.'",
         [("Give him Wren's 'soup'.", "He sips. 'This is... ale. Good ale. Who brewed this?' He goes looking for Wren. It's a match!", True),
          ("Give him a flower.", "He sneezes into his beard.", False)], -10.0, -4.0),
        ("lonely_orc", "Lonely Grusha", 6929, "Wants Someone Who Can Cook",
         "Grusha looks at the stalls. 'Nobody here can cook. Nobody.'",
         [("Point her at Bruk.", "She marches over. Bruk offers her ale. She offers him a stew. They argue about salt. It's a match!", True),
          ("Offer her a cooked boot.", "She eats it. She looks sad. Wrong boot.", False)], 10.0, -4.0),
        ("lonely_forsaken", "Lonely Tobias", 1518, "Wants Someone Who Doesn't Mind",
         "Tobias rattles quietly. 'Everyone runs when they see me. My jaw falls off when I laugh.'",
         [("Introduce him to Madame Whiskers.", "The cat looks at his jaw, decides it is a toy, and adopts him. Hilariously wrong match. Both are delighted.", True),
          ("Tell him a joke.", "His jaw falls off. You hand it back. He is mortified.", False)], -4.0, 8.0),
        ("lonely_footman", "Lonely Rob", 25258, "Wants Someone Brave",
         "Rob straightens his helmet. 'I want someone brave. Braver than me. That's not hard.'",
         [("Introduce him to Wren.", "Wren takes his hand and drags him to the joust. He screams the whole way. It's a match!", True),
          ("Show him your teeth.", "He faints.", False)], 4.0, 8.0),
    )
    objs = []
    for key, name, clone, sub, text, options, dx, dy in lonely:
        b = book.beast(key, name, clone, level=20, faction=35, passive=True, scale=1.0, subname=sub, spawns=[spot(dx, dy)],
                       gossip=(text, options, 0))
        objs.append(gossip(b, f"{name.split()[1]} matched"))
    book.quest(
        9109299, "Wren's Matchmaking Booth", 15, 1, board, board, "wren",
        "Wren, at a booth with a heart on it:$B$BLove is easy, Snack. Like soup. Four lonely fairgoers came in from "
        "the Thin Place and they all need someone. Give each the right gift, or the right introduction. One of them "
        "will go hilariously wrong. That's fine. That's love.",
        "Make a match for each of the 4 lonely fairgoers at the Faire.",
        "Love is easy, Snack!",
        "Four matches! One of them is a man and a cat, but they're happy, so it counts. You played every game. You "
        "get the big ticket. The magic one. It flies, apparently.",
        objectives=objs, sort=s, items=reins(20), xp=4,
        story=_story("Wren's matchmaking booth: four lonely fairgoers, four matches, one hilariously wrong.", reins(20)))



# --- 49. Bramble's Salvage Yard -----------------------------------------------------------------------------------------

def salvage(book, board):
    book.region("49. Bramble's Salvage Yard (levels 60-80)",
                "Bramble rebuilds wrecks and 'improves' every one. Salvage the parts where the wreck died, then test-drive "
                "it round Booty Bay; each machine has one quirk.")
    s = Z_INBETWEEN
    yards = (
        (9109300, "The Shredder Tank", "the Venture Co. shredders in Stranglethorn", 0,
         [(-12014.1, -742.0), (-12096.5, -700.8), (-12137.4, -588.1)], GEAR, 62,
         "It sneezes sparks. Don't stand downwind.", reins(157)),
        (9109301, "The Gnome Suits", "the scrap outside Gnomeregan", 0,
         [(-5165.0, 636.0), (-5072.6, 441.6), (-5120.0, 560.0)], GEAR, 64,
         "It walks backwards when it's nervous. It's always nervous.", reins(204, 221, 225)),
        (9109302, "The Juggernaut", "the broken engines of Netherstorm's manaforges", 530,
         [(2829.8, 4365.0), (2665.8, 4390.0), (3143.8, 2544.7), (2918.7, 2581.1)], MACHINE_BROKEN, 68,
         "It honks at goblins. Booty Bay is full of goblins.", reins(188, 193)),
        (9109303, "Three Wonkas", "the cities: Ironforge's gears, Orgrimmar's spikes and a Dalaran spark", None,
         [(0, -4795.1, -1108.6), (1, 2055.5, -4802.1), (571, 5807.0, 683.0)], GEAR, 70,
         "It plays music. Only one song. Loudly.", reins(377, 378, 379)),
        (9109304, "Three More Wonkas", "the far places: Shadowmoon's felsteel, Netherstorm's void and Booty Bay's paint", None,
         [(530, -4428.8, 1879.5), (530, 3835.9, 2045.9), (0, -14354.0, 414.0)], GEAR, 72,
         "It changes colour when it's happy. It's very happy.", reins(380, 381, 382)),
        (9109305, "Meat Wagons", "the dead meat wagons of Icecrown", 571,
         [(6505.8, 1195.0), (6902.4, 1266.2), (7075.9, 1134.2), (6839.0, 594.4)], BONES, 76,
         "It only turns left. Left round the dock, left past the scrapyard, left up to the bank.",
         reins(103, 104)),
    )
    prev = None
    for qid, title, where, map_id, spots, look, level, quirk, rewards in yards:
        if map_id is None:
            spawns = [(m, x, y, 0.0, 0.0) for m, x, y in spots]
        else:
            spawns = [(map_id, x, y, 0.0, 0.0) for x, y in spots]
        parts = book.thing(f"salvage_{qid}", "Salvageable Parts", look, spawns, size=0.8)
        q = book.quest(
            qid, ("WANTED: " if not prev else "") + title, level, level - 4, board, board, "wren",
            f"Bramble, upside down under something:$B$BOne goblin's wreck is another gnome's ride! I need the parts "
            f"from {where}. All {len(spawns)} of them. Then I build it, and then you test-drive it round Booty Bay, "
            f"because I'm not getting in it. {quirk} It's supposed to do that. Probably. Mostly. Duck.",
            f"Salvage the {len(spawns)} parts from {where.split(':')[0]}, then test-drive the machine round Booty Bay.",
            "Parts, then the lap. Duck.",
            "It works! It did the thing! The thing it's supposed to do, and also the other thing! It's yours.",
            objectives=[touch(parts, len(spawns), "Parts salvaged")]
                       + [visit(f"Test lap: {text.lower()}", 0, x, y, radius=12.0) for x, y, text in BOOTY_LAP],
            prev=prev, sort=s, items=rewards, xp=6,
            story=_story(f"Salvage parts from {where.split(':')[0]} and test-drive the rebuilt machine round Booty Bay. "
                         f"Quirk: {quirk.split('.')[0].lower()}.", rewards))
        prev = q.id


# --- 50. Silithid Secrets -----------------------------------------------------------------------------------------------

def silithid(book, board):
    book.region("50. Silithid Secrets (levels 55-60)",
                "The hives whisper. Only something that smells like a silithid gets close: eat one, then walk (never "
                "run) to the listening stones.")
    s = Z_INBETWEEN
    ashi = [11698, 11721, 11722, 11723, 11724]
    zora = [11725, 11726, 11727]
    a = book.quest(
        9109310, "WANTED: Listening to the Hive", 56, 54, board, board, "hagatha",
        "Hagatha:$B$BA scholar at Cenarion Hold says the hives of Silithus are singing, little horror, and she wants "
        "someone to listen. Only something that smells like a silithid gets close. Eat one; you will smell like it "
        "for a while. Then walk, never run, to the listening stones in Hive'Ashi. Running wakes them.",
        "Devour a Hive'Ashi silithid, then walk (never run) to the 3 listening stones in Hive'Ashi.",
        "Walk, little horror. The hive hears feet.",
        "Three stones, and they sang to you. The scholar has been writing for an hour. A drone followed you out of the "
        "hive; it thinks you're its queen. Keep it.",
        objectives=[devour(1, "A silithid devoured for its scent", entries=ashi),
                    visit("The first listening stone, walking", 1, -6663.7, 1069.6, radius=15.0, walking=True),
                    visit("The second listening stone, walking", 1, -6476.1, 1085.8, radius=15.0, walking=True),
                    visit("The third listening stone, walking", 1, -6580.2, 794.6, radius=15.0, walking=True)],
        sort=s, items=reins(10), xp=6,
        story=_story("Eat a silithid for its scent and walk to three listening stones in Hive'Ashi.", reins(10)))
    b = book.quest(
        9109311, "Hive'Zora Sings Louder", 58, 56, board, board, "hagatha",
        "Hagatha:$B$BHive'Zora sings louder, little horror. Same again: eat one of theirs, walk to the stones. The "
        "guardians there are old and listen too.",
        "Devour a Hive'Zora silithid, then walk to the 3 listening stones in Hive'Zora.",
        "Walk. Listen.",
        "The guardians listened with you, and then they followed you out. A krolusk came too; it says the song is about "
        "it, which it isn't.",
        objectives=[devour(1, "A Hive'Zora silithid devoured", entries=zora),
                    visit("A listening stone in Hive'Zora, walking", 1, -7087.8, 1764.9, radius=15.0, walking=True),
                    visit("A deeper stone in Hive'Zora, walking", 1, -7061.7, 1659.7, radius=15.0, walking=True),
                    visit("The deepest stone in Hive'Zora, walking", 1, -7448.4, 1404.4, radius=20.0, walking=True)],
        prev=a.id, sort=s, items=reins(297, 346), xp=6,
        story=_story("Listen at three stones in Hive'Zora.", reins(297, 346)))
    book.quest(
        9109312, "Why Is It Singing?", 60, 58, board, board, "hagatha",
        "Hagatha:$B$BThe scholar has worked it out, little horror. The hives are singing to the worms. Go back to the "
        "deepest stone in Hive'Zora, smelling of silithid, and stand still until the worms answer.",
        "Smelling of silithid, stand still by the deepest stone in Hive'Zora until the worms answer.",
        "Still, little horror. Worms are slow to answer.",
        "The ground shook. The worms answered. One of them came up and stayed. The scholar fainted. It's singing.",
        objectives=[devour(1, "A silithid devoured for its scent", entries=zora),
                    visit("Stood still until the worms answered", 1, -7448.4, 1404.4, radius=20.0, stay=45, still=True)],
        prev=b.id, sort=s, items=reins(383), xp=6,
        story=_story("Stand still at the deepest stone until the worms answer the hive's song.", reins(383)))


# --- 53. The Moon Remembers ---------------------------------------------------------------------------------------------

def moonwells(book, board):
    book.region("53. The Moon Remembers (levels 40-70)",
                "At night the moonwells show a saber's reflection. It bows, dances and kneels; copy it. After the fifth "
                "well the saber steps out of the water.")
    s = Z_INBETWEEN
    wells = (
        (9109320, "Shadowglen", "Teldrassil", 1, 10709.6, 762.3, reins(239)),
        (9109321, "Auberdine", "Darkshore", 1, 6410.9, 467.4, reins(293)),
        (9109322, "Raynewood Retreat", "Ashenvale", 1, 2368.1, -1720.3, reins(300)),
        (9109323, "Thalanaar", "Feralas", 1, -4512.5, -782.2, reins(71)),
        (9109324, "Nighthaven", "Moonglade", 1, 7793.5, -2446.9, reins(387)),
    )
    reflection = book.beast("saber_reflection", "The Saber's Reflection", 6368, display=mount_look(239), level=50,
                            faction=FACTION_SHY, passive=True, scale=1.0, subname="Moves When You Move",
                            spawns=[(m, x + 4.0, y + 4.0, 0.0, 0.0) for _, _, _, m, x, y, _ in wells])
    prev = None
    for i, (qid, name, zone, m, x, y, rewards) in enumerate(wells):
        q = book.quest(
            qid, ("WANTED: " if not prev else "") + f"The Reflection at {name}",
            44 + i * 5, 40 + i * 5, board, board, "hagatha",
            ("Hagatha, unimpressed:$B$BElves and their glowing water, little horror. At night the moonwells show a "
             "saber's reflection, and the reflection moves, and if you copy it, it remembers you. Bow, dance, kneel: "
             f"it does them in that order. The first well is {name} in {zone}." if i == 0 else
             f"Hagatha:$B$BThe next well is {name} in {zone}. Same reflection, same order: bow, dance, kneel. It is "
             "getting brighter each time; the moon is paying attention."),
            f"At night, at the moonwell of {name} in {zone}, /bow, /dance and /kneel to the saber's reflection.",
            "Bow, dance, kneel. At night.",
            ("The reflection copied you back, and then something stepped half out of the water and left a saber "
             "behind. It is yours. Four more wells." if i == 0 else
             "The saber stepped all the way out of the water this time. It shook itself dry and went to stand by you. "
             "It was always yours; it just had to remember." if i == 4 else
             "Another saber stepped out of the water and decided you are worth following."),
            objectives=[visit(f"At {name}'s moonwell at night", m, x, y, radius=12.0, night=True, stay=5),
                        emote(1, "Bowed to the reflection", EMOTE_BOW, entries=[reflection.entry]),
                        emote(1, "Danced with the reflection", EMOTE_DANCE, entries=[reflection.entry]),
                        emote(1, "Knelt to the reflection", EMOTE_KNEEL, entries=[reflection.entry])],
            prev=prev, sort=s, items=rewards, xp=5,
            story=_story(f"At night at {name}'s moonwell, copy the saber's reflection: bow, dance, kneel.", rewards))
        prev = q.id
    book.quest(
        9109325, "Frostsabers Come Down", 64, 60, board, board, "hagatha",
        "Hagatha:$B$BThe frostsabers of Winterspring heard about the moonwells, little horror, and they are jealous. "
        "They have no moonwell; they have Frostsaber Rock. Go up there at night and stand still a while, and they will "
        "come down to see the Devourer the moon remembers.",
        "At night, stand still for a while at Frostsaber Rock in Winterspring.",
        "At night. Still. They are proud animals.",
        "They came down, one after another, and the striped one stayed. It is yours, and it purrs like a snowstorm.",
        objectives=[visit("Stood still at Frostsaber Rock at night", 1, 6915.4, -4129.6, radius=25.0, night=True, stay=30,
                          still=True)],
        prev=prev, sort=s, items=reins(134), xp=6,
        story=_story("At night, stand still at Frostsaber Rock and the frostsabers come down.", reins(134)))


# --- 54. Wren's Duck Pond -------------------------------------------------------------------------------------------------

def ducks(book, board):
    book.region("54. Wren's Duck Pond (any level)",
                "Ducklings follow the first thing they see. Whistle the eggs open and be that thing, not Wren. Then "
                "walk them home to the duck pond without running.")
    s = Z_INBETWEEN
    duckling = book.beast("duckling", "A Duckling", 721, display=mount_look(94), level=1, faction=FACTION_SHY, passive=True,
                          scale=0.25, subname="Imprinting")
    nest = book.thing("duck_nest", "A Nest by the Thin Place", EGG, [(IN_BETWEEN, -120.0, 147.0, Z_HALL, 0.0)], size=0.8,
                      summon=duckling.entry, count=5, follow=True)
    book.quest(
        9109330, "WANTED: Mummy Duck", 5, 1, board, board, "wren",
        "Wren, with a duck on her head:$B$BSnack! Eggs! By the Thin Place! Ducklings follow the first thing they see, "
        "and it has to be you, not me, because I'm busy and also I'm not a duck. Wake the nest, whistle at each "
        "duckling as it hatches so it sees you, and walk them home to the pond. WALK. Run and the line breaks.",
        "Wake the nest by the Thin Place, /whistle at the 5 ducklings, and walk them to the duck pond.",
        "Quack. That means mummy.",
        "Five ducklings in the pond! Four of them think you're their mother. One of them saw me first. It hates you. "
        "It's yours anyway; it insists on hating you from close up.",
        objectives=[wake(nest, "The ducklings hatched"),
                    emote(5, "A duckling whistled at", EMOTE_WHISTLE, entries=[duckling.entry]),
                    visit("Walked the ducklings past the cauldron", IN_BETWEEN, -98.0, 157.0, radius=6.0, walking=True),
                    visit("Walked them home to the duck pond", IN_BETWEEN, -90.5, 138.5, radius=5.0, walking=True)],
        sort=s, items=reins(94), xp=3,
        story=_story("Whistle five ducklings out of their eggs and walk them home without running.", reins(94)))
    ghost = book.beast("ghost_duckling", "A Golden Duckling", 721, display=mount_look(95), level=1, faction=FACTION_SHY,
                       passive=True, scale=0.25, subname="Only Hatches at Night")
    ghost_nest = book.thing("duck_nest_night", "A Nest That Glows", EGG, [(IN_BETWEEN, -121.0, 152.0, Z_HALL, 0.0)], size=0.8,
                            summon=ghost.entry, count=3, follow=True)
    book.quest(
        9109331, "The Golden Clutch", 10, 1, board, board, "wren",
        "Wren, whispering:$B$BSnack, there's another nest. It glows. It only hatches at night. Same as before: "
        "whistle, walk, don't run. These ones are made of light, so if you lose one you'll see where it went.",
        "At night, wake the glowing nest, /whistle at the 3 golden ducklings, and walk them to the pond.",
        "At night, Snack. They're shy in the day.",
        "Golden ducklings in the pond, glowing like little lanterns. The biggest one is yours. It glows when it "
        "quacks.",
        objectives=[wake(ghost_nest, "The golden clutch hatched", night=True),
                    emote(3, "A golden duckling whistled at", EMOTE_WHISTLE, entries=[ghost.entry]),
                    visit("Walked them home to the pond", IN_BETWEEN, -90.5, 138.5, radius=5.0, walking=True)],
        prev=9109330, sort=s, items=reins(95), xp=3,
        story=_story("At night, whistle three golden ducklings out and walk them home.", reins(95)))


# --- 55. Lunar Festival: Lanterns for the Lost ----------------------------------------------------------------------------

def lunar(book, board):
    book.region("55. Lunar Festival: Lanterns for the Lost (any level, Lunar Festival only)",
                "Lost ancestors drift as paper lanterns, and the wind wants to blow them out. Carry each one to its "
                "elder; shelter it at the stones on the way.")
    s = Z_INBETWEEN
    spirits = (
        (9109340, "Elwynn Forest", "Elder Stormbrow in Goldshire", 0, (-9280.0, 460.0), (-9413.3, 154.3),
         [(-9330.0, 360.0), (-9380.0, 260.0)], reins(207)),
        (9109341, "Darkshore", "Elder Starweave by Auberdine", 1, (6450.0, 520.0), (6292.1, 530.7),
         [(6360.0, 500.0)], reins(208)),
        (9109342, "Moonglade", "the elders' gathering in Nighthaven", 1, (7419.9, -2235.9), (7561.2, -2206.3),
         [(7470.0, -2225.0), (7520.0, -2212.0)], reins(209)),
    )
    prev = None
    for i, (qid, zone, elder, m, src, dst, dips, rewards) in enumerate(spirits):
        spirit = book.thing(f"lunar_spirit_{qid}", "A Drifting Lantern Spirit", LANTERN_HANGING, [(m, src[0], src[1], 0.0, 0.0)],
                            size=0.7)
        last = i == len(spirits) - 1
        q = book.quest(
            qid, ("WANTED: " if not prev else "") + f"Lantern for the Lost: {zone}", 20 if not last else 30, 1, board,
            board, "wren",
            ("Wren, holding a paper lantern very carefully:$B$BSnack. At the Lunar Festival the lost ancestors come "
             "back as lanterns, and they drift, and they can't find their elders, and the wind keeps trying to blow "
             f"them out. There's one in {zone}. Carry it to {elder}. The wind is mean. When the flame gutters, duck "
             "behind the stones on the way and it'll catch again." if i == 0 else
             f"Wren:$B$BAnother lantern, in {zone}. Its elder is {elder}." + (
                 " This is the last one, Snack, from the Timbermaw road down into Nighthaven, and there's a storm "
                 "coming. Shelter it at every stone." if last else "")),
            f"During the Lunar Festival, carry the drifting lantern spirit in {zone} to {elder}.",
            "Keep it lit, Snack. Shelter it.",
            ("'You brought them home,' the elder said, and the lantern went up like a star. Something came down in its "
             "place." if not last else
             "'You brought them home.' All of them. The sky over Moonglade is full of lanterns, and one of them came "
             "back down as a rocket, a lucky one. It's yours."),
            objectives=[carry(spirit, f"The lantern spirit brought to {elder.split(' in ')[0].split(' by ')[0]}", m, dst[0],
                              dst[1], radius=15.0, seconds=40 if not last else 30, dips=dips, dip_radius=10.0,
                              picked="The lantern spirit settles in your hands. The wind is already pulling at it.",
                              warning="The flame is guttering. Find shelter.", refreshed="Sheltered, the flame catches again.",
                              lost="The wind blew it out. It drifts back to where you found it.",
                              delivered="The elder takes the lantern, and it rises.")],
            prev=prev, sort=s, event=EVENT_LUNAR, items=rewards, xp=4,
            story=_story(f"At the Lunar Festival, carry a lost ancestor's lantern spirit in {zone} to {elder}, sheltering "
                         "it from the wind.", rewards))
        prev = q.id


# --- 57. Banners of the Old Horde -----------------------------------------------------------------------------------------

def banners(book, board):
    book.region("57. Banners of the Old Horde (levels 60-70)",
                "The Old Horde's war beasts still wait at their clans' old camps, and only come for whoever carries the "
                "clan's banner. Plant it, and the ogres come for it; the beast stays if you hold the camp.")
    s = Z_INBETWEEN
    ogre = book.beast("banner_ogre", "Banner-Hungry Ogre", 17134, level=65, faction=14, scale=1.0, subname="Wants That Banner")
    clans = (
        (9109350, "Shattered Hand", "Hellfire Peninsula", 530, (-212.7, 2889.6), (-66.2, 3132.8),
         "the ruins below Hellfire Citadel", "the Shattered Hand's old camp above the ramparts", reins(141, 212, 217)),
        (9109351, "Warsong", "Nagrand", 530, (-1289.8, 8510.7), (-1637.0, 8569.5),
         "the ruins by Kil'sorrow", "the Warsong's old ground by the Ancestral Grounds", reins(186, 187, 142)),
        (9109352, "Frostwolf", "Nagrand", 530, (-1420.0, 7275.9), (-1297.0, 6949.1),
         "the old Frostwolf stones by Garadar", "the Frostwolf camp below Garadar", reins(74, 375, 374)),
        (9109353, "Thunderlord", "Blade's Edge Mountains", 530, (2154.4, 4902.7), (2274.4, 6133.0),
         "the ruins by Sylvanaar's road", "the Thunderlord's old stronghold", reins(30, 202)),
    )
    prev = None
    for qid, clan, zone, m, found, camp, found_where, camp_where, rewards in clans:
        banner = book.thing(f"banner_{qid}", f"The {clan} Banner", BANNER, [(m, found[0], found[1], 0.0, 0.0)], size=1.0)
        pole = book.thing(f"banner_pole_{qid}", f"The {clan} Camp's Empty Pole", BANNER, [(m, camp[0] + 3.0, camp[1] + 3.0, 0.0, 0.0)],
                          size=0.8, summon=ogre.entry, count=4)
        q = book.quest(
            qid, ("WANTED: " if not prev else "") + f"The {clan} Banner", 64 if clan != "Thunderlord" else 67, 62, board,
            board, "hagatha",
            (f"Hagatha, with an old orc's letter:$B$B'They remember the drums.' The Old Horde's war beasts still wait at "
             f"their clans' old camps, little horror, and they only come for someone who carries the clan's banner. The "
             f"{clan} banner lies in {found_where} in {zone}. Carry it to {camp_where} and plant it on the empty pole. "
             "The ogres will come for it. Hold the camp." if not prev else
             f"Hagatha:$B$BThe {clan} banner lies in {found_where} in {zone}. Carry it to {camp_where}, plant it, hold "
             "the camp. The beasts remember the drums."),
            f"Carry the {clan} banner from {found_where} to {camp_where}, plant it, and beat the 4 ogres who come.",
            "Hold the camp, little horror.",
            f"The banner flies over the {clan} camp again, and the beasts came out of the hills to stand under it. They "
            "sized you up while you fought. They have decided.",
            objectives=[carry(banner, f"The {clan} banner carried to its camp", m, camp[0], camp[1], radius=20.0,
                              slow=20, picked=f"The {clan} banner is heavy, and the wind snaps it like a drum.",
                              delivered="The banner is home."),
                        wake(pole, "The banner planted; the ogres came"),
                        slay(4, "A banner-hungry ogre beaten", entries=[ogre.entry])],
            prev=prev, sort=s, items=rewards, xp=7,
            story=_story(f"Carry the {clan} banner to its old camp and hold it against ogres; the war beasts come.", rewards))
        prev = q.id
    alpha = book.beast("fenrir_blood", "Fenrir's Blood", 385, display=mount_look(372), level=70, faction=FACTION_SHY,
                       passive=True, scale=1.1, subname="The Alpha")
    horn = book.thing("banner_alpha", "Four Banners, One Pole", BANNER, [(530, -1300.0, 6955.0, 0.0, 0.0)], size=1.0,
                      summon=alpha.entry, count=1)
    book.quest(
        9109354, "The Alpha", 70, 66, board, board, "hagatha",
        "Hagatha:$B$BFour banners flying, little horror. Now go back to the Frostwolf camp below Garadar, where the "
        "wolves are thickest, and sound all four at once on the old pole. The alpha will come. Fenrir's own blood. "
        "Roar at it. It will only follow something that roars back.",
        "Sound the four banners at the Frostwolf camp below Garadar, and /roar at the alpha when it comes.",
        "Roar, little horror. Like you mean it.",
        "It roared back, and the whole camp shook, and then it lay down at your feet. Fenrir's blood follows you now. "
        "The horn is yours to call it.",
        objectives=[wake(horn, "The four banners sounded"),
                    emote(1, "Roared at Fenrir's blood", EMOTE_ROAR, entries=[alpha.entry])],
        prev=prev, sort=s, items=reins(372), xp=8,
        story=_story("Sound all four banners at the Frostwolf camp and out-roar the alpha.", reins(372)))


# --- 58. Bramble's Maiden Flights ------------------------------------------------------------------------------------------

def flights(book, board):
    book.region("58. Bramble's Maiden Flights (levels 60-80)",
                "Bramble builds airships. Every maiden flight ends in a crash somewhere new, and a letter arrives with only "
                "what Bramble could see from the wreck. Find her, patch the ship, bring it home to Booty Bay.")
    s = Z_INBETWEEN
    a = book.quest(
        9109360, "WANTED: See Her Off", 60, 58, board, board, "wren",
        "Wren, worried:$B$BBramble built an airship, Snack. She's taking it up from the Booty Bay dock. Go and see her "
        "off. Wave. Then wait for the letter. There's always a letter.",
        "See Bramble off at the Booty Bay dock.",
        "Wave, Snack. Then wait.",
        "She took off! It flew! Briefly! Downwards, I think. Watch the post.",
        objectives=[visit("Saw Bramble off at the dock", BOOTY_DOCK[0], BOOTY_DOCK[1], BOOTY_DOCK[2], radius=25.0, stay=10)],
        sort=s, xp=3,
        mail=("Slight problem", "Snack,$B$BSlight problem. Come find me. I can see sand, a big statue and angry "
                                "bugs.$B$B- Bramble", 300),
        story="See Bramble off from the Booty Bay dock in her first airship. A letter follows.")
    wrecks = (
        (9109361, "Sand, a Big Statue, Angry Bugs", "the sand by the great scarab gate in Silithus", 1, (-8130.0, 1525.0),
         "It flew! Briefly! Downwards!", ("Another slight problem",
         "Snack,$B$BNew ship. Same problem. Snow. Bones of something enormous. A dragon is looking at me.$B$B- Bramble", 600),
         reins(5)),
        (9109362, "Snow, Bones, a Dragon Looking at Me", "the dragon bones below Wyrmrest in the Dragonblight", 571, (3700.0, 450.0),
         "The dragon was very nice about it.", ("Problem, slight",
         "Snack,$B$BMushrooms. Taller than me. They glow. Something is singing at me in a language made of mud.$B$B- Bramble", 600),
         reins(2)),
        (9109363, "Mushrooms Taller Than Me", "the giant mushrooms by Sporeggar in Zangarmarsh", 530, (215.0, 8540.0),
         "The sporelings want to keep the propeller.", ("Small problem",
         "Snack,$B$BA waterfall. Dinosaurs. I think one licked me.$B$B- Bramble", 600),
         reins(180)),
        (9109364, "I Think One Licked Me", "the waterfall by Marshal's Refuge in Un'Goro Crater", 1, (-6150.0, -1080.0),
         "It was a friendly lick. Mostly.", ("Problem",
         "Snack,$B$BPurple. Floating rocks. Nothing below. I don't know how I got here. I think I'm in the Twisting "
         "Nether. Somehow.$B$B- Bramble", 600),
         reins(200)),
        (9109365, "Purple, Floating Rocks, Nothing Below", "the very edge of Netherstorm, over the Twisting Nether", 530,
         (3835.9, 2045.9), "She says it's the best one yet.", None, reins(3)),
    )
    prev = a.id
    for i, (qid, title, where, m, at, line, mail, rewards) in enumerate(wrecks):
        wreck = book.thing(f"wreck_{qid}", "Bramble's Airship (Crashed)", MACHINE_BROKEN, [(m, at[0], at[1], 0.0, 0.0)], size=1.6)
        leaks = book.thing(f"leaks_{qid}", "A Leak in the Hull", CRATE,
                           [(m, at[0] + 8.0, at[1], 0.0, 0.0), (m, at[0] - 6.0, at[1] + 6.0, 0.0, 0.0),
                            (m, at[0], at[1] - 8.0, 0.0, 0.0)], size=0.6)
        q = book.quest(
            qid, title, 62 + i * 4, 58 + i * 3, board, board, "wren",
            f"Wren, reading the letter for the hundredth time:$B$BShe's at {where}, Snack, I worked it out. Find the "
            "wreck, pull her out, patch the three leaks, and fly the ship home to the Booty Bay dock. It'll fall "
            "apart on the way. Hold it together.",
            f"Find Bramble's crashed airship at {where}, patch its 3 leaks, and bring it home to the Booty Bay dock.",
            "Is she in one piece? Is the ship?",
            f"Home! Mostly in one piece! {line} The ship's yours, Snack; she's already building the next one.",
            objectives=[touch(wreck, 1, "Bramble pulled out of the wreck"), touch(leaks, 3, "A leak patched"),
                        visit("The ship flown home to Booty Bay", BOOTY_DOCK[0], BOOTY_DOCK[1], BOOTY_DOCK[2], radius=30.0)],
            prev=prev, sort=s, items=rewards, xp=6, mail=mail,
            story=_story(f"Find Bramble's crashed airship at {where}, patch it, fly it home.", rewards))
        prev = q.id
