import asyncio

import nats
from nats.errors import ConnectionClosedError, NoServersError, TimeoutError


class NatsBus:
    def __init__(self, server_url="nats://localhost:4222"):
        self.server_url = server_url
        self.nc = None

    async def connect(self):
        try:
            self.nc = await nats.connect(self.server_url)
            print(f"Connected to NATS at {self.server_url}")
        except NoServersError as e:
            print(f"Could not connect to any NATS server: {e}")
        except Exception as e:
            print(f"Error connecting to NATS: {e}")

    async def disconnect(self):
        if self.nc:
            await self.nc.close()
            print("Disconnected from NATS")

    async def publish(self, subject, message):
        if not self.nc:
            await self.connect()
        if self.nc:
            try:
                await self.nc.publish(subject, message.encode('utf-8'))
                print(f"Published message to '{subject}'")
            except Exception as e:
                print(f"Error publishing message: {e}")

    async def subscribe(self, subject, callback):
        if not self.nc:
            await self.connect()
        if self.nc:
            try:
                await self.nc.subscribe(subject, cb=callback)
                print(f"Subscribed to '{subject}'")
            except Exception as e:
                print(f"Error subscribing: {e}")

# Exemplo de uso
async def message_handler(msg):
    subject = msg.subject
    data = msg.data.decode()
    print(f"Received a message on '{subject}': {data}")

async def main():
    bus = NatsBus()
    await bus.connect()

    # Publicar uma mensagem
    await bus.publish("viability.check.requested", '{"check_id": "123", "location": "some_location"}')

    # Subscrever a um tópico
    await bus.subscribe("viability.analysis.completed", message_handler)

    # Manter a conexão aberta para receber mensagens
    await asyncio.sleep(10)

    await bus.disconnect()

if __name__ == '__main__':
    asyncio.run(main())

if __name__ == '__main__':
    asyncio.run(main())
