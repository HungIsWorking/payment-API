import hashlib
import hmac
from typing import Dict
from urllib.parse import quote_plus
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def hmacsha256(key, data):
    """Create HMAC SHA256 signature"""
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha256).hexdigest()

def create_vnpay_secure_hash(params: Dict[str, str]) -> str:
    """Create VNPAY secure hash from parameters using SHA256"""
    # Remove hash key if exists
    if 'vnp_SecureHash' in params:
        params.pop('vnp_SecureHash')
    
    # Convert all values to strings
    for key in params:
        params[key] = str(params[key])
    
    # Sort parameters by key
    sorted_keys = sorted(params.keys())
    
    # Create data string EXACTLY as VNPAY requires
    hash_data = ""
    for key in sorted_keys:
        if hash_data:
            hash_data += "&"
        hash_data += f"{key}={params[key]}"
    
    # Log the exact string being hashed
    logger.info(f"Hash data string: {hash_data}")
    
    # Create secure hash using HMAC-SHA256
    hmac_obj = hmac.new(
        settings.VNPAY_HASH_SECRET.encode('utf-8'),
        hash_data.encode('utf-8'),
        hashlib.sha256
    )
    secure_hash = hmac_obj.hexdigest().upper()
    
    return secure_hash

def verify_vnpay_response(params: Dict[str, str]) -> bool:
    """Verify VNPAY response signature"""
    if 'vnp_SecureHash' not in params:
        return False
    
    # Get secure hash from response
    received_hash = params.pop('vnp_SecureHash')
    
    # Calculate hash from received parameters
    calculated_hash = create_vnpay_secure_hash(params)
    
    # Log both hashes for debugging
    logger.info(f"Received hash: {received_hash}")
    logger.info(f"Calculated hash: {calculated_hash}")
    
    return received_hash.upper() == calculated_hash.upper()