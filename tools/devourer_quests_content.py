"""Task 021: the content of the Devourer's quests (tools/devourer_quests.py writes the SQL, header and doc from it).

Every creature, place and reward here was checked against the live world database and the server's map files
(2026-10-05): the creatures are spawned in that region at about the quest's level, the lanterns and objects stand on
dry ground, and the rewards are stock 3.3.5a quest rewards a Devourer can use (leather, its weapons, cloaks, rings).

Voices: Hagatha Hollowmoor tells tales ("little horror"); Wren Hollowmoor makes lists ("Snack").
"""

from devourer_quests import (HAGATHA, WREN, HUMAN, ORC, DWARF, NIGHTELF, UNDEAD, TAUREN, GNOME, TROLL, BLOODELF,
                             DRAENEI, LINES, kill, devour, slay, visit, touch, item)

# Creature families and types (creature_template.family / type)
F_WOLF, F_CAT, F_SPIDER, F_BEAR, F_BOAR, F_CROC, F_CARRION, F_CRAB, F_RAPTOR, F_TALLSTRIDER = 1, 2, 3, 4, 5, 6, 7, 8, 11, 12
F_SCORPID, F_TURTLE, F_BAT, F_HYENA, F_BIRD, F_WINDSERPENT, F_DRAGONHAWK, F_RAVAGER, F_WARPSTALKER = (
    20, 21, 24, 25, 26, 27, 30, 31, 32)
F_SPOREBAT, F_NETHERRAY, F_SERPENT, F_MOTH, F_CHIMAERA, F_DEVILSAUR, F_SILITHID, F_WORM, F_RHINO, F_WASP = (
    33, 34, 35, 37, 38, 39, 41, 42, 43, 44)
T_BEAST, T_DRAGON, T_DEMON, T_ELEMENTAL, T_GIANT, T_UNDEAD, T_HUMANOID = 1, 2, 3, 4, 5, 6, 7

# Zones (AreaTable ids), for the quest log headers
Z_ELWYNN, Z_DUNMOROGH, Z_TELDRASSIL, Z_AZUREMYST, Z_DUROTAR, Z_MULGORE, Z_TIRISFAL, Z_EVERSONG = (
    12, 1, 141, 3524, 14, 215, 85, 3430)

LANTERN_OPEN = "The lantern's flame leans toward you, and "


def breadcrumb(book, qid, title, level, giver, ender, races, text, reward_text, story, prev=None, sort=0):
    return book.quest(qid, title, level, level, giver, ender, "hagatha", text,
                      f"Find Hagatha's Lantern: {ender.where}, {ender.region}.",
                      "The lantern is not lit yet? Then you are not there yet, little horror.",
                      reward_text, prev=prev, races=races, xp=2, sort=sort, story=story)


def build(book):
    home(book)


# --- Homecoming: a lantern in every home region (levels 6-11) --------------------------------------------------------

