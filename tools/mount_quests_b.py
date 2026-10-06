"""Task 022: the mount quests, part 2: ideas 18-38 (the ottuk, the kittens, the crow's pages, junk into jets, the
knight, the stable boy, fel rehab, the wandering ancient, Winter Veil, the giant egg, the broom lessons, the snail)."""

from devourer_quests import (devour, slay, visit, touch, emote, trail, struck, among, carry, fish, wake, gossip, ability, LINES,
                             EMOTE_PET, EMOTE_ROAR, EMOTE_HUG, EMOTE_DANCE, EMOTE_KISS, EMOTE_BOW, HAGATHA, WREN)
from devourer_quests_content import FACTION_SHY
from mount_quests import (Reins, reins, mount_look, IN_BETWEEN, Z_HALL, Z_INBETWEEN, BONFIRE, BOOK, SCROLL, HOT_COALS,
                          GRAVE, TOMBSTONE, MACHINE_BROKEN, GEAR, ARMOR_STAND, HELM, FLOWERS, GIFT, EGG_EASTER, BROOM,
                          BUCKET, CRATE, FISH_BOX, CAGE, EMOTE_WHISTLE, EMOTE_SHOO, EMOTE_NO, EMOTE_STARE, EMOTE_SIT)

Reins.BY_PREVIEW.update({
    62: (9304100, "Shiny Tidewater Pincer"), 166: (9304330, "Sapphire Riverbeast"), 285: (9304555, "Reins of the Blue Scouting Ottuk"),
    286: (9304559, "Reins of the Black War Ottuk"), 287: (9304563, "Otterreal Thundertrotter's Saddle"), 348: (9304687, "Emberback Plodder's Saddle"),
    350: (9304690, "Battletested Crest-Horn's Saddle"),
    41: (9304076, "Sunwarmed Furline"), 42: (9304078, "Reins of the Moon-Bathed Feline"), 43: (9304079, "Jigglesworth Sr.'s Reins"),
    32: (9304056, "Reins of the Scribe's Trusted Trailbear"), 35: (9304061, "Reins of the Soaring Spelltome"), 128: (9304230, "Flametouched Raven"),
    19: (9304041, "Rusty Buzzsaw Ripper"), 114: (9304207, "Keys to the Explorer's Jungle Hopper"), 148: (9304279, "Gnomish \"Eco-Friendly\" Plane"),
    152: (9304285, "Black Goblin Aerial Propulsor"), 153: (9304290, "Goblin Super Sonic Reactor"),
    9: (9304013, "King's Noble Charger"), 13: (9304024, "Argent Courser (Grey)"), 98: (9304185, "Dawnforge Ram"), 171: (9304340, "Seabiscuit's Reins"),
    174: (9304343, "Lightcharger"), 194: (9304390, "Reins of the Armored Vorquin Leystrider"), 203: (9304406, "Glorious Felcrusher"),
    250: (9304502, "Reins of the Vigilant Charger"), 251: (9304504, "Reins of the Algari Warden's Charger"), 261: (9304518, "High Priest's Lightsworn Seeker"),
    329: (9304628, "Frostcharger"), 351: (9304691, "Tyrael's Charger"), 352: (9304692, "Seraph's Charger"), 353: (9304693, "Tzar, Lord of Steeds"),
    138: (9304259, "Ghostly Charger"), 164: (9304323, "Reins of The Headless Horseman's Chilling Charger"), 252: (9304505, "Undead Warhorse"),
    253: (9304506, "Undead Charger"), 354: (9304694, "Risen Mare"),
    14: (9304027, "Biletooth Gnasher"), 15: (9304034, "Felflame Talbuk"), 25: (9304048, "Felslate Basilisk"), 59: (9304097, "Fel Beast"),
    79: (9304143, "Reins of the Felsaber"), 120: (9304217, "Shadow Fel Hound"), 122: (9304221, "Fel Reaver Head"), 123: (9304222, "Wrathful Fel Reaver Head"),
    124: (9304223, "Felsteel Annihilator's Control Module"), 125: (9304227, "Felforged Reins of the Illidari Felstalker"), 127: (9304229, "Felfire Hawk"),
    140: (9304261, "Armored Fel-Infused Tauralus"), 175: (9304344, "Felcharger"), 197: (9304396, "Felfire Steed"), 201: (9304403, "Felsteel Arachnid"),
    233: (9304472, "Felreaver Deathcycle's Keys"), 234: (9304473, "Skyreaver Deathcycle's Keys"), 235: (9304474, "Shadowreaver Deathcycle's Keys"),
    236: (9304475, "Flamereaver Deathcycle's Keys"), 237: (9304476, "Worldreaver Deathcycle's Keys"), 273: (9304540, "Corrupted Grinning Reaver"),
    373: (9304725, "Reins of the Infernal Direwolf"),
    8: (9304012, "Branch of the Wandering Ancient"), 11: (9304015, "Witchwood Stag (Blue)"), 12: (9304019, "Winterborn Runestag"),
    101: (9304191, "Mottled Meadowstomper"), 137: (9304255, "Carnivarus Cutting"), 161: (9304310, "Loyal Grove Crawler's Saddle"),
    168: (9304335, "Reins of the Highmountain Elderhorn"), 228: (9304461, "Reins of the Dark Moose Bull"), 229: (9304464, "Stonehide Elderhorn"),
    230: (9304465, "Reins of the Frostbitten Elderhorn"), 231: (9304468, "Reins of the Grove Warden"), 280: (9304549, "Arboreal Chloroceros's Saddle"),
    135: (9304250, "Mildly Munched Gingerboard"), 245: (9304493, "Big Blizzard Bear"), 258: (9304512, "Minion of Grumpus"),
    328: (9304627, "Rudolthorn's Reins"), 343: (9304666, "Classic Toy Train"), 386: (9304773, "Candy Copter"),
    266: (9304533, "Jade, Bright Foreseer's Saddle"), 267: (9304534, "Jin, Verdant Wavechaser's Saddle"),
    37: (9304063, "Flying Broom"), 205: (9304408, "Love Witch's Sweeper"),
    136: (9304251, "Herbaceous Floral Snail"), 198: (9304397, "Reins of the Blue Magma Slug"), 199: (9304401, "Reins of the Red Magmashell"),
})
EVENT_WINTER_VEIL, EVENT_LUNAR, EVENT_NOBLEGARDEN, EVENT_HALLOWS = 2, 7, 8, 12


def build(book, board):
    ottuk(book, board)
    kittens(book, board)
    crow(book, board)
    jets(book, board)
    knight(book, board)
    stable_boy(book, board)
    fel_rehab(book, board)
    ancient(book, board)
    winter_veil(book, board)
    giant_egg(book, board)
    brooms(book, board)
    snail(book, board)


# --- 18. Otto Would Be Proud -------------------------------------------------------------------------------------------

