from fastapi import FastAPI
# Import routers from api/v1
from .api.v1 import recommendations
from backend.app.api.v1 import books
from backend.app.api.v1 import users


print("🐛 DEBUG: Starting app.py")

try:
    from model.P_R_M.hybrid_model import recommend_books
    print("🐛 DEBUG: Imports successful")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    raise

app = FastAPI()
print("🐛 DEBUG: FastAPI app created")


# Include routers
app.include_router(recommendations.router, prefix="/api/v1")

app.include_router(books.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")



@app.get("/")
async def root():
    return {"message": "Congrats, It Works!"}

if __name__ == "__main__":
    print("🐛 DEBUG: Starting Uvicorn")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")