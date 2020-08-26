import asyncio
import time

from twino_client import TwinoClient
from twino_message import TwinoMessage

client: TwinoClient = TwinoClient()


def rec(msg: TwinoMessage) -> None:
    print('received')
    print(msg.get_content())
    client.ack(msg)


def rec_all(msg: TwinoMessage) -> None:
    print('all_received')
    print(msg.get_content())

async def main():
    client.message_received = rec_all
    connected = client.connect("tmqs://echo.websocket.org:443")
    print(connected)
    input()
    await client.on("model-a", 1001, rec)


asyncio.run(main())
input()
