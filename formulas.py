import pdb
import re 
from lark import Lark, Transformer
from graphviz import Source
from operators import *

class SimpleTree:
	def __init__(self, label = "dummy"):	
		self.left = None
		self.right = None
		self.label = label
	
	def __hash__(self):
		# return hash((self.label, self.left, self.right))
		return hash(self.label) + id(self.left) + id(self.right)
	
	def __eq__(self, other):
		if other is None:
			return False
		else:
			return self.label == other.label and self.left == other.left and self.right == other.right
	
	def __ne__(self, other):
		return not self == other
	
	def _isLeaf(self):
		return self.right is None and self.left is None
	
	def _addLeftChild(self, child):
		if child is None:
			return
		if type(child) is str:
			child = SimpleTree(child)
		self.left = child
		
	def _addRightChild(self, child):
		if type(child) is str:
			child = SimpleTree(child)
		self.right = child
	
	def addChildren(self, leftChild = None, rightChild = None): 
		self._addLeftChild(leftChild)
		self._addRightChild(rightChild)
		
		
	def addChild(self, child):
		self._addLeftChild(child)
		
	def getAllNodes(self):
		leftNodes = []
		rightNodes = []
		
		if not self.left is None:
			leftNodes = self.left.getAllNodes()
		if not self.right is None:
			rightNodes = self.right.getAllNodes()
		return [self] + leftNodes + rightNodes

	def getAllLabels(self):
		if not self.left is None:
			leftLabels = self.left.getAllLabels()
		else:
			leftLabels = []
			
		if not self.right is None:
			rightLabels = self.right.getAllLabels()
		else:
			rightLabels = []
		return [self.label] + leftLabels + rightLabels

	def __repr__(self):
		if self.left is None and self.right is None:
			return self.label
		
		# the (not enforced assumption) is that if a node has only one child, that is the left one
		elif (not self.left is None) and self.right is None:
			return self.label + '(' + self.left.__repr__() + ')'
		
		elif (not self.left is None) and (not self.right is None):
			return self.label + '(' + self.left.__repr__() + ',' + self.right.__repr__() + ')'



