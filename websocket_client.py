import asyncio
import websockets


async def hello():
    uri = "ws://127.0.0.1:65432"
    async with websockets.connect(uri) as websocket:
        command = input("Command: ")

        await websocket.send(command)
        result = await websocket.recv()
        print(result)


asyncio.get_event_loop().run_until_complete(hello())