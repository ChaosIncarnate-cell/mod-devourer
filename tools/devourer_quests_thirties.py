"""Task 021: the lanterns of the thirties and forties (levels 30-50). Part of tools/devourer_quests_content.py."""

from devourer_quests import devour, slay, emote, trail, struck, among, visit, tale, LINES
from devourer_quests_content import mercy, FACTION_SHY
from devourer_quests_teens import onward, campfire

Z_STV, Z_DUSTWALLOW, Z_ALTERAC, Z_TANARIS, Z_FERALAS, Z_HINTERLANDS = 33, 15, 36, 440, 357, 47
TOAD = LINES["toad"]                          # Biletoad, Giant Marsh Frog, Water Salamander
EMOTE_FLEX = 41


def thirties(book, twenties):
    stv = book.lantern("stv", "Stranglethorn Vale", 0, -11700.0, -450.0, 21.02, 4.9,
                       "the jungle south-east of Nesingwary's camp")
    dustwallow = book.lantern("dustwallow", "Dustwallow Marsh", 1, -2900.0, -3300.0, 31.69, 3.6,
                              "the marsh north-east of Brackenwall")
    alterac = book.lantern("alterac", "the Alterac Mountains", 0, 500.0, -650.0, 167.4, 2.0,
                           "Gallows' Corner, on the road through the mountains")
    tanaris = book.lantern("tanaris", "Tanaris", 1, -7400.0, -3400.0, 14.1, 5.5, "the dunes south-west of Gadgetzan")
    feralas = book.lantern("feralas", "Feralas", 1, -4600.0, 700.0, 48.23, 1.1,
                           "the forest south-west of Camp Mojache")
    hinterlands = book.lantern("hinterlands", "the Hinterlands", 0, 150.0, -2900.0, 112.45, 2.7,
                               "the hills south-east of Aerie Peak")

    book.region("The lanterns of the thirties and forties (levels 30-50)",
                "Six lanterns along the long roads: crocolisks, turtles and owlbeasts on their way to their last "
                "forms, scent trails to the Stone Fury, Narillasanz, the Oozeworm and Gammerita, and the toad line's "
                "own quests (only a Devourer that owns a toad shape sees them).")

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
    bongo = book.beast("bongo", "Bongo", 1108, level=30, faction=FACTION_SHY, passive=True, scale=0.4,
                       subname="Mistvale Baby")
    a = book.quest(
        9105230, "Young Hunters of the Vale", 31, 30, lantern, lantern, "hagatha",
        "Hagatha's voice, heavy with the heat:$B$BIn Stranglethorn the cats grow up fast or not at all. Young tigers, "
        "young panthers, all teeth and no patience. Eat six of them, little horror. Your saber will learn what it is "
        "to be hunted while it hunts.",
        "Devour 6 young tigers or panthers in Stranglethorn Vale.",
        "Six young cats. They are everywhere; so is the heat.",
        "Fast, and foolish, and gone. Your saber is neither now.$B$BTake this.",
        objectives=[devour(6, "Young jungle cat devoured", entries=[683, 681, 682, 736])], sort=s,
        choices=[(33237, "Brogg's Battle Harness"), (4108, "Panther Hunter Leggings"), (33263, "Raptor Eye Ring")],
        story="The lesson: the jungle's young cats, hunted while they hunt.")
    book.quest(
        9105233, "The Scariest Thing in the Water", 35, 33, lantern, lantern, "wren",
        "Wren, very excited, for a toad:$B$BSnack, you're a TOAD! Or you can be one. That means you can do the toad "
        "thing: sit in the river looking innocent and then EAT. The vale's rivers are full of crocolisks and frenzies "
        "and little water elementals that think they're the scariest thing in the water.$B$BShow them. As a toad, or "
        "a frog, or your salamander, slay eight of them.",
        "As a Biletoad, Giant Marsh Frog or Water Salamander, slay 8 crocolisks, sharptooth frenzies or water "
        "elementals in Stranglethorn Vale.",
        "Eight, Snack. And you have to be a toad when you do it. Those are the rules. I made them up.",
        "The scariest thing in the water! That's you.$B$BHere. I wanted to give you a frog, but Hagatha says you ARE "
        "a frog, sometimes, and that's enough frog.",
        objectives=[slay(8, "Water creature slain as a toad", entries=[1150, 1152, 1151, 905, 691], shapes=TOAD)],
        prev=a.id, sort=s, needs=TOAD,
        choices=[(33241, "Oiled Leather Leggings"), (6727, "Razzeric's Racing Grips"), (4511, "Black Water Hammer")],
        story="For a Devourer with a toad shape: be the scariest thing in the vale's rivers, as a toad.")
    c = book.quest(
        9105232, "Who Flexes First", 34, 32, lantern, lantern, "wren",
        "Wren, howling with laughter:$B$BSnack, there are GORILLAS in the Mistvale Valley, south-west of the lantern, and "
        "they show off. They puff up and beat their chests at anything that walks by. Hagatha says a gorilla backs "
        "down from anything that shows off better.$B$BSo show off. Flex at them. Four gorillas. Big flex. Biggest flex. "
        "Make them run.",
        "Flex (/flex) at 4 Mistvale gorillas and send them running.",
        "Still puffing up, Snack. Flex HARDER.",
        "They RAN! From a flex! You're the strongest-looking thing in Stranglethorn. Hagatha left the room.$B$BHere!",
        objectives=[emote(4, "Gorilla out-flexed", EMOTE_FLEX, entries=[1108, 1114], flee=True)], prev=a.id, sort=s,
        choices=[(10748, "Wanderlust Boots"), (4114, "Darktide Cape"), (9520, "Silent Hunter")],
        story="Wren's contest with the gorillas of Mistvale: flex at them until they back down.")
    mercy(book, 9105235, "Bongo", 33, lantern, bongo,
          [(-11760, -525), (-11775, -585), (-11805, -645)],
          "Wren, worried:$B$BSnack, a baby gorilla fell out of the Mistvale trees and rolled all the way down the hill "
          "south-east of the lantern. It's sitting in the ferns beating its tiny chest at a beetle. It smells of "
          "banana and fern and trying to look big.$B$BSniff it out and pat it. Don't flex at this one. Just pat.",
          "Banana and fern, Snack.",
          "It beat its chest at you and then it held your hand and followed you. Then it heard its mother and ran "
          "back up the hill.$B$BHagatha found you a parrot. It's very loud. It already knows the word 'Snack'.",
          (8494, "Parrot Cage (Hyacinth Macaw)", 1), s,
          "Mercy: Sniff out a baby gorilla that rolled down the hill, and pat it. Reward: a parrot companion.",
          prev=a.id)
    d = book.quest(
        9105234, "The Night's Mouth", 38, 36, lantern, lantern, "hagatha",
        "Hagatha tells it, and the flame goes black at its heart:$B$BIn the south of the vale, where the trolls built "
        "their temples, there are panthers so dark the trolls named them for the mouth of the night: shadowmaw. They "
        "leave no shadow, little horror, because they are made of it. But they leave a smell: wet stone and old "
        "blood.$B$BTurn on your Sniff by the lantern and follow it south. Eat the one at the end of it, and two more. "
        "A saber that has eaten the night's mouth hunts in it.",
        "Follow the shadowmaw's scent with Sniff south of the lantern, then devour 3 Shadowmaw Panthers.",
        "The shadowmaws are still in the dark.",
        "Dark, and quiet, and yours.$B$BTake this.",
        objectives=[trail("The shadowmaw's scent followed", "a Shadowmaw Panther", 0,
                          [(-11820, -510), (-11940, -525), (-12060, -585), (-12180, -660), (-12285, -720)],
                          summon=684),
                    devour(3, "Shadowmaw Panther devoured", entries=[684])], prev=c.id, sort=s, xp=6,
        choices=[(9630, "Pratt's Handcrafted Boots"), (6788, "Magram Hunter's Belt"), (10703, "Fiendish Skiv")],
        story="Sniff out the shadowmaw panthers, the night's mouth, and eat three (a Shadowclaw task).")
    return d


