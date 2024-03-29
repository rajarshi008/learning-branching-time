import os
import pytest
from lark import Lark, Transformer
from formulas import CTLFormula
from graph_structures import Kripke
from sample import SampleKripke

folder_path = 'learning-branching-time/tests/'

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
    kripke = Kripke()
    structure_path = os.path.join(os.path.dirname(__file__), 'inputs', 'example_kripke.str')
    kripke.read_structure_file(structure_path)
    actual_labels = {'s0': ['p','q'], 's1': ['q'], 's2': [''], 's3': ['p']}
    actual_transitions = {'s0': ['s0'], 's1': ['s2'], 's2': ['s0', 's3'], 's3': ['s3']}
    actual_states = ['s0', 's1', 's2', 's3']
    actual_init_states = ['s0']
    actual_propositions = ['p', 'q']

    assert(kripke.labels == actual_labels)
    assert(kripke.transitions == actual_transitions)
    assert(kripke.states == actual_states)
    assert(kripke.init_states == actual_init_states)
    assert(kripke.propositions == actual_propositions)
    assert(len(kripke.states) == 4)
    
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
