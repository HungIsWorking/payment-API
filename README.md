python3 -m venv .venv
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
http://localhost:8000/api/v1/docs#/payment/create_payment_api_v1_create_payment_post