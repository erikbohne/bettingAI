import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from values import *


def runner():
    """
    Main function of the program that runs the logic
    """
    
    print("Connecting to firebase...")
    if not initFirebase():
        raise ValueError("Could not connect to Firebase")
    
    for league in LEAGUES:
        for team in league["teams"]:
            # TODO: 
            # 1 - Get a link to all fixtures that are not saved
            fixtures = get_match_links()
            for fixture in fixtures:
                # TODO:
                # 1 - Gather info about that fixture
                # 2 - Add fixture to the databse
            for players in PLAYERS[team]:
                # TODO: 
                # 1 - Get a link to the current player
                # 2 - Gather info about current player
                # 3 - Update info about player in the database
            for round in ROUNDS:
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
    
    