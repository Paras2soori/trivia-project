import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.user = "postgres"
        self.pwd = "postgres"
        self.host = "localhost"
        self.port = "5432"
        self.database_path = "postgresql://{}:{}@{}:{}/{}".format(self.user,self.pwd,self.host,self.port, self.database_name)
        self.new_question = {
            'id': 24,
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 2,
            'category': 1,
        }
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_retrieve_question(self):
        """Retrieve question test"""
        res = self.client.__get__('/questions?page=1')
        data = json.load(res.data)

        # Status code
        self.assertEqual(data['success'], True)

        # Questions
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 10)

        # Total questions
        self.assertEqual(data['total_questions'], 19)

        # Categories
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
        self.assertIsInstance(data['categories'], dict)
        self.assertEqual(data['current_category'], None)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()