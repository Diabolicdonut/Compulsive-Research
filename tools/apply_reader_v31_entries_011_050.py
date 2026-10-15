#!/usr/bin/env python3
"""Apply the approved Reader V3.1 story/read-time treatment to entries 011-050."""
from __future__ import annotations

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

from reader_experience_v3 import editorial_word_count, reading_time_minutes, WORDS_PER_MINUTE

ROOT = Path(__file__).resolve().parents[1]
CARD_TOKEN = re.compile(r"\[\[([^\]]+)\]\]")

VIGNETTES = {
11: dict(title="The last three points were already waiting", era="1994 World Championship", matchup="R/G Weenie against U/W control", deck="Bertrand Lestree — R/G Weenie", opening="life-total-pressure", body="My opponent went to six and tapped out for [[Serra Angel]], certain the 4/4 flier had bought two turns. I had a [[Kird Ape]] in play, a [[Chain Lightning]] in hand, and two red mana available. During his end step I cast [[Lightning Bolt]] at him, dropping him to three. I untapped, drew another land, and sent the Ape into the Angel. He blocked, expecting to trade the creature for time. I let combat damage clear, then cast Chain Lightning at his face. The Angel was still on the battlefield when his life total reached zero."),
12: dict(title="The new hand never arrived", era="1994 U.S. National Championship", matchup="Mind Twist Control against five-color Zoo", deck="Bo Bell — Mind Twist Control", opening="topdeck-denied", body="The only card left in my opponent's hand was the one he had just drawn. I had already resolved [[Mind Twist]] for four, and [[The Rack]] was waiting for his next upkeep. He smiled, tapped three mana, and put [[Timetwister]] on the stack. Seven new cards would have erased the whole exchange. I tapped two Islands and cast [[Counterspell]]. Timetwister went to the graveyard, his hand stayed empty, and the Rack remained pointed at him. He untapped, took three, drew a single card, and passed without casting it."),
13: dict(title="Three black mana before the first attack", era="1995 World Championship", matchup="Rack Control against white-green creatures", deck="Alexander Blumke — Rack Control", opening="mana-burst", body="A single [[Swamp]] was all I showed before casting [[Dark Ritual]]. The three black mana became [[Hypnotic Specter]] on turn one. My opponent played a Plains and passed with [[Swords to Plowshares]] somewhere in the deck but not in hand. The Specter attacked on turn two and stripped [[Wrath of God]] at random. After combat I cast [[Hymn to Tourach]], taking two more cards, then laid [[The Rack]]. He began his second turn with three cards, no answer to the flier, and a permanent already measuring how little he had left."),
14: dict(title="The Dervish never reached a second counter", era="1994 World Championship", matchup="U/W/G Stasis Control against R/G Weenie", deck="Zak Dolan — U/W/G Stasis Control", opening="combat-window", body="My opponent's [[Whirling Dervish]] had already connected once and picked up its first +1/+1 counter. He added [[Kird Ape]], then moved to combat expecting protection from black to keep the Dervish safe. I let him declare both attackers before tapping [[Tundra]] for [[Swords to Plowshares]]. The Dervish disappeared, he gained three life, and [[Old Man of the Sea]] took the Ape before damage. On my turn I untapped, cast [[Serra Angel]], and left him with more life than before but no creatures and no pressure."),
15: dict(title="The tutor found the missing turn", era="2007 Vintage Championship", matchup="Gro-A-Tog against Flash combo", deck="Stephen Menendian — Gro-A-Tog", opening="exact-draw-needed", body="My opponent was at fourteen with no creature in play, but I knew [[Flash]] could end the game as soon as he untapped. My [[Quirion Dryad]] was already a 5/5, and the cards in hand did not quite make a two-turn clock. I tapped [[Underground Sea]] and [[Mox Jet]] for [[Demonic Tutor]], found [[Time Walk]], and cast it with [[Mox Sapphire]] and [[Tropical Island]]. The two blue spells grew the Dryad to 7/7. I attacked, took the extra turn, untapped, and attacked for the remaining seven before my opponent received another draw step."),
16: dict(title="Seven new cards after the hand was spent", era="2023 Old Frame Vintage World Championship", matchup="The Perfect Storm against blue control", deck="Vedast Sanxis — The Perfect Storm", opening="empty-hand-refill", body="My first six spells left almost nothing in hand: [[Duress]] took [[Force of Will]], [[Black Lotus]] and [[Dark Ritual]] made mana, and two Moxen joined the battlefield. My opponent still had four cards and two untapped lands, but no permission I had seen. I used [[Mox Ruby]] for the red mana and cast [[Wheel of Fortune]]. The last cards from both hands went to the graveyard and seven fresh ones arrived. Mine contained [[Yawgmoth's Will]], another Dark Ritual, and [[Tendrils of Agony]]. I placed the Ritual on the stack while my opponent was still reading the new seven."),
17: dict(title="The artifacts survived the equalizer", era="1996 Pro Tour New York", matchup="R/W Orb Control against green-white creatures", deck="Mark Justice — Pro Tour New York 1996", opening="asymmetric-board-count", body="Four creatures faced my empty side of the battlefield, and my opponent still held five cards. I had three lands, [[Howling Mine]], [[Winter Orb]], and one card in hand: [[Balance]]. On my turn I cast it, and my hand count was zero and my creature count was zero. He sacrificed every creature, discarded all five cards, and reduced his lands to three. My artifacts stayed exactly where they were. I passed with Howling Mine still feeding the game and Winter Orb allowing only one land back at a time. My opponent untapped a single land, drew two cards, and stared at the empty battlefield he had controlled a minute earlier."),
18: dict(title="The fourth creature made the answer better", era="1994 World Championship", matchup="U/W/G Stasis Control against R/G Weenie", deck="Zak Dolan — U/W/G Stasis Control", opening="overextension", body="My opponent already had [[Kird Ape]], [[Argothian Pixies]], and [[Whirling Dervish]] in play when he cast a second Ape. I was at eight life and had spent one [[Swords to Plowshares]], so the extra creature looked safe. I untapped [[Tundra]], [[Savannah]], [[Mox Pearl]], and [[Sol Ring]], then cast [[Wrath of God]]. All four creatures went to the graveyard at once. He drew for turn, played a land, and passed with nothing to attack. I untapped again with Serra Angel in hand and every permanent that had produced the Wrath still on my side."),
19: dict(title="The Factory was the only land left", era="1997 Pro Tour Chicago", matchup="Prison against five-color control", deck="Jon Finkel — Prison", opening="mana-base-collapse", body="My opponent tapped out for a draw spell with five lands in play. I had [[Marble Diamond]], [[Sky Diamond]], [[Winter Orb]], and three lands of my own, including [[Mishra's Factory]]. I cast [[Armageddon]]. He used his last two blue mana for [[Counterspell]], and I answered with a Counterspell of my own from the Diamonds. Every land went to the graveyard. On the next turn the artifacts still made mana, Winter Orb kept his recovery to one land at a time, and Mishra's Factory became a creature. It attacked while my opponent's hand remained full of spells he could no longer cast."),
20: dict(title="The Angel became a turn-three attacker", era="2000 Pro Tour Chicago", matchup="My Fires against blue-white control", deck="Zvi Mowshowitz — My Fires", opening="opening-curve", body="My opening hand began with [[Forest]], [[Birds of Paradise]], [[Fires of Yavimaya]], and [[Blastoderm]]. The Bird came down on turn one. On turn two it supplied the green mana while two lands cast Fires. My opponent used his second turn for [[Counterspell]] mana but let the enchantment resolve. I played a third land, tapped the Bird with the lands, and cast Blastoderm on turn three. Fires gave it haste. The 5/5 attacked immediately, and shroud kept the removal spell in my opponent's hand from touching it. The Bird had turned a four-mana creature into pressure a full turn early."),
21: dict(title="One Elf moved every threat forward", era="2000 Pro Tour Chicago", matchup="Fires of Yavimaya against blue-white control", deck="Jon Finkel — Fires of Yavimaya", opening="one-drop-acceleration", body="Turn one [[Llanowar Elves]] made the rest of my hand arrive early. On turn two the Elf and two lands cast [[Chimeric Idol]]. On turn three I played [[Fires of Yavimaya]], tapped my lands to animate the Idol, and attacked for three. My opponent spent the next turn holding up [[Counterspell]] instead of adding to the board. I made my fourth land drop, used the Elf as the fifth mana for [[Saproling Burst]], and removed three fade counters. Fires gave all three Saprolings haste. Twelve power crossed the table before the control deck had reached its fourth untap."),
22: dict(title="The Angel attacked without opening the door", era="1994 World Championship", matchup="Angel Stasis against R/G Weenie", deck="Zak Dolan — Angel Stasis", opening="vigilance-race", body="I was at five life when [[Serra Angel]] finally untapped. My opponent had [[Kird Ape]] and an animated [[Mishra's Factory]], with [[Lightning Bolt]] threatening the last points. I attacked for four and left the Angel upright. On his turn he animated the Factory and sent both creatures. Serra Angel blocked the Factory without tapping from its own attack, and [[Swords to Plowshares]] removed the Ape before damage. The Factory died in combat. I untapped at five, attacked again, and watched my opponent leave both hands on the table with no creature able to race the vigilant flier."),
23: dict(title="The Dragon made eight damage from nowhere", era="1995 U.S. National Championship", matchup="Vice Age against blue-white control", deck="Henry Stern — Vice Age", opening="late-game-topdeck", body="My opponent was at nine behind an empty battlefield and four untapped lands. I drew [[Shivan Dragon]] with [[Birds of Paradise]], six lands, and [[Lightning Bolt]] available. The Dragon resolved after he used [[Counterspell]] on an earlier [[Howling Mine]]. On my next combat he had no flier, so Shivan Dragon attacked for five. Before damage I used a Mountain to give it +1/+0, then cast Lightning Bolt after combat. The pumped Dragon and the burn spell accounted for all nine life in one turn. My opponent picked up the Counterspell in his graveyard and looked at the Dragon that had arrived one draw too late to stop."),
24: dict(title="The die found Wrath", era="1994 U.S. National Championship", matchup="Mind Twist Control against white-blue control", deck="Bo Bell — Mind Twist Control", opening="random-discard", body="[[Black Lotus]] became three black mana before my opponent’s first turn, and [[Hypnotic Specter]] entered beside [[Underground Sea]] and [[Mox Sapphire]]. He opened on [[Tundra]] and passed. On my second turn I played [[Island]], attacked, and let the Specter’s trigger decide which card left his hand. We turned the cards face down, rolled for one, and [[Wrath of God]] went to the graveyard. I tapped the Mox for [[The Rack]] and passed with both lands untapped. He played [[Plains]] on his second turn and cast [[Swords to Plowshares]] at the Specter. I answered with [[Counterspell]]. He picked up his remaining hand, counted it once, and passed. On my third turn the Specter crossed the empty sky again.", sequence={"schema_version": 1, "on_the_play": "speaker", "turns": [{"active_player": "speaker", "turn": 1, "land_drops": ["Underground Sea"], "actions": ["played Mox Sapphire", "sacrificed Black Lotus for three black mana", "cast Hypnotic Specter"]}, {"active_player": "opponent", "turn": 1, "land_drops": ["Tundra"], "actions": ["passed"]}, {"active_player": "speaker", "turn": 2, "land_drops": ["Island"], "actions": ["attacked with Hypnotic Specter", "random discard put Wrath of God into the graveyard", "cast The Rack using Mox Sapphire"]}, {"active_player": "opponent", "turn": 2, "land_drops": ["Plains"], "actions": ["cast Swords to Plowshares targeting Hypnotic Specter", "speaker cast Counterspell using Underground Sea and Island"]}, {"active_player": "speaker", "turn": 3, "land_drops": [], "actions": ["attacked with Hypnotic Specter"]}]}),
25: dict(title="Combat stopped while the Assassin waited", era="1994 U.S. National Championship", matchup="Mind Twist Control against R/G creatures", deck="Bo Bell — Mind Twist Control", opening="threat-of-activation", body="My [[Royal Assassin]] had not destroyed anything yet, but my opponent's combat step had already changed. He controlled [[Kird Ape]] and [[Argothian Pixies]], both large enough to pressure my life total. When he tried [[Control Magic]] on the Assassin, I used [[Counterspell]]. He moved to combat, tapped the Pixies to attack, and I activated Royal Assassin before damage. The Pixies died. On the next turn he looked at the Ape, looked at the untapped Assassin, and passed without attacking. [[The Rack]] dealt damage during his upkeep while his best creature remained standing still."),
26: dict(title="The Factory left a counter behind", era="1996 World Championship", matchup="Mono-black control against white-blue control", deck="Henry Stern — 1996 World Championship", opening="combat-growth", body="After [[Nevinyrral’s Disk]] cleared the battlefield, I cast [[Sengir Vampire]] into an empty sky. My opponent rebuilt with [[Mishra's Factory]] and animated it to block the first attack. The Factory dealt two damage, Sengir dealt four, and the land went to the graveyard. Because the Vampire had damaged the creature that died, it received a +1/+1 counter. On the next turn my opponent cast [[Swords to Plowshares]], but I used [[Contagion]] to remove his only other threat before the Vampire left. I gained five life from the enlarged Sengir, and the counter it had earned changed the size of the answer as well as the attack."),
27: dict(title="The Djinn survived the counter war", era="1994 U.S. National Championship", matchup="Mind Twist Control against white-blue control", deck="Bo Bell — Mind Twist Control", opening="permission-fight", body="My opponent cast [[Serra Angel]] with two cards left in hand. I used [[Counterspell]], and he answered with his own Counterspell. A second blue pair from [[Mox Sapphire]] and [[Underground Sea]] let me win the exchange. On my turn [[Black Lotus]] supplied the last mana for [[Mahamoti Djinn]], leaving two lands untapped. He tried [[Control Magic]] immediately. I countered that too. The 5/6 flier survived the stack fight, untapped, and began attacking while my opponent drew one card at a time looking for another answer."),
28: dict(title="Four green mana paid the impossible upkeep", era="1995 World Championship", matchup="Green-white aggro against white-blue control", deck="Ivan Curina — Green-White Aggro", opening="upkeep-payment", body="My opponent passed the turn expecting [[Force of Nature]] to punish me. The upkeep trigger demanded four green mana, and my lands looked short because one Forest was tapped. I used [[Llanowar Elves]], [[Fyndhorn Elves]], [[Birds of Paradise]], and the untapped Forest to pay all four. Force of Nature remained in play. During combat he blocked the 8/8 with [[Serra Angel]]. I cast [[Giant Growth]], making the trampler 11/11. Four damage killed the Angel and seven carried over to my opponent. The creature that was supposed to damage me instead removed his best blocker and most of his life total."),
29: dict(title="The Thrull paid the Lord's price", era="2009 Duel Decks era", matchup="Demonic against Divine", deck="Demonic", opening="sacrifice-engine", body="[[Breeding Pit]] had already made two Thrull tokens when I drew [[Lord of the Pit]]. Five Swamps and [[Dark Ritual]] produced the seven mana to cast it. My opponent attacked with [[Serra Angel]] on the next turn, then left a smaller flier back to block. At my upkeep the Lord demanded a creature, so I sacrificed one Thrull and kept the 7/7. The remaining token stayed beside [[Fallen Angel]] while Lord of the Pit attacked. The small flier absorbed part of the damage, but trample carried the rest across. My opponent moved the blocker to the graveyard and stared at the second Thrull already waiting for the next upkeep."),
30: dict(title="His Dragon left, but mine stayed", era="1994 World Championship", matchup="Angel Stasis against red-green control", deck="Zak Dolan — Angel Stasis", opening="copy-and-remove", body="My opponent tapped six mana for [[Shivan Dragon]] and passed with one red source open. I untapped and cast [[Vesuvan Doppelganger]], choosing the Dragon as it entered. He attacked first on the next turn and pumped his original once. I took six, then used [[Swords to Plowshares]] on his Shivan Dragon before my own combat. The original disappeared, but the Doppelganger remained a 5/5 flying copy. I attacked with it, then passed with [[Mana Drain]] available. His Dragon was gone, and the blue imitation was still on my side of the table."),
31: dict(title="The second Angel created an extra turn", era="1994 World Championship", matchup="Angel Stasis against R/G Weenie", deck="Zak Dolan — Angel Stasis", opening="copy-own-threat", body="One [[Serra Angel]] had already attacked my opponent to four when I drew [[Clone]]. I cast Clone and chose my own Angel, creating a second vigilant 4/4. The new creature could not attack that turn, so I used [[Mox Sapphire]] and [[Tundra]] to cast [[Time Walk]]. On the extra turn both Angels untapped and attacked together for eight. My opponent used [[Swords to Plowshares]] on the original, gaining me four life, but the Clone remained Serra Angel and dealt the last four damage. The copy had entered one turn late and still arrived in time."),
32: dict(title="The Dragon changed sides", era="1994 U.S. National Championship", matchup="Mind Twist Control against red-green creatures", deck="Bo Bell — Mind Twist Control", opening="stolen-finisher", body="My opponent spent six mana on [[Shivan Dragon]] and left one Mountain untapped for the pump ability. I untapped, paid four for [[Control Magic]], and moved the Dragon to my side. He immediately cast [[Disenchant]] on the Aura. I tapped two blue sources for [[Counterspell]], leaving Control Magic attached. On my combat step the stolen Dragon attacked its former controller for five, and [[Fireball]] finished the remaining life after damage. He had committed an entire turn to the largest creature in his deck and watched it become mine before it ever attacked for him."),
33: dict(title="The Orb disappeared before my untap", era="1997 Pro Tour Paris", matchup="Mono-blue skies against prison", deck="Jason Gordon — Pro Tour Paris 1997", opening="end-step-answer", body="My opponent resolved [[Winter Orb]] after I tapped low for [[Waterspout Djinn]]. I untapped only one land, attacked, and passed with three lands still tapped. During his end step I used the single white source from [[Flood Plain]] and cast [[Disenchant]] on the Orb. He tried [[Power Sink]], but I paid with the Island that had remained untapped. Winter Orb went to the graveyard before my next untap step. All my lands returned, Waterspout Djinn attacked again, and I held [[Dissipate]] with enough mana to stop the artifact he hoped would replace it."),
34: dict(title="The blocked Boa still dealt five", era="1999 World Championship", matchup="Mono-green Stompy against blue control", deck="Nicolai Herzog — 1999 World Championship", opening="blocked-lethal", body="My opponent was at five and put a 2/2 creature in front of [[River Boa]]. The Boa already carried [[Rancor]], so it was a 4/1 with trample. After blockers I cast [[Giant Growth]], raising it to 7/4. Two damage was enough to destroy the blocker, and the remaining five trampled through. He showed me the [[Counterspell]] he had kept for [[Overrun]], but combat was already resolving. The one-mana instant had turned an ordinary block into exactly lethal damage."),
35: dict(title="The Ruins became the last point of mana", era="1996 Sligh era", matchup="Sligh against white-blue control", deck="Paul Sligh — Sligh", opening="mana-count-puzzle", body="My opponent stabilized at five life with [[Serra Angel]] and no cards in hand. I had four Mountains, [[Dwarven Ruins]], and [[Fireball]]. The Ruins could have tapped for one red mana, but I sacrificed it for two instead. Together the five lands produced six mana: one red and five for X. I cast Fireball for five damage. Earlier [[Lightning Bolt]] and [[Black Vise]] had done the rest of the work; the final spell only needed the exact amount. My opponent counted the mana twice, then moved Serra Angel and the rest of the battlefield together into the box."),
36: dict(title="Nineteen life became twenty damage", era="1994 World Championship", matchup="R/G Weenie against U/W/G control", deck="Bertrand Lestrée — Red-Green Weenie", opening="turn-one-combo", body="My opening was [[Taiga]], [[Black Lotus]], [[Channel]], and [[Fireball]]. I played Taiga, sacrificed the Lotus for three green mana, and spent two of it on Channel. The remaining green mana waited in the pool. I paid nineteen life to Channel for nineteen colorless mana, tapped Taiga for red, and cast Fireball with X equal to twenty. My opponent had not played a land and still held [[Swords to Plowshares]], [[Serra Angel]], and the rest of a perfectly reasonable opening hand. Fireball resolved, and the game ended with me at one life before his first turn."),
37: dict(title="Five cards vanished at random", era="1995 World Championship", matchup="Rack Control against white-blue control", deck="Alexander Blumke — Rack Control", opening="hand-destruction", body="My opponent had rebuilt to five cards behind [[Land Tax]] and was holding enough removal to survive the creatures on my side. I tapped four Swamps, used a fifth to cast [[Dark Ritual]], and spent six mana on [[Mind Twist]] for five. Every card in his hand was discarded at random, including [[Swords to Plowshares]] and [[Wrath of God]]. I followed with [[The Rack]] and passed. He untapped with no hand, took three damage, drew one card, and found a land. The answer-rich hand he had protected for several turns was gone in a single resolution."),
38: dict(title="The first land never reached turn two", era="2011 Legacy", matchup="Mono-Black Pox against blue-green tempo", deck="Reid Duke — Mono-Black Pox", opening="first-land-attack", body="My opponent led with [[Tropical Island]] and [[Ponder]]. I played [[Swamp]], cast [[Dark Ritual]], and used one black mana for [[Inquisition of Kozilek]]. The hand showed [[Brainstorm]], [[Tarmogoyf]], and only one additional land. I took Brainstorm, then spent the remaining two black mana on [[Sinkhole]], destroying Tropical Island. He drew, failed to find a land, and discarded at end step. On my next turn [[Wasteland]] was ready for the second land from his opening hand, while [[Mishra's Factory]] waited to become the clock."),
39: dict(title="The Island lasted one turn", era="1998 Tempest-era Extended", matchup="Original Ponza against mono-blue control", deck="Brian Kowal and Adrian Sullivan — Original Ponza", opening="turn-two-land-destruction", body="My opponent opened on [[Island]] and passed. I had played [[Mountain]] and [[Mogg Fanatic]] on turn one; on turn two I added [[Ancient Tomb]]. The Tomb and Mountain cast [[Stone Rain]], destroying the Island before [[Counterspell]] was available. He played another land and passed. I untapped, used [[Wasteland]] on that land, and attacked with Mogg Fanatic. By the time [[Shard Phoenix]] joined the battlefield, my opponent had drawn several blue spells and still controlled no mana source capable of casting them."),
40: dict(title="The extra cards became the damage", era="2006 Pro Tour Honolulu", matchup="Owling Mine against white-blue control", deck="Tiago Chan — Pro Tour Honolulu 2006", opening="draw-step-trap", body="My opponent began the turn at nine life with seven cards in hand. [[Ebony Owl Netsuke]] triggered during upkeep and dealt four before the draw step. Two copies of [[Howling Mine]] then made him draw three cards. He tapped four mana for [[Wrath of God]], reducing the hand to nine cards. With Wrath still on the stack I cast [[Sudden Impact]]. It dealt nine damage, and the game ended before the sweeper resolved. The Mines had looked symmetrical when they entered; on that turn every extra card became another point aimed at their controller."),
41: dict(title="I tapped the prison before my own untap", era="1996 Pro Tour New York", matchup="R/W Orb Control against midrange creatures", deck="Mark Justice — R/W Orb Control", opening="orb-toggle", body="[[Winter Orb]] had limited my opponent to one land for three turns, but it restricted me too. At the end of his turn I paid one mana and used [[Icy Manipulator]] to tap my own Orb. Because the artifact was tapped during my untap step, all four of my lands untapped. I cast [[Balance]], activated [[Mishra's Factory]], and still had mana for [[Lightning Bolt]]. Winter Orb untapped with everything else and locked the game again before my opponent's next untap. He untapped one land while I had used a full turn's mana and an animated Factory. The Manipulator had opened the prison only for me."),
42: dict(title="The Disk left one land ready to attack", era="1997 Pro Tour Chicago", matchup="U/R/W control against creature midrange", deck="David Mills — Pro Tour Chicago 1997", opening="delayed-reset", body="I cast [[Nevinyrral’s Disk]] tapped and passed with [[Counterspell]] available. My opponent added a third creature, then used [[Control Magic]] on my [[Frenetic Efreet]], trying to win before the Disk could untap. I countered the Aura but let the creature resolve. On my turn the Disk untapped. I paid one mana, tapped it, and destroyed every creature, artifact, and enchantment on the battlefield. [[Mishra's Factory]] survived because it was still only a land. I activated the Factory after the board cleared and attacked into an empty table."),
43: dict(title="Four mana drew the only answer", era="1996 U.S. National Championship", matchup="U/W Millstone Control against red control", deck="Michael Loconto — U/W Millstone Control", opening="end-step-draw", body="I was at three life with four untapped lands and no counterspell in hand. During my opponent's end step I activated [[Jayemdae Tome]], paid four mana, and drew [[Counterspell]]. On his next turn he tapped out for [[Fireball]] with X equal to three. I used two lands to counter it and kept the other two available for [[Swords to Plowshares]]. The following turn [[Millstone]] removed two more cards from his library. The Tome had spent an entire turn's mana to draw one card, and that one card was the difference between losing immediately and returning to the control plan."),
44: dict(title="The opening hand dealt damage before combat", era="1996 U.S. National Championship", matchup="Necropotence against white-blue control", deck="Dennis Bentley — Necropotence", opening="opening-hand-punishment", body="I used my first [[Swamp]] to cast [[Black Vise]] and named my opponent. His seven-card hand dealt three damage during the first upkeep. On turn two I cast [[Dark Ritual]] into [[Hypnotic Specter]]. The Specter connected once, then [[Hymn to Tourach]] removed two more cards. Black Vise stopped dealing damage as the hand shrank, but by then it had already turned the keep itself into a liability and helped force my opponent to cast [[Swords to Plowshares]] before he wanted to. The artifact had done its work before either player reached the middle game."),
45: dict(title="Two empty-hand triggers ended it", era="2017 Modern", matchup="8-Rack against Jund", deck="Tom Ross — 8-Rack", opening="upkeep-triggers", body="My opponent was at six with two cards in hand. [[Liliana of the Veil]] made both of us discard; I put [[Raven's Crime]] into my graveyard. I then played a land, retraced Raven's Crime, and took his final card. [[The Rack]] and [[Shrieking Affliction]] were already on the battlefield. At the beginning of his upkeep, The Rack saw zero cards and dealt three. Shrieking Affliction saw one or fewer and dealt three more. He never reached the draw step. The last land in my hand had become the discard spell that turned both permanents on at once."),
46: dict(title="The Ranger found mana inside the lock", era="1997 World Championship", matchup="Señor Stompy against blue control", deck="Svend Geertsen — Señor Stompy", opening="resource-workaround", body="[[Winter Orb]] left my opponent with one untapped land, but my own deck was built to keep moving. I untapped a Forest, tapped [[Fyndhorn Elves]] for green, then used [[Quirion Ranger]] to return the tapped Forest to my hand and untap the Elf. I replayed the Forest as my land for the turn and used the mana to cast [[Lhurgoyf]]. My opponent could not hold up [[Counterspell]] and develop the battlefield at the same time. On the next attack, [[Giant Growth]] turned the smaller creature he chose to block into a losing exchange while the Orb kept the rest of his lands sideways."),
47: dict(title="The Dragon never untapped again", era="1994 World Championship", matchup="Control/Prison against red-green creatures", deck="Zak Dolan — Control/Prison", opening="large-creature-lock", body="My opponent attacked once with [[Shivan Dragon]] and left it tapped. I untapped, cast [[Meekstone]], and passed with [[Icy Manipulator]] available. During his next untap step the Dragon's power kept it from untapping. He played another large creature, so I used Icy Manipulator to tap that one before the following untap. [[Serra Angel]] attacked from my side and remained untapped because of vigilance, so Meekstone never needed to release it during an untap step. The Dragon stayed sideways for the rest of the game, present on the battlefield but removed from combat by a one-mana artifact."),
48: dict(title="The flip landed on the one card that mattered", era="2015 Eternal Weekend Old School", matchup="R/G Aggro against white prison", deck="Kevin An — R/G Aggro", opening="physical-action", body="My opponent had arranged [[Moat]] away from the lands and creatures, but it was still the permanent stopping every ground attack. I set [[Chaos Orb]] on the table, raised it above the play area, and flipped it. The card turned once and landed across Moat without touching anything else. Moat went to the graveyard. I untapped, cast [[Ball Lightning]], and attacked with it beside [[Kird Ape]]. A [[Giant Growth]] on the Ape pushed the combat beyond the blockers he had left. The entire board had been organized around one enchantment, and the Orb removed exactly that square of cardboard."),
49: dict(title="The subgame cut five life to two", era="1994 Old School representative play", matchup="B/W Shahrazad against red-green aggression", deck="B/W Shahrazad — Dreams and Pestilence", opening="game-within-game", body="My opponent was at five life in the main game when I cast [[Shahrazad]]. We set the main battlefield aside and began the subgame with the cards remaining in our libraries. [[White Knight]] held off his early creatures, [[Swords to Plowshares]] removed the largest attacker, and [[Underworld Dreams]] punished the extra cards he drew while trying to recover. He conceded the subgame rather than play through the lock. We returned to the original table, and Shahrazad made him lose half his life rounded up, dropping five to two. I untapped in the main game and cast [[Drain Life]] for the last two."),
50: dict(title="I destroyed the lock only on my turn", era="1996 World Championship", matchup="Turbo Stasis against creature midrange", deck="Tommi Hovi — Turbo Stasis", opening="self-reset-lock", body="[[Kismet]] made my opponent's new lands enter tapped, and [[Stasis]] prevented the old ones from untapping. I paid the blue upkeep for several turns while [[Howling Mine]] supplied cards. At the end of his turn I tapped [[Despotic Scepter]] to destroy my own Stasis. My untap step returned every land and the Scepter. I drew, replayed a second Stasis, and passed. My opponent had never received an untap step between the two copies because the first enchantment disappeared only after his turn was over. He looked at the tapped lands, then at the new Stasis, and moved directly to drawing a card."),
}


