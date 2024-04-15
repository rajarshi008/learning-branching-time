from formulas import CTLFormula
from sample import SampleKripke
from operators import *
from pysmt.shortcuts import Symbol, And, Or, Implies, Solver, Not, ExactlyOne, Bool, Iff

class CTLSATEncoding:
	
	def __init__(self, sample, propositions, operators, solver_name, neg_props):
		
		
		self.solver = Solver(name=solver_name)
		self.sample = sample
		self.propositions = propositions
		self.operators = operators

		self.unary_operators = ctl_unary
		self.binary_operators = ctl_binary

		self.neg_props = neg_props
		self.neg_propositions = list(map(lambda x: '!'+x, self.propositions)) if self.neg_props else []
		self.operators_and_propositions = self.operators + self.propositions + self.neg_propositions

		# initializing the variables
		self.x = {}
		self.r = {}
		self.l = {}
		self.y = {}
		self.aux_y = {}

	"""
	the working variables are 
		- x[i][o]: i is a subformula (row) identifier, o is an operator or a propositional variable. Meaning is "subformula i is an operator (variable) o"
		- l[i][j]:  "left operand of subformula i is subformula j"
		- r[i][j]: "right operand of subformula i is subformula j"
		- y[i][tr][t]: semantics of formula i at state s of kripke M
	"""
	def encodeFormula(self, formula_size):
		
		#print('Preparing encoding for size %d'%formula_size)

		self.x.update({ (formula_size - 1, o) : Symbol('x_%d_%s'%(formula_size-1,o)) for o in self.operators_and_propositions})

		self.l.update({(formula_size - 1, childOperator) : Symbol('l_%d_%d'%(formula_size - 1,childOperator))\
												 for childOperator in range(formula_size-1)})
		
		self.r.update({(formula_size - 1, childOperator) : Symbol('r_%d_%d'%(formula_size - 1,childOperator))\
												 for childOperator in range(formula_size-1)})

		self.y.update({ (formula_size - 1, kripke_id, state): Symbol('y_%d_%d_%d'%(formula_size - 1,kripke_id,state))
						for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative) for state in kripke.states})
		
		self.aux_y.update({(formula_size - 1, kripke_id, state, dist): Symbol('y_%d_%d_%d_%d'%(formula_size - 1,kripke_id,state,dist))
						for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative) for state in kripke.states
						for dist in range(kripke.size+1)})
		
		if formula_size > 1:
			self.solver.pop()
			self.solver.pop()

		#if formula_size == 3:
		#	self.solver.add_assertion(And([self.x[(2, '&')], self.x[(1, 'p')], self.x[(0, 'q')], self.l[(2, 1)], self.r[(2, 0)]]))
		#	self.solver.add_assertion(And([self.x[(1, 'AX')], self.x[(0, 'q')], self.l[(1, 0)]]))

		# Structural Constraints
		self.exactlyOneOperator(formula_size)	   
		self.firstOperatorProposition(formula_size)	
		#self.noDanglingNodes(formula_size)
		
		# Semantic Constraints
		self.propositionsSemantics(formula_size)
		self.operatorsSemantics(formula_size) #<---
		self.solver.push()

		# Consistency Constraints
		self.consistency(formula_size)
		self.solver.push()
		

		#self.solver.minimize(self.fr[formula_size-1])

	def consistency(self, formula_size):
		for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
			if kripke_id < self.sample.num_positive:
				self.solver.add_assertion(Or([self.y[(formula_size - 1, kripke_id, state)] for state in kripke.init_states]))
			else:
				self.solver.add_assertion(And([Not(self.y[(formula_size - 1, kripke_id, state)]) for state in kripke.init_states]))

	def propositionsSemantics(self, formula_size):

		i = formula_size-1

		for p in self.propositions:
			for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
				self.solver.add_assertion(Implies(self.x[(i, p)],\
									And([Iff(self.y[(i, kripke_id, state)], Bool(p in kripke.labels[state]))\
									for state in kripke.states\
										])))
		if self.neg_props:
			for p in self.neg_propositions:
				for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
					self.solver.add_assertion(Implies(self.x[(i, p)],\
										And([Iff(self.y[(i, kripke_id, state)], (Bool(p not in kripke.labels[state])))\
										for state in kripke.states\
											])))

		
	def exactlyOneOperator(self, formula_size):
		
		i = formula_size - 1
		
		self.solver.add_assertion(ExactlyOne([self.x[k] for k in self.x if k[0] == i]))
		
		self.solver.add_assertion(Implies(Or([self.x[(i, op)] for op in self.propositions]),\
										And(Not(Or([self.l[k] for k in self.l if k[0] == i])),\
			  								Not(Or([self.r[k] for k in self.r if k[0] == i]))\
											)))
			

		if i > 0:
			
			self.solver.add_assertion(Implies(Or([self.x[(i, op)] for op in self.operators]),\
												ExactlyOne([self.l[k] for k in self.l if k[0]==i])))										  

			self.solver.add_assertion(Implies(Or([self.x[(i, op)] for op in self.binary_operators]),\
												ExactlyOne([self.r[k] for k in self.r if k[0] == i])))
			
			self.solver.add_assertion(Implies(Or([self.x[(i, op)] for op in self.unary_operators]),\
										Not(Or([self.r[k] for k in self.r if k[0] == i]))))


	
	def firstOperatorProposition(self, formula_size):
		i = formula_size - 1
		if i == 0:
			self.solver.add_assertion(Or([self.x[(0,prop)] for prop in self.propositions]))

	def noDanglingNodes(self, formula_size):
		i = formula_size - 1
		self.solver.add_assertion(
			And([
				Or(
					Or([self.l[(rowId, j)] for rowId in range(j+1, i+1)]),
					Or([self.r[(rowId, j)] for rowId in range(j+1, i+1)])
				)
				for j in range(formula_size-1)]
			)
		)

	def operatorsSemantics(self, formula_size):

		i = formula_size-1

		for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
			
			if '!' in self.operators:
				#negation
				self.solver.add_assertion(Implies(self.x[(i, '!')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, kripke_id, state)],\
																		Not(self.y[(only_arg, kripke_id, state)]))
																	for state in kripke.states\
																	])\
																	)\
														for only_arg in range(i)\
														])\
													))

			
			if '|' in self.operators:
				#disjunction
				self.solver.add_assertion(Implies(self.x[(i, '|')],\
														And([ Implies(\
																	   And(\
																		   [self.l[i, left_arg], self.r[i, right_arg]]\
																		   ),\
																	   	And([Iff(self.y[(i, kripke_id, state)],
																	   			Or(self.y[(left_arg, kripke_id, state)], self.y[(right_arg, kripke_id, state)]))
																	   			for state in kripke.states\
																			])\
																	   )\
																	  for left_arg in range(i) for right_arg in range(i) ])))

			

			
			if '&' in self.operators:
				#conjunction
				self.solver.add_assertion(Implies(self.x[(i, '&')],\
														And([ Implies(\
																	   And(\
																		   [self.l[i, left_arg], self.r[i, right_arg]]\
																		   ),\
																	   	And([Iff(self.y[(i, kripke_id, state)],
																	   			And(self.y[(left_arg, kripke_id, state)], self.y[(right_arg, kripke_id, state)]))
																	   			for state in kripke.states\
																			])\
																	   )\
																	  for left_arg in range(i) for right_arg in range(i) ])))
				
			if '->' in self.operators:
				#implication
				self.solver.add_assertion(Implies(self.x[(i, '->')],\
														And([ Implies(\
																	   And(\
																		   [self.l[i, left_arg], self.r[i, right_arg]]\
																		   ),\
																	   	And([Iff(self.y[(i, kripke_id, state)],
																	   			Implies(self.y[(left_arg, kripke_id, state)], self.y[(right_arg, kripke_id, state)]))
																	   			for state in kripke.states\
																			])\
																	   )\
																	  for left_arg in range(i) for right_arg in range(i) ])))
				
			if 'EX' in self.operators:
				#EX
				self.solver.add_assertion(Implies(self.x[(i, 'EX')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, kripke_id, state)],\
																		Or([self.y[(only_arg, kripke_id, succ)] for succ in kripke.successors(state)]))
																	for state in kripke.states\
																	])\
																	)\
														for only_arg in range(i)\
														])\
													))
			
			if 'AX' in self.operators:
				#AX
				self.solver.add_assertion(Implies(self.x[(i, 'AX')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, kripke_id, state)],\
																		And([self.y[(only_arg, kripke_id, succ)] for succ in kripke.successors(state)]))
																	for state in kripke.states\
																	])\
																	)\
														for only_arg in range(i)\
														])\
													))
			
			if 'EG' in self.operators:
				#EG
				self.solver.add_assertion(Implies(self.x[(i, 'EG')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, kripke_id, state)],\
																		self.aux_y[(i,kripke_id,state,kripke.size)])
																	for state in kripke.states\
																	]+[self.auxConstraintsEG(i,only_arg)])\
																	)\
														for only_arg in range(i)\
														])\
													))

			if 'AG' in self.operators:
				#AG
				self.solver.add_assertion(Implies(self.x[(i, 'AG')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, kripke_id, state)],\
																		self.aux_y[(i,kripke_id,state,kripke.size)])
																	for state in kripke.states\
																	]+[self.auxConstraintsAG(i,only_arg)])\
																	)\
														for only_arg in range(i)\
														])\
													))

			if 'EF' in self.operators:
				#EF
				self.solver.add_assertion(Implies(self.x[(i, 'EF')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, kripke_id, state)],\
																		self.aux_y[(i,kripke_id,state,kripke.size)])
																	for state in kripke.states\
																	]+[self.auxConstraintsEF(i,only_arg)])\
																	)\
														for only_arg in range(i)\
														])\
													))

			if 'AF' in self.operators:
				#AG
				self.solver.add_assertion(Implies(self.x[(i, 'AF')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, kripke_id, state)],\
																		self.aux_y[(i,kripke_id,state,kripke.size)])
																	for state in kripke.states\
																	]+[self.auxConstraintsAF(i,only_arg)])\
																	)\
														for only_arg in range(i)\
														])\
													))
			
			if 'EU' in self.operators:
				#EU
				self.solver.add_assertion(Implies(self.x[(i, 'EU')],\
													And([\
														Implies(\
																	And(self.l[(i,left_arg)], self.r[(i,right_arg)]),\
																	And([Iff(self.y[(i, kripke_id, state)],\
																		self.aux_y[(i,kripke_id,state,kripke.size)])
																	for state in kripke.states\
																	]+[self.auxConstraintsEU(i,left_arg,right_arg)])\
																	)\
														for left_arg in range(i) for right_arg in range(i)\
														])\
													))

			if 'AU' in self.operators:
				#AU
				self.solver.add_assertion(Implies(self.x[(i, 'AU')],\
													And([\
														Implies(\
																	And(self.l[(i,left_arg)], self.r[(i,right_arg)]),\
																	And([Iff(self.y[(i, kripke_id, state)],\
																		self.aux_y[(i,kripke_id,state,kripke.size)])
																	for state in kripke.states\
																	]+[self.auxConstraintsAU(i,left_arg,right_arg)])\
																	)\
														for left_arg in range(i) for right_arg in range(i)\
														])\
													))
	
	
	def auxConstraintsEG(self, i, j):
		
		aux_formula = Bool(True)
		for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
			for state in kripke.states:
				aux_formula = And(aux_formula, Iff(self.aux_y[(i, kripke_id, state, 0)], self.y[(j, kripke_id, state)]))
				aux_formula = And([aux_formula]+[Iff(\
											self.aux_y[(i, kripke_id, state, dist+1)],\
											And(self.y[(j, kripke_id, state)],
			   								Or([self.aux_y[(i, kripke_id, succ, dist)] for succ in kripke.successors(state)]))\
											) for dist in range(kripke.size)])
		return aux_formula
	
	
	
	def auxConstraintsAG(self, i, j):

		aux_formula = Bool(True)
		for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
			for state in kripke.states:
				aux_formula = And(aux_formula, Iff(self.aux_y[(i, kripke_id, state, 0)], self.y[(j, kripke_id, state)]))
				aux_formula = And([aux_formula]+[Iff(\
											self.aux_y[(i, kripke_id, state, dist+1)],\
											And(self.y[(j, kripke_id, state)],
			   								And([self.aux_y[(i, kripke_id, succ, dist)] for succ in kripke.successors(state)]))\
											) for dist in range(kripke.size)])
		return aux_formula
	
	
	
	def auxConstraintsEF(self, i, j):

		aux_formula = Bool(True)
		for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
			for state in kripke.states:
				aux_formula = And(aux_formula, Iff(self.aux_y[(i, kripke_id, state, 0)], self.y[(j, kripke_id, state)]))
				aux_formula = And([aux_formula]+[Iff(\
											self.aux_y[(i, kripke_id, state, dist+1)],\
											Or(self.aux_y[(i, kripke_id, state, dist)],
			   								Or([self.aux_y[(i, kripke_id, succ, dist)] for succ in kripke.successors(state)]))\
											) for dist in range(kripke.size)])
		return aux_formula
	
	def auxConstraintsAF(self, i, j):

		aux_formula = Bool(True)
		for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
			for state in kripke.states:
				aux_formula = And(aux_formula, Iff(self.aux_y[(i, kripke_id, state, 0)], self.y[(j, kripke_id, state)]))
				aux_formula = And([aux_formula]+[Iff(\
											self.aux_y[(i, kripke_id, state, dist+1)],\
											Or(self.aux_y[(i, kripke_id, state, dist)],
			   								And([self.aux_y[(i, kripke_id, succ, dist)] for succ in kripke.successors(state)]))\
											) for dist in range(kripke.size)])
		return aux_formula

	def auxConstraintsEU(self, i, j, k):

		aux_formula = Bool(True)
		for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
			for state in kripke.states:
				aux_formula = And(aux_formula, Iff(self.aux_y[(i, kripke_id, state, 0)], self.y[(k, kripke_id, state)]))
				aux_formula = And([aux_formula]+[Iff(\
											self.aux_y[(i, kripke_id, state, dist+1)],\
											Or(self.aux_y[(i, kripke_id, state, dist)],
			  								And(self.y[(j,kripke_id, state)],\
			   								Or([self.aux_y[(i, kripke_id, succ, dist)] for succ in kripke.successors(state)])))\
											) for dist in range(kripke.size)])
		return aux_formula

	def auxConstraintsAU(self, i, j, k):
	
		aux_formula = Bool(True)
		for kripke_id, kripke in enumerate(self.sample.positive + self.sample.negative):
			for state in kripke.states:
				aux_formula = And(aux_formula, Iff(self.aux_y[(i, kripke_id, state, 0)], self.y[(k, kripke_id, state)]))
				aux_formula = And([aux_formula]+[Iff(\
											self.aux_y[(i, kripke_id, state, dist+1)],\
											Or(self.aux_y[(i, kripke_id, state, dist)],
			  								And(self.y[(j,kripke_id, state)],\
			   								And([self.aux_y[(i, kripke_id, succ, dist)] for succ in kripke.successors(state)])))\
											) for dist in range(kripke.size)])
		return aux_formula
	

	def reconstructWholeFormula(self, model, formula_size):

		return self.reconstructFormula(model, formula_size-1)

		
	def reconstructFormula(self, model, rowId):

		def getValue(row, vars):
	
			tt = [k[1] for k in vars if k[0] == row and model[vars[k]].is_true()]
			if len(tt) > 1:
				raise Exception("more than one true value")
			else:
				return tt[0]
		
		operator = getValue(rowId, self.x)
		#print(operator)
		if operator in self.propositions:
			return CTLFormula([operator, None, None])
		if operator in self.neg_propositions:
			return CTLFormula(['!', CTLFormula([operator[1:], None, None]), None])
		
		elif operator in self.unary_operators:
			left_child = getValue(rowId, self.l)
			left_formula = self.reconstructFormula(model, left_child)
			return CTLFormula([operator, left_formula, None])
		
		elif operator in self.binary_operators:
			left_child = getValue(rowId, self.l)
			right_child = getValue(rowId, self.r)
			left_formula = self.reconstructFormula(model, left_child)
			right_formula = self.reconstructFormula(model, right_child)
			return CTLFormula([operator, left_formula, right_formula])
		
	