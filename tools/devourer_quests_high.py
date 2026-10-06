"""Task 021: the lanterns of the fifties, Outland and Northrend (levels 49-80). Part of
tools/devourer_quests_content.py."""

from devourer_quests import devour, slay, emote, trail, struck, among, visit, tale, ability, LINES
from devourer_quests_content import mercy, FACTION_SHY, T_DRAGON
from devourer_quests_teens import onward, campfire

Z_UNGORO, Z_WINTERSPRING, Z_BURNING = 490, 618, 46
Z_TEROKKAR, Z_NAGRAND, Z_NETHERSTORM = 3519, 3518, 3523
Z_FJORD, Z_BOREAN, Z_GRIZZLY, Z_SHOLAZAR, Z_STORMPEAKS = 495, 3537, 394, 3711, 67
TOAD = LINES["toad"]
DRAKES = (36, 44)                             # Proto-Drake, Earthen Proto-Drake
STORM_DRAGON = (37,)
EMOTE_SALUTE = 78


def high(book, thirties):
    ungoro = book.lantern("ungoro", "Un'Goro Crater", 1, -6800.0, -1850.0, -272.22, 0.9,
                          "the crater floor north-east of Fire Plume Ridge")
    winterspring = book.lantern("winterspring", "Winterspring", 1, 6500.0, -3500.0, 637.96, 4.2,
                                "the snow below Timbermaw Post")
    burning = book.lantern("burning", "the Burning Steppes", 0, -8100.0, -1800.0, 133.46, 3.1,
                           "the ash fields below the Pillar of Ash")
    terokkar = book.lantern("terokkar", "Terokkar Forest", 530, -2500.0, 4000.0, -3.81, 2.4,
                            "the forest road between Allerian Stronghold and Stonebreaker Hold")
    nagrand = book.lantern("nagrand", "Nagrand", 530, -2200.0, 6700.0, -2.24, 5.0, "the plains near the Ring of Trials")
    netherstorm = book.lantern("netherstorm", "Netherstorm", 530, 3000.0, 3400.0, 105.28, 1.7,
                               "the waste south of Area 52")
    fjord = book.lantern("fjord", "the Howling Fjord", 571, 600.0, -4600.0, 204.51, 3.9, "the hills north of Valgarde")
    borean = book.lantern("borean", "the Borean Tundra", 571, 3000.0, 5300.0, 61.12, 0.6,
                          "the tundra between Valiance Keep and Warsong Hold")
    grizzly = book.lantern("grizzly", "the Grizzly Hills", 571, 3800.0, -3600.0, 231.46, 2.2,
                           "the pines of central Grizzly Hills")
    sholazar = book.lantern("sholazar", "Sholazar Basin", 571, 5300.0, 5200.0, -129.8, 4.4, "the Wildgrowth Mangal")
    stormpeaks = book.lantern("stormpeaks", "the Storm Peaks", 571, 6300.0, -1050.0, 414.59, 1.3,
                              "the Snowblind Hills near K3")

    book.region("The lanterns of the fifties, Outland and Northrend (levels 49-80)",
                "Eleven lanterns for the last forms: the devilsaur and the moon-touched owlbeasts, black dragonkin for "
                "the storm, the warp stalkers and nether rays of Outland, and the proto-drakes, jormungar and storm "
                "wyrms of Northrend. The last lantern ends with both sisters at one campfire.")

    def onto(key, qid, level, target, line, source=thirties):
        lantern, finale = source[key]
        onward(book, qid, level, lantern, target, finale.id, line)

    onto("tanaris", 9105269, 49, ungoro, "West of the desert there is a crater where the world is young and very "
                                         "hungry.")
    onto("feralas", 9105279, 53, winterspring, "Far to the north, past the burning woods, the snow never melts and "
                                               "the owlbeasts are touched by the moon.")
    onto("hinterlands", 9105289, 51, burning, "South of the dwarves' mountains the land burns, and the black "
                                              "dragons keep their children there.")

    found = {
        "ungoro": (ungoro, ungoro_quests(book, ungoro)),
        "winterspring": (winterspring, winterspring_quests(book, winterspring)),
        "burning": (burning, burning_quests(book, burning)),
    }
    for key, qid in (("ungoro", 9105299), ("winterspring", 9105309), ("burning", 9105319)):
        lantern, finale = found[key]
        onward(book, qid, 60, lantern, terokkar, finale.id,
               "There is nothing left in this world that can teach you, little horror. Go through the Dark Portal. "
               "On the other side the world is broken, and broken worlds are very thin.")

    found["terokkar"] = (terokkar, terokkar_quests(book, terokkar))
    onward(book, 9105329, 64, terokkar, nagrand, found["terokkar"][1].id,
           "West of the forest the plains of Nagrand float in a broken sky.")
    found["nagrand"] = (nagrand, nagrand_quests(book, nagrand))
    onward(book, 9105339, 67, nagrand, netherstorm, found["nagrand"][1].id,
           "At the very edge of this world the storm eats the land. You will like it there.")
    found["netherstorm"] = (netherstorm, netherstorm_quests(book, netherstorm))
    onward(book, 9105348, 68, netherstorm, fjord, found["netherstorm"][1].id,
           "Go home and then north, to the cold continent. The fjords there are full of young drakes.")
    onward(book, 9105349, 68, netherstorm, borean, found["netherstorm"][1].id,
           "Go home and then north, to the cold continent. The tundra there is full of old beasts.")
    found["fjord"] = (fjord, fjord_quests(book, fjord))
    found["borean"] = (borean, borean_quests(book, borean))
    onward(book, 9105359, 72, fjord, grizzly, found["fjord"][1].id, "North of the fjord the hills are full of pines "
                                                                    "and wolves and very large bears.")
    onward(book, 9105369, 75, borean, sholazar, found["borean"][1].id, "West of the tundra there is a basin where "
                                                                        "the world is green and very old.")
    found["grizzly"] = (grizzly, grizzly_quests(book, grizzly))
    found["sholazar"] = (sholazar, sholazar_quests(book, sholazar))
    onward(book, 9105379, 77, grizzly, stormpeaks, found["grizzly"][1].id, "North, to the peaks where the storm "
                                                                            "dragons nest. This is the last lantern.")
    onward(book, 9105389, 77, sholazar, stormpeaks, found["sholazar"][1].id, "North-east, to the peaks where the "
                                                                              "storm dragons nest. This is the last "
                                                                              "lantern.")
    found["stormpeaks"] = (stormpeaks, stormpeaks_quests(book, stormpeaks))
    return found


