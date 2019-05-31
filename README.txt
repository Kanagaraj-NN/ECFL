#############################################
Enhanced Cost-aware Fault Localization (ECFL)
#############################################


A short background about the project:
====================================
1) The title of the project is Enhanced Cost-aware Fault Localization (ECFL).
2) ECFL Combines line level source code features
   such as line length, line recency, line commit size and line change count
   with the DStar SBFL technique.
3) The goal of the project is to improve the existing best accuracy cost-aware
   fault localization technique by combining source code line features.


Replication Instructions:
=========================
1) Follow all the steps in order.
2) All the scripts are run inside the "ecfl" folder.
    # $ANY_DIRECTORY/ecfl


Prerequisite Tools:
===================
Install or verify all the following dependencies before proceeding further:

    # Python 3.6 or greater (ECFL scripts)
    # Python 2.7 or Python 2.x (FL scripts)
    # Java 1.7 (Defects4J)
    # Git >= 1.9 (Defects4J)
    # SVN >= 1.8 (Defects4J)
    # Perl >= 5.0.10 (Defects4J)



PART 1: (ECFL setup)
====================
1) Clone and setup ECFL bitbucket repository

    # Get the git clone link from the URL: https://bitbucket.org/sealabvt/ecfl/src
    # In the "ecfl" directory, execute git clone "link"
        For example:
        # git clone https://kanagarajnn@bitbucket.org/sealabvt/ecfl.git
        # (username will be different for you)
    # After the git clone, a directory named "fault-localization-data" will be created in "ecfl"
    # cd ecfl

2) Verify the contents of the "ecfl" folder

    "ecfl" folder contains the following items

    Documentation file (Instructions to run):
    =========================================
    # 0_README.txt (this file)

    Main Python script files:
    ========================
    # 0_execute_all_scripts_main.py
    # 0_execute_all_DStar_scripts.py
    # 0_execute_all_ECFL_scripts.py

    Python script files (Coverage Download and DStar Fault Localization Computation):
    =================================================================================
    # 1_download_data_from_FL_repo.py
    # 2_extract_coverage_files.py
    # 3_compute_suspiciousness.py
    # 4_stmt_to_line_suspiciousness.py
    # 5_sort_susp_lines_DStar.py

    Python script files (ECFL and Evaluation):
    =========================================
    # step1a_extract_LineLength_feature.py
    # step1b_extract_LineRecency_feature.py
    # step1c_extract_LineCommitSize_feature.py
    # step1d_extract_LineChangeCount_feature.py
    # step2_compute_normalized_feature.py
    # step3_compute_weighted_sum.py
    # step4_compute_output_rank_ECFL.py
    # step5_evaluate_DStar_ECFL_using_TopN.py

    ECFL line mapping jar executables (ECFL dependency files):
    =========================================================
    # line_mapping_history_slicing (folder)
        # RunDiffProcessor_1.jar
        # RunDiffProcessor_2.jar
        # HistorySlicingFuzzy.properties



Part 2: Fault Localization and Defects4J dataset setup
======================================================
1) Clone and setup Fault Localization bitbucket repository provided by Pearson et al. [1] by following the installation steps
   provided below.

    # Get the git clone link from the URL: https://bitbucket.org/rjust/fault-localization-data/src/master/
    # In the ecfl directory, execute git clone "link"
        For example:
        # git clone https://kanagarajnn@bitbucket.org/rjust/fault-localization-data.git
        # (username will be different for you)
    # After the git clone, a directory named "fault-localization-data" will be created in ecfl
    # cd fault-localization-data
    # Execute the following installation script in the directory "fault-localization-data"
        # ./setup.sh
				This script will clone, install and configure the right Defects4j repository (v1.1.0).
			commit id: 7fe984602110d12408643daee76bb43f367ee70a
		# source ~/.bashrc
				This command is run to update the bash shell settings

2) After installation, verify the installation

    # defects4j info -p Lang
        This command will provide details about the defects4j Lang project along with the defects4j directories
	# cd ..
		This command will take back to the parent directory (working directory: "ecfl")



PART 3: Coverage Download and DStar Fault Localization Computation
==================================================================

Option 1: Execute all scripts using a single script
****************************************************
    # python3.6 0_execute_all_DStar_scripts.py (Will run all the DStar scripts)
    # python3.6 0_execute_all_scripts.py (Will run all the DStar anad ECFL scripts)


Option 2: Execute each script one by one
*****************************************

	Each script depends on the output of the previous script. So run in order.

1) Download Coverage data from the repository [2]

    # Coverage information consists of matrix and spectra files for each fault (zipped files)
    # Follow either option 1 or option 2 (from ecfl directory)
        # Option 1: Download the coverage files for only real faults (395 real faults)
            # python3.6 1_download_data_from_FL_repo.py
        # Option 2: Download the coverage files for all faults (395 real faults + 3242 artifical faults)
            # wget --recursive --no-parent --accept gzoltar-files.tar.gz http://fault-localization.cs.washington.edu/data

2) Extract the coverage files (matrix and spectra) from the zipped files
    # python3.6 2_extract_coverage_files.py

3) Compute the suspiciousness scores for DStar Fault Localiztion technique
    # python 3_compute_suspiciousness.py