def append_card_markup(soup: BeautifulSoup, parent, text: str) -> None:
    pos = 0
    for match in CARD_TOKEN.finditer(text):
        if match.start() > pos:
            parent.append(NavigableString(text[pos:match.start()]))
        card = match.group(1)
        span = soup.new_tag("span", attrs={"class": "card-name", "data-card": card, "tabindex": "0"})
        span.string = card
        parent.append(span)
        pos = match.end()
    if pos < len(text):
        parent.append(NavigableString(text[pos:]))


def v3_style_from_pilot() -> str:
    pilot = BeautifulSoup((ROOT / "010-sol-ring.html").read_text(encoding="utf-8"), "lxml")
    style = pilot.find("style", id="cr-reader-experience-v3")
    if style is None:
        raise RuntimeError("Pilot Reader V3 style not found")
    return style.decode()


def ensure_read_time(soup: BeautifulSoup) -> tuple[int, int]:
    count = editorial_word_count(soup)
    minutes = reading_time_minutes(count)
    byline = soup.select_one(".byline")
    if byline is None:
        raise RuntimeError("missing .byline")
    pill = None
    for candidate in byline.select(".pill"):
        if "minute read" in candidate.get_text(" ", strip=True).lower():
            pill = candidate
            break
    if pill is None:
        raise RuntimeError("missing read-time pill")
    pill["data-reading-word-count"] = str(count)
    pill["data-reading-time-wpm"] = str(WORDS_PER_MINUTE)
    pill.string = f"Approximately {minutes} minute read"
    return count, minutes


