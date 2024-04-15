import argparse
import json
import time
from sample import SampleKripke, SampleCGS, consistency_checker
from formulas import CTLFormula
from operators import *
from ctl_encoding import CTLSATEncoding
from atl_encoding import ATLSATEncoding

class LearnFramework:

	def __init__(self, sample_file='tests/inputs/example_sample.sp', size_bound=10,\
			  			 operators=ctl_operators, solver_name='z3', cgs=False, atl=False):
		self.sample_file = sample_file
		self.size_bound = size_bound
		self.operators = operators
		self.solver_name = solver_name
		self.json_file = sample_file.split('.')[0] +'-'+solver_name+'.json'
		self.cgs = cgs
		self.formula_type = 'atl' if atl else 'ctl'
		self.model_type = 'cgs' if cgs else 'kripke'

		# Time stats
		self.enc_time = 0
		self.solving_time = 0
		self.total_time = 0

		# Learning stats
		self.learned_formula = None
		self.learned_formula_size = None
		
		if self.cgs:
			self.sample = SampleCGS(positive=[], negative=[], propositions=[])
			self.sample.read_sample(self.sample_file)
			self.sample.positive[0].show()
			#self.sample.negative[0].show()

			og_formula_text = None
			if self.sample.formula != None:
				og_formula_text = self.sample.formula.prettyPrint()

			self.metadata = {
				'Sample': self.sample_file, 'Sample size': self.sample.num_total,
							'Size Bound': self.size_bound, 'Solver': self.solver_name,
							'Players': self.sample.num_players, 'Propositions': self.sample.num_props,
							'Encoding Time':self.enc_time,'Solving Time': self.solving_time, 
							'Total Time': self.total_time, 'Original Formula': og_formula_text, 
							'Learned Formula': self.learned_formula, 'Learned Formula Size': self.learned_formula_size,
							'Model Type': self.model_type, 'Formula Type': self.formula_type
							}
		else:
			self.sample = SampleKripke(positive=[], negative=[], propositions=[])
			self.sample.read_sample(self.sample_file)
			og_formula_text = None
			if self.sample.formula != None:
				og_formula_text = self.sample.formula.prettyPrint()

			self.metadata = {
				'Sample': self.sample_file, 'Sample size': self.sample.num_total,
							'Size Bound': self.size_bound, 'Solver': self.solver_name,
							'Encoding Time':self.enc_time,'Solving Time': self.solving_time, 
							'Total Time': self.total_time, 'Original Formula': og_formula_text, 
							'Learned Formula': self.learned_formula, 'Learned Formula Size': self.learned_formula_size,
							'Model Type': self.model_type, 'Formula Type': self.formula_type
							}
			self.dump_json(self.json_file)


	def learn_ctl(self, neg_props=False):
		
		formula = None

		enc_time_incr = time.time()
		enc = CTLSATEncoding(self.sample, self.sample.propositions, self.operators, self.solver_name, neg_props=neg_props)
		enc_time_incr = time.time() - enc_time_incr
		self.enc_time += enc_time_incr

		for size in range(1,self.size_bound+1):
			print('--- Preparing encoding for size %d ---'%size)
			# Propositional Encoding
			enc_time_incr = time.time() 
			enc.encodeFormula(size)
			enc_time_incr = time.time() - enc_time_incr
			self.enc_time += enc_time_incr

			# SAT solving
			solving_time_incr = time.time()
			solverRes = enc.solver.solve()
			solving_time_incr = time.time() - solving_time_incr
			self.solving_time += solving_time_incr
			
			print('Size %d took %.2f seconds'%(size, enc_time_incr+solving_time_incr))

			if solverRes == True:
				#print('sat')
				solverModel = enc.solver.get_model()
				#for var in solverModel:
				#	if solverModel[var[0]].is_true():
				#		print(var)
				formula = enc.reconstructWholeFormula(solverModel, size)
				print("Found formula {}".format(formula.prettyPrint()))
				break
		
		# Formula verification
		if formula != None:
			ver = consistency_checker(self.sample, formula, self.model_type, self.formula_type)
			print('Verification',ver)
			if not ver:
				raise Exception('Incorrect Formula found')
		else:		
			print('No formula found within %d size bound'%size)

		self.metadata.update({'Encoding Time':round(self.enc_time,2), 'Solving Time': round(self.solving_time,2),
							'Total Time': round(self.enc_time + self.solving_time,2), 'Learned Formula': formula.prettyPrint(),
							'Learned Formula Size': size, 'Verification': ver})

		self.dump_json(self.json_file)

		return formula

	def learn_atl(self):
		
		formula = None

		enc_time_incr = time.time()
		enc = ATLSATEncoding(self.sample, self.sample.propositions, self.operators, self.solver_name)
		enc_time_incr = time.time() - enc_time_incr
		self.enc_time += enc_time_incr

		for size in range(1,self.size_bound+1):
			print('--- Preparing encoding for size %d ---'%size)
			# Propositional Encoding
			enc_time_incr = time.time() 
			enc.encodeFormula(size)
			enc_time_incr = time.time() - enc_time_incr
			self.enc_time += enc_time_incr
			
			# SAT solving
			solving_time_incr = time.time()
			solverRes = enc.solver.solve()
			solving_time_incr = time.time() - solving_time_incr
			self.solving_time += solving_time_incr
			
			print('Size %d took %.2f seconds'%(size, enc_time_incr+solving_time_incr))

			if solverRes == True:
				#print('sat')
				solverModel = enc.solver.get_model()
				for var in solverModel:
					if solverModel[var[0]].is_true():
						print(var)
				formula = enc.reconstructWholeFormula(solverModel, size)
				print(formula)
				print("Found formula {}".format(formula.prettyPrint()))
				break
			
			
		
		# Formula verification
		if formula != None:
			ver = consistency_checker(self.sample, formula, self.model_type, self.formula_type)
			print('Verification',ver)
			if not ver:
				raise Exception('Incorrect Formula found')
		else:		
			print('No formula found within %d size bound'%size)

		self.metadata.update({'Encoding Time':round(self.enc_time,2), 'Solving Time': round(self.solving_time,2),
							'Total Time': round(self.enc_time + self.solving_time,2), 'Learned Formula': formula.prettyPrint(),
							'Learned Formula Size': size, 'Verification': ver})

		self.dump_json(self.json_file)

		return formula


	def dump_json(self, json_file='metadata.json'):
		with open(json_file, 'w') as f:
			json.dump(self.metadata, f, indent=4)


