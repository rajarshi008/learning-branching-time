# compile all json files
import json
import os
import argparse


def compile_jsons(json_folder, output_file):
	all_jsons = []
	for root, dirs, files in os.walk(json_folder):
		for file in files:
			if file.endswith('.json'):
				with open(os.path.join(root, file), 'r') as json_file:
					all_jsons.append(json.load(json_file))
	with open(output_file, 'w') as out_file:
		json.dump(all_jsons, out_file, indent=4)

#write a main function that calls compile_jsons with the appropriate arguments
def main():

	parser = argparse.ArgumentParser(description='Compile JSON files.')
	parser.add_argument('-f', '--json_folder', default='test_suite', help='Path to the folder containing JSON files.')
	parser.add_argument('-o', '--output_file', default='compiled.json', help='Path to the output file.')

	args = parser.parse_args()

	json_folder = args.json_folder
	output_file = args.output_file
	

	compile_jsons(json_folder, output_file)