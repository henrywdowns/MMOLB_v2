from pybaseball import statcast

dir(statcast)


# i actually dont know if this is worthwhile. it uses real life stats which obviously have very different underlying factors
# despite the same data, so it's not really apples to apples. INSTEAD i'll probably use this page to detail findings as i look
# at real-life baseball stats. the most compelling is WAR - wins above replacement...


"""
WAR - Wins Above Replacement
Pick up average performance of a generic replacement-level player (thought of as the most eligible minor-leagues player irl - these stats are found
by looking at the bottom 25% of lineups, fresh call-ups from the minor leagues, etc perform, as well as average-to-high minor-league stats) The 
ultimate, intended output assigns *a number of wins attributable to keeping this player on the team vs fishing for someone else*. A little bit 
like a GIH WR or IWD. Now, the Spicy Chicken Crunchwraps ARE minor league, and callups are more or less random. BUT that also offers an opportunity:
once the season begins, I can start collecting an average (running average? maybe just one that omits the first week or so of S1?) of players during
their first 5 appearances. That way I know they're fresh call-ups, and I can get a representative sample of what's in the pool of call-ups. 

THIS ALONE IS PROBABLY ENOUGH! I can get an idea of who's at the bottom of the barrel just by comparing stats. But wins attribution seems like a cool
opoprtunity to do deeper analysis, just generally familiarize myself with some more complex statistics, and just generally ID my strongest players in
a more tangible way. I think it will boil down to having a relatively trustworthy blanket metric to gauge player value. 

The Idea:
Ascertain the average performance across MMOLB to compare against my own players, to see who should be relegated and determine when I should
start spending motes on buffs, knowing that I won't risk spending them on rote underperformers. 

I'll collect data - a running average, with historical figures stored - on any player with less than 12 (number of games in a day) appearances. Realistically this seems like it 
might be compute-heavy, and that's a problem worth solving. Maybe I'll access random team data until I've collected 100-200 players and make that my
sample? Trending the running avg will reveal whether or not that's a viable sample size. 

Complications:
WAR calcs require some weighted calculations (such as wOBA - weighted on-base-average, which uses derived weights based on each combination of outs
and on-base scenarios). These weights are updated every season, which means I either need to learn how to derive the weights for my league, or use 
real-life weights as a proxy. I *think* I might be able to do the latter considering every player is under the same constraints, but it will most 
certainly introduce some inaccuracies.

Steps:

Calculate (or simply lift) wOBA weights
Calculate wRAA (weighted Runs Above Average)
    ((wOBA - league OBA)/wOBA scale) * PAs
    Once calculated...
    Add runs from stolen-bases, defensive saves, positional adjustment for PAs depending on defensive position
    [Current replacement threshold is -20 runs per 600 PAs, so the league average is 20 runs above replacement]
    So, we take the wRAA and subtract -20 (...add 20) and then convert this to WAR by dividing by average run 
    differential equivalent to a game, which is 10. 
    WAR = wRAA/10
"""

