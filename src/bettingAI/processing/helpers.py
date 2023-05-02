import re


def euros_to_number(input):
    match = re.match(r"€([\d.]+)([MK]?)", input)
    if not match:
        raise ValueError("Invalid currency format")

    amount, unit = match.groups()
    amount = float(amount)

    if unit == "M":
        amount *= 1_000_000
    elif unit == "K":
        amount *= 1_000

    return int(amount)


def get_outcome(match, team_id):
    if match.home_team_id == team_id:
        if match.home_goals > match.away_goals:
            return 1
        elif match.home_goals < match.away_goals:
            return -1
        else:
            return 0
    else:
        if match.home_goals < match.away_goals:
            return 1
        elif match.home_goals > match.away_goals:
            return -1
        else:
            return 0
