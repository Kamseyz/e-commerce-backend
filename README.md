# ShopStream API — E-Commerce Backend (Django + DRF)

## Overview

ShopStream is a modern e-commerce backend built with Django Rest Framework (DRF).  
It supports:

- JWT Authentication
- Cloudinary image uploads
- Paystack payment integration
- Auto-generated API documentation via Swagger (drf-yasg)
- Custom user model

## Project Structure

```
e-commerce_backend/
│
├── backend/
│   ├── shopstream/
│   │   ├── .env
│   │   ├── manage.py
│   │   ├── db.sqlite3
│   │   ├── shopstream/        # Core project files (settings, urls, etc.)
│   │   ├── product/           # Product, Cart, and Order app
│   │   ├── payment/           # Paystack integration
│   │   ├── users/             # Custom user authentication
│   │
│   ├── requirements.txt
│
├── README.md
├── LICENCE
└── .gitignore
```

## Setup Instructions

1. **Clone the repository**
    ```sh
    git clone <your_repo_url>
    cd e-commerce_backend/backend/shopstream
    ```

2. **Create and activate a virtual environment**
    ```sh
    python -m venv myenv
    source myenv/bin/activate  # on Mac/Linux
    myenv\Scripts\activate     # on Windows
    ```

3. **Install dependencies**
    ```sh
    pip install -r ../requirements.txt
    ```

4. **Run migrations**
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Create a superuser**
    ```sh
    python manage.py createsuperuser
    ```

6. **Run the development server**
    ```sh
    python manage.py runserver
    ```

## Magic Link Login

ShopStream supports passwordless authentication via Magic Links.  
When a user logs in or registers, they receive a unique link via email that can be consumed to obtain JWT tokens.


### 🔑 Magic Link Login Flow

1. **User Receives Magic Link**

   - After login (`POST /login/`), the backend sends a magic link to the user's email.
   - Example link:
     ```
     http://localhost:5173/login/magic?token=8b9769e9-20e1-414a-9deb-76f9de476ed6&redirect=/dashboard
     ```

2. **Consume the Token**

   - The frontend extracts the `token` from the URL and sends it to the backend:
     ```
     POST /consume-link/
     Content-Type: application/json

     {
       "token": "8b9769e9-20e1-414a-9deb-76f9de476ed6"
     }
     ```
   - **Response:**
     ```json
     {
       "access": "<your-access-token>"
     }
     ```
   - The refresh token is set as an HTTP-only cookie.

3. **Use the JWT Access Token**

   - Include the access token in the Authorization header to call protected endpoints:
     ```
     GET /api/products/
     Authorization: Bearer <your-access-token>
     ```

4. **Refresh the Access Token**

   - When the access token expires, refresh it using the cookie-based refresh token:
     ```
     POST /refresh/
     ```
   - **Response:**
     ```json
     {
       "access": "<new-access-token>"
     }
     ```

5. **Logout (Optional)**

   - Call the logout endpoint to invalidate tokens and remove the refresh cookie:
     ```
     POST /logout/
     ```

---

**Notes:**
- All endpoints are relative to your backend root (e.g., `/login/`, `/consume-link/`, `/refresh/`, `/logout/`).
- The refresh token is stored as an HTTP-only cookie for security.
- Update the frontend URL and redirect path as needed for your deployment.


## Environment Variables Setup

Before running the project, create a `.env` file in your project root (next to `manage.py`) and add the following keys:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here

# Cloudinary CDN
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-cloud-key
CLOUDINARY_API_SECRET=your-cloud-secret

# Brevo Email Service
BREVO_API_KEY=your-brevo-key

# Paystack Payment
PAYSTACK_KEY=your-paystack-secret
```

## API Documentation (Swagger)

API documentation is auto-generated via drf-yasg.

- **Swagger:** [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
- **ReDoc:** [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

> **Note:**  
> When Swagger loads your endpoints, it runs without authentication.  
> If you filter by `self.request.user`, add this check in your views:
> ```python
> if getattr(self, 'swagger_fake_view', False) or self.request.user.is_anonymous:
>     return Model.objects.none()
> ```
> Add this to all views using `self.request.user` in `get_queryset()`.

## API Endpoints (Examples)

| Method | Endpoint                | Description           |
|--------|-------------------------|-----------------------|
| POST   | /api/token/             | Get JWT token         |
| POST   | /api/token/refresh/     | Refresh JWT token     |
| GET    | /api/products/          | List all products     |
| POST   | /api/cart/              | Add to cart           |
| GET    | /api/orders/            | View user orders      |

## Webhooks (Optional via Ngrok)

To test Paystack webhooks locally:

```sh
ngrok http 8000
```

Then update your Paystack webhook URL to:

```
https://<your_ngrok_subdomain>.ngrok.io/webhook/paystack/
```
Also, don't forget to add `<your_ngrok_subdomain>.ngrok.io` to your allowed hosts in the settings.

> Using Ngrok is optional — it's only needed for testing live webhook responses locally.

## Development Notes

- Throttling is enabled in REST_FRAMEWORK settings.
- Use `IsAuthenticated` for endpoints requiring login.
- Replace `pain@xyz.com` in `DEFAULT_FROM_EMAIL` with your actual domain.
- Update allowed hosts and webhook URLs for production.

---

## Credits

Backend designed by me.
