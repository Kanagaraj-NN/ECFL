# ========================================================================================
# IMPORTS AND GLOBAL CONFIGURATIONS
# ========================================================================================

import csv
import os
import time
import datetime

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

# FEATURE = 'LineLength' or 'LineRecency' or 'LineCommitSize'  or 'LineChangeCount'
FEATURE = 'LineLength'

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

    line_feature = []
    suspiciousness = []
    dates = []

    for susp_line in sorted_susp_lines:
        if FEATURE == 'LineRecency':
            date = susp_line[-1].strip()
            datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            bug_date = datetime_obj.date()
            dates.append(bug_date)
        else:
            line_feature.append(int(susp_line[-1].strip()))

        suspiciousness.append(float(susp_line[-2].strip()))

    if FEATURE == 'LineRecency':
        # Date
        no_of_days_elapsed = []
        for date in dates:
            no_of_days_elapsed.append((max(dates) - date).days)
        min_days = min(no_of_days_elapsed)
        max_days = max(no_of_days_elapsed)
        diff_days = max_days - min_days
    else:
        # Other line features
        min_line_feature, max_line_feature = min(line_feature), max(line_feature)
        diff_line_feature = max_line_feature - min_line_feature

    # Suspiciousness
    min_suspiciousness, max_suspiciousness = min(suspiciousness), max(suspiciousness)
    diff_suspiciousness = max_suspiciousness - min_suspiciousness

    line_counter = 0

    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"susp_line_id,suspiciousness,{FEATURE},normalized_suspiciousness,normalized_{FEATURE}\n")

    for susp_line in sorted_susp_lines:
        normalized_line_feature = 0.5
        if FEATURE == 'LineRecency':
            if diff_days:
                # min-max normalization
                normalized_time = (no_of_days_elapsed[line_counter] - min_days) / diff_days
                normalized_line_feature = 1 - normalized_time
        else:
            if diff_line_feature:
                # min-max normalization
                normalized_line_feature = (line_feature[line_counter] - min_line_feature) / diff_line_feature

        normalized_suspiciousness = 0.5
        if diff_suspiciousness:
            # min-max normalization
            normalized_suspiciousness = (suspiciousness[line_counter] - min_suspiciousness) / diff_suspiciousness

        add_normalized_metrics_to_file(output_file, susp_line, normalized_suspiciousness, normalized_line_feature)
        line_counter += 1
        

def add_normalized_metrics_to_file(output_file, susp_line, normalized_suspiciousness, normalized_line_feature):

    """Adds the normalized values to the output file
    
    Paramaeters:
    ------------
    output_file: str 
    susp_line: str
    normalized_suspiciousness: float
    normalized_line_complexity: float

    """

    normalized_suspiciousness = round(normalized_suspiciousness, 4)
    normalized_line_feature = round(normalized_line_feature, 4)

    susp_line = [val.strip() for val in susp_line]
    susp_line = ",".join(susp_line)
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line},{normalized_suspiciousness},{normalized_line_feature}\n")


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

    return sorted_susp_lines[1:]  # Skip header # Top 100


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    """Main function.

    Command to run:
    --------------
    # python3.6 step2_compute_normalized_feature.py

    """

    start_time = time.time()
    bug_count = 0

    input_directory = f"{WORKING_DIR}/output_{FEATURE}/step1_{FEATURE}_feature"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found. "
                         "Plz run the previous step with correct feature configured. "
                         "Then re-run this step")

    output_directory = f"{WORKING_DIR}/output_{FEATURE}/step2_{FEATURE}_normalized"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError(f"Output directory {output_directory} already exists. "
                         f"Plz backup and delete the directory. Then re-run")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            input_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}.csv"
            output_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-normalized.csv"
            find_normalized_metrics(os.path.join(input_directory, input_csv),
                 os.path.join(output_directory, output_csv))
            bug_count += 1

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / bug_count), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: step2_compute_normalized_feature.py")
    print(f"FEATURE SELECTED: {FEATURE}")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    print(f"\nBUG IDs SELECTED: {PROJECT_BUGS}")
    print(f"TOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")

    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")

    total_runtime_minutes = round((total_runtime / 60), 2)
    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes")
    print(f"Average Running Time per Bug : {avg_running_time} seconds")

    print("\n############################ END ############################")
