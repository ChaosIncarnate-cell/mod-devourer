"""Task 021: the lanterns of the thirties and forties (levels 30-50). Part of tools/devourer_quests_content.py."""

from devourer_quests import devour, slay, LINES
from devourer_quests_content import LANTERN_OPEN
from devourer_quests_teens import onward, BAIT

Z_STV, Z_DUSTWALLOW, Z_ALTERAC, Z_TANARIS, Z_FERALAS, Z_HINTERLANDS = 33, 15, 36, 440, 357, 47
TOAD = LINES["toad"]                          # Biletoad, Giant Marsh Frog, Water Salamander

# Mounts from the mounts thread (tools/mounts/ascension/new_quests.txt); ground, riding 75 at level 20.
SPITEFUL_FROGS = (9304919, "Spiteful Frog pouch (one of six Spiteful Frogs)")
JIGGLESWORTH = (9304079, "Jigglesworth Sr.'s Reins")
GULPERS = (9304917, "Gulper pouch (one of five Gulpers)")
SLIMESABERS = (9304817, "Slimesaber pouch (one of three Slimesabers)")


def thirties(book, twenties):
    stv = book.lantern("stv", "Stranglethorn Vale", 0, -11700.0, -450.0, 21.02, 4.9,
                       "the jungle south-east of Nesingwary's camp")
    dustwallow = book.lantern("dustwallow", "Dustwallow Marsh", 1, -2900.0, -3300.0, 31.69, 3.6,
                              "the marsh north-east of Brackenwall")
    alterac = book.lantern("alterac", "Alterac Mountains", 0, 500.0, -650.0, 167.4, 2.0,
                           "Gallows' Corner, on the road through the mountains")
    tanaris = book.lantern("tanaris", "Tanaris", 1, -7400.0, -3400.0, 14.1, 5.5, "the dunes south-west of Gadgetzan")
    feralas = book.lantern("feralas", "Feralas", 1, -4600.0, 700.0, 48.23, 1.1,
                           "the forest south-west of Camp Mojache")
    hinterlands = book.lantern("hinterlands", "The Hinterlands", 0, 150.0, -2900.0, 112.45, 2.7,
                               "the hills south-east of Aerie Peak")

    book.region("The lanterns of the thirties and forties (levels 30-50)",
                "Six lanterns along the long roads: crocolisks, turtles and owlbeasts on their way to their last "
                "forms, Hagatha's bait for the Stone Fury, Narillasanz and the Oozeworm, and the toad line's own "
                "quests (only a Devourer that owns a toad shape sees them).")

    def onto(key, qid, level, target, line):
        lantern, finale = twenties[key]
        onward(book, qid, level, lantern, target, finale.id, line)

    onto("duskwood", 9105179, 30, stv, "South of the dark woods the jungle begins, and everything in it is green "
                                       "and hungry.")
    onto("wetlands", 9105189, 33, dustwallow, "Take the ship from Menethil to Theramore; the marsh beyond it is "
                                              "older than the Wetlands and wetter.")
    onto("ashenvale", 9105199, 33, dustwallow, "Go south, through the Barrens, to the marsh on the eastern coast.")
    onto("hillsbrad", 9105209, 31, alterac, "Above the hills the mountains are full of things the ogres "
                                            "left alive.")
    onto("stonetalon", 9105219, 28, book_lantern(book, "needles"), "East of the mountains the land drops into "
                                                                   "a canyon full of stone needles.")
    onto("needles", 9105229, 35, dustwallow, "North-east of the canyon the land turns to marsh, and the marsh "
                                             "has a worm I want you to meet.")

    return {
        "stv": (stv, stv_quests(book, stv)),
        "dustwallow": (dustwallow, dustwallow_quests(book, dustwallow, tanaris, feralas)),
        "alterac": (alterac, alterac_quests(book, alterac)),
        "tanaris": (tanaris, tanaris_quests(book, tanaris)),
        "feralas": (feralas, feralas_quests(book, feralas)),
        "hinterlands": (hinterlands, hinterlands_quests(book, hinterlands, stv, alterac)),
    }


def book_lantern(book, key):
    return next(lantern for lantern in book.lanterns if lantern.key == key)


