"""
API to connect backend with frondend
"""
# Database imports
from bettingAI.googleCloud.initPostgreSQL import initSession
from sqlalchemy import text

# API specific imports
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Helper imports
from datetime import timedelta

app = FastAPI()

# Add CORS middleware if you're fetching data from another domain
@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
    return response


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
            value as value,
            change as change
        FROM schedule
        INNER JOIN teams as home ON schedule.home_team_id = home.id
        INNER JOIN teams as away ON schedule.away_team_id = away.id
        INNER JOIN bets ON schedule.match_id = bets.match_id
        ORDER BY time ASC;
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
            "time": (match["time"] + timedelta(hours=2)).strftime('%b %d %H:%M'),
            "name": f"{match['home_team']} vs {match['away_team']}",
            "h": match["h_odds"],
            "u": match["u_odds"],
            "b": match["b_odds"],
            "strength": match["strength"],
            "value": match["value"],
            "change": match["change"]
        })

    return JSONResponse(content=formatted_matches)

@app.get("/performance")
async def performance():
    session = initSession()
    result_proxy = session.execute(text(
        "SELECT id, model_id, bet_type, bet_outcome, odds, placed, outcome FROM performance ORDER BY id;"
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
        data_points = [{"x": 0, "y": 0}]  # Start with a data point at x=0, y=0

        for bet in model_data:
            # Determine which odds value to use
            if bet["bet_outcome"] == "H":
                odds = bet["odds"][0]  # Use first odds value for home outcome
            elif bet["bet_outcome"] == "D":
                odds = bet["odds"][1]  # Use second odds value for draw outcome
            else:
                odds = bet["odds"][2]  # Use third odds value for away outcome

            if bet["outcome"]:
                profit += bet["placed"] * (odds - 1)
            else:
                profit -= bet["placed"]

            data_points.append({"x": bet["id"], "y": profit})

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
            SUM(CASE WHEN outcome = TRUE THEN placed * 
                CASE
                    WHEN bet_outcome = 'H' THEN odds[1]
                    WHEN bet_outcome = 'D' THEN odds[2]
                    WHEN bet_outcome = 'A' THEN odds[3]
                END
            ELSE 0 END) AS total_won,
            COUNT(CASE WHEN outcome = TRUE THEN 1 END) AS bets_won,
            COUNT(id) AS total_bets
        FROM performance;
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
    prev_money_won = 912
    prev_bets_won = 5
    prev_bets_placed = 5
    prev_winrate = 0.13
    
    goal_money_won = 5000
    goal_bets_won = 10
    goal_bets_placed = 50
    goal_winrate = 0.25

    # Calculate the increase and progress values
    money_won_increase = (money_won_result - prev_money_won) / prev_money_won if prev_money_won > 0 else 0
    bets_won_increase = (bets_won_result - prev_bets_won) / prev_bets_won if prev_bets_won > 0 else 0
    bets_placed_increase = (bets_placed - prev_bets_placed) / prev_bets_placed if prev_bets_placed > 0 else 0
    winrate_increase = (winrate - prev_winrate) / prev_winrate if prev_winrate > 0 else 0

    return {
        "money_won": {
            "title": f"{money_won_result:,.0f}",
            "subtitle": "Money Won",
            "progress": money_won_result / goal_money_won if goal_money_won > 0 else 0,
            "increase": f"{money_won_increase:.2%}"
        },
        "bets_won": {
            "title": f"{bets_won_result:,.0f}",
            "subtitle": "Bets Won",
            "progress": bets_won_result / goal_bets_won if goal_bets_won > 0 else 0,
            "increase": f"{bets_won_increase:.2%}"
        },
        "winrate": {
            "title": f"{winrate:.2f}",
            "subtitle": "Winrate",
            "progress": winrate / goal_winrate if goal_winrate > 0 else 0,
            "increase": f"{winrate_increase:.2%}"
        },
        "bets_placed": {
            "title": f"{bets_placed:,.0f}",
            "subtitle": "Bets Placed",
            "progress": bets_placed / goal_bets_placed if goal_bets_placed > 0 else 0,
            "increase": f"{bets_placed_increase:.2%}"
        },
    }
    
@app.get("/match/{id}")
async def get_match(id: int):
    session = initSession()

    # Fetch match details along with associated odds
    result_proxy = session.execute(text(
        f"""
        SELECT 
            s.match_id as id, 
            s.date as time, 
            s.home_team_id, 
            s.away_team_id, 
            b.odds[1] as h_odds, 
            b.odds[2] as u_odds, 
            b.odds[3] as b_odds
        FROM schedule s
        LEFT JOIN bets b ON s.match_id = b.match_id
        WHERE s.match_id = :match_id;
        """),
        {'match_id': id}
    )

    result = result_proxy.fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="Match not found")

    keys = result_proxy.keys()
    match_info = dict(zip(keys, result))

    formatted_match = {
        "id": match_info["id"],
        "time": (match_info["time"] + timedelta(hours=2)).strftime('%b %d %H:%M'),
        "team1_id": match_info["home_team_id"],
        "team2_id": match_info["away_team_id"],
        "h_odds": match_info["h_odds"],
        "u_odds": match_info["u_odds"],
        "b_odds": match_info["b_odds"]
    }

    return JSONResponse(content=formatted_match)


@app.get("/history")
async def get_history():
    session = initSession()
    result_proxy = session.execute(text("""
        SELECT
            p.id,
            p.match_id as id,
            s.date as time,
            home.name as home_team,
            away.name as away_team,
            p.odds as odds,
            p.bet_outcome as outcome,
            p.outcome as result
        FROM performance as p
        INNER JOIN schedule as s ON p.match_id = s.match_id
        INNER JOIN teams as home ON s.home_team_id = home.id
        INNER JOIN teams as away ON s.away_team_id = away.id
        ORDER BY time DESC
        LIMIT 100;
    """))

    # Fetch column names
    keys = result_proxy.keys()

    # Convert result to list of dictionaries
    bets = [dict(zip(keys, row)) for row in result_proxy.fetchall()]

    # Create a new list of dictionaries with the desired format
    formatted_bets = []
    for bet in bets:
        formatted_bets.append({
            "id": bet["id"],
            "time": bet["time"].strftime('%b %d %H:%M'),
            "name": f"{bet['home_team']} vs {bet['away_team']}",
            "odds": bet["odds"],
            "outcome": bet["outcome"],
            "result": bet["result"],
        })

    return JSONResponse(content=formatted_bets)
