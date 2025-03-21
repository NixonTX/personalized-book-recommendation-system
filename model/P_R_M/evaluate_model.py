import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from hybrid_model import hybrid_score, recommend_books
from tqdm import tqdm  # Import tqdm for progress tracking

# Load factors and similarities
user_factors = np.load("../datasets/user_factors.npy")
item_factors = np.load("../datasets/item_factors.npy")
top_k_similarities = np.load("../datasets/top_k_similarities.npy")
top_k_indices = np.load("../datasets/top_k_indices.npy")

# Load ratings data for evaluation
ratings_df = pd.read_csv("../datasets/bookcrossing_dataset/Ratings.csv", sep=";")
ratings_df["Rating"] = pd.to_numeric(ratings_df["Rating"], errors="coerce")
ratings_df = ratings_df[ratings_df["Rating"] > 0]  # Filter out implicit feedback

# Debug prints to verify alignment
print(f"Number of users in dataset: {ratings_df['User-ID'].nunique()}")
print(f"Shape of user_factors: {user_factors.shape}")  # Should match the number of users in the dataset
print(f"Number of books in dataset: {ratings_df['ISBN'].nunique()}")
print(f"Shape of item_factors: {item_factors.shape}")  # Should match the number of books in the dataset

# Split data into train and test sets
train_df, test_df = train_test_split(ratings_df, test_size=0.2, random_state=42)

# Filter test_df to only include users present in user_factors
valid_user_ids = set(range(user_factors.shape[0]))  # Valid user IDs are 0 to user_factors.shape[0] - 1
test_df = test_df[test_df["User-ID"].isin(valid_user_ids)]

# Debug prints to verify filtered test dataset
print(f"Number of users in test dataset after filtering: {test_df['User-ID'].nunique()}")
print(f"Sample user IDs in test dataset: {test_df['User-ID'].unique()[:5]}")


# Evaluation function
def evaluate_model(test_df, top_n=10):
    precision_scores = []
    recall_scores = []

    # Use tqdm to track progress
    for user_id in tqdm(test_df["User-ID"].unique(), desc="Evaluating users"):
        # Get true interactions for the user
        true_books = test_df[test_df["User-ID"] == user_id]["ISBN"].values

        # Get recommended books
        recommended_books = recommend_books(user_id, train_df, top_n=top_n)

        # Debugging: Print recommendations and true interactions
        print(f"User {user_id}:")
        print(f"Recommended books: {recommended_books}")
        print(f"True interactions: {true_books}")

        # Compute Precision@k and Recall@k
        relevant = len(set(recommended_books) & set(true_books))
        precision_scores.append(relevant / top_n)
        recall_scores.append(relevant / len(true_books))

    # Average Precision@k and Recall@k
    avg_precision = np.mean(precision_scores)
    avg_recall = np.mean(recall_scores)

    return avg_precision, avg_recall

# Evaluate the model
avg_precision, avg_recall = evaluate_model(test_df)
print(f"Average Precision@10: {avg_precision:.4f}")
print(f"Average Recall@10: {avg_recall:.4f}")