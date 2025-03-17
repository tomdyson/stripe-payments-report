# Stripe Payments Report

A FastAPI application that displays Stripe payment links and associated payments.

## Local Development

1. Clone this repository
2. Copy `.env.example` to `.env` and add your Stripe secret key:
   ```
   cp .env.example .env
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```
   uvicorn main:app --reload
   ```

## Docker Deployment

The application can be deployed using Docker:

```bash
docker build -t stripe-payments-report .
docker run -p 8000:8000 -e STRIPE_SECRET_KEY=your_key_here stripe-payments-report
```

## Coolify Deployment

1. Connect your GitHub repository to Coolify
2. Add the required environment variable:
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
3. Deploy using the provided Dockerfile

The application will be available on port 8000.