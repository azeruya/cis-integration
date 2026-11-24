import asyncio
import logging

from app.integration.framer import (
    extract_messages, FramingError, START_BLOCK, END_BLOCK, CARRIAGE_RETURN
)
from app.integration.parser import parse_hl7_message, extract_fallback_metadata
from app.integration.router import route_message
from app.config import HL7_HOST, HL7_PORT
from app.integration.acknowledgements.ack_generator import generate_ack

logger = logging.getLogger(__name__)


async def send_ack(writer, metadata, acknowledgement_code):
    """
    Build an ACK for the given MSH metadata, frame it, and send it.
    """

    ack = generate_ack({"metadata": metadata}, acknowledgement_code)

    framed_ack = (
        START_BLOCK
        + ack.encode("utf-8")
        + END_BLOCK
        + CARRIAGE_RETURN
    )

    writer.write(framed_ack)
    await writer.drain()

    logger.info("Sent %s ACK for message %s", acknowledgement_code,
                metadata.get("message_control_id"))
    logger.debug("ACK content: %r", ack)


async def handle_message(writer, hl7_message):
    """
    Parse, route, and acknowledge a single HL7 message.

    Always attempts to send an ACK: AA when the message was parsed and
    routed, AE when it was parsed but routing rejected it (e.g.
    unsupported message type) or when it failed to parse but enough of
    MSH could still be recovered to address a reply to. If not even MSH
    can be read, no ACK is possible and the failure is only logged --
    the sender's own retry/timeout handling will apply.
    """

    parsed_data = parse_hl7_message(hl7_message)

    if parsed_data is None:
        logger.warning("Failed to parse HL7 message")

        fallback_metadata = extract_fallback_metadata(hl7_message)

        if fallback_metadata is None:
            logger.error(
                "No MSH segment recoverable; cannot send an ACK for "
                "this message"
            )
            return

        await send_ack(writer, fallback_metadata, "AE")
        return

    metadata = parsed_data["metadata"]

    logger.info(
        "Received %s (control id %s) for patient %s",
        metadata["message_type"],
        metadata["message_control_id"],
        parsed_data["patient"].get("patient_id")
    )
    logger.debug("Full parsed message: %s", parsed_data)

    result = route_message(parsed_data)

    logger.debug("Processing result: %s", result)

    acknowledgement_code = (
        "AA" if result and result.get("status") == "processed" else "AE"
    )

    await send_ack(writer, metadata, acknowledgement_code)


async def handle_client(reader, writer):
    """
    Handle an incoming TCP client connection.
    """

    address = writer.get_extra_info("peername")
    logger.info("Connected to client: %s", address)

    # Each client connection gets its own buffer.
    buffer = bytearray()

    try:
        while True:
            # Read data from the client.
            data = await reader.read(4096)

            if not data:
                # Client has closed the connection.
                logger.info("Client %s disconnected", address)
                break

            # Append the received data to the buffer.
            buffer.extend(data)

            # Extract complete HL7 messages from the buffer. A single
            # malformed frame is handled internally (resynced, not
            # raised); FramingError here means the buffer itself is in
            # an unrecoverable state (e.g. flooded) and the connection
            # should be dropped.
            try:
                messages = extract_messages(buffer)
            except FramingError as e:
                logger.error("Framing error from %s: %s", address, e)
                break

            for message in messages:
                # Convert message bytes into text.
                try:
                    hl7_message = message.decode("utf-8")
                except UnicodeDecodeError:
                    logger.warning(
                        "Invalid message encoding from %s", address
                    )
                    continue

                await handle_message(writer, hl7_message)

    except Exception as e:
        logger.exception("Connection error with %s: %s", address, e)

    finally:
        logger.info("Disconnected from client: %s", address)

        writer.close()
        await writer.wait_closed()


async def start_server():
    """
    Start the TCP server to listen for incoming HL7 messages.
    """

    server = await asyncio.start_server(handle_client, HL7_HOST, HL7_PORT)

    logger.info("HL7 listener running on %s:%s", HL7_HOST, HL7_PORT)

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("listener.log")]
    )
    asyncio.run(start_server())