def home(book):
    elwynn = book.lantern("elwynn", "Elwynn Forest", 0, -9620.0, -560.0, 54.44, 2.4, "south-east of Crystal Lake")
    dunmorogh = book.lantern("dunmorogh", "Dun Morogh", 0, -5620.0, -1100.0, 392.25, 1.2, "the hills east of Kharanos")
    teldrassil = book.lantern("teldrassil", "Teldrassil", 1, 9810.0, 840.0, 1304.01, 3.9, "the woods south-east of Dolanaar")
    azuremyst = book.lantern("azuremyst", "Azuremyst Isle", 530, -4050.0, -12000.0, 1.55, 5.1, "Moongraze Woods")
    durotar = book.lantern("durotar", "Durotar", 1, 300.0, -4500.0, 28.58, 0.7, "the scrub west of Razor Hill")
    mulgore = book.lantern("mulgore", "Mulgore", 1, -2100.0, -900.0, -1.06, 2.0, "the plains north-east of Bloodhoof")
    tirisfal = book.lantern("tirisfal", "Tirisfal Glades", 0, 2500.0, 600.0, 30.68, 4.4, "the glades north-west of Brill")
    eversong = book.lantern("eversong", "Eversong Woods", 530, 8900.0, -6600.0, 33.61, 1.6, "the woods west of the Dead Scar")

    book.region("Homecoming: the lanterns of the home regions (levels 6-11)",
                "After Wren's Apprentice, Hagatha sends the Devourer home: her lantern burns in the region it came "
                "from. Three quests at each lantern teach the local beasts, then point onward.")

    homes = (
        (9105001, HUMAN, elwynn, "Elwynn's"), (9105002, DWARF | GNOME, dunmorogh, "Dun Morogh's"),
        (9105003, NIGHTELF, teldrassil, "Teldrassil's"), (9105004, DRAENEI, azuremyst, "Azuremyst's"),
        (9105005, ORC | TROLL, durotar, "Durotar's"), (9105006, TAUREN, mulgore, "Mulgore's"),
        (9105007, UNDEAD, tirisfal, "Tirisfal's"), (9105008, BLOODELF, eversong, "Eversong's"),
    )
    for qid, races, lantern, owner in homes:
        breadcrumb(
            book, qid, "A Lantern at Home", 6, HAGATHA, lantern, races,
            "You were not born, little horror, you were found. But even a found thing has a place it was found in, "
            f"and the world remembers you there. I have hung one of my lanterns in {lantern.region}, {lantern.where}. "
            "Go back the way Wren brought you and look for its light.$B$BWhen you stand beside it, my sister and I "
            "will hear you. We will tell you what the beasts there taste of.",
            "There you are. The flame knew you before I did.$B$BSit, hungry thing. Your home is full of meals, and "
            "every meal is a lesson.",
            f"Hagatha sends the Devourer home, to her lantern in {lantern.region}.", prev=9101305)

    elwynn_quests(book, elwynn)
    dunmorogh_quests(book, dunmorogh)
    teldrassil_quests(book, teldrassil)
    azuremyst_quests(book, azuremyst)
    durotar_quests(book, durotar)
    mulgore_quests(book, mulgore)
    tirisfal_quests(book, tirisfal)
    eversong_quests(book, eversong)


def elwynn_quests(book, lantern):
    s = Z_ELWYNN
    a = book.quest(
        9105010, "The Wolves of Elwynn", 6, 6, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice comes with it, dry as old paper:$B$BThe wolf was the first shape you wore "
        "outside the ritual, and you wore it badly. A wolf is not teeth, little horror. A wolf is the pack it runs "
        "with. The forests of Elwynn are full of them, mangy and grey and hungry.$B$BEat six of them. Not to kill "
        "them, to know them. Then come back and tell me what they tasted of.",
        "Devour 6 wolves in Elwynn Forest.",
        "Six wolves, I said. I can count your meals, little horror. I can smell them on you.",
        "Fear, mostly. And rabbit. That is the taste of a wolf that runs alone.$B$BTake something for your trouble. "
        "Old things I have kept, and they will fit a shape like yours better than they fit me.",
        objectives=[devour(6, "Elwynn wolf devoured", family=1)], sort=s,
        choices=[(3511, "Cloak of the People's Militia"), (23404, "Padded Running Shoes"), (2218, "Craftsman's Dagger")],
        story="Hagatha wants the Devourer to learn the wolf by eating its kin.")
    b = book.quest(
        9105011, "Wren's Picnic", 8, 7, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice tumbles out of it, all at once:$B$BSnack! Picnic! I'm packing a basket, a pretend "
        "basket, because I can't come, so you're eating for both of us. List! One boar, the rocky kind, with the "
        "grumpy face. One bear, a young one, they're softer. And one spider. Don't make that face, spiders are "
        "crunchy and good for you.$B$BEat them all and tell me which one was best. I'm writing it down!",
        "Devour a Rockhide Boar, a Young Forest Bear and a forest spider in Elwynn Forest.",
        "The basket's still pretend-full, Snack. Boar, bear, spider!",
        "The spider was best, wasn't it? I KNEW it. I'm putting a star next to spider.$B$BHagatha says I have to give "
        "you something useful and not another pretend basket. Here!",
        objectives=[devour(1, "Rockhide Boar devoured", entries=[524]),
                    devour(1, "Young Forest Bear devoured", entries=[822]),
                    devour(1, "Forest or Mine Spider devoured", entries=[30, 43])],
        prev=a.id, sort=s,
        choices=[(6085, "Footman Tunic"), (5617, "Vagabond Leggings"), (3440, "Bonecracker")],
        story="Wren packs a pretend picnic: a boar, a bear and a spider, eaten for both of them.")
    c = book.quest(
        9105012, "Hogger's Last Supper", 10, 9, lantern, lantern, "hagatha",
        LANTERN_OPEN + "the old voice turns slow, the way it does before a tale:$B$BThe Riverpaw gnolls tell of one "
        "of their own who ate so much that the pack could not feed him any more, so they left him at the edge of "
        "the forest, and he ate the edge of the forest instead. They call him Hogger. The farmers call him worse.$B$B"
        "He has been the hungriest thing in Elwynn for a long time. Go to Forest's Edge in the south-west and show "
        "him that he is not.",
        "Devour Hogger at Forest's Edge in Elwynn Forest.",
        "Hogger is still the hungriest thing in Elwynn. That should bother you more than it does.",
        "Now you are the hungriest thing in Elwynn. Do not let it go to your head; it is a very small forest.$B$B"
        "Here. Wren says these are for heroes. I say they are for whoever ate the hero's problem.",
        objectives=[devour(1, "Hogger devoured", entries=[448])], prev=b.id, sort=s, xp=6,
        choices=[(1436, "Frontier Britches"), (1302, "Black Whelp Gloves"), (3581, "Serrated Knife")],
        story="Hagatha's tale of Hogger, the gnoll who ate the edge of the forest; the Devourer eats him.")
    return c


