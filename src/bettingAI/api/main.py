"""
API to connect backend with frondend
"""
# Database imports
from bettingAI.googleCloud.initPostgreSQL import initSession
from sqlalchemy import text

# API specific imports
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware if you're fetching data from another domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/matches")
async def get_matches():
    session = initSession()
    result_proxy = session.execute(text("""
        SELECT 
            schedule.match_id as id, 
            date as time, 
            home.name as home_team, 
            away.name as away_team, 
            odds[1] as h_odds, 
            odds[2] as u_odds, 
            odds[3] as b_odds,
            strength as strength, 
            value as value 
        FROM schedule
        INNER JOIN teams as home ON schedule.home_team_id = home.id
        INNER JOIN teams as away ON schedule.away_team_id = away.id
        INNER JOIN bets ON schedule.match_id = bets.match_id;
    """))

    # Fetch column names
    keys = result_proxy.keys()

    # Convert result to list of dictionaries
    matches = [dict(zip(keys, row)) for row in result_proxy.fetchall()]

    # Create a new list of dictionaries with the desired format
    formatted_matches = []
    for match in matches:
        formatted_matches.append({
            "id": match["id"],
            "time": match["time"].strftime('%b %d %H:%M'),
            "name": f"{match['home_team']} vs {match['away_team']}",
            "h": match["h_odds"],
            "u": match["u_odds"],
            "b": match["b_odds"],
            "strength": match["strength"],
            "value": match["value"],
        })

    return JSONResponse(content=formatted_matches)

@app.get("/performance")
async def performance():
    session = initSession()
    result_proxy = session.execute(text(
        "SELECT model_id, bet_n, odds, placed, outcome FROM model_performance ORDER BY model_id, bet_n;"
        ))
    
    keys = result_proxy.keys()
    performance_data = [dict(zip(keys, row)) for row in result_proxy.fetchall()]
    
    # Group the data by modelID
    grouped_data = {}
    for data in performance_data:
        if data["model_id"] not in grouped_data:
            grouped_data[data["model_id"]] = []
        grouped_data[data["model_id"]].append(data)
    
    # Calculate the profit and format the JSON
    formatted_data = []
    for modelID, model_data in grouped_data.items():
        profit = 0  # Starting profit
        data_points = []

        for bet in model_data:
            if bet["outcome"]:
                profit += bet["placed"] * (bet["odds"] - 1)
            else:
                profit -= bet["placed"]

            data_points.append({"x": bet["bet_n"], "y": profit})

        formatted_data.append({
            "id": f"model {modelID}",
            "color": "hsl(310, 70%, 50%)",
            "data": data_points,
        })

    return formatted_data

@app.get("/stats")
async def get_stats():
    session = initSession()

    combined_query = text("""
        SELECT
            SUM(CASE WHEN outcome = TRUE THEN placed * odds ELSE 0 END) AS total_won,
            COUNT(CASE WHEN outcome = TRUE THEN 1 END) AS bets_won,
            COUNT(id) AS total_bets
        FROM model_performance;
    """)

    result = session.execute(combined_query).fetchone()

    money_won_result = result[0]
    bets_won_result = result[1]
    total_bets_result = result[2]

    if total_bets_result > 0:
        winrate = bets_won_result / total_bets_result
    else:
        winrate = 0

    bets_placed = total_bets_result

    session.close()

    # Define previous values for demonstration purposes
    prev_money_won = 2000
    prev_bets_won = 5
    prev_bets_placed = 10
    prev_winrate = 0.34
    
    goal_money_won = 10000
    goal_bets_won = 50
    goal_bets_placed = 50
    goal_winrate = 0.75

    # Calculate the increase and progress values
    money_won_increase = (money_won_result - prev_money_won) / prev_money_won
    bets_won_increase = (bets_won_result - prev_bets_won) / prev_bets_won
    bets_placed_increase = (bets_placed - prev_bets_placed) / prev_bets_placed
    winrate_increase = (winrate - prev_winrate) / prev_winrate

    return {
        "money_won": {
            "title": f"{money_won_result:,.0f}",
            "subtitle": "Money Won",
            "progress": money_won_result / goal_money_won,
            "increase": f"{money_won_increase:.2%}"
        },
        "bets_won": {
            "title": f"{bets_won_result:,.0f}",
            "subtitle": "Bets Won",
            "progress": bets_won_result / goal_bets_won,
            "increase": f"{bets_won_increase:.2%}"
        },
        "winrate": {
            "title": f"{winrate:.2f}",
            "subtitle": "Winrate",
            "progress": winrate / goal_winrate,
            "increase": f"{winrate_increase:.2%}"
        },
        "bets_placed": {
            "title": f"{bets_placed:,.0f}",
            "subtitle": "Bets Placed",
            "progress": bets_placed / goal_bets_placed,
            "increase": f"{bets_placed_increase:.2%}"
        },
    }