def stv_quests(book, lantern):
    s = Z_STV
    a = book.quest(
        9105230, "Young Hunters of the Vale", 31, 30, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice, heavy with the heat:$B$BIn Stranglethorn the cats grow up fast or not at "
        "all. Young tigers, young panthers, all teeth and no patience. Eat six of them, little horror. Your saber "
        "will learn what it is to be hunted while it hunts.",
        "Devour 6 young tigers or panthers in Stranglethorn Vale.",
        "Six young cats. They are everywhere; so is the heat.",
        "Fast, and foolish, and gone. Your saber is neither now.$B$BTake this.",
        objectives=[devour(6, "Young jungle cat devoured", entries=[683, 681, 682, 736])], sort=s,
        choices=[(33237, "Brogg's Battle Harness"), (4108, "Panther Hunter Leggings"), (33263, "Raptor Eye Ring")],
        story="Hagatha teaches the jungle's young cats: hunted while they hunt.")
    b = book.quest(
        9105231, "Crocolisks of the Vale", 33, 31, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, slow as a river:$B$BThe river crocolisks of the vale, and the snapjaws, and the "
        "saltwater ones on the coast. A komodo that has eaten its way along a whole river is ready for the "
        "southern islands, little horror, where the lizards grow as big as dragons.$B$BEat five.",
        "Devour 5 crocolisks in Stranglethorn Vale.",
        "Five crocolisks. Follow the river.",
        "A whole river in your belly. Your komodo is nearly grown.$B$BTake this.",
        objectives=[devour(5, "Stranglethorn crocolisk devoured", entries=[1150, 1152, 1151])], prev=a.id, sort=s,
        choices=[(33241, "Oiled Leather Leggings"), (6727, "Razzeric's Racing Grips"), (4511, "Black Water Hammer")],
        story="Hagatha's river of crocolisks: the komodo line grows on.")
    c = book.quest(
        9105232, "Mistvale Gorillas", 34, 32, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, howling with laughter:$B$BSnack, there are GORILLAS. They beat their chests and they "
        "throw things! I threw a spoon at Hagatha once and she said it was undignified. Gorillas are undignified "
        "too, so it's fine.$B$BEat four. Beat your chest first. For me.",
        "Devour 4 gorillas in Stranglethorn Vale.",
        "Four gorillas, Snack. Chest-beating optional but encouraged.",
        "Did you beat your chest? I did, from here. Hagatha left the room.$B$BHere!",
        objectives=[devour(4, "Gorilla devoured", entries=[1108, 1114])], prev=b.id, sort=s,
        choices=[(10748, "Wanderlust Boots"), (4114, "Darktide Cape"), (9520, "Silent Hunter")],
        story="Wren wants the chest-beating gorillas of Mistvale.")
    book.quest(
        9105233, "The Spiteful Frogs", 35, 33, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, very excited, for a toad:$B$BSnack, you're a TOAD! Or you can be one. That means you "
        "can do the toad thing: sit in the river looking innocent and then EAT. The vale's rivers are full of "
        "crocolisks and frenzies and little water elementals that think they're the scariest thing in the water.$B$B"
        "Show them. As a toad, or a frog, or your salamander, slay eight of them. I'll send you a friend for it.",
        "As a Biletoad, Giant Marsh Frog or Water Salamander, slay 8 crocolisks, sharptooth frenzies or water "
        "elementals in Stranglethorn Vale.",
        "Eight, Snack. And you have to be a toad when you do it. Those are the rules. I made them up.",
        "The scariest thing in the water! That's you.$B$BAnd here's your friend: a spiteful frog. It's grumpy. "
        "It's big enough to ride. It doesn't like anyone, but it'll like you, because you're also a frog, "
        "sometimes.",
        objectives=[slay(8, "Water creature slain as a toad", entries=[1150, 1152, 1151, 905, 691], shapes=TOAD)],
        prev=a.id, sort=s, needs=TOAD,
        items=[(SPITEFUL_FROGS[0], SPITEFUL_FROGS[1], 1)],
        story="For a Devourer with a toad shape: slay the vale's river creatures as a toad. Reward: a Spiteful Frog "
              "mount.")
    d = book.quest(
        9105234, "Shadowmaw", 38, 36, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and the flame goes black at its heart:$B$BIn the south of the vale, where "
        "the trolls built their temples, there are panthers so dark the trolls named them for the mouth of the "
        "night: shadowmaw. The trolls are gone. The shadowmaws are not.$B$BEat three of them, little horror. A "
        "saber that has eaten the night's mouth hunts in it.",
        "Devour 3 Shadowmaw Panthers in southern Stranglethorn Vale.",
        "The shadowmaws are still in the dark.",
        "Dark, and quiet, and yours.$B$BWren sent you a cat. A large one. A VERY large one, she says, and old, and "
        "very fond of its dinner. She calls him Jigglesworth. You can ride him, if he lets you.",
        objectives=[devour(3, "Shadowmaw Panther devoured", entries=[684])], prev=c.id, sort=s, xp=6,
        items=[(JIGGLESWORTH[0], JIGGLESWORTH[1], 1)],
        choices=[(9630, "Pratt's Handcrafted Boots"), (6788, "Magram Hunter's Belt"), (10703, "Fiendish Skiv")],
        story="Hagatha's tale of the shadowmaw panthers, the night's mouth. Reward: Jigglesworth Sr.")
    return d


