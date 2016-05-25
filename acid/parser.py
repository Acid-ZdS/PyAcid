#!/usr/bin/env python3.4
# coding: utf-8

"""
Defines the AST structure of programs and expressions.

To add an expression type, use the following template:

class CustomExpr(Expr):

	abstract = # True if your type is not meant to be parsed directly, but
			   # subclassed first, and False otherwise

	priority = # an integer defining the order in which expression types try
			   # to parse from the token queue. The closest this number if from
			   # 0, the highest will be its priority.

	def __init__(self, [*args]):
		...  # your constructor code

	@classmethod
	def feed(self, token_queue):
		...  # your parsing method

Contributors: myrma
"""

__all__ = [
	'Program',                                   # program AST
	'Expr', 'Literal',                           # abstract AST nodes
	'Call', 'Lambda',                            # calls
	'Variable', 'IntLiteral', 'FloatLiteral',    # atoms
	'parse'                                      # str <-> Program
]


from abc import *

from acid.lexer import TokenType, tokenize
from acid.exception import ParseError


class Program:
	"""
	Represents a sequence of instructions.
	"""

	def __init__(self, instructions, path=None):
		self.instructions = instructions
		self.path = path


# question: is ABC needed ?
class Expr(ABC):
	"""
	Abstract AST element.
	"""

	# says that this class' `consume` method will iterate through
	# every subclass
	abstract = True

	@abstractclassmethod
	def feed(cls, token_queue):
		"""
		Consumes a token list and returns an Expr instance if the code was
		correct, raises a ParseError otherwise.

		Override this function to implement a new AST node.
		"""

		raise NotImplementedError

	@classmethod
	def consume(cls, token_queue):
		"""
		Tries to parse an Expr node from a token list.
		This does not affect the list if the function failed to parse.
		"""

		# tries every concrete Expr node
		for node_type in resolve_node_order(cls):
			# copies the token list
			tmp_queue = token_queue[:]

			try:
				node = node_type.feed(tmp_queue)
			except ParseError:
				continue
			except IndexError:
				# when the user tries to call token_queue.pop(0)
				raise ParseError(token_queue[0].pos, 'Unexpected EOF')
			else:
				# assign tmp_queue to reference token_queue
				token_queue[:] = tmp_queue
				break
		else:
			# when every expr node has been tried, but none succeeded to parse
			raise ParseError(token_queue[0].pos, 'Failed to parse code')

		return node


class Call(Expr):
	"""
	Function call.
	ex: `(func x y z)`
	"""

	# make the `consume` method use this class' `feed` instead of
	# iterating its subclasses
	abstract = False

	# specify the order in which the parser will try expression types
	priority = 2

	def __init__(self, name, args):
		self.name = name
		self.args = args

	@classmethod
	def feed(cls, token_queue):
		expect(TokenType.LPAREN, token_queue)
		atom = expect(TokenType.ATOM, token_queue)
		name = atom.value

		args = []
		# consumes expressions as long as it parses.
		while True:
			try:
				arg = Expr.consume(token_queue)
			except ParseError:
				break
			else:
				args.append(arg)

		expect(TokenType.RPAREN, token_queue)

		return Call(name, args)


class Lambda(Expr):
	"""
	Lambda function definition.
	ex: `(lambda (x y) (+ x y))`
	"""

	abstract = False
	priority = 1

	def __init__(self, params, body):
		self.params = params
		self.body = body

	@classmethod
	def feed(cls, token_queue):
		expect(TokenType.LPAREN, token_queue)
		expect(TokenType.LAMBDA, token_queue)
		expect(TokenType.LPAREN, token_queue)

		params = []
		while token_queue[0].type == TokenType.ATOM:
			token = token_queue.pop(0)
			params.append(token.value)

		expect(TokenType.RPAREN, token_queue)
		body = Expr.consume(token_queue)
		expect(TokenType.RPAREN, token_queue)
		return Lambda(params, body)


class Declaration(Expr):
	"""
	Lambda function definition.
	ex: `(lambda (x y) (+ x y))`
	"""

	abstract = False
	priority = 1

	def __init__(self, name, value):
		self.name = name
		self.value = value

	@classmethod
	def feed(cls, token_queue):
		expect(TokenType.LPAREN, token_queue)
		expect(TokenType.DEFINE, token_queue)

		atom = expect(TokenType.ATOM, token_queue)
		name = atom.value

		value = Expr.consume(token_queue)
		expect(TokenType.RPAREN, token_queue)
		return Declaration(name, value)


class Variable(Expr):
	"""
	Variable name.
	ex: `pi`
	"""

	abstract = False
	priority = 3

	def __init__(self, name):
		self.name = name

	@classmethod
	def feed(cls, token_queue):
		atom = expect(TokenType.ATOM, token_queue)
		return Variable(atom.value)


class Literal(Expr):
	"""
	Abstract literal expression.
	ex: `42`, `3.14`
	"""

	abstract = True
	priority = 3

	def __init__(self, value):
		self.value = value


class IntLiteral(Literal):
	"""
	Integer literal expression.
	ex: `42`
	"""

	abstract = False

	@classmethod
	def feed(cls, token_queue):
		token = expect(TokenType.INT_LITERAL, token_queue)
		return cls(int(token.value))


class FloatLiteral(Literal):
	"""
	Floating point number literal expression.
	ex: `3.14`
	"""

	abstract = False

	@classmethod
	def feed(cls, token_queue):
		token = expect(TokenType.FLOAT_LITERAL, token_queue)
		return cls(float(token.value))


def resolve_node_order(expr_type=Expr):
	"""
	Yields the different expression types according to their priority.
	"""

	# list every subclasses of the given type
	subclasses = expr_type.__subclasses__()

	# sort the types by their priority
	subclasses.sort(key=lambda typ: typ.priority)


	for sub_expr_type in subclasses:
		if sub_expr_type.abstract:
			# yield every concrete subtypes
			yield from resolve_node_order(sub_expr_type)
		else:
			# when the type is concrete (i.e. when sub_expr_type.abstract is
			# False)
			yield sub_expr_type


def parse(code, path=None):
	"""
	Parses a given string into a Program object.
	"""

	token_queue = list(tokenize(code))  # the tokenized string
	instrs = []                         # the instructions of the program

	while token_queue:
		try:
			# tries to parse an expression from the token queue
			instr = Expr.consume(token_queue)
		except ParseError:
			raise  # when no expression could be parsed
		else:
			# append the instruction to the program
			instrs.append(instr)

	# returns the resulting Program object.
	return Program(instrs, path)


def expect(token_type, token_queue):
	"""
	Tries to consume a single token from the token queue.
	Returns the token if the next token is of the given type, raises a
	ParseError otherwise.
	"""

	token = token_queue.pop(0)

	# if the next token is not of the expected type
	if token.type != token_type:
		msg = 'Expected {}, got {}'.format(token_type.name, token.type.name)
		raise ParseError(token.pos, msg)

	return token
