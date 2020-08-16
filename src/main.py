from twino_client import TwinoClient

client = TwinoClient()
connected = client.connect("tmq://127.0.0.1:22200")
print(connected)
input()
