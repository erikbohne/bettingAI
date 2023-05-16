import datetime as dt
from typing import List, Optional, Dict, Union, Any

from bettingAI.writer.values import *


def gather_dtg(
    information: List[str]
    ) -> dt.datetime:
    """Extracts and returns datetime information from the match details.

    Args:
        information (List[str]): A list of strings containing match details.

    Returns:
        datetime.datetime: The date and time of the match.
    
    Note:
        If the match round is not available (e.g. Club Friendlies), 
        it is set to None.
    """
    for i in range(15):
        if information[i] in MONTHS:
            dtg = {}
            for j, value in enumerate(["month", "date", "year", "time", "timezone"]):
                dtg[value] = information[i + j]
            try:  # Not all matches have a match round e.g Club Friendlies
                dtg["matchround"] = int(information[i + j + 2])
            except ValueError:
                dtg["matchround"] = None

    # Convert month name to its corresponding integer value
    month = dt.datetime.strptime(dtg["month"], "%b").month
    # Extract the day, year, hour, and minute
    day = int(dtg["date"])
    year = int(dtg["year"])
    hour, minute = map(int, dtg["time"].split(":"))

    # Create a datetime object and return it
    return dt.datetime(year, month, day, hour, minute)


def gather_league(
    information: List[str]
    ) -> Dict[str, Any]:
    """Extracts and returns the league ID from the provided match details.

    Args:
        information (List[str]): A list of strings containing match details.

    Returns:
        dict: A dictionary containing the league ID. If no ID is found, 
        the dictionary will contain a None value for the ID.

    Note:
        The function searches for the key 'parentLeagueId' in the list.
        If it is found, the following element (which is assumed to be the ID) is returned.
        If 'parentLeagueId' is not found in the list, a UnboundLocalError is caught and None is returned.
    """
    for i in range(50):
        if information[i] == "parentLeagueId":
            id = information[i + 1][1:]  # removing colon in front of ID -> ':47' -> '47'
            break
    try:
        return {"id": id}
    except UnboundLocalError:
        return {"id": None}

def gather_main_info(
    information: List[str]
    ) -> Dict[
        str,
        Union[str, int]]:
    """Extracts and returns the initial match stats from the provided match details.

    The function searches for the keys 'homeTeam' and 'awayTeam' in the list 
    to find the team names and IDs. It also searches for the key 'score' to find the scores.
    The goal difference is calculated as the difference between the home team score and the away team score.
    
    Args:
        information (List[str]): A list of strings containing match details.

    Returns:
        dict: A dictionary containing the following match stats:
            - 'hometeam' (str): The home team name
            - 'awayteam' (str): The away team name
            - 'homeID' (int): The home team ID
            - 'awayID' (int): The away team ID
            - 'homescore' (str): The home team score
            - 'awayscore' (str): The away team score
            - 'homegd' (int): The home goal difference (home score - away score)
            - 'awaygd' (int): The away goal difference (away score - home score)
    """
    # Find team names
    team = dict()
    ids = list()
    for side in ["homeTeam", "awayTeam"]:
        for i, info in enumerate(information):
            if info == side:
                for j in range(1, 10):
                    if information[i + j][0] == ":":
                        length = j
                        team[side] = [information[i + j] for j in range(1, length)]
                        ids.append(information[i + j].replace(":", ""))
                        break
    # Find score
    score = []
    for i, info in enumerate(information):
        if len(score) == 2:
            break
        if info == "score":
            score.append(information[i + 1].replace(":", ""))

    # Create dict with information
    mainInfo = {
        "hometeam": " ".join(team["homeTeam"]),
        "awayteam": " ".join(team["awayTeam"]),
        "homeID": ids[0],
        "awayID": ids[1],
        "homescore": score[0],
        "awayscore": score[1],
        "homegd": int(score[0]) - int(score[1]),
        "awaygd": int(score[1]) - int(score[0]),
    }

    return mainInfo