def dustwallow_quests(book, lantern, tanaris, feralas):
    s = Z_DUSTWALLOW
    ember = book.beast("ember", "Ember", 4323, level=34, faction=FACTION_SHY, passive=True, scale=0.7,
                       subname="Does Not Want to Be Wicked")
    fire = campfire(book, "dustwallow_fire", lantern, 6.0, 6.0, 32.6, [
        "Sit, both of you. Mind the mud. Everything here is mud, eventually.",
        "In the Dragonmurk, in the south, the black dragons let their filth run down into the marsh.",
        "A worm lived there. An ordinary worm, eating ordinary dirt.",
        "It ate the filth because the filth was there. Then it ate more, because filth is never full.",
        "It swelled. It forgot it had ever been small. It forgot it had ever been anything but hungry.",
        "The goblins call it the Oozeworm. They do not go into the Dragonmurk.",
        "That is what happens, little horror, when you eat without ever choosing what.",
        "You choose. Every time. That is why you are you, and it is only an ooze."],
        "Bramble wrinkles her nose. \"I'm only eating things I choose. Mostly biscuits.\"")
    a = book.quest(
        9105240, "Drywallow", 35, 34, lantern, lantern, "hagatha",
        "Hagatha, satisfied:$B$BThe crocolisks of Dustwallow are called drywallow, because even here they find the "
        "driest mud to lie in. Strange, proud beasts. Eat six of them, little horror. Your komodo will learn to be "
        "proud of its own mud.",
        "Devour 6 Drywallow crocolisks in Dustwallow Marsh.",
        "Six drywallows. They lie in the driest mud.",
        "Proud, and now humble, inside you.$B$BTake this.",
        objectives=[devour(6, "Drywallow crocolisk devoured", entries=[4341, 4343, 4344])], sort=s,
        choices=[(4108, "Panther Hunter Leggings"), (4109, "Excelsior Boots"), (9680, "Tok'kar's Murloc Shanker")],
        story="The lesson: the proud drywallow crocolisks.")
    b = book.quest(
        9105241, "Bitten Too Often", 36, 35, lantern, lantern, "hagatha",
        "Hagatha tells it, slow as a shell:$B$BOld turtles grow spikes because the world kept biting them. You will "
        "understand that, little horror. On the Dreadmurk Shore, east of here, the mudrock spikeshells have been "
        "bitten so often they are more spike than turtle. Touch one and it will stick you full of barbs.$B$BLet it. "
        "Then eat three. Your snapjaw is waiting to grow its spikes.",
        "Let a Mudrock Spikeshell stick you with its barbs, then devour 3 of them on the Dreadmurk Shore.",
        "Three spikeshells, and their barbs. Mind your mouth.",
        "Prickly, wasn't it? That is what being bitten too often tastes like.$B$BTake this.",
        objectives=[struck(1, "The spikeshell's barbs felt", entries=[4397]),
                    devour(3, "Mudrock Spikeshell devoured", entries=[4397])], prev=a.id, sort=s,
        choices=[(33237, "Brogg's Battle Harness"), (4430, "Ethereal Talisman"), (4511, "Black Water Hammer")],
        story="Hagatha's tale of the turtle that grew spikes: take a spikeshell's barbs, then eat three (Spikeshell).")
    book.quest(
        9105243, "The Gulper's Grin", 37, 35, lantern, lantern, "wren",
        "Wren, plotting:$B$BToad Snack. Toady Snack. The murlocs on the Dreadmurk Shore keep stealing frogspawn from "
        "the marsh and I need you to have a WORD with them. As a toad. A big hungry toad with a big hungry grin.$B$B"
        "Eat six Mirefin murlocs while you're wearing your toad, or your frog, or the salamander.",
        "As a Biletoad, Giant Marsh Frog or Water Salamander, devour 6 Mirefin murlocs in Dustwallow Marsh.",
        "Six murlocs, Snack, as a toad. They're still stealing frogspawn.",
        "Grin! Big grin! The frogspawn is safe and you are a hero to frogs everywhere.$B$BHere, from all the frogs.",
        objectives=[devour(6, "Mirefin murloc devoured as a toad", entries=[4359], shapes=TOAD)],
        prev=a.id, sort=s, needs=TOAD,
        choices=[(10748, "Wanderlust Boots"), (6727, "Razzeric's Racing Grips"), (33263, "Raptor Eye Ring")],
        story="For a Devourer with a toad shape: devour the frogspawn-stealing Mirefin murlocs, as a toad.")
    mercy(book, 9105244, "Ember", 37, lantern, ember,
          [(-2970, -3240), (-3030, -3225), (-3090, -3195)],
          "Wren, whispering:$B$BSnack, I have to tell you something and you can't tell Hagatha. One of the black "
          "dragon hatchlings ran away from the nursery in the south. It doesn't want to be wicked. It told me. Well, "
          "it told a frog and the frog told me. It's hiding in the marsh south-west of the lantern. It smells of "
          "smoke and mud and not wanting to be wicked.$B$BSniff it out. Pat it. Tell it it doesn't have to be.",
          "Smoke and mud, Snack.",
          "It followed you! It's not wicked at all. It sneezed a little fire and apologised.$B$BI told Hagatha. Of "
          "course I told Hagatha. She gave me this for you without saying anything, which is how she says she's "
          "proud.",
          (10822, "Dark Whelpling", 1), s,
          "Mercy: Sniff out a black dragon hatchling that ran from the nursery because it does not want to be wicked, "
          "and pat it. Reward: a dark whelpling companion.", prev=a.id)
    e = book.quest(
        9105245, "Eaten Without Choosing", 38, 36, lantern, lantern, "hagatha",
        "Hagatha's voice, low:$B$BI have lit a fire beside the lantern. There is a worm in this marsh you will meet "
        "soon, little horror, and before you meet it you should hear what it was. Bring your little friend. This tale "
        "is a warning, and warnings are best heard by two.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit. Sit.",
        "You heard. Good. Now go and meet it, and remember: you choose.$B$BTake this.",
        objectives=[tale(fire, "The tale of the Oozeworm heard")], prev=b.id, sort=s, xp=4,
        choices=[(9632, "Jangdor's Handcrafted Gloves"), (17778, "Sagebrush Girdle"), (10703, "Fiendish Skiv")],
        story="A campfire tale for the Devourer and Bramble: the worm that ate without ever choosing what.")
    f = book.quest(
        9105246, "The Oozeworm", 40, 38, lantern, lantern, "hagatha",
        "Hagatha tells it, and the flame shrinks:$B$BThe Oozeworm lives in the Dragonmurk, south-west of here, past "
        "the Quagmire. You can smell it from the lantern if you try: rot and black fire and too much.$B$BTurn on your "
        "Sniff and follow it. It will rise when it smells you. Eat it, little horror. Choose to. A borer that has eaten "
        "the Oozeworm will dig deeper than any worm has dug.",
        "Follow the Oozeworm's stench with Sniff through the Quagmire to the Dragonmurk, then devour the Oozeworm.",
        "The worm is still under the mud. Follow the stench.",
        "Swollen, and slow, and now inside something that chooses. Your borer will dig.$B$BTake this.",
        objectives=[trail("The Oozeworm's stench followed", "the Oozeworm", 1,
                          [(-3120, -3225), (-3330, -3225), (-3555, -3135), (-3780, -3015), (-3990, -2910),
                           (-4200, -2895)], summon=14237),
                    devour(1, "Oozeworm devoured", entries=[14237])], prev=e.id, sort=s, xp=6,
        choices=[(17776, "Sprightring Helm"), (9647, "Failed Flying Experiment"), (4549, "Seafire Band")],
        story="Follow the Oozeworm's stench through the Quagmire and eat it, by choice (a Deep Borer task).")
    onward(book, 9105248, 41, lantern, tanaris, f.id, "South of the marsh the land dries into sand, and the sand "
                                                     "is full of teeth.")
    onward(book, 9105249, 41, lantern, feralas, f.id, "West of the Barrens the forests of Feralas grow taller than "
                                                     "anything you have eaten.")
    return f