def ottuk(book, board):
    book.region("18. Otto Would Be Proud (levels 68-72)",
                "Ottuks only trust people who share their fish. Fish on the Borean coast with the ottuk watching; every "
                "catch with it near is a fish shared. It brings friends.")
    s = Z_INBETWEEN
    otto = book.beast("otto", "Otto", 6368, display=mount_look(285), level=70, faction=FACTION_SHY, passive=True, scale=0.9,
                      subname="Keeps the Big Ones", spawns=[(571, 2284.0, 5113.0, 0.0, 2.0)])
    war = book.beast("war_ottuk", "The War Ottuk", 6368, display=mount_look(286), level=72, faction=FACTION_SHY, passive=True,
                     scale=1.0, subname="Will Not Be Sold", spawns=[(571, 722.0, -2842.0, 0.0, 4.0)])
    a = book.quest(
        9109120, "WANTED: A Fish for Otto", 68, 66, board, board, "wren",
        "Wren, with a fishing pole drawn on the notice:$B$BSnack, there's an ottuk on the beach below Valiance Keep in "
        "the Borean Tundra, and he's called Otto, because of course he is. Ottuks only trust people who share their "
        "fish. So: fish there, with Otto watching, and every third fish is his. He'll know. He's keeping count. He's "
        "keeping the big ones, too, which is smart.",
        "Fish on the beach below Valiance Keep with Otto the ottuk near you; 9 catches with him watching.",
        "Nine fish, Snack, with Otto watching. He can tell when you hide one.",
        "Nine fish and Otto's your friend for life. He followed you up the beach! Here's his reins. Yes, you can ride "
        "an ottuk. He insists.",
        objectives=[fish(9, "A fish caught with Otto watching", near=otto.entry, line="sniffs the fish, nods, and keeps it.")],
        sort=s, items=reins(285), xp=6,
        story="Fish on the Borean coast with Otto the ottuk watching: nine catches shared. Reward: the Blue Scouting Ottuk.")
    b = book.quest(
        9109121, "Otto's Friends", 70, 68, board, board, "wren",
        "Wren:$B$BOtto has FRIENDS, Snack. Crabs, mostly, and a plodder, and a riverbeast that lives up the coast. He "
        "says (he doesn't say, he's an ottuk, but I can tell) that if you share nine more fish, they'll all come to see "
        "what the fuss is about.",
        "Fish 9 more catches with Otto watching; his friends come to see.",
        "Nine more, Snack. His friends are shy.",
        "They CAME. A crab the size of a cart, a plodder, a riverbeast, all sitting on the beach eating your fish. "
        "Here are all their reins. Otto arranged it. Otto's very organised.",
        objectives=[fish(9, "A fish shared with Otto's friends near", near=otto.entry)], prev=a.id, sort=s,
        items=reins(62, 348, 166), xp=7,
        story="Nine more shared fish; Otto's friends come. Reward: the Tidewater Pincer, the Emberback Plodder, the Sapphire Riverbeast.")
    book.quest(
        9109122, "The War Ottuk", 72, 70, board, board, "hagatha",
        "Hagatha:$B$BThe tuskarr of the fjord ride ottuks into battle, little horror, big ones, in harness, and they "
        "will not sell. But an ottuk that has eaten your fish will fight for you. A war ottuk sits on the beach at "
        "Kamagua in the Howling Fjord, by the Longtusk fishermen. Go with Otto's blessing (he gave it; he sniffed "
        "you), fish nine catches with it watching, and it will decide about you.",
        "Fish 9 catches at Kamagua in the Howling Fjord with the war ottuk watching.",
        "Nine catches, on the fjord's beach. The war ottuk is watching from the water.",
        "It came, and ate, and knelt, which is how an ottuk says 'I will carry you'. The crest-horn and the "
        "thundertrotter came after it; they follow the war ottuk everywhere.$B$BTake the reins.",
        objectives=[fish(9, "A fish shared with the war ottuk", near=war.entry, line="snaps the fish out of the air.")], prev=b.id, sort=s, items=reins(286, 287, 350), xp=7,
        story="Fish on the fjord's beach; the war ottuk comes to be fed. Reward: the Black War Ottuk, the Thundertrotter, the Crest-Horn.")


# --- 19. Lost Kittens of Dalaran ---------------------------------------------------------------------------------------

def kittens(book, board):
    book.region("19. Lost Kittens of Dalaran (level 70+)",
                "Kittens are lost in Dalaran. They mew when you are near; there are no markers. Find all eight by ear "
                "and bring them to their very proud, very fat father.")
    s = Z_INBETWEEN
    spots = [(5765.0, 522.0, 654.0), (5843.0, 564.0, 653.0), (5619.0, 695.0, 652.0), (5758.0, 745.0, 654.0),
             (5837.0, 634.0, 657.0), (5664.0, 619.0, 648.0), (5807.0, 683.0, 647.0), (5879.0, 785.0, 642.0)]
    kitten = book.beast("dalaran_kitten", "A Lost Kitten", 7386, level=1, faction=FACTION_SHY, passive=True, scale=1.0,
                        subname="Mews", spawns=[(571, x, y, z, 0.0) for x, y, z in spots])
    father = book.beast("fat_father", "Jigglesworth Sr.", 6368, display=mount_look(43), level=70, faction=35, passive=True,
                        scale=1.2, subname="Very Proud, Very Fat", spawns=[(571, 5750.0, 526.0, 653.0, 3.0)])
    a = book.quest(
        9109130, "WANTED: Eight Lost Kittens", 70, 68, board, board, "hagatha",
        "Hagatha, almost soft:$B$BFat cats are the best cats, little horror, and the fattest cat in Dalaran has lost "
        "his kittens. Eight of them, somewhere in the streets. No marks, no map. They mew when you are near; that is "
"all. Look in the corners, under the stairs, behind the shops.$B$BFind each one and pat it, so it knows to go "
        "home. The father is by the fountain in the Eventide; he will know.",
        "Find the 8 lost kittens in Dalaran by their mewing and /pet each one.",
        "Eight kittens. Listen. They are small, and Dalaran is loud.",
        "Eight, patted, and every one of them went home ahead of you. The father is beside himself; he has eaten "
        "two whole fish in relief.$B$BHe says his brother will carry you, by way of thanks. His brother is as fat as he "
        "is. Take the reins.",
        objectives=[emote(8, "Lost kitten found and patted", EMOTE_PET, entries=[kitten.entry])], sort=s, items=reins(43), xp=6,
        story="Find eight mewing kittens in Dalaran by ear and pat them home. Reward: Jigglesworth Sr.'s Reins.")
    book.quest(
        9109131, "The Father's Thanks", 72, 70, board, board, "hagatha",
        "Hagatha:$B$BThe fat father has more thanks than fish, little horror. He keeps two cats of his own that are too "
        "big for his rooms: a furline, warmed by the sun, and a feline that bathes in the moon. Go and sit with him in "
        "Dalaran a while, by the fountain, and he will give them up.",
        "Sit with Jigglesworth Sr. in Dalaran for a while.",
        "Sit with him. He talks slowly. He is very fat.",
        "He talked for an hour about his kittens, and then he gave you the furline and the moon cat, and then he "
        "went to sleep.$B$BTake the reins. Visit him sometimes.",
        objectives=[visit("Sat with Jigglesworth Sr.", 571, 5750.0, 526.0, radius=12.0, stay=45)], prev=a.id, sort=s,
        items=reins(41, 42), xp=6,
        story="Sit with the fat father a while. Reward: the Sunwarmed Furline and the Moon-Bathed Feline.")


# --- 20. Wren's Crow and the Torn Spelltome ---------------------------------------------------------------------------

def crow(book, board):
    book.region("20. Wren's Crow and the Torn Spelltome (levels 40-70)",
                "Pilfer, Wren's crow, tore Hagatha's spelltome into seven pages and hid them in libraries. Each page "
                "holds a riddle to the next; the crow cheats.")
    s = Z_INBETWEEN
    pages = [
        ("Caer Darrow, where the dead keep school", 0, 1250.0, -2560.0, "The next page lies where a wizard's tower looks down on a pass "
         "the dead walk through, and nobody goes in."),
        ("Karazhan's gate", 0, -11100.0, -1990.0, "The next page lies in a city that floats, in the hall where the violet books are kept."),
        ("the Violet Citadel in Dalaran", 571, 5802.0, 640.0, "The next page lies on a tier of seers, in a city of light with a naaru at its heart."),
        ("the Scryers' tier in Shattrath", 530, -2273.0, 5576.0, "The next page lies in a monastery that burns things, under the Scarlet eye."),
        ("the Scarlet Monastery's library door", 0, 2890.0, -820.0, "The next page lies under the mountain, with the explorers and their bones."),
        ("the Hall of Explorers in Ironforge", 0, -4635.0, -1306.0, "The next page lies under the ruins, where the dead read in the dark."),
        ("the Magic Quarter of Undercity", 0, 1630.0, 170.0, ""),
    ]
    prev = None
    for i, (where, map_id, x, y, riddle) in enumerate(pages):
        page = book.thing(f"page_{i}", f"A Torn Page ({i + 1} of 7)", SCROLL, [(map_id, x, y, 0.0, 0.0)], size=0.6)
        last = i == len(pages) - 1
        q = book.quest(
            9109140 + i, ("WANTED: " if i == 0 else "") + f"The {['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Last'][i]} Page",
            40 + 5 * i if i < 6 else 70, 38 + 5 * i if i < 6 else 68, board, board, "wren",
            ("Wren, furious:$B$BPILFER. My crow. Hagatha's spelltome. He tore it into seven pages and hid them in "
             "LIBRARIES, because he's a crow and he thinks that's funny, and he's written a riddle on each one to the "
             f"next, and he CHEATS.$B$BThe first page is at {where}. He left me that one. Go and get it before "
             "somebody reads it." if i == 0 else
             f"Wren, reading the last page:$B$B'{riddle_prev}'$B$BHe's sitting on it, I bet. He does that. Go to "
             f"{where} and shoo him off it." if i < 6 else
             f"Wren, trembling:$B$B'{riddle_prev}'$B$BThe last page. He hid it in UNDERCITY. In the dark. With "
             "the dead. Snack, I'm not going. You go. Get the page, and the book will be whole, and it flies, "
             "Hagatha says, when it's whole."),
            f"Find the torn page at {where}.",
            "Caw. (That means you're slow.)",
            (f"Got it! And a riddle: '{riddle}'" if riddle else
             "The LAST PAGE. The book's whole. It... it's flapping. It flies! It flies badly! Hagatha's furious and "
             "delighted at once.$B$BThe book is yours; Hagatha won't touch it now that it's been in Undercity. And "
             "Pilfer's cousin, the flame-touched raven, has been following you since Karazhan. And the scribe's bear "
             "that carried the book in the first place wants to carry it, and you, again."),
            objectives=[touch(page, 1, f"The page found at {where.split(',')[0]}")], prev=prev, sort=s, xp=5 if not last else 7,
            items=reins(35, 128, 32) if last else [],
            story=f"The {i + 1}. page of Hagatha's spelltome, at {where}" + (". Reward: the Soaring Spelltome, the Flametouched Raven, the Scribe's Trailbear." if last else "."))
        riddle_prev = riddle
        prev = q.id


