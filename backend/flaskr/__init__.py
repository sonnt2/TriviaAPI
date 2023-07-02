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
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def list_catergories():
        categoriesLst = Category.query.order_by(Category.type).all()
        formatted_categoriesLst = {category.id: category.type for category in categoriesLst}

        if len(formatted_categoriesLst) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': formatted_categoriesLst
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
    # define private func paging
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route('/questions', methods=['GET'])
    def list_all_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categoriesLst = Category.query.order_by(Category.type).all()
        formatted_categoriesLst = {category.id: category.type for category in categoriesLst}

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': formatted_categoriesLst,
            'current_category': ''
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # question = Question.query.filler(Question.id == question_id).one_or_none()
            question = Question.query.get(question_id)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })

        except:
            abort(422)

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

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        if not (question and answer and category and difficulty):
            abort(422)

        try:
            createQuestion = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            createQuestion.insert()

            return jsonify({
                'success': True,
                'created': createQuestion.id
            })
        except:
            abort(422)

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
    def search_question():
        body = request.get_json()

        searchTerm = body.get('searchTerm', None)

        if not searchTerm:
            abort(404)

        search_results = Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
        formatted_questionsList = [question.format() for question in search_results]

        return jsonify({
            'success': True,
            'questions': formatted_questionsList,
            'total_questions': len(formatted_questionsList),
            'current_category': ''
        })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def list_question_by_catergory(category_id):
        category =  Category.query.get(category_id)

        if category is None:
            abort(404)

        questionsList = Question.query.filter_by(category=category_id).all()
        formatted_questionsLst = [question.format() for question in questionsList]

        return jsonify({
            'success': True,
            'questions': formatted_questionsLst,
            'total_questions': len(formatted_questionsLst),
            'current_category': category.type
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
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        if quiz_category is None:
            abort(400)

        if quiz_category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=quiz_category['id']).all()

        valid_questionsLst = [question for question in questions if question.id not in previous_questions]
        if len(valid_questionsLst) == 0:
            next_question = ''
        else:
            next_question = random.choice(valid_questionsLst).format()

        return jsonify({
            'success': True,
            'question': next_question
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable'
        }), 422

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    return app

