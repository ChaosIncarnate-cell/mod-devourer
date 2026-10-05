"""Task 021: the lanterns of the twenties (levels 20-34). Part of tools/devourer_quests_content.py."""

from devourer_quests import devour, touch
from devourer_quests_content import LANTERN_OPEN
from devourer_quests_teens import onward, BAIT

Z_DUSKWOOD, Z_WETLANDS, Z_ASHENVALE, Z_HILLSBRAD, Z_STONETALON, Z_NEEDLES = 10, 11, 331, 267, 406, 400
CANDLE = 4152                                 # the look of the sisters' ritual candles

# Mounts from the mounts thread (tools/mounts/ascension/new_quests.txt); ground mounts, riding 75 at level 20.
HARVESTHOGS = (9304855, "Harvesthog pouch (one of four Harvesthogs)")
MARSH_HOPPERS = (9304918, "Marsh Hopper pouch (one of three Marsh Hoppers)")
FLORAL_SNAILS = (9304841, "Floral Snail pouch (one of four Floral Snails)")
FURLINE = (9304816, "Sunwarmed Furline pouch (ground)")


def twenties(book, teens):
    duskwood = book.lantern("duskwood", "Duskwood", 0, -10450.0, 100.0, 38.57, 2.5,
                            "the edge of Raven Hill Cemetery")
    wetlands = book.lantern("wetlands", "Wetlands", 0, -3300.0, -2400.0, 22.64, 1.4, "the marsh north of Thelgen Rock")
    ashenvale = book.lantern("ashenvale", "Ashenvale", 1, 2400.0, -1000.0, 99.85, 0.3, "the woods south-east of Astranaar")
    hillsbrad = book.lantern("hillsbrad", "Hillsbrad Foothills", 0, -200.0, -1100.0, 36.99, 5.2,
                             "the hills south-east of Tarren Mill")
    stonetalon = book.lantern("stonetalon", "Stonetalon Mountains", 1, 1700.0, 650.0, 194.97, 3.8,
                              "the high pass north-east of Mirkfallon Lake")
    needles = book.lantern("needles", "Thousand Needles", 1, -5000.0, -1800.0, -57.74, 4.6,
                           "the canyon floor below Darkcloud Pinnacle")

    book.region("The lanterns of the twenties (levels 20-34)",
                "Six lanterns between the first molts and the long roads: the whelp and the turtle shapes begin here, "
                "Hagatha's bait calls Lupos and Nal'taszar, and the first ground mounts from the witches' stable are "
                "rewards.")

    def onto(key, qid, target, line):
        lantern, finale = teens[key]
        onward(book, qid, 20, lantern, target, finale.id, line)

    onto("westfall", 9105109, duskwood, "East of the farms the woods go dark and stay dark.")
    onto("lochmodan", 9105119, wetlands, "North of the tunnel the land turns to marsh, and the marsh has teeth.")
    onto("darkshore", 9105129, ashenvale, "South of you the forest is old and full of things that remember.")
    onto("bloodmyst", 9105139, ashenvale, "Take the boat west; the forest of Ashenvale is old and full of "
                                          "things that remember.")
    onto("barrens", 9105149, stonetalon, "West of the Barrens the mountains climb into the clouds, and so do the "
                                         "wyverns.")
    onto("silverpine", 9105159, hillsbrad, "South of the pines the hills roll down to the sea, and the bears "
                                           "roll with them.")
    onto("ghostlands", 9105169, hillsbrad, "Go south, through the Plaguelands if you must, to the green hills of "
                                           "Hillsbrad.")

    return {
        "duskwood": (duskwood, duskwood_quests(book, duskwood)),
        "wetlands": (wetlands, wetlands_quests(book, wetlands)),
        "ashenvale": (ashenvale, ashenvale_quests(book, ashenvale)),
        "hillsbrad": (hillsbrad, hillsbrad_quests(book, hillsbrad)),
        "stonetalon": (stonetalon, stonetalon_quests(book, stonetalon)),
        "needles": (needles, needles_quests(book, needles)),
    }


