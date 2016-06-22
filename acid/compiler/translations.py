#!/usr/bin/env python3.4
# coding: utf-8

"""
This module defines some conversions between Acid's and Python's AST nodes.

Contributors: myrma
"""

import ast as python_ast

from acid.compiler.compiler import Compiler
from acid.parser.ast import *


@Compiler.register(Program)
def translate_program(compiler, program):
	instrs = map(compiler.translate, program.instructions)
	module = python_ast.Module(body=list(instrs))
	return module


@Compiler.register(Declaration)
def translate_declaration(compiler, declaration):
	assign = python_ast.Assign()
	assign.targets = [
		python_ast.Name(id=declaration.name, ctx=python_ast.Store())
	]
	assign.value = compiler.translate(declaration.value)
	return assign


@Compiler.register(Call)
def translate_call(compiler, call):
	return python_ast.Call(
		func=compiler.translate(call.func),
		args=list(map(compiler.translate, call.args)),
		keywords=[]
	)


@Compiler.register(Lambda)
def translate_lambda(compiler, lambda_):
	return python_ast.Lambda(
		args=python_ast.arguments(
			args=list(map(lambda n: python_ast.arg(arg=n, annotation=None), lambda_.params)),
			vararg=None,
			kwonlyargs=[],
			kw_defaults=[],
			kwarg=None,
			defaults=[]
		),
		body=compiler.translate(lambda_.body)
	)


@Compiler.register(Variable)
def translate_variable(compiler, var):
	return python_ast.Name(var.name, python_ast.Load())


@Compiler.register(IntLiteral, FloatLiteral)
def translate_num(compiler, num):
	return python_ast.Num(num.value)


@Compiler.register(CharLiteral, StringLiteral)
def translate_string_or_char(compiler, string_or_char):
	return python_ast.Str(string_or_char.value)
