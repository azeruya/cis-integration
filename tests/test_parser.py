
from pathlib import Path

from app.integration.parser import parse_hl7_message


def test_parse_oru_message():

    # Locate and load the sample HL7 message.
    hl7_file_path = (
        Path(__file__).parent.parent
        / "sample_messages"
        / "sample_oru.hl7"
    )

    raw_message = hl7_file_path.read_text()

    # Parse the HL7 message.
    parsed_data = parse_hl7_message(raw_message)

    # Check that parsing was successful.
    assert parsed_data is not None

    # Check the message type.
    assert parsed_data["message_type"] == "ORU^R01^ORU_R01"

    # Check the patient identifier.
    assert parsed_data["patient_id"] == "P000123^^^HOSPITAL^MR"

    # Check that both observations were extracted.
    assert len(parsed_data["observations"]) == 2

    # Check the first observation (Heart rate).
    first_observation = parsed_data["observations"][0]

    assert first_observation["observation_id"] == "8867-4^Heart rate^LN"
    assert first_observation["value_type"] == "NM"
    assert first_observation["value"] == "82"
    assert first_observation["units"] == "/min"
    assert first_observation["status"] == "F"

    # Check the second observation (Body temperature).
    second_observation = parsed_data["observations"][1]

    assert second_observation["observation_id"] == "8310-5^Body temperature^LN"
    assert second_observation["value"] == "37.2"
    assert second_observation["units"] == "Cel"
