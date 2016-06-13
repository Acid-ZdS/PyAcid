#!/usr/bin/env python3.4
# coding: utf-8

"""
This module defines a compiler class which can compile and dump an Acid code
to a Python code object.

Contributors: myrma
"""

import os
import ast
import marshal

from acid.parser import Parser
from acid.prelude import default_env


class Compiler:
	"""
	Compiles an Acid AST to a Python AST.
	"""

	translations = {}

	def __init__(self, ast, path=None):
		self.path = path
		self.ast = ast

	@classmethod
	def from_file(cls, path):
		"""
		Loads the Acid AST from a given path.
		"""

		parser = Parser.from_file(path)
		ast = parser.run()
		return cls(ast, path)

	@classmethod
	def execute_compiled_file(cls, path, prelude=default_env):
		"""
		Executes a Python code object stored in a file.
		"""

		with open(path, 'rb') as compiled_file:
			code = marshal.load(compiled_file)

			exec(code, prelude.copy())

	@classmethod
	def register(cls, *node_types):
		"""
		Registers a translation from an Acid AST node to a Python AST node.
		"""

		def _decorator_wrapper(translation):
			for node_type in node_types:
				cls.translations[node_type] = translation

			return translation

		return _decorator_wrapper

	def translate(self, node):
		"""
		Translates an Acid AST node into a Python AST node.
		"""

		py_ast = self.translations[type(node)](self, node)
		return ast.fix_missing_locations(py_ast)

	def compile(self):
		"""
		Compiles the Acid AST to a Python code object.
		"""

		py_ast = self.translate(self.ast)

		code = compile(py_ast, self.path or '<string>', mode='exec')
		return code

	def dump(self, target=None):
		"""
		Dumps the Python code object to a given path.
		"""

		if target is None and self.path is None:
			raise ValueError('Unspecified target path')

		code = self.compile()
		target = target or os.path.basename(self.path).split('.')[0] + '.acidc'

		with open(target, 'wb') as dump_file:
			marshal.dump(code, dump_file)

	def execute(self, prelude=default_env):
		"""
		Executes the resulting Python code object.
		"""

		code = self.compile()
		exec(code, prelude.copy())
