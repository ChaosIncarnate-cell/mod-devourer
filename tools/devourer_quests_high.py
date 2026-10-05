"""Task 021: the lanterns of the fifties, Outland and Northrend (levels 49-80). Part of
tools/devourer_quests_content.py."""

from devourer_quests import devour, slay, LINES
from devourer_quests_content import LANTERN_OPEN, T_DRAGON
from devourer_quests_teens import onward

Z_UNGORO, Z_WINTERSPRING, Z_BURNING = 490, 618, 46
Z_TEROKKAR, Z_NAGRAND, Z_NETHERSTORM = 3519, 3518, 3523
Z_FJORD, Z_BOREAN, Z_GRIZZLY, Z_SHOLAZAR, Z_STORMPEAKS = 495, 3537, 394, 3711, 67
TOAD = LINES["toad"]
DRAKES = (36, 44)                             # Proto-Drake, Earthen Proto-Drake
STORM_DRAGON = (37,)

# Mounts from the mounts thread (tools/mounts/ascension/new_quests.txt). Ground: riding 75 at level 20; flying:
# riding 225 at level 60.
CARNIVARUS = (9304842, "Carnivarus Cutting pouch (one of four)")
PRISMATIC_SLIMESABER = (9304083, "Prismatic Slimesaber's Reins")
ARBOREAL_GULPER = (9304656, "Arboreal Gulper")
MOON_FELINE = (9304078, "Reins of the Moon-Bathed Feline")
ARDENMOTHS = (9304885, "Ardenmoth pouch (one of three)")
BUTTERFLIES = (9304813, "Butterfly pouch (one of three, flying)")


def high(book, thirties):
    ungoro = book.lantern("ungoro", "Un'Goro Crater", 1, -6800.0, -1850.0, -272.22, 0.9,
                          "the crater floor north-east of Fire Plume Ridge")
    winterspring = book.lantern("winterspring", "Winterspring", 1, 6500.0, -3500.0, 637.96, 4.2,
                                "the snow below Timbermaw Post")
    burning = book.lantern("burning", "Burning Steppes", 0, -8100.0, -1800.0, 133.46, 3.1,
                           "the ash fields below the Pillar of Ash")
    terokkar = book.lantern("terokkar", "Terokkar Forest", 530, -2500.0, 4000.0, -3.81, 2.4,
                            "the forest road between Allerian Stronghold and Stonebreaker Hold")
    nagrand = book.lantern("nagrand", "Nagrand", 530, -2200.0, 6700.0, -2.24, 5.0, "the plains near the Ring of Trials")
    netherstorm = book.lantern("netherstorm", "Netherstorm", 530, 3000.0, 3400.0, 105.28, 1.7,
                               "the waste south of Area 52")
    fjord = book.lantern("fjord", "Howling Fjord", 571, 600.0, -4600.0, 204.51, 3.9, "the hills north of Valgarde")
    borean = book.lantern("borean", "Borean Tundra", 571, 3000.0, 5300.0, 61.12, 0.6,
                          "the tundra between Valiance Keep and Warsong Hold")
    grizzly = book.lantern("grizzly", "Grizzly Hills", 571, 3800.0, -3600.0, 231.46, 2.2, "the pines of central Grizzly Hills")
    sholazar = book.lantern("sholazar", "Sholazar Basin", 571, 5300.0, 5200.0, -129.8, 4.4, "the Wildgrowth Mangal")
    stormpeaks = book.lantern("stormpeaks", "The Storm Peaks", 571, 6300.0, -1050.0, 414.59, 1.3,
                              "the Snowblind Hills near K3")

    book.region("The lanterns of the fifties, Outland and Northrend (levels 49-80)",
                "Eleven lanterns for the last forms: devilsaurs and oozes in the crater, the moon-touched owlbeasts, "
                "black dragonkin for the storm, then the warp stalkers and drakes of Outland and the proto-drakes, "
                "jormungar and storm wyrms of Northrend.")

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
    a = book.quest(
        9105290, "Ravasaurs", 49, 48, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice, and somewhere in the flame something roars:$B$BIn the crater the world is "
        "young, little horror, and young worlds are hungry. The ravasaurs hunt the marsh in packs. Eat six of them "
        "and taste a hunger older than any you have met.",
        "Devour 6 ravasaurs in Un'Goro Crater.",
        "Six ravasaurs. They hunt in packs; so can you.",
        "Old hunger, in a young world. It suits you.$B$BTake this.",
        objectives=[devour(6, "Ravasaur devoured", entries=[6505, 6506, 6507, 6508])], sort=s,
        choices=[(15789, "Deep River Cloak"), (12114, "Nightfall Gloves"), (11120, "Belgrom's Hammer")],
        story="Hagatha teaches the young world's old hunger: six ravasaurs.")
    b = book.quest(
        9105291, "Pterrordax", 51, 49, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, ducking:$B$BSnack, something with LEATHER WINGS just flew past the lantern. In the "
        "crater! Pterrordax! They're like bats that went to a lot of trouble. Eat five before they dive at me again.",
        "Devour 5 pterrordax in Un'Goro Crater.",
        "Five pterrordax, Snack. One's circling me right now.",
        "No more diving! I can stand up straight again.$B$BHere!",
        objectives=[devour(5, "Pterrordax devoured", entries=[9165, 9166, 9167])], prev=a.id, sort=s,
        choices=[(11874, "Clouddrift Mantle"), (18411, "Spry Boots"), (18400, "Ring of Living Stone")],
        story="Wren ducks the pterrordax of the crater.")
    c = book.quest(
        9105292, "A Very Hungry Plant", 51, 49, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, giggling:$B$BSnack, the flowers in the crater WALK and they BITE. Bloodpetals! I want "
        "one for the cauldron garden. Hagatha says no. So here's my plan: you eat six of them, and from what's left "
        "on your breath I grow a cutting. A big one. A rideable one. Hagatha doesn't have to know.",
        "Devour 6 bloodpetals in Un'Goro Crater.",
        "Six bloodpetals, Snack. The plan is in motion.",
        "It worked! A carnivarus! It bites, but only things you don't like. Hagatha found out. She's not speaking "
        "to me. Here's your cutting!",
        objectives=[devour(6, "Bloodpetal devoured", entries=[6509, 6511, 6510, 6512])], prev=a.id, sort=s,
        items=[(CARNIVARUS[0], CARNIVARUS[1], 1)],
        story="Wren grows a rideable carnivarus from the bloodpetals the Devourer eats. Reward: a Carnivarus mount.")
    d = book.quest(
        9105293, "The Primal Oozes", 52, 50, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, curious despite herself:$B$BThe oozes of the crater are the oldest soup in "
        "the world, little horror: muculent, primal, glutinous. Some say all life crawled out of such a pool. Eat "
        "five of them, and taste where everything began.",
        "Devour 5 oozes in Un'Goro Crater.",
        "Five oozes. They have been waiting since the world began.",
        "The beginning of everything, and it tastes of nothing much. Most beginnings do.$B$BWren saved what dripped "
        "off you and made a sabercat of it again, a shining one this time. You can ride it. Do not let her make "
        "another.",
        objectives=[devour(5, "Un'Goro ooze devoured", entries=[6556, 6557, 6559])], prev=a.id, sort=s,
        items=[(PRISMATIC_SLIMESABER[0], PRISMATIC_SLIMESABER[1], 1)],
        story="Hagatha's oldest soup in the world: the crater's oozes. Reward: the Prismatic Slimesaber.")
    book.quest(
        9105294, "The Arboreal Gulper", 52, 50, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, whispering a secret:$B$BToad Snack. In the crater there's a frog that lives in the "
        "TREES and eats wasps. I want you to be that frog. As your toad, or your frog, or the salamander, catch "
        "eight of the Gorishi bugs in the south of the crater. Snap! Like that.$B$BThere's a tree frog in it for "
        "you. A big one.",
        "As a Biletoad, Giant Marsh Frog or Water Salamander, slay 8 Gorishi silithid in Un'Goro Crater.",
        "Eight bugs, Snack. Snap snap. As a toad!",
        "SNAP! You're the best frog in the crater.$B$BHere's your tree frog. It's a gulper that lives in trees, so "
        "it's very good at climbing on things it shouldn't. You can ride it.",
        objectives=[slay(8, "Gorishi slain as a toad", entries=[6551, 6552, 6553], shapes=TOAD)],
        prev=a.id, sort=s, needs=TOAD,
        items=[(ARBOREAL_GULPER[0], ARBOREAL_GULPER[1], 1)],
        story="For a Devourer with a toad shape: catch the Gorishi bugs as a toad. Reward: the Arboreal Gulper.")
    e = book.quest(
        9105295, "Diemetradon", 53, 51, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe diemetradon wear sails on their backs to catch the sun. Lizards that "
        "learned to drink light. Your komodo should taste what that is like, little horror. Eat five.",
        "Devour 5 diemetradon in Un'Goro Crater.",
        "Five diemetradon. Follow the sails.",
        "Sunlight in a lizard. Your komodo is warm now.$B$BTake this.",
        objectives=[devour(5, "Diemetradon devoured", entries=[9162, 9163, 9164])], prev=b.id, sort=s,
        choices=[(15825, "Traphook Jerkin"), (21319, "Gloves of the Pathfinder"), (12066, "Shaleskin Cape")],
        story="Hagatha's sun-drinking diemetradon, for a komodo that wants to be warm.")
    f = book.quest(
        9105296, "Devilsaur", 55, 53, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and the ground in the flame shakes:$B$BThe devilsaur is the biggest hunger "
        "in the crater, little horror. Everything else in Un'Goro is food to it, and it knows. It does not hide; "
        "it does not need to. You hear it before you see it, and then you see nothing else.$B$BEat one. Show the "
        "crater who is hungriest now.",
        "Devour a Devilsaur in Un'Goro Crater.",
        "The devilsaur still walks. Listen for it.",
        "The biggest hunger in the crater, inside the hungriest thing in the world. I am proud of you, little "
        "horror. Do not tell Wren I said so.$B$BTake this.",
        objectives=[devour(1, "Devilsaur devoured", entries=[6498])], prev=e.id, sort=s, xp=7,
        choices=[(20715, "Dunestalker's Boots"), (19106, "Ice Barbed Spear"), (22008, "Darkmantle Spaulders")],
        story="Hagatha's tale of the devilsaur, the biggest hunger in the crater; the Devourer is bigger.")
    return f


