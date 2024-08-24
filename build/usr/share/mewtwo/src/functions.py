import platform 
import os
import subprocess
from src import database 

def format_response(text):
    color = database.get_text_color()
    if color:
        return f"\n{color}{text}\033[0m\n"
    else:
        return f"\n{text}\n"

def get_system_info():
    # Get the basic operating system information
    if platform.system() == 'Linux':
        freedesktop_os_release = platform.freedesktop_os_release()
        os_info = f'{freedesktop_os_release['NAME']} {freedesktop_os_release['VERSION']}'
    else:
        os_info = f'{platform.system()} {platform.version()} {platform.release()}'

    return os_info

def get_home_path():
    # Determine the home directory path based on the OS
    system = platform.system()

    if system == 'Linux' or system == 'Darwin':  # Darwin is the system name for macOS
        home_path = os.path.expanduser('~')
    elif system == 'Windows':
        user_login = os.getlogin()
        home_path = f'C:\\Users\\{user_login}\\'
    else:
        raise ValueError(f"Unsupported operating system: {system}")

    return home_path

def is_wsl_subprocess():
    import subprocess
    try:
        # Run the uname -r command
        output = subprocess.check_output(['uname', '-r'], text=True).strip()
        
        # Check if "microsoft" or "WSL" is in the output
        if 'microsoft' in output.lower() or 'wsl' in output.lower():
            return True
        return False
    except subprocess.CalledProcessError:
        return False
    
def get_directory_tree(root_dir, padding=""):
    tree_str = padding[:-1] + "+--" + os.path.basename(root_dir) + "\n"
    padding = padding + "   "
    
    for root, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        
        for dir_name in dirs:
            tree_str += get_directory_tree(os.path.join(root, dir_name), padding + "|  ")
        
        for file_name in files:
            tree_str += padding + "+--" + file_name + "\n"
        
        break  # prevent os.walk from descending into subdirectories
    
    return tree_str