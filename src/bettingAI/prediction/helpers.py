from sqlalchemy import text
import textdistance

def calculate_real_odds(probabilities):
    """ Returns a real odds distribution based on the probabilities """
    real_odds = []
    for probability in probabilities:
        real_odds.append(1 / probability)
    
    return real_odds

def find_value(real_odds, bookmaker):
    """ Returns the outcome with the highest expected value and its value """
    outcomes = ["H", "U", "B"]
    max_expected_value = 0
    max_expected_outcome = ""
    bet_strength = 0

    for real_odds, odds, outcome in zip(real_odds, bookmaker, outcomes):
        expected_value = (odds / real_odds)

        if expected_value > max_expected_value:
            max_expected_value = expected_value
            max_expected_outcome = outcome
            bet_strength = expected_value

    return max_expected_outcome, bet_strength

def get_team_names(session):
    query = text("SELECT id, name FROM teams")
    result = session.execute(query)
    team_names = {}
    for row in result:
        team_names[row[0]] = row[1]
    return team_names

def match_team_names(team1, team2, threshold=0.7):
    similarity = textdistance.jaro_winkler(team1.lower(), team2.lower())
    return similarity >= threshold
