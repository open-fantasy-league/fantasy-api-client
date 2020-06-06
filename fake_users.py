import asyncio
import json
import random
import uuid

from clients.fantasy_websocket_client import FantasyWebsocketClient
from messages.fantasy_msgs import ExternalUser, FantasyTeam, DraftQueue
from data.dota_ids import FANTASY_LEAGUE_ID


async def add_fake_users(fantasy_client=None):
    if fantasy_client is None:
        fantasy_client = FantasyWebsocketClient('0.0.0.0', 3003)
        asyncio.create_task(fantasy_client.run())
    users = []
    teams = []
    draft_queues = []
    with open("data/players.json") as f:
        dota_teams = json.load(f)
    for i in range(35):
        user = ExternalUser(uuid.uuid4(), f"tpain{i}", meta={'discord_id': f'blahblah{i}'})
        team = FantasyTeam(uuid.uuid4(), user.external_user_id, FANTASY_LEAGUE_ID, f'tpain{i}_team', meta={'discord_id': f'blahblah{i}'})
        users.append(user)
        teams.append(team)
        players = [random.choice([p for t in dota_teams for p in t["players"]])["fantasy_id"] for _ in range(12)]
        draft_queues.append(DraftQueue(team.fantasy_team_id, players))
    await fantasy_client.send_insert_users(users)
    await fantasy_client.send_insert_fantasy_teams(teams)
    await fantasy_client.send_insert_draft_queues(draft_queues)


if __name__ == "__main__":
    asyncio.run(add_fake_users())
