"""Task 021: the first lanterns abroad (levels 11-20). Part of tools/devourer_quests_content.py."""

from devourer_quests import devour, visit, emote, trail, struck, among, tale, ability, LINES, EMOTE_PET
from devourer_quests_content import breadcrumb, mercy, FACTION_SHY

Z_WESTFALL, Z_LOCHMODAN, Z_DARKSHORE, Z_BLOODMYST, Z_BARRENS, Z_SILVERPINE, Z_GHOSTLANDS = (
    40, 38, 148, 3525, 17, 130, 3433)
DERBY_WREN = 9101360                          # Wren at the Derby's starting line (task 020)
BONFIRE = 200                                 # the look of the sisters' campfire
BAIT = 216                                    # the look of Hagatha's Bait (the sisters' bubbling cauldron)
EMOTE_LAUGH, EMOTE_SHOO = 60, 129
HAGATHA_NAME, WREN_NAME = "Hagatha Hollowmoor", "Wren Hollowmoor"


def onward(book, qid, level, home, lantern, prev, line):
    """The last quest of a lantern: Hagatha points to the next one."""
    return breadcrumb(
        book, qid, f"A Lantern in {lantern.region}", level, home, lantern, 0,
        f"You have eaten what {home.region} had to teach, little horror. {line}$B$BI have hung another lantern in "
        f"{lantern.region}: {lantern.where}. Go to it. The beasts there are bigger, and so are the tales.",
        "You found it. Of course you did; you follow your stomach, and your stomach follows me.$B$BSit. Listen. "
        f"There is hunger in {lantern.region} too.",
        f"Hagatha sends the Devourer on to her lantern in {lantern.region}.", prev=prev)


def campfire(book, key, lantern, dx, dy, z, lines, reaction, speaker=HAGATHA_NAME):
    """The sisters' campfire beside a lantern: a tale, heard with Bramble."""
    return book.thing(key, "The Sisters' Campfire", BONFIRE, [(lantern.map, lantern.x + dx, lantern.y + dy, z, 0.0)],
                      size=0.6, lines=lines, speaker=speaker, companion=True, reaction=reaction)


def teens(book, homes):
    westfall = book.lantern("westfall", "Westfall", 0, -10800.0, 1100.0, 39.36, 5.6,
                            "the plains south-west of Sentinel Hill")
    lochmodan = book.lantern("lochmodan", "Loch Modan", 0, -5600.0, -3200.0, 325.16, 0.4,
                             "Grizzlepaw Ridge, south of Thelsamar")
    darkshore = book.lantern("darkshore", "Darkshore", 1, 6300.0, 150.0, 33.71, 2.9, "the hills south of Auberdine")
    bloodmyst = book.lantern("bloodmyst", "Bloodmyst Isle", 530, -2300.0, -11900.0, 25.92, 1.0,
                             "the red woods north of Blood Watch")
    barrens = book.lantern("barrens", "the Barrens", 1, -780.0, -2680.0, 92.04, 2.2,
                           "beside Wren's Derby, west of the Crossroads")
    silverpine = book.lantern("silverpine", "Silverpine Forest", 0, 500.0, 1200.0, 87.17, 4.0,
                              "the pines south of the Sepulcher")
    ghostlands = book.lantern("ghostlands", "the Ghostlands", 530, 7400.0, -6900.0, 51.34, 3.3,
                              "Sungraze Peak, south-west of Tranquillien")

    book.region("The first lanterns abroad (levels 11-20)",
                "Each home lantern points to one of seven lanterns abroad. Their quests lead into the first molts: "
                "the beasts and the named creatures the tier-2 forms grow on. Here the sisters start telling their "
                "tales by the campfire, for the Devourer and Bramble together.")

    nxt = {"elwynn": (9105019, westfall, "The plains west of it are full of hungry things that got there first."),
           "dunmorogh": (9105029, lochmodan, "Beyond the tunnel the troggs dig deeper and the crocolisks grow longer."),
           "teldrassil": (9105039, darkshore, "Across the water the cats grow black and the owls grow wise."),
           "azuremyst": (9105049, bloodmyst, "North of you the island bleeds, and its beasts have drunk it."),
           "durotar": (9105059, barrens, "West of you the grass goes on for ever, and so does what lives in it."),
           "mulgore": (9105069, barrens, "East of the mesas the grass goes on for ever, and so does what lives in it."),
           "tirisfal": (9105079, silverpine, "South of you the worgs howl under the pines."),
           "eversong": (9105089, ghostlands, "South of you the woods are dead, and the dead are hungry.")}
    for key, (qid, target, line) in nxt.items():
        home_lantern, finale = homes[key]
        onward(book, qid, 11, home_lantern, target, finale.id, line)

    return {
        "westfall": (westfall, westfall_quests(book, westfall)),
        "lochmodan": (lochmodan, lochmodan_quests(book, lochmodan)),
        "darkshore": (darkshore, darkshore_quests(book, darkshore)),
        "bloodmyst": (bloodmyst, bloodmyst_quests(book, bloodmyst)),
        "barrens": (barrens, barrens_quests(book, barrens)),
        "silverpine": (silverpine, silverpine_quests(book, silverpine)),
        "ghostlands": (ghostlands, ghostlands_quests(book, ghostlands)),
    }


