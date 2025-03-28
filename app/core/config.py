from pydantic import BaseSettings
from dotenv import load_dotenv
import os

# Load biến môi trường từ file .env
load_dotenv()

class Settings(BaseSettings):
    # Project information
    PROJECT_NAME: str = "MyProject"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # VNPAY Configuration
    VNPAY_TMN_CODE: str
    VNPAY_HASH_SECRET: str
    VNPAY_URL: str
    VNPAY_RETURN_URL: str
    VNPAY_API_VERSION: str

    # MoMo Configuration
    MOMO_PARTNER_CODE: str
    MOMO_ACCESS_KEY: str
    MOMO_SECRET_KEY: str
    MOMO_API_ENDPOINT: str
    MOMO_RETURN_URL: str
    MOMO_NOTIFY_URL: str

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()