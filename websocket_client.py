import asyncio
from typing import List
from messages.result_msgs import Competition, Series, Match, TeamPlayer, Player

import websockets
import json
import uuid


class WebsocketClient:

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.websocket = None

    async def send(self, method, data, message_id=None):
        # Could use an 'event' or something to handle this better
        for i in range(5):
            if self.websocket is not None:
                break
            await asyncio.sleep(0.5)
        if self.websocket is None:
            raise Exception("Websocket still None after 5 attempts")

        print("Sending {}:\n {}\n\n".format(method, data))
        msg = {
            "message_id": message_id or str(uuid.uuid4()),
            "method": method,
            "data": data
        }
        await self.websocket.send(json.dumps(msg))
        await asyncio.sleep(0)

    async def listener(self):
        while True:
            response = await self.websocket.recv()
            print("RESPONSE: {}\n".format(response))
            await asyncio.sleep(0)

    async def run(self):
        async with websockets.connect('ws://{}:{}/echo'.format(self.addr, self.port)) as websocket:
            self.websocket = websocket
            await self.listener()


class ResultWebsocketClient(WebsocketClient):

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

    async def send_insert_teams(self, data: List[Match]):
        await self.send("Team", data)

    async def send_insert_players(self, data: List[Player]):
        await self.send("Player", data)

    async def send_insert_team_players(self, data: List[TeamPlayer]):
        await self.send("TeamPlayer", data)