def ungoro_quests(book, lantern):
    s = Z_UNGORO
    fire = campfire(book, "ungoro_fire", lantern, 6.0, 6.0, -272.22, [
        "Sit, both of you. Feel how warm the ground is? The world is still being made here.",
        "Long ago, when there was nothing, there was a pool. Warm, like this, and full of soup.",
        "The soup did not think. It only wanted. It wanted so much that it grew edges, and the edges grew mouths.",
        "That was the first hunger. Everything that has ever eaten anything comes from it.",
        "The oozes in this crater are what is left of that soup. They still only want.",
        "You come from the dark between, little horror, not from the soup. But you are its grandchild, in a way.",
        "Every hunger is."],
        "Bramble stirs the fire with a stick. \"So we're all soup. I knew it. I always felt like soup.\"")
    a = book.quest(
        9105290, "Ravasaurs", 49, 48, lantern, lantern, "hagatha",
        "Hagatha's voice, and somewhere in the flame something roars:$B$BIn the crater the world is young, little "
        "horror, and young worlds are hungry. The ravasaurs hunt the marsh in packs. Eat six of them and taste a "
        "hunger older than any you have met.",
        "Devour 6 ravasaurs in Un'Goro Crater.",
        "Six ravasaurs. They hunt in packs; so can you.",
        "Old hunger, in a young world. It suits you.$B$BTake this.",
        objectives=[devour(6, "Ravasaur devoured", entries=[6505, 6506, 6507, 6508])], sort=s,
        choices=[(15789, "Deep River Cloak"), (12114, "Nightfall Gloves"), (11120, "Belgrom's Hammer")],
        story="The lesson: the young world's old hunger, six ravasaurs.")
    b = book.quest(
        9105291, "Leather Wings", 51, 49, lantern, lantern, "wren",
        "Wren, ducking:$B$BSnack, something with LEATHER WINGS just flew past the lantern. Pterrordax! They're like "
        "bats that went to a lot of trouble. They dive and screech and scare people silly. Take Bramble; she needs to see what I'm "
        "talking about. Eat five before they dive at me again.",
        "With Bramble watching, devour 5 pterrordax in Un'Goro Crater.",
        "Five pterrordax, Snack. One's circling me right now.",
        "No more diving! I can stand up straight again.$B$BHere!",
        objectives=[devour(5, "Pterrordax devoured, Bramble ducking", entries=[9165, 9166, 9167],
                           companion="DUCK! It's coming back! Why do they have TEETH on their WINGS?")], prev=a.id, sort=s,
        choices=[(11874, "Clouddrift Mantle"), (18411, "Spry Boots"), (18400, "Ring of Living Stone")],
        story="Wren ducks the pterrordax: Bramble ducks while you eat five.")
    d = book.quest(
        9105293, "The First Hunger", 52, 50, lantern, lantern, "hagatha",
        "Hagatha speaks, curious despite herself:$B$BI have lit a fire beside the lantern; the ground is warm enough "
        "that it hardly needs one. This crater is where hunger began, little horror. Fetch your little friend, sit, "
        "and I will tell you both where everything comes from.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit. Sit.",
        "Soup, she says. She is not wrong.$B$BTake this.",
        objectives=[tale(fire, "The tale of the first hunger heard")], prev=a.id, sort=s, xp=4,
        choices=[(15825, "Traphook Jerkin"), (21319, "Gloves of the Pathfinder"), (12066, "Shaleskin Cape")],
        story="A campfire tale for the Devourer and Bramble: the warm pool where the first hunger began.")
    book.quest(
        9105294, "Snap!", 52, 50, lantern, lantern, "wren",
        "Wren, whispering a secret:$B$BToad Snack. In the crater there's a frog that lives in the TREES and eats "
        "wasps. I want you to be that frog. As your toad, or your frog, or the salamander, catch eight of the "
        "Gorishi bugs in the south of the crater. Snap! Like that.",
        "As a Biletoad, Giant Marsh Frog or Water Salamander, slay 8 Gorishi silithid in Un'Goro Crater.",
        "Eight bugs, Snack. Snap snap. As a toad!",
        "SNAP! You're the best frog in the crater.$B$BHere, from all the frogs who are scared of wasps.",
        objectives=[slay(8, "Gorishi slain as a toad", entries=[6551, 6552, 6553], shapes=TOAD)],
        prev=a.id, sort=s, needs=TOAD,
        choices=[(15861, "Swiftfoot Treads"), (20649, "Sunprism Pendant"), (12114, "Nightfall Gloves")],
        story="For a Devourer with a toad shape: catch the Gorishi bugs, as a toad.")
    f = book.quest(
        9105296, "You Hear It First", 55, 53, lantern, lantern, "hagatha",
        "Hagatha tells it, and the ground in the flame shakes:$B$BThe devilsaur is the biggest hunger in the crater, "
        "little horror. It does not hide; it does not need to. You hear it before you see it, and you smell it before "
        "you hear it: hot breath and old bones.$B$BTurn on your Sniff by the lantern and follow it south. Let it hit "
        "you, once, so you know what the biggest hunger feels like. Then eat it, and show the crater who is hungriest "
        "now.",
        "Follow the devilsaur's breath with Sniff south of the lantern, let it strike you, then devour a Devilsaur.",
        "The devilsaur still walks. Listen for it. Smell it first.",
        "The biggest hunger in the crater, inside the hungriest thing in the world. I am proud of you, little horror. "
        "Do not tell Wren I said so.$B$BTake this.",
        objectives=[trail("The devilsaur's breath followed", "a Devilsaur", 1,
                          [(-6780, -1935), (-6780, -2040), (-6780, -2145), (-6780, -2220)], summon=6498),
                    struck(1, "The devilsaur's blow felt", entries=[6498]),
                    devour(1, "Devilsaur devoured", entries=[6498])], prev=d.id, sort=s, xp=7,
        choices=[(20715, "Dunestalker's Boots"), (19106, "Ice Barbed Spear"), (22008, "Darkmantle Spaulders")],
        story="Sniff out the devilsaur, the biggest hunger in the crater, take its blow, and eat it.")
    return f


def winterspring_quests(book, lantern):
    s = Z_WINTERSPRING
    a = book.quest(
        9105300, "Shardtooth", 54, 53, lantern, lantern, "hagatha",
        "Hagatha, her breath frosting the glass:$B$BThe bears of Winterspring have teeth like shards of ice. "
        "Shardtooth, the furbolgs call them, and give them room. Eat six, little horror. Cold meat keeps.",
        "Devour 6 shardtooth bears in Winterspring.",
        "Six shardtooths. They are cold; you will warm them.",
        "Cold, and sharp, and now warm inside you.$B$BTake this.",
        objectives=[devour(6, "Shardtooth bear devoured", entries=[7444, 7443, 7445])], sort=s,
        choices=[(15861, "Swiftfoot Treads"), (20649, "Sunprism Pendant"), (16995, "Duskwing Mantle")],
        story="The lesson: the ice-toothed bears of Winterspring.")
    b = book.quest(
        9105303, "Twice the Hats", 55, 53, lantern, lantern, "wren",
        "Wren, impressed:$B$BSnack, the chimaeras in Winterspring have TWO HEADS and they breathe COLD and LIGHTNING. "
        "Two heads! Twice the hats! Take Bramble and let her count the heads while you eat four of the chillwinds. "
        "One head each is still eight heads.",
        "With Bramble counting heads, devour 4 chillwind chimaeras in Winterspring.",
        "Four chimaeras, Snack. Eight heads.",
        "Eight heads! That's a lot of hats I won't be knitting.$B$BHere!",
        objectives=[devour(4, "Chimaera devoured, Bramble counting heads", entries=[7447, 7448, 7449],
                           companion="Two! Four! Six! Eight heads! I'm never going to sleep again.")], prev=a.id, sort=s,
        choices=[(16995, "Duskwing Mantle"), (20649, "Sunprism Pendant"), (18400, "Ring of Living Stone")],
        story="Wren counts the heads of the two-headed chimaeras: Bramble counts the heads while you eat four.")
    book.quest(
        9105302, "Moonlight Cats", 57, 55, lantern, lantern, "hagatha",
        "Hagatha, quiet as falling snow:$B$BOn Frostsaber Rock, in the north-east, the white cats hunt under the moon. "
        "The night elves ride them, when the cats allow it.$B$BWear your saber, little horror, and walk among them on "
        "the rock. They will take you for a cat from the south who has come home. Walk slowly. Let the moon find "
        "you.",
        "Wearing your Saber (or what it grew into), walk among the frostsabers on Frostsaber Rock without starting a "
        "fight.",
        "They are waiting under the moon.",
        "Moonlight and snow. Your saber will remember both, and that the cats of the north let it come home.$B$B"
        "Take this.",
        objectives=[among("Walked among the frostsabers", 1, 7720.0, -4336.0, [7430, 7431, 7432, 7433],
                          LINES["saber"], radius=25.0)],
        prev=a.id, sort=s, needs=LINES["saber"],
        choices=[(15825, "Traphook Jerkin"), (21319, "Gloves of the Pathfinder"), (15708, "Blight Leather Gloves")],
        story="For a Devourer with the Saber shape: walk among the frostsabers of Frostsaber Rock as a cat come home.")
    f = book.quest(
        9105305, "The Moon-Touched", 58, 56, lantern, lantern, "hagatha",
        "Hagatha tells it, and the flame goes white as the moon:$B$BAn owl that eats moonlight becomes a moonkin. A "
        "moonkin that eats the wild becomes an owlbeast. But here, in the snow, the owlbeasts ate so much of the moon "
        "that it touched them back. Moontouched, the furbolgs say, and bow their heads.$B$BThey smell of snow under "
        "moonlight, if you can imagine that. Turn on your Sniff and follow it east, all the way to the Hidden Grove. "
        "Let one call the moon down on you, little horror. Then eat it. Your moonkin has been waiting for this since "
        "the first owl you swallowed.",
        "Follow the moontouched scent with Sniff to the Hidden Grove, let a Moontouched Owlbeast cast Moonfire on you, "
        "then devour it.",
        "The moon-touched still wander the snow. Follow the moonlight.",
        "The moon, in you. Your moonkin will never forget it now.$B$BTake this. You have come a very long way from "
        "the first owl.",
        objectives=[trail("The moontouched scent followed", "a Moontouched Owlbeast", 1,
                          [(6675, -3690), (6810, -3945), (6975, -4200), (7245, -4455), (7500, -4725),
                           (7695, -4920)], summon=7453),
                    struck(1, "The moon felt", entries=[7453]),
                    devour(1, "Moontouched Owlbeast devoured", entries=[7453])], prev=b.id, sort=s, xp=7,
        choices=[(18420, "Bonecrusher"), (21187, "Earthweave Cloak"), (22002, "Darkmantle Belt")],
        story="Sniff out a moon-touched owlbeast at the Hidden Grove, feel its moon, and eat it (Moontouched Owlbeast).")
    return f


