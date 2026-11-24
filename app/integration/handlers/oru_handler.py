import logging

logger = logging.getLogger(__name__)


def handle_oru(parsed_data):
    """
    Handle incoming ORU messages containing observations.
    """

    metadata = parsed_data["metadata"]
    patient = parsed_data["patient"]
    observations = parsed_data["observations"]

    logger.info(
        "ORU message %s for patient %s: %d observation(s)",
        metadata["message_control_id"],
        patient["patient_id"],
        len(observations)
    )

    for observation in observations:
        logger.debug(
            "%s: %s %s",
            observation["observation_id"],
            observation["value"],
            observation["units"]
        )

    return {
        "status": "processed",
        "message_type": metadata["message_type"],
        "observation_count": len(observations)
    }