import datetime as dt
from typing import List, Optional, Dict, Union, Any

from bettingAI.writer.values import *


def gather_dtg(information: List[str]) -> dt.datetime:
    """
    Returns time and date information from the match
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


def gather_league(information: List[str]) -> Dict[str, Any]:
    """
    Returns league name and id for competition
    """
    for i in range(50):
        if information[i] == "parentLeagueId":
            id = information[i + 1][1:]  # removing colon in front of ID -> ':47' -> '47'
            break
    try:
        return {"id": id}
    except UnboundLocalError:
        return {"id": None}

def gather_main_info(information: List[str]) -> Dict[str, Any]:
    """
    Returns the initial match stats:
    * Home team name
    * Away team name
    * Home team score
    * Away team score
    * Home goal diff
    * Away goal diff
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
    """
    Returns a dict with all the statistics from the match:
    - Shots:
        * total shots
        * shots off target
        * shots on target
        * blocked shots
        * hit woodwork
        * shots inside box
        * shots outside box

    - xG (Exptected goals):
        * xG total
        * xG first half
        * xG second half
        * xG open play
        * xG set play
        * xG on target (xGOT)

    - Passes:
        * Passes
        * Accurate passes
        * Accuracy
        * Own half
        * Opposition half
        * Accurate long balls
        * Accurate crosses
        * Throws

    - Defence:
        * Tackles won
        * Accuracy tackles
        * Interceptions
        * Blocks
        * Clearances
        * Keeper saves

    - Dicipline:
        * Yellow cards
        * Red cards

    - Duels:
        * Duels won
        * Ground duels won
        * Aerial duels won
        * Successfull dribbles
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
) -> Dict[str, Union[Dict[str, Any], List]]:
    """
    Returns a dict with all the statistics from the match:

    - Bio:
        * Height
        * Preffered foot
        * Age
        * Country
        * Shirt
        * Market val (Euro)
        * Primary position

    - Season stats:
        * Matches
        * Goals
        * Assists
        * FotMob Rating
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
    Gather player performance of each player from each team
    - Player:
        * FotMob Rating
        * Minutes played
        * Goals
        * Assists
        * Total shots
        * Accurate passes [accurate/inaccurate, %]
        * Chances created
    - Attack stats:
        * Touches
        * Successful dribbles
        * Passes into final third
        * Accurate long balls
        * Dispossessed
    - Defence stats:
        * Tackles won
        * Blocks
        * Clearances
        * Headed clearance
        * Recoveries
    - Duels stats:
        * Ground duels won
        * Aerial duels won
        * Was fouled
        * Fouls comitted
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

def gather_next_match_info(information):
    """
    Returns team ids for the upcoming match
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