class CTLFormula(SimpleTree):
	'''
	A class for encoding syntax Trees and syntax DAGs of CTL formulas
	'''
	def __init__(self, formulaArg='dummy'):
		self.size = None
		if not isinstance(formulaArg, str):
			self.label = formulaArg[0]
			self.left = formulaArg[1]
			try:
				self.right = formulaArg[2]
			except:
				self.right = None

		else:
			super().__init__(formulaArg)

	def __lt__(self, other):

		if self.getDepth() < other.getDepth():
			return True
		elif self.getDepth() > other.getDepth():
			return False
		else:
			if self._isLeaf() and other._isLeaf():
				return self.label < other.label

			if self.left != other.left:
				return self.left < other.left

			if self.right is None:
				return False
			if other.right is None:
				return True
			if self.right != other.right:
				return self.right < other.right

			else:
				return self.label < other.label


	def prettyPrint(self, top=False):
		
		if top is True:
			lb = ""
			rb = ""
		else:
			lb = "("
			rb = ")"
		if self._isLeaf():
			return self.label
		if self.label in ctl_unary:
			return self.label + lb + self.left.prettyPrint() + rb
		if self.label in ctl_binary:
			if self.label == 'EU':
				return 'E' + lb + self.left.prettyPrint() + rb + " U " + lb + self.right.prettyPrint() + rb
			elif self.label == 'AU':
				return  'A' + lb + self.left.prettyPrint() + rb + " U " + lb + self.right.prettyPrint() + rb 
			else:
				return lb + self.left.prettyPrint() + rb + self.label + lb + self.right.prettyPrint() + rb

	
	def getAllVariables(self):
		allNodes = list(set(self.getAllNodes()))
		return [ node for node in allNodes if node._isLeaf() == True ]
	
	def getDepth(self):
		if self.left is None and self.right is None:
			return 0
		leftValue = -1
		rightValue = -1
		if not self.left is None:
			leftValue = self.left.getDepth()
		if not self.right is None:
			rightValue = self.right.getDepth()
		return 1 + max(leftValue, rightValue)
	
	def getNumberOfSubformulas(self):
		return len(self.getSetOfSubformulas())
	
	def getSetOfSubformulas(self):
		if self.left is None and self.right is None:
			return [repr(self)]
		leftValue = []
		rightValue = []
		if not self.left is None:
			leftValue = self.left.getSetOfSubformulas()
		if not self.right is None:
			rightValue = self.right.getSetOfSubformulas()
		return list(set([repr(self)] + leftValue + rightValue))

	
	def treeSize(self):
		if self.size is None:
			if self.left is None and self.right is None:
				if self.label == 'true' or self.label == 'false':
					self.size = 0
				else:
					self.size = 1
			leftSize=0
			rightSize=0
			if not self.left is None:
				leftSize= self.left.treeSize()
			if not self.right is None:
				rightSize = self.right.treeSize()
			self.size = 1+ leftSize + rightSize

		return self.size


	@classmethod
	def convertTextToFormula(cls, formulaText):
		
		f = CTLFormula()
		try:
			formula_parser = Lark(r"""
				?formula: _binary_expression
						|_unary_expression
						| constant
						| variable
				!constant: "true"
						| "false"
				_binary_expression: binary_operator "(" formula "," formula ")"
				_unary_expression: unary_operator "(" formula ")"
				variable: /[a-z]/
				!binary_operator: "&" | "|" | "->" | "EU" | "AU"
				!unary_operator: "!" | "EX" | "AF" | "AG" | "AX" | "EF" | "EG"
				
				%import common.SIGNED_NUMBER
				%import common.WS
				%ignore WS 
			""", start='formula')

			tree = formula_parser.parse(formulaText)

		except Exception as e:
			print("can't parse formula %s" % formulaText)
			print("error: %s" % e)
				
			
		f = TreeToCTLFormula().transform(tree)
		return f
			
class TreeToCTLFormula(Transformer):
		def formula(self, formulaArgs):
			return CTLFormula(formulaArgs)
		def variable(self, varName):
			return CTLFormula([str(varName[0]), None, None])
		def constant(self, arg):
			connector = ""
			if str(arg[0]) == "true":
				connector = "|"
			elif str(arg[0]) == "false":
				connector = "&"
			return CTLFormula([connector, CTLFormula(["p", None, None]), CTLFormula(["!", CTLFormula(["p", None, None] ), None])])
				
		def binary_operator(self, args):
			return str(args[0])
		def unary_operator(self, args):
			return str(args[0])



