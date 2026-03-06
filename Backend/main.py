from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.user_controller import user_router
from controllers.task_controller import router as task_router
from controllers.auth_controller import auth_router
import uvicorn
from mangum import Mangum
from contextlib import asynccontextmanager
import psycopg2
import os
from core.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# 1. Database Table Setup
def setup_database_tables():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        schema_path = os.path.join(current_dir, "schema.sql")
        
        with open(schema_path, "r") as file:
            sql_script = file.read()
            
        cur.execute(sql_script)
        conn.commit()
        cur.close()
        conn.close()
        print("Database tables verified/created successfully!")
    except Exception as e:
        print(f"Database Setup Error: {e}")

# 2. Lifespan for Lambda Cold Starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database_tables()
    yield

# 3. App Initialization (Strict Routing)
app = FastAPI(lifespan=lifespan, redirect_slashes=False)

# 4. Middleware (Added both slash and non-slash origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://task-manager-frontend-xyz123.s3-website.ap-south-1.amazonaws.com",
        "http://task-manager-frontend-xyz123.s3-website.ap-south-1.amazonaws.com/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Include Routers (Only Once)
app.include_router(auth_router)
app.include_router(task_router)
app.include_router(user_router)

# 6. Lambda Handler
handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run("main:app")