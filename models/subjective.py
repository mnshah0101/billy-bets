from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import time
import os

"""
serp api request function
"""


def serpapi_get_request(q):
    try:
        params = {
            'q': q,
            'location': "New York",
            'api_key': os.environ['SERP_API_KEY'],
            'engine': 'google'
            # replace 'YOUR_SERPAPI_API_KEY' with your actual key
        }

        response = requests.get('https://serpapi.com/search', params=params)

        return response
    except:
        print("There was an error")


"""
Functions for getting page content
Both web driver and beautiful soup implementations
params: 
    url: string for url
    
return:
    text: string of webpage text
"""


def get_page_content_driver(url):
    try:
        # Initiate driver
        driver = webdriver.Chrome()

        # To open a page
        driver.get(url)

        # Get page HTML source
        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')

        article = soup.find('article', class_='article')

        # get all text
        text = article.get_text()
        return web_text(text)
    except:
        return None


def get_page_content_requests(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check that the GET request was successful
        response.raise_for_status()

        # Parse the response text with Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all text within the body of the HTML
        return clean_up(soup.get_text())

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


def get_search_string(q):
    try:
        response = serpapi_get_request(q)
        response = response.json()
        links = []
        try:
            links = [res['link'] for res in response['organic_results'] if 'espn.com' not in res['link'] and 'twitter' not in res['link']
                     and 'instagram' not in res['link'] and 'facebook' not in res['link'] and 'tiktok' not in res['link']][:3]
        except:
            links = []

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
        "Answer this question as an expert sports AI model interacting with a user: {question} given this web page text from multiple web pages. If there is no text, tell the user there wasnt enough information to answer this. Web Page Text: {web_page_text} ")
    model = ChatOpenAI(model="gpt-3.5-turbo-1106")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    output = chain.invoke({"question": question, "web_page_text": text})
    return output


"""
create google question from chat question
"""


def create_google_query(question):
    prompt = ChatPromptTemplate.from_template(
        "Create a google search that will find relevant articles to answer this question. The most current year is 2024.: {question}.")
    model = ChatOpenAI(model="gpt-3.5-turbo-1106")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    output = chain.invoke({"question": question})
    return output


"""
get subjective question answer
"""


def get_subjective_answer(question):
    google_question = create_google_query(question)
    text = get_search_string(google_question)
    answer = get_answer(question, text)
    return answer


answer = get_subjective_answer(
    "What are UVA's chance in March Madness this season.")

print(answer)