def dunmorogh_quests(book, lantern):
    s = Z_DUNMOROGH
    a = book.quest(
        9105020, "The Cold Pantry", 7, 6, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice crackles through the frost on the glass:$B$BSnack, it's SO cold where you are. "
        "Cold is good for meat, everybody knows that, it keeps. Dun Morogh is basically a big cold pantry. I want "
        "you to taste the pantry. One snow leopard, one of the big ice-clawed bears, and one winter wolf.$B$BChew "
        "properly. Frozen things crack your teeth if you're greedy.",
        "Devour a Snow Leopard, an Ice Claw Bear and a Winter Wolf in Dun Morogh.",
        "Pantry's still full, Snack. Leopard, bear, wolf!",
        "Crunchy? Crunchy. I can hear it in your voice.$B$BHere, Hagatha found these in the cellar. They smell like "
        "dwarves. Everything in the cellar smells like dwarves.",
        objectives=[devour(1, "Snow Leopard devoured", entries=[1201]),
                    devour(1, "Ice Claw Bear devoured", entries=[1196]),
                    devour(1, "Winter Wolf devoured", entries=[1131])], sort=s,
        choices=[(23404, "Padded Running Shoes"), (6085, "Footman Tunic"), (2218, "Craftsman's Dagger")],
        story="Wren calls Dun Morogh a cold pantry: a leopard, a bear and a wolf.")
    b = book.quest(
        9105021, "Stone in the Belly", 8, 7, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, slow and low:$B$BThe trogg is a strange thing to wear, little horror. It "
        "came out of the stone and never forgot it; its skin is half rock, its hunger is all of it. The Rockjaw "
        "troggs dig in Gol'Bolar Quarry, south-east of here, and around the lake beyond.$B$BEat six of them. You will "
        "feel the stone settle in your belly. That weight is the beginning of the trogg's strength.",
        "Devour 6 Rockjaw troggs in Dun Morogh.",
        "Your belly is still light, little horror. Six troggs.",
        "Heavy, is it? Good. A thing that carries stone inside it does not fall over easily.$B$BTake one of these. "
        "Something to wear over the weight.",
        objectives=[devour(6, "Rockjaw trogg devoured", entries=[1115, 1116, 1117, 1118])], prev=a.id, sort=s,
        choices=[(5617, "Vagabond Leggings"), (26051, "2 Stone Sledgehammer"), (4974, "Compact Fighting Knife")],
        story="Hagatha teaches the trogg's stone strength: six Rockjaw troggs.")
    c = book.quest(
        9105022, "The Backbreaker", 11, 10, lantern, lantern, "hagatha",
        LANTERN_OPEN + "the flame sinks low, and Hagatha tells it:$B$BThe dwarves tell of a trogg that gnawed on a "
        "stone giant's toe. It never stopped growing harder. Neither did its hunger. Its children still dig at "
        "Helm's Bed Lake, the biggest of the Rockjaw, the ones the dwarves call Backbreakers.$B$BEat one. One is "
        "enough to show you what your troggs could become.",
        "Devour a Rockjaw Backbreaker at Helm's Bed Lake in Dun Morogh.",
        "The Backbreakers still dig, little horror. One of them, I said.",
        "Now you have tasted what a trogg grows into. Remember it: one day your own stone will crack open and "
        "something like that will crawl out.$B$BWear this until then.",
        objectives=[devour(1, "Rockjaw Backbreaker devoured", entries=[1118])], prev=b.id, sort=s, xp=6,
        choices=[(2036, "Dusty Mining Gloves"), (1436, "Frontier Britches"), (3570, "Bonegrinding Pestle")],
        story="Hagatha's tale of the trogg that gnawed a giant's toe; the Devourer eats a Rockjaw Backbreaker.")
    return c


