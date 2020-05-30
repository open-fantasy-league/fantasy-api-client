import asyncio
import uuid

from clients.fantasy_websocket_client import FantasyWebsocketClient
from messages.fantasy_msgs import ExternalUser, FantasyTeam
from data.dota_ids import FANTASY_LEAGUE_ID


async def add_fake_users():
    fantasy_client = FantasyWebsocketClient('0.0.0.0', 3003)
    asyncio.create_task(fantasy_client.run())
    users = []
    teams = []
    for i in range(35):
        user = ExternalUser(uuid.uuid4(), f"tpain{i}")
        team = FantasyTeam(uuid.uuid4(), user.external_user_id, FANTASY_LEAGUE_ID, f'tpain{i}_team')
        users.append(user)
        teams.append(team)
    await fantasy_client.send_insert_users(users)
    await fantasy_client.send_insert_fantasy_teams(teams)


if __name__ == "__main__":
    asyncio.run(add_fake_users())
