import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix, save_npz
from scipy.io import mmwrite

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
import pickle
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
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(books2_df["Title_Author"])

# # Save the sparse TF-IDF matrix
# mmwrite("tfidf_matrix_sparse.mtx", tfidf_matrix)
# Saving .npz format
save_npz("tfidf_matrix_sparse.npz", tfidf_matrix)