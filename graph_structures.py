
from graphviz import Source
import random
import numpy as np
from scipy.stats import geom, expon


epsilon = ''

def merge_kripkes(kripke1, kripke2, extra_transitions=10):
	'''
	Auxiliary function required to create large Kripke structures
	'''
	merged_kripke = Kripke(init_states=set(), transitions={}, labels={}, propositions=kripke1.propositions)
	kripke1.size = len(kripke1.states)

	merged_kripke.init_states = kripke1.init_states
	merged_kripke.labels = {**kripke1.labels, **{kripke1.size+state: kripke2.labels[state]  for state in kripke2.labels}}
	merged_kripke.transitions = {**kripke1.transitions, **{kripke1.size+state1: set([kripke1.size+state2 for state2 in kripke2.transitions[state1]])\
													    for state1 in kripke2.states}}
	merged_kripke.states = set(merged_kripke.labels.keys())
	# Additional transitions (modify the parameters for better results)
	init_transition_prob = random.choices([0,1], [0.1, 0.9], k=1)[0]
	if init_transition_prob:
		merged_kripke.transitions[0].add(kripke1.size)
	random_transitions = extra_transitions
	for _ in range(random_transitions):
		transition_prob = random.choices([0,1], [0.5, 0.5], k=1)[0]
		if transition_prob:
			state1 = random.choices(list(kripke1.states), k=1)[0]
			state2 = random.choices(list(kripke2.states), k=1)[0]
			direction = random.choices([0,1], [0.5, 0.5], k=1)[0]
			if direction:
				merged_kripke.transitions[state1].add(kripke1.size+state2)
			else:
				merged_kripke.transitions[kripke1.size+state2].add(state1)

	return merged_kripke

def generate_random_kripke(max_in_deg, max_out_deg, num_states, transition_density, propositions):
	'''Generates a random Kripke structure with given parameters'''
	rand_kripke = Kripke(init_states=set(), transitions={}, labels={}, propositions=propositions)
	rand_kripke.add_init_state()
	for _ in range(1, num_states):
		rand_kripke.add_random_state(in_deg=max_in_deg, out_deg=max_out_deg)
	if transition_density == 'low':
		rand_kripke.reduce_transitions()
	return rand_kripke

def generate_random_cgs(max_in_deg, max_out_deg, num_states, transition_density, propositions, players, turn_based):
	'''Generates a random Concurrent Game structure with given parameters'''
	rand_cgs = ConcurrentGameStructure(init_states=set(), transitions={}, labels={}, players=set(players), propositions=propositions)
	rand_cgs.add_init_state()
	for _ in range(1, num_states):
		rand_cgs.add_random_state(in_deg=max_in_deg, out_deg=max_out_deg, transition_density=transition_density, turn_based=turn_based)
	return rand_cgs


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


