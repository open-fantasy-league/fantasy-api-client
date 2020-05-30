from clients.websocket_client import WebsocketClient
from messages.leaderboard_msgs import *


class LeaderboardWebsocketClient(WebsocketClient):

    async def send_sub_leaderboards(self, data: SubLeaderboard):
        return await self.send_and_get_resp("SubLeaderboard", data)

    async def send_sub_leagues(self, data: SubLeague):
        return await self.send_and_get_resp("SubLeague", data)

    async def send_insert_leaderboard(self, data: List[Leaderboard]):
        return await self.send_and_get_resp("Leaderboard", data)

    # async def send_update_competitions(self, data: List[Leaderboard]):
    #     # Really the timespan, meta etc are optional and can be left out to not update
    #     return await self.send_and_get_resp("Leaderboard", data)

    async def send_insert_stat(self, data: List[Stat]):
        return await self.send_and_get_resp("Stat", data)

    async def send_get_latest_leaderboards(self, data: List[uuid.UUID]):
        return await self.send_and_get_resp("LeaderboardGet", data)



