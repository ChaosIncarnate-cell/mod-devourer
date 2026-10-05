"""Task 021: the lanterns of the twenties (levels 20-34). Part of tools/devourer_quests_content.py."""

from devourer_quests import devour, trail, struck, among, tale, LINES
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
    stitch = book.beast("stitch", "Stitch", 930, level=20, faction=FACTION_SHY, passive=True, scale=0.6,
                        subname="Spins Crooked Webs")
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
        "Mad, and hungry, and now part of you. Use it, do not let it use you.$B$BTake this.",
        objectives=[devour(6, "Dire wolf devoured", entries=[213, 565])], sort=s,
        choices=[(17005, "Boorguard Tunic"), (5355, "Beastmaster's Girdle"), (15464, "Brute Hammer")],
        story="The lesson: the madness of Duskwood's starving dire wolves.")
    b = book.quest(
        9105171, "The Night That Stayed", 21, 20, lantern, lantern, "hagatha",
        "Hagatha's voice turns careful:$B$BI have lit a fire at the edge of the cemetery, beside the lantern. Duskwood "
        "has a tale, little horror, and it should be told to two at once, so that one of you can keep watch while "
        "the other listens. Bring your little friend. Sit.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit. Do not keep the night waiting.",
        "Now you know why it is dark here. Most people who live here never ask.$B$BTake this, for listening.",
        objectives=[tale(fire, "The tale of the night that stayed heard")], prev=a.id, sort=s, xp=4,
        choices=[(16659, "Deftkin Belt"), (6752, "Lancer Boots"), (6748, "Monkey Ring")],
        story="A campfire tale for the Devourer and Bramble: why the night came to Duskwood and never left.")
    mercy(book, 9105174, "Stitch", 21, lantern, stitch,
          [(-10500, 165), (-10545, 210), (-10560, 255)],
          "Wren, in a very small voice:$B$BSnack. There's a spider. A baby black widow in the cemetery south-west of "
          "the lantern. All the others spin perfect webs and this one spins them CROOKED, so the others chase it off. "
          "It smells of dust and silk and trying again.$B$BI'm scared of spiders. I'm scared of this one. Sniff it "
          "out and pat it anyway. For me. I'm practising being brave.",
          "Dust and silk and trying again, Snack.",
          "You patted a SPIDER. On purpose. And it followed you like a little crooked shadow. I watched the whole "
          "time through the lantern and I only screamed twice.$B$BHagatha says anyone who'll pat a spider deserves a "
          "black cat. Here. It doesn't spin anything.",
          (8485, "Cat Carrier (Bombay)", 1), s,
          "Mercy: Sniff out a baby black widow that spins crooked webs, and pat it (Wren is practising being brave). "
          "Reward: a black cat companion.", prev=a.id)
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
    return d


