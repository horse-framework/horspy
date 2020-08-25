import asyncio
import time

from twino_client import TwinoClient
from twino_message import TwinoMessage

client: TwinoClient = TwinoClient()


def rec(msg: TwinoMessage) -> None:
    print('received')
    print(msg.get_content())
    client.ack(msg)


async def main():
    connected = client.connect("tmq://127.0.0.1:22200")
    print(connected)
    input()
    await client.on("model-a", 1001, rec)


asyncio.run(main())
input()
