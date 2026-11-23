import socket
from pathlib import Path


HOST = "127.0.0.1"
PORT = 2575

START = b"\x0b"
END = b"\x1c\x0d"


def send_hl7_message():

    # Load the sample ORU message.
    file_path = (
        Path(__file__).parent.parent
        / "sample_messages"
        / "sample_oru.hl7"
    )

    hl7_message = file_path.read_text().strip()

    # Add MLLP framing.
    framed_message = (
        START
        + hl7_message.encode("utf-8")
        + END
    )

    # Connect to the local TCP listener.
    with socket.create_connection((HOST, PORT)) as client:
        print("Connected to CIS listener.")

        for i in range(3):
            print(f"Sending message {i + 1}...")
            client.sendall(framed_message)

        print("All messages sent.")


if __name__ == "__main__":
    send_hl7_message()