def duskwood_quests(book, lantern):
    s = Z_DUSKWOOD
    candles = book.thing("raven_candles", "Unlit Grave Candle", CANDLE,
                         [(0, -10560.0, 250.0, 29.96, 0.0), (0, -10520.0, 330.0, 28.74, 1.0),
                          (0, -10480.0, 250.0, 30.8, 2.0), (0, -10540.0, 290.0, 30.24, 3.0)])
    lupos = book.thing("lupos_bait", "Hagatha's Bait", BAIT, [(0, -10185.0, -55.0, 27.81, 0.0)], size=0.7, summon=521)
    a = book.quest(
        9105170, "Dire Wolves", 20, 19, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice, pleased with the dark:$B$BDuskwood was a forest once, little horror, before "
        "the night came and would not leave. The wolves stayed. They starved, and then they went mad, and now "
        "they are dire. Eat six of the starving ones and the rabid ones along the Darkened Bank. A wolf that has "
        "eaten madness does not go mad itself. It learns to use it.",
        "Devour 6 dire wolves in Duskwood.",
        "Six wolves. They are easy to find; they want to find you.",
        "Mad, and hungry, and now part of you. Use it, do not let it use you.$B$BTake this.",
        objectives=[devour(6, "Dire wolf devoured", entries=[213, 565])], sort=s,
        choices=[(17005, "Boorguard Tunic"), (5355, "Beastmaster's Girdle"), (15464, "Brute Hammer")],
        story="Hagatha teaches the madness of Duskwood's starving dire wolves.")
    b = book.quest(
        9105171, "Candles for the Thin Places", 22, 20, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice turns careful:$B$BRaven Hill Cemetery is a thin place, little horror. The "
        "world is worn there, like cloth at the elbow, and things push through from the other side. I have left "
        "four candles among the graves. Light them for me; touch each one and the flame will know my hand through "
        "yours.$B$BDo not mind the dead. They mind you more.",
        "Light 4 Unlit Grave Candles in Raven Hill Cemetery, Duskwood.",
        "Some of my candles are still dark.",
        "Four flames. Now the thin place is watched, and what pushes through will find me waiting.$B$BTake this "
        "for your trouble; you walked among the graves for an old woman's candles.",
        objectives=[touch(candles, 4, "Grave candle lit")], prev=a.id, sort=s,
        choices=[(16659, "Deftkin Belt"), (6752, "Lancer Boots"), (6748, "Monkey Ring")],
        story="Hagatha has the Devourer light her candles among the graves of Raven Hill, a thin place.")
    c = book.quest(
        9105172, "Ravagers and Widows", 24, 22, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, whispering because it's spooky:$B$BSnack, the woods round you have black ravagers. "
        "They're wolves that are also, I think, nightmares? And black widow hatchlings, which are SPIDERS, which "
        "are babies, which is somehow worse.$B$BEat four ravagers and three hatchlings. I'll keep the lantern "
        "turned up so you can see.",
        "Devour 4 Young Black Ravagers and 3 Black Widow Hatchlings in Duskwood.",
        "Four ravagers, three hatchlings. I'm still whispering, Snack.",
        "You did it! I can stop whispering. I'm STILL whispering. It's a habit now.$B$BHere!",
        objectives=[devour(4, "Young Black Ravager devoured", entries=[923]),
                    devour(3, "Black Widow Hatchling devoured", entries=[930])], prev=b.id, sort=s,
        choices=[(10653, "Trailblazer Boots"), (6719, "Windborne Belt"), (6093, "Orc Crusher")],
        story="Wren whispers about Duskwood's nightmare wolves and spider babies.")
    d = book.quest(
        9105173, "Lupos", 25, 23, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and the flame goes pale as a ghost:$B$BThere is a wolf in Duskwood that the "
        "night does not touch. It shines. The hunters of Darkshire call it Lupos, and they say it was the first "
        "wolf to die when the night came, and it did not notice. It walks the Darkened Bank in the north and is "
        "almost never seen.$B$BI left a bait on the bank. Touch it. When Lupos comes, eat a wolf that does not "
        "know it is dead.",
        "Devour Lupos in Duskwood. Hagatha's Bait, on the Darkened Bank, will call it.",
        "The shining wolf still walks. Touch my bait.",
        "Did it taste of anything? No. It had forgotten how.$B$BWren found something in my pumpkin patch while you "
        "were gone, and she says it is yours. Hedgehogs, little horror. Big ones. You can ride them. I do not "
        "understand my sister, but take them.",
        objectives=[devour(1, "Lupos devoured", entries=[521])], prev=c.id, sort=s, xp=6, lures=[lupos],
        items=[(HARVESTHOGS[0], HARVESTHOGS[1], 1)],
        choices=[(6745, "Swiftrunner Cape"), (3754, "Shepherd's Gloves"), (24118, "Signet of Argas")],
        story="Hagatha's bait calls Lupos, the wolf that died and did not notice. Reward: a Harvesthog mount.")
    return d


