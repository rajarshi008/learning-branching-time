
from graphviz import Source
import random

epsilon = ''

def generate_random_kripke(max_in_deg, max_out_deg, num_states, transition_density, propositions):
	'''Generates a random Kripke structure with given parameters'''
	rand_kripke = Kripke(init_states=set(), transitions={}, labels={}, propositions=propositions)
	rand_kripke.add_init_state()
	for _ in range(1, num_states):
		rand_kripke.add_random_state(in_deg=max_in_deg, out_deg=max_out_deg)
	if transition_density == 'low':
		rand_kripke.reduce_transitions()
	return rand_kripke

class Kripke:
	def __init__(self, init_states=set(), transitions={}, labels={}, propositions=set()):
		self.init_states = init_states
		self.transitions = transitions
		self.labels = labels
		self.states = set(transitions.keys())
		self.propositions = propositions
		if propositions == []:
			self.propositions = set(label for state in self.states for label in self.labels[state])
			if epsilon in self.propositions:
				self.propositions.remove(epsilon)

	def calc_stats(self):
		
		self.propositions = set(label for state in self.states for label in self.labels[state])
		if epsilon in self.propositions:
			self.propositions.remove(epsilon)
		self.size = len(self.states)

	def successors(self, state):
		return self.transitions[state]
	
	def predecessors(self, state):
		return {s for s in self.states if state in self.transitions[s]}

	def read_structure_file(self, file_path):
		with open(file_path, 'r') as file:
			lines = file.read()
			self.read_structure(lines)

	def read_structure(self, kripke_str):
		'''Reads a Kripke structure from a text file with following format:

			Init States
			---
			Labels
			---
			Transitions
		'''
		init_states_str, labels_str, transitions_str = kripke_str.split('---\n')
		self.init_states = set(int(state) for state in init_states_str.strip().split(','))
		labels_dict_str = labels_str.strip().split('\n')
		for label_str in labels_dict_str:
			state, prop_str = label_str.strip().split(':')
			if prop_str == '':
				self.labels[int(state)] = set()
			else:	
				self.labels[int(state)] = set(prop_str.split(','))
		self.states = set(self.labels.keys())

		transitions_dict_str = transitions_str.strip().split('\n')
		self.transitions = {state: set() for state in self.states}
		for transition_str in transitions_dict_str:
			state1, state2 = transition_str.strip().split(',')
			self.transitions[int(state1)].add(int(state2))
		
		self.calc_stats()


	def add_init_state(self, self_loop_prob=0.1):
		init_state = 0
		self.init_states.add(init_state)
		self.states.add(init_state)

		self.labels[init_state] = set(random.choices(list(self.propositions), k=random.randint(0, len(self.propositions))))
		self_loop = random.choices([0,1], [1-self_loop_prob, self_loop_prob], k=1)[0]
		
		if self_loop:
			self.transitions[init_state] = {init_state}
		else:
			self.transitions[init_state] = set()


	def add_random_state(self, in_deg=2, out_deg=2, transition_density='low'):
		'''
		Generates random states with random transitions for the state (ensuring connectedness)
		'''
		new_state = len(self.states)
		self.states.add(new_state)
		self.labels[new_state] = set(random.choices(list(self.propositions), k=random.randint(0, len(self.propositions))))		
		self.transitions[new_state] = set()
		
		if transition_density == 'low' or transition_density == 'med':
			max_instates = max(1,len(self.states)//4)
			max_outstates = max(1,len(self.states)//4)
			#special method to reduce transitions for intermediate states
			

		if transition_density == 'high':
			max_instates = max(1,len(self.states)//2)
			max_outstates = max(1,len(self.states)//2)

		eligible_instates = [state for state in self.states if len(self.transitions[state]) < out_deg and state != new_state]
		if eligible_instates == []:
			raise ValueError('No states with outdegree less than %d'%out_deg)
		instate = random.choices(eligible_instates, k=random.randint(1, max_instates))
		#print(new_state, 'instate size', len(instate))

		for state in instate:
			self.transitions[state].add(new_state)

		eligible_outstates = [state for state in self.states if len(self.predecessors(state)) < in_deg]
		if eligible_outstates == []:
			raise ValueError('No states with indegree less than %d'%in_deg)
		outstate = random.choices(eligible_outstates, k=random.randint(1, max_outstates))
		#print(new_state, 'outstate size', len(outstate))

		for state in outstate:
			self.transitions[new_state].add(state)
		#print(new_state, 'transitions', self.transitions[new_state])

	def reduce_transitions(self, reduction_prob=0.9, num=1):
		'''
		Heursitic to reduce transitions in the Kripke structure ensuring connectedness
		'''

		for state in self.states:
			remove = random.choices([0,1], [1-reduction_prob, reduction_prob], k=1)[0]
			if len(self.transitions[state]) == 1 or not remove:
				continue
			stateComplement = set(other_state for other_state in self.states if other_state != state)
			if stateComplement & self.transitions[state] != 0:
				removable_states = set(other_state for other_state in self.states if other_state <= state) & self.transitions[state]
				if not removable_states:
					continue
				else:
					self.transitions[state] = self.transitions[state] - set(random.choices(list(removable_states), k=num))

	def __str__(self):
		'''
		Prints the Kripke structure in a human readable way
		'''
		
		string = "Kripke structure:\n"
		string += "Initial state: " + str(self.init_states) + "\n"
		string += "States: " + str(self.states) + "\n"
		string += "Transitions:\n"
		for state in self.states:
			string += str(state) + " -> " + str(self.transitions[state]) + "\n"
		string += "Labels:\n"
		for state in self.states:
			string += str(state) + " -> " + str(self.labels[state]) + "\n"

		return string
		

	def to_string(self):
		'''Prints the Kripke structure in a machine readable way'''
		string = ''
		string += ','.join([str(state) for state in self.init_states]) + '\n'
		string += '---\n'
		for state in self.states:
			string += str(state) + ':' + ','.join(self.labels[state]) + '\n'
		string += '---\n'
		for state in self.states:
			for succ in self.transitions[state]:
				string += str(state) + ',' + str(succ) + '\n'
		return string


	def to_dot(self, filename='dummy.str'):
		'''Creates a .dot file of the Kripke structure'''
		dot_str =  "digraph g {\n"
		dot_str += "-1 [label=\"\", style=invis]\n"
		for state in self.states:
			dot_str += ('{} [label="{}:{}"]\n'.format(state, str(state), self.labels[state]))

		for init_state in self.init_states:
			dot_str += ('{} -> {}\n'.format("-1", init_state))
		for state in self.states:
			for succ in self.transitions[state]:
				dot_str += ('{} -> {}\n'.format(state, succ))
		dot_str += ("}\n")	
		
		return dot_str
	
	def show(self, filename='dummy.png'):
		'''Shows the Kripke structure in a window'''
		s = Source(self.to_dot(), filename=filename, format="png")
		s.view()


class Concurrent_Game_Structure:
	class Concurrent_Game_Structure:
		def __init__(self, players, states, transitions, labels):
			self.players = players
			self.states = states
			self.transitions = transitions
			self.labels = labels
		
		def __str__(self):
			'''Prints the concurrent game structure in a human readable way'''
			string = "Concurrent game structure:\n"
			string += "Players: " + str(self.players) + "\n"
			string += "States: " + str(self.states) + "\n"
			string += "Transitions:\n"
			for state in self.states:
				string += str(state) + " -> " + str(self.transitions[state]) + "\n"
			string += "Labels:\n"
			for state in self.states:
				string += str(state) + " -> " + str(self.labels[state]) + "\n"
			return string
	
#k = Kripke()
#k.read_structure_file('example_kripke.str')
#k.show()
#k = generate_random_kripke(max_in_deg=4, max_out_deg=4, num_states=10, propositions={'p', 'q'})
#k.show()
#print(k.write_format())