class ATLFormula(SimpleTree):

	def __init__(self, formulaArg='dummy'):
		self.size = None
		if not isinstance(formulaArg, str):
			self.label = formulaArg[0]
			if self.label[-1] in atl_temporal:
				self.players = set(int(digit) for digit in formulaArg[0].split('<')[1].split('>')[0])
			else:
				self.players = None
			self.left = formulaArg[1]
			try:
				self.right = formulaArg[2]
			except:
				self.right = None
		else:
			super().__init__(formulaArg)

	def __lt__(self, other):

		if self.getDepth() < other.getDepth():
			return True
		elif self.getDepth() > other.getDepth():
			return False
		else:
			if self._isLeaf() and other._isLeaf():
				return self.label < other.label

			if self.left != other.left:
				return self.left < other.left

			if self.right is None:
				return False
			if other.right is None:
				return True
			if self.right != other.right:
				return self.right < other.right

			else:
				return self.label < other.label


	def prettyPrint(self, top=False):
		
		if top is True:
			lb = ""
			rb = ""
		else:
			lb = "("
			rb = ")"

		if self._isLeaf():
			return self.label
		if self.label in atl_boolean:
			if self.label in atl_unary:
				return lb + self.label +" "+ self.left.prettyPrint() + rb
			if self.label in atl_binary:
				return lb + self.left.prettyPrint() +" "+  self.label +" "+ self.right.prettyPrint() + rb
		elif self.label[-1] in atl_temporal:
			temporal_operator = self.label[-1]
			if self.label[-1] in atl_unary:
				return '<' + ','.join(map(str,self.players)) + '>' + temporal_operator + lb + self.left.prettyPrint() + rb
			if self.label[-1] in atl_binary:
				return '<' + ','.join(map(str,self.players)) + '>' + lb + self.left.prettyPrint() + " " +  temporal_operator + " " + self.right.prettyPrint() + rb

	def getAllVariables(self):
		allNodes = list(set(self.getAllNodes()))
		return [ node for node in allNodes if node._isLeaf() == True ]
	
	def getDepth(self):
		if self.left is None and self.right is None:
			return 0
		leftValue = -1
		rightValue = -1
		if not self.left is None:
			leftValue = self.left.getDepth()
		if not self.right is None:
			rightValue = self.right.getDepth()
		return 1 + max(leftValue, rightValue)
	
	def getNumberOfSubformulas(self):
		return len(self.getSetOfSubformulas())
	
	def getSetOfSubformulas(self):
		if self.left is None and self.right is None:
			return [repr(self)]
		leftValue = []
		rightValue = []
		if not self.left is None:
			leftValue = self.left.getSetOfSubformulas()
		if not self.right is None:
			rightValue = self.right.getSetOfSubformulas()
		return list(set([repr(self)] + leftValue + rightValue))

	
	def treeSize(self):
		if self.size is None:
			if self.left is None and self.right is None:
				if self.label == 'true' or self.label == 'false':
					self.size = 0
				else:
					self.size = 1
			leftSize=0
			rightSize=0
			if not self.left is None:
				leftSize= self.left.treeSize()
			if not self.right is None:
				rightSize = self.right.treeSize()
			self.size = 1+ leftSize + rightSize

		return self.size


	@classmethod
	def convertTextToFormula(cls, formulaText):
		
		f = ATLFormula()
		try:
			formula_parser = Lark(r"""
				?formula: _binary_expression
						| _unary_expression
						| _temporal_unary_expression_
						| _temporal_binary_expression_						
						| constant
						| variable
				!constant: "true"
						| "false"
				_binary_expression: binary_operator "(" formula "," formula ")"
				_unary_expression: unary_operator "(" formula ")"
				_temporal_unary_expression_: players unary_operator "(" formula ")"
				_temporal_binary_expression_: players binary_operator "(" formula "," formula ")"
				variable: /[a-z]/
				players: "<" /[0-9]+/ ">"
				!binary_operator: "&" | "|" | "->" | "U"
				!unary_operator: "!" | "X" | "F" | "G"
				
				%import common.SIGNED_NUMBER
				%import common.WS
				%ignore WS 
			""", start='formula')

			tree = formula_parser.parse(formulaText)

		except Exception as e:
			print("can't parse formula %s" % formulaText)
			print("error: %s" % e)
				
			
		f = TreeToATLFormula().transform(tree)
		return f
			
class TreeToATLFormula(Transformer):
		
		def formula(self, formulaArgs):

			if formulaArgs[0][0] == '<':
				modifiedArgs = [formulaArgs[0]+formulaArgs[1]]+formulaArgs[2:]
				return ATLFormula(modifiedArgs)
			else:
				return ATLFormula(formulaArgs)
		
		def variable(self, varName):
			return ATLFormula([str(varName[0]), None, None])
		
		def constant(self, arg):
			connector = ""
			if str(arg[0]) == "true":
				connector = "|"
			elif str(arg[0]) == "false":
				connector = "&"
			return ATLFormula([connector, ATLFormula(["p", None, None]), ATLFormula(["!", ATLFormula(["p", None, None] ), None])])
		
		def players(self, args):
			return '<'+str(args[0])+'>'

		def binary_operator(self, args):
			return str(args[0])
		def unary_operator(self, args):
			return str(args[0])
		

#formula = ATLFormula.convertTextToFormula("&(<1>U(p,q),q)")
#print(formula)