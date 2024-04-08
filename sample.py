import os
from graph_structures import *
from formulas import *
from std_modelcheck import ModelChecker


def consistency_checker(sample, formula):
	for structure in sample.positive:
		checker = ModelChecker(model=structure, formula=formula)
		if not checker.check():
			print('Positive example')
			print(structure)
			return False
	for structure in sample.negative:
		checker = ModelChecker(model=structure, formula=formula)
		if checker.check():
			print('Negative example')
			print(structure)
			return False
	return True

class Sample:
	'''
	contains the sample of postive and negative examples
	'''
	def __init__(self, positive=[], negative=[], propositions=[]):

		self.positive = positive
		self.negative = negative
		self.propositions = propositions
		self.formula = None

	def calc_stats(self):
		self.num_positive = len(self.positive)
		self.num_negative = len(self.negative)
		self.num_total = self.num_positive + self.num_negative
		all_props = []
		for structure in self.positive+self.negative:
			all_props += structure.propositions
		self.propositions = list(set(all_props))
		self.num_props = len(self.propositions)

	def read_sample(self):
		pass


class SampleKripke(Sample):
	'''
	Sample of positive and negative Kripke structures
	'''
	def __init__(self, positive=[], negative=[], propositions=[]):
		super().__init__(positive, negative, propositions)
	
	def read_sample(self, file_path):
		
		with open(file_path, 'r') as file:
			lines = file.read()
			info = lines.split('---\n---\n---\n')	
			
			if len(info) == 2:
				positive_str, negative_str = info
				self.formula = None
			elif len(info) == 3:
				positive_str, negative_str, formula_str = info
				self.formula = CTLFormula.convertTextToFormula(formula_str)

			# Read positive examples
			kripke_strs = positive_str.split('---\n---\n')
			for kripke_str in kripke_strs:
				k = Kripke(init_states=[], transitions={}, labels={}, propositions=[])
				k.read_structure(kripke_str)
				self.positive.append(k)
			
			# Read negative examples
			kripke_strs = negative_str.split('---\n---\n')
			for kripke_str in kripke_strs:
				k = Kripke(init_states=[], transitions={}, labels={}, propositions=[])
				k.read_structure(kripke_str)
				self.negative.append(k)
			
			self.calc_stats()

	def generate_random(self, file_path, total_num_positive=10, total_num_negative=10, formula=None, total_trials=10000):
		'''
		Generates a random sample of Kripke structures
		'''
		positive = []
		negative = []

		trials = 0
		num_positive = 0
		num_negative = 0

		while True:
			trials += 1
			if trials == total_trials:
				break
			
			
			transition_density = random.choices(['low', 'medium', 'high'], [0.7, 0.2, 0.1], k=1)[0]
			num_states = random.randint(2, 10)
			max_deg = random.randint(2, 4)
			try:
				rand_kripke = generate_random_kripke(max_deg, max_deg, num_states, transition_density, self.propositions)
			except:
				continue
			
			checker = ModelChecker(model=rand_kripke, formula=formula)

			if checker.check() and num_positive < total_num_positive:
				self.positive.append(rand_kripke)
				num_positive += 1
			elif not checker.check() and num_negative < total_num_negative:
				self.negative.append(rand_kripke)
				num_negative += 1
			elif num_positive == total_num_positive and num_negative == total_num_negative:
				break

		print('##### Generated! Positive: %d, Negative: %d, Trials: %d #####'%(num_positive, num_negative, trials))		
		self.formula = formula
		self.calc_stats()
		self.write(file_path)

	def write(self, file_path):
		# create file path if it does not exist
		
		with open(file_path, 'w') as file:
			file.write('---\n---\n'.join([kripke.to_string() for kripke in self.positive]))
			file.write('---\n---\n---\n')
			file.write('---\n---\n'.join([kripke.to_string() for kripke in self.negative]))
			if self.formula != None:
				file.write('---\n---\n---\n')
				file.write(str(self.formula))

#s = SampleKripke()
#s.read_sample('tests/inputs/example_sample.sp')
#example = s.positive[1]
#example.show()
#print(example)

#formula_list = ['EF(p)', 'AG(p)', 'EU(p,q)', '&(EF(p),AX(q))']


#formula = CTLFormula.convertTextToFormula(formula_list[1])
#print(formula)
#sample = SampleKripke(positive=[], negative=[], propositions=['p', 'q'])
#sample.generate_random('random_sample.sp', 30, 30, formula, 10000)

