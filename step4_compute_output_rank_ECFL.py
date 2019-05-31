# ========================================================================================
# IMPORTS AND GLOBAL CONFIGURATIONS
# ========================================================================================

import argparse
import csv
import os
from scipy.stats import rankdata
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

def find_avg_rank(input_file_dstar, input_file_wt_addition, output_file_dstar, output_file_wt_addition):
    """Compute average rank of the susp lines

    Parameters:
    ----------
    input_file_dstar:   str
    input_file_wt_addition: str
    output_file_dstar: str (contains the average rank for each susp line)
    output_file_wt_addition: str (contains the average rank for each weighted susp line)
    """

    sorted_susp_lines_dstar = read_susp_lines_from_file(input_file_dstar)
    sorted_susp_lines_addition = read_susp_lines_from_file_new_technique(input_file_wt_addition)

    compute_avg_rank(sorted_susp_lines_dstar, 3)     # Dstar normalized susp
    compute_avg_rank(sorted_susp_lines_addition, -1)  # New tech susp value is the last index

    write_sorted_list_to_file(output_file_dstar, sorted_susp_lines_dstar)
    write_sorted_list_to_file(output_file_wt_addition, sorted_susp_lines_addition)


def compute_avg_rank(sorted_susp_lines, tech_indx):
    """Compute average rank of the susp lines

    Parameters:
    ----------
    sorted_susp_lines:   list
    tech_indx: int (which column in the csv file to consider for ranking
    """

    scores_list = []
    for line in sorted_susp_lines:
        scores_list.append((float(line[tech_indx])))

    random_rank = [i+1 for i in range(len(scores_list))]   # rank starts at 1 but index starts at 0
    avg_rank = rankdata([-1 * i for i in scores_list], method='average').astype(float).tolist()
    min_rank = rankdata([-1 * i for i in scores_list], method='min').astype(float).tolist()

    avg_rank = convert_list_to_ints(avg_rank)
    min_rank = convert_list_to_ints(min_rank)

    for k in range(len(scores_list)):
        sorted_susp_lines[k].append(str(random_rank[k]))
        sorted_susp_lines[k].append(str(avg_rank[k]))
        sorted_susp_lines[k].append(str(min_rank[k]))


def convert_list_to_ints(list_input):
    return [int(val) for val in list_input]


def write_sorted_list_to_file(output_file, sorted_susp_lines):
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"susp_line_id,suspiciousness,{FEATURE},normalized_suspiciousness,normalized_{FEATURE},"
                     "new_score,random_rank,avg_rank,min_rank\n")

        for sorted_line in sorted_susp_lines:
            susp_line_full = ",".join(sorted_line)
            myFile.write(f"{susp_line_full}\n")


def read_susp_lines_from_file_new_technique(input_file):
    """Reads the suspiciousness lines data from the given file

    Parameters:
    ----------
    input_file: str

    Return:
    ------
    sorted_susp_lines: list (2D)

    """
    susp_data = csv.reader(open(input_file, encoding="latin-1"), delimiter=',')
    sorted_susp_lines = [susp_line for susp_line in susp_data]
    
    return sorted_susp_lines[1:]   # Skipping the header


def read_susp_lines_from_file(input_file):
    """
    reads the suspiciousness lines data from the sorted suspiciousness file

    Parameters:
    ----------
    input_file: str

    return:
    ------
    sorted_susp_lines: list (2D)

    """
    susp_data = csv.reader(open(input_file, encoding="latin-1"), delimiter=',')
    sorted_susp_lines = [susp_line for susp_line in susp_data]

    return sorted_susp_lines    # Don't skip the header as no header in the DStar file


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    """Main function.

    Command to run:
    --------------
    # python3.6 step4_compute_output_rank_ECFL.py

    """

    start_time = time.time()
    bug_count = 0

    input_directory = f"{WORKING_DIR}/output_{FEATURE}/step3_{FEATURE}_weighted"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found. "
                         "Plz run the previous step with correct feature configured. "
                         "Then re-run this step")

    output_directory = f"{WORKING_DIR}/output_{FEATURE}/step4_{FEATURE}_ranked"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError(f"Output directory {output_directory} already exists. "
                         "Plz backup and delete the directory. Then re-run")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for susp_weight, feature_weight in WEIGHT_PAIRS:
            for bug in bugs:
                input_csv_dstar = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-weighted-{FL_TECHNIQUE}-{susp_weight}-{feature_weight}.csv"
                input_csv_wt_addition = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-weighted-addition-{susp_weight}-{feature_weight}.csv"
                output_csv_dstar = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-{FL_TECHNIQUE}-{susp_weight}-{feature_weight}-ranked.csv"
                output_csv_wt_addition = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-addition-{susp_weight}-{feature_weight}-ranked.csv"

                find_avg_rank(os.path.join(input_directory, input_csv_dstar),
                              os.path.join(input_directory, input_csv_wt_addition),
                              os.path.join(output_directory, output_csv_dstar),
                              os.path.join(output_directory, output_csv_wt_addition))
                bug_count += 1

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / bug_count), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: step4_compute_output_rank_ECFL.py")
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
