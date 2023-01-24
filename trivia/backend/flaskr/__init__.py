import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from random import randint

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def pagination(request,collection):
    page = request.args.get('page',1,type=int)
    start  = (page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE
    obj = [each.format() for each in collection]
    objs = obj[start:end]
    return objs

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app,resources={r"*": {'origins':'*'}})

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response
    

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def retrieve_category():
        categories  = Category.query.order_by(Category.id).all()
        category = pagination(request,categories)
        if len(category)==0:
            abort(404)
        return jsonify({
            'success':True,
            'question' : category,
            'total_question':len(categories)
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
    @app.route('/questions')
    def retrieve_questions():
        questions = Question.query.order_by(Question.id).all()
        question = pagination(request,questions)
        categories = Category.query.order_by(Category.id)
        categories_format = {category.id:category.type for category in categories}
        if len(question)==0:
            abort(404)
        return jsonify({
            'success':True,
            'list of questions':question,
            'total questions':len(questions),
            'current_category':None,
            'categories':categories_format
        })





    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:question_id>',methods = ['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id==question_id).one_or_none()
        if question is None:
            abort(404)
        question.delete()
        selection = Question.query.order_by(Question.id).all()
        question_selection = pagination(request,selection)
        categories = Category.query.order_by(Category.id)
        categories_format = {category.id:category.type for category in categories}
        return jsonify({
            'success':True,
            'questions':question_selection,
            'categories':categories_format,
            'total questions':len(selection)

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
    @app.route('/questions/create',methods = ['POST'])
    def create_question():
        questions = request.get_json()
        new_question = questions.get('question',None)
        new_answer = questions.get('answer',None)
        new_category = questions.get('category',None)
        new_difficulty = questions.get('difficulty',None)
        try:
            new_questions = Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
            new_questions.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = pagination(request,selection)
            categories = Category.query.order_by(Category.id)
            categories_format = {category.id:category.type for category in categories}
            return jsonify({
                'success':True,
                'questions':current_questions,
                'category':categories_format,
                'total questions':len(selection),
                
                
                            })

        except:
            abort(400)


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search',methods = ['POST'])
    def question_search():
        body = request.get_json()
        search = body.get('searchTerm',None)
        if search:
            selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
            current_question = pagination(request, selection)
            return jsonify({
                'seccess':True,
                'question':current_question,
                'total question':len(Question.query.all())

            })
        else:
            abort(422)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/question',methods = ['GET'])
    def question_by_category(category_id):
        questions = Question.query.filter(Question.category==category_id).order_by(Question.id).all()
        current_question = pagination(request,questions)
        current_category  = Category.query.filter(Category.id==category_id).one_or_none()

        return jsonify({
            'Success':True,
            'current question':current_question,
            'current category ':current_category.format(),
            'total question':len(current_question)
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
    @app.route('/quiz',methods = ['POST'])
    def quiz():
        try:
            body = request.get_json()
            pre_question = body['previous_questions']
            category = body['quiz_category']['id']
            matching_question = Question.query.filter(Question.category==int(category)).filter(Question.id.not_in(pre_question)).all()
            if len(matching_question)==0:
                abort(422)
            else:
                index = randint(0,len(matching_question)-1)
                return jsonify({
                    'question':matching_question[index].format(),
                })
        except:
            abort(404)
            
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
        "message": f"Not Found: {error}"
        }), 404
    @app.errorhandler(422)
    def errormessage(error):
        return jsonify({
            'success':False,
            'error':422,
            'message':"unprocessable"
        }),422 
    return app