def wetlands_quests(book, lantern):
    s = Z_WETLANDS
    croaker = book.beast("croaker", "Lord Croaker", 1420, level=20, faction=FACTION_SHY, passive=True, scale=1.6,
                         subname="King of the Puddle")
    a = book.quest(
        9105180, "Young Crocolisks", 21, 20, lantern, lantern, "hagatha",
        "Hagatha's voice, wet and low:$B$BThe Wetlands are a nursery for crocolisks, little horror. The young ones "
        "crowd the shallows and wait to grow. Eat six of them. A komodo grows on patience, and the young are all "
        "patience and no teeth yet.",
        "Devour 6 Young Wetlands Crocolisks.",
        "The shallows are still crowded.",
        "Patient little things. Now your komodo is patient too.$B$BTake this.",
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
        "flight.$B$BTake this.",
        objectives=[among("Sat among the lost whelps", 0, -3500.0, -3100.0, [1042, 1043, 1069, 1044],
                          LINES["whelp"], radius=25.0)],
        prev=a.id, sort=s, needs=LINES["whelp"],
        choices=[(3754, "Shepherd's Gloves"), (2953, "Watch Master's Cloak"), (24119, "Band of Argas")],
        story="For a Devourer with the Whelp shape: sit among the red flight's lost whelps as one of them.")
    c = book.quest(
        9105182, "Flamesnorting", 25, 23, lantern, lantern, "wren",
        "Wren, giggling:$B$BSnack, there are whelps that SNORT FIRE. On purpose! Like little kettles! The "
        "flamesnorting whelps, out in the Green Belt with the others. Hagatha says let one snort a fireball at you, "
        "so you know what a whelp's fire tastes like from the outside, before you taste it from the inside.$B$BThen "
        "eat four. Snort snort.",
        "Let a Flamesnorting Whelp throw its fireball at you, then devour 4 whelps in the Wetlands.",
        "Four whelps and one fireball, Snack.",
        "Snort! I'm doing the whelp noise. Snort snort. Did it singe you? Hagatha says a little singe is good for "
        "the soul.$B$BHere!",
        objectives=[struck(1, "Whelp fire felt", entries=[1044]),
                    devour(4, "Wetlands whelp devoured", entries=[1042, 1043, 1069, 1044])], prev=a.id, sort=s,
        choices=[(7751, "Vorrel's Boots"), (6719, "Windborne Belt"), (6749, "Tiger Band")],
        story="Wren's fire-snorting whelps: take a fireball, then eat four (the start of the Whelp line).")
    mercy(book, 9105184, "Lord Croaker", 22, lantern, croaker,
          [(-3225, -2355), (-3165, -2340), (-3105, -2295)],
          "Wren, solemn:$B$BSnack, I must tell you about Lord Croaker. He is a toad. He is the biggest toad in the "
          "marsh north of the lantern, and he sits on a puddle like a throne, and every crocolisk in the Wetlands "
          "would like to eat him. He smells of pondweed and importance.$B$BSniff him out. Bow if you like. Then pat "
          "him. Gently. He is a lord.",
          "Pondweed and importance, Snack.",
          "He allowed you to pat him? He ALLOWED it? You've been knighted, Snack. Toad-knighted.$B$BHere: a frog of "
          "your own. It isn't a lord. Don't tell it.",
          (11026, "Tree Frog Box", 1), s,
          "Mercy: Sniff out Lord Croaker, the biggest toad in the marsh, and pat him. Reward: a frog companion.",
          prev=a.id)
    d = book.quest(
        9105183, "As Old as Hagatha", 27, 25, lantern, lantern, "wren",
        "Wren, whispering so her sister can't hear:$B$BSnack, Hagatha says the giant crocolisks of Sundown Marsh are "
        "as old as she is. I said that's impossible, nothing is as old as she is, and she threw a spoon at me.$B$B"
        "Settle it. Turn on your Sniff and follow the old-croc smell north into Sundown Marsh, find the biggest one, "
        "and eat it. If it tastes like spoons, she was right.",
        "Follow the old-croc smell with Sniff north into Sundown Marsh, then devour a Giant Wetlands Crocolisk.",
        "No croc yet, Snack. The spoon is waiting.",
        "Well? Spoons? ...Just old? Then she's older. HA. I'm telling her.$B$BHere, from me. Not from the spoon.",
        objectives=[trail("The old-croc smell followed", "a Giant Wetlands Crocolisk", 0,
                          [(-3195, -2160), (-3120, -1905), (-3015, -1665), (-2925, -1410), (-2805, -1185)],
                          summon=2089),
                    devour(1, "Giant Wetlands Crocolisk devoured", entries=[2089])], prev=c.id, sort=s, xp=6,
        choices=[(9699, "Garrison Cloak"), (10653, "Trailblazer Boots"), (6748, "Monkey Ring")],
        story="Wren and the spoon argument: sniff out a giant crocolisk as old as Hagatha, and eat it (Komodo line).")
    return d


