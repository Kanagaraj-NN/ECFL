import csv
import os

# PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Time']
# PROJECTS = ['Lang']

# PROJECT_BUGS = [
#     [str(x) for x in range(1, 134)],      # Closure
#     [str(x) for x in range(1, 66)],       # Lang
#     [str(x) for x in range(1, 27)],       # Chart
#     [str(x) for x in range(1, 107)],      # Math
#     [str(x) for x in range(1, 39)],       # Mockito
#     [str(x) for x in range(1, 28)]        # Time
# ]

PROJECT_BUGS = [
    [str(x) for x in range(1, 134)],      # Closure
    [str(x) for x in range(1, 66)],       # Lang
    [str(x) for x in range(1, 27)],       # Chart
    [str(x) for x in range(1, 107)],      # Math
    [str(x) for x in range(1, 28)]        # Time
]

# PROJECT_BUGS = [
#      [str(x) for x in range(1, 2)]       # Lang
#      ]


FL_TECHNIQUE = 'dstar2'          # Fault Localization (FL) Technique : DStar
WORKING_DIR = os.path.abspath('')

# FEATURE = 'LineLength' or 'LineRecency' or 'LineCommitSize' or 'LineChangeCount'
FEATURE = 'LineLength'


# ========================================================================================
# FUNCTIONS
# ========================================================================================

def convert_csv_to_json_format(input_file, output_file):
    """
    Converts CSV to JSON format

    Parameters
    ----------
    input_file : str (file contains normalized feature)
    output_file: str (output json file)

    """

    sorted_susp_lines = read_susp_lines_from_file(input_file)

    with open(output_file, mode="a", encoding="utf-8") as myFile:
        for i, susp_line in enumerate(sorted_susp_lines):
            line_id = susp_line[0]
            line_id_parts = line_id.split('#')
            line_id_path = line_id_parts[0]
            line_id_number = line_id_parts[1]
            line_id_path = line_id_path.replace('/', '.')
            line_path = line_id_path.replace('.java', '')
            feature = susp_line[-1]
            myFile.write(f'\t\t"{line_path}:{line_id_number}": ')
            myFile.write("{\n")
            myFile.write(f'\t\t\t"{FEATURE}": {feature}\n')
            if i == len(sorted_susp_lines) - 1:
                myFile.write('\t\t}\n')
            else:
                myFile.write('\t\t},\n')


def read_susp_lines_from_file(input_file):
    """
    Reads the suspiciousness lines data from the sorted suspiciousness file

    Parameters:
    ----------
    input_file: str

    Return:
    ------
    sorted_susp_lines: list (2D)

    """
    susp_data = csv.reader(open(input_file), delimiter=',')
    sorted_susp_lines = [susp_line for susp_line in susp_data]

    return sorted_susp_lines[1:]  # skip the header


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':
    """Main function.

    Command to run:
    --------------
    # python3.6 convert_feature_csv_to_json_format.py

    """

    bug_counter = 0

    input_directory = f"{WORKING_DIR}/output_{FEATURE}/step2_{FEATURE}_normalized"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found. "
                         "Plz run the previous step with correct feature configured. "
                         "Then re-run this step")

    output_directory = f"{WORKING_DIR}/output_{FEATURE}/{FEATURE}_json"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError(f"Output directory {output_directory} already exists. "
                         f"Plz backup and delete the directory. Then re-run")

    output_file_name = f"{FEATURE}_feature_top_100.json"
    output_file = os.path.join(output_directory, output_file_name)

    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write("{\n\t")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug_count, bug in enumerate(bugs):
            with open(output_file, mode="a", encoding="utf-8") as myFile:
                myFile.write(f'"{project.lower()+bug}": ')
                myFile.write("{\n")
            # Closure-1-dstar2-sorted-susp-LineLength-normalized.csv
            input_csv = f"{project}-{bug}-{FL_TECHNIQUE}-sorted-susp-{FEATURE}-normalized.csv"
            convert_csv_to_json_format(os.path.join(input_directory, input_csv), output_file)
            with open(output_file, mode="a", encoding="utf-8") as myFile:
                if bug_count != len(bugs) - 1:
                    myFile.write('\t},\n')
                else:
                    if project == 'Time':       # Time is the last project
                        myFile.write('\t}\n')
                    else:
                        myFile.write('\t},\n')
                myFile.write("\t")
            bug_counter += 1

    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write("\n}")

    print("\n\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: convert_feature_csv_to_json_format.py")
    print(f"FEATURE SELECTED: {FEATURE}")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    # print(f"BUG IDs SELECTED: {PROJECT_BUGS}")
    print(f"\nTOTAL NUMBER OF BUGS SELECTED: {bug_counter}\n")
    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")

    print("\n############################ END ############################")