# ========================================================================================
# IMPORTS AND GLOBAL CONFIGURATIONS
# ========================================================================================

import csv
import os
import time
import re

# PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
# PROJECTS = ['Closure', 'Lang', 'Math', 'Mockito', 'Time']
PROJECTS = ['Lang']

# PROJECT_BUGS = [
#     [str(x) for x in range(1, 134)],      # Closure
#     [str(x) for x in range(1, 66)],       # Lang
#     [str(x) for x in range(1, 27)],       # Chart
#     [str(x) for x in range(1, 107)],      # Math
#     [str(x) for x in range(1, 39)],       # Mockito
#     [str(x) for x in range(1, 28)]        # Time
# ]

# PROJECT_BUGS = [
#     [str(x) for x in range(1, 134)],      # Closure
#     [str(x) for x in range(1, 66)],       # Lang
#     [str(x) for x in range(1, 107)],      # Math
#     [str(x) for x in range(1, 39)],       # Mockito
#     [str(x) for x in range(1, 28)]        # Time
# ]

PROJECT_BUGS = [
     [str(x) for x in range(1, 2)]       # Lang
     ]


FL_TECHNIQUE = 'dstar2'          # Fault Localization (FL) Technique : DStar
WORKING_DIR = os.path.abspath('')

# FEATURE = 'LineLength' or 'LineCommitSize' or 'LineRecency' or 'LineChangeCount'
FEATURE = 'LineChangeCount'


# ========================================================================================
# FUNCTIONS
# ========================================================================================

def extract_line_feature(input_file, output_file, project_name, bug_id, orig_buggy_commit_id):
    """Extract the line change count feature by doing history slicing for every suspicious line

    Parameters
    ----------
    input_file : str (sorted suspicousness lines file)
    output_file: str (sorted suspiciousness lines file with the feature)
    project_name: str (project name)
    bug_id: str (bug id)
    orig_buggy_commit_id: str (Original buggy version commit id, different from Defects4J buggy version)

    """

    sorted_susp_lines = read_susp_lines_from_file(input_file)

    # Running git checkout buggy_version
    checkout_project_git(project_name, bug_id)

    # To checkout to the last version (defects4j buggy version)
    checkout_project_git_using_tag(project_name, bug_id)

    # Find all the previous commit ids starting with the latest commit for this bug starting from defects4j buggy version
    git_prev_commit_ids_all = find_all_commit_ids_per_file()

    # List to store commits ids from defects4j buggy to original buggy commit
    git_prev_commit_ids_till_buggy_ver = []

    for commit_id_prev in git_prev_commit_ids_all:
        if commit_id_prev == orig_buggy_commit_id:
            break
        git_prev_commit_ids_till_buggy_ver.append(commit_id_prev)

    git_blame_output = f"{WORKING_DIR}/line_mapping_history_slicing/git_blame_{project_name}_{bug_id}"

    line_counter = 1

    # Adding output file header out of loop
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"susp_line,suspiciousness,{FEATURE}\n")

    # Optimization
    file_names_seen = set()
    line_mapping_info_per_file = {}
    git_blame_lines_per_file = {}

    # history slicing
    lines_change_history_per_file = {}

    for susp_line in sorted_susp_lines:
        suspiciousness = round(float(susp_line[-1]), 4)
        susp_line_id = susp_line[0]
        file_name_full, line_number = susp_line[0].split("#")
        line_number = int(line_number)
        file_name = file_name_full.split("/")[-1]

        if file_name not in file_names_seen:
            checkout_project_git_using_tag(project_name, bug_id)
            if project_name == 'Chart':
                line_mapping_info, git_blame_lines = compute_diff_git_blame_lines_svn_Chart(file_name, file_name_full, git_blame_output, orig_buggy_commit_id, project_name, bug_id)
            else:
                line_mapping_info, git_blame_lines = compute_diff_git_blame_lines(file_name, file_name_full, git_blame_output, orig_buggy_commit_id)

            file_names_seen.add(file_name)
            line_mapping_info_per_file[file_name] = line_mapping_info
            git_blame_lines_per_file[file_name] = git_blame_lines

            # History slicing code
            if project_name == 'Chart':
                checkout_project_git_using_tag_delete_svn(project_name, bug_id)
                correct_file_name = find_file_path(file_name, file_name_full)
                svn_prev_commit_ids_per_file = find_all_commit_ids_per_file_svn(correct_file_name)

                for start_indx, svn_commit_id in enumerate(svn_prev_commit_ids_per_file):
                    if int(svn_commit_id) <= int(orig_buggy_commit_id):
                        break

                svn_prev_commit_ids_per_file = svn_prev_commit_ids_per_file[start_indx:]
                if orig_buggy_commit_id not in svn_prev_commit_ids_per_file:
                    svn_prev_commit_ids_per_file.insert(0, orig_buggy_commit_id)

                lines_change_history, orig_file = compute_line_history_slicing_svn_Chart(file_name, file_name_full, git_blame_output, orig_buggy_commit_id, svn_prev_commit_ids_per_file, project_name, bug_id)
                lines_change_history_per_file[file_name] = lines_change_history

            else:
                checkout_project_git_using_tag(project_name, bug_id)
                correct_file_name = find_file_path(file_name, file_name_full)
                git_prev_commit_ids_per_file = find_all_commit_ids_per_file(correct_file_name)

                commit_id_start_index_file = 0
                for i, commind_id_file in enumerate(git_prev_commit_ids_per_file):
                    if commind_id_file not in git_prev_commit_ids_till_buggy_ver:
                        commit_id_start_index_file = i
                        break

                git_prev_commit_ids_per_file = git_prev_commit_ids_per_file[commit_id_start_index_file:]
                if orig_buggy_commit_id not in git_prev_commit_ids_per_file:
                    git_prev_commit_ids_per_file.insert(0, orig_buggy_commit_id)

                lines_change_history, orig_file = compute_line_history_slicing(file_name, file_name_full, git_blame_output, orig_buggy_commit_id, git_prev_commit_ids_per_file)
                lines_change_history_per_file[file_name] = lines_change_history

        else:
            line_mapping_info = line_mapping_info_per_file[file_name]
            git_blame_lines = git_blame_lines_per_file[file_name]
            lines_change_history = lines_change_history_per_file[file_name]

        if line_mapping_info:   # If the diff is non empty, then take the correct line number from the mapping
            if line_number in line_mapping_info:
                line_number = line_mapping_info[line_number]
            else:
                continue

        if line_number in git_blame_lines:
            line_change_count = 0
            if line_number in lines_change_history:
                line_change_count = lines_change_history[line_number]
            add_susp_data_to_file(output_file, susp_line_id, suspiciousness, line_change_count)

        line_counter += 1


