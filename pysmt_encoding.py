from pysmt.shortcuts import Symbol, Or, get_model, And, Implies, Solver, Equals, Iff, Int, Bool, Not
from pysmt.typing import INT, BOOL

# Create a solver object
solver = Solver()

# Create 10 boolean variables
x = {(i,str(j)): Symbol("x_%d_%s"%(i,j)) for i in range(10) for j in range(2)}

# Perform OR operation on the variables

result = Or([x[(i,'0')] for i in range(10)])
solver.add_assertion(result)
solver.push()

result = And([Not(x[(i,'0')]) for i in range(10)])
solver.add_assertion(result)
solver.push()

# Check if the formula is satisfiable
# print the formulas in the solver

res = solver.solve()
print('Before pop')
print(solver.assertions)
print('SAT', res)
if res:
	model = solver.get_model()
	for i in x:
		print(x[i], (model[x[i]].is_true()))

solver.pop()
solver.pop()

res = solver.solve()
print('After pop')
print(solver.assertions)
print('SAT', res)
if res:
	model = solver.get_model()
	for i in x:
		print(x[i], (model[x[i]].is_true()))

solver.delete()