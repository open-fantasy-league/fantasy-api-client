from clients.websocket_client import WebsocketClient
from messages.fantasy_msgs import *


class FantasyWebsocketClient(WebsocketClient):

    async def send_sub_users(self, data: SubUser):
        await self.send("SubUser", data)

    async def send_sub_leagues(self, data: SubLeague):
        await self.send("SubLeague", data)

    async def send_sub_drafts(self, data: SubDraft):
        await self.send("SubDraft", data)

    async def send_insert_leagues(self, data: List[League]):
        await self.send("League", data)

    async def send_insert_periods(self, data: List[Period]):
        await self.send("Period", data)

    async def send_insert_stat_multipliers(self, data: List[StatMultiplier]):
        await self.send("StatMultiplier", data)

    async def send_insert_users(self, data: List[ExternalUser]):
        await self.send("ExternalUser", data)

    async def send_insert_fantasy_teams(self, data: List[FantasyTeam]):
        await self.send("FantasyTeam", data)

    async def send_insert_draft_queues(self, data: List[DraftQueue]):
        await self.send("DraftQueue", data)

    async def send_update_draft_choices(self, data: List[DraftChoice]):
        await self.send("DraftChoice", data)

    async def send_insert_pick(self, data: List[Pick]):
        await self.send("Pick", data)

    async def send_insert_active_pick(self, data: List[ActivePick]):
        await self.send("ActivePick", data)