def ashenvale_quests(book, lantern):
    s = Z_ASHENVALE
    dapple = book.beast("dapple", "Dapple", 3817, level=20, faction=FACTION_SHY, passive=True, scale=0.4,
                        subname="Shadowhorn Fawn")
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
        "Not spirits. Meat. Remember that when the night elves tell you stories.$B$BTake this.",
        objectives=[devour(6, "Ghostpaw devoured", entries=[3823, 3824])], sort=s,
        choices=[(6670, "Panther Armor"), (15462, "Loamflake Bracers"), (1264, "Headbasher")],
        story="The lesson: the soft walk of Ashenvale's ghostpaw wolves.")
    b = book.quest(
        9105191, "A Shape Is Not a Coat", 23, 21, lantern, lantern, "hagatha",
        "Hagatha's voice is very serious:$B$BI have lit a fire beside the lantern. There is a tale I tell every "
        "shapeshifter once, little horror, and Ashenvale is where I tell it. Bring your little friend. She should "
        "hear it too; she has a shape of her own to keep.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit. This one matters.",
        "Now you know what the satyrs are. When you meet them in the east of the forest, you will taste the "
        "difference.$B$BTake this.",
        objectives=[tale(fire, "The tale of the satyrs' bargain heard")], prev=a.id, sort=s, xp=4,
        choices=[(7751, "Vorrel's Boots"), (5355, "Beastmaster's Girdle"), (6749, "Tiger Band")],
        story="A campfire tale for the Devourer and Bramble: the night elves who sold their shape and became satyrs.")
    c = book.quest(
        9105192, "Bought Cheap", 27, 25, lantern, lantern, "hagatha",
        "Hagatha's voice hardens:$B$BThe satyrs gather at Night Run and Satyrnaar in the east of the forest. They will "
        "curse you and slash at you and stink at you; let them, once. Taste what a shape bought cheap can do.$B$B"
        "Then eat five of them, little horror. A cat that eats satyrs learns to hunt in silence, the way they never "
        "could.",
        "Let a satyr use one of its tricks on you, then devour 5 Felmusk or Bleakheart satyrs in Ashenvale.",
        "Five satyrs. They are loud; follow the noise.",
        "Bitter, wasn't it? That is the taste of a shape bought cheap.$B$BTake this.",
        objectives=[struck(1, "A satyr's trick felt", entries=[3758, 3759, 3762, 3763, 3770]),
                    devour(5, "Satyr devoured", entries=[3758, 3763, 3762, 3759, 3765, 3770, 3767, 3771])],
        prev=b.id, sort=s,
        choices=[(2953, "Watch Master's Cloak"), (3754, "Shepherd's Gloves"), (24118, "Signet of Argas")],
        story="After the tale, the satyrs themselves: feel a satyr's trick, then eat five (a Shadowclaw task).")
    mercy(book, 9105194, "Dapple", 21, lantern, dapple,
          [(2430, -1110), (2505, -1215), (2565, -1305)],
          "Wren, melting:$B$BSnack. There is a FAWN. A shadowhorn fawn, all spots and legs, in the woods east of the "
          "lantern. It lost its mother in the fighting at the Warsong camp and now it follows anything with fur. It "
          "smells of moss and milk and spots.$B$BSniff it out and pat it. And then let it follow you for a bit. It "
          "needs to follow something.",
          "Moss and milk and spots, Snack.",
          "It followed you! And then it found the herd and ran to them. All spots. I'm not crying, the lantern's "
          "smoky.$B$BHagatha gave me this for you. It's a salt lick. A fawn comes with it. Don't ask how.",
          (44841, "Little Fawn's Salt Lick", 1), s,
          "Mercy: Sniff out a shadowhorn fawn that lost its mother and follows anything with fur, and pat it. Reward: "
          "a fawn companion.", prev=a.id)
    d = book.quest(
        9105193, "The Voidcallers of Althalaxx", 28, 26, lantern, lantern, "hagatha",
        "Hagatha speaks, and the flame shrinks away from something:$B$BNorth of here, in Darkshore, the Twilight's "
        "followers call the void at the Tower of Althalaxx. The dark strand voidcallers, they name themselves. Fools "
        "who knock on a door and do not wonder what will open it.$B$BLet one of them throw its shadow at you, little "
        "horror. You will know the taste; you came from there. Then eat three of them. A voidcreeper that has eaten "
        "the ones who call the void becomes the mother of what answers.",
        "Let a Dark Strand Voidcaller throw its Shadow Bolt at you, then devour 3 of them at the Tower of Althalaxx.",
        "They are still knocking on the door.",
        "Quiet now, the tower. Your voidcreeper heard every knock.$B$BTake this.",
        objectives=[struck(1, "The voidcaller's shadow felt", entries=[2337]),
                    devour(3, "Dark Strand Voidcaller devoured", entries=[2337])], prev=c.id, sort=s, xp=6,
        choices=[(6745, "Swiftrunner Cape"), (9687, "Grappler's Belt"), (6748, "Monkey Ring")],
        story="The voidcallers of Althalaxx: feel their shadow, then eat three (a Voidcreeper Broodmother task).")
    return d


