# MLLP control characters
START_BLOCK = b"\x0b"
END_BLOCK = b"\x1c"
CARRIAGE_RETURN = b"\x0d"

MAX_BUFFER_SIZE = 10 * 1024 * 1024  # 10 MB


class FramingError(Exception):
    """
    Raised only for an abnormal condition the caller should treat as fatal
    for the connection (e.g. a flooded buffer). A single malformed
    terminator is NOT fatal -- see extract_messages below -- so callers
    can tell the two apart and keep the connection open for the common
    case of one glitched frame.
    """


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
            # Malformed terminator: a device glitch or a stray byte. Drop
            # just this fragment (through the bad END_BLOCK) and
            # resynchronize on the next START_BLOCK, instead of raising
            # and forcing the whole connection to be torn down.
            del buffer[:end + 1]
            continue

        message = bytes(buffer[1:end])
        messages.append(message)

        # Remove the extracted message and its terminator.
        del buffer[:end + 2]

    if len(buffer) > MAX_BUFFER_SIZE:
        buffer.clear()
        raise FramingError(
            f"MLLP buffer exceeded {MAX_BUFFER_SIZE} bytes without a "
            "complete message; buffer cleared"
        )

    return messages