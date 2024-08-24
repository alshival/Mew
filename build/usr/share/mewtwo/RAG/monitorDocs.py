import os
import time
import pandas as pd
from pathlib import Path
import pickle 
from RAG import rag
from src import database
import sys 

def update():
    state_path = '/usr/share/mewtwo/RAG/monitor.pkl'
    monitor_path = '/usr/share/mewtwo/Documentation/'

    try:
        config =database.get_config()
    except:
        sys.exit(1)

    # Load previous state if it exists
    if os.path.exists(state_path):
        with open(state_path, 'rb') as f:
            previous_state = pickle.load(f)
        print("Previous state loaded successfully.")
    else:
        print("No previous state found. Initializing new state.")
        previous_state = None

    def format_timestamp(timestamp):
        """Convert a timestamp to a human-readable format."""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

    def build_tree(directory):
        records = []
        
        for entry in os.scandir(directory):
            record = {
                "filepath": str(Path(entry.path).resolve()),
                "filename": entry.name,
                "directory": str(Path(directory).resolve()),
                "created": format_timestamp(entry.stat().st_ctime),
                "modified": format_timestamp(entry.stat().st_mtime)
            }
            records.append(record)
            
            if entry.is_dir(follow_symlinks=False):
                records.extend(build_tree(entry.path))
        
        return records

    def create_directory_tree_dataframe(path):
        tree_data = build_tree(path)
        df = pd.DataFrame(tree_data, columns=["filepath", "filename", "directory", "created", "modified"])
        return df

    # Build the current directory tree DataFrame
    current_state = create_directory_tree_dataframe(monitor_path)

    def find_changed_files(current_state, previous_state):
        merged_df = current_state.merge(previous_state, on="filepath", suffixes=('_current', '_previous'), how="outer", indicator=True)
        
        # Files that are either new or modified
        modified_or_new_files = merged_df[(merged_df['_merge'] != 'both') |
                                        (merged_df['modified_current'] != merged_df['modified_previous'])]['filepath']
        
        # Files that have been deleted
        deleted_files = merged_df[merged_df['_merge'] == 'right_only']['filepath']
        
        return modified_or_new_files.tolist(), deleted_files.tolist()

    # Compare with the previous state (if it exists)
    if previous_state is not None:
        modified_or_new_files, deleted_files = find_changed_files(current_state, previous_state)
        
        if modified_or_new_files or deleted_files:
            print("Directory structure has changed.")
            
            # Handle modified or new files
            for filepath in modified_or_new_files:
                if os.path.exists(filepath):
                    print(f"Updating document: {filepath}")
                    rag.update_document(filepath)
                else:
                    print(f"File not found, skipping update: {filepath}")
            
            # Handle deleted files
            for filepath in deleted_files:
                print(f"Deleting document: {filepath}")
                rag.delete_document(filepath)
            
            # Update the saved state
            with open(state_path, 'wb') as f:
                pickle.dump(current_state, f)
            print("State updated successfully.")
        else:
            print("No changes detected in the directory structure.")
    else:
        # If there's no previous state, add all files and save the current one
        print("Adding all documents as this is the initial state.")
        for filepath in current_state['filepath']:
            if os.path.exists(filepath):
                print(f"Adding document: {filepath}")
                rag.add_document(filepath)
            else:
                print(f"File not found, skipping add: {filepath}")
        
        # Save the initial state
        with open(state_path, 'wb') as f:
            pickle.dump(current_state, f)
        print("Initial state saved successfully.")
