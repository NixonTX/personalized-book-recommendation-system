import pandas as pd

# Load Users.csv with Age as string
users_df = pd.read_csv("bookcrossing_dataset/Users.csv", sep=";", dtype={"User-ID": str, "Age": str})
# Clean the Age column
# Replace empty strings and invalid entries with NaN
users_df["Age"] = users_df["Age"].replace({"": None, " canada": None})
# Convert Age to float
users_df["Age"] = pd.to_numeric(users_df["Age"], errors="coerce")


books_df = pd.read_csv("goodreadsbooks/books.csv", on_bad_lines='skip')

# Book-Crossing data
books2_df = pd.read_csv("bookcrossing_dataset/Books.csv", delimiter=";")
ratings_df = pd.read_csv("bookcrossing_dataset/Ratings.csv", sep=";")
# users_df = pd.read_csv("bookcrossing_dataset/Users.csv", sep=";", dtype={"User-ID": str, "Age": float})

# Simulated data
ratings_df = pd.read_csv("UserInteractionData/simulated_ratings.csv")
clicks_df = pd.read_csv("UserInteractionData/simulated_clicks.csv")
search_df = pd.read_csv("UserInteractionData/simulated_search_history.csv")

# Fill missing values in books2_df
books2_df["Author"] = books2_df["Author"].fillna("Unknown")
books2_df["Publisher"] = books2_df["Publisher"].fillna("Unknown")

# Fill missing Age in users_df
users_df["Age"] = users_df["Age"].fillna("Unknown")



print("Missing values in books_df:\n", books_df.isnull().sum())
print("Missing values in books2_df:\n", books2_df.isnull().sum())
print("Missing values in ratings_df:\n", ratings_df.isnull().sum())
print("Missing values in users_df:\n", users_df.isnull().sum())