def burning_quests(book, lantern):
    s = Z_BURNING
    a = book.quest(
        9105310, "Ember Worgs", 52, 51, lantern, lantern, "hagatha",
        "Hagatha, her voice crackling like coals:$B$BThe worgs of the Burning Steppes sleep in the ash and wake with "
        "embers in their fur. Eat five of them, little horror. A wolf that has eaten fire does not fear it.",
        "Devour 5 ember worgs in the Burning Steppes.",
        "Five ember worgs. Follow the smoke.",
        "Embers in the belly. Your wolf will not flinch from fire again.$B$BTake this.",
        objectives=[devour(5, "Ember worg devoured", entries=[9690, 9694, 9697, 7055])], sort=s,
        choices=[(15789, "Deep River Cloak"), (12114, "Nightfall Gloves"), (11874, "Clouddrift Mantle")],
        story="The lesson: the ember-furred worgs of the Burning Steppes.")
    b = book.quest(
        9105311, "Black Broodlings", 53, 51, lantern, lantern, "hagatha",
        "Hagatha speaks, and the flame darkens:$B$BThe black dragonflight keeps its broods in these ash fields: "
        "broodlings, dragonspawn, wyrmkin, scalding and flamescaled. Wear your whelp, little "
        "horror, and walk in among the broodlings on the Terror Wing Path; they will take you for a cousin from a "
        "colder nest. Then eat six of the brood. A drake that eats its own kind grows into a storm.",
        "Wearing your Whelp (or what it grew into), walk among the black broodlings on the Terror Wing Path, then devour 6 black dragonkin in the Burning Steppes.",
        "Six of the black brood, after you have walked among them.",
        "Ash and fire and dragon. Your drake is learning what it will become.$B$BTake this.",
        objectives=[among("Walked among the black brood", 0, -7759.0, -2958.0, [7047, 7048, 7049, 7040],
                          LINES["whelp"], radius=25.0),
                    devour(6, "Black dragonkin devoured", entries=[7047, 7040, 7048, 7049, 7041, 7042, 7043])],
        prev=a.id, sort=s, needs=LINES["whelp"],
        choices=[(11193, "Blazewind Breastplate"), (18411, "Spry Boots"), (18400, "Ring of Living Stone")],
        story="Hagatha sends the Devourer among the black brood: walk among the broodlings as a cousin, then eat six (towards the storm).")
    d = book.quest(
        9105313, "Drakes of the Steppes", 56, 54, lantern, lantern, "hagatha",
        "Hagatha tells it, slow and grim:$B$BAmong the black brood there are drakes, little horror, grown ones with "
        "wings: black drakes, scalding drakes, searscale drakes. They are few and proud and they do not share the "
        "sky.$B$BEat one, and you will see the last thing it saw: the high path where the drakes nest. Go and stand "
        "there, among their shadows. Then eat another. Your drake should meet its elders before it outgrows them.",
        "Devour a drake, go where its last memory shows you, then devour another in the Burning Steppes.",
        "Did you see the path? Go and stand there.",
        "Elders, eaten. Your drake has nothing left to look up to but the storm.$B$BTake this.",
        objectives=[devour(1, "Drake devoured (you see a high path)", entries=[7044, 7045, 7046]),
                    visit("The Terror Wing Path, where they nest", 0, -7759.0, -2958.0, radius=45.0),
                    devour(1, "Black drake devoured", entries=[7044, 7045, 7046])], prev=b.id, sort=s, xp=6,
        choices=[(15861, "Swiftfoot Treads"), (16995, "Duskwing Mantle"), (20649, "Sunprism Pendant")],
        story="Hagatha's proud black drakes: eat one, see the path it nested on, stand there, eat another.")
    book.quest(
        9105314, "The Storm Gathers", 56, 55, lantern, lantern, "hagatha",
        "Hagatha, and the flame flickers like lightning:$B$BYou wear a drake now, little horror. Good. A drake that "
        "eats dragonkin while it wears its own wings gathers the storm in its chest. Wear your proto-drake, or the "
        "earthen one, and eat ten of the black brood. When you breathe out, the sky will answer.",
        "As a Proto-Drake or Earthen Proto-Drake, devour 10 dragonkin in the Burning Steppes.",
        "Ten, little horror. In your drake's own shape.",
        "Do you feel it, behind your ribs? Thunder. The storm is gathering in you.$B$BTake this.",
        objectives=[devour(10, "Dragonkin devoured as a drake", ctype=T_DRAGON, shapes=DRAKES)],
        prev=b.id, sort=s, needs=DRAKES, xp=6,
        choices=[(18420, "Bonecrusher"), (22377, "The Thunderwood Poker"), (22004, "Darkmantle Bracers")],
        story="For a Devourer with a drake shape: eat dragonkin in drake shape and gather the storm (towards the "
              "Storm Dragon).")
    return d


