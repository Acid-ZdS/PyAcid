#!/usr/bin/env python3.4
# coding: utf-8

"""
Defines the AST structure of programs and expressions.

Contributors: myrma
"""

__all__ = [
	'Node',                            # Base node
	'Program',                         # program AST
	'Stmt', 'Expr', 'Literal',         # abstract AST nodes
	'Declaration', 'TypeDeclaration',  # assignment (value or type)
	'Call', 'Lambda',                  # calls
	'Variable',                        # atom
	'IntLiteral', 'FloatLiteral',      # numeric literal
	'CharLiteral', 'StringLiteral'     # string-related literals
]


class Node:
	"""
	Abstract Acid AST node.
	"""

	def __init__(self):
		self.span = None

	@property
	def pos(self):
		if self.span is not None:
			return self.span.start

	@classmethod
	def sub_types(cls):
		for sub_type in cls.__subclasses__():
			yield sub_type
			yield from sub_type.sub_types()


class Program(Node):
	"""
	Represents a sequence of instructions.
	"""

	def __init__(self, instructions, path=None):
		super().__init__()
		self.path = path
		self.instructions = instructions

	def __repr__(self):
		fmt = 'Program(path={0.path!r}, instructions={0.instructions})'
		return fmt.format(self)


class Stmt(Node):
	"""
	Abstract AST element representing a top-level statement.
	"""


class Declaration(Stmt):
	"""
	Declaring a name.
	ex: `(define pi 3.14)`
	"""

	def __init__(self, name, value):
		super().__init__()
		self.name = name
		self.value = value

	def __repr__(self):
		return 'Declaration(name={0.name!r}, value={0.value!r})'.format(self)


class TypeDeclaration(Stmt):
	"""
	Assigning a type to a name.
	ex: `(:: not (lambda (Bool) Bool))`
	"""

	def __init__(self, name, type):
		super().__init__()
		self.name = name
		self.type = type

	def __repr__(self):
		return 'TypeDeclaration(name={0.name!r}, type={0.type!r})'.format(self)


class Expr(Node):
	"""
	Abstract AST element representing an expression node.
	"""


class Call(Expr):
	"""
	Function call.
	ex: `(func x y z)`
	"""

	def __init__(self, func, args):
		super().__init__()
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
		super().__init__()
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
		super().__init__()
		self.name = name

	def __repr__(self):
		return 'Variable(name={0.name!r})'.format(self)


class Literal(Expr):
	"""
	Abstract literal expression.
	"""

	def __init__(self, value):
		super().__init__()
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
	ex: `'a'`, `'\\t'`
	"""


class StringLiteral(Literal):
	"""
	Literal sequence of potentially escaped characters.
	ex: `"this is a string !\\nnew line here"`
	"""
