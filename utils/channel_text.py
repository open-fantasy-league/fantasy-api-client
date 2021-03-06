import pprint

from utils.dota_scoring import scoring

SCORING_TEXT = pprint.pformat({s.name: s.multiplier for s in scoring}).replace("{", "").replace("}", "")
HELP_COMMAND_TEXT = """Hi! Checkout all these lovely commands.

If you need more help the help, rules, and scoring channels might be what you need!
"""
HELP_TEXT = """Enter our draft fantasy league with `!join`

Tuesday morning, you will be placed into a draft channel,
where you and other users will take it in turns to pick pro-players with a __**30 second**__ time-limit.
The draft starts at 13PM UTC.

See the list of pro-players with `!players`.
               
Each day of the tournament will have a separate draft, always the morning before games start.
               
Your players will earn points for every match they play in (fingers crossed for best-of-3's),
with the final day being worth double.
               
If you cannot make it to the draft time, you can preset a draft preference by messaging Mr. Robot:
`!order puppey micke s4 zai miracle nikobaby`

and the server will pick your favourites (left to right) for you,
(make sure to set more than 5, in-case someone else drafts one of your preferences).

See `!rules` for limits on who you can pick

Any problems or questions contact admin `ThePianoDentist`, I will be around 11am -> games finishing.

Good luck!
"""
RULES_TEXT = """
Maximum of **2** players from the same team.

**1 offlaner, 2 supports, 2 cores**.

If you do not pick before your draft-time is up, it will auto-pick from your preset `!order`.
If you do not have one, it will select a random player for you.    
"""
# see https://pypi.org/project/tabulate/ for options
LEADERBOARD_FORMAT = "fancy_grid"