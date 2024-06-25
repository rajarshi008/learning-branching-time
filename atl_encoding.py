from formulas import ATLFormula
from sample import SampleCGS
from operators import *
from pysmt.shortcuts import Symbol, And, Or, Implies, Solver, Not, ExactlyOne, Bool, Iff

class ATLSATEncoding:
	
	def __init__(self, sample, propositions, operators, solver_name, turn_based):
		
		self.solver = Solver(name=solver_name)
		self.sample = sample
		self.propositions = propositions
		self.operators = operators

		self.unary_operators = [op for op in operators if op in atl_unary]
		self.binary_operators = [op for op in operators if op in atl_binary]
		self.temporal_operators = [op for op in operators if op in atl_temporal]
		self.operators_and_propositions = self.operators + self.propositions
		self.turn_based = turn_based

		# initializing the variables
		self.x = {}
		self.r = {}
		self.l = {}
		self.y = {}
		self.aux_y = {}
		self.A = {}

	"""
	the working variables are 
		- x[i][o]: i is a subformula (row) identifier, o is an operator or a propositional variable. Meaning is "subformula i is an operator (variable) o"
		- l[i][j]:  "left operand of subformula i is subformula j"
		- r[i][j]: "right operand of subformula i is subformula j"
		- y[i][tr][t]: semantics of formula i at state s of cgs M
	"""
	def encodeFormula(self, formula_size):
		
		#print('Preparing encoding for size %d'%formula_size)

		self.x.update({ (formula_size - 1, o) : Symbol('x_%d_%s'%(formula_size-1,o)) for o in self.operators_and_propositions})

		self.l.update({(formula_size - 1, childOperator) : Symbol('l_%d_%d'%(formula_size - 1,childOperator))\
												 for childOperator in range(formula_size-1)})
		
		self.r.update({(formula_size - 1, childOperator) : Symbol('r_%d_%d'%(formula_size - 1,childOperator))\
												 for childOperator in range(formula_size-1)})

		self.A.update({(formula_size - 1, player): Symbol('A_%d_%d'%(formula_size - 1, player)) for player in self.sample.players})

		self.y.update({ (formula_size - 1, cgs_id, state): Symbol('y_%d_%d_%d'%(formula_size - 1,cgs_id,state))
						for cgs_id, cgs in enumerate(self.sample.positive + self.sample.negative) for state in cgs.states})
		
		self.aux_y.update({(formula_size - 1, cgs_id, state, dist): Symbol('y_%d_%d_%d_%d'%(formula_size - 1,cgs_id,state,dist))
						for cgs_id, cgs in enumerate(self.sample.positive + self.sample.negative) for state in cgs.states
						for dist in range(cgs.size+1)})

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
		for cgs_id, cgs in enumerate(self.sample.positive + self.sample.negative):
			if cgs_id < self.sample.num_positive:
				self.solver.add_assertion(Or([self.y[(formula_size - 1, cgs_id, state)] for state in cgs.init_states]))
			else:
				self.solver.add_assertion(And([Not(self.y[(formula_size - 1, cgs_id, state)]) for state in cgs.init_states]))

	def propositionsSemantics(self, formula_size):

		i = formula_size-1

		for p in self.propositions:
			for cgs_id, cgs in enumerate(self.sample.positive + self.sample.negative):
				self.solver.add_assertion(Implies(self.x[(i, p)],\
									And([Iff(self.y[(i, cgs_id, state)], Bool(p in cgs.labels[state]))\
									for state in cgs.states\
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

		for cgs_id, cgs in enumerate(self.sample.positive + self.sample.negative):
			
			if '!' in self.operators:
				#negation
				self.solver.add_assertion(Implies(self.x[(i, '!')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, cgs_id, state)],\
																		Not(self.y[(only_arg, cgs_id, state)]))
																	for state in cgs.states\
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
																	   	And([Iff(self.y[(i, cgs_id, state)],
																	   			Or(self.y[(left_arg, cgs_id, state)], self.y[(right_arg, cgs_id, state)]))
																	   			for state in cgs.states\
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
																	   	And([Iff(self.y[(i, cgs_id, state)],
																	   			And(self.y[(left_arg, cgs_id, state)], self.y[(right_arg, cgs_id, state)]))
																	   			for state in cgs.states\
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
																	   	And([Iff(self.y[(i, cgs_id, state)],
																	   			Implies(self.y[(left_arg, cgs_id, state)], self.y[(right_arg, cgs_id, state)]))
																	   			for state in cgs.states\
																			])\
																	   )\
																	  for left_arg in range(i) for right_arg in range(i) ])))
				
			if 'X' in self.operators:
				#X
				self.solver.add_assertion(Implies(self.x[(i, 'X')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, cgs_id, state)],\
																		self.preConstraint(i, only_arg, cgs, cgs_id, state))
																	for state in cgs.states\
																	])\
																	)\
														for only_arg in range(i)\
														])\
													))
			
			if 'F' in self.operators:
				#F
				self.solver.add_assertion(Implies(self.x[(i, 'F')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, cgs_id, state)],\
																		self.aux_y[(i,cgs_id,state,cgs.size)])
																	for state in cgs.states\
																	]+[self.auxConstraintsF(i,only_arg)])\
																	)\
														for only_arg in range(i)\
														])\
													))
			
			if 'G' in self.operators:
				#G
				self.solver.add_assertion(Implies(self.x[(i, 'G')],\
													And([\
														Implies(\
																	self.l[(i,only_arg)],\
																	And([Iff(self.y[(i, cgs_id, state)],\
																		self.aux_y[(i, cgs_id, state, cgs.size)])
																	for state in cgs.states\
																	]+[self.auxConstraintsG(i,only_arg)])\
																	)\
														for only_arg in range(i)\
														])\
													))
			
			
			if 'U' in self.operators:
				#U
				self.solver.add_assertion(Implies(self.x[(i, 'U')],\
													And([\
														Implies(\
																	And(self.l[(i,left_arg)], self.r[(i,right_arg)]),\
																	And([Iff(self.y[(i, cgs_id, state)],\
																		self.aux_y[(i,cgs_id,state,cgs.size)])
																	for state in cgs.states\
																	]+[self.auxConstraintsU(i,left_arg,right_arg)])\
																	)\
														for left_arg in range(i) for right_arg in range(i)\
														])\
													))


	def preConstraint(self, i, j, cgs, cgs_id, state):

		all_transitions = cgs.actions[state]
		
		if self.turn_based:
			state_player = cgs.state_player[state]	
			result = And(Implies(self.A[(i,state_player)],Or([self.y[(j, cgs_id, cgs.transitions[state][trans])] \
								for trans in all_transitions])),
						Implies(Not(self.A[(i,state_player)]),And([self.y[(j, cgs_id, cgs.transitions[state][trans])] \
								for trans in all_transitions])))	
		else:
			result = Or([\
					And([ Implies( And([Implies(self.A[(i,player)],Bool(trans1[player]==trans2[player]))\
											for player in cgs.players\
										]),\
				   			self.y[(j, cgs_id, cgs.transitions[state][trans2])]) \
							for trans2 in all_transitions\
						]) for trans1 in all_transitions\
					])
		
		return result
	
	def preConstraintTemporal(self, i, cgs, cgs_id, state, dist):

		all_transitions = cgs.actions[state]

		if self.turn_based:
			state_player = cgs.state_player[state]	
			result = And(Implies(self.A[(i,state_player)],Or([self.aux_y[(i, cgs_id, cgs.transitions[state][trans], dist)] \
								for trans in all_transitions])),
						Implies(Not(self.A[(i,state_player)]),And([self.aux_y[(i, cgs_id, cgs.transitions[state][trans], dist)] \
								for trans in all_transitions])))
		else:
			result = Or([\
					And([ Implies( And([Implies(self.A[(i,player)],Bool(trans1[player]==trans2[player]))\
											for player in cgs.players\
										]),\
				   			self.aux_y[(i, cgs_id, cgs.transitions[state][trans2],dist)]) \
							for trans2 in all_transitions\
						]) for trans1 in all_transitions\
					])
		return result

	def auxConstraintsF(self, i, j):
		
		aux_formula = Bool(True)
		for cgs_id, cgs in enumerate(self.sample.positive + self.sample.negative):
			for state in cgs.states:
				aux_formula = And(aux_formula, Iff(self.aux_y[(i, cgs_id, state, 0)], self.y[(j, cgs_id, state)]))
				aux_formula = And([aux_formula]+[Iff(\
											self.aux_y[(i, cgs_id, state, dist+1)],\
											Or(self.aux_y[(i, cgs_id, state, dist)],
			   								self.preConstraintTemporal(i,cgs,cgs_id,state,dist))\
											) for dist in range(cgs.size)])
		return aux_formula

	def auxConstraintsG(self, i, j):

		aux_formula = Bool(True)
		for cgs_id, cgs in enumerate(self.sample.positive + self.sample.negative):
			for state in cgs.states:
				aux_formula = And(aux_formula, Iff(self.aux_y[(i, cgs_id, state, 0)], self.y[(j, cgs_id, state)]))
				aux_formula = And([aux_formula]+[Iff(\
											self.aux_y[(i, cgs_id, state, dist+1)],\
											And(self.y[(j, cgs_id, state)],
			   								self.preConstraintTemporal(i, cgs, cgs_id, state, dist))\
											) for dist in range(cgs.size)])
		return aux_formula

	def auxConstraintsU(self, i, j, k):

		aux_formula = Bool(True)
		for cgs_id, cgs in enumerate(self.sample.positive + self.sample.negative):
			for state in cgs.states:
				aux_formula = And(aux_formula, Iff(self.aux_y[(i, cgs_id, state, 0)], self.y[(k, cgs_id, state)]))
				aux_formula = And([aux_formula]+[Iff(\
											self.aux_y[(i, cgs_id, state, dist+1)],\
											Or(self.aux_y[(i, cgs_id, state, dist)],
			  								And(self.y[(j,cgs_id, state)],\
			   								self.preConstraintTemporal(i, cgs, cgs_id, state, dist)))\
											) for dist in range(cgs.size)])
		return aux_formula

	def reconstructWholeFormula(self, model, formula_size):

		return self.reconstructFormula(model, formula_size-1)

		
	def reconstructFormula(self, model, rowId):

		def getValue(row, vars, unique=True):
			
			tt = [k[1] for k in vars if k[0] == row and model[vars[k]].is_true()]
			if unique and len(tt) > 1:
				raise Exception("more than one true value")
			else:
				return tt
		
		operator = getValue(rowId, self.x)[0]
		
		if operator in self.propositions:
			
			return ATLFormula([operator, None, None])
		
		elif operator in self.unary_operators:

			left_child = getValue(rowId, self.l)[0]
			left_formula = self.reconstructFormula(model, left_child)
			
			if operator in self.temporal_operators:
				players = getValue(rowId, self.A, False)
				operator = '<'+''.join(map(str, players))+'>'+operator
			return ATLFormula([operator, left_formula, None])
		
		elif operator in self.binary_operators:
			
			left_child = getValue(rowId, self.l)[0]
			right_child = getValue(rowId, self.r)[0]
			left_formula = self.reconstructFormula(model, left_child)
			right_formula = self.reconstructFormula(model, right_child)

			if operator in self.temporal_operators:
				players = getValue(rowId, self.A, False)
				operator = '<'+''.join(map(str, players))+'>'+operator

			return ATLFormula([operator, left_formula, right_formula])