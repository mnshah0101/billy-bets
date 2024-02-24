from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import time
import os
from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper
os.environ["GOOGLE_CSE_ID"] = ""
os.environ["GOOGLE_API_KEY"] = ""
os.environ['OPENAI_API_KEY'] = ""


"""
Functions for getting page content
Both web driver and beautiful soup implementations
params: 
    url: string for url
    
return:
    text: string of webpage text
"""


def get_page_content_requests(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check that the GET request was successful
        response.raise_for_status()

        # Parse the response text with Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all text within the body of the HTML
        body = soup.find('body')

        if body is None:
            return "NOT_ENOUGH_INFORMATION_ERROR"

        return clean_up(body.get_text())

    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "A Network Error occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "Timeout Error:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "Something went wrong: " + repr(err)


"""
Text processing functions
"""


def clean_up(web_text):
    web_text.replace('\n', '')
    web_text.replace('\t', '')
    # Removes unnecessary whitespaces
    web_text = ' '.join(web_text.split())
    web_text = re.sub(r'\S*@\S*\s?', '', web_text)  # Removes Email
    # Removes Website URL's
    web_text = re.sub(r'http\S+|www.\S+', '', web_text)
    web_text = re.sub(r'@\w+', '', web_text)       # Removes Twitter text
    # Removes button text(ALL CAPS)
    web_text = re.sub(r'\b[A-Z]+\b', '', web_text)

    return web_text


"""
Get text from Google Search
"""


def get_search_string(query):
    try:
        query = query.replace('"', '')
        links = get_links_from_search(query)
        complete_string = ''
        for link in links:
            complete_string += get_page_content_requests(link)
        return complete_string
    except KeyError as err:
        print(err)


"""
get answer from question and https
"""


def get_answer(question, text):
    prompt = ChatPromptTemplate.from_template(
        "Answer this question as an expert sports AI model interacting with a user: {question} given this web page text from a web page. If you cannot answer the question, output 'NOT_ENOUGH_INFORMATION_ERROR' word for word. This is the web pages text: {web_page_text} ")
    model = ChatOpenAI(model="gpt-4-1106-preview")
    output_parser = StrOutputParser()
    try:
        chain = prompt | model | output_parser
        output = chain.invoke({"question": question, "web_page_text": text})
        return output
    except KeyError as err:
        print(err)
        return "NOT_ENOUGH_INFORMATION_ERROR"


"""
create google question from chat question
"""


def create_google_query(question):
    prompt = ChatPromptTemplate.from_template(
        "Create a google search that will find relevant articles to answer this question. The most current year is 2024. This is the question: {question}.")
    model = ChatOpenAI(model="gpt-4-1106-preview")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    output = chain.invoke({"question": question})

    return output


"""
get subjective question answer
"""


def get_subjective_answer(question):
    google_question = create_google_query(question)
    links = get_links_from_search(google_question)

    print(len(links))

    for link in links:
        print("trying link: ", link)
        text = get_page_content_requests(link)
        answer = get_answer(question, text)
        if ("NOT_ENOUGH_INFORMATION_ERROR" not in answer):
            return answer

    return "Sorry, I don't have enough information to answer that question."


def get_links_from_search(query):
    search = GoogleSearchAPIWrapper()
    query = query.replace('"', '')
    response = search.results(query, 10)

    links = [res['link']
             for res in response if 'espn' and 'youtube' and 'reddit' and 'instagram' and 'video' and 'facebook' and 'twitter' and 'tiktok' not in res['link']]

    return links
