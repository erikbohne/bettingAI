"""
Started on March 2nd 2023 @ 17:47

Library that is created to scrape fotbmob.com to gather match info
"""

# Import libraries
from bs4 import BeautifulSoup
import requests
import datetime
from nltk.tokenize import word_tokenize
from time import strptime

from values import *

def tokenize_page(url):
    """
    Returns the tokens from the website
    """
    # Request page
    page = requests.get(url)

    # Read and format HTML doc from page
    soup = BeautifulSoup(page.content, "html.parser")
    text = soup.prettify()

    # Tokenize the text so it is iterable
    tokenized = [token for token in word_tokenize(text) if token not in notIncluded]
    
    return tokenized

def get_match_links(teamID, teamUrlName):
    """
    Returns a list of all available matches in a given league
    """
    # Tokenize page
    tokenized = tokenize_page(f"https://www.fotmob.com/teams/{teamID}/fixtures/")

    print(teamUrlName)
    # Find all the urls from the page
    matchUrls = list()
    for token in tokenized:
        if token[:6] == "/match" and teamUrlName in token:
            matchUrls.append(token)

    return matchUrls

def get_match_info(url):
    """
    Returns a dictionary of all information from the match
    """
    # Request page
    tokenized = tokenize_page("https://www.fotmob.com" + url)
    #for i, token in enumerate(tokenized):
    #    if token == "Who":
    #        tokenized = tokenized[i + 3:]
            
    print(tokenized[:500])
    # Set up lists
    home_stats = []
    away_stats = []
    
    # Get time and date of match
    dtg = {
        'weekday' : 0,
        'month' : 0,
        'date' : 0,
        'year' : 0,
        'time' : 0,
        'timezone' : "UTC"
    }
    
    # Block to get stats from match
    home_team = 0
    away_team = 0
    home_score = 0
    away_score = 0
    home_gd = int(home_score) - int(away_score)
    away_gd = home_gd * -1
    
    
    
    
    