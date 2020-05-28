import asyncio
import datetime
import json
import uuid

from clients.fantasy_websocket_client import FantasyWebsocketClient
from clients.leaderboard_websocket_client import LeaderboardWebsocketClient
from clients.result_websocket_client import ResultWebsocketClient
from messages.fantasy_msgs import League, StatMultiplier, Period
from messages.leaderboard_msgs import Leaderboard
from messages.result_msgs import Competition, Team, TeamName, Player, PlayerName, PlayerPosition, TeamPlayer
from utils.constants import DATE_FMT
from data.dota_ids import FANTASY_PLAYER_LEADERBOARD_ID, FANTASY_LEAGUE_ID, FANTASY_USER_LEADERBOARD_ID, \
    FANTASY_COMPETITION_ID, DOTA_TEAM_IDS_TO_FANTASY, TEAM_NAMES_TO_IDS


async def create_league(league_id, name):
    result_client = ResultWebsocketClient('0.0.0.0', 3001)
    result_client_fut = result_client.run()
    fantasy_client = FantasyWebsocketClient('0.0.0.0', 3003)
    fantasy_client_fut = result_client.run()
    leaderboard_client = LeaderboardWebsocketClient('0.0.0.0', 3002)
    leaderboard_client_fut = result_client.run()

    start_time = datetime.datetime(2020, 5, 10)
    end_time = datetime.datetime(2020, 6, 10)
    await leaderboard_client.send_insert_leaderboard([
        Leaderboard(
            FANTASY_PLAYER_LEADERBOARD_ID, FANTASY_LEAGUE_ID, "ESL Birmingham Player Points",
            (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT))
        ),
        Leaderboard(
            FANTASY_USER_LEADERBOARD_ID, FANTASY_LEAGUE_ID,  "ESL Birmingham User Points",
            (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT))
        ),
    ])
    await result_client.send_insert_competitions([
        Competition(FANTASY_COMPETITION_ID, "ESL Birmingham",  (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
                    meta={"valve_id": league_id})
    ])
    await fantasy_client.send_insert_leagues([
        League(FANTASY_LEAGUE_ID, "ESL Birmingham", FANTASY_COMPETITION_ID, 5, 5, 2, 3)
    ])

    await fantasy_client.send_insert_stat_multipliers([
        StatMultiplier('kills', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('assists', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('deaths', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('last hits', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('denies', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('first blood', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('stun', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('teamfight participation', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('GPM', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('towers', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('observer wards', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('dewards', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('camps stacked', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('runes', 1.0, league_id=FANTASY_LEAGUE_ID),
        StatMultiplier('roshans', 1.0, league_id=FANTASY_LEAGUE_ID),
    ])

    now = datetime.datetime.now(datetime.timezone.utc)
    await fantasy_client.send_insert_periods([
        Period(
            uuid.uuid4(), 'Day 1', (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
            1.0, 8, 20, (now + datetime.timedelta(minutes=2)).strftime(DATE_FMT),
            (now + datetime.timedelta(minutes=1)).strftime(DATE_FMT), league_id=FANTASY_LEAGUE_ID
        ),
        Period(
            uuid.uuid4(), 'Day 2', (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
            1.0, 4, 20, (now + datetime.timedelta(minutes=4)).strftime(DATE_FMT),
            (now + datetime.timedelta(minutes=3)).strftime(DATE_FMT), league_id=FANTASY_LEAGUE_ID
        ),
        Period(
            uuid.uuid4(), 'Day 3', (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
            1.0, 4, 20, (now + datetime.timedelta(minutes=6)).strftime(DATE_FMT),
            (now + datetime.timedelta(minutes=5)).strftime(DATE_FMT), league_id=FANTASY_LEAGUE_ID
        ),
        Period(
            uuid.uuid4(), 'Day 4', (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
            1.0, 2, 20, (now + datetime.timedelta(minutes=8)).strftime(DATE_FMT),
            (now + datetime.timedelta(minutes=7)).strftime(DATE_FMT), league_id=FANTASY_LEAGUE_ID
        ),
        Period(
            uuid.uuid4(), 'Day 5', (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
            2.0, 2, 20, (now + datetime.timedelta(minutes=10)).strftime(DATE_FMT),
            (now + datetime.timedelta(minutes=9)).strftime(DATE_FMT), league_id=FANTASY_LEAGUE_ID
        ),
    ])

    with open("data/players.json") as f:
        teams = json.load(f)
    await result_client.send_insert_teams([Team(
        t["fantasy_id"],
        meta={"dota_id": TEAM_NAMES_TO_IDS[t["name"]]},
        names=[TeamName(t["name"], (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)))]
    ) for t in teams])

    await result_client.send_insert_players([Player(
        p["fantasy_id"],
        meta={"dota_id": p["account_id"]},
        names=[PlayerName(p["name"], (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)))],
        positions=[PlayerPosition(p["position"], (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)))]
    ) for t in teams for p in t["players"]])

    await result_client.send_insert_team_players([TeamPlayer(
        DOTA_TEAM_IDS_TO_FANTASY[TEAM_NAMES_TO_IDS[t["name"]]],
        (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
        p["fantasy_id"],
    ) for t in teams for p in t["players"]])

    await fantasy_client.send_insert_valid_players([p["fantasy_id"] for t in teams for p in t["players"]])


if __name__ == "__main__":
    asyncio.run(create_league(12027, 'ESL Birmingham'))
