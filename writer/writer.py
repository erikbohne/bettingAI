import firebase_admin
import json
from firebase_admin import credentials
from firebase_admin import db


from values import *
from scraper import *


def runner():
    """
    Main function of the program that runs the logic
    """
    
    print("Connecting to firebase...")
    if not initFirebase():
        raise ValueError("Could not connect to Firebase")
    else:
        print("-> Connected to firebase")
    
    leagues = loadLeagues()
    
    for league in leagues.keys():
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
            
                
def initFirebase():
    """
    Connects and initializes Firebase
    """
    cred = credentials.Certificate("../../keys/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
    "databaseURL" : "https://tipping-c53ce-default-rtdb.europe-west1.firebasedatabase.app"
    })
    
    return True

def loadLeagues():
    """
    Returns data from league
    """
    return json.load(open("leagues.json"))

def createReport(data):
    """
    Creates reports with information about the execution:
    
        - Time started
        - Time ended
        - Delta
        - Matches explored
        - Matches added
        - Players explored
        - Players added

    Saves report as a .txt file.
    """

if __name__ == "__main__":
    runner()