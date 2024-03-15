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

filename = '../cbb_endpoints.json'


with open(filename, 'r') as file:
    cbb_endpoints = json.load(file)

player_ids = '../cbb_playerids.json'

with open(player_ids, 'r') as file:
    cbb_playerids = json.load(file)

team_ids = '../team_ids.json'

with open(team_ids, 'r') as file:
    cbb_teamids = json.load(file)

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

    print(endpoint)

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

def modify_question(input_1):

    client = OpenAI()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You will be acting as an AI assistant to take in the question given by {input_1}, and make it understandable to an LLM. Remove all spelling errors, correct the spelling of player names you think have been spelled incorrectly, and clarify the question based on context - you are an AI assistant that helps users answer questions about college basketball."
        }],
        model="gpt-4",
    )
    response_1 = chat_completion.choices[0].message.content
    print(response_1)
    return response_1



def chat_query(input_1):

    client = OpenAI()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You will be acting as an AI assistant to translate the user question {input_1} and key components into identifying API endpoints from {cbb_endpoints} and parameters relevant to answering the sports question the user has proposed. Use betting trends by team endpoint for all questions related to teh spread. Only answer in JSON format with {{base_url: , path_parms: {{season: , playerid (should just be player name): , etc.}} , question: }}. The base_url should be presented with filler parameters, such as {{season}} and the path_params should contain all the parameters (season, playerid, etc). If team or opponent is a relevant parameter, match the team or opponent to a team or opponent listed in {team_ids} and add that as part of the parameters. Current season is 2023. "}
        ],
        model="gpt-4",
    )
    response_1 = chat_completion.choices[0].message.content
    print(response_1)
    return response_1




def format_response(response_1):
    response_json = json.loads(response_1)
    url_template = response_json['base_url']
    if 'path_params' in response_json:
        params = response_json['path_params']
    else: 
        params = response_json['path_parms']
    return_df = pd.DataFrame()



    if 'playerid' in params: 
        params['playerid'] = cbb_playerids[params['playerid']]
        
    if 'team' in params: 
        params['team'] = cbb_teamids[params['team']]

    if 'opponent' in params: 
        params['opponent'] = cbb_teamids[params['opponent']]
    

    if 'season' in params and type(params['season']) == list:
        for season in params['season']:
            # Update path_params for the current season
            current_path_params = params.copy()
            current_path_params['season'] = season
            # Make the GET request for the current season
            response_df = make_get_request(url_template, current_path_params)
            # Check if response_df is not None and is a DataFrame before concatenating
            if response_df is not None and isinstance(response_df, pd.DataFrame):
                return_df = pd.concat(
                    [return_df, response_df], ignore_index=True)
    else:
        
        return_df = make_get_request(url_template, params)
        

    print(return_df)
    return return_df
def find_answer(query, info): 
    client = OpenAI()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You are an AI assistant that takes in a sports-related query and uses the data given by {info} to answer the {query} "        
            }],
        model="gpt-4"
        )
    response_1 = chat_completion.choices[0].message.content
    print(response_1)
    return response_1


def run_agent(return_df, query):
    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model="gpt-4"),
        return_df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = agent.invoke(query)
    print(response)
    return response


def get_team_id(): 
    df = make_get_request(base_url='https://api.sportsdata.io/v3/cbb/scores/json/teams', path_params=None)
    # Create a dictionary mapping school names to keys
    school_to_key = pd.Series(df.Key.values, index=df.School).to_dict()

    # Convert the dictionary to JSON format
    json_data = json.dumps(school_to_key, indent=4)

    # Write the JSON data to a file
    with open('team_ids.json', 'w') as json_file:
        json_file.write(json_data)

    

def get_objective_answer(query):
    revised_query = modify_question(query)
    chat_response = chat_query(revised_query)
    formatted = format_response(chat_response)
    if isinstance(formatted, pd.DataFrame):
        return run_agent(formatted, revised_query)
    else:
        return find_answer(revised_query, formatted)
    
def get_player_by_active():
    df = make_get_request(base_url=cbb_endpoints['players_by_active'], path_params=None)
    df['FullName'] = df['FirstName'] + ' ' + df['LastName']
    player_id_map = pd.Series(df.PlayerID.values, index=df.FullName).to_dict()
   
    with open('player_id_map.json', 'w') as json_file:
        json.dump(player_id_map, json_file, indent=4)

#print(make_get_request("https://api.sportsdata.io/v3/cbb/stats/json/PlayerGameStatsBySeason/2023/60028205/all", path_params=None))
#print(make_get_request("https://api.sportsdata.io/v3/cbb/stats/json/PlayerGameStatsBySeason/{season}/{playerid}/{numberofgames}", path_params={'season': '2023', 'playerid': 60028205, 'numberofgames': 'all'}))
print(get_objective_answer("How has Kentucky performed against the spread on the road this season when listed as an underdog?"))
