import argparse
import json
import time
from sample import SampleKripke
from formulas import CTLFormula
from operators import *
from ctl_encoding import CTLSATEncoding
from std_modelcheck import consistency_checker

class LearnFramework:

	def __init__(self, sample_file='tests/inputs/example_sample.sp', size_bound=10, operators=ctl_operators, json_file='metadata.json'):
		self.sample_file = sample_file
		self.size_bound = size_bound
		self.operators = operators

		# Time stats
		self.enc_time = 0
		self.solving_time = 0
		self.total_time = 0

		# Learning stats
		self.learned_formula = None
		self.learned_formula_size = None

		self.metadata = {'Sample': self.sample_file, 'Size Bound': self.size_bound,
						 'Operators': self.operators, 'Encoding Time':self.enc_time,
						 'Solving Time': self.solving_time, 'Total Time': self.total_time,
						 'Learned Formula': self.learned_formula, 'Learned Formula Size': self.learned_formula_size
						}
		
	def learn_ctl(self):

		sample = SampleKripke()
		sample.read_sample(self.sample_file)
		formula = None

		enc_time_incr = time.time() 
		enc = CTLSATEncoding(sample, sample.propositions, self.operators)
		enc_time_incr = time.time() - enc_time_incr
		self.enc_time += enc_time_incr

		for size in range(1,self.size_bound+1):

			# Propositional Encoding
			enc_time_incr = time.time() 
			enc.encodeFormula(size)
			enc_time_incr = time.time() - enc_time_incr
			self.enc_time += enc_time_incr

			# SAT solving
			solving_time_incr = time.time()
			solverRes = enc.solver.solve()
			print('Solved for size %d'%size, solverRes)
			if solverRes == True:
				#print('sat')
				solverModel = enc.solver.get_model()
				#for var in solverModel:
				#	if solverModel[var[0]].is_true():
				#		print(var)
				formula = enc.reconstructWholeFormula(solverModel, size)
				print("Found formula {}".format(formula.prettyPrint()))
				break
			
			solving_time_incr = time.time() - solving_time_incr
			self.solving_time += solving_time_incr

		# Formula verification
		if formula != None:
			ver = consistency_checker(sample, formula)
			print('Verification',ver)
			if not ver:
				raise Exception('Incorrect Formula found')
		else:		
			print('No formula found within %d size bound'%size)

	def dump_json(self, json_file='metadata.json'):
		with open(json_file, 'w') as f:
			json.dump(self.metadata, f, indent=4)


def main():
	parser = argparse.ArgumentParser(description='Parameters for the learning algo')
	parser.add_argument('-f', '--input_file', default='tests/inputs/small_example_sample.sp', help='The input sample file')
	parser.add_argument('-s', '--formula_size', default=3, type=int, help='The size of the formula')
	parser.add_argument('-o', '--operators', nargs='+', default=ctl_boolean+['AX'], help='Choice of CTL operators')

	args = parser.parse_args()

	#print(f"Input file: {args.input_file}")
	#print(f"Formula size: {args.formula_size}")
	#print(f"CTL operators: {args.operators}")
	print(args.operators)
	learn = LearnFramework(sample_file=args.input_file, size_bound=args.formula_size, operators=args.operators)
	learn.learn_ctl()

if __name__ == "__main__":
	main()