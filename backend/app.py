from fastapi import FastAPI
import sys
import os

print("🐛 DEBUG: Starting app.py")  # Debug line 1

try:
    from model.P_R_M.hybrid_model import recommend_books
    print("🐛 DEBUG: Imports successful")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    raise

app = FastAPI()
print("🐛 DEBUG: FastAPI app created")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/recommend/{user_id}")
async def get_recommendations(user_id: int):
    try:
        print(f"🐛 DEBUG: Recommending for user {user_id}")
        recs = recommend_books(user_id)
        return {"user_id": user_id, "recommendations": recs}
    except Exception as e:
        print(f"❌ Recommendation Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🐛 DEBUG: Starting Uvicorn")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")