def terokkar_quests(book, lantern):
    s = Z_TEROKKAR
    fire = campfire(book, "terokkar_fire", lantern, 6.0, 6.0, -3.7, [
        "Sit close. I am further away than ever, little horror; this tale comes down a thread.",
        "South of here lies a city of the dead. The draenei buried their own there, in the old way.",
        "Then the world broke, and something hungry came through the cracks and ate the souls before they could leave.",
        "Now the dead walk there, and the living do not go.",
        "Some hungers are only hunger. That one was theft.",
        "You never steal, little horror. You take what is in front of you, and you keep it, and you carry it.",
        "That is the difference between a Devourer and a thief. Never forget it."],
        "Bramble shivers and pulls her cloak tight. \"I'm not going south. I'm staying right here, by the soup.\"")
    a = book.quest(
        9105320, "Timber Worgs", 62, 60, lantern, lantern, "hagatha",
        "Hagatha's voice comes thin, from very far away:$B$BI can barely reach you here, little horror. This world is "
        "broken; my lantern hangs on a thread. Listen anyway. The worgs of this forest are bigger than any in our "
        "world, and their alphas bigger still. Eat six.",
        "Devour 6 timber worgs in Terokkar Forest.",
        "Six worgs. I can hear them through the thread.",
        "Bigger worlds, bigger wolves, bigger you.$B$BTake this.",
        objectives=[devour(6, "Timber worg devoured", entries=[18476, 18477])], sort=s,
        choices=[(31788, "Blacksting Gloves"), (25504, "Pilgrim's Belt"), (25499, "Felblood Band")],
        story="The lesson, down a thread: Terokkar's timber worgs.")
    book.quest(
        9105322, "Blinking", 64, 62, lantern, lantern, "hagatha",
        "Hagatha tells it, and the thread hums:$B$BOut where the world thins, little horror, the warp stalkers blink "
        "in and out of the forest like candle flames. You were born in the dark between. So were they, nearly.$B$B"
        "Wear your warp stalker and walk among the warp hunters in the south of the forest. They will blink at you, "
        "and you will blink back, and they will think you are one of them. Learn how they forget which side of the "
        "dark they belong to.",
        "Wearing your Warp Stalker (or what it grew into), walk among the warp hunters of Terokkar without starting a "
        "fight.",
        "They are blinking in the forest. Go and blink with them.",
        "Dark and cold and familiar. Your warp stalker is ready to forget which side it belongs to.$B$BTake this.",
        objectives=[among("Blinked among the warp hunters", 530, -2794.0, 4495.0, [18464, 18465],
                          LINES["warpstalker"], radius=25.0)],
        prev=a.id, sort=s, needs=LINES["warpstalker"],
        choices=[(27724, "Wild Shoulderpads"), (25487, "Wind Dancer's Pendant"), (25986, "Dreadtusk's Fury")],
        story="For a Devourer with the Warp Stalker shape: blink among the warp hunters as one of them (Void Terror).")
    c = book.quest(
        9105323, "The Theft of Souls", 64, 62, lantern, lantern, "hagatha",
        "Hagatha's voice, thin as thread:$B$BI have lit a fire beside the lantern, as well as I can from here. There "
        "is a city of the dead south of this forest, and you should know why, before you go near it. Bring your "
        "little friend. I want her to hear this too.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit. The thread is thin; do not make me wait.",
        "A Devourer, not a thief. Good.$B$BTake this.",
        objectives=[tale(fire, "The tale of the city of the dead heard")], prev=a.id, sort=s, xp=4,
        choices=[(27731, "Vindicator's Cloak"), (25932, "Cenarion Thicket Jerkin"), (27733, "Warden's Ring of Precision")],
        story="A campfire tale for the Devourer and Bramble: the city of the dead, and why a Devourer is not a thief.")
    d = book.quest(
        9105324, "The Bone Wastes", 65, 63, lantern, lantern, "wren",
        "Wren, whispering:$B$BSnack, in the Bone Wastes the birds eat bones and the scorpids crawl IN the bones. "
        "Bonelashers and bonecrawlers. Take Bramble; she collects bones, she says, for science. Eat four bonelashers and three "
        "bonecrawlers where she can see. Bones bones bones.",
        "With Bramble watching, devour 4 Bonelashers and 3 Scorpid Bonecrawlers in the Bone Wastes.",
        "Four and three, Snack. Bones bones bones.",
        "Bone appetit! I've been saving that one.$B$BHere!",
        objectives=[devour(4, "Bonelasher devoured, Bramble watching", entries=[18470],
                           companion="Can I keep the beak? For science. Bone science."),
                    devour(3, "Scorpid Bonecrawler devoured", entries=[22100])], prev=c.id, sort=s, xp=6,
        choices=[(31729, "Heirloom Signet of Valor"), (31471, "T'chali's Kilt"), (31422, "Heavy Elven Dirk")],
        story="Wren's bone-eating birds and bone-dwelling scorpids: eat them while Bramble collects bones for science.")
    return d


def nagrand_quests(book, lantern):
    s = Z_NAGRAND
    a = book.quest(
        9105330, "Talbuk", 65, 64, lantern, lantern, "hagatha",
        "Hagatha, as if the air were sweeter:$B$BNagrand is the only green left in this broken world, and the talbuk "
        "graze on it as if nothing were wrong. Eat six of them, little horror. Innocence has a taste, and you should "
        "know it before it is gone.",
        "Devour 6 talbuk in Nagrand.",
        "Six talbuk. They graze as if nothing were wrong.",
        "Sweet, wasn't it? Remember it.$B$BTake this.",
        objectives=[devour(6, "Talbuk devoured", entries=[17130, 17131])], sort=s,
        choices=[(31486, "Bear-Strength Harness"), (31482, "Dire Wolf Handler Gloves"), (25927, "Consortium Cloak of the Quick")],
        story="The lesson: the taste of innocence, the grazing talbuk of Nagrand.")
    b = book.quest(
        9105331, "Windrocs", 65, 64, lantern, lantern, "wren",
        "Wren, holding onto her hat:$B$BSnack, the birds in Nagrand are WINDROCS and they're the size of a cart. I'm "
        "holding onto my hat and counting. Eat five before I lose it. The hat, I mean. Five minutes! Then your eagle "
        "can dream big.",
        "Devour 5 windrocs in Nagrand before Wren loses her hat (5 minutes).",
        "Lost the hat! Found it. Again! Five windrocs.",
        "Big dreams, big bird, big Snack!$B$BHere!",
        objectives=[devour(5, "Windroc devoured", entries=[17128, 18220, 17129])], prev=a.id, sort=s, timed=300,
        choices=[(31419, "Living Grove Shoulderpads"), (31660, "Feralfen Skulker's Belt"), (25926, "Nexus-Stalker's Band")],
        story="Wren's cart-sized windrocs: five before Wren loses her hat (5 minutes).")
    d = book.quest(
        9105333, "Voidspawn", 66, 64, lantern, lantern, "hagatha",
        "Hagatha, and the thread trembles:$B$BIn the Spirit Fields, in the south, the void leaks through and takes "
        "shape as it likes: voidspawn, little blots of nothing that hunger. Your voidling began as one of these, "
        "near enough. Wear it, little horror, or what it grew into, and kill five of them in that shape. Let it "
        "remember where it came from.",
        "As a Voidling (or what it grew into), slay 5 Voidspawn in the Spirit Fields of Nagrand.",
        "Five voidspawn, in your void's own shape.",
        "Nothing, eaten. It tastes like home, doesn't it?$B$BTake this.",
        objectives=[slay(5, "Voidspawn slain as a voidling", entries=[17981], shapes=LINES["void"])],
        prev=b.id, sort=s, needs=LINES["void"], xp=6,
        choices=[(31820, "Blessed Signet Ring"), (25616, "Tim's Trusty Helmet"), (27749, "Staff of the Wild")],
        story="Hagatha sends the voidling home: slay five in the void's own shape (the void line).")
    return d


