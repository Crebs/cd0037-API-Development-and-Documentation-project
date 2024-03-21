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
        self.database_name = "trivia_test"
        self.database_path = "postgresql://rzcrebs:l1nds2y@{}/{}".format('localhost:5432', self.database_name)
        
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })

        self.client = self.app.test_client

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        """Test GET all categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertIsInstance(data['categories'], dict)
    
    def test_get_paginated_questions(self):
        """Test GET paginated questions"""
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_delete_question(self):
        """Test DELETE question"""
        with self.app.app_context():
            question = Question(question="Test Question", answer="Test Answer", category="1", difficulty=1)
            question.insert()
            question_id = question.id

        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
    
    def test_create_new_question(self):
        """Test POST new question"""
        new_question = {
            'question': 'New Question',
            'answer': 'New Answer',
            'difficulty': 1,
            'category': '1'
        }

        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_search_questions(self):
        """Test POST search questions"""
        search_term = {'searchTerm': 'title'}
        response = self.client().post('/questions/search', json=search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['questions'], list)

    def test_get_questions_by_category(self):
        """Test GET questions by category"""
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_play_quiz(self):
        """Test POST play quiz"""
        quiz_info = {'previous_questions': [], 'quiz_category': {'id': '1'}}
        response = self.client().post('/quizzes', json=quiz_info)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404_delete_nonexistent_question(self):
        """Test DELETE non-existent question"""
        response = self.client().delete('/questions/999999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_404_get_nonexistent_category(self):
        """Test GET non-existent category"""
        response = self.client().get('/categories/999999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_422_create_question_invalid_data(self):
        """Test POST create new question with invalid data"""
        new_question = {
            'question': '',
            'answer': '',
            'difficulty': '',
            'category': ''
        }
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_400_search_questions_invalid_body(self):
        """Test POST search questions with invalid body"""
        response = self.client().post('/questions/search', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)  
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')
    
    def test_404_get_questions_by_nonexistent_category(self):
        """Test GET questions by non-existent category"""
        response = self.client().get('/categories/999999/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_400_play_quiz_incomplete_data(self):
        """Test POST play quiz with incomplete data"""
        quiz_info = {}  # Incomplete data, e.g., missing 'quiz_category' or 'previous_questions'
        response = self.client().post('/quizzes', json=quiz_info)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)  # Assumes your API returns 400 for incomplete data
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')















# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()