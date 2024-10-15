import subprocess
import json
import re

def map_player_name_to_number(player_name):
    if player_name == "player_1":
        return 0
    elif player_name == "player_2":
        return 1
    else:
        raise ValueError("Invalid player name. Should be 'player_1' or 'player_2'.")

def generate_set_board_command(game_data, your_player_number):
    checker_positions = game_data['checker_positions']
    board_positions = []
    for point in range(1, 25):
        point_str = str(point)
        checkers = checker_positions.get(point_str, [])
        count = len(checkers)
        if count == 0:
            board_positions.append(0)
        else:
            first_checker = checkers[0]
            if first_checker == 'player_1':
                player_num = 0
            elif first_checker == 'player_2':
                player_num = 1
            else:
                raise ValueError(f"Invalid player in checker_positions at point {point}")
            if player_num == your_player_number:
                board_positions.append(count)
            else:
                board_positions.append(-count)
    # Convert the list to a string of numbers separated by spaces
    board_positions_str = ' '.join(map(str, board_positions))
    set_board_command = f"set board {board_positions_str}"
    return set_board_command

def generate_set_dice_command(game_data):
    dices = game_data['dices']
    if len(dices) != 2:
        raise ValueError("There should be exactly two dice values.")
    dice_values = [dice['value'] for dice in dices]
    set_dice_command = f"set dice {dice_values[0]} {dice_values[1]}"
    return set_dice_command

def generate_set_turn_command(your_player_number):
    set_turn_command = f"set turn {your_player_number}"
    return set_turn_command


def start_gnubg_subprocess():
    gnubg_process = subprocess.Popen(
        ['gnubg', '--tty'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    return gnubg_process

def send_commands_to_gnubg(gnubg_process, commands):
    for command in commands:
        gnubg_process.stdin.write(command + '\n')
        gnubg_process.stdin.flush()
        # Optionally, read the output to ensure gnubg has processed the command
        # gnubg_process.stdout.readline()

def get_hints_from_gnubg(gnubg_process):
    gnubg_process.stdin.write('hint\n')
    gnubg_process.stdin.flush()
    
    hints = []
    while True:
        line = gnubg_process.stdout.readline()
        if not line:
            break
        line = line.strip()
        if line == '':
            continue
        if re.match(r'\d+\.', line):
            hints.append(line)
        elif 'Rollout' in line or 'pip' in line:
            break  # End of hint output
    return hints

def parse_hints(hints):
    parsed_hints = []
    for line in hints:
        # Example line:
        # "1. Cubeful 2-ply    13/7 13/10 8/5               Eq.: -0.797"
        match = re.match(r'(\d+)\.\s+.*?\s+([\d/ ()]+)\s+Eq\.\:\s+([-\d\.]+)', line)
        if match:
            move_number = int(match.group(1))
            moves = match.group(2).strip()
            equity = float(match.group(3))
            parsed_hints.append({
                'move_number': move_number,
                'moves': moves,
                'equity': equity
            })
    return parsed_hints

def get_gnubg_hints(player, game_data):
    player_number = map_player_name_to_number(player)
    
    set_board_command = generate_set_board_command(game_data, player_number)
    set_dice_command = generate_set_dice_command(game_data)
    set_turn_command = generate_set_turn_command(player_number)

    # Start GNU Backgammon
    gnubg_process = start_gnubg_subprocess()
    
    # Commands to set up the match and board
    commands = [
        'new match 1',  # Start a new match to 1 point
        set_board_command,
        set_dice_command,
        set_turn_command,
        # Set analysis level if desired
        # 'set analysis chequer eval plies 2',
        # 'set analysis movefilter 0 0 0 0 0 0',
        # 'set analysis luck adjusted off',
        # 'set analysis enable on',
    ]
    
    send_commands_to_gnubg(gnubg_process, commands)
    
    # Get hints
    hints = get_hints_from_gnubg(gnubg_process)
    
    # Close the gnubg process
    gnubg_process.stdin.close()
    gnubg_process.terminate()
    
    # Parse and return the hints
    parsed_hints = parse_hints(hints)
    return parsed_hints

# Example usage:
if __name__ == "__main__":
    player = 'player_1'
    game_data = {
        "checker_positions": {
            "1": ["player_2", "player_2", "player_2"],
            "2": ["player_2", "player_2"],
            "3": [],
            "4": [],
            "5": [],
            "6": [],
            "7": [],
            "8": ["player_1"],
            "9": [],
            "10": ["player_1"],
            "11": ["player_1"],
            "12": ["player_1"],
            "13": ["player_2"],
            "14": ["player_1"],
            "15": [],
            "16": [],
            "17": ["player_1", "player_1"],
            "18": ["player_1"],
            "19": ["player_1", "player_1", "player_1", "player_1"],
            "20": ["player_1", "player_1"],
            "21": [],
            "22": [],
            "23": ["player_1"],
            "24": []
        },
        "dices": [
            {
                "confidence": 0.9805632829666138,
                "value": 3
            },
            {
                "confidence": 0.7749348282814026,
                "value": 3
            }
        ]
    }
    
    hints = get_gnubg_hints(player, game_data)
    for hint in hints:
        print(f"Move {hint['move_number']}: {hint['moves']} with equity {hint['equity']}")
