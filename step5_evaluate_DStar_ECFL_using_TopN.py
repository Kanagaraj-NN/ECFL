# ========================================================================================
# IMPORTS AND GLOBAL CONFIGURATIONS
# ========================================================================================

import argparse
import csv
import os

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

# top_N_lines = 1, 3, 5, 10
TOP_N = 1

# FEATURE = 'LineLength' or 'LineRecency' or 'LineCommitSize' or 'LineChangeCount'
FEATURE = 'LineLength'


# ========================================================================================
# FUNCTIONS
# ========================================================================================

def evaluate_Top_N(input_file_DStar, input_file_ECFL, buggy_lines_file, buggy_lines_cand_file, top_N_lines):
    """Evaluate DStar and ECFl against ground truth using Top-N evaluation metric

    Parameters:
    ----------
    input_file_dstar : str
    input_file_ECFL: str
    buggy_lines_file: str (ground truth containing buggy lines for each bug)
    buggy_lines_cand_file: str (ground truth containing candidate buggy lines for each bug)
    top_N_lines: int (Top-N evaluation metric)

    Return:
    ------
    is_buggy_line_in_topN_DStar: tuple of 3 elements for DStar (is_bug_located, position_in_list, rank)
    is_buggy_line_in_topN_ECFL: tuple of 3 elements for ECFL (is_bug_located, position_in_list, rank)
    """

    sorted_susp_lines_DStar = read_susp_lines_from_file(input_file_DStar)
    sorted_susp_lines_ECFL = read_susp_lines_from_file_new_technique(input_file_ECFL)
    buggy_lines = read_buggy_lines(buggy_lines_file)

    # To remove extra information (source code line) from the buggy line
    for i, buggy_line_i in enumerate(buggy_lines):
        buggy_line_parts_i = buggy_line_i[0].split('#')
        buggy_line_id_i = buggy_line_parts_i[0] + "#" + buggy_line_parts_i[1]
        buggy_lines[i][0] = buggy_line_id_i

    buggy_lines_cand = read_candidate_buggy_lines(buggy_lines_cand_file)

    consider_candidate_buggy_lines = True
    if buggy_lines_cand and consider_candidate_buggy_lines:
        for buggy_lines_c in buggy_lines_cand:
            buggy_lines.append(buggy_lines_c)

    # Remove duplicates
    buggy_lines_list = set()
    for buggy_line in buggy_lines:
        buggy_lines_list.add(buggy_line[0])

    # Dstar evaluation
    is_buggy_line_in_topN_DStar = search_faulty_line_in_topN_avg_rank(sorted_susp_lines_DStar, buggy_lines_list, top_N_lines)
    # ECFL evaluation
    is_buggy_line_in_topN_ECFL = search_faulty_line_in_topN_avg_rank(sorted_susp_lines_ECFL, buggy_lines_list, top_N_lines)

    return is_buggy_line_in_topN_DStar, is_buggy_line_in_topN_ECFL


def search_faulty_line_in_topN_avg_rank(sorted_susp_lines, buggy_lines_list, top_N_lines):
    """Evaluate DStar and ECFl against ground truth using Top-N evaluation metric

    Parameters:
    ----------
    sorted_susp_lines : list
    buggy_lines_list: list (ground truth)
    top_N_lines: int (Top-N evaluation metric)

    Return:
    ------
    is_buggy_line_in_topN: tuple of 3 elements (is_bug_located, position_in_list, rank)
    """

    is_buggy_line_in_topN = (False, -1, -1)

    for p, sorted_susp_line in enumerate(sorted_susp_lines):
        rank = int(sorted_susp_line[-2])  # Avg rank
        if rank <= top_N_lines:
            if sorted_susp_line[0] in buggy_lines_list:
                is_buggy_line_in_topN = (True, p, rank)
                break
        else:
            break

    return is_buggy_line_in_topN


def read_susp_lines_from_file_new_technique(input_file):
    """Reads the suspiciousness lines data from the file

    Parameters:
    ----------
    input_file: str

    return:
    ------
    sorted_susp_lines: list (2D)

    """
    susp_data = csv.reader(open(input_file, encoding="latin-1"), delimiter=',')
    sorted_susp_lines = [susp_line for susp_line in susp_data]
    
    return sorted_susp_lines[1:]   # Skipping the header


