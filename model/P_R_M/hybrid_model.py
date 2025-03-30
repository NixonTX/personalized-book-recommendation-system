import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle
from joblib import Parallel, delayed
import random
import os

from utils.config import (
    RATINGS_PATH,
    INDEX_TO_ISBN_PATH,
    USER_FACTORS_PATH,
    ITEM_FACTORS_PATH,
    TOP_K_SIMILARITIES_PATH,
    TOP_K_INDICES_PATH
)

# Load all data using centralized paths
with open(INDEX_TO_ISBN_PATH, "rb") as f:

    index_to_isbn = pickle.load(f)

# Create isbn_to_index mapping
isbn_to_index = {isbn: idx for idx, isbn in index_to_isbn.items()}

# Load training data
train_df = pd.read_csv(RATINGS_PATH, sep=";")
train_df["Rating"] = pd.to_numeric(train_df["Rating"], errors="coerce")
train_df = train_df[train_df["Rating"] > 0]  # Filter out implicit feedback

user_factors = np.load(USER_FACTORS_PATH)
item_factors = np.load(ITEM_FACTORS_PATH)
top_k_similarities = np.load(TOP_K_SIMILARITIES_PATH)
top_k_indices = np.load(TOP_K_INDICES_PATH)

# Load the similarity matrix
with open("similarity_matrix.pkl", "rb") as f:
    similarity_matrix = pickle.load(f)

def hybrid_score(user_id, book_id, alpha=0.8):
    cf_score = np.dot(user_factors[user_id], item_factors[book_id])
    cb_score = np.mean(top_k_similarities[book_id])
    return alpha * cf_score + (1 - alpha) * cb_score

def recommend_books(user_id, top_n=10):
    """
    Recommend top-n books for a user based on hybrid scores.
    :param user_id: ID of the user.
    :param top_n: Number of recommendations to generate.
    :return: List of recommended book ISBNs.
    """
    scores = [hybrid_score(user_id, book_id) 
             for book_id in range(item_factors.shape[0])]
    top_books_indices = np.argsort(scores)[-top_n:][::-1]
    return [index_to_isbn[idx] for idx in top_books_indices]
    # Collaborative filtering score
    cf_score = np.dot(user_factors[user_id], item_factors[book_id])
    
    # Content-based filtering score (average similarity to top-k books)
    cb_score = np.mean(top_k_similarities[book_id])
    
    # Hybrid score (weighted average)
    return alpha * cf_score + (1 - alpha) * cb_score

def recommend_books(user_id, train_df=None, top_n=10):
    """
    Recommend top-n books for a user based on hybrid scores.
    :param user_id: ID of the user.
    :param train_df: Training data (optional).
    :param top_n: Number of recommendations to generate.
    :return: List of recommended book ISBNs.
    """
    # Compute hybrid scores for all books
    scores = [hybrid_score(user_id, book_id) for book_id in range(item_factors.shape[0])]
    
    # Sort and get top-n books
    top_books_indices = np.argsort(scores)[-top_n:][::-1]
    
    # Convert indices to ISBNs
    top_books_isbns = [index_to_isbn[idx] for idx in top_books_indices]
    return top_books_isbns

def content_based_recommendations(user_id, train_df, top_n=10):
    """
    Recommend top-n books for a user based on content-based filtering.
    :param user_id: ID of the user.
    :param train_df: Training data.
    :param top_n: Number of recommendations to generate.
    :return: List of recommended book ISBNs.
    """
    user_books = train_df[train_df["User-ID"] == user_id]["ISBN"].values
    user_book_indices = [isbn_to_index[isbn] for isbn in user_books if isbn in isbn_to_index]
    
    mask = np.isin(top_k_indices, user_book_indices)
    scores = np.mean(np.where(mask, top_k_similarities, 0), axis=1)
    
    top_books_indices = np.argsort(scores)[-top_n:][::-1]
    return [index_to_isbn[idx] for idx in top_books_indices]
    # Get user's interacted books from the training data
    user_books = train_df[train_df["User-ID"] == user_id]["ISBN"].values
    
    # Convert user_books to indices
    user_book_indices = [isbn_to_index[isbn] for isbn in user_books if isbn in isbn_to_index]
    
    # Compute content-based scores for all books using broadcasting
    mask = np.isin(top_k_indices, user_book_indices)  # Create a mask for user's interacted books
    scores = np.mean(np.where(mask, top_k_similarities, 0), axis=1)  # Compute mean similarity scores
    
    # Sort and get top-n books
    top_books_indices = np.argsort(scores)[-top_n:][::-1]
    
    # Convert indices to ISBNs
    top_books_isbns = [index_to_isbn[idx] for idx in top_books_indices]
    return top_books_isbns

def evaluate_user(user_id):
    """
    Evaluate Precision@10 and Recall@10 for a single user.
    :param user_id: ID of the user.
    :return: Tuple of (precision, recall).
    """
    true_books = train_df[train_df["User-ID"] == user_id]["ISBN"].values
    if len(true_books) == 0:
        return None
    
    recommended_books = content_based_recommendations(user_id, train_df, top_n=10)
    relevant = len(set(recommended_books) & set(true_books))
    return (relevant / 10, relevant / len(true_books))
    # Get true interactions for the user
    true_books = train_df[train_df["User-ID"] == user_id]["ISBN"].values
    
    # Skip users with no interactions
    if len(true_books) == 0:
        return None
    
    # Get content-based recommendations for the user
    recommended_books = content_based_recommendations(user_id, train_df, top_n=10)
    
    # Compute Precision@10 and Recall@10
    relevant = len(set(recommended_books) & set(true_books))
    precision = relevant / 10
    recall = relevant / len(true_books)
    
    return precision, recall

def evaluate_model():
    """
    Evaluate the model for all users with interactions.
    :return: Average Precision@10 and Recall@10.
    """
    user_interaction_counts = train_df["User-ID"].value_counts()
    users_with_interactions = user_interaction_counts[user_interaction_counts > 0]
    sampled_users = random.sample(list(users_with_interactions.index), 
                                k=int(0.1 * len(users_with_interactions)))

    results = Parallel(n_jobs=-1)(
        delayed(evaluate_user)(user_id) 
        for user_id in tqdm(sampled_users)
    )
    
    results = [r for r in results if r is not None]
    precision_scores, recall_scores = zip(*results)
    
    print(f"Average Precision@10: {np.mean(precision_scores):.4f}")
    print(f"Average Recall@10: {np.mean(recall_scores):.4f}")
    return np.mean(precision_scores), np.mean(recall_scores)

if __name__ == "__main__":
    # Test the recommendation system
    print("Testing recommendation for user 1:")
    print(recommend_books(1))
    
    # Evaluate model performance
    print("\nEvaluating model:")
    evaluate_model()