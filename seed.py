"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import app, db
from models import User, Message, Follows

# Create an application context
with app.app_context():
    # Drop all tables
    db.drop_all()
    # Create all tables
    db.create_all()

    # Load data from CSV files and insert into the database
    with open('generator/users.csv') as users:
        db.session.bulk_insert_mappings(User, DictReader(users))

    with open('generator/messages.csv') as messages:
        db.session.bulk_insert_mappings(Message, DictReader(messages))

    with open('generator/follows.csv') as follows:
        db.session.bulk_insert_mappings(Follows, DictReader(follows))

    # Commit the changes
    db.session.commit()

