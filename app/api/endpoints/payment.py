import logging
from fastapi import APIRouter, HTTPException, Request
from app.models.payment import (
    PaymentRequest, PaymentResponse, 
    PaymentStatus, WebhookRequest, WebhookResponse,
    MomoPaymentRequest, MomoPaymentResponse,
    MomoWebhookRequest, MomoWebhookResponse
)
from app.services.vnpay import vnpay_service
from app.services.momo import momo_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create-payment", response_model=PaymentResponse)
async def create_payment(payment: PaymentRequest):
    payment_url = vnpay_service.create_payment_url(
        payment.order_id,
        payment.amount,
        payment.order_info,
        payment.ip_addr
    )
    return PaymentResponse(payment_url=payment_url)

@router.get("/payment-status/{transaction_id}", response_model=PaymentStatus)
async def get_payment_status(transaction_id: str):
    """Get payment status for either VNPAY or MoMo transaction"""
    if transaction_id in vnpay_service.transaction_store:
        return PaymentStatus(
            transaction_id=transaction_id,
            status=vnpay_service.transaction_store[transaction_id]
        )
    elif transaction_id in momo_service.transaction_store:
        return PaymentStatus(
            transaction_id=transaction_id,
            status=momo_service.transaction_store[transaction_id]
        )
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.post("/webhook", response_model=WebhookResponse)
async def handle_webhook(webhook: WebhookRequest):
    webhook_data = webhook.dict()
    if not vnpay_service.verify_webhook(webhook_data):
        return WebhookResponse(
            RspCode="97",
            Message="Invalid Signature"
        )
    
    transaction_id = webhook.vnp_TxnRef
    status = "success" if webhook.vnp_ResponseCode == "00" else "failed"
    vnpay_service.transaction_store[transaction_id] = status
    
    return WebhookResponse(
        RspCode="00",
        Message="Confirm Success"
    )

@router.get("/vnpay-return")
async def vnpay_return(request: Request):
    """Handle return URL from VNPAY"""
    # Get all query parameters
    params = dict(request.query_params)
    
    logger.info("Return URL Parameters:")
    for key, value in sorted(params.items()):
        logger.info(f"{key}: {value}")
    
    # Verify response
    if not vnpay_service.verify_vnpay_response(params):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Get transaction status
    response_code = params.get('vnp_ResponseCode', '')
    transaction_id = params.get('vnp_TxnRef', '')
    
    # Update transaction status
    status = "success" if response_code == "00" else "failed"
    vnpay_service.transaction_store[transaction_id] = status
    
    # Return result page
    return {
        "status": status,
        "order_id": transaction_id,
        "message": "Payment processed successfully" if status == "success" else "Payment failed"
    }

# MoMo endpoints
@router.post("/momo/create-payment", response_model=MomoPaymentResponse)
async def create_momo_payment(payment: MomoPaymentRequest):
    """Create MoMo payment URL"""
    try:
        payment_url = momo_service.create_payment_url(
            payment.order_id,
            payment.amount,
            payment.order_info,
            payment.extra_data
        )
        return MomoPaymentResponse(payment_url=payment_url)
    except Exception as e:
        logger.error(f"Error creating MoMo payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/momo-webhook", response_model=MomoWebhookResponse)
async def momo_webhook(request: Request):
    """Handle MoMo webhook notifications"""
    try:
        # Get JSON data from request
        data = await request.json()
        
        logger.info("MoMo Webhook Data:")
        for key, value in sorted(data.items()):
            logger.info(f"{key}: {value}")
        
        # Verify signature
        if not momo_service.verify_webhook(data):
            logger.warning("Invalid MoMo signature")
            return MomoWebhookResponse(status=1, message="Invalid signature")
        
        # Update transaction status
        order_id = data.get("orderId", "")
        result_code = data.get("resultCode", 99)
        
        status = "success" if result_code == 0 else "failed"
        momo_service.transaction_store[order_id] = status
        
        return MomoWebhookResponse()
        
    except Exception as e:
        logger.error(f"Error processing MoMo webhook: {str(e)}")
        return MomoWebhookResponse(status=1, message=str(e))

@router.get("/momo-return")
async def momo_return(request: Request):
    """Handle MoMo return URL"""
    # Get query parameters
    params = dict(request.query_params)
    
    logger.info("MoMo Return Parameters:")
    for key, value in sorted(params.items()):
        logger.info(f"{key}: {value}")
    
    # Extract data
    order_id = params.get("orderId", "")
    result_code = int(params.get("resultCode", "99"))
    
    # Update transaction status
    status = "success" if result_code == 0 else "failed"
    if order_id:
        momo_service.transaction_store[order_id] = status
    
    # Return result page
    return {
        "status": status,
        "order_id": order_id,
        "message": "Payment processed successfully" if status == "success" else "Payment failed"
    }