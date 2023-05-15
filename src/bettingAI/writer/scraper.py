"""
Started on March 2nd 2023 @ 17:47

Library that is created to scrape fotbmob.com to gather match info
"""

import datetime
from time import strptime
from typing import List, Optional, Dict, Union, Any, Tuple

import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize

# My own libraries
from bettingAI.writer.values import *
from bettingAI.writer.gather import *


def tokenize_page(url: str, match: Optional[bool] = False) -> List[str]:
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

    information = []
    if match:  # Get spesified data for matches
        i = 0
        for token in tokenized:
            if token == "matchName":
                information = tokenized[i:]
                break
            i += 1
        return information

    return tokenized


def get_team_links(leagueID: int, nTeams: Optional[str] = None) -> List[str]:
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
            print(f"found {len(teamUrls)} team Urls but there are {nTeams} in the league")
        else:
            return teamUrls
    return teamUrls


def get_match_links(leagueID: int, season: str) -> List[str]:
    """
    Returns a list of all available matches in a given league
    """
    # Tokenize page
    tokenized = tokenize_page(
        f"https://www.fotmob.com/leagues/{leagueID}/overview/league?season={season}"
    )

    # Find all the urls from the page
    matchUrls = list()
    for token in tokenized:
        if token[:6] == "/match":  # and teamUrlName in token
            matchUrls.append(token)

    # Remove duplicates links
    matchUrls = [*set(matchUrls)]

    return matchUrls


def get_player_links(teamID: int) -> List[str]:
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
        if token[len(main) : len(main) + len(player)] == player:
            if token[len(main) :] not in playerUrls:
                playerUrls.append(token[len(main) :])

    return playerUrls


def get_match_info(
    url: str,
    justMain=False
) -> Union[bool, Tuple[Dict[str, Any], Dict[Any, Any]]]:
    """
    Returns a dictionary of all information from the match
    """
    # Request page
    tokenized = tokenize_page("https://www.fotmob.com" + url, match=True)

    if not justMain:
        # Get time and date of match
        dtg = gather_dtg(tokenized[:50])

        # Check if match is in the past
        today = datetime.date.today()  # current day
        difference = today - dtg.date()  # find time delta
        if difference.days < 1:  # if game is not played yet
            return False, False

        # Get competition name and id
        league = gather_league(tokenized[10:100])

    # Block to get init stats from match
    mainInfo = gather_main_info(tokenized[:150])
    
    if justMain:
        return mainInfo

    # Block to get all stats from match
    statistics = gather_match_statistics(tokenized[:6000])

    # Get player stats from match
    if statistics is not None:
        playerPerformance = gather_player_performance(tokenized[2000:])
    else:
        playerPerformance = None

    return {
        "dtg": dtg,
        "league": league,
        "maininfo": mainInfo,
        "statistics": statistics,
    }, playerPerformance
    
def get_next_match_info(
    url: str,
) -> Union[bool, Dict[Any, Any]]:
    """
    Returns a necessary info about upcoming matches
    """
    # Request page
    tokenized = tokenize_page("https://www.fotmob.com" + url, match=True)

    # Get time and date of match
    dtg = gather_dtg(tokenized[:50])

    # Check if match is in the past
    today = datetime.date.today()  # current day
    difference = today - dtg.date()  # find time delta
    if not -7 <= difference.days < 0:  # makes sure the game is within a week ahead of time
        #return False
        pass

    info = gather_next_match_info(tokenized[:200])
    
    # Get competition name and id
    league = gather_league(tokenized[10:100])
    
    if info is not None:
        return {
            "leagueID": league["id"],
            "teamID" : info[0],
            "opponentID" : info[1],
            "date" : dtg
        }
    else:
        return False


def get_player_bio(url: str) -> Dict[str, Union[Dict[str, Any], List]]:
    """
    Returns a dictionary with information from the player bio on fotmob.
    """
    # Request page
    tokenized = tokenize_page("https://www.fotmob.com" + url)

    # Get player info
    playerInfo = gather_player_bio(tokenized)

    return playerInfo


def get_name(url: str) -> str:
    """
    Return the full name of the player or team based on the link
    """
    # Get the last part of the link
    subNames = url.split("/")

    # Remove all occurrences of "-"
    subNames = subNames[len(subNames) - 1].split("-")

    # Return full name with capitalization on the subnames
    return " ".join([subName.capitalize() for subName in subNames])
