import os

# Get the absolute path to L2/ (where utils/ folder lives)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset paths
DATASETS_DIR = os.path.join(BASE_DIR, "model", "datasets")
RATINGS_PATH = os.path.join(DATASETS_DIR, "bookcrossing_dataset", "Ratings.csv")

# Precomputed data paths
INDEX_TO_ISBN_PATH = os.path.join(DATASETS_DIR, "index_to_isbn.pkl")
USER_FACTORS_PATH = os.path.join(DATASETS_DIR, "user_factors.npy")
ITEM_FACTORS_PATH = os.path.join(DATASETS_DIR, "item_factors.npy")
TOP_K_SIMILARITIES_PATH = os.path.join(DATASETS_DIR, "top_k_similarities.npy")
TOP_K_INDICES_PATH = os.path.join(DATASETS_DIR, "top_k_indices.npy")