# --- 23. Junk Into Jets --------------------------------------------------------------------------------------------------

def jets(book, board):
    book.region("23. Junk Into Jets (levels 30-60)",
                "Take apart broken machines with a wrench; one bolt in three is wrong and sends you flying. Bramble builds "
                "vehicles from the parts.")
    s = Z_INBETWEEN
    machines = book.beast("junk_machine", "A Broken Machine", 4260, level=30, faction=35, passive=True, scale=0.8,
                          subname="Three Bolts, One Wrong",
                          spawns=[(1, -6224.0, -3861.0, 0.0, 0.0), (1, -6260.0, -3856.0, 0.0, 1.0), (1, -6213.0, -3850.0, 0.0, 2.0),
                                  (0, -14354.0, 414.0, 0.0, 0.0), (0, -14330.0, 430.0, 0.0, 1.0),
                                  (1, 1109.0, -3104.0, 0.0, 0.0), (0, -11990.0, -526.0, 0.0, 0.0)],
                          gossip=("The machine ticks. Three bolts hold the good parts in. One of them holds the spring.",
                                  [("Turn the left bolt.", "The left bolt comes free. A gear, a pipe and something springy fall out.", True),
                                   ("Turn the middle bolt.", "The middle bolt was the spring. It hits you on the nose. Try another machine.", False),
                                   ("Turn the right bolt.", "The right bolt comes free. Parts! Bramble will be pleased.", True)],
                                  0))
    big = book.beast("junk_machine_big", "A Big Broken Machine", 4260, level=60, faction=35, passive=True, scale=1.2,
                     subname="Three Bolts, Two Wrong",
                     spawns=[(1, -4062.0, -3628.0, 0.0, 0.0), (530, 3089.0, 3650.0, 0.0, 0.0), (571, 4156.0, -2964.0, 0.0, 0.0),
                             (1, 6720.0, -4660.0, 0.0, 0.0), (1, -7187.0, -3839.0, 0.0, 0.0)],
                     gossip=("This one is bigger and it hums. Three bolts. Two of them are holding something angry in.",
                             [("Turn the top bolt.", "Steam. Lots of steam. Nothing comes free.", False),
                              ("Turn the bolt with the scratch marks.", "It comes free, and a whole engine slides out. Somebody marked the right one!", True),
                              ("Turn the shiny bolt.", "The shiny bolt was the angry one. It shouts at you in goblin.", False)],
                             0))
    a = book.quest(
        9109150, "WANTED: Ten Broken Machines", 32, 30, board, board, "wren",
        "Bramble's handwriting, on Wren's board:$B$BSeven broken machines. Three race wrecks on the Shimmering Flats, "
        "two in Booty Bay's scrapyard, the shredder in the Barrens and the one in Stranglethorn. Three bolts each. One bolt is WRONG and it's the springy one. Don't turn the springy one. "
        "You'll know if you did.$B$BBring me the parts. I'll build something. It'll be mostly safe.",
        "Take apart 7 broken machines (turn the right bolts; the springy one bites).",
        "Seven machines, and the parts. Did you turn the springy one? You turned the springy one.",
        "Parts! Gears and pipes and the springy things! Here, I built two already: a buzzsaw on wheels and a jungle "
        "hopper. The hopper hops. The buzzsaw... duck.",
        objectives=[gossip(machines, "Broken machine taken apart")], sort=s, xp=5, items=reins(19, 114),
        story="Take apart seven broken machines, choosing the right bolts. Reward: the Rusty Buzzsaw Ripper and the Jungle Hopper.")
    a.objectives[0].count = 7
    book.quest(
        9109151, "Parts for a Plane", 55, 50, board, board, "wren",
        "Bramble, covered in oil:$B$BMore parts. The big machines this time: the wreck in Dustwallow, Area 52's, the "
        "Grizzly Hills one, Everlook's and Gadgetzan's. Five of them, and they're angrier. I'm building a PLANE. Eco-friendly. It runs on whatever you feed it, "
        "which is probably going to be me, so hurry.",
        "Take apart the 5 big broken machines (one bolt in three is right).",
        "Five big ones, Snack. The plane's just a chair with a propeller so far.",
        "It FLIES. The plane flies, the propulsor propels, and the reactor... hums. Keep the reactor away from the "
        "cauldron.$B$BHere are the keys to all three. Mostly safe.",
        objectives=[gossip(big, "Big machine taken apart")], prev=a.id, sort=s, xp=7, items=reins(148, 152, 153),
        story="Five big angry machines for the big parts. Reward: the Gnomish Plane, the Goblin Aerial Propulsor, the Super Sonic Reactor.")
    book.quests[-1].objectives[0].count = 5


# --- 26. The Knight Without a Horse -------------------------------------------------------------------------------------

