import sqlite3
import time

class StateActionLogger:
    def __init__(self, db_path="shadow_mode.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS state_action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                rms REAL,
                centroid REAL,
                peak REAL,
                action_width REAL,
                action_ratio REAL
            )
        ''')
        self.conn.commit()

    def log(self, features, actions):
        """
        features: dict from shared memory
        actions: current DSP parameters (observed from engine)
        """
        self.cursor.execute('''
            INSERT INTO state_action_logs 
            (timestamp, rms, centroid, peak, action_width, action_ratio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            time.time(),
            features['rms'],
            features['centroid'],
            features['peak'],
            actions.get('width', 0),
            actions.get('ratio', 0)
        ))
        self.conn.commit()

    def close(self):
        self.conn.close()
