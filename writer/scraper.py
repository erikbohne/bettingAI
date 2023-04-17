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

def get_team_links(leagueID, nTeams=None):
    """
    Returns a list with all team links in a given league
    """
    tokenized = tokenize_page(f"https://www.fotmob.com/leagues/{leagueID}/overview/")
    
    # Find all the urls from the page
    teamUrls = list()
    for token in tokenized:
        if token[:6] == "/teams":
            teamUrls.append(token)
            
    # Remove duplicate links
    teamUrls = [*set(teamUrls)]
    
    if nTeams is not None:
        if len(teamUrls) != nTeams:
            print(f"found {teamUrls} team Urls but there are {nTeams} in the league")
        else:
            return teamUrls
    return teamUrls

def get_match_links(leagueID, season):
    """
    Returns a list of all available matches in a given league
    """
    # Tokenize page
    tokenized = tokenize_page(f"https://www.fotmob.com/leagues/{leagueID}/overview/league?season={season}")

    # Find all the urls from the page
    matchUrls = list()
    for token in tokenized:
        if token[:6] == "/match": # and teamUrlName in token
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
    
    # Get time and date of match
    dtg = gather_dtg(tokenized[:50])
    
    # Check if match is in the past
    today = datetime.date.today() # current day
    difference = today - dtg.date() # find time delta
    if difference.days < 1: # if game is not played yet
        return False
    
    # Get competition name and id
    league = gather_league(tokenized[10:100])
    
    # Block to get init stats from match
    mainInfo = gather_main_info(tokenized[:150])
    # Block to get all stats from match
    statistics = gather_match_statistics(tokenized[1500:4000])
    
    # Get player stats from match
    playerPerformance = gather_player_performance(tokenized[2000:])
    
    return {"dtg" : dtg, "league": league, "maininfo" : mainInfo, "statistics" : statistics}, playerPerformance
    
def get_player_bio(url):  
    """
    Returns a dictionary with information from the player bio on fotmob.
    """
    # Request page
    tokenized = tokenize_page("https://www.fotmob.com" + url)
    
    # Get player info
    playerInfo = gather_player_bio(tokenized)
    
    return playerInfo

def get_name(url):
    """
    Return the full name of the player or team based on the link
    """
    # Get the last part of the link
    subNames = url.split("/")
    
    # Remove all occurrences of "-"
    subNames = subNames[len(subNames) - 1].split("-")
    
    # Return full name with capitalization on the subnames
    return " ".join([subName.capitalize() for subName in subNames])