def teldrassil_quests(book, lantern):
    s = Z_TELDRASSIL
    a = book.quest(
        9105030, "Moonlit Teeth", 6, 6, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice is soft as moss:$B$BThe nightsaber hunts by moonlight and is never seen "
        "until it wants to be. The elves love them. That is the trouble with being loved, little horror: you stop "
        "being careful.$B$BEat six of the great cats of Teldrassil. Learn how quiet a hunter can be.",
        "Devour 6 nightsabers in Teldrassil.",
        "Six cats. They are quiet, but they are not hidden from you.",
        "Quiet, were they? You were quieter. That is the lesson.$B$BThese were left in my lantern by someone who "
        "did not need them any more.",
        objectives=[devour(6, "Nightsaber devoured", entries=[2042, 2043, 2033, 2034])], sort=s,
        choices=[(23405, "Farstrider's Tunic"), (26020, "Shard-Covered Leggings"), (4974, "Compact Fighting Knife")],
        story="Hagatha teaches the quiet of the nightsaber: six of Teldrassil's great cats.")
    b = book.quest(
        9105031, "Pellets and Feathers", 7, 7, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice hoots out of it:$B$BHoo! That's an owl. I do a good owl. Snack, the owls up "
        "there, the strigid ones, they swallow mice whole and then they cough up the bones in a little ball. Isn't "
        "that WONDERFUL? You do the same thing but bigger.$B$BEat five of them. If you're lucky you'll get their "
        "shape too, and then you can hoot back at me.",
        "Devour 5 Strigid owls in Teldrassil.",
        "Hoo? Hoo hoo? That means 'still five owls', Snack.",
        "Did you get the shape? Hoot at me. No? Hoot anyway, it's good practice.$B$BHagatha told me to give you this "
        "and to stop hooting. I'll stop hooting when I'm finished.",
        objectives=[devour(5, "Strigid owl devoured", entries=[1995, 1996, 1997])], prev=a.id, sort=s,
        choices=[(6215, "Balanced Fighting Stick"), (23404, "Padded Running Shoes"), (3511, "Cloak of the People's Militia")],
        story="Wren wants owl pellets: five Strigid owls, and maybe the Owl shape.")
    c = book.quest(
        9105032, "The Queen of Webs", 11, 10, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's tale comes thin and careful, like thread:$B$BIn the Oracle Glade in the north of "
        "the island there is a spider the elves call Lady Sathrah. She eats what the glade's guardians let fall, "
        "and they let a great deal fall. She has grown fat on their kindness and thinks herself a queen.$B$BThere "
        "are no queens to a Devourer, little horror. Only meals with longer names.",
        "Devour Lady Sathrah in the Oracle Glade, Teldrassil.",
        "The queen still sits in her web.",
        "A long name, and in the end only a meal. Remember that when you meet names longer than hers.$B$BTake your "
        "pick. She had no use for them, and neither do I.",
        objectives=[devour(1, "Lady Sathrah devoured", entries=[7319])], prev=b.id, sort=s, xp=6,
        choices=[(1302, "Black Whelp Gloves"), (5327, "Greasy Tinker's Pants"), (3581, "Serrated Knife")],
        story="Hagatha's tale of Lady Sathrah, the spider who thinks herself a queen.")
    return c