def netherstorm_quests(book, lantern):
    s = Z_NETHERSTORM
    a = book.quest(
        9105340, "Warp Chasers", 67, 66, lantern, lantern, "hagatha",
        "Hagatha, from the very edge of hearing:$B$BAt the edge of this world, the warp chasers run after whatever "
        "the storm throws loose. Eat six of them, little horror. Your warp stalker has nearly forgotten which side of "
        "the dark it belongs to. Help it forget.",
        "Devour 6 warp chasers in Netherstorm.",
        "Six chasers. They chase; you catch.",
        "Forgotten. Good.$B$BTake this.",
        objectives=[devour(6, "Warp chaser devoured", entries=[18884])], sort=s,
        choices=[(30401, "Farahlite Studded Boots"), (31527, "Leafbeard Ring"), (31703, "Nether-Stalker's Blade")],
        story="The lesson: the warp chasers at the edge of the world (the Void Terror line).")
    b = book.quest(
        9105341, "Phase Hunters", 68, 66, lantern, lantern, "hagatha",
        "Hagatha speaks:$B$BThe phase hunters slip between this world and the next as easily as you slip between "
        "shapes, little horror, Take your little friend; she has never seen anything slip between worlds, and she should, once. "
        "Eat five where she can see. Learn how they slip.",
        "With Bramble watching, devour 5 phase hunters in Netherstorm.",
        "Five phase hunters, and Bramble has to see.",
        "Slippery. Now so are you.$B$BTake this.",
        objectives=[devour(5, "Phase hunter devoured, Bramble watching", entries=[18879],
                           companion="Where did it GO? It was right there. Now it's in you. I need to sit down.")], prev=a.id, sort=s,
        choices=[(30362, "Energized Helm"), (30384, "Brightdawn Bracers"), (31414, "Wild Wood Staff")],
        story="Hagatha's phase hunters, who slip between worlds: Bramble watches one slip, then five are eaten.")
    book.quest(
        9105343, "Walk In Like You Belong", 68, 66, lantern, lantern, "wren",
        "Wren, flapping her arms:$B$BSnack, inside the big glass domes there are moths that SHIMMER. The Eco-Dome "
        "Midrealm, north-east of here. The ethereals guard it and they don't like visitors. So don't be a visitor. "
        "Walk in like you live there. No fighting at the door. Then eat four shimmerwings. Catching is eating, for "
        "you.",
        "Walk into the Eco-Dome Midrealm without being in a fight, then devour 4 Shimmerwing Moths there.",
        "Four shimmerwings, Snack. And walk in nicely.",
        "Shimmer shimmer! And nobody even noticed you. You're a natural.$B$BHere!",
        objectives=[visit("Walked into the dome", 530, 3529.0, 3100.0, radius=40.0, quiet=True),
                    devour(4, "Shimmerwing Moth devoured", entries=[20611])], prev=a.id, sort=s,
        choices=[(31532, "Supple Leather Boots"), (31790, "Expedition Pendant"), (30277, "Ripfang Paw")],
        story="Wren's shimmering moths in the eco-dome: walk in like you belong, then eat four.")
    e = book.quest(
        9105344, "Nether Drakes", 69, 67, lantern, lantern, "hagatha",
        "Hagatha tells it, slow:$B$BOn the Celestial Ridge in the north-east, the nether drakes nest: dragons born of a "
        "dragon that tore itself apart. Their scales shift like the storm, and near them the world goes thin as "
        "paper. Feel it, little horror; stand close enough that their presence presses on you. Then eat three. Your "
        "drake has eaten every colour of our world; let it eat one from beyond it.",
        "Feel a nether drake's presence on the Celestial Ridge, then devour 3 nether drakes there.",
        "Three nether drakes. Climb the ridge.",
        "A colour from beyond the world. Your drake will be strange now. Good.$B$BTake this, and go home, and then go "
        "north.",
        objectives=[struck(1, "The nether presence felt", entries=[18877]),
                    devour(3, "Nether drake devoured", entries=[18877])], prev=b.id, sort=s, xp=6,
        choices=[(32869, "Illidari Lord's Tunic"), (32865, "Drake Tamer's Gloves"), (30339, "Protectorate Assassin's Ring")],
        story="Hagatha's nether drakes of the Celestial Ridge: feel their presence, then eat three (the whelp line).")
    book.quest(
        9105345, "Mother of What Answers", 69, 67, lantern, lantern, "hagatha",
        "Hagatha, from the very edge:$B$BYou are the broodmother now, little horror: the mother of what answers when "
        "fools knock on the void's door. The warp chasers at the edge of this world are what came through without "
        "anyone knocking.$B$BWear your broodmother. Tear six of them with your mandibles, and let the storm see what "
        "the dark between can grow into.",
        "As a Voidcreeper Broodmother, tear 6 Warp Chasers in Netherstorm with Rending Mandibles.",
        "Six chasers, little horror, torn properly.",
        "The storm saw. It will think twice before it throws anything else loose.$B$BTake this.",
        objectives=[ability(6, "Warp Chaser torn as a Broodmother", 9102271, entries=[18884], shapes=(43,))],
        prev=a.id, sort=s, needs=(43,),
        choices=[(30362, "Energized Helm"), (30384, "Brightdawn Bracers"), (31414, "Wild Wood Staff")],
        story="For a Devourer with the Voidcreeper Broodmother: Rending Mandibles on six Warp Chasers.")
    return e