def gather_match_statistics(information: List[str]) -> Dict[str, Any]:
    """Extracts and returns the match statistics from the provided match details.

    The function searches for specific activation words to locate the start index of each category of statistics.
    It then extracts the corresponding statistics based on the activation words and their positions in the list.
    Some statistics may be optional and may not be present in certain matches.
    The extracted statistics are returned in a dictionary with the following structure:

    {
        "shots": {
            "total shots": str,
            "off target": str,
            "on target": str,
            "blocked shot": str,
            "hit woodwork": str,
            "inside box": str,
            "outside box": str
        },
        "xG": {
            "expected goals": str,
            "first half": str,
            "second half": str,
            "open play": str,
            "set play": str,
            "penalty": Optional[str],
            "on target": str
        },
        "passes": {
            "passes": str,
            "accurate passes": str,
            "own half": str,
            "opposition half": str,
            "accurate long balls": str,
            "accurate crosses": str,
            "throws": str
        },
        "defence": {
            "tackles won": str,
            "interceptions": str,
            "blocks": str,
            "clearances": str,
            "keeper saves": str
        },
        "duels": {
            "duels won": str,
            "ground duels": str,
            "aerial duels": str,
            "successful dribbles": str
        },
        "cards": {
            "yellow cards": str,
            "red cards": str
        }
    }

    Args:
        information (List[str]): A list of strings containing match details.

    Returns:
        Optional[Dict[str, Dict[str, Union[str, List[List[str]]]]]]: A dictionary containing the match statistics.
        If the start index of the statistics cannot be found, None is returned.
    """

    def find_start_index(information: List[str]) -> int:
        total = 0
        start = None
        for i, info in enumerate(information):
            if info == "showSuperLive":
                for j in range(200):
                    if information[i + j] == "Total":
                        total += 1
                    if total == 2:
                        return i + j

        if start is None:
            for i, info in enumerate(information):
                if info == "Top":
                    total = 0
                    for j in range(200):
                        if i + j == len(information):
                            return False
                        if information[i + j] == "Total":
                            total += 1
                        if total == 2:
                            start = i + j
                            return start
        return False

    def extract_stats_by_activation_word(
        activation_word: str, start: int, stats_count: int
    ) -> List[List[str]]:
        data = []
        found_values = 0
        i = start
        while found_values < stats_count and i < len(information):
            if information[i] == activation_word:
                i += 1
                while found_values < stats_count and i < len(information):
                    if any(char.isdigit() for char in information[i]):
                        if "," not in information[i]:
                            if information[i + 2] == "%":
                                data.append(
                                    [
                                        information[i],
                                        information[i + 1],
                                        information[i + 3],
                                        information[i + 4],
                                    ]
                                )
                                found_values += 1
                                i += 5
                            else:
                                data.append([information[i], information[i + 1]])
                                found_values += 1
                                i += 2
                        else:
                            data.append(information[i].split(","))
                            found_values += 1
                            i += 1
                    else:
                        i += 1
            else:
                i += 1
        return data

    start = find_start_index(information)
    if not start:
        return None

    # Shots
    shots_keys = [
        "total shots",
        "off target",
        "on target",
        "blocked shot",
        "hit woodwork",
        "inside box",
        "outside box",
    ]
    shots = extract_stats_by_activation_word("shots", start, len(shots_keys))
    shots_dict = {key: value for key, value in zip(shots_keys, shots)}

    # xG
    xg_keys = [
        "expected goals",
        "first half",
        "second half",
        "open play",
        "set play",
        "penalty",
        "on target",
    ]
    if "penalty" not in information[start : start + 200]:
        xg_keys.remove(
            "penalty"
        )  # information will only contain xg penalty if there was a penalty

    xg = extract_stats_by_activation_word("xG", start, len(xg_keys))
    xg_dict = {key: value for key, value in zip(xg_keys, xg)}

    # Passes
    passes_keys = [
        "passes",
        "accurate passes",
        "own half",
        "opposition half",
        "accurate long balls",
        "accurate crosses",
        "throws",
    ]
    passes = extract_stats_by_activation_word("Passes", start, len(passes_keys))
    passes_dict = {key: value for key, value in zip(passes_keys, passes)}

    # Defence
    defence_keys = [
        "tackles won",
        "interceptions",
        "blocks",
        "clearances",
        "keeper saves",
    ]
    defence = extract_stats_by_activation_word("Defence", start, len(defence_keys))
    defence_dict = {key: value for key, value in zip(defence_keys, defence)}

    # Duels
    duels_keys = [
        "duels won",
        "ground duels",
        "aerial duels",
        "successfull dribbles",
    ]
    duels = extract_stats_by_activation_word("Duels", start, len(duels_keys))
    duels_dict = {key: value for key, value in zip(duels_keys, duels)}

    # Cards
    cards_keys = ["yellow cards", "red cards"]
    cards = extract_stats_by_activation_word("Yellow", start, len(cards_keys))
    cards_dict = {key: value for key, value in zip(cards_keys, cards)}

    return {
        "shots": shots_dict,
        "xG": xg_dict,
        "passes": passes_dict,
        "defence": defence_dict,
        "duels": duels_dict,
        "cards": cards_dict,
    }

