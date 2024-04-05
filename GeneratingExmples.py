from graph_structures import *
from sample import *

Test = Kripke({0},{0: {0}, 1: {2}, 2: {0, 3}, 3: {3}},{0: {'p','q'}, 1: {'q'}, 2: set(), 3: {'p'}},{'p', 'q'})

def GenerateKripke(n):
	init_state = set([0])
	transitions = {n: {n},n+1: {n+1}}
	for i in range(0,n):
		transitions.update({i: {i+1,n+1}})
	labels = {n: {'p'},n+1: {}}
	for i in range(0,n):
		labels.update({i: {}})
	propositions = {'p'}
	return Kripke(init_state,transitions,labels,propositions)

def GenerateSample(n):
	KripkePos = GenerateKripke(n)
	KripkeNeg = GenerateKripke(n+1)
	return SampleKripke([KripkePos],[KripkeNeg],{'p'})

S = GenerateSample(4)