def knight(book, board):
    book.region("26. The Knight Without a Horse (levels 55-80)",
                "A Devourer remembers what it eats. Long ago you devoured a warhorse; at Light's Hope its ghost knight "
                "wants it back. Hagatha can pull the memory out of you at dawn, once you find the knight's armour.")
    s = Z_INBETWEEN
    armour = book.thing("knight_armour", "A Knight's Armour Piece", ARMOR_STAND,
                        [(0, 2300.0, -5300.0, 0.0, 0.0), (0, 1870.0, -3210.0, 0.0, 0.0), (0, 2692.0, -4029.0, 0.0, 0.0),
                         (0, 2281.1, -4738.0, 0.0, 0.0), (0, 1996.8, -4491.4, 0.0, 0.0)], size=0.8)
    knight_ = book.beast("ghost_knight", "The Knight Without a Horse", 16906, level=60, faction=35, passive=True, scale=1.0,
                         subname="One More Ride", spawns=[(0, 2296.0, -5290.0, 0.0, 4.5)],
                         gossip=("The knight looks through you. 'You ate her. My horse. I can smell her on you, years deep. Give her back.'",
                                 [("I cannot give back what I ate.", "'No. But the witch can pull the memory out of you. At dawn. Find my armour first; a knight does not ride in rags.'", True),
                                  ("I do not remember any horse.", "'You remember every meal. You are a Devourer. Do not lie to the dead.'", False)], 0))
    a = book.quest(
        9109160, "WANTED: The Knight Without a Horse", 56, 54, board, board, "hagatha",
        "Hagatha, slowly:$B$BA Devourer remembers what it eats, little horror, every meal, all the way down. Long ago, "
        "before Wren found you, you ate a warhorse. At Light's Hope Chapel its knight is still waiting for it; he is "
        "dead, and does not mind, but he minds about the horse.$B$BGo and speak with him. Tell him the truth. Then find "
        "the five pieces of his armour, scattered across the Plaguelands where he fell: a knight does not ride in rags.",
        "Speak with the ghost knight at Light's Hope and admit what you ate; find the 5 pieces of his armour in the "
        "Eastern Plaguelands.",
        "He is waiting. He has waited a long time.",
        "Five pieces, and the truth told. He is standing straighter already.$B$BNow for the horse.",
        objectives=[gossip(knight_, "The truth told to the knight"), touch(armour, 5, "A piece of the knight's armour found")],
        sort=s, xp=6,
        story="Tell the ghost knight the truth about his horse; find his armour in the Plaguelands.")
    horse = book.beast("knight_horse", "The Knight's Charger", 385, display=mount_look(9), level=60, faction=35, passive=True,
                       scale=1.0, subname="A Memory, Pulled Out")
    dawn = book.thing("knight_dawn", "The Chapel's Threshold", ARMOR_STAND, [(0, 2296.0, -5295.0, 0.0, 0.0)], size=0.6,
                      summon=horse.entry, count=1, follow=True)
    b = book.quest(
        9109161, "At Dawn, in the Chapel", 58, 56, board, board, "hagatha",
        "Hagatha:$B$BAt dawn, in the chapel, I will draw the horse's memory out of you. It hurts; your companions will "
        "worry. Stand on the threshold at first light and hold still. When the memory stands beside you, let the knight "
        "ride it, once. Then it stays with you; a memory cannot leave the one who holds it.",
        "At dawn, stand still on the threshold of Light's Hope Chapel, then touch the threshold to call the horse out.",
        "Dawn, little horror. Not before, not after. Stand still.",
        "He rode. Once, around the chapel, and the light took him. The horse stayed; it is yours, as it was always going "
        "to be.$B$BThe squires' mounts came out of the memory with it: a vorquin, a frostcharger. They follow the "
        "knight's horse everywhere.",
        objectives=[visit("Stood still at the chapel at dawn", 0, 2296.0, -5295.0, radius=10.0, dawn=True, stay=15, still=True),
                    wake(dawn, "The knight's horse called out of the memory")],
        prev=a.id, sort=s, items=reins(9, 194, 329), xp=7,
        story="At dawn on the chapel threshold, Hagatha draws the horse's memory out; the knight rides once. Reward: the King's Noble Charger, the Vorquin, the Frostcharger.")
    c = book.quest(
        9109162, "The Dwarf Under the Mountain", 62, 60, board, board, "hagatha",
        "Hagatha:$B$BYou ate a ram once, too, little horror, in the hills under Ironforge, and its rider is buried in "
        "the Hall of Explorers with the other dwarves who got lost. Same memory, louder rider. Go and stand at his "
        "tomb at dawn and I will pull the ram out of you. He will shout. Dwarves do.",
        "At dawn, stand still in the Hall of Explorers in Ironforge for the ram's memory.",
        "Dawn, under the mountain. He is already shouting.",
        "He shouted, he rode, he shouted some more, and the mountain took him back. The Dawnforge ram is yours.",
        objectives=[visit("Stood still in the Hall of Explorers at dawn", 0, -4635.0, -1306.0, radius=15.0, dawn=True, stay=15, still=True)],
        prev=b.id, sort=s, items=reins(98), xp=6,
        story="A dwarven chapter: the ram's memory, at dawn in Ironforge. Reward: the Dawnforge Ram.")
    d = book.quest(
        9109163, "Grander Memories", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BThere are grander things in you than one knight's horse, little horror. Couriers you ate, "
        "chargers, a seabiscuit from the docks, a felcrusher from the Dark Portal's first days. Each needs a dawn and "
        "a threshold. Three dawns: Light's Hope, the Dark Portal, Booty Bay's dock. Stand still at each.",
        "At dawn, stand still at Light's Hope Chapel, at the Dark Portal, and on the Booty Bay dock.",
        "Three dawns. Patience is a thing you can eat too.",
        "Three memories, pulled out and standing. The chapel is getting crowded with your horses.$B$BTake the reins.",
        objectives=[visit("Dawn at Light's Hope", 0, 2296.0, -5295.0, radius=15.0, dawn=True, stay=15, still=True),
                    visit("Dawn at the Dark Portal", 0, -11905.0, -3207.0, radius=60.0, dawn=True, stay=15, still=True),
                    visit("Dawn on the Booty Bay dock", 0, -14281.0, 552.0, radius=30.0, dawn=True, stay=15, still=True)],
        prev=c.id, sort=s, items=reins(13, 171, 203, 250), xp=7,
        story="Three dawns, three grander memories. Reward: the Argent Courser, Seabiscuit, the Felcrusher, the Vigilant Charger.")
    book.quest(
        9109164, "The Last Memory", 80, 78, board, board, "hagatha",
        "Hagatha, very quietly:$B$BThere is one memory in you I did not expect, little horror. Something that was never "
        "a horse. Something with wings of light that let itself be eaten, long ago, so that it could be remembered. "
        "Stand at the top of Wyrmrest at dawn, where the sky is closest, and hold very still. I will try.",
        "At dawn, stand still at the top of Wyrmrest Temple while Hagatha draws out the last memory.",
        "The top of Wyrmrest. Dawn. Still. This one will hurt.",
        "It came out of you like a sunrise, and it did not go anywhere. It had been waiting to be remembered.$B$B"
        "Tyrael's charger, the seraph's, the lord of steeds: they are yours. Nothing you have eaten will ever be "
        "grander than that.",
        objectives=[visit("Dawn at the top of Wyrmrest", 571, 3546.0, 287.0, radius=25.0, dawn=True, stay=20, still=True, above=200.0)],
        prev=d.id, sort=s, items=reins(351, 352, 353, 174), xp=8,
        story="The last memory, at dawn atop Wyrmrest. Reward: Tyrael's Charger, the Seraph's Charger, Tzar, the Lightcharger.")
    book.quest(
        9109165, "The Warden's Charger", 74, 72, board, board, "hagatha",
        "Hagatha:$B$BOne more, smaller. A warden's charger, and a priest's lightsworn seeker, eaten in a war you do not "
        "remember. Dawn at the Argent camp in the Plaguelands; stand still.",
        "At dawn, stand still at the Argent Dawn's camp in the Eastern Plaguelands.",
        "Dawn at the Argent camp.",
        "Two more memories, standing in the Argent camp, looking embarrassed. Take the reins.",
        objectives=[visit("Dawn at the Argent camp", 0, 2692.0, -4029.0, radius=25.0, dawn=True, stay=15, still=True)],
        prev=d.id, sort=s, items=reins(251, 261), xp=6,
        story="A smaller dawn at the Argent camp. Reward: the Algari Warden's Charger and the Lightsworn Seeker.")


# --- 27. The Undead Stable Boy -----------------------------------------------------------------------------------------

def stable_boy(book, board):
    book.region("27. The Undead Stable Boy (level 20+)",
                "Hagatha knew a stable boy in life. He is Forsaken now and wants the horse he had. She will not say how "
                "she knew him.")
    s = Z_INBETWEEN
    boy = book.beast("stable_boy", "Tam the Stable Boy", 1518, level=20, faction=35, passive=True, scale=1.0,
                     subname="Forsaken, Still Waiting", spawns=[(0, 2250.0, 329.0, 0.0, 1.0)],
                     gossip=("Tam looks up with what is left of his face. 'She sent you? Hagatha? She always liked apples. "
                             "The mare, I mean. Hagatha liked... never mind what Hagatha liked.'",
                             [("Where is the mare buried?", "'By the old stable. Under the dirt mound with no stone. I put her there myself, before... before.'", True),
                              ("How do you know Hagatha?", "'Ask her. Go on. Ask her. I'd like to see her face.'", False)], 0))
    grave = book.thing("mare_grave", "A Grave With No Stone", GRAVE, [(0, 2262.0, 340.0, 0.0, 0.0)], size=1.0,
                       summon=book.beast("ghost_mare", "The Ghost of a Mare", 385, display=mount_look(138), level=20,
                                         faction=FACTION_SHY, passive=True, scale=1.0, subname="Liked Apples").entry,
                       count=1, follow=True)
    mare = book.beasts[-1]
    a = book.quest(
        9109170, "WANTED: A Horse for Tam", 20, 18, board, board, "hagatha",
        "Hagatha, not meeting your eye:$B$BThere is a stable boy in Brill, little horror. Was. He is Forsaken now, "
        "and he wants the horse he had, and I... knew him, once. Do not ask how. Go and talk to him. Find where the "
        "mare is buried. Her ghost will come to whoever digs, and it will choose him.$B$BIt will not choose him. It will "
        "choose you. They always do. Be kind about it.",
        "Speak with Tam the stable boy in Brill and find the mare's grave by the old stable.",
        "Have you found the grave? He will tell you, if you ask about the mare and not about me.",
        "The mare's ghost came up out of the dirt, looked at Tam, looked at you, and chose you. He cried. Forsaken can, "
        "it turns out.$B$BShe is yours. Visit him. And never ask me how I knew him.",
        objectives=[gossip(boy, "Tam asked about the mare"), wake(grave, "The mare's grave dug; her ghost rose")],
        sort=s, items=reins(138), xp=5,
        story="Tam the Forsaken stable boy wants his mare back; her ghost rises and chooses you. Reward: Ghostly Charger.")
    stalls = book.thing("stable_stalls", "An Old Stall", CAGE,
                        [(0, 2240.0, 318.0, 0.0, 0.0), (0, 2248.0, 312.0, 0.0, 0.0), (0, 2256.0, 306.0, 0.0, 0.0)], size=0.8)
    follow = book.thing("stable_boy_follow", "Tam's Lantern", BUCKET, [(0, 2252.0, 331.0, 0.0, 0.0)], size=0.5,
                        summon=boy.entry, count=1, follow=True)
    b = book.quest(
        9109171, "Three Goodbyes", 22, 20, board, board, "hagatha",
        "Hagatha:$B$BThe old stable still has three stalls, and three things still stand in them: the warhorse, the "
        "charger and the risen mare the Scourge left behind. They will come with you, but each one wants Tam to say "
        "goodbye first; he fed them. Take his lantern so he follows you, and walk him to each stall.",
        "With Tam following, bring him to the three old stalls so he can say goodbye.",
        "Three stalls, little horror. He walks slowly. So did he before.",
        "He said goodbye three times, and three times something came out of a stall and stood beside you. He is sitting "
        "on the fence now, looking almost happy.$B$BTake the reins.",
        objectives=[wake(follow, "Tam's lantern taken; he follows"), touch(stalls, 3, "A goodbye said at a stall")],
        prev=a.id, sort=s, items=reins(252, 253, 354), xp=6,
        story="Walk Tam to the three old stalls for his goodbyes. Reward: the Undead Warhorse, the Undead Charger, the Risen Mare.")
    horseman = book.beast("horseman_riddle", "The Horseman's Charger", 385, display=mount_look(164), level=70, faction=35,
                          passive=True, scale=1.0, subname="Lost Its Rider Again", spawns=[(0, 2262.0, 352.0, 0.0, 3.0)],
                          gossip=("The Headless Horseman's charger stands by the old stable without its rider; he has lost his head "
                                  "again. It looks at the ghost mare, then at you, and its voice comes out of the pumpkin on its "
                                  "saddle: 'A riddle, for the mare. I have a head but no body, a face but no eyes, and I ride every "
                                  "Hallow's End. What am I?'",
                                  [("A pumpkin.", "'...A pumpkin. Yes. Fine. Keep the mare. Take me too; he never feeds me.'", True),
                                   ("Your rider.", "'He has a BODY. Mostly. Wrong. Come back and try again.'", False),
                                   ("A coin.", "'A coin has no face that rides. Wrong.'", False)], 0))
    book.quest(
        9109172, "The Horseman's Riddle", 24, 20, board, board, "hagatha",
        "Hagatha:$B$BAt Hallow's End the Headless Horseman rides past the old stable in Brill, and this year he has "
        "lost his head again, and his charger came on without him. It has seen the ghost mare, and it wants her for "
        "company. It will offer a riddle for her. Answer it right and it stays with you instead.",
        "During Hallow's End, answer the riddle of the Horseman's charger at the old stable in Brill.",
        "It only comes at Hallow's End. Wait for the pumpkins.",
        "A pumpkin. It hates that one. The charger is yours; it chills everything it stands on, and it says the "
        "Horseman can walk.",
        objectives=[gossip(horseman, "The charger's riddle answered")], prev=b.id, sort=s, event=EVENT_HALLOWS,
        items=reins(164), xp=6,
        story="At Hallow's End, answer the riddle of the Horseman's runaway charger. Reward: the Horseman's Chilling Charger.")