def fjord_quests(book, lantern):
    s = Z_FJORD
    fire = campfire(book, "fjord_fire", lantern, 6.0, 6.0, 204.1, [
        "Ah. I can hear you clearly again. Sit, both of you. This land is cold, but it is ours.",
        "Before the Titans came, the dragons were wild. No colours, no flights, no names. Just wings and hunger.",
        "Then the Titans tidied them. Gave them colours and duties and long, proud names.",
        "Some dragons hid from the tidying. Their children are the proto-drakes, north of here, in the Ember Clutch.",
        "Wild, hungry, and proud of it. They never got their colours. They never wanted them.",
        "You never got tidied either, little horror. Nobody will ever give you a colour.",
        "Good. Stay wild."],
        "Bramble grins into the fire. \"Wild. I like wild. Wild and with biscuits.\"")
    a = book.quest(
        9105350, "Shoveltusk", 69, 68, lantern, lantern, "hagatha",
        "Hagatha, her voice strong again:$B$BAh. I can hear you clearly. This land is cold, little horror, but it is "
        "ours. The shoveltusk dig in the snow for moss and do not look up. Eat six of them. Warm yourself.",
        "Devour 6 shoveltusk in the Howling Fjord.",
        "Six shoveltusk. They are digging; dig them up.",
        "Warm now? Good.$B$BTake this.",
        objectives=[devour(6, "Shoveltusk devoured", entries=[23690, 23691, 29479])], sort=s,
        choices=[(37355, "Reinforced Caribou-Hide Chestguard"), (37387, "Charred Treads"), (36879, "Soldier's Spiked Mace")],
        story="The lesson: Hagatha warms the Devourer with the shoveltusk of the fjord.")
    b = book.quest(
        9105351, "Untidied", 69, 68, lantern, lantern, "hagatha",
        "Hagatha, warm as a hearth:$B$BI have lit a fire beside the lantern. Fetch your little friend. Before you go "
        "to the Ember Clutch, there is a tale about the wild dragons I want you both to hear.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit. Sit.",
        "Stay wild. Now go and meet the ones who did.$B$BTake this.",
        objectives=[tale(fire, "The tale of the untidied dragons heard")], prev=a.id, sort=s, xp=4,
        choices=[(37391, "Rhinohide Mask"), (37383, "Seared Scale Cape"), (37029, "Fin Carver")],
        story="A campfire tale for the Devourer and Bramble: the dragons that hid from the Titans' tidying.")
    book.quest(
        9105352, "A Sibling in the Clutch", 70, 68, lantern, lantern, "hagatha",
        "Hagatha, proud:$B$BIn the Ember Clutch, in the north of the fjord, the proto-whelps hatch in the warm rocks. "
        "Wear your whelp, or your drake, little horror, and walk into the clutch. They will take you for one more "
        "sibling, hatched a little late and a little strange. Lie in the warm rocks with them. You will fit right "
        "in.",
        "Wearing your Whelp (or what it grew into), walk among the proto-whelps of the Ember Clutch without starting a "
        "fight.",
        "The clutch is warm, and waiting for one more.",
        "Wild and hungry and proud, and they took you in. You fit right in, as I said.$B$BTake this.",
        objectives=[among("Lay in the clutch", 571, 953.0, -3678.0, [23688, 23689], LINES["whelp"], radius=25.0)],
        prev=b.id, sort=s, needs=LINES["whelp"],
        choices=[(35914, "Proto-Drake Tooth Spaulders"), (35893, "Coldstone-Inlaid Waistguard"), (35936, "Worg-Fang Talisman")],
        story="For a Devourer with the Whelp shape: lie among the proto-whelps of the Ember Clutch as a late sibling.")
    d = book.quest(
        9105353, "Proto-Drakes", 71, 69, lantern, lantern, "hagatha",
        "Hagatha, proud:$B$BThe grown ones guard the clutch: proto-drakes, little horror, the wild dragons of the "
        "north. There are not many. Let one breathe on you; feel the fire of a dragon nobody tidied. Then eat two, and "
        "let your drake meet what it already is.",
        "Let a Proto-Drake breathe fire or buffet you, then devour 2 Proto-Drakes at the Ember Clutch.",
        "Two proto-drakes, and one breath. They guard the clutch.",
        "Your drake has met itself and eaten it. That is the most a Devourer can do.$B$BTake this.",
        objectives=[struck(1, "Wild fire felt", entries=[23689]),
                    devour(2, "Proto-Drake devoured", entries=[23689])], prev=b.id, sort=s, xp=6,
        choices=[(35815, "Bone-Threaded Harness"), (37380, "Whalehunter Leggings"), (36878, "Writhing Longstaff")],
        story="Hagatha's wild proto-drakes of the Ember Clutch: take the breath, then eat two.")
    return d


def borean_quests(book, lantern):
    s = Z_BOREAN
    a = book.quest(
        9105360, "Wooly Rhinos", 69, 68, lantern, lantern, "hagatha",
        "Hagatha's voice, clear in the cold:$B$BThe rhinos of the tundra wear wool against the wind and horns against "
        "everything else. Eat five of them, little horror, the matriarchs and the bulls.",
        "Devour 5 wooly rhinos in the Borean Tundra.",
        "Five rhinos. They are hard to miss.",
        "Wool and horn. Warm and hard. Both useful here.$B$BTake this.",
        objectives=[devour(5, "Wooly rhino devoured", entries=[25487, 25489])], sort=s,
        choices=[(37356, "Rhinohide Wristwraps"), (37354, "Reinforced Caribou-Hide Boots"), (35830, "Worn Vrykul Smasher")],
        story="The lesson: the wooly rhinos of the tundra.")
    b = book.quest(
        9105361, "Bloodspore Moths", 69, 68, lantern, lantern, "wren",
        "Wren, sneezing:$B$BSnack! The moths on the Bloodspore Plains are covered in SPORES. Achoo! Take Bramble, "
        "she's got a cold anyway. Eat five where she can see. Your moth will be sneezy, but it'll be fine.",
        "With Bramble watching, devour 5 Bloodspore Moths in the Borean Tundra.",
        "Five moths, Snack. Achoo.",
        "Bless you! Bless your moth!$B$BHere!",
        objectives=[devour(5, "Bloodspore Moth devoured, Bramble sneezing", entries=[25464],
                           companion="Ah... ah... ACHOO. Sorry. ACHOO. Keep going, I'm fine. ACHOO.")], prev=a.id, sort=s,
        choices=[(36885, "Marshwalker Chestpiece"), (37394, "Marshwalker Waistguard"), (35852, "Fullered Coldsteel Dagger")],
        story="Wren's sneezy spore-covered moths: Bramble sneezes while you eat five (the moth line).")
    d = book.quest(
        9105363, "Coldarra", 72, 70, lantern, lantern, "hagatha",
        "Hagatha's voice turns careful:$B$BOn Coldarra, in the west, the blue dragonflight gathers its servants: "
        "wyrmkin and spellweavers, half dragon and all arrogance. Wear your drake, little horror, and kill four of them in "
        "that shape. Your drake has eaten blue whelps; now let the ones who serve the blue see a drake they do not "
        "serve.",
        "As a Whelp (or what it grew into), slay 4 Coldarra wyrmkin or spellweavers on Coldarra, Borean Tundra.",
        "Four of the blue's servants. Coldarra is in the west.",
        "Arrogance, eaten. It tastes like everything else, in the end.$B$BTake this.",
        objectives=[slay(4, "Coldarra dragonkin slain as a drake", entries=[25728, 25722, 25717],
                         shapes=LINES["whelp"])], prev=b.id, sort=s, needs=LINES["whelp"], xp=6,
        choices=[(39023, "Wax-Coated Chestguard"), (39013, "Discoverer's Mitts"), (39113, "Jagged Troll Render")],
        story="The blue dragonflight's servants on Coldarra: slay four in your drake's own shape.")
    return d


