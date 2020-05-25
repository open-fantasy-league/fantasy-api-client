from collections import namedtuple
# https://realpython.com/python-data-classes/

# Subscriptions
SubTeam = namedtuple('SubUser', 'toggle')
SubLeague = namedtuple('SubLeague', 'all, sub_league_ids, unsub_league_ids')
SubDraft = namedtuple('SubDraft', 'all, sub_draft_ids, unsub_draft_ids')


# Insert/Updates
League = namedtuple('League', 'league_id, name, meta, team_size, squad_size, competition_id, '
                              'max_squad_players_same_team, max_squad_players_same_position, '
                              'max_team_players_same_team,'
                              'max_team_players_same_position')
# Draft-lockdown is the time when server locks in users who are playing, and sets the draft choice order.
# (i.e. anybody who joins league after draft lockdown, doesnt get a draft for that period. they sit out)
Period = namedtuple('Series', 'period_id, league_id, name, meta, timespan, points_multiplier, teams_per_draft,'
                              ' draft_interval_secs, draft_start, draft_lockdown')
StatMultiplier = namedtuple('StatMultiplier', 'league_id, name, meta, multiplier')

ExternalUser = namedtuple('ExternalUser', 'external_user_id, name, meta')
FantasyTeam = namedtuple('FantasyTeam', 'fantasy_team_id, league_id, external_user_id, name')

DraftQueue = namedtuple('DraftQueue', 'fantasy_team_id, player_ids')
DraftChoice = namedtuple('DraftChoice', 'draft_choice_id, timespan')

Pick = namedtuple('Pick', 'pick_id, fantasy_team_id, draft_choice_id, player_id, timespan')
ActivePick = namedtuple('ActivePick', 'active_pick_id, pick_id, timespan')