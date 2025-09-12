import sqlite3
from .config import DB_FILE

def safe_db_operation(operation_func, *args, **kwargs):
    """
    Helper function to safely execute database operations with proper connection management.
    
    Args:
        operation_func: Function that takes a cursor and performs database operations
        *args, **kwargs: Arguments to pass to the operation function
    
    Returns:
        Result of the operation function, or None if an error occurred
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        result = operation_func(cursor, *args, **kwargs)
        conn.commit()
        return result
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def init_db():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # Clients table
        c.execute('''CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            date_of_birth TEXT,
            place_of_birth TEXT,
            date_joined TEXT NOT NULL,
            sessions_done INTEGER DEFAULT 0,
            total_paid REAL DEFAULT 0,
            total_amount_required REAL NOT NULL,
            license_type TEXT NOT NULL,
            checked_out INTEGER DEFAULT 0
        )''')
        # Migration: add columns if they do not exist
        c.execute("PRAGMA table_info(clients)")
        columns = [row[1] for row in c.fetchall()]
        if 'date_of_birth' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN date_of_birth TEXT")
        if 'place_of_birth' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN place_of_birth TEXT")
        if 'checked_out' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN checked_out INTEGER DEFAULT 0")
        if 'numero_dossier' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN numero_dossier TEXT")
        if 'fathers_name' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN fathers_name TEXT")
        if 'gender' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN gender TEXT")
        if 'image_path' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN image_path TEXT")
        if 'blood_type' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN blood_type TEXT")
        # Payments table
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY(client_id) REFERENCES clients(id)
        )''')
        # Sessions table
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY(client_id) REFERENCES clients(id)
        )''')
        # Examen groups table (add license_type if not exists)
        c.execute('''CREATE TABLE IF NOT EXISTS examen_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            examen_date TEXT NOT NULL
        )''')
        c.execute("PRAGMA table_info(examen_groups)")
        tg_columns = [row[1] for row in c.fetchall()]
        if 'license_type' not in tg_columns:
            c.execute("ALTER TABLE examen_groups ADD COLUMN license_type TEXT")
        if 'centre_examen' not in tg_columns:
            c.execute("ALTER TABLE examen_groups ADD COLUMN centre_examen TEXT")
        # Examen group candidates table
        c.execute('''CREATE TABLE IF NOT EXISTS examen_group_candidates (
            group_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            examen_type TEXT NOT NULL,
            result TEXT,
            FOREIGN KEY(group_id) REFERENCES examen_groups(id),
            FOREIGN KEY(candidate_id) REFERENCES clients(id)
        )''')
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()