def winterspring_quests(book, lantern):
    s = Z_WINTERSPRING
    a = book.quest(
        9105300, "Shardtooth", 54, 53, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, her breath frosting the glass:$B$BThe bears of Winterspring have teeth like shards "
        "of ice. Shardtooth, the furbolgs call them, and give them room. Eat six, little horror. Cold meat keeps.",
        "Devour 6 shardtooth bears in Winterspring.",
        "Six shardtooths. They are cold; you will warm them.",
        "Cold, and sharp, and now warm inside you.$B$BTake this.",
        objectives=[devour(6, "Shardtooth bear devoured", entries=[7444, 7443, 7445])], sort=s,
        choices=[(15861, "Swiftfoot Treads"), (20649, "Sunprism Pendant"), (16995, "Duskwing Mantle")],
        story="Hagatha's ice-toothed bears of Winterspring.")
    b = book.quest(
        9105301, "Winterspring Owls", 55, 53, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, hooting softly:$B$BHoo. Hoo. Snack, the owls in the snow are WHITE. Winterspring owls "
        "and the screechers! They're so pretty. Hagatha says your owl should eat its northern cousins before it "
        "grows up for good. Eat five. Gently. If you can eat gently.",
        "Devour 5 Winterspring owls in Winterspring.",
        "Hoo hoo. Still five owls, Snack.",
        "Hoo! Your owl is very nearly grown. I'm a bit sad. Owls grow up so fast.$B$BHere!",
        objectives=[devour(5, "Winterspring owl devoured", entries=[7455, 7456])], prev=a.id, sort=s,
        choices=[(11193, "Blazewind Breastplate"), (18411, "Spry Boots"), (12066, "Shaleskin Cape")],
        story="Wren's white owls of the snow (the owl line).")
    c = book.quest(
        9105302, "Frostsabers", 57, 55, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, quiet as falling snow:$B$BOn Frostsaber Rock the white cats hunt under the moon. "
        "The night elves ride them, when the cats allow it. Eat five, little horror, the cubs and the grown and the "
        "huntresses. A saber that has eaten the moon's own cats walks in moonlight.",
        "Devour 5 frostsabers at Frostsaber Rock in Winterspring.",
        "Five frostsabers. Look for them under the moon.",
        "Moonlight and snow. Your saber will remember both.$B$BWren has a cat for you. A moon-bathed one, she says, "
        "that she found sleeping in the lantern's light. You can ride it. It will not mind.",
        objectives=[devour(5, "Frostsaber devoured", entries=[7430, 7431, 7433, 7432])], prev=a.id, sort=s,
        items=[(MOON_FELINE[0], MOON_FELINE[1], 1)],
        choices=[(15825, "Traphook Jerkin"), (21319, "Gloves of the Pathfinder"), (15708, "Blight Leather Gloves")],
        story="Hagatha's moon-lit frostsabers. Reward: the Moon-Bathed Feline.")
    d = book.quest(
        9105303, "Chillwind", 57, 55, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, impressed:$B$BSnack, the chimaeras in Winterspring have TWO HEADS and they breathe "
        "COLD. Two heads! Twice the hats! Eat four of the chillwinds. One head each is still eight heads.",
        "Devour 4 chillwind chimaeras in Winterspring.",
        "Four chimaeras, Snack. Eight heads.",
        "Eight heads! That's a lot of hats I won't be knitting.$B$BHere!",
        objectives=[devour(4, "Chillwind chimaera devoured", entries=[7447, 7448, 7449])], prev=b.id, sort=s,
        choices=[(16995, "Duskwing Mantle"), (20649, "Sunprism Pendant"), (18400, "Ring of Living Stone")],
        story="Wren counts the heads of the two-headed chillwind chimaeras.")
    e = book.quest(
        9105304, "Cobalt Whelps", 56, 54, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BIn the caves of Mazthoril, south of Everlook, the blue dragonflight keeps "
        "its young. Cobalt whelps, cobalt broodlings, cold as the caves. Eat five, little horror. Your drake has "
        "tasted red fire and black; let it taste blue frost.",
        "Devour 5 cobalt whelps or broodlings in Mazthoril, Winterspring.",
        "Five cobalt whelps. The caves are cold; mind your step.",
        "Red, black and now blue. Your drake knows every colour of dragon now.$B$BTake this.",
        objectives=[devour(5, "Cobalt whelp devoured", entries=[10659, 10660])], prev=a.id, sort=s,
        choices=[(15861, "Swiftfoot Treads"), (11874, "Clouddrift Mantle"), (12114, "Nightfall Gloves")],
        story="Hagatha sends the Devourer into the blue dragonflight's caves (the whelp line).")
    f = book.quest(
        9105305, "The Moon-Touched", 58, 56, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and the flame goes white as the moon:$B$BAn owl that eats moonlight becomes "
        "a moonkin. A moonkin that eats the wild becomes an owlbeast. But here, in the snow, the owlbeasts ate so "
        "much of the moon that it touched them back. Moontouched, the furbolgs say, and bow their heads.$B$BEat two, "
        "little horror. Your moonkin has been waiting for this since the first owl you swallowed.",
        "Devour 2 Moontouched Owlbeasts in Winterspring.",
        "The moon-touched still wander the snow.",
        "The moon, in you. Your moonkin will never forget it now.$B$BTake this. You have come a very long way from "
        "the first owl.",
        objectives=[devour(2, "Moontouched Owlbeast devoured", entries=[7453])], prev=d.id, sort=s, xp=7,
        choices=[(18420, "Bonecrusher"), (21187, "Earthweave Cloak"), (22002, "Darkmantle Belt")],
        story="Hagatha's tale of the owlbeasts the moon touched back (a Moontouched Owlbeast task).")
    return f


