import os
from formulas import CTLFormula
from graph_structures import Kripke, ConcurrentGameStructure
from sample import SampleKripke
from std_modelcheck import *
from operators import *
from learn_formulas import LearnFramework

# Testing formula classes
def test_ctl_formulas():
	formula = CTLFormula.convertTextToFormula("EU(&(EG(p),AF(q)),q)")
	
	assert(formula.label == 'EU')
	assert(formula.left.label == '&')
	assert(formula.right.label == 'q')
	assert(formula.getNumberOfSubformulas() == 6)
	assert(formula.prettyPrint() == '(E(((EG p) & (AF q)) U q))')

def test_atl_formulas():
	formula = ATLFormula.convertTextToFormula("&(<01>F(p),<1>U(p,<0>G(q)))")
	
	assert(formula.label == '&')
	assert(formula.left.label[-1] == 'F')
	assert(formula.left.players == {0,1})
	assert(formula.right.label[-1] == 'U')
	assert(formula.right.players == {1})

	assert(formula.getNumberOfSubformulas() == 6)


# Testing graph structures
def test_structures():

	#Kripke 1
	kripke = Kripke(init_states=set(), transitions={}, labels={}, propositions=set())
	structure_path = os.path.join(os.path.dirname(__file__), 'inputs', 'example_kripke1.str')
	kripke.read_structure_file(structure_path)
	actual_labels = {0: {'p','q'}, 1: {'q'}, 2: set(), 3: {'p'}}
	actual_transitions = {0: {0}, 1: {2}, 2: {0, 3}, 3: {3}}
	actual_states = {0, 1, 2, 3}
	actual_init_states = {0}
	actual_propositions = {'p', 'q'}

	assert(kripke.labels == actual_labels)
	assert(kripke.transitions == actual_transitions)
	assert(kripke.states == actual_states)
	assert(kripke.init_states == actual_init_states)
	assert(kripke.propositions == actual_propositions)
	assert(len(kripke.states) == 4)

	#Kripke2
	kripke = Kripke(init_states=set(), transitions={}, labels={}, propositions=set())
	structure_path = os.path.join(os.path.dirname(__file__), 'inputs', 'example_kripke2.str')
	kripke.read_structure_file(structure_path)
	actual_labels = {0: {'p'}, 1: {'p'}, 2: {'q'}, 3: set(), 4: {'p'}}
	actual_transitions = {0: {1, 3}, 1: {2}, 2: {2}, 3: {4}, 4: {0}}
	actual_states = {0, 1, 2, 3, 4}
	actual_init_states = {0}
	actual_propositions = {'p', 'q'}
	assert(kripke.labels == actual_labels)
	assert(kripke.transitions == actual_transitions)
	assert(kripke.states == actual_states)
	assert(kripke.init_states == actual_init_states)
	assert(kripke.propositions == actual_propositions)
	assert(len(kripke.states) == 5)
   


# Testing sample classes
def test_samples():
	sample = SampleKripke(positive=[], negative=[], propositions=[])
	sample_path = os.path.join(os.path.dirname(__file__), 'inputs', 'example_sample.sp')
	sample.read_sample(sample_path)
	assert(len(sample.positive) == 2)
	assert(len(sample.negative) == 2)

	for structure in sample.negative:
		assert(type(structure) == Kripke)
		assert(len(structure.states) == 4)
		assert(len(structure.propositions) == 2)

# Testing standard CTL model checking
def test_modelcheck_ctl():
	
	# One sample many formulas
	#Kripke 2
	kripke = Kripke(init_states=set(), transitions={}, labels={}, propositions=set())
	structure_path = os.path.join(os.path.dirname(__file__), 'inputs', 'example_kripke2.str')
	kripke.read_structure_file(structure_path)

	#Formulas
	formula_results = [
		('p', True),
		('AX(p)', False),
		('EX(p)', True),
		('AG(p)', False),
		('EG(p)', False),
		('AF(p)', True),
		('EF(p)', True),
		('AU(p,q)', False),
		('EU(p,q)', True),
	]

	for formula_str, expected_result in formula_results:
		formula = CTLFormula.convertTextToFormula(formula_str)
		modelchecker = ModelChecker(model=kripke, formula=formula)
		result = modelchecker.check()
		#print(modelchecker.SatSetCTL)
		assert result == expected_result
	
	# Different sample for specific formula
	
	name_list = [('sample_EX.sp', 'EX(p)'), ('sample_EG.sp', 'EG(p)'), ('sample_EF.sp', 'EF(p)'), ('sample_EU.sp', 'EU(p,q)')]
	for name in name_list:
		
		sample = SampleKripke(positive=[], negative=[], propositions=[])
		sample_path = os.path.join(os.path.dirname(__file__), 'inputs', name[0])
		sample.read_sample(sample_path)
		
		formula = CTLFormula.convertTextToFormula(name[1])
		result = consistency_checker(sample, formula)
		assert result == True, "Failed for formula %s"%formula.prettyPrint()
	


def test_learning():
	
	name_list = [('sample_EX.sp', 'EX(p)'), ('sample_EG.sp', 'EG(p)'), ('sample_EF.sp', 'EF(p)'), ('sample_EU.sp', 'EU(p,q)')]
	
	for name in name_list:
		
		sample_path = os.path.join(os.path.dirname(__file__), 'inputs', name[0])
		learn = LearnFramework(sample_file=sample_path, size_bound=4, operators=ctl_operators)
		learned_formula = learn.learn_ctl()
		original_formula = CTLFormula.convertTextToFormula(name[1])
		
		assert learned_formula.prettyPrint() == original_formula.prettyPrint(), "Failed for formula %s"%original_formula.prettyPrint()
		
def test_cgs():
	c = ConcurrentGameStructure()
	with open('example.cgs', 'r') as file:
		string = file.read()
		c.read_structure(string)
	
	assert(c.size == 4)
	assert(c.players == [0,1])
	assert(c.init_states == {0})
	assert(c.propositions == {'o', 'i', 'r','g'})
	
