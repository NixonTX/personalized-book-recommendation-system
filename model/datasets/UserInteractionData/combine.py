import pandas as pd
import os

# print(os.path.exists("../goodreadsbooks/books.csv"))

books_df = pd.read_csv("../goodreadsbooks/books.csv", on_bad_lines='skip')

# Book-Crossing data
books2_df = pd.read_csv("Books.csv")
ratings_df = pd.read_csv("Ratings.csv")
users_df = pd.read_csv("Users.csv")

# Simulated data
ratings_df = pd.read_csv("simulated_ratings.csv")
clicks_df = pd.read_csv("simulated_clicks.csv")
search_df = pd.read_csv("simulated_search_history.csv")

print(books_df.head())

# Inspect Book-Crossing data
print(books2_df.head())
print(ratings_df.head())
print(users_df.head())

# Inspect simulated data
print(ratings_df.head())
print(clicks_df.head())
print(search_df.head())