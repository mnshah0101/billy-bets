import requests
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from subjective import get_subjective_answer
from objective import get_objective_answer

load_dotenv()

def filter_response(query): 
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You are an AI assistant takes in a sports-related question and parses it into a refined query without any grammer or spelling mistakes. Rememeber that the context is sports, so adjust any mistakes you see with that information: {query}. Also determine if {query} is an objective question or a question that requires opinion (subjective). If the questions asks for what people think about a certain topic, it's likely subjective, if it asks for a specific fact, it's objective. Format your response in a json, {{'formatted_question:, bool: (respond with either objective or subjective)}}"
            }

        ],
        model="gpt-3.5-turbo-1106",
    )
    response_1 = chat_completion.choices[0].message.content
    return response_1


def get_answer(query): 
    filtered_string = filter_response(query)
    formatted_dict = json.loads(filtered_string)
    print(formatted_dict)
    if formatted_dict['bool'] == 'subjective': 
        return get_subjective_answer(filtered_string)
    else: 
        return get_objective_answer(filtered_string)

print(get_answer('Rthere any CBB games going on rn?'))


