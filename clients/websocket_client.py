import asyncio

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