def dustwallow_quests(book, lantern, tanaris, feralas):
    s = Z_DUSTWALLOW
    ooze_bait = book.thing("oozeworm_bait", "Hagatha's Bait", BAIT, [(1, -4238.0, -2896.0, 34.2, 0.0)], size=0.7,
                           summon=14237)
    a = book.quest(
        9105240, "Drywallow", 35, 34, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, satisfied:$B$BThe crocolisks of Dustwallow are called drywallow, because even here "
        "they find the driest mud to lie in. Strange, proud beasts. Eat six of them, little horror. Your komodo will "
        "learn to be proud of its own mud.",
        "Devour 6 Drywallow crocolisks in Dustwallow Marsh.",
        "Six drywallows. They lie in the driest mud.",
        "Proud, and now humble, inside you.$B$BTake this.",
        objectives=[devour(6, "Drywallow crocolisk devoured", entries=[4341, 4343, 4344])], sort=s,
        choices=[(4108, "Panther Hunter Leggings"), (4109, "Excelsior Boots"), (9680, "Tok'kar's Murloc Shanker")],
        story="Hagatha teaches the proud drywallow crocolisks.")
    b = book.quest(
        9105241, "Spikeshell", 36, 35, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, slow as a shell:$B$BOld turtles grow spikes because the world kept biting "
        "them. You will understand that, little horror. On the Dreadmurk Shore the mudrock spikeshells have been "
        "bitten so often they are more spike than turtle.$B$BEat five. Your snapjaw is waiting to grow its spikes.",
        "Devour 5 Mudrock Spikeshells on the Dreadmurk Shore in Dustwallow Marsh.",
        "Five spikeshells. Mind your mouth.",
        "Prickly, wasn't it? That is what being bitten too often tastes like.$B$BTake this.",
        objectives=[devour(5, "Mudrock Spikeshell devoured", entries=[4397])], prev=a.id, sort=s,
        choices=[(33237, "Brogg's Battle Harness"), (4430, "Ethereal Talisman"), (4511, "Black Water Hammer")],
        story="Hagatha's tale of the turtle that grew spikes because the world kept biting it (the Spikeshell).")
    c = book.quest(
        9105242, "Noxious Wings", 37, 35, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, holding her nose:$B$BSnack, the wind serpents in the marsh are NOXIOUS. That's their "
        "actual name. Flayers and reavers and shredders, and they smell like old soup. Eat four. Hold your nose. "
        "Can you hold your nose? Depends what you're wearing, I suppose.",
        "Devour 4 noxious wind serpents in Dustwallow Marsh.",
        "Four stinky serpents, Snack.",
        "Phew! Well done. You can breathe again. Can you breathe? Depends what you're wearing.$B$BHere!",
        objectives=[devour(4, "Noxious wind serpent devoured", entries=[4346, 4347, 4348])], prev=b.id, sort=s,
        choices=[(10748, "Wanderlust Boots"), (6727, "Razzeric's Racing Grips"), (33263, "Raptor Eye Ring")],
        story="Wren holds her nose for the noxious wind serpents.")
    book.quest(
        9105243, "The Gulper's Grin", 37, 35, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, plotting:$B$BToad Snack. Toady Snack. The murlocs on the Dreadmurk Shore keep stealing "
        "frogspawn from the marsh and I need you to have a WORD with them. As a toad. A big hungry toad with a big "
        "hungry grin.$B$BEat six Mirefin murlocs while you're wearing your toad, or your frog, or the salamander. "
        "There's a gulper in it for you.",
        "As a Biletoad, Giant Marsh Frog or Water Salamander, devour 6 Mirefin murlocs in Dustwallow Marsh.",
        "Six murlocs, Snack, as a toad. They're still stealing frogspawn.",
        "Grin! Big grin! The frogspawn is safe and you are a hero to frogs everywhere.$B$BHere's a gulper. It's a "
        "frog you can ride, which is the best kind of frog. It grins too.",
        objectives=[devour(6, "Mirefin murloc devoured as a toad", entries=[4359], shapes=TOAD)],
        prev=a.id, sort=s, needs=TOAD,
        items=[(GULPERS[0], GULPERS[1], 1)],
        story="For a Devourer with a toad shape: devour the frogspawn-stealing Mirefin murlocs as a toad. Reward: a "
              "Gulper mount.")
    d = book.quest(
        9105244, "Searing Whelps", 39, 37, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, low:$B$BIn the Dragonmurk and the Wyrmbog in the south of the marsh, the black "
        "dragonflight keeps a nursery. Searing hatchlings, searing whelps. Their mother is a very great and very "
        "wicked dragon, and she will not notice a few gone. Eat five, little horror. Your whelp needs the black's "
        "fire as much as the red's.",
        "Devour 5 searing hatchlings or whelps in southern Dustwallow Marsh.",
        "Five searing whelps. The nursery is in the south.",
        "Black fire in the belly. Your whelp has tasted both colours now.$B$BTake this.",
        objectives=[devour(5, "Searing whelp devoured", entries=[4323, 4324])], prev=c.id, sort=s,
        choices=[(9631, "Pratt's Handcrafted Gloves"), (4549, "Seafire Band"), (11856, "Ceremonial Elven Blade")],
        story="Hagatha sends the Devourer into the black dragonflight's nursery (the whelp line).")
    e = book.quest(
        9105245, "Swamp Oozes", 40, 38, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, fascinated:$B$BSnack, near the crashed zeppelin there are OOZES. Acidic ones and "
        "bubbling ones. They're like soup that walks. I've always wanted to know what walking soup tastes like.$B$B"
        "Eat five. Tell me everything.",
        "Devour 5 swamp oozes near Beezil's Wreck in Dustwallow Marsh.",
        "Five oozes, Snack. The soup is still walking.",
        "Acidic? Bubbly? Both? I'm writing a whole page.$B$BHere!",
        objectives=[devour(5, "Swamp ooze devoured", entries=[4393, 4394])], prev=d.id, sort=s,
        choices=[(9632, "Jangdor's Handcrafted Gloves"), (17778, "Sagebrush Girdle"), (10703, "Fiendish Skiv")],
        story="Wren wants to know what walking soup tastes like: the swamp oozes.")
    f = book.quest(
        9105246, "The Oozeworm", 40, 38, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and the flame shrinks:$B$BIn the Dragonmurk there is a worm so swollen with "
        "ooze that it no longer remembers being a worm. The goblins call it the Oozeworm, when they are brave "
        "enough to call it anything. It comes up rarely and goes down slowly.$B$BI left a bait in the Dragonmurk. "
        "Touch it. Eat what rises. A borer that has eaten the Oozeworm will dig deeper than any worm has dug.",
        "Devour the Oozeworm in the Dragonmurk, Dustwallow Marsh. Hagatha's Bait, in the Dragonmurk, will call it.",
        "The worm is still under the mud. Touch my bait.",
        "Swollen, and slow, and now inside something faster. Your borer will dig.$B$BAnd Wren made something from "
        "what the oozes left behind: a sabercat of living slime. Do not ask me how. You can ride it. It is warm.",
        objectives=[devour(1, "Oozeworm devoured", entries=[14237])], prev=e.id, sort=s, xp=6, lures=[ooze_bait],
        items=[(SLIMESABERS[0], SLIMESABERS[1], 1)],
        choices=[(17776, "Sprightring Helm"), (9647, "Failed Flying Experiment"), (4549, "Seafire Band")],
        story="Hagatha's bait calls the Oozeworm (a Deep Borer task). Reward: a Slimesaber mount.")
    onward(book, 9105248, 41, lantern, tanaris, f.id, "South of the marsh the land dries into sand, and the sand "
                                                     "is full of teeth.")
    onward(book, 9105249, 41, lantern, feralas, f.id, "West of the Barrens the forests of Feralas grow taller than "
                                                     "anything you have eaten.")
    return f


