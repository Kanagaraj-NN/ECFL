import time
from subprocess import check_call


if __name__ == '__main__':

    start_time = time.time()

    print("\n###########################################################")
    print("ECFL Computation and Evaluation")
    print("###########################################################\n")

    check_call("python3.6 step1a_extract_LineLength_feature.py", shell=True)
    check_call("python3.6 step1b_extract_LineRecency_feature.py", shell=True)
    check_call("python3.6 step1c_extract_LineCommitSize_feature.py", shell=True)
    check_call("python3.6 step1d_extract_LineChangeCount_feature.py", shell=True)
    check_call("python3.6 step2_compute_normalized_feature.py", shell=True)
    check_call("python3.6 step3_compute_weighted_sum.py", shell=True)
    check_call("python3.6 step4_compute_output_rank_ECFL.py", shell=True)
    check_call("python3.6 step5_evaluate_DStar_ECFL_using_TopN.py", shell=True)

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    total_runtime_minutes = round((total_runtime / 60), 2)

    print("\n############# COMPLETED RUNNING ALL ECFL SCRIPTS SUCCESSFULLY #############")
    print("\n############################ SUMMARY ############################")

    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes\n\n")





