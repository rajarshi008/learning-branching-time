from formulas import CTLFormula
from sample import SampleKripke
from graph_structures import Kripke
from operators import *


def consistency_checker(sample, formula):
	for structure in sample.positive:
		checker = ModelChecker(model=structure, formula=formula)
		if not checker.check():
			#print(structure)
			return False
	for structure in sample.negative:
		checker = ModelChecker(model=structure, formula=formula)
		if checker.check():
			#print(structure)
			return False
	return True


class ModelChecker():
	def __init__(self, model, formula, model_type='kripke', formula_type='ctl', operators=ctl_operators):
		self.model = model
		self.formula = formula
		self.model_type = model_type
		self.formula_type = formula_type

	def check(self):
		if self.model_type == 'kripke' and  self.formula_type == 'ctl':
				return self.checkCTLKripke()
		if self.model_type == 'cgs' and self.formula_type == 'atl':
			return self.check_cgs_atl() 
	
	def checkCTLKripke(self):
		
		self.SatSetCTL = {}
		sat_sets_kripke = self.computeSatSet(self.formula)
		
		if self.model.init_states & sat_sets_kripke:
			return True
		else:
			return False

	def computeSatSet(self, formula):

		if formula in self.SatSetCTL:
			return self.SatSetCTL[formula]
		else:
			
			# computing the sets for subformulas
			if formula.label in ctl_unary:
				left_set = self.computeSatSet(formula.left)
			elif formula.label in ctl_binary:
				left_set = self.computeSatSet(formula.left)
				right_set = self.computeSatSet(formula.right)
			else:
				# atomic proposition
				self.SatSetCTL[formula] = {state for state in self.model.states if formula.label in self.model.labels[state]}
				return self.SatSetCTL[formula]
					
			# case analysis for different operators
			if formula.label == '&':
				self.SatSetCTL[formula] = left_set & right_set
				return self.SatSetCTL[formula]
			
			elif formula.label == '|':
				self.SatSetCTL[formula] = left_set | right_set
				return self.SatSetCTL[formula]
			
			elif formula.label == '->':
				self.SatSetCTL[formula] = self.stateComplement(left_set) | right_set
				return self.SatSetCTL[formula]
			
			elif formula.label == '!':
				self.SatSetCTL[formula] = self.stateComplement(left_set)
				return self.SatSetCTL[formula]
			
			elif formula.label == 'EX':
				self.SatSetCTL[formula] = {state for state in self.model.states \
										   if self.model.successors(state) & left_set}
				return self.SatSetCTL[formula]
			
			elif formula.label == 'AX':
				self.SatSetCTL[formula] = {state for state in self.model.states \
										   if self.model.successors(state).issubset(left_set)}
				return self.SatSetCTL[formula]
			
			elif formula.label == 'EF':
				lfp = left_set
				while True:
					pre_lfp = {state for state in self.model.states - lfp if self.model.successors(state) & lfp}
					if pre_lfp == set():
						break
					else:
						lfp = lfp | pre_lfp
				self.SatSetCTL[formula] = lfp
				return self.SatSetCTL[formula]
			
			elif formula.label == 'AF':
				lfp = left_set
				while True:
					pre_lfp = {state for state in self.model.states - lfp if self.model.successors(state).issubset(lfp)}
					if pre_lfp == set():
						break
					else:
						lfp = lfp | pre_lfp
				self.SatSetCTL[formula] = lfp
				return self.SatSetCTL[formula]
			
			elif formula.label == 'EG':
				gfp = left_set
				while True:
					post_gfp = {state for state in gfp if not (self.model.successors(state) & gfp)}

					if post_gfp == set():
						break
					else:
						gfp = gfp - post_gfp
				
				self.SatSetCTL[formula] = gfp
				return self.SatSetCTL[formula]
			
			elif formula.label == 'AG':
				gfp = left_set
				while True:
					post_gfp = {state for state in gfp if not (self.model.successors(state).issubset(gfp))}

					if post_gfp == set():
						break
					else:
						gfp = gfp - post_gfp
				
				self.SatSetCTL[formula] = gfp
				return self.SatSetCTL[formula]
			
			elif formula.label == 'EU':
				lfp = right_set
				while True:
					pre_lfp = {state for state in left_set - lfp if self.model.successors(state) & lfp}
					if pre_lfp == set():
						break
					else:
						lfp = lfp | pre_lfp
				self.SatSetCTL[formula] = lfp
				return self.SatSetCTL[formula]
			
			elif formula.label == 'AU':
				lfp = right_set
				while True:
					pre_lfp = {state for state in left_set - lfp if self.model.successors(state).issubset(lfp)}
					if pre_lfp == set():
						break
					else:
						lfp = lfp | pre_lfp
				self.SatSetCTL[formula] = lfp
				return self.SatSetCTL[formula]

	# some aux functions
	def stateComplement(self, state_set):
		return set(self.model.states) - state_set
	

		
	def check_cgs_atl(self):
		# perform ATL model checking
		if self.formula == None:
			return None	 
	
			