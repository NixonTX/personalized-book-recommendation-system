# L2/services/recommendation_service.py
import numpy as np
from model.P_R_M.hybrid_model import (
    hybrid_score,
    index_to_isbn,
    user_factors,
    item_factors,
    top_k_similarities
)

def recommend_books(user_id, top_n=10):
    """Wrapper function for recommendations"""
    scores = [hybrid_score(user_id, book_id) 
              for book_id in range(item_factors.shape[0])]
    top_books_indices = np.argsort(scores)[-top_n:][::-1]
    return [index_to_isbn[idx] for idx in top_books_indices]