def westfall_quests(book, lantern):
    s = Z_WESTFALL
    a = book.quest(
        9105100, "Goretusk Stew", 12, 11, lantern, lantern, "wren",
        "Wren's voice, munching something:$B$BMmf. Snack! Westfall's famous for its stew. Goretusk stew! The farmers "
        "used to make it before they all ran off. I want to make it, but I can't catch a goretusk from in here, so "
        "you eat the goretusks and I'll make the stew in my imagination.$B$BSix goretusks. The big grumpy ones are "
        "the tastiest. In my imagination.",
        "Devour 6 goretusks in Westfall.",
        "Imaginary stew needs real goretusks, Snack.",
        "Imaginary stew is DONE. It's the best stew I've never had.$B$BHere's your bowl. Well. Not a bowl.",
        objectives=[devour(6, "Goretusk devoured", entries=[454, 157, 547])], sort=s,
        choices=[(1310, "Smith's Trousers"), (5609, "Steadfast Cinch"), (5757, "Hardwood Cudgel")],
        story="The lesson, Wren's way: six goretusks for an imaginary stew.")
    book.quest(
        9105101, "Running with the Coyotes", 13, 12, lantern, lantern, "hagatha",
        "Hagatha's voice drifts out over the dry grass:$B$BThe coyotes of Westfall live on what the farmers left when "
        "they fled. They are thin, little horror, and thinness is a kind of hunger that has learned to wait.$B$BWear "
        "your wolf and go and run with them, in the fields around the Jansen Stead, in the north of Westfall. They will take you "
        "for a cousin from the forest. Do not eat any. Just learn how they wait.",
        "Wearing your Wolf (or what it grew into), walk among the coyotes at the Jansen Stead without starting a fight.",
        "They are waiting, little horror. Go and wait with them.",
        "Thin, and patient, and hungry. You have more in common with them than with the farmers.$B$BTake this.",
        objectives=[among("Ran with the coyotes", 0, -9686.0, 930.0, [834, 833], LINES["wolf"], radius=25.0)],
        prev=a.id, sort=s, needs=LINES["wolf"],
        choices=[(5299, "Gloves of the Moon"), (1306, "Wolfmane Wristguards"), (2908, "Thornblade")],
        story="For a Devourer with the Wolf shape: run with Westfall's coyotes as a cousin from the forest.")
    d = book.quest(
        9105103, "Old Murk-Eye", 18, 16, lantern, lantern, "hagatha",
        "Hagatha tells it low, like a secret:$B$BAt the far south of the Longshore there is a murloc so old that his "
        "eye has gone milky, and the other murlocs bring him fish so he will not eat them instead. Old Murk-Eye, the "
        "sailors call him. Whatever he has, he gives you: a wound that will not close.$B$BTurn on your Sniff by the "
        "lantern and follow the stink of old fish south, over the Dagger Hills, to the coast. Let him give you his "
        "wound, little horror. Then eat him. Toads stay in the swamp; the salamander is the one that crawled out and "
        "liked it.",
        "Follow Old Murk-Eye's stink with Sniff to the Longshore, let him infect you, then devour him.",
        "The old one still eats the coast.",
        "Old, and cold, and finally still. Something in your toad stirred when you swallowed him; I felt it from "
        "here.$B$BTake this. You have earned something better than murloc.",
        objectives=[trail("Old Murk-Eye's stink followed", "Old Murk-Eye", 0,
                          [(-10870, 1266), (-11041, 1349), (-11144, 1494), (-11200, 1671), (-11330, 1790)],
                          summon=391),
                    struck(1, "Volatile Infection felt", entries=[391]),
                    devour(1, "Old Murk-Eye devoured", entries=[391])], prev=a.id, sort=s, xp=6,
        choices=[(3431, "Bone-studded Leather"), (17694, "Band of the Fist"), (1264, "Headbasher")],
        story="Sniff out Old Murk-Eye along the coast, catch his infection, and eat him (a Water Salamander task).")
    book.quest(
        9105105, "Peck Order", 16, 14, lantern, lantern, "wren",
        "Wren, bouncing:$B$BSnack, your strider grew! It's got a beak like a PICKAXE now. The Defias are all over "
        "Westfall robbing farms, and they've never been pecked by anything with a beak like that. Wear your greater "
        "plainstrider and peck six of them. Properly. Rupturing.",
        "As a Greater Plainstrider, hit 6 Defias in Westfall with Rupturing Peck.",
        "Six Defias, Snack. Peck peck.",
        "Peck ORDER. I've been waiting all day to say that.$B$BHere!",
        objectives=[ability(6, "Defias pecked as a Greater Plainstrider", 9102001,
                            entries=[95, 504, 590, 589, 824, 1727, 122, 449], shapes=(16,))],
        prev=a.id, sort=s, needs=(16,),
        choices=[(1310, "Smith's Trousers"), (5609, "Steadfast Cinch"), (2908, "Thornblade")],
        story="For a Devourer with the Greater Plainstrider: Rupturing Peck six Defias.")
    return d


