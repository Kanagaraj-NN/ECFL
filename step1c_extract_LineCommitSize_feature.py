# ========================================================================================
# IMPORTS AND GLOBAL CONFIGURATIONS
# ========================================================================================

import argparse
import csv
import os
import time

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

# FEATURE = 'LineLength' or or 'LineRecency' or 'LineCommitSize'  or 'LineChangeCount'
FEATURE = 'LineCommitSize'


# ========================================================================================
# FUNCTIONS
# ========================================================================================

def extract_line_feature(input_file, output_file, project_name, bug_id, orig_buggy_commit_id):
    """Extract the line length (number of characters) for every suspicious line

    Parameters
    ----------
    input_file : str (sorted suspicousness lines file)
    output_file: str (sorted suspiciousness lines file with the feature)
    project_name: str (project name)
    bug_id: str (bug id)
    orig_buggy_commit_id: str (Original buggy version commit id, different from Defects4J buggy version)

    Return:
    ------
    line_mapping_time: int (time taken for line mapping from Defects4j buggy version to original buggy version)

    """

    sorted_susp_lines = read_susp_lines_from_file(input_file)

    # Running git checkout buggy_version
    checkout_project_git(project_name, bug_id)
    git_blame_output = f"{WORKING_DIR}/line_mapping_history_slicing/git_blame_{project_name}_{bug_id}"
    line_counter = 1
    # Addding output file header out of the loop
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"susp_line,suspiciousness,{FEATURE}\n")

    # Optimization code. Saving the line mapping per file.
    file_names_seen = set()
    line_mapping_info_per_file = {}
    git_blame_lines_per_file = {}

    # Commit size hash table (optimization)
    commit_id_size_table = {}

    line_mapping_time = 0

    # Loop through every line, do line mapping and extract line length feature
    for susp_line in sorted_susp_lines:
        suspiciousness = round(float(susp_line[-1]), 4)
        susp_line_id = susp_line[0]
        file_name_full, line_number = susp_line[0].split("#")
        line_number = int(line_number)
        file_name = file_name_full.split("/")[-1]

        if file_name not in file_names_seen:
            checkout_project_git_using_tag(project_name, bug_id)
            if project_name == 'Chart':
                line_mapping_info, git_blame_lines, line_mapping_time_per_file = compute_diff_git_blame_lines_svn_Chart(file_name, file_name_full, git_blame_output, orig_buggy_commit_id, project_name, bug_id)
            else:
                line_mapping_info, git_blame_lines, line_mapping_time_per_file = compute_diff_git_blame_lines(file_name, file_name_full, git_blame_output, orig_buggy_commit_id)
            file_names_seen.add(file_name)
            line_mapping_info_per_file[file_name] = line_mapping_info
            git_blame_lines_per_file[file_name] = git_blame_lines
            line_mapping_time += line_mapping_time_per_file

        else:
            line_mapping_info = line_mapping_info_per_file[file_name]
            git_blame_lines = git_blame_lines_per_file[file_name]

        if line_mapping_info:   # If the diff is non empty, then take the correct line number from the mapping
            line_number = line_mapping_info[line_number]

        if line_number in git_blame_lines:
            blame_line = git_blame_lines[line_number] # Picking the line
            if project_name == 'Chart':
                line_commit_id = extract_line_commit_id_svn_Chart(blame_line[0])
                if line_commit_id in commit_id_size_table:
                    line_commit_size = commit_id_size_table[line_commit_id]
                else:
                    line_commit_size = find_commit_size_svn_Chart(line_commit_id, project)
                    commit_id_size_table[line_commit_id] = line_commit_size  # storing in hashtable
            else:
                line_commit_id = extract_line_commit_id(blame_line[0])
                if line_commit_id in commit_id_size_table:
                    line_commit_size = commit_id_size_table[line_commit_id]
                else:
                    line_commit_size = find_commit_size(line_commit_id, project)
                    commit_id_size_table[line_commit_id] = line_commit_size  # storing in hashtable

            add_susp_data_to_file(output_file,susp_line_id,suspiciousness,line_commit_size)

        line_counter += 1

    return line_mapping_time


def add_susp_data_to_file(output_file, susp_line_id, suspiciousness, line_recency):
    """Adds LineLength feature to the sorted suspiciousness file

    Parameters:
    ----------
    output_file: str
    susp_line_id: int
    suspiciousness: float
    LineLength: int

    """

    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line_id},{suspiciousness},{line_recency}\n")


