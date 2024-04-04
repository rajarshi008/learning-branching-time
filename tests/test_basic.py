import os
from formulas import CTLFormula
from graph_structures import Kripke
from sample import SampleKripke
from std_modelcheck import *


# Testing formula classes
def test_formulas():
    formula = CTLFormula.convertTextToFormula("EU(&(EG(p),AF(q)),q)")
    print(os.getcwd())
    assert(formula.label == 'EU')
    assert(formula.left.label == '&')
    assert(formula.right.label == 'q')
    assert(formula.getNumberOfSubformulas() == 6)
    assert(formula.prettyPrint() == '(E(((EG p) & (AF q)) U q))')

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
    print(kripke.labels, actual_labels )
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
    sample = SampleKripke()
    sample_path = os.path.join(os.path.dirname(__file__), 'inputs', 'example_sample.sp')
    sample.read_sample(sample_path)
    assert(len(sample.positive) == 2)
    assert(len(sample.negative) == 2)

    for structure in sample.negative:
        assert(type(structure) == Kripke)
        print(structure)
        assert(len(structure.states) == 4)
        assert(len(structure.propositions) == 2)

# Testing standard CTL model checking
def test_modelcheck_ctl():
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
    
test_modelcheck_ctl()