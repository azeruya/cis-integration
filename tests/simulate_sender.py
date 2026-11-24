import socket
from pathlib import Path

from app.integration.framer import (
    extract_messages,
    START_BLOCK,
    END_BLOCK,
    CARRIAGE_RETURN
)

HOST = "127.0.0.1"
PORT = 2575


def send_hl7_message():

    file_path = (
        Path(__file__).parent.parent
        / "sample_messages"
        / "sample_oru.hl7"
    )

    hl7_message = file_path.read_text().strip()

    framed_message = (
        START_BLOCK
        + hl7_message.encode("utf-8")
        + END_BLOCK
        + CARRIAGE_RETURN
    )

    with socket.create_connection((HOST, PORT)) as client:

        client.settimeout(10)

        print("Connected to CIS listener.")

        # Send HL7 message
        print("\nSending ORU message...")

        client.sendall(framed_message)

        print("ORU message sent.")

        # Receive ACK
        print("\nWaiting for ACK...")

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

                if "MSA|AA|MSG00001" in ack:
                    print("ACK successfully verified!")

                else:
                    print("ACK received, but verification failed.")

                break


if __name__ == "__main__":
    send_hl7_message()