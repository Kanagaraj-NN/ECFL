# ========================================================================================
# IMPORTS AND GLOBAL CONFIGURATIONS
# ========================================================================================

import argparse
import csv
import os
from scipy.stats import rankdata
import time

# PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Time']

# PROJECT_BUGS = [
#     [str(x) for x in range(1, 134)],
#     [str(x) for x in range(1, 66)],
#     [str(x) for x in range(1, 27)],
#     [str(x) for x in range(1, 107)],
#     [str(x) for x in range(1, 39)],
#     [str(x) for x in range(1, 28)]
# ]

PROJECT_BUGS = [
    [str(x) for x in range(1, 134)],
    [str(x) for x in range(1, 66)],
    [str(x) for x in range(1, 27)],
    [str(x) for x in range(1, 107)],
    [str(x) for x in range(1, 28)]
]

# 'ML_MBFL', ML_predicate', 'ML_slicing', 'ML_stacktrace'
# 'ML_combineFastestFL_run_2', 'ML_combineFL_nearest_LineLength', 'ML_combineFL_nearest_LineRecency', 'ML_combineFL_nearest_LineCommitSize', 'ML_combineFL_nearest_all_3'
FL_TECHNIQUE = 'ML_combineFL_all_3_features' # 'ML_combineFastestFL_all_3', 'ML_combineFastestFL_LineCommitSize', 'ML_combineFastestFL_LineRecency', ML_combineFastestFL_LineLength', dstar2_all_3', dstar2_LineCommitSize', 'dstar2_LineRecency', 'dstar2_LineLength', 'combineFastestFL', 'combineFL_nearest'
WORKING_DIR = os.path.abspath('')



# ========================================================================================
# FUNCTIONS
# ========================================================================================

def find_avg_rank(input_file_susp, output_file_susp):
    """Compute average rank of the susp lines

    Parameters:
    ----------
    input_file_susp:   str
    output_file_susp: str (contains the average rank for each susp line)
    """

    sorted_susp_lines = read_susp_lines_from_file_new_technique(input_file_susp)
    compute_avg_rank(sorted_susp_lines, -1)     # normalized susp
    write_sorted_list_to_file(output_file_susp, sorted_susp_lines)


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
        myFile.write(f"susp_line_id,suspiciousness,normalized_suspiciousness,random_rank,avg_rank,min_rank\n")

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


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':


    start_time = time.time()
    bug_count = 0

    input_directory = f"{WORKING_DIR}/ML_output/output_{FL_TECHNIQUE}/step2_{FL_TECHNIQUE}_normalized"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found. "
                         "Plz run the previous step with correct feature configured. "
                         "Then re-run this step")

    output_directory = f"{WORKING_DIR}/ML_output/output_{FL_TECHNIQUE}/step4_{FL_TECHNIQUE}_ranked"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError(f"Output directory {output_directory} already exists. "
                         "Plz backup and delete the directory. Then re-run")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            # Chart-1-dstar2_LineLength-sorted-susp-normalized.csv
            input_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-normalized.csv"
            output_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-ranked.csv"

            find_avg_rank(os.path.join(input_directory, input_csv),
                          os.path.join(output_directory, output_csv))
            bug_count += 1

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / bug_count), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: step4_compute_output_rank_ECFL.py")
    print(f"FL TECHNIQUE SELECTED: {FL_TECHNIQUE}")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    # print(f"BUG IDs SELECTED: {PROJECT_BUGS}")
    print(f"\nTOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")

    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")

    total_runtime_minutes = round((total_runtime / 60), 2)
    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes")
    print(f"Average Running Time per Bug : {avg_running_time} seconds")

    print("\n############################ END ############################")
