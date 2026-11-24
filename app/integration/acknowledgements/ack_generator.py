from datetime import datetime

VALID_ACK_CODES = {
    "AA", "AE", "AR",
    "CA", "CE", "CR"
}

def generate_ack(parsed_data, acknowledgement_code="AA"):

    if acknowledgement_code not in VALID_ACK_CODES:
        raise ValueError(
            f"Invalid acknowledgement code: {acknowledgement_code}"
        )

    metadata = parsed_data["metadata"]

    message_control_id = metadata["message_control_id"]

    sending_application = metadata["sending_application"]
    sending_facility = metadata["sending_facility"]

    receiving_application = metadata["receiving_application"]
    receiving_facility = metadata["receiving_facility"]

    processing_id = metadata["processing_id"]
    hl7_version = metadata["hl7_version"]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    ack_control_id = f"ACK{message_control_id}"

    ack_message = (
        f"MSH|^~\\&|"
        f"{receiving_application}|"
        f"{receiving_facility}|"
        f"{sending_application}|"
        f"{sending_facility}|"
        f"{timestamp}||"
        f"ACK^R01^ACK|"
        f"{ack_control_id}|"
        f"{processing_id}|"
        f"{hl7_version}\r"
        f"MSA|{acknowledgement_code}|"
        f"{message_control_id}\r"
    )

    return ack_message