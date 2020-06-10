import datetime
import asyncio
import json
import random
import uuid

from clients.leaderboard_websocket_client import LeaderboardWebsocketClient
from data.dota_ids import FANTASY_LEAGUE_ID, FANTASY_USER_LEADERBOARD_ID, FANTASY_PLAYER_LEADERBOARD_ID
from messages.leaderboard_msgs import Stat
from utils.constants import DATE_FMT

import os
import dotenv

dotenv.load_dotenv()


async def add_fake_leaderboards(user_ids, leaderboard_client=None):
    if leaderboard_client is None:
        leaderboard_client = LeaderboardWebsocketClient(os.getenv('ADDRESS', '0.0.0.0'), 3002)
        asyncio.create_task(leaderboard_client.run())
    stats = []
    for user_id in user_ids:
        stats.append(Stat(
            FANTASY_USER_LEADERBOARD_ID,
            user_id,
            datetime.datetime.now(tz=datetime.timezone.utc).strftime(DATE_FMT),
            random.random() * 250.
        ))
    with open("data/players.json") as f:
        dota_teams = json.load(f)
        player_ids = [p["fantasy_id"] for t in dota_teams for p in t["players"]]
        for player_id in player_ids:
            stats.append(Stat(
                FANTASY_PLAYER_LEADERBOARD_ID,
                player_id,
                datetime.datetime.now(tz=datetime.timezone.utc).strftime(DATE_FMT),
                random.random() * 250.
            ))
    await leaderboard_client.send_insert_stats(stats)


if __name__ == "__main__":
    asyncio.run(add_fake_leaderboards([]))
