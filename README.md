# 🛍️ E-Commerce FastAPI Application

A full-featured e-commerce REST API built with FastAPI, PostgreSQL, and SQLAlchemy. This application provides comprehensive user management, business profiles, product management, and email verification functionality.

## ✨ Features

### 👤 User Management
- **User Registration** with email verification
- **JWT Authentication** (OAuth2 with Password Bearer)
- **Password Hashing** with bcrypt and SHA-256
- **Profile Picture Upload** with automatic resizing
- **User Profile Management**

### 🏢 Business Management
- **Automatic Business Profile** creation on user registration
- **Business Profile Updates** (name, city, region, description)
- **Business Logo Upload**
- **Business Listing**

### 📦 Product Management
- **Create Products** with pricing and categories
- **Update Products** with automatic discount calculation
- **Delete Products** (owner authorization required)
- **Product Image Upload** with automatic resizing (200x200)
- **Get All Products**
- **Get Individual Product** with business details
- **Automatic Percentage Discount** calculation

### 📧 Email System
- **Email Verification** with JWT tokens (24-hour expiry)
- **FastMail & SMTP** fallback support
- **Beautiful HTML Email Templates**
- **Background Task Processing**

### 🔐 Security
- **JWT Token Authentication**
- **Password Hashing** (SHA-256 + bcrypt)
- **Role-Based Access Control**
- **Owner Verification** for updates/deletes
- **Email Verification** required for login

## 🚀 Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Authentication:** JWT (PyJWT)
- **Password Hashing:** bcrypt + hashlib
- **Email:** FastMail + SMTP
- **Image Processing:** Pillow (PIL)
- **File Storage:** Local static files

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- SMTP server (Gmail recommended)

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd ecommerce-fastapi
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib bcrypt python-multipart pillow fastapi-mail python-dotenv
```

### 4. Create `.env` file
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/ecommerce_db

# JWT Secret (minimum 32 characters)
SECRET=your-super-secret-key-here-min-32-chars

# Email Configuration (Gmail)
EMAIL=your-email@gmail.com
PASSWORD=your-gmail-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Frontend URL
FRONTEND_URL=http://localhost:8000
```

