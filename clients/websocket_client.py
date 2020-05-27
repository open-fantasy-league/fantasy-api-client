import asyncio
from collections import defaultdict

import websockets
import json
import uuid


class WebsocketClient:

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.websocket = None
        # TODO clear this out so doesnt infinitely grow in size
        self.resps = defaultdict(dict)
        self.resp_events = {}

    async def send(self, method, data, message_id=None):
        # Could use an 'event' or something to handle this better
        for i in range(5):
            if self.websocket is not None:
                break
            await asyncio.sleep(0.5)
        if self.websocket is None:
            raise Exception("Websocket still None after 5 attempts")

        message_id = message_id or str(uuid.uuid4())
        print("Sending {} ({}):\n {}\n\n".format(method, message_id, data))
        msg = {
            "message_id": message_id,
            "method": method,
            "data": data
        }
        resp_event = asyncio.Event()
        self.resp_events[message_id] = resp_event
        await self.websocket.send(json.dumps(msg))
        await asyncio.sleep(0)
        return resp_event

    async def send_and_get_resp(self, method, data, message_id=None):
        message_id = message_id or str(uuid.uuid4())
        resp_event = await self.send(method, data, message_id)
        await resp_event.wait()
        return self.resps[message_id]

    async def listener(self):
        while True:
            response = await self.websocket.recv()
            print("RESPONSE: {}\n".format(response))
            resp = json.loads(response)
            self.resps[resp['message_id']] = resp
            self.resp_events[resp['message_id']].set()
            await asyncio.sleep(0)

    async def run(self):
        async with websockets.connect('ws://{}:{}/echo'.format(self.addr, self.port)) as websocket:
            self.websocket = websocket
            await self.listener()