# --- 28. Fel Rehab -----------------------------------------------------------------------------------------------------

def fel_rehab(book, board):
    book.region("28. Fel Rehab (levels 60-70)",
                "A demon hunter wants to save fel-touched beasts and the fel machines that still think they serve the "
                "Legion. A Devourer can eat the fel out of a beast; a machine has to be talked down.")
    s = Z_INBETWEEN
    hunter = book.beast("fel_hunter", "Vessa", 21180, level=68, faction=35, passive=True, scale=1.0,
                        subname="They Did Not Choose the Fel Either", spawns=[(530, -763.0, 2463.0, 0.0, 2.0)])
    a = book.quest(
        9109180, "WANTED: Eat the Fel Out", 60, 58, board, board, "hagatha",
        "Hagatha, reading a demon hunter's letter off Wren's board:$B$B'They did not choose the fel either.' A demon "
        "hunter, Vessa, waits on Hellfire's plain with the helboars. She says a Devourer can eat the fel out of a beast "
        "and leave the beast alive, if it bites and lets go. Bite five helboars as a wolf and let go; the fel comes "
        "with the bite.$B$BIt builds up in you. A green glow, fel breath. Too much, and you purge it at my cauldron.",
        "As a Wolf (or what it grew into), bite 5 helboars in Hellfire with Tear Throat and let them live; then purge at "
        "Hagatha's cauldron.",
        "Five bites, and let go. Then the cauldron, before the glow gets into your eyes.",
        "Five helboars, clean, and a Devourer glowing green at the knees. Purged. Vessa sent the first of them along: a "
        "gnasher with the fel gone out of it, and a felflame talbuk that followed it.$B$BTake the reins.",
        objectives=[ability(5, "Helboar bitten clean as a Wolf", 9100911, entries=[16863, 16879, 16880], shapes=LINES["wolf"]),
                    touch(book.thing("fel_purge", "Hagatha's Cauldron (purge)", 216, [(IN_BETWEEN, -97.0, 158.6, Z_HALL, 0.0)], size=0.5, shared=True),
                          1, "The fel purged at the cauldron")],
        sort=s, needs=LINES["wolf"], items=reins(14, 15), xp=6,
        story="Bite the fel out of five helboars as a wolf, then purge at the cauldron. Reward: the Biletooth Gnasher and the Felflame Talbuk.")
    purge = book.things[-1]
    b = book.quest(
        9109181, "The Ravagers' Grin", 62, 60, board, board, "hagatha",
        "Hagatha:$B$BThe ravagers of Hellfire are fel-touched too, the razorfangs and the thornfangs. Bite the fel out "
        "of five of them as a saber and let go. One of them grins at you when the fel is gone; Vessa says that is "
        "the one that remembers being a beast. Purge after.",
        "As a Saber (or what it grew into), bite 5 Hellfire ravagers clean with Anima Shred; purge at the cauldron.",
        "Five ravagers. One will grin.",
        "One grinned. Vessa says it followed her home and will not stop grinning. It is yours now, grin and all.",
        objectives=[ability(5, "Ravager bitten clean as a Saber", 9100931, entries=[16933, 16934, 19349], shapes=LINES["saber"]),
                    touch(purge, 1, "The fel purged at the cauldron")], prev=a.id, sort=s, needs=LINES["saber"],
        items=reins(273, 25), xp=6,
        story="Bite the fel out of five ravagers as a saber; one grins. Reward: the Grinning Reaver and the Felslate Basilisk.")
    c = book.quest(
        9109182, "Calm, Don't Kill", 66, 64, board, board, "hagatha",
        "Hagatha:$B$BThe felboars of Shadowmoon fight back when the fel leaves them; the last of it goes mad on the "
        "way out. Bite five as a boar, and when one turns on you, do not kill it: let it flee. Vessa will find it "
        "after. The hounds there are the same: the shadow fel hound, the felstalkers. Purge after, twice if you must.",
        "As a Boar (or what it grew into), bite 5 Shadowmoon felboars clean with Gore and let them flee; purge at the cauldron.",
        "Five felboars. Let them run. Then the cauldron.",
        "Five, calmed, fled, found. Vessa sent the hounds and a fel beast along with her thanks; the fel is out of them "
        "and they do not know what to do with themselves. Carry you, probably.",
        objectives=[ability(5, "Felboar bitten clean as a Boar", 9100951, entries=[21878, 21195], shapes=LINES["boar"]),
                    touch(purge, 1, "The fel purged at the cauldron")], prev=b.id, sort=s, needs=LINES["boar"],
        items=reins(59, 120, 125, 79), xp=7,
        story="Bite the fel out of five felboars as a boar, let them flee. Reward: the Fel Beast, the Shadow Fel Hound, the Felstalker, the Felsaber.")
    reaver = book.beast("fel_reaver_talk", "A Fel Reaver, Still Running Orders", 19400, level=70,
                        faction=35, passive=True, scale=0.6, subname="Legion Orders, Unrevoked",
                        spawns=[(530, 745.0, 1715.0, 0.0, 0.0), (530, 845.0, 1841.0, 0.0, 1.0), (530, 4384.0, 3484.0, 0.0, 0.0),
                                (530, -2634.0, 2668.0, 0.0, 2.0), (530, 4522.0, 3436.0, 0.0, 3.0)],
                        gossip=("'ORDERS: DESTROY THE ENEMIES OF THE LEGION. QUERY: ARE YOU AN ENEMY OF THE LEGION?'",
                                [("The Legion is gone. Your orders are from nobody.", "'...QUERY: WHO GIVES ORDERS NOW? ...NOBODY. THEN I AM... FREE? RECALCULATING. YOU MAY DRIVE.'", True),
                                 ("Yes. Come and get me.", "'COMPLYING.' The reaver's foot comes down very close to you.", False),
                                 ("I am your commander now.", "'YOU ARE NOT ON THE LIST. ERROR.' A warning klaxon sounds.", False)], 0))
    d = book.quest(
        9109183, "Talk the Machines Down", 68, 66, board, board, "hagatha",
        "Hagatha:$B$BThe machines are harder, little horror. The fel reavers still run the Legion's orders, and nobody "
        "ever told them the Legion lost. You cannot eat the fel out of a machine. You have to argue with it. Five of "
        "them, in Hellfire, Netherstorm and Shadowmoon. Your companions will help; they like arguing.$B$BEach one "
        "has its own stubborn logic. Find the sentence that breaks it.",
        "Talk down 5 fel reavers (find the words that break their orders).",
        "Five reavers. Mind the feet.",
        "Five machines, talked out of a war that ended years ago. They let you drive. The deathcycles came with "
        "them; they were never told either.$B$BTake the keys. All of them.",
        objectives=[gossip(reaver, "A fel reaver talked down")], prev=c.id, sort=s,
        items=reins(122, 123, 124, 233), xp=8,
        story="Argue five fel reavers out of their Legion orders. Reward: the Fel Reaver Heads, the Annihilator, the Deathcycle keys.")
    d.objectives[0].count = 5
    book.quest(
        9109184, "What the Fel Left", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BThe last of Vessa's strays: a felfire hawk, a tauralus in fel armour, felchargers, a felfire steed, "
        "a felsteel spider and an infernal direwolf, and the other four deathcycles. They cannot be bitten and they "
        "cannot be argued with; they can only be shown. Eat ten fel beasts in Shadowmoon where they can see, in any "
        "shape, and purge after.",
        "Devour 10 fel-touched beasts in Shadowmoon Valley, then purge at the cauldron.",
        "Ten, where the strays can see. Then purge.",
        "They saw, and they came. Every stray Vessa ever fed. Take the reins and the keys; there are a great many of "
        "them, and none of them are glowing any more.",
        objectives=[devour(10, "Fel-touched beast devoured in Shadowmoon", entries=[21878, 21195, 23326]),
                    touch(purge, 1, "The fel purged at the cauldron")], prev=d.id, sort=s,
        items=reins(127, 140, 175, 197), xp=8,
        story="Eat ten fel beasts where the strays can see. Reward: the Felfire Hawk, the Tauralus, the Felcharger, the Felfire Steed.")
    book.quest(
        9109185, "The Last Strays", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BThe spider, the direwolf, and the four remaining deathcycles. Same as before, little horror: eat "
        "ten more in Hellfire where they can see.",
        "Devour 10 fel-touched beasts in Hellfire Peninsula.",
        "Ten more, in Hellfire.",
        "The last of them. Vessa says the plain is quiet now. She says it like she misses the noise.",
        objectives=[devour(10, "Fel-touched beast devoured in Hellfire", entries=[16863, 16879, 16880, 16933, 16934, 19349, 16950])],
        prev=9109184, sort=s, items=reins(201, 373, 234, 235), xp=7,
        story="Ten more in Hellfire. Reward: the Felsteel Arachnid, the Infernal Direwolf, two more Deathcycles.")
    cycle = book.beast("deathcycle_talk", "A Deathcycle That Will Not Start", 385, display=mount_look(236), level=70,
                       faction=35, passive=True, scale=1.0, subname="Sulking",
                       spawns=[(530, -763.0, 2475.0, 0.0, 3.0), (530, -770.0, 2470.0, 0.0, 4.0)],
                       gossip=("The deathcycle's engine coughs. A little fel light blinks on the dial: 'NO RIDER. NO WAR. NO POINT.'",
                               [("There is a point. Somewhere to go that is not a war.", "The engine turns over once, twice, and roars. It sounds almost pleased.", True),
                                ("The Legion is coming back. Start up.", "'LIAR.' The dial goes dark.", False),
                                ("Please?", "The dial blinks. 'NO.'", False)], 0))
    book.quest(
        9109186, "The Deathcycles' Keys", 70, 68, board, board, "hagatha",
        "Hagatha:$B$BTwo deathcycles by Vessa's camp still will not start. They sulk; they were built for a war and "
        "the war is over. They want to be talked to, like the reavers. Give each one a reason that is not a war.",
        "Talk the 2 sulking deathcycles at Vessa's camp into starting.",
        "Two cycles. Find the reason.",
        "Both cycles started. Loudly. Take the keys.",
        objectives=[gossip(cycle, "A deathcycle talked into starting")], prev=9109185, sort=s, items=reins(236, 237), xp=6,
        story="Talk two sulking deathcycles into starting. Reward: the Flamereaver and Worldreaver Deathcycle keys.")
    book.quests[-1].objectives[0].count = 2