def lochmodan_quests(book, lantern):
    s = Z_LOCHMODAN
    bumble = book.beast("bumble", "Bumble", 1186, level=12, faction=FACTION_SHY, passive=True, scale=0.4,
                        subname="Black Bear Cub")
    fire = campfire(book, "loch_fire", lantern, 6.0, 6.0, 325.6, [
        "Sit, little horror. You too, Bramble. Closer to the fire; the loch wind bites.",
        "Before the dwarves built the dam, the loch was a valley, and a crocolisk lived in the stream at the bottom.",
        "It was not a big crocolisk. Then the dwarves closed the valley, and the stream became a lake.",
        "A crocolisk grows to fit its water. That is the whole secret of crocolisks.",
        "It grew, and it grew, and one morning a dwarf rowed out to fish, and came home without his boat.",
        "The children of Thelsamar do not believe it. The dwarf does. He still will not row.",
        "It comes up to the eastern shore, they say, when it smells something worth the climb.",
        "Remember that, little horror. You smell like something worth the climb."],
        "Bramble shivers. \"I'm never rowing anywhere again. Not that I was going to.\"")
    a = book.quest(
        9105110, "Stonesplinter Bones", 13, 12, lantern, lantern, "hagatha",
        "Hagatha speaks:$B$BThe Stonesplinter troggs of the valley south-east of here dig because digging is all they "
        "remember. Their bones are half stone already. A trogg that eats them grows harder in the back, where the "
        "blows land.$B$BEat six of them in Stonesplinter Valley.",
        "Devour 6 Stonesplinter troggs in Loch Modan.",
        "Six troggs. They are still digging.",
        "Hard to chew? Good. Something hard to chew is something hard to kill.$B$BTake this.",
        objectives=[devour(6, "Stonesplinter trogg devoured", entries=[1161, 1162, 1166, 1163, 1197, 1164])],
        sort=s,
        choices=[(5629, "Hammerfist Gloves"), (24351, "Mace of the Hand"), (22998, "Ghostclaw Leggings")],
        story="The lesson: six Stonesplinter troggs, for a trogg's hard back.")
    b = book.quest(
        9105111, "The Boat-Eater", 15, 13, lantern, lantern, "hagatha",
        "Hagatha's voice, warm for once:$B$BI have lit a fire beside the lantern. Bring your little friend, the one "
        "who follows you about and talks to her boots. Sit with her, and I will tell you both a tale about this "
        "loch.$B$BThe tale is for her as much as for you. Listen to it together, or not at all.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit. Bring her, and sit.",
        "You listened. She listened too; I watched her ears.$B$BNow you know where it comes up. Take this, and when "
        "you are ready, go and be worth the climb.",
        objectives=[tale(fire, "The tale of the Boat-Eater heard")], prev=a.id, sort=s, xp=4,
        choices=[(1310, "Smith's Trousers"), (5351, "Bounty Hunter's Ring"), (2908, "Thornblade")],
        story="A campfire tale for the Devourer and Bramble: the crocolisk that grew to fit the loch.")
    d = book.quest(
        9105113, "Worth the Climb", 22, 20, lantern, lantern, "hagatha",
        "Hagatha, pleased with herself:$B$BYou heard the tale. Now taste it. Turn on your Sniff by the lantern and "
        "follow the crocolisk smell south and around the shore of the loch, past the excavation, to the eastern "
        "shore. When you get there, it will smell you, and it will decide you are worth the climb.$B$BIt will be "
        "wrong. Eat it. A komodo that has eaten the Boat-Eater is ready to become a dragon.",
        "Follow the Boat-Eater's scent with Sniff around the loch, then devour the Large Loch Crocolisk.",
        "It is still at the bottom of the loch. Follow your nose around the shore.",
        "A crocolisk that ate a boat, and a Devourer that ate the crocolisk. The children will tell it now.$B$B"
        "Take this. And when your komodo is grown enough, it will know what to do.",
        objectives=[trail("The Boat-Eater's scent followed", "the Boat-Eater", 0,
                          [(-5745, -3405), (-5595, -3600), (-5415, -3735), (-5220, -3645)], summon=2476),
                    devour(1, "Large Loch Crocolisk devoured", entries=[2476])], prev=b.id, sort=s, xp=6,
        choices=[(6670, "Panther Armor"), (16659, "Deftkin Belt"), (6093, "Orc Crusher")],
        story="Follow the Boat-Eater's scent around the loch, and eat the Large Loch Crocolisk (a Komodo Dragon task).")
    mercy(book, 9105114, "Bumble", 13, lantern, bumble,
          [(-5655, -3150), (-5700, -3105), (-5745, -3090)],
          "Wren, worried:$B$BSnack, there's a bear cub up on Grizzlepaw Ridge, west of the lantern, and it's stuck. "
          "It climbed up after honey and now it's crying because it can't climb down. It smells of honey and bark "
          "and silly decisions.$B$BSniff it out. Pat it. Show it the way down.",
          "Honey and bark, Snack. And silly decisions.",
          "It followed you all the way down! Bears are terrible at climbing down. So am I. I once got stuck in a "
          "chimney for a day. Then it lumbered off into the woods to find more honey. Bumble will remember you; "
          "bears remember whoever got them down.$B$BHere's a cub to keep for now, a dwarven one. It won't climb "
          "anything. Probably.",
          (44970, "Dun Morogh Cub", 1), s,
          "Mercy: Sniff out Bumble, a bear cub stuck on Grizzlepaw Ridge, and lead it down. It comes back grown "
          "(mounts idea 1). Reward: a bear cub companion.", prev=a.id)
    return d


