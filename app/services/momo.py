import json
import uuid
import hmac
import hashlib
import requests
from typing import Dict, Any
import logging
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class MomoService:
    def __init__(self):
        self.transaction_store: Dict[str, str] = {}
        
    def create_payment_url(self, order_id: str, amount: int, order_info: str, extra_data: str = "") -> str:
        """Create MoMo payment URL"""
        # Create request ID
        request_id = str(uuid.uuid4())
        
        # Prepare parameters
        request_data = {
            "partnerCode": settings.MOMO_PARTNER_CODE,
            "accessKey": settings.MOMO_ACCESS_KEY,
            "requestId": request_id,
            "amount": amount,
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": settings.MOMO_RETURN_URL,  # Changed from returnUrl
            "ipnUrl": settings.MOMO_NOTIFY_URL,       # Changed from notifyUrl
            "extraData": extra_data,
            "requestType": "captureWallet",           # Changed from captureMoMoWallet
            "lang": "vi"                              # Added language parameter
        }
        
        # Create signature - update the raw_signature string format
        raw_signature = (
            f"accessKey={settings.MOMO_ACCESS_KEY}"
            f"&amount={amount}"
            f"&extraData={extra_data}"
            f"&ipnUrl={settings.MOMO_NOTIFY_URL}"
            f"&orderId={order_id}"
            f"&orderInfo={order_info}"
            f"&partnerCode={settings.MOMO_PARTNER_CODE}"
            f"&redirectUrl={settings.MOMO_RETURN_URL}"
            f"&requestId={request_id}"
            f"&requestType=captureWallet"
        )
        
        # Log the raw signature for debugging
        logger.info(f"Raw signature: {raw_signature}")
        
        signature = self.create_signature(raw_signature)
        request_data["signature"] = signature
        
        # Log request data
        logger.info(f"MoMo Request Data: {json.dumps(request_data)}")
        
        # Send request to MoMo
        try:
            response = requests.post(
                settings.MOMO_API_ENDPOINT,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Log response status and content
            logger.info(f"MoMo Response Status: {response.status_code}")
            logger.info(f"MoMo Response Content: {response.text}")
            
            response_data = response.json()
            
            if response_data.get("resultCode") == 0:
                payment_url = response_data.get("payUrl", "")
                self.transaction_store[order_id] = "pending"
                return payment_url
            else:
                error_msg = f"MoMo Error: {response_data.get('message')} (Code: {response_data.get('resultCode')})"
                logger.error(error_msg)
                raise Exception(f"MoMo payment creation failed: {response_data.get('message')}")
                
        except Exception as e:
            logger.error(f"Error creating MoMo payment: {str(e)}")
            raise
            
    def create_signature(self, raw_signature: str) -> str:
        """Create MoMo signature using HMAC SHA256"""
        h = hmac.new(
            bytes(settings.MOMO_SECRET_KEY, 'utf-8'),
            bytes(raw_signature, 'utf-8'),
            hashlib.sha256
        )
        return h.hexdigest()
        
    def verify_webhook(self, data: Dict[str, Any]) -> bool:
        """Verify MoMo webhook signature"""
        if "signature" not in data:
            return False
            
        # Extract signature
        received_signature = data.pop("signature")
        
        # Create raw signature string
        raw_signature = f"accessKey={settings.MOMO_ACCESS_KEY}"
        
        # Add all other fields
        for key in sorted(data.keys()):
            raw_signature += f"&{key}={data[key]}"
            
        # Calculate signature
        calculated_signature = self.create_signature(raw_signature)
        
        # Log signatures for debugging
        logger.info(f"MoMo Received Signature: {received_signature}")
        logger.info(f"MoMo Calculated Signature: {calculated_signature}")
        
        return received_signature == calculated_signature

momo_service = MomoService()