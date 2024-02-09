"""Message model tests."""

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app


db.create_all()


class MessageModelTestCase(TestCase):
    """Test cases for Message model."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user = User(email="test@test.com", username="testuser", password="testpassword")

        db.session.commit()

        self.user = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_create_message(self):
        """Does message.create successfully create a new user given valid credentials?"""

        message = Message.create(text="test", user_id=self.user.id)
        
        db.session.add(message)
        db.session.commit()

        self.assertEqual(self.user.messages[0].text, "test")

