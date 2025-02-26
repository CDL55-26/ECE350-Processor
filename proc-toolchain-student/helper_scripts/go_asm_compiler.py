"""
Calls the Go assembler to compile assembly files. If LAB9 is selected, it will instead call gtkwave_lab_asm.py.

@author: Vincent Chen
"""

import subprocess
from helper_scripts.logger import Logger
import sys
import os
import shutil
import yaml
import hashlib  
from helper_scripts.gtkwave_lab_asm import assemble_lab9
from helper_scripts.html_generator import HTMLGenerator

def assemble_all(asm_dir=os.path.join('test_files', 'assembly_files'), mem_dir=os.path.join('test_files', 'mem_files'), filter_files=False, mode="MIPS", act_appendix=''):
    if not os.path.exists(asm_dir):
        Logger.error(f"Could not find directory '{asm_dir}' for assembly files.")
        sys.exit(1)

    if not os.path.isdir(asm_dir):
        Logger.error(f"'{asm_dir}' is not a directory.")
        sys.exit(1)

    # Create mem dir if it does not exist
    if not os.path.exists(mem_dir):
        os.makedirs(mem_dir)
        Logger.warn(f"'{mem_dir}' did not exist. Directory created.")

    # Clear previous files in mem dir
    for filename in os.listdir(mem_dir):
        file_path = os.path.join(mem_dir, filename)
        try:
            if os.path.isfile(file_path) and file_path.endswith('.mem'):
                os.remove(file_path)
        except OSError as e:
            Logger.warn(f"Error deleting mem file '{file_path}'. Error: {e}")
    
    if filter_files:
        active_files = get_active_list(asm_dir=asm_dir, appendix=act_appendix)
    else:
        active_files = [f for f in os.listdir(asm_dir) if f.endswith('.s')]

    for filename in active_files:
        path = os.path.join(asm_dir, f"{filename}")
        if not os.path.isfile(path):
            Logger.warn(f"Could not find assembly file '{path}'.")
            HTMLGenerator.add_content(filename, f"Could not find assembly file '{path}'.", keep=True)
            HTMLGenerator.set_state(filename, -1)
            continue

        if mode == 'LAB9':
            assemble_lab9(file_path=path, canonical_name=os.path.splitext(filename)[0], asm_dir=asm_dir, mem_dir=mem_dir)
        else:
            assemble(file_path=path, canonical_name=os.path.splitext(filename)[0], asm_dir=asm_dir, mem_dir=mem_dir)

def get_active_list(asm_dir=os.path.join('test_files', 'assembly_files'), appendix=''):
    file = os.path.join(asm_dir, f"active_{appendix}.txt")
    if not os.path.exists(file):
        Logger.warn(f"Could not find active assembly file list '{file}'.")
        return []

    lines = []
    with open(file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    trimmed_lines = [line.strip() + ".s" for line in lines]

    if len(trimmed_lines) == 0:
        Logger.warn(f"No active assembly files found in '{file}'.")

    return trimmed_lines

def assemble(file_path, canonical_name, asm_dir, mem_dir):
    # Add assembly contents to HTML generator
    with open(file_path, 'r', encoding='utf-8') as f:
        asm_contents = f.read()

    # Check if Go is installed
    try:
        subprocess.run(['go', 'version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        Logger.error("Go is not installed or not in PATH. Please install Go (https://golang.org/dl/) to use this script.")
        sys.exit(1)

    # Command to run the Go program
    try:
        # Change to the assembler directory
        original_dir = os.getcwd()
        os.chdir('assembler-program')

        # Adjust file path to be relative to new working directory
        relative_file_path = os.path.join('..', file_path)
        command = ['go', 'run', '.', relative_file_path]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Change back to original directory
        os.chdir(original_dir)

        # Move mem file to correct location
        mem_file_path = os.path.join(asm_dir, canonical_name + ".mem")
        moved_to = os.path.join(mem_dir, canonical_name + ".mem")
        shutil.move(mem_file_path, moved_to)

        HTMLGenerator.add_content(canonical_name, asm_contents, keep=True)
        Logger.info(f"Assembly successful for {file_path}. Output written to {moved_to}.")
    except subprocess.CalledProcessError as e:
        HTMLGenerator.add_content(canonical_name, "Assembly file failed to compile.", keep=True)
        Logger.warn(f"Go assembler failed to execute for {file_path}. Error: {e.stderr}")
    except IOError as e:
        HTMLGenerator.add_content(canonical_name, "Mem file failed to write.", keep=True)
        Logger.warn(f"Error writing to memory file for {file_path}. Error: {e}")
    finally:
        # Ensure we return to the original directory
        if 'original_dir' in locals():
            os.chdir(original_dir)

def should_assemble(config_data = None, active_files = [], tests_folder="test_files"):
    state_path = os.path.join(tests_folder, "mem_files", "state.yaml")

    # Delete state file if always or never assemble
    if config_data["ASM_COMP"] == "ALWAYS" or config_data["ASM_COMP"] == "NEVER":
        if os.path.exists(state_path):
            try:
                os.remove(state_path)
                Logger.info(f"Deleted state file '{state_path}' because ASM_COMP is {config_data['ASM_COMP']}.")
            except OSError as e:
                Logger.warn(f"Failed to delete state file '{state_path}': {e}")

        return config_data["ASM_COMP"] == "ALWAYS"
    
    # Assume we are now in auto state
    # Hash contents of active assembly files
    hash_obj = hashlib.sha256()
    all_contents = b''
    
    # Read and hash all active files in sorted order
    for filename in sorted(active_files):
        filepath = os.path.join(tests_folder, "assembly_files", f"{filename}.s")
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                all_contents += f.read()
    
    hash_obj.update(all_contents)
    current_hash = hash_obj.hexdigest()

    if not os.path.exists(state_path):
        Logger.warn(f"Could not find state file '{state_path}'. Defaulting to always assemble.")
        write_state_file(state_path, config_data, current_hash)
        return True

    try:
        with open(state_path, 'r') as f:
            state_data = yaml.safe_load(f)
            
        # Return True if active file changed or hash doesn't match
        outdated = state_data.get('HASH') != current_hash
        Logger.info(f"Mem files are {'' if outdated else 'not '}outdated.")
        write_state_file(state_path, config_data, current_hash)

        return outdated
    
    except (yaml.YAMLError, IOError) as e:
        Logger.warn(f"Could not parse state file '{state_path}'. Defaulting to always assemble : {e}")
        write_state_file(state_path, config_data, current_hash)
        return True

def write_state_file(state_path, config_data, current_hash):
    with open(state_path, 'w') as f:
        yaml.dump({'ACTIVE_FILE': config_data["ACTIVE_FILE"], 'HASH': current_hash}, f) 

if __name__ == "__main__":
    Logger.setup(log_level="INFO", output_destination="TERM")
    assemble_all()