def alterac_quests(book, lantern):
    s = Z_ALTERAC
    fury = book.thing("stonefury_bait", "Hagatha's Bait", BAIT, [(0, 674.3, -997.6, 164.3, 0.0)], size=0.7,
                      summon=2258)
    naril = book.thing("narillasanz_bait", "Hagatha's Bait", BAIT, [(0, 305.2, -1265.5, 50.36, 0.0)], size=0.7,
                       summon=2447)
    a = book.quest(
        9105250, "Mountain Lions of Alterac", 33, 31, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe lions of Alterac are bigger than their cousins in the foothills; the "
        "ogres eat everything smaller. The hulking ones especially. Eat five of them, little horror, and taste a "
        "cat that has learned to be big.",
        "Devour 5 mountain lions in the Alterac Mountains.",
        "Five lions. The big ones, mostly.",
        "Big, and now bigger for being in you.$B$BTake this.",
        objectives=[devour(5, "Alterac mountain lion devoured", entries=[2406, 2407])], sort=s,
        choices=[(33243, "Skirmisher's Cover"), (33250, "Archer's Wristguard"), (33268, "Bone Dirk")],
        story="Hagatha teaches the big cats of Alterac.")
    b = book.quest(
        9105251, "Elemental Slaves", 34, 32, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, angry on someone else's behalf:$B$BSnack, in the crater where Dalaran used to be, the "
        "wizards left elementals TIED UP. Slaves! Of rock and water and whatever! That's horrible. Hagatha says the "
        "kindest thing is to eat them, which is a very Hagatha kind of kindness.$B$BEat four. Kindly.",
        "Devour 4 Elemental Slaves at the Dalaran Crater in the Alterac Mountains.",
        "Four of them, Snack. Kindly.",
        "Free! In a very Hagatha way. I'm going to feel weird about this for a while.$B$BHere.",
        objectives=[devour(4, "Elemental Slave devoured", entries=[2359])], prev=a.id, sort=s,
        choices=[(15456, "Lightstep Leggings"), (33261, "Destroyer's Cloak"), (4978, "Ryedol's Hammer")],
        story="Wren's very Hagatha kindness for the elementals tied up in the Dalaran Crater.")
    c = book.quest(
        9105252, "The Stone Fury", 37, 35, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and the flame grinds like rock:$B$BWhen the Syndicate took Strahnbrad, a "
        "spirit of the mountain rose against them and never lay back down. The Stone Fury, the villagers called it. "
        "It wanders the town now, angry at everything, and is gone again for days.$B$BI left a bait at the edge of "
        "Strahnbrad. Touch it. Eat the fury of a mountain, little horror. A whelp that has eaten stone grows into "
        "an earthen drake.",
        "Devour the Stone Fury at Strahnbrad. Hagatha's Bait, at the edge of the town, will call it.",
        "The fury is still in the mountain. Touch my bait.",
        "A mountain's anger, and now yours. Your whelp may grow scales of stone.$B$BTake this.",
        objectives=[devour(1, "Stone Fury devoured", entries=[2258])], prev=b.id, sort=s, xp=6, lures=[fury],
        choices=[(10702, "Enormous Ogre Boots"), (9705, "Tharg's Shoelace"), (9520, "Silent Hunter")],
        story="Hagatha's bait calls the Stone Fury of Strahnbrad (an Earthen Proto-Drake task).")
    d = book.quest(
        9105253, "Narillasanz", 45, 43, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice, very quiet, the way she speaks of dangerous things:$B$BOn Chillwind Point, "
        "above the lake, a red drake has made its home. Narillasanz. Old enough to remember the orcs who rode its "
        "kin, strong enough that the ogres leave it alone. Come back to me when you are strong enough too.$B$BI "
        "left a bait on the point. Touch it, and it will come. Eat it, little horror, and your drake will be ready "
        "to ride the storm.",
        "Devour Narillasanz on Chillwind Point in the Alterac Mountains. Hagatha's Bait, on the point, will call it.",
        "The drake still sits on its point. Are you strong enough yet?",
        "You were. I knew you would be.$B$BThat was a dragon, little horror. A real one. Your drake has eaten its "
        "elder; the storm is waiting for it.$B$BTake this.",
        objectives=[devour(1, "Narillasanz devoured", entries=[2447])], prev=c.id, sort=s, xp=7, lures=[naril],
        choices=[(19127, "Charred Leather Tunic"), (15822, "Shadowskin Spaulders"), (11863, "White Bone Shredder")],
        story="Hagatha's bait calls Narillasanz, the old red drake of Chillwind Point (a Storm Dragon task).")
    return c


