### run in Kaggle(for utilizing the GPU)
# Step 1: Import Libraries
import pickle
import numpy as np
import cupy as cp  # GPU-accelerated NumPy
import cupyx.scipy.sparse as csp  # Sparse matrices on GPU
from scipy.sparse import load_npz
from tqdm import tqdm
import time
import os

# Start the timer
start_time = time.time()

# Step 2: Debug Dataset Path
dataset_path = "/kaggle/input/for-book-recommendation"
if os.path.exists(dataset_path):
    print(f"Dataset directory found: {dataset_path}")
    print("Files in the dataset directory:")
    print(os.listdir(dataset_path))
else:
    print(f"Error: Dataset directory not found at {dataset_path}")
    exit(1)

# Step 3: Load Data
try:
    print("Loading TF-IDF matrix...")
    tfidf_matrix_sparse = load_npz(f"{dataset_path}/tfidf_matrix_sparse/tfidf_matrix_sparse.npz")
    print("TF-IDF matrix loaded successfully!")
except FileNotFoundError:
    print("Error: TF-IDF matrix file not found!")
    exit(1)

# Convert sparse matrix to CuPy sparse matrix (GPU)
try:
    print("Converting TF-IDF matrix to CuPy sparse format and moving to GPU...")
    tfidf_matrix_gpu = csp.csr_matrix(tfidf_matrix_sparse)
    print("TF-IDF matrix converted and moved to GPU successfully!")
except Exception as e:
    print(f"Error converting TF-IDF matrix: {e}")
    exit(1)

try:
    print("Loading book-to-index mapping...")
    with open(f"{dataset_path}/book_to_index/book_to_index.pkl", "rb") as f:
        book_to_index = pickle.load(f)
    print("Book-to-index mapping loaded successfully!")
except FileNotFoundError:
    print("Error: Book-to-index mapping file not found!")
    exit(1)

# Step 4: Set Parameters
n_books = tfidf_matrix_gpu.shape[0]
n_features = tfidf_matrix_gpu.shape[1]
top_k = 100  # Save only top 100 similar books for each book

# Step 5: Compute Cosine Similarity on GPU (Batch Processing)
print("Computing cosine similarity on GPU (batch processing)...")

# Define batch size (adjust based on your GPU memory)
batch_size = 1000  # Process 1000 books at a time
top_k_indices = cp.zeros((n_books, top_k), dtype=int)
top_k_similarities = cp.zeros((n_books, top_k))

# Compute norms for all books
print("Computing norms for all books...")
norms = cp.sqrt(cp.array(tfidf_matrix_gpu.power(2).sum(axis=1)).flatten())

# Process in batches
for i in tqdm(range(0, n_books, batch_size)):
    batch_end = min(i + batch_size, n_books)
    batch = tfidf_matrix_gpu[i:batch_end]

    # Compute dot product for the batch
    batch_similarity = batch.dot(tfidf_matrix_gpu.T)

    # Normalize for cosine similarity
    batch_norms = norms[i:batch_end]
    similarity_matrix_normalized = batch_similarity / cp.outer(batch_norms, norms)

    # Find top-k similarities for the batch
    for j in range(similarity_matrix_normalized.shape[0]):
        similarities = similarity_matrix_normalized[j].get()  # Move row to CPU for argpartition
        top_k_indices_cpu = np.argpartition(similarities, -top_k)[-top_k:]  # Use NumPy for argpartition
        top_k_similarities_cpu = similarities[top_k_indices_cpu]

        # Assign results to CuPy arrays
        top_k_indices[i + j] = cp.array(top_k_indices_cpu)
        top_k_similarities[i + j] = cp.array(top_k_similarities_cpu)

print("Cosine similarity computation completed!")

# Move results back to CPU for saving
top_k_indices = cp.asnumpy(top_k_indices)
top_k_similarities = cp.asnumpy(top_k_similarities)

print("Top-k similarities computed successfully!")

# Step 6: Save Results
try:
    print("Saving top-k similarities and indices...")
    np.save("/kaggle/working/top_k_similarities.npy", top_k_similarities)
    np.save("/kaggle/working/top_k_indices.npy", top_k_indices)
    print("Top-k similarities and indices saved successfully!")
except Exception as e:
    print(f"Error saving top-k similarities and indices: {e}")
    exit(1)

# Step 7: Print Total Time
end_time = time.time()
total_time = end_time - start_time
print(f"Content-Based Filtering: Top-k cosine similarities computed and saved!")
print(f"Total time taken: {total_time:.2f} seconds (~{total_time / 60:.2f} minutes)")