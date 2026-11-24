import os
from dotenv import load_dotenv

load_dotenv()


HL7_HOST = os.getenv("HL7_HOST", "127.0.0.1")
HL7_PORT = int(os.getenv("HL7_PORT", "2575"))