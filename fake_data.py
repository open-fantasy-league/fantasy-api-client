import uuid
from messages.result_msgs import Competition, Series, Match, Team, TeamName, Player, PlayerPosition, PlayerName, \
    TeamPlayer

comp_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
series_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
match_ids = [str(uuid.uuid4()) for _ in range(4)]
team_ids = [str(uuid.uuid4()) for _ in range(4)]
player_ids = [str(uuid.uuid4()) for _ in range(8)]

EXAMPLE_COMPS = [
    Competition(comp_ids[0], "comp 1", {}, ["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], None),
    Competition(comp_ids[0], "comp 2", {"jim": "jones"}, ["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], None)
]

EXAMPLE_SERIES = [
    Series(competition_id=comp_ids[0], series_id=series_ids[0], name="series 1", meta={}, timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], matches=None, team_results=None),
    Series(competition_id=comp_ids[0], series_id=series_ids[1], name="series 2", meta={"jim": "jones"}, timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], matches=None, team_results=None)
]

EXAMPLE_MATCHES = [
    Match(match_id=match_ids[0], series_id=series_ids[0], name="match 1", meta={}, timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], team_match_results=None, player_results=None),
    Match(match_id=match_ids[1], series_id=series_ids[1], name="match 2", meta={"jim": "jones"}, timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], team_match_results=None, player_results=None),
    Match(match_id=match_ids[2], series_id=series_ids[0], name="match 3", meta={},
          timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], team_match_results=None,
          player_results=None),
    Match(match_id=match_ids[3], series_id=series_ids[1], name="match 4", meta={"jim": "jones"},
          timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], team_match_results=None,
          player_results=None)
]

EXAMPLE_TEAMS = [
    Team(team_id=team_ids[0], meta={}, names=[
        TeamName(team_id=None, name="EG", timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
        TeamName(team_id=None, name="EvilGeniuses", timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
    ]),
    Team(team_id=team_ids[1], meta={}, names=[
        TeamName(team_id=None, name="OG", timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
        TeamName(team_id=None, name="Monkey Business",
                 timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
    ]),
    Team(team_id=team_ids[2], meta={}, names=[
        TeamName(team_id=None, name="Team Liquid", timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
        TeamName(team_id=None, name="Other team",
                 timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
    ]),
    Team(team_id=team_ids[3], meta={}, names=[
        TeamName(team_id=None, name="VP", timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
        TeamName(team_id=None, name="Virtus Pro",
                 timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
    ])
]

EXAMPLE_PLAYERS = [
    Player(
        player_id=player_ids[0], meta={}, names=[
            PlayerName(player_id=None, name="Notail", timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerName(player_id=None, name="BigDaddy", timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ],
        positions=[
            PlayerPosition(player_id=None, name="Carry", timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerPosition(player_id=None, name="Support", timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ]
    ),
    Player(
        player_id=player_ids[1], meta={}, names=[
            PlayerName(player_id=None, name="Support",
                       timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerName(player_id=None, name="Carry",
                       timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ],
        positions=[
            PlayerPosition(player_id=None, name="Carry",
                           timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerPosition(player_id=None, name="Support",
                           timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ]
    ),
    Player(
        player_id=player_ids[2], meta={}, names=[
            PlayerName(player_id=None, name="Player 3",
                       timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerName(player_id=None, name="Player 3.3",
                       timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ],
        positions=[
            PlayerPosition(player_id=None, name="Offlane",
                           timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerPosition(player_id=None, name="Carry",
                           timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ]
    ),
    Player(
        player_id=player_ids[3], meta={}, names=[
            PlayerName(player_id=None, name="Player 4",
                       timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerName(player_id=None, name="Player 4.4",
                       timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ],
        positions=[
            PlayerPosition(player_id=None, name="Carry",
                           timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerPosition(player_id=None, name="Offlane",
                           timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ]
    ),
    Player(
        player_id=player_ids[4], meta={}, names=[
            PlayerName(player_id=None, name="Player 5",
                       timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerName(player_id=None, name="BigDaddy",
                       timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ],
        positions=[
            PlayerPosition(player_id=None, name="Offlane",
                           timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerPosition(player_id=None, name="Carry",
                           timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ]
    ),
    Player(
        player_id=player_ids[5], meta={}, names=[
            PlayerName(player_id=None, name="Player 6",
                       timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerName(player_id=None, name="Player 6.6",
                       timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ],
        positions=[
            PlayerPosition(player_id=None, name="Support",
                           timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
            PlayerPosition(player_id=None, name="Carry",
                           timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
        ]
    ),
]

EXAMPLE_TEAM_PLAYERS = [
    TeamPlayer(team_id=team_ids[0], player_id=player_ids[0], timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
    TeamPlayer(team_id=team_ids[0], player_id=player_ids[0], timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
    TeamPlayer(team_id=team_ids[0], player_id=player_ids[1], timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
    TeamPlayer(team_id=team_ids[0], player_id=player_ids[1], timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
    TeamPlayer(team_id=team_ids[1], player_id=player_ids[2], timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
    TeamPlayer(team_id=team_ids[2], player_id=player_ids[3], timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
    TeamPlayer(team_id=team_ids[2], player_id=player_ids[4], timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
    TeamPlayer(team_id=team_ids[3], player_id=player_ids[5], timespan=["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]),
    TeamPlayer(team_id=team_ids[3], player_id=player_ids[5], timespan=["2019-08-16T17:41:18+00:00", "2020-08-16T17:41:18+00:00"]),
]