def ensure_serra_strategic_legacy(soup: BeautifulSoup, entry: int) -> None:
    if entry != 22 or soup.find("section", id="strategic-legacy-brief") is not None:
        return
    opening = soup.find("section", id="opening")
    if opening is None:
        raise RuntimeError("Serra Angel: missing opening")
    fragment = BeautifulSoup("""<section class="strategic-legacy-brief" id="strategic-legacy-brief"><div class="chapter-number">Strategic legacy</div><h2>Why Serra Angel matters</h2><p class="brief-lead">Serra Angel established white's iconic finisher: a large evasive creature whose vigilance turns every attack into pressure without surrendering defense.</p><div class="strategic-legacy-grid"><div class="strategic-legacy-card"><h3>How to use it</h3><p>Cast Serra Angel when the battlefield is stable enough for a five-mana threat to matter, then exploit vigilance by attacking while preserving a blocker. Removal and sweepers are strongest before the Angel arrives, because an open board converts every turn into both offense and defense.</p></div><div class="strategic-legacy-card"><h3>How to fight it</h3><p>Use unconditional removal, countermagic, or a larger flier rather than relying on a race that vigilance disrupts. If direct removal is scarce, force the Angel to block in a combat that trades it for multiple attackers or clears the way for a second threat.</p></div><div class="strategic-legacy-card tournament-impact"><h3>Tournament and cultural record</h3><p class="tournament-impact">Serra Angel appeared in Zak Dolan's 1994 World Championship control deck and remained a defining white finisher through early tournament Magic, starter products, and decades of core-set reprints.</p></div></div></section>""", "lxml").find("section")
    opening.insert_after(fragment)
    toc = soup.find("nav", class_="toc")
    if toc is not None and toc.find("a", href="#strategic-legacy-brief") is None:
        opening_link = toc.find("a", href="#opening")
        if opening_link is not None:
            link = soup.new_tag("a", href="#strategic-legacy-brief")
            link.string = "Why Serra Angel matters"
            opening_link.insert_after(link)


