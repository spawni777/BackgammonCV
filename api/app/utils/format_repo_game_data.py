import random

def format_repo_game_data(data):
    checker_positions = data['checker_position']
    dices = data['dices']
    
    # Initialize the result dictionary
    result = {
        "checkerPositions": {},
        "dices": []
    }
    
    # Transform checker positions
    for i, position in enumerate(checker_positions, start=1):
        if position > 0:
            result["checkerPositions"][str(i)] = ["player_1"] * position
        elif position < 0:
            result["checkerPositions"][str(i)] = ["player_2"] * abs(position)
        else:
            result["checkerPositions"][str(i)] = []

    # Transform dice values with a dummy confidence score
    for dice in dices:
        result["dices"].append({
            "confidence": random.uniform(0.9, 1.0),  # You can replace this with actual confidence
            "value": dice
        })

    return result