from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os
from fastapi import FastAPI

# Load environment variables from .env
load_dotenv()

# Fetch variables (use UPPERCASE names if you prefer)
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# Create the SQLAlchemy engine
# Using the Transaction Pooler, so we disable SQLAlchemy client side pooling
# https://docs.sqlalchemy.org/en/20/core/pooling.html#switching-pool-implementations
engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Test the connection
try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")


# ASGI app for uvicorn / FastAPI
app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "running"}
