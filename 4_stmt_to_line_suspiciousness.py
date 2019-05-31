# Download the following directory
# https://bitbucket.org/rjust/fault-localization-data/src/master/analysis/pipeline-scripts/source-code-lines.tar.gz
# wget https://bitbucket.org/rjust/fault-localization-data/src/master/analysis/pipeline-scripts/source-code-lines.tar.gz

import csv
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

SOURCE_CODE_SUFFIX = '.source-code.lines'
FORMULA = {'dstar2'}
FL_TECHNIQUE = 'dstar2'
WORKING_DIR = os.path.abspath('')


def classname_to_filename(classname):
    """
    Convert classname to filename

    Parameters
    ----------
    classname : str
        the value from of the classname from suspiciouss spectra file

    Returns
    -------
    str
        filename
    """
    if '$' in classname:
        classname = classname[:classname.find('$')]
    return classname.replace('.', '/') + '.java'


def stmt_to_line(statement):
    """
    Convert statement to line

    Parameters
    ----------
    statement : str
        the statement number along with the classname

    Returns
    -------
    str
        line number in file
    """
    classname, line_number = statement.rsplit('#', 1)
    return '{}#{}'.format(classname_to_filename(classname), line_number)


def convert_statement_to_line(source_code_lines_file, statement_suspiciousness, output_file):
    source_code = dict()
    with open(source_code_lines_file) as f:
        for line in f:
            line = line.strip()
            entry = line.split(':')
            key = entry[0]
            if key in source_code:
                source_code[key].append(entry[1])
            else:
                source_code[key] = []
                source_code[key].append(entry[1])

    with open(statement_suspiciousness) as fin:
        reader = csv.DictReader(fin)
        with open(output_file, 'w') as f:
            writer = csv.DictWriter(f, ['Line', 'Suspiciousness'])
            writer.writeheader()
            for row in reader:
                line = stmt_to_line(row['Statement'])
                susps = row['Suspiciousness']

                writer.writerow({
                    'Line': line,
                    'Suspiciousness': susps})

                # check whether there are any sub-lines
                if line in source_code:
                    for additional_line in source_code[line]:
                        writer.writerow({'Line': additional_line, 'Suspiciousness': susps})
        f.close()
    fin.close()


# ========================================================================================
# MAIN
# ========================================================================================

if __name__ == '__main__':

    start_time = time.time()

    input_directory = "%s/fault-localization.cs.washington.edu/stmt_suspiciousness" % WORKING_DIR
    if not os.path.exists(input_directory):
        raise ValueError("Input directory %s is not found. "
                         "Plz run the previous step. "
                         "Then re-run this step" % input_directory)

    input_dir_source_code_lines = "%s/fault-localization-data/analysis/pipeline-scripts/source-code-lines" % WORKING_DIR
    if not os.path.exists(input_dir_source_code_lines):
        raise ValueError("Input source code lines directory %s is not found. "
                         "Plz run the previous step. "
                         "Then re-run this step" % input_dir_source_code_lines)


    output_directory = "%s/fault-localization.cs.washington.edu/line_suspiciousness" % WORKING_DIR
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError("Output directory %s already exists. "
                         "Plz backup and delete the directory. Then re-run" % output_directory)



    bug_count = 0
    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            source_code_lines_file = os.path.join(input_dir_source_code_lines,
                                                  '%s-%sb%s' % (project, bug, SOURCE_CODE_SUFFIX))

            statement_suspiciousness_file = os.path.join(input_directory,
                                                         '%s-%s-%s-suspiciousness' % (project, bug, FL_TECHNIQUE))
            output_file = os.path.join(output_directory,
                                       '%s-%s-%s-line-suspiciousness' % (project, bug, FL_TECHNIQUE))
            convert_statement_to_line(source_code_lines_file, statement_suspiciousness_file, output_file)

            bug_count += 1
            print("===== bug_count : %s =====" % bug_count)


    end_time = time.time()
    total_runtime = round((end_time - start_time), 4)
    avg_running_time = round((total_runtime / 395), 2)

    print("\n############################ COMPLETED RUNNING SUCCESSFULLY ############################")
    print("\n############################ SUMMARY ############################")

    print("\nSCRIPT NAME: 4_stmt_to_line_suspiciousness.py")
    print("PROJECTS SELECTED: %s" % PROJECTS)
    print("TOTAL NUMBER OF BUGS SELECTED: %s" % bug_count)

    print("\nINPUT DIRECTORY: %s" % input_directory)
    print("INPUT SOURCE CODE LINES DIRECTORY: %s" % input_dir_source_code_lines)
    print("OUTPUT DIRECTORY: %s" % output_directory)

    total_runtime_minutes = round((total_runtime / 60), 2)
    print("\nTotal Running Time : %s minutes" % total_runtime_minutes)
    print("Average Running Time per Bug : %s seconds" % avg_running_time)

    print("\n############################ END ############################")