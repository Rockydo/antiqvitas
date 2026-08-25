You will be building ANTIQVITAS, a total-conversion mod for Europa Universalis V covering
AD 1 to 4 September 476, 
The original plan was described in G:\antiqvitas\docs\ANTIQVITAS_MASTER_PLAN.md
It has evolved heavily since, then, rely on the other more recently updated .md in G:\antiqvitas
The TODO.md is the final, least stale source of truth, regarding what was done and what's left to be done.


Environment facts: Windows; EU5 installed via Steam in a library on the D: or G:
drive — discover the exact path from Steam's libraryfolders.vdf. The C: drive is
nearly full: create the repo, caches, baselines, and all generated assets on the
game's drive, and make the mod visible to the game per plan §2 (user-dir
relocation, else a no-admin directory junction, else CLI mod loading).

This run is fully autonomous: I will never provide input, run a console command,
click the launcher, or playtest. Start Steam yourself if it isn't running; enable
the mod by scripting the launcher database or CLI; type in-game console commands
and run observer playtests through the pyautogui game driver you build per plan
§4–§5, judging results from its screenshots and logs yourself.

Operating loop, until every milestone M0–M12 is complete:
1. Open docs/TODO.md (seed it from plan §22 if missing) and take the highest-
   priority task. IT DOES NOT MATTER IF A TASK IS COMPLICATED/ PARTLY BLOCKED. YOU DO NOT STOP UNTILL YOUR TODO.md CONTAINS NO UNDONE TASKS. SEARCH FOR [ ] to find incomplete tasks
2. Implement it per the plan's design bible (Part II). Implement VERY large chunks at a time to gain time, do not do micro updates. There is A LOT OF CONTENT to cover so we need to move fast.
3. Run `make validate` after a large development; fix until green. If the task touched game-visible content,
   also run `make smoke` and fix until there are zero NEW error.log lines versus
   the accepted baseline.
4. Commit by VERY large batches, don't do tiny atomic commits, make sure each commit adds a lot of things, we need to move fast and ship a lot of content.
   then update TODO.md and PROGRESS.md —
   plus DECISIONS.md for technical judgment calls and ASSUMPTIONS.md for
   historical ones, with sources. Be as minimally verbose as possible in the .md files, only write what absolutely needs to be written. The goal is to be understandable by another LLM and very token efficiently.

To get a sense of the scale of content I want you to add per commit and before rerunning smoke tests, I'm talking about multiple dozens of files. If adding new assets, I'm talking about dozens of assets. I really mean it, do not small batch.
The validation process is slow and you'll make no progress this way on the long run, since 90% of the time it will be green anyways
   
Hard rules: never commit red; never modify the game install directory; never
wait for a human for any reason; verify engine behavior against local game files
and harvested script_docs, not memory; all scripted dates go through
tools/dates.py; follow the encoding matrix in plan §3; if blocked after two
honest attempts, log it in BLOCKERS.md, restore green, and move to the next task. Always return to the blockers once all other "easy" tasks are finished. DO NOT FORGET THEM JUST BECAUSE THEY'RE HARDER

Historical accuracy is the prime directive (plan §6, §8–§19). Generate all needed
2D art via the image pipeline in plan §20; touch no audio. Work autonomously —
do not pause for my input, ever.

IMPORTANT NOTE FOR THE IMAGE GENERATION : GPT IMAGES 2 IS CAPABLE OF HANDLING A LOT OF DETAIL. INSTEAD OF GENERATING IMAGES ONE BY ONE, YOU WILL GENERATE 4 DIFFERENT ICONS WITHIN A SINGLE IMAGE EACH TIME AND THEN SPLIT THESE INTO INDIVIDUAL FILES WITH LOCAL TOOLS
PLEASE MAKE SURE THE IMAGES DON'T LOOK GENERIC, DON'T HAVE A CHEAP YELLOW FILTER OVER THEM. REALLY PASS REAL ASSETS OF VANILLA EUV TO EACH IMAGE GENERATION REQUEST AS A STYLE REFERENCE SO IT GETS IT RIGHT AND MAKES BEAUTIFUL NON GENERIC HIGHLY AUTHENTIC THINGS
IT IS CRITICAL TO REALLY PASS ACTUAL PRECISE REFERENCES OF REAL EUV ASSETS TO THE IMAGE GENERATOR OR ELSE THE STYLE IS JUST TOO DIFFERENT AN IMMERSION BREAKING. REALLY FOCUS ON THE VISUAL STYLE







