from collections import namedtuple
# https://realpython.com/python-data-classes/

# Subscriptions
SubTeam = namedtuple('SubTeam', 'toggle')
SubCompetition = namedtuple('SubTeam', 'all, sub_competition_ids, unsub_competition_ids')


# Insert/Updates
Competition = namedtuple('Competition', 'competition_id, name, meta, timespan, series')
Series = namedtuple('Series', 'series_id, name, meta, timespan, matches, team_results, competition_id')
Match = namedtuple('Match', 'match_id, name, meta, timespan, team_match_results, player_results, series_id')
TeamSeriesResult = namedtuple('TeamSeriesResult', 'team_id, series_id, meta, result')
TeamMatchResult = namedtuple('TeamMatchResult', 'team_id, match_id, meta, result')
PlayerResult = namedtuple('PlayerResult', 'player_id, match_id, meta, result')

Team = namedtuple('Team', 'team_id, meta, names')
TeamName = namedtuple('TeamName', 'team_id, name, timespan')
TeamPlayer = namedtuple('TeamPlayer', 'team_id, player_id, timespan')
Player = namedtuple('Player', 'player_id, meta, names, positions')
PlayerName = namedtuple('PlayerName', 'player_id, name, timespan')
PlayerPosition = namedtuple('PlayerPosition', 'player_id, position, timespan')