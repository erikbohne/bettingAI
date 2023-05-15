"""
Program to fill up the Schedule table in the database
"""
from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.writer.scraper import get_match_links, get_next_match_info
from bettingAI.processing.features import features_for_model0
from bettingAI.writer.databaseClasses import Schedule
from tensorflow.keras.models import load_model
from tqdm.auto import tqdm
from helpers import *

# Odds API
from bettingAI.oddsapi.odds import get_odds

from datetime import datetime
import numpy as np
import traceback

SEASON = "2022-2023"

def fill_schedule(session):
    # Find matches for the league in the current season
    links, matches = [], []
    for id, season in [(59, "2023")]:
        links += get_match_links(id, season)
    
    for link in tqdm(links):
        info = get_next_match_info(link)
        if type(info) == dict:
            matchID = link.split("/")[2]
            
            try:
                session.add(Schedule(
                    match_id=matchID,
                    date=info["date"],
                    season=SEASON,
                    league_id=info["leagueID"],
                    home_team_id=info["teamID"],
                    away_team_id=info["opponentID"]
                ))
                session.commit()
            except Exception as e:
                session.rollback()
                print(e)
                traceback.print_exc()
                
    
if __name__ == "__main__":
    session = initSession()
    fill_schedule(session)