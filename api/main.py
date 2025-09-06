# api/main.py
from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI()

# Define a path operation decorator for a GET request to the root URL "/"
@app.get("/")
def read_root():
    """
    This is the root endpoint of the API.
    It returns a welcome message.
    """
    return {"message": "Dermatology AI API is running"}