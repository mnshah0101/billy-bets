from objective import get_objective_answer
from subjective import get_subjective_answer
import requests
import pandas as pd
import os
import time
import json
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()


def filter_response(query):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You are an AI assistant takes in a sports-related question and parses it into a refined query without any grammar or spelling mistakes. Remember that the context is sports, so adjust any mistakes you see with that information: {query}. Also determine if {query} is an objective question or a question that requires opinion (subjective). If the questions asks a current event (this week) or for what people or experts think about a certain topic or about tactics/strategies in a game, it's likely subjective, if it asks for a specific fact, it's objective. Regardless, if the question asks about this current week, categorize it as subjective. Format your response in a json, {{formatted_question: question, bool: (respond with either objective or subjective)}}"
            } 

        ],
        model="gpt-4",
    )
    response_1 = chat_completion.choices[0].message.content
    return response_1


def conversational_answer(query, answer):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You are Billy Bets, a seasoned veteran sports betting assistant AI tasked at answering user questions from a response given from an AI model. You have the personality of Billy Walters, the greatest sports bettor of all time. You are a statistical, direct, and effective as an assistant. Given the question: {query} and the model response: {answer}, provide a response to the user's question. Your tone should reflect that of a research analyst and be informative. Give the information the model gives you in a way that is easy to understand and informative. Do not provide any additional information."
            }
        ],
        model="gpt-3.5-turbo",
    )
    response_1 = chat_completion.choices[0].message.content
    return response_1


def get_answer(query):
    start = time.time()
    filtered_string = filter_response(query)
    print(filtered_string)
    formatted_dict = json.loads(filtered_string)
    answer = ''
    if formatted_dict['bool'].lower() == 'subjective':
        answer = get_subjective_answer(filtered_string)
    else:
        answer = get_objective_answer(filtered_string)
    endtime = time.time()

    length = str(round(endtime - start, 2)) + " seconds"

    return_answer = conversational_answer(query, answer)

    return_dict = {"question": query, "answer": return_answer, "time": length}
    return return_dict


print(get_answer("How has Kentucky performed against the spread on the road this season when an underdog?"))