# Little Lemon API

A RESTful API for the Little Lemon restaurant, built with Django and Django REST Framework. It supports menu browsing, cart management, order placement, and role-based staff administration (Managers and Delivery Crew).

## Features

- Token-based authentication via [Djoser](https://djoser.readthedocs.io/)
- Role-based access control: **Admin**, **Manager**, **Delivery Crew**, and **Customer**
- Menu item and category management with filtering, searching, sorting, and pagination
- Shopping cart per user
- Order placement, assignment to delivery crew, and status updates
- API throttling for anonymous and authenticated users

## Tech Stack

- Python / Django
- Django REST Framework
- Djoser (authentication)
- SQLite (default database)

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone or extract the project, then move into it
cd LittleLemon

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install django djangorestframework djoser
```

### Running the Server

```bash
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

### Test Accounts

The bundled `db.sqlite3` includes the following seeded accounts for local testing:

| Role          | Username    | Password    |
|---------------|-------------|-------------|
| Admin         | admin       | admin123    |
| Manager       | manager1    | Test1234!   |
| Delivery Crew | delivery1   | Test1234!   |
| Customer      | customer1   | Test1234!   |

> These are development-only credentials seeded for local testing. Replace them and update `SECRET_KEY` / `DEBUG` before deploying anywhere public.

## Authentication

Authentication is handled by Djoser and DRF's Token Authentication.

| Endpoint | Method | Description |
|---|---|---|
| `/auth/users/` | POST | Register a new user |
| `/auth/token/login/` | POST | Obtain an auth token |
| `/auth/token/logout/` | POST | Invalidate the current token |

Include the token on subsequent requests:

```
Authorization: Token <your_token_here>
```

## API Endpoints

All endpoints below are prefixed with `/api/`.

### Menu Items

| Endpoint | Method | Access | Description |
|---|---|---|---|
| `/menu-items` | GET | Authenticated | List menu items. Supports `category`, `featured`, `search`, `ordering`, `perpage`, `page` query params |
| `/menu-items` | POST | Manager/Admin | Create a menu item |
| `/menu-items/<id>` | GET | Authenticated | Retrieve a single menu item |
| `/menu-items/<id>` | PUT/PATCH | Manager/Admin | Update a menu item |
| `/menu-items/<id>` | DELETE | Manager/Admin | Delete a menu item |

**Query parameters for `GET /menu-items`:**
- `category` — filter by category title (contains match)
- `featured` — filter by featured flag (`true`/`false`)
- `search` — filter by title (contains match)
- `ordering` — one of `price`, `-price`, `title`, `-title`, `id`, `-id`
- `perpage` — page size (default 10)
- `page` — page number (default 1)

### Categories

| Endpoint | Method | Access | Description |
|---|---|---|---|
| `/categories` | GET | Authenticated | List categories |
| `/categories` | POST | Manager/Admin | Create a category |

### Cart

| Endpoint | Method | Access | Description |
|---|---|---|---|
| `/cart/menu-items` | GET | Customer | View items in the current user's cart |
| `/cart/menu-items` | POST | Customer | Add a menu item to the cart |
| `/cart/menu-items` | DELETE | Customer | Clear the current user's cart |

> Managers and delivery crew cannot access cart endpoints.

### Orders

| Endpoint | Method | Access | Description |
|---|---|---|---|
| `/orders` | GET | Authenticated | List orders. Managers/Admin see all orders, delivery crew see their assigned orders, customers see their own |
| `/orders` | POST | Customer | Place an order from the current cart (cart must not be empty) |
| `/orders/<id>` | GET | Authenticated | Retrieve an order (owner, assigned delivery crew, or Manager/Admin) |
| `/orders/<id>` | PUT/PATCH | Manager/Admin | Update `delivery_crew` and/or `status` |
| `/orders/<id>` | PUT/PATCH | Delivery Crew | Update `status` on their assigned orders |
| `/orders/<id>` | DELETE | Manager/Admin | Delete an order |

### User Group Management (Manager/Admin only)

| Endpoint | Method | Description |
|---|---|---|
| `/groups/manager/users` | GET | List users in the Manager group |
| `/groups/manager/users` | POST | Add a user to the Manager group (body: `username`) |
| `/groups/manager/users/<userId>` | DELETE | Remove a user from the Manager group |
| `/groups/delivery-crew/users` | GET | List users in the Delivery Crew group |
| `/groups/delivery-crew/users` | POST | Add a user to the Delivery Crew group (body: `username`) |
| `/groups/delivery-crew/users/<userId>` | DELETE | Remove a user from the Delivery Crew group |

## Data Model

- **Category** — `slug`, `title`
- **MenuItem** — `title`, `price`, `featured`, `category` (FK)
- **Cart** — `user` (FK), `menuitem` (FK), `quantity`, `unit_price`, `price` — unique per (user, menuitem)
- **Order** — `user` (FK), `delivery_crew` (FK, nullable), `status`, `total`, `date`
- **OrderItem** — `order` (FK), `menuitem` (FK), `quantity`, `unit_price`, `price` — unique per (order, menuitem)

## Permissions Summary

| Role | Menu Items | Categories | Cart | Orders | Groups |
|---|---|---|---|---|---|
| Admin/Manager | Full CRUD | Full CRUD | No access | View all, assign/update status, delete | Manage |
| Delivery Crew | Read only | Read only | No access | View assigned, update status only | No access |
| Customer | Read only | Read only | Full access | Create, view own | No access |

## Throttling

- Anonymous users: 100 requests/day
- Authenticated users: 1000 requests/day

## Running Tests

```bash
python manage.py test
```

## Project Structure

```
LittleLemon/
├── LittleLemon/            # Project settings, root URLs, WSGI/ASGI
├── LittleLemonAPI/          # App: models, views, serializers, urls, tests
│   └── migrations/
├── db.sqlite3                # Seeded development database
└── manage.py
```