def alterac_quests(book, lantern):
    s = Z_ALTERAC
    snowball = book.beast("snowball", "Snowball", 2251, level=31, faction=FACTION_SHY, passive=True, scale=0.35,
                          subname="Yeti Cub")
    a = book.quest(
        9105250, "Mountain Lions of Alterac", 33, 31, lantern, lantern, "hagatha",
        "Hagatha speaks:$B$BThe lions of Alterac are bigger than their cousins in the foothills; the ogres eat "
        "everything smaller. The hulking ones especially. Eat five of them, little horror, and taste a cat that has "
        "learned to be big.",
        "Devour 5 mountain lions in the Alterac Mountains.",
        "Five lions. The big ones, mostly.",
        "Big, and now bigger for being in you.$B$BTake this.",
        objectives=[devour(5, "Alterac mountain lion devoured", entries=[2406, 2407])], sort=s,
        choices=[(33243, "Skirmisher's Cover"), (33250, "Archer's Wristguard"), (33268, "Bone Dirk")],
        story="The lesson: the big cats of Alterac.")
    b = book.quest(
        9105251, "Rubble and Mercy", 34, 32, lantern, lantern, "wren",
        "Wren, angry on someone else's behalf:$B$BSnack, in the crater where Dalaran used to be, the wizards left "
        "elementals TIED UP. Slaves! Of rock! They're crumbling, and when they hit you they crumble you too. Hagatha "
        "says the kindest thing is to eat them, which is a very Hagatha kind of kindness.$B$BTake Bramble. She wants "
        "to see them go free. Eat four where she can see.",
        "With Bramble watching, devour 4 Elemental Slaves at the Dalaran Crater in the Alterac Mountains.",
        "Four of them, Snack. Kindly. And Bramble has to see.",
        "Free! In a very Hagatha way. Bramble says they looked relieved. I'm going to feel weird about this for a "
        "while.$B$BHere.",
        objectives=[devour(4, "Elemental Slave freed", entries=[2359],
                           companion="They looked relieved. Like when you take off boots that are too tight.")],
        prev=a.id, sort=s,
        choices=[(15456, "Lightstep Leggings"), (33261, "Destroyer's Cloak"), (4978, "Ryedol's Hammer")],
        story="Wren's very Hagatha kindness: free the elementals bound in the Dalaran Crater, with Bramble watching.")
    mercy(book, 9105254, "Snowball", 33, lantern, snowball,
          [(555, -585), (615, -510), (615, -465)],
          "Wren, bouncing:$B$BSnack, there's a YETI CUB. A baby yeti. It's lost in the snow north of the lantern, near "
          "the old ruins, and the ogres are looking for it because they want a pet. It smells of snow and fur and "
          "hiding badly.$B$BSniff it out before they do. Pat it. Yetis are very huggable, I've heard.",
          "Snow and fur and hiding badly, Snack.",
          "It followed you through the snow, and then its mother came stomping out of the ruins and picked it up. The "
          "ogres went home sad.$B$BHagatha built you a yeti out of clockwork so you don't miss it. It whirrs.",
          (21277, "Tranquil Mechanical Yeti", 1), s,
          "Mercy: Sniff out a yeti cub before the ogres find it, and pat it. Reward: a clockwork yeti companion.",
          prev=a.id)
    c = book.quest(
        9105252, "The Stone Fury", 37, 35, lantern, lantern, "hagatha",
        "Hagatha tells it, and the flame grinds like rock:$B$BWhen the Syndicate took Strahnbrad, a spirit of the "
        "mountain rose against them and never lay back down. The Stone Fury, the villagers called it. It wanders, "
        "angry at everything, and is gone again for days.$B$BAn angry mountain smells of flint and lightning. Turn on "
        "your Sniff by the lantern and follow it east, through Strahnbrad. Let it stamp the ground under you; feel the "
        "mountain's anger. Then eat it. A whelp that has eaten stone grows into an earthen drake.",
        "Follow the Stone Fury's scent with Sniff through Strahnbrad, let it shake the ground at you, then devour it.",
        "The fury is still in the mountain. Follow the flint.",
        "A mountain's anger, and now yours. Your whelp may grow scales of stone.$B$BTake this.",
        objectives=[trail("The Stone Fury's scent followed", "the Stone Fury", 0,
                          [(555, -750), (615, -855), (660, -945), (660, -1035)], summon=2258),
                    struck(1, "The mountain's anger felt", entries=[2258]),
                    devour(1, "Stone Fury devoured", entries=[2258])], prev=b.id, sort=s, xp=6,
        choices=[(10702, "Enormous Ogre Boots"), (9705, "Tharg's Shoelace"), (9520, "Silent Hunter")],
        story="Sniff out the Stone Fury of Strahnbrad, feel it shake the ground, and eat it (Earthen Proto-Drake).")
    book.quest(
        9105253, "Narillasanz", 45, 43, lantern, lantern, "hagatha",
        "Hagatha's voice, very quiet, the way she speaks of dangerous things:$B$BOn Chillwind Point, south-east of "
        "here above the lake, a red drake has made its home. Narillasanz. Old enough to remember the orcs who rode its "
        "kin, strong enough that the ogres leave it alone. Come back to me when you are strong enough too.$B$BThen "
        "follow its smell down the mountain: hot stone and old fire. Let it breathe on you, once. Eat it, little "
        "horror, and your drake will be ready to ride the storm.",
        "Follow Narillasanz's scent with Sniff to Chillwind Point, let it breathe fire on you, then devour it.",
        "The drake still sits on its point. Are you strong enough yet?",
        "You were. I knew you would be.$B$BThat was a dragon, little horror. A real one. Your drake has eaten its "
        "elder; the storm is waiting for it.$B$BTake this.",
        objectives=[trail("Narillasanz's scent followed", "Narillasanz", 0,
                          [(465, -780), (345, -900), (255, -1035), (240, -1155), (285, -1275)], summon=2447),
                    struck(1, "Narillasanz's fire felt", entries=[2447]),
                    devour(1, "Narillasanz devoured", entries=[2447])], prev=c.id, sort=s, xp=7,
        choices=[(19127, "Charred Leather Tunic"), (15822, "Shadowskin Spaulders"), (11863, "White Bone Shredder")],
        story="Come back strong enough: sniff out Narillasanz on Chillwind Point, take its fire, and eat it "
              "(a Storm Dragon task).")
    return c


