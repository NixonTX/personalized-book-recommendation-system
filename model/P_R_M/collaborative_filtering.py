import numpy as np
from scipy.io import mmread
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD

# Load sparse
user_item_matrix = mmread("../datasets/user_item_matrix_sparse.mtx")

# convert to CSR(Compressed Sparse Row), efficient for mathematical operations.
user_item_matrix = csr_matrix(user_item_matrix)

# Matrix Factorization(SVD)
n_components = 50
svd = TruncatedSVD(n_components=n_components, random_state=42)
user_factors = svd.fit_transform(user_item_matrix)
item_factors = svd.components_.T

# save the latent factors for later use
np.save("../datasets/user_factors.npy", user_factors) # user_factors.npy → Contains the user latent factors (hidden user preferences).
np.save("../datasets/item_factors.npy", item_factors) # item_factors.npy → Contains the item latent factors (hidden item characteristics)

print("Collaborative Filtering: Matrix Factorization completed!")