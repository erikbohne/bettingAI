"""
Program to test The Odds API!
"""
import requests
import json

API_KEY = "ba3d67199a51d1b78c33465778749672"

def get_odds(league_id, REGIONS='uk', MARKETS='h2h', ODDS_FORMAT='decimal', DATE_FORMAT='iso'):
    
    SPORT = sport_from_id(league_id)
    
    response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    })
    
    if response.status_code == 200:
        data = response.json()
        unibet_odds = extract_unibet_odds(data)
        return unibet_odds
        print(unibet_odds)
    else:
        print(f"Request failed with status code {response.status_code}")
        
def extract_unibet_odds(json_data):
    odds = {}
    
    for match in json_data:
        home_team = match['home_team']
        away_team = match['away_team']
        match_key = f"{home_team} vs {away_team}"
        
        for bookmaker in match['bookmakers']:
            if bookmaker['key'] == 'unibet_uk':
                for market in bookmaker['markets']:
                    if market['key'] == 'h2h':
                        outcomes = market['outcomes']
                        home_odds = [outcome['price'] for outcome in outcomes if outcome['name'] == home_team][0]
                        draw_odds = [outcome['price'] for outcome in outcomes if outcome['name'] == 'Draw'][0]
                        away_odds = [outcome['price'] for outcome in outcomes if outcome['name'] == away_team][0]
                        
                        odds[match_key] = {
                            'h': home_odds,
                            'd': draw_odds,
                            'a': away_odds
                        }
                        break
                break
                
    return odds

def sport_from_id(league_id):
    with open("/Users/eriknymobohne/Documents/vscode/machine-learning/tipping/bettingAI/bettingAI/src/bettingAI/oddsapi/sport_id.json") as f:
        ids = json.load(f)
        
    return ids[league_id]
    
    
if __name__ == "__main__":
    
    SPORT = "47"
    REGIONS = 'uk' # uk | us | eu | au. Multiple can be specified if comma delimited
    MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited
    ODDS_FORMAT = 'decimal' # decimal | american
    DATE_FORMAT = 'iso' # iso | unix
    
    get_odds(SPORT, REGIONS, MARKETS, ODDS_FORMAT, DATE_FORMAT)