def tanaris_quests(book, lantern):
    s = Z_TANARIS
    prickles = book.beast("prickles", "Prickles", 5422, level=40, faction=FACTION_SHY, passive=True, scale=0.4,
                          subname="Scorpid Hatchling")
    a = book.quest(
        9105260, "Blisterpaw", 42, 41, lantern, lantern, "wren",
        "Wren, fanning herself:$B$BSnack, it's so HOT there the hyenas have blisters on their paws. Blisterpaws! Poor "
        "things. Well, they're also horrible. Eat six. They'll be glad to get off the sand.",
        "Devour 6 Blisterpaw hyenas in Tanaris.",
        "Six blisterpaws, Snack. Their paws still hurt.",
        "No more sore paws! Well. No more paws. Same thing.$B$BHere!",
        objectives=[devour(6, "Blisterpaw hyena devoured", entries=[5425, 5426])], sort=s,
        choices=[(9630, "Pratt's Handcrafted Boots"), (17778, "Sagebrush Girdle"), (11856, "Ceremonial Elven Blade")],
        story="The lesson, Wren's way: the blistered hyenas of the desert.")
    b = book.quest(
        9105261, "Glasshide", 44, 42, lantern, lantern, "hagatha",
        "Hagatha speaks, dry as the dunes:$B$BThe basilisks of the Abyssal Sands ate so much sand their hides turned "
        "to glass. Glasshides, the goblins call them. Their hide flashes in the sun and blinds whatever looks at "
        "it.$B$BLook at it, little horror. Let one flash you. Then eat five. A meal that was once a beach.",
        "Let a Glasshide Basilisk or Gazer flash you, then devour 5 glasshide basilisks in Tanaris.",
        "Five glasshides, and one flash. Do look into their eyes, this once.",
        "Crunchy. Like a beach. Your teeth will forgive you, and so will your eyes, eventually.$B$BTake this.",
        objectives=[struck(1, "The glass flash felt", entries=[5419, 5420]),
                    devour(5, "Glasshide basilisk devoured", entries=[5419, 5420])], prev=a.id, sort=s,
        choices=[(19041, "Pratt's Handcrafted Tunic"), (17776, "Sprightring Helm"), (11863, "White Bone Shredder")],
        story="Hagatha's glass-hided basilisks of the Abyssal Sands: be flashed, then eat five.")
    c = book.quest(
        9105262, "The Sandfury", 44, 42, lantern, lantern, "hagatha",
        "Hagatha tells it, and sand hisses in the flame:$B$BThe Sandfury trolls of Zul'Farrak keep a watch at "
        "Sandsorrow, just north of here, and pray to a great hydra in their city. Every serpent that sheds long "
        "enough stands up one day and starts to pray, little horror. The sand people began like you.$B$BTheir "
        "witch doctors pray with fire. Let one burn you. Then eat six of the Sandfury. Your serpent will remember what "
        "praying tastes like.",
        "Let a Sandfury Firecaller burn you, then devour 6 Sandfury trolls at Sandsorrow Watch in Tanaris.",
        "Six Sandfury, and one prayer of fire. They are still praying.",
        "Prayer and sand and fire. Your serpent is closer to standing up.$B$BTake this.",
        objectives=[struck(1, "The Sandfury's fire felt", entries=[5647]),
                    devour(6, "Sandfury troll devoured", entries=[5645, 5646, 5647])], prev=a.id, sort=s,
        choices=[(10745, "Kaylari Shoulders"), (9657, "Vinehedge Cinch"), (11120, "Belgrom's Hammer")],
        story="Hagatha's tale of the serpent that stands up and prays: feel a Sandfury's fire, then eat six (Sethrak).")
    mercy(book, 9105265, "Prickles", 43, lantern, prickles,
          [(-7320, -3405), (-7245, -3405), (-7185, -3405)],
          "Wren, curious:$B$BSnack, there's a scorpid hatchling in the dunes north of the lantern that keeps stinging "
          "its own shadow. It thinks the shadow is following it. It is. It smells of hot sand and confusion.$B$BSniff "
          "it out and pat it. Mind the tail. Maybe show it how shadows work.",
          "Hot sand and confusion, Snack.",
          "It stopped stinging its shadow and started following yours. Then it decided your shadow was scarier and "
          "ran home. Good choice.$B$BHagatha found a little scorpion for you. It's from Durotar. It knows how shadows "
          "work.",
          (44973, "Durotar Scorpion", 1), s,
          "Mercy: Sniff out a scorpid hatchling at war with its own shadow, and pat it. Reward: a scorpion companion.",
          prev=a.id)
    e = book.quest(
        9105264, "Rocs", 46, 44, lantern, lantern, "wren",
        "Wren, gasping:$B$BSnack, the birds in the desert are as big as HOUSES. Rocs! Fire rocs, that SPIT fire! "
        "Hagatha says an eagle that eats a roc grows into something the sky is afraid of. I'm afraid of it already and "
        "it doesn't exist yet.$B$BLet one spit at you, so you know. Then eat four rocs. Four houses!",
        "Let a Fire Roc spit fire at you, then devour 4 rocs in Tanaris.",
        "Four rocs, Snack. As big as houses! And one spit.",
        "You ate four houses! Bird houses! House birds! I'm too excited.$B$BHere!",
        objectives=[struck(1, "Roc fire felt", entries=[5429]),
                    devour(4, "Roc devoured", entries=[5428, 5429, 5430])], prev=b.id, sort=s, xp=6,
        choices=[(15822, "Shadowskin Spaulders"), (19127, "Charred Leather Tunic"), (15703, "Chemist's Smock")],
        story="Wren is frightened of eagles that ate rocs: take a fire roc's spit, then eat four.")
    return e


