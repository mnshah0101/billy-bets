import requests
import pandas as pd
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI


load_dotenv()

filename = 'cbb_endpoints.json'


with open(filename, 'r') as file:
    cbb_endpoints = json.load(file)


def make_get_request(base_url, path_params, query_params=None, headers={'Ocp-Apim-Subscription-Key': os.getenv('CBB_API_KEY')}):
    """
    Makes a GET request to a specified URL with given path and query parameters.

    Args:
    base_url (str): The base URL to which the GET request is made.
    path_params (dict): Path parameters to construct the endpoint.
    headers (dict, optional): Headers to include in the request.
    query_params (dict, optional): Query parameters to include in the request.

    Returns:
    DataFrame/JSON/Object: The response data in the desired format, or None if the request fails.
    """

    if path_params:
        endpoint = base_url.format(**path_params)
    else:
        endpoint = base_url

    response = requests.get(endpoint, headers=headers, params=query_params)

    if response.status_code == 200:
        try:
            data = response.json()
            return pd.DataFrame(data) if isinstance(data, list) else data
        except ValueError:
            return response.content
    else:
        print('Error:', response.status_code, response.text)
        return None


def map_info_to_index(df):
    index_to_info = {}
    for index, row in df.iterrows():
        name_key = row['Teams']
        for elem in name_key:
            index_to_info[elem['Name']] = elem['TeamID']

    sorted_teams = dict(sorted(index_to_info.items(), key=lambda x: x[1]))
    return sorted_teams


# Maps name to playerID
def map_name_to_player_id(df):
    name_to_id = {}
    for index, row in df.iterrows():
        name_key = f"{row['Teams']}"
        name_to_id[name_key] = row['Teams']
    return name_to_id


def chat_query(input_1):

    client = OpenAI()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You will be acting as an AI assistant to translate the user question {input_1} and key components into identifying API endpoints from {cbb_endpoints} and parameters relevant to answering the sports question the user has proposed. Only answer in JSON format with {{base_url: , path_parms: ,}}. Current season is 2023. Example: User: What are scores for every single Kansas City Chiefs game this season? Assistant: {{base_url : https://api.sportsdata.io/v3/nfl/scores/json/SchedulesBasic/{{season}}, path_params: {{season: 2023}}. If the specific endpoint does note exist, you can output an endpoint who's output that can be used to get the answer. Only output the JSON. Spell path_params correctly. If the request asks for multiple seasons, add a dictionary entry that specifies all seasons relevant to the question"
            }
        ],
        model="gpt-4",
    )
    response_1 = chat_completion.choices[0].message.content
    return response_1


def format_response(response_1):
    response_json = json.loads(response_1)
    url_template = response_json['base_url']
    params = response_json["path_params"]
    return_df = pd.DataFrame()

    if 'season' in params and type(params['season']) != int:
        for season in params['season']:
            # Update path_params for the current season
            current_path_params = {'season': season, 'team': params['team']}
            # Make the GET request for the current season
            response_df = make_get_request(url_template, current_path_params)
            # Check if response_df is not None and is a DataFrame before concatenating
            if response_df is not None and isinstance(response_df, pd.DataFrame):
                return_df = pd.concat(
                    [return_df, response_df], ignore_index=True)
    else:
        return_df = make_get_request(url_template, params)
    return return_df


def run_agent(return_df, query):
    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
        return_df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = agent.run(query)
    return response


def get_objective_answer(query):
    chat_response = chat_query(query)
    formatted = format_response(chat_response)
    if isinstance(formatted, pd.DataFrame):
        return run_agent(formatted, query)
    else:
        return formatted