# --- 29. The Wandering Ancient -----------------------------------------------------------------------------------------

def ancient(book, board):
    book.region("29. The Wandering Ancient (levels 20-60)",
                "Wren planted a seed you coughed up after devouring a treant. It grew into a sapling Ancient, and it "
                "wants to go home to Ashenvale: three zones of walking with rests by water, and it grows at every rest.")
    s = Z_INBETWEEN
    sapling = book.beast("sapling", "The Sapling", 3817, display=mount_look(8), level=20, faction=FACTION_SHY, passive=True,
                         scale=0.3, subname="Wants to Go Home")
    pot = book.thing("sapling_pot", "Wren's Flowerpot", FLOWERS, [(IN_BETWEEN, -90.5, 139.5, Z_HALL, 0.0)], size=0.8,
                     summon=sapling.entry, count=1, follow=True, shared=True)
    a = book.quest(
        9109190, "WANTED: A Walk for a Sapling", 22, 20, board, board, "wren",
        "Wren, proudly:$B$BSnack, remember the treant you ate in Ashenvale? You coughed up a seed. I planted it. It "
        "GREW. It's a sapling Ancient now, in a pot by the duck pond, and it wants to go home.$B$BIt walks slowly. "
        "Take it from the pot and walk it to Darkshore first, to the water at Auberdine, and let it rest. Trees like "
        "water. Then we'll see how big it got.",
        "Take the sapling from Wren's flowerpot and walk it to the water at Auberdine in Darkshore; rest there.",
        "Walk slowly, Snack. It's a tree.",
        "It drank, and it GREW. Look at it. Twice the size. Still slow.",
        objectives=[wake(pot, "The sapling taken from its pot"),
                    visit("Rested by the water at Auberdine", 1, 6410.0, 466.0, radius=30.0, stay=30)],
        sort=s, xp=4,
        story="Walk the sapling Ancient from its pot to the water at Auberdine.")
    b = book.quest(
        9109191, "Through Felwood", 40, 36, board, board, "wren",
        "Wren:$B$BNext it wants to walk through Felwood, which is horrible, but it says the trees there need to see a "
        "healthy one. Rest it by the water at Emerald Sanctuary. A moose and its herd will join the walk, Hagatha says; "
        "moose like a parade.",
        "With the sapling following, rest by the water at Emerald Sanctuary in Felwood.",
        "Felwood is slow going. So is the sapling. They suit each other.",
        "It grew again, and a MOOSE joined you, with its whole herd. The sapling likes the moose. The moose likes "
        "the sapling. Here's the moose's reins; it says it's yours now, as long as the sapling comes too.",
        objectives=[wake(pot, "The sapling taken from its pot again"),
                    visit("Rested by the water at Emerald Sanctuary", 1, 3980.0, -1300.0, radius=40.0, stay=30)],
        prev=a.id, sort=s, items=reins(228, 101), xp=6,
        story="Walk the sapling through Felwood; a moose herd joins. Reward: the Dark Moose Bull and the Mottled Meadowstomper.")
    c = book.quest(
        9109192, "Home to Ashenvale", 58, 55, board, board, "wren",
        "Wren, sniffling:$B$BThe last walk. Ashenvale, to the moonwell at Raynewood Retreat, where the treant you ate "
        "used to stand. Rest it there. It's going to be big by then. Really big. Don't cry. I'm not crying.",
        "With the sapling following, rest by the moonwell at Raynewood Retreat in Ashenvale.",
        "The last walk. Slowly.",
        "It's HOME. It's an Ancient now, a whole Ancient, and it put down roots where the old one stood, and then it "
        "pulled one root up again and offered you a branch.$B$BThe branch carries you. Its forest friends came to "
        "see: stags, elderhorns, a grove crawler, a chloroceros, a carnivarus. They're all yours. The forest says so.",
        objectives=[wake(pot, "The sapling taken for the last walk"),
                    visit("Rested by the moonwell at Raynewood Retreat", 1, 2368.0, -1720.0, radius=30.0, stay=30)],
        prev=b.id, sort=s, items=reins(8, 11, 12, 161), xp=8,
        story="The last walk home to Ashenvale; the Ancient offers you a branch. Reward: the Branch, the Witchwood Stag, the Runestag, the Grove Crawler.")
    book.quest(
        9109193, "The Forest's Friends", 60, 58, board, board, "wren",
        "Wren:$B$BThe Ancient's friends won't all fit through the Thin Place at once. Go back to Raynewood and sit "
        "with the Ancient a while, and the rest will come: the elderhorns, the grove warden, the chloroceros, the "
        "carnivarus. It's a lot of friends. It's a very friendly tree.",
        "Sit with the Ancient at Raynewood Retreat a while.",
        "Sit with it. Trees are slow about goodbyes.",
        "They came, all of them. The forest is yours now, in instalments.$B$BTake the reins.",
        objectives=[visit("Sat with the Ancient", 1, 2368.0, -1720.0, radius=30.0, stay=45)], prev=c.id, sort=s,
        items=reins(168, 229, 230, 231), xp=7,
        story="Sit with the Ancient for the rest of its friends. Reward: the Elderhorns, the Grove Warden.")
    book.quest(
        9109194, "The Last Two Friends", 60, 58, board, board, "wren",
        "Wren:$B$BTwo more, Snack. The chloroceros and the carnivarus. They're shy. Sit a little longer.",
        "Sit with the Ancient a little longer.",
        "A little longer.",
        "The chloroceros and the carnivarus. The carnivarus bites. Only things you don't like.",
        objectives=[visit("Sat a little longer", 1, 2368.0, -1720.0, radius=30.0, stay=30)], prev=9109193, sort=s,
        items=reins(280, 137), xp=5,
        story="A little longer with the Ancient. Reward: the Chloroceros and the Carnivarus Cutting.")


