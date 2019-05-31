import io,json,sys,os
import argparse

FL_TECHNIQUE = 'ML_combineFL'          # Fault Localization (FL) Technique : combineFastestFL
WORKING_DIR = os.path.abspath('')

class CombineFL:
    def __init__(self):
        self.raw_data_file = 'data/release.json'
        with io.open(self.raw_data_file) as f:
            self.data = json.load(f)
        self.techniques = set([
            'ochiai',
            'dstar',
            'metallaxis',
            'muse',
            'slicing',
            'slicing_count',
            'slicing_intersection',
            'stacktrace',
            'predicateswitching'
        ])

        self.projects = [
            ('Math', 106),
            ('Closure', 133),
            ('Time',27),
            ('Chart',26),
            ('Lang',65)
        ]

        # self.projects = [
        #     ('Math', 1)
        #     # ('Closure', 133),
        #     # ('Time',27),
        #     # ('Chart',26),
        #     # ('Lang',65)
        # ]

        self.data_dir = 'data'
        self.output_svm_file = 'l2r_format.dat'
        self.new_techniques = set()

    def unique_name(self, project, number):
        return project.lower()+str(number)

    def convert_to_svm_format(self, keys, output_directory):
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        out_path = os.path.join(self.data_dir, self.output_svm_file)
        # clean file content
        with io.open(out_path, 'w') as f:
            pass
        qid = 1
        for proj, numbers in self.projects:
            for bug_id in range(1, numbers+1):
                lines = self.gen_svm_format(proj,bug_id,qid,keys,output_directory)
                print '\r', 'handling..',proj, bug_id, 'qid:',qid,'        ',
                sys.stdout.flush()
                # print("\nProject: %s" % proj)
                # print("Bug id: %s" % bug_id)
                # print("qid: %s" % qid)
                # print("length of lines: %s" % len(lines))

                qid += 1

                with io.open(out_path, 'a') as f:
                    for l in lines:
                        f.write(unicode(l))




            print
        print '\nDone.'

    def gen_svm_format(self, project, bug_id, qid, keys, output_directory):
        fault_name = self.unique_name(project, bug_id)
        fault_data = self.data[fault_name]
        lines = []

        output_csv = "%s-%s-%s-suspiciousness" % (project, bug_id, FL_TECHNIQUE)
        output_csv_file = os.path.join(output_directory, output_csv)
        with open(output_csv_file, mode="a") as myFile:
            myFile.write("Statement,Suspiciousness\n")

        for statement in fault_data:

            statement_str = statement.replace(':', '#')
            with open(output_csv_file, mode="a") as myFile:
                myFile.write("%s\n" % statement_str)

            # is_fault
            faultystr = str(fault_data[statement]['faulty'])
            # qid
            qidstr = 'qid:'+str(qid)
            # features
            features = []
            for i, key in enumerate(keys, start=1):
                if key in fault_data[statement]:
                    feature = str(i)+':'+str(fault_data[statement][key])
                else:
                    feature = str(i)+':0.0'
                features.append(feature)
            line = faultystr + ' ' + qidstr
            for feature in features:
                line += ' ' + feature
            line += '\n'
            lines.append(line)
        return lines

    def add_in(self, file_path):
        with io.open(file_path) as f:
            add_in_data = json.load(f)
        for fault_name in add_in_data:
            if fault_name not in self.data:
                print 'Error.',fault_name, 'is not a valid fault in dataset. Valid example: closure5'
                return
            new_fault_data = add_in_data[fault_name]
            origin_fault_data = self.data[fault_name]
            for statement in new_fault_data:
                if statement not in origin_fault_data:
                    origin_fault_data[statement] = {}
                    origin_fault_data[statement]['faulty'] = 0
                for key in new_fault_data[statement]:
                    if key in self.techniques or key == 'faulty':
                        print 'Error.', key, 'is a reserved key in original dataset. Please change the keyword in add-in data.'
                        return
                    origin_fault_data[statement][key] = new_fault_data[statement][key]
                    self.new_techniques.add(key)

def main():
    parser = argparse.ArgumentParser(description='Combine and Generate SVMRank file.')
    parser.add_argument('-f', '--add_in_file', help="Add-in data file.")
    args = parser.parse_args()

    output_directory = "%s/output_stmt_%s" % (WORKING_DIR, FL_TECHNIQUE)
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    else:
        raise ValueError("Output directory %s already exists. " % output_directory)

    if args.add_in_file:
        combine = CombineFL()
        combine.add_in(args.add_in_file)

        combine.convert_to_svm_format(combine.techniques.union(combine.new_techniques), output_directory)
    else:
        combine = CombineFL()
        combine.convert_to_svm_format(combine.techniques, output_directory)

if __name__ == '__main__':
    main()