def grizzly_quests(book, lantern):
    s = Z_GRIZZLY
    fire = campfire(book, "grizzly_fire", lantern, 6.0, 6.0, 233.45, [
        "Sit, both of you. Listen. Can you hear the hills breathing? That is Ursoc.",
        "The furbolgs say the great bear sleeps beneath these hills. He fought something terrible once, and won, and lay down.",
        "He has been asleep so long that pines grew on him.",
        "His children guard his den. They are not cruel. They are only keeping him safe while he dreams.",
        "Now the plague has touched some of them, and they have forgotten what they guard.",
        "When you meet them, little horror, eat them as the great bear would want. Quickly. Without anger.",
        "And remember him. A thing that is remembered is never quite eaten."],
        "Bramble is very quiet, then: \"I'll remember him. I'll remember all the bears.\"")
    a = book.quest(
        9105370, "Duskhowl", 72, 71, lantern, lantern, "hagatha",
        "Hagatha, approving:$B$BThese hills are a wolf's country, little horror: duskhowl prowlers, graymist hunters, "
        "packs that sing to each other across the valleys. Eat six. Let your wolf sing too.",
        "Devour 6 wolves in the Grizzly Hills.",
        "Six wolves. Follow the singing.",
        "Can you hear it? Your wolf is singing.$B$BTake this.",
        objectives=[devour(6, "Grizzly Hills wolf devoured", entries=[27408, 26592])], sort=s,
        choices=[(39033, "Discarded Miner's Jerkin"), (38748, "Seal of the Slumbering Wolf"), (39017, "Belt of Keen Hearing")],
        story="The lesson: the singing wolves of the Grizzly Hills.")
    b = book.quest(
        9105371, "Imperial Eagles", 73, 71, lantern, lantern, "wren",
        "Wren, saluting:$B$BSnack, the eagles here are IMPERIAL. They act like they own the sky. So be polite: salute "
        "five of them, properly, before you eat them. Manners first. Show them who owns the sky now. (It's you. Or "
        "Hagatha. Don't tell her I said you.)",
        "Salute (/salute) 5 Imperial Eagles, then devour 5 Imperial Eagles in the Grizzly Hills.",
        "Five eagles, Snack. They still think they own the sky.",
        "The sky is yours! Shh.$B$BHere!",
        objectives=[emote(5, "Imperial Eagle saluted", EMOTE_SALUTE, entries=[26369]),
                    devour(5, "Imperial Eagle devoured", entries=[26369])], prev=a.id, sort=s,
        choices=[(39018, "Boots of Safe Travel"), (39021, "Ectoplasm Stained Wristguards"), (39015, "Crackpot Spaulders")],
        story="Wren's imperial eagles that think they own the sky: salute them first, then eat five (the eagle line).")
    c = book.quest(
        9105372, "The Sleeping Bear", 73, 71, lantern, lantern, "hagatha",
        "Hagatha tells it, with respect:$B$BI have lit a fire beside the lantern. The bears of these hills have a tale, "
        "and it should be told before you meet them. Bring your little friend. She will want to hear about the great "
        "bear.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit. The hills are breathing. Sit.",
        "Quickly. Without anger. Remember him.$B$BTake this.",
        objectives=[tale(fire, "The tale of the sleeping bear heard")], prev=a.id, sort=s, xp=4,
        choices=[(39019, "Iron-Shatter Leggings"), (39029, "Waistguard of Expedient Procurement"), (39109, "Branch of the Roaming Spirit")],
        story="A campfire tale for the Devourer and Bramble: Ursoc, the great bear who sleeps beneath the hills.")
    e = book.quest(
        9105374, "Ursoc's Children", 74, 72, lantern, lantern, "hagatha",
        "Hagatha, quiet:$B$BNow go and meet them: the ursus maulers by the den, and the grizzlies the plague has "
        "touched. Go to the den quietly, little horror, without a fight on the way, so the great bear is not woken. "
        "Then eat three, quickly and without anger. Not to insult him. To remember him.",
        "Walk to Ursoc's Den without being in a fight, then devour 3 of Ursoc's bears in the Grizzly Hills.",
        "Three bears. Go carefully near the den.",
        "Remembered. Ursoc will not mind; bears understand hunger.$B$BTake this.",
        objectives=[visit("Came quietly to Ursoc's Den", 571, 4718.0, -3855.0, radius=35.0, quiet=True),
                    devour(3, "Grizzly Hills bear devoured", entries=[26644, 26706])], prev=c.id, sort=s, xp=6,
        choices=[(39030, "Patchhide Pants"), (38002, "Honorborn Cloak"), (38171, "Battleworn Magnataur Crusher")],
        story="After the tale, Ursoc's children: come quietly to the den, then eat three, without anger.")
    return e


def sholazar_quests(book, lantern):
    s = Z_SHOLAZAR
    a = book.quest(
        9105381, "Mangal Crocolisks", 75, 74, lantern, lantern, "wren",
        "Wren, peering:$B$BSnack, the crocodiles in the mangal are GREEN and HUGE and they look like logs. Like the "
        "ones in Loch Modan, remember? But bigger. Eat six. Your komodo will feel very at home.",
        "Devour 6 Mangal Crocolisks in Sholazar Basin.",
        "Six crocolisks, Snack. Count the logs.",
        "Logs eaten! Your komodo says thank you.$B$BHere!",
        objectives=[devour(6, "Mangal Crocolisk devoured", entries=[28002])], sort=s,
        choices=[(43906, "Cunning Leather Tunic"), (43894, "Gryphon Hide Moccasins"), (42861, "Jormungar Fang")],
        story="The lesson, Wren's way: the log-like crocolisks of the mangal (the komodo line).")
    b = book.quest(
        9105382, "Dreadsabers", 76, 74, lantern, lantern, "hagatha",
        "Hagatha speaks:$B$BThe dreadsabers of the basin hunt the hunters; Nesingwary's men are afraid of them, and "
        "they are not afraid of anything else. Wear your saber, little horror, and hunt five of them in that shape. Your saber has hunted in the "
        "dark and in the moonlight; now let it hunt the ones who hunt.",
        "As a Saber (or what it grew into), slay 5 dreadsabers in Sholazar Basin.",
        "Five dreadsabers, as a saber. They hunt the hunters; you hunt them.",
        "Hunter of hunters. That is what you are.$B$BTake this.",
        objectives=[slay(5, "Dreadsaber slain as a saber", entries=[28001], shapes=LINES["saber"])],
        prev=a.id, sort=s, needs=LINES["saber"],
        choices=[(43889, "Hulking Abomination Hide Cloak"), (42812, "The \"D\" Ring"), (42862, "Hyldnir Painbringer")],
        story="Hagatha's dreadsabers that hunt the hunters: hunt five as a saber (the saber line).")
    c = book.quest(
        9105383, "Spoon Hardknuckle", 76, 74, lantern, lantern, "wren",
        "Wren, with her spoon held high:$B$BSnack, there are gorillas here called HARDKNUCKLES. That's the best name "
        "anything has ever had. I'm naming my spoon Hardknuckle, and to make it official there has to be a contest. "
        "When you say yes, I bang the spoon, and you eat four hardknuckles before I've banged it three hundred "
        "times.$B$BReady? *BANG*",
        "Devour 4 hardknuckle gorillas in Sholazar Basin before Wren bangs her spoon three hundred times (5 minutes).",
        "Three hundred bangs! Out of time! I'll start again. *BANG*",
        "FOUR! Spoon Hardknuckle is official! It's the best spoon in Northrend.$B$BHere!",
        objectives=[devour(4, "Hardknuckle devoured", entries=[28098, 28096])], prev=a.id, sort=s, timed=300,
        choices=[(39036, "Hulking Horror Tunic"), (39035, "Glacier-walker's Mukluks"), (43890, "Interrogator's Flaming Knuckles")],
        story="Wren names her spoon after the hardknuckle gorillas: four of them before three hundred bangs (5 minutes).")
    e = book.quest(
        9105385, "The First Dragons", 77, 75, lantern, lantern, "hagatha",
        "Hagatha tells it, and the flame burns very old:$B$BIn the Savage Thicket, in the east of the basin, there are "
        "drakes from before anyone was keeping count. Primordial, the Oracles call them. They smell of the beginning "
        "of the world: green fire and old stone.$B$BTurn on your Sniff by the lantern and follow it east. Eat two, little horror. Your drake has eaten the young and the wild and the broken; let "
        "it eat the first.",
        "Follow the primordial scent with Sniff to the Savage Thicket, then devour 2 Primordial Drakes.",
        "The first dragons still nest in the east. Follow the green fire.",
        "The first dragons, nearly. Your drake has eaten its whole history now.$B$BTake this, and go to the peaks.",
        objectives=[trail("The primordial scent followed", "a Primordial Drake", 571,
                          [(5445, 5010), (5640, 5010), (5850, 5025), (6045, 4905), (6240, 4905), (6420, 4800)],
                          summon=28378),
                    devour(2, "Primordial Drake devoured", entries=[28378])], prev=b.id, sort=s, xp=6,
        choices=[(43924, "Illskar's Greatcloak"), (42874, "Wooly Stompers"), (43929, "Vile's Uglystick")],
        story="Sniff out the primordial drakes in the Savage Thicket, and eat two (the whelp line).")
    return e