def darkshore_quests(book, lantern):
    s = Z_DARKSHORE
    a = book.quest(
        9105120, "Moonstalkers", 12, 11, lantern, lantern, "hagatha",
        "Hagatha speaks under her breath:$B$BThe moonstalkers of Darkshore are the nightsaber's darker cousins. The "
        "night elves left this coast to them when they left everything else. Eat six of them, little horror, the "
        "runts and the grown ones. A saber needs to know the dark it hunts in.",
        "Devour 6 moonstalkers in Darkshore.",
        "Six moonstalkers. They are darker than the night, but not darker than you.",
        "Darker. Quieter. Hungrier. Your cat will be all three one day.$B$BTake this.",
        objectives=[devour(6, "Moonstalker devoured", entries=[2070, 2069])], sort=s,
        choices=[(5299, "Gloves of the Moon"), (22998, "Ghostclaw Leggings"), (5279, "Harpy Skinner")],
        story="The lesson: six moonstalkers, the dark the saber hunts in.")
    b = book.quest(
        9105121, "A Moonkin Among Moonkin", 13, 12, lantern, lantern, "hagatha",
        "Hagatha speaks, and the flame goes silver:$B$BAn owl that eats enough moonlight stands up one night and "
        "becomes a moonkin. The young moonkin of Darkshore wander the woods right around this lantern, hooting at "
        "the trees.$B$BWear your owl, little horror, and go and stand among them. They will think you are one of "
        "them who has not stood up yet. Let them think it. Listen to what they hoot about.",
        "Wearing your Owl (or what it grew into), walk among the young moonkin around the lantern without starting a "
        "fight.",
        "They are hooting for you, little horror.",
        "What do they hoot about? The moon, mostly. And you, now. They think you are a late bloomer.$B$BTake this.",
        objectives=[among("Stood among the young moonkin", 1, 6297.0, 95.0, [10159, 10158, 10160], LINES["owl"],
                          radius=20.0)],
        prev=a.id, sort=s, needs=LINES["owl"],
        choices=[(1306, "Wolfmane Wristguards"), (1310, "Smith's Trousers"), (24351, "Mace of the Hand")],
        story="For a Devourer with the Owl shape: stand among the young moonkin as one who has not stood up yet.")
    c = book.quest(
        9105122, "The Oracle's Moon", 15, 13, lantern, lantern, "hagatha",
        "Hagatha's tale comes silver and sharp:$B$BThe moonkin oracles of Darkshore went mad when the coast went dark. "
        "They wander the woods south of the lantern, calling the moon down on anything that moves.$B$BLet one call "
        "it down on you, little horror. Feel what the moon does to the mad. Then eat the oracle. Your owl is waiting "
        "to stand up, and it needs to know what standing up costs.",
        "Let a Moonkin Oracle cast its Moonfire on you, then devour a Moonkin Oracle in Darkshore.",
        "The oracles still call the moon. Go and be called.",
        "Moonlight and madness. A heavy meal. Your owl will carry it.$B$BTake this.",
        objectives=[struck(1, "The oracle's moon felt", entries=[10157]),
                    devour(1, "Moonkin Oracle devoured", entries=[10157])], prev=b.id, sort=s,
        choices=[(26023, "Ravager Hide Gloves"), (3585, "Camouflaged Tunic"), (2908, "Thornblade")],
        story="Hagatha's tale of the mad oracles: feel the oracle's Moonfire, then eat it (a Moonkin task).")
    d = book.quest(
        9105123, "Shadowclaw", 16, 14, lantern, lantern, "hagatha",
        "Hagatha's voice drops to almost nothing:$B$BOn Darkshore they say a black cat once swallowed a scream, and it "
        "has hunted in silence ever since. Shadowclaw. It walks the woods north of here and comes when it pleases, "
        "which is rarely.$B$BIt leaves no tracks. It leaves a smell, though: cold ash and old fear. Turn on your Sniff "
        "by the lantern and follow it. When the trail ends, the cat will be there. It will curse you, little horror; "
        "a cursed meal tastes no worse. Eat it.",
        "Follow Shadowclaw's scent with Sniff north of the lantern, then devour Shadowclaw.",
        "The cat still hunts in silence. Follow the ash.",
        "Did it scream when it died? No. It had nothing left to scream with.$B$BTake this, and when your saber is "
        "ready, you will hunt as quietly as that.",
        objectives=[trail("Shadowclaw's scent followed", "Shadowclaw", 1,
                          [(6400, 177), (6461, 272), (6560, 300)], summon=2175),
                    devour(1, "Shadowclaw devoured", entries=[2175])], prev=c.id, sort=s, xp=6,
        choices=[(3741, "Stomping Boots"), (17694, "Band of the Fist"), (3431, "Bone-studded Leather")],
        story="Sniff out Shadowclaw, the cat that swallowed a scream, and eat it (a Shadowclaw task).")
    return d