def azuremyst_quests(book, lantern):
    s = Z_AZUREMYST
    a = book.quest(
        9105040, "Long Legs on the Isle", 6, 6, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe timberstriders of this island are cousins of the plainstriders of "
        "Mulgore; the draenei did not bring them, they were here before the crash, picking at the moss. A strider "
        "is legs and a beak and a great deal of running away.$B$BEat five. If their shape is not yours yet, it "
        "will be.",
        "Devour 5 timberstriders on Azuremyst Isle.",
        "Five striders, little horror. They run, but not far.",
        "Long legs. You will want them one day, when something bigger than you is hungry.$B$BTake one of these.",
        objectives=[devour(5, "Timberstrider devoured", entries=[17372, 17373, 17374])], sort=s,
        choices=[(26018, "Elekk Handler's Leathers"), (24439, "Savage Leggings"), (4974, "Compact Fighting Knife")],
        story="Hagatha sends the Devourer after the timberstriders, cousins of the plainstrider.")
    b = book.quest(
        9105041, "Root Tea", 8, 7, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice, muffled, like she has her head in a cupboard:$B$BSnack! I'm out of roots. For "
        "tea. Root tea. The roots on your island WALK, which is rude, but it also means you can catch them. Eat "
        "six of the root trappers and I'll brew from whatever's left in your mouth. Don't ask how.$B$BAnd four of "
        "the moongraze deer while you're there. For biscuits.",
        "Devour 6 Root Trappers and 4 Moongraze deer on Azuremyst Isle.",
        "No tea yet, Snack. Roots and deer!",
        "Mm, earthy. Hagatha says it tastes like a boot. Hagatha has never tasted a boot, she's guessing.$B$BHere, a "
        "biscuit. Well. Not a biscuit. Better than a biscuit.",
        objectives=[devour(6, "Root Trapper devoured", entries=[17196]),
                    devour(4, "Moongraze deer devoured", entries=[17200, 17201])], prev=a.id, sort=s,
        choices=[(26024, "Vindicator's Leather Moccasins"), (26020, "Shard-Covered Leggings"), (24343, "The Thumper")],
        story="Wren is out of tea: walking roots and moongraze deer.")
    c = book.quest(
        9105042, "The Moonwing Owlbeasts", 10, 9, lantern, lantern, "hagatha",
        LANTERN_OPEN + "the flame turns the colour of a bruise, and Hagatha tells it:$B$BWhen the draenei ship fell, "
        "its broken crystals poisoned the island's owlbeasts. They gather in the Moonwing Den on Silvermyst Isle, "
        "south-west of here, raving. Madness has a taste, little horror. It is sharp, and it stays.$B$BEat three "
        "of them. One day you will meet owlbeasts that the moon touched instead of the crystals, and you will know "
        "the difference.",
        "Devour 3 owlbeasts at the Moonwing Den on Silvermyst Isle.",
        "Three owlbeasts. Their madness keeps them home; go to them.",
        "Sharp, and it stays. Now you know.$B$BThese came out of the wreck. The draenei will not miss them.",
        objectives=[devour(3, "Moonwing owlbeast devoured", entries=[17186, 17187, 17188])], prev=b.id, sort=s, xp=6,
        choices=[(26021, "Vindicator's Leather Chaps"), (28159, "Undertaker's Gloves"), (26052, "Vindicator's Smasher")],
        story="Hagatha's tale of the owlbeasts the crashed ship drove mad.")
    return c


