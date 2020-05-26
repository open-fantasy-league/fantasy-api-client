from clients.websocket_client import WebsocketClient
from messages.result_msgs import *


class ResultWebsocketClient(WebsocketClient):

    async def send_sub_competitions(self, data: SubCompetition):
        await self.send("SubCompetition", data)

    async def send_sub_teams(self, data: SubTeam):
        await self.send("SubTeam", data)

    async def send_insert_competitions(self, data: List[Competition]):
        await self.send("Competition", data)

    async def send_update_competitions(self, competitions: List[Competition]):
        # This is because being flexible with inserts, letting people insert the whole hierarchy,
        # yet updates are more limited, have to do a separate call to update each level
        assert all(c.series is None for c in competitions)
        await self.send("Competition", competitions)

    async def send_insert_series(self, data: List[Series]):
        await self.send("Series", data)

    async def send_insert_matches(self, data: List[Match]):
        await self.send("Match", data)

    async def send_insert_team_series_results(self, data: List[TeamSeriesResult]):
        await self.send("TeamSeriesResult", data)

    async def send_insert_team_match_results(self, data: List[TeamMatchResult]):
        await self.send("TeamSeriesResult", data)

    async def send_insert_player_results(self, data: List[PlayerResult]):
        await self.send("PlayerResult", data)

    async def send_insert_teams(self, data: List[Team]):
        await self.send("Team", data)

    async def send_insert_players(self, data: List[Player]):
        await self.send("Player", data)

    async def send_insert_team_players(self, data: List[TeamPlayer]):
        await self.send("TeamPlayer", data)
