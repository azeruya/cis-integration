
from hl7apy.parser import parse_message


def get_field(segment, field_name):
    """
    Retrieve a field from an HL7 segment.
    Returns an empty string if the field is unavailable.
    """

    field = getattr(segment, field_name, None)

    if field is None:
        return ""

    return field.to_er7()


def parse_hl7_message(raw_message):
    """
    Parse a raw HL7 message and extract selected information.
    """

    try:
        # Normalize line endings into HL7 segment separators.
        normalized_message = (
            raw_message
            .replace("\r\n", "\r")
            .replace("\n", "\r")
        )

        # Parse the raw HL7 message.
        message = parse_message(
            normalized_message,
            find_groups=False
        )

        # Find the MSH segment.
        msh = next(
            (seg for seg in message.children if seg.name == "MSH"),
            None
        )

        if msh is None:
            raise ValueError("MSH segment not found")

        # Extract the message type from MSH-9.
        message_type = get_field(msh, "msh_9")

        # Find the PID segment.
        pid = next(
            (seg for seg in message.children if seg.name == "PID"),
            None
        )

        # Extract the patient identifier from PID-3.
        patient_id = get_field(pid, "pid_3") if pid else ""

        # Collect all OBX segments.
        observations = []

        for obx in (
            seg for seg in message.children
            if seg.name == "OBX"
        ):

            observation = {
                "observation_id": get_field(obx, "obx_3"),
                "value_type": get_field(obx, "obx_2"),
                "value": get_field(obx, "obx_5"),
                "units": get_field(obx, "obx_6"),
                "status": get_field(obx, "obx_11"),
                "timestamp": get_field(obx, "obx_14")
            }

            observations.append(observation)

        # Return the extracted information after processing all segments.
        return {
            "message_type": message_type,
            "patient_id": patient_id,
            "observations": observations
        }

    except Exception as e:
        print(f"Error parsing HL7 message: {e}")
        return None
