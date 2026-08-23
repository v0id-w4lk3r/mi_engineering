import os
from dotenv import load_dotenv

load_dotenv()

env = os.getenv("ENV", "dev")

if env == "prod":
    from .prod import *  # noqa: F403
else:
    from .dev import *  # noqa: F403