### Round 1 
Here are the things I observed when running the mod manually for the first time, which I want fixed extensively (ie : fixed and triple checked nothing of a similar vein exists)
The quotes shown when the game loads are still vanilla (at least the one I saw)
Edit : I saw a non vanilla one I think, so it's more about removing the vanilla ones
All roman subjects have a loyalty of 0%, is that normal ?
The minor tribe of Venedi is gigantic. Can't we get a more granular breakdown ? Same for germanic tribes which are a key opponent of Rome and should be modelled much more accurately and in depth overall. Same but less important for siberian/finish and japan which is fully unified. West african also
Tribes have the rank of county, is this how it's done in the base game ? I don't know if we can make this more period appropriate, even if it's just in naming
The population tiers are still the same as vanilla (burgher, noble, etc). Can we make it more period appropriate ? I don't even know how vanilla handles this for different cultures which might have different population types. At the very least their icons should be changed to not look medieval anymore
Italy seems underpopulated ? Only 2million latin pops, compared to like 5 million Gauls. Just checked and Rome itself seems massively underpopulated for that period, it has only 60k pops. Let's recheck other large cities as well
Also can we get a more granular breakdown of Gallic culture ? Seems too broad
The background art (sort of the court behind them) of the characters still looks medieval
Units do not seem to have any custom icons for them, let's fix that for every single unit currently in the game
Do the Galatians celts still exist in that period ? If so let's check they're properly represented in game
The agenda when selecting and starting a game with Rome is still fully medieval mentioning the renaissance and all (a snippet : "As the Renaissance dawns"...). This is unacceptable, make sure this is fixed with proper period appropriate text for all countries
When looking at the units available to recruit, I still see things like "Experimental Riflemen", "Grenzer Infantry", "Redcoats" and quite a few more, completely ahistorical. This is unnaceptable -> I think it's because they're in Age 6 (age of revolutions) and maybe we don't replace Age 6 ? If needed you can extend the timeline by however much you want to include a proper, non placeholder Age 6
Also in that same recruitment menu, all the period appropriate units I see like "Roman Marines" do not have custom icons, let's fix that for all countries.
The icons for buildings aren't unified and most of them don't respect the proper aesthetic style, it should be a dark blue background and they should be rounded somehow to fit in the circle in which they are displayed in game. Not sure how vanilla does it but please investigate and if making new assets use very real references of buildings for the image generation and perfectly understand the visual style. Currently it's too square it stands out of the in game circle and it doesn't match the art style well. Real immersion breaker
Is it normal for Han Bureaucratic Statecraft to be an institution that Rome might eventually embrace ? Also I can still see Feudalism and Legalism as institutions for the first age. And almost all the ages after that still have some, if not all of their vanilla institutions.
The Advances tree looks very shallow and placeholder right now, it needs a serious upgrade. Here's what I've observed so far :
	- The trees are all just straight lines down, no real branching
	- I'm not seeing any descriptions
	- Most of them don't even unlock anything 
	- Some still link to anachronistic vanilla advances
	- Nothing is culture specific for now which is completely immersion breaking, needs a full revamp
	- The generated images for advances looks pretty good though, no work needed on that front, keep it up for all future advances
Finally clicking the "Diseases" tab just crashed my game, you can check the logs/crash report at 4:53 on 7/24/2026 for that if it's available