def durotar_quests(book, lantern):
    s = Z_DUROTAR
    a = book.quest(
        9105050, "Tusk and Gristle", 6, 6, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice is dry as the dust around it:$B$BThe boar of Durotar eats thorns and stones "
        "and anything the orcs leave behind, and it charges at whatever moves. It is not clever. It does not need "
        "to be. Some hungers are like that.$B$BEat six of the mottled boars. Taste how little a boar needs to "
        "think.",
        "Devour 6 mottled boars in Durotar.",
        "Six boars. They come to you if you stand still long enough.",
        "Tough, and not much else. Do not underestimate 'not much else', little horror.$B$BHere.",
        objectives=[devour(6, "Mottled boar devoured", entries=[3099, 3100, 3098])], sort=s,
        choices=[(24439, "Savage Leggings"), (26051, "2 Stone Sledgehammer"), (4947, "Jagged Dagger")],
        story="Hagatha teaches the boar's simple hunger: six mottled boars.")
    b = book.quest(
        9105051, "Scales and Stings", 8, 7, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice, delighted:$B$BSnack, your desert has the BEST snacks. Raptors! Scorpids! "
        "Scorpids are like little crabs that hate you. Eat four raptors and four scorpids and tell me which ones "
        "bite back harder.$B$BI bet scorpids. I've got a whole jar of bets on scorpids.",
        "Devour 4 Bloodtalon raptors and 4 scorpids in Durotar.",
        "Four and four, Snack! I need it for my bet.",
        "Scorpids! I WIN. Hagatha bet raptors. Hagatha has to fold the laundry.$B$BHere's your share of the winnings.",
        objectives=[devour(4, "Bloodtalon raptor devoured", entries=[3122, 3123]),
                    devour(4, "Durotar scorpid devoured", entries=[3125, 3126, 3127])], prev=a.id, sort=s,
        choices=[(5617, "Vagabond Leggings"), (23404, "Padded Running Shoes"), (2218, "Craftsman's Dagger")],
        story="Wren bets on which bites harder: raptors or scorpids.")
    c = book.quest(
        9105052, "The Dreadmaw", 10, 9, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it slow:$B$BThe crocolisks of the Southfury River lie still for days, and the "
        "orcs who water their wolves there forget they are there, and then one day they remember. The Dreadmaw, "
        "they call them. A thing that waits that long is a thing that is very sure of its hunger.$B$BEat two of "
        "them, on the river north of here. Their shape will lie in you like they lie in the water.",
        "Devour 2 Dreadmaw Crocolisks on the Southfury River in Durotar.",
        "They are still lying in the river. Go and remind them.",
        "Patient, wasn't it? That is a crocolisk's whole secret. Some day the patience will grow teeth, and then "
        "more teeth.$B$BTake this, and go north when you are ready.",
        objectives=[devour(2, "Dreadmaw Crocolisk devoured", entries=[3110])], prev=b.id, sort=s, xp=6,
        choices=[(1436, "Frontier Britches"), (28159, "Undertaker's Gloves"), (3570, "Bonegrinding Pestle")],
        story="Hagatha's tale of the patient Dreadmaw crocolisks; their shape is the Baby Komodo's.")
    return c


