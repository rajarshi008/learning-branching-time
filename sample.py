import os
from graph_structures import *
from formulas import *
from std_modelcheck import ModelChecker


def consistency_checker(sample, formula, model_type='kripke', formula_type='ctl'):
	for structure in sample.positive:
		checker = ModelChecker(model=structure, formula=formula, model_type=model_type, formula_type=formula_type)
		if not checker.check():
			print('Positive example')
			print(structure)
			return False
	for structure in sample.negative:
		checker = ModelChecker(model=structure, formula=formula, model_type=model_type, formula_type=formula_type)
		if checker.check():
			print('Negative example')
			print(structure)
			return False
	return True

class Sample:
	'''
	contains the sample of postive and negative examples
	'''
	def __init__(self, positive=[], negative=[], propositions=[], formula=None):

		self.positive = positive
		self.negative = negative
		self.propositions = propositions
		self.formula = formula

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
	def __init__(self, positive=[], negative=[], propositions=[], formula=None):
		super().__init__(positive, negative, propositions, formula)
	
	def read_sample(self, file_path):
		
		with open(file_path, 'r') as file:
			lines = file.read()
			info = lines.split('---\n---\n---\n')	
			
			#if len(info) == 1:

			print(len(info))
			if len(info) == 2:
				positive_str, negative_str = info
				self.formula = None
			elif len(info) == 3:
				positive_str, negative_str, formula_str = info
				self.formula = CTLFormula.convertTextToFormula(formula_str)
			else:
				raise Exception("File format not correct for file %s"%(file_path))

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

	def generate_random(self, 
					 file_path, 
					 total_num_positive=10, 
					 total_num_negative=10, 
					 model_size=(2,10),
					 model_deg=3,
					 formula=None,
					 total_trials=10000,
					 write=True):
		'''
		Generates a random sample of Kripke structures
		'''
		positive = []
		negative = []

		trials = 0
		num_positive = 0
		num_negative = 0
		print('Method: Standard Random Generation')
		while True:
			
			trials += 1
			if trials == total_trials:
				break
			if trials%1000 == 0:
				print('- Trials: %d, Positive: %d, Negative: %d'%(trials, num_positive, num_negative))
			
			transition_density = random.choices(['low', 'medium', 'high'], [0.7, 0.2, 0.1], k=1)[0]
			num_states = random.randint(model_size[0], model_size[1])
			max_deg = random.randint(model_deg-1, model_deg+1)
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

		self.formula = formula
		self.calc_stats()
		print('##### Generated! Positive: %d, Negative: %d, Trials: %d #####'%(self.num_positive, self.num_negative, trials))		
		if write:
			self.write(file_path)

	def generate_random_split(self, 
					 file_path,
					 total_num_positive=10,
					 total_num_negative=10,
					 model_size=(2,10),
					 model_deg=3,
					 formula=None, 
					 total_trials=10000,
					 write=True):
		'''
		Special function that generates a random sample of Kripke structures by spliting the size of structures
		'''
		
		num_positive = 0
		num_negative = 0
		trials1 = 0
		total_intermediate_trials = total_trials//10
		print('Method: Splitting-based Random Generation')
		# For positive examples
		while True:
			trials1 += 1
			
			if trials1 == total_trials or num_positive == total_num_positive:
				break

			if trials1%200 == 0:
				print('- Trials: %d, Positive: %d, Negative: %d'%(trials1, num_positive, num_negative))
			
			transition_density_1 = random.choices(['low', 'medium', 'high'], [0.7, 0.2, 0.1], k=1)[0]
			num_states_1 = random.randint(model_size[0]//2, model_size[1]//2)
			max_deg_1 = random.randint(model_deg-1, model_deg+1)
			positive_1 = None
			intermediate_trials = 0
			while True:
				intermediate_trials += 1
				if intermediate_trials == total_intermediate_trials:
					break
				try:
					rand_kripke_1 = generate_random_kripke(max_deg_1, max_deg_1, num_states_1, transition_density_1, self.propositions)
				except:
					continue
				checker = ModelChecker(model=rand_kripke_1, formula=formula)
				if checker.check():
					positive_1 = rand_kripke_1 
					break
			
			positive_2 = None
			transition_density_2 = random.choices(['low', 'medium', 'high'], [0.7, 0.2, 0.1], k=1)[0]
			num_states_2 = random.randint(model_size[0]//2, model_size[1]//2)
			max_deg_2 = random.randint(model_deg-1, model_deg+1)
			intermediate_trials = 0
			while True:
				intermediate_trials += 1
				if intermediate_trials == total_intermediate_trials:
					break
				try:
					rand_kripke_2 = generate_random_kripke(max_deg_2, max_deg_2, num_states_2, transition_density_2, self.propositions)
				except:
					continue
				checker = ModelChecker(model=rand_kripke_2, formula=formula)
				if checker.check():
					positive_2 = rand_kripke_2 
					break
			if positive_1 == None or positive_2 == None:
				continue
			#print('Found two models')
			rand_kripke = merge_kripkes(positive_1, positive_2)
			checker = ModelChecker(model=rand_kripke, formula=formula)

			if checker.check():
				self.positive.append(rand_kripke)
				num_positive += 1

		# For negative examples
		trials2 = 0
		while True:
			trials2 += 1
			if trials2 == total_trials or num_negative == total_num_negative:
				break
			if trials2%200 == 0:
				print('- Trials: %d, Positive: %d, Negative: %d'%(trials2, num_positive, num_negative))
			
			transition_density_1 = random.choices(['low', 'medium', 'high'], [0.7, 0.2, 0.1], k=1)[0]
			num_states_1 = random.randint(model_size[0]//2, model_size[1]//2)
			max_deg_1 = random.randint(model_deg-1, model_deg+1)
			intermediate_trials = 0
			negative_1 = None
			while True:
				intermediate_trials += 1
				if intermediate_trials == total_intermediate_trials:
					break
				try:
					rand_kripke_1 = generate_random_kripke(max_deg_1, max_deg_1, num_states_1, transition_density_1, self.propositions)
				except:
					continue
				checker = ModelChecker(model=rand_kripke_1, formula=formula)
				if not checker.check():
					negative_1 = rand_kripke_1
					break

			transition_density_2 = random.choices(['low', 'medium', 'high'], [0.7, 0.2, 0.1], k=1)[0]
			num_states_2 = random.randint(model_size[0]//2, model_size[1]//2)
			max_deg_2 = random.randint(model_deg-1, model_deg+1)
			intermediate_trials = 0
			negative_2 = None
			while True:
				intermediate_trials += 1
				if intermediate_trials == total_intermediate_trials:
					break
				try:
					rand_kripke_2 = generate_random_kripke(max_deg_2, max_deg_2, num_states_2, transition_density_2, self.propositions)
				except:
					continue
				checker = ModelChecker(model=rand_kripke_2, formula=formula)
				if not checker.check():
					negative_2 = rand_kripke_2 
					break
			if negative_1 == None or negative_2 == None:
				continue	
			rand_kripke = merge_kripkes(negative_1, negative_2)
			checker = ModelChecker(model=rand_kripke, formula=formula)

			if not checker.check():
				self.negative.append(rand_kripke)
				num_negative += 1

			
		self.formula = formula
		self.calc_stats()
		print('##### Generated! Positive: %d, Negative: %d, Trials: %d #####'%(self.num_positive, self.num_negative, trials1+trials2))		
		if write:
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



class SampleCGS(Sample):
	'''
	Sample of positive and negative Concurrent Game Structures
	'''
	def __init__(self, positive=[], negative=[], propositions=[], formula=None):
		super().__init__(positive, negative, propositions, formula)

	def calc_stats(self):
		self.num_positive = len(self.positive)
		self.num_negative = len(self.negative)
		self.num_total = self.num_positive + self.num_negative
		all_props = []
		for structure in self.positive+self.negative:
			all_props += structure.propositions
		self.propositions = list(set(all_props))
		self.num_props = len(self.propositions)
		self.num_players = len(self.positive[0].players)

	def read_sample(self, file_path):
		
		with open(file_path, 'r') as file:
			lines = file.read()
			info = lines.split('---\n---\n---\n')	
			self.players = None

			if len(info) == 2:
				positive_str, negative_str = info
				self.formula = None
			elif len(info) == 3:
				positive_str, negative_str, formula_str = info
				self.formula = ATLFormula.convertTextToFormula(formula_str)

			# Read positive examples
			cgs_strs = positive_str.split('---\n---\n')
			for cgs_str in cgs_strs:
				c = ConcurrentGameStructure(init_states=[], transitions={}, labels={}, propositions=[], players=[])
				c.read_structure(cgs_str)
				self.positive.append(c)
				if self.players == None:
					self.players = c.players
				else:
					if self.players != c.players:
						raise('Mismatch of players in different CGS')
			# Read negative examples
			cgs_strs = negative_str.split('---\n---\n')
			for cgs_str in cgs_strs:
				c = ConcurrentGameStructure(init_states=[], transitions={}, labels={}, propositions=[], players=[])
				c.read_structure(cgs_str)
				self.negative.append(c)
			

			self.calc_stats()
			self.write(file_path)

	def generate_random(self, 
					 file_path, 
					 total_num_positive=10, 
					 total_num_negative=10, 
					 model_size=(2,10),
					 model_deg=3,
					 formula=None,
					 players=[0,1],
					 total_trials=10000,
					 turn_based=True,
					 write=True
					 ):
		'''
		Generates a random sample of Kripke structures
		'''
		trials = 0
		num_positive = 0
		num_negative = 0
		print('Method: Standard Random Generation')
		while True:
			
			trials += 1
			if trials == total_trials:
				break
			if trials%1000 == 0:
				print('- Trials: %d, Positive: %d, Negative: %d'%(trials, num_positive, num_negative))
			
			transition_density = random.choices(['low', 'high'], [0.8, 0.2], k=1)[0]
			num_states = random.randint(model_size[0], model_size[1])
			max_deg = random.randint(model_deg-1, model_deg+1)
			try:
				rand_cgs = generate_random_cgs(max_in_deg=max_deg, max_out_deg=max_deg, num_states=num_states,\
								transition_density=transition_density, propositions=self.propositions, \
								players=players, turn_based=turn_based)
			except:
				continue
			checker = ModelChecker(model=rand_cgs, formula=formula, model_type='cgs', formula_type='atl')

			if checker.check() and num_positive < total_num_positive:
				self.positive.append(rand_cgs)
				num_positive += 1
			elif not checker.check() and num_negative < total_num_negative:
				self.negative.append(rand_cgs)
				num_negative += 1
			elif num_positive == total_num_positive and num_negative == total_num_negative:
				break

		self.formula = formula
		self.calc_stats()
		print('##### Generated! Positive: %d, Negative: %d, Trials: %d #####'%(self.num_positive, self.num_negative, trials))		
		if write:
			self.write(file_path)

	def write(self, file_path):
		# create file path if it does not exist
		
		with open(file_path, 'w') as file:
			file.write('---\n---\n'.join([cgs.to_string() for cgs in self.positive]))
			file.write('---\n---\n---\n')
			file.write('---\n---\n'.join([cgs.to_string() for cgs in self.negative]))
			if self.formula != None:
				file.write('---\n---\n---\n')
				file.write(str(self.formula))

#s = SampleKripke()
#s.read_sample('sample_kr.sp')
#example = s.positive[1]
#example.show()
#print(example)

#formula_list = ['EF(p)', 'AG(p)', 'EU(p,q)', '&(EF(p),AX(q))']


#formula = CTLFormula.convertTextToFormula(formula_list[1])
#print(formula)
#sample = SampleKripke(positive=[], negative=[], propositions=['p', 'q'])
#sample.generate_random('random_sample.sp', 30, 30, formula, 10000)


#formula = ATLFormula.convertTextToFormula('!(<1>F(g))')
#sample = SampleCGS()
#sample_path = 'sample_cgs.sp'
#sample.read_sample(sample_path)
#print(consistency_checker(sample, formula, model_type='cgs', formula_type='atl'))

#formula_list = ['EF(p)', 'AG(p)', 'EU(p,q)', '&(EF(p),AX(q))', 'AG(->(p,AF(q)))']
#formula = CTLFormula.convertTextToFormula(formula_list[4])

#sample = SampleKripke(positive=[], negative=[], propositions=['p', 'q'])
#total_num_positive = 60
#total_num_negative = 60
#model_size = (40,50)
#deg = 4

#sample.generate_random('random_sample.sp', total_num_positive, total_num_negative, model_size, deg, formula, 1000)
#if sample.num_positive != total_num_positive or sample.num_negative != total_num_negative:
#	print('Need to generate more %d postive and %d negative examples'%(total_num_positive-sample.num_positive, total_num_negative-sample.num_negative))
#	sample.generate_random_split('random_sample.sp', total_num_positive-sample.num_positive, \
#							  	total_num_negative-sample.num_negative, model_size, deg, formula, 1000)
	
#print(consistency_checker(sample, formula))

# formula = ATLFormula.convertTextToFormula('!(<1>F(g))')
# sample = SampleCGS(positive=[], negative=[], propositions=['p', 'q'])
# total_num_positive = 5
# total_num_negative = 5
# model_size = (5,10)
# players=[0,1]
# deg = 4

# sample.generate_random('random_sample.sp', total_num_positive, total_num_negative, model_size, deg, formula, players, 1000)