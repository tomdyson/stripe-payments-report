from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import stripe
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/payment-links")
async def get_payment_links():
    try:
        # First get all payment links
        payment_links = stripe.PaymentLink.list(limit=100)
        
        # Transform the response to include product names
        links_with_products = []
        for link in payment_links.data:
            # Fetch individual payment link to get line items
            link_details = stripe.PaymentLink.retrieve(
                link.id,
                expand=['line_items']
            )
            
            product_name = 'Unknown Product'
            if hasattr(link_details, 'line_items') and link_details.line_items.data:
                # Get price ID from line item
                price_id = link_details.line_items.data[0].price.id
                # Fetch price to get product details
                price = stripe.Price.retrieve(price_id, expand=['product'])
                product_name = price.product.name
            
            links_with_products.append({
                'id': link.id,
                'url': link.url,
                'product_name': product_name  # Removed the ({link.id})
            })
        
        return links_with_products
    except Exception as e:
        print(f"Error in get_payment_links: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/payments/{payment_link_id}")
async def get_payments(payment_link_id: str):
    try:
        # Get checkout sessions for the payment link with increased limit
        sessions = stripe.checkout.Session.list(
            payment_link=payment_link_id,
            expand=['data.customer', 'data.payment_intent'],
            limit=100  # Increased from default (10) to 100
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
