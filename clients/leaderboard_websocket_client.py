from clients.websocket_client import WebsocketClient
from messages.leaderboard_msgs import *


class LeaderboardWebsocketClient(WebsocketClient):

    async def send_sub_leaderboards(self, data: SubLeaderboard):
        await self.send("SubLeaderboard", data)

    async def send_sub_leagues(self, data: SubLeague):
        await self.send("SubLeague", data)

    async def send_insert_leaderboard(self, data: List[Leaderboard]):
        await self.send("Competition", data)

    async def send_update_competitions(self, data: List[Leaderboard]):
        # Really the timespan, meta etc are optional and can be left out to not update
        await self.send("Leaderboard", data)

    async def send_insert_stat(self, data: List[Stat]):
        await self.send("Stat", data)


