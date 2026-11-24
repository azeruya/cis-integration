from app.integration.parser import parse_hl7_message
from app.integration.acknowledgements.ack_generator import generate_ack
import pytest

def test_generate_ack():

    raw_message = (
        "MSH|^~\\&|MINDRAY_EGW|ICU|CIS|HOSPITAL|"
        "20261124100000||ORU^R01^ORU_R01|MSG00001|T|2.5.1\r"
        "PID|||P000123^^^HOSPITAL^MR||DOE^JANE\r"
    )

    parsed_data = parse_hl7_message(raw_message)

    ack = generate_ack(parsed_data)

    assert "CIS|HOSPITAL|MINDRAY_EGW|ICU" in ack
    assert "ACK^R01^ACK" in ack
    assert "MSA|AA|MSG00001" in ack
@pytest.mark.parametrize(
    "acknowledgement_code",
    ["AA", "AE", "AR", "CA", "CE", "CR"]
)
def test_generate_ack_with_different_codes(acknowledgement_code):

    raw_message = (
        "MSH|^~\\&|MINDRAY_EGW|ICU|CIS|HOSPITAL|"
        "20261124100000||ORU^R01^ORU_R01|MSG00001|T|2.5.1\r"
    )

    parsed_data = parse_hl7_message(raw_message)

    ack = generate_ack(
        parsed_data,
        acknowledgement_code
    )

    assert f"MSA|{acknowledgement_code}|MSG00001" in ack


def test_generate_ack_with_invalid_code():

    raw_message = (
        "MSH|^~\\&|MINDRAY_EGW|ICU|CIS|HOSPITAL|"
        "20261124100000||ORU^R01^ORU_R01|MSG00001|T|2.5.1\r"
    )

    parsed_data = parse_hl7_message(raw_message)

    with pytest.raises(ValueError):
        generate_ack(parsed_data, "XX")