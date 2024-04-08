
import argparse
import os, shutil
import datetime
from sample import Sample, SampleKripke, consistency_checker
from formulas import CTLFormula


class SampleGenerator:
	'''
	sample generator class
	'''
	def __init__(self,
				formula_file = 'test_suite/formulas.txt',
				trace_type = 'trace',
				sample_sizes = [(10,10),(50,50)],
				trace_lengths = [(6,6)],
				output_folder = 'test_suite/Random_generated/' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
				total_num = 1):

		self.formula_file = formula_file
		
		self.sample_sizes = sample_sizes
		
		self.output_folder = output_folder
		self.total_num = total_num
		
		self.operators = ['F', 'G', 'X', '!', '&', '|']

		#self.structure_size = size
		#self.gen_method = gen_method

		if os.path.exists(self.output_folder):
			shutil.rmtree(self.output_folder)

		os.makedirs(output_folder)
		formula_file_name = self.formula_file.split('/')[-1]

		shutil.copyfile(self.formula_file, output_folder+'/'+formula_file_name)
		self.sample_sizes.sort()
		self.max_size = sample_sizes[-1]
		

	def generateFromLargeSample(self):
		
		generated_files = self.generate(gen_from_large_sample=True)
		#generating small benchmarks from large ones
		self.generateSmallBenchmarks(generated_files, self.sample_sizes[:-1])



	def generate(self, gen_from_large_sample=False):

		if gen_from_large_sample:
			sample_sizes = [self.max_size]
		else:	
			sample_sizes = self.sample_sizes

		sample_folder = self.output_folder+'/Kripke/' 
		os.makedirs(sample_folder)

		#if trace_type == 'words':
		#	words_folder = output_folder+'/TracesFiles/'
		#	os.makedirs(words_folder)

		generated_files = []
		with open(self.formula_file, 'r') as file:
			formula_num=0
			for line in file:
				
				formula_text, propositions = line.split(';')
				propositions = propositions.split(',')
				propositions[-1] = propositions[-1].rstrip('\n')
				
				#trace_lengths = lengths.split(',')
				#trace_lengths = [(int(i),int(i)) for i in trace_lengths]

				formula = CTLFormula.convertTextToFormula(formula_text)
		
				formula_num+=1
				print('---------------Generating Benchmarks for formula %s---------------'%(formula.prettyPrint()))
				
				for size in sample_sizes:				
					print('* Generating for size: %d, %d'%(size[0],size[1]))

					sample_file = sample_folder+'f:'+str(formula_num).zfill(2)+'-'+'nw:'+str((size[0]+size[1])//2).zfill(3)+'.sp'
					generated_files.append(sample_file)
					sample = SampleKripke(positive=[], negative=[], propositions=propositions)
					sample.generate_random(sample_file, size[0], size[1], formula, 10000)

					assert consistency_checker(sample, formula)

		return generated_files


	def generateSmallBenchmarks(self, generated_files, sizes):
		
		for filename in generated_files:
			
			s = SampleKripke(positive=[],negative=[],propositions=[])
			s.read_sample(filename)
			
			for (i,j) in sizes:
				
				new_filename = filename.replace("nw:"+str((self.max_size[0]+self.max_size[1])//2).zfill(3), "nw:"+str(i).zfill(3))
				new_positive = s.positive[:i]
				new_negative = s.negative[:j]
				new_s = SampleKripke(positive=new_positive, negative=new_negative, propositions=s.propositions)
				new_s.write(new_filename)



#Data type for parser
def tupleList(s):
	try:
		return tuple(map(int , s.split(',')))
	except:
		print("Wrong format; provide comma separated values")



def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--formula_file', '-f', dest='formula_file', default = 'formulas.txt')
	parser.add_argument('--size', '-s', dest='sample_sizes', default=[(10,10),(25,25),(50,50),(100,100)], nargs='+', type=tupleList)
	parser.add_argument('--total_num', '-n', dest='total_num', default=1, type=int)
	parser.add_argument('--output_folder', '-o', dest='output_folder', default = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	#Structure sizes

	args,unknown = parser.parse_known_args()
	formula_file = 'test_suite/'+ args.formula_file
	sample_sizes = list(args.sample_sizes)
	output_folder = 'test_suite/' + args.output_folder
	total_num = int(args.total_num)
	


	generator = SampleGenerator(formula_file=formula_file,
				sample_sizes=sample_sizes,
				output_folder=output_folder,
				total_num=total_num)

	generator.generateFromLargeSample()

if __name__=='__main__':
	main()