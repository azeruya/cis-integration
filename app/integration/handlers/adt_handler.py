import logging

logger = logging.getLogger(__name__)


def handle_adt(parsed_data):
    """
    Handle incoming ADT messages containing patient events.
    """

    metadata = parsed_data["metadata"]
    patient = parsed_data["patient"]

    message_type = metadata["message_type"]

    # Extract the ADT event from MSH-9.
    # Example: ADT^A01^ADT_A01 -> A01
    message_parts = message_type.split("^")

    event_type = (
        message_parts[1]
        if len(message_parts) > 1
        else "UNKNOWN"
    )

    event_names = {
        "A01": "Patient Admission",
        "A02": "Patient Transfer",
        "A03": "Patient Discharge",
        "A08": "Patient Information Update"
    }

    event_name = event_names.get(
        event_type,
        "Other ADT Event"
    )

    logger.info(
        "ADT %s (%s) message %s for patient %s",
        event_type,
        event_name,
        metadata["message_control_id"],
        patient["patient_id"]
    )
    # Patient name/location carry PHI, so they stay out of the default
    # log level and are only emitted at DEBUG.
    logger.debug(
        "Patient name: %s, location: %s",
        patient["patient_name"],
        patient["patient_location"]
    )

    return {
        "status": "processed",
        "event_type": event_type,
        "event_name": event_name,
        "patient_id": patient["patient_id"]
    }