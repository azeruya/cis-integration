import asyncio
from app.integration.framer import (
    extract_messages, START_BLOCK, END_BLOCK, CARRIAGE_RETURN
)
from app.integration.parser import parse_hl7_message
from app.integration.router import route_message
from app.config import HL7_HOST, HL7_PORT
from app.integration.acknowledgements.ack_generator import generate_ack

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
                    continue

                # Route the parsed message.
                result = route_message(parsed_data)

                print("\nProcessing result:")
                print(result)

                # Generate ACK
                ack = generate_ack(parsed_data, "AA")

                # Wrap ACK using MLLP framing
                framed_ack = (
                    START_BLOCK
                    + ack.encode("utf-8")
                    + END_BLOCK
                    + CARRIAGE_RETURN
                )

                writer.write(framed_ack)
                await writer.drain()

                print("\nACK sent:")
                print(repr(ack))

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

    server = await asyncio.start_server(handle_client, HL7_HOST, HL7_PORT)

    print(f"HL7 listener running on {HL7_HOST}:{HL7_PORT}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_server())