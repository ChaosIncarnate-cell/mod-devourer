"""Task 021: the lanterns of the twenties (levels 20-34). Part of tools/devourer_quests_content.py."""

from devourer_quests import devour, slay, trail, struck, among, visit, tale, ability, LINES
from devourer_quests_content import mercy, FACTION_SHY
from devourer_quests_teens import onward, campfire, BAIT

Z_DUSKWOOD, Z_WETLANDS, Z_ASHENVALE, Z_HILLSBRAD, Z_STONETALON, Z_NEEDLES = 10, 11, 331, 267, 406, 400


def twenties(book, teens):
    duskwood = book.lantern("duskwood", "Duskwood", 0, -10450.0, 100.0, 38.57, 2.5,
                            "the edge of Raven Hill Cemetery")
    wetlands = book.lantern("wetlands", "the Wetlands", 0, -3300.0, -2400.0, 22.64, 1.4,
                            "the marsh north of Thelgen Rock")
    ashenvale = book.lantern("ashenvale", "Ashenvale", 1, 2400.0, -1000.0, 99.85, 0.3, "the woods south-east of Astranaar")
    hillsbrad = book.lantern("hillsbrad", "Hillsbrad Foothills", 0, -200.0, -1100.0, 36.99, 5.2,
                             "the hills south-east of Tarren Mill")
    stonetalon = book.lantern("stonetalon", "Stonetalon Mountains", 1, 1700.0, 650.0, 194.97, 3.8,
                              "the high pass north-east of Mirkfallon Lake")
    needles = book.lantern("needles", "Thousand Needles", 1, -5000.0, -1800.0, -57.74, 4.6,
                           "the canyon floor below Darkcloud Pinnacle")

    book.region("The lanterns of the twenties (levels 20-34)",
                "Six lanterns between the first molts and the long roads: the whelp and the turtle shapes begin here, "
                "the Devourer sniffs out Lupos, the Boat-Eater's cousins and Nal'taszar, and walks among whelps and "
                "snapjaws as one of them.")

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
    fire = campfire(book, "duskwood_fire", lantern, 6.0, 6.0, 37.0, [
        "Sit close, little horror. Bramble, closer still. Duskwood does not like a small fire.",
        "This was a bright wood once. Elwynn's sister. Deer, and woodcutters, and a road with flowers on it.",
        "Then something old woke under Karazhan, and the night came to look at what had woken it.",
        "The night looked, and looked, and forgot to leave.",
        "The woodcutters left instead. The ones who stayed became what lives here now.",
        "The night is not cruel, you understand. It is only curious, and it has nowhere else to be.",
        "Like you, little horror. Be curious. But always have somewhere else to be."],
        "Bramble pulls her knees up. \"I'll be somewhere else. Somewhere with lamps.\"")
    a = book.quest(
        9105170, "Dire Wolves", 20, 19, lantern, lantern, "hagatha",
        "Hagatha's voice, pleased with the dark:$B$BDuskwood was a forest once, little horror, before the night came "
        "and would not leave. The wolves stayed. They starved, and then they went mad, and now they are dire. Eat "
        "six of the starving ones and the rabid ones. A wolf that has eaten madness does not go mad itself. It learns "
        "to use it.",
        "Devour 6 dire wolves in Duskwood.",
        "Six wolves. They are easy to find; they want to find you.",
        "Mad, and hungry, and now part of you. Use it, do not let it use you.$B$BTake this. It was going to waste.",
        objectives=[devour(6, "Dire wolf devoured", entries=[213, 565])], sort=s,
        choices=[(17005, "Boorguard Tunic"), (5355, "Beastmaster's Girdle"), (15464, "Brute Hammer")],
        story="The lesson: the madness of Duskwood's starving dire wolves.")
    b = book.quest(
        9105171, "The Night That Stayed", 21, 20, lantern, lantern, "hagatha",
        "Hagatha's voice turns careful:$B$BI have given your little friend a tale to carry. Duskwood "
        "has a tale, little horror, and it should be told to two at once, so that one of you can keep watch while "
        "the other listens. Sit with her by any fire, and let her tell it.",
        "Sit by any campfire or inn fire with Bramble for a while, and hear Hagatha's tale to its end.",
        "Any fire will do. Do not keep the night waiting.",
        "Now you know why it is dark here. Most people who live here never ask.$B$BTake this, for listening.",
        objectives=[tale(fire, "The tale of the night that stayed heard")], prev=a.id, sort=s, xp=4,
        choices=[(16659, "Deftkin Belt"), (6752, "Lancer Boots"), (6748, "Monkey Ring")],
        story="A campfire tale for the Devourer and Bramble: why the night came to Duskwood and never left.")
    d = book.quest(
        9105173, "Lupos", 25, 23, lantern, lantern, "hagatha",
        "Hagatha tells it, and the flame goes pale as a ghost:$B$BThere is a wolf in Duskwood that the night does not "
        "touch. It shines. The hunters of Darkshire call it Lupos, and they say it was the first wolf to die when the "
        "night came, and it did not notice.$B$BA dead thing has a smell, little horror, even one that shines: cold "
        "earth and moonlight. Turn on your Sniff by the lantern and follow it north-east to the Darkened Bank. When "
        "Lupos comes, eat a wolf that does not know it is dead.",
        "Follow Lupos's scent with Sniff to the Darkened Bank, then devour Lupos.",
        "The shining wolf still walks. Follow the moonlight.",
        "Did it taste of anything? No. It had forgotten how.$B$BTake this. Your wolf will never forget.",
        objectives=[trail("Lupos's scent followed", "Lupos", 0, [(-10365, 60), (-10260, 0), (-10185, -45)],
                          summon=521),
                    devour(1, "Lupos devoured", entries=[521])], prev=b.id, sort=s, xp=6,
        choices=[(6745, "Swiftrunner Cape"), (3754, "Shepherd's Gloves"), (24118, "Signet of Argas")],
        story="Sniff out Lupos, the shining wolf that died and did not notice, and eat him.")
    book.quest(
        9105175, "Roots for the Restless", 22, 20, lantern, lantern, "hagatha",
        "Hagatha, half asleep:$B$BYour bear cub grew into a dreambear, little horror: leaves where fur should be, and "
        "roots in every paw. The dire wolves of this wood have not rested since the night came.$B$BWear your "
        "dreambear and maul five of them so that roots grow where they stand. Rooted things are quieter. Then let "
        "them be.",
        "As a Dreambear, root 5 dire wolves in Duskwood with Overgrowth.",
        "Five wolves, little horror, rooted.",
        "Rooted, and quiet, for a while. That is more rest than the night has given them in years.$B$BTake this.",
        objectives=[ability(5, "Dire wolf rooted as a Dreambear", 9102314, entries=[213, 565], shapes=(47,))],
        prev=a.id, sort=s, needs=(47,),
        choices=[(16659, "Deftkin Belt"), (6752, "Lancer Boots"), (6748, "Monkey Ring")],
        story="For a Devourer with the Dreambear: Overgrowth on five of Duskwood's restless dire wolves.")
    return d