4) Covert statement suspiciousness scores to line suspiciousness scores
    # python 4_stmt_to_line_suspiciousness.py

5) Sort the lines by suspiciousness scores
    # python3.6 5_sort_susp_lines_DStar.py



PART 4: ECFL Computation and Evaluation
=======================================
IMPORTANT NOTES:
===============
# Step1 (1a, 1b, 1c, 1d) is different for each feature and other remaining steps (2, 3, 4 and 5) are same for all features.
# Some configurations such as PROJECTS, PROJECT_BUGS, WEIGHT_PAIRS, FEATURE, TOP_N are present inside the scripts in the top section.
# Default configuration parameters are as follows (395 bugs)
    # PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
    # PROJECT_BUGS = [
                        [str(x) for x in range(1, 134)],      # Closure
                        [str(x) for x in range(1, 66)],       # Lang
                        [str(x) for x in range(1, 27)],       # Chart
                        [str(x) for x in range(1, 107)],      # Math
                        [str(x) for x in range(1, 39)],       # Mockito
                        [str(x) for x in range(1, 28)]        # Time
                      ]
    # WEIGHT_PAIRS = [(0.8, 0.2)]
    # FEATURE = 'LineLength'
    # TOP_N = 1
# Configurations can be changed based on the need
# Each step creates an output folder and stores the intermediate results that will be used for the next step
# Last step (step5) creates a the final output folder containing the evaluation results



STEPS TO RUN:
============

    There are five python scripts to be run in order.

1) step1a_extract_LineLength_feature.py (or other features such as step1b_*, step1c_* or step1d_*)
2) step2_compute_normalized_feature.py
3) step3_compute_weighted_DStar_LineLength.py
4) step4_compute_output_rank_ECFL.py
5) step5_evaluate_DStar_ECFL_using_TopN.py


INSTRUCTIONS ON HOW TO RUN
===========================

Option 1: Execute all scripts using a single script
***************************************************
    # python3.6 0_execute_all_ECFL_scripts.py
        This will execute with the default configurations in each script.
        Before running this script, make changes to configuration to individual scripts as needed

Option 2: Execute each script one by one
*****************************************
    # Before running every script, make changes to configuration as needed
    # Each script depends on the output of the previous script
    # If you want to run same script again, old output folder should be backed up or removed (if not required)

1) Source Code Feature Extraction:
==================================
    # Script Name: step1a_extract_LineLength_feature.py  (or other features such as step1b_*, step1c_* or step1d_*)

    Command to run:
    --------------
    # python3.6 step1a_extract_LineLength_feature.py

    Input directory: $WORKING_DIR/fault-localization.cs.washington.edu/line_suspiciousness_sorted_Dstar
    Output directory: $WORKING_DIR/output_LineLength/step1_LineLength_feature

    Note:
    -----
    $WORKING_DIR = ANY_DIRECTORY/ecfl


2) Normalization of the Feature using Min-Max normalization (0 to 1):
=====================================================================
    # Script Name: step2_compute_normalized_LineLength.py

    Command to run:
    --------------
    # python3.6 step2_compute_normalized_feature.py

    Input directory: $WORKING_DIR/output_LineLength/step1_LineLength_feature
    Output directory: $WORKING_DIR/output_LineLength/step2_LineLength_normalized


3) Combining DStar and ECFL using Weighted Sum
==============================================
    # Script Name: step3_compute_weighted_sum.py

    Command to run:
    --------------
    # python3.6 step3_compute_weighted_sum.py

    Input directory: $WORKING_DIR/output_LineLength/step2_LineLength_normalized
    Output directory: $WORKING_DIR/output_LineLength/step3_LineLength_weighted


4) Computation of Ranks based on New Weighted Scores
====================================================
    # Script Name: step4_compute_output_rank_ECFL.py

    Command to run:
    --------------
    # python3.6 step4_compute_output_rank_ECFL.py

    Input directory: $WORKING_DIR/output_LineLength/step3_LineLength_weighted
    Output directory: $WORKING_DIR/output_LineLength/step4_LineLength_ranked


5) Evaluation of DStar and ECFL using Top-N using Ground Truth
===============================================================
    # Script Name:  step5_evaluate_DStar_ECFL_using_TopN.py

    Command to run:
    --------------
    # python3.6 step5_evaluate_DStar_ECFL_using_TopN.py

    Input directory: $WORKING_DIR/output_LineLength/step4_LineLength_ranked
    Buggy_lines directory: $WORKING_DIR/buggy_lines
        - A directory that contains buggy lines for all bugs (ground truth)
    Ouput directory: $WORKING_DIR/output_LineLength/step5_LineLength_results

    Default configuration:
    ----------------------
    # TOP_N = 1   (Can be set as 1, 3, 5, or 10)










References:
============
Fault Localization data source:
===============================
[1] Spencer Pearson, Jose Campos, Rene Just, Gordon Fraser, Rui Abreu, Michael D. Ernst, Deric Pang, and Benjamin Keller. 2017.
    Evaluating and improving fault localization.
    In Proceedings of the 39th International Conference on Software Engineering (ICSE '17).
    IEEE Press, Piscataway, NJ, USA, 609-620.

    Data and Scripts Repository:
    ============================
    https://bitbucket.org/rjust/fault-localization-data/src/master/

[2] http://fault-localization.cs.washington.edu/


