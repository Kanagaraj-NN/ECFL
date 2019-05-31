import time
from subprocess import check_call


if __name__ == '__main__':

    start_time = time.time()

    print("\n###########################################################")
    print("Coverage Download and DStar Fault Localization Computation")
    print("###########################################################\n")

    check_call("python3.6 1_download_data_from_FL_repo.py", shell=True)
    check_call("python3.6 2_extract_coverage_files.py", shell=True)
    check_call("python 3_compute_suspiciousness.py", shell=True)
    check_call("python 4_stmt_to_line_suspiciousness.py", shell=True)
    check_call("python3.6 5_sort_susp_lines_DStar.py", shell=True)

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    total_runtime_minutes = round((total_runtime / 60), 2)

    print("\n############# COMPLETED RUNNING ALL DSTAR SCRIPTS SUCCESSFULLY #############")
    print("\n############################ SUMMARY ############################")

    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes\n\n")





