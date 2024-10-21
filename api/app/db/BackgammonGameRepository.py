import os
import sqlite3
import json

class BackgammonRepository:
    def __init__(self, db_name='./app/data/db/backgammon.db'):
        # Ensure the 'data' directory exists
        if not os.path.exists(os.path.dirname(db_name)):
            os.makedirs(os.path.dirname(db_name))

        # Get the absolute path of the database file and print it
        abs_db_path = os.path.abspath(db_name)
        print(f"Database file path: {abs_db_path}")

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

        # Check if the checker_positions table has any records
        self.cursor.execute('SELECT COUNT(*) FROM checker_positions')
        count = self.cursor.fetchone()[0]

        # If no data, initialize the checker positions with 26 zeros
        if count == 0:
            initial_positions = [0] * 26  # 26 zeros for checker positions
            self.update(initial_positions, [{"value": 0, "randomized": False}, {"value": 0, "randomized": False}])

    def update(self, new_positions, dice_values):
        if len(new_positions) != 26:
            raise ValueError("The checker positions must have exactly 26 integers.")

        # Serialize the arrays into JSON strings
        positions_str = json.dumps(new_positions)
        dice_str = json.dumps(dice_values)

        # Insert or update the checker positions and dices
        self.cursor.execute('INSERT INTO checker_positions (positions) VALUES (?)', (positions_str,))
        self.cursor.execute('INSERT INTO dices (dice) VALUES (?)', (dice_str,))
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

        # Temp slice (we need to detect bar checkers later, now the first element and the last element are zeros)
        checker_positions = checker_positions[1:-1]

        return checker_positions, dices

    def delete(self):
        # Delete the most recent checker positions entry
        self.cursor.execute('DELETE FROM checker_positions WHERE id = (SELECT id FROM checker_positions ORDER BY id DESC LIMIT 1)')
        
        # Delete the most recent dices entry
        self.cursor.execute('DELETE FROM dices WHERE id = (SELECT id FROM dices ORDER BY id DESC LIMIT 1)')
        
        self.conn.commit()

    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    repo = BackgammonRepository()
    
    # Update the checker positions and dices
    new_positions = [1, 2, 0, 3, -1, 0, 0, 4, -3, 2, 1, 0, 0, 0, 0, -2, 0, 0, 5, -1, 0, 0, 3, 1]
    new_dices = [{"value": 6, "randomized": True}, {"value": 3, "randomized": True}]
    repo.update(new_positions, new_dices)
    
    # Get the current checker positions and dices
    current_positions, current_dices = repo.get()
    print("Current checker positions:", current_positions)
    print("Current dice state:", current_dices)
    
    # Delete the most recent entries
    repo.delete()
    print("Deleted the most recent checker positions and dices.")
    
    # Get the updated state after deletion
    updated_positions, updated_dices = repo.get()
    print("Updated checker positions after deletion:", updated_positions)
    print("Updated dice state after deletion:", updated_dices)
    
    # Close the repository
    repo.close()
