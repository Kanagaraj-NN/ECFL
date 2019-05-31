# ========================================================================================
# IMPORTS AND GLOBAL CONFIGURATIONS
# ========================================================================================

import csv
import os
import time
import datetime

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

# FEATURE = 'LineLength' or 'LineRecency' or 'LineCommitSize'  or 'LineChangeCount'
# FEATURE = 'LineChangeCount'

# ========================================================================================
# FUNCTIONS
# ========================================================================================

def find_normalized_metrics(input_file, output_file):
    """Find the normalized line length of suspicious lines

    Parameters
    ----------
    input_file : str (file contains sorted suspicousness lines with line length feature)
    output_file: str (file with normalized values)

    """

    sorted_susp_lines = read_susp_lines_from_file(input_file)

    suspiciousness = []

    for susp_line in sorted_susp_lines:
        suspiciousness.append(float(susp_line[-1].strip()))     # Last column of csv is susp

    # Suspiciousness
    min_suspiciousness, max_suspiciousness = min(suspiciousness), max(suspiciousness)
    diff_suspiciousness = max_suspiciousness - min_suspiciousness

    line_counter = 0

    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"susp_line_id,suspiciousness,normalized_suspiciousness\n")

    for susp_line in sorted_susp_lines:
        normalized_suspiciousness = 0.5
        if diff_suspiciousness:
            # min-max normalization
            normalized_suspiciousness = (suspiciousness[line_counter] - min_suspiciousness) / diff_suspiciousness

        add_normalized_metrics_to_file(output_file, susp_line, normalized_suspiciousness)
        line_counter += 1
        

def add_normalized_metrics_to_file(output_file, susp_line, normalized_suspiciousness):

    """Adds the normalized values to the output file
    
    Paramaeters:
    ------------
    output_file: str 
    susp_line: str
    normalized_suspiciousness: float
    normalized_line_complexity: float

    """

    normalized_suspiciousness = round(normalized_suspiciousness, 4)
    susp_line = [val.strip() for val in susp_line]
    susp_line = ",".join(susp_line)
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line},{normalized_suspiciousness}\n")


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

    return sorted_susp_lines[1:101]  # Skip header # Considering only Top 100


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    start_time = time.time()
    bug_count = 0

    input_directory = f"{WORKING_DIR}/fault-localization.cs.washington.edu/line_suspiciousness_sorted_{FL_TECHNIQUE}"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found")

    output_feature_directory = f"{WORKING_DIR}/ML_output/output_{FL_TECHNIQUE}"
    if not os.path.exists(output_feature_directory):
        os.mkdir(output_feature_directory)
    else:
        raise ValueError(f"Output directory {output_feature_directory} already exists. "
                         f"Plz backup and delete the directory. Then re-run")

    output_directory = f"{WORKING_DIR}/ML_output/output_{FL_TECHNIQUE}/step2_{FL_TECHNIQUE}_normalized"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError(f"Output directory {output_directory} already exists. "
                         f"Plz backup and delete the directory. Then re-run")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            input_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp.csv"
            output_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-normalized.csv"
            find_normalized_metrics(os.path.join(input_directory, input_csv),
                 os.path.join(output_directory, output_csv))
            bug_count += 1

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / bug_count), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: step2_compute_normalized_feature.py")
    print(f"FL TECHNIQUE SELECTED: {FL_TECHNIQUE}")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    print(f"\nBUG IDs SELECTED: {PROJECT_BUGS}")
    print(f"TOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")

    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")

    total_runtime_minutes = round((total_runtime / 60), 2)
    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes")
    print(f"Average Running Time per Bug : {avg_running_time} seconds")

    print("\n############################ END ############################")