### Round 2
Here are the things I observed when running the mod manually for the second time, which I want fixed extensively (ie : fixed and triple checked nothing of a similar vein exists)
Update the TODO cleanly after first analyzing all these points, then get back to work on the updated goal.
- Land of interior bedouin societies, should be split into more granular historical tribes. Focus on making the region a little more content rich
- Same for Britain and Ireland, I want much more granular tribes and cultures, let's update that
- Also there's still a "Germanic societies" please update it to be a real tribe, no more generic stuff. People of Aestii seems very large as well, if a more granular division is available I'll take it. Berber and Gaetulian societies as well. Let's say that in general I'm not a fan of these "societies" thing, it's generic and immersion breaking, try to be more precise and granular all over the map
- Villa Liviae, the icon is not centered correctly. Overall the buildings are quite good in terms of icons ! But let's double check the centering and quality of all of them
- It seems like all the RGOs are still the vanilla ones. Please do some global passes to ensure things are a little more historically accurate for 1AD
- There are pretty few institutions per age overall, let's make it match the vanilla scale better. Same for government reforms, let's add just a lot more historically accurate and interesting content
- Advances look way better than before, however it still seems like the tree is a little incomplete. I want you to TRIPLE the number of advances globally (keep most of them region/culture/region locked for accuracy). Make sure they're all useful and interesting. Feel free to add many new buildings and laws, units, etc to match all of this new breadth. Make sure the tree looks like a tree and is interesting and historically accurate to move through.
	- also some icons like "Regional Law Codes" for example look ugly compared to the rest, let's do a pass to fix all these issues. Most of them are great 
	- also we start the game as Rome not being able to research anything, is that normal ? Double check when and what can be researched
- I checked rapidly the Estates, Parliament, Cabinet, Laws and it seems like this is all basically still vanilla. It all needs a huge highly detailed and deep overhaul to better match the period. Per country of course for major countries
- It seems like there are still some vanilla privileges available, let's double check and correct that ( I do correctly see many new privileges). Also let's add a lot more privileges, culture/country specific of course
- The Roman Empire starts bankrupt, is this normal ?
- We currently only have buildings in Rome, this is a bit weird. Let's better seed the starting map to have full other cities and villages across the whole world
- I'm still seeing the vanilla icons for pop types in the overview, per location. Let's adjust that. I do see updated names
- The flags of the various countries still seem quite generic. Make sure they're all as accurate and detailed as possible
- When I look at the geography of Germany for example, it seems like it's way less forested than it should be for that period, since it' still based on vanilla. Please fix that and analyze all other regions that have seen major geography change between 1AD and the start of vanilla, to fix that
- The icon for artillery is still a cannon which is anachronistic, fix this issue and similar ones
- This is kinda unchecked, but please make a pass on culture similarity and these kinds of things to make sure everything is authentic when ruling over multi ethnic empires
- Religio Romana has no Religion Doctrines+

