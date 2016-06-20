#!/usr/bin/env python3.4
# coding: utf-8

"""
This module defines the parser rules. To define a custom parser rule, use this
snippet as a template:

	@Parser.register([NodeType], priority=[n])
	def [rule_name](self):
		# To consume a token of a given type:
		expected_token = self.expect([token type])

		node = self.consume([NodeType to consume])

		...  # Processing tokens

		return [AST node]

Contributors: myrma
"""

from acid.parser.parser import Parser
from acid.parser.lexer import *
from acid.parser.ast import *
from acid.parser.types import SourceSpan
from acid.exception import *


@Parser.register(Program, priority=1)
def consume_program(self):
	# the program instructions
	instrs = []

	while self.token_queue:
		try:
			# tries to parse an expression from the token queue
			instr = self.consume(Stmt)
		except ParseError:
			raise  # when no expression could be parsed
		else:
			# append the instruction to the program
			instrs.append(instr)

	# returns the resulting Program object.
	prog = Program(instrs, self.path)
	prog.span = SourceSpan.between(instrs[0], instrs[-1])
	return prog


@Parser.register(Declaration, priority=1)
def consume_declaration(self):
	first = self.expect(TokenType.LPAREN)
	self.expect(TokenType.DEFINE)

	atom = self.expect(TokenType.ATOM)
	name = atom.value

	value = self.consume(Expr)
	last = self.expect(TokenType.RPAREN)

	decl = Declaration(name, value)
	decl.span = SourceSpan.between(first, last)
	return decl


@Parser.register(Call, priority=2)
def consume_call(self):
	first = self.expect(TokenType.LPAREN)
	func = self.consume(Expr)

	args = []
	# consumes expressions as long as it parses.
	while True:
		try:
			arg = self.consume(Expr)
		except ParseError:
			break
		else:
			args.append(arg)

	last = self.expect(TokenType.RPAREN)

	call = Call(func, args)
	call.span = SourceSpan.between(first, last)
	return call


@Parser.register(Lambda, priority=1)
def consume_lambda(self):
	first = self.expect(TokenType.LPAREN)
	self.expect(TokenType.LAMBDA)
	self.expect(TokenType.LPAREN)

	params = []
	while self.token_queue[0].type == TokenType.ATOM:
		token = self.token_queue.pop(0)
		params.append(token.value)

	self.expect(TokenType.RPAREN)
	body = self.consume(Expr)
	last = self.expect(TokenType.RPAREN)

	lam = Lambda(params, body)
	lam.span = SourceSpan.between(first, last)
	return lam


@Parser.register(Variable, priority=1)
def consume_variable(self):
	atom = self.expect(TokenType.ATOM)

	var = Variable(atom.value)
	var.span = atom.span
	return var


@Parser.register(IntLiteral, priority=1)
def consume_int_literal(self):
	token = self.expect(TokenType.INT_LITERAL)

	lit = IntLiteral(int(token.value))
	lit.span = token.span
	return lit


@Parser.register(FloatLiteral, priority=1)
def consume_float_literal(self):
	token = self.expect(TokenType.FLOAT_LITERAL)

	lit = FloatLiteral(float(token.value))
	lit.span = token.span
	return lit


@Parser.register(CharLiteral, priority=1)
def consume_char_literal(self):
	token = self.expect(TokenType.CHAR_LITERAL)
	char = token.value.strip("'")

	lit = CharLiteral(char)
	lit.span = token.span
	return lit


@Parser.register(StringLiteral, priority=1)
def consume_string_literal(self):
	token = self.expect(TokenType.STRING_LITERAL)

	# todo: find another way to unescape strings
	string = token.value.strip('"').encode('latin-1').decode('unicode_escape')

	lit = StringLiteral(string)
	lit.span = token.span
	return lit
