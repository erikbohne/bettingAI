"""
The goal of this program is to check what matches and players are added to the database and which are not.
To better understand why some dont get added.
"""
import os
import sys
import traceback

from google.cloud.sql.connector import Connector
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from bettingAI.googleCloud.initPostgreSQL import initPostgreSQL
from bettingAI.writer.databaseClasses import *
from bettingAI.writer.addRow import *
from bettingAI.writer.scraper import get_match_links, get_player_links, get_player_bio
from bettingAI.writer.values import SEASONS

def main(session: sqlalchemy.orm.Session) -> None:
    
    # Gather a list of the league ids
    leagues = session.query(Leagues).all()
    leagueIDs = [(league.id, league.year_span) for league in leagues]
    
    notInDatabase = {"matches" : {}, "players" : {}}
    
    for id, span in leagueIDs: # iterate over each league
        print(id)
        notInDatabase["matches"][id] = {}
        notInDatabase["players"][id] = {}
        
        for season in SEASONS[span]: # iterate through each season
            print(season)
            matches = [int(link.split("/")[2]) for link in get_match_links(id, season)]
            database = session.query(Matches).filter(and_(Matches.league_id == id, Matches.season == season))
            database = set([match.id for match in database])
            
            notInDatabase["matches"][id][season] = []
            for match in matches:
                if match not in database:
                    notInDatabase["matches"][id][season].append(match)

        continue
        teams = session.query(Teams).filter(Teams.league_id == id)
        teams = [team.id for team in teams]
        
        for team in teams: # iterate over each team
            continue
            players = [int(link.split("/")[2]) for link in get_player_links(team)]
            database = session.query(Players).filter(Players.team_id == team)
            database = set([player.id for player in database])

            notInDatabase["players"][id][team] = {}
            for player in players:
                if player not in database:
                    notInDatabase["players"][id][team][player] = str()
                    try:
                        print(f"Trying to add {player}")
                        session.add(add_player_bio(player, team, "test", get_player_bio(f"/players/{player}]")))
                        session.commit()
                    except Exception as e:
                        session.rollback()
                        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
                        print(player)
                        print("".join(tb_str))
                        exit()
                        notInDatabase["players"][id][team][player] = e
    
    print(notInDatabase["matches"][59])
            
            
    
if __name__ == "__main__":
    
    connection = initPostgreSQL()

    # Start session with connection
    Session = sessionmaker(connection)
    session = Session()
    
    main(session)
