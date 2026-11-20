# Rematch: all dialogue

Working copy (source of truth while we iterate; started from the scripts via `game/tools/rematch/dialogue_sheet.py`). Each box is one message window sequence; blank lines are page breaks (the player presses A). **🟡** marks lines new in the latest round, for review (**✨** earlier rounds). **↻ Again** lines (in `code font`): what a character says the second time you talk to them, and every time after. Variables: `{PLAYER}` (default RED), `{RIVAL}` (BLUE), `{BORN_YEAR}` (1993), `{PLAY_YEAR}` (2007); derived from them and the current year: `{AGE_THEN}` (age when they played), `{AGE_NOW}`, `{YEARS_AGO}` (years since they played).

## Home (Mom)

### Mom

> MOM: Have a wonderful time, dear!

### MomStopsYou

> MOM: {PLAYER}! Wait!

> MOM: Don't run off yet! Something came for you this morning.

### Letter

> MOM: A letter came for you, dear! There's no name on it.
>
> Let's see what it says...

*[the letter is shown in neutral text, like a narrator]*

> "Dear {PLAYER},
>
> You were the kid from PALLET TOWN who made it into the HALL OF FAME."

> Tonight, everyone from that journey is gathering one more time.

> It's all arranged and all paid for. All that's missing is you.
>
> I'll be waiting at the end of the night.
>
> - A friend from the old days"

> MOM: Oh! There's something else in the envelope...

*[received S.S. TICKET jingle]*

> A cruise ticket! The ship is leaving right away, dear.

> 🟡 Oh, and I found your old FAME CHECKER in your desk drawer. Take it!
>
> You'll want to remember everyone you see tonight.

*[🟡 receives the FAME CHECKER, item jingle]*

> ✨ Take CHARIZARD, PIKACHU and LAPRAS with you. They've been pacing by the door since breakfast.
>
> They know something's up.

*[✨ the three join you here (until now you have no POKéMON): jingle, "CHARIZARD, PIKACHU and LAPRAS joined {PLAYER}!"]*

> MOM: And say hello to everyone for me!
>
> Oh, and pack a sweater, dear. It gets chilly out on the water.

> Don't worry about the dishes. I'll manage. Go!

### TV (downstairs) ✨ *(new)*

> ✨ There's a news program on TV.
>
> "...A golden-haired man is ROARING about TARIFFS again. Experts warn prices will go up on... well, everything."
>
> ...Even POKé BALLS, apparently.

### Notice (upstairs, by the stairs) ✨ *(new; was the L/R help notice)*

> ✨ It's a poster for an AI assistant. "ASK ME ANYTHING!"
>
> Someone has scribbled underneath: "Where's MEW?"
>
> No answer yet.

### PC (upstairs) ✨ *(new; replaces the PC menu)*

> ✨ {PLAYER} booted up the PC.
>
> 2,048 unread messages. 99+ notifications. Every single app wants an update.

> ✨ In the MAILBOX, buried under the newsletters, there's one old message that never got deleted:
>
> "Smell ya later! - {RIVAL}"

> ✨ ...{PLAYER} turned off the PC.

## Arrival harbor

### GiovanniStopsYou

> ...{PLAYER}. A moment, if you would.

### Giovanni

