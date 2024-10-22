import os
import sqlite3
import json

from ..utils.format_repo_game_data import format_repo_game_data

class BackgammonRepository:
    def __init__(self, db_name='./app/data/db/backgammon.db'):
        # Ensure the 'data' directory exists
        if not os.path.exists(os.path.dirname(db_name)):
            os.makedirs(os.path.dirname(db_name))

        # Get the absolute path of the database file and print it
        # abs_db_path = os.path.abspath(db_name)
        # print(f"Database file path: {abs_db_path}")

        # Initialize the connection and create the tables if they don't exist
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Create table to store checker positions (if it doesn't exist)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS checker_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            positions TEXT NOT NULL
        )
        ''')

        # Create table to store dices (if it doesn't exist)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS dices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dice TEXT NOT NULL
        )
        ''')

        # Create table to info about player
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_player TEXT NOT NULL
        )
        ''')

        # Check if the checker_positions table has any records
        self.cursor.execute('SELECT COUNT(*) FROM checker_positions')
        count = self.cursor.fetchone()[0]

        if count == 0:
            initial_positions = [0] * 26  # 26 zeros for checker positions
            self.update(initial_positions, [{"value": 0, "randomized": False}, {"value": 0, "randomized": False}], "player_2")

    def derive_current_player(self, prev_data, new_data):
        prev_positions = prev_data['checkerPositions']
        new_positions = new_data['checkerPositions']
        player_moved = None

        for position in range(1, 25):
            str_position = str(position)
            prev_checkers = prev_positions.get(str_position, [])
            new_checkers = new_positions.get(str_position, [])
            
            # print(f'Index: {str_position}, len(new_checkers): {len(new_checkers)}, len(prev_checkers): {len(prev_checkers)}')
            if len(new_checkers) > len(prev_checkers):
                # A checker was added to this position
                added_checker = new_checkers[-1]  # The checker that was added
                if added_checker in ['player_1', 'player_2']:
                    player_moved = added_checker
                    break  # Found the move, exit loop
        
        if player_moved:
            print(f'player_moved: {player_moved}')
            return 'player_1' if player_moved == 'player_2' else 'player_2'
        else:
            # If no increase found, check for captures or default to previous player
            return prev_data.get('currentPlayer', 'player_1')

    def update(self, new_positions, dice_values, current_player=None):
        if len(new_positions) != 26:
            raise ValueError("The checker positions must have exactly 26 integers.")
        
        prev_checker_position, prev_dices, prev_current_player = self.get()

        prev_formatted_data = format_repo_game_data(prev_checker_position, prev_dices, prev_current_player)
        formatted_data = format_repo_game_data(new_positions[1:-1], dice_values, current_player)

        if current_player is None:
            current_player = self.derive_current_player(prev_formatted_data, formatted_data)

        # Serialize the arrays into JSON strings
        positions_str = json.dumps(new_positions)
        dice_str = json.dumps(dice_values)

        # Insert or update the checker positions, dices, and current player
        self.cursor.execute('INSERT INTO checker_positions (positions) VALUES (?)', (positions_str,))
        self.cursor.execute('INSERT INTO dices (dice) VALUES (?)', (dice_str,))
        self.cursor.execute('INSERT INTO game_state (current_player) VALUES (?)', (current_player,))
        self.conn.commit()


    def get(self):
        # Fetch the most recent checker positions
        self.cursor.execute('SELECT positions FROM checker_positions ORDER BY id DESC LIMIT 1')
        row = self.cursor.fetchone()
        checker_positions = json.loads(row[0]) if row else [0] * 26  # Default 26 zeros if no data exists

        # Fetch the most recent dices
        self.cursor.execute('SELECT dice FROM dices ORDER BY id DESC LIMIT 1')
        row = self.cursor.fetchone()
        dices = json.loads(row[0]) if row else [{"value": 0, "randomized": False}, {"value": 0, "randomized": False}]  # Default dice state

        # Fetch the most recent player turn
        self.cursor.execute('SELECT current_player FROM game_state ORDER BY id DESC LIMIT 1')
        row = self.cursor.fetchone()
        current_player = row[0] if row else "player_1"  # Default to player_1 if no data exists

        # Temp slice (we need to detect bar checkers later, now the first element and the last element are zeros)
        checker_positions = checker_positions[1:-1]

        return checker_positions, dices, current_player

    def generate_start_position(self):
        checker_positions = {str(i): 0 for i in range(1, 25)}

        # Assign checkers to the starting positions for player_1
        checker_positions["1"] = 2  # 2 checkers for player_1
        checker_positions["12"] = 5  # 5 checkers for player_1
        checker_positions["17"] = 3  # 3 checkers for player_1
        checker_positions["19"] = 5  # 5 checkers for player_1

        # Assign checkers to the starting positions for player_2 (negative values)
        checker_positions["24"] = -2  # 2 checkers for player_2
        checker_positions["13"] = -5  # 5 checkers for player_2
        checker_positions["8"] = -3  # 3 checkers for player_2
        checker_positions["6"] = -5  # 5 checkers for player_2

        return checker_positions


    def delete(self):
        # Delete the most recent checker positions entry
        self.cursor.execute('DELETE FROM checker_positions WHERE id = (SELECT id FROM checker_positions ORDER BY id DESC LIMIT 1)')
        
        # Delete the most recent dices entry
        self.cursor.execute('DELETE FROM dices WHERE id = (SELECT id FROM dices ORDER BY id DESC LIMIT 1)')

        # Delete the most recent game state entry
        self.cursor.execute('DELETE FROM game_state WHERE id = (SELECT id FROM game_state ORDER BY id DESC LIMIT 1)')
        
        # Commit the changes
        self.conn.commit()

        # After deletion, insert default values to ensure it is reset to player_1
        initial_positions_dict = self.generate_start_position()  # Use the generate_start_position method

        # Convert the dictionary to a list format, preserving the order of the positions from 1 to 24
        initial_positions = [initial_positions_dict[str(i)] for i in range(1, 25)]

        default_dices = [{"value": 0, "randomized": False}, {"value": 0, "randomized": False}]  # Default dice state
        default_current_player = "player_1"  # Default to player_1

        # Insert the default values
        self.update([0] + initial_positions + [0], default_dices, default_current_player)


    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    repo = BackgammonRepository()
    
    # Update the checker positions, dices, and current player
    new_positions = [1, 2, 0, 3, -1, 0, 0, 4, -3, 2, 1, 0, 0, 0, 0, -2, 0, 0, 5, -1, 0, 0, 3, 1]
    new_dices = [{"value": 6, "randomized": True}, {"value": 3, "randomized": True}]
    current_player = "player_2"
    repo.update(new_positions, new_dices, current_player)
    
    # Get the current checker positions, dices, and current player
    current_positions, current_dices, current_player = repo.get()
    print("Current checker positions:", current_positions)
    print("Current dice state:", current_dices)
    print("Current player:", current_player)
    
    # Delete the most recent entries
    repo.delete()
    print("Deleted the most recent checker positions, dices, and game state.")
    
    # Get the updated state after deletion
    updated_positions, updated_dices, updated_player = repo.get()
    print("Updated checker positions after deletion:", updated_positions)
    print("Updated dice state after deletion:", updated_dices)
    print("Updated player after deletion:", updated_player)
    
    # Close the repository
    repo.close()
