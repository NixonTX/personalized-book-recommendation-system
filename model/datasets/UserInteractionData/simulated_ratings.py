# In the absence of real data, simulating user interactions

import pandas as pd
import random

users = [f"user_{i}" for i in range(1, 101)]
books = [f"book_{i}" for i in range(1, 1001)]
ratings = []

for user in users:
    for book in random.sample(books, 50):
        rating = random.randint(1, 5)

        ratings.append({"user_id": user, "book_id": book, "rating": rating})

ratings_df = pd.DataFrame(ratings)
ratings_df.to_csv("simulated_ratings.csv", index=False)