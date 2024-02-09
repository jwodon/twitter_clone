"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError


from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test cases for User model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_repr(self):
        """Does the repr method work as expected?"""

        user = User(email="test@test.com", username="testuser", password="testpassword")
        db.session.add(user)
        db.session.commit()

        self.assertEqual(repr(user), f"<User #{user.id}: {user.username}, {user.email}>")

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""

        user1 = User(email="user1@test.com", username="user1", password="password1")
        user2 = User(email="user2@test.com", username="user2", password="password2")
        
        db.session.add_all([user1, user2])
        db.session.commit()

        user1.following.append(user2)
        db.session.commit()

        self.assertTrue(user1.is_following(user2))

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""

        user1 = User(email="user1@test.com", username="user1", password="password1")
        user2 = User(email="user2@test.com", username="user2", password="password2")
        
        db.session.add_all([user1, user2])
        db.session.commit()

        self.assertFalse(user1.is_following(user2))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""

        user1 = User(email="user1@test.com", username="user1", password="password1")
        user2 = User(email="user2@test.com", username="user2", password="password2")
        
        db.session.add_all([user1, user2])
        db.session.commit()

        user1.followers.append(user2)
        db.session.commit()

        self.assertTrue(user1.is_followed_by(user2))

    def test_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""

        user1 = User(email="user1@test.com", username="user1", password="password1")
        user2 = User(email="user2@test.com", username="user2", password="password2")
        
        db.session.add_all([user1, user2])
        db.session.commit()

        self.assertFalse(user1.is_followed_by(user2))

    def test_create_user(self):
        """Does User.create successfully create a new user given valid credentials?"""

        user = User.create(username="testuser", email="test@test.com", password="testpassword")

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@test.com")

    def test_create_duplicate_user(self):
        """Does User.create fail to create a new user if any of the validations fail?"""

        user = User.create(username="testuser", email="test@test.com", password="testpassword")
        duplicate_user = User.create(username="testuser", email="test@test.com", password="testpassword")

        self.assertIsNone(duplicate_user)

    def test_authenticate_valid_credentials(self):
        """Does User.authenticate successfully return a user when given valid credentials?"""

        user = User.create(username="testuser", email="test@test.com", password="testpassword")
        authenticated_user = User.authenticate(username="testuser", password="testpassword")

        self.assertEqual(user, authenticated_user)

    def test_authenticate_invalid_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""

        User.create(username="testuser", email="test@test.com", password="testpassword")
        authenticated_user = User.authenticate(username="invaliduser", password="testpassword")

        self.assertFalse(authenticated_user)

    def test_authenticate_invalid_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""

        User.create(username="testuser", email="test@test.com", password="testpassword")
        authenticated_user = User.authenticate(username="testuser", password="invalidpassword")

        self.assertFalse(authenticated_user)
