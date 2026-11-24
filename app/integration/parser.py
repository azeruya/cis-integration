import logging

from hl7apy.parser import parse_message

logger = logging.getLogger(__name__)


def extract_fallback_metadata(raw_message):
    """
    Best-effort extraction of MSH metadata directly from the raw text,
    for building an ACK when full HL7 parsing fails (e.g. a malformed
    or incomplete message). Returns None if there isn't even a
    recognizable MSH segment to read.
    """

    first_segment = raw_message.strip().split("\r")[0].split("\n")[0]

    if not first_segment.startswith("MSH") or len(first_segment) < 4:
        return None

    field_separator = first_segment[3]
    fields = first_segment.split(field_separator)

    def field(index):
        return fields[index] if len(fields) > index else ""

    return {
        # MSH-1 is the field separator itself, so fields[2] is MSH-3.
        "message_control_id": field(9) or "UNKNOWN",
        "sending_application": field(2),
        "sending_facility": field(3),
        "receiving_application": field(4),
        "receiving_facility": field(5),
        "processing_id": field(10),
        "hl7_version": field(11)
    }


def get_field(segment, field_name):
    """
    Retrieve a field from an HL7 segment.

    Returns an empty string if the segment or field is unavailable.
    """
    if segment is None:
        return ""

    field = getattr(segment, field_name, None)

    if field is None:
        return ""

    return field.to_er7()


def get_segment(message, segment_name):
    """
    Find the first occurrence of a segment in an HL7 message.
    """
    return next(
        (
            segment
            for segment in message.children
            if segment.name == segment_name
        ),
        None
    )


def parse_hl7_message(raw_message):
    """
    Parse an HL7 message and extract common metadata,
    patient information, and observation data.
    """

    try:
        # Normalize line endings to HL7 segment separators.
        normalized_message = (
            raw_message
            .replace("\r\n", "\r")
            .replace("\n", "\r")
        )

        message = parse_message(
            normalized_message,
            find_groups=False
        )

        # ---------------------------------
        # 1. Extract message header (MSH)
        # ---------------------------------

        msh = get_segment(message, "MSH")

        if msh is None:
            raise ValueError("MSH segment not found")

        message_type = get_field(msh, "msh_9")

        metadata = {
            "message_type": message_type,
            "message_control_id": get_field(msh, "msh_10"),
            "sending_application": get_field(msh, "msh_3"),
            "sending_facility": get_field(msh, "msh_4"),
            "receiving_application": get_field(msh, "msh_5"),
            "receiving_facility": get_field(msh, "msh_6"),
            "message_timestamp": get_field(msh, "msh_7"),
            "processing_id": get_field(msh, "msh_11"),
            "hl7_version": get_field(msh, "msh_12")
        }

        # ---------------------------------
        # 2. Extract patient information
        # ---------------------------------

        pid = get_segment(message, "PID")
        pv1 = get_segment(message, "PV1")

        patient = {
            "patient_id": get_field(pid, "pid_3"),
            "patient_name": get_field(pid, "pid_5"),
            "visit_number": get_field(pv1, "pv1_19"),
            "patient_location": get_field(pv1, "pv1_3")
        }

        # ---------------------------------
        # 3. Extract observations (OBX)
        # ---------------------------------

        observations = []

        for obx in (
            segment
            for segment in message.children
            if segment.name == "OBX"
        ):

            observation = {
                "observation_id": get_field(obx, "obx_3"),
                "value_type": get_field(obx, "obx_2"),
                "value": get_field(obx, "obx_5"),
                "units": get_field(obx, "obx_6"),
                "reference_range": get_field(obx, "obx_7"),
                "abnormal_flag": get_field(obx, "obx_8"),
                "status": get_field(obx, "obx_11"),
                "timestamp": get_field(obx, "obx_14")
            }

            observations.append(observation)

        # ---------------------------------
        # 4. Return parsed message
        # ---------------------------------

        return {
            "metadata": metadata,
            "patient": patient,
            "observations": observations
        }

    except Exception as e:
        logger.warning("Error parsing HL7 message: %s", e)
        return None