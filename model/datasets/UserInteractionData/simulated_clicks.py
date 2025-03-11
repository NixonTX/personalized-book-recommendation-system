import pandas as pd
import random

genres = ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Non-Fiction"]
users = [f"user_{i}" for i in range(1, 101)]
books = [f"book_{i}" for i in range(1, 1001)] 

book_genres = {book: random.sample(genres, k=random.randint(1, 3)) for book in books}

user_preferences = {user: random.choice(genres) for user in users}

clicks = []
for user in users:
    preferred_genre = user_preferences[user]
    for book in random.sample(books, 20):
        if preferred_genre in book_genres[book]:
            clicks.append({"user_id": user, "book_id": book})

clicks_df = pd.DataFrame(clicks)
clicks_df.to_csv("simulated_clicks.csv", index=False)
print("Simulated clicks saved to 'simulated_clicks.csv'")