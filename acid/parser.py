#!/usr/bin/env python3.4
# coding: utf-8

"""
Declares the Parser class, which can transform a code string into an AST.

Contributors: myrma
"""

__all__ = [
	'Parser',
	'parse'
]


import functools

from acid.ast import *
from acid.lexer import TokenType, tokenize
from acid.exception import ParseError


class Parser:
	"""
	Registers some consumers to parse the AST.
	"""

	consumers = []

	def __init__(self, code, path=None):
		self.path = path

		with open(path) as file:
			self.code = file.read()

	@classmethod
	def from_file(cls, path):
		with open(path) as file:
			code = file.read()
			return cls(code, path)

	@classmethod
	def register(cls, priority=1):
		"""
		Registers a given consumer function with a priority. `priority` is an
		integer defining the order in which expression types try to parse from
		the token queue. The closest this number if from 1, the highest will be
		its priority.

		`priority` must be greater than one (not strictly).
		"""

		def _decorator_wrapper(consumer):
			@functools.wraps(consumer)
			def _consumer_wrapper(self, token_queue):
				# copies the token list
				tmp_queue = token_queue[:]

				try:
					node = consumer(self, tmp_queue)
				except ParseError:
					raise
				except IndexError:
					# when the user tries to call token_queue.pop(0)
					raise ParseError(token_queue[0].pos, 'Unexpected EOF')
				else:
					# assign tmp_queue to reference token_queue
					token_queue[:] = tmp_queue
					return node

			cls.consumers.insert(priority - 1, _consumer_wrapper)

		return _decorator_wrapper


	def consume_expr(self, token_queue):
		"""
		Tries to parse an Expr node from a token list.
		This does not affect the list if the function failed to parse.
		"""

		# tries every concrete Expr node
		for consumer in self.consumers:
			try:
				node = consumer(self, token_queue)
			except ParseError:
				continue
			else:
				return node
		else:
			# when every expr node has been tried, but none succeeded to parse
			raise ParseError(token_queue[0].pos, 'Failed to parse code')


	def run(self):
		"""
		Parses a given string into a Program object.
		"""

		token_queue = list(tokenize(self.code))  # the tokenized string
		instrs = []                              # the instructions of the program

		while token_queue:
			try:
				# tries to parse an expression from the token queue
				instr = self.consume_expr(token_queue)
			except ParseError:
				raise  # when no expression could be parsed
			else:
				# append the instruction to the program
				instrs.append(instr)

		# returns the resulting Program object.
		return Program(instrs, self.path)


@Parser.register(priority=2)
def consume_call(self, token_queue):
	expect(TokenType.LPAREN, token_queue)
	atom = expect(TokenType.ATOM, token_queue)
	name = atom.value

	args = []
	# consumes expressions as long as it parses.
	while True:
		try:
			arg = self.consume_expr(token_queue)
		except ParseError:
			break
		else:
			args.append(arg)

	expect(TokenType.RPAREN, token_queue)

	return Call(name, args)


@Parser.register(priority=1)
def consume_lambda(self, token_queue):
	expect(TokenType.LPAREN, token_queue)
	expect(TokenType.LAMBDA, token_queue)
	expect(TokenType.LPAREN, token_queue)

	params = []
	while token_queue[0].type == TokenType.ATOM:
		token = token_queue.pop(0)
		params.append(token.value)

	expect(TokenType.RPAREN, token_queue)
	body = self.consume_expr(token_queue)
	expect(TokenType.RPAREN, token_queue)
	return Lambda(params, body)


@Parser.register(priority=1)
def consume_declaration(self, token_queue):
	expect(TokenType.LPAREN, token_queue)
	expect(TokenType.DEFINE, token_queue)

	atom = expect(TokenType.ATOM, token_queue)
	name = atom.value

	value = self.consume_expr(token_queue)
	expect(TokenType.RPAREN, token_queue)
	return Declaration(name, value)


@Parser.register(priority=1)
def consume_variable(self, token_queue):
	atom = expect(TokenType.ATOM, token_queue)
	return Variable(atom.value)


@Parser.register(priority=1)
def consume_int_literal(self, token_queue):
	token = expect(TokenType.INT_LITERAL, token_queue)
	return IntLiteral(int(token.value))


@Parser.register(priority=1)
def consume_int_literal(self, token_queue):
	token = expect(TokenType.FLOAT_LITERAL, token_queue)
	return FloatLiteral(float(token.value))


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


def parse(code, path=None):
	"""
	Parses the given code, without needing to instantiate a Parser object.
	"""

	parser = Parser(code, path)
	ast = parser.run()
	return ast
