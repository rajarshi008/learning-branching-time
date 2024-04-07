# compile all json files
import json
import os


def compile_jsons(json_folder, output_file):
	all_jsons = []
	for root, dirs, files in os.walk(json_folder):
		for file in files:
			if file.endswith('.json'):
				with open(os.path.join(root, file), 'r') as json_file:
					all_jsons.append(json.load(json_file))
	with open(output_file, 'w') as out_file:
		json.dump(all_jsons, out_file, indent=4)

