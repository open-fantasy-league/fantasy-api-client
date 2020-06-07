import pprint

from utils.dota_scoring import scoring

SCORING_TEXT = pprint.pformat({s.name: s.multiplier for s in scoring})
HELP_TEXT = """Join our free draft fantasy league with !join\n
               At 12PM UTC on Tuesday, you will be placed into a draft channel,
               where you and other users will take it in turns to pick a pro-player.
               
               See the list of pro-players with !players.
               
               Each day of the tournament a new draft will occur, for you to pick a new team.
               
               Your players will earn points for every match they play in (fingers crossed for best-of-3's),
               with the final day being worth double.
               
               If you cannot make it to the draft time, you can preset a draft preference like so:
               !draft order puppey micke s4 zai miracle
               
               and the server will pick your favourites (left to right) for you,
               (make sure to set more than 5, in-case someone else drafts one of your preferences).
               
               See !rules for limits on who you can pick
               
               Any problems or questions contact admin `ThePianoDentist`, I will be around 11am -> games finishing.
               
               Good luck!
            """
RULES_TEXT = """
    Maximum of 2 players from the same team.
    1 offlaner, 2 supports, 2 cores.
    (Each draft has correct number of users so that everyone should get 1 offlaner, 2 supports, 2 cores)
"""