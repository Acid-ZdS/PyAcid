#!/usr/bin/env python3.4
# coding: utf-8

"""
Defines the AST structure of programs and expressions.

Contributors: myrma
"""

__all__ = [
	'Program',                       # program AST
	'Stmt', 'Expr', 'Literal',       # abstract AST nodes
	'Declaration', 'TopLevelExpr',   # top-level statement
	'Call', 'Lambda',                # calls
	'Variable',                      # atom
	'IntLiteral', 'FloatLiteral',    # numeric literal
	'CharLiteral', 'StringLiteral'   # string-related literals
]


class Program:
	"""
	Represents a sequence of instructions.
	"""

	def __init__(self, instructions, path=None):
		self.path = path
		self.instructions = instructions

	def __repr__(self):
		fmt = 'Program(path={0.path!r}, instructions={0.instructions})'
		return fmt.format(self)


class Stmt:
	"""
	Abstract AST element representing a top-level statement.
	"""


class Declaration(Stmt):
	"""
	Declaring a name.
	ex: `(define pi 3.14)`
	"""

	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __repr__(self):
		return 'Declaration(name={0.name!r}, value={0.value!r})'.format(self)


class TopLevelExpr(Stmt):
	"""
	Regular expression at top-level.
	ex: `(+ 1 2)`
	"""

	def __init__(self, expr):
		self.expr = expr

	def __repr__(self):
		return 'TopLevelExpr(expr={0.expr!r})'.format(self)


class Expr:
	"""
	Abstract AST element representing an expression node.
	"""


class Call(Expr):
	"""
	Function call.
	ex: `(func x y z)`
	"""

	def __init__(self, func, args):
		self.func = func
		self.args = args

	def __repr__(self):
		return 'Call(func={0.func!r}, args={0.args})'.format(self)


class Lambda(Expr):
	"""
	Lambda function definition.
	ex: `(lambda (x y) (+ x y))`
	"""

	def __init__(self, params, body):
		self.params = params
		self.body = body

	def __repr__(self):
		return 'Lambda(params={0.params!r}, body={0.body!r})'.format(self)


class Variable(Expr):
	"""
	Variable name.
	ex: `pi`
	"""

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return 'Variable(name={0.name!r})'.format(self)


class Literal(Expr):
	"""
	Abstract literal expression.
	"""

	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return '{0.__class__.__name__}(value={0.value!r})'.format(self)


class IntLiteral(Literal):
	"""
	Integer literal expression.
	ex: `42`
	"""


class FloatLiteral(Literal):
	"""
	Floating point number literal expression.
	ex: `3.14`
	"""


class CharLiteral(Literal):
	"""
	Literal character. May be escaped.
	ex: `'a'`, `'\t'`
	"""


class StringLiteral(Literal):
	"""
	Literal sequence of potentially escaped characters.
	ex: `"this is a string !\nnew line here"`
	"""