def feralas_quests(book, lantern):
    s = Z_FERALAS
    flicker = book.beast("flicker", "Flicker", 5278, level=41, faction=FACTION_SHY, passive=True, scale=0.7,
                         subname="Shy Sprite Darter")
    a = book.quest(
        9105270, "Longtooth", 41, 40, lantern, lantern, "hagatha",
        "Hagatha speaks:$B$BIn Feralas the wolves have teeth too long for their mouths. Longtooth, the hunters call "
        "them. A wolf that eats its longtooth cousins learns to bite deeper. Eat six.",
        "Devour 6 Longtooth wolves in Feralas.",
        "Six longtooths. Mind their teeth.",
        "Long teeth, short lives. Yours are long enough now.$B$BTake this.",
        objectives=[devour(6, "Longtooth wolf devoured", entries=[5286, 5287])], sort=s,
        choices=[(9633, "Jangdor's Handcrafted Boots"), (9631, "Pratt's Handcrafted Gloves"), (10703, "Fiendish Skiv")],
        story="The lesson: the deep bite of Feralas's longtooth wolves.")
    b = book.quest(
        9105271, "Ironfur", 43, 41, lantern, lantern, "wren",
        "Wren, impressed:$B$BSnack, the bears in Feralas have fur like IRON. Ironfur bears! Hagatha says a bear with "
        "iron fur is a bear that's been hit a lot, and a bear that's been hit a lot swipes back HARD.$B$BLet one swipe "
        "at you, so you know how hard. Then eat five and see if the fur's really iron.",
        "Let an Ironfur bear swipe at you, then devour 5 Ironfur bears in Feralas.",
        "Five ironfurs, Snack, and one swipe. Bring a big appetite.",
        "Iron fur in your tummy! You're basically armoured now.$B$BHere!",
        objectives=[struck(1, "An ironfur swipe felt", entries=[5268, 5272]),
                    devour(5, "Ironfur bear devoured", entries=[5268, 5272])], prev=a.id, sort=s,
        choices=[(19042, "Jangdor's Handcrafted Tunic"), (9647, "Failed Flying Experiment"), (4549, "Seafire Band")],
        story="Wren marvels at the iron fur of Feralas's bears: take a swipe, then eat five.")
    book.quest(
        9105272, "Frayfeather", 45, 43, lantern, lantern, "hagatha",
        "Hagatha, thoughtful:$B$BOn the Frayfeather Highlands, in the south-west, live the hippogryphs, half bird, "
        "half stag. Their feathers fray at the ends from flying too long.$B$BWear your eagle and go and stand among "
        "them in the highlands. They will take you for a strange young cousin. Listen to them complain about their "
        "feathers. An eagle that knows how far a feather lasts knows how far it can fly.",
        "Wearing your Eagle (or what it grew into), walk among the Frayfeather hippogryphs without starting a fight.",
        "They are preening, little horror. Go and preen with them.",
        "Frayed and tired and kind to strangers. Remember that; the sky is not always cruel.$B$BTake this.",
        objectives=[among("Preened with the frayfeathers", 1, -5640.0, 1590.0, [5300, 5304, 5305, 5306],
                          LINES["eagle"], radius=25.0)],
        prev=b.id, sort=s, needs=LINES["eagle"],
        choices=[(17776, "Sprightring Helm"), (9657, "Vinehedge Cinch"), (11120, "Belgrom's Hammer")],
        story="For a Devourer with the Eagle shape: preen among the frayfeather hippogryphs as a strange young cousin.")
    mercy(book, 9105273, "Flicker", 44, lantern, flicker,
          [(-4575, 780), (-4575, 855), (-4605, 915)],
          "Wren, giggling:$B$BSnack! Fairy dragons! Sprite darters! They're tiny and colourful and they blink in and "
          "out like soap bubbles in the woods west of the lantern. One of them is too shy to blink. It just hides. It "
          "smells of soap and flowers and shyness.$B$BSniff it out and pat it. Gently. It might pop.",
          "Soap and flowers and shyness, Snack.",
          "It blinked! For the first time! Right after you patted it. Then it blinked all the way home.$B$BHagatha had "
          "a sprite darter egg in the cauldron. Don't ask why. It's yours. It'll be shy too, probably.",
          (11474, "Sprite Darter Egg", 1), s,
          "Mercy: Sniff out a sprite darter too shy to blink, and pat it. Reward: a sprite darter companion.",
          prev=a.id)
    e = book.quest(
        9105274, "Groddoc", 47, 45, lantern, lantern, "hagatha",
        "Hagatha speaks:$B$BThe great apes of Feralas, the groddoc, beat the ground until it shakes. Thunderers, the "
        "elves call the biggest. Stand close when one beats the ground, little horror; feel the thunder go up through "
        "your feet. Then eat four. There is strength in them the forest itself respects.",
        "Let a Groddoc Thunderer shake the ground under you, then devour 4 Groddoc apes in Feralas.",
        "Four groddoc, and one thunder. Listen for it.",
        "The forest shook when they fell. It will not shake when you walk now; it will be still.$B$BTake this.",
        objectives=[struck(1, "The thunder felt", entries=[5262]),
                    devour(4, "Groddoc ape devoured", entries=[5260, 5262])], prev=b.id, sort=s, xp=6,
        choices=[(9652, "Gryphon Rider's Leggings"), (19992, "Devilsaur Tooth"), (19159, "Woven Ivy Necklace")],
        story="Hagatha's thundering groddoc apes: feel the thunder, then eat four.")
    return e