def stormpeaks_quests(book, lantern):
    s = Z_STORMPEAKS
    snowdrift = book.beast("snowdrift", "Snowdrift", 29562, level=76, faction=FACTION_SHY, passive=True,
                           scale=0.3, subname="Icemaw Cub")
    fire = campfire(book, "stormpeaks_fire", lantern, 6.0, 6.0, 414.34, [
        "Come in, come in. Both of you. Wren, stop poking the fire.",
        "[Wren] I'm not poking it, I'm encouraging it.",
        "This is the last lantern, little horror. I hung it at the top of the world on purpose.",
        "[Wren] I wanted it in a bakery. I was outvoted.",
        "When Wren found you, you were a shadow in a ritual circle with nothing inside it but hunger.",
        "[Wren] You ate my sandwich. First thing you ever did. I was so proud.",
        "Since then you have eaten wolves and whelps and storms, and you have spared what deserved sparing.",
        "[Wren] And you patted a SPIDER.",
        "You are not a shadow any more. You are a Devourer. Our Devourer. That is all a witch can hope to make.",
        "[Wren] Come home for soup sometimes, Snack. Bring Bramble."],
        "Bramble wipes her eyes on her sleeve. \"I'm not crying. The fire's smoky. Can we have the soup now?\"")
    a = book.quest(
        9105390, "Crystalweb", 77, 76, lantern, lantern, "wren",
        "Wren, shivering:$B$BSnack, the spiders up there spin webs of CRYSTAL. Like frost on a window, but with legs. "
        "Eat five. They'll crunch like ice.",
        "Devour 5 crystalweb spiders in the Storm Peaks.",
        "Five crystal spiders, Snack. Crunch.",
        "Crunch! Like ice! I knew it.$B$BHere!",
        objectives=[devour(5, "Crystalweb spider devoured", entries=[29411, 29412])], sort=s,
        choices=[(43911, "Vile's Poker"), (42864, "Frozen Mood Ring"), (39130, "Corrupter's Shanker")],
        story="The lesson, Wren's way: the crystal-webbed spiders of the peaks.")
    b = book.quest(
        9105391, "Jormungar", 79, 77, lantern, lantern, "hagatha",
        "Hagatha speaks, and the ground in the flame trembles:$B$BBelow the deepest mine there are tunnels no pick "
        "ever cut. The deep borers made them, looking for the heart of the world. Here, the jormungar dig through the "
        "ice the same way, as big as ships, Wear your borer, little horror, and kill four of them in its shape. It "
        "will learn to dig through anything.",
        "As a Borer (or what it grew into), slay 4 jormungar in the Storm Peaks.",
        "Four jormungar, as a borer. Listen for the ice breaking.",
        "As big as ships, and gone. Your borer will dig to the heart of the world.$B$BTake this.",
        objectives=[slay(4, "Jormungar slain as a borer", entries=[29605, 30291, 30422, 29390, 30148],
                         shapes=LINES["borer"])], prev=a.id, sort=s, needs=LINES["borer"],
        choices=[(43926, "Signet of Baron Sliver"), (43919, "Curved Assassin's Dagger"), (39036, "Hulking Horror Tunic")],
        story="Hagatha's tale of the deep borers: slay four as a borer (the borer line).")
    d = book.quest(
        9105393, "Stormpeak Wyrms", 80, 78, lantern, lantern, "hagatha",
        "Hagatha tells it, and thunder rolls through the flame:$B$BAt the top of the world the storm has children: "
        "stormpeak wyrms and their hatchlings, dragons of lightning and snow. Their spit freezes, their wings smash. "
        "Let one strike you, little horror. This is where your drake has been going since the first whelp you "
        "swallowed. Then eat four.",
        "Let a stormpeak wyrm or hatchling strike you, then devour 4 of them in the Storm Peaks.",
        "Four of the storm's children, and one blow. Climb.",
        "Do you hear it? That is the storm, and it is in you.$B$BTake this. You are nearly at the end of my "
        "lanterns, little horror. Come back to the fire when you are ready.",
        objectives=[struck(1, "The storm's blow felt", entries=[29753, 29755]),
                    devour(4, "Stormpeak wyrm devoured", entries=[29753, 29755])], prev=b.id, sort=s, xp=6,
        choices=[(43207, "Hardened Tongue Tunic"), (44397, "Handwraps of Preserved History"), (42859, "Thorim's Crusher")],
        story="Hagatha's storm wyrms at the top of the world: take a blow, then eat four (the Storm Dragon line).")
    f = book.quest(
        9105395, "The Last Lantern", 80, 78, lantern, lantern, "hagatha",
        "Both sisters' voices at once, then Hagatha's alone:$B$BWe have lit a fire beside the last lantern, little "
        "horror. Both of us are here, as much as we can be. Bring your little friend. This is the last tale, and it "
        "is about you.",
        "Sit at the Sisters' Campfire by the last lantern with Bramble, and hear the sisters' last tale to its end.",
        "The fire is lit. We are waiting. Bring her.",
        "That is all, little horror. That is the whole tale, so far.$B$B[Wren] SO FAR. There'll be more. Here, this "
        "is from both of us.",
        objectives=[tale(fire, "The sisters' last tale heard")], prev=d.id, sort=s, xp=7,
        choices=[(44409, "Headguard of Retaliation"), (44405, "Exotic Leather Tunic"), (42859, "Thorim's Crusher")],
        story="The end of the lanterns: Hagatha and Wren tell the Devourer and Bramble the tale of the Devourer itself.")
    book.quest(
        9105394, "The Storm Answers", 80, 80, lantern, lantern, "hagatha",
        "Hagatha, very quietly:$B$BYou wear the storm now, little horror. A storm dragon, grown from a whelp in a "
        "marsh. I remember the whelp. Go and show the peaks what you became: wear your storm dragon and slay ten of "
        "the dragons and dragonkin of these mountains. Let them see what a Devourer grows into.",
        "As a Storm Dragon, slay 10 dragonkin in the Storm Peaks.",
        "Ten, little horror. In your storm.",
        "They saw. The whole sky saw.$B$BI have nothing left to teach you. Take this, and come and sit with us in the "
        "In-Between some evening. Wren will make soup. Do not eat Wren.",
        objectives=[slay(10, "Dragonkin slain as a Storm Dragon", ctype=T_DRAGON, shapes=STORM_DRAGON)],
        prev=d.id, sort=s, needs=STORM_DRAGON, xp=7,
        choices=[(44409, "Headguard of Retaliation"), (44405, "Exotic Leather Tunic"), (43207, "Hardened Tongue Tunic")],
        story="For a Devourer with the Storm Dragon: show the peaks what it became.")
    mercy(book, 9105392, "Snowdrift", 78, lantern, snowdrift,
          [(6300, -975), (6300, -885), (6300, -825)],
          "Wren, outraged:$B$BSnack, the vrykul took an icemaw cub to train as a war-bear, and it ran away, and now it's "
          "hiding in the snow west of the lantern. It's tiny! It doesn't want to go to war! It smells of snow and fur "
          "and absolutely not wanting to go to war.$B$BSniff it out and pat it. Then let it follow you somewhere the "
          "vrykul won't look.",
          "Snow and fur and no war, Snack.",
          "It followed you right out of sight of the vrykul and then curled up in a snowdrift and went to sleep. No "
          "war for that one. Snowdrift will remember you; bears remember whoever let them sleep.$B$BHere's a polar "
          "cub to keep for now. It's never been to war either. It's only been to Winter Veil.",
          (22781, "Polar Bear Collar", 1), s,
          "Mercy: Sniff out Snowdrift, an icemaw cub that ran from the vrykul war-bear pens, and pat it. It comes "
          "back grown (mounts idea 1). Reward: a polar bear cub companion.", prev=a.id)
    return f