def burning_quests(book, lantern):
    s = Z_BURNING
    a = book.quest(
        9105310, "Ember Worgs", 52, 51, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, her voice crackling like coals:$B$BThe worgs of the Burning Steppes sleep in the "
        "ash and wake with embers in their fur. Eat five of them, little horror. A wolf that has eaten fire does "
        "not fear it.",
        "Devour 5 ember worgs in the Burning Steppes.",
        "Five ember worgs. Follow the smoke.",
        "Embers in the belly. Your wolf will not flinch from fire again.$B$BTake this.",
        objectives=[devour(5, "Ember worg devoured", entries=[9690, 9694, 9697, 7055])], sort=s,
        choices=[(15789, "Deep River Cloak"), (12114, "Nightfall Gloves"), (11874, "Clouddrift Mantle")],
        story="Hagatha's ember-furred worgs of the Burning Steppes.")
    b = book.quest(
        9105311, "Black Broodlings", 53, 51, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and the flame darkens:$B$BThe black dragonflight keeps its broods in these "
        "ash fields: broodlings, dragonspawn, wyrmkin, scalding and flamescaled. Their master is the son of a very "
        "wicked dragon, and he will not notice a few gone. Eat six of them, little horror. A drake that eats its "
        "own kind grows into a storm.",
        "Devour 6 black dragonkin in the Burning Steppes.",
        "Six of the black brood. They are everywhere here.",
        "Ash and fire and dragon. Your drake is learning what it will become.$B$BTake this.",
        objectives=[devour(6, "Black dragonkin devoured", entries=[7047, 7040, 7048, 7049, 7041, 7042, 7043])],
        prev=a.id, sort=s,
        choices=[(11193, "Blazewind Breastplate"), (18411, "Spry Boots"), (18400, "Ring of Living Stone")],
        story="Hagatha sends the Devourer among the black brood (the whelp line, towards the Storm Dragon).")
    c = book.quest(
        9105312, "Scorpids of the Steppes", 54, 52, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, fanning the smoke away:$B$BSnack, the scorpids there have FIRE TAILS. Venomtip and "
        "deathlash and firetail! Who gave scorpids fire? Nobody needed that. Eat four. Fireproof your tummy.",
        "Devour 4 scorpids in the Burning Steppes.",
        "Four fire scorpids, Snack.",
        "Fireproof tummy achieved!$B$BHere!",
        objectives=[devour(4, "Burning Steppes scorpid devoured", entries=[9691, 9695, 9698])], prev=a.id, sort=s,
        choices=[(15825, "Traphook Jerkin"), (12066, "Shaleskin Cape"), (21319, "Gloves of the Pathfinder")],
        story="Wren fireproofs the Devourer's tummy with fire-tailed scorpids.")
    d = book.quest(
        9105313, "Drakes of the Steppes", 56, 54, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, slow and grim:$B$BAmong the black brood there are drakes, little horror, "
        "grown ones with wings: black drakes, scalding drakes, searscale drakes. They are few and proud and they do "
        "not share the sky.$B$BEat two of them. Your drake should meet its elders before it outgrows them.",
        "Devour 2 drakes in the Burning Steppes.",
        "Two drakes. They are few; look to the sky and the high rocks.",
        "Elders, eaten. Your drake has nothing left to look up to but the storm.$B$BTake this.",
        objectives=[devour(2, "Black drake devoured", entries=[7044, 7045, 7046])], prev=b.id, sort=s, xp=6,
        choices=[(15861, "Swiftfoot Treads"), (16995, "Duskwing Mantle"), (20649, "Sunprism Pendant")],
        story="Hagatha's tale of the proud black drakes; the Devourer's drake meets its elders.")
    book.quest(
        9105314, "The Storm Gathers", 56, 55, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, and the flame flickers like lightning:$B$BYou wear a drake now, little horror. Good. "
        "A drake that eats dragonkin while it wears its own wings gathers the storm in its chest. Wear your "
        "proto-drake, or the earthen one, and eat ten of the black brood. When you breathe out, the sky will "
        "answer.",
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
    a = book.quest(
        9105320, "Timber Worgs", 62, 60, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice comes thin, from very far away:$B$BI can barely reach you here, little horror. "
        "This world is broken; my lantern hangs on a thread. Listen anyway. The worgs of this forest are bigger "
        "than any in our world, and their alphas bigger still. Eat six.",
        "Devour 6 timber worgs in Terokkar Forest.",
        "Six worgs. I can hear them through the thread.",
        "Bigger worlds, bigger wolves, bigger you.$B$BTake this.",
        objectives=[devour(6, "Timber worg devoured", entries=[18476, 18477])], sort=s,
        choices=[(31788, "Blacksting Gloves"), (25504, "Pilgrim's Belt"), (25499, "Felblood Band")],
        story="Hagatha's thread-thin voice sends the Devourer after Terokkar's timber worgs.")
    b = book.quest(
        9105321, "Teromoths", 63, 61, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, faint but excited:$B$BSnack! Can you hear me? The moths there are ENORMOUS. Teromoths! "
        "Royal ones! Your moth will be so jealous. Eat five and let it eat the jealousy too.$B$BAnd I'll send you "
        "something with wings. If the thread holds.",
        "Devour 5 teromoths in Terokkar Forest.",
        "Five teromoths, Snack. The thread's still holding.",
        "Your moth isn't jealous any more! It's FULL.$B$BThe thread held! Here's an ardenmoth. It's a moth you can "
        "ride. On the ground. It's working on the flying.",
        objectives=[devour(5, "Teromoth devoured", entries=[18468, 18437, 18469])], prev=a.id, sort=s,
        items=[(ARDENMOTHS[0], ARDENMOTHS[1], 1)],
        choices=[(27731, "Vindicator's Cloak"), (25932, "Cenarion Thicket Jerkin"), (27733, "Warden's Ring of Precision")],
        story="Wren's enormous teromoths (the moth line). Reward: an Ardenmoth mount.")
    c = book.quest(
        9105322, "Warp Stalkers", 64, 62, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and the thread hums:$B$BOut where the world thins, little horror, the warp "
        "stalkers grow until they forget which side of the dark they belong to. Here, in Terokkar, they blink in and "
        "out of the forest like candle flames. Eat five of them, the stalkers and the hunters.$B$BYou were born in "
        "the dark between. So were they, nearly.",
        "Devour 5 warp stalkers or warp hunters in Terokkar Forest.",
        "Five of them. They blink; be faster than the blink.",
        "Dark and cold and familiar. Your warp stalker is ready to forget which side it belongs to.$B$BTake this.",
        objectives=[devour(5, "Warp stalker devoured", entries=[18464, 18465])], prev=a.id, sort=s,
        choices=[(27724, "Wild Shoulderpads"), (25487, "Wind Dancer's Pendant"), (25986, "Dreadtusk's Fury")],
        story="Hagatha's tale of the warp stalkers that forget which side of the dark they belong to (the Void "
              "Terror line).")
    d = book.quest(
        9105323, "The Bone Wastes", 65, 63, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, whispering:$B$BSnack, in the Bone Wastes the birds eat bones and the scorpids crawl "
        "IN the bones. Bonelashers and bonecrawlers. It's horrible and I love it. Eat four bonelashers and three "
        "bonecrawlers.",
        "Devour 4 Bonelashers and 3 Scorpid Bonecrawlers in the Bone Wastes, Terokkar Forest.",
        "Four and three, Snack. Bones bones bones.",
        "Bone appetit! I've been saving that one.$B$BHere!",
        objectives=[devour(4, "Bonelasher devoured", entries=[18470]),
                    devour(3, "Scorpid Bonecrawler devoured", entries=[22100])], prev=c.id, sort=s, xp=6,
        choices=[(31729, "Heirloom Signet of Valor"), (31471, "T'chali's Kilt"), (31422, "Heavy Elven Dirk")],
        story="Wren's bone-eating birds and bone-dwelling scorpids of the Bone Wastes.")
    return d


def nagrand_quests(book, lantern):
    s = Z_NAGRAND
    a = book.quest(
        9105330, "Talbuk", 65, 64, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, as if the air were sweeter:$B$BNagrand is the only green left in this broken world, "
        "and the talbuk graze on it as if nothing were wrong. Eat six of them, little horror. Innocence has a taste, "
        "and you should know it before it is gone.",
        "Devour 6 talbuk in Nagrand.",
        "Six talbuk. They graze as if nothing were wrong.",
        "Sweet, wasn't it? Remember it.$B$BTake this.",
        objectives=[devour(6, "Talbuk devoured", entries=[17130, 17131])], sort=s,
        choices=[(31486, "Bear-Strength Harness"), (31482, "Dire Wolf Handler Gloves"), (25927, "Consortium Cloak of the Quick")],
        story="Hagatha teaches the taste of innocence: the grazing talbuk of Nagrand.")
    b = book.quest(
        9105331, "Windrocs", 65, 64, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, holding onto her hat:$B$BSnack, the birds in Nagrand are WINDROCS and they're the size "
        "of a cart. Your eagle would love to be that size. Eat five, and let it dream big.",
        "Devour 5 windrocs in Nagrand.",
        "Five windrocs, Snack. Dream big.",
        "Big dreams, big bird, big Snack!$B$BHere!",
        objectives=[devour(5, "Windroc devoured", entries=[17128, 18220, 17129])], prev=a.id, sort=s,
        choices=[(31419, "Living Grove Shoulderpads"), (31660, "Feralfen Skulker's Belt"), (25926, "Nexus-Stalker's Band")],
        story="Wren's cart-sized windrocs, for an eagle that dreams big.")
    c = book.quest(
        9105332, "Clefthoof", 66, 64, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe clefthoof are the oldest beasts of this world. They were here before "
        "the orcs, before the draenei, before the world broke. Eat four, little horror. Old meat, from an old world.",
        "Devour 4 clefthoof in Nagrand.",
        "Four clefthoof. They are slow, but they are many.",
        "Old, and heavy, and patient. A world's worth of patience.$B$BTake this.",
        objectives=[devour(4, "Clefthoof devoured", entries=[18205, 17132, 17133])], prev=a.id, sort=s,
        choices=[(31426, "Agile Mountain Bracers"), (25975, "Wolf Hunter's Guise"), (25622, "Staff of the Four Golden Coins")],
        story="Hagatha's ancient clefthoof of Nagrand.")
    d = book.quest(
        9105333, "Voidspawn", 66, 64, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, and the thread trembles:$B$BIn the Spirit Fields, in the south, the void leaks "
        "through and takes shape as it likes: voidspawn, little blots of nothing that hunger. Your voidling began as "
        "one of these, near enough. Eat five, and let it remember where it came from.",
        "Devour 5 Voidspawn in the Spirit Fields of Nagrand.",
        "Five voidspawn. The fields are full of them.",
        "Nothing, eaten. It tastes like home, doesn't it?$B$BTake this.",
        objectives=[devour(5, "Voidspawn devoured", entries=[17981])], prev=c.id, sort=s, xp=6,
        choices=[(31820, "Blessed Signet Ring"), (25616, "Tim's Trusty Helmet"), (27749, "Staff of the Wild")],
        story="Hagatha sends the voidling home: the voidspawn of the Spirit Fields (the void line).")
    return d


def netherstorm_quests(book, lantern):
    s = Z_NETHERSTORM
    a = book.quest(
        9105340, "Warp Chasers", 67, 66, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, from the very edge of hearing:$B$BAt the edge of this world, the warp chasers run "
        "after whatever the storm throws loose. Eat six of them, little horror. Your warp stalker has nearly "
        "forgotten which side of the dark it belongs to. Help it forget.",
        "Devour 6 warp chasers in Netherstorm.",
        "Six chasers. They chase; you catch.",
        "Forgotten. Good.$B$BTake this.",
        objectives=[devour(6, "Warp chaser devoured", entries=[18884])], sort=s,
        choices=[(30401, "Farahlite Studded Boots"), (31527, "Leafbeard Ring"), (31703, "Nether-Stalker's Blade")],
        story="Hagatha's warp chasers at the edge of the world (the Void Terror line).")
    b = book.quest(
        9105341, "Phase Hunters", 68, 66, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe phase hunters slip between this world and the next as easily as you "
        "slip between shapes, little horror. They are the nearest thing to you in this broken place. Eat five. "
        "Learn how they slip.",
        "Devour 5 phase hunters in Netherstorm.",
        "Five phase hunters. Catch them on this side.",
        "Slippery. Now so are you.$B$BTake this.",
        objectives=[devour(5, "Phase hunter devoured", entries=[18879])], prev=a.id, sort=s,
        choices=[(30362, "Energized Helm"), (30384, "Brightdawn Bracers"), (31414, "Wild Wood Staff")],
        story="Hagatha's phase hunters, who slip between worlds as the Devourer slips between shapes.")
    c = book.quest(
        9105342, "Nether Rays", 68, 66, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, dreamy:$B$BSnack, the nether rays FLOAT. They swim in the air like fish that forgot "
        "about water. I want to float too. Eat four. Maybe you'll float a bit. Then you can teach me.",
        "Devour 4 nether rays in Netherstorm.",
        "Four nether rays, Snack. Are you floating yet?",
        "Not floating? Oh well. You've got four fish-that-forgot-water in you, that's nearly floating.$B$BHere!",
        objectives=[devour(4, "Nether ray devoured", entries=[18880])], prev=a.id, sort=s,
        choices=[(31532, "Supple Leather Boots"), (31790, "Expedition Pendant"), (30277, "Ripfang Paw")],
        story="Wren wants to float like the nether rays.")
    d = book.quest(
        9105343, "Shimmerwings", 68, 66, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, flapping her arms:$B$BSnack, inside the big glass domes there are moths that SHIMMER. "
        "Shimmerwing moths! Catch four for me. Eat them, I mean. Catching is eating, for you.$B$BIf the thread "
        "holds, I'll send you wings of your own.",
        "Devour 4 Shimmerwing Moths in the Eco-Dome Midrealm, Netherstorm.",
        "Four shimmerwings, Snack.",
        "Shimmer shimmer! The thread held!$B$BHere: a butterfly you can ride, in the air this time. You'll need your "
        "flying for it. Don't fly into the storm.",
        objectives=[devour(4, "Shimmerwing Moth devoured", entries=[20611])], prev=a.id, sort=s,
        items=[(BUTTERFLIES[0], BUTTERFLIES[1], 1)],
        story="Wren's shimmering moths in the eco-dome. Reward: a flying butterfly mount.")
    e = book.quest(
        9105344, "Nether Drakes", 69, 67, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, slow:$B$BOn the Celestial Ridge in the north-east, the nether drakes nest: "
        "dragons born of a dragon that tore itself apart. Their scales shift like the storm. Eat three, little "
        "horror. Your drake has eaten every colour of our world; let it eat one from beyond it.",
        "Devour 3 nether drakes on the Celestial Ridge, Netherstorm.",
        "Three nether drakes. Climb the ridge.",
        "A colour from beyond the world. Your drake will be strange now. Good.$B$BTake this, and go home, and then "
        "go north.",
        objectives=[devour(3, "Nether drake devoured", entries=[18877])], prev=b.id, sort=s, xp=6,
        choices=[(32869, "Illidari Lord's Tunic"), (32865, "Drake Tamer's Gloves"), (30339, "Protectorate Assassin's Ring")],
        story="Hagatha's nether drakes of the Celestial Ridge (the whelp line).")
    return e


def fjord_quests(book, lantern):
    s = Z_FJORD
    a = book.quest(
        9105350, "Shoveltusk", 69, 68, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, her voice strong again:$B$BAh. I can hear you clearly. This land is cold, little "
        "horror, but it is ours. The shoveltusk dig in the snow for moss and do not look up. Eat six of them. Warm "
        "yourself.",
        "Devour 6 shoveltusk in the Howling Fjord.",
        "Six shoveltusk. They are digging; dig them up.",
        "Warm now? Good.$B$BTake this.",
        objectives=[devour(6, "Shoveltusk devoured", entries=[23690, 23691, 29479])], sort=s,
        choices=[(37355, "Reinforced Caribou-Hide Chestguard"), (37387, "Charred Treads"), (36879, "Soldier's Spiked Mace")],
        story="Hagatha warms the Devourer with the shoveltusk of the fjord.")
    b = book.quest(
        9105351, "Fjord Hawks", 69, 68, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, squinting at the sky:$B$BSnack, the hawks in the fjord dive straight into the sea and "
        "come up with fish! Fjord hawks and the big duskwing eagles. Eat five. Your eagle wants to learn to dive.",
        "Devour 5 fjord hawks or duskwing eagles in the Howling Fjord.",
        "Five birds, Snack. Watch them dive.",
        "Splash! Your eagle can dive now. Probably. Don't test it off a cliff.$B$BHere!",
        objectives=[devour(5, "Fjord bird devoured", entries=[24747, 23693])], prev=a.id, sort=s,
        choices=[(37391, "Rhinohide Mask"), (37383, "Seared Scale Cape"), (37029, "Fin Carver")],
        story="Wren's diving hawks of the fjord (the eagle line).")
    c = book.quest(
        9105352, "The Ember Clutch", 70, 68, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, warm as a hearth:$B$BProto-drakes are what dragons were before the Titans "
        "tidied them. Wild, hungry, and proud of it. In the Ember Clutch, in the north of the fjord, their whelps "
        "hatch in the warm rocks. Eat five of the proto-whelps, little horror. You will fit right in.",
        "Devour 5 Proto-Whelps in the Ember Clutch, Howling Fjord.",
        "Five proto-whelps. The clutch is warm; they will not leave it.",
        "Wild and hungry and proud. You fit right in, as I said.$B$BTake this.",
        objectives=[devour(5, "Proto-Whelp devoured", entries=[23688])], prev=b.id, sort=s,
        choices=[(35914, "Proto-Drake Tooth Spaulders"), (35893, "Coldstone-Inlaid Waistguard"), (35936, "Worg-Fang Talisman")],
        story="Hagatha's untidied whelps of the Ember Clutch (the Proto-Drake line).")
    d = book.quest(
        9105353, "Proto-Drakes", 71, 69, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, proud:$B$BThe grown ones guard the clutch: proto-drakes, little horror, the wild "
        "dragons of the north. There are not many. Eat two, and let your drake meet what it already is.",
        "Devour 2 Proto-Drakes at the Ember Clutch, Howling Fjord.",
        "Two proto-drakes. They guard the clutch.",
        "Your drake has met itself and eaten it. That is the most a Devourer can do.$B$BTake this.",
        objectives=[devour(2, "Proto-Drake devoured", entries=[23689])], prev=c.id, sort=s, xp=6,
        choices=[(35815, "Bone-Threaded Harness"), (37380, "Whalehunter Leggings"), (36878, "Writhing Longstaff")],
        story="Hagatha's wild proto-drakes of the Ember Clutch.")
    return d


def borean_quests(book, lantern):
    s = Z_BOREAN
    a = book.quest(
        9105360, "Wooly Rhinos", 69, 68, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice, clear in the cold:$B$BThe rhinos of the tundra wear wool against the wind "
        "and horns against everything else. Eat five of them, little horror, the matriarchs and the bulls.",
        "Devour 5 wooly rhinos in the Borean Tundra.",
        "Five rhinos. They are hard to miss.",
        "Wool and horn. Warm and hard. Both useful here.$B$BTake this.",
        objectives=[devour(5, "Wooly rhino devoured", entries=[25487, 25489])], sort=s,
        choices=[(37356, "Rhinohide Wristwraps"), (37354, "Reinforced Caribou-Hide Boots"), (35830, "Worn Vrykul Smasher")],
        story="Hagatha's wooly rhinos of the tundra.")
    b = book.quest(
        9105361, "Bloodspore Moths", 69, 68, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, sneezing:$B$BSnack! The moths on the Bloodspore Plains are covered in SPORES. Achoo! "
        "Eat five. Your moth will be sneezy, but it'll be fine.",
        "Devour 5 Bloodspore Moths in the Borean Tundra.",
        "Five moths, Snack. Achoo.",
        "Bless you! Bless your moth!$B$BHere!",
        objectives=[devour(5, "Bloodspore Moth devoured", entries=[25464])], prev=a.id, sort=s,
        choices=[(36885, "Marshwalker Chestpiece"), (37394, "Marshwalker Waistguard"), (35852, "Fullered Coldsteel Dagger")],
        story="Wren's sneezy spore-covered moths (the moth line).")
    c = book.quest(
        9105362, "Tundra Wolves", 70, 68, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe wolves of the tundra are white and lean; the oil-stained ones near "
        "the Scalding Pools are black and miserable. Eat five, little horror, of either. A wolf should know how "
        "the cold feels to its kin.",
        "Devour 5 tundra or oil-stained wolves in the Borean Tundra.",
        "Five wolves. The tundra is wide.",
        "Cold kin, warm belly.$B$BTake this.",
        objectives=[devour(5, "Borean wolf devoured", entries=[25675, 25791])], prev=a.id, sort=s,
        choices=[(35877, "Worgskin Shoulders"), (37396, "Whalehunter Gloves"), (37030, "Blubber Grinder")],
        story="Hagatha's white and oil-stained wolves of the tundra.")
    d = book.quest(
        9105363, "Coldarra", 72, 70, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice turns careful:$B$BOn Coldarra, in the west, the blue dragonflight gathers "
        "its servants: wyrmkin and spellweavers, half dragon and all arrogance. Eat four, little horror. Your drake "
        "has eaten blue whelps; now let it eat the ones who serve the blue.",
        "Devour 4 Coldarra wyrmkin or spellweavers on Coldarra, Borean Tundra.",
        "Four of the blue's servants. Coldarra is in the west.",
        "Arrogance, eaten. It tastes like everything else, in the end.$B$BTake this.",
        objectives=[devour(4, "Coldarra dragonkin devoured", entries=[25728, 25722, 25717])], prev=c.id, sort=s,
        xp=6,
        choices=[(39023, "Wax-Coated Chestguard"), (39013, "Discoverer's Mitts"), (39113, "Jagged Troll Render")],
        story="Hagatha sends the Devourer among the blue dragonflight's servants on Coldarra.")
    return d


def grizzly_quests(book, lantern):
    s = Z_GRIZZLY
    a = book.quest(
        9105370, "Duskhowl", 72, 71, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, approving:$B$BThese hills are a wolf's country, little horror: duskhowl prowlers, "
        "graymist hunters, packs that sing to each other across the valleys. Eat six. Let your wolf sing too.",
        "Devour 6 wolves in the Grizzly Hills.",
        "Six wolves. Follow the singing.",
        "Can you hear it? Your wolf is singing.$B$BTake this.",
        objectives=[devour(6, "Grizzly Hills wolf devoured", entries=[27408, 26592])], sort=s,
        choices=[(39033, "Discarded Miner's Jerkin"), (38748, "Seal of the Slumbering Wolf"), (39017, "Belt of Keen Hearing")],
        story="Hagatha's singing wolves of the Grizzly Hills.")
    b = book.quest(
        9105371, "Imperial Eagles", 73, 71, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, saluting:$B$BSnack, the eagles here are IMPERIAL. They act like they own the sky. Eat "
        "five. Show them who owns the sky now. (It's you. Or Hagatha. Don't tell her I said you.)",
        "Devour 5 Imperial Eagles in the Grizzly Hills.",
        "Five eagles, Snack. They still think they own the sky.",
        "The sky is yours! Shh.$B$BHere!",
        objectives=[devour(5, "Imperial Eagle devoured", entries=[26369])], prev=a.id, sort=s,
        choices=[(39018, "Boots of Safe Travel"), (39021, "Ectoplasm Stained Wristguards"), (39015, "Crackpot Spaulders")],
        story="Wren's imperial eagles that think they own the sky (the eagle line).")
    c = book.quest(
        9105372, "Ice Serpents", 73, 71, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, cold and pleased:$B$BA snake that swallows enough storms grows wings. A snake that "
        "swallows enough winter grows ice. The ice serpents of the troll ruins in the west coil around the old "
        "stones. Eat four, little horror. Your wind serpent will learn the cold.",
        "Devour 4 ice serpents in the Grizzly Hills.",
        "Four ice serpents. They coil around the troll stones.",
        "Ice and wind. Your serpent has both now.$B$BTake this.",
        objectives=[devour(4, "Ice serpent devoured", entries=[26446, 29693])], prev=a.id, sort=s,
        choices=[(39019, "Iron-Shatter Leggings"), (39029, "Waistguard of Expedient Procurement"), (39109, "Branch of the Roaming Spirit")],
        story="Hagatha's ice serpents of the troll ruins (the wind serpent line).")
    d = book.quest(
        9105373, "Fern Feeders", 73, 71, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, softly:$B$BSnack, the moths here eat ferns. Fern feeder moths! They're the gentlest "
        "thing I've ever heard of. Eat five. Gently. Your moth will be gentle too. For about a minute.",
        "Devour 5 Fern Feeder Moths in the Grizzly Hills.",
        "Five gentle moths, Snack.",
        "Gentle! For a minute. That's a lot, for you.$B$BHere!",
        objectives=[devour(5, "Fern Feeder Moth devoured", entries=[27421])], prev=b.id, sort=s,
        choices=[(39020, "Drakuru's Ghastly Helm"), (39025, "Shackles of Sanity"), (39110, "Staff of Righteous Vengeance")],
        story="Wren's gentle fern-eating moths (the moth line).")
    e = book.quest(
        9105374, "Ursoc's Children", 74, 72, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, with respect:$B$BThe furbolgs say Ursoc, the great bear, sleeps beneath "
        "these hills, and his children guard his den: ursus maulers, and the grizzlies the plague has touched. Eat "
        "three, little horror. Not to insult him. To remember him.",
        "Devour 3 bears of Ursoc's Den or infected grizzlies in the Grizzly Hills.",
        "Three bears. Go carefully near the den.",
        "Remembered. Ursoc will not mind; bears understand hunger.$B$BTake this.",
        objectives=[devour(3, "Grizzly Hills bear devoured", entries=[26644, 26706])], prev=c.id, sort=s, xp=6,
        choices=[(39030, "Patchhide Pants"), (38002, "Honorborn Cloak"), (38171, "Battleworn Magnataur Crusher")],
        story="Hagatha's tale of Ursoc's children, the bears of the den.")
    return e


def sholazar_quests(book, lantern):
    s = Z_SHOLAZAR
    a = book.quest(
        9105380, "Emperor Cobras", 75, 74, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice, hissing a little:$B$BIn the basin the cobras are emperors, little horror, "
        "and they know it. Every serpent that sheds long enough stands up one day; these ones are still deciding. "
        "Eat six. Your viper will learn to rule.",
        "Devour 6 Emperor Cobras in Sholazar Basin.",
        "Six cobras. They rule the mangal.",
        "Emperors, eaten. Your serpent wears a crown now.$B$BTake this.",
        objectives=[devour(6, "Emperor Cobra devoured", entries=[28011])], sort=s,
        choices=[(43891, "Jhaeqon's Tunic"), (42804, "Spiked Iceclimber's Boots"), (43915, "Pilot's Knife")],
        story="Hagatha's emperor cobras (the viper line).")
    b = book.quest(
        9105381, "Mangal Crocolisks", 75, 74, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, peering:$B$BSnack, the crocodiles in the mangal are GREEN and HUGE and they look like "
        "logs. Like the ones in Loch Modan, remember? But bigger. Eat five. Your komodo will feel very at home.",
        "Devour 5 Mangal Crocolisks in Sholazar Basin.",
        "Five crocolisks, Snack. Count the logs.",
        "Logs eaten! Your komodo says thank you.$B$BHere!",
        objectives=[devour(5, "Mangal Crocolisk devoured", entries=[28002])], prev=a.id, sort=s,
        choices=[(43906, "Cunning Leather Tunic"), (43894, "Gryphon Hide Moccasins"), (42861, "Jormungar Fang")],
        story="Wren's log-like crocolisks of the mangal (the komodo line).")
    c = book.quest(
        9105382, "Dreadsabers", 76, 74, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe dreadsabers of the basin hunt the hunters; Nesingwary's men are afraid "
        "of them, and they are not afraid of anything else. Eat five, little horror. Your saber has hunted in the "
        "dark and in the moonlight; now let it hunt the ones who hunt.",
        "Devour 5 dreadsabers in Sholazar Basin.",
        "Five dreadsabers. They hunt the hunters; you hunt them.",
        "Hunter of hunters. That is what you are.$B$BTake this.",
        objectives=[devour(5, "Dreadsaber devoured", entries=[28001])], prev=a.id, sort=s,
        choices=[(43889, "Hulking Abomination Hide Cloak"), (42812, "The \"D\" Ring"), (42862, "Hyldnir Painbringer")],
        story="Hagatha's dreadsabers that hunt the hunters (the saber line).")
    d = book.quest(
        9105383, "Hardknuckles", 76, 74, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, giggling:$B$BSnack, there are gorillas here called HARDKNUCKLES. That's the best name "
        "anything has ever had. Eat four. Then I'm naming my spoon Hardknuckle.",
        "Devour 4 hardknuckle gorillas in Sholazar Basin.",
        "Four hardknuckles, Snack. My spoon is waiting for its name.",
        "Spoon Hardknuckle! It's perfect.$B$BHere!",
        objectives=[devour(4, "Hardknuckle devoured", entries=[28098, 28096])], prev=b.id, sort=s,
        choices=[(39036, "Hulking Horror Tunic"), (39035, "Glacier-walker's Mukluks"), (43890, "Interrogator's Flaming Knuckles")],
        story="Wren names her spoon after the hardknuckle gorillas.")
    e = book.quest(
        9105384, "Primordial Drakes", 77, 75, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and the flame burns very old:$B$BIn the Savage Thicket, in the east of the "
        "basin, there are drakes from before anyone was keeping count. Primordial, the Oracles call them. Eat three, "
        "little horror. Your drake has eaten the young and the wild and the broken; let it eat the first.",
        "Devour 3 Primordial Drakes in the Savage Thicket, Sholazar Basin.",
        "Three primordial drakes. They are in the east of the basin.",
        "The first dragons, nearly. Your drake has eaten its whole history now.$B$BTake this, and go to the peaks.",
        objectives=[devour(3, "Primordial Drake devoured", entries=[28378])], prev=c.id, sort=s, xp=6,
        choices=[(43924, "Illskar's Greatcloak"), (42874, "Wooly Stompers"), (43929, "Vile's Uglystick")],
        story="Hagatha's primordial drakes, the first dragons nearly (the whelp line).")
    return e


def stormpeaks_quests(book, lantern):
    s = Z_STORMPEAKS
    a = book.quest(
        9105390, "Crystalweb", 77, 76, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, shivering:$B$BSnack, the spiders up there spin webs of CRYSTAL. Like frost on a "
        "window, but with legs. Eat five. They'll crunch like ice.",
        "Devour 5 crystalweb spiders in the Storm Peaks.",
        "Five crystal spiders, Snack. Crunch.",
        "Crunch! Like ice! I knew it.$B$BHere!",
        objectives=[devour(5, "Crystalweb spider devoured", entries=[29411, 29412])], sort=s,
        choices=[(43911, "Vile's Poker"), (42864, "Frozen Mood Ring"), (39130, "Corrupter's Shanker")],
        story="Wren's crystal-webbed spiders of the peaks.")
    b = book.quest(
        9105391, "Jormungar", 79, 77, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and the ground in the flame trembles:$B$BBelow the deepest mine there are "
        "tunnels no pick ever cut. The deep borers made them, looking for the heart of the world. Here, the "
        "jormungar dig through the ice the same way, as big as ships. Eat four, little horror. Your borer will "
        "learn to dig through anything.",
        "Devour 4 jormungar in the Storm Peaks.",
        "Four jormungar. Listen for the ice breaking.",
        "As big as ships, and gone. Your borer will dig to the heart of the world.$B$BTake this.",
        objectives=[devour(4, "Jormungar devoured", entries=[29605, 30291, 30422, 29390, 30148])], prev=a.id,
        sort=s,
        choices=[(43926, "Signet of Baron Sliver"), (43919, "Curved Assassin's Dagger"), (39036, "Hulking Horror Tunic")],
        story="Hagatha's tale of the deep borers; the jormungar dig through ice (the borer line).")
    c = book.quest(
        9105392, "Icemaw", 79, 77, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, impressed:$B$BSnack, the bears up there are ICEMAW bears and the vrykul RIDE them. "
        "Into battle! On bears! Eat four. Then you can tell the vrykul you're scarier than their bears.",
        "Devour 4 Icemaw bears in the Storm Peaks.",
        "Four icemaws, Snack.",
        "Scarier than bears! I'm putting that on a banner.$B$BHere!",
        objectives=[devour(4, "Icemaw bear devoured", entries=[29562])], prev=a.id, sort=s,
        choices=[(43906, "Cunning Leather Tunic"), (42848, "Razor-sharp Icicle"), (43894, "Gryphon Hide Moccasins")],
        story="Wren's battle bears of the vrykul.")
    d = book.quest(
        9105393, "Stormpeak Wyrms", 80, 78, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and thunder rolls through the flame:$B$BAt the top of the world the storm "
        "has children: stormpeak wyrms and their hatchlings, dragons of lightning and snow. This is where your drake "
        "has been going since the first whelp you swallowed, little horror. Eat four.",
        "Devour 4 stormpeak wyrms or hatchlings in the Storm Peaks.",
        "Four of the storm's children. Climb.",
        "Do you hear it? That is the storm, and it is in you.$B$BTake this. You are nearly at the end of my "
        "lanterns, little horror.",
        objectives=[devour(4, "Stormpeak wyrm devoured", entries=[29753, 29755])], prev=b.id, sort=s, xp=6,
        choices=[(43207, "Hardened Tongue Tunic"), (44397, "Handwraps of Preserved History"), (42859, "Thorim's Crusher")],
        story="Hagatha's storm wyrms at the top of the world (the Storm Dragon line).")
    book.quest(
        9105394, "The Storm Answers", 80, 80, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, very quietly:$B$BYou wear the storm now, little horror. A storm dragon, grown from a "
        "whelp in a marsh. I remember the whelp. Go and show the peaks what you became: wear your storm dragon and "
        "slay ten of the dragons and dragonkin of these mountains. Let them see what a Devourer grows into.",
        "As a Storm Dragon, slay 10 dragonkin in the Storm Peaks.",
        "Ten, little horror. In your storm.",
        "They saw. The whole sky saw.$B$BI have nothing left to teach you. Take this, and come and sit with us in "
        "the In-Between some evening. Wren will make soup. Do not eat Wren.",
        objectives=[slay(10, "Dragonkin slain as a Storm Dragon", ctype=T_DRAGON, shapes=STORM_DRAGON)],
        prev=d.id, sort=s, needs=STORM_DRAGON, xp=7,
        choices=[(44409, "Headguard of Retaliation"), (44405, "Exotic Leather Tunic"), (43207, "Hardened Tongue Tunic")],
        story="For a Devourer with the Storm Dragon: show the peaks what it became. Hagatha's last lantern quest.")
    return d
