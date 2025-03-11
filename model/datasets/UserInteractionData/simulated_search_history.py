import pandas as pd
import random

genres = ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Non-Fiction"]
users = [f"user_{i}" for i in range(1, 101)]

search_history = []
for user in users:
    for _ in range(10):
        query = random.choice(genres)
        search_history.append({"user_id": user, "query": query})

search_df = pd.DataFrame(search_history)
search_df.to_csv("simulated_search_history.csv", index=False)
print("Simulated search history saved to 'simulated_search_history.csv'")