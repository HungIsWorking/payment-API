import logging
from fastapi import FastAPI
from app.api.endpoints import payment
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vnpay.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
)

app.include_router(
    payment.router,
    prefix=settings.API_PREFIX,
    tags=["payment"]
)