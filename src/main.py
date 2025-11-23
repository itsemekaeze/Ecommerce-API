from fastapi import FastAPI, Depends
from src.database.core import engine, Base, SessionLocal
from src.database import init_db
from src.entities import users, products, carts, category, order, payments, reviews, shipping_address as table_models 
from src.users.controller import router as user_routes
from src.auth.controller import router as login_routes
from src.payment.controller import router as payment_routes
from src.order.controller import router as order_routes
from src.review.controller import router as review_routes
from src.cart_items.controller import router as cart_routes
from src.category.controller import router as category_routes
from src.products.controller import router as product_routes
from src.address.controller import router as address_routes
from src.admin_dashboard.controller import router as admin_routes
from src.sellers import router as sellers_routes
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.entities.users import UserRole, User
from src.auth.service import get_current_user

table_models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    
    yield
    
    
    print("Shutting down...")

app = FastAPI(
    title="E-Commerce API",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "E-Commerce API with FastAPI",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "categories": "/api/categories",
            "products": "/api/products",
            "cart": "/api/cart",
            "orders": "/api/orders",
            "payments": "/api/payments",
            "reviews": "/api/reviews",
            "admin": "/api/admin",
            "seller": "/api/seller"
        }
    }


@app.get("/check-role")
def check_role(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "role_value": current_user.role,
        "role_type": str(type(current_user.role)),
        "is_admin_enum": current_user.role == UserRole.ADMIN,
        "is_admin_string": str(current_user.role) == "admin",
        "admin_enum_value": UserRole.ADMIN,
        "admin_enum_type": str(type(UserRole.ADMIN))
    }

app.include_router(login_routes)
app.include_router(user_routes)
app.include_router(admin_routes)
app.include_router(sellers_routes)
app.include_router(category_routes)
app.include_router(product_routes)
app.include_router(cart_routes)
app.include_router(address_routes)
app.include_router(order_routes)
app.include_router(payment_routes)
app.include_router(review_routes)



app.mount("/static", StaticFiles(directory="static"), name="static")
