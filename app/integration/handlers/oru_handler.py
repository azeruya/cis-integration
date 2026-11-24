def handle_oru(parsed_data):
    """
    Handle incoming ORU messages containing observations.
    """

    metadata = parsed_data["metadata"]
    patient = parsed_data["patient"]
    observations = parsed_data["observations"]

    print("\n--- ORU Handler ---")

    print(f"Message ID: {metadata['message_control_id']}")
    print(f"Patient ID: {patient['patient_id']}")

    for observation in observations:
        print(
            f"{observation['observation_id']}: "
            f"{observation['value']} "
            f"{observation['units']}"
        )

    return {
        "status": "processed",
        "message_type": metadata["message_type"],
        "observation_count": len(observations)
    }