# Systems

Technical systems, services, and their key details.

## payment-service
- **Language:** [[TypeScript]] / Node.js
- **Database:** [[PostgreSQL]] 15
- **Owner:** [[Alice Chen]]
- **Repo:** `backend/services/payment`
- **Key endpoints:** `/api/v1/payments`, `/api/v1/refunds`
- **Notes:** Uses [[Stripe]] SDK, connection pool max 20

## dashboard
- **Language:** [[TypeScript]] / React 18
- **Owner:** [[Bob Martinez]]
- **Repo:** `frontend/dashboard`
- **Key routes:** `/dashboard`, `/analytics`, `/settings`
- **Notes:** Server-side rendering enabled, bundle budget 250KB gzipped