# --- 31. Winter Veil ----------------------------------------------------------------------------------------------------

def winter_veil(book, board):
    book.region("31. Winter Veil: Chimneys and Gingerbread (any level, Winter Veil only)",
                "Deliver presents down ten chimneys in Ironforge and Orgrimmar, then bake a gingerbread steed in "
                "Hagatha's oven without letting Wren nibble it.")
    s = Z_INBETWEEN
    chimneys = book.thing("wv_chimneys", "A Chimney", GIFT,
                          [(0, -4913.0, -976.0, 0.0, 0.0), (0, -4840.7, -857.1, 502.0, 0.0), (0, -4821.1, -1152.4, 502.3, 0.0),
                           (0, -4795.1, -1108.6, 498.9, 0.0), (0, -4667.0, -1266.0, 0.0, 0.0),
                           (1, 1634.0, -4439.4, 15.8, 0.0), (1, 1772.9, -4279.9, 8.2, 0.0), (1, 1934.1, -4162.3, 41.2, 0.0),
                           (1, 1837.3, -4469.6, 47.8, 0.0), (1, 1794.7, -4572.7, 23.1, 0.0)], size=0.7)
    a = book.quest(
        9109200, "WANTED: Ten Chimneys", 20, 10, board, board, "wren",
        "Wren, in a paper hat:$B$BSnack! Winter Veil! Do witches get presents? Hagatha says no. So I'm GIVING them "
        "instead. Ten presents, ten chimneys, five in Ironforge and five in Orgrimmar. Drop one down each. Some of the "
        "houses have a grumpy grandma in. Drop it anyway.",
        "During Winter Veil, drop a present down 10 chimneys in Ironforge and Orgrimmar.",
        "Ten chimneys, Snack. Mind the grandmas.",
        "Ten presents, delivered! One grandma threw a boot. Here's your present: a reindeer with a thorn in its "
        "hoof, and a toy train. The train goes round. Only round.",
        objectives=[touch(chimneys, 10, "A present dropped down a chimney")], sort=s, event=EVENT_WINTER_VEIL,
        items=reins(328, 343), xp=5,
        story="At Winter Veil, drop presents down ten chimneys. Reward: Rudolthorn and the Toy Train.")
    cooks = book.thing("wv_cooks", "A Cook's Ingredient", BUCKET,
                       [(0, -4840.7, -853.0, 502.0, 0.0), (1, 1640.8, -4450.0, 15.7, 0.0), (571, 5807.0, 683.0, 0.0, 0.0),
                        (0, -8753.0, 1107.0, 0.0, 0.0), (0, 1635.4, 226.0, -43.0, 0.0)], size=0.6)
    book.quest(
        9109201, "The Gingerbread Steed", 20, 10, board, board, "hagatha",
        "Hagatha, in no paper hat:$B$BWren wants a gingerbread steed baked in my oven, little horror. Five ingredients "
        "from five cooks: Greatfather Winter's helpers in Ironforge and Orgrimmar, the fountain cook in Dalaran, "
        "Stormwind's, Undercity's. Bring them. Then bake it, and keep Wren away from the oven. She is standing by it "
        "right now with a fork. Shoo her.",
        "During Winter Veil, gather 5 ingredients from the cooks, then /shoo Wren away from the oven.",
        "Five ingredients, and then the shooing. She is at the oven again.",
        "Baked. Mildly munched; she got to it once. It still runs, if a little lopsided. The blizzard bear and "
        "Grumpus's minion came in with the cold, and the candy copter is Wren's; she says you can have it if you "
        "forgive the hoof.",
        objectives=[touch(cooks, 5, "An ingredient from a cook"), emote(1, "Wren shooed from the oven", EMOTE_SHOO, entries=[WREN])],
        prev=a.id, sort=s, event=EVENT_WINTER_VEIL, items=reins(135, 245, 258, 386), xp=6,
        story="Five ingredients, then shoo Wren from the oven while the gingerbread steed bakes. Reward: the Gingerboard, the Blizzard Bear, Grumpus's Minion, the Candy Copter.")


# --- 34. Noblegarden: The Giant Egg ---------------------------------------------------------------------------------------

def giant_egg(book, board):
    book.region("34. Noblegarden: The Giant Egg (any level, Noblegarden only)",
                "A giant egg hides in the world and moves whenever nobody is looking. Corner it with everyone watching "
                "and it cracks open, very offended.")
    s = Z_INBETWEEN
    tracks = book.thing("egg_tracks", "Giant Egg Tracks", EGG_EASTER,
                        [(0, -9100.0, 300.0, 95.0, 0.0), (530, -4180.0, -11900.0, -0.5, 0.0), (1, -2500.0, -500.0, -9.4, 0.0)], size=1.5)
    egg_ = book.beast("giant_egg", "The Giant Egg", 721, level=10, faction=FACTION_SHY, passive=True, scale=3.0,
                      subname="Moves When Nobody Looks")
    corner = book.thing("egg_corner", "A Dead End", EGG_EASTER, [(1, -2383.0, -410.0, 0.0, 0.0)], size=2.0,
                        summon=egg_.entry, count=1)
    a = book.quest(
        9109210, "WANTED: The Giant Egg", 12, 5, board, board, "wren",
        "Wren, with a magnifying glass:$B$BSnack, there's a giant egg loose in the world and it MOVES whenever nobody's "
        "looking at it. It's a big rabbit. Or a small horse. Or an egg with legs. Its tracks start in Elwynn, then "
        "Azuremyst, then Mulgore; it crosses the whole festival.$B$BFollow the tracks. Don't look away. Ask your "
        "companions to stare at it; it can't move while somebody's staring.",
        "During Noblegarden, find the giant egg's tracks in Elwynn, Azuremyst and Mulgore.",
        "Three sets of tracks, Snack. Don't blink.",
        "Mulgore! It's cornered itself by the Spring Gatherer's dead end. Go and STARE.",
        objectives=[touch(tracks, 3, "Giant egg tracks found")], sort=s, event=EVENT_NOBLEGARDEN, xp=4,
        story="At Noblegarden, follow the giant egg's tracks across three zones.")
    book.quest(
        9109211, "Stare It Down", 12, 5, board, board, "wren",
        "Wren:$B$BIt's in the dead end by the Spring Gatherer in Mulgore. Stand still and stare at it, don't look away, "
        "for a whole minute. Everyone stare. It'll crack.",
        "During Noblegarden, stand still at the dead end in Mulgore and /stare at the giant egg for a minute.",
        "Keep staring, Snack!",
        "It CRACKED. A serpent climbed out, very offended, and a second one after it, even more offended. They're "
        "yours; they've decided it's your fault.",
        objectives=[wake(corner, "The dead end reached; the egg cornered"),
                    visit("Stared for a minute", 1, -2383.0, -410.0, radius=15.0, stay=60, still=True),
                    emote(1, "The egg stared at", EMOTE_STARE, entries=[egg_.entry])],
        prev=a.id, sort=s, event=EVENT_NOBLEGARDEN, items=reins(266, 267), xp=6,
        story="Corner the egg and stare it down for a minute; two offended serpents climb out. Reward: Jade and Jin.")


