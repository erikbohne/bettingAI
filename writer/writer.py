import sys
import os
import json
import logging
import sqlalchemy
import datetime as dt

from google.cloud.sql.connector import Connector
from sqlalchemy.orm import sessionmaker
from collections import Counter

from databaseClasses import *
from values import *
from scraper import *
from addRow import *

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../keys/googleCloudKey.json'

def runner():
    """
    Main function of the program that runs the logic
    """
    # Register start time of the program
    startTime = dt.datetime.now()
    
    # Establish connection to the database
    logger.info("Connecting to PostgreSQL")
    connection = initPostgreSQL()
    if connection is None:
        logger.critical("Could not connect to PostgreSQL -> {e}")
    else:
        logger.info("Connected to PostgreSQL")

    # Start session with connection
    try:
        Session = sessionmaker(connection)
        session = Session()
        logger.info("Session established")
    except Exception as e:
        logger.warning(e)
    
    # Import leagues from database
    leagues = session.query(Leagues).all()
    leagues = [league.__dict__ for league in leagues]
    for league in leagues: # remove unnecessary keys from the dictionaries
        del league["_sa_instance_state"]

    trackData = Counter() # class to track explored, updated and added teams, matches and players
    for league in leagues: # iterate over each league
        if league["id"] != 59:
            continue
        logger.info(f"Updating {league['name']}")
        exceptions[league["id"]] = Counter() # create specific Counter() for this league
        
        # Get the fotmob links to all team in that league
        teams = get_team_links(league["id"], nTeams=league["n_teams"])
        
        for team in teams: # iterate over each team
            
            teamID = team.split("/")[2] # fotmob team id
            urlName = team.split("/")[4] # how the team is spelled in the fotmob url
            
            # Get the fotmob links to all matches and players for the given team
            fixtures = get_match_links(teamID, urlName)
            players = get_player_links(teamID)

            # Add the team if possible
            #try:
            #    trackData["tExplored"] += 1
            #    teamSQL = add_team(teamID, get_name(team), league["id"])
            #    session.add(teamSQL)
            #    session.commit()
            #    trackData["tAdded"] += 1
            #except Exception as e:
            #    session.rollback()
            #    exceptions[league["id"]][f"{type(e)} : {e}"] += 1

            for fixture in fixtures: # iterate over all matches found for the team
                
                # Gather info about that fixture
                try:
                    matchStats, playerStats = get_match_info(fixture)
                    matchID = fixture.split("/")[2] # get match ID from fotmob
                except Exception as e:
                    exceptions[league["id"]][f"{type(e)} : {e}"] += 1
                    continue
                
                # Add match data to the database
                try:
                    trackData["mExplored"] += 1 # track matches explored
                    match, homeSide, awaySide = add_match(matchID, matchStats)
                    session.add(match) # add main info
                    session.add(homeSide) # add home stats
                    session.add(awaySide) # add away stats
                    session.commit() # commit match
                    print(f"added -> {matchStats['maininfo']['hometeam']} - {matchStats['maininfo']['awayteam']}")
                    trackData["mAdded"] += 1 # track match added
                except Exception as e:
                    session.rollback()
                    exceptions[league["id"]][f"{type(e)} : {e}"] += 1
                    
                # Add player performance stats do database
                for player in playerStats.keys(): # iterate over all players returned from gather_player_performance()
                    try:
                        trackData["psExplored"] += 1
                        playerPerformance = add_player_performance(matchID, playerStats, player)
                        session.add(playerPerformance)
                        session.commit()
                        trackData["psAdded"] += 1
                    except Exception as e:
                        session.rollback()
                        exceptions[league["id"]][f"{type(e)} : {e}"] += 1
                        
            for player in players: # iterate over all players in the team
                continue
                try:
                    trackData["pExplored"] += 1 # update number of explored players
                    playerBio = add_player_bio(player.split("/")[2], teamID, get_name(player), get_player_bio(player))
                    session.add(playerBio) # add player
                    session.commit() # commit player to databse
                    trackData["pAdded"] += 1 # keep track of players added
                except Exception as e:
                    session.rollback()
                    exceptions[league["id"]][f"{type(e)} : {e}"] += 1
            
            print(trackData)
                    
        # Log error messages that occoured in the league
        if exceptions[league["id"]].items(): # check for any exceptions
            logger.info(f"Exceptions for {league['name']}:") 
            for error, count in exceptions[league["id"]].items(): # iterate over all exceptions
                if count > 5: # ensure we dont record the error of trying to add something that is already there
                    logger.error(f"    {error}   ->  {count}") # log each exception
    
    # Get the end time of the data gathering
    session.close()
    endTime = dt.datetime.now()
    
    # Create a report of the writer.py execution
    try:
        createReport(startTime, endTime, trackData)
    except:
        logger.error("Could not create report")
        print(startTime, endTime, trackData)
    
    # Exit program after successful execution
    logger.info(f"Successfully run in a time of {str(endTime - startTime)}")
    

def initLogger():
    # Create a logger object
    logger = logging.getLogger()

    # Set the logger level to INFO
    logger.setLevel(logging.INFO)

    # Create a handler for writing log messages to a file
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_handler = logging.FileHandler(f"logs/app_{timestamp}.log")
    file_handler.setLevel(logging.INFO)

    # Create a handler for printing log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Set a formatter for the log messages
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger 
  
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
        return engine
    except Exception as e: # Connection failed
        logger.critical(e)
        return None

def loadJSON(path):
    """
    Returns data from JSON file @ path
    """
    return json.load(open(path))

def createReport(start, end, report, test=False):
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
    Teams explored: {report.get("tExplored", 0)}
    Teams added: {report.get("tAdded", 0)}
    Matches explored: {report.get("mExplored", 0)}
    Matches added: {report.get("mAdded", 0)}
    Player stats explored: {report.get("psExplored", 0)}
    Player stats added: {report.get("psAdded", 0)}
    Players explored: {report.get("pExplored", 0)}
    Players updated: {report.get("pUpdated", 0)}
    Players added: {report.get("pAdded", 0)}
    -------------------
    """
    
    # Decide filename
    today = dt.datetime.now()
    formattedDate = today.strftime("%d %B %Y").lower()
    filename = f"report {formattedDate}.txt"
    
    # Create and write to file
    if not test:
        with open(os.path.join("reports", filename), "w") as f:
            f.write(reportContent)
    
    # Confirm that the report was created by returning filename
    logger.info(f"Report saved as {filename}")

if __name__ == "__main__":
    
    # Start logging session
    exceptions = Counter() # class to track number of each exception instance
    logger = initLogger() # initialize logger
    
    # Run program
    runner()