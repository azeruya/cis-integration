from app.integration.handlers.oru_handler import handle_oru
from app.integration.handlers.adt_handler import handle_adt

def route_message(parsed_data):
    """
    Route the parsed HL7 message to the appropriate handler based on its type.
    """

    if parsed_data is None:
        print("Cannot route an invalid message")
        return None

    message_type = parsed_data["metadata"]["message_type"]

    if message_type.startswith("ORU"):
        return handle_oru(parsed_data)
    elif message_type.startswith("ADT"):
        return handle_adt(parsed_data)
    else:
        print(f"Unsupported message type: {message_type}")
        return {"status": "unsupported", "message_type": message_type}