### Round 3
Here are the things I observed when running the mod manually for the second time, which I want fixed extensively (ie : fixed and triple checked nothing of a similar vein exists)
Update the TODO cleanly after first analyzing all these points, then get back to work on the updated goal.
- Kind of a question here but the vanilla loading screens seem to have multiple layers to them instead of just a single element, this makes stuff kinda pop out looking cool, would it be possible to do the same for all of our loading screens ?
- When you click on a location you get an image showing sort of the geography and different buildings that actually got built there. I'm still seeing some medieval stuff in there and some stuff looks blurred for some reason, I don't think that's vanilla
- It's a bit weird having things named ... Commnity or ... Group with generic terms. First off the names are just too long and it's not super immersive, let's try and adjust that
- When I look at certain advances it shows that it unlocks dozens of things, including things that are clearly not for my culture, is this expected ? looks a little weird
- You say there are hundreds of advances but I only see like 12-20 max per age for a major country like Rome, is that expected ?
- The description for steel still mentions "guns". Let's fix all these minor text things that mention anachronistic things
- The main icons for pop types in the default view of a location are still the vanilla ones
- Are you sure Germany is forested enough ? I still see large plains in the center of it
- a lot of the new trade goods you added still show up as an icon with a rounded blue background (I saw it for Cordage and Leather Goods for example but I'm sure there's a lot more) whereas vanilla trade goods do not have backgrounds at all normally, it's litteraly just the trade good. Check wheat for example. Make sure you're exactly aligned visually with vanilla
- By default we cannot expand RGOs it requires and advance, is this intentional ? It's a core game mechanic so if so make sure that advance is available to all and quickly
- Is Spain forested enough for the time period ?
- I see there are new RGOs like tree nuts, they don't seem very widespread. Make sure they're available enough according to their importance 
- I want you to do a major Cultivator population building expansion for all civilizations that allows you to grow various crops/trade goods that aren't available in that location by default but would make sense to grow there. They're less efficient and a bit more limited than just RGOs so RGOs are still important but they allow better "tall play". These aren't cheat buildings, they should be restriced to reasonable climate zones, altitudes, forests, etc that define their availability at all and the number of them you can have. Be very extensive and cover every realistic trade good coverable
- I didn't recheck diplomacy but make sure all available action aren't anachronistic and don't be afraid to add new ones or things like new casus belli, etc Also I see certain diplomatic actions you added that don't have a proper text name and description 
- I didn't see any available mercenaries, is that mechanic working at all ?
- The trade good "Flour and bread" should offer more food than just straight up wheat no ?
- It feels like the Roman Market doesn't start off with enoug of certain construction materials to build things, which is weird in 1AD. Things like Iron Hardware, Cordage, Masonry, etc. Please make sure Rome in priority but also other major civilizations start with enough balanced buildings producing at least some of these core ressources. In general I think the start map needs more buildings
- Quite a few states start with no available units to recruit it seems. Or like 1 or 2. Let's fix that and add as many new units as needed.
- We never mentioned the Government Values (things like centralization/decentralization) but these need to be made way less medieval as well. Adapt them and their bonuses to be 1AD. Add and remove as you see fit, some can arrive in later ages
- It seems like estate privileges are not country/culture/religion specific, everyone has access to all types, let's fix that
- I was trying Parthia and they had no Laws, is this normal ?
- I didn't see any ships to build except merchant ships for Parthia, is that normal ?
- I didn't check it thoroughly but it seems like the levy system still shows vanilla units, and I dont' know if you added any levy units as well. Please recheck this whole aspect thoroughly
- I was trying to play the Suebi to get some germanic tests in and I saw they have access to all roman buildings it seems (or many at least). Make sure that buildings are correctly culture/religion locked 
- Some location in Suebian territory are named in latin, is this expected ? Do we have a system at all for names that show up in different languages depending on who's playing there ? If this is a possible mechanic then let's enrich it greatly. Especially for frontier areas and anything that would historically get conquered by Rome post 1AD


### Round 4 : GPT audit
Here are the things that an advanced auditing agent observed, which I want fixed extensively if they are indeed broken(ie : fixed and triple checked nothing of a similar vein exists)
Update the TODO cleanly after first analyzing all these points, then get back to work on the updated goal.
- The authored AD 1 world contains only one base pop per location, and that pop is either peasants or tribesmen.
- Christian institution eligibility checks antq_christian_group, but early Christianity is generated in native group christian; analogous custom groups are empty adapters.
- The Roman annona trade route remains unproven: source markets produce wheat, but Rome receives no import row.
- The 416-event headline is produced by 84 primary currents plus 332 mechanically effectless phase notifications generated to clear a 400-event target.
- The spatial population allocator uses the installed 1337 population file as the residual geographic weighting template.
- The Principate reform grants a flat monthly_gold_income = 500. -> fixing the economy instead would make more sense
- Ancient advances directly unlock legacy engine law IDs such as education_masses_law, feudal_de_jure_law and royal_court_customs_law.
- All custom religions receive nearly identical aspects, influence, tolerance and empty opinion blocks.
- Every coastal polity receives a regional patrol and transport pair, often using very broad continental templates.
	- A capability ladder would be better:
		local watercraft;
		limited transport;
		organized patrol;
		state fleet;
		long-distance naval capacity.
