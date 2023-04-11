import json
import sys
import os
import sqlalchemy
import datetime as dt

from google.cloud.sql.connector import Connector
from sqlalchemy.orm import sessionmaker
from colorama import Fore

from databaseClasses import *
from values import *
from scraper import *

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../keys/googleCloudKey.json'

def runner():
    """
    Main function of the program that runs the logic
    """
    
    startTime = dt.datetime.now()
    
    print("Connecting to PostgreSQL...")
    # Establish connection to the database
    connection = initPostgreSQL()
    if connection is None:
        sys.exit(Fore.RED + "-> Could not connect to PostgreSQL")
    else:
        print(Fore.GREEN + "-> Connected to PostgreSQL")
        
    # Start session with connection
    Session = sessionmaker(connection)
    session = Session()
    
    # Import leagues, think i will change this to get it from the PostgreSQL databse
    leagues = session.query(Leagues).all()
    leagues = [league.__dict__ for league in leagues]
    # remove unnecessary keys from the dictionaries
    for league in leagues:
        del league["_sa_instance_state"]

    mExplored, mAdded, pExplored, pUpdated, pAdded = 0, 0, 0, 0, 0
    for league in leagues:
        print(Fore.MAGENTA + f"Updating {league['name']}" + Fore.WHITE)
        
        teams = get_team_links(league["id"], nTeams=league["n_teams"])
        
        for team in teams:
            
            urlName = team.split("/")
            teamID = urlName[2]
            urlName = urlName[len(urlName) - 1]
            
            print(teamID, get_name(team))
            
            fixtures = get_match_links(teamID, urlName) # Gets a list of all matches for the team
            players = get_player_links(teamID) # Gets a list of all players of the team
        
            try:
                teamSQL = Teams(id = teamID,
                                name = get_name(team),
                                stadium = "NA",
                                league_id = league["id"])
                session.add(teamSQL)
                session.commit()
            except Exception as e:
                print(f"Could not add {get_name(team)} -> {e}")

            
            for fixture in fixtures:
                # Gather info about that fixture
                try:
                    matchStats, playerStats = get_match_info(fixture)
                except:
                    continue
                
                # Add match data to the database
                try:
                    match = Matches(id=fixture.split("/")[2],
                                    home_team_id=matchStats["maininfo"]["homeID"], 
                                    away_team_id=matchStats["maininfo"]["awayID"], 
                                    league_id=matchStats["league"]["id"], 
                                    date=matchStats["dtg"])
                    
                    homeSide = MatchStats(match_id = fixture.split("/")[2],
                                          side = "home",
                                          
                                          total_shots = matchStats["statistics"]["shots"]["total shots"][0],
                                          shots_off_target = matchStats["statistics"]["shots"]["off target"][0],
                                          shots_on_target = matchStats["statistics"]["shots"]["on target"][0],
                                          blocked_shots = matchStats["statistics"]["shots"]["blocked shot"][0],
                                          hit_woodwork = matchStats["statistics"]["shots"]["hit woodwork"][0],
                                          shots_inside_box = matchStats["statistics"]["shots"]["inside box"][0],
                                          shots_outside_box = matchStats["statistics"]["shots"]["outside box"][0],
                                          
                                          xG_total = matchStats["statistics"]["xG"]["expected goals"][0],
                                          xG_first_half = matchStats["statistics"]["xG"]["first half"][0],
                                          xG_second_half = matchStats["statistics"]["xG"]["second half"][0],
                                          xG_open_play = matchStats["statistics"]["xG"]["open play"][0],
                                          xG_set_play = matchStats["statistics"]["xG"]["set play"][0],
                                          xGOT = matchStats["statistics"]["xG"]["on target"][0],
                                          
                                          accurate_passes = matchStats["statistics"]["passes"]["accurate passes"][0],
                                          accuracy = matchStats["statistics"]["passes"]["accurate passes"][1],
                                          own_half = matchStats["statistics"]["passes"]["own half"][0],
                                          opposition_half = matchStats["statistics"]["passes"]["opposition half"][0],
                                          accurate_long_balls = matchStats["statistics"]["passes"]["accurate long balls"][0],
                                          accurate_crosses = matchStats["statistics"]["passes"]["accurate crosses"][0],
                                          throws = matchStats["statistics"]["passes"]["throws"][0],
                                          
                                          tackles_won = matchStats["statistics"]["defence"]["tackles won"][0],
                                          accuracy_tackles = matchStats["statistics"]["defence"]["tackles won"][1],
                                          interceptions = matchStats["statistics"]["defence"]["interceptions"][0],
                                          blocks = matchStats["statistics"]["defence"]["blocks"][0],
                                          clearances = matchStats["statistics"]["defence"]["clearances"][0],
                                          keeper_saves = matchStats["statistics"]["defence"]["keeper saves"][0],
                                          
                                          yellow_cards = matchStats["statistics"]["cards"]["yellow cards"][0],
                                          red_cards = matchStats["statistics"]["cards"]["red cards"][0],
                                          
                                          duels_won = matchStats["statistics"]["duels"]["duels won"][0],
                                          ground_duels_won = matchStats["statistics"]["duels"]["ground duels"][0],
                                          aerial_duels_won = matchStats["statistics"]["duels"]["aerial duels"][0],
                                          successfull_dribbles = matchStats["statistics"]["duels"]["successfull dribbles"][0])
                    
                    awaySide = MatchStats(match_id = fixture.split("/")[2],
                                          side = "away",
                                          
                                          total_shots = matchStats["statistics"]["shots"]["total shots"][1],
                                          shots_off_target = matchStats["statistics"]["shots"]["off target"][1],
                                          shots_on_target = matchStats["statistics"]["shots"]["on target"][1],
                                          blocked_shots = matchStats["statistics"]["shots"]["blocked shot"][1],
                                          hit_woodwork = matchStats["statistics"]["shots"]["hit woodwork"][1],
                                          shots_inside_box = matchStats["statistics"]["shots"]["inside box"][1],
                                          shots_outside_box = matchStats["statistics"]["shots"]["outside box"][1],
                                          
                                          xG_total = matchStats["statistics"]["xG"]["expected goals"][1],
                                          xG_first_half = matchStats["statistics"]["xG"]["first half"][1],
                                          xG_second_half = matchStats["statistics"]["xG"]["second half"][1],
                                          xG_open_play = matchStats["statistics"]["xG"]["open play"][1],
                                          xG_set_play = matchStats["statistics"]["xG"]["set play"][1],
                                          xGOT = matchStats["statistics"]["xG"]["on target"][1],
                                          
                                          accurate_passes = matchStats["statistics"]["passes"]["accurate passes"][3],
                                          accuracy = matchStats["statistics"]["passes"]["accurate passes"][4],
                                          own_half = matchStats["statistics"]["passes"]["own half"][1],
                                          opposition_half = matchStats["statistics"]["passes"]["opposition half"][1],
                                          accurate_long_balls = matchStats["statistics"]["passes"]["accurate long balls"][3],
                                          accurate_crosses = matchStats["statistics"]["passes"]["accurate crosses"][3],
                                          throws = matchStats["statistics"]["passes"]["throws"][1],
                                          
                                          tackles_won = matchStats["statistics"]["defence"]["tackles won"][3],
                                          accuracy_tackles = matchStats["statistics"]["defence"]["tackles won"][4],
                                          interceptions = matchStats["statistics"]["defence"]["interceptions"][1],
                                          blocks = matchStats["statistics"]["defence"]["blocks"][1],
                                          clearances = matchStats["statistics"]["defence"]["clearances"][1],
                                          keeper_saves = matchStats["statistics"]["defence"]["keeper saves"][1],
                                          
                                          yellow_cards = matchStats["statistics"]["cards"]["yellow cards"][1],
                                          red_cards = matchStats["statistics"]["cards"]["red cards"][1],
                                          
                                          duels_won = matchStats["statistics"]["duels"]["duels won"][1],
                                          ground_duels_won = matchStats["statistics"]["duels"]["ground duels"][3],
                                          aerial_duels_won = matchStats["statistics"]["duels"]["aerial duels"][3],
                                          successfull_dribbles = matchStats["statistics"]["duels"]["successfull dribbles"][3])
                    
                    session.add(match)
                    session.add(homeSide)
                    session.add(awaySide)
                    session.commit()
                    mAdded += 1
                except Exception as e:
                    print(f"Could not add match -> {e}")
                    
                # Add player stats do database
                for player in playerStats.keys():
                    try:
                        playerPerformance = PlayerStats(player_id = playerStats[player]["id"],
                                                        match_id = fixture.split("/")[2],
                                                        
                                                        rating = playerStats[player]["fotmob rating"],
                                                        minutes_played = playerStats[player]["minutes played"],
                                                        goals = playerStats[player]["goals"],
                                                        assists = playerStats[player]["assits"],
                                                        shots = playerStats[player]["shots"],
                                                        passes = playerStats[player]["passes"].split("/")[0],
                                                        passes_accuracy = int(playerStats[player]["passes"].split("/")[0] / playerStats[player]["passes"].split("/")[1]),
                                                        chances_created = playerStats[player]["chances created"],
                                                        touches = playerStats[player]["touches"],
                                                        passes_into_final_third = playerStats[player]["passes into final thirds"],
                                                        dispossesed = playerStats[player]["dispossesed"],
                                                        tackles_won = playerStats[player]["tackles won"].split("/")[0],
                                                        tackles_accuracy = int(playerStats[player]["tackles won"].split("/")[0] / playerStats[player]["tackles won"].split("/")[1]),
                                                        recoveries = playerStats[player]["recoveries"],
                                                        ground_duels_won = playerStats[player]["ground duels won"],
                                                        aerial_duels_won = playerStats[player]["aerial duels won"],
                                                        was_fouled = playerStats[player]["was fouled"],
                                                        fouls_committed = playerStats[player]["fouls committed"])
                        session.add(playerPerformance)
                        session.commit(playerPerformance)
                    except:
                        print(f"Could not add {get_name(player)} -> {e}")
            for player in players:
                # 1 - Gather info about current player
                try:
                    pExplored += 1
                    stats = get_player_bio(player)
                    name = get_name(player)
                    playerSQL = Players(id = player.split("/")[2],
                                    team_id = int(teamID),
                                    name = name,
                                    age = int(stats["bio"]["Age"]),
                                    country = stats["bio"]["Country"],
                                    height = int(stats["bio"]["Height"]),
                                    market_val = stats["bio"]["Market"],
                                    preffered_foot = stats["bio"]["foot"],
                                    primary_postition = stats["bio"]["position"],
                                    played = int(stats["season"]["Matches"]),
                                    goals = int(stats["season"]["Goals"]),
                                    assists = int(stats["season"]["Assists"]),
                                    rating = float(stats["season"]["FotMob"]))
                    session.add(playerSQL)
                    session.commit()
                    pAdded += 1
                except Exception as e:
                    print(f"Could not add {get_name(player)} -> {e}")
    
    # Get the end time of the data gathering
    session.close()
    endTime = dt.datetime.now()
    
    # For test purposes only
    dictionary = {
        "mExplored" : mExplored,
        "mAdded" : mAdded,
        "pExplored" : pExplored,
        "pUpdated" : pUpdated,
        "pAdded" : pAdded
    }
    
    # Create a report of the writer.py execution
    createReport(startTime, endTime, dictionary)
    
    # Exit program after successful execution
    sys.exit(Fore.GREEN + "writer.py successfully run in a time of " + str(endTime - startTime))
            
                
