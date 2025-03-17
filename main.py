from fastapi import FastAPI, HTTPException, Depends, Response, Request, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyCookie
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from jose import jwt, JWTError
import stripe
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from datetime import timedelta
import logging

# Set up logging with reduced verbosity
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Configure CORS - more permissive for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PASSWORD = os.getenv("PASSWORD")
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.urandom(32).hex()
COOKIE_NAME = "session_token"

cookie_sec = APIKeyCookie(name=COOKIE_NAME, auto_error=False)

def create_token():
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    return jwt.encode({"exp": expires.timestamp()}, SECRET_KEY, algorithm="HS256")

async def get_current_user(request: Request, token: str = Depends(cookie_sec)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if not exp or datetime.now(timezone.utc).timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expired")
        return True
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/login")
async def login_page():
    return FileResponse("static/login.html")

@app.get("/dashboard")
async def dashboard_page():
    return FileResponse("static/index.html")

@app.post("/api/login")
async def login(request: Request, response: Response, password: str = Form()):
    if password == PASSWORD:
        token = create_token()
        response = JSONResponse({"status": "success"})
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            secure=False,  # Set to True in production
            samesite="lax",
            path="/",
            max_age=86400
        )
        return response
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password"
    )

@app.get("/api/payment-links")
async def get_payment_links(request: Request, current_user: bool = Depends(get_current_user)):
    try:
        payment_links = stripe.PaymentLink.list(limit=100)
        links_with_products = []
        for link in payment_links.data:
            link_details = stripe.PaymentLink.retrieve(
                link.id,
                expand=['line_items']
            )
            
            product_name = 'Unknown Product'
            if hasattr(link_details, 'line_items') and link_details.line_items.data:
                price_id = link_details.line_items.data[0].price.id
                price = stripe.Price.retrieve(price_id, expand=['product'])
                product_name = price.product.name
            
            links_with_products.append({
                'id': link.id,
                'url': link.url,
                'product_name': product_name
            })
        
        return links_with_products
    except Exception as e:
        logger.error(f"Error in get_payment_links: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/payments/{payment_link_id}")
async def get_payments(payment_link_id: str, _: bool = Depends(get_current_user)):
    try:
        # Get checkout sessions for the payment link with increased limit
        sessions = stripe.checkout.Session.list(
            payment_link=payment_link_id,
            expand=['data.customer', 'data.payment_intent'],
            limit=100
        )
        
        # Transform the data to match our frontend expectations
        payments = []
        for session in sessions.data:
            if session.payment_intent:
                payment = session.payment_intent
                payment['customer'] = session.customer
                payments.append(payment)
                
        return payments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