def wetlands_quests(book, lantern):
    s = Z_WETLANDS
    a = book.quest(
        9105180, "Young Crocolisks", 21, 20, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice, wet and low:$B$BThe Wetlands are a nursery for crocolisks, little horror. "
        "The young ones crowd the shallows and wait to grow. Eat six of the young and two of the grown. A komodo "
        "grows on patience, and the young are all patience and no teeth yet.",
        "Devour 6 Young Wetlands Crocolisks and 2 Wetlands Crocolisks.",
        "The shallows are still crowded.",
        "Patient little things. Now your komodo is patient too.$B$BTake this.",
        objectives=[devour(6, "Young Wetlands Crocolisk devoured", entries=[1417]),
                    devour(2, "Wetlands Crocolisk devoured", entries=[1400])], sort=s,
        choices=[(17005, "Boorguard Tunic"), (2033, "Ambassador's Boots"), (5322, "Demolition Hammer")],
        story="Hagatha sends the Devourer into the crocolisk nursery of the Wetlands.")
    b = book.quest(
        9105181, "Raptors of the Highlands", 24, 22, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, breathless:$B$BSnack, I counted the raptors in the Wetlands. I got to forty and a "
        "frog jumped on the lantern and I lost count. There are LOTS. Mottled ones in the marsh and highland ones "
        "in the hills.$B$BEat five and I'll start counting again from thirty-five.",
        "Devour 5 Wetlands raptors.",
        "Still lots of raptors, Snack.",
        "Thirty-five! Thirty-six... no, wait, you ate them, they don't count. Thirty-five.$B$BHere!",
        objectives=[devour(5, "Wetlands raptor devoured", entries=[1020, 1015, 1016, 1021, 1022, 1017])],
        prev=a.id, sort=s,
        choices=[(7751, "Vorrel's Boots"), (6719, "Windborne Belt"), (6749, "Tiger Band")],
        story="Wren lost count of the Wetlands raptors.")
    c = book.quest(
        9105182, "Whelps of the Green Belt", 25, 23, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice warms, as if over a fire:$B$BIn the hills of the Green Belt, east of here, "
        "the red dragons lost some of their children. Lost whelps, red whelps, crimson whelps: little dragons with "
        "nobody to tell them what they are.$B$BEat six, little horror. If the whelp's shape is not yours yet, it "
        "will be. And a whelp is the beginning of everything with wings and fire.",
        "Devour 6 whelps in the Wetlands.",
        "Six whelps. They are lost; they will not run far.",
        "Fire in the belly. Do you feel it? That is the first step of a long road: whelp, drake, storm.$B$BTake "
        "this.",
        objectives=[devour(6, "Wetlands whelp devoured", entries=[1042, 1043, 1069])], prev=b.id, sort=s,
        choices=[(3754, "Shepherd's Gloves"), (2953, "Watch Master's Cloak"), (24119, "Band of Argas")],
        story="Hagatha sends the Devourer to the lost red whelps: the start of the Whelp shape.")
    d = book.quest(
        9105183, "Flamesnorting", 27, 25, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, giggling:$B$BSnack, there are whelps that SNORT FIRE. On purpose! Like little "
        "kettles! Flamesnorting whelps, out east past the others. And Hagatha says the giant crocolisks down in "
        "Sundown Marsh are as old as she is, which I told her is impossible, and she threw a spoon at me.$B$BEat "
        "three snorty whelps and two giant crocs. For me and the spoon.",
        "Devour 3 Flamesnorting Whelps and 2 Giant Wetlands Crocolisks.",
        "Three snorters, two giants. The spoon is waiting.",
        "Snort! I'm doing the whelp noise. Snort snort.$B$BAnd look what I found in the marsh behind the cauldron: "
        "marsh hoppers! Big friendly frogs you can SIT on. One's yours. I named it. You can rename it, but you "
        "shouldn't.",
        objectives=[devour(3, "Flamesnorting Whelp devoured", entries=[1044]),
                    devour(2, "Giant Wetlands Crocolisk devoured", entries=[2089])], prev=c.id, sort=s, xp=6,
        items=[(MARSH_HOPPERS[0], MARSH_HOPPERS[1], 1)],
        choices=[(9699, "Garrison Cloak"), (10653, "Trailblazer Boots"), (6748, "Monkey Ring")],
        story="Wren's snorting whelps and old crocolisks. Reward: a Marsh Hopper mount.")
    return d


