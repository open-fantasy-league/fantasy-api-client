from data.dota_ids import FANTASY_LEAGUE_ID
from messages.fantasy_msgs import StatMultiplier

scoring = [
    StatMultiplier('kills', 0.3, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('assists', 0.1, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('deaths', -0.3, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('last hits', 0.003, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('denies', 0.003, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('first blood', 4.0, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('stun', 0.05, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('teamfight participation', 3.0, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('GPM', 0.002, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('towers', 1.0, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('observer wards', 0.15, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('dewards', 0.25, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('camps stacked', 0.5, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('runes', 0.25, league_id=FANTASY_LEAGUE_ID),
    StatMultiplier('roshans', 1.0, league_id=FANTASY_LEAGUE_ID)
]