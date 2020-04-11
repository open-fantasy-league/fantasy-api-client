import asyncio
import websockets

async def test():

    async with websockets.connect('ws://127.0.0.1:3030/echo') as websocket:
        
        while True:
            await websocket.send("hello")
            response = await websocket.recv()
            print(response)
            await asyncio.sleep(2)

asyncio.run(test())
