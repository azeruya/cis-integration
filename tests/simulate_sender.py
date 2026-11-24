import re
import socket
import sys
from pathlib import Path

from app.integration.framer import (
    extract_messages,
    START_BLOCK,
    END_BLOCK,
    CARRIAGE_RETURN
)
from app.config import HL7_HOST, HL7_PORT

DEFAULT_SAMPLE = "sample_oru.hl7"


def control_id(hl7_message):
    """
    Pull MSH-10 (message control id) out of the message so the ACK can be
    verified against whichever sample file was sent, instead of a
    hardcoded value.
    """

    first_segment = hl7_message.strip().split("\r")[0].split("\n")[0]
    field_separator = first_segment[3]
    fields = first_segment.split(field_separator)

    return fields[9] if len(fields) > 9 else None


def send_hl7_message(sample_name=DEFAULT_SAMPLE):

    file_path = Path(__file__).parent.parent / "sample_messages" / sample_name

    hl7_message = file_path.read_text().strip()
    expected_control_id = control_id(hl7_message)

    framed_message = (
        START_BLOCK
        + hl7_message.encode("utf-8")
        + END_BLOCK
        + CARRIAGE_RETURN
    )

    with socket.create_connection((HL7_HOST, HL7_PORT)) as client:

        client.settimeout(10)

        print(f"Connected to CIS listener. Sending {sample_name}...")

        client.sendall(framed_message)

        print("Message sent.\n\nWaiting for ACK...")

        buffer = bytearray()

        while True:

            data = client.recv(4096)

            if not data:
                raise ConnectionError(
                    "CIS disconnected before sending ACK."
                )

            buffer.extend(data)

            messages = extract_messages(buffer)

            if messages:
                ack = messages[0].decode("utf-8")

                print("\nReceived ACK:")
                print(repr(ack))

                expected = f"MSA|AA|{expected_control_id}"

                if expected in ack:
                    print(f"ACK successfully verified! ({expected})")
                elif "MSA|AE|" in ack:
                    print(
                        "ACK received with AE (rejected) -- check the "
                        "listener log for why."
                    )
                else:
                    print("ACK received, but verification failed.")

                break


if __name__ == "__main__":
    # Usage: python -m tests.simulate_sender [sample_messages/<file>.hl7]
    arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SAMPLE
    send_hl7_message(Path(arg).name)