def ashenvale_quests(book, lantern):
    s = Z_ASHENVALE
    a = book.quest(
        9105190, "Ghostpaw", 20, 19, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and the leaves seem to listen:$B$BThe wolves of Ashenvale are called "
        "ghostpaws, because they walk so softly the night elves thought them spirits. They are not spirits, little "
        "horror. They are only quiet. Eat six of them and learn the difference.",
        "Devour 6 Ghostpaw wolves in Ashenvale.",
        "Six ghostpaws. Quiet things; be quieter.",
        "Not spirits. Meat. Remember that when the night elves tell you stories.$B$BTake this.",
        objectives=[devour(6, "Ghostpaw devoured", entries=[3823, 3824])], sort=s,
        choices=[(6670, "Panther Armor"), (15462, "Loamflake Bracers"), (1264, "Headbasher")],
        story="Hagatha teaches the soft walk of Ashenvale's ghostpaw wolves.")
    b = book.quest(
        9105191, "Antler and Fur", 23, 21, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, enthusiastic:$B$BSnack! Ashenvale has the prettiest deer. Shadowhorn stags! I'd love "
        "one as a pet, but Hagatha says no pets bigger than the cauldron. So you eat them and I'll draw one from "
        "memory. Four stags. And four bears, because bears are cuddly and I can't have one of those either.",
        "Devour 4 shadowhorn stags and 4 Ashenvale bears.",
        "Four stags, four bears. My drawing's still blank.",
        "I drew a stag! It looks like a chair. A lovely chair.$B$BHere!",
        objectives=[devour(4, "Shadowhorn stag devoured", entries=[3817, 3818]),
                    devour(4, "Ashenvale bear devoured", entries=[3809, 3810])], prev=a.id, sort=s,
        choices=[(7751, "Vorrel's Boots"), (5355, "Beastmaster's Girdle"), (6749, "Tiger Band")],
        story="Wren can't have a pet stag or a pet bear, so the Devourer eats them.")
    c = book.quest(
        9105192, "Satyr Horns", 27, 25, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice hardens:$B$BThe satyrs were night elves once. They sold their shape for "
        "power, little horror, and got horns for it. A bad bargain; you would never make a bad bargain for a shape. "
        "They gather at Night Run and Satyrnaar in the east of the forest.$B$BEat five of them. A cat that eats "
        "satyrs learns to hunt in silence, the way they never could.",
        "Devour 5 Felmusk or Bleakheart satyrs in Ashenvale.",
        "Five satyrs. They are loud; follow the noise.",
        "Bitter, wasn't it? That is the taste of a shape bought cheap.$B$BTake this.",
        objectives=[devour(5, "Satyr devoured",
                           entries=[3758, 3763, 3762, 3759, 3765, 3770, 3767, 3771])], prev=b.id, sort=s,
        choices=[(2953, "Watch Master's Cloak"), (3754, "Shepherd's Gloves"), (24118, "Signet of Argas")],
        story="Hagatha's tale of the satyrs who sold their shape (a Shadowclaw task).")
    d = book.quest(
        9105193, "The Voidcallers of Althalaxx", 28, 26, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and the flame shrinks away from something:$B$BNorth of here, in Darkshore, "
        "the Twilight's followers call the void at the Tower of Althalaxx. The dark strand voidcallers, they name "
        "themselves. Fools who knock on a door and do not wonder what will open it.$B$BEat three of them, little "
        "horror. A voidcreeper that has eaten the ones who call the void becomes the mother of what answers.",
        "Devour 3 Dark Strand Voidcallers at the Tower of Althalaxx in Darkshore.",
        "They are still knocking on the door.",
        "Quiet now, the tower. Your voidcreeper heard every knock.$B$BWren left you a present. She grew snails in "
        "the cauldron again, the flowered ones, big enough to ride. Slowly. Take one, and do not let her grow any "
        "more.",
        objectives=[devour(3, "Dark Strand Voidcaller devoured", entries=[2337])], prev=c.id, sort=s, xp=6,
        items=[(FLORAL_SNAILS[0], FLORAL_SNAILS[1], 1)],
        choices=[(6745, "Swiftrunner Cape"), (9687, "Grappler's Belt"), (6748, "Monkey Ring")],
        story="Hagatha sends the Devourer after the voidcallers of Althalaxx (a Voidcreeper Broodmother task). "
              "Reward: a Floral Snail mount.")
    return d


