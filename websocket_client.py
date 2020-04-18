import asyncio
import websockets
import json
import uuid
import sys

existing_uuid = ['a67dd7fa-2ccf-4d31-b42c-365d59af3066', '78206abb-6658-4ded-a2bc-e19c99644e51']

async def test():

    async with websockets.connect('ws://127.0.0.1:3030/echo') as websocket:
        
        async def sender():
            while True:
                msg = {
                    "message_id": str(uuid.uuid4()),
                    "method": "upsert_competitions",
                    "data": [{"competition_id": existing_uuid[0], "name": sys.argv[1], "meta": {}, "timespan": ["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]}, 
                    {"competition_id": str(uuid.uuid4()), "name": "woof", "meta": {},"timespan": ["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]}
                    ]
                }
                #await websocket.send("hello")
                await websocket.send(json.dumps(msg))
                await asyncio.sleep(5)

        async def listener():
            while True:
                response = await websocket.recv()
                print(response)
                print("\n\n")
                await asyncio.sleep(0.0)
        t1 = asyncio.create_task(sender())
        t2 = asyncio.create_task(listener())
        await t1
        await t2
        await asyncio.sleep(10000)

asyncio.run(test())
