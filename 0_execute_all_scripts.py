import time
from subprocess import check_call


if __name__ == '__main__':

    start_time = time.time()

    check_call("python3.6 0_execute_all_DStar_scripts.py", shell=True)
    check_call("python3.6 0_execute_all_ECFL_scripts.py", shell=True)

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    total_runtime_minutes = round((total_runtime / 60), 2)

    print("\n############# COMPLETED RUNNING ALL SCRIPTS SUCCESSFULLY #############")
    print("\n############################ SUMMARY ############################")

    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes\n\n")





