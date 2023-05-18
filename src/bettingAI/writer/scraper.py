"""
scraper.py

A library for scraping match information from fotmob.com.

This library allows you to scrape match information from fotmob.com 
to gather data about matches, teams, and players. 
It provides functions for fetching match details, team information, player information, and more.

Created on March 2, 2023, at 17:47.

Author: Erik Nymo Bohne
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


def tokenize_page(
    url: str,
    match: Optional[bool] = False
    ) -> List[str]:
    """Tokenizes the content of a web page and returns the tokens.

    The function requests the content of the specified URL and tokenizes the HTML document using the NLTK library.
    The resulting tokens are returned as a list.

    Args:
        url (str): The URL of the web page to tokenize.
        match (bool, optional): Specifies whether to extract specified data for matches. Default is False.

    Returns:
        List[str]: A list of tokens extracted from the web page content.

    Note:
        If the `match` parameter is set to True, the function searches for specific data related to matches.
        It returns a subset of tokens starting from the "matchName" token.
        This behavior is useful when extracting specific information from match-related pages.
        If the `match` parameter is False or not provided, the function tokenizes the entire web page content.

    Example:
        tokens = tokenize_page("https://www.fotmob.com/match/3901289", match=True)
        # Returns a list of tokens containing specified match-related data.
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


def get_team_links(
    leagueID: int,
    nTeams: Optional[str] = None
    ) -> List[str]:
    """Retrieves and returns a list of team links for a given league.

    The function fetches the web page of the specified league from the FotMob website.
    It extracts the URLs of all teams participating in the league and returns them as a list.

    Args:
        leagueID (int): The ID of the league.
        nTeams (str, optional): Specifies the expected number of teams in the league.
            If provided, the function verifies that the number of retrieved team links matches the expected number.
            If the numbers don't match, a warning message is printed. Default is None.

    Returns:
        List[str]: A list of team links belonging to the league.

    Note:
        The function uses the `tokenize_page` function to tokenize the league overview page.
        It searches for URLs that start with "/teams" to identify the team links.

    Example:
        team_links = get_team_links(47)
        # Returns a list of team links for the league with ID 47.
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


def get_match_links(
    leagueID: int,
    season: str = ""
    ) -> List[str]:
    """
    Retrieves and returns a list of match links for a given league and season.

    The function fetches the web page of the specified league and season from the FotMob website.
    It extracts the URLs of all available matches in the league and returns them as a list.

    Args:
        leagueID (int): The ID of the league.
        season (str): The season for which match links are requested. It should be in the format "YYYY-YYYY" (e.g., "2022-2023").

    Returns:
        List[str]: A list of match links belonging to the specified league and season.

    Note:
        The function uses the `tokenize_page` function to tokenize the league overview page for the given season.
        It searches for URLs that start with "/match" to identify the match links.

    Example:
        match_links = get_match_links(47, "2022-2023")
        # Returns a list of match links for the league with ID 47 and the season "2022-2023".
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


