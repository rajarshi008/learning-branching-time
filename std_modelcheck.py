from formulas import CTLFormula, ATLFormula
from graph_structures import Kripke, ConcurrentGameStructure
from operators import *


class ModelChecker():
	def __init__(self, model, formula, model_type='kripke', formula_type='ctl', operators=ctl_operators):
		self.model = model
		self.formula = formula
		self.model_type = model_type
		self.formula_type = formula_type

	def check(self):
		if self.formula_type == 'ctl':
				return self.checkCTLKripke()
		elif self.formula_type == 'atl':
			return self.checkATLCGS() 
	
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

	def checkATLCGS(self):
		
		self.SatSetATL = {}
		sat_sets_cgs = self.computeSatSetATL(self.formula)

		if self.model.init_states & sat_sets_cgs:
			return True
		else:
			return False
		
	def computeSatSetATL(self, formula):

		if formula in self.SatSetATL:
			return self.SatSetATL[formula]
		else:
			
			# computing the sets for subformulas
			if formula.label in atl_unary or formula.label[-1] in atl_unary:
				left_set = self.computeSatSetATL(formula.left)
			elif formula.label in atl_binary or formula.label[-1] in atl_binary:
				left_set = self.computeSatSetATL(formula.left)
				right_set = self.computeSatSetATL(formula.right)
			else:
				# atomic proposition
				self.SatSetATL[formula] = {state for state in self.model.states if formula.label in self.model.labels[state]}
				return self.SatSetATL[formula]

			# case analysis for different operators
			if formula.label == '&':
				
				self.SatSetATL[formula] = left_set & right_set
				return self.SatSetATL[formula]
			
			elif formula.label == '|':
				
				self.SatSetATL[formula] = left_set | right_set
				return self.SatSetATL[formula]
			
			elif formula.label == '->':
				
				self.SatSetATL[formula] = self.stateComplement(left_set) | right_set
				return self.SatSetATL[formula]
			
			elif formula.label == '!':
				
				self.SatSetATL[formula] = self.stateComplement(left_set)
				return self.SatSetATL[formula]

			elif formula.label[-1] == 'X':

				self.SatSetATL[formula] = self.model.predecessors_players(left_set, formula.players)
				return self.SatSetATL[formula]

			elif formula.label[-1] == 'F':

				lfp = left_set
				while True:
					pre_lfp = self.model.predecessors_players(lfp, formula.players)
					new_lfp = pre_lfp - lfp
					if new_lfp == set():
						break
					else:
						lfp = lfp | pre_lfp
				self.SatSetATL[formula] = lfp
				return self.SatSetATL[formula]
			
			elif formula.label[-1] == 'G':

				gfp = left_set
				while True:
					post_gfp = left_set & self.model.predecessors_players(gfp, formula.players)
					new_gfp = gfp - post_gfp
					if new_gfp == set():
						break
					else:
						gfp = post_gfp
				self.SatSetATL[formula] = gfp
				return self.SatSetATL[formula]

			elif formula.label[-1] == 'U':
				
				lfp = right_set
				
				while True:
					pre_lfp = left_set & self.model.predecessors_players(lfp, formula.players)
					new_lfp = pre_lfp - lfp
					if new_lfp == set():
						break
					else:
						lfp = lfp | pre_lfp
				self.SatSetATL[formula] = lfp
				return self.SatSetATL[formula]

	# some aux functions
	def stateComplement(self, state_set):
		return set(self.model.states) - state_set
	

#formula = CTLFormula.convertTextToFormula('EU(p,q)')
#sample = SampleKripke()
#sample_path = 'tests/inputs/small_example_sample.sp'
#sample.read_sample(sample_path)
#print(consistency_checker(sample, formula))

# model = ConcurrentGameStructure()
# model_path = 'tests/inputs/example_cgs.cgs'
# with open(model_path, 'r') as file:
# 	string = file.read()
# 	model.read_structure(string)
# formula = ATLFormula.convertTextToFormula('<01>U(o,r)')
# print(formula.prettyPrint())
# model.show()
# checker = ModelChecker(model, formula, model_type='cgs', formula_type='atl')
# print(checker.check())