**Note:** For Gmail, you need to create an [App Password](https://myaccount.google.com/apppasswords)

### 5. Create static directories
```bash
mkdir -p static/images
mkdir -p static/profile_pictures
mkdir -p templates
```

### 6. Create database tables
```bash
# Tables will be auto-created on first run
python -c "from src.database.core import engine, Base; from src.entities import users, products, business; Base.metadata.create_all(bind=engine)"
```

## 🏃 Running the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📚 API Endpoints

### 🔐 Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/token` | Login and get JWT token | No |

**Login Request:**
```json
{
  "username": "user@example.com",
  "password": "your-password"
}
```

### 👥 Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/users/registeration` | Register new user | No |
| GET | `/users/me` | Get current user profile | Yes |
| POST | `/users/upload/profile` | Upload profile picture | Yes |

**Registration Request:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

### 📧 Email Verification

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/verification?token=<jwt_token>` | Verify email address | No |

### 🏢 Business

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/business/` | Get all businesses | Yes |
| PUT | `/business/{id}` | Update business profile | Yes |

**Update Business Request:**
```json
{
  "business_name": "My Store",
  "city": "Lagos",
  "region": "Lagos State",
  "business_description": "We sell quality products"
}
```

### 📦 Products

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/products/create` | Create new product | Yes |
| GET | `/products/` | Get all products | Yes |
| GET | `/products/{id}` | Get single product | Yes |
| PUT | `/products/{id}` | Update product | Yes |
| DELETE | `/products/{id}` | Delete product | Yes |
| POST | `/products/{id}/upload` | Upload product image | Yes |

**Create Product Request:**
```json
{
  "name": "iPhone 15 Pro",
  "categories": "Electronics",
  "description": "Latest iPhone model",
  "original_price": 1200.00,
  "new_price": 999.99,
  "profile_image": "default.jpg"
}
```

**Update Product Request:**
```json
{
  "new_price": 899.99
}
```

## 🔑 Authentication Flow

1. **Register User** → `POST /users/registeration`
2. **Check Email** → Click verification link
3. **Verify Email** → `GET /verification?token=...`
4. **Login** → `POST /auth/token` (returns access token)
5. **Use Token** → Add header: `Authorization: Bearer <token>`

## 📁 Project Structure

```
ecommerce-fastapi/
├── src/
│   ├── auth/
│   │   ├── controller.py      # Login endpoints
│   │   ├── service.py          # JWT & password functions
│   │   └── models.py           # Token models
│   ├── users/
│   │   ├── controller.py       # User endpoints
│   │   ├── service.py          # User business logic
│   │   └── models.py           # User schemas
│   ├── business/
│   │   ├── controller.py       # Business endpoints
│   │   ├── service.py          # Business logic
│   │   └── models.py           # Business schemas
│   ├── products/
│   │   ├── controller.py       # Product endpoints
│   │   ├── service.py          # Product logic
│   │   └── models.py           # Product schemas
│   ├── email/
│   │   ├── controller.py       # Email verification endpoint
│   │   └── service.py          # Email sending logic
│   ├── entities/
│   │   ├── users.py            # User database model
│   │   ├── business.py         # Business database model
│   │   └── products.py         # Product database model
│   └── database/
│       └── core.py             # Database connection
├── static/
│   └── images/                 # Uploaded images
├── templates/
│   └── verification.html       # Email verification page
├── .env                        # Environment variables
├── main.py                     # Application entry point
└── requirements.txt            # Dependencies
```

## 🗄️ Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password` (Hashed)
- `is_verified` (Boolean)
- `created_at` (Timestamp)

### Business Table
- `id` (Primary Key)
- `business_name`
- `city`
- `region`
- `business_description`
- `logo`
- `business_id` (Foreign Key → Users)

### Products Table
- `id` (Primary Key)
- `name`
- `categories`
- `description`
- `original_price` (Decimal)
- `new_price` (Decimal)
- `percentage_discount` (Float)
- `product_image`
- `offer_expiration_date` (Timestamp)
- `profile_id` (Foreign Key → Business)

## 🛡️ Security Features

- ✅ **JWT Token Authentication** with expiry
- ✅ **Password Hashing** (SHA-256 + bcrypt with 12 rounds)
- ✅ **Email Verification** required before login
- ✅ **Owner Authorization** for updates/deletes
- ✅ **SQL Injection Protection** via SQLAlchemy ORM
- ✅ **File Upload Validation** (type, size, extension)
- ✅ **CORS Ready** (can be configured)

## 🧪 Testing the API

### Using Swagger UI (Recommended)
1. Go to `http://localhost:8000/docs`
2. Register a new user
3. Verify email (check console for verification link)
4. Click "Authorize" button
5. Login to get token
6. Use token for authenticated requests

### Using cURL
```bash
# Register User
curl -X POST "http://localhost:8000/users/registeration" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# Get User Profile (with token)
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer <your-token-here>"
```

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |
| `SECRET` | JWT secret key (32+ chars) | `your-super-secret-key-here` |
| `EMAIL` | SMTP email address | `your-email@gmail.com` |
| `PASSWORD` | Email app password | `your-app-password` |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `FRONTEND_URL` | Frontend URL for links | `http://localhost:8000` |

## 🐛 Common Issues & Solutions

### 1. Email Verification Error
**Issue:** FastMail configuration warning
**Solution:** Ensure `EMAIL` in `.env` is a valid email address

### 2. Database Connection Error
**Issue:** `psycopg2.OperationalError: server closed the connection`
**Solution:** 
- Restart PostgreSQL service
- Add `pool_pre_ping=True` to database engine

### 3. Login 403 Error
**Issue:** "Please verify your email before logging in"
**Solution:** Click verification link in email or manually update database:
```sql
UPDATE users SET is_verified = TRUE WHERE email = 'your-email@example.com';
```

### 4. File Upload Error
**Issue:** "Invalid file extension"
**Solution:** Only `.jpg`, `.jpeg`, `.png` files are allowed

## 🚀 Production Deployment

### 1. Update `.env` for production
```env
DATABASE_URL=postgresql://user:pass@production-host:5432/db
SECRET=generate-a-strong-secret-key-here
FRONTEND_URL=https://yourdomain.com
```

### 2. Install production server
```bash
pip install gunicorn
```

### 3. Run with Gunicorn
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI**