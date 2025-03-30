from fastapi import APIRouter, HTTPException
from model.P_R_M.hybrid_model import recommend_books

router = APIRouter()

@router.get("/recommend/{user_id}")
async def get_recommendations(user_id: int):
    try:
        print(f"🐛 DEBUG: Recommending for user {user_id}")
        recs = recommend_books(user_id)
        return {"user_id": user_id, "recommendations": recs}
    except Exception as e:
        print(f"❌ Recommendation Error: {e}")
        return {"error": str(e)}