def hillsbrad_quests(book, lantern):
    s = Z_HILLSBRAD
    a = book.quest(
        9105200, "Gray Bears", 21, 20, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, mild:$B$BThe gray bears of Hillsbrad are old and slow and very, very strong. Eat "
        "six of them, little horror. Not every lesson is about speed.",
        "Devour 6 gray bears in Hillsbrad Foothills.",
        "Six bears. They are slow; do not make me wait longer than they do.",
        "Heavy, warm, patient. A good meal for a cold night.$B$BTake this.",
        objectives=[devour(6, "Gray bear devoured", entries=[2351, 2354, 2356])], sort=s,
        choices=[(17005, "Boorguard Tunic"), (6668, "Draftsman Boots"), (5322, "Demolition Hammer")],
        story="Hagatha teaches the strength of Hillsbrad's old gray bears.")
    b = book.quest(
        9105201, "Moss Creepers", 24, 22, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, horrified:$B$BSnack, the spiders there are covered in MOSS. They're growing a "
        "garden on their backs. That's MY thing. I grow gardens. Eat six of the moss creepers before they start "
        "growing herbs.",
        "Devour 6 moss creepers in Hillsbrad Foothills.",
        "Six creepers, Snack. They're planting tomatoes, probably.",
        "No more spider gardens! Mine are the only gardens again.$B$BHere!",
        objectives=[devour(6, "Moss creeper devoured", entries=[2350, 2349, 2348])], prev=a.id, sort=s,
        choices=[(10653, "Trailblazer Boots"), (16659, "Deftkin Belt"), (6749, "Tiger Band")],
        story="Wren is jealous of the moss creepers' gardens.")
    c = book.quest(
        9105202, "Mountain Lions", 26, 24, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe mountain lions came down from Alterac when the ogres took the "
        "mountains. They are starving, little horror, and starving cats are honest hunters. Eat five of them, the "
        "starving ones and the feral ones in the south.",
        "Devour 5 mountain lions in Hillsbrad Foothills.",
        "Five lions. They are hungry too.",
        "Honest hunger, again. You will meet it often.$B$BWren has something for you. She says it is a cat. It is "
        "much too big to be a cat. You can ride it.",
        objectives=[devour(5, "Mountain lion devoured", entries=[2384, 2385])], prev=b.id, sort=s,
        items=[(FURLINE[0], FURLINE[1], 1)],
        choices=[(2953, "Watch Master's Cloak"), (3754, "Shepherd's Gloves"), (24118, "Signet of Argas")],
        story="Hagatha's starving mountain lions. Reward: a Sunwarmed Furline mount.")
    d = book.quest(
        9105203, "Snapjaws of Lordamere", 30, 28, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, slow as a turtle:$B$BAlong the shore of Lordamere Lake, to the north, the snapjaws "
        "lie in the sun. Old turtles, little horror, with jaws that close and do not open again. Eat four of them. "
        "If the turtle's shape is not yours yet, it will be, and turtles live a very long time.",
        "Devour 4 Snapjaws on the shore of Lordamere Lake.",
        "Four snapjaws. They will not come to you; turtles never do.",
        "A shell in the belly. Now, when the world bites you, you will bite back from inside it.$B$BTake this.",
        objectives=[devour(4, "Snapjaw devoured", entries=[2408])], prev=c.id, sort=s, xp=6,
        choices=[(4107, "Tiger Hunter Gloves"), (33249, "Boots of the Skirmisher"), (33267, "Fleshripper")],
        story="Hagatha sends the Devourer after the snapjaw turtles: the start of the Snapjaw shape.")
    return d


