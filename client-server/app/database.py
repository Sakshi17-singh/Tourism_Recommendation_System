from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
import os

# -----------------------------
# SQLAlchemy setup
# -----------------------------
# Use absolute path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tourism.db')
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

print(f"📊 Using database: {DB_PATH}")

# -----------------------------
# Flask-SQLAlchemy setup
# -----------------------------
db = SQLAlchemy()

def init_db():
    """Initialize database with all models"""
    # Import all models to ensure they're registered with Base
    from . import models
    
    # Create all tables for SQLAlchemy models
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialized successfully")

def init_flask_db(app):
    """Initialize Flask-SQLAlchemy tables (Chat, Message, SearchHistory)"""
    with app.app_context():
        db.create_all()
        print("✅ Flask-SQLAlchemy tables created successfully")
