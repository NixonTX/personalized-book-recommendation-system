"""
Run this in Kaggle notebook

# Install FAISS
# !pip install faiss-gpu

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix, save_npz
from scipy.io import mmwrite
import pickle
from tqdm import tqdm  # For progress bars
from sklearn.decomposition import TruncatedSVD  # For dimensionality reduction
import faiss  # For approximate nearest neighbors

# Configurable parameters (set manually in notebook)
k = 100  # Number of nearest neighbors
nprobe = 10  # FAISS nprobe for accuracy vs speed

# Load Users.csv with error handling
print("Loading Users.csv...")
try:
    users_df = pd.read_csv("/kaggle/input/books-for/Users.csv", sep=";", dtype={"User-ID": str, "Age": str})
except FileNotFoundError:
    print("Error: Users.csv not found! Adjust the file path for your environment.")
    raise
# Replace empty strings and invalid entries with NaN
users_df["Age"] = users_df["Age"].replace({"": None, " canada": None})
# Convert Age to float
users_df["Age"] = pd.to_numeric(users_df["Age"], errors="coerce")
# Fill missing Age in users_df
users_df["Age"] = users_df["Age"].fillna("Unknown")
# Save the encoded users data
users_df.to_csv("encoded_users.csv", index=False)

# Load Books.csv with error handling
print("Loading Books.csv...")
try:
    books_df = pd.read_csv("/kaggle/input/books-for/Books.csv", delimiter=";")
except FileNotFoundError:
    print("Error: Books.csv not found! Adjust the file path for your environment.")
    raise

# Create a mapping from index to ISBN
index_to_isbn = {idx: isbn for idx, isbn in enumerate(books_df["ISBN"])}

# Save the mapping to a file
with open("index_to_isbn.pkl", "wb") as f:
    pickle.dump(index_to_isbn, f)

# Fill missing values in books_df
books_df["Author"] = books_df["Author"].fillna("Unknown")
books_df["Publisher"] = books_df["Publisher"].fillna("Unknown")
# Ensure Year is numeric
books_df["Year"] = pd.to_numeric(books_df["Year"], errors="coerce")

# Save the encoded books data
books_df.to_csv("encoded_books.csv", index=False)

# Load Ratings.csv with error handling
print("Loading Ratings.csv...")
try:
    ratings_df = pd.read_csv("/kaggle/input/books-for/Ratings.csv", sep=";")
except FileNotFoundError:
    print("Error: Ratings.csv not found! Adjust the file path for your environment.")
    raise

# Ensure ratings are numeric
ratings_df["Rating"] = pd.to_numeric(ratings_df["Rating"], errors="coerce")
# Filter out implicit feedback (ratings = 0)
ratings_df = ratings_df[ratings_df["Rating"] > 0]

# Filter users with at least 5 ratings
print("Filtering users with at least 5 ratings...")
user_counts = ratings_df["User-ID"].value_counts()
ratings_df = ratings_df[ratings_df["User-ID"].isin(user_counts[user_counts >= 5].index)]

# Filter books with at least 10 ratings
print("Filtering books with at least 10 ratings...")
book_counts = ratings_df["ISBN"].value_counts()
ratings_df = ratings_df[ratings_df["ISBN"].isin(book_counts[book_counts >= 10].index)]

# Map User-ID and ISBN to categorical codes for sparse matrix indices
ratings_df["User-ID"] = ratings_df["User-ID"].astype("category").cat.codes
ratings_df["ISBN"] = ratings_df["ISBN"].astype("category").cat.codes

# Create a sparse user-item matrix
print("Creating sparse user-item matrix...")
user_item_matrix = csr_matrix((ratings_df["Rating"], 
                               (ratings_df["User-ID"], ratings_df["ISBN"])))

# Save the sparse matrix
mmwrite("user_item_matrix_sparse.mtx", user_item_matrix)

# Vectorize Title and Author for content-based filtering
books_df["Title"] = books_df["Title"].fillna("Unknown")
books_df["Author"] = books_df["Author"].fillna("Unknown")
books_df["Title_Author"] = books_df["Title"] + " " + books_df["Author"]

# Create TF-IDF vectorizer
print("Creating TF-IDF vectorizer...")
tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = tfidf.fit_transform(books_df["Title_Author"])

# Save the TF-IDF matrix (optional, for reference)
save_npz("tfidf_matrix_sparse.npz", tfidf_matrix)

# Save the TF-IDF vectorizer
with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(tfidf, f)

# Reduce dimensionality using Truncated SVD
print("Reducing dimensionality using Truncated SVD...")
svd = TruncatedSVD(n_components=1000)  # Reduce to 1000 features
tfidf_matrix_reduced = svd.fit_transform(tfidf_matrix)

# Save the SVD model for new book projections
with open("svd_model.pkl", "wb") as f:
    pickle.dump(svd, f)

# Convert TF-IDF matrix to float32 (required by FAISS)
tfidf_matrix_reduced = tfidf_matrix_reduced.astype(np.float32)

# Build FAISS index on GPU
print("Building FAISS index on GPU...")
try:
    res = faiss.StandardGpuResources()  # Use GPU resources
    index = faiss.IndexFlatIP(tfidf_matrix_reduced.shape[1])  # Inner product for cosine similarity
    gpu_index = faiss.index_cpu_to_gpu(res, 0, index)  # Move index to GPU
    gpu_index.add(tfidf_matrix_reduced)  # Add data to the index
except Exception as e:
    print(f"Error building FAISS index: {e}")
    raise

# Search for top-k similarities
print(f"Computing top-{k} similarities using FAISS on GPU...")
gpu_index.nprobe = nprobe  # Set nprobe for accuracy vs speed
similarities, indices = gpu_index.search(tfidf_matrix_reduced, k)

# Save the top-k indices and similarities
np.save("top_k_indices.npy", indices)
np.save("top_k_similarities.npy", similarities)

# Save the FAISS index for dynamic queries
print("Saving FAISS index...")
cpu_index = faiss.index_gpu_to_cpu(gpu_index)  # Move back to CPU for saving
faiss.write_index(cpu_index, "faiss_index.index")

print("Preprocessing completed and files saved!")
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix, save_npz
from scipy.io import mmwrite
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# Load Users.csv with Age as string
users_df = pd.read_csv("bookcrossing_dataset/Users.csv", sep=";", dtype={"User-ID": str, "Age": str})
# Replace empty strings and invalid entries with NaN
users_df["Age"] = users_df["Age"].replace({"": None, " canada": None})
# Convert Age to float
users_df["Age"] = pd.to_numeric(users_df["Age"], errors="coerce")
# Fill missing Age in users_df
users_df["Age"] = users_df["Age"].fillna("Unknown")
# Save the encoded users data
users_df.to_csv("encoded_users.csv", index=False)

# Load books data
books_df = pd.read_csv("goodreadsbooks/books.csv", on_bad_lines='skip')
books2_df = pd.read_csv("bookcrossing_dataset/Books.csv", delimiter=";")

# Create a mapping from index to ISBN
index_to_isbn = {idx: isbn for idx, isbn in enumerate(books2_df["ISBN"])}

# Save the mapping to a file
with open("index_to_isbn.pkl", "wb") as f:
    pickle.dump(index_to_isbn, f)

# Fill missing values in books2_df
books2_df["Author"] = books2_df["Author"].fillna("Unknown")
books2_df["Publisher"] = books2_df["Publisher"].fillna("Unknown")
# Ensure Year is numeric
books2_df["Year"] = pd.to_numeric(books2_df["Year"], errors="coerce")

# Encode Author and Publisher
author_encoder = LabelEncoder()
books2_df["Author_Encoded"] = author_encoder.fit_transform(books2_df["Author"])

publisher_encoder = LabelEncoder()
books2_df["Publisher_Encoded"] = publisher_encoder.fit_transform(books2_df["Publisher"])

# One-hot encode language_code in books_df
books_df = pd.get_dummies(books_df, columns=["language_code"])

# Save the encoded books data
books2_df.to_csv("encoded_books2.csv", index=False)
books_df.to_csv("encoded_books.csv", index=False)

# Load ratings data
ratings_df = pd.read_csv("bookcrossing_dataset/Ratings.csv", sep=";")

# Ensure ratings are numeric
ratings_df["Rating"] = pd.to_numeric(ratings_df["Rating"], errors="coerce")
# Filter out implicit feedback (ratings = 0)
ratings_df = ratings_df[ratings_df["Rating"] > 0]

# Filter users with at least 5 ratings
user_counts = ratings_df["User-ID"].value_counts()
ratings_df = ratings_df[ratings_df["User-ID"].isin(user_counts[user_counts >= 5].index)]

# Filter books with at least 10 ratings
book_counts = ratings_df["ISBN"].value_counts()
ratings_df = ratings_df[ratings_df["ISBN"].isin(book_counts[book_counts >= 10].index)]

# Map User-ID and ISBN to categorical codes for sparse matrix indices
ratings_df["User-ID"] = ratings_df["User-ID"].astype("category").cat.codes
ratings_df["ISBN"] = ratings_df["ISBN"].astype("category").cat.codes

# Create a sparse user-item matrix
user_item_matrix = csr_matrix((ratings_df["Rating"], 
                               (ratings_df["User-ID"], ratings_df["ISBN"])))

# Save the sparse matrix
mmwrite("user_item_matrix_sparse.mtx", user_item_matrix)

# Load simulated data
clicks_df = pd.read_csv("UserInteractionData/simulated_clicks.csv")
search_df = pd.read_csv("UserInteractionData/simulated_search_history.csv")

# Encode query in search_df
query_encoder = LabelEncoder()
search_df["query_encoded"] = query_encoder.fit_transform(search_df["query"])

# Save the encoded simulated data
clicks_df.to_csv("encoded_clicks.csv", index=False)
search_df.to_csv("encoded_search.csv", index=False)

# Vectorize Title and Author for content-based filtering
books2_df["Title_Author"] = books2_df["Title"] + " " + books2_df["Author"]
tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = tfidf.fit_transform(books2_df["Title_Author"])

# Save the TF-IDF matrix
save_npz("tfidf_matrix_sparse.npz", tfidf_matrix)

# Save the TF-IDF vectorizer
with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(tfidf, f)

# Compute cosine similarity matrix
similarity_matrix = cosine_similarity(tfidf_matrix)

# Save the similarity matrix
with open("similarity_matrix.pkl", "wb") as f:
    pickle.dump(similarity_matrix, f)

print("Preprocessing completed and files saved!")
