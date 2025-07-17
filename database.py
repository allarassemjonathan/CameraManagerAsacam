import sqlite3
import os
from contextlib import contextmanager

class CameraDatabase:
    def __init__(self, db_path='cameras.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with the cameras table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cameras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    link TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        try:
            yield conn
        finally:
            conn.close()
    
    def add_camera(self, name, link):
        """Add a new camera to the database"""
        with self.get_db_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO cameras (name, link) VALUES (?, ?)',
                (name, link)
        )
        conn.commit()
        return cursor.lastrowid
    
    def get_all_cameras(self):
        """Get all cameras from the database"""
        with self.get_db_connection() as conn:
            cameras = conn.execute('SELECT * FROM cameras ORDER BY name').fetchall()
            return [dict(camera) for camera in cameras]
    
    def search_cameras(self, query):
        """Search cameras by name or link"""
        with self.get_db_connection() as conn:
            cameras = conn.execute(
                'SELECT * FROM cameras WHERE name LIKE ? OR link LIKE ? ORDER BY name',
                (f'%{query}%', f'%{query}%')
            ).fetchall()
            return [dict(camera) for camera in cameras]
    
    def get_camera_by_id(self, camera_id):
        """Get a specific camera by ID"""
        with self.get_db_connection() as conn:
            camera = conn.execute(
                'SELECT * FROM cameras WHERE id = ?',
                (camera_id,)
            ).fetchone()
            return dict(camera) if camera else None
    
    def update_camera(self, camera_id, name, link):
        """Update an existing camera"""
        with self.get_db_connection() as conn:
            conn.execute(
                'UPDATE cameras SET name = ?, link = ? WHERE id = ?',
                (name, link, camera_id)
            )
            conn.commit()
            return conn.rowcount > 0
    
    def delete_camera(self, camera_id):
        """Delete a camera by ID"""
        with self.get_db_connection() as conn:
            conn.execute('DELETE FROM cameras WHERE id = ?', (camera_id,))
            conn.commit()
            return conn.rowcount > 0