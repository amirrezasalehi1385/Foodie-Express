# Foodie Express

A food ordering and delivery backend built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. It models the full lifecycle of a food-delivery platform: restaurants and menus, carts and checkout, payments (via a simulated gateway), a wallet system, promo-code discounts, order-to-delivery workflow, and post-delivery reviews.

## Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy (2.0-style, `Mapped`/`mapped_column`)
- **Database:** PostgreSQL
- **Migrations:** Alembic
- **Package manager:** uv

## Architecture

The codebase follows a layered structure used consistently across every feature:

```
routes/       -> HTTP layer: request/response, auth dependency, calls a service, commits/rolls back the DB transaction
services/     -> business logic: validation, authorization, orchestration across repositories
repositories/ -> data access only: querying and persisting models, no business rules
models/       -> SQLAlchemy ORM models
dto/          -> Pydantic request/response schemas
```

**Transaction pattern:** repositories only `flush()`; routes own the transaction and call `db.commit()` on success or `db.rollback()` on any exception. This lets a single request touch multiple tables (e.g. creating an order, its line items, and a discount usage record) atomically.

**Row locking:** any operation that reads-then-writes a value under potential concurrent access (wallet balance, discount redemption counts, payment confirmation) uses `SELECT ... FOR UPDATE` to avoid race conditions.

## Core Domains

### Authentication
Register/login with JWT-based auth (`/auth/register`, `/auth/login`).

### Users & Addresses
Profile management, role-based access (`CUSTOMER`, `RESTAURANT_OWNER`, `DELIVERY_MAN`, `ADMIN`), and saved delivery addresses.

### Restaurants, Menus & Foods
Restaurant CRUD, categories, menus with ordered items, and food items with their own category tags and availability flags.

### Cart & Ordering
A cart is scoped to a single restaurant at a time. Checkout validates food availability, computes subtotal, applies an optional discount code, and creates the order with its line items in one transaction.

### Payments
A simulated ("fake") payment gateway: initiating payment creates a `Payment` record and a checkout token; confirming payment simulates gateway processing (including a random decline rate) and updates both the payment and the order status together. Wallet balance is applied automatically before falling back to card payment for any remainder.

### Wallet & Transactions
Each user has a wallet balance backed by an append-only transaction ledger (top-ups, order payments, refunds), rather than a single mutable counter — this preserves a full audit trail and lets balance be recomputed from history.

### Discounts
Promo codes with percentage or fixed-amount value, optional restaurant scoping, minimum order amount, usage caps (total and per-user), and a validity window. Redemptions are tracked in a separate usage ledger to correctly enforce limits under concurrent use.

### Order Lifecycle & Delivery
Orders move through a defined state machine:

```
PENDING_PAYMENT -> PAID -> ACCEPTED -> PREPARING -> READY
  -> ASSIGNED -> DELIVERING -> DELIVERED
```
(or `CANCELLED` / `PAYMENT_FAILED` at applicable points)

Each role can only perform the transitions relevant to it:
- **Restaurant owner:** `PAID -> ACCEPTED -> PREPARING -> READY`
- **Delivery man:** claims a `READY` order (`-> ASSIGNED`), then `ASSIGNED -> DELIVERING -> DELIVERED`

A delivery man must first claim an available order before being able to update its status, and can only act on orders they've claimed.

### Reviews
A review can only be created by the customer who placed the order, and only once that order's status is `DELIVERED` — this ties every review to a verified, completed purchase. One review per order; restaurant-level rating is aggregated on read.

## API Overview

All endpoints are served under the `/api` prefix. Interactive documentation is available at `/docs` (Swagger UI) once the server is running.

| Area | Endpoints |
|---|---|
| **Auth** | `POST /auth/register`, `POST /auth/login` |
| **Users** | `GET/PATCH /users/me`, `GET /users/{id}`, `PATCH /users/{id}` (admin), `GET /users` (admin), `GET/POST /users/me/addresses`, `GET /users/me/restaurants`, `GET/POST/DELETE /users/me/favorites/{restaurant_id}` |
| **Addresses** | `GET/PATCH/DELETE /addresses/{id}` |
| **Restaurants** | `GET/POST /restaurants`, `GET/PATCH/DELETE /restaurants/{id}`, `GET/POST /restaurants/{id}/menus`, `GET/POST /restaurants/{id}/foods`, `GET/POST /restaurants/{id}/categories`, `DELETE /restaurants/{id}/categories/{category_id}`, `GET /restaurants/{id}/orders` |
| **Menus & Menu Items** | `GET/PATCH/DELETE /menus/{id}`, `GET /menus/{id}/items`, `PUT/DELETE /menus/{id}/items/{food_id}` |
| **Foods** | `GET/PATCH/DELETE /foods/{id}`, `GET/POST /foods/{id}/categories`, `DELETE /foods/{id}/categories/{category_id}` |
| **Categories** | `GET/POST /restaurant-categories`, `GET/PATCH/DELETE /restaurant-categories/{id}`, `GET/POST /food-categories`, `GET/PATCH/DELETE /food-categories/{id}` |
| **Cart** | `GET/DELETE /cart`, `POST /cart/items`, `PATCH/DELETE /cart/items/{id}` |
| **Orders** | `GET/POST /orders`, `GET /orders/{id}`, `PATCH /orders/{id}/status`, `POST /orders/{id}/cancel`, `GET /orders/available` (delivery) |
| **Payments** | `POST /orders/{id}/payment`, `GET /fake-checkout/{token}`, `POST /fake-checkout/{token}/confirm`, `GET /payments/{id}`, `GET /payments` (admin) |
| **Wallet & Transactions** | `GET /wallet/balance`, `POST /wallet/topup`, `GET /users/me/transactions`, `GET /transactions/{id}`, `GET /transactions` (admin) |
| **Discounts** | `GET/POST /discounts`, `GET /discounts/{id}`, `GET /discounts/restaurant/{restaurant_id}`, `POST /discounts/{id}/deactivate`, `POST /discounts/preview` |
| **Delivery** | `POST /orders/{id}/claim`, `GET /deliveries/{order_id}`, `GET /users/me/deliveries` |
| **Reviews** | `GET/POST /reviews`, `GET/PATCH/DELETE /reviews/{id}`, `GET /restaurants/{id}/reviews`, `GET /restaurants/{id}/reviews/summary`, `GET /users/me/reviews` |

## Getting Started

```bash
# install dependencies
uv sync

# apply database migrations
uv run alembic upgrade head

# run the dev server
uv run uvicorn main:app --reload
```

Once running, visit `http://127.0.0.1:8000/docs` for the interactive API explorer.

## Database Migrations

Schema changes are managed with Alembic:

```bash
# generate a migration after changing a model
uv run alembic revision --autogenerate -m "description of change"

# apply pending migrations
uv run alembic upgrade head
```

## Project Status

Implemented: auth, users, addresses, restaurants, menus, foods, categories, favorites, cart, orders, payments, wallet, discounts, delivery, reviews.

Not yet implemented: refresh token persistence, order status history/audit log, notifications, admin action logs.