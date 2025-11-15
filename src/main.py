from fastapi import FastAPI
from src.database.core import engine, Base
from src.entities import users, products, business as table_models 
from src.users.controller import router as user_routes
from src.auth.controller import router as login_routes
from src.email.controller import router as verification_routes
from src.products.controller import router as product_routes
from src.business.controller import router as business_routes
from fastapi.staticfiles import StaticFiles


table_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce API")


@app.get("/")
def root():
    return {"message": "Welcome to Ecommerce FastAPI"}



app.include_router(user_routes)
app.include_router(login_routes)
app.include_router(verification_routes)
app.include_router(business_routes)
app.include_router(product_routes)


app.mount("/static", StaticFiles(directory="static"), name="static")





