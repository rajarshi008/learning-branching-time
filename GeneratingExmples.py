from graph_structures import *
from sample import *

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

if not os.path.exists('test_suite/increasing_sample'):
	os.makedirs('test_suite/increasing_sample')

for i in range(5,16):
	s = GenerateSample(i)
	s.write('test_suite/increasing_sample/ex_sample'+str(i)+'.sp')

