import asyncio

from twino_client import TwinoClient


async def main():
    client = TwinoClient()
    connected = client.connect("tmq://127.0.0.1:22200")
    print(connected)
    input()
    result = await client.push_queue("model-b", 200, "Hello, World!", True)
    print(result.code)
    print(result.reason)


asyncio.run(main())
input()