def tanaris_quests(book, lantern):
    s = Z_TANARIS
    a = book.quest(
        9105260, "Blisterpaw", 42, 41, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, fanning herself:$B$BSnack, it's so HOT there the hyenas have blisters on their paws. "
        "Blisterpaws! Poor things. Well, they're also horrible. Eat six. They'll be glad to get off the sand.",
        "Devour 6 Blisterpaw hyenas in Tanaris.",
        "Six blisterpaws, Snack. Their paws still hurt.",
        "No more sore paws! Well. No more paws. Same thing.$B$BHere!",
        objectives=[devour(6, "Blisterpaw hyena devoured", entries=[5425, 5426])], sort=s,
        choices=[(9630, "Pratt's Handcrafted Boots"), (17778, "Sagebrush Girdle"), (11856, "Ceremonial Elven Blade")],
        story="Wren pities the blistered hyenas of the desert.")
    b = book.quest(
        9105261, "Glasshide", 44, 42, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, dry as the dunes:$B$BThe basilisks of the Abyssal Sands ate so much sand "
        "their hides turned to glass. Glasshides, the goblins call them, and do not look into their eyes. Eat five "
        "of them, little horror. A meal that was once a beach.",
        "Devour 5 glasshide basilisks in Tanaris.",
        "Five glasshides. Do not look into their eyes.",
        "Crunchy. Like a beach. Your teeth will forgive you.$B$BTake this.",
        objectives=[devour(5, "Glasshide basilisk devoured", entries=[5419, 5420])], prev=a.id, sort=s,
        choices=[(19041, "Pratt's Handcrafted Tunic"), (17776, "Sprightring Helm"), (11863, "White Bone Shredder")],
        story="Hagatha's glass-hided basilisks of the Abyssal Sands.")
    c = book.quest(
        9105262, "The Sandfury", 44, 42, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and sand hisses in the flame:$B$BThe Sandfury trolls of Zul'Farrak keep a "
        "watch at Sandsorrow, north of here, and pray to a great hydra in their city. Every serpent that sheds long "
        "enough stands up one day and starts to pray, little horror. The sand people began like you.$B$BEat six of "
        "the Sandfury. Your serpent will remember what praying tastes like.",
        "Devour 6 Sandfury trolls at Sandsorrow Watch in Tanaris.",
        "Six Sandfury. They are still praying.",
        "Prayer and sand. Your serpent is closer to standing up.$B$BTake this.",
        objectives=[devour(6, "Sandfury troll devoured", entries=[5645, 5646, 5647])], prev=a.id, sort=s,
        choices=[(10745, "Kaylari Shoulders"), (9657, "Vinehedge Cinch"), (11120, "Belgrom's Hammer")],
        story="Hagatha's tale of the serpent that stands up and prays: the Sandfury trolls (a Sethrak task).")
    d = book.quest(
        9105263, "Rocs", 45, 43, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, gasping:$B$BSnack, the birds in the desert are as big as HOUSES. Rocs! Fire rocs! "
        "Hagatha says an eagle that eats a roc grows into something the sky is afraid of. I'm afraid of it already "
        "and it doesn't exist yet.$B$BEat four rocs.",
        "Devour 4 rocs in Tanaris.",
        "Four rocs, Snack. As big as houses!",
        "You ate four houses! Bird houses! House birds! I'm too excited.$B$BHere!",
        objectives=[devour(4, "Roc devoured", entries=[5428, 5429, 5430])], prev=b.id, sort=s,
        choices=[(15822, "Shadowskin Spaulders"), (19127, "Charred Leather Tunic"), (15703, "Chemist's Smock")],
        story="Wren is frightened of eagles that ate rocs.")
    e = book.quest(
        9105264, "Surf and Steel", 48, 46, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, pleased:$B$BOn the beaches of Tanaris the turtles are as old as the sea. Steeljaw "
        "snappers on the northern beach, surf gliders on Land's End in the south. Eat five, little horror. Your "
        "spikeshell has a long way still to grow, and turtles are never in a hurry.",
        "Devour 5 Steeljaw Snappers or Surf Gliders on the beaches of Tanaris.",
        "Five turtles. They are not in a hurry; neither am I.",
        "Old as the sea. Your shell will be older.$B$BTake this, and go west, into the crater, when you are "
        "ready.",
        objectives=[devour(5, "Tanaris turtle devoured", entries=[14123, 5431])], prev=c.id, sort=s, xp=6,
        choices=[(22274, "Grizzled Pelt"), (20255, "Whisperwalk Boots"), (9651, "Gryphon Rider's Stormhammer")],
        story="Hagatha's sea-old turtles of the Tanaris beaches (the turtle line).")
    return e


