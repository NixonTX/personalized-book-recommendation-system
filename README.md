<h1>Personalized Book Recommendation System</h1>

A scalable backend for personalized book recommendations, powered by a hybrid model combining collaborative and content-based filtering. Built with FastAPI, it uses PostgreSQL for persistent storage and Redis for caching, providing efficient API endpoints for recommendations, book details, ratings, reviews, bookmarks, user management, and search.

---

**Features**

- Personalized Recommendations: Generates top-10 book recommendations per user using a hybrid model.  

- Book Details: Retrieves metadata (title, author, etc.) by ISBN.  

- Ratings: Allows users to submit and store book ratings.  

- Reviews: Supports user-submitted book reviews.  

- Bookmarks: Enables saving books to a personalized list.  

- User Management: Handles user registration, authentication, and profiles.  

- Search: Provides book search by title, author, or metadata.  

- Caching: Uses Redis with a cache-aside pattern (1-hour TTL) for fast data access.  

- Database: Stores data in PostgreSQL with async SQLAlchemy for efficient operations.
  
---


**Tech Stack**

- Language: Python 3.12  
- Framework: FastAPI  
- Database: PostgreSQL (primary), Redis (caching)  
- ORM: SQLAlchemy (async)  
- Migration Tool: Alembic  
- Dependencies: fastapi, uvicorn, sqlalchemy, asyncpg, redis, pydantic, numpy, pandas

---


**Project Structure**
```
L2/
├── alembic/                    # Database migration scripts
│   ├── versions/              # Migration files (e.g., create_reviews_table)
│   ├── env.py
│   ├── script.py.mako
│   └── README
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API endpoints (recommendations, books, etc.)
│   │   ├── models/            # SQLAlchemy models (Book, User, Rating, etc.)
│   │   ├── schemas/           # Pydantic schemas for API validation
│   │   ├── services/          # Business logic for endpoints
│   │   ├── database/          # Database and cache configuration
│   │   ├── core/              # Authentication utilities
│   │   └── utils/             # Helper scripts (config, validators, etc.)
│   ├── tests/                 # Unit tests
├── model/                     # ML model and datasets
│   ├── P_R_M/                # Hybrid recommendation model
│   └── datasets/             # CSV and precomputed data files
├── utils/                     # Global configuration
├── .env                      # Environment variables
├── alembic.ini               # Alembic configuration
└── book_recommendation_backup.sql  # Database backup
```

---

**Setup Instructions**
**Prerequisites**

- Python 3.12+  
- PostgreSQL 15+  
- Redis  
- Git

**Installation**

1. Clone the repository:  
```
git clone https://github.com/NixonTX/personalized-book-recommendation-system.git
cd L2
```

2. Set up a virtual environment:
```
python -m venv mlenv
source mlenv/bin/activate  # Linux/Mac
mlenv\Scripts\activate     # Windows
```


3. Install dependencies:
```
cd backend
pip install -r requirements.txt
```


4. Configure environment variables:  
```
Create a .env file in L2/:  DATABASE_URL=postgresql+asyncpg://bookadmin:0123@localhost/book_recommendation

REDIS_URL=redis://localhost:6379/0
```

---





**Database Setup**

1. Start PostgreSQL and create the database:
```
psql -U postgres
```

```
CREATE DATABASE book_recommendation;
CREATE USER bookadmin WITH PASSWORD '0123';
GRANT ALL PRIVILEGES ON DATABASE book_recommendation TO bookadmin;
\q
```


2. Create the book_app schema and grant privileges:
```
psql -U postgres -d book_recommendation
```


```
CREATE SCHEMA book_app;
GRANT ALL PRIVILEGES ON SCHEMA book_app TO bookadmin;
\q
```


3. Initialize tables with Alembic:
```
cd backend
alembic upgrade head
```


4. Load book data from Books.csv:
```
python -u app/database/load_data.py
```


5. Start Redis:
```  
redis-server
```

---




**Running the Backend**

1. Start the FastAPI server:
``` 
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. Access the API:  

- Swagger UI: http://localhost:8000/docs
- Example:
```
   curl http://localhost:8000/v1/recommend/1
```

---



**API Endpoints**

Method  &emsp;Endpoint  &emsp;Description



Recommendations


GET&emsp;`/api/v1/recommend/{user_id}`&emsp;Get Recommendations


default


GET&emsp;`/api/v1/books/{isbn}`&emsp;Read Book


POST&emsp;`/api/v1/books/`&emsp;Create Book Endpoint



GET
/
Root


Users


POST&emsp;`/api/v1/users/users/`&emsp;Register User


GET&emsp;`/api/v1/users/me`&emsp;Read Users Me


User Ratings


POST&emsp;`/api/v1/ratings/`&emsp;Create Rating


DELETE&emsp;`/api/v1/{isbn}`&emsp;Delete User Rating


GET&emsp;`/api/v1/me/ratings`&emsp;Get My Ratings


User Bookmarks


POST&emsp;`/api/v1/bookmarks/`&emsp;Create Bookmark


DELETE&emsp;`/api/v1/bookmarks/{book_isbn}`&emsp;Delete Bookmark


GET&emsp;`/api/v1/bookmarks/me/`&emsp;Get My Bookmarks


Reviews


POST&emsp;`/api/v1/reviews/`&emsp;Create New Review


PUT&emsp;`/api/v1/reviews/{review_id}`&emsp;Update Existing Review


DELETE&emsp;`/api/v1/reviews/{review_id}`&emsp;Delete User Review


GET&emsp;`/api/v1/reviews/book/{book_isbn}`&emsp;Get Reviews For Book


Search


GET&emsp;`/api/v1/search`&emsp;Search Books


GET&emsp;`/api/v1/search/suggestions`&emsp;Search Suggestions


GET&emsp;`/api/v1/search/history`&emsp;Get Search History


DELETE&emsp;`/api/v1/search/history`&emsp;Clear Search History


DELETE&emsp;`/api/v1/search/history/{query}`&emsp;Delete Search History Item


Authentication


POST&emsp;`/api/v1/auth/register`&emsp;Register


POST&emsp;`/api/v1/auth/login`&emsp;Login


POST&emsp;`/api/v1/auth/logout`&emsp;Logout


POST&emsp;`/api/v1/auth/refresh`&emsp;Refresh Token


POST&emsp;`/api/v1/auth/sessions/revoke`&emsp;Revoke Session


GET&emsp;`/api/v1/auth/sessions`&emsp;List Sessions


GET&emsp;`/api/v1/auth/verify-email/{token}`&emsp;Verify Email


GET&emsp;`/api/v1/auth/debug/session/{session_id}`&emsp;Debug Session


GET&emsp;`/api/v1/auth/status`&emsp;Auth Status

---

**Testing**

Run unit tests to verify API functionality:  
```
cd backend
pytest tests/
```
---

**Contributing**

We welcome contributions! To contribute:  

- Fork the repository.

- Create a feature branch:  git checkout -b feature/xyz

- Commit your changes:  git commit -m "Add xyz feature"

- Push to the branch:  git push origin feature/xyz

- Open a pull request.

---

**License**

MIT License
