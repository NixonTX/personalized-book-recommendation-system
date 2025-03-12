import numpy as np
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm  # For progress bar

# Load the sparse TF-IDF matrix
tfidf_matrix = load_npz("../datasets/tfidf_matrix_sparse.npz")

# Parameters
n_books = tfidf_matrix.shape[0]
chunk_size = 1000  # Adjust based on your system's memory
top_k = 100  # Save only top 100 similar books for each book

# Initialize arrays to store top-k similarities and indices
top_k_similarities = np.zeros((n_books, top_k))
top_k_indices = np.zeros((n_books, top_k), dtype=int)

# Compute cosine similarity in chunks
for i in tqdm(range(0, n_books, chunk_size)):
    chunk = tfidf_matrix[i:i + chunk_size]
    sim_chunk = cosine_similarity(chunk, tfidf_matrix)

    # Find top-k similarities for the current chunk
    for j in range(sim_chunk.shape[0]):
        top_k_indices[i + j] = np.argpartition(sim_chunk[j], -top_k)[-top_k:]
        top_k_similarities[i + j] = sim_chunk[j][top_k_indices[i + j]]

# Save the top-k similarities and indices
np.save("../datasets/top_k_similarities.npy", top_k_similarities)
np.save("../datasets/top_k_indices.npy", top_k_indices)

print("Content-Based Filtering: Top-k cosine similarities computed!")