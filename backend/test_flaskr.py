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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'admin', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Create new question',
            'answer': 'Yes',
            'difficulty': 1,
            'category': 1
        }

        self.new_question_fail = {
            'question': 'Create new question',
            'category': 1
        }

        self.new_quiz = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 1}
        }

        self.new_quiz_fail = {
            'previous_questions': [],
            'quiz_category': None
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    """
    Test case for get catergories(success)
    """
    def test_list_catergories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    """
    Test case for get questions(paginated, 404)
    """
    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_questions_valid_page(self):
        response = self.client().get('/questions?page=10')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    """
    Test case for delete questions(sucesss, fail(422))
    """
    def test_delete_question(self):
        # mock data insert then delete to run it always true
        questionMock = Question(question='Do you want to delete?', answer='Yes', difficulty=1, category=1)
        questionMock.insert()

        # delete the mock question
        response = self.client().delete(f'/questions/{questionMock.id}')
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == questionMock.id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], questionMock.id)
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        response = self.client().delete('/questions/10000000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    """
    Test case for create new questions(sucesss, fail(422))
    """
    def test_create_question(self):
        # Count total question before insert
        current_total_question = len(Question.query.all())
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)
        # Count total question after insert
        after_total_question = len(Question.query.all())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(after_total_question - 1, current_total_question)

    def test_422_if_question_creation_fail(self):
        response = self.client().post('/questions', json=self.new_question_fail)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    """
    Test case for search questions(sucesss, fail(404))
    """
    def test_search_questions(self):
        search_Term = {'searchTerm': 'who'}
        response = self.client().post('/questions/search', json=search_Term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_search_questions(self):
        search_Term = {'searchTerm': ''}
        response = self.client().post('/questions/search', json=search_Term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    """
    Test case for get questions based on categor(sucesss, fail(404))
    """
    def test_list_question_by_catergory(self):
        response = self.client().get('/categories/3/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['current_category']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_list_question_by_catergory(self):
        response = self.client().get('/categories/100/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'Not found')

    """
    Test case for get questions questions to play the quiz(sucesss, fail(400))
    """
    def test_play_quiz(self):
        response = self.client().post('/quizzes', json=self.new_quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_400_play_quiz(self):
        response = self.client().post('/quizzes', json=self.new_quiz_fail)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'Bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()