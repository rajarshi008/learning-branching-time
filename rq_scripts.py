import os, glob
from operators import *
import argparse
import multiprocessing
from learn_formulas import *
import csv


def read_json_files_to_csv(folder_path, output_csv_path):
    compiled_data = []
    
    # List all files in the specified folder
    files = os.listdir(folder_path)
    
    # Filter out files with '.json' extension
    json_files = [file for file in files if file.endswith('.json')]
    
    # Read and compile the contents of each '.json' file
    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)
        with open(file_path, 'r') as file:
            content = json.load(file)
            compiled_data.append(content)
    
    # Get the headers from the first JSON object (assuming all JSON objects have the same structure)
    if compiled_data:
        headers = compiled_data[0].keys()
        
        # Write the compiled data to a CSV file
        with open(output_csv_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for data in compiled_data:
                writer.writerow(data)



def read_sp_files(folder_path):
    # List all files in the specified folder
    files = os.listdir(folder_path)
    
    # Filter out files with '.sp' extension
    sp_files = [folder_path+'/'+file for file in files if file.endswith('.sp')]
    
    return sp_files


def run_ctl_test(file, timeout=900, wu=False):
	
	if wu:
		operators=list(set(ctl_operators).difference(set(['EU', 'AU'])))
	else:
		operators=ctl_operators


	learn = LearnFramework(sample_file=file, size_bound=20,\
								operators=operators, solver_name='msat',\
								cgs=False, atl=False, turn=True)


	manager = multiprocessing.Manager()
	return_dict = manager.dict()
	jobs = []
		
	p = multiprocessing.Process(target=learn.learn_ctl, args=())
		
	jobs.append(p)
	p.start()

	p.join(timeout)
	if p.is_alive():
		print("Timeout reached, check your output in result file")
		p.terminate()
		p.join()

	for proc in jobs:
		proc.join()


def run_atl_test(file, timeout=900, turn=True):

	learn = LearnFramework(sample_file=file, size_bound=20,\
								operators=atl_operators, solver_name='msat',\
								cgs=True, atl=True, turn=turn)

	manager = multiprocessing.Manager()
	return_dict = manager.dict()
	jobs = []
		
	p = multiprocessing.Process(target=learn.learn_atl, args=())
		
	jobs.append(p)
	p.start()

	p.join(timeout)
	if p.is_alive():
		print("Timeout reached, check your output in result file")
		p.terminate()
		p.join()

	for proc in jobs:
		proc.join()




def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('-e', '--exp', dest='exp', default='ctl', choices=['ctl', 'ctl_wu', 'atl', 'atl_tb'])
	parser.add_argument('--timeout', '-t', dest='timeout', default=900, type=int)
	parser.add_argument('--all', '-a', dest='all_files', default=False, action='store_true')


	args,unknown = parser.parse_known_args()
	exp_num = args.exp
	all_files = args.all_files
	timeout = int(args.timeout)

	if exp_num == 'ctl':

		if all_files:
			folder_path = 'test_suite/first_suite_CTL'
		else:
			folder_path = 'test_suite/first_suite_CTL_too_small'

		sp_files = read_sp_files(folder_path)
		for file in sp_files:
			run_ctl_test(file, timeout=timeout, wu=False)

		read_json_files_to_csv(folder_path, 'exp_ctl.csv')
		
		
	if exp_num == 'ctl_wu':

		if all_files:
			folder_path = 'test_suite/first_suite_CTL'
		else:
			folder_path = 'test_suite/first_suite_CTL_small'
		sp_files = read_sp_files(folder_path)
		
		for file in sp_files:
			run_ctl_test(file, timeout=timeout, wu=True)
		
		read_json_files_to_csv(folder_path, 'exp_ctl_wu.csv')

	if exp_num == 'atl':

		if all_files:
			folder_path = 'test_suite/second_suite_ATL'
		else:
			folder_path = 'test_suite/second_suite_ATL_small'
		sp_files = read_sp_files(folder_path)
		
		for file in sp_files:
			run_atl_test(file, timeout=timeout, turn=False)

		read_json_files_to_csv(folder_path, 'exp_atl.csv')

	if exp_num == 'atl_tb':

		if all_files:
			folder_path = 'test_suite/second_suite_ATL'
		else:
			folder_path = 'test_suite/second_suite_ATL_small'

		sp_files = read_sp_files(folder_path)
		
		for file in sp_files:
			run_atl_test(file, timeout=timeout, turn=True)
		
		read_json_files_to_csv(folder_path, 'exp_atl_tb.csv')

if __name__ == "__main__":
	main()