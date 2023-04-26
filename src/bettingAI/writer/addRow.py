from typing import Optional, Tuple, Mapping

from bettingAI.writer.databaseClasses import *

def add_team(id: int, name: str, league_id: int, stadium: Optional[str] = "NA") -> Teams:
    
    team = Teams(id = id,
                 name = name,
                 stadium = stadium,
                 league_id = league_id)
    
    return team

def add_match(id: int, season: str, matchStats: Mapping) -> Tuple[Matches, MatchStats, MatchStats]:
    
    # main info
    match = Matches(id = id,
                    home_team_id = matchStats["maininfo"]["homeID"], 
                    away_team_id = matchStats["maininfo"]["awayID"], 
                    league_id = matchStats["league"]["id"], 
                    season = season,
                    date = matchStats["dtg"],
                    home_goals = matchStats["maininfo"]["homescore"],
                    away_goals = matchStats["maininfo"]["awayscore"])
                    
    # home side statistics
    homeSide = MatchStats(match_id = id,
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
                    
    # away side statistics
    awaySide = MatchStats(match_id = id,
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
    
    return match, homeSide, awaySide

def add_player_performance(match_id: int, playerStats: Mapping, player: str) -> PlayerStats:
    
    playerPerformance = PlayerStats(player_id = playerStats[player]["id"],
                                    match_id = match_id,
                                    
                                    rating = playerStats[player]["fotmob rating"],
                                    minutes_played = playerStats[player]["minutes played"],
                                    goals = playerStats[player]["goals"],
                                    assists = playerStats[player]["assists"],
                                    shots = playerStats[player]["shots"],
                                    passes = playerStats[player]["passes"].split("/")[0],
                                    passes_accuracy = int(float(playerStats[player]["passes"].split("/")[0]) / float(playerStats[player]["passes"].split("/")[1])),
                                    chances_created = playerStats[player]["chances created"],
                                    touches = playerStats[player]["touches"],
                                    passes_into_final_third = playerStats[player]["passes into final third"],
                                    dispossesed = playerStats[player]["dispossessed"],
                                    tackles_won = playerStats[player]["tackles won"].split("/")[0],
                                    tackles_accuracy = int(float(playerStats[player]["tackles won"].split("/")[0]) / float(playerStats[player]["tackles won"].split("/")[1])),
                                    recoveries = playerStats[player]["recoveries"],
                                    ground_duels_won = playerStats[player]["ground duels won"].split("/")[0],
                                    aerial_duels_won = playerStats[player]["aerial duels won"].split("/")[0],
                                    was_fouled = playerStats[player]["was fouled"],
                                    fouls_committed = playerStats[player]["fouls committed"])
    
    return playerPerformance

def add_player_bio(playerID: int, teamID: int, name: str, stats: Mapping) -> Players:
    
    playerBio = Players(id=playerID,
                        team_id=int(teamID),
                        name=name if name else "NA",
                        age=int(stats["bio"].get("Age")) if stats["bio"].get("Age") else 0,
                        country=stats["bio"].get("Country") if stats["bio"].get("Country") else "NA",
                        height=int(stats["bio"].get("Height")) if stats["bio"].get("Height") else 0,
                        market_val=stats["bio"].get("Market") if stats["bio"].get("Market") else "NA",
                        primary_position=stats["bio"].get("position") if stats["bio"].get("position") else "NA",
                        played=int(stats["season"].get("Matches")) if stats["season"].get("Matches") else 0,
                        goals=int(stats["season"].get("Goals")) if stats["season"].get("Goals") else 0,
                        assists=int(stats["season"].get("Assists")) if stats["season"].get("Assists") else 0,
                        rating=float(stats["season"].get("FotMob")) if stats["season"].get("FotMob") else 0.0)
    
    return playerBio