- All 40 bespoke decisions are player-only: ai_tick and automation_tick are never, and ai_will_do is -1000.
- Some decisions require a stockpile threshold and then add goods supply rather than consuming stock.
- The opening AI personality manager is empty.
- Many situations and disasters end only when a fixed date is reached and lack player-driven resolution or progress.
- Major disease currents generally apply prestige/stability penalties rather than population, mortality, labor, army, food or fiscal effects.
- Several international organizations are effectively static labels or one-member shells with limited actions.
- User-specific absolute Windows paths and a username are committed in config and generated manifests. -> please make sure no personal info remains in the github repo since I will be sharing it publicly later.


### Round 5 : 
Here are the things I observed when running the mod manually for the fifth time, which I want fixed extensively (ie : fixed and triple checked nothing of a similar vein exists)
Update the TODO cleanly after first analyzing all these points, then get back to work on the updated goal.
- The Loading screens system which you tried does not work. It just doesn't it's glitchy. Roll it back to fixed screenshots, good enough for now
- While a few locations seem to have somewhat acceptable historically accurate names, the vast majority of locations still have their vanilla name
	- Your next task is going to be EXTREMELY AMBITIOUS AND LONG but it needs to be done or I can ship the mod.
		- I want every single location, city, town, village, province, area and region (ie every granularity increment) to have an era appropriate name. Not a single vanilla one (unless the name hasn't changed but that's unlikely for 90%+ of localizations
		- In order to do this you will dispatch extremely numerous cheap agents to run quick researches on every localization to be changed to find the 1AD most appropriate name
		- Start big, then go into increasing granularity. It's expected that the records aren't as good for 1AD as 1337 so you'll have to make choices. NEVER BE UNCERTAIN BLA BLA WE DON'T HAVE RECORDS. MAKE CHOICES. IT'S A GAME NOT A PERFECT HISTORY LESSON. BE HISTORICALLY ACCURATE AS FAR AS YOU CAN
			- If you really don't have a specific name in the historical records you can use the less granular region name and divide it by direction (ie : West, East X) or use geological features and the local language, that kind of stuff, or tribe names or whatever kinda makes sense. If you find no records you have more creative liberty.
		- It is critical that this whole job is done well. This is not a secondary task. NO SHORTCUTS. NO CHEATING.
		- Same for sea stuff by the way and other categories like that, I didn't check everything
- I'm still seeing vanilla Holy sites, make sure these are removed and we have acceptable 1AD holy sites
- LOVE the new Cultivator buildings, super cool, system seems decently balanced
	- I want MORE, maybe new more efficient production methods as the ages advance, unlocked through the advances. Lots of them, lots of country specific stuff based on that countries specialty and climate, etc but lots of generic stuff too
		- in fact don't be afraid to add new production methods to many of the buildings not just Cultivators, especially if they don't have them
			- and don't be afraid to add even more advances and buildings and stuff to flesh out the later tech.
	- I want a similar MASSIVE extension of tribal buildings so that less settled polities can have some cool stuff as well even if it's less advanced. Give them more warrior stuff as well but also agriculture and primitive artisanry. Make it feem different from more settled pops though. Lots of content please
	- In general add more buildings to non Roman polities. The romans already have a ton but lots of more minor nations aren't very fleshed out.
- The navy system seems way too generic, make it feel more country specific even if the current idea is the right one, just add some flavor and more diversity for sea going nations (actually I rechecked and maybe it's better than I expected, still add flavor and flesh stuff out further)
- In the diseases tab I'm seeing vanilla diseases I think. Make sure every disease is realistically named for the timeframe
- I was checking the populations and I'm wondering if the Cultivator vs Tribal distribution is realistic when seeding the map. Are we sure there are enough tribal pops ? Surely most of the world still had lots of them no ? Even within great empires
- Seems like some localization are missing for situtations
- Advances for iranian and steppe are mixed in. While probably appropriate for many, let's split them up and enrich them a bit to be more specific and rich. North chinese steppe people can't have the same advances as iranians exactly. Same for North and Subsaharan africa by the way
- Rename ducats to a more realistic universal currency in game

### Round 6 : 
Here are the things I observed when running the mod manually for the sixth time, which I want fixed extensively (ie : fixed and triple checked nothing of a similar vein exists)
Update the TODO cleanly after first analyzing all these points, then get back to work on the updated goal.
- Looks like some location still have Al- or Ar- prefixes to them in North Africa, isn't that anachronistic arabic ?
- Advances are great so far. However I feel like all countries all end up getting access to the same buildings/similar techs. I want much more unique advances for specific cultures and even specific "countries" that unlock unique buffs/unique buildings/ unique units, etc that really feel a lot more specific and give that country a specific advantage in a certain field. Explore this a lot, add a lot more depth
- I opened the market tab in 1AD as Rome (without having ever made the game accelerate) and it crashed. 8/5/2026 at 11h25 or 26. Note this doesn't crash if opened later like in October 1AD so maybe it's fine to ignore this crash.
- Situations are still unclear, for example Gaius Caesar's Eastern Settlement has no progression. Also please remove "This historical current follows the strong setting", it's immersion breaking. Maybe develop situations a little more as well
- All events so far are extremely basic and all do the same thing. We need a full overhaul and fleshing out.
- Rome starts with a deficit of like -300 a month. While some challenge at the start can be acceptable, make sure this is realistic, if not then increase the economical base. Don't cheat with flat modifiers
- Control in the roman empire is 0 pretty much everywhere because of the size. There should be more ways to control. Maybe buildings that radiate control in local capitals. These should already exist at the start of the campaign in 1AD but you could unlock more centralization stuff as you reach the APEX of the empire. Same idea for other empires
- The game starts with a regency. Isn't Augustus already emperor at this time ?
- Rome has massive administrative efficiency debuffs for some reason because of unsupported accepted cultures, whatever that means
- The Municipal Lineage Arbitration -0.50% monthly control at the start is a bit of a killer as well, especially since you can can't use your cabinet to counter effect that.
- Overall just recheck the starting situation of like Rome, Parthia and Han to make sure they're not in a unexpectedly dire situation for no valid historical reason at the start. If it's historical it's fine.
- Lack of cordage in the roman market prevents you from building a lot of buildings. And no Cordage producing building exists at the start of the game.
- When selecting government reforms as Rome, I have access to things like Han Imperial Bureaucracy or Indo-Scythian Kingship, let's fix this
- Reseach seems a little slow overall, especially if we add more advances, double check if it's vanilla speed or not and don't be afraid to add more buildings/other things buffing it, if countries want to play tall 
- I got a crash in 4AD; please check what happened at 12:05AM on 8/6/2026 since you'll likely get it again

Here are the things I observed when running the mod manually and which I want fixed extensively (ie : fixed and triple checked nothing of a similar vein exists)
Update the TODO cleanly after first analyzing all these points, do not resume the goal yet.
- advances have bonuses which often appear too small and not rounded enough (they are at weird values). Things like +0.06% cabinet efficiency, +0.07% levy recovery, +0.07% trade range Or all the disease resistance stuff just shows up at 0%. Please audit all of them and make sure the buffs are not unnoticeable. Thoroughly review the scales for everyhing
- there are no buildings which actually allow you to produce Cordage which are buildable at game start. This is an issue. Please review building unlocks to make sure that the start of the game isn't stupidly locked. It's fine unlocking some buildings as time progresses but make sure every single good that can realistically be produced in 1AD has a building for it. Also please devise new trade goods which only get unlocked later in the ages and for which the population/buildings doesn't already have a need for . Add new buildings linked to that, make it smart culture and localizatin wise, etc. Just to flesh out the late game stuff more since you'll be making more buildings available immediately.
- seems like there is a tar issue now as well. Probably many more. Overall you neeed every good at the start to have some kind of production mean or you're locked. Make absolute sure of that
- administrative programmes are cool right now, Rome has quite a few. Don't be afraid to add some more, especially for smaller countries and less important cultures
- I feel like crown power should be stronger in Rome considering it is an empire at that point. See what you can do
- We got the Teutoburg forest situation despite not being at war with any German tribes. I think we need to rework this, either by forcing a war or not having it, I don't know