def wetlands_quests(book, lantern):
    s = Z_WETLANDS
    a = book.quest(
        9105180, "Young Crocolisks", 21, 20, lantern, lantern, "hagatha",
        "Hagatha's voice, wet and low:$B$BThe Wetlands are a nursery for crocolisks, little horror. The young ones "
        "crowd the shallows and wait to grow. Eat six of them. A komodo grows on patience, and the young are all "
        "patience and no teeth yet.",
        "Devour 6 Young Wetlands Crocolisks.",
        "The shallows are still crowded.",
        "Patient little things. Now your komodo is patient too.$B$BThis is yours now.",
        objectives=[devour(6, "Young Wetlands Crocolisk devoured", entries=[1417])], sort=s,
        choices=[(17005, "Boorguard Tunic"), (2033, "Ambassador's Boots"), (5322, "Demolition Hammer")],
        story="The lesson: the crocolisk nursery of the Wetlands.")
    b = book.quest(
        9105181, "A Whelp Among Whelps", 24, 22, lantern, lantern, "hagatha",
        "Hagatha's voice warms, as if over a fire:$B$BIn the hills of the Green Belt, east of here, the red dragons "
        "lost some of their children. Lost whelps, red whelps, crimson whelps: little dragons with nobody to tell "
        "them what they are.$B$BWear your whelp, little horror, and go and sit among them. They will think you are "
        "another one the flight forgot. Tell them nothing. Just be a whelp for a while, with others of your kind.",
        "Wearing your Whelp (or what it grew into), walk among the lost whelps of the Green Belt without starting a "
        "fight.",
        "They are waiting for one more lost one.",
        "Did they curl up around you? Whelps do that, when they are cold. Now you know what it is to have a "
        "flight.$B$BHere. It fits a shape like yours.",
        objectives=[among("Sat among the lost whelps", 0, -3500.0, -3100.0, [1042, 1043, 1069, 1044],
                          LINES["whelp"], radius=25.0)],
        prev=a.id, sort=s, needs=LINES["whelp"],
        choices=[(3754, "Shepherd's Gloves"), (2953, "Watch Master's Cloak"), (24119, "Band of Argas")],
        story="For a Devourer with the Whelp shape: sit among the red flight's lost whelps as one of them.")
    c = book.quest(
        9105182, "Flamesnorting", 25, 23, lantern, lantern, "wren",
        "Wren, giggling:$B$BSnack, there are whelps that SNORT FIRE. On purpose! Like little kettles! The "
        "flamesnorting whelps, out in the Green Belt with the others. Bramble says she doesn't believe in whelps that snort fire. Take her! Eat four where she can see, "
        "and watch her face. Snort snort.",
        "With Bramble watching, devour 4 flamesnorting whelps in the Wetlands.",
        "Four whelps, Snack, and Bramble has to see them snort.",
        "Snort! I'm doing the whelp noise. Snort snort. Bramble believes in them now. She's a little singed.$B$BHere! You earned it!",
        objectives=[devour(4, "Flamesnorting Whelp devoured, Bramble watching", entries=[1044],
                           companion="It SNORTED. Fire! Out of its NOSE. I take it all back.")], prev=a.id, sort=s,
        choices=[(7751, "Vorrel's Boots"), (6719, "Windborne Belt"), (6749, "Tiger Band")],
        story="Wren's fire-snorting whelps: Bramble doesn't believe in them, so she watches you eat four (the start of the Whelp line).")
    d = book.quest(
        9105183, "As Old as Hagatha", 27, 25, lantern, lantern, "wren",
        "Wren, whispering so her sister can't hear:$B$BSnack, Hagatha says the giant crocolisks of Sundown Marsh are "
        "as old as she is. I said that's impossible, nothing is as old as she is, and she threw a spoon at me.$B$B"
        "Settle it. Turn on your Sniff and follow the old-croc smell north-west into Sundown Marsh, find the biggest one, "
        "and eat it. If it tastes like spoons, she was right.",
        "Follow the old-croc smell with Sniff north-west into Sundown Marsh, then devour a Giant Wetlands Crocolisk.",
        "No croc yet, Snack. The spoon is waiting.",
        "Well? Spoons? ...Just old? Then she's older. HA. I'm telling her.$B$BHere, from me. Not from the spoon.",
        objectives=[trail("The old-croc smell followed", "a Giant Wetlands Crocolisk", 0,
                          [(-3195, -2160), (-3120, -1905), (-3015, -1665), (-2925, -1410), (-2805, -1185)],
                          summon=2089),
                    devour(1, "Giant Wetlands Crocolisk devoured", entries=[2089])], prev=c.id, sort=s, xp=6,
        choices=[(9699, "Garrison Cloak"), (10653, "Trailblazer Boots"), (6748, "Monkey Ring")],
        story="Wren and the spoon argument: sniff out a giant crocolisk as old as Hagatha, and eat it (Komodo line).")
    book.quest(
        9105186, "In Passing", 23, 21, lantern, lantern, "hagatha",
        "Hagatha, quick and light:$B$BYour grub grew wings of glass, little horror. A glasswing does not stand and "
        "fight; it bites in passing and is gone. The Dragonmaw orcs hold the hills north of here and expect "
        "everything to come at them head on.$B$BWear your glasswing. Bite five of them in passing. Never stop.",
        "As a Glasswing, bite 5 Dragonmaw orcs in the Wetlands with Needle Bite.",
        "Five orcs, little horror, in passing.",
        "Five bites, and they never caught the wing that gave them. That is the whole glasswing.$B$BTake this.",
        objectives=[ability(5, "Dragonmaw bitten as a Glasswing", 9102351, entries=[2103, 2102, 1034, 1035, 1057],
                            shapes=(51,))],
        prev=a.id, sort=s, needs=(51,),
        choices=[(7751, "Vorrel's Boots"), (6719, "Windborne Belt"), (6749, "Tiger Band")],
        story="For a Devourer with the Glasswing: Needle Bite five Dragonmaw orcs in passing.")
    return d


