"""
Initialize the database with tables.
Run this script once to create all database tables.
"""

from src.config.database import init_database

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
    print("Tables created: users, connections, messages, ratings")
