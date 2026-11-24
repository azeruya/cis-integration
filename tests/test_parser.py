from pathlib import Path
from app.integration.parser import parse_hl7_message


def test_parse_oru_message():

    hl7_file_path = (
        Path(__file__).parent.parent
        / "sample_messages"
        / "sample_oru.hl7"
    )

    raw_message = hl7_file_path.read_text()

    parsed_data = parse_hl7_message(raw_message)

    assert parsed_data is not None

    # Test metadata
    metadata = parsed_data["metadata"]

    assert metadata["message_type"] == "ORU^R01^ORU_R01"
    assert metadata["message_control_id"] == "MSG00001"
    assert metadata["sending_application"] == "MINDRAY_EGW"
    assert metadata["sending_facility"] == "ICU"
    assert metadata["receiving_application"] == "CIS"
    assert metadata["hl7_version"] == "2.5.1"

    # Test patient
    patient = parsed_data["patient"]

    assert patient["patient_id"] == "P000123^^^HOSPITAL^MR"
    assert patient["patient_name"] == "DOE^JANE"
    assert patient["patient_location"] == "ICU^BED03"

    # Test observations
    observations = parsed_data["observations"]

    assert len(observations) == 2

    first_observation = observations[0]

    assert first_observation["observation_id"] == "8867-4^Heart rate^LN"
    assert first_observation["value_type"] == "NM"
    assert first_observation["value"] == "82"
    assert first_observation["units"] == "/min"
    assert first_observation["status"] == "F"

    second_observation = observations[1]

    assert second_observation["observation_id"] == "8310-5^Body temperature^LN"
    assert second_observation["value"] == "37.2"
    assert second_observation["units"] == "Cel"

def test_parse_adt_a01_message():

    hl7_file_path = (
        Path(__file__).parent.parent
        / "sample_messages"
        / "sample_adt_a01.hl7"
    )

    raw_message = hl7_file_path.read_text()

    parsed_data = parse_hl7_message(raw_message)

    assert parsed_data is not None

    # Test metadata
    metadata = parsed_data["metadata"]

    assert metadata["message_type"] == "ADT^A01^ADT_A01"
    assert metadata["message_control_id"] == "ADT00001"
    assert metadata["sending_application"] == "SIMRS"
    assert metadata["hl7_version"] == "2.5.1"

    # Test patient
    patient = parsed_data["patient"]

    assert patient["patient_id"] == "P000123^^^HOSPITAL^MR"
    assert patient["patient_name"] == "DOE^JANE"
    assert patient["patient_location"] == "ICU^BED03"
    assert patient["visit_number"] == "ENC001"

    # ADT messages don't necessarily contain OBX segments.
    assert parsed_data["observations"] == []