def bloodmyst_quests(book, lantern):
    s = Z_BLOODMYST
    fire = campfire(book, "bloodmyst_fire", lantern, 6.0, 6.0, 25.4, [
        "Come, sit. Bramble, you sit there, where the smoke will not find you.",
        "When the draenei's ship fell, it fell with moths in its belly. Blue ones, from a world that is gone.",
        "They flew out of the wreck into the red woods and found they had nothing to eat but dreams.",
        "So they ate the dreams of everything that slept here. The bears. The elekk. The draenei children.",
        "That is why they are so blue, little horror. Blue is the colour of other people's dreams.",
        "Never let one land on you when you sleep. It will not hurt. You will just wake up a little less.",
        "And if you eat one... well. Then you will have dreams that are not yours. Some of them are lovely."],
        "Bramble rubs her eyes. \"I'm keeping my dreams. All of them. Even the one with the soup.\"")
    a = book.quest(
        9105130, "Ravager Hatchlings", 12, 11, lantern, lantern, "wren",
        "Wren, horrified and delighted:$B$BSnack, the red island has RAVAGERS. Babies! All claws and no manners. They "
        "fell out of the ship with everything else and they've been eating the island ever since. That's YOUR "
        "job.$B$BEat six of the hatchlings before they grow up and get ideas.",
        "Devour 6 Bloodmyst Hatchlings on Bloodmyst Isle.",
        "Six hatchlings, Snack. They're getting ideas.",
        "Crunchy babies. That sounds bad when I say it out loud.$B$BHere!",
        objectives=[devour(6, "Bloodmyst Hatchling devoured", entries=[17525])], sort=s,
        choices=[(26023, "Ravager Hide Gloves"), (23408, "Farstrider's Bracers"), (2908, "Thornblade")],
        story="The lesson, Wren's way: the ravager hatchlings, eaten before they grow up.")
    b = book.quest(
        9105131, "Other People's Dreams", 14, 12, lantern, lantern, "hagatha",
        "Hagatha's voice, low and kind:$B$BI have lit a fire beside the lantern. Fetch your little friend, the one "
        "who keeps her dreams in her boots, and sit with her. I have a tale about the blue moths of this island, "
        "and it is a tale for two.",
        "Sit at the Sisters' Campfire by the lantern with Bramble, and hear Hagatha's tale to its end.",
        "The fire is lit. Bring her.",
        "Some of them are lovely, I said, and I meant it. The flutterers drift over the north of the island, along "
        "the Bloodwash. If your moth is ever hungry for a dream that is not yours, you know where they are.$B$BTake "
        "this.",
        objectives=[tale(fire, "The tale of the blue moths heard")], prev=a.id, sort=s, xp=4,
        choices=[(22998, "Ghostclaw Leggings"), (5351, "Bounty Hunter's Ring"), (5757, "Hardwood Cudgel")],
        story="A campfire tale for the Devourer and Bramble: the blue moths that eat other people's dreams.")
    c = book.quest(
        9105132, "Where the World Is Thin", 16, 15, lantern, lantern, "hagatha",
        "Hagatha's voice comes wrong, as if from far away:$B$BWhere the ship's engine broke open, at the Warp Piston "
        "in the north-east, the world has thinned to a rag. Things come through. Void anomalies, the draenei call "
        "them: little tears that learned to move.$B$BGo and stand at the Piston, little horror, right where the "
        "world is thinnest. Feel it pull. Then eat three of the anomalies. You were born from the dark between; you "
        "will find they taste of home.",
        "Stand at the Warp Piston on Bloodmyst Isle, then devour 3 Void Anomalies there.",
        "Three anomalies, and the place where they come through.",
        "Home, wasn't it? Cold and close. Your voidling and your warp stalker will both grow on that taste.$B$B"
        "Take this.",
        objectives=[visit("Stood where the world is thin", 530, -1220.0, -11810.0, radius=30.0),
                    devour(3, "Void Anomaly devoured", entries=[17550])], prev=b.id, sort=s,
        choices=[(3585, "Camouflaged Tunic"), (1306, "Wolfmane Wristguards"), (24351, "Mace of the Hand")],
        story="Stand where the world is thin at the Warp Piston and eat what comes through (a Void line task).")
    d = book.quest(
        9105133, "Wyrmscar", 17, 15, lantern, lantern, "wren",
        "Wren, whispering for once:$B$BSnack, on Wyrmscar Island in the south-west there are dragons. Well, little "
        "ones. Bony veridian whelps, still flapping around the bones of the dragon they came from. Hagatha says if "
        "you eat one, you'll see what it saw last: its mother's bones. Eat one, then go and stand where it "
        "showed you.$B$BThen eat four more. Bones are good for your teeth!",
        "Devour a veridian whelp, go where its last memory shows you, then devour 4 more on Wyrmscar Island.",
        "Did you see the bones? Go and stand there, Snack.",
        "Dragon! You've eaten DRAGON. Well, dragon-ish. I'm telling everyone.$B$BHere's your prize.",
        objectives=[devour(1, "Veridian whelp devoured (you see great bones)", entries=[17588, 17589]),
                    visit("The dragon's bones", 530, -1350.0, -12350.0, radius=40.0),
                    devour(4, "Veridian whelp devoured", entries=[17588, 17589])], prev=c.id, sort=s, xp=6,
        choices=[(3741, "Stomping Boots"), (16990, "Spritekin Cloak"), (1264, "Headbasher")],
        story="Wren sends the Devourer to Wyrmscar Island: eat a whelp, see its mother's bones in its last memory, stand there, eat more (Whelp line).")
    book.quest(
        9105135, "Sweet Dreams, Bears", 16, 14, lantern, lantern, "wren",
        "Wren, whispering:$B$BSnack, your moth is BLUE now. Royal blue! The dream-eating kind! Hagatha says it can "
        "puff spores that put things to sleep. The bears of Bloodmyst are grumpy from the crystals and they haven't "
        "slept in months.$B$BWear your flutterer. Puff sleep spores on five bears. Give them a nap. And maybe a dream. "
        "A nice one.",
        "As a Royal Blue Flutterer, put 5 Bloodmyst bears to sleep with Sleep Spores.",
        "Five sleepy bears, Snack. Shh.",
        "Five bears, snoring. I could hear it through the lantern. Did you give them good dreams? I think you "
        "did.$B$BHere!",
        objectives=[ability(5, "Bear put to sleep as a Flutterer", 9102072, entries=[17345, 17347, 17348],
                            shapes=(23,))],
        prev=a.id, sort=s, needs=(23,),
        choices=[(22998, "Ghostclaw Leggings"), (5351, "Bounty Hunter's Ring"), (5757, "Hardwood Cudgel")],
        story="For a Devourer with the Royal Blue Flutterer: Sleep Spores on five sleepless Bloodmyst bears.")
    book.quest(
        9105136, "Spit at the Dark", 17, 15, lantern, lantern, "hagatha",
        "Hagatha, low:$B$BYou wear the voidling now, little horror: a small piece of the dark between, with a mouth "
        "that should not be there. At the Warp Piston the void anomalies come through the same tear you did.$B$BWear "
        "it. Spit at five of them. Let the dark see what came out of it and learned to spit.",
        "As a Voidling, hit 5 Void Anomalies at the Warp Piston with Void Spit.",
        "Five anomalies, little horror, spat at properly.",
        "The dark saw. It will remember you, and that is no bad thing.$B$BTake this.",
        objectives=[ability(5, "Anomaly spat at as a Voidling", 9102254, entries=[17550], shapes=(41,))],
        prev=a.id, sort=s, needs=(41,),
        choices=[(3585, "Camouflaged Tunic"), (1306, "Wolfmane Wristguards"), (24351, "Mace of the Hand")],
        story="For a Devourer with the Voidling: Void Spit at five anomalies at the Warp Piston.")
    return d


