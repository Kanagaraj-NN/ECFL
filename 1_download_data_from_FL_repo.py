# Script to download the required Fault Localization coverage data for 395 bugs
# from the following repository.

#  https://bitbucket.org/rjust/fault-localization-data/src/master/ (dataset code and scripts)
#  http://fault-localization.cs.washington.edu/         (contains info about data)
#  http://fault-localization.cs.washington.edu/data/    (data)
#  http://fault-localization.cs.washington.edu/data/Lang/1/gzoltar-files.tar.gz (sample file name)


# ========================================================================================
# IMPORTS AND GLOBAL CONFIGURATIONS
# ========================================================================================


import time
import os
from subprocess import check_call

PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']

PROJECT_BUGS = [
    [str(x) for x in range(1, 134)],      # Closure
    [str(x) for x in range(1, 66)],       # Lang
    [str(x) for x in range(1, 27)],       # Chart
    [str(x) for x in range(1, 107)],      # Math
    [str(x) for x in range(1, 39)],       # Mockito
    [str(x) for x in range(1, 28)]        # Time
]

WORKING_DIR = os.path.abspath('')

# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    start_time = time.time()
    bug_count = 0

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            check_call(f"wget --recursive --no-parent http://fault-localization.cs.washington.edu/data/{project}/{bug}/gzoltar-files.tar.gz", shell=True)
            bug_count += 1
            print(f"===== bug_count : {bug_count} =====")

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / bug_count), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: 1_download_data_from_FL_repo.py")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    print(f"TOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")

    print(f"\nOUTPUT DIRECTORY: {WORKING_DIR}/fault-localization.cs.washington.edu/data")

    total_runtime_minutes = round((total_runtime / 60), 2)
    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes")
    print(f"Average Running Time per Bug : {avg_running_time} seconds")

    print("\n############################ END ############################")
