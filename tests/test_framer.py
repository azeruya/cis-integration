
from app.integration.framer import (
    extract_messages,
    START_BLOCK,
    END_BLOCK,
    CARRIAGE_RETURN
)


def frame(message):
    return START_BLOCK + message + END_BLOCK + CARRIAGE_RETURN


def test_extract_single_message():
    message = b"MSH|^~\\&|TEST|ICU"

    buffer = bytearray(frame(message))

    result = extract_messages(buffer)

    assert result == [message]
    assert buffer == bytearray()


def test_extract_multiple_messages():
    message1 = b"MSH|^~\\&|TEST1|ICU"
    message2 = b"MSH|^~\\&|TEST2|ICU"

    buffer = bytearray(frame(message1) + frame(message2))

    result = extract_messages(buffer)

    assert result == [message1, message2]
    assert buffer == bytearray()


def test_incomplete_message():
    message = b"MSH|^~\\&|TEST|ICU"
    framed = frame(message)

    # Send only part of the message.
    buffer = bytearray(framed[:10])

    result = extract_messages(buffer)

    assert result == []
    assert buffer == bytearray(framed[:10])

    # Simulate receiving the remaining bytes.
    buffer.extend(framed[10:])

    result = extract_messages(buffer)

    assert result == [message]
    assert buffer == bytearray()
