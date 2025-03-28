from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Payment Integration"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # VNPAY Configuration
    VNPAY_TMN_CODE: str
    VNPAY_HASH_SECRET: str
    VNPAY_URL: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNPAY_RETURN_URL: str = "http://localhost:8000/api/v1/payment/vnpay-return"
    VNPAY_API_VERSION: str = "2.1.0"
    
    # MoMo Configuration
    MOMO_PARTNER_CODE: str
    MOMO_ACCESS_KEY: str
    MOMO_SECRET_KEY: str
    MOMO_API_ENDPOINT: str = "https://test-payment.momo.vn/v2/gateway/api/create"
    MOMO_RETURN_URL: str = "http://localhost:8000/api/v1/payment/momo-return"
    MOMO_NOTIFY_URL: str = "http://localhost:8000/api/v1/payment/momo-webhook"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()