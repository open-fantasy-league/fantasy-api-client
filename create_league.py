import asyncio
import datetime
import json
import random
import uuid
from pprint import pprint
from typing import List

from clients.fantasy_websocket_client import FantasyWebsocketClient
from clients.leaderboard_websocket_client import LeaderboardWebsocketClient
from clients.result_websocket_client import ResultWebsocketClient
from fake_users import add_fake_users
from messages.fantasy_msgs import League, StatMultiplier, Period, ValidPlayer, MaxPlayersPerPosition
from messages.leaderboard_msgs import Leaderboard
from messages.result_msgs import Competition, Team, TeamName, Player, PlayerName, PlayerPosition, TeamPlayer
from utils.constants import DATE_FMT
from data.dota_ids import FANTASY_PLAYER_LEADERBOARD_ID, FANTASY_LEAGUE_ID, FANTASY_USER_LEADERBOARD_ID, \
    FANTASY_COMPETITION_ID, TEAM_NAMES_TO_IDS


import os
import dotenv

dotenv.load_dotenv()
ADDRESS = os.getenv('ADDRESS', '0.0.0.0')

async def create_league(
        league_id: int, name: str,
        period_starts: List[datetime.datetime],
        draft_start_before_period: datetime.timedelta = datetime.timedelta(hours=1),
        draft_lockdown_before_period: datetime.timedelta = datetime.timedelta(hours=3),
        fake_users: bool =False
):
    result_client = ResultWebsocketClient(ADDRESS, 3001)
    asyncio.create_task(result_client.run())
    fantasy_client = FantasyWebsocketClient(ADDRESS, 3003)
    asyncio.create_task(fantasy_client.run())
    leaderboard_client = LeaderboardWebsocketClient(ADDRESS, 3002)
    asyncio.create_task(leaderboard_client.run())

    start_time = datetime.datetime(2020, 5, 10, tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime(2020, 6, 10, tzinfo=datetime.timezone.utc)
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
        Competition(FANTASY_COMPETITION_ID, name,  (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
                    meta={"valve_id": league_id})
    ])
    await fantasy_client.send_insert_leagues([
        League(FANTASY_LEAGUE_ID, name, FANTASY_COMPETITION_ID, 5, 5, 2, 3, 2, 3)
    ])

    if fake_users:
        await add_fake_users(fantasy_client)

    await fantasy_client.send_insert_stat_multipliers([
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
        StatMultiplier('roshans', 1.0, league_id=FANTASY_LEAGUE_ID),
    ])

    await fantasy_client.send_insert_max_players_per_position([
        MaxPlayersPerPosition('support', 2, 2, league_id=FANTASY_LEAGUE_ID),
        MaxPlayersPerPosition('core', 2, 2, league_id=FANTASY_LEAGUE_ID),
        MaxPlayersPerPosition('offlane', 1, 1, league_id=FANTASY_LEAGUE_ID),

    ])

    now = datetime.datetime.now(datetime.timezone.utc)
    period_inserts = []
    for i, p in enumerate(period_starts):
        final_period = False
        try:
            next_period = period_starts[i+1]
        except IndexError:
            next_period = p + datetime.timedelta(days=1)
            final_period = True

        # equal to number of teams playing on that day
        users_per_draft = 3 if final_period else 4
        period_inserts.append(Period(
            uuid.uuid4(), 'Day {}'.format(i+1), (p.strftime(DATE_FMT), next_period.strftime(DATE_FMT)),
            2.0 if final_period else 1.0, users_per_draft, 20, (p - draft_start_before_period).strftime(DATE_FMT),
            (now - draft_lockdown_before_period).strftime(DATE_FMT), league_id=FANTASY_LEAGUE_ID
        ))
    await fantasy_client.send_insert_periods(period_inserts)

    with open("data/players.json") as f:
        teams = json.load(f)
    pprint([Team(
        t["fantasy_id"],
        meta={"dota_id": TEAM_NAMES_TO_IDS[t["name"]]},
        names=[TeamName(t["name"], (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)))]
    ) for t in teams])
    await result_client.send_insert_teams([Team(
        t["fantasy_id"],
        meta={"dota_id": TEAM_NAMES_TO_IDS[t["name"]]},
        names=[TeamName(t["name"], (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)), team_id=t["fantasy_id"])]
    ) for t in teams])

    await result_client.send_insert_players([Player(
        p["fantasy_id"],
        meta={"dota_id": p["account_id"]},
        names=[PlayerName(p["name"], (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)))],
        positions=[PlayerPosition(p["position"], (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)))]
    ) for t in teams for p in t["players"]])

    await result_client.send_insert_team_players([TeamPlayer(
        t["fantasy_id"],
        (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
        p["fantasy_id"],
    ) for t in teams for p in t["players"]])

    valid_players = [ValidPlayer(player_id=p["fantasy_id"], period_id=period.period_id) for t in teams for p in t["players"] for period in period_inserts]
    await fantasy_client.send_insert_valid_players(valid_players)


if __name__ == "__main__":
    period_starts = [
        datetime.datetime(2020, 6, 9, hour=14, tzinfo=datetime.timezone.utc),
        datetime.datetime(2020, 6, 10, hour=14, tzinfo=datetime.timezone.utc),
        datetime.datetime(2020, 6, 11, hour=14, tzinfo=datetime.timezone.utc),
        datetime.datetime(2020, 6, 12, hour=14, tzinfo=datetime.timezone.utc),
        datetime.datetime(2020, 6, 13, hour=12, tzinfo=datetime.timezone.utc),
    ]
    asyncio.run(create_league(
        # 12027, 'ESL Birmingham',
        11979, 'Blast Bounty Hunt',
        period_starts, draft_lockdown_before_period=datetime.timedelta(hours=3),
        #period_starts, draft_lockdown_before_period=datetime.timedelta(hours=9001),
        draft_start_before_period=datetime.timedelta(hours=1), fake_users=True
    ))