def feralas_quests(book, lantern):
    s = Z_FERALAS
    a = book.quest(
        9105270, "Longtooth", 41, 40, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BIn Feralas the wolves have teeth too long for their mouths. Longtooth, "
        "the hunters call them. A wolf that eats its longtooth cousins learns to bite deeper. Eat six.",
        "Devour 6 Longtooth wolves in Feralas.",
        "Six longtooths. Mind their teeth.",
        "Long teeth, short lives. Yours are long enough now.$B$BTake this.",
        objectives=[devour(6, "Longtooth wolf devoured", entries=[5286, 5287])], sort=s,
        choices=[(9633, "Jangdor's Handcrafted Boots"), (9631, "Pratt's Handcrafted Gloves"), (10703, "Fiendish Skiv")],
        story="Hagatha teaches the deep bite of Feralas's longtooth wolves.")
    b = book.quest(
        9105271, "Ironfur", 43, 41, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, impressed:$B$BSnack, the bears in Feralas have fur like IRON. Ironfur bears! Can you "
        "imagine brushing that? I'd break the brush. Hagatha says a bear with iron fur is a bear that's been hit "
        "a lot. Eat five and see if it's true.",
        "Devour 5 Ironfur bears in Feralas.",
        "Five ironfurs, Snack. Bring a big appetite.",
        "Iron fur in your tummy! You're basically armoured now.$B$BHere!",
        objectives=[devour(5, "Ironfur bear devoured", entries=[5268, 5272])], prev=a.id, sort=s,
        choices=[(19042, "Jangdor's Handcrafted Tunic"), (9647, "Failed Flying Experiment"), (4549, "Seafire Band")],
        story="Wren marvels at the iron fur of Feralas's bears.")
    c = book.quest(
        9105272, "Frayfeather", 45, 43, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, thoughtful:$B$BOn the Frayfeather Highlands live the hippogryphs, half bird, half "
        "stag. Their feathers fray at the ends from flying too long. An eagle that eats one learns to fly longer "
        "than its feathers last. Eat four, little horror.",
        "Devour 4 Frayfeather hippogryphs in Feralas.",
        "Four hippogryphs. Look up.",
        "Frayed and tired and now part of something that does not tire.$B$BTake this.",
        objectives=[devour(4, "Frayfeather hippogryph devoured", entries=[5300, 5304, 5305, 5306])], prev=b.id,
        sort=s,
        choices=[(17776, "Sprightring Helm"), (9657, "Vinehedge Cinch"), (11120, "Belgrom's Hammer")],
        story="Hagatha's frayed-feather hippogryphs, for an eagle that wants to fly longer.")
    d = book.quest(
        9105273, "Sprite Darters", 45, 43, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, giggling:$B$BSnack! Fairy dragons! Sprite darters! They're tiny and colourful and "
        "they blink in and out like soap bubbles. Hagatha says they're dragons, technically, so they count for your "
        "whelp. I say they're adorable, so they count for me.$B$BEat four. Adorably.",
        "Devour 4 Sprite Darters in Feralas.",
        "Four sprite darters, Snack. Adorably.",
        "Bubbles! Dragon bubbles! Your whelp says thank you.$B$BHere!",
        objectives=[devour(4, "Sprite Darter devoured", entries=[5278])], prev=b.id, sort=s,
        choices=[(10745, "Kaylari Shoulders"), (15703, "Chemist's Smock"), (11863, "White Bone Shredder")],
        story="Wren's adorable fairy dragons (they count for the whelp line).")
    e = book.quest(
        9105274, "Groddoc", 47, 45, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe great apes of Feralas, the groddoc, beat the ground until it shakes. "
        "Thunderers, the elves call the biggest. Eat four, little horror. There is strength in them the forest "
        "itself respects.",
        "Devour 4 Groddoc apes in Feralas.",
        "Four groddoc. Listen for the thunder.",
        "The forest shook when they fell. It will not shake when you walk now; it will be still.$B$BTake this.",
        objectives=[devour(4, "Groddoc ape devoured", entries=[5260, 5262])], prev=c.id, sort=s, xp=6,
        choices=[(9652, "Gryphon Rider's Leggings"), (19992, "Devilsaur Tooth"), (19159, "Woven Ivy Necklace")],
        story="Hagatha's thundering groddoc apes of Feralas.")
    return e


