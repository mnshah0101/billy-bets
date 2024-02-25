from __future__ import absolute_import
from models.subjective import get_subjective_answer
from models.objective import get_objective_answer
from models.chat import get_answer
from flask import Flask, request, jsonify
import sys
sys.path.insert(0, '..')


app = Flask(__name__)


@app.route('/askSubjective')
def ask_subjective():
    question = request.args.get('question', '')
    # Replace this with the code to process the question and generate a response.
    answer = get_subjective_answer(question)
    return jsonify({'question': question, 'answer': answer})


@app.route('/askObjective')
def ask_objective():
    question = request.args.get('question', '')
    # Replace this with the code to process the question and generate a response.
    answer = get_objective_answer(question)
    return jsonify({'question': question, 'answer': answer})

@app.route('/chat')
def chat(): 
    question = request.args.get('question', '')
    # Replace this with the code to process the question and generate a response.
    answer = chat(question)
    return jsonify({'question': question, 'answer': answer})





if __name__ == '__main__':
    app.run(debug=True)
