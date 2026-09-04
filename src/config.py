from pathlib import Path
import os

import toml
from dotenv import load_dotenv

class Config:
    """
    Loads the project configuration from .env file and config.toml file.
    """

    def __init__(self):

        self.PROJECT_ROOT = Path(__file__).resolve().parent.parent
        self.tomlFile = self.PROJECT_ROOT / "config.toml"
        self.envFile = self.PROJECT_ROOT / ".env"

        load_dotenv(self.envFile)

        self.config = toml.load(self.tomlFile)

        # openai configurations
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured in .env")
        self.MODELS = self.config["models"]

        # token limits
        self.TOKEN_LIMIT = self.config["token_limit"]

        # cost tracking
        self.COST = self.config["cost"]

        # logging
        self.LOGGING = self.config["logging"]

        # paths
        self.PATHS = self.config["paths"]

        # Email configuration
        self.EMAIL = self.config.get("email", {})
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

config = Config()