def barrens_quests(book, lantern):
    s = Z_BARRENS
    littlethunder = book.beast("littlethunder", "Little Thunder", 3234, level=12, faction=FACTION_SHY,
                               passive=True, scale=0.35, subname="Kodo Calf")
    a = book.quest(
        9105140, "Fleeting Legs", 12, 11, lantern, lantern, "hagatha",
        "Hagatha's voice rolls over the grass:$B$BIn Mulgore they tell of a chick that never stopped running. The "
        "wind caught up with it once, and has been chasing it ever since. Its children are here: the greater "
        "plainstriders, the fleeting ones, the ornery ones.$B$BEat six of them, little horror. Your strider has more "
        "running in it than it knows.",
        "Devour 6 plainstriders in the Barrens.",
        "Six striders. They will not stand still for you.",
        "Did you feel the wind? That was the chase. One day you will be the one it is chasing.$B$BTake this.",
        objectives=[devour(6, "Barrens plainstrider devoured", entries=[3244, 3246, 3245])], sort=s,
        choices=[(1306, "Wolfmane Wristguards"), (5299, "Gloves of the Moon"), (5279, "Harpy Skinner")],
        story="The lesson: Hagatha's tale of the chick the wind chases, and six Barrens plainstriders.")
    b = book.quest(
        9105141, "The Last Laugh", 15, 13, lantern, lantern, "wren",
        "Wren, offended:$B$BSnack, the hecklefang hyenas LAUGH at everything. At the caravans. At the kodos. At ME, "
        "through the lantern, I heard them. Hagatha says hyenas laugh because they're scared, and the one thing a "
        "scared laugher can't stand is being laughed at.$B$BGo and laugh at them. Five of them. Right in their silly "
        "spotty faces. See who's laughing then.",
        "Laugh (/laugh) at 5 hecklefang hyenas in the Barrens and send them running.",
        "They're still laughing, Snack. Laugh LOUDER.",
        "They RAN! With their tails down! Who's laughing now? Us. We're laughing.$B$BHere, for the best laugh in the "
        "Barrens.",
        objectives=[emote(5, "Hecklefang laughed off", EMOTE_LAUGH, entries=[4127, 4129], flee=True)],
        prev=a.id, sort=s,
        choices=[(1310, "Smith's Trousers"), (5609, "Steadfast Cinch"), (24351, "Mace of the Hand")],
        story="Wren hates being laughed at: laugh at the hecklefang hyenas until they run.")
    c = book.quest(
        9105142, "Thunder in a Small Lizard", 17, 15, lantern, lantern, "hagatha",
        "Hagatha tells it, and the flame crackles:$B$BThe thunder lizards of the Barrens swallowed a storm once, the "
        "tauren say, and they have been spitting it out a little at a time ever since. The stormsnouts in the south "
        "throw lightning from their mouths like a cough.$B$BTake your little friend; she has never seen lightning up close, and she should. Eat three where she "
        "can see. A thing that eats lightning learns that the sky is only another kind of meal.",
        "With Bramble watching, devour 3 thunder lizards in the Barrens.",
        "Three lizards, and Bramble has to see.",
        "Your hair is standing up. Do you have hair? Something is standing up.$B$BTake this.",
        objectives=[devour(3, "Thunder lizard devoured, Bramble watching", entries=[3240, 3239, 3238],
                           companion="My hair's standing up! Is that supposed to happen? Do it again!")], prev=b.id, sort=s,
        choices=[(3741, "Stomping Boots"), (26023, "Ravager Hide Gloves"), (5757, "Hardwood Cudgel")],
        story="Hagatha's tale of the lizards that swallowed a storm: eat three while Bramble watches the lightning.")
    d = book.quest(
        9105143, "The Thunderhawk Nests", 19, 17, lantern, lantern, "hagatha",
        "Hagatha tells it, and thunder rumbles somewhere in the flame:$B$BThe tauren say the thunder is only the "
        "wind serpents clearing their throats. Their young nest in the south, at Agama'gor. A strider that eats one "
        "learns how the wind feels from above; a snake that eats one starts to grow wings.$B$BTurn on your Sniff and "
        "follow the smell of rain south-west from the lantern. At the end of it a hatchling will be waiting. Eat it. "
        "Then Wren has something for you.",
        "Follow the smell of rain with Sniff to Agama'gor, then devour a Thunderhawk Hatchling.",
        "The hatchlings still nest in the south. Follow the rain.",
        "Did you feel the sky in it? Good.$B$BTake this. And go and see my sister at her starting line; she has "
        "been bursting to tell you something for days.",
        objectives=[trail("The smell of rain followed", "a Thunderhawk Hatchling", 1,
                          [(-990, -2520), (-1200, -2310), (-1395, -2190), (-1605, -2145), (-1800, -2145)],
                          summon=3247),
                    devour(1, "Thunderhawk Hatchling devoured", entries=[3247])], prev=c.id, sort=s, xp=6,
        choices=[(6670, "Panther Armor"), (17694, "Band of the Fist"), (6093, "Orc Crusher")],
        story="Sniff the smell of rain to a thunderhawk nest and eat the hatchling (a Greater Plainstrider task).")
    book.quest(
        9105144, "Wren's Starting Line", 20, 20, lantern, DERBY_WREN, "wren",
        "Wren's voice, so excited it squeaks:$B$BSnack! SNACK. Come to the starting line, right next to the lantern, "
        "by the road west of the Crossroads. I'm there! Well, a bit of me is there. Enough of me to start a race. "
        "I'll explain when you get here.$B$BBring Bramble!",
        "Speak with Wren Hollowmoor at the Derby's starting line, west of the Crossroads.",
        "I'm RIGHT HERE, Snack.",
        "You came! Hagatha thinks her bird can beat you. Her BIRD. Let me tell you about the bet...",
        prev=d.id, sort=s, xp=2,
        story="Wren calls the Devourer to the Derby's starting line (Wren's Derby, task 020).")
    mercy(book, 9105145, "Little Thunder", 13, lantern, littlethunder,
          [(-702, -2629), (-677, -2532), (-600, -2480)],
          "Wren, softly:$B$BSnack, a kodo calf got left behind when its herd ran from the hyenas. It's north of the "
          "lantern, all knees and worry, and every time it takes a step the ground goes thump. It smells of dust and "
          "milk and being frightened.$B$BSniff it out. Pat it. It'll find its herd; kodos always do, once they stop "
          "being scared.",
          "Dust and milk and being frightened, Snack.",
          "It followed you, thump thump thump, and then it heard its herd and it RAN. The ground shook. Nobody laughed "
          "at it. Little Thunder will remember you; kodos never forget a kindness, it's why they're so slow.$B$BHere's "
          "something for the road.",
          (5609, "Steadfast Cinch", 1), s,
          "Mercy: Sniff out Little Thunder, a kodo calf left behind by its herd, and pat it. It comes back grown "
          "(mounts idea 1).", prev=a.id)
    book.quest(
        9105146, "Quilboar Bacon", 15, 13, lantern, lantern, "wren",
        "Wren, scandalised:$B$BSnack, the quilboar of Thorn Hill are throwing rocks at the caravans AND they smell. "
        "That's two crimes. And you're an agam'ar now, which is a boar that's been hit so often it stopped falling "
        "over. The quilboar say a boar struck often enough forgets how to fall. Let's find out!$B$BWear your agam'ar "
        "and charge six Razormane. Tremor Charge. The ground should shake.",
        "As a Raging Agam'ar, charge 6 Razormane quilboar in the Barrens with Tremor Charge.",
        "Six quilboar, Snack. They're still throwing rocks.",
        "Justice! Smelly, shaking justice.$B$BHere's your reward for being a good agam'ar.",
        objectives=[ability(6, "Razormane charged as an Agam'ar", 9102022, entries=[3267, 3268, 3265, 3266, 3269, 3271],
                            shapes=(18,))],
        prev=a.id, sort=s, needs=(18,),
        choices=[(1310, "Smith's Trousers"), (5609, "Steadfast Cinch"), (24351, "Mace of the Hand")],
        story="For a Devourer with the Raging Agam'ar: Tremor Charge six rock-throwing Razormane quilboar.")
    return d


