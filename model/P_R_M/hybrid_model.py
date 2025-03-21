import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle
from joblib import Parallel, delayed
import random

# Load the index-to-ISBN mapping
with open("../datasets/index_to_isbn.pkl", "rb") as f:
    index_to_isbn = pickle.load(f)

# Create isbn_to_index mapping
isbn_to_index = {isbn: idx for idx, isbn in index_to_isbn.items()}

# Load train_df
train_df = pd.read_csv("../datasets/bookcrossing_dataset/Ratings.csv", sep=";")
train_df["Rating"] = pd.to_numeric(train_df["Rating"], errors="coerce")
train_df = train_df[train_df["Rating"] > 0]  # Filter out implicit feedback

# Load precomputed data
user_factors = np.load("../datasets/user_factors.npy")
item_factors = np.load("../datasets/item_factors.npy")
top_k_similarities = np.load("../datasets/top_k_similarities.npy")
top_k_indices = np.load("../datasets/top_k_indices.npy")

def hybrid_score(user_id, book_id, alpha=0.8):
    """
    Compute the hybrid score for a user-item pair.
    :param user_id: ID of the user.
    :param book_id: ID of the book.
    :param alpha: Weight for collaborative filtering score (0 <= alpha <= 1).
    :return: Hybrid score.
    """
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
    # Count the number of interactions per user
    user_interaction_counts = train_df["User-ID"].value_counts()

    # Filter users with at least one interaction
    users_with_interactions = user_interaction_counts[user_interaction_counts > 0]

    # Randomly sample 10% of users
    sampled_users = random.sample(list(users_with_interactions.index), k=int(0.1 * len(users_with_interactions)))

    # Use joblib to evaluate the sampled users in parallel
    results = Parallel(n_jobs=-1)(delayed(evaluate_user)(user_id) for user_id in tqdm(sampled_users))

    # Filter out None results and compute averages
    results = [r for r in results if r is not None]
    precision_scores, recall_scores = zip(*results)
    avg_precision = np.mean(precision_scores)
    avg_recall = np.mean(recall_scores)

    # Print the results
    print(f"Average Precision@10 across sampled users: {avg_precision:.4f}")
    print(f"Average Recall@10 across sampled users: {avg_recall:.4f}")

# Example usage
if __name__ == "__main__":
    evaluate_model()