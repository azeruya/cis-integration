
# MLLP control characters
START_BLOCK = b"\x0b"
END_BLOCK = b"\x1c"
CARRIAGE_RETURN = b"\x0d"

MAX_BUFFER_SIZE = 10 * 1024 * 1024  # 10 MB


def extract_messages(buffer):
    """
    Extract complete HL7 messages from a bytearray buffer.

    Returns a list of complete messages as bytes.
    Incomplete messages remain in the buffer.
    """

    messages = []

    while True:
        start = buffer.find(START_BLOCK)

        if start == -1:
            buffer.clear()
            break

        # Discard bytes before the start block.
        if start > 0:
            del buffer[:start]

        end = buffer.find(END_BLOCK, 1)

        if end == -1:
            break

        # Wait for the complete terminator.
        if len(buffer) <= end + 1:
            break

        if buffer[end + 1] != CARRIAGE_RETURN[0]:
            raise ValueError("Invalid MLLP message terminator")

        message = bytes(buffer[1:end])
        messages.append(message)

        # Remove the extracted message and its terminator.
        del buffer[:end + 2]

    if len(buffer) > MAX_BUFFER_SIZE:
        raise ValueError("MLLP buffer exceeds maximum size")

    return messages
