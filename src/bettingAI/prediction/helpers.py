from sqlalchemy import text
import textdistance

def calculate_real_odds(probabilities):
    """ Returns a real odds distribution based on the probabilities """
    real_odds = []
    for probability in probabilities:
        real_odds.append(1 / probability)
    
    return real_odds

def find_value(real_odds, bookmaker, threshold=0.01):
    """ Returns the outcome with the highest expected value above the given threshold and its value """
    outcomes = ["HOME VALUE", "DRAW VALUE", "AWAY VALUE"]
    max_expected_value = -1
    max_expected_outcome = "NO VALUE"
    bet_strength = 0

    for real_odds, odds, outcome in zip(real_odds, bookmaker, outcomes):
        expected_value = (odds / real_odds) - 1

        if expected_value > threshold and expected_value > max_expected_value:
            max_expected_value = expected_value
            max_expected_outcome = outcome
            bet_strength = odds / real_odds

    return max_expected_outcome, bet_strength

def get_team_names(session):
    query = text("SELECT id, name FROM teams")
    result = session.execute(query)
    team_names = {}
    for row in result:
        team_names[row[0]] = row[1]
    return team_names

def match_team_names(team1, team2, threshold=0.8):
    similarity = textdistance.jaro_winkler(team1.lower(), team2.lower())
    return similarity >= threshold