def read_susp_lines_from_file(input_file):
    """Reads the suspiciousness lines data from the file

    Parameters:
    ----------
    input_file: str

    return:
    ------
    sorted_susp_lines: list (2D)

    """
    susp_data = csv.reader(open(input_file, encoding="latin-1"), delimiter=',')
    sorted_susp_lines = [susp_line for susp_line in susp_data]

    return sorted_susp_lines[1:]    # Added header in previous step, so skip it here


def read_buggy_lines(input_file):
    """Reads the buggy lines data from the file

    Parameters:
    ----------
    input_file: str

    return:
    ------
    buggy_lines: list (2D)

    """
    buggy_data = csv.reader(open(input_file, encoding="latin-1"), delimiter=',')
    buggy_lines = [buggy_line for buggy_line in buggy_data]

    return buggy_lines


def read_candidate_buggy_lines(input_file):
    """Reads the candidate buggy lines data from the file

    Parameters:
    ----------
    input_file: str

    return:
    ------
    sorted_susp_lines: list (2D)

    """
    try:
        buggy_data = csv.reader(open(input_file, encoding="latin-1"), delimiter=',')
    except FileNotFoundError:
        cand_buggy_lines = []
    else:
        cand_buggy_lines_unformated = [cand_buggy_line for cand_buggy_line in buggy_data]

        cand_buggy_lines = []
        for lines in cand_buggy_lines_unformated:
            for line in lines:
                cand_buggy_lines.append([line])

    return cand_buggy_lines


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    """Main function.

    Command to run:
    --------------
    # python3.6 step5_evaluate_DStar_ECFL_using_TopN.py

    """

    bug_found_position_DStar = []
    bug_found_position_ECFL = []

    total_bugs_found_DStar = 0
    total_bugs_found_ECFL = 0

    input_directory = f"{WORKING_DIR}/output_{FEATURE}/step4_{FEATURE}_ranked"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found. "
                         "Plz run the previous step with correct feature configured. "
                         "Then re-run this step")

    output_directory = f"{WORKING_DIR}/output_{FEATURE}/step5_{FEATURE}_results"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    for susp_weight, feature_weight in WEIGHT_PAIRS:
        output_result_file = output_directory + f"/output-Top-{TOP_N}-{FEATURE}-{susp_weight}-{feature_weight}-results.txt"
        if os.path.exists(output_result_file):
            raise ValueError(f"Output result file {output_result_file} already exists. "
                             f"Plz backup and delete the file. Then re-run")

    # fault-localization-data has to be present in the working directory
    buggy_lines_directory = f"{WORKING_DIR}/fault-localization-data/analysis/pipeline-scripts/buggy-lines"
    if not os.path.exists(buggy_lines_directory):
        raise ValueError(f"buggy_lines directory {buggy_lines_directory} is not found in the working directory ")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for susp_weight, feature_weight in WEIGHT_PAIRS:
            print(f"======= susp weight: {susp_weight}, feature_weight: {feature_weight}======")

            buggy_line_in_topN_DStar_counter = 0
            buggy_line_in_topN_ECFL_counter = 0
            for bug in bugs:
                input_csv_dstar = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-{FL_TECHNIQUE}-{susp_weight}-{feature_weight}-ranked.csv"
                input_csv_wt_addition = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-addition-{susp_weight}-{feature_weight}-ranked.csv"

                buggy_lines_csv = f"{project}-{bug}.buggy.lines"
                buggy_lines_cand_csv = f"{project}-{bug}.candidates"

                # Calling the main functionality
                is_buggy_line_in_topN_DStar, is_buggy_line_in_topN_ECFL = evaluate_Top_N(os.path.join(input_directory, input_csv_dstar),
                                                                                         os.path.join(input_directory, input_csv_wt_addition),
                                                                                         os.path.join(buggy_lines_directory, buggy_lines_csv),
                                                                                         os.path.join(buggy_lines_directory, buggy_lines_cand_csv),
                                                                                         TOP_N)

                bug_found_position_DStar.append(is_buggy_line_in_topN_DStar[1])
                bug_found_position_ECFL.append(is_buggy_line_in_topN_ECFL[1])

                if is_buggy_line_in_topN_DStar[0]:
                    buggy_line_in_topN_DStar_counter += 1

                if is_buggy_line_in_topN_ECFL[0]:
                    buggy_line_in_topN_ECFL_counter += 1

            total_bugs_found_DStar += buggy_line_in_topN_DStar_counter
            total_bugs_found_ECFL += buggy_line_in_topN_ECFL_counter


            print(f"PROJECT: {project}")
            print(f"Top {TOP_N} lines: \t DStar \t\t\t ECFL")
            print(f"Top {TOP_N} lines: \t {buggy_line_in_topN_DStar_counter} \t\t\t {buggy_line_in_topN_ECFL_counter} \t\t winner: ", end="")
            if buggy_line_in_topN_DStar_counter > buggy_line_in_topN_ECFL_counter:
                winner = "DStar"
                print(f" Dstar")
            elif buggy_line_in_topN_DStar_counter < buggy_line_in_topN_ECFL_counter:
                winner = "ECFL"
                print(f" ECFL")
            else:   #Equal
                winner = "Tie"
                print(f" Tie")

            with open(output_result_file, mode="a", encoding="utf-8") as myFile:
                myFile.write(f"\n======= susp weight: {susp_weight}, feature_weight: {feature_weight}======\n")
                myFile.write(f"PROJECT: {project}\n")
                myFile.write(f"Top {TOP_N} lines: \t DStar \t\t\t ECFL\n")
                myFile.write(f"Top {TOP_N} lines: \t {buggy_line_in_topN_DStar_counter} \t\t\t {buggy_line_in_topN_ECFL_counter}")
                myFile.write(f"\t\t winner: {winner}\n")

        print(f"================================================================================\n")

    bug_count = 0
    for bugs in PROJECT_BUGS:
        for bug in bugs:
            bug_count += 1

    print("\n\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: step5_evaluate_DStar_ECFL_using_TopN.py")
    print(f"FEATURE SELECTED: {FEATURE}")
    print(f"WEIGHT PAIRS SELECTED: [(DStar_weight, Feature_weight)]: {WEIGHT_PAIRS}")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    print(f"BUG IDs SELECTED: {PROJECT_BUGS}")
    print(f"\nTOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")
    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")


    print(f"\nEVALUATION METRIC: TOP-{TOP_N}")
    print(f"===================================")
    print(f"Total Bugs Found by DStar in Top-{TOP_N}: {total_bugs_found_DStar}")
    print(f"Total Bugs Found by ECFL in Top-{TOP_N}: {total_bugs_found_ECFL}")

    percent_change = 0
    if total_bugs_found_DStar != 0:
        percent_change = ((total_bugs_found_ECFL - total_bugs_found_DStar) / total_bugs_found_DStar) * 100
        print(f"Improvement from DStar to ECFL in percentage: {round(percent_change, 2)} %")

    print("\n############################ END ############################")

    with open(output_result_file, mode="a", encoding="utf-8") as myFile:
        myFile.write("\n############################ SUMMARY ############################\n")
        myFile.write(f"\nSCRIPT NAME: step5_evaluate_DStar_ECFL_using_TopN.py\n")
        myFile.write(f"FEATURE SELECTED: {FEATURE}\n")
        myFile.write(f"WEIGHT PAIRS SELECTED: [(DStar_weight, Feature_weight)]: {WEIGHT_PAIRS}\n")
        myFile.write(f"PROJECTS SELECTED: {PROJECTS}\n")
        myFile.write(f"BUG IDs SELECTED: {PROJECT_BUGS}\n")
        myFile.write(f"TOTAL NUMBER OF BUGS SELECTED: {bug_count}\n\n")
        myFile.write(f"INPUT DIRECTORY: {input_directory}\n")
        myFile.write(f"OUTPUT DIRECTORY: {output_directory}\n")


        myFile.write(f"\nEVALUATION METRIC: TOP-{TOP_N}\n")
        myFile.write(f"===================================\n")
        myFile.write(f"Total Bugs Found by DStar in Top-{TOP_N}: {total_bugs_found_DStar}\n")
        myFile.write(f"Total Bugs Found by ECFL in Top-{TOP_N}: {total_bugs_found_ECFL}\n")
        myFile.write(f"Improvement from DStar to ECFL in percentage: {round(percent_change, 2)} %\n")
        myFile.write("\n############################ END ############################\n")