# Stripe Payments Report

A FastAPI application that displays Stripe payment links and associated payments.

## Local Development

1. Clone this repository
2. Copy `.env.example` to `.env` and add your Stripe secret key and password:
   ```
   cp .env.example .env
   ```
3. Configure the required environment variables in `.env`:
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
   - `PASSWORD`: Access password for the dashboard
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the development server:
   ```
   uvicorn main:app --reload
   ```

## Docker Deployment

The application can be deployed using Docker:

```bash
docker build -t stripe-payments-report .
docker run -p 8000:8000 \
  -e STRIPE_SECRET_KEY=your_key_here \
  -e PASSWORD=your_password_here \
  stripe-payments-report
```

## Coolify Deployment

1. Connect your GitHub repository to Coolify
2. Add the required environment variables:
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
   - `PASSWORD`: Access password for the dashboard
3. Deploy using the provided Dockerfile

The application will be available on port 8000.