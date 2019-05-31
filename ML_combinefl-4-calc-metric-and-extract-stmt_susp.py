import operator as op
import io
import os
import sys
import csv

# PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Time']
PROJECTS = ['Math', 'Closure', 'Time', 'Chart', 'Lang']


# PROJECT_BUGS = [
#     [str(x) for x in range(1, 134)],      # Closure
#     [str(x) for x in range(1, 66)],       # Lang
#     [str(x) for x in range(1, 27)],       # Chart
#     [str(x) for x in range(1, 107)],      # Math
#     [str(x) for x in range(1, 39)],       # Mockito
#     [str(x) for x in range(1, 28)]        # Time
# ]

PROJECT_BUGS = [
    [str(x) for x in range(1, 107)],         # Math
    [str(x) for x in range(1, 134)],         # Closure
    [str(x) for x in range(1, 28)],          # Time
    [str(x) for x in range(1, 27)],          # Chart
    [str(x) for x in range(1, 66)]           # Lang
]


FL_TECHNIQUE = 'ML_combineFastestFL_run_1'          # Fault Localization (FL) Technique : combineFastestFL
WORKING_DIR = os.path.abspath('')

pred_f = 'svmrank-pred.dat'

def nCr(n, r):
    r = min(r, n-r)
    if r == 0:
        return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    demon = reduce(op.mul, xrange(1, r+1))
    return numer // demon

def E_inspect(st, en, nf):
    expected = float(st)
    n = en - st + 1
    for k in xrange(1, n-nf+1):
        term = float(nCr(n-k-1, nf-1) * k) / nCr(n, nf)
        expected += term
    return expected

# List = [
#   {
#       is_fault: 1 / 2,
#       score: 0.123
#   },
# ]
def get_E_inspect(lst):
    sorted_lst = sorted(lst, key=lambda f: f['score'], reverse=True)
    pos = -1
    for i, f in enumerate(sorted_lst):
        if f['is_fault'] == 1:
            pos = i
            pos_score = f['score']
            break
    if pos == -1:
        return -1
    start = 0
    end = len(sorted_lst) -1
    for i in range(pos-1, -1, -1):
        f = sorted_lst[i]
        if f['score'] != pos_score:
            start = i+1
            break
    for i in range(pos+1, len(sorted_lst)):
        f = sorted_lst[i]
        if f['score'] != pos_score:
            end = i-1
            break
    count = 0
    for i in range(start, end+1):
        if sorted_lst[i]['is_fault'] == 1:
            count += 1
    return E_inspect(start+1, end+1, count)

def read_info_ranksvm(num):
    # data -> bug(qid) -> pos(line) -> score / is_fault
    data = {}
    curdir = 'data/cross_data'
    curdir = os.path.join(curdir, str(num))
    pred_file = os.path.join(curdir, pred_f)
    test_file = os.path.join(curdir, 'test.dat')
    with io.open(test_file) as f:
        test_data = f.readlines()
    with io.open(pred_file) as f:
        pred_data = f.readlines()
    for i in range(len(pred_data)):
        test_line = test_data[i]
        pred_line = pred_data[i]
        is_fault = int(test_line.split(' ', 1)[0])
        qid = test_line.split(' ', 2)[1]
        score = float(pred_line)
        if qid not in data:
            data[qid] = []
        item = {'score': score, 'is_fault': is_fault}
        data[qid].append(item)
    return data

def qid_to_lines():
    data = {}
    with io.open('data/qid-lines.csv') as f:
        raw = f.readlines()
        for line in raw:
            qid = int(line.split(',')[0])
            lines = int(line.split(',')[1])
            data[qid] = lines
    return data


def read_susp_lines_from_file(input_file):
    susp_data = csv.reader(open(input_file), delimiter=',')
    sorted_susp_lines = [susp_line for susp_line in susp_data]

    return sorted_susp_lines[1:]  # Skip header # Top 100


def append_susp(input_file, output_file, fault_data_values):

    statements = read_susp_lines_from_file(input_file)

    if len(fault_data_values) != len(statements):
        raise ValueError("Count of lines not matching in append_susp function()")

    with open(output_file, mode="a") as myFile:
        myFile.write("Statement,Suspiciousness\n")

    for i, stmt in enumerate(statements):
        stmt.append(fault_data_values[i]['score'])      # Mapping susp stmt with the new score

    for stmt in statements:
        stmt_str = stmt[0] + ',' + str(stmt[1])
        # print(stmt_str)
        with open(output_file, mode="a") as myFile:
            myFile.write("%s\n" % stmt_str)


def main():
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 10      # Number of n-fold cross validation

    input_directory = "%s/output_stmt_%s" % (WORKING_DIR, FL_TECHNIQUE)
    if not os.path.exists(input_directory):
        raise ValueError("Input directory %s does not exist. " % input_directory)

    output_directory = "%s/output_stmt_susp_%s" % (WORKING_DIR, FL_TECHNIQUE)
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError("Output directory %s already exists. " % output_directory)

    E_pos_list = []
    EXAM_list = []
    qid2line = qid_to_lines()

    data_dict = {}

    for i in range(n):
        print '\r','Handle', i+1, '/', n,
        sys.stdout.flush()
        data = read_info_ranksvm(i)
        data_dict.update(data)

        for key in data.keys():
            # key: u'qid:117'
            E_inspect = get_E_inspect(data[key])
            E_pos_list.append(E_inspect)
            # calc EXAM
            qid = int(key.split(':')[1])
            lines = qid2line[qid]
            EXAM = E_inspect / float(lines)
            EXAM_list.append(EXAM)
    top = []
    # print("\nE position list")
    # print(E_pos_list)
    # print("len(E_pos_list): %s" % len(E_pos_list))
    top.append(len(filter(lambda item: item < 1.01 and item > 0, E_pos_list)))
    top.append(len(filter(lambda item: item < 3.01 and item > 0, E_pos_list)))
    top.append(len(filter(lambda item: item < 5.01 and item > 0, E_pos_list)))
    top.append(len(filter(lambda item: item < 10.01 and item > 0, E_pos_list)))
    print '\nTop 1/3/5/10:', top
    # print '\nTop 1:', top
    EXAM_list = [e for e in EXAM_list if e > 0]
    print 'EXAM: ', sum(EXAM_list) / len(EXAM_list)

    print("Bugs count: %s" % len(data_dict))

    qid_count = 1
    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            input_csv = "%s-%s-%s-suspiciousness" % (project, bug, FL_TECHNIQUE)
            output_csv = "%s-%s-%s-suspiciousness" % (project, bug, FL_TECHNIQUE)
            qid_str = 'qid:' + str(qid_count)
            fault_data_values = data_dict[qid_str]
            append_susp(os.path.join(input_directory, input_csv),
                 os.path.join(output_directory, output_csv), fault_data_values)

            qid_count += 1



if __name__ == '__main__':
    main()
