import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix, csr_matrix
from sklearn.decomposition import TruncatedSVD
import pickle

ratings_df = pd.read_csv("../datasets/bookcrossing_dataset/Ratings.csv", sep=";")
ratings_df["Rating"] = pd.to_numeric(ratings_df["Rating"], errors="coerce")
ratings_df = ratings_df[ratings_df["Rating"] > 0]  # Filter out implicit feedback

# Create mappings for user and book IDs to indices
user_to_index = {user_id: idx for idx, user_id in enumerate(ratings_df["User-ID"].unique())}
book_to_index = {book_id: idx for idx, book_id in enumerate(ratings_df["ISBN"].unique())}

# # Debug prints to verify mappings
# print(f"User to index sample: {list(user_to_index.items())[:5]}")
# print(f"Book to index sample: {list(book_to_index.items())[:5]}")

# Create the user-item matrix in lil format for efficient updates
num_users = len(user_to_index)
num_books = len(book_to_index)
user_item_matrix = lil_matrix((num_users, num_books), dtype=np.float32)

# Populate the user-item matrix with ratings
for idx, row in ratings_df.iterrows():
    user_idx = user_to_index[row["User-ID"]]
    book_idx = book_to_index[row["ISBN"]]
    user_item_matrix[user_idx, book_idx] = row["Rating"]
    if idx % 10000 == 0:  # Print progress every 10,000 rows
        print(f"Processed {idx + 1} / {len(ratings_df)} rows...")

# Convert to csr format for efficient computations
user_item_matrix = user_item_matrix.tocsr()

# Debug prints to check sparsity
sparsity = 1 - (user_item_matrix.nnz / (user_item_matrix.shape[0] * user_item_matrix.shape[1]))
print(f"Sparsity of user-item matrix: {sparsity:.4f}")

# Matrix Factorization (SVD)
n_components = 50
svd = TruncatedSVD(n_components=n_components, random_state=42)
user_factors = svd.fit_transform(user_item_matrix)
item_factors = svd.components_.T

# print(f"User factors sample: {user_factors[:5]}")
# print(f"Item factors sample: {item_factors[:5]}")

# Save the latent factors for later use
np.save("../datasets/user_factors.npy", user_factors)
np.save("../datasets/item_factors.npy", item_factors)

# Save the mappings for later use
with open("../datasets/user_to_index.pkl", "wb") as f:
    pickle.dump(user_to_index, f)
with open("../datasets/book_to_index.pkl", "wb") as f:
    pickle.dump(book_to_index, f)

print("Collaborative Filtering: Matrix Factorization completed!")