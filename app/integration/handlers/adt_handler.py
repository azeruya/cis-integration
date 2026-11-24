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

    print("\n--- ADT Handler ---")

    print(f"Event: {event_name}")
    print(f"Message ID: {metadata['message_control_id']}")
    print(f"Patient ID: {patient['patient_id']}")
    print(f"Patient Name: {patient['patient_name']}")
    print(f"Patient Location: {patient['patient_location']}")

    return {
        "status": "processed",
        "event_type": event_type,
        "event_name": event_name,
        "patient_id": patient["patient_id"]
    }