def read_susp_lines_from_file(input_file):
    """Reads the suspiciousness lines data from the sorted suspiciousness file

    Parameters:
    ----------
    input_file: str

    Return:
    ------
    sorted_susp_lines: list (Top 100 DStar susp lines)

    """

    top_n_lines = 100
    susp_data = csv.reader(open(input_file), delimiter=',')
    sorted_susp_lines = []

    for i, susp_line in enumerate(susp_data):
        if i > top_n_lines:
            break
        sorted_susp_lines.append(susp_line)

    return sorted_susp_lines[1:]    # Skip header


def checkout_project_git_using_tag(project, bug):
    """Checkout to the Defects4j buggy version

    Parameters:
    ----------
    project: str
    bug: str
    """

    commit_tag = f"D4J_{project}_{bug}_BUGGY_VERSION"
    os.system(f"git checkout {commit_tag}")


def checkout_project_git(project, bug):
    """Checkout to the project using git commands

    Parameters:
    ----------
    project: str
    bug: str
    """

    checkout_directory = f"/tmp/{project}_{bug}_buggy_ver"
    command_git_checkout = f"defects4j checkout -p {project} -v {bug}b -w {checkout_directory}"
    os.system(command_git_checkout)
    os.chdir(checkout_directory)


def extract_line_commit_id(blame_line):
    """Parses the line and extract the line commit id

    Parameters:
    ----------
    line: str (line from the git blame output file)

    Return:
    -------
    line_commit_id: int

    """

    # git blame line:
    #    ^61b319c (John 2019-02-10 20:49:59 -0800  135) a = start + 2;


    line = blame_line
    line_commit_id = line[: line.find(" ")]
    name_start_index = line.find("(") + 1

    author = ""
    i = name_start_index
    while not (line[i].isdigit() and line[i+1].isdigit() and line[i+2].isdigit() and line[i+3].isdigit()) :
        author += line[i]
        i += 1

    author = author.strip()     # removing sorrounding white spaces
    date = "".join([line[indx] for indx in range(i, i+10)])

    i += 10
    while line[i] != ")":
        i += 1

    i += 1  # Skipping the last bracket

    line = line[i:].strip()
    i = 0
    while i < len(line):
        i += 1

    line_len_counter = i

    return line_commit_id


def find_commit_size(line_commit_id, project):
    """Finds the commit size as number of additions
    """
    commit_size_output_file = f"/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/Git_blame_output/{project}_temp_file.txt"
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

    line_commit_size = int(git_commit_size_line[(start_index + 1):end_index].strip())
    os.remove(commit_size_output_file)
    return line_commit_size


def extract_line_commit_id_svn_Chart(blame_line):
    """Parses the line and extract the line commit id

    Parameters:
    ----------
    line: str (line from the git blame output file)

    Return:
    -------
    line_commit_id: int

    """

    # svn blame line:
    #       1    mungady 2007-06-19 05:39:34 -0400 (Tue, 19 Jun 2007) import org.jfree.chart.LegendItem;

    line = blame_line

    i = 0
    while i < len(line):
        if line[i].isalpha():
            break
        i += 1

    line_commit_id = line[:i].strip()

    author_name_start_index = i
    while i < len(line):
        if line[i].isdigit() and line[i - 1] == ' ':
            break
        i += 1

    author = line[author_name_start_index: i].strip()

    date = line[i: i+10]

    i += 10
    while i < len(line):
        if line[i] == ')':
            break
        i += 1

    line_content = line[i+1 :].strip()
    line_length = len(line_content)

    return line_commit_id


