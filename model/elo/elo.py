import pandas as pd

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
    
    expected_home = 1 / (1 + 10 ** ((awayElo - homeElo - homeAdvantage) / 400))
    expected_away = 1 / (1 + 10 ** ((homeElo - awayElo + homeAdvantage) / 400))

    
    if result == 'H':
        home_score, away_score = 1, -1
    elif result == 'D':
        home_score, away_score = 0.5, 0.5
    elif result == 'A':
        home_score, away_score = -1, 1
    
    print(expected_home)
    print(expected_away)
        
    newHomeElo = homeElo + k * (home_score * expected_home)
    newAwayElo = awayElo + k * (away_score * expected_away)
    
    return newHomeElo, newAwayElo

if __name__ == "__main__":
    main()