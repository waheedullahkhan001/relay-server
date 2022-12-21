import asyncio


HEADER_SIZE = 64

clients = []


async def send_text(writer: asyncio.StreamWriter, text: str):
    """Send text to client."""
    payload = text.encode('utf8')
    header = f'{len(payload):<{HEADER_SIZE}}'.encode('utf8')
    writer.write(header + payload)
    await writer.drain()

async def receive_text(reader: asyncio.StreamReader) -> str:
    """Receive text from client."""
    header = await reader.read(HEADER_SIZE)
    while len(header) < HEADER_SIZE:
        header += await reader.read(HEADER_SIZE - len(header))
    payload_size = int(header.decode('utf8').strip())

    payload = await reader.read(payload_size)
    while len(payload) < payload_size:
        payload += await reader.read(payload_size - len(payload))
    return payload.decode('utf8')

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle client connection."""
    print('Client connected')
    clients.append((reader, writer))
    try:
        while True:
            text = await receive_text(reader)
            print(f'Received: {text}')
            for client in clients:
                await send_text(client[1], text)
    except Exception as e:
        print(f'Error: {e}')
    finally:
        clients.remove((reader, writer))
        writer.close()
        print('Client disconnected')

async def run_server():
    server = await asyncio.start_server(handle_client, 'localhost', 8888)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(run_server())
