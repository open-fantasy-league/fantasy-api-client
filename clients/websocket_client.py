import asyncio
from collections import defaultdict
from pprint import pprint

import websockets
import json
import uuid

from utils.errors import ApiException
from utils.utils import Encoder


class WebsocketClient:

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.websocket = None
        # TODO clear this out so doesnt infinitely grow in size
        self.resps = defaultdict(dict)
        self.resp_events = {}
        self.sub_events = asyncio.Queue()

    async def send(self, method, data, message_id=None):
        # Could use an 'event' or something to handle this better
        for i in range(5):
            if self.websocket is not None:
                break
            await asyncio.sleep(0.5)
        if self.websocket is None:
            raise Exception("Websocket still None after 5 attempts")

        message_id = message_id or str(uuid.uuid4())
        print("Sending {} ({}):\n {}\n".format(method, message_id, data))
        msg = {
            "message_id": message_id,
            "method": method,
            "data": data
        }
        resp_event = asyncio.Event()
        self.resp_events[message_id] = resp_event
        await self.websocket.send(json.dumps(msg, cls=Encoder))
        await asyncio.sleep(0)
        return resp_event

    async def send_and_get_resp(self, method, data, message_id=None):
        message_id = message_id or str(uuid.uuid4())
        resp_event = await self.send(method, data, message_id)
        await resp_event.wait()
        resp = self.resps[message_id]
        if resp["mode"] == "error":
            raise ApiException(resp)
        return self.resps[message_id]

    async def listener(self):
        while True:
            response = await self.websocket.recv()
            print("RESPONSE: {}\n".format(response))
            resp = json.loads(response)
            if resp['mode'] in ('resp', 'error'):
                self.resps[resp['message_id']] = resp
                self.resp_events[resp['message_id']].set()
            elif resp['mode'] == 'push':
                await self.sub_events.put(resp)
            await asyncio.sleep(0)

    async def run(self):
        async with websockets.connect('ws://{}:{}/echo'.format(self.addr, self.port)) as websocket:
            self.websocket = websocket
            await self.listener()
