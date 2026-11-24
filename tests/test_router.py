from pathlib import Path

from app.integration.parser import parse_hl7_message
from app.integration.router import route_message


def test_route_oru_message():

    hl7_file_path = (
        Path(__file__).parent.parent
        / "sample_messages"
        / "sample_oru.hl7"
    )

    raw_message = hl7_file_path.read_text()

    parsed_data = parse_hl7_message(raw_message)

    result = route_message(parsed_data)

    assert result is not None
    assert result["status"] == "processed"
    assert result["message_type"] == "ORU^R01^ORU_R01"
    assert result["observation_count"] == 2

def test_route_adt_a01_message():

    hl7_file_path = (
        Path(__file__).parent.parent
        / "sample_messages"
        / "sample_adt_a01.hl7"
    )

    raw_message = hl7_file_path.read_text()

    parsed_data = parse_hl7_message(raw_message)

    result = route_message(parsed_data)

    assert result is not None
    assert result["status"] == "processed"
    assert result["event_type"] == "A01"
    assert result["event_name"] == "Patient Admission"
    assert result["patient_id"] == "P000123^^^HOSPITAL^MR"

def test_route_unsupported_message():

    parsed_data = {
        "metadata": {
            "message_type": "XYZ^R01"
        },
        "patient": {},
        "observations": []
    }

    result = route_message(parsed_data)

    assert result["status"] == "unsupported"