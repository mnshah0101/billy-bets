from bs4 import BeautifulSoup
import json
import requests


def get_fox_sports_url(link):
    html_doc = requests.get(link).text
    soup = BeautifulSoup(html_doc, 'html.parser')
    scripts = soup.find_all('script', {"type": "application/ld+json"})
    text = ''
    for script in scripts:
        data = json.loads(script.string)
        text += data['articleBody']
    return text
