Personalized Book Recommendation System
A backend system for personalized book recommendations using a hybrid model combining collaborative and content-based filtering. Built with FastAPI, it leverages PostgreSQL for persistent storage and Redis for caching, delivering efficient and scalable API endpoints for book recommendations, details, ratings, reviews, bookmarks, user management, and search.
Features

Personalized Recommendations: Generates top-10 book recommendations per user via a hybrid model.
Book Details: Retrieves metadata (title, author, etc.) for books by ISBN.
Ratings: Allows users to submit and store book ratings.
Reviews: Supports user reviews for books.
Bookmarks: Enables users to save books to a personalized list.
User Management: Handles user registration, authentication, and profiles.
Search: Provides book search by title, author, or other metadata.
Caching: Uses Redis with a cache-aside pattern for fast access to frequently requested data.
Database: Stores data in PostgreSQL with async SQLAlchemy for efficient operations.

Tech Stack

Language: Python 3.12
Framework: FastAPI
Database: PostgreSQL (primary), Redis (caching)
ORM: SQLAlchemy (async)
Migration Tool: Alembic
Dependencies: fastapi, uvicorn, sqlalchemy, asyncpg, redis, pydantic, numpy, pandas

Project Structure
L2/
├── alembic/                    # Database migration scripts
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API endpoints (recommendations, books, ratings, etc.)
│   │   ├── models/            # SQLAlchemy models (Book, User, Rating, etc.)
│   │   ├── schemas/           # Pydantic schemas for API validation
│   │   ├── services/          # Business logic for API endpoints
│   │   ├── database/          # Database and cache configuration
│   │   └── core/              # Authentication utilities
│   ├── tests/                 # Unit tests
│   └── utils/                 # Helper scripts (config, validators, etc.)
├── model/                     # ML model and datasets
│   ├── P_R_M/                # Hybrid recommendation model
│   └── datasets/             # CSV and precomputed data files
├── utils/                     # Global configuration
├── .env                      # Environment variables
├── alembic.ini               # Alembic configuration
└── book_recommendation_backup.sql  # Database backup

Setup Instructions
Prerequisites

Python 3.12+
PostgreSQL 15+
Redis
Git

Installation

Clone the repository:
git clone <https://github.com/NixonTX/personalized-book-recommendation-system.git>
cd L2


Set up a virtual environment:
python -m venv mlenv
source mlenv/bin/activate  # Linux/Mac
mlenv\Scripts\activate     # Windows


Install dependencies:
cd backend
pip install -r requirements.txt


Configure environment variables:

Create a .env file in L2/:DATABASE_URL=postgresql+asyncpg://bookadmin:0123@localhost/book_recommendation
REDIS_URL=redis://localhost:6379/0





Database Setup

Start PostgreSQL and create the database:
psql -U postgres
CREATE DATABASE book_recommendation;
CREATE USER bookadmin WITH PASSWORD '0123';
GRANT ALL PRIVILEGES ON DATABASE book_recommendation TO bookadmin;
\q


Create the book_app schema and grant privileges:
psql -U postgres -d book_recommendation
CREATE SCHEMA book_app;
GRANT ALL PRIVILEGES ON SCHEMA book_app TO bookadmin;
\q


Initialize tables with Alembic:
cd backend
alembic upgrade head


Load book data from Books.csv:
python -u app/database/load_data.py


Start Redis:
redis-server



Running the Backend

Start the FastAPI server:
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


Access the API:

Swagger UI: http://localhost:8000/docs
Example endpoint: curl http://localhost:8000/v1/recommend/1



API Endpoints



Method
Endpoint
Description



GET
/v1/recommend/{user_id}
Get top-10 book recommendations


GET
/v1/book/{isbn}
Get book details by ISBN


POST
/v1/rate/{user_id}/{isbn}
Submit a book rating


POST
/v1/review/{user_id}/{isbn}
Submit a book review


POST
/v1/bookmark/{user_id}/{isbn}
Add a book to user’s bookmarks


GET
/v1/user/{user_id}
Get user profile


POST
/v1/auth/register
Register a new user


POST
/v1/auth/login
Authenticate a user


GET
/v1/search?query={term}
Search books by title/author


Testing
Run unit tests:
cd backend
pytest tests/

Contributing
Contributions are welcome! Please:

Fork the repository.
Create a feature branch (git checkout -b feature/xyz).
Commit changes (git commit -m "Add xyz feature").
Push to the branch (git push origin feature/xyz).
Open a pull request.

License
MIT License