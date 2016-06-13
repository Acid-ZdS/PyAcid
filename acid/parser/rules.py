#!/usr/bin/env python3.4
# coding: utf-8

"""
This module defines the parser rules. To define a custom parser rule, use this
snippet as a template:

	@Parser.register(priority=[n])
	def [rule_name](self, token_queue):
		# To consume a token of a given type:
		expected_token = expect([token type], token_queue)

		...  # Processing tokens

		return [AST node]

Contributors: myrma
"""

from acid.parser.parser import Parser, expect
from acid.parser.lexer import *
from acid.parser.ast import *
from acid.exception import *


@Parser.register_stmt(priority=1)
def consume_declaration(self, token_queue):
	expect(TokenType.LPAREN, token_queue)
	expect(TokenType.DEFINE, token_queue)

	atom = expect(TokenType.ATOM, token_queue)
	name = atom.value

	value = self.consume_expr(token_queue)
	expect(TokenType.RPAREN, token_queue)
	return Declaration(name, value)


@Parser.register_stmt(priority=2)
def consume_toplevel_expr(self, token_queue):
	expr = self.consume_expr(token_queue)
	return TopLevelExpr(expr)


@Parser.register_expr(priority=2)
def consume_call(self, token_queue):
	expect(TokenType.LPAREN, token_queue)
	func = self.consume_expr(token_queue)

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

	return Call(func, args)


@Parser.register_expr(priority=1)
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


@Parser.register_expr(priority=1)
def consume_variable(self, token_queue):
	atom = expect(TokenType.ATOM, token_queue)
	return Variable(atom.value)


@Parser.register_expr(priority=1)
def consume_int_literal(self, token_queue):
	token = expect(TokenType.INT_LITERAL, token_queue)
	return IntLiteral(int(token.value))


@Parser.register_expr(priority=1)
def consume_int_literal(self, token_queue):
	token = expect(TokenType.FLOAT_LITERAL, token_queue)
	return FloatLiteral(float(token.value))