def silverpine_quests(book, lantern):
    s = Z_SILVERPINE
    a = book.quest(
        9105150, "Worg Meat", 12, 11, lantern, lantern, "hagatha",
        "Hagatha speaks, and somewhere a wolf howls:$B$BThe worgs of Silverpine are wolves that remember something "
        "older. Their eyes are too clever. Eat six of them, little horror, the plain worgs and the mottled ones. A "
        "wolf that has eaten worg starts to remember too.",
        "Devour 6 worgs in Silverpine Forest.",
        "Six worgs. They watch you from the pines.",
        "Clever eyes, and now clever in your belly. Your wolf is listening.$B$BTake this.",
        objectives=[devour(6, "Worg devoured", entries=[1765, 1766])], sort=s,
        choices=[(1306, "Wolfmane Wristguards"), (5299, "Gloves of the Moon"), (2908, "Thornblade")],
        story="The lesson: six worgs of Silverpine, the wolves that remember something older.")
    b = book.quest(
        9105151, "Shoo!", 14, 12, lantern, lantern, "wren",
        "Wren, exhausted:$B$BSnack, the Moonrage gnolls howl at the moon all night and I can hear it from HERE. In "
        "the In-Between. Through a lantern. That's how loud they are. I haven't slept in three days.$B$BGo to their "
        "camps north-east of the lantern and SHOO them. Wave your arms. Say shoo. Five of them. Gnolls hate being "
        "shooed; it's undignified.",
        "Shoo (/shoo) 5 Moonrage gnolls in Silverpine Forest and send them running.",
        "Still howling, Snack. Still awake. Shoo harder.",
        "Silence! Beautiful silence. I'm going to have the best nap.$B$BHere, and goodnight. Don't wake me.",
        objectives=[emote(5, "Moonrage gnoll shooed", EMOTE_SHOO, entries=[1769, 1770, 1779, 1782, 1924],
                          flee=True)],
        prev=a.id, sort=s,
        choices=[(1310, "Smith's Trousers"), (5609, "Steadfast Cinch"), (24351, "Mace of the Hand")],
        story="Wren cannot sleep for the Moonrage gnolls' howling: shoo them away.")
    c = book.quest(
        9105152, "Behind the Pack", 17, 15, lantern, lantern, "hagatha",
        "Hagatha tells it, and the flame runs red:$B$BEvery pack has one that runs behind the others. Not out of "
        "fear, little horror. It is choosing which leg to take first. Along the Greymane Wall, in the south, those "
        "ones have become a pack of their own: the bloodsnout worgs.$B$BWear your wolf and run behind them. They will "
        "let you, because you smell like their future. Do not bite. Not yet. Learn what it is to choose.",
        "Wearing your Wolf (or what it grew into), walk among the Bloodsnout Worgs at the Greymane Wall without "
        "starting a fight.",
        "They are waiting at the wall, little horror. Run behind them.",
        "Did they let you? Of course they did. That is what your wolf will be.$B$BTake this.",
        objectives=[among("Ran behind the bloodsnouts", 0, -574.0, 1549.0, [1923], LINES["wolf"], radius=25.0)],
        prev=b.id, sort=s, needs=LINES["wolf"],
        choices=[(3585, "Camouflaged Tunic"), (26023, "Ravager Hide Gloves"), (5757, "Hardwood Cudgel")],
        story="For a Devourer with the Wolf shape: run behind the Bloodsnout Worgs, the wolf's own future.")
    d = book.quest(
        9105153, "Fenris Isle", 18, 16, lantern, lantern, "hagatha",
        "Hagatha's voice turns sharp:$B$BOn Fenris Isle, in the lake, the Rot Hide gnolls dig up the dead and eat "
        "them, and the dead have cursed them for it. The Curse of Thule, they call it. Let one of them pass the "
        "curse to you, little horror, so you know what grave-robbing costs. Then eat five of them.$B$BSomebody has "
        "to eat the Rot Hides; that is how the world stays tidy.",
        "Let a Rot Hide gnoll curse you, then devour 5 Rot Hide gnolls on Fenris Isle in Silverpine Forest.",
        "Five Rot Hides, and one curse. The isle is full of both.",
        "Tidy. I like tidy. The curse will fade; the taste will not.$B$BTake this, little horror. You have earned it.",
        objectives=[struck(1, "The Curse of Thule felt", entries=[1939, 1940, 1942, 1943]),
                    devour(5, "Rot Hide devoured", entries=[1939, 1940, 1942, 1943])], prev=c.id, sort=s, xp=6,
        choices=[(3741, "Stomping Boots"), (17694, "Band of the Fist"), (1264, "Headbasher")],
        story="Hagatha keeps the world tidy: feel the grave-robbers' curse, then eat the Rot Hides of Fenris Isle.")
    book.quest(
        9105155, "Open a Vein", 16, 14, lantern, lantern, "hagatha",
        "Hagatha, with something like pride:$B$BYour bat has grown teeth that fit it. The vampiric duskbat drinks, "
        "little horror; it does not nibble. The Rot Hide gnolls on Fenris Isle are full of the blood of the dead they "
        "dug up, and nobody will miss it.$B$BWear your duskbat. Open five of them, and drink.",
        "As a Vampiric Duskbat, open 5 Rot Hide gnolls on Fenris Isle with Exsanguinate.",
        "Five Rot Hides, little horror, opened properly.",
        "Old blood, but blood. Your duskbat knows what it is for now.$B$BTake this.",
        objectives=[ability(5, "Rot Hide opened as a Vampiric Duskbat", 9102051, entries=[1939, 1940, 1942, 1943],
                            shapes=(21,))],
        prev=a.id, sort=s, needs=(21,),
        choices=[(3585, "Camouflaged Tunic"), (26023, "Ravager Hide Gloves"), (5757, "Hardwood Cudgel")],
        story="For a Devourer with the Vampiric Duskbat: Exsanguinate five Rot Hides on Fenris Isle.")
    return d