class ConcurrentGameStructure:
	
	def __init__(self, init_states=set(), transitions={}, labels={}, players=set(), propositions=set()):
		self.players = players # ordered list
		self.transitions = transitions
		self.labels = labels
		self.states = set(self.labels.keys())
		self.init_states = init_states
		self.propositions = propositions
		self.player2pos = {player: i for i, player in enumerate(self.players)}

	def calc_stats(self):
		
		self.propositions = set(label for state in self.states for label in self.labels[state])
		self.player2pos = {player: i for i, player in enumerate(self.players)}
		self.actions = {state: set([action for action in self.transitions[state]]) for state in self.states}
		if epsilon in self.propositions:
			self.propositions.remove(epsilon)
		self.size = len(self.states)

	def __str__(self):
		'''Prints the concurrent game structure in a human readable way'''
		string = "Concurrent game structure:\n"
		string += "Players: " + str(self.players) + "\n"
		string += "States: " + str(self.states) + "\n"
		string += "Initial states: " + str(self.init_states) + "\n"
		string += "Transitions:\n"
		for state in self.states:
			for action in self.transitions[state]:
				string += str(state) + " -" + str(action) + '-> ' + str(self.transitions[state][action]) + "\n"
		string += "Labels:\n"
		for state in self.states:
			string += str(state) + " -> " + str(self.labels[state]) + "\n"
		return string
	

	def read_structure(self, cgs_str):
		'''Reads a CGS from a text file with following format:

			Init States
			---
			Labels
			---
			Transitions
			---
			Players
		'''
		init_states_str, labels_str, transitions_str, players_str = cgs_str.split('---\n')
		
		#Initial States
		self.init_states = set(int(state) for state in init_states_str.strip().split(','))
		
		#Labels
		labels_dict_str = labels_str.strip().split('\n')
		for label_str in labels_dict_str:
			state, prop_str = label_str.strip().split(':')
			if prop_str == '':
				self.labels[int(state)] = set()
			else:
				self.labels[int(state)] = set(prop_str.split(','))
		self.states = set(self.labels.keys())

		#Transitions
		transitions_dict_str = transitions_str.strip().split('\n')
		self.transitions = {state: dict() for state in self.states}
		for transition_str in transitions_dict_str:
			split_list = transition_str.strip().split(':')
			state1, state2 = split_list[0].split(',')
			action_list = [ tuple(map(int,action_str.split(','))) for action_str in split_list[1].split(';')]
			for action in action_list:
				self.transitions[int(state1)][action] = int(state2)
		#Players
		self.players = list(map(int,players_str.strip().split(',')))

		self.calc_stats()
	
	def add_init_state(self, turn_based=True, self_loop_prob=0.3):
		
		#Basic Info
		init_state = 0
		self.init_states.add(init_state)
		self.states.add(init_state)
		self.transitions[init_state] = {}
		self.actions = {}
		self.labels[init_state] = set(random.choices(list(self.propositions), k=random.randint(0, len(self.propositions))))

		#Transition (Self loop)
		self.state_player = {}
		if turn_based:
			player = random.choices(list(self.players), k=1)[0]
			self.state_player[init_state] = player
			zero_action = [0]*len(self.players)
			zero_action[self.player2pos[player]] = 1
			init_action = tuple(zero_action)
		else:
			raise('Not implemented yet')
		
		self_loop = random.choices([0,1], [1-self_loop_prob, self_loop_prob], k=1)[0]
		if self_loop:
			self.transitions[init_state][init_action] = init_state
			self.actions[init_state] = {init_action}
		else:
			self.transitions[init_state] = {}
			self.actions[init_state] = set()

	def add_random_state(self, in_deg=2, out_deg=2, transition_density='low', turn_based=True):
		'''
		Generates random states with random transitions for the state (ensuring connectedness)
		'''
		new_state = len(self.states)
		self.states.add(new_state)
		self.labels[new_state] = set(random.choices(list(self.propositions), k=random.randint(0, len(self.propositions))))		
		self.actions[new_state] = set()

		if turn_based:
			self.state_player[new_state] = random.choices(list(self.players), k=1)[0]
		self.transitions[new_state] = {}

		if transition_density == 'low' or transition_density == 'med':
			max_instates = max(1,len(self.states)//4)
			max_outstates = max(1,len(self.states)//4)
			#special method to reduce transitions for intermediate states

		if transition_density == 'high':
			max_instates = max(1,len(self.states)//2)
			max_outstates = max(1,len(self.states)//2)

		
		eligible_instates = [state for state in self.states if len(self.actions[state]) < out_deg and state != new_state]
		if eligible_instates == []:
			raise ValueError('No states with outdegree less than %d'%out_deg)
		instate = random.choices(eligible_instates, k=random.randint(1, max_instates))
		#print(new_state, 'instate size', len(instate))

		for state in instate:
			player = self.state_player[state] if turn_based else random.choices(self.players, k=1)[0]	
			try:
				instate_player_last_action = max(list(self.actions[state]), key=lambda x: x[self.player2pos[player]])
			except:
				instate_player_last_action = tuple([0]*len(self.players))
			#instate_player_last_action = tuple([0]*len(self.players))
			aux_list = list(instate_player_last_action)
			aux_list[self.player2pos[player]] += 1
			instate_player_new_action = tuple(aux_list)
			self.transitions[state][instate_player_new_action] = new_state
			self.actions[state].add(instate_player_new_action)

		eligible_outstates = [state for state in self.states if len(self.predecessors(state)) < in_deg]
		if eligible_outstates == []:
			raise ValueError('No states with indegree less than %d'%in_deg)
		outstate = random.choices(eligible_outstates, k=random.randint(1, max_outstates))
		#print(new_state, 'outstate size', len(outstate))

		for state in outstate:
			player = self.state_player[new_state] if turn_based else random.choices(self.players, k=1)[0]	
			try:
				player_last_action = max(list(self.actions[new_state]), key=lambda x: x[self.player2pos[player]])
			except:
				player_last_action = tuple([0]*len(self.players))
			aux_list = list(player_last_action)
			aux_list[self.player2pos[player]] += 1
			player_new_action = tuple(aux_list)
			self.transitions[new_state][player_new_action] = state
			self.actions[new_state].add(player_new_action)
		#print(new_state, 'transitions', self.transitions[new_state])
		
	
	def to_string(self):
		'''Prints the CGS in a machine readable way'''
		
		string = ''
		string += ','.join([str(state) for state in self.init_states]) + '\n'
		string += '---\n'
		for state in self.states:
			string += str(state) + ':' + ','.join(self.labels[state]) + '\n'
		string += '---\n'
		for state in self.states:
			succ_states = self.transitions[state].values()
			for succ_state in succ_states:
				action_list = []
				for action in self.transitions[state]:
					if self.transitions[state][action] == succ_state:		
						action_list.append(','.join(map(str,action)))
				string += str(state) + ',' + str(succ_state) + ':' + ';'.join(action_list) + '\n'
			
		string += '---\n'
		string += ','.join(map(str,self.players)) + '\n'
		
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
			succ_states = self.transitions[state].values()
			for succ_state in succ_states:
				action_list = []
				for action in self.transitions[state]:
					if self.transitions[state][action] == succ_state:		
						action_list.append('(' + ','.join(map(str,action)) + ')')
				dot_str += ('{} -> {} [label="{}"]\n'.format(state, succ_state, ' '.join(action_list)))
		dot_str += ("}\n")	
		
		return dot_str

	def show(self, filename='dummy.png'):
		'''Shows the Kripke structure in a window'''
		s = Source(self.to_dot(), filename=filename, format="png")
		s.view()

	def successors(self, state):
		return set(self.transitions[state][action] for action in self.transitions[state])
	
	def predecessors(self, state):
		return {s for s in self.states for action in self.transitions[s] if self.transitions[s][action] == state}

	def predecessors_players(self, target_states, players):
		'''Returns the predecessors of a state wrt to give players'''
		
		playing_pos = [self.player2pos[player] for player in players]
		pred_set = set()
		for state in self.states:
			action_partition = {}
			
			for action in self.transitions[state]:
				partial_action = tuple(action[pos] for pos in playing_pos)
				if partial_action not in action_partition:
					action_partition[partial_action] = [action]
				else:
					action_partition[partial_action].append(action)
			for partial_action in action_partition:
				possible = True
				for action in action_partition[partial_action]:
					if self.transitions[state][action] not in target_states:
						possible = False
						break
				if possible:
					pred_set.add(state)
					break

		return pred_set
				



#k = Kripke()
#k.read_structure_file('example_kripke.str')
#k.show()
#k1 = generate_random_kripke(max_in_deg=2, max_out_deg=2, num_states=5, transition_density='low', propositions={'p', 'q'})
#k2 = generate_random_kripke(max_in_deg=2, max_out_deg=2, num_states=5, transition_density='low', propositions={'p', 'q'})
#k = merge_kripkes(k1, k2, 5)
#k.show()
#k.show()
#print(k.write_format())


#c = ConcurrentGameStructure()
#with open('example.cgs', 'r') as file:
#	string = file.read()
#	c.read_structure(string)
#print(c.predecessors({0,1}, [0]))


#c = generate_random_cgs(max_in_deg=4, max_out_deg=4, num_states=10, \
#						transition_density='low', propositions={'p', 'q'}, players=[0,1,2], turn_based=True)
#c.show()
#print(c.to_string())