def get_player_links(
    teamID: int
    ) -> List[str]:
    """Retrieves and returns a list of player links for a given team.

    The function fetches the web page of the specified team from the FotMob website.
    It extracts the URLs of all players in the team and returns them as a list.

    Args:
        teamID (int): The ID of the team.

    Returns:
        List[str]: A list of player links belonging to the specified team.

    Note:
        The function uses the `tokenize_page` function to tokenize the team squad page.
        It searches for URLs that represent individual players.

    Example:
        player_links = get_player_links(123)
        # Returns a list of player links for the team with ID 123.
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
    """Retrieves and returns information about a match.

    The function fetches the web page of the specified match from the FotMob website.
    It extracts various information from the match page, such as the date and time, competition details,
    initial match stats, detailed match statistics, and player performance.

    Args:
        url (str): The URL of the match page.
        justMain (bool, optional): If True, only the initial match stats are returned. Defaults to False.

    Returns:
        Union[bool, Tuple[Dict[str, Any], Dict[Any, Any]]]: If justMain is True, returns a dictionary
        with the initial match stats. If justMain is False, returns a tuple containing a dictionary
        with the match information and a dictionary with player performance stats.

    Note:
        The function uses the `tokenize_page` function to tokenize the match page.
        It calls various helper functions, such as `gather_dtg`, `gather_league`, `gather_main_info`,
        `gather_match_statistics`, and `gather_player_performance`, to extract specific information
        from the tokenized data.

    Example:
        match_info = get_match_info("/match/12345")
        # Returns a tuple with the match information and player performance stats for the match with ID 12345.
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
    """Retrieves and returns necessary information about an upcoming match.

    The function fetches the web page of the specified match from the FotMob website.
    It extracts the date and time of the match, checks if the match is within a week ahead of the current day,
    and gathers information about the league and team IDs for the match.

    Args:
        url (str): The URL of the match page.

    Returns:
        Union[bool, Dict[Any, Any]]: If the match is within a week ahead of the current day and the necessary
        information is available, returns a dictionary with the following keys:
        - "leagueID" (int): The ID of the league the match belongs to.
        - "teamID" (str): The ID of the home team.
        - "opponentID" (str): The ID of the away team.
        - "date" (datetime.datetime): The date and time of the match.

        If the match is not within the specified timeframe or the necessary information is not available,
        returns False.

    Note:
        The function uses the `tokenize_page` function to tokenize the match page.
        It calls the `gather_dtg`, `gather_next_match_info`, and `gather_league` functions to extract
        specific information from the tokenized data.

    Example:
        next_match_info = get_next_match_info("/match/67890")
        # Returns a dictionary with the necessary information for the upcoming match with ID 67890,
        # or False if the match is not within a week ahead or the necessary information is not available.
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


def get_player_bio(
    url: str
) -> Dict[str, Union[Dict[str, Any], List]]:
    """
    Retrieves and returns information from the player biography on FotMob.

    The function fetches the web page of the specified player from the FotMob website.
    It tokenizes the page content and extracts relevant information from the player bio section.

    Args:
        url (str): The URL of the player's bio page.

    Returns:
        Dict[str, Union[Dict[str, Any], List]]: A dictionary containing information from the player biography.
        The dictionary has the following keys:
        - "bio" (Dict[str, Any]): A dictionary containing player's bio details, including:
            * "height" (str): The player's height.
            * "preffered foot" (str): The player's preferred foot.
            * "age" (str): The player's age.
            * "country" (str): The player's country of origin.
            * "shirt" (str): The player's shirt number.
            * "market val" (str): The player's market value in Euro.
            * "primary position" (str): The player's primary position.

        - "season" (Dict[str, Any]): A dictionary containing player's season statistics, including:
            * "matches" (int): The number of matches played.
            * "goals" (int): The number of goals scored.
            * "assists" (int): The number of assists made.
            * "FotMob Rating" (float): The player's FotMob rating.

    Note:
        The function uses the `tokenize_page` function to tokenize the player's bio page.
        It calls the `gather_player_bio` function to extract the specific information from the tokenized data.

    Example:
        player_bio = get_player_bio("/players/12345")
        # Returns a dictionary with the player's bio information and season statistics
        # for the player with ID 12345 on FotMob.
    """
    # Request page
    tokenized = tokenize_page("https://www.fotmob.com" + url)

    # Get player info
    playerInfo = gather_player_bio(tokenized)

    return playerInfo


def get_name(url: str) -> str:
    """
    Returns the full name of a player or team based on the given URL.

    The function extracts the name from the URL by splitting it and manipulating the parts.
    It removes any occurrences of "-" and capitalizes the subnames to form the full name.

    Args:
        url (str): The URL containing the name of the player or team.

    Returns:
        str: The full name of the player or team with proper capitalization.

    Example:
        full_name = get_name("/players/12345/player-name")
        # Returns "Player Name" as the full name extracted from the URL.

        full_name = get_name("/teams/54321/team-name")
        # Returns "Team Name" as the full name extracted from the URL.
    """
    # Get the last part of the link
    subNames = url.split("/")

    # Remove all occurrences of "-"
    subNames = subNames[len(subNames) - 1].split("-")

    # Return full name with capitalization on the subnames
    return " ".join([subName.capitalize() for subName in subNames])
