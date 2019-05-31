import tarfile
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

WORKING_DIR = os.path.abspath('')
TAR_FILE = 'gzoltar-files.tar.gz'


def extract_files(data_dir, output_dir):
    """
    Extract tar gz files from data directory to get coverage and spectra files

    Parameters
    ----------
    data_dir : str
        the main data directory which holds all projects

    output_dir : str
        the output directory to write coverage and spectra files to
        this directory must exist

    Returns
    -------
    None
    """

    bug_counter = 0
    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            tar = os.path.join(data_dir, project, bug, TAR_FILE)
            coverage, spectra = extract_tar_file(tar)
            if coverage is None or spectra is None:
                # print('Could not get coverage/spectra for %s' % tar)
                print(f"Could not get coverage/spectra for {tar}")
            else:
                # coverage_file = os.path.join(output_dir, '%s-%s-%s' % (project, bug, 'coverage'))
                coverage_file = os.path.join(output_dir, f"{project}-{bug}-coverage")
                spectra_file = os.path.join(output_dir, f"{project}-{bug}-spectra")
                # spectra_file = os.path.join(output_dir, '%s-%s-%s' % (project, bug, 'spectra'))
                write_file(coverage_file, coverage)
                write_file(spectra_file, spectra)

                bug_counter += 1
                print(f"===== bug_count : {bug_counter} =====")



def extract_tar_file(tar):
    """
    Extract a tar file and return the matrix and spectra content

    Parameters
    ----------
    tar : str
        the path to the tarfile

    Returns
    tuple(str, str)
        the contents of the coverage matrix and spectra
    """
    coverage, spectra = None, None
    tar = tarfile.open(tar)
    for member in tar.getmembers():
        if 'matrix' in member.get_info()['name']:
            f = tar.extractfile(member)
            if f is not None:
                coverage = f.read()
        if 'spectra' in member.get_info()['name']:
            f = tar.extractfile(member)
            if f is not None:
                spectra = f.read()
    return coverage, spectra


def write_file(filename, content):
    """
    Write content to the given filename

    Parameters
    ----------
    filename : str
    content : str
    """
    with open(filename, 'wb') as fwriter:
        fwriter.write(content)


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    start_time = time.time()

    input_directory = f"{WORKING_DIR}/fault-localization.cs.washington.edu/data"
    if not os.path.exists(input_directory):
        raise ValueError(f"Input directory {input_directory} is not found. "
                         "Plz run the previous step. "
                         "Then re-run this step")

    output_directory = f"{WORKING_DIR}/fault-localization.cs.washington.edu/coverage"
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError(f"Output directory {output_directory} already exists. "
                         f"Plz backup and delete the directory. Then re-run")

    extract_files(input_directory, output_directory)

    bug_count = 0
    for bugs in PROJECT_BUGS:
        for bug in bugs:
            bug_count += 1

    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / bug_count), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print(f"\nSCRIPT NAME: 2_extract_coverage_files.py")
    print(f"PROJECTS SELECTED: {PROJECTS}")
    print(f"TOTAL NUMBER OF BUGS SELECTED: {bug_count}\n")

    print(f"INPUT DIRECTORY: {input_directory}")
    print(f"OUTPUT DIRECTORY: {output_directory}")

    total_runtime_minutes = round((total_runtime / 60), 2)
    print(f"\nTotal Running Time : {total_runtime} seconds => {total_runtime_minutes} minutes")
    print(f"Average Running Time per Bug : {avg_running_time} seconds")

    print("\n############################ END ############################")
