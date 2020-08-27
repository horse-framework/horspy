import asyncio
import time

from twino_client import TwinoClient
from twino_message import TwinoMessage


def rec_all(msg: TwinoMessage) -> None:
    print('all_received')
    print(msg.get_content())

client: TwinoClient = TwinoClient()

def receive_event(msg: TwinoMessage) -> None:
    print('received')
    print(msg.get_content())
    client.ack(msg)

async def main():
    client.connect("tmq://127.0.0.1:22200")
    await client.on("model-a", 1001, receive_event)

asyncio.run(main())
