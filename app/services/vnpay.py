from datetime import datetime
import pytz
import urllib.parse
from typing import Dict
import logging
from app.core.config import settings
from app.core.security import create_vnpay_secure_hash, verify_vnpay_response

logger = logging.getLogger(__name__)

class VNPayService:
    def __init__(self):
        self.transaction_store: Dict[str, str] = {}

    def create_payment_url(self, order_id: str, amount: int, order_info: str, ip_addr: str) -> str:
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        curr_time = datetime.now(tz)
        
        # Ensure all values are strings
        vnp_params = {
            "vnp_Version": settings.VNPAY_API_VERSION,
            "vnp_Command": "pay",
            "vnp_TmnCode": settings.VNPAY_TMN_CODE,
            "vnp_Amount": str(amount * 100),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": order_id,
            "vnp_OrderInfo": order_info,
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_BankCode": "VISA",
            "vnp_TransactionNo": order_id,
            "vnp_ReturnUrl": settings.VNPAY_RETURN_URL,
            "vnp_CreateDate": curr_time.strftime('%Y%m%d%H%M%S'),
            "vnp_ExpireDate": (curr_time.replace(day=curr_time.day+1)).strftime('%Y%m%d%H%M%S'),
            "vnp_IpAddr": ip_addr,
        }
        print(vnp_params)
        # Log original parameters
        logger.info("Original Payment Parameters:")
        for key, value in sorted(vnp_params.items()):
            logger.info(f"{key}: {value}")
        
        # Create secure hash
        secure_hash = create_vnpay_secure_hash(vnp_params)
        vnp_params["vnp_SecureHash"] = secure_hash
        
        # Log final parameters with hash
        logger.info(f"Generated Hash: {secure_hash}")
        
        # Create URL with properly encoded parameters
        # Using separate encoding to match VNPAY requirements
        parts = []
        for key, value in vnp_params.items():
            parts.append(f"{key}={urllib.parse.quote_plus(str(value))}")
        
        query_string = "&".join(parts)
        payment_url = f"{settings.VNPAY_URL}?{query_string}"
        
        # Log final URL for debugging
        logger.info(f"Final payment URL: {payment_url}")
        
        self.transaction_store[order_id] = "pending"
        return payment_url

    def verify_webhook(self, webhook_data: dict) -> bool:
        logger.info("Webhook Data Received:")
        for key, value in sorted(webhook_data.items()):
            logger.info(f"{key}: {value}")
            
        return verify_vnpay_response(webhook_data)

vnpay_service = VNPayService()