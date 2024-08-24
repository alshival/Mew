#!/usr/share/mewtwo/mewtwo-env/bin/python3

import getpass
import os
import sys
from src import database
import subprocess
from RAG import monitorDocs

def print_help():
    print("Usage: mewtwo-setup [options] [command]\n")
    print("Documentation path: `/usr/share/mewtwo/Documentation`")
    print("mewtwo is able to provide support with documentation stored in this directory.\n")
    print("After updating documentation, run `mewtwo-setup rag` to update mewtwo's search algorithm with the new content.\n\n")

    print("Options:")
    print("  --help, -h          Show this help message and exit")
    print("  --team              Use team database for setup (requires sudo)")
    print("  --user              Use user database for setup (default)")
    print("\nCommands:")
    print("  doc-directory       Set the documentation directory. mewtwo will search through the documents within that folder. Default path is `/usr/share/mewtwo/Documentation`")
    print("  openai-api          Set the OpenAI API key and organization ID")
    print("  rag                 Updates mewtwo's vector database for searching through documentation. Run after adding/updating documentation.")
    print("  sudo                Update the `sudo` password used by mewtwo. Should be defined at the user level: `mewtwo-setup --user sudo`")
    print("  text-color          Set the text color")
    print("  wipe-memory         Clears the chat history.")


def update_openai_api(conn):
    openai_api_key = getpass.getpass("Please enter your OpenAI API key: ").strip()
    if not openai_api_key:
        print("API key cannot be empty. No changes were made.")
        return
    org_id = input("Please enter your Organization ID (Optional): ").strip()
    if not org_id:
        org_id = None  # Allow empty organization ID

    c = conn.cursor()
    c.execute("UPDATE config SET openai_api_key = ?, org_id = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (openai_api_key, org_id,))
    conn.commit()
    print("OpenAI API credentials updated successfully.")

def choose_text_color(conn):
    n = 3  # Number of colors per row
    max_length = max(len(color_name) for color_name in database.COLOR_OPTIONS) + 2  # Calculate the max length of color names + padding
    print("Please choose a text color:")
    counter = 0
    for color_name in database.COLOR_OPTIONS:
        print(f"{database.COLOR_OPTIONS[color_name]}{color_name.ljust(max_length)}\033[0m", end="")
        counter += 1
        if counter % n == 0:
            print()  # New line
    if counter % n != 0:
        print()  # Ensure the cursor moves to the next line
    color_choice = input("Enter your color choice: ").strip()
    if color_choice not in database.COLOR_OPTIONS:
        print("Invalid choice. No changes were made.")
        return
    c = conn.cursor()
    c.execute("UPDATE config SET text_color = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (color_choice,))
    conn.commit()
    print(f"Text color set to {color_choice}.")

def setup(conn):
    update_openai_api(conn)
    choose_text_color(conn)
    update_sudo_password(conn)
    conn.close()

def doc_path(conn):
    answer = input("Enter the path to the directory containing your server's documentation: ").strip()
    if answer:
        cursor = conn.cursor()
        cursor.execute("UPDATE config SET documentation_path = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)",(answer,))
        conn.commit()
        print(f"Documentation path set to `{answer}`")
        print(f"Run `mewtwo-setup rag` to update the search algorithm")
    else:
        current_path = database.get_documentation_path()
        print(f"Documentation path was not updated: `{current_path}`")


def wipe_memory(conn):
    print("Would you like to wipe mewtwo's memory?")
    answer = input("Yes/No: ").strip()
    if answer.lower() in ['y', 'yes']:
        database.clear_chat_history(conn)
    else:
        print("Mewtwo's memory was not wiped.")

def ensure_sudo():
    """Ensure the script is running with sudo."""
    if os.geteuid() != 0:
        print("Team setup requires elevated privileges. Re-running with sudo...")
        # Use 'sudo -E' to preserve the environment and ensure the correct Python interpreter is used
        os.execvp('sudo', ['sudo', '-E', sys.executable] + sys.argv)
        sys.exit(1)

def update_sudo_password(conn):
    sudo_password = getpass.getpass("Please enter your sudo password (Optional): ").strip()
    if not sudo_password:
        print("Sudo password cannot be empty. No changes were made.")
        return 
    cursor = conn.cursor()
    cursor.execute("UPDATE config SET sudo_password = ? WHERE id = (SELECT id FROM config ORDER BY id DESC LIMIT 1)", (sudo_password,))
    conn.commit()
    print("Sudo password updated successfully.")

def update_rag():
    monitorDocs.update()

if __name__ == "__main__":
    db_type = 'user'  # Default to user
    conn = None       # Initialize conn to None
    command = None    # No command by default

    # Parse arguments
    for arg in sys.argv[1:]:
        if arg in ['--help', '-h']:
            print_help()
            sys.exit(0)
        elif arg == '--team':
            ensure_sudo()  # Ensure the script is running with sudo for --team
            database.initialize_team_db()
            conn = database.db_team()
        elif arg == '--user':
            database.initialize_user_db()
            conn = database.db_user()
        elif arg in ['text-color', 'openai-api', 'wipe-memory', 'rag', 'doc-directory','sudo']:
            command = arg
        else:
            print(f"Unknown option or command: {arg}")
            print_help()
            sys.exit(1)

    # Default to user database if no --team or --user is provided
    if conn is None:
        database.initialize_user_db()
        conn = database.db_user()

    # Execute command or setup
    if command == 'text-color':
        choose_text_color(conn)
        conn.close()
    elif command == 'openai-api':
        update_openai_api(conn)
        conn.close()
    elif command == 'wipe-memory':
        wipe_memory(conn)
        conn.close()
    elif command == 'rag':
        ensure_sudo()
        update_rag()
    elif command == 'doc-directory':
        doc_path(conn)
        conn.close()
    elif command == 'sudo':
        update_sudo_password(conn)
        conn.close()
    else:
        setup(conn)
        print("\nRun `mewtwo-setup rag` to update the documentation search algorithm.")