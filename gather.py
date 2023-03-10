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
    
    try:
        return {"name" : name, "id": id}
    except UnboundLocalError:
        return {"name" : None, "id" : None}

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
            total = 0
            for j in range(100):
                if information[i + j] == "Total":
                    total += 1
                if total == 2:
                    start = i + j
                    break
    
    # Find all shots statistics
    shots = []
    for i in range(start, start + 100):
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
    
    # Find and gather defence statistics
    defence = []
    cooldown = 0
    for i in range(start, start + 100):
        if cooldown != 0:
            cooldown -= 1
            continue
        if any(char.isdigit() for char in information[i]):
            if len(defence) in [0]: # for the stats that include accuracy
                defence.append([information[j] for j in range(i, i + 5)])
                cooldown = 4
            else:
                defence.append(information[i].split(","))
            if len(defence) == 5:
                start = i + 1
                break
    
    # Put all defence stats in a dict
    defence = {
        "tackles won" : defence[0],
        "interceptions": defence[1],
        "blocks" : defence[2],
        "clearances" : defence[3],
        "keeper saves" : defence[4]
    }
            
            
    
    # TODO Find and gather duels stats
    duels = []
    cooldown = 0
    for i in range(start, start + 100):
        if cooldown != 0:
            cooldown -= 1
            continue
        if any(char.isdigit() for char in information[i]):
            if len(duels) in [1, 2, 3]: # for the stats that include accuracy
                duels.append([information[j] for j in range(i, i + 5)])
                cooldown = 4
            else:
                duels.append(information[i].split(","))
            if len(duels) == 4:
                start = i + 6
                break
    
    # Put all duel stats in a dict
    duels = {
        "duels won" : duels[0],
        "ground duels" : duels[1],
        "aerial duels" : duels[2],
        "successfull dribbles" : duels[3]
    }
    
    # Find and gather dicipline stats
    cards = []
    for i in range(start, start + 50):
        if any(char.isdigit() for char in information[i]): # check if there is a digit
            cards.append(information[i].split(",")) # from eg '14,7' -> ['14', '7']
            if len(cards) == 2:
                break
    
    # Put card stats in a dict
    cards = {
        "yellow cards" : cards[0],
        "red cards" : cards[1]
    }
    
    return {
        "shots" : shots,
        "xG" : xG,
        "passes" : passes,
        "defence" : defence,
        "duels" : duels,
        "cards" : cards
    }

def gather_player_bio(information):
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
    # Find bio statistics
    bio = []
    indicator, idx = ["Height", "foot", "Age", "Country", "Shirt", "Value", "Position"], 0
    for i, _ in enumerate(information):
        if information[i] == indicator[idx]: # TODO Make is so it can append both Strike and Centre back.
            bio.append(information[i + 1])
            idx += 1
        if len(bio) == 7:
            break
    
    # Create a dictionary with bio statistics
    bio = {indicator[i] : bio[i] for i in range(len(bio))}
    
    # Find indexes for next iteration
    for i, info in enumerate(information):
        if info == "__NEXT_DATA__":
            start = i
    
    # Find season statistics
    season = []
    indicator, idx = ["Matches", "Goals", "Assists", "FotMob"], 0
    for i, _ in enumerate(information[start:start+200]):
        if information[start + i] == indicator[idx]:
            season.append(information[start + i - 1])
            idx += 1
        if len(season) == 4:
            break
    
    # Create a dictionary with season stats
    season = {indicator[i] : season[i] for i in range(len(season))}

    return {"bio": bio, "season" : season}

def gather_player_performance(information):
    """
    Gather player performance of each player from each team
    - Player:
        * Shirt
        * Role
        * FotMob Rating
        * Minutes played
        * Goals
        * Assists
        * Total shots
        * Accurate passes [accurate/inaccurate, %]
        * Chances created
        * Conceded penalty
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
    playerPerformance = {} # init the dict to store players
    
    #for i, info in enumerate(information):
    #    if info == "usingOptaId":
    #        print(i)
    #        information[i:]
    #        break
    
    for i, info in enumerate(information):
        if info == "firstName":
            pass
            #print(information[i + 1], information[i + 3])
    
    
    