def gather_player_bio(
    information: List[str],
    ) -> Dict[
        str, 
        Union[Dict[str, Any], List]]:
    """Extracts and returns the player's bio and season statistics from the provided match details.

    The function searches for specific indicators to locate the corresponding values in the information list.
    Some indicators may not be present in certain player details, in which case their values are set to 0.
    The extracted information is returned in a dictionary with the following structure:

    {
        "bio": {
            "position": str,
            "Height": str,
            "Age": str,
            "Country": str,
            "Shirt": str,
            "Market": str
        },
        "season": {
            "Matches": int,
            "Goals": int,
            "Assists": int,
            "FotMob": Union[int, float]
        }
    }

    Args:
        information (List[str]): A list of strings containing player details.

    Returns:
        Dict[str, Union[Dict[str, Any], List]]: A dictionary containing the player's bio and season statistics.
    """
    # Find indexes for iteration
    for i, info in enumerate(information):
        if info == "__NEXT_DATA__":
            information = information[i : i + 200]

    # Find bio statistics
    bio = {}
    for i, _ in enumerate(information[:100]):
        if information[i] == "strPosShort" or information[i] == "primaryPosition":
            bio["position"] = information[i + 2]
            information = information[i + 2 :]
            break

    indicator = ["Height", "Age", "Country", "Shirt", "Market"]
    for i, value in enumerate(information):
        for ind in indicator:
            if value == ind:
                try:
                    if ind == "Height":
                        prev_value = information[i - 2].replace(":", "")
                    else:
                        prev_value = information[i - 1].replace(":", "")
                    if prev_value in bio.values():
                        bio[ind] = information[i - 2].replace(":", "")
                    else:
                        bio[ind] = prev_value
                except:
                    bio[ind] = 0

    # Find season statistics
    season = []
    indicator, idx = ["Matches", "Goals", "Assists", "FotMob"], 0
    for i, _ in enumerate(information):
        if information[i] == indicator[idx]:
            try:
                value = int(information[i - 1].replace(":", ""))
                season.append(value)
            except ValueError:
                value = float(information[i - 1].replace(":", ""))
                season.append(value)
            except Exception as e:
                value
                season.append(0)
            idx += 1
        if len(season) == 4:
            break

    # Create a dictionary with season stats
    season = {indicator[i]: season[i] for i in range(len(season))}
    return {"bio": bio, "season": season}