def mulgore_quests(book, lantern):
    s = Z_MULGORE
    mazz = book.thing("mazz_bait", "Hagatha's Bait", 216, [(1, -1740.0, -545.0, -10.9, 0.0)], size=0.7,
                      summon=3068)
    a = book.quest(
        9105060, "Legs of the Plains", 6, 6, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe tauren say the plainstrider was the Earth Mother's first runner, "
        "sent to carry news across Mulgore before there were tauren to hear it. It still runs, little horror, and "
        "it still has no news.$B$BEat six of the grown ones, the adults and the elders.",
        "Devour 6 plainstriders in Mulgore.",
        "Six striders. They will not stop running for you.",
        "Fast. Stringy. Proud of itself for no reason. A good shape to wear when you need to leave.$B$BTake this.",
        objectives=[devour(6, "Plainstrider devoured", entries=[2956, 2957])], sort=s,
        choices=[(24439, "Savage Leggings"), (26018, "Elekk Handler's Leathers"), (4948, "Stinging Mace")],
        story="Hagatha's plains lesson: six grown plainstriders.")
    b = book.quest(
        9105061, "The Prairie's Teeth", 8, 7, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice, breathless:$B$BSnack, I was reading about Mulgore and it says there are WOLVES "
        "and COUGARS and nobody told me. You could have a wolf shape AND a cat shape. Like hats! Eat four prairie "
        "wolves and three of the flatland cougars and you'll have the whole hat stand.$B$BI'm making you a hat "
        "stand. A real one. Hagatha says no.",
        "Devour 4 prairie wolves and 3 flatland cougars in Mulgore.",
        "Hat stand's still empty, Snack. Wolves and cougars!",
        "Two new hats! If you didn't have them already. If you did, then two very full bellies, which is also "
        "good.$B$BHagatha said no to the hat stand, so here's this instead.",
        objectives=[devour(4, "Prairie wolf devoured", entries=[2958, 2959, 2960]),
                    devour(3, "Flatland cougar devoured", entries=[3035, 3566])], prev=a.id, sort=s,
        choices=[(5617, "Vagabond Leggings"), (23404, "Padded Running Shoes"), (2218, "Craftsman's Dagger")],
        story="Wren wants the Devourer to collect shapes like hats: wolves and cougars.")
    c = book.quest(
        9105062, "Mazzranache", 10, 9, lantern, lantern, "hagatha",
        LANTERN_OPEN + "the flame flickers, and Hagatha tells it:$B$BThe Bloodhoof hunters speak of Mazzranache, a "
        "beast of the plains with no herd and no name of its own; they gave it one so they could curse it. It "
        "wanders, and it does not come when called. Except by me.$B$BI have left a bait in the grass of the Golden "
        "Plains, north-east of Bloodhoof. Touch it, and Mazzranache will come for it. Then eat it. Your striders will "
        "remember the taste when they grow.",
        "Devour Mazzranache in Mulgore. Hagatha's Bait, on the Golden Plains, will call it.",
        "Mazzranache still wanders. Touch my bait, little horror; it is there for you.",
        "A beast with a name it never wanted. Now it has no name at all, only you.$B$BWear this. And when your "
        "plainstrider is ready to grow, remember the taste.",
        objectives=[devour(1, "Mazzranache devoured", entries=[3068])], prev=b.id, sort=s, xp=6, lures=[mazz],
        choices=[(26021, "Vindicator's Leather Chaps"), (1436, "Frontier Britches"), (26052, "Vindicator's Smasher")],
        story="Hagatha's bait calls Mazzranache, the nameless beast of the plains (one of the Greater "
              "Plainstrider's tasks).")
    return c


def tirisfal_quests(book, lantern):
    s = Z_TIRISFAL
    a = book.quest(
        9105070, "Wings in the Gloom", 6, 6, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice is almost fond:$B$BThe duskbats of Tirisfal grew fat on what the plague left "
        "behind. They are blind, little horror, and they need nothing else. They hear your heart. They hear its "
        "hunger.$B$BEat six of them, the greater ones and the vampiric ones. Learn to hear like they do.",
        "Devour 6 duskbats in Tirisfal Glades.",
        "Six bats. Listen for them; they are listening for you.",
        "Did you hear them? A heartbeat, a wing, a breath. That is how a bat sees.$B$BTake this.",
        objectives=[devour(6, "Duskbat devoured", entries=[1553, 1554])], sort=s,
        choices=[(26020, "Shard-Covered Leggings"), (4974, "Compact Fighting Knife"), (23405, "Farstrider's Tunic")],
        story="Hagatha teaches the bat's hearing: six of Tirisfal's duskbats.")
    b = book.quest(
        9105071, "Hounds of the Glade", 8, 7, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice, unusually serious:$B$BSnack, the darkhounds in your glades aren't dogs. "
        "They're something from the other side of the dark that LOOKS like dogs, which is worse. Hagatha says "
        "demons taste like burnt sugar. I want to know if that's true.$B$BEat six of the cursed and ravenous ones "
        "and tell me. For science.",
        "Devour 6 darkhounds in Tirisfal Glades.",
        "Six hounds, Snack. Science is waiting.",
        "Burnt sugar! She was RIGHT. I hate when she's right, she does a little smile.$B$BHere, for science.",
        objectives=[devour(6, "Darkhound devoured", entries=[1548, 1549])], prev=a.id, sort=s,
        choices=[(5617, "Vagabond Leggings"), (6215, "Balanced Fighting Stick"), (23404, "Padded Running Shoes")],
        story="Wren wants to know if demons really taste of burnt sugar: six darkhounds.")
    c = book.quest(
        9105072, "The Scarlet Table", 10, 9, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's tale comes cold:$B$BThe Scarlet Crusade came to Tirisfal to burn the dead. They "
        "have burned a great many things that were not dead yet. They are very sure of themselves, little horror, "
        "and sureness is a flavour. It goes well with fear.$B$BEat five of them, at their farms and their watch "
        "posts around the glades. A bat that drinks the Scarlet's blood grows into something the Scarlet have nightmares "
        "about.",
        "Devour 5 of the Scarlet Crusade in Tirisfal Glades.",
        "Five crusaders. They are easy to find; they shout.",
        "Sure of themselves to the very end. Now you are sure of something too.$B$BTake this, and when your bat is "
        "ready to grow, remember the taste of red.",
        objectives=[devour(5, "Scarlet crusader devoured", entries=[1535, 1536, 1537, 1538, 1539, 1540])],
        prev=b.id, sort=s, xp=6,
        choices=[(1302, "Black Whelp Gloves"), (5327, "Greasy Tinker's Pants"), (3581, "Serrated Knife")],
        story="Hagatha's tale of the Scarlet Crusade; their blood is what a Vampiric Duskbat grows on.")
    return c


