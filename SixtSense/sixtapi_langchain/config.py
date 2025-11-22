from dotenv import load_dotenv
import os

load_dotenv()

SIXT_BASE_URL = os.getenv("SIXT_BASE_URL", "https://hackatum25.sixt.io")