def hinterlands_quests(book, lantern, stv, alterac):
    s = Z_HINTERLANDS
    a = book.quest(
        9105280, "Silvermane", 43, 41, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, admiring:$B$BThe wolves of the Hinterlands have silver manes, and the dwarves of "
        "Aerie Peak make cloaks of them. Eat six, little horror. A wolf that has eaten silver shines a little, even "
        "in the dark.",
        "Devour 6 Silvermane wolves in the Hinterlands.",
        "Six silvermanes. They shine; you will find them.",
        "Silver in your belly. Shine a little.$B$BTake this.",
        objectives=[devour(6, "Silvermane wolf devoured", entries=[2923, 2924, 2925, 2926])], sort=s,
        choices=[(9632, "Jangdor's Handcrafted Gloves"), (17778, "Sagebrush Girdle"), (11856, "Ceremonial Elven Blade")],
        story="Hagatha's silver-maned wolves of the Hinterlands.")
    b = book.quest(
        9105281, "Owlbeasts of the Hinterlands", 44, 42, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice goes silver:$B$BAn owl that eats enough moonlight becomes a moonkin. A "
        "moonkin that eats enough of the wild becomes an owlbeast, and then it forgets the moon entirely. The "
        "Hinterlands are full of them: vicious, primitive, savage.$B$BEat five. Your moonkin should know what it "
        "could forget.",
        "Devour 5 owlbeasts in the Hinterlands.",
        "Five owlbeasts. They have forgotten the moon; do not let them forget you.",
        "Wild, and moonless. Your moonkin will remember the moon for both of you.$B$BTake this.",
        objectives=[devour(5, "Hinterlands owlbeast devoured", entries=[2927, 2928, 2929])], prev=a.id, sort=s,
        choices=[(19042, "Jangdor's Handcrafted Tunic"), (9647, "Failed Flying Experiment"), (11120, "Belgrom's Hammer")],
        story="Hagatha's tale of the owlbeasts that forgot the moon (the owl line).")
    c = book.quest(
        9105282, "Saltwater Snapjaws", 45, 43, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, waving:$B$BSnack, on the Overlook Cliffs in the south the turtles are SALTY. Saltwater "
        "snapjaws! They live by the sea and they're grumpy about it. Eat five and tell me if they taste like the "
        "sea or like grump.",
        "Devour 5 Saltwater Snapjaws on the Overlook Cliffs in the Hinterlands.",
        "Five salty snapjaws, Snack.",
        "Sea AND grump? Both? Amazing.$B$BHere!",
        objectives=[devour(5, "Saltwater Snapjaw devoured", entries=[2505])], prev=a.id, sort=s,
        choices=[(15822, "Shadowskin Spaulders"), (10745, "Kaylari Shoulders"), (15703, "Chemist's Smock")],
        story="Wren wants to know if the salty snapjaws taste of sea or of grump (the turtle line).")
    d = book.quest(
        9105283, "Jade Oozes", 47, 45, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, collecting jars:$B$BSnack, at Skulk Rock the oozes are GREEN. Jade green! I'm making a "
        "collection: the walking soups of the world. Eat five jade oozes and I'll add them to the list. I have a "
        "list. It's long.",
        "Devour 5 Jade Oozes at Skulk Rock in the Hinterlands.",
        "Five jade oozes, Snack. For the list.",
        "Added to the list! The list now has a page about green.$B$BHere!",
        objectives=[devour(5, "Jade Ooze devoured", entries=[2656])], prev=b.id, sort=s,
        choices=[(19127, "Charred Leather Tunic"), (9657, "Vinehedge Cinch"), (11863, "White Bone Shredder")],
        story="Wren's list of the walking soups of the world: jade oozes.")
    e = book.quest(
        9105284, "Gammerita", 48, 46, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, slow and fond:$B$BOn the Overlook Cliffs there lives a turtle the dwarves "
        "named Gammerita, after an aunt who was also very old and very cross. She has been bitten by everything "
        "that lives on that coast, and she has outlived all of it.$B$BEat her, little horror. A spikeshell that has "
        "eaten Gammerita will outlive you, probably. That is the best thing a shell can do.",
        "Devour Gammerita on the Overlook Cliffs in the Hinterlands.",
        "Gammerita is still cross on her cliffs.",
        "Old and cross and gone at last. The dwarves will tell it for a hundred years.$B$BTake this.",
        objectives=[devour(1, "Gammerita devoured", entries=[7977])], prev=c.id, sort=s, xp=6,
        choices=[(22274, "Grizzled Pelt"), (9652, "Gryphon Rider's Leggings"), (19992, "Devilsaur Tooth")],
        story="Hagatha's tale of Gammerita, the cross old turtle of the cliffs (a Spikeshell task).")
    onward(book, 9105239, 41, stv, lantern, 9105234, "North, past the Wetlands, the hills grow wild and the "
                                                     "owlbeasts forget the moon.")
    onward(book, 9105259, 41, alterac, lantern, 9105252, "East of the mountains the Hinterlands grow wild and the "
                                                         "owlbeasts forget the moon.")
    return e
