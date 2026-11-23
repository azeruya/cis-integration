import asyncio
from app.integration.framer import extract_messages
from app.integration.parser import parse_hl7_message

HOST = "127.0.0.1"
PORT = 2575

async def handle_client(reader, writer):
    """
    Handle an incoming TCP client connection.
    """

    address = writer.get_extra_info("peername")
    print(f"Connected to client: {address}")

    # Each client connection gets its own buffer.
    buffer = bytearray()

    try:
        while True:
            # Read data from the client.
            data = await reader.read(4096)

            if not data:
                # Client has closed the connection.
                print(f"Client {address} disconnected")
                break

            # Append the received data to the buffer.
            buffer.extend(data)

            # Extract complete HL7 messages from the buffer.
            messages = extract_messages(buffer)

            for message in messages:
                # Convert message bytes into text.
                try:
                    hl7_message = message.decode("utf-8")
                except UnicodeDecodeError:
                    print("Invalid message encoding")
                    continue

                print("\nReceived HL7 message:")
                print(hl7_message)

                # Parse the HL7 message.
                parsed_data = parse_hl7_message(hl7_message)

                if parsed_data is None:
                    print("Failed to parse HL7 message")
                else:
                    print("\nParsed HL7 data:")
                    print(parsed_data)

    except Exception as e:
        print(f"Connection error: {e}")

    finally:
        print(f"Disconnected from client: {address}")

        writer.close()
        await writer.wait_closed()

async def start_server():
    """
    Start the TCP server to listen for incoming HL7 messages.
    """

    server = await asyncio.start_server(handle_client, HOST, PORT)

    print(f"HL7 listener running on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_server())