def calculate_real_odds(probabilities):
    """ Returns a real odds distribution based on the probabilities """
    real_odds = []
    for probability in probabilities:
        real_odds.append(1 / probability)
    
    return real_odds

def find_value(real_odds, norsk_tipping):
    """ Returns potential value after comparing real odds vs norsk tipping odds"""
    advice  = []

    for real_odds, odds in zip(real_odds, norsk_tipping):
        
        expected_value = (odds / real_odds) - 1
        
        if expected_value < 0:
            advice.append("No value")
        elif expected_value > 0.01:
            advice.append("Value")

    return advice