def stonetalon_quests(book, lantern):
    s = Z_STONETALON
    nal = book.thing("naltaszar_bait", "Hagatha's Bait", BAIT, [(1, 2530.0, 1985.0, 415.74, 0.0)], size=0.7,
                     summon=4066)
    a = book.quest(
        9105210, "Deepmoss", 20, 19, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, from under a blanket:$B$BSnack, the spiders in the Windshear Crag are called DEEPMOSS "
        "and they SPIT. I'm hiding until you've eaten six of them. I've got biscuits under here. I'll save you one.",
        "Devour 6 Deepmoss spiders in Stonetalon Mountains.",
        "Still under the blanket, Snack.",
        "I'm out! Here's your biscuit. I ate half. Here's the other half of a prize, too.",
        objectives=[devour(6, "Deepmoss spider devoured", entries=[4007, 4006])], sort=s,
        choices=[(6670, "Panther Armor"), (2033, "Ambassador's Boots"), (15464, "Brute Hammer")],
        story="Wren hides under a blanket from the spitting Deepmoss spiders.")
    b = book.quest(
        9105211, "Pridewings", 23, 21, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe pridewings of Stonetalon are wyverns, little horror: lion, bat and "
        "scorpion, stitched together by a world that could not make up its mind. They nest around Mirkfallon Lake. "
        "Eat five of them. A thing that is three things at once is a good lesson for a thing like you.",
        "Devour 5 pridewings in Stonetalon Mountains.",
        "Five pridewings. They fly, but they come down to feed.",
        "Three things at once. You are a hundred. Never forget which one you are wearing.$B$BTake this.",
        objectives=[devour(5, "Pridewing devoured", entries=[4012, 4014, 4013, 4011])], prev=a.id, sort=s,
        choices=[(6752, "Lancer Boots"), (6719, "Windborne Belt"), (24119, "Band of Argas")],
        story="Hagatha's lesson of the stitched-together pridewing wyverns.")
    c = book.quest(
        9105212, "Charred Basilisks", 26, 24, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, chewing:$B$BSnack, the basilisks in the Charred Vale got cooked when the forest "
        "burned. They're still walking around, but they're CRISPY. Crispy basilisk! Eat four for me. Tell me if "
        "they're crispy all the way through.",
        "Devour 4 basilisks in the Charred Vale, Stonetalon Mountains.",
        "Four crispy basilisks, Snack.",
        "Crispy all the way through? I KNEW it.$B$BHere, a crispy prize.",
        objectives=[devour(4, "Charred Vale basilisk devoured", entries=[4044, 4042, 4041])], prev=b.id, sort=s,
        choices=[(9699, "Garrison Cloak"), (7751, "Vorrel's Boots"), (6748, "Monkey Ring")],
        story="Wren wants to know if the burned basilisks are crispy.")
    d = book.quest(
        9105213, "Nal'taszar", 30, 28, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice grows teeth:$B$BHigh on Stonetalon Peak a drake makes its lair: Nal'taszar, "
        "a wild thing of the old flights, too proud to serve and too old to die. It comes down from the peak once "
        "in a long while.$B$BI left a bait near the summit, in the north of the mountains. Touch it, and "
        "Nal'taszar will come down for it. Eat it, little horror. A whelp that has eaten a wild drake remembers "
        "what dragons were before anyone tamed them.",
        "Devour Nal'taszar on Stonetalon Peak. Hagatha's Bait, near the summit, will call it.",
        "The drake is still on its peak. Touch my bait.",
        "Wild and proud, and now yours. Your whelp has tasted the proto-drake it will become.$B$BTake this.",
        objectives=[devour(1, "Nal'taszar devoured", entries=[4066])], prev=c.id, sort=s, xp=6, lures=[nal],
        choices=[(4107, "Tiger Hunter Gloves"), (15456, "Lightstep Leggings"), (33268, "Bone Dirk")],
        story="Hagatha's bait calls Nal'taszar, the wild drake of Stonetalon Peak (a Proto-Drake task).")
    return d


