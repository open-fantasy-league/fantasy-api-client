from clients.websocket_client import WebsocketClient
from messages.result_msgs import *


class ResultWebsocketClient(WebsocketClient):

    async def send_sub_competitions(self, data: SubCompetition):
        return await self.send_and_get_resp("SubCompetition", data)

    async def send_sub_teams(self, data: SubTeam):
        return await self.send_and_get_resp("SubTeam", data)

    async def send_insert_competitions(self, data: List[Competition]):
        return await self.send_and_get_resp("Competition", data)

    async def send_update_competitions(self, competitions: List[Competition]):
        # This is because being flexible with inserts, letting people insert the whole hierarchy,
        # yet updates are more limited, have to do a separate call to update each level
        assert all(c.series is None for c in competitions)
        return await self.send_and_get_resp("Competition", competitions)

    async def send_insert_series(self, data: List[Series]):
        return await self.send_and_get_resp("Series", data)

    async def send_insert_matches(self, data: List[Match]):
        return await self.send_and_get_resp("Match", data)

    async def send_insert_team_series_results(self, data: List[TeamSeriesResult]):
        return await self.send_and_get_resp("TeamSeriesResult", data)

    async def send_insert_team_match_results(self, data: List[TeamMatchResult]):
        return await self.send_and_get_resp("TeamSeriesResult", data)

    async def send_insert_player_results(self, data: List[PlayerResult]):
        return await self.send_and_get_resp("PlayerResult", data)

    async def send_insert_teams(self, data: List[Team]):
        return await self.send_and_get_resp("Team", data)

    async def send_insert_players(self, data: List[Player]):
        return await self.send_and_get_resp("Player", data)

    async def send_insert_team_players(self, data: List[TeamPlayer]):
        return await self.send_and_get_resp("TeamPlayer", data)
