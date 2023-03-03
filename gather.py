from values import *

def gather_dtg(information):
    """
    Returns time and date information from the match
    """
    for i in range(15):
        if information[i] in MONTHS:
            dtg = {}
            for j, value in enumerate(["month", "date", "year", "time", "timezone"]):
                dtg[value] = information[i + j]
            try: # Not all matches have a match round e.g Club Friendlies
                dtg["matchround"] = int(information[i + j + 2])
            except ValueError:
                dtg["matchround"] = None
    return dtg

def gather_league(information):
    """
    Returns league name and id for competition
    """
    for i in range(10):
        if information[i] == "leagueId":
            id = information[i + 1][1:len(information[i])] # removing colon in front of ID -> ':47' -> '47'
            for j in range(10):
                if information[i + j] == "leagueRoundName":
                    name = ' '.join([information[i + n] for n in range(3, j)])
    
    return {"name" : name, "id": id}

def gather_main_info(information):
    """
    Returns the initial match stats:
    * Home team name
    * Away team name
    * Home team score
    * Away team score
    * Home goal diff
    * Away goal diff
    """
    # TODO
    return True