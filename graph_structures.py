
from graphviz import Source

epsilon = ''

class Kripke:
	def __init__(self, init_states=[], transitions={}, labels={}, propositions=[]):
		self.init_states = init_states
		self.transitions = transitions
		self.labels = labels
		self.states = list(transitions.keys())
		self.propositions = propositions
		if propositions == []:
			self.propositions = sorted(list(set(label for state in self.states for label in self.labels[state])))
			if epsilon in self.propositions:
				self.propositions.remove(epsilon)

	def calc_stats(self):
		
		self.propositions = sorted(list(set(label for state in self.states for label in self.labels[state])))
		if epsilon in self.propositions:
			self.propositions.remove(epsilon)


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
		self.init_states = init_states_str.strip().split(',')
		labels_dict_str = labels_str.strip().split('\n')
		for label_str in labels_dict_str:
			state, prop_str = label_str.strip().split(':')
			self.labels[state] = prop_str.split(',')
		self.states = list(self.labels.keys())

		transitions_dict_str = transitions_str.strip().split('\n')
		self.transitions = {state: [] for state in self.states}
		for transition_str in transitions_dict_str:
			state1, state2 = transition_str.strip().split(',')
			self.transitions[state1].append(state2)
		
		self.calc_stats()

	def __str__(self):
		'''Prints the Kripke structure in a human readable way'''
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