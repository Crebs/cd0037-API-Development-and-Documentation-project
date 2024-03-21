import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    with app.app_context():
        if test_config is None:
            setup_db(app)
        else:
            database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
            setup_db(app, database_path=database_path)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})


    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })



    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]

        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'questions': formatted_questions[start:end],
            'total_questions': len(questions),
            'categories': formatted_categories,
            'current_category': None  # Modify this part as needed
        })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)

        question.delete()
        return jsonify({
            'success': True,
            'deleted': question_id
        })


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        if not all([new_question, new_answer, new_category, new_difficulty]):
            abort(422)
        
        try:
            # Try to convert category and difficulty to integers to ensure they are valid
            new_category = int(new_category)
            new_difficulty = int(new_difficulty)
        except ValueError:
            abort(422)

        question = Question(question=new_question, answer=new_answer,
                        difficulty=new_difficulty, category=new_category)
        question.insert()

        return jsonify({
            'success': True,
            'created': question.id
        })


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', '')

        if not body or 'searchTerm' not in body or not body['searchTerm']:
            # Return a 400 error with a JSON response
            return jsonify({
                'success': False,
                'message': 'bad request'
            }), 400

        search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        formatted_questions = [question.format() for question in search_results]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(search_results),
            'current_category': None  # Modify this as necessary
        })


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        category = Category.query.filter_by(id=category_id).first()
        if not category:
            # If the category does not exist, return a 404 response
            return jsonify({
                'success': False,
                'message': 'resource not found'
            }), 404
        
        questions = Question.query.filter_by(category=str(category_id)).all()
        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': category_id
        })


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()

        if not body:
            return jsonify({
                'success': False,
                'message': 'bad request'
            }), 400

        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

        if previous_questions is None or not isinstance(previous_questions, list):
            return jsonify({
                'success': False,
                'message': 'bad request'
            }), 400

        if not quiz_category or 'id' not in quiz_category:
            return jsonify({
                'success': False,
                'message': 'bad request'
            }), 400

        if quiz_category['id'] == 0:
            questions_query = Question.query.filter(Question.id.notin_(previous_questions))
        else:
            try:
                category_id = int(quiz_category['id'])
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'bad request'
                }), 400
            questions_query = Question.query.filter_by(category=str(category_id)).filter(Question.id.notin_(previous_questions))

        new_question = questions_query.first()

        return jsonify({
            'success': True,
            'question': new_question.format() if new_question else None
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422


    return app