def needles_quests(book, lantern):
    s = Z_NEEDLES
    a = book.quest(
        9105220, "Pesterhide", 26, 25, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, annoyed:$B$BSnack, the hyenas down there are called PESTERHIDE. They named themselves "
        "after what they do! They follow travellers and laugh at them. Eat six. Nobody laughs at my Snack.",
        "Devour 6 Pesterhide hyenas in Thousand Needles.",
        "Six hyenas. They're still laughing, Snack.",
        "No more laughing! Except mine. HA.$B$BHere!",
        objectives=[devour(6, "Pesterhide hyena devoured", entries=[4248, 4249])], sort=s,
        choices=[(9699, "Garrison Cloak"), (6752, "Lancer Boots"), (6093, "Orc Crusher")],
        story="Wren won't have the Pesterhide hyenas laughing at her Snack.")
    b = book.quest(
        9105221, "Cloud Serpents", 27, 26, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, and somewhere in the flame the wind howls:$B$BA snake that swallows enough storms "
        "grows wings to carry them. The cloud serpents of the Needles are what that looks like, little horror. "
        "They coil around the spires. Eat five of them. Your snake, or your eagle, will learn what it is to be both "
        "at once.",
        "Devour 5 cloud serpents in Thousand Needles.",
        "Five serpents. They coil around the needles.",
        "Did you taste the storm? It is still in you. Your Baby Wind Serpent will feel it.$B$BTake this.",
        objectives=[devour(5, "Cloud serpent devoured", entries=[4117, 4118, 4119])], prev=a.id, sort=s,
        choices=[(3754, "Shepherd's Gloves"), (9687, "Grappler's Belt"), (24119, "Band of Argas")],
        story="Hagatha's tale of the snake that swallowed storms: five cloud serpents (the wind serpent line).")
    c = book.quest(
        9105222, "Sparkleshell", 31, 29, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, delighted:$B$BSnack! The turtles on the Shimmering Flats SPARKLE. Sparkleshell "
        "tortoises and snappers! Hagatha says sparkly things are bad luck to eat. I say she's jealous because her "
        "cauldron doesn't sparkle.$B$BEat five. Find out who's right.",
        "Devour 5 Sparkleshell turtles on the Shimmering Flats.",
        "Five sparkly turtles, Snack.",
        "No bad luck? I WIN. Hagatha's polishing her cauldron now. Out of spite.$B$BHere!",
        objectives=[devour(5, "Sparkleshell turtle devoured", entries=[4142, 4143, 4144])], prev=b.id, sort=s,
        choices=[(33249, "Boots of the Skirmisher"), (33250, "Archer's Wristguard"), (4978, "Ryedol's Hammer")],
        story="Wren and Hagatha argue over whether sparkly turtles are bad luck (the turtle line).")
    d = book.quest(
        9105223, "The Shimmering Flats", 33, 31, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, dry as the salt:$B$BOn the Shimmering Flats the scorpids grow as big as "
        "carts, and the goblins race their machines over the bones of the ones the scorpids caught. Eat four of "
        "the reavers and terrors, little horror, and two of the saltstone basilisks that stare at nothing. The salt "
        "keeps them; it will keep you.",
        "Devour 4 scorpids and 2 saltstone basilisks on the Shimmering Flats.",
        "The scorpids still guard the salt.",
        "Salt and venom. A dry meal, but a long-keeping one.$B$BTake this, and go south when you are ready.",
        objectives=[devour(4, "Shimmering Flats scorpid devoured", entries=[4140, 4139]),
                    devour(2, "Saltstone basilisk devoured", entries=[4147, 4151, 4150])], prev=c.id, sort=s,
        xp=6,
        choices=[(33243, "Skirmisher's Cover"), (4108, "Panther Hunter Leggings"), (33261, "Destroyer's Cloak")],
        story="Hagatha sends the Devourer over the salt for scorpids and staring basilisks.")
    return d
