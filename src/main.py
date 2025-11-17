from fastapi import FastAPI
from src.database.core import engine, Base
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
from src.admin import router as admin_routes
from src.sellers import router as sellers_routes
from fastapi.staticfiles import StaticFiles


table_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce API")


@app.get("/")
def root():
    return {
        "message": "E-Commerce API",
        "version": "1.0.0",
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





