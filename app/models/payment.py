from pydantic import BaseModel
from typing import Optional, Dict, Any

# Existing VNPAY models
class PaymentRequest(BaseModel):
    order_id: str
    amount: int
    order_info: str
    ip_addr: str

class PaymentResponse(BaseModel):
    payment_url: str

class PaymentStatus(BaseModel):
    transaction_id: str
    status: str

class WebhookRequest(BaseModel):
    vnp_TxnRef: str
    vnp_TransactionNo: str
    vnp_ResponseCode: str
    vnp_SecureHash: str

class WebhookResponse(BaseModel):
    RspCode: str
    Message: str

# MoMo models
class MomoPaymentRequest(BaseModel):
    order_id: str
    amount: int
    order_info: str
    extra_data: Optional[str] = ""

class MomoPaymentResponse(BaseModel):
    payment_url: str

class MomoWebhookRequest(BaseModel):
    partnerCode: str
    orderId: str
    requestId: str
    amount: int
    orderInfo: str
    orderType: str
    transId: str
    resultCode: int
    message: str
    payType: str
    responseTime: int
    extraData: str
    signature: str

class MomoWebhookResponse(BaseModel):
    status: int = 0
    message: str = "success"