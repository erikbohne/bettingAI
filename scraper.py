"""
Started on March 2nd 2023 @ 17:47

Library that is created to scrape fotbmob.com to gather match info
"""

# Import libraries
from bs4 import BeautifulSoup
import requests
import datetime
import datetime

from nltk.tokenize import word_tokenize
from time import strptime

# My own libraries
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
    
    # Remove duplicates links
    matchUrls = [*set(matchUrls)]
    
    return matchUrls

def get_player_links(teamID):
    """
    Returns a list off all players in a team
    """
    # Tokenize page
    tokenized = tokenize_page(f"https://www.fotmob.com/teams/{teamID}/squad/")
    
    # Main page and specific page
    main = "//www.fotmob.com"
    player = "/players"
    
    # Find all the urls from the page
    playerUrls = []
    for token in tokenized:
        if token[len(main):len(main) + len(player)] == player:
            if token[len(main):] not in playerUrls:
                playerUrls.append(token[len(main):])
    
    return playerUrls

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
    
    # Check if match is in the past
    today = datetime.date.today() # current day
    difference = today - datetime.date(
                            int(dtg["year"]), 
                            strptime(dtg["month"],'%b').tm_mon, # change month from word -> int
                            int(dtg["date"])) # find time delta
    if difference.days < 1: # if game is not played yet
        return False
    
    # Get competition name and id
    league = gather_league(tokenized[10:50])
    if league["id"] != "47":
        return 0
    
    # Block to get init stats from match
    mainInfo = gather_main_info(tokenized[:70])
    print(mainInfo)
    # Block to get all stats from match
    statistics = gather_match_statistics(tokenized[1500:4000])
    
    # Get player stats from match
    playerPerformance = gather_player_performance(tokenized[2000:])
    
    return {"dtg" : dtg, "league": league, "maininfo" : mainInfo, "statistics" : statistics}
    
def get_player_bio(url):  
    """
    Returns a dictionary with information from the player bio on fotmob.
    """
    # Request page
    tokenized = tokenize_page("https://www.fotmob.com" + url)
    
    # Get player info
    playerInfo = gather_player_bio(tokenized)
    
    return playerInfo
