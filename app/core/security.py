import hashlib
import hmac
from typing import Dict
import urllib.parse
from app.core.config import settings

def create_vnpay_secure_hash(data: Dict[str, str]) -> str:
    """
    Create a secure hash for VNPay payment request
    VNPay requires a specific way of creating the hash:
    1. Sort the parameters alphabetically
    2. Create a query string without URL encoding 
    3. Apply HMAC-SHA512 using the secret key
    """
    # Create a sorted list of parameters
    sorted_items = sorted(data.items())
    
    # Build query string without encoding
    hash_data = "&".join([f"{key}={value}" for key, value in sorted_items])
    
    # Create HMAC-SHA512 hash
    hmac_obj = hmac.new(
        bytes(settings.VNPAY_HASH_SECRET, 'utf-8'),
        bytes(hash_data, 'utf-8'), 
        hashlib.sha512
    )
    
    return hmac_obj.hexdigest()

def verify_vnpay_response(response_data: Dict[str, str]) -> bool:
    """
    Verify the VNPay response signature
    """
    # Extract the secure hash from the response
    received_hash = response_data.get("vnp_SecureHash", "")
    if not received_hash:
        return False
    
    # Create a copy of the data without the secure hash
    data_to_verify = {k: v for k, v in response_data.items() if k != "vnp_SecureHash" and k != "vnp_SecureHashType"}
    
    # Compute the expected hash
    expected_hash = create_vnpay_secure_hash(data_to_verify)
    
    # Compare the hashes
    return expected_hash.lower() == received_hash.lower()