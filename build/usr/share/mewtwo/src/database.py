from src import functions
import os 
import sys
import sqlite3

#######################################################################
# Database Initialization
#######################################################################
chat_history_CREATE = '''
creaTE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    source_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''
config_CREATE = '''
CREATE TABLE IF NOT EXISTS config (
id INTEGER PRIMARY KEY AUTOINCREMENT,
openai_api_key TEXT,
org_id TEXT,
os_info TEXT,
text_color TEXT,
documentation_path TEXT,
sudo_password TEXT,
wsl INTEGER
)
'''
# Team database. Used to share team info.
def db_team():
    db_path = "/usr/share/mewtwo/mewtwo.db"
    conn = sqlite3.connect(db_path)
    return conn

# User's database.
def db_user():
    db_path = os.path.expanduser(os.path.join(functions.get_home_path(),".mewtwo.db"))
    conn = sqlite3.connect(db_path)
    return conn

def create_config(cursor):
    cursor.execute(config_CREATE)
    cursor.execute("SELECT COUNT(*) FROM config")
    count = cursor.fetchone()[0]

    if count == 0:
        os_info = functions.get_system_info()
        wsl = 1 if functions.is_wsl_subprocess() else 0
        cursor.execute("""
INSERT INTO config 
(openai_api_key, org_id, os_info, text_color, documentation_path, sudo_password, wsl) 
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (None, None, os_info, None,'/usr/share/mewtwo/Documentation/', None, wsl))

def initialize_team_db():
    db = db_team()
    cursor = db.cursor()
    cursor.execute(chat_history_CREATE) # not used but we'll create it for consistency anyways
    create_config(cursor)
    db.commit()
    db.close()

def initialize_user_db():
    db = db_user()
    cursor = db.cursor()
    cursor.execute(chat_history_CREATE)
    create_config(cursor)
    db.commit()
    db.close()


#----------------------------------------------------------------------
# Chat History
#----------------------------------------------------------------------
def update_chat_history(message, source_id=None):
    message_string = str(message)
    db = db_user()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO chat_history (message, source_id)
    VALUES (?,?)
    """, (message_string, source_id,))

    # Retrieve the id of the newly inserted row
    chat_id = cursor.lastrowid

    db.commit()
    db.close()

    return chat_id

def get_chat_history(limit=6):
    db = db_user()
    cursor = db.cursor()
    
    cursor.execute("""
    with starting_id as (
        select id from chat_history 
        where source_id is null
        order by timestamp desc
        limit ?
    ),
    tbl as (
        SELECT id, message, source_id, timestamp
        FROM chat_history
        where id >= (select min(id) from starting_id)
        ORDER BY timestamp desc
    )
    select * from tbl order by timestamp
    """, (limit,))  # Pass limit as a tuple
    
    # Fetch all results
    results = cursor.fetchall()
    
    db.close()
    
    return results

def get_chat_message(chat_id):
    db = db_user()
    cursor = db.cursor()

    cursor.execute("""
    SELECT message FROM chat_history
    WHERE id = ?
    """, (chat_id,))

    result = cursor.fetchone()
    db.close()

    if result:
        message = eval(result[0])  # Convert JSON string back to a dictionary
        return message
    else:
        return None  # Return None if no record is found

def clear_chat_history(conn):
    cursor = conn.cursor()
    cursor.execute("delete from chat_history")
    conn.commit()

def delete_chat_message(chat_id):
    db = db_user()
    cursor = db.cursor()
    cursor.execute("delete from chat_history where id = ?",(chat_id,))
    db.commit()
    db.close()

COLOR_OPTIONS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright black": "\033[90m",
    "bright red": "\033[91m",
    "bright green": "\033[92m",
    "bright yellow": "\033[93m",
    "bright blue": "\033[94m",
    "bright magenta": "\033[95m",
    "bright cyan": "\033[96m",
    "bright white": "\033[97m",
    "orange": "\033[38;5;214m",  # Approximate orange
    "lime": "\033[38;5;154m",    # Approximate lime
    "pink": "\033[38;5;213m",    # Approximate pink
    "purple": "\033[38;5;141m",  # Approximate purple
    "teal": "\033[38;5;37m",     # Approximate teal
    "olive": "\033[38;5;100m",   # Approximate olive
    "brown": "\033[38;5;94m",    # Approximate brown
    "gold": "\033[38;5;220m",    # Approximate gold
    "silver": "\033[38;5;250m",  # Approximate silver
    "navy": "\033[38;5;18m",     # Approximate navy
    "maroon": "\033[38;5;52m",   # Approximate maroon,
    "shiny mewtwo": "\033[38;5;110m",  # Approximate Cyan Azure
    "mewtwo": "\033[38;5;224m",  # Approximate Piggy Pink
}

def get_text_color():
    conn = db_user()
    c = conn.cursor()
    
    # Fetch the text_color from the config table
    c.execute("SELECT text_color FROM config ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    
    conn.close()
    
    if result:
        try:
            response = COLOR_OPTIONS[result[0]]
        except:
            response = None
        return response
    else:
        return None  # Return None if no color is found

def get_sudo():
    conn = db_user()
    c = conn.cursor()
    
    # Fetch the sudo_password from the config table
    c.execute("SELECT sudo_password FROM config ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return result[0]  # Return the sudo password if found
    else:
        return None  # Return None if no sudo password is found

def get_config():
    # Check the user's database first
    user_db = db_user()
    cursor = user_db.cursor()
    cursor.execute("SELECT openai_api_key, org_id, os_info, wsl FROM config")
    user_config = cursor.fetchone()
    user_db.close()

    # If the user's database has the API key, return it
    if user_config and user_config[0]:
        return {
            'openai_api_key': user_config[0],
            'openai_org_id': user_config[1],
            'os_info': user_config[2],
            'wsl': user_config[3]
        }

    # If not, check the team database
    team_db = db_team()
    cursor = team_db.cursor()
    cursor.execute("SELECT openai_api_key, org_id, os_info, wsl FROM config")
    team_config = cursor.fetchone()
    team_db.close()

    # If the team database has the API key, return it
    if team_config and team_config[0]:
        return {
            'openai_api_key': team_config[0],
            'openai_org_id': team_config[1],
            'os_info': team_config[2],
            'wsl': team_config[3]
        }

    # If neither database has the API key, raise an error and exit
    print("API key not found. Please run 'mewtwo-setup' to configure.")
    sys.exit(1)

def get_text_color():
    initialize_user_db()
    initialize_team_db()
    # Check the user's database first
    user_db = db_user()
    cursor = user_db.cursor()
    cursor.execute("SELECT text_color FROM config")
    user_text_color = cursor.fetchone()
    user_db.close()

    # If the user's database has the text color, return it
    if user_text_color and user_text_color[0]:
        response = COLOR_OPTIONS[user_text_color[0]]
        return response

    # If not, check the team database
    team_db = db_team()
    cursor = team_db.cursor()
    cursor.execute("SELECT text_color FROM config")
    team_text_color = cursor.fetchone()
    team_db.close()

    # If the team database has the text color, return it
    if team_text_color and team_text_color[0]:
        response = COLOR_OPTIONS[team_text_color[0]]
        return response

    # If neither database has the text color, return None
    return None

def get_documentation_path():
    initialize_user_db()
    initialize_team_db()
    # Check the user's database first
    user_db = db_user()
    cursor = user_db.cursor()
    cursor.execute("SELECT documentation_path FROM config")
    user_documentation_path = cursor.fetchone()
    user_db.close()

    # If the user's database has the text color, return it
    if user_documentation_path and user_documentation_path[0]:
        return user_documentation_path[0]

    # If not, check the team database
    team_db = db_team()
    cursor = team_db.cursor()
    cursor.execute("SELECT documentation_path FROM config")
    team_documentation_path = cursor.fetchone()
    team_db.close()

    # If the team database has the text color, return it
    if team_documentation_path and team_documentation_path[0]:
        return team_documentation_path[0]

    # If neither database has the text color, return default path
    return '/usr/share/mewtwo/Documentation/'