def ashenvale_quests(book, lantern):
    s = Z_ASHENVALE
    fire = campfire(book, "ashenvale_fire", lantern, -6.0, -6.0, 99.73, [
        "Sit, both of you. The trees here are listening; let them.",
        "Long ago the night elves of this forest were offered a trade. Power, for their shape.",
        "Most said no. Some said yes. They got their power, and horns, and hooves, and a hunger that never ends.",
        "Satyrs, we call them now. They remember being beautiful. That is the cruelest part.",
        "A shape is not a coat, little horror. You cannot sell it and buy it back.",
        "You change your shape every day. But you never sell it. You eat it, and you keep it. That is the difference.",
        "Never forget the difference."],
        "Bramble looks at her own hands for a long moment. \"I like my shape. I'm keeping it.\"")
    a = book.quest(
        9105190, "Ghostpaw", 20, 19, lantern, lantern, "hagatha",
        "Hagatha speaks, and the leaves seem to listen:$B$BThe wolves of Ashenvale are called ghostpaws, because they "
        "walk so softly the night elves thought them spirits. They are not spirits, little horror. They are only "
        "quiet. Eat six of them and learn the difference.",
        "Devour 6 Ghostpaw wolves in Ashenvale.",
        "Six ghostpaws. Quiet things; be quieter.",
        "Not spirits. Meat. Remember that when the night elves tell you stories.$B$BTake this, little horror.",
        objectives=[devour(6, "Ghostpaw devoured", entries=[3823, 3824])], sort=s,
        choices=[(6670, "Panther Armor"), (15462, "Loamflake Bracers"), (1264, "Headbasher")],
        story="The lesson: the soft walk of Ashenvale's ghostpaw wolves.")
    b = book.quest(
        9105191, "A Shape Is Not a Coat", 23, 21, lantern, lantern, "hagatha",
        "Hagatha's voice is very serious:$B$BThere is a tale I tell every shapeshifter once, little horror, and "
        "Ashenvale is where I tell it. I have given it to your little friend to carry. Sit with her by any fire and "
        "let her tell it; she should hear it too, she has a shape of her own to keep.",
        "Sit by any campfire or inn fire with Bramble for a while, and hear Hagatha's tale to its end.",
        "Any fire will do. This one matters.",
        "Now you know what the satyrs are. When you meet them in the east of the forest, you will taste the "
        "difference.$B$BTake this. I have no use for it.",
        objectives=[tale(fire, "The tale of the satyrs' bargain heard")], prev=a.id, sort=s, xp=4,
        choices=[(7751, "Vorrel's Boots"), (5355, "Beastmaster's Girdle"), (6749, "Tiger Band")],
        story="A campfire tale for the Devourer and Bramble: the night elves who sold their shape and became satyrs.")
    c = book.quest(
        9105192, "Bought Cheap", 27, 25, lantern, lantern, "hagatha",
        "Hagatha's voice hardens:$B$BThe satyrs gather at Night Run and Satyrnaar in the east of the forest. Wear "
        "your saber, little horror, and hunt them as a cat: five of them, in the shape you kept, against the shape "
        "they sold. A cat that kills satyrs learns to hunt in silence, the way they never could.",
        "As a Saber (or what it grew into), slay 5 Felmusk or Bleakheart satyrs in Ashenvale.",
        "Five satyrs. They are loud; follow the noise.",
        "Bitter, wasn't it? That is the taste of a shape bought cheap.$B$BThis is yours now.",
        objectives=[slay(5, "Satyr slain as a saber", entries=[3758, 3763, 3762, 3759, 3765, 3770, 3767, 3771],
                         shapes=LINES["saber"])],
        prev=b.id, sort=s, needs=LINES["saber"],
        choices=[(2953, "Watch Master's Cloak"), (3754, "Shepherd's Gloves"), (24118, "Signet of Argas")],
        story="After the tale, the satyrs themselves: hunt five as a saber (a Shadowclaw task).")
    d = book.quest(
        9105193, "The Voidcallers of Althalaxx", 28, 26, lantern, lantern, "hagatha",
        "Hagatha speaks, and the flame shrinks away from something:$B$BNorth of here, in Darkshore, the Twilight's "
        "followers call the void at the Tower of Althalaxx. The dark strand voidcallers, they name themselves. Fools "
        "who knock on a door and do not wonder what will open it.$B$BWalk into the tower quietly, little horror, without a fight at the door; let them finish their "
        "knocking. Then eat three of them. A voidcreeper that has eaten "
        "the ones who call the void becomes the mother of what answers.",
        "Walk into the Tower of Althalaxx without being in a fight, then devour 3 Dark Strand Voidcallers there.",
        "They are still knocking on the door.",
        "Quiet now, the tower. Your voidcreeper heard every knock.$B$BHere. It fits a shape like yours.",
        objectives=[visit("Walked into the Tower of Althalaxx", 1, 7197.0, -732.0, radius=35.0, quiet=True),
                    devour(3, "Dark Strand Voidcaller devoured", entries=[2337])], prev=c.id, sort=s, xp=6,
        choices=[(6745, "Swiftrunner Cape"), (9687, "Grappler's Belt"), (6748, "Monkey Ring")],
        story="The voidcallers of Althalaxx: walk in quietly, then eat three (a Voidcreeper Broodmother task).")
    book.quest(
        9105195, "Fangs From Below", 27, 25, lantern, lantern, "hagatha",
        "Hagatha, from somewhere dark:$B$BYour voidling grew legs, little horror, and then more legs. A voidcreeper "
        "hunts from under the ground, with fangs wet with the dark. The Dark Strand fanatics on the coast north of "
        "here think they serve the void. Show them what the void grows.$B$BWear your voidcreeper. Sink your fangs "
        "into five of them.",
        "As a Voidcreeper, sink Creeper Fangs into 5 Dark Strand fanatics in Darkshore.",
        "Five fanatics, little horror. Fangs first.",
        "Did they scream? They always scream when they meet what they pray to.$B$BTake this. I have no use for it.",
        objectives=[ability(5, "Fanatic bitten as a Voidcreeper", 9102261, entries=[2336, 2337], shapes=(42,))],
        prev=a.id, sort=s, needs=(42,),
        choices=[(6745, "Swiftrunner Cape"), (9687, "Grappler's Belt"), (6748, "Monkey Ring")],
        story="For a Devourer with the Voidcreeper: Creeper Fang five Dark Strand fanatics.")
    return d