def eversong_quests(book, lantern):
    s = Z_EVERSONG
    a = book.quest(
        9105080, "Spilled Magic", 6, 6, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and the flame hums:$B$BWhen the elves spill their magic, something always "
        "laps it up. In the West Sanctum the spill has grown legs: mana stalkers and manawraiths, little "
        "whirlwinds of leftover spell. Your mana wyrm would love them.$B$BEat six. Taste what the elves threw "
        "away.",
        "Devour 6 mana stalkers or manawraiths at the West Sanctum in Eversong Woods.",
        "Six of them. The West Sanctum hums with them.",
        "Sweet and thin, like the elves. That is the taste of magic without anyone holding it.$B$BTake this.",
        objectives=[devour(6, "Spilled magic devoured", entries=[15647, 15648])], sort=s,
        choices=[(28149, "Tranquillien Breeches"), (24439, "Savage Leggings"), (4974, "Compact Fighting Knife")],
        story="Hagatha teaches the taste of spilled magic: six mana stalkers and manawraiths.")
    b = book.quest(
        9105081, "Dragonhawk Down", 8, 7, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice, very fast:$B$BSnack, the elves have DRAGONHAWKS. Little dragons that are also "
        "hawks. That's two snacks in one! The crazed ones are flapping around everywhere and the elves want them "
        "gone, so nobody will mind.$B$BEat six. Is it chicken? Tell me if it's chicken.",
        "Devour 6 Crazed Dragonhawks in Eversong Woods.",
        "Six dragonhawks, Snack! I need to know about the chicken.",
        "Not chicken. 'Spicy hawk.' I'll write that down.$B$BHere, for all the flapping.",
        objectives=[devour(6, "Crazed Dragonhawk devoured", entries=[15650])], prev=a.id, sort=s,
        choices=[(28147, "Tranquillien Scout's Bracers"), (5617, "Vagabond Leggings"), (2218, "Craftsman's Dagger")],
        story="Wren wants to know if dragonhawk tastes like chicken.")
    c = book.quest(
        9105082, "The Wretched Feast", 10, 9, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice is sad and not at all sorry:$B$BThe Wretched were elves who could not stop "
        "drinking magic, and now magic is all they are hungry for. They are like you, little horror, except they "
        "never learned to be anything else. They haunt Sunsail Anchorage and the shore to the west.$B$BEat six. "
        "It is a mercy, of a kind. And a wyrm that eats the Wretched grows into a wraith of pure spell.",
        "Devour 6 Wretched in Eversong Woods.",
        "Six of the Wretched. They will not be missed.",
        "Hungry things eating hungry things. Do not think about it too long.$B$BTake this, and when your wyrm "
        "grows, you will know why I sent you.",
        objectives=[devour(6, "Wretched devoured", entries=[15645, 16162, 15644])], prev=b.id, sort=s, xp=6,
        choices=[(28142, "Farstrider's Belt"), (28157, "Black Leather Jerkin"), (3581, "Serrated Knife")],
        story="Hagatha's tale of the Wretched, elves who could only hunger for magic.")
    return c