def gather_player_performance(information: List[str]) -> Dict[str, Any]:
    """
    Extracts and returns the performance statistics for each player from the provided match details.

    The function searches for specific indicators in the information list to extract 
    the performance statistics for each player.
    If a particular statistic is not available for a player, its value is set to None.
    The extracted information is returned in a dictionary with the following structure:

    {
        "Player Name 1": {
            "id": str,
            "fotmob rating": Union[int, None],
            "minutes played": Union[int, None],
            "goals": Union[int, None],
            "assists": Union[int, None],
            "shots": Union[int, None],
            "passes": Union[int, None],
            "chances created": Union[int, None],
            "touches": Union[int, None],
            "passes into final third": Union[int, None],
            "dispossessed": Union[int, None],
            "tackles won": Union[int, None],
            "recoveries": Union[int, None],
            "ground duels won": Union[int, None],
            "aerial duels won": Union[int, None],
            "was fouled": Union[int, None],
            "fouls committed": Union[int, None]
        },
        "Player Name 2": {
            ...
        },
        ...
    }

    Args:
        information (List[str]): A list of strings containing player performance details.

    Returns:
        Dict[str, Any]: A dictionary containing the performance statistics for each player.
    """
    playerPerformance = {}  # init the dict to store players

    # Find the start of the player stats section
    for i, info in enumerate(information):
        if (
            info == "lineup" and information[i + 1] == "lineup"
        ):  # two lineup following each other is the start signal
            information = information[i:]
            break

    playerInfo = [
        "Top",
        "rating",
        "played",
        "Goals",
        "Assists",
        "shots",
        "passes",
        "created",
        "Touches",
        "third",
        "Dispossessed",
        "won",
        "Recoveries",
        "won",
        "won",
        "fouled",
        "committed",
    ]
    playerStat = [
        "fotmob rating",
        "minutes played",
        "goals",
        "assists",
        "shots",
        "passes",
        "chances created",
        "touches",
        "passes into final third",
        "dispossessed",
        "tackles won",
        "recoveries",
        "ground duels won",
        "aerial duels won",
        "was fouled",
        "fouls committed",
    ]

    playerID = None  # assign value before iteration
    currentPlayer, idx = {}, 0  # to store current player stats
    onPlayer = False  # to switch between to modes: gather stats or find new player

    for i, info in enumerate(information):

        # Check if we are starting on a new player
        if (info == "firstName" and onPlayer) or (
            len(currentPlayer.keys()) == len(playerStat) - 1
        ):
            if currentPlayer != {}:
                playerPerformance[playerName] = currentPlayer
                playerPerformance[playerName]["id"] = playerID
            onPlayer = False  # mark the end of this player
            currentPlayer, idx = {}, 0  # reset stats list and index

        if onPlayer:  # if in gather stats mode
            if info[: len("/players")] == "/players":
                playerID = info.split("/")[2]
            if info == playerInfo[idx]:  # find current stat
                if idx > 0:
                    if any(char.isdigit() for char in information[i + 1]):
                        currentPlayer[playerStat[idx]] = information[i + 1].replace(
                            ":", ""
                        )  # append the current stat and remove colon from number: ":2" -> "2"
                    else:
                        currentPlayer[playerStat[idx]] = None
                idx += 1  # next index value
        else:  # if in find new player mode
            if info == "firstName":  # gather the name of the player
                for j in range(10):
                    if (
                        information[i + j] == "fullName"
                    ):  # full name is between "firstName and imageUrl"
                        playerName = " ".join(
                            [
                                information[i + n]
                                for n in range(j)
                                if information[i + n] not in ["firstName", "lastName"]
                            ]
                        )
                        if playerName in playerPerformance.keys():
                            pass
                        playerPerformance[playerName] = {}
                        onPlayer = True  # we are on a player and the following stats will belong to current player
                        break

    # Return a dict containing all players
    return playerPerformance

def gather_next_match_info(
    information: List[str]
    ) -> Optional[List[str]]:
    """
    Extracts and returns the team IDs for the upcoming match from the provided match details.

    The function searches for the keys 'homeTeam' and 'awayTeam' in the information list to find the team IDs.
    Once both team IDs are found, they are returned as a list.
    If the necessary information is not found, or if the information is incomplete, None is returned.

    Args:
        information (List[str]): A list of strings containing match details.

    Returns:
        Optional[List[str]]: A list containing the team IDs of the home and away teams, respectively.
        If the team IDs are not found or incomplete information is provided, None is returned.
    """
    ids = []
    nextNumber = False
    for info in information:
        if info == "homeTeam" or info == "awayTeam":
            nextNumber = True
        if info[0] == ":" and nextNumber:
            ids.append(info[1:])
            if len(ids) == 2:
                return ids
            nextNumber = False
            
    return None