def ghostlands_quests(book, lantern):
    s = Z_GHOSTLANDS
    a = book.quest(
        9105160, "Ghostclaw", 12, 11, lantern, lantern, "hagatha",
        "Hagatha speaks, and the flame goes pale:$B$BThe lynxes of the Ghostlands starve, because the Scourge ate "
        "everything first. A starving cat is the most honest hunter there is. Eat six of them, little horror, the "
        "starving ones and the ghostclaws.",
        "Devour 6 Ghostclaw lynxes in the Ghostlands.",
        "Six cats. They are thin; you will have to be quick.",
        "Honest hunger. Remember the taste; you will meet the other kind soon enough.$B$BTake this.",
        objectives=[devour(6, "Ghostclaw lynx devoured", entries=[16347, 16348, 16349])], sort=s,
        choices=[(22998, "Ghostclaw Leggings"), (5299, "Gloves of the Moon"), (5279, "Harpy Skinner")],
        story="The lesson: six Ghostclaw lynxes, and honest hunger.")
    b = book.quest(
        9105162, "What the Word Means", 13, 12, lantern, lantern, "hagatha",
        "Hagatha, amused:$B$BNorth-east of the lantern, by the Sanctum of the Moon, there are things the elves call "
        "arcane devourers. Devourers! As if a little ball of spilled magic knew what the word means.$B$BWalk into the "
        "sanctum quietly, little horror, without a fight at the door, so they get a good look at what is coming. "
        "Then eat four of them, and show them what the word means.",
        "Walk into the Sanctum of the Moon without being in a fight, then devour 4 Arcane Devourers there.",
        "They are still calling themselves devourers.",
        "Now there is only one Devourer near the Sanctum of the Moon.$B$BTake this. Your wyrm drank well.",
        objectives=[visit("Walked into the Sanctum of the Moon", 530, 7478.0, -6406.0, radius=35.0, quiet=True),
                    devour(4, "Arcane Devourer devoured", entries=[16304])], prev=a.id, sort=s,
        choices=[(3585, "Camouflaged Tunic"), (26023, "Ravager Hide Gloves"), (2908, "Thornblade")],
        story="Hagatha mocks the 'Arcane Devourers': walk in quietly, then show them what the word means.")
    d = book.quest(
        9105163, "Eyes Shut, Counting", 17, 15, lantern, lantern, "wren",
        "Wren, from very far back in the lantern:$B$BSnack I'm not coming closer to the glass because your spiders "
        "are THIS big. The spindlewebs! They're everywhere down there. Hagatha says spiders are good for you. Hagatha "
        "is not the one who has to look at them.$B$BSo here's what's happening. I'm shutting my eyes and counting to "
        "three hundred. When I open them, five spiders have to be gone. Into you. Go!",
        "Devour 5 spindleweb spiders in the Ghostlands before Wren finishes counting (5 minutes).",
        "...two hundred and ninety-nine, three hundred. Are they gone? THEY'RE NOT GONE. Again!",
        "...three hundred. Are they gone? Really gone? Okay. Okay. I'm coming back to the glass.$B$BHere. You're "
        "very brave. I'm very brave too, for not screaming.",
        objectives=[devour(5, "Spindleweb spider devoured", entries=[16350, 16351, 16352])], prev=b.id, sort=s,
        xp=6, timed=300,
        choices=[(3741, "Stomping Boots"), (16990, "Spritekin Cloak"), (1264, "Headbasher")],
        story="Wren shuts her eyes and counts to 300; five spindleweb spiders must be gone when she opens them.")
    book.quest(
        9105165, "Swallow It Whole", 15, 13, lantern, lantern, "hagatha",
        "Hagatha, amused again:$B$BYour wyrm grew into a wraith, little horror, and a wraith does not spit magic back. "
        "It swallows it in the air. The mana shifters at the Sanctum of the Moon cast and cast and never finish a "
        "thought.$B$BWear your arcane wraith. When one of them starts a spell, swallow it. Five times.",
        "As an Arcane Wraith, swallow 5 spells cast by Mana Shifters or Arcane Devourers with Swallow Spell.",
        "Five spells, little horror, swallowed before they land.",
        "Did they taste of anything? Surprise, mostly. That is the taste of a spell that never finished.$B$BTake this.",
        objectives=[ability(5, "Spell swallowed as an Arcane Wraith", 9102062, entries=[16310, 16304], shapes=(22,))],
        prev=a.id, sort=s, needs=(22,),
        choices=[(22998, "Ghostclaw Leggings"), (5351, "Bounty Hunter's Ring"), (24351, "Mace of the Hand")],
        story="For a Devourer with the Arcane Wraith: Swallow Spell five of the Sanctum's casters mid-cast.")
    return d
