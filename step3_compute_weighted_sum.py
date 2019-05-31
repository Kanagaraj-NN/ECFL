# ========================================================================================
# IMPORTS AND GLOBAL CONFIGURATIONS
# ========================================================================================

import argparse
import csv
import os
import time

PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
# PROJECTS = ['Closure', 'Lang', 'Math', 'Mockito', 'Time']
# PROJECTS = ['Lang']

PROJECT_BUGS = [
    [str(x) for x in range(1, 134)],      # Closure
    [str(x) for x in range(1, 66)],       # Lang
    [str(x) for x in range(1, 27)],       # Chart
    [str(x) for x in range(1, 107)],      # Math
    [str(x) for x in range(1, 39)],       # Mockito
    [str(x) for x in range(1, 28)]        # Time
]

# PROJECT_BUGS = [
#     [str(x) for x in range(1, 134)],      # Closure
#     [str(x) for x in range(1, 66)],       # Lang
#     [str(x) for x in range(1, 107)],      # Math
#     [str(x) for x in range(1, 39)],       # Mockito
#     [str(x) for x in range(1, 28)]        # Time
# ]

# PROJECT_BUGS = [
#      [str(x) for x in range(1, 2)]       # Lang
#      ]


FL_TECHNIQUE = 'dstar2'          # Fault Localization (FL) Technique : DStar
WORKING_DIR = os.path.abspath('')

# WEIGHT PAIR = (susp_weight, feature_weight)
# WEIGHT_PAIRS = [(0.1, 0.9), (0.2, 0.8), (0.3, 0.7), (0.4, 0.6), (0.5, 0.5),
#            (0.6, 0.4), (0.7, 0.3), (0.8, 0.2), (0.9, 0.1)]
WEIGHT_PAIRS = [(0.8, 0.2)]

# FEATURE = 'LineLength' or 'LineRecency' or 'LineCommitSize'  or 'LineChangeCount'
FEATURE = 'LineLength'


# ========================================================================================
# FUNCTIONS
# ========================================================================================


def compute_weighted_suspiciousness(input_file, output_file):
    """Compute weighted suspicioussness for susp lines

    Parameters
    ----------
    input_file : str (file contains normalized suspicious scores and normalized feature scores)
    output_file: str (file contains weighted scores)

    """

    sorted_susp_lines = read_susp_lines_from_file(input_file)

    for susp_weight, feature_weight in WEIGHT_PAIRS:
        compute_different_weights(sorted_susp_lines, susp_weight, feature_weight, output_file)


def compute_different_weights(sorted_susp_lines, susp_weight, feature_weight, output_file):
    """Compute weighted suspicioussness for susp lines

    Parameters
    ----------
    sorted_susp_lines: list
    susp_weight : float
    feature_weight: float
    output_file: str

    """

    output_file_temp = output_file + f"-dstar2-{susp_weight}-{feature_weight}.csv"

    for susp_line in sorted_susp_lines:
        susp = susp_line[-2].strip()
        feature = susp_line[-1].strip()
        weighted_susp = combine_susp_feature_weigthed_addition(susp, feature, susp_weight, feature_weight)
        add_weighted_susp_to_file(output_file_temp, susp_line, weighted_susp)

    # Sorting
    reader = csv.reader(open(output_file_temp), delimiter=',')
    sorted_list = sorted(reader, key=lambda row: row[-1], reverse=True)

    output_file += f'-addition-{susp_weight}-{feature_weight}.csv'

    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"susp_line_id,suspiciousness,{FEATURE},normalized_suspiciousness,normalized_{FEATURE}\n")

    for sorted_line in sorted_list:
        write_sorted_list_to_file(output_file, sorted_line)


def combine_susp_feature_weigthed_addition(susp, feature, susp_weight, feature_weight):
    return susp_weight * float(susp) + feature_weight * float(feature)


def write_sorted_list_to_file(output_file, susp_line_full):
    susp_line_full = ",".join(susp_line_full)
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line_full}\n")


def add_weighted_susp_to_file(output_file, susp_line, weighted_susp):
    """Appends the author and date to the output file containing suspiciousness lines
    
    Paramaeters:
    ------------
    output_file: str 
    susp_line: str
    recency: str

    """
    susp_line = ",".join(susp_line)
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line},{weighted_susp}\n")


def read_susp_lines_from_file(input_file):
    """Reads the suspiciousness lines data from the sorted suspiciousness file

    Parameters:
    ----------
    input_file: str

    Return:
    ------
    sorted_susp_lines: list (2D)

    """
    susp_data = csv.reader(open(input_file), delimiter=',')
    sorted_susp_lines = [susp_line for susp_line in susp_data]
    
    return sorted_susp_lines[1:]    # Skipping the header


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    """Main function.

    Command to run:
    --------------
    # python3.6 step3_compute_weighted_sum.py 

    """

    start_time = time.time()
    bug_count = 0

    input_directory = f"{WORKING_DIR}/output_{FEATURE}/step2_{FEATURE}_normalized"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found. "
                         "Plz run the previous step with correct feature configured. "
                         "Then re-run this step")

    output_directory = f"{WORKING_DIR}/output_{FEATURE}/step3_{FEATURE}_weighted"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError(f"Output directory {output_directory} already exists. "
                         f"Plz backup and delete the directory. Then re-run")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            input_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-normalized.csv"
            output_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-weighted"
            compute_weighted_suspiciousness(os.path.join(input_directory, input_csv),
                                            os.path.join(output_directory, output_csv))
            bug_count += 1

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / bug_count), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: step3_compute_weighted_sum.py")
    print(f"FEATURE SELECTED: {FEATURE}")
    print(f"WEIGHT PAIRS SELECTED: [(DStar_weight, Feature_weight)]: {WEIGHT_PAIRS}")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    print(f"BUG IDs SELECTED: {PROJECT_BUGS}")
    print(f"\nTOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")

    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")

    total_runtime_minutes = round((total_runtime / 60), 2)
    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes")
    print(f"Average Running Time per Bug : {avg_running_time} seconds")

    print("\n############################ END ############################")