def hillsbrad_quests(book, lantern):
    s = Z_HILLSBRAD
    a = book.quest(
        9105200, "Gray Bears", 21, 20, lantern, lantern, "hagatha",
        "Hagatha, mild:$B$BThe gray bears of Hillsbrad are old and slow and very, very strong. Eat six of them, little "
        "horror. Not every lesson is about speed.",
        "Devour 6 gray bears in Hillsbrad Foothills.",
        "Six bears. They are slow; do not make me wait longer than they do.",
        "Heavy, warm, patient. A good meal for a cold night.$B$BTake this. It was going to waste.",
        objectives=[devour(6, "Gray bear devoured", entries=[2351, 2354, 2356])], sort=s,
        choices=[(17005, "Boorguard Tunic"), (6668, "Draftsman Boots"), (5322, "Demolition Hammer")],
        story="The lesson: the slow strength of Hillsbrad's old gray bears.")
    c = book.quest(
        9105202, "Honest Claws", 26, 24, lantern, lantern, "hagatha",
        "Hagatha, after a long breath:$B$BThe mountain lions came down from Alterac when the ogres took the mountains. They are "
        "starving, little horror, and starving cats are honest hunters. Wren wants to time you against them; she says a starving cat is the only fair race. Five of them, "
        "the starving ones and the feral ones in the south, before her candle burns down.",
        "Devour 5 mountain lions in Hillsbrad Foothills before Wren's candle burns down (5 minutes).",
        "The candle is out. Wren is lighting another. Five lions.",
        "Honest hunger, again. You will meet it often.$B$BTake this.",
        objectives=[devour(5, "Mountain lion devoured", entries=[2384, 2385])], prev=a.id, sort=s, timed=300,
        choices=[(2953, "Watch Master's Cloak"), (3754, "Shepherd's Gloves"), (24118, "Signet of Argas")],
        story="Hagatha's honest hunters: five starving mountain lions against Wren's candle (5 minutes).")
    book.quest(
        9105203, "Sunning with the Snapjaws", 30, 28, lantern, lantern, "hagatha",
        "Hagatha, slow as a turtle:$B$BRight by the lantern, along the river, the snapjaws lie in the sun. Old "
        "turtles, little horror, with jaws that close and do not open again.$B$BWear your turtle and go and lie down "
        "among them. Do nothing. Turtles are very good at nothing. Let the sun warm your shell, and learn how long a "
        "thing can wait when it has a house on its back.",
        "Wearing your Snapjaw (or what it grew into), lie down among the snapjaws by the river without starting a "
        "fight.",
        "They are sunning. Go and do nothing with them.",
        "Warm? Good. Now, when the world bites you, you will bite back from inside your shell, slowly.$B$BTake this. You walked far for it.",
        objectives=[among("Sunned with the snapjaws", 0, -283.0, -1102.0, [2408], LINES["turtle"], radius=25.0)],
        prev=c.id, sort=s, needs=LINES["turtle"], xp=6,
        choices=[(4107, "Tiger Hunter Gloves"), (33249, "Boots of the Skirmisher"), (33267, "Fleshripper")],
        story="For a Devourer with the Snapjaw shape: lie in the sun among the old snapjaws and do nothing.")
    book.quest(
        9105205, "Over and Out", 23, 21, lantern, lantern, "wren",
        "Wren, cackling:$B$BSnack, your grub grew a HORN. A rhino beetle! Hagatha says you can get the horn under "
        "something and flip it clean over your back. The Syndicate thieves around Durnholde Keep, east of the lantern, "
        "have never been flipped.$B$BWear your beetle. Flip five of them. Over and out.",
        "As a Rhino Beetle, flip 5 Syndicate thieves in Hillsbrad Foothills with Horn Toss.",
        "Five thieves, Snack. Over and OUT.",
        "Five thieves, flipped! I'd pay to see that. I did see it. Through the lantern. Free.$B$BHere!",
        objectives=[ability(5, "Syndicate flipped as a Rhino Beetle", 9102342, entries=[2261, 2244, 2260],
                            shapes=(50,))],
        prev=a.id, sort=s, needs=(50,),
        choices=[(10653, "Trailblazer Boots"), (16659, "Deftkin Belt"), (6749, "Tiger Band")],
        story="For a Devourer with the Rhino Beetle: Horn Toss five Syndicate thieves near Durnholde.")
    return c


