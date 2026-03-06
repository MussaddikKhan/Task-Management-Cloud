from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.user_controller import user_router
from controllers.task_controller import router as task_router
from controllers.auth_controller import auth_router
import uvicorn
from mangum import Mangum

# --- SETUP IMPORTS ---
from contextlib import asynccontextmanager
import psycopg2
import os
from core.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# 1. Database Table Banane ka Function (Sync)
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

# 2. FastAPI Lifespan Event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Yeh code Lambda start (Cold Start) hone par chalega
    setup_database_tables()
    yield
    # Yeh code Lambda band hone par chalega (AWS usually isko ignore kar deta hai)
    pass

# 3. App initialization with lifespan
app = FastAPI(lifespan=lifespan, redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://task-manager-frontend-xyz123.s3-website.ap-south-1.amazonaws.com",
        "http://task-manager-frontend-xyz123.s3-website.ap-south-1.amazonaws.com/" # Slash
    ], #Replace it with S3 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(user_router)

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run("main:app")