def find_commit_size_svn_Chart(line_commit_id, project):
    """Finds the commit size as number of additions
    """

    commit_size_output_file = f"/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/Git_blame_output/{project}_temp_file.txt"
    # os.system(f"git show {line_commit_id} --shortstat > {commit_size_output_file}")
    os.system(f"svn log -r{line_commit_id} > {commit_size_output_file}")
    output_lines = csv.reader(open(commit_size_output_file, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_new = list(output_lines)

    # Bug fix for ^adl2232 (commit id starts with carret)
    if not git_blame_lines_new or len(git_blame_lines_new) < 2:
        return 0

    # print(git_blame_lines_new[-1])
    # [' 2 files changed, 165 insertions(+), 74 deletions(-)']

    changed_lines_count = git_blame_lines_new[1][0].split('|')[-1].strip()
    count_size = []
    for c in changed_lines_count:
        if c.isdigit():
            count_size.append(c)
        else:
            break

    line_commit_size = int("".join(count_size))

    os.remove(commit_size_output_file)
    return line_commit_size




def find_file_path(file_name, susp_file_path):
    """Find the full path of the given file

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


def extract_git_blame_lines(file_name, susp_file_path, git_blame_output):
    """Run git blame on the given file and return the git blame lines

    Parameters:
    ----------
    file_name: str (file name passed to git blame command)
    susp_file_path: str (file path in the suspiciousness output)
    git_blame_output : str (output file where git blame command output is dumped)

    """
    file_path = find_file_path(file_name, susp_file_path)
    os.system(f"git blame {file_path} > {git_blame_output}")
    git_blame_data = csv.reader(open(git_blame_output, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_list =  list(git_blame_data)
    git_blame_lines = {(i+1):git_blame_list[i] for i in range(len(git_blame_list))}

    return git_blame_lines


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
    line_mapping_time_taken: float (time taken in seconds for this function)

    """

    start_time = time.time()

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
        line_mapping_time_taken = round((end_time - start_time), 4)
        return None, git_blame_lines_orig, line_mapping_time_taken

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

    end_time = time.time()
    line_mapping_time_taken = round((end_time - start_time), 4)

    return line_mapping_info, git_blame_lines_orig, line_mapping_time_taken


def compute_diff_git_blame_lines_svn_Chart(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version, project, bug):
    """Line mapping code

    Parameters:
    ----------
    file_name: str (file name of susp line)
    file_name_full: str (full file path of susp line)
    git_blame_output : str (output file where git blame command output is dumped)
    commit_id_original_buggy_version: str (Original buggy version commit id, different from Defects4J buggy version)
    project: str
    bug: str

    Return:
    -------
    line_mapping_info: dictionary (key: value pair is Defects4J_buggy_line_id: Original_buggy_line_id)
    git_blame_lines_orig: dictionary
        (key: value pair is Original_buggy_line_id: git blame line with all details such as line content, data modified)
    line_mapping_time_taken: float (time taken in seconds for this function)

    """

    start_time = time.time()

    file_path = find_file_path(file_name, file_name_full)
    os.system(f"git blame {file_path} > {git_blame_output}")

    defects4j_buggy_file = git_blame_output + "_defects4j_buggy_file"
    os.system(f"cat {file_path} > {defects4j_buggy_file}")

    d4j_home = os.environ['D4J_HOME']   # Accessing environment variable, echo $D4J_HOME
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

    # if the diff is empty, no need of line mapping
    if os.stat(diff_output).st_size == 0:
        # Removing unnecessary files after use
        os.remove(defects4j_buggy_file)
        os.remove(git_blame_output_orig)
        os.remove(git_blame_output)
        os.remove(git_blame_diff)
        os.remove(diff_output)
        os.remove(original_buggy_file)

        end_time = time.time()
        line_mapping_time_taken = round((end_time - start_time), 4)

        return None, git_blame_lines_orig, line_mapping_time_taken

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

    end_time = time.time()
    line_mapping_time_taken = round((end_time - start_time), 4)

    return line_mapping_info, git_blame_lines_orig, line_mapping_time_taken


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
    commit_ids = {commit_id_line[0]:commit_id_line[1] for commit_id_line in commit_db_list}

    return commit_ids


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    """Main function.
    
    Command to run:
    --------------
    # python3.6 step1c_extract_LineCommitSize_feature.py
    
    """

    start_time = time.time()
    line_mapping_time = 0
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
            output_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}.csv"
            # Call the extract feature function
            line_mapping_time_per_bug = extract_line_feature(os.path.join(input_directory, input_csv),
                                                             os.path.join(output_directory, output_csv), project, bug, commit_ids[bug])
            line_mapping_time += line_mapping_time_per_bug
            bug_count += 1

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    total_runtime_excluding_line_mapping = total_runtime - line_mapping_time
    total_runtime_excluding_line_mapping = round(total_runtime_excluding_line_mapping, 4)
    avg_running_time_with_line_mapping = round(total_runtime / bug_count, 2)
    avg_running_time = round(total_runtime_excluding_line_mapping / bug_count, 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: step1c_extract_LineCommitSize_feature.py")
    print(f"FEATURE SELECTED: {FEATURE}")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    print(f"BUG IDs SELECTED: {PROJECT_BUGS}")
    print(f"\nTOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")

    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")

    total_runtime_minutes = round((total_runtime / 60), 2)
    total_runtime_minutes_wo_line_mapping = round((total_runtime_excluding_line_mapping / 60), 2)
    print(f"\nTotal Running Time (with line mapping): {total_runtime} seconds => {total_runtime_minutes} minutes")
    print(f"Total Running Time (without line mapping): {total_runtime_excluding_line_mapping} seconds => {total_runtime_minutes_wo_line_mapping} minutes")
    print(f"\nAvg Running Time per Bug (with mapping): {avg_running_time_with_line_mapping} seconds")
    print(f"Avg Running Time per Bug (without line mapping): {avg_running_time} seconds")

    print("\n############################ END ############################")
