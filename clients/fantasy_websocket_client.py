from clients.websocket_client import WebsocketClient
from messages.fantasy_msgs import *


class FantasyWebsocketClient(WebsocketClient):

    def __init__(self, addr='0.0.0.0', port=3003):
        super().__init__(addr, port)

    async def send_sub_users(self, data: SubUser):
        return await self.send_and_get_resp("SubUser", data)

    async def send_sub_leagues(self, data: SubLeague):
        return await self.send_and_get_resp("SubLeague", data)

    async def send_sub_drafts(self, data: SubDraft):
        return await self.send_and_get_resp("SubDraft", data)

    async def send_insert_leagues(self, data: List[League]):
        return await self.send_and_get_resp("League", data)

    async def send_insert_periods(self, data: List[Period]):
        return await self.send_and_get_resp("Period", data)

    async def send_update_periods(self, data: List[PeriodUpdate]):
        return await self.send_and_get_resp("PeriodUpdate", data)

    async def send_insert_stat_multipliers(self, data: List[StatMultiplier]):
        return await self.send_and_get_resp("StatMultiplier", data)

    async def send_insert_max_players_per_position(self, data: List[MaxPlayersPerPosition]):
        return await self.send_and_get_resp("MaxPlayersPerPosition", data)

    async def send_insert_users(self, data: List[ExternalUser]):
        return await self.send_and_get_resp("ExternalUser", data)

    async def send_insert_fantasy_teams(self, data: List[FantasyTeam]):
        return await self.send_and_get_resp("FantasyTeam", data)

    async def send_insert_draft_queues(self, data: List[DraftQueue]):
        return await self.send_and_get_resp("DraftQueue", data)

    async def send_update_draft_choices(self, data: List[DraftChoice]):
        return await self.send_and_get_resp("DraftChoice", data)

    async def send_insert_picks(self, data: List[Pick]):
        return await self.send_and_get_resp("Pick", data)

    async def send_insert_draft_pick(self, data: DraftPick):
        return await self.send_and_get_resp("DraftPick", data)

    async def send_insert_active_picks(self, data: List[ActivePick]):
        return await self.send_and_get_resp("ActivePick", data)

    async def send_insert_valid_players(self, data: List[ValidPlayer]):
        return await self.send_and_get_resp("ValidPlayer", data)
