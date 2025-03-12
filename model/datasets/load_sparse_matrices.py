from scipy.io import mmread

# for loading sparse matrices
tfidf_matrix = mmread("tfidf_matrix_sparse.mtx")
user_item_matrix = mmread("user_item_matrix_sparse.mtx")