import pandas as pd

import sys
sys.path.insert(1, '../../writer')

from writer import initPostgreSQL

def main():
    
    engine = initPostgreSQL()
    
    teams_ids = None # TODO fetch from postgresql database
    
    # Assign a starting elo of 1000 for every team
    elo_ratings = {team_id: 1000 for team_id in teams_ids}
    
    # Fetch all matches in chronological order
    query = '''
    SELECT id, home_team_id, away_team_id, home_goals, away_goals
    FROM matches
    ORDER BY date ASC
    '''

    matches = pd.read_sql(query, con=engine)

    # Iterate through matches and update Elo ratings
    for _, match in matches.iterrows():
        match_id = match['id']
        home_team_id = match['home_team_id']
        away_team_id = match['away_team_id']
        home_goals = match['home_goals']
        away_goals = match['away_goals']
        
        # Determine the result of the match
        if home_goals > away_goals:
            result = 'H'
        elif home_goals == away_goals:
            result = 'D'
        else:
            result = 'A'
            
        # Get the current Elo ratings for the teams
        home_elo = elo_ratings[home_team_id]
        away_elo = elo_ratings[away_team_id]
        
        # Update Elo ratings
        new_home_elo, new_away_elo = updateElo(home_elo, away_elo, result)
        elo_ratings[home_team_id] = new_home_elo
        elo_ratings[away_team_id] = new_away_elo
    

def updateElo(homeElo, awayElo, result, k=32, homeAdvantage=100):
    
    diff = 1 + abs(homeElo - awayElo) / 1000
    
    expected_home = 1 / (1 + 10 ** ((awayElo - homeElo - homeAdvantage) / 400))
    expected_away = 1 / (1 + 10 ** ((homeElo - awayElo + homeAdvantage) / 400))
    
    # Estimate draw probability
    prob_draw = 1 - abs(expected_home - expected_away)
    prob_home = expected_home * (1 - prob_draw)
    prob_away = expected_away * (1 - prob_draw)

    # Normalize probabilities
    normalization_factor = prob_home + prob_draw + prob_away
    prob_home /= normalization_factor
    prob_draw /= normalization_factor
    prob_away /= normalization_factor
    
    if result == 'H':
        home_score, away_score = 1, -1
        expectancy = prob_home
    elif result == 'D':
        home_score, away_score = 0.2, 0.2
        expectancy = prob_draw
    elif result == 'A':
        home_score, away_score = -1, 1
        expectancy = prob_away
    
    print("Probability Home Win:", prob_home)
    print("Probability Draw:", prob_draw)
    print("Probability Away Win:", prob_away)
        
    newHomeElo = homeElo + k * (home_score * (1 - expectancy) * diff)
    newAwayElo = awayElo + k * (away_score * (1 - expectancy) * diff)
    
    return newHomeElo, newAwayElo


if __name__ == "__main__":
    main()