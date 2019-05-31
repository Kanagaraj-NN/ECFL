import csv
import operator
import os
import time

PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
PROJECT_BUGS = [
    [str(x) for x in range(1, 134)],
    [str(x) for x in range(1, 66)],
    [str(x) for x in range(1, 27)],
    [str(x) for x in range(1, 107)],
    [str(x) for x in range(1, 39)],
    [str(x) for x in range(1, 28)]
]

FL_TECHNIQUE = 'dstar2'
WORKING_DIR = os.path.abspath('')


def sort(input_csv, output_csv, column=1):
    """
    Sort a csv based on a column

    Parameters
    ----------
    input_csv : str
        input csv file
    output_csv : str
        output csv file
    column : int
        the column number to sort the input csv file on
    """
    data = csv.reader(open(input_csv), delimiter=',')
    sortedlist = sorted(data, key=operator.itemgetter(column))
    sortedlist.reverse()

    with open(output_csv, 'w') as f:
        fileWriter = csv.writer(f, delimiter=',')
        for row in sortedlist:
            fileWriter.writerow(row)


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    start_time = time.time()

    input_directory = f"{WORKING_DIR}/fault-localization.cs.washington.edu/line_suspiciousness"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found. "
                         "Plz run the previous step. "
                         "Then re-run this step")

    output_directory = f"{WORKING_DIR}/fault-localization.cs.washington.edu/line_suspiciousness_sorted_Dstar"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError(f"Output directory {output_directory} already exists. "
                         f"Plz backup and delete the directory. Then re-run")


    bug_count = 0
    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            input_csv = '%s-%s-%s-line-suspiciousness' % (project, bug, FL_TECHNIQUE)
            output_csv = '%s-%s-%s-sorted-susp.csv' % (project, bug, FL_TECHNIQUE)
            sort(os.path.join(input_directory, input_csv),
                 os.path.join(output_directory, output_csv))
            bug_count += 1
            print(f"===== bug_count : {bug_count} =====")

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / 395), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")
    print(f"\nSCRIPT NAME: 5_sort_susp_lines_DStar.py")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    print(f"TOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")

    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")

    total_runtime_minutes = round((total_runtime / 60), 2)
    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes")
    print(f"Average Running Time per Bug : {avg_running_time} seconds")

    print("\n############################ END ############################")