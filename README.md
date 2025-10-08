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

Backend designed by me (Dike Ebuka Christopher).