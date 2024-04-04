from graph_structures import *

class Sample:
	'''
	contains the sample of postive and negative examples
	'''
	def __init__(self, positive=[], negative=[], propositions=[]):

		self.positive = positive
		self.negative = negative
	
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
	def __init__(self, positive=[], negative=[], alphabet=[]):
		super().__init__(positive, negative, alphabet)
	
	def read_sample(self, file_path):
		
		with open(file_path, 'r') as file:
			lines = file.read()
			positive_str, negative_str = lines.split('---\n---\n---\n')	
			
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

#s = SampleKripke()
#s.read_sample('tests/inputs/example_sample.sp')
#example = s.positive[1]
#example.show()
#print(example)