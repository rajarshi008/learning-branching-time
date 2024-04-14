
import argparse
import os, shutil
import datetime
from sample import Sample, SampleKripke, consistency_checker
from formulas import CTLFormula
import math
import csv

class SampleGenerator:
	'''
	sample generator class
	'''
	def __init__(self,
				formula_file = 'test_suite/formulas.txt',
				num_models = [(5,5),(10,10)],
				size_models = [(6,6)],
				output_folder = 'test_suite/Random_generated/' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
				):

		self.formula_file = formula_file
		self.num_models = num_models
		self.size_models = size_models
		self.output_folder = output_folder
		
		#self.structure_size = size
		#self.gen_method = gen_method
		

		if os.path.exists(self.output_folder):
			shutil.rmtree(self.output_folder)

		os.makedirs(output_folder)
		formula_file_name = self.formula_file.split('/')[-1]

		shutil.copyfile(self.formula_file, output_folder+'/'+formula_file_name)
		self.num_models.sort()
		self.max_size = num_models[-1]
		
		self.sample_stats = {}

	def generateFromLargeSample(self):
		
		generated_files = self.generate(gen_from_large_sample=True)
		#generating small benchmarks from large ones
		self.generateSmallBenchmarks(generated_files, self.num_models[:-1])


	def generate(self, gen_from_large_sample=False):

		if gen_from_large_sample:
			num_models = [self.max_size]
		else:	
			num_models = self.num_models

		sample_folder = self.output_folder+'/Kripke/' 
		os.makedirs(sample_folder)

		#if trace_type == 'words':
		#	words_folder = output_folder+'/TracesFiles/'
		#	os.makedirs(words_folder)

		generated_files = []
		with open(self.formula_file, 'r') as file:
			formula_num=0
			sample_data = {}
			for line in file:
				
				formula_text, propositions = line.split(';')
				propositions = propositions.split(',')
				propositions[-1] = propositions[-1].rstrip('\n')
				
				#trace_lengths = lengths.split(',')
				#trace_lengths = [(int(i),int(i)) for i in trace_lengths]

				formula = CTLFormula.convertTextToFormula(formula_text)
		
				formula_num+=1
				print('---------------Generating Benchmarks for formula %s---------------'%(formula.prettyPrint()))
				
				for num in num_models:
					for size in self.size_models:				
						print('* Positive examples %d, Negative examples %d in size range (%d,%d)'%(num[0],num[1],size[0],size[1]))
						sample_file = sample_folder+'f:'+str(formula_num).zfill(2)+'-'+'nm:'+str((num[0]+num[1])//2).zfill(3)+'-'+'sm:'+str((size[0]+size[1])//2).zfill(3)+'.sp'
						generated_files.append(sample_file)
						sample = SampleKripke(positive=[], negative=[], propositions=propositions)
						deg = math.ceil(math.log(size[1],2)-1)
						sample.generate_random(sample_file, num[0], num[1], size, deg, formula, 10000, write=False)
						if sample.num_positive != num[0] or sample.num_negative != num[1]:
							sample.generate_random_split(sample_file, num[0]-sample.num_positive, num[1]-sample.num_negative,\
														 size, deg, formula, 20000, write=True)
						sample.write(sample_file)
						ver =  consistency_checker(sample, formula)
						assert ver
						sample_data = {'File': sample_file, 'Formula': formula.prettyPrint(),\
										'Positive': num[0], 'Negative': num[1], 'Size Lower': size[0],\
										'Size Upper': size[1], 'Verification': ver}
						self.sample_stats[sample_file] = sample_data
					 	
		return generated_files


	def generateSmallBenchmarks(self, generated_files, num_models):
		print(generated_files, num_models)
		for filename in generated_files:
			
			s = SampleKripke(positive=[],negative=[],propositions=[])
			s.read_sample(filename)
			old_sample_data = self.sample_stats[filename]
			for (i,j) in num_models:
				
				new_filename = filename.replace("nm:"+str((self.max_size[0]+self.max_size[1])//2).zfill(3), "nw:"+str(i).zfill(3))
				print(new_filename)
				new_positive = s.positive[:i]
				new_negative = s.negative[:j]

				new_s = SampleKripke(positive=new_positive, negative=new_negative, propositions=s.propositions, formula=s.formula)
				

				sample_data = {'File': new_filename, 'Formula': old_sample_data['Formula'],\
								'Positive': i, 'Negative':j, 'Size Lower': old_sample_data['Size Lower'],\
								'Size Upper': old_sample_data['Size Upper'], 'Verification': old_sample_data['Verification']}
				
				self.sample_stats[new_filename] = sample_data
				new_s.write(new_filename)

	def writeStats(self):
		'''Write stats as a csv file'''
		stats_file = self.output_folder+'/stats.csv'
		stats_list = list(self.sample_stats.values())
		print(len(stats_list))
		with open(stats_file, 'w') as file:
			writer = csv.DictWriter(file, fieldnames=stats_list[0].keys())
			writer.writeheader()
			for data in stats_list:
				writer.writerow(data)
		

#Data type for parser
def tupleList(s):
	try:
		return tuple(map(int , s.split(',')))
	except:
		print("Wrong format; provide comma separated values")



def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--formula_file', '-f', dest='formula_file', default = 'formulas.txt')
	parser.add_argument('--num_models', '-s', dest='num_models', default=[(5,5),(25,25),(50,50)], nargs='+', type=tupleList)
	parser.add_argument('--output_folder', '-o', dest='output_folder', default = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	parser.add_argument('--size_models', '-m', dest='size_models', default=[(5,15),(15,25)], nargs='+', type=tupleList)
	#Structure sizes

	args,unknown = parser.parse_known_args()
	formula_file = 'test_suite/'+ args.formula_file
	num_models = list(args.num_models)
	output_folder = 'test_suite/' + args.output_folder
	size_models = list(args.size_models)

	generator = SampleGenerator(formula_file=formula_file,
				num_models=num_models,
				output_folder=output_folder,
				size_models=size_models)

	generator.generateFromLargeSample()
	generator.writeStats()

if __name__=='__main__':
	main()