import asyncio
import logging
from collections import defaultdict

import websockets
import json
import uuid

from utils.constants import TRUNCATED_MESSAGE_LENGTH
from utils.errors import ApiException
from utils.utils import Encoder

logger = logging.getLogger(__name__)


class WebsocketClient:

    def __init__(self, addr, port):
        logger.info(f"Websocket client for {addr}:{port}")
        self.addr = addr
        self.port = port
        self.websocket = None
        # TODO clear this out so doesnt infinitely grow in size
        self.resps = defaultdict(dict)
        self.resp_events = {}
        self.sub_events = asyncio.Queue()
        self.initialized = asyncio.Event()

    async def send(self, method, data, message_id=None):
        await self.initialized.wait()
        #Could use an 'event' or something to handle this better
        # for i in range(5):
        #     if self.websocket is not None:
        #         break
        #     await asyncio.sleep(0.5)
        # if self.websocket is None:
        #     raise Exception("Websocket still None after 5 attempts")

        message_id = message_id or str(uuid.uuid4())
        logger.info("Sending {} ({})".format(method, message_id))
        logger.debug("Sending {} ({}):\n {}\n".format(method, message_id, data))
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
            logger.error(resp)
            raise ApiException(resp)
        return self.resps[message_id]

    async def listener(self):
        while True:
            try:
                # @JK is it possible to let the bot catch this exception to handle
                # when server goes down? (if thats even worthile anyway...)
                response = await self.websocket.recv()
                # maybe not such a smart change, cos if actually want to see this stuff
                # setting logger to debug gives a load of other shit too...
                resp = json.loads(response)
                # logger.info(f'{resp["message_type"]} received - {response[:TRUNCATED_MESSAGE_LENGTH]}...') #  KeyError: 'message_type'
                logger.info(f'RESPONSE received - {resp["mode"]} - {resp["message_type"]}')
                logger.debug("RESPONSE: {}\n".format(response))
                if resp['mode'] in ('resp', 'error'):
                    self.resps[resp['message_id']] = resp
                    self.resp_events[resp['message_id']].set()
                elif resp['mode'] == 'push':
                    await self.sub_events.put(resp)
                await asyncio.sleep(0)
            except Exception:
                logger.exception("Error in websocket listener")
                raise

    async def run(self):
        async with websockets.connect('ws://{}:{}/echo'.format(self.addr, self.port), ping_interval=60) as websocket:
            logger.info('Websocket connected ws://{}:{}/echo'.format(self.addr, self.port))
            self.websocket = websocket
            self.initialized.set()
            await self.listener()
        logger.info('Disconnected websocket ws://{}:{}/echo'.format(self.addr, self.port))
