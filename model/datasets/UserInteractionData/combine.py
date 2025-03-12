import pandas as pd
import os

# print(os.path.exists("../goodreadsbooks/books.csv"))

books_df = pd.read_csv("../goodreadsbooks/books.csv", on_bad_lines='skip')

# Book-Crossing data
books2_df = pd.read_csv("../bookcrossing_dataset/Books.csv", delimiter=";")
ratings_df = pd.read_csv("../bookcrossing_dataset/Ratings.csv", sep=";")
users_df = pd.read_csv("../bookcrossing_dataset/Users.csv", sep=";")

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


print("Missing values in books_df:\n", books_df.isnull().sum())
print("Missing values in books2_df:\n", books2_df.isnull().sum())
print("Missing values in ratings_df:\n", ratings_df.isnull().sum())
print("Missing values in users_df:\n", users_df.isnull().sum())