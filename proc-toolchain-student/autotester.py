"""
Main autograder script. Calls helper scripts to compile and test assembly files and processors.

@author: Vincent Chen
"""

import sys
import os
import yaml

from helper_scripts.logger import Logger
import helper_scripts.default_values as dv
import helper_scripts.go_asm_compiler as asm
import helper_scripts.proc_compiler as proc
import helper_scripts.results_export as rexp
from helper_scripts.html_generator import HTMLGenerator

def read_config(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
            return config_data
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) > 2:
        print("Usage: python autotester.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1] if len(sys.argv) == 2 else dv.DEFAULT_CONFIG_FILE

    config_data = read_config(config_file)

    # Logging setup
    try:
        Logger.setup(log_level=config_data["LOG_LEVEL"], output_destination=config_data["LOG_LOC"], 
            rolling=config_data["LOG_ROLL"], folder_path=config_data["LOG_DIR"])
    except KeyError as e:
        print(f"Missing logging-related key in config file: {e}")
        sys.exit(1)

    Logger.info("Logger setup complete.")

    # Assemble all files
    # FIXME: Extremely messy
    tests_folder = "gtkwave_lab_test_files" if config_data["MODE"] == "LAB9" else "test_files"
    active_files = (asm.get_active_list(
        asm_dir= os.path.join(tests_folder, "assembly_files"), 
        appendix=config_data["ACTIVE_FILE"]) 
        if config_data["FILT_ASM"] else [
            f for f in os.listdir(os.path.join(tests_folder, "assembly_files")) if f.endswith('.s')
        ]
    )
    active_files = [f[:-2] if f.endswith('.s') else f for f in active_files]

    if asm.should_assemble(config_data, active_files, tests_folder):            
        try:
            asm.assemble_all(
                asm_dir= os.path.join(tests_folder, "assembly_files"), 
                mem_dir= os.path.join(tests_folder, "mem_files"), 
                filter_files=config_data["FILT_ASM"], mode=config_data["MODE"], 
                act_appendix=config_data["ACTIVE_FILE"]
            )
        except KeyError as e:
            asm.assemble_all()
            Logger.warn(f"Missing assembler-related key in config file. Defaulting filter_files to False: {e}")

    Logger.info("Assembly file compilation complete.")

    tests = get_tests(os.path.join(tests_folder, "mem_files"), active_files)
    # Compile all processors
    try:
        proc_results = proc.compile_all_procs(procs_folder=config_data["PROCS"], tests=tests, en_mt=config_data["EN_MT"], wrapper_path=dv.L9_WRAPPER_PATH if config_data["MODE"] == "LAB9" else dv.WRAPPER_PATH, test_folder=tests_folder, config_data=config_data)
    except KeyError as e:
        proc_results = proc.compile_all_procs()
        Logger.warn(f"Unable to find one or more keys for processor compilation. Using all default values: {e}")

    Logger.info("Processor compilation complete.")

    # Export results
    if config_data["EN_CSV"]:
        try:
            rexp.export_results(proc_results, tests, rolling = config_data["OUT_ROLL"])
        except KeyError as e:
            rexp.export_results(proc_results, tests)
            Logger.warn(f"Missing OUT_ROLL key in config file. Defaulting to False.")
        
        Logger.info("Results exported.")
    
    if config_data["AUTO_OPEN"]:
        HTMLGenerator.open_report() 
        Logger.info("HTML report opened.")

    Logger.close()

def get_tests(tests_folder, active_files=[]):
    if not os.path.exists(tests_folder):
        Logger.error(f"Memory files directory '{tests_folder}' does not exist.")
        sys.exit(1)    

    tests = []
    for test_file in active_files:
        if os.path.isfile(os.path.join(tests_folder, f"{test_file}.mem")):
            tests.append(test_file)
        else:
            Logger.warn(f"Memory file '{test_file}.mem' not found.")
            HTMLGenerator.add_content(test_file, f"Memory file '{test_file}.mem' not found.", keep=True)
            HTMLGenerator.set_state(test_file, -1)
    return tests

if __name__ == "__main__":
    main()
