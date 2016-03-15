# Veripeditus AR Game Server

Server component for the Veripeditus augmented-reality game framework

## What is Veripeditus?

Veripeditus (from Latin „veritas“ → „truth“ and „pedis“ → „foot“) is a
client/server augmented reality gaming engine and framework. It allows
writing game „cartridges“ for the server, which it can then run. Players
access the game while being outside with a mobile device.

## Reference games

While developing the framework, two reference games are developed:

 * [Verimagica](https://github.com/Veripeditus/game-verimagica),
   a fantasy game about magic, designed by Eike
 * [Ingressio](https://github.com/Veripeditus/game-ingressio),
   a clone of the popular Ingress game, designed by Nik

## Development

The server component, the framework and the games are developed in pure
Python. There are a few design/development principals:

 * Game cartridges must be easy to develop with basic Python skills
 * The framework and engine must be dynamic enough to allow a large
   number of different game types to be developed
 * The framework must not carry any code that is specific to only
   a single type of game
 * Development is test-driven and test-first
 * pylint is to be used and obeyed
 * Code must at all times be compatible with Python versions in Debian
   stable and Debian unstable

### Code state

The CI state represents the results from unit tests, pylint and coverage
assessment.

[![Build Status](https://travis-ci.org/Veripeditus/veripeditus-server.svg?branch=master)](https://travis-ci.org/Veripeditus/veripeditus-server)

## Authors

The authors and lead developers of Veripeditus are…

 * … Eike Time Jesinghaus <<eike@naturalnet.de>>, a young Python and PyGame
   developer, born 2001 (14 years old at the time the project started)
   and an expert Python and PyGame developer and tutor since his 11ᵗʰ
   birthday, and …
 * … Dominik George <<nik@naturalnet.de>>, formerly teacher of Eike, now
   at times his trainee regarding Python magic.

## Licence

The project is licenced under the GNU Affero GeneralPublic License
version 3 or later. All artwork and other non-code parts are also
dual-licenced under the Creative Commons-Attribution-Share Alike 4.0
Unported licence (or later). See the
[COPYING](https://github.com/Veripeditus/veripeditus-server/blob/master/COPYING)
file for more details.

## Description
Players can open up groups that are made of 2 or more players. The players in
this group move in there own world of the game so the players can only
interact directly with the other ones in their group. The following all takes
place in a single group not globally. Every player is meant as every player in
one group.

Every player embodies some kind of magician. These can collect experience
points in different ways. At a particular number of experience points the
player gets a level-up. This number of points grows larger exponentielly with
the increase of the level of the player. Through a level-up players can learn
new spells, equip new armor etc. Also with a level-up the base-values of the
player. That means that the same spell could do more damage if the player is
level 5 than if the player was only level 3. Examples of base-values would be:
HP (Health Points)
AP (Attack Points)
DP (Defense Points)

For gathering experience points a player can accept a quest which he gets
from NPCs. A quest for example could be beating 10 enemys X or farming
5 items Y. When a quest is completed you go to the NPC that gave it to you
to acquire your earnings. If items need to be given to the NPC those get
removed from the players inventory. NPCs can spawn everywhere but also despawn
after 5 days or so. If you have a quest from an NPC that despawns that quest
counts as uncompleted and the player doesn't get any rewards. Every NPC only
has one quest, but that can be done by every player of the group and every
player can also get the rewards for that quest.

Items and armor are stored in a slot system in the players inventory. Items
can't be stacked so there can be only one item per slot. The size of the
inventory (so the number of slots) can only be increased with upgrades that
can be bought from marchants. Marchants spawn and despawn like every other
NPC. You trade with the in-game currency gold which you can earn for fighting,
completing quests and collecting it on the map. When collecting gold from the
map you also get a little amount of XP. Players can also trade between them
selves. If two players want to trade they have to be next to each other.
One of the players makes an offer out of items armor and gold. The other one
then makes a counter offer that the other one can accept. If he does, items
armor and gold are switched and the trading is finished. You can only pay
with gold with NPCs.

A main part of the game shall be fighting with other players and computer
controlled enemies like wild enemies and monsters. To fight against another
player that player needs to accept a fighting offer. You can also start a
team fight with sending the offer to different people simultaniously. If
every player accepts it teams can be built. Also every player can place a bet
made out of items gold and armor. If a bet is removed or placed every other
player needs to accept again so that at the end every player is happy with
the bets. The winner or winner team of a fight gets all the items gold and
armor that was placed. If the winner was a team of players these things are
shared among the players of the winning team. Which things that are is random.
The players can still trade them if they want to switch the items. Both the
winners and the losers get experience points for the fight but the winners
get way more. When fighting against computer controlled enemies there is a
chance of them dropping items and/or materials like bones etc. You fight
with the use of spells. A fight takes place in realtime, so attacks aren't
chosen turn by turn. When not in a fight a player can equip 4 (or 6 maybe)
spells that he can then use for the case of a fight. A player can learn as
many spells as he wants, but that way he can only use 4 of them at a time.
When a spell was used that spell gets a cooldown which varys from spell to
spell. The cooldown is the time that the spell can't be used after usage.
Damage works as follows:
DMG = attacker.AP + spell.AP - defender.DP
The HP of the defender get decreased by the damage. An attack only deals
damage when it actually hits the other player. An attack has a hit rate from
10% to 100%. It's random whether an attack hits or not. Also a player can
evade an attack which is also random. The evasion rate is determined by the
armor the player is wearing. Without any armor armor it is 0%. The evasion
rate can't be over 20%. Per random you can also land a critical hit which
deals much more damage! The chance for a critical hit and the multiplicator
of the damage when landing a critical hit both vary from spell to spell and
the chance can also be slightly increased by armor. Additionally to the normal
damage an attack can cause state changes like parilyzis or poisoning.

To learn a new spell when possible one needs to got to a magician NPC who
teaches you a new spell for the cost of gold. The acquisition of a spell takes
time! Some spells may need only 10 minutes while others may need 2 hours.
Whilst learning a spell you can only move over the map but not act in any
other way. You can abort that process but afterwards you need to start again
from the beginning. Some spells are used for attacking others are used for
healing your self and such. The attributes of an attack spell are:

- Strength
	- Critical hit rate
	- Critical hit multiplicator
	- Minimal damage
- State changes
	- Target
	- Strenght
	- Duration
- Cooldown
- Hit rate
- Conditions

The attributes of a state spell are:

- State changes
	- Target
	- Strength
	- Duration
- Cooldown
- Hit rate
- Conditions

When a player is beaten in battle he gets a game-over. The player now has to
wait for 15 minutes until he can play again or he can pay a little fee to
get back in play immediately.