def hinterlands_quests(book, lantern, stv, alterac):
    s = Z_HINTERLANDS
    feathers = book.beast("featherbrain", "Featherbrain", 9526, level=41, faction=FACTION_SHY, passive=True,
                          scale=0.4, subname="Gryphon Chick")
    fire = campfire(book, "hinterlands_fire", lantern, 6.0, 6.0, 112.0, [
        "Sit, both of you. Look up. The moon is big here. It always has been.",
        "An owl that eats enough moonlight stands up one night and becomes a moonkin.",
        "A moonkin that eats enough of the wild forgets the moon. It goes down on all fours again. An owlbeast.",
        "They still look up sometimes, the owlbeasts. They do not know why. Something in them remembers.",
        "That is the danger of eating, little horror. You can eat so much that you forget what you were.",
        "So every night, before you sleep, remember one thing you were. Just one.",
        "Bramble will help you. She remembers everything. Especially the embarrassing things."],
        "Bramble grins. \"I remember when you were a frog and fell in the cauldron.\"")
    a = book.quest(
        9105280, "Silvermane", 43, 41, lantern, lantern, "hagatha",
        "Hagatha, admiring:$B$BThe wolves of the Hinterlands have silver manes, and the dwarves of Aerie Peak make "
        "cloaks of them. Eat six, little horror. A wolf that has eaten silver shines a little, even in the dark.",
        "Devour 6 Silvermane wolves in the Hinterlands.",
        "Six silvermanes. They shine; you will find them.",
        "Silver in your belly. Shine a little.$B$BTake this.",
        objectives=[devour(6, "Silvermane wolf devoured", entries=[2923, 2924, 2925, 2926])], sort=s,
        choices=[(9632, "Jangdor's Handcrafted Gloves"), (17778, "Sagebrush Girdle"), (11856, "Ceremonial Elven Blade")],
        story="The lesson: the silver-maned wolves of the Hinterlands.")
    b = book.quest(
        9105281, "The Ones That Forgot the Moon", 44, 42, lantern, lantern, "hagatha",
        "Hagatha's voice goes silver:$B$BI have lit a fire beside the lantern, under the big moon. There is a tale "
        "about the owlbeasts of these hills, little horror, and it is really a tale about you. Bring your little "
        "friend; she has a part in it.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit, and the moon is up. Sit.",
        "Remember one thing you were. Every night.$B$BTake this.",
        objectives=[tale(fire, "The tale of the owlbeasts heard")], prev=a.id, sort=s, xp=4,
        choices=[(19042, "Jangdor's Handcrafted Tunic"), (9647, "Failed Flying Experiment"), (11120, "Belgrom's Hammer")],
        story="A campfire tale for the Devourer and Bramble: the owlbeasts that ate so much they forgot the moon.")
    c = book.quest(
        9105282, "Fatal Bites", 45, 43, lantern, lantern, "hagatha",
        "Hagatha, quiet:$B$BNow go and meet them. The owlbeasts of the Hinterlands are vicious, primitive, savage, "
        "and their bite goes to the bone. Let one bite you, little horror, and feel what a creature does when it has "
        "forgotten everything but hunger. Then eat five.$B$BYour moonkin should know what it could forget.",
        "Let a Hinterlands owlbeast bite or shred you, then devour 5 owlbeasts in the Hinterlands.",
        "Five owlbeasts. They have forgotten the moon; do not let them forget you.",
        "Wild, and moonless. Your moonkin will remember the moon for both of you.$B$BTake this.",
        objectives=[struck(1, "An owlbeast's bite felt", entries=[2927, 2928, 2929]),
                    devour(5, "Hinterlands owlbeast devoured", entries=[2927, 2928, 2929])], prev=b.id, sort=s,
        choices=[(15822, "Shadowskin Spaulders"), (10745, "Kaylari Shoulders"), (15703, "Chemist's Smock")],
        story="After the tale, the owlbeasts themselves: feel their bite, then eat five (the owl line).")
    mercy(book, 9105283, "Featherbrain", 45, lantern, feathers,
          [(225, -2895), (315, -2895), (375, -2895)],
          "Wren, delighted:$B$BSnack, a gryphon chick fell out of an Aerie Peak nest and walked the wrong way. It's in "
          "the hills north of the lantern, below Quel'Danil Lodge, squawking at elves. It smells of feathers and "
          "biscuits. The dwarves feed them biscuits!$B$BSniff it out and pat it. Point it home. It's a bit of a "
          "featherbrain.",
          "Feathers and biscuits, Snack.",
          "It followed you, then it saw a dwarf with a biscuit and ran to him. Featherbrain.$B$BHagatha had a gryphon "
          "chick of her own hatching. It's yours now. It already likes biscuits.",
          (49662, "Gryphon Hatchling", 1), s,
          "Mercy: Sniff out a gryphon chick that walked the wrong way from Aerie Peak, and pat it. Reward: a gryphon "
          "companion.", prev=a.id)
    e = book.quest(
        9105284, "Gammerita", 48, 46, lantern, lantern, "hagatha",
        "Hagatha tells it, slow and fond:$B$BOn the Overlook Cliffs, far to the south, there lives a turtle the dwarves "
        "named Gammerita, after an aunt who was also very old and very cross. She has been bitten by everything that "
        "lives on that coast, and she has outlived all of it.$B$BShe smells of salt and grudges. Turn on your Sniff by "
        "the lantern and follow it south, all the way to the sea. Eat her, little horror. A spikeshell that has eaten "
        "Gammerita will outlive you, probably. That is the best thing a shell can do.",
        "Follow Gammerita's scent with Sniff south to the Overlook Cliffs, then devour Gammerita.",
        "Gammerita is still cross on her cliffs. Follow the grudges.",
        "Old and cross and gone at last. The dwarves will tell it for a hundred years.$B$BTake this.",
        objectives=[trail("Gammerita's scent followed", "Gammerita", 0,
                          [(120, -3195), (120, -3495), (90, -3795), (-60, -4095), (-225, -4395), (-30, -4665)],
                          summon=7977),
                    devour(1, "Gammerita devoured", entries=[7977])], prev=c.id, sort=s, xp=6,
        choices=[(22274, "Grizzled Pelt"), (9652, "Gryphon Rider's Leggings"), (19992, "Devilsaur Tooth")],
        story="Sniff out Gammerita, the cross old turtle of the cliffs, all the way to the sea, and eat her (Spikeshell).")
    onward(book, 9105239, 41, stv, lantern, 9105234, "North, past the Wetlands, the hills grow wild and the "
                                                     "owlbeasts forget the moon.")
    onward(book, 9105259, 41, alterac, lantern, 9105252, "East of the mountains the Hinterlands grow wild and the "
                                                         "owlbeasts forget the moon.")
    return e
