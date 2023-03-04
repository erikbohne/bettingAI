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
    # Find team names
    team = dict()
    for side in ["homeTeam", "awayTeam"]:
        for i, info in enumerate(information):
            if info == side:
                for j in range(1, 10):
                    if information[i + j][0] == ":":
                        length = j
                        team[side] = [information[i + j] for j in range(1, length)]
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
        "hometeam" : " ".join(team["homeTeam"]),
        "awayteam" : " ".join(team["awayTeam"]),
        "homescore" : score[0],
        "awayscore" : score[1],
        "homegd" :  int(score[0]) - int(score[1]),
        "awaygd" : int(score[1]) - int(score[0])
    }
    
    return mainInfo

def gather_match_statistics(information):
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
        * xG og target (xGOT)
    
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
    for i, info in enumerate(information):
        if info == "showSuperLive":
            start = i + 85
    
    # Find all shots statistics
    shots = []
    for i in range(start, 1000):
        if any(char.isdigit() for char in information[i]): # check if there is a digit
            shots.append(information[i].split(",")) # from eg '14,7' -> ['14', '7']
            if len(shots) == 7:
                start = i + 1
                break
            
    # Put all shots info in dict
    shots = {
        "total shots" : shots[0],
        "off target" : shots[1],
        "on target" : shots[2],
        "blocked shot" : shots[3],
        "hit woodwork" : shots[4],
        "inside box" : shots[5],
        "outside box" : shots[6]
    }
    print(shots)

    # Find all xG statistics
    xG = []
    current = []
    for i in range(start, start + 100):
        if any(char.isdigit() for char in information[i]):
            current.append(information[i])
            if len(current) % 2 == 0:
                xG.append(current)
                if len(xG) == 6:
                    start = i + 1
                    break
                current = []
    
    # Put all xG stats in a dict
    xG = {
        "expected goals" : xG[0],
        "first half" : xG[1],
        "second half" : xG[2],
        "open play" : xG[3],
        "set play" : xG[4],
        "on target" : xG[5]
    }
    print(xG)
    
    # Find and gather passes statistics
    passes = []
    cooldown = 0
    for i in range(start, start + 100):
        if cooldown != 0:
            cooldown -= 1
            continue
        if any(char.isdigit() for char in information[i]):
            if len(passes) in [1, 4, 5]: # for the stats that include accuracy
                passes.append([information[j] for j in range(i, i + 5)])
                cooldown = 4
            else:
                passes.append(information[i].split(","))
            if len(passes) == 7:
                start = i + 1
                break
            
    # Put all pass stats in a dict
    passes = {
        "passes" : passes[0],
        "accurate passes" : passes[1],
        "own half" : passes[2],
        "opposition hald" : passes[3],
        "accurate long balls" : passes[4],
        "accurate crosses" : passes[5],
        "throws" : passes[6]
    }
    print(passes)
    
    
    # TODO Find and gather defence statistics
    # TODO Find and gather dicipline stats
    # TODO Find and gather duels stats
    
    
    
    

    
    
                