def hillsbrad_quests(book, lantern):
    s = Z_HILLSBRAD
    clover = book.beast("clover", "Clover", 1933, level=21, faction=FACTION_SHY, passive=True, scale=0.6,
                        subname="Lost Lamb")
    a = book.quest(
        9105200, "Gray Bears", 21, 20, lantern, lantern, "hagatha",
        "Hagatha, mild:$B$BThe gray bears of Hillsbrad are old and slow and very, very strong. Eat six of them, little "
        "horror. Not every lesson is about speed.",
        "Devour 6 gray bears in Hillsbrad Foothills.",
        "Six bears. They are slow; do not make me wait longer than they do.",
        "Heavy, warm, patient. A good meal for a cold night.$B$BTake this.",
        objectives=[devour(6, "Gray bear devoured", entries=[2351, 2354, 2356])], sort=s,
        choices=[(17005, "Boorguard Tunic"), (6668, "Draftsman Boots"), (5322, "Demolition Hammer")],
        story="The lesson: the slow strength of Hillsbrad's old gray bears.")
    mercy(book, 9105204, "Clover", 22, lantern, clover,
          [(-285, -1050), (-330, -975), (-405, -900)],
          "Wren, worried:$B$BSnack, a lamb ran away from the farms when the Syndicate came through, and it's been "
          "hiding in the hills south-west of the lantern for days. It's too scared to go home. It smells of wool and "
          "clover and being very far from home.$B$BSniff it out and pat it. Then walk it a little way home. Lambs need "
          "someone to walk behind.",
          "Wool and clover, Snack.",
          "You walked it home! Well, part of the way, and then it ran the rest bleating. That's how lambs say thank "
          "you.$B$BHere: a lamb of your own. Hagatha says it's from Elwynn. It still bleats the same.",
          (44974, "Elwynn Lamb", 1), s,
          "Mercy: Sniff out a lamb hiding in the hills since the Syndicate came, and pat it. Reward: a lamb companion.",
          prev=a.id)
    c = book.quest(
        9105202, "Honest Claws", 26, 24, lantern, lantern, "hagatha",
        "Hagatha speaks:$B$BThe mountain lions came down from Alterac when the ogres took the mountains. They are "
        "starving, little horror, and starving cats are honest hunters. Let one of them swipe at you; feel how "
        "honest a hungry claw is. Then eat five of them, the starving ones and the feral ones in the south.",
        "Let a mountain lion claw you, then devour 5 mountain lions in Hillsbrad Foothills.",
        "Five lions. They are hungry too.",
        "Honest hunger, again. You will meet it often.$B$BTake this.",
        objectives=[struck(1, "A lion's claw felt", entries=[2384, 2385]),
                    devour(5, "Mountain lion devoured", entries=[2384, 2385])], prev=a.id, sort=s,
        choices=[(2953, "Watch Master's Cloak"), (3754, "Shepherd's Gloves"), (24118, "Signet of Argas")],
        story="Hagatha's honest hunters: feel a starving mountain lion's claw, then eat five.")
    book.quest(
        9105203, "Sunning with the Snapjaws", 30, 28, lantern, lantern, "hagatha",
        "Hagatha, slow as a turtle:$B$BRight by the lantern, along the river, the snapjaws lie in the sun. Old "
        "turtles, little horror, with jaws that close and do not open again.$B$BWear your turtle and go and lie down "
        "among them. Do nothing. Turtles are very good at nothing. Let the sun warm your shell, and learn how long a "
        "thing can wait when it has a house on its back.",
        "Wearing your Snapjaw (or what it grew into), lie down among the snapjaws by the river without starting a "
        "fight.",
        "They are sunning. Go and do nothing with them.",
        "Warm? Good. Now, when the world bites you, you will bite back from inside your shell, slowly.$B$BTake this.",
        objectives=[among("Sunned with the snapjaws", 0, -283.0, -1102.0, [2408], LINES["turtle"], radius=25.0)],
        prev=c.id, sort=s, needs=LINES["turtle"], xp=6,
        choices=[(4107, "Tiger Hunter Gloves"), (33249, "Boots of the Skirmisher"), (33267, "Fleshripper")],
        story="For a Devourer with the Snapjaw shape: lie in the sun among the old snapjaws and do nothing.")
    return c