def main():
	parser = argparse.ArgumentParser(description='Parameters for the learning algo')
	parser.add_argument('-f', '--input_file', default='sample_kr.sp', help='The input sample file')
	parser.add_argument('-s', '--formula_size', default=20, type=int, help='The size of the formula')
	parser.add_argument('-o', '--operators', nargs='+', default=[], help='Choice of CTL operators')
	parser.add_argument('-z', '--solver', default='msat', choices=['z3', 'msat', 'btor'], help='Choice of solver; note you must have the chosen solver installed')
	parser.add_argument('-j', '--json_file', default='metadata.json', help='The json file to store metadata')
	parser.add_argument('-g', '--game', action='store_true', default=False, help='Input is a CGS sample file')
	parser.add_argument('-a', '--atl', action='store_true', default=False, help='Learn CTL instead of ATL')
	#Learning optimizations
	parser.add_argument('-n', '--neg_props', action='store_true', default=False, help='Negation optimization')
	#parser.add_argument('-t', '--timeout', default=1800, type=int, help='Timeout for the solver')
	
	args = parser.parse_args()

	#print(f"Input file: {args.input_file}")
	#print(f"Formula size: {args.formula_size}")
	#print(f"CTL operators: {args.operators}")

	if args.operators == [] and args.atl:
		args.operators = atl_operators
	elif args.operators == [] and not args.atl:
		args.operators = ctl_operators
	
	learn = LearnFramework(sample_file=args.input_file, size_bound=args.formula_size,\
							operators=args.operators, solver_name=args.solver, \
							cgs=args.game, atl=args.atl)
	
	if args.atl:
		learn.learn_atl()
	else:
		learn.learn_ctl(neg_props=args.neg_props)
	
if __name__ == "__main__":
	main()