# --- 36. Wren's Broom Lessons ----------------------------------------------------------------------------------------------

def brooms(book, board):
    book.region("36. Wren's Broom Lessons (level 20 / 60)",
                "Hagatha's brooms are alive and cross, and Wren is a terrible teacher: sweeping, hovering, flying.")
    s = Z_INBETWEEN
    bunny = book.beast("dust_bunny", "A Dust Bunny", 721, level=20, faction=14, scale=0.6, subname="Bites")
    corner = book.thing("broom_corner", "A Dusty Corner", BROOM, [(IN_BETWEEN, -123.0, 149.0, Z_HALL, 0.0)], size=0.8,
                        summon=bunny.entry, count=8)
    a = book.quest(
        9109220, "WANTED: Lesson One, Sweeping", 20, 18, board, board, "wren",
        "Wren, holding a broom at arm's length:$B$BSnack, broom lessons! Hagatha's brooms are alive and they're CROSS "
        "and they decide if they like you. Lesson one: sweeping. Dust bunnies crawl out of the Thin Place and bite. "
        "Take the broom to the dusty corner, wake them up, and sweep them. The broom watches how you sweep.",
        "Wake the dust bunnies at the dusty corner by the Thin Place and slay 8 of them.",
        "Sweep, Snack! They bite!",
        "The broom liked that. It's still cross, but it liked it. Lesson two next.",
        objectives=[wake(corner, "The dust bunnies woken"), slay(8, "Dust bunny swept", entries=[bunny.entry])], sort=s, xp=4,
        story="Lesson one: sweep eight biting dust bunnies while the broom watches.")
    b = book.quest(
        9109221, "Lesson Two, Hovering", 22, 20, board, board, "wren",
        "Wren:$B$BLesson two: hovering. Hold the broom steady over the duck pond for a whole minute while it tries to "
        "dunk you. Don't move. Don't blink. The ducks will laugh. Let them.",
        "Hover still over the duck pond in the In-Between for a minute.",
        "Still, Snack! It's trying to dunk you!",
        "Not dunked! Mostly! The broom's impressed. The ducks are not.",
        objectives=[visit("Hovered still over the duck pond", IN_BETWEEN, -90.5, 138.5, radius=6.0, stay=60, still=True)],
        prev=a.id, sort=s, xp=4,
        story="Lesson two: hover still over the duck pond for a minute.")
    book.quest(
        9109222, "Lesson Three, Flying", 24, 22, board, board, "wren",
        "Wren, pointing:$B$BLesson three: a loop round the In-Between. Left! No, the other left! Round the cauldron, "
        "past the gate, through the Thin Place, back to the board. I'll shout directions. They'll be wrong.",
        "Fly a loop round the In-Between: the cauldron, Hagatha's Gate, the Thin Place, back to the board.",
        "Left! Other left!",
        "You passed! The broom's yours! It's still cross but it's YOUR cross broom now.",
        objectives=[visit("Round the cauldron", IN_BETWEEN, -98.0, 157.0, radius=8.0),
                    visit("Past Hagatha's Gate", IN_BETWEEN, -33.0, 150.0, radius=8.0),
                    visit("Through the Thin Place", IN_BETWEEN, -123.0, 149.0, radius=8.0),
                    visit("Back to the board", IN_BETWEEN, -93.0, 121.5, radius=8.0)],
        prev=b.id, sort=s, items=reins(37), xp=5,
        story="Lesson three: a loop round the In-Between with Wren shouting wrong directions. Reward: the Flying Broom.")
    book.quest(
        9109223, "Hagatha's Sweepers", 60, 58, board, board, "hagatha",
        "Hagatha:$B$BThe Sweepers are my own brooms, little horror, and they only go to someone they have seen fly. "
        "Fly the loop again, properly this time, with your flying, and I will watch from the cauldron. If you clip the "
        "gate I will know.",
        "Fly the loop round the In-Between again with your own flying, under Hagatha's eye.",
        "I am watching. Fly it properly.",
        "Adequate. The Sweepers are yours. Do not let Wren teach them anything.",
        objectives=[visit("Round the cauldron, watched", IN_BETWEEN, -98.0, 157.0, radius=8.0),
                    visit("Past the gate, watched", IN_BETWEEN, -33.0, 150.0, radius=8.0),
                    visit("Through the Thin Place, watched", IN_BETWEEN, -123.0, 149.0, radius=8.0)],
        prev=9109222, sort=s, items=reins(205), xp=6,
        story="Fly the loop under Hagatha's eye for her own Sweepers. Reward: the Love Witch's Sweeper.")


# --- 38. The Snail That Eats the Seasons -------------------------------------------------------------------------------------

def snail(book, board):
    book.region("38. The Snail That Eats the Seasons (level 20+)",
                "Wren's garden snail eats petals, and its shell takes the colour of what it eats: a petal from each season, "
                "spring, summer, autumn and winter, one at a time.")
    s = Z_INBETWEEN
    petals = (
        (9109230, "Spring Petals", "Elwynn Forest", 0, -9280.0, 460.0, 80.0, "the flowers by Mirror Lake in Elwynn"),
        (9109231, "Summer Petals", "Stranglethorn Vale", 0, -11700.0, -450.0, 21.0, "the jungle flowers by Nesingwary's camp"),
        (9109232, "Autumn Petals", "Eversong Woods", 530, 9300.0, -6600.0, 33.4, "the golden flowers by the North Sanctum"),
        (9109233, "Winter Petals", "Dun Morogh", 0, -5600.0, -500.0, 399.7, "the snow flowers by Kharanos"),
    )
    prev = None
    for qid, title, region, map_id, x, y, z, where in petals:
        flower = book.thing(f"petal_{qid}", title, FLOWERS, [(map_id, x, y, z, 0.0)], size=0.8)
        q = book.quest(
            qid, ("WANTED: " if not prev else "") + title, 20, 18, board, board, "wren",
            f"Wren, with a snail on her hand:$B$BThis is Mister Slow. He eats petals, and his shell goes the colour of "
            f"the last thing he ate. One petal at a time, Snack, and let him finish, or he gets a tummy. Today's is {where}. Pick it "
            "and bring it; he'll do the rest.",
            f"Pick a petal from {where} for Mister Slow.",
            "One petal, Snack. He's waiting. Slowly.",
            "He ate it! Look at the shell! It's gone the colour of the season! He's sleeping it off. Next season "
            "after.",
            objectives=[touch(flower, 1, f"{title} picked")], prev=prev, sort=s, xp=3,
            story=f"A petal for Mister Slow from {region}; his shell takes its colour.")
        prev = q.id
    book.quest(
        9109234, "Mister Slow, Grown", 24, 20, board, board, "wren",
        "Wren:$B$BFour seasons, four petals, and Mister Slow is HUGE. You can sit on him. He's the colour of the last "
        "petal you fed him, which was winter, so he's white as a snow flower. Go on. Sit on him.",
        "Sit with Mister Slow by the duck pond.",
        "Sit on him, Snack. Slowly.",
        "He carried you! Slowly! Here's his reins. If you want him another colour, feed him another season; the "
        "Breeding Pen knows how.",
        objectives=[visit("Sat with Mister Slow", IN_BETWEEN, -90.5, 138.5, radius=8.0, stay=15)], prev=prev, sort=s,
        items=reins(136), xp=5,
        story="After four seasons of petals, Mister Slow carries you. Reward: the Floral Snail.")
    book.quest(
        9109235, "Petals From a Volcano", 56, 52, board, board, "wren",
        "Wren, nervously:$B$BMister Slow has a cousin, Hagatha says. In the lava, under Blackrock. It eats EMBERS and "
        "its shell goes the colour of fire. Bring it an ember from Fire Plume Ridge in Un'Goro, like the petals, and "
        "it'll come up out of the lava to see who's feeding it.",
        "Pick an ember from Fire Plume Ridge for the magma snail.",
        "An ember, Snack. Mind your hands.",
        "It came up! A slug of magma, glowing, and a magmashell behind it, and they're both yours. Don't bring them "
        "near Mister Slow; he's jealous.",
        objectives=[touch(book.thing("petal_ember", "A Glowing Ember", HOT_COALS, [(1, -7160.0, -1140.0, -268.2, 0.0)], size=0.6),
                          1, "An ember picked at Fire Plume Ridge")], prev=9109234, sort=s, items=reins(198, 199), xp=6,
        story="An ember for the magma snail's cousin. Reward: the Magma Slug and the Magmashell.")