*[already built: this is GIOVANNI's **↻ Again** line, said every time you talk to him after the battle]*

> GIOVANNI: Go on in. I'll follow... in a little while.
>
> It's been a long time since anyone held a door open for me.

### GiovanniTalk

> GIOVANNI: So. The child who brought down TEAM ROCKET. Taller now.

> An invitation came for me too. No name on it. Me, of all people.
>
> After everything I did... I wasn't sure I deserved a seat at that table.

> So I've stayed out here a while, catching up with these two. They followed me once.
>
> Now one runs a noodle stand, and the other has a daughter who wants to be a GYM LEADER.

> Before you go in, indulge an old man. One friendly battle.
>
> Not to win. Just to shake the rust off. For both of us.

> I only brought MEOWTH today. These days, it's the only partner I need.

> Hm. You haven't lost your touch.

> Hm. A little rusty, are we?

> GIOVANNI: Good. That's the feeling. You'll want it in there.

> Go on, {PLAYER}. That rival of yours has been checking the door every five minutes.

### Meowth

> MEOWTH: Meowth!
>
> It's wearing a tiny bow tie. GIOVANNI must have tied it himself.

**↻ Again:** `MEOWTH is fussing with its bow tie. It's crooked now. It looks to GIOVANNI for help.`

### GruntM

> 🆕 Hey... it's you! The kid who wrecked our hideout under the GAME CORNER! Look at you now, all grown up!
>
> Ha! No hard feelings. Best thing that ever happened to me, honestly.

> I run a noodle stand in CELADON now. My son helps out on weekends.
>
> The BOSS came by last month and ordered three bowls. Didn't say a word. Just ate.

**↻ Again:** `Come by CELADON sometime. First bowl's on the house. Second one too.`

### GruntF

> I used to steal POKéMON. Now I volunteer at the POKéMON CENTER in LAVENDER.
>
> Turns out I like making them better more than taking them.

> This is my little girl. She's been dying to meet you all week.

**↻ Again:** `My little girl here has been practising GYM LEADER poses in the mirror all week.`

### GruntDaughter

*[a little girl standing next to GruntF; !! over her when you talk to her]*

> I'm gonna be a GYM LEADER when I grow up! A WATER one, like MISTY!

> Mom says you're super famous. Can I... can I have your autograph?

*[yes/no]*

> She holds up a crumpled piece of paper.
>
> You sign it as neatly as you can.
>
> Yay! I'm never washing this hand again!

> Aww... okay! I'll ask again when I'm a GYM LEADER. Then you'll want MY autograph!

**↻ Again:** `[if you signed] Look! I'm keeping it in my pocket. The one with the zip!   [if you said no] she asks again, with the yes/no.`

### Sailor

> SAILOR: Welcome ashore, {PLAYER}! Mind your step, the gangplank's a bit short tonight.
>
> The café's right through that door. Smells like somebody's making curry!

**↻ Again:** `SAILOR: Curry's still on, {PLAYER}! The café's right through that door.`

## Café

### Oak

*[✨ walks up, like MOM: if you head for the garden door without having talked to OAK or BLAINE, OAK spots you ("!"), calls out, and hurries over]*

> ✨ PROF. OAK: {PLAYER}! Wait!

> PROF. OAK: {PLAYER}! My, my! Is that CHARIZARD? I remember a tiny CHARMANDER that chewed a hole in my lab coat!

> BLAINE and I were just arguing about the new kids. He wants to start a school for young trainers.
>
> I keep telling him: give a child a POKéMON and a map, and get out of the way. It worked for you!

> I still keep your POKéDEX on my desk. Some evenings I flip through it, just to see how far you went.

**↻ Again:** `PROF. OAK: Go on, {PLAYER}! Everyone's dying to see you. I'll save you a seat.`

### Blaine

> BLAINE: Hah! {PLAYER}! Pop quiz! Which trainer answered every one of my questions... and then melted my RAPIDASH?
>
> ...You! Correct!

> 🆕 A rematch? Hah! Not today, champ. My knees creak louder than my volcano these days.
>
> And ARCANINE here... he's an old dog now. Loyal as ever, but he'd rather nap by the fire.

> These days I spend my time teaching the young ones. Fire is easy. Patience is the hard part!
>
> OAK says just let them go explore. I say teach them the quiz first! We've been at it all evening.

*[🎁 new gift]*

> BLAINE: Final question! What does CHARIZARD deserve, after all these years?
>
> ...This! Correct!

*[receives CHARCOAL, item jingle]*

> CHARCOAL! A little fuel for that old flame. Hah!

**↻ Again:** `BLAINE: Bonus question! Where does ARCANINE nap? ...By the fire! Correct again!`

### Arcanine

> ARCANINE: Wooo...
>
> Its muzzle has gone a little grey. It thumps its tail at you slowly.

**↻ Again:** `ARCANINE is fast asleep. Its paws twitch. It's dreaming of running.`

### Chef

*[✨ walks up: he now stands out front of the counter, and comes over as soon as you walk in from the port]*

> CHEF: Welcome, welcome! You must be {PLAYER}! Somebody booked the whole café for tonight. Paid in advance, and left no name!
>
> Dinner's covered. Drinks, though... those are on you. Ask at the counter!

> The kitchen's open all night.
>
> Later we're pushing every table together into one long one for the big feast...

> ...if the power comes back on in time, that is. Half my ovens are dark.
>
> LT. SURGE swore he'd fix it. Over at the POWER PLANT, if you see him.

*[🎁 new gift]*

> Oh, and here! I baked this in the one oven that still works.

*[receives LAVA COOKIE, item jingle]*

> A LAVA COOKIE, to hold you over until dinner. On the house!

**↻ Again:** `CHEF: The feast is later, {PLAYER}! Assuming SURGE gets my ovens back.`

### Waitress

> Hi there! Something to drink? Our LEMONADE is the same recipe as the CELADON rooftop vending machines.
>
> And no, we don't serve TEA. Every guard from SAFFRON has already asked.

> Enjoy the party, {PLAYER}!

**↻ Again:** `The LEMONADE's on ice whenever you want one, {PLAYER}!`

### Guard *(new: to build)*

*[a SAFFRON gate guard standing by the drinks table; ! over him when you talk to him]*

> GUARD: You! You're the kid who gave me TEA at the SAFFRON gate!
>
> I was so thirsty that day, I thought I'd faint on duty.

> I've been chasing that taste ever since.
>
> ...They don't serve it here. I asked. Twice.

**↻ Again:** `GUARD: If you ever find TEA again... you know where I'll be.`

## Garden

### Welcome

> {RIVAL}: Well, well, well! Look who finally showed up!
>
> It's been {YEARS_AGO} years, {PLAYER}! What, did you get lost on ROUTE 1 again?

> And you still brought CHARIZARD? Figures. You never could let go of anything.
>
> Smell ya lat... no, wait. You just got here.

> ...

> ...Hey. Don't look at me like that.

> {RIVAL}: Remember Gramps's lab? Three POKé BALLS on the table, and we nearly knocked it over fighting about who'd pick first.
>
> You beat me at everything after that. Every single time.

> And then one day you just... weren't around anymore.

> ...sniff...
>
> I-it's the sea breeze! Gets in your eyes out here!

> ...
>
> Okay. Okay, I'm fine. Listen up, {PLAYER}!

> Everybody came. Gramps and BLAINE are back in the café. The GYM LEADERS are all over this garden.

> And the ELITE FOUR are in the tall tower at the far end. Word is, they've got something planned for you.

> The CHEF's cooking up a feast for later. If your POKéMON need a rest, there's a POKéMON CENTER up the path.

> Oh, and... take this. Don't make it weird.

*[✨ receives a FULL RESTORE, item jingle (instead of ¥20,000)]*

> ✨ {RIVAL}: Gramps gave me two of those before my League run. I used one in our battle for CHAMPION...
>
> I kept the other. Guess I was saving it for tonight.
>
> Now go on! Everybody's waiting for you.

### Rival

> {RIVAL}: The GYM LEADERS are all over this garden. The ELITE FOUR are in the big tower at the far end.
>
> Go on, I'll catch up!

### GardenSign

> REUNION GARDEN

### PowerPlantSign

> POWER PLANT

### CutTree

> A thin little tree is growing in the gap of the fence. Beyond it, you can hear waves.
>
> Cut it down?

> CHARIZARD sizes up the tree... and slices clean through it!

### Misty

> MISTY: Shh! STARYU almost had a fish!
>
> ...Oh! It's you! You actually came!

> You know what I remember? You marching into my GYM like you owned the place.
>
> I was so mad afterwards, I made my trainers swim extra laps for a whole week.

> Truth is, I trained harder after you left than I ever had before.
>
> So... thanks, I guess. Don't let it go to your head.

*[🎁 new gift]*

> Here. Water from CERULEAN, for that LAPRAS of yours.

*[receives MYSTIC WATER, item jingle]*

> And don't tell anyone I was being nice.

> They promised me a lake, by the way. This is a pond. A pond with ambition.

**↻ Again:** `MISTY: Still no fish. STARYU says it's the pond's fault. I agree.`

### Psyduck

> PSYDUCK: Psy...?
>
> It's holding its head. It seems to have forgotten why it walked over here.

**↻ Again:** `PSYDUCK is still standing here. It's forgotten why again.`

### Starmie

> STARMIE: Hyah!
>
> Its core flickers red, then blue. It definitely remembers you... and it doesn't seem to hold a grudge.

**↻ Again:** `STARMIE spins once, showing off. Its core glows a steady blue.`

### Staryu

> STARYU is spinning slowly in the water, catching the last of the sunlight.

**↻ Again:** `STARYU has stopped spinning. It seems to be watching the sunset too.`

### Brock

*[✨ walks up: when you first step onto the stairs into his hollow, he comes to the foot of the stairs, then goes back to ONIX]*

> BROCK: Hey! Watch your step on the way down, those stairs are older than both of us.
>
> It's good to see you, {PLAYER}. Really good.

> You know, you're the trainer who made ONIX lose its cool. A little CHARMANDER against a mountain of rock... I still don't know how you pulled it off.

> I'm studying to be a POKéMON doctor now.
>
> Funny. Healing turned out to be harder than any GYM battle ever was.

*[🎁 new gift]*

> Here, take this. Doctor's orders.

*[receives MAX REVIVE, item jingle]*

> Keep it for when it really counts. I hope you never need it.

> ONIX found this hollow the moment we arrived. It says it smells like PEWTER.

**↻ Again:** `BROCK: Careful on those stairs. I'm almost a doctor, not quite one yet.`

### Onix

> ONIX: Gorooo...
>
> It lowers its enormous head so you can pat it. The rocks are warm from the sun.

**↻ Again:** `ONIX has curled up in the hollow, rumbling softly like a far-off rockslide.`

### Geodude

> GEODUDE is doing push-ups.
>
> It has been doing push-ups since you arrived. It shows no sign of stopping.

**↻ Again:** `GEODUDE is still doing push-ups. You're starting to feel lazy.`

### Erika

> ERIKA: ...Mm? Oh my. I must have dozed off among the flowers again.
>
> Forgive me. The fountains are so soothing.

> {PLAYER}... Goodness, you've grown so tall. For a moment I took you for one of my trees.

> Is that CHARIZARD? It once singed my VILEPLUME's petals, you know.
>
> They grew back twice as lovely. Please tell it I forgave it long ago.

> Oh, and do look at the young couples over there. They quarrelled for ages, I hear.
>
> They made up right here, beside my VILEPLUME. I like to think the flowers helped.

**↻ Again:** `ERIKA: ...Zzz... Mm... VILEPLUME, a little less pollen, please...`

### Vileplume

> VILEPLUME: Plooo...
>
> A sweet, drowsy scent drifts from its petals. Your eyelids feel heavy...

**↻ Again:** `VILEPLUME sways. You decide not to stand downwind this time.`

### Oddish

> ODDISH is trying very hard to plant itself in the flower bed.
>
> ERIKA doesn't seem to mind one bit.

**↻ Again:** `ODDISH has made progress. Its feet are now slightly underground.`

### Tangela

> TANGELA wanders through the flowers, collecting petals in its vines.
>
> It offers you one, very seriously.

**↻ Again:** `TANGELA offers you another petal. You now have a small bouquet.`

### MrMime

> MR. MIME: Bari! Bari!
>
> It's pressing both hands against an invisible wall... right between you and the door.

**↻ Again:** `MR. MIME is leaning on its invisible wall now, completely at ease.`

### Lex

> LEX: Oh, hey. You're the one who beat NYA and me back in the canyon.
>
> Nobody had managed that in years. We talked about it for a month.

> JED and I haven't spoken since a double battle on ROUTE 16 went... badly. Very badly.
>
> Tonight NYA marched us over here and made us shake hands.

> Turns out we both cut out the same POKéMON magazine column. The same one! Since we were kids.
>
> Feels kind of silly now.

**↻ Again:** `LEX: Fishing next week. With JED. If you'd told me that years ago...`

### Nya

> NYA: Don't mind the boys. They sulked for ages over whose POKéMON were rarer.

> Our MILTANK came all the way from JOHTO. LEA's NINETALES has the softest tails in KANTO.
>
> We've agreed it's a tie. Officially.

*[🎁 new gift]*

> Oh! Take some of this before the boys drink it all.
>
> Fresh from our MILTANK. Best in two regions!

*[receives MOOMOO MILK ×3, item jingle]*

**↻ Again:** `NYA: A tie. Officially. Don't let either of them tell you otherwise.`

### Jed

> JED: Ha... you probably remember us from CYCLING ROAD's end. LEA and I used to battle everyone in sight.

> LEX and I fell out over one battle. One! His TAUROS said my RAPIDASH false-started.
>
> RAPIDASH doesn't false-start. It's just fast.

> ...Anyway. He's alright. We're going fishing next week, apparently.

**↻ Again:** `JED: For the record, RAPIDASH did NOT false-start.`

### Lea

> LEA: JED practised his apology on me all week. He was so nervous he called NINETALES "Lex" twice.

> Funny, isn't it? All those battles, and what we really wanted was someone who loved their POKéMON as much as we loved ours.
>
> They were right across the field the whole time.

**↻ Again:** `LEA: Look at them. Like they never stopped being friends.`

### Tauros

> TAUROS: Mooooh!
>
> It snorts at RAPIDASH across the way... then wags its tails. Old rivals, new friends.

**↻ Again:** `TAUROS and RAPIDASH are touching noses. Nobody is false-starting.`

### Miltank

> MILTANK: Moooo!
>
> It looks very proud of itself. You've never seen one of these in KANTO before.

**↻ Again:** `MILTANK moos at you again, even prouder than before.`

### Rapidash

> RAPIDASH: Hihiiin!
>
> Its mane is burning very low and very carefully. It doesn't want to singe ERIKA's garden.

**↻ Again:** `RAPIDASH's mane flickers a little brighter as you come close.`

### Ninetales

> NINETALES gazes at you with calm red eyes.
>
> Its nine tails sway together like they're keeping time to music only it can hear.

**↻ Again:** `NINETALES has wrapped its tails around itself like a blanket.`

### MegaPunch

> Hah! A visitor! Wait... I know you! The trainer who walked past us outside MT. MOON!
>
> I wanted to teach you MEGA PUNCH. HE wanted to teach you MEGA KICK.

> We argued about it for years. Punch or kick. Kick or punch.
>
> Then one day HITMONCHAN and HITMONLEE started sparring together... and they were stronger as a pair than either one alone.

> So here we are. Partners! A fist and a foot. We're thinking of opening a DOJO.

**↻ Again:** `🆕 A fist and a foot! Remember that, friend. It'll be on the DOJO sign.`

### MegaKick

> We used to stand three steps apart and shout at each other all day.
>
> Now we stand three steps apart and shout ENCOURAGEMENT at each other. Huge improvement!

> If you'd come to me first back then, you'd know: a great kick starts in the heart.
>
> And so does a great punch. He finally convinced me of that.

**↻ Again:** `Kick and punch. Punch and kick. ...We still argue about the order on the sign.`

### Hitmonchan

> HITMONCHAN throws a quick one-two at the air, then bows to you politely.

**↻ Again:** `HITMONCHAN is cooling down. It bows to you again, just as politely.`

### Hitmonlee

> HITMONLEE stretches one leg impossibly high.
>
> It's definitely showing off for HITMONCHAN.

**↻ Again:** `HITMONLEE is now stretching the OTHER leg. Even higher.`

### FishingGuru

> Shhh! Fish can hear footsteps, you know.
>
> ...Hm? Wait a moment. You're the youngster I gave that OLD ROD to, back in VERMILION!

> Let me guess what you caught first. A MAGIKARP.
>
> Everyone's first catch is a MAGIKARP. And everyone remembers it. That's the beauty of fishing!

> My little brother's down on the beach. He used to out-fish all of us.
>
> Hasn't cast a line since his first kid was born. Says the fish can wait.

**↻ Again:** `MAGIKARP. Always MAGIKARP. I wouldn't change a thing.`

### FishingBrother

> Oh, hello! You look familiar... FUCHSIA! I gave you a GOOD ROD once, didn't I?

> See those two splashing out there? Mine. I hung up my rod the day they were born.
>
> These days the only thing I reel in is a kid who swam out too far.

> My big brother's up on the old landing past the POKéMON CENTER, still at it.
>
> Tell him I said his MAGIKARP story gets bigger every year.

**↻ Again:** `NOT TOO FAR, you two! ...Sorry. Habit.`

### TuberBoy

> Look! Look! I can float without kicking!

> Dad says he used to be the best fisherman in KANTO.
>
> Now he just yells "NOT TOO FAR!" all day.

**↻ Again:** `Watch! I'm floating! ...Is Dad watching?`

### TuberGirl

> I'm gonna catch a GYARADOS when I grow up!

> Uncle says first you have to catch a hundred MAGIKARP.
>
> I've caught... zero. But I'm really close!

**↻ Again:** `That's ONE! ...Oh. It's seaweed.`

### BikeShop

> Well, if it isn't my most famous customer!
>
> You walked into my shop with a BIKE VOUCHER and rode out on my finest model. Didn't pay a single coin!

> Everyone said a million for a BICYCLE was madness.
>
> They were right, of course. But nobody ever forgot my shop, did they?

*[🎁 new gift]*

> 🆕 But tonight... no vouchers, and no prices.
>
> This is the best BICYCLE I've ever built. I finished it this morning, just for you.

*[receives BICYCLE, item jingle]*

> 🆕 Ride it like it's {PLAY_YEAR} again!

**↻ Again:** `🆕 Every BICYCLE has a price. Tonight, yours was a smile. Worth a million.`

### Biker

*[✨ rides up: he's parked on the beach and rides over (bike bell) the first time you reach it]*

> Yo. Relax, I ain't here to rumble.
>
> Back in the day, my gang ruled CYCLING ROAD. Revving engines, cutting off every kid on a BICYCLE... you included, probably.

**↻ Again:** `These days I ride a BICYCLE. Don't laugh. ...Okay, you can laugh a little.`

## Pokémon Center

### Nurse *(🆕 first visit only; after that, the usual healing)*

> 🆕 Oh! {PLAYER}! I'd know that CHARIZARD anywhere. You must have visited every one of our CENTERS back then.
>
> Welcome back. Your POKéMON are in good hands tonight, just like always.

*[then the usual healing]*

### PC

> The PC's screen is dark.
>
> A sticky note on it says: "No work tonight. Go enjoy the party!"

### Escalator

> The escalator isn't moving.
>
> A sign hangs from a rope: "2nd FLOOR CLOSED for maintenance. Sorry for the trouble!"

### Chansey

> CHANSEY: Chaaan-sey!
>
> It's carrying an EGG very carefully, as if it's the most important job in the world.

**↻ Again:** `CHANSEY still hasn't taken a single step. The EGG is a very important job.`

## Mart

### Clerk *(🆕 first visit only; after that, the usual shop)*

> 🆕 Oh! You're the one who carried PROF. OAK's PARCEL out of our VIRIDIAN store!
>
> I still think of you every time a package comes in.

> ✨ ...Speaking of packages, everything costs more to ship these days. Tariffs, they say.
>
> So the prices went up. Again. Don't look at me, I just work here!

*[✨ Mart prices are up about 7%: POKé BALL ¥215, POTION ¥320, SUPER POTION ¥750, HYPER POTION ¥1,290, FULL HEAL ¥640, REVIVE ¥1,620]*

*[then the usual shop]*

## Sabrina's room

### Sabrina

*[✨ walks up: the first time you come in, she walks down to meet you at the door]*

> SABRINA: ...You came through that door at exactly the moment I saw you would. Three days ago.

> When you came to my GYM, I sensed you long before you reached me.
>
> I did not sense that I would lose. It was the first thing in years I hadn't seen coming. I've treasured it ever since.

> The KARATE MASTER from the DOJO next door sends his regards. We take tea together on Sundays now.
>
> He still can't bend a spoon. I still can't break a board. We've stopped keeping score.

> Don't ask me how tonight ends. I already know... and I won't spoil it for you.

**↻ Again:** `SABRINA: You were going to ask me again. ...The answer is still no.`

### Alakazam

> ALAKAZAM: Kazam.
>
> It bends one of its spoons into a little heart... then quickly straightens it again, as if nothing happened.

**↻ Again:** `ALAKAZAM is pretending its spoons are perfectly straight. They aren't.`

## Koga's cave

### Dark

> It's pitch-black in here. You can't see a thing...
>
> But PIKACHU could light up the cave with FLASH. Use FLASH?

> PIKACHU used FLASH!

> You decide to feel your way along the walls in the dark.

### Koga

> KOGA: Fwahahaha! You found me, even here. Your instincts are as sharp as ever.

> Do you remember my GYM in FUCHSIA? The invisible walls?
>
> You walked into them so many times that my students kept a tally on the wall. I still have it.

> My daughter runs the GYM now. She added even more walls. I could not be prouder.

> A ninja never rests... but tonight, I will make an exception. Go. Enjoy yourself.

> 🆕 ...But first, a little game. Let us see if you can find me twice.

*[🆕 a puff of smoke: KOGA vanishes and reappears in the far corner of the cave]*

**↻ Again:** `KOGA: You found me twice. I need a better hiding spot.`

### Weezing

> WEEZING: Weez-ing!
>
> It puffs out a little cloud of... mint? Someone has been feeding it herbs for the party.

**↻ Again:** `WEEZING puffs out another minty cloud. The cave smells like toothpaste.`

### Muk

> MUK: Muuuk!
>
> It oozes over to say hello, leaves a small puddle, then politely oozes back over it to clean up.

**↻ Again:** `MUK waves a gooey arm. The floor stays spotless.`

## Lt. Surge's Power Plant

### Surge

> 🆕 LT. SURGE: Hey, soldier! Perfect timing! The whole island blacked out an hour before the party!

> We borrowed this network machine from CELIO over on ONE ISLAND to link up the generators.
>
> Problem is, the manual's written in pure nerd.

> Ha! Remember my GYM in VERMILION? You dug through every trash can in the place looking for my switches.
>
> Today I'm the one digging through junk. Elbow-deep in wires!

*[🎁 new gift]*

> Funny thing, though. Look what turned up in the junk.
>
> This LIGHT BALL belongs with your PIKACHU. Better hands than mine!

*[receives LIGHT BALL, item jingle]*

> Treat it right. It's been waiting for a PIKACHU worth the shine.

> Don't you worry. The café will serve dinner on time tonight. That's an order!

**↻ Again:** `🆕 LT. SURGE: Still elbow-deep, soldier! Dinner on time. That's an order!`

### Aide

> I'm one of PROF. OAK's aides. He sent me to help LT. SURGE with the machine.
>
> We've rerouted the power three times. Every time RAICHU sneezes, the lights go out again.

> Oh! Wait, I remember you! ROUTE 2! I gave you HM05 FLASH once you'd caught ten POKéMON.
>
> I hope it came in handy in a certain dark cave tonight!

**↻ Again:** `That's four reroutes now. RAICHU, please. No more sneezing.`

### Raichu

> RAICHU: Rai-chu!
>
> Sparks crackle from its cheeks. It looks very pleased with itself. You suspect it caused the blackout.

**↻ Again:** `RAICHU looks away and whistles. It definitely caused the blackout.`

### Voltorb

> VOLTORB rolls past you.
>
> It looks exactly like a POKé BALL. Some memories never fade. You do NOT pick it up.

**↻ Again:** `VOLTORB rolls past again. Your hand twitches. You do NOT pick it up.`

### Machine

> A huge network machine, humming loudly.
>
> The screen flickers: "POWER 12%... REROUTING..."

## Elite Four tower

### Lorelei

> LORELEI: {PLAYER}... You walked into my ice chamber in short sleeves, I remember. I lent you my scarf afterwards.
>
> You never gave it back. I'm only a little bitter.

> I retired to FOUR ISLAND, you know. This garden reminded me of home the moment I saw it.

**↻ Again:** `LORELEI: The scarf can wait. Go say hello to the others.`

### Bruno

> BRUNO: Hoo hah! {PLAYER}! I spent a month training on a mountain in JOHTO. Berries for every meal!
>
> ...Never again.

> 🆕 Every morning, I tell MACHOKE: one day, that trainer will come back. Today is that day!

**↻ Again:** `BRUNO: Greet the others, {PLAYER}! Then... you'll see. Hoo hah!`

### Agatha

> AGATHA: Oh ho! The brat is back! Still afraid of my GENGAR? ...Hmph. You never were. That was the annoying part.

> Oak still talks about you, you know. The old fool. Hmph. ...🆕 It's good to see you. Look how you've grown.

**↻ Again:** `AGATHA: Go on, go on. The others are waiting too. Hmph.`

### Lance

> LANCE: {PLAYER}. Only one trainer ever beat my dragons while still a child.

> CHARIZARD, PIKACHU, LAPRAS... You never traded them away for something flashier. That's real strength.

**↻ Again:** `LANCE: Speak with the others first. We have something to ask you.`

### AfterGreeting

*[said once, right after each member's first greeting; after that they say their own **↻ Again** line]*

> Say hello to the others too. We have something to ask you.

### Proposal

> Now that you've seen all four of us... We talked it over before you came.

> The last time we battled, you were a child, and so, in a way, were we.
>
> One more rematch, {PLAYER}. One of us at a time. A farewell to our childhood.

> Then gather round, everyone! It's time!

### BattleScene

> PROF. OAK: Ho ho! Everyone's here! Just like the old days!

> MISTY: Go get 'em, {PLAYER}!

> 🆕 LT. SURGE: Give 'em a jolt, soldier!

> 🆕 ERIKA: ...Mm? Oh! It's starting! Do your best, {PLAYER}!

> {RIVAL}: Hey! Hold it! You think I'd let you have all the fun?

> {RIVAL}: Four against one? That's not a farewell, that's an ambush!
>
> I'm in. Four against two. Now it's fair.

> For once, we're on the same side. Weird, huh?

> BLASTOISE! SNORLAX! ALAKAZAM! You're with {PLAYER} on this one. Fight side by side with their team.
>
> We've been on opposite sides since Gramps's lab. Let's see what we can do together.

> BLASTOISE, SNORLAX and ALAKAZAM joined {PLAYER}'s team!

*[🆕 **One run:** the four battles are back to back, and your team is NOT healed in between, so the gifts in your bag matter. The run ends at your first loss: whoever beat you closes it, and the story goes straight to the ending. Nobody you didn't reach gets a battle.]*

*[battle 1: LORELEI (2 POKéMON, double battle)]*

> 🆕 LORELEI: The two of you, side by side. Good. I'll go first.

*[win] 🆕 "You two still melt my ice."  [lose] 🆕 "The ice holds... this time."*

*[if you won]*

> ✨ LORELEI: Ice melts. That's what I tell my students on FOUR ISLAND.
>
> I never told them it was two kids from PALLET TOWN who taught me that.

> {RIVAL}: One down!
>
> 🆕 No breaks and no healing, {PLAYER}. Got anything in that bag? Now's the time.

*[✨ **get-ready menu**, after every win: TEAM (the POKéMON screen: reorder, summaries, held items) / BAG (use or give items) / READY!. TEAM and BAG come back to the menu; READY! brings on the next member. You never leave your spot]*

> ✨ {RIVAL} [READY!]: Let's go!

*[battle 2: BRUNO]*

> 🆕 BRUNO: Hoo hah! {PLAYER}! {RIVAL}! Show me those muscles!

*[win] 🆕 "You two hit like a MACHAMP!"  [lose] 🆕 "Hoo hah! Still got it!"*

*[if you won]*

> ✨ BRUNO: Hoo hah... my fists are shaking.
>
> Not from losing. From how glad I am that you two came back. Together!

> {RIVAL}: Halfway there!
>
> ✨ Man, BRUNO hits like a truck. Patch up whoever needs it... and think about who goes out first.

*[✨ get-ready menu]*

> ✨ {RIVAL} [READY!]: Okay. Let's do this.

*[battle 3: AGATHA]*

> 🆕 AGATHA: Oh ho! Two brats for the price of one! Let's see if you're still not afraid of my ghosts.

*[win] 🆕 "Hmph! Well done, you two."  [lose] "Hee hee! The old lady still has it!"*

*[if you won]*

> ✨ AGATHA: Hmph. Oak and I used to argue about which of you two was the bigger brat.
>
> ...We never settled it. Look at you both now.

> {RIVAL}: One more. Don't you dare quit on me now.
>
> ✨ LANCE won't hold back. If you've been saving anything, this is it.

*[✨ get-ready menu]*

> ✨ {RIVAL} [READY!]: ...Together. Like we should've been all along.

*[battle 4: LANCE]*

> 🆕 LANCE: {PLAYER}. {RIVAL}. Together, one last time.

*[win] 🆕 "So this is what you two became."  [lose] 🆕 "No shame in it. Not tonight."*

### Ending

*[🆕 the music fades into the quiet PALLET TOWN theme, however the run ended]*

*[if you won all four]*

> ✨ LORELEI: Keep the scarf, by the way. Share it. You two always did share everything... except first place.

> ✨ BRUNO: Hoo hah! Next time, I'm bringing berries for everyone!

> ✨ AGATHA: Hmph. Tell Oak his two favourite brats haven't changed one bit.

> 🆕 LANCE: That was a farewell worthy of you both.
>
> ✨ Don't wait so long next time. The dragons missed you both.

> {RIVAL}: ...We did it. Together, for once.

*[🆕 if LORELEI beat you]*

> LORELEI: Frozen at the very first step.
>
> ✨ ...At least this time neither of you needed my scarf.

> ✨ BRUNO: Hoo hah! I didn't even get to flex!

> ✨ LANCE: It was never about winning, you two. It was about seeing you here again. Together.

> {RIVAL}: ...We lost. Right at the start.
>
> ...Huh. Why can't I stop laughing?

*[🆕 if BRUNO beat you]*

> BRUNO: Hoo hah! A month of berries, every meal... and it was worth it!

> ✨ LORELEI: You two still beat me, you know. My ice will be melting for weeks.

> ✨ LANCE: It was never about winning, you two. It was about seeing you here again. Together.

> {RIVAL}: One down, and then... yeah. Who cares. Together, for once.

*[🆕 if AGATHA beat you]*

> AGATHA: Hee hee. Tell Oak the old lady won this time. He'll never believe it.

> ✨ BRUNO: Two of us down, though! That's more than most trainers ever manage!

> ✨ LANCE: It was never about winning, you two. It was about seeing you here again. Together.

> {RIVAL}: Two out of four! Not bad for a couple of old-timers. Together, for once.

*[🆕 if LANCE beat you]*

> 🆕 LANCE: You lost, and you're both smiling. Children couldn't do that.
>
> Farewell, you two. That was worthy of you.

> ✨ AGATHA: Hmph. Three out of four. Oak will brag about it for a month.

> {RIVAL}: So close! One more and... ah, who cares. Together, for once.

*[then, in every case]*

> {RIVAL}: BLASTOISE, SNORLAX, ALAKAZAM... you were amazing out there. ...You too, {PLAYER}. Don't let it go to your head.

> You know what, {PLAYER}? I'm glad it's you. It was always going to be you.

> ...sniff... Hey. Promise me something.
>
> Don't be a stranger this time, okay?

> PROF. OAK: Splendid! Simply splendid! Now then, everyone... SURGE, how are those lights?

> LT. SURGE: Power's back at one hundred percent, sir!

> PROF. OAK: Then dinner is served! Everyone, to the café!

*[everyone turns toward the exit; OAK turns back to you]*

> PROF. OAK: Not you, {PLAYER}.
>
> Someone has been waiting behind that door all evening. They asked to see you once the battles were over.

*[fade to black; everyone else has left the room; fade back in with only you there]*

### ExitBlocked *(new: to build)*

*[stepping onto the exit after the ending]*

> Someone is still waiting behind the door at the back.
>
> Dinner can wait a little longer.

### BackDoorLocked

> 🆕 The door is closed.
>
> A voice comes from the other side: "Not yet, {PLAYER}! The ELITE FOUR are preparing a surprise for you. Go talk to them first!"

### Lapras

> LAPRAS: Laaa...
>
> Its gentle song fills the room.

**↻ Again:** `LAPRAS hums the same song again. It sounds a little like home.`

### Machoke

> MACHOKE: Macho!
>
> It flexes. Then flexes again, in case you missed it.

**↻ Again:** `MACHOKE is still flexing. It has not stopped. It will not stop.`

### Gengar

> GENGAR: Gengar!
>
> It grins. You feel a chill... and a little nostalgic.

**↻ Again:** `GENGAR is suddenly right behind you. ...It grins again.`

### Dragonite

> DRAGONITE: Grooo!
>
> It bows its big head politely.

**↻ Again:** `DRAGONITE bows again, a little lower this time.`

## Creator's room

### Creator

> ???: ...Hi, {PLAYER}. You made it all the way here.

> ???: I suppose I should introduce myself.
>
> I'm a solo developer who made all of this. The letter, the ferry, the café, the garden... this whole night. (Even this game, if you know what I mean.)

> CREATOR: A while ago, I realized how much I missed this world, and y'all.
>
> The tall grass. The GYM music. Trading with friends after school. The feeling that all of KANTO was out there, waiting.

> So I did something a little silly.
>
> I rebuilt it, piece by piece, and put a little bit of myself inside it. Then I sent out the invitations.

> Everyone you met tonight... and you.
>
> You're the friends I wanted at this table.

> Thank you for coming back, {PLAYER}. For battling one more time. For remembering.

> The power's back on, and dinner is getting cold.
>
> Let's not keep everyone waiting.

> In {PLAY_YEAR}, a {AGE_THEN}-year-old named {PLAYER} set off with a dream.

> Now you're {AGE_NOW}.
>
> School. Work. Friends. Life.
>
> But some things stayed exactly where you left them.

> Welcome home, {PLAYER}.
>
> Thank you for playing, one more time.

## Dinner (finale) ✨ *(new: to build)*

*[after the creator's last lines the screen fades to black. Music: the S.S. ANNE party theme for the feast; at "CHEERS!" it gives way to the FireRed ending theme, which plays on to THE END]*

*[fade in on the café: every table pushed together into one long feast table, covered in dishes and drinks. Everyone from tonight sits around it and every seat is taken: ✨ {PLAYER} and {RIVAL} side by side at the left end, PROF. OAK and the CREATOR at the right end, the GYM LEADERS and the ELITE FOUR along the top (facing us), and GIOVANNI, the old Rocket grunt and her daughter, the guard, the couples, the fishing brothers and the BIKE SHOP owner along the bottom. The CHEF and the noodle guy walk around the table serving. The POKéMON wander around the room, not on chairs. The camera slowly pans along the table.]*

> ✨ CHEF: Make room, make room! Hot plates coming through!

> ✨ GRUNT (noodle guy): Noodles, CELADON style! The BOSS's bowl gets extra.

*[✨ the toasts. MISTY, LT. SURGE and ERIKA already cheered before the battles, so others raise their glasses here. Each toast is about memory, friendship or love, in the speaker's own voice]*

*[PROF. OAK stands up and taps his glass]*

> ✨ PROF. OAK: Everyone! A toast!
>
> To old friends... and to every journey that led back to this table.

> ✨ BROCK: To the CHEF! Feeding a whole island with half the ovens dark...
>
> Take it from a guy who cooked for nine little brothers and sisters. That's love, right there.

> ✨ GIOVANNI: ...To second chances.
>
> And to my old friend with the noodles. You were always better at this than at anything I ever asked of you.

> ✨ NOODLE GUY: B-BOSS...! ...Extra noodles. For everyone.

> ✨ AGATHA: Hee hee. To memory. The only thing in this world that never gets old.
>
> ...Unlike the rest of us.

> ✨ SABRINA: To the future. I've seen it.
>
> ...I won't spoil it. But all of you are in it.

*[everyone turns to the head of the table, where {PLAYER} and {RIVAL} sit side by side]*

> ✨ {RIVAL}: ...You say it, {PLAYER}. You were always better at this part.

> ✨ {PLAYER}: To all of you. Thank you for waiting for us.
>
> We missed this. We missed you.

> ✨ {RIVAL}: ...Yeah. What they said.
>
> We love you guys. ...Don't make it weird.

> ✨ EVERYONE: CHEERS!

*[glasses clink; the POKéMON hop and cry together]*

> 🟡 PROF. OAK: Wait, wait! Everyone squeeze in! One photo, for old times' sake!

*[🟡 the group photo: a camera click, a white flash, the FireRed photo jingle; everyone holds still for a moment]*

*[slow fade to black]*

*[🟡 credits on black, each line fading in on its own, no button needed:]*

> 🟡 Starring {PLAYER}
>
> 🟡 and {RIVAL}
>
> 🟡 with everyone who came tonight
>
> 🟡 Made with love, for the friends I wanted at this table.

*[✨ THE END: the words "THE END" fade in on black over the last bars of the music, hold, then fade out. The game goes back to the title screen, so it loops.]*


## Fame Checker (reunion book) 🟡 *(new)*

*[MOM hands it over at home. Each person's page unlocks the first time you talk to them tonight (GIOVANNI's after his battle). A page shows a note "From: (them) To: {PLAYER}" with one of their lines from tonight, plus one entry: where they were tonight. Daisy, Bill and Mr. Fuji aren't at the party, so they never appear.]*

| Person | Their note (a line they say tonight) | Where they were tonight |
|---|---|---|
| PROF. OAK | "Give a child a POKéMON and a map, and get out of the way. It worked for you!" | The café, arguing with BLAINE about the new kids. |
| BROCK | "Healing turned out to be harder than any GYM battle ever was." | The rocky hollow in the garden, with ONIX. |
| MISTY | "Truth is, I trained harder after you left than I ever had before." | Fishing at the garden pond. The fish were winning. |
| LT. SURGE | "Today I'm the one digging through junk. Elbow-deep in wires!" | The POWER PLANT, getting the lights back on. |
| ERIKA | "They grew back twice as lovely. Please tell it I forgave it long ago." | Asleep among the flowers by the fountain. |
| KOGA | "My daughter runs the GYM now. She added even more walls." | Hiding in a dark cave. Found, twice. |
| SABRINA | "I did not sense that I would lose. I've treasured it ever since." | Her quiet house. She knew you were coming. |
| BLAINE | "Fire is easy. Patience is the hard part!" | The café, quizzing anyone who'd listen. |
| LORELEI | "Ice melts. I never told them it was two kids from PALLET TOWN who taught me that." | The tower. Still waiting for her scarf. |
| BRUNO | "One day, that trainer will come back. Today is that day!" | The tower, flexing with MACHOKE. |
| AGATHA | "It's good to see you. Look how you've grown." | The tower, pretending not to be happy. |
| LANCE | "You never traded them away for something flashier. That's real strength." | The tower, with DRAGONITE. |
| GIOVANNI | "It's been a long time since anyone held a door open for me." | The harbor, with his old friends and MEOWTH. |

## Build notes

Done (built 2026-11-17): the café GUARD, the grunt's daughter at the harbor, no CHEF healing, the ELITE FOUR one at a time
(2 POKéMON each, double battles, no yes/no), the ending where everyone leaves for dinner and the exit is blocked.

Still to do:
- Later (dinner scene): PROF. OAK's toast, saved from the ELITE FOUR ending:
  "PROF. OAK: Everyone! A toast! / To {PLAYER}, the kid who left PALLET TOWN with a map and a dream... and came home tonight! / And to CHARIZARD, PIKACHU and LAPRAS, who never stopped believing in you!"
