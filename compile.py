# compile all json files
import json
import os
import argparse
import csv


def compile_jsons_to_csv(json_folder, output_file):
	all_jsons = []
	for root, dirs, files in os.walk(json_folder):
		for file in files:
			if file.endswith('.json'):
				with open(os.path.join(root, file), 'r') as json_file:
					all_jsons.append(json.load(json_file))

	# extract the key and values from the json dict
	keys = set()
	for json_data in all_jsons:
		keys.update(json_data.keys())

	# write the data to a csv file
	with open(output_file, 'w', newline='') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(list(keys))
		for json_data in all_jsons:
			row = [json_data.get(key, '') for key in keys]
			writer.writerow(row)

	

#write a main function that calls compile_jsons with the appropriate arguments
def main():

	parser = argparse.ArgumentParser(description='Compile JSON files.')
	parser.add_argument('-f', '--json_folder', default='test_suite', help='Path to the folder containing JSON files.')
	parser.add_argument('-o', '--output_file', default='compiled.csv', help='Path to the output file.')

	args = parser.parse_args()

	json_folder = args.json_folder
	output_file = args.output_file
	

	compile_jsons_to_csv(json_folder, output_file)

main()