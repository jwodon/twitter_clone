"""User View tests."""
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
           
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_add_like(self):
        """Can a logged-in user add a like to a message?"""

        msg = Message(text='Warble!', user_id=self.testuser_id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.post(f'/users/add_like/{msg.id}', follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == msg.id).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_remove_like(self):
        """Can a logged-in user remove a like from a message?"""
        self.test_add_like()

        msg = Message.query.filter_by(user_id=self.testuser_id).first()  

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.post(f'/users/add_like/{msg.id}', follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == msg.id).all()
            self.assertEqual(len(likes), 0)

    def test_show_following(self):
        """Can a logged-in user see who they're following?"""
        # Create another user and then have self.testuser follow them
        new_user = User.signup(username="newuser",
                                email="new@email.com",
                                password="password",
                                image_url=None)
        db.session.add(new_user)
        db.session.commit()

        new_user_id = new_user.id
        self.testuser.following.append(new_user)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.get(f'/users/{self.testuser_id}/following') 
            self.assertEqual(res.status_code, 200)
            self.assertIn('@newuser', res.get_data(as_text=True))