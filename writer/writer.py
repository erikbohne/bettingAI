import json
import sys
import os
import sqlalchemy
import datetime as dt

from google.cloud.sql.connector import Connector

from colorama import Fore
from values import *
from scraper import *


def runner():
    """
    Main function of the program that runs the logic
    """
    
    startTime = dt.datetime.now()
    
    print("Connecting to PostgreSQL...")
    if not initPostgreSQL():
        sys.exit(Fore.RED + "-> Could not connect to PostgreSQL")
    else:
        print(Fore.GREEN + "-> Connected to PostgreSQL")
    
    leagues = loadJSON("leagues.json")
    
    for league in leagues.keys():
        break
        print(f"Updating {league}")
        for team in leagues[league]["teams"]:
            
            fixtures = get_match_links(team["id"], team["UrlName"]) # Gets a list of all matches for the team
            players = get_player_links(team["id"]) # Gets a list of all players of the team
            
            for fixture in fixtures:
                # Gather info about that fixture
                try:
                    matchStats, playerStats = get_match_info(fixture)
                except:
                    continue
                
                # TODO Add fixture to the databse
                matchID = fixture.split("/")[2]
                ref = db.reference(f"/{league['name']}/{team['name']}")
                ref = ref.child(f"{matchID}")
                ref.set(matchStats)
                ref = ref.child("Players")
                ref.set(playerStats)
                
            for player in players:
                # TODO: 
                # 1 - Gather info about current player
                try:
                    players.append(get_player_bio(player))
                except:
                    pass
                # 2 - Update info about player in the database
            #for round in ROUNDS:
                # TODO: 
                # 1 - Calculate new table for current previous round
                # 2 - Update database
    
    # Get the end time of the data gathering
    endTime = dt.datetime.now()
    
    # For test purposes only
    dictionary = {
        "mExplored" : 4,
        "mAdded" : 2,
        "pExplored" : 34,
        "pAdded" : 2
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
        pool = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getConnection,
        )
    except Exception as e: # Connection failed
        print(f"Error: {e}")
        return False 
    
    return True

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