def stonetalon_quests(book, lantern):
    s = Z_STONETALON
    a = book.quest(
        9105210, "Deepmoss", 20, 19, lantern, lantern, "wren",
        "Wren, from under a blanket:$B$BSnack, the spiders in the Windshear Crag are called DEEPMOSS and they SPIT. "
        "I'm hiding until you've eaten six of them. I've got biscuits under here. I'll save you one.",
        "Devour 6 Deepmoss spiders in Stonetalon Mountains.",
        "Still under the blanket, Snack.",
        "I'm out! Here's your biscuit. I ate half. Here's the other half of a prize, too.",
        objectives=[devour(6, "Deepmoss spider devoured", entries=[4007, 4006])], sort=s,
        choices=[(6670, "Panther Armor"), (2033, "Ambassador's Boots"), (15464, "Brute Hammer")],
        story="The lesson, Wren's way: she hides under a blanket from the spitting Deepmoss spiders.")
    b = book.quest(
        9105211, "Three Things at Once", 23, 21, lantern, lantern, "hagatha",
        "Hagatha, low and even:$B$BThe pridewings of Stonetalon are wyverns, little horror: lion, bat and scorpion, stitched "
        "together by a world that could not make up its mind. They nest around Mirkfallon Lake.$B$BTake your little "
        "friend and let her count the three things while you eat five. A thing that is three things at once is a "
        "good lesson for a thing like you.",
        "With Bramble watching, devour 5 pridewings in Stonetalon Mountains.",
        "Five pridewings. They fly, but they come down to feed.",
        "Three things at once. You are a hundred. Never forget which one you are wearing.$B$BTake this; it has waited for you.",
        objectives=[devour(5, "Pridewing devoured, Bramble counting", entries=[4012, 4014, 4013, 4011],
                           companion="Lion. Bat. Scorpion. That's three. Wait, does the tail count twice?")], prev=a.id, sort=s,
        choices=[(6752, "Lancer Boots"), (6719, "Windborne Belt"), (24119, "Band of Argas")],
        story="Hagatha's lesson of the stitched-together pridewings: Bramble counts the three things while you eat five.")
    c = book.quest(
        9105212, "Crispy All the Way Through", 26, 24, lantern, lantern, "wren",
        "Wren, chewing:$B$BSnack, the basilisks in the Charred Vale got cooked when the forest burned. They're still "
        "walking around, but they're CRISPY. I need an expert opinion and you eat everything, so you're not an "
        "expert. Bramble is an expert. She's very picky.$B$BTake her with you. Eat four basilisks where she can see. "
        "She'll tell us if they're crispy all the way through. Watch out, they stare people to sleep.",
        "With Bramble watching, devour 4 basilisks in the Charred Vale, Stonetalon Mountains.",
        "No verdict yet, Snack. Bramble has to see it.",
        "Bramble says crispy all the way through! I KNEW it. Expert opinion!$B$BHere, a crispy prize.",
        objectives=[devour(4, "Basilisk eaten, Bramble's verdict heard", entries=[4044, 4042, 4041],
                           companion="Crispy all the way through. Eight out of ten. It looked at me funny.")],
        prev=b.id, sort=s,
        choices=[(9699, "Garrison Cloak"), (7751, "Vorrel's Boots"), (6748, "Monkey Ring")],
        story="Wren needs an expert: eat four burned basilisks while Bramble watches and judges the crispiness.")
    d = book.quest(
        9105213, "Nal'taszar", 30, 28, lantern, lantern, "hagatha",
        "Hagatha's voice grows teeth:$B$BHigh on Stonetalon Peak a drake makes its lair: Nal'taszar, a wild thing of "
        "the old flights, too proud to serve and too old to die.$B$BIts scent runs down the mountain like smoke from "
        "a chimney: sulphur and old gold. Turn on your Sniff by the lantern and climb it, north-west, past the "
        "lake and up the peak. At the top, Nal'taszar will be waiting. Eat it, little horror. A whelp that has eaten "
        "a wild drake remembers what dragons were before anyone tamed them.",
        "Follow Nal'taszar's scent with Sniff up Stonetalon Peak, then devour Nal'taszar.",
        "The drake is still on its peak. Climb.",
        "Wild and proud, and now yours. Your whelp has tasted the proto-drake it will become.$B$BHere. Something from my shelf.",
        objectives=[trail("Nal'taszar's scent followed", "Nal'taszar", 1,
                          [(1890, 825), (2070, 1050), (2400, 1155), (2400, 1470), (2445, 1770), (2535, 1980)],
                          summon=4066),
                    devour(1, "Nal'taszar devoured", entries=[4066])], prev=c.id, sort=s, xp=6,
        choices=[(4107, "Tiger Hunter Gloves"), (15456, "Lightstep Leggings"), (33268, "Bone Dirk")],
        story="Climb Stonetalon Peak on Nal'taszar's scent and eat the wild drake (a Proto-Drake task).")
    book.quest(
        9105215, "Long Legs, Loud Boots", 24, 22, lantern, lantern, "wren",
        "Wren, thrilled:$B$BSnack! The Derby made you a primal tallstrider! Armoured legs! A horn! The Venture Co. in "
        "the Windshear Crag are cutting down the whole mountain for timber, and the elves are too busy being sad "
        "about it.$B$BWear your tallstrider and go and kick six of them. Primal kicks. Loud ones.",
        "As a Primal Tallstrider, kick 6 Venture Co. workers in the Windshear Crag with Primal Kick.",
        "Six loggers, Snack. KICK.",
        "Six kicked! I heard the boots from here. The mountain thanks you, probably.$B$BHere!",
        objectives=[ability(6, "Venture Co. kicked as a Tallstrider", 9102291, entries=[3989, 3988, 3991],
                            shapes=(45,))],
        prev=a.id, sort=s, needs=(45,),
        choices=[(6752, "Lancer Boots"), (6719, "Windborne Belt"), (24119, "Band of Argas")],
        story="For a Devourer with the Primal Tallstrider: Primal Kick six Venture Co. loggers.")
    return d