def stonetalon_quests(book, lantern):
    s = Z_STONETALON
    gust = book.beast("gust", "Gust", 4011, level=21, faction=FACTION_SHY, passive=True, scale=0.4,
                      subname="Pridewing Cub")
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
        "Hagatha speaks:$B$BThe pridewings of Stonetalon are wyverns, little horror: lion, bat and scorpion, stitched "
        "together by a world that could not make up its mind. They nest around Mirkfallon Lake.$B$BLet one sting "
        "you, so you feel the scorpion in it. Then eat five. A thing that is three things at once is a good lesson "
        "for a thing like you.",
        "Let a pridewing sting or swoop at you, then devour 5 pridewings in Stonetalon Mountains.",
        "Five pridewings. They fly, but they come down to feed.",
        "Three things at once. You are a hundred. Never forget which one you are wearing.$B$BTake this.",
        objectives=[struck(1, "The pridewing's sting felt", entries=[4012, 4013, 4014, 4011]),
                    devour(5, "Pridewing devoured", entries=[4012, 4014, 4013, 4011])], prev=a.id, sort=s,
        choices=[(6752, "Lancer Boots"), (6719, "Windborne Belt"), (24119, "Band of Argas")],
        story="Hagatha's lesson of the stitched-together pridewings: feel the scorpion in one, then eat five.")
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
    mercy(book, 9105214, "Gust", 22, lantern, gust,
          [(1605, 570), (1530, 510), (1500, 480)],
          "Wren, excited:$B$BSnack, a pridewing cub fell out of its nest by Mirkfallon Lake, south-east of the lantern. "
          "Its wings are too small. It keeps jumping off rocks and flapping and landing on its face. It smells of "
          "feathers and fur and stubbornness.$B$BSniff it out and pat it. Don't eat it. It's going to fly one day, I "
          "can tell.",
          "Feathers, fur and stubbornness, Snack.",
          "It followed you, jumping off every rock on the way. Then one jump went a bit further. A BIT. It's going to "
          "fly!$B$BHagatha has a wyvern cub for you, too. It's from the Barrens. It can't fly either. Yet.",
          (49663, "Wind Rider Cub", 1), s,
          "Mercy: Sniff out a pridewing cub that keeps trying to fly off rocks, and pat it. Reward: a wyvern cub "
          "companion.", prev=a.id)
    d = book.quest(
        9105213, "Nal'taszar", 30, 28, lantern, lantern, "hagatha",
        "Hagatha's voice grows teeth:$B$BHigh on Stonetalon Peak a drake makes its lair: Nal'taszar, a wild thing of "
        "the old flights, too proud to serve and too old to die.$B$BIts scent runs down the mountain like smoke from "
        "a chimney: sulphur and old gold. Turn on your Sniff by the lantern and climb it, north-west, past the "
        "lake and up the peak. At the top, Nal'taszar will be waiting. Eat it, little horror. A whelp that has eaten "
        "a wild drake remembers what dragons were before anyone tamed them.",
        "Follow Nal'taszar's scent with Sniff up Stonetalon Peak, then devour Nal'taszar.",
        "The drake is still on its peak. Climb.",
        "Wild and proud, and now yours. Your whelp has tasted the proto-drake it will become.$B$BTake this.",
        objectives=[trail("Nal'taszar's scent followed", "Nal'taszar", 1,
                          [(1890, 825), (2070, 1050), (2400, 1155), (2400, 1470), (2445, 1770), (2535, 1980)],
                          summon=4066),
                    devour(1, "Nal'taszar devoured", entries=[4066])], prev=c.id, sort=s, xp=6,
        choices=[(4107, "Tiger Hunter Gloves"), (15456, "Lightstep Leggings"), (33268, "Bone Dirk")],
        story="Climb Stonetalon Peak on Nal'taszar's scent and eat the wild drake (a Proto-Drake task).")
    return d


