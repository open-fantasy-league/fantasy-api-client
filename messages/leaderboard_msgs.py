from collections import namedtuple
# https://realpython.com/python-data-classes/

# Subscriptions
SubLeague = namedtuple('SubLeaderboard', 'all, sub_league_ids, unsub_league_ids')
SubLeaderboard = namedtuple('SubLeaderboard', 'all, sub_leaderboard_ids, unsub_leaderboard_ids')


# Insert/Updates
Leaderboard = namedtuple('Leaderboard', 'leaderboard_id, league_id, name, meta, timespan')
Stat = namedtuple('Stat', 'leaderboard_id, player_id, timestamp, points, meta')