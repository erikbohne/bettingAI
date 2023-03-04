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
from gather import *

def tokenize_page(url, match=False):
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
    
    if match: # Get spesified data for matches
        i = 0
        for token in tokenized:
            if token == "matchName":
                information = tokenized[i:]
                break
            i += 1
        return information
    
    return tokenized

def get_match_links(teamID, teamUrlName):
    """
    Returns a list of all available matches in a given league
    """
    # Tokenize page
    tokenized = tokenize_page(f"https://www.fotmob.com/teams/{teamID}/fixtures/")

    # Find all the urls from the page
    matchUrls = list()
    for token in tokenized:
        if token[:6] == "/match" and teamUrlName in token:
            matchUrls.append(token)
    
    print(len(matchUrls))
    # Remove duplicates links
    matchUrls = [*set(matchUrls)]
    print(len(matchUrls))
    
    return matchUrls

def get_match_info(url):
    """
    Returns a dictionary of all information from the match
    """
    # Request page
    tokenized = tokenize_page("https://www.fotmob.com" + url, match=True)
 
    # Set up lists
    home_stats = []
    away_stats = []
    
    # Get time and date of match
    dtg = gather_dtg(tokenized[:50])
    print(dtg)
    
    # Get competition name and id
    league = gather_league(tokenized[10:50])
    print(league)
    
    # Block to get init stats from match
    mainInfo = gather_main_info(tokenized[:70])
    print(mainInfo)
    
    # Block to get all stats from match
    statistics = gather_match_statistics(tokenized[1500:3000])
    
    # Get player stats
    
    
    
    
    