def rewrite(path: Path, entry: int, style_html: str) -> dict:
    spec = VIGNETTES[entry]
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "lxml")
    body = soup.body
    opening = soup.find("section", id="opening")
    if body is None or opening is None:
        raise RuntimeError(f"{path.name}: missing body/opening")
    card = body.get("data-article-card")
    if not card:
        raise RuntimeError(f"{path.name}: missing data-article-card")

    ensure_serra_strategic_legacy(soup, entry)

    deck_titles = {n.get_text(" ", strip=True) for n in soup.select("details.deck summary strong")}
    if spec["deck"] not in deck_titles:
        raise RuntimeError(f"{path.name}: deck reference {spec['deck']!r} not found")

    old = opening.select_one(":scope > .play-vignette")
    if old:
        old.decompose()

    vignette = soup.new_tag("aside", attrs={
        "class": "play-vignette",
        "data-featured-card": card,
        "aria-label": f"First-person table story for {card}",
        "data-vignette-scenario": "representative-recollection",
        "data-vignette-voice": "first-person-recollection",
        "data-vignette-era": spec["era"],
        "data-vignette-matchup": spec["matchup"],
        "data-vignette-deck-reference": spec["deck"],
        "data-vignette-opening": spec["opening"],
    })
    label = soup.new_tag("div", attrs={"class": "vignette-label"})
    label.string = "A story from the table"
    heading = soup.new_tag("h3")
    heading.string = spec["title"]
    paragraph = soup.new_tag("p")
    append_card_markup(soup, paragraph, spec["body"])
    vignette.extend([label, heading, paragraph])
    if spec.get("sequence"):
        sequence = soup.new_tag("script", attrs={"class": "vignette-sequence-data", "type": "application/json"})
        sequence.string = "\n" + json.dumps(spec["sequence"], indent=2, ensure_ascii=False) + "\n"
        vignette.append(sequence)
    opening.append(vignette)

    body["data-reader-experience"] = "v3"
    body["data-vignette-specificity"] = "period-grounded-oral-history"

    old_style = soup.find("style", id="cr-reader-experience-v3")
    if old_style:
        old_style.decompose()
    style_node = BeautifulSoup(style_html, "lxml").find("style")
    soup.head.append(style_node)

    # Compute after the story and style are in place.
    count, minutes = ensure_read_time(soup)
    path.write_text(str(soup), encoding="utf-8")

    return {
        "entry": entry,
        "file": path.name,
        "card": card,
        "title": spec["title"],
        "era": spec["era"],
        "matchup": spec["matchup"],
        "deckReference": spec["deck"],
        "scenario": "representative-recollection",
        "openingMode": spec["opening"],
        "wordCount": count,
        "readingMinutes": minutes,
        "story": CARD_TOKEN.sub(lambda m: m.group(1), spec["body"]),
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=11)
    parser.add_argument("--end", type=int, default=50)
    args = parser.parse_args()
    if args.start < 11 or args.end > 50 or args.start > args.end:
        raise SystemExit("range must be within 11-50")

    style_html = v3_style_from_pilot()
    rows = []
    for entry in range(args.start, args.end + 1):
        matches = list(ROOT.glob(f"{entry:03d}-*.html"))
        if len(matches) != 1:
            raise RuntimeError(f"entry {entry:03d}: expected one article, found {len(matches)}")
        row = rewrite(matches[0], entry, style_html)
        rows.append(row)
        print(f"Updated {matches[0].name}: {row['wordCount']} words -> {row['readingMinutes']} minutes")

    ledger_path = ROOT / "research-dossiers" / "READER-V3.1-NUMBERED-WAVE-01-STORY-LEDGER.json"
    existing = []
    if ledger_path.exists():
        try:
            existing = json.loads(ledger_path.read_text(encoding="utf-8")).get("stories", [])
        except Exception:
            existing = []
    by_entry = {int(x["entry"]): x for x in existing if "entry" in x}
    for row in rows:
        by_entry[row["entry"]] = row
    payload = {
        "project": "Compulsive Research",
        "readerVersion": "3.1",
        "wave": "Numbered Wave 1 Reader V3.1 retrofit",
        "range": "011-050",
        "method": "Each visible story is a representative first-person reconstruction grounded in the exact Deck Archive title recorded in hidden article metadata. It is not a quotation or a claim that a documented match followed the narrated sequence word for word.",
        "stories": [by_entry[k] for k in sorted(by_entry)],
    }
    ledger_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