def needles_quests(book, lantern):
    s = Z_NEEDLES
    giggles = book.beast("giggles", "Giggles", 4248, level=25, faction=FACTION_SHY, passive=True, scale=0.45,
                         subname="Pesterhide Pup")
    a = book.quest(
        9105220, "Pesterhide", 26, 25, lantern, lantern, "wren",
        "Wren, annoyed:$B$BSnack, the hyenas down there are called PESTERHIDE. They named themselves after what they "
        "do! They follow travellers and nip at their heels. Eat six. Nobody nips at my Snack.",
        "Devour 6 Pesterhide hyenas in Thousand Needles.",
        "Six hyenas. They're still nipping, Snack.",
        "No more nipping! Except me. I nip biscuits.$B$BHere! You earned it!",
        objectives=[devour(6, "Pesterhide hyena devoured", entries=[4248, 4249])], sort=s,
        choices=[(9699, "Garrison Cloak"), (6752, "Lancer Boots"), (6093, "Orc Crusher")],
        story="The lesson, Wren's way: nobody nips at her Snack, so the Pesterhide hyenas get eaten.")
    b = book.quest(
        9105221, "Cloud Serpents", 27, 26, lantern, lantern, "hagatha",
        "Hagatha, and somewhere in the flame the wind howls:$B$BA snake that swallows enough storms grows wings to "
        "carry them. The cloud serpents of the Needles are what that looks like, little horror. They coil around the "
        "spires.$B$BEat one, and you will see the last thing it saw: the canyon it nested in, in the south-east. Go and "
        "stand there, where the wind breaks. Then eat four more. Your snake, or your eagle, will learn what it "
        "is to be both at once.",
        "Devour a cloud serpent, go to the canyon its last memory shows you, then devour 4 more.",
        "Did you see the canyon? Go and stand in it.",
        "Did you taste the storm? It is still in you. Your wind serpent will feel it.$B$BHere. Wren picked it; I checked it.",
        objectives=[devour(1, "Cloud serpent devoured (you see a canyon)", entries=[4117, 4118, 4119]),
                    visit("Windbreak Canyon, where it nested", 1, -5470.0, -2900.0, radius=45.0),
                    devour(4, "Cloud serpent devoured", entries=[4117, 4118, 4119])], prev=a.id, sort=s,
        choices=[(3754, "Shepherd's Gloves"), (9687, "Grappler's Belt"), (24119, "Band of Argas")],
        story="Hagatha's tale of the snake that swallowed storms: eat one, see the canyon it nested in, go there, eat more.")
    d = book.quest(
        9105223, "The Stare of the Salt", 33, 31, lantern, lantern, "hagatha",
        "Hagatha speaks, dry as the salt:$B$BOn the Shimmering Flats, south-east of here, the saltstone basilisks "
        "stare at nothing, and anything they stare at turns a little to crystal. Let one stare at you, little horror. "
        "Feel your skin go hard and glittering. Then eat three of them, and four of the great scorpids that guard "
        "the salt with them.$B$BThe salt keeps them; it will keep you.",
        "Let a Saltstone Gazer stare at you, then devour 3 saltstone basilisks and 4 scorpids on the Shimmering Flats.",
        "The basilisks still stare at nothing.",
        "Salt and venom and a little crystal. A dry meal, but a long-keeping one.$B$BTake this, and go south when you "
        "are ready.",
        objectives=[struck(1, "The salt stare felt", entries=[4150]),
                    devour(3, "Saltstone basilisk devoured", entries=[4147, 4151, 4150]),
                    devour(4, "Shimmering Flats scorpid devoured", entries=[4140, 4139])], prev=b.id, sort=s, xp=6,
        choices=[(33243, "Skirmisher's Cover"), (4108, "Panther Hunter Leggings"), (33261, "Destroyer's Cloak")],
        story="The salt flats: let a basilisk's stare crystallise you, then eat the basilisks and the great scorpids.")
    mercy(book, 9105224, "Giggles", 27, lantern, giggles,
          [(-5070, -1755), (-5130, -1755), (-5190, -1695)],
          "Wren, trying to stay cross:$B$BSnack, I know I said nobody nips at my Snack. But there's a pesterhide pup "
          "in the canyon south-west of the lantern that can't laugh yet. It just hiccups. The pack won't take it "
          "hunting until it can laugh properly. It smells of dust and hiccups.$B$BSniff it out and pat it. Maybe tell "
          "it a joke.",
          "Dust and hiccups, Snack.",
          "You told it a joke? It LAUGHED. A real hyena laugh, with a hiccup in the middle. Then it ran off to show "
          "the pack. Giggles will remember you; hyenas remember whoever made them laugh first.$B$BHere's something "
          "for the road. I'd give you a hyena pup, but Hagatha says one laugh in the cauldron room is enough.",
          (6719, "Windborne Belt", 1), s,
          "Mercy: Sniff out Giggles, a hyena pup that can only hiccup, and pat it. It comes back grown (mounts idea "
          "1).", prev=a.id)
    book.quest(
        9105225, "Up From Behind", 28, 26, lantern, lantern, "hagatha",
        "Hagatha, quiet as sand:$B$BYour viper has a trick the Galak centaur have never seen, little horror. It sinks "
        "into the ground and comes up behind. The Galak hold the eastern canyons, and they always face the way the "
        "trouble comes from.$B$BWear your viper. Slither under the sand and come up behind five of them. Then do "
        "what vipers do.",
        "As a Viper, come up behind 5 Galak centaur in Thousand Needles with Sand Slither.",
        "Five centaur, little horror, from behind.",
        "They never saw you. They never do. That is the viper's whole gift.$B$BHere. Wren picked it; I checked it.",
        objectives=[ability(5, "Galak slithered up on as a Viper", 9102092,
                            entries=[4096, 4094, 4093, 4099, 4097, 4095], shapes=(25,))],
        prev=a.id, sort=s, needs=(25,),
        choices=[(3754, "Shepherd's Gloves"), (9687, "Grappler's Belt"), (24119, "Band of Argas")],
        story="For a Devourer with the Viper: Sand Slither up behind five Galak centaur.")
    return d
