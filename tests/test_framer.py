import pytest

from app.integration.framer import (
    extract_messages,
    FramingError,
    MAX_BUFFER_SIZE,
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


def test_invalid_terminator_resyncs_instead_of_raising():
    good_message = b"MSH|^~\\&|TEST|ICU"

    # A glitched frame: END_BLOCK is followed by garbage instead of CR.
    bad_frame = START_BLOCK + b"GARBLED" + END_BLOCK + b"\x00"

    buffer = bytearray(bad_frame + frame(good_message))

    result = extract_messages(buffer)

    # The malformed frame is dropped, but the next good message is
    # still recovered -- the connection does not need to be torn down.
    assert result == [good_message]
    assert buffer == bytearray()


def test_buffer_overflow_raises_framing_error_and_clears_buffer():
    buffer = bytearray(START_BLOCK + b"x" * (MAX_BUFFER_SIZE + 1))

    with pytest.raises(FramingError):
        extract_messages(buffer)

    assert buffer == bytearray()