def find_commit_size(line_commit_id, project):
    commit_size_output_file = f"{WORKING_DIR}/line_mapping_history_slicing/{project}_temp_file.txt"
    os.system(f"git show {line_commit_id} --shortstat > {commit_size_output_file}")
    output_lines = csv.reader(open(commit_size_output_file, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_new = list(output_lines)

    # Bug fix for ^adl2232 (commit id starts with carret)
    if not git_blame_lines_new:
        return 0

    # print(git_blame_lines_new[-1])
    # [' 2 files changed, 165 insertions(+), 74 deletions(-)']

    git_commit_size_line = git_blame_lines_new[-1][0]     # Last line contains the commit size
    start_index = git_commit_size_line.find(', ')
    end_index = git_commit_size_line.find('insertion')

    # print(git_commit_size_line[(start_index + 1):end_index].strip())
    line_commit_size = int(git_commit_size_line[(start_index + 1):end_index].strip())
    os.remove(commit_size_output_file)
    return line_commit_size


def compute_line_history_slicing(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version, git_prev_commit_ids):

    # First commit id is the original buggy version
    # git_prev_commit_ids = ["1f001d06a2bde5ee4e3204ab38c4b1db8e95db0b", "ccddbbd3c5beff36e6b959f0f3f0105109692f34", "eccfbc4c4ba1539e415509096acd2a9d9255a8f3", "9f2c007cc1591d47722526cb90709ef309d04ceb"]

    # dictionary=> key: line number, value: list of line mappings of previous versions
    line_mapping_table, line_changes_table, git_blame_lines_orig, orig_file_1 = compute_diff_git_blame_lines_first_mapping(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version)

    # Simple fix to remove the changes done by defects4j team
    for line_num in line_changes_table:
        if line_changes_table[line_num][0] != 'u':
            line_changes_table[line_num][0] = 'u'      # Making the line as unchanged to remove the changes done by defects4j team

    lines_change_history = {}
    number_of_non_empty_diffs = 0
    number_of_commits_to_run = len(git_prev_commit_ids) - 1     # Going back to all the commtis that modified this file

    for i in range(number_of_commits_to_run):
        line_mapping, line_changes, orig_file = compute_line_mapping_bet_two_versions_history_slicing(file_name, file_name_full, git_blame_output, git_prev_commit_ids[i + 1], git_prev_commit_ids[i])
        if line_mapping == -1:
            break       # File not found. So no point of going further back in history
        if line_mapping and orig_file:        # Diff is present and mapping is there
            for line_num in range(1, len(line_mapping_table) + 1):
                if line_mapping_table[line_num][-1] != -1:
                    prev_line_num = line_mapping_table[line_num][-1]
                    if prev_line_num not in line_mapping:
                        continue
                    line_mapping_table[line_num].append(line_mapping[prev_line_num])
                    line_changes_table[line_num].append(line_changes[prev_line_num])

                else:       # -1 (newly added line, so no history)
                    line_mapping_table[line_num].append(-1)
                    line_changes_table[line_num].append('n')    # n => non-existant

            number_of_non_empty_diffs += 1

    # Computing Line change counts from the history table
    for line_num in line_changes_table:
        lines_change_history[line_num] = line_changes_table[line_num].count('c') + line_changes_table[line_num].count('a')

    return lines_change_history, orig_file_1


def compute_line_history_slicing_svn_Chart(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version, svn_prev_commit_ids, project, bug):

    # First commit id is the original buggy version
    # git_prev_commit_ids = ["1f001d06a2bde5ee4e3204ab38c4b1db8e95db0b", "ccddbbd3c5beff36e6b959f0f3f0105109692f34", "eccfbc4c4ba1539e415509096acd2a9d9255a8f3", "9f2c007cc1591d47722526cb90709ef309d04ceb"]

    # dictionary=> key: line number, value: list of line mappings of previous versions
    line_mapping_table, line_changes_table, git_blame_lines_orig, orig_file_1 = compute_diff_git_blame_lines_first_mapping_svn_Chart(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version, project, bug)

    # Simple fix to remove the changes done by defects4j team
    for line_num in line_changes_table:
        if line_changes_table[line_num][0] != 'u':
            line_changes_table[line_num][0] = 'u'      # Making the line as unchanged to remove the changes done by defects4j team

    lines_change_history = {}
    number_of_non_empty_diffs = 0
    number_of_commits_to_run = len(svn_prev_commit_ids) - 1     # Going back to all the commits that modified this file

    for i in range(number_of_commits_to_run):
        line_mapping, line_changes, orig_file = compute_line_mapping_bet_two_versions_history_slicing_svn_Chart(file_name, file_name_full, git_blame_output, svn_prev_commit_ids[i + 1], svn_prev_commit_ids[i], project, bug)
        if line_mapping == -1:
            break       # File not found. So no point of going further back in history
        if line_mapping and orig_file:        # Diff is present and mapping is there
            for line_num in range(1, len(line_mapping_table) + 1):
                if line_mapping_table[line_num][-1] != -1:
                    prev_line_num = line_mapping_table[line_num][-1]
                    if prev_line_num not in line_mapping:
                        continue
                    line_mapping_table[line_num].append(line_mapping[prev_line_num])
                    line_changes_table[line_num].append(line_changes[prev_line_num])

                else:       # -1 (newly added line, so no history)
                    line_mapping_table[line_num].append(-1)
                    line_changes_table[line_num].append('n')    # n => non-existant

            number_of_non_empty_diffs += 1

    # Computing Line change counts from the history table
    for line_num in line_changes_table:
        lines_change_history[line_num] = line_changes_table[line_num].count('c') + line_changes_table[line_num].count('a')

    return lines_change_history, orig_file_1


def compute_diff_git_blame_lines(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version):
    """Line mapping code

    Parameters:
    ----------
    file_name: str (file name of susp line)
    file_name_full: str (full file path of susp line)
    git_blame_output : str (output file where git blame command output is dumped)
    commit_id_original_buggy_version: str (Original buggy version commit id, different from Defects4J buggy version)

    Return:
    -------
    line_mapping_info: dictionary (key: value pair is Defects4J_buggy_line_id: Original_buggy_line_id)
    git_blame_lines_orig: dictionary
        (key: value pair is Original_buggy_line_id: git blame line with all details such as line content, data modified)

    """

    file_path = find_file_path(file_name, file_name_full)
    os.system(f"git blame {file_path} > {git_blame_output}")
    defects4j_buggy_file = git_blame_output + "_defects4j_buggy_file"
    os.system(f"cat {file_path} > {defects4j_buggy_file}")

    # Original buggy version
    os.system(f"git checkout {commit_id_original_buggy_version}")
    file_path = find_file_path(file_name, file_name_full)
    git_blame_output_orig = git_blame_output + "_orig"
    os.system(f"git blame {file_path} > {git_blame_output_orig}")
    original_buggy_file = git_blame_output + "_" + file_name + "_original_buggy_file"
    os.system(f"cat {file_path} > {original_buggy_file}")

    git_blame_diff = git_blame_output + "_diff_blame"
    os.system(f"diff {git_blame_output_orig} {git_blame_output} > {git_blame_diff}")
    diff_output = git_blame_output + "_diff_output"
    os.system(f"diff {original_buggy_file} {defects4j_buggy_file} > {diff_output}")

    git_blame_lines_new = csv.reader(open(git_blame_output, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_new = list(git_blame_lines_new)
    git_blame_lines_new = {(i + 1): git_blame_lines_new[i] for i in range(len(git_blame_lines_new))}
    number_of_lines_new = len(git_blame_lines_new)

    git_blame_lines_orig = csv.reader(open(git_blame_output_orig, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_orig = list(git_blame_lines_orig)
    git_blame_lines_orig = {(i + 1): git_blame_lines_orig[i] for i in range(len(git_blame_lines_orig))}
    number_of_lines_old = len(git_blame_lines_orig)

    # If the diff is empty, no need of line mapping
    if os.stat(diff_output).st_size == 0:
        # Removing unnecessary files after use
        os.remove(defects4j_buggy_file)
        os.remove(git_blame_output_orig)
        os.remove(git_blame_output)
        os.remove(git_blame_diff)
        os.remove(diff_output)
        os.remove(original_buggy_file)
        end_time = time.time()
        return None, git_blame_lines_orig

    path_to_diff_runner = f"{WORKING_DIR}/line_mapping_history_slicing/RunDiffProcessor_1.jar"
    properties_file = f"{WORKING_DIR}/line_mapping_history_slicing/HistorySlicingFuzzy.properties"
    line_mapping_output_file = git_blame_output + "_line_mapping"
    os.system(f"java -jar {path_to_diff_runner} {properties_file} {diff_output} {number_of_lines_old} {number_of_lines_new} > {line_mapping_output_file}")

    line_mapping_info = csv.reader(open(line_mapping_output_file, encoding='ISO-8859-1'), delimiter='\n')
    line_mapping_info = list(line_mapping_info)
    line_mapping_info = {(i + 1): int(*line_mapping_info[i]) for i in range(len(line_mapping_info))}

    # Removing unnecessary files after use
    os.remove(defects4j_buggy_file)
    os.remove(git_blame_output_orig)
    os.remove(git_blame_output)
    os.remove(git_blame_diff)
    os.remove(diff_output)
    os.remove(line_mapping_output_file)
    os.remove(original_buggy_file)

    return line_mapping_info, git_blame_lines_orig




def compute_diff_git_blame_lines_svn_Chart(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version, project, bug):

    file_path = find_file_path(file_name, file_name_full)
    os.system(f"git blame {file_path} > {git_blame_output}")

    defects4j_buggy_file = git_blame_output + "_defects4j_buggy_file"
    os.system(f"cat {file_path} > {defects4j_buggy_file}")

    d4j_home = os.environ['D4J_HOME']  # Accessing environment variable, echo $D4J_HOME
    os.system(f"svn checkout -r {commit_id_original_buggy_version} file://{d4j_home}project_repos/jfreechart/")
    checkout_directory = f"/tmp/{project}_{bug}_buggy_ver/jfreechart/"
    os.chdir(checkout_directory)

    file_path = find_file_path(file_name, file_name_full)
    git_blame_output_orig = git_blame_output + "_orig"
    os.system(f"svn blame -v {file_path} > {git_blame_output_orig}")

    original_buggy_file = git_blame_output + "_" + file_name + "_original_buggy_file"
    os.system(f"cat {file_path} > {original_buggy_file}")

    git_blame_diff = git_blame_output + "_diff_blame"
    os.system(f"diff {git_blame_output_orig} {git_blame_output} > {git_blame_diff}")

    diff_output = git_blame_output + "_diff_output"
    os.system(f"diff {original_buggy_file} {defects4j_buggy_file} > {diff_output}")

    git_blame_lines_new = csv.reader(open(git_blame_output, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_new = list(git_blame_lines_new)
    git_blame_lines_new = {(i+1):git_blame_lines_new[i] for i in range(len(git_blame_lines_new))}
    number_of_lines_new = len(git_blame_lines_new)

    git_blame_lines_orig = csv.reader(open(git_blame_output_orig, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_orig = list(git_blame_lines_orig)
    git_blame_lines_orig = {(i+1):git_blame_lines_orig[i] for i in range(len(git_blame_lines_orig))}
    number_of_lines_old = len(git_blame_lines_orig)

    buggy_file_lines_orig = csv.reader(open(original_buggy_file, encoding='ISO-8859-1'), delimiter='\n')
    buggy_file_lines_orig = list(buggy_file_lines_orig)
    buggy_file_lines_orig = {(i + 1): buggy_file_lines_orig[i] for i in range(len(buggy_file_lines_orig))}
    number_of_lines_old_buggy_file = len(buggy_file_lines_orig)

    # if the diff is empty, no need of line mapping
    if os.stat(diff_output).st_size == 0:
        # Removing unnecessary files after use
        os.remove(defects4j_buggy_file)
        os.remove(git_blame_output_orig)
        os.remove(git_blame_output)
        os.remove(git_blame_diff)
        os.remove(diff_output)
        os.remove(original_buggy_file)

        return None, git_blame_lines_orig

    home_path = f"{WORKING_DIR}/line_mapping_history_slicing/"
    path_to_diff_runner = home_path + "RunDiffProcessor_1.jar"
    properties_file = home_path + "HistorySlicingFuzzy.properties"
    line_mapping_output_file = git_blame_output + "_line_mapping"

    os.system(f"java -jar {path_to_diff_runner} {properties_file} {diff_output} {number_of_lines_old} {number_of_lines_new} > {line_mapping_output_file}")

    line_mapping_info = csv.reader(open(line_mapping_output_file, encoding='ISO-8859-1'), delimiter='\n')
    line_mapping_info = list(line_mapping_info)
    line_mapping_info = {(i + 1): int(*line_mapping_info[i]) for i in range(len(line_mapping_info))}

    # Removing unnecessary files after use
    os.remove(defects4j_buggy_file)
    os.remove(git_blame_output_orig)
    os.remove(git_blame_output)
    os.remove(git_blame_diff)
    os.remove(diff_output)
    os.remove(line_mapping_output_file)
    os.remove(original_buggy_file)

    return line_mapping_info, git_blame_lines_orig


def compute_line_mapping_bet_two_versions_history_slicing(file_name, file_name_full, output_file_path, commit_id_old, commit_id_new):

    # Checkout new version.
    os.system(f"git checkout {commit_id_new}")
    git_blame_output_new = output_file_path + "_blame_new_file"
    file_path = find_file_path(file_name, file_name_full)
    if not file_path:
        print("Inside compute_line_mapping_bet_two_versions_history_slicing(): file_path is empty")
        return -1, -1, -1

    os.system(f"git blame {file_path} > {git_blame_output_new}")
    file_contents_output_new = output_file_path + "_content_new_file"
    os.system(f"cat {file_path} > {file_contents_output_new}")

    # Checkout old version.
    os.system(f"git checkout {commit_id_old}")
    git_blame_output_old = output_file_path + "_blame_old_file"

    file_path = find_file_path(file_name, file_name_full)
    if not file_path:
        print("Inside compute_line_mapping_bet_two_versions_history_slicing(): file_path is empty")
        return -1, -1, -1


    os.system(f"git blame {file_path} > {git_blame_output_old}")
    file_contents_output_old = output_file_path + "_content_old_file"
    os.system(f"cat {file_path} > {file_contents_output_old}")

    # Compute diff.
    git_blame_diff = output_file_path + "_diff_blame"
    os.system(f"diff {git_blame_output_old} {git_blame_output_new} > {git_blame_diff}")
    diff_output = output_file_path + "_diff_output"
    os.system(f"diff {file_contents_output_old} {file_contents_output_new} > {diff_output}")

    git_blame_lines_new = csv.reader(open(git_blame_output_new, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_new = list(git_blame_lines_new)
    git_blame_lines_new = {(i+1):git_blame_lines_new[i] for i in range(len(git_blame_lines_new))}
    number_of_lines_new = len(git_blame_lines_new)

    git_blame_lines_orig = csv.reader(open(git_blame_output_old, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_orig = list(git_blame_lines_orig)
    git_blame_lines_orig = {(i+1):git_blame_lines_orig[i] for i in range(len(git_blame_lines_orig))}
    number_of_lines_old = len(git_blame_lines_orig)

    orig_file = csv.reader(open(file_contents_output_old, encoding='ISO-8859-1'), delimiter='\n')
    orig_file = list(orig_file)
    orig_file = {(i + 1): orig_file[i] for i in range(len(orig_file))}
    number_of_lines_old_orig_file = len(orig_file)

    if number_of_lines_old_orig_file == 0:
        return -1, -1, -1

    # if the diff is empty, no need of line mapping
    if os.stat(diff_output).st_size == 0:
        # Removing unnecessary files
        os.remove(git_blame_output_old)
        os.remove(git_blame_output_new)
        os.remove(git_blame_diff)
        os.remove(file_contents_output_old)
        os.remove(file_contents_output_new)
        os.remove(diff_output)

        return None, None, None
        # If there is no change, then use the previous values. So, you need to pass None

    home_path = f"{WORKING_DIR}/line_mapping_history_slicing/"
    path_to_diff_runner = home_path + "RunDiffProcessor_2.jar"
    properties_file = home_path + "HistorySlicingFuzzy.properties"
    line_mapping_output_file = output_file_path + "_line_mapping"

    os.system(f"java -jar {path_to_diff_runner} {properties_file} {diff_output} {number_of_lines_old} {number_of_lines_new} > {line_mapping_output_file}")

    line_mapping_info = csv.reader(open(line_mapping_output_file, encoding='ISO-8859-1'), delimiter='\n')
    line_mapping_info_tmp = list(line_mapping_info)

    # storing line change info separately. 'a' -> added, 'u' -> unchanged, 'c' -> changed
    line_mapping_info = line_mapping_info_tmp[: number_of_lines_new]    # First half is line mapping
    line_changes_info = line_mapping_info_tmp[number_of_lines_new:]     # Next half is changes (a or u or c)
    line_mapping_info_dict = {(i + 1): int(*line_mapping_info[i]) for i in range(len(line_mapping_info))}
    line_changes_info_dict = {(i + 1): str(*line_changes_info[i]) for i in range(len(line_changes_info))}

    # Removing unnecessary files after use
    os.remove(git_blame_output_old)
    os.remove(git_blame_output_new)
    os.remove(git_blame_diff)
    os.remove(file_contents_output_old)
    os.remove(file_contents_output_new)
    os.remove(diff_output)
    os.remove(line_mapping_output_file)

    return line_mapping_info_dict, line_changes_info_dict, orig_file


def compute_line_mapping_bet_two_versions_history_slicing_svn_Chart(file_name, file_name_full, output_file_path, commit_id_old, commit_id_new, project, bug):

    # Checkout new version.
    d4j_home = os.environ['D4J_HOME']  # Accessing environment variable, echo $D4J_HOME
    os.system(f"svn checkout -r {commit_id_new} file://{d4j_home}project_repos/jfreechart/")
    checkout_directory = f"/tmp/{project}_{bug}_buggy_ver/jfreechart/"
    os.chdir(checkout_directory)

    git_blame_output_new = output_file_path + "_blame_new_file"
    file_path = find_file_path(file_name, file_name_full)
    if not file_path:
        print("Inside compute_line_mapping_bet_two_versions_history_slicing(): file_path is empty")
        return -1, -1, -1

    os.system(f"svn blame -v {file_path} > {git_blame_output_new}")
    file_contents_output_new = output_file_path + "_content_new_file"
    os.system(f"cat {file_path} > {file_contents_output_new}")

    # Checkout old version.
    d4j_home = os.environ['D4J_HOME']  # Accessing environment variable, echo $D4J_HOME
    os.system(f"svn checkout -r {commit_id_old} file://{d4j_home}project_repos/jfreechart/")
    checkout_directory = f"/tmp/{project}_{bug}_buggy_ver/jfreechart/"
    os.chdir(checkout_directory)

    git_blame_output_old = output_file_path + "_blame_old_file"

    file_path = find_file_path(file_name, file_name_full)
    if not file_path:
        print("Inside compute_line_mapping_bet_two_versions_history_slicing(): file_path is empty")
        return -1, -1, -1

    os.system(f"svn blame -v {file_path} > {git_blame_output_old}")
    file_contents_output_old = output_file_path + "_content_old_file"
    os.system(f"cat {file_path} > {file_contents_output_old}")

    # Compute diff.
    git_blame_diff = output_file_path + "_diff_blame"
    os.system(f"diff {git_blame_output_old} {git_blame_output_new} > {git_blame_diff}")
    diff_output = output_file_path + "_diff_output"
    os.system(f"diff {file_contents_output_old} {file_contents_output_new} > {diff_output}")

    git_blame_lines_new = csv.reader(open(git_blame_output_new, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_new = list(git_blame_lines_new)
    git_blame_lines_new = {(i+1):git_blame_lines_new[i] for i in range(len(git_blame_lines_new))}
    number_of_lines_new = len(git_blame_lines_new)

    git_blame_lines_orig = csv.reader(open(git_blame_output_old, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_orig = list(git_blame_lines_orig)
    git_blame_lines_orig = {(i+1):git_blame_lines_orig[i] for i in range(len(git_blame_lines_orig))}
    number_of_lines_old = len(git_blame_lines_orig)

    orig_file = csv.reader(open(file_contents_output_old, encoding='ISO-8859-1'), delimiter='\n')
    orig_file = list(orig_file)
    orig_file = {(i + 1): orig_file[i] for i in range(len(orig_file))}
    number_of_lines_old_orig_file = len(orig_file)

    if number_of_lines_old_orig_file == 0:
        return -1, -1, -1

    # if the diff is empty, no need of line mapping
    if os.stat(diff_output).st_size == 0:
        # Removing unnecessary files
        os.remove(git_blame_output_old)
        os.remove(git_blame_output_new)
        os.remove(git_blame_diff)
        os.remove(file_contents_output_old)
        os.remove(file_contents_output_new)
        os.remove(diff_output)

        return None, None, None
        # If there is no change, then use the previous values. So, you need to pass None

    home_path = f"{WORKING_DIR}/line_mapping_history_slicing/"
    path_to_diff_runner = home_path + "RunDiffProcessor_2.jar"
    properties_file = home_path + "HistorySlicingFuzzy.properties"
    line_mapping_output_file = output_file_path + "_line_mapping"

    os.system(f"java -jar {path_to_diff_runner} {properties_file} {diff_output} {number_of_lines_old} {number_of_lines_new} > {line_mapping_output_file}")

    line_mapping_info = csv.reader(open(line_mapping_output_file, encoding='ISO-8859-1'), delimiter='\n')
    line_mapping_info_tmp = list(line_mapping_info)

    # storing line change info separately. 'a' -> added, 'u' -> unchanged, 'c' -> changed
    line_mapping_info = line_mapping_info_tmp[: number_of_lines_new]    # First half is line mapping
    line_changes_info = line_mapping_info_tmp[number_of_lines_new:]     # Next half is changes (a or u or c)
    line_mapping_info_dict = {(i + 1): int(*line_mapping_info[i]) for i in range(len(line_mapping_info))}
    line_changes_info_dict = {(i + 1): str(*line_changes_info[i]) for i in range(len(line_changes_info))}

    # Removing unnecessary files after use
    os.remove(git_blame_output_old)
    os.remove(git_blame_output_new)
    os.remove(git_blame_diff)
    os.remove(file_contents_output_old)
    os.remove(file_contents_output_new)
    os.remove(diff_output)
    os.remove(line_mapping_output_file)

    return line_mapping_info_dict, line_changes_info_dict, orig_file


def find_all_commit_ids_per_file_svn(file_name=""):
    commit_ids = []

    if file_name:
        os.system(fr"svn log {file_name} | perl -l40pe 's/^-+/\n/' > svn_log_single_line.txt")
    else:
        os.system(r"svn log | perl -l40pe 's/^-+/\n/' > svn_log_single_line.txt")

    # r is added to say it is a raw string since \n was present
    commits_file = csv.reader(open("svn_log_single_line.txt", encoding='ISO-8859-1'), delimiter='\n')
    commits_list = list(commits_file)
    for c in commits_list:
        if c:
            commit_line = c[0].split("|")
            commit_ids.append(commit_line[0].strip()[1:])
    return commit_ids


def find_all_commit_ids_per_file(file_name = ""):
    git_commit_ids = []
    git_commits = get_commits(file_name)
    for commit in git_commits:
        git_commit_ids.append(commit['hash'])
    return git_commit_ids


def get_commits(file_name):
    import subprocess
    import re

    leading_4_spaces = re.compile('^    ')

    if file_name:
        lines = subprocess.check_output(['git', 'log', file_name])
    else:
        lines = subprocess.check_output(['git', 'log'])

    lines = lines.decode().split('\n')
    commits = []
    current_commit = {}

    def save_current_commit():
        title = current_commit['message'][0]
        message = current_commit['message'][1:]
        if message and message[0] == '':
            del message[0]
        current_commit['title'] = title
        current_commit['message'] = '\n'.join(message)
        commits.append(current_commit)

    for line in lines:
        if not line.startswith(' '):
            if line.startswith('commit '):
                if current_commit:
                    save_current_commit()
                    current_commit = {}
                current_commit['hash'] = line.split('commit ')[1]
            else:
                try:
                    key, value = line.split(':', 1)
                    current_commit[key.lower()] = value.strip()
                except ValueError:
                    pass
        else:
            current_commit.setdefault(
                'message', []
            ).append(leading_4_spaces.sub('', line))

    if current_commit:
        save_current_commit()
    return commits


def add_susp_data_to_file(output_file, susp_line_id, suspiciousness, line_change_count):
    """Adds LineLength feature to the sorted suspiciousness file

    Parameters:
    ----------
    output_file: str
    susp_line_id: int
    suspiciousness: float
    LineLength: int

    """

    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line_id},{suspiciousness},{line_change_count}\n")


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
    susp_data = csv.reader(open(input_file), delimiter=',')

    top_n_lines = 100
    # header line is not needed (first line is skipped)
    sorted_susp_lines = [susp_line for i, susp_line in enumerate(susp_data) if i != 0 and i <= top_n_lines]

    return sorted_susp_lines


def checkout_project_git_using_tag(project, bug):
    """
    Checkout to the Defects4j buggy version

    Parameters:
    ----------
    project: str
    bug: str
    """
    commit_tag = f"D4J_{project}_{bug}_BUGGY_VERSION"
    os.system(f"git checkout {commit_tag}")


def checkout_project_git_using_tag_delete_svn(project, bug):
    checkout_directory = f"/tmp/{project}_{bug}_buggy_ver"
    os.chdir("/tmp/")
    import shutil
    shutil.rmtree(checkout_directory)   # remove non-empty directory
    command_git_checkout = f"defects4j checkout -p {project} -v {bug}b -w {checkout_directory}"
    os.system(command_git_checkout)
    os.chdir(checkout_directory)


def checkout_project_git(project, bug):
    """
    checkout to the project using git commands

    Parameters:
    ----------
    project: str
    bug: str
    """

    checkout_directory = f"/tmp/{project}_{bug}_buggy_ver"
    command_git_checkout = f"defects4j checkout -p {project} -v {bug}b -w {checkout_directory}"
    os.system(command_git_checkout)
    os.chdir(checkout_directory)


def find_file_path(file_name, susp_file_path):
    """
    Find the full path of the file

    Parameters:
    ----------
    file_name: str
    susp_file_path: str
    """
    find_command = f"find -name {file_name}"
    os.system(f"{find_command} > find_output.txt")

    file_paths = None
    with open("find_output.txt") as file:
        file_paths = file.readlines()

    if not file_paths:
        return None

    if len(file_paths) == 1:
        return file_paths[0].strip("\n")

    for file_path in file_paths:
        if susp_file_path in file_path:
            return file_path.strip("\n")


def compute_diff_git_blame_lines_first_mapping(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version):

    file_path = find_file_path(file_name, file_name_full)
    os.system(f"git blame {file_path} > {git_blame_output}")

    defects4j_buggy_file = git_blame_output + "_defects4j_buggy_file"
    os.system(f"cat {file_path} > {defects4j_buggy_file}")

    # Original buggy version
    os.system(f"git checkout {commit_id_original_buggy_version}")

    file_path = find_file_path(file_name, file_name_full)
    git_blame_output_orig = git_blame_output + "_orig"
    os.system(f"git blame {file_path} > {git_blame_output_orig}")

    original_buggy_file = git_blame_output + "_" + file_name + "_original_buggy_file"
    os.system(f"cat {file_path} > {original_buggy_file}")

    git_blame_diff = git_blame_output + "_diff_blame"
    os.system(f"diff {git_blame_output_orig} {git_blame_output} > {git_blame_diff}")

    diff_output = git_blame_output + "_diff_output"
    os.system(f"diff {original_buggy_file} {defects4j_buggy_file} > {diff_output}")

    git_blame_lines_new = csv.reader(open(git_blame_output, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_new = list(git_blame_lines_new)
    git_blame_lines_new = {(i+1):git_blame_lines_new[i] for i in range(len(git_blame_lines_new))}
    number_of_lines_new = len(git_blame_lines_new)

    git_blame_lines_orig = csv.reader(open(git_blame_output_orig, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_orig = list(git_blame_lines_orig)
    git_blame_lines_orig = {(i+1):git_blame_lines_orig[i] for i in range(len(git_blame_lines_orig))}
    number_of_lines_old = len(git_blame_lines_orig)


    buggy_file_lines_orig = csv.reader(open(original_buggy_file, encoding='ISO-8859-1'), delimiter='\n')
    buggy_file_lines_orig = list(buggy_file_lines_orig)
    buggy_file_lines_orig = {(i + 1): buggy_file_lines_orig[i] for i in range(len(buggy_file_lines_orig))}
    number_of_lines_old_buggy_file = len(buggy_file_lines_orig)

    # if the diff is empty, no need of line mapping
    if os.stat(diff_output).st_size == 0:
        # Removing unnecessary files after use
        os.remove(defects4j_buggy_file)
        os.remove(git_blame_output_orig)
        os.remove(git_blame_output)
        os.remove(git_blame_diff)
        os.remove(diff_output)
        os.remove(original_buggy_file)

        # This function is called one time and then a separate function is called for history slicing
        line_mapping_info_dict_temp = {(i + 1): [(i + 1)] for i in range(number_of_lines_new)}
        line_changes_info_dict_temp = {(i + 1): ['u'] for i in range(number_of_lines_new)}

        return line_mapping_info_dict_temp, line_changes_info_dict_temp, git_blame_lines_orig, buggy_file_lines_orig

        # return None, git_blame_lines_orig, buggy_file_lines_orig

    home_path = f"{WORKING_DIR}/line_mapping_history_slicing/"
    path_to_diff_runner = home_path + "RunDiffProcessor_2.jar"
    properties_file = home_path + "HistorySlicingFuzzy.properties"
    line_mapping_output_file = git_blame_output + "_line_mapping"

    os.system(f"java -jar {path_to_diff_runner} {properties_file} {diff_output} {number_of_lines_old} {number_of_lines_new} > {line_mapping_output_file}")

    line_mapping_info = csv.reader(open(line_mapping_output_file, encoding='ISO-8859-1'), delimiter='\n')
    line_mapping_info = list(line_mapping_info)

    # storing line change info separately. 'a' -> added, 'u' -> unchanged, 'c' -> changed
    line_changes_info = line_mapping_info[number_of_lines_new:]
    line_mapping_info = line_mapping_info[: number_of_lines_new]
    line_mapping_info_dict = {(i + 1): [int(*line_mapping_info[i])] for i in range(len(line_mapping_info))}
    line_changes_info_dict = {(i + 1): [str(*line_changes_info[i])] for i in range(len(line_changes_info))}

    # Removing unnecessary files after use
    os.remove(defects4j_buggy_file)
    os.remove(git_blame_output_orig)
    os.remove(git_blame_output)
    os.remove(git_blame_diff)
    os.remove(diff_output)
    os.remove(line_mapping_output_file)
    os.remove(original_buggy_file)

    return line_mapping_info_dict, line_changes_info_dict, git_blame_lines_orig, buggy_file_lines_orig



def compute_diff_git_blame_lines_first_mapping_svn_Chart(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version, project, bug):

    file_path = find_file_path(file_name, file_name_full)
    os.system(f"git blame {file_path} > {git_blame_output}")

    defects4j_buggy_file = git_blame_output + "_defects4j_buggy_file"
    os.system(f"cat {file_path} > {defects4j_buggy_file}")

    # Original buggy version
    # os.system(f"git checkout {commit_id_original_buggy_version}")
    d4j_home = os.environ['D4J_HOME']  # Accessing environment variable, echo $D4J_HOME
    os.system(f"svn checkout -r {commit_id_original_buggy_version} file://{d4j_home}project_repos/jfreechart/")
    checkout_directory = f"/tmp/{project}_{bug}_buggy_ver/jfreechart/"
    os.chdir(checkout_directory)

    file_path = find_file_path(file_name, file_name_full)
    git_blame_output_orig = git_blame_output + "_orig"
    os.system(f"svn blame -v {file_path} > {git_blame_output_orig}")

    original_buggy_file = git_blame_output + "_" + file_name + "_original_buggy_file"
    os.system(f"cat {file_path} > {original_buggy_file}")

    git_blame_diff = git_blame_output + "_diff_blame"
    os.system(f"diff {git_blame_output_orig} {git_blame_output} > {git_blame_diff}")

    diff_output = git_blame_output + "_diff_output"
    os.system(f"diff {original_buggy_file} {defects4j_buggy_file} > {diff_output}")

    git_blame_lines_new = csv.reader(open(git_blame_output, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_new = list(git_blame_lines_new)
    git_blame_lines_new = {(i+1):git_blame_lines_new[i] for i in range(len(git_blame_lines_new))}
    number_of_lines_new = len(git_blame_lines_new)

    git_blame_lines_orig = csv.reader(open(git_blame_output_orig, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_orig = list(git_blame_lines_orig)
    git_blame_lines_orig = {(i+1):git_blame_lines_orig[i] for i in range(len(git_blame_lines_orig))}
    number_of_lines_old = len(git_blame_lines_orig)

    buggy_file_lines_orig = csv.reader(open(original_buggy_file, encoding='ISO-8859-1'), delimiter='\n')
    buggy_file_lines_orig = list(buggy_file_lines_orig)
    buggy_file_lines_orig = {(i + 1): buggy_file_lines_orig[i] for i in range(len(buggy_file_lines_orig))}
    number_of_lines_old_buggy_file = len(buggy_file_lines_orig)

    # if the diff is empty, no need of line mapping
    if os.stat(diff_output).st_size == 0:
        # Removing unnecessary files after use
        os.remove(defects4j_buggy_file)
        os.remove(git_blame_output_orig)
        os.remove(git_blame_output)
        os.remove(git_blame_diff)
        os.remove(diff_output)
        os.remove(original_buggy_file)

        # This function is called one time and then a separate function is called for history slicing
        line_mapping_info_dict_temp = {(i + 1): [(i + 1)] for i in range(number_of_lines_new)}
        line_changes_info_dict_temp = {(i + 1): ['u'] for i in range(number_of_lines_new)}

        return line_mapping_info_dict_temp, line_changes_info_dict_temp, git_blame_lines_orig, buggy_file_lines_orig

    home_path = f"{WORKING_DIR}/line_mapping_history_slicing/"
    path_to_diff_runner = home_path + "RunDiffProcessor_2.jar"
    properties_file = home_path + "HistorySlicingFuzzy.properties"
    line_mapping_output_file = git_blame_output + "_line_mapping"

    os.system(f"java -jar {path_to_diff_runner} {properties_file} {diff_output} {number_of_lines_old} {number_of_lines_new} > {line_mapping_output_file}")

    line_mapping_info = csv.reader(open(line_mapping_output_file, encoding='ISO-8859-1'), delimiter='\n')
    line_mapping_info = list(line_mapping_info)

    # storing line change info separately. 'a' -> added, 'u' -> unchanged, 'c' -> changed
    line_changes_info = line_mapping_info[number_of_lines_new:]
    line_mapping_info = line_mapping_info[: number_of_lines_new]
    line_mapping_info_dict = {(i + 1): [int(*line_mapping_info[i])] for i in range(len(line_mapping_info))}
    line_changes_info_dict = {(i + 1): [str(*line_changes_info[i])] for i in range(len(line_changes_info))}

    # Removing unnecessary files after use
    os.remove(defects4j_buggy_file)
    os.remove(git_blame_output_orig)
    os.remove(git_blame_output)
    os.remove(git_blame_diff)
    os.remove(diff_output)
    os.remove(line_mapping_output_file)
    os.remove(original_buggy_file)

    return line_mapping_info_dict, line_changes_info_dict, git_blame_lines_orig, buggy_file_lines_orig



def get_commit_ids(project):
    """Finds the commit data for all the bugs for the given defects4j project

    Parameters:
    ----------
    project: str (name of the project)

    Return:
    ------
    commit_ids : dictionary (key:value pair is bug id: buggy version commit id)

    """

    path_to_commit_db = f"{WORKING_DIR}/fault-localization-data/defects4j/framework/projects"
    commit_db_file = os.path.join(path_to_commit_db, project, "commit-db")
    commit_db_data = csv.reader(open(commit_db_file), delimiter=',')
    commit_db_list = list(commit_db_data)
    commit_ids = {commit_id_line[0]: commit_id_line[1] for commit_id_line in commit_db_list}

    return commit_ids


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    """Main function.

    Command to run:
    --------------
    # python3.6 step1d_extract_LineChangeCount_feature.py

    """

    start_time = time.time()
    bug_count = 0

    input_directory = f"{WORKING_DIR}/fault-localization.cs.washington.edu/line_suspiciousness_sorted_Dstar"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found in the working directory")

    output_feature_directory = f"{WORKING_DIR}/output_{FEATURE}"
    if not os.path.exists(output_feature_directory):
        os.mkdir(output_feature_directory)
    else:
        raise ValueError(f"Output directory {output_feature_directory} already exists. "
                         f"Plz backup and delete the directory. Then re-run")

    output_directory = f"{WORKING_DIR}/output_{FEATURE}/step1_{FEATURE}_feature"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError(f"Output directory {output_directory} already exists. "
                         f"Plz backup and delete the directory. Then re-run")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        commit_ids = get_commit_ids(project)
        for bug in bugs:
            input_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp.csv"
            output_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-LineChangeCount.csv"
            extract_line_feature(os.path.join(input_directory, input_csv),
                                   os.path.join(output_directory, output_csv), project, bug, commit_ids[bug])
            bug_count += 1

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / bug_count), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: step1d_extract_LineChangeCount_feature.py")
    print(f"FEATURE SELECTED: {FEATURE}")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    print(f"BUG IDs SELECTED: {PROJECT_BUGS}")
    print(f"\nTOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")

    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")

    total_runtime_minutes = round((total_runtime / 60), 2)
    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes")
    print(f"Average Running Time per Bug : {avg_running_time} seconds")

    print("\n############################ END ############################")