def initPostgreSQL():
    """
    Connects and initializes PostgreSQL
    """
    # Import database creditations
    creds = loadJSON("../../keys/postgreSQLKey.json")

    def getConnection():
        connector = Connector()
        connection = connector.connect(
            creds["connectionName"],
            "pg8000",
            user=creds["user"],
            password=creds["password"],
            db=creds["dbname"]
        )
        return connection
    
    try: # Try to connecto to database
        engine = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getConnection,
        )
        #connection = engine.connect()
        return engine
    except Exception as e: # Connection failed
        print(f"Error: {e}")
        return None

def loadJSON(path):
    """
    Returns data from JSON file @ path
    """
    return json.load(open(path))

def createReport(start, end, report):
    """
    Creates reports with information about the execution.
    Saves report as a .txt file and adds to SQLdatabase.
    """
    # Format report content
    reportContent = f"""
    -------------------
    Time started: {start}
    Time ended: {end}
    Time delta: {end - start}
    Matches explored: {report.get("mExplored")}
    Matches added: {report.get("mAdded")}
    Players explored: {report.get("pExplored")}
    Players updated: {report.get("pUpdated")}
    Players added: {report.get("pAdded")}
    -------------------
    """
    
    # Decide filename
    today = dt.datetime.now()
    formattedDate = today.strftime("%d %B %Y").lower()
    filename = f"report {formattedDate}.txt"
    
    # Create and write to file
    with open(os.path.join("reports", filename), "w") as f:
        f.write(reportContent)
    
    # Confirm that the report was created
    print(f"Report saved as {filename}")
    
    # TODO: Add report to SQL database

if __name__ == "__main__":
    runner()