import firebase_admin
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
    
    for league in LEAGUES:
        for team in league["teams"]:
            
            fixtures = get_match_links(team["id"], team["UrlName"]) # Gets a list of all matches for the team
            players = get_player_links(team["id"]) # Gets a list of all players of the team
            
            for fixture in fixtures:
                # Gather info about that fixture
                info = get_match_info(fixture)
                
                # TODO Add fixture to the databse
                #ref = db.reference("/")
                #ref = ref.child(f"{fixture[1:]}")
                #ref.set(info)
                
            for player in players:
                # TODO: 
                # 1 - Gather info about current player
                info = get_player_info(player)
                # 2 - Update info about player in the database
            #for round in ROUNDS:
                # TODO: 
                # 1 - Calculate new table for current previous round
                # 2 - Update database
                
def initFirebase():
    """
    Connects and initializes Firebase
    """
    cred = credentials.Certificate("../keys/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
    "databaseURL" : "https://tipping-c53ce-default-rtdb.europe-west1.firebasedatabase.app"
    })
    
    return True
    

if __name__ == "__main__":
    runner()