def needles_quests(book, lantern):
    s = Z_NEEDLES
    glint = book.beast("glint", "Glint", 4142, level=25, faction=FACTION_SHY, passive=True, scale=0.4,
                       subname="Sparkleshell Hatchling")
    a = book.quest(
        9105220, "Pesterhide", 26, 25, lantern, lantern, "wren",
        "Wren, annoyed:$B$BSnack, the hyenas down there are called PESTERHIDE. They named themselves after what they "
        "do! They follow travellers and nip at their heels. Eat six. Nobody nips at my Snack.",
        "Devour 6 Pesterhide hyenas in Thousand Needles.",
        "Six hyenas. They're still nipping, Snack.",
        "No more nipping! Except me. I nip biscuits.$B$BHere!",
        objectives=[devour(6, "Pesterhide hyena devoured", entries=[4248, 4249])], sort=s,
        choices=[(9699, "Garrison Cloak"), (6752, "Lancer Boots"), (6093, "Orc Crusher")],
        story="The lesson, Wren's way: nobody nips at her Snack, so the Pesterhide hyenas get eaten.")
    b = book.quest(
        9105221, "Cloud Serpents", 27, 26, lantern, lantern, "hagatha",
        "Hagatha, and somewhere in the flame the wind howls:$B$BA snake that swallows enough storms grows wings to "
        "carry them. The cloud serpents of the Needles are what that looks like, little horror. They coil around the "
        "spires and spit lightning at anything that looks up.$B$BLook up. Let one spit at you. Then eat five. Your "
        "snake, or your eagle, will learn what it is to be both at once.",
        "Let a cloud serpent strike you with its lightning, then devour 5 cloud serpents in Thousand Needles.",
        "Five serpents, and one bolt. They coil around the needles.",
        "Did you taste the storm? It is still in you. Your Baby Wind Serpent will feel it.$B$BTake this.",
        objectives=[struck(1, "A cloud serpent's lightning felt", entries=[4117, 4119]),
                    devour(5, "Cloud serpent devoured", entries=[4117, 4118, 4119])], prev=a.id, sort=s,
        choices=[(3754, "Shepherd's Gloves"), (9687, "Grappler's Belt"), (24119, "Band of Argas")],
        story="Hagatha's tale of the snake that swallowed storms: feel a cloud serpent's lightning, then eat five.")
    mercy(book, 9105224, "Glint", 27, lantern, glint,
          [(-5070, -1755), (-5130, -1755), (-5190, -1695)],
          "Wren, triumphant:$B$BSnack, Hagatha says sparkly things are bad luck. I say she's jealous because her "
          "cauldron doesn't sparkle. PROOF: a sparkleshell hatchling wandered all the way from the salt flats to the "
          "canyon south-west of the lantern and it's lost. It smells of salt and sunshine and good luck.$B$BSniff it "
          "out and pat it. If nothing bad happens to you, I win.",
          "Salt and sunshine, Snack.",
          "Nothing bad happened? I WIN. Hagatha's polishing her cauldron now. Out of spite.$B$BHere: a turtle of "
          "your own. It doesn't sparkle, but it's very lucky. I've decided.",
          (23002, "Turtle Box", 1), s,
          "Mercy: Wren's bet with Hagatha. Sniff out a lost sparkleshell hatchling and pat it